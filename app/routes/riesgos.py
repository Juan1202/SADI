from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from models import db, Control, Evaluacion, ResultadoControl, PreguntaControl, PlanTratamiento
from extensions import s3_client, S3_BUCKET
from routes.auditoria import actualizar_promedio_auditoria
from escalas import madurez_desde_riesgo, riesgo_de_hallazgo, zona_riesgo, UMBRAL_RIESGO_BLOQUEANTE
from utils import role_required, registrar_actividad, ROL_ADMINISTRADOR, ROL_AUDITOR
from remediacion import sugerir, borrador_acciones

riesgos_bp = Blueprint('riesgos', __name__)


def _procesar_pregunta(pregunta_data, index, resultado_control, auditoria):
    """
    Procesa los datos de una pregunta, sube archivos adjuntos, calcula el riesgo
    y crea un nuevo objeto PreguntaControl.
    """
    texto_in = pregunta_data.get('texto', '')
    hallazgo_in = pregunta_data.get('hallazgo', '')
    archivo_nombre_final = pregunta_data.get('archivo_previo', None)

    file_key = f'file_{index}'
    if file_key in request.files:
        file = request.files[file_key]
        if file and file.filename != '':
            try:
                fname = secure_filename(file.filename)
                unique_name = f"{auditoria.codigo}_{resultado_control.control.codigo}_P{index}_{fname}"
                s3_client.upload_fileobj(
                    file, S3_BUCKET, unique_name,
                    ExtraArgs={'ContentType': file.content_type}
                )
                archivo_nombre_final = unique_name
            except Exception as e:
                print(f"Error subiendo archivo a MinIO: {e}")

    try:
        prob = int(pregunta_data.get('probabilidad', 1))
    except (ValueError, TypeError):
        prob = 1
    try:
        imp = int(pregunta_data.get('impacto', 1))
    except (ValueError, TypeError):
        imp = 1

    riesgo = riesgo_de_hallazgo(prob, imp)

    nueva_pregunta = PreguntaControl(
        resultado_control_id=resultado_control.id,
        texto_pregunta=texto_in,
        peso_porcentaje=0,
        tipo_respuesta='riesgo',
        probabilidad=prob,
        impacto=imp,
        nivel_riesgo=riesgo,
        hallazgo=hallazgo_in,
        archivo_evidencia=archivo_nombre_final
    )

    return nueva_pregunta, riesgo


@riesgos_bp.route('/api/control/<int:control_id>/obtener_preguntas', methods=['GET'])
@login_required
def obtener_preguntas(control_id):
    preguntas = PreguntaControl.query.filter_by(resultado_control_id=control_id).all()
    data = []
    for p in preguntas:
        data.append({
            'id': p.id,
            'texto': p.texto_pregunta,
            'peso': p.peso_porcentaje,
            'tipo': p.tipo_respuesta,
            'respuesta_bool': p.respuesta_bool,
            'respuesta_texto': p.respuesta_texto,
            'hallazgo': p.hallazgo,
            'archivo': p.archivo_evidencia,
            'probabilidad': p.probabilidad,
            'impacto': p.impacto
        })
    return jsonify(data)


@riesgos_bp.route('/api/control/<int:control_id>/guardar_preguntas', methods=['POST'])
@login_required
def guardar_preguntas_control(control_id):
    json_data = request.form.get('data')
    if not json_data:
        return jsonify({'error': 'No data'}), 400

    preguntas_list = json.loads(json_data)
    resultado_control = ResultadoControl.query.get_or_404(control_id)
    auditoria = resultado_control.evaluacion

    PreguntaControl.query.filter_by(resultado_control_id=resultado_control.id).delete()

    max_riesgo_detectado = 0
    if preguntas_list:
        for index, p_data in enumerate(preguntas_list):
            nueva_pregunta, riesgo = _procesar_pregunta(p_data, index, resultado_control, auditoria)
            db.session.add(nueva_pregunta)
            if riesgo > max_riesgo_detectado:
                max_riesgo_detectado = riesgo

    resultado_control.nivel_riesgo_max = max_riesgo_detectado
    resultado_control.nivel_madurez = madurez_desde_riesgo(max_riesgo_detectado)
    resultado_control.nivel_cumplimiento = float(max_riesgo_detectado)  # deprecado

    db.session.commit()

    actualizar_promedio_auditoria(auditoria.id)

    return jsonify({'message': 'Guardado', 'riesgo_real': max_riesgo_detectado})


