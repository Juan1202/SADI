from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import text, func
from sqlalchemy.orm import joinedload
from models import db, Control, Evaluacion, PreguntaControl, ResultadoControl
from escalas import UMBRAL_RIESGO_BLOQUEANTE

dashboard_bp = Blueprint('dashboard', __name__)


def _riesgos_residuales(ids_auditorias):
    """
    {id_auditoria: riesgo residual} en una sola consulta.

    Residual = el mayor probabilidad x impacto que queda entre los controles
    SIN tratar. Un control cuyo plan de tratamiento se cerro deja de sumar,
    que es lo que ya asume la regla de bloqueo al permitir finalizar.
    """
    if not ids_auditorias:
        return {}
    filas = (db.session.query(
                 ResultadoControl.evaluacion_id,
                 func.max(PreguntaControl.probabilidad * PreguntaControl.impacto))
             .join(PreguntaControl,
                   PreguntaControl.resultado_control_id == ResultadoControl.id)
             .filter(ResultadoControl.evaluacion_id.in_(ids_auditorias),
                     ResultadoControl.riesgo_tratado == False)
             .group_by(ResultadoControl.evaluacion_id)
             .all())
    return {id_auditoria: (riesgo or 0) for id_auditoria, riesgo in filas}


def _calculate_risk_counts(auditorias):
    """
    Clasifica las auditorias por su riesgo RESIDUAL para el grafico del tablero.

    Antes se leia Evaluacion.riesgo_maximo, que guarda el riesgo INHERENTE: una
    auditoria que ya habia cerrado todos sus planes de riesgo alto seguia
    contando como critica y el grafico se quedaba con un solo segmento.
    """
    counts = {'critico': 0, 'alerta': 0, 'optimo': 0}
    auditorias_riesgo = []
    residuales = _riesgos_residuales([a.id for a in auditorias])
    for aud in auditorias:
        riesgo = residuales.get(aud.id, 0)
        if riesgo >= UMBRAL_RIESGO_BLOQUEANTE:
            counts['critico'] += 1
            auditorias_riesgo.append(aud)
        elif riesgo >= 3:
            counts['alerta'] += 1
        else:
            counts['optimo'] += 1
    return counts, auditorias_riesgo


def _calculate_domain_averages():
    """
    Madurez promedio (0-5) por dominio del Anexo A, para el grafico GAP.

    El dominio es el PRIMER segmento del codigo del control ("5.1" -> 5). Antes
    se tomaba el segundo segmento, que devolvia "1" y hacia que ninguna suma se
    acumulara, dejando el grafico siempre en cero (defecto B1).
    """
    dom_sums = {i: 0.0 for i in range(5, 9)}
    dom_counts = {i: 0 for i in range(5, 9)}

    all_results = (db.session.query(ResultadoControl)
                   .join(Evaluacion)
                   .options(joinedload(ResultadoControl.control))
                   .filter(Evaluacion.eliminado == False)
                   .all())

    for res in all_results:
        codigo = (res.control.codigo or '').replace('A.', '')
        dom_num_str = codigo.split('.')[0]
        if not dom_num_str.isdigit():
            continue
        dom_num = int(dom_num_str)
        if dom_num not in dom_sums:
            continue
        madurez = res.nivel_madurez or 0.0
        if madurez <= 0:
            continue  # control sin evaluar: no arrastra el promedio hacia abajo
        dom_sums[dom_num] += madurez
        dom_counts[dom_num] += 1

    return [round(dom_sums[i] / dom_counts[i], 2) if dom_counts[i] > 0 else 0
            for i in range(5, 9)]


def _get_all_controls_details():
    """Helper to get average risk for all controls using a single efficient query."""
    avg_risk_subquery = db.session.query(
        ResultadoControl.control_id,
        func.avg(ResultadoControl.nivel_madurez).label('avg_risk')
    ).join(Evaluacion).filter(
        Evaluacion.eliminado == False,
        ResultadoControl.nivel_madurez > 0
    ).group_by(ResultadoControl.control_id).subquery()

    controles_con_riesgo = db.session.query(
        Control,
        avg_risk_subquery.c.avg_risk
    ).outerjoin(
        avg_risk_subquery, Control.id == avg_risk_subquery.c.control_id
    ).order_by(Control.id).all()

    controles_detalle = [{
        'codigo': ctrl.codigo,
        'nombre': ctrl.nombre,
        'madurez': float(avg_risk or 0)
    } for ctrl, avg_risk in controles_con_riesgo]

    return controles_detalle, len(controles_con_riesgo)


@dashboard_bp.route('/')
@login_required
def home():
    db_connected = False
    try:
        db.session.execute(text('SELECT 1'))
        db_connected = True
    except Exception as e:
        print(f"Error de conexión: {e}")
    return render_template('index.html', db_connected=db_connected)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard_metrics():
    page = request.args.get('page', 1, type=int)

    total_auditorias = Evaluacion.query.filter_by(eliminado=False).count()

    auditorias_activas = Evaluacion.query.filter_by(eliminado=False).all()
    risk_counts, auditorias_riesgo = _calculate_risk_counts(auditorias_activas)

    data_dom = _calculate_domain_averages()

    controles_detalle, total_controles = _get_all_controls_details()

    pagination = Evaluacion.query.filter_by(eliminado=False).order_by(Evaluacion.fecha_creacion.desc()).paginate(page=page, per_page=5)

    return render_template('dashboard_metrics.html',
                           total_auditorias=total_auditorias,
                           count_riesgo=risk_counts['critico'],
                           auditorias_riesgo=auditorias_riesgo,
                           estado_counts={
                               'Critico': risk_counts['critico'],
                               'Alerta': risk_counts['alerta'],
                               'Optimo': risk_counts['optimo']
                           },
                           data_dom=data_dom,
                           controles_detalle=controles_detalle,
                           pagination=pagination,
                           total_controles=total_controles)
