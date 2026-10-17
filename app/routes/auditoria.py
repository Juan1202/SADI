from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response, send_file
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from io import BytesIO
from xhtml2pdf import pisa
from models import db, Control, Evaluacion, ResultadoControl, PreguntaControl, PlanTratamiento
from extensions import s3_client, S3_BUCKET
from utils import allowed_file, admin_required, role_required, registrar_actividad, PDF_MIME_TYPE, ROL_ADMINISTRADOR, ROL_AUDITOR, ROL_CONSULTOR, ROL_LECTOR, DOMINIO_FISICO, DOMINIO_TECNOLOGICO, DOMINIO_ORGANIZACIONAL, DOMINIO_PERSONAS
from escalas import madurez_desde_riesgo, riesgo_de_hallazgo, UMBRAL_RIESGO_BLOQUEANTE

auditoria_bp = Blueprint('auditoria', __name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _check_critical_risk(evaluacion):
    """
    Regla de bloqueo: devuelve el hallazgo sin tratar de MAYOR riesgo que impide
    cerrar la auditoria (antes devolvia el primero que encontraba, no el peor).
    """
    peor_control, peor_riesgo = "", 0
    for res in evaluacion.resultados:
        if res.riesgo_tratado:
            continue
        for preg in res.preguntas:
            riesgo = riesgo_de_hallazgo(preg.probabilidad, preg.impacto)
            if riesgo >= UMBRAL_RIESGO_BLOQUEANTE and riesgo > peor_riesgo:
                peor_control, peor_riesgo = res.control.codigo, riesgo
    if peor_riesgo:
        return True, peor_control, peor_riesgo
    return False, "", 0


def _calculate_audit_score(evaluacion):
    """
    Madurez promedio de la auditoria (0-5), segun ADR-011.

    Antes leia respuesta_bool / respuesta_texto, campos que el flujo de riesgos
    nunca escribe, por lo que el resultado siempre era 0.0 (defecto B2). Ahora
    se deriva del riesgo maximo de cada control evaluado, que es lo que el flujo
    de riesgos si persiste.
    """
    suma, conteo = 0.0, 0
    for res in evaluacion.resultados:
        riesgo = _calculate_max_risk_for_result(res)
        if riesgo <= 0:
            continue  # control sin hallazgos: no participa en el promedio
        suma += madurez_desde_riesgo(riesgo)
        conteo += 1
    return round(suma / conteo, 2) if conteo > 0 else 0.0


def _calculate_max_audit_risk(evaluacion):
    """Riesgo maximo (1-25) encontrado en toda la auditoria."""
    return max(
        (_calculate_max_risk_for_result(res) for res in evaluacion.resultados),
        default=0,
    )


def _calculate_max_risk_for_result(result):
    return max(
        (riesgo_de_hallazgo(p.probabilidad, p.impacto) for p in result.preguntas),
        default=0,
    )


def _prepare_in_progress_evaluation(evaluacion):
    db.session.expire_all()
    for res in evaluacion.resultados:
        setattr(res, 'riesgo_calculado_temp', _calculate_max_risk_for_result(res))
        plan = PlanTratamiento.query.filter_by(resultado_control_id=res.id).first()
        setattr(res, 'plan_tratamiento_temp', plan)


def actualizar_promedio_auditoria(auditoria_id):
    """
    Recalcula las dos metricas de la auditoria (ADR-011):
      * score_promedio : madurez promedio 0-5
      * riesgo_maximo  : riesgo maximo 1-25
    """
    auditoria = Evaluacion.query.get(auditoria_id)
    auditoria.score_promedio = _calculate_audit_score(auditoria)
    auditoria.riesgo_maximo = _calculate_max_audit_risk(auditoria)
    db.session.commit()
    return auditoria.score_promedio


# ── Rutas ─────────────────────────────────────────────────────────────────────

@auditoria_bp.route('/evaluacion/nueva')
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def vista_nueva_evaluacion():
    controles_raw = Control.query.all()
    controles = sorted(
        controles_raw,
        key=lambda x: [int(n) for n in x.codigo.replace('A.', '').split('.') if n.isdigit()]
    )
    conteo = {d: Control.query.filter_by(dominio=d).count() for d in [DOMINIO_ORGANIZACIONAL, DOMINIO_PERSONAS, DOMINIO_FISICO, DOMINIO_TECNOLOGICO]}
    return render_template('nueva_evaluacion.html', controles=controles, conteo=conteo)


@auditoria_bp.route('/evaluacion/preparar', methods=['POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def preparar_auditoria():
    ids_controles  = request.form.getlist('controles')
    nombre_auditor = request.form.get('auditor')
    titulo         = request.form.get('titulo')

    if not ids_controles:
        flash('Debes seleccionar al menos un control.', 'warning')
        return redirect(url_for('auditoria.vista_nueva_evaluacion'))

    controles_seleccionados = Control.query.filter(Control.id.in_(ids_controles)).all()
    controles_seleccionados.sort(
        key=lambda x: [int(n) for n in x.codigo.replace('A.', '').split('.') if n.isdigit()]
    )

    base_code = f"AUD-{datetime.now().strftime('%Y%m')}"
    if controles_seleccionados:
        first = controles_seleccionados[0].codigo
        if len(controles_seleccionados) == 1:
            base_code = f"AUD-{first}"
        else:
            base_code = f"AUD-{first}-{controles_seleccionados[-1].codigo}"

    codigo_final, contador = base_code, 1
    while Evaluacion.query.filter_by(codigo=codigo_final).first() is not None:
        codigo_final = f"{base_code}-{contador}"
        contador += 1

    nueva_evaluacion = Evaluacion(
        codigo=codigo_final, titulo=titulo, evaluador=nombre_auditor,
        user_id=current_user.id, estado='En Proceso', fecha_creacion=datetime.now()
    )
    db.session.add(nueva_evaluacion)
    db.session.flush()

    for control in controles_seleccionados:
        db.session.add(ResultadoControl(
            evaluacion_id=nueva_evaluacion.id, control_id=control.id, nivel_cumplimiento=0.0
        ))

    db.session.commit()
    registrar_actividad('Crear auditoría', 'auditorias', f'Auditoría creada: {codigo_final}')

    return render_template('ejecutar_auditoria.html',
                           controles=nueva_evaluacion.resultados,
                           nombre_auditor=nombre_auditor,
                           titulo=titulo,
                           codigo=codigo_final,
                           evaluacion_id=nueva_evaluacion.id)


@auditoria_bp.route('/auditoria/finalizar', methods=['POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def finalizar_auditoria():
    codigo     = request.form.get('codigo_auditoria_final')
    evaluacion = Evaluacion.query.filter_by(codigo=codigo).first()

    if not evaluacion:
        flash('Error: Auditoría no encontrada.', 'error')
        return redirect(url_for('auditoria.listar_auditorias'))

    db.session.expire_all()
    riesgo_critico, bloqueante, nivel_detectado = _check_critical_risk(evaluacion)

    if riesgo_critico:
        evaluacion.estado = "En Proceso"
        db.session.commit()
        flash(f'ALERTA: No se puede finalizar. El control {bloqueante} tiene Riesgo ALTO/EXTREMO ({nivel_detectado}). Trate el riesgo primero.', 'error')
        return redirect(url_for('auditoria.ver_evaluacion', id=evaluacion.id))

    evaluacion.estado       = "Finalizada"
    evaluacion.fecha_fin    = datetime.now(timezone.utc)
    evaluacion.score_promedio = _calculate_audit_score(evaluacion)
    evaluacion.riesgo_maximo  = _calculate_max_audit_risk(evaluacion)

    try:
        db.session.commit()
        registrar_actividad('Finalizar auditoría', 'auditorias', f'Auditoría finalizada: {codigo}')
        flash('Auditoría finalizada.', 'success')
        return redirect(url_for('dashboard.dashboard_metrics'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('auditoria.ver_evaluacion', id=evaluacion.id))


@auditoria_bp.route('/auditoria/<int:id>')
@login_required
def ver_evaluacion(id):
    evaluacion = Evaluacion.query.get_or_404(id)
    if evaluacion.estado == 'En Proceso':
        _prepare_in_progress_evaluation(evaluacion)
        flash(f'Retomando auditoría {evaluacion.codigo}.', 'info')
        return render_template('ejecutar_auditoria.html',
                               controles=evaluacion.resultados,
                               nombre_auditor=evaluacion.evaluador,
                               titulo=evaluacion.titulo,
                               codigo=evaluacion.codigo,
                               evaluacion=evaluacion)
    return render_template('detalle_evaluacion.html', evaluacion=evaluacion)


@auditoria_bp.route('/auditorias')
@login_required
def listar_auditorias():
    page   = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    query  = Evaluacion.query.filter_by(eliminado=False)

    if current_user.role != ROL_ADMINISTRADOR:
        query = query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(or_(
            Evaluacion.codigo.ilike(f"%{search}%"),
            Evaluacion.titulo.ilike(f"%{search}%")
        ))

    pagination = query.order_by(Evaluacion.fecha_creacion.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('auditorias.html', pagination=pagination, search=search)


@auditoria_bp.route('/auditorias/editar/<int:id>', methods=['POST'])
@login_required
def editar_auditoria(id):
    ev = Evaluacion.query.get_or_404(id)
    if current_user.role != ROL_ADMINISTRADOR and ev.user_id != current_user.id:
        abort(403)
    ev.evaluador   = request.form.get('evaluador')
    ev.descripcion = request.form.get('descripcion')
    fecha_str      = request.form.get('fecha')
    if fecha_str:
        try:
            ev.fecha_creacion = datetime.strptime(fecha_str, '%Y-%m-%d')
        except ValueError:
            pass
    db.session.commit()
    registrar_actividad('Editar auditoría', 'auditorias', f'Auditoría editada: {ev.codigo}')
    flash('Auditoría actualizada.', 'success')
    return redirect(url_for('auditoria.listar_auditorias'))


@auditoria_bp.route('/auditorias/eliminar/<int:id>', methods=['GET', 'POST'])
@login_required
def eliminar_auditoria(id):
    ev = Evaluacion.query.get_or_404(id)
    if current_user.role != ROL_ADMINISTRADOR and ev.user_id != current_user.id:
        abort(403)
    if ev.estado == 'Finalizada' and current_user.role != ROL_ADMINISTRADOR:
        flash('No puedes eliminar una auditoría finalizada.', 'danger')
        return redirect(url_for('auditoria.listar_auditorias'))
    ev.eliminado = True
    db.session.commit()
    registrar_actividad('Eliminar auditoría', 'auditorias', f'Auditoría enviada a papelera: {ev.codigo}')
    return redirect(url_for('auditoria.listar_auditorias'))


@auditoria_bp.route('/evaluacion/actualizar/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def actualizar_auditoria(id):
    evaluacion = Evaluacion.query.get_or_404(id)
    suma_puntos, total_controles = 0, 0

    for resultado in evaluacion.resultados:
        nivel_cumplimiento = request.form.get(f'cumplimiento_{resultado.id}')
        evidencia_texto    = request.form.get(f'evidencia_{resultado.id}')
        archivo            = request.files.get(f'archivo_{resultado.id}')

        if nivel_cumplimiento is not None:
            # El formulario clasico captura madurez 0-5, no riesgo (ADR-011).
            resultado.nivel_madurez = float(nivel_cumplimiento)
            resultado.nivel_cumplimiento = float(nivel_cumplimiento)
        if evidencia_texto is not None:
            resultado.evidencia_texto = evidencia_texto

        if archivo and archivo.filename != '' and allowed_file(archivo.filename):
            fname       = secure_filename(archivo.filename)
            unique_name = f"ev_{evaluacion.id}_ctrl_{resultado.control_id}_{fname}"
            try:
                s3_client.upload_fileobj(
                    archivo, S3_BUCKET, unique_name,
                    ExtraArgs={'ContentType': archivo.content_type}
                )
                resultado.evidencia_archivo = unique_name
            except Exception as e:
                print(f"Error MinIO Update: {e}")

    for res in evaluacion.resultados:
        suma_puntos     += res.nivel_madurez or 0.0
        total_controles += 1

    if total_controles > 0:
        evaluacion.score_promedio = round(suma_puntos / total_controles, 2)
    evaluacion.riesgo_maximo = _calculate_max_audit_risk(evaluacion)

    db.session.commit()
    registrar_actividad('Actualizar auditoría', 'auditorias', f'Respuestas guardadas: {evaluacion.codigo}')
    flash('Auditoría actualizada.', 'success')
    return redirect(url_for('auditoria.ver_evaluacion', id=id))


@auditoria_bp.route('/uploads/<path:filename>')
@login_required
def download_file(filename):
    try:
        file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
        return send_file(file_obj['Body'], download_name=filename, as_attachment=True)
    except Exception as e:
        print(f"Error S3: {e}")
        return abort(404)


@auditoria_bp.route('/auditoria/reporte/<int:evaluacion_id>')
@login_required
def generar_pdf(evaluacion_id):
    ev   = Evaluacion.query.get_or_404(evaluacion_id)
    html = render_template('reporte_pdf.html', evaluacion=ev)
    result = BytesIO()
    pdf    = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type']        = PDF_MIME_TYPE
        response.headers['Content-Disposition'] = f'inline; filename=Informe_{ev.codigo}.pdf'
        return response
    return "Error al generar el PDF", 500


@auditoria_bp.route('/auditoria/cerrar/<int:id>', methods=['POST'])
@login_required
def cerrar_ciclo_auditoria(id):
    ev = Evaluacion.query.get_or_404(id)
    if current_user.role != ROL_ADMINISTRADOR and ev.user_id != current_user.id:
        abort(403)
    # La regla de bloqueo aplica a TODAS las rutas que cierran una auditoria;
    # antes esta ruta la omitia y permitia cerrar con riesgos altos sin tratar.
    riesgo_critico, bloqueante, nivel_detectado = _check_critical_risk(ev)
    if riesgo_critico:
        flash(f'ALERTA: No se puede finalizar. El control {bloqueante} tiene Riesgo ALTO/EXTREMO ({nivel_detectado}). Trate el riesgo primero.', 'error')
        return redirect(url_for('auditoria.ver_evaluacion', id=ev.id))
    ev.estado   = 'Finalizada'
    ev.fecha_fin = datetime.now()
    db.session.commit()
    registrar_actividad('Cerrar auditoría', 'auditorias', f'Auditoría cerrada: {ev.codigo}')
    flash('Auditoría finalizada.', 'success')
    return redirect(url_for('auditoria.listar_auditorias'))


@auditoria_bp.route('/papelera')
@role_required(ROL_ADMINISTRADOR)
def ver_papelera():
    auditorias = Evaluacion.query.filter_by(eliminado=True).all()
    return render_template('papelera.html', auditorias=auditorias)


@auditoria_bp.route('/auditoria/restaurar/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR)
def restaurar_auditoria(id):
    ev = Evaluacion.query.get_or_404(id)
    ev.eliminado = False
    db.session.commit()
    registrar_actividad('Restaurar auditoría', 'auditorias', f'Auditoría restaurada: {ev.codigo}')
    return redirect(url_for('auditoria.ver_papelera'))


@auditoria_bp.route('/auditoria/eliminar_definitivo/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR)
def eliminar_auditoria_definitivo(id):
    ev = Evaluacion.query.get_or_404(id)
    codigo = ev.codigo
    db.session.delete(ev)
    db.session.commit()
    registrar_actividad('Eliminar auditoría definitivo', 'auditorias', f'Auditoría eliminada permanentemente: {codigo}')
    return redirect(url_for('auditoria.ver_papelera'))