@riesgos_bp.route('/analisis-riesgos')
@login_required
def analisis_riesgos():
    """
    Riesgos altos y extremos consolidados de las auditorias visibles.

    Excluye las auditorias de la papelera y, para los roles no administradores,
    las de otros propietarios (defecto B5). Cada fila enlaza al plan del
    ResultadoControl concreto, que es el unico que marca riesgo_tratado y por
    tanto desbloquea el cierre de la auditoria (defecto B6).
    """
    query = (db.session.query(PreguntaControl)
             .join(ResultadoControl, PreguntaControl.resultado_control_id == ResultadoControl.id)
             .join(Evaluacion, ResultadoControl.evaluacion_id == Evaluacion.id)
             .filter(
                 (PreguntaControl.probabilidad * PreguntaControl.impacto) >= UMBRAL_RIESGO_BLOQUEANTE,
                 Evaluacion.eliminado == False
             ))

    if current_user.role != ROL_ADMINISTRADOR:
        query = query.filter(Evaluacion.user_id == current_user.id)

    riesgos_map = {}
    for h in query.all():
        resultado = h.resultado
        nivel = riesgo_de_hallazgo(h.probabilidad, h.impacto)
        actual = riesgos_map.get(resultado.id)
        if actual is None:
            riesgos_map[resultado.id] = {
                'control': resultado.control,
                'resultado': resultado,
                'evaluacion': resultado.evaluacion,
                'nivel_max': nivel,
                'zona': zona_riesgo(nivel),
                'plan_existente': PlanTratamiento.query.filter_by(
                    resultado_control_id=resultado.id).first(),
            }
        elif nivel > actual['nivel_max']:
            actual['nivel_max'] = nivel
            actual['zona'] = zona_riesgo(nivel)

    riesgos = sorted(riesgos_map.values(), key=lambda r: r['nivel_max'], reverse=True)
    return render_template('analisis_riesgos.html', riesgos=riesgos)


@riesgos_bp.route('/tratamiento/resultado/<int:resultado_id>', methods=['GET', 'POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def tratar_riesgo_auditoria(resultado_id):
    """Plan de tratamiento ligado a un ResultadoControl específico de una auditoría."""
    resultado = ResultadoControl.query.get_or_404(resultado_id)
    control = resultado.control
    evaluacion = resultado.evaluacion

    plan = PlanTratamiento.query.filter_by(resultado_control_id=resultado_id).first()

    if request.method == 'POST':
        if not plan:
            plan = PlanTratamiento(control_id=control.id, resultado_control_id=resultado_id)
            count = PlanTratamiento.query.count() + 1
            plan.codigo_riesgo = f"R-{control.codigo}-{count:03d}"
            db.session.add(plan)

        plan.descripcion_riesgo = request.form.get('descripcion')
        plan.nivel_riesgo_inicial = request.form.get('nivel_riesgo')
        plan.proceso_negocio = request.form.get('proceso')
        plan.activos_relacionados = request.form.get('activos')
        plan.estrategia = request.form.get('estrategia')
        plan.acciones = request.form.get('acciones')
        plan.tipo_control = request.form.get('tipo_control')
        plan.responsable = request.form.get('responsable')
        plan.estado = request.form.get('estado')
        d_str = request.form.get('plazo')
        if d_str:
            plan.plazo = datetime.strptime(d_str, '%Y-%m-%d').date()

        resultado.riesgo_tratado = (plan.estado == 'Cerrado')

        db.session.commit()
        registrar_actividad('Tratar riesgo', 'riesgos',
                            f'Plan {plan.codigo_riesgo} ({plan.estado}) — Auditoría {evaluacion.codigo}')
        flash('Plan de tratamiento guardado.', 'success')
        return redirect(url_for('auditoria.ver_evaluacion', id=evaluacion.id))

    riesgo = (plan.nivel_riesgo_inicial if plan and plan.nivel_riesgo_inicial
              else resultado.nivel_riesgo_max)
    sugerencia = sugerir(control.codigo, riesgo)
    return render_template('plan_tratamiento_auditoria.html',
                           control=control, plan=plan,
                           resultado=resultado, evaluacion=evaluacion,
                           sugerencia=sugerencia,
                           borrador=borrador_acciones(sugerencia))


@riesgos_bp.route('/api/remediacion/<codigo>')
@login_required
def api_remediacion(codigo):
    """Sugerencia de remediacion NIST para un control ISO y un nivel de riesgo (?riesgo=N)."""
    control = Control.query.filter_by(codigo=codigo).first()
    if control is None:
        abort(404)
    riesgo = request.args.get('riesgo', type=int, default=0)
    sugerencia = sugerir(control.codigo, riesgo)
    sugerencia['borrador_acciones'] = borrador_acciones(sugerencia)
    return jsonify(sugerencia)


@riesgos_bp.route('/tratamiento/control/<int:control_id>', methods=['GET', 'POST'])
@login_required
def tratar_riesgo(control_id):
    control = Control.query.get_or_404(control_id)
    plan = PlanTratamiento.query.filter_by(control_id=control_id, estado='Abierto').first()

    if request.method == 'POST':
        if not plan:
            plan = PlanTratamiento(control_id=control_id)
            count = PlanTratamiento.query.count() + 1
            plan.codigo_riesgo = f"R-{control.codigo}-{count:03d}"
            db.session.add(plan)

        plan.descripcion_riesgo = request.form.get('descripcion')
        plan.nivel_riesgo_inicial = request.form.get('nivel_riesgo')
        plan.proceso_negocio = request.form.get('proceso')
        plan.activos_relacionados = request.form.get('activos')
        plan.estrategia = request.form.get('estrategia')
        plan.acciones = request.form.get('acciones')
        plan.tipo_control = request.form.get('tipo_control')
        plan.responsable = request.form.get('responsable')
        plan.estado = request.form.get('estado')
        d_str = request.form.get('plazo')
        if d_str:
            plan.plazo = datetime.strptime(d_str, '%Y-%m-%d').date()

        db.session.commit()
        return redirect(url_for('riesgos.analisis_riesgos'))
    return render_template('plan_tratamiento.html', control=control, plan=plan)
