from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import cast, Integer
from models import db, CategoriaDiagnostico, PreguntaDiagnostico, Diagnostico, RespuestaDiagnostico
from utils import role_required, registrar_actividad, ROL_ADMINISTRADOR, ROL_AUDITOR

diagnostico_bp = Blueprint('diagnostico', __name__)


VALORES_EVALUADOS = ('cumple', 'parcial', 'no_cumple')


def _puntaje(respuestas):
    """
    Porcentaje de cumplimiento de un conjunto de respuestas, redondeado a un decimal.

    Cuenta 1 por 'cumple' y 0,5 por 'parcial', sobre las respuestas realmente
    evaluadas: 'no_aplica' y 'no_evaluado' quedan fuera del denominador.
    """
    evaluadas = [r for r in respuestas if r.valor in VALORES_EVALUADOS]
    if not evaluadas:
        return 0.0
    puntos = sum(1 for r in evaluadas if r.valor == 'cumple')
    puntos += sum(0.5 for r in evaluadas if r.valor == 'parcial')
    return round(puntos / len(evaluadas) * 100, 1)


@diagnostico_bp.route('/diagnostico/iniciar')
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def iniciar_diagnostico():
    if CategoriaDiagnostico.query.count() == 0:
        categorias_data = [
            ("4", "Contexto de la Organización", [
                ("4.1", "¿Se han determinado las cuestiones externas e internas que son pertinentes para el propósito del SGSI?"),
                ("4.2", "¿Se han identificado las partes interesadas pertinentes y sus requisitos de seguridad de la información?"),
                ("4.3", "¿Están definidos los límites y la aplicabilidad del SGSI (Alcance) y se encuentra documentado?"),
                ("4.4", "¿Se ha establecido, implementado y mantenido un SGSI de acuerdo con los requisitos de la norma?")
            ]),
            ("5", "Liderazgo", [
                ("5.1", "¿La alta dirección demuestra liderazgo y compromiso respecto al SGSI?"),
                ("5.2", "¿Existe una Política de Seguridad de la Información aprobada, comunicada y disponible?"),
                ("5.3", "¿Se han asignado y comunicado las responsabilidades y autoridades para los roles pertinentes a la seguridad?")
            ]),
            ("6", "Planificación", [
                ("6.1.2", "¿Se ha establecido y aplicado un proceso de apreciación de riesgos de seguridad de la información?"),
                ("6.1.3", "¿Se ha establecido y aplicado un proceso de tratamiento de riesgos y se ha generado una Declaración de Aplicabilidad (SoA)?"),
                ("6.2", "¿Se han establecido objetivos de seguridad de la información medibles y comunicados?")
            ]),
            ("7", "Apoyo", [
                ("7.1", "¿La organización ha determinado y proporcionado los recursos necesarios para el SGSI?"),
                ("7.2", "¿Se ha determinado la competencia necesaria de las personas y se conserva información documentada como evidencia?"),
                ("7.3", "¿Las personas toman conciencia de la política de seguridad y de las implicaciones de no cumplir los requisitos?"),
                ("7.5", "¿La información documentada requerida por la norma está controlada, protegida y disponible?")
            ]),
            ("8", "Operación", [
                ("8.1", "¿Se planifican, implementan y controlan los procesos necesarios para cumplir los requisitos de seguridad?"),
                ("8.2", "¿Se realizan apreciaciones de riesgos a intervalos planificados o tras cambios significativos?"),
                ("8.3", "¿Se ha implementado el plan de tratamiento de riesgos de seguridad de la información?")
            ]),
            ("9", "Evaluación del Desempeño", [
                ("9.1", "¿Se evalúa el desempeño de la seguridad de la información y la eficacia del SGSI?"),
                ("9.2", "¿Se llevan a cabo auditorías internas a intervalos planificados?"),
                ("9.3", "¿La alta dirección revisa el SGSI a intervalos planificados para asegurar su conveniencia, adecuación y eficacia continuas?")
            ]),
            ("10", "Mejora", [
                ("10.1", "¿La organización mejora continuamente la idoneidad, adecuación y eficacia del SGSI?"),
                ("10.2", "¿Se reacciona de manera oportuna ante las no conformidades y se toman acciones correctivas?")
            ])
        ]

        for num, nombre, preguntas in categorias_data:
            cat = CategoriaDiagnostico(numero=num, nombre=nombre)
            db.session.add(cat)
            db.session.flush()
            for req, texto in preguntas:
                preg = PreguntaDiagnostico(categoria_id=cat.id, requisito=req, texto=texto)
                db.session.add(preg)
        db.session.commit()

    nuevo_diag = Diagnostico(user_id=current_user.id)
    db.session.add(nuevo_diag)
    db.session.flush()

    todas_las_preguntas = PreguntaDiagnostico.query.all()
    for pregunta in todas_las_preguntas:
        resp = RespuestaDiagnostico(diagnostico_id=nuevo_diag.id, pregunta_id=pregunta.id)
        db.session.add(resp)

    db.session.commit()
    registrar_actividad('Iniciar diagnóstico', 'diagnostico', f'Diagnóstico #{nuevo_diag.id} iniciado')
    return redirect(url_for('diagnostico.ejecutar_diagnostico', id=nuevo_diag.id))


@diagnostico_bp.route('/diagnostico/ejecutar/<int:id>')
@login_required
def ejecutar_diagnostico(id):
    diagnostico = Diagnostico.query.get_or_404(id)

    if diagnostico.user_id != current_user.id and current_user.role != ROL_ADMINISTRADOR:
        flash('No tienes permiso para ver este diagnóstico.', 'danger')
        return redirect(url_for('info.clausulas_iso'))

    categorias = CategoriaDiagnostico.query.order_by(cast(CategoriaDiagnostico.numero, Integer)).all()
    respuestas_raw = RespuestaDiagnostico.query.filter_by(diagnostico_id=id).all()
    resp_dict = {r.pregunta_id: r for r in respuestas_raw}

    # Los puntajes se calculan aqui y no solo en el navegador: antes la pantalla
    # solo los actualizaba con la respuesta del guardado por AJAX, asi que al
    # reabrir un diagnostico terminado todas las clausulas aparecian en 0 %.
    puntajes = {c.id: _puntaje([resp_dict[p.id] for p in c.preguntas if p.id in resp_dict])
                for c in categorias}

    return render_template('ejecutar_diagnostico.html',
                           diagnostico=diagnostico,
                           categorias=categorias,
                           resp_dict=resp_dict,
                           puntajes=puntajes,
                           puntaje_global=_puntaje(respuestas_raw))


@diagnostico_bp.route('/diagnostico/api/guardar', methods=['POST'])
@login_required
def api_guardar_diagnostico():
    data = request.json
    resp_id = data.get('respuesta_id')
    valor = data.get('valor')
    observacion = data.get('observacion')

    respuesta = RespuestaDiagnostico.query.get_or_404(resp_id)

    if valor is not None:
        respuesta.valor = valor
    if observacion is not None:
        respuesta.observacion = observacion

    db.session.commit()

    todas = RespuestaDiagnostico.query.filter_by(diagnostico_id=respuesta.diagnostico_id).all()

    puntaje_global = _puntaje(todas)
    respuesta.diagnostico.puntaje_global = puntaje_global
    db.session.commit()

    cat_id = respuesta.pregunta.categoria_id
    cat_score = _puntaje([r for r in todas if r.pregunta.categoria_id == cat_id])

    return jsonify({
        'success': True,
        'puntaje_global': puntaje_global,
        'cat_id': cat_id,
        'cat_score': cat_score,
    })
