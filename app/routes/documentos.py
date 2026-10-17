from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from io import BytesIO
from xhtml2pdf import pisa
import json
import base64
from models import db, Control, SoADocument, SoADetalle, PoliticaSGSI
from extensions import s3_client, S3_BUCKET_DOCS
from utils import role_required, registrar_actividad, PDF_MIME_TYPE, ROL_ADMINISTRADOR, ROL_AUDITOR, DOMINIO_FISICO, DOMINIO_TECNOLOGICO, DOMINIO_ORGANIZACIONAL, DOMINIO_PERSONAS

documentos_bp = Blueprint('documentos', __name__)


# ---- Helpers ----

def _collect_policy_form_data(tipo_doc):
    """Recopila y formatea los datos del formulario para un nuevo documento de política."""
    fecha_input = request.form.get('fecha_version')
    try:
        fecha_formateada = datetime.strptime(fecha_input, '%Y-%m-%d').strftime('%d/%m/%Y') if fecha_input else datetime.now().strftime('%d/%m/%Y')
    except ValueError:
        fecha_formateada = datetime.now().strftime('%d/%m/%Y')

    return {
        'tipo_documento': tipo_doc.upper(),
        'titulo': request.form.get('titulo'),
        'codigo': request.form.get('codigo'),
        'objetivo': request.form.get('objetivo'),
        'alcance': request.form.get('alcance'),
        'responsables': request.form.get('responsables'),
        'marco_legal': request.form.get('marco_legal'),
        'lineamientos': request.form.get('lineamientos'),
        'version': request.form.get('version'),
        'desc_cambio': request.form.get('desc_cambio'),
        'fecha': fecha_formateada,
        'elaboro': {'nombre': request.form.get('elaboro_nombre'), 'cargo': request.form.get('elaboro_cargo')},
        'reviso': {'nombre': request.form.get('reviso_nombre'), 'cargo': request.form.get('reviso_cargo')},
        'aprobo': {'nombre': request.form.get('aprobo_nombre'), 'cargo': request.form.get('aprobo_cargo')},
        'autor': current_user.username
    }


def _process_logo_upload():
    """Procesa el archivo de logo subido y lo convierte a una data URL en base64."""
    if 'logo_empresa' not in request.files:
        return None
    file = request.files['logo_empresa']
    if not file or not file.filename:
        return None
    try:
        image_bytes = file.read()
        logo_b64 = base64.b64encode(image_bytes).decode('utf-8')
        mime = "image/png" if file.filename.lower().endswith('png') else "image/jpeg"
        return f"data:{mime};base64,{logo_b64}"
    except Exception as e:
        print(f"Error procesando el logo: {e}")
        return None


def _generate_policy_pdf(data):
    """Genera el documento PDF para la política usando una plantilla HTML."""
    html = render_template('plantilla_politica_pdf.html', data=data)
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer


def _save_policy_to_db_and_s3(policy_data, pdf_buffer, tipo_doc):
    """Sube el PDF a S3 y guarda los metadatos de la política en la base de datos."""
    safe_code = secure_filename(policy_data['codigo'])
    filename = f"{tipo_doc[:3].upper()}_{safe_code}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    try:
        s3_client.upload_fileobj(pdf_buffer, S3_BUCKET_DOCS, filename, ExtraArgs={'ContentType': PDF_MIME_TYPE})

        datos_para_bd = policy_data.copy()
        datos_para_bd.pop('logo', None)

        nueva_pol = PoliticaSGSI(
            codigo=policy_data['codigo'], titulo=policy_data['titulo'], tipo=tipo_doc,
            version=policy_data['version'], nombre_archivo=filename,
            ruta_minio=S3_BUCKET_DOCS, user_id=current_user.id,
            datos_formulario=json.dumps(datos_para_bd)
        )
        db.session.add(nueva_pol)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error guardando la política: {e}")
        db.session.rollback()
        return False


# ---- Rutas SOA ----

@documentos_bp.route('/documentos')
@login_required
def vista_documentos():
    dominios = [DOMINIO_ORGANIZACIONAL, DOMINIO_PERSONAS, DOMINIO_FISICO, DOMINIO_TECNOLOGICO]
    for dom in dominios:
        soa = SoADocument.query.filter_by(dominio=dom).first()
        if not soa:
            soa = SoADocument(codigo=f"SOA-{datetime.now().year}-{dom[:3].upper()}", dominio=dom)
            db.session.add(soa)
            db.session.flush()
        # Sincronizar controles nuevos que no tengan SoADetalle aún
        existentes = {d.control_id for d in SoADetalle.query.filter_by(soa_id=soa.id).all()}
        for c in Control.query.filter_by(dominio=dom).all():
            if c.id not in existentes:
                db.session.add(SoADetalle(soa_id=soa.id, control_id=c.id, aplicable=True))
        db.session.commit()
    soas = SoADocument.query.order_by(SoADocument.dominio).all()
    return render_template('documentos.html', soas=soas)


@documentos_bp.route('/soa/<int:id>/editar/<dominio>', methods=['GET', 'POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def editar_soa_dominio(id, dominio):
    soa = SoADocument.query.get_or_404(id)

    if request.method == 'POST':
        detalles = SoADetalle.query.join(Control).filter(SoADetalle.soa_id == id, Control.dominio == dominio).all()
        for d in detalles:
            val = request.form.get(f'aplicable_{d.id}')
            d.aplicable = (val == 'si')
            d.justificacion = request.form.get(f'justificacion_{d.id}')
        soa.fecha_actualizacion = datetime.now(timezone.utc)
        db.session.commit()
        registrar_actividad('Editar SOA', 'documentos', f'SOA editado: dominio {dominio}')
        return redirect(url_for('documentos.vista_documentos'))

    detalles_raw = SoADetalle.query.join(Control).filter(SoADetalle.soa_id == id, Control.dominio == dominio).all()
    detalles_ordenados = sorted(
        detalles_raw,
        key=lambda d: [int(n) for n in d.control.codigo.replace('A.', '').split('.') if n.isdigit()]
    )
    return render_template('soa_editor.html', soa=soa, dominio=dominio, detalles=detalles_ordenados)


@documentos_bp.route('/soa/<int:id>/pdf')
@login_required
def generar_pdf_soa(id):
    soa = SoADocument.query.get_or_404(id)
    detalles_raw = SoADetalle.query.join(Control).filter(SoADetalle.soa_id == id).all()
    detalles_ordenados = sorted(
        detalles_raw,
        key=lambda d: [int(n) for n in d.control.codigo.replace('A.', '').split('.') if n.isdigit()]
    )
    html = render_template('reporte_soa_pdf.html', soa=soa, detalles=detalles_ordenados)
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    resp = make_response(pdf.getvalue())
    resp.headers['Content-Type'] = PDF_MIME_TYPE
    resp.headers['Content-Disposition'] = f'attachment; filename=SoA_{soa.codigo}.pdf'
    return resp


# ---- Rutas Políticas ----

@documentos_bp.route('/documentos/tipo')
@login_required
def seleccionar_tipo_documento():
    return render_template('seleccionar_doc.html')


@documentos_bp.route('/documentos/crear-politica', methods=['GET', 'POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def crear_politica():
    tipo_doc = request.args.get('tipo', 'Política')

    if request.method == 'POST':
        datos_completos = _collect_policy_form_data(tipo_doc)
        datos_completos['logo'] = _process_logo_upload()

        pdf_buffer = _generate_policy_pdf(datos_completos)
        if not pdf_buffer:
            flash('Error al generar el PDF del documento.', 'danger')
            return redirect(url_for('documentos.crear_politica', tipo=tipo_doc))

        if _save_policy_to_db_and_s3(datos_completos, pdf_buffer, tipo_doc):
            registrar_actividad('Crear documento', 'documentos', f'Documento creado: {datos_completos.get("codigo")} — {datos_completos.get("titulo")}')
            flash('Documento creado exitosamente.', 'success')
            return redirect(url_for('documentos.listar_documentos_generados'))
        else:
            flash('Ocurrió un error al guardar el documento.', 'danger')

    return render_template('crear_politica.html', tipo_doc=tipo_doc, fecha_hoy=datetime.now().strftime('%Y-%m-%d'))


@documentos_bp.route('/documentos/repositorio')
@login_required
def listar_documentos_generados():
    documentos = PoliticaSGSI.query.order_by(PoliticaSGSI.fecha_creacion.desc()).all()
    return render_template('listar_documentos.html', documentos=documentos)


@documentos_bp.route('/documentos/eliminar/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR)
def eliminar_documento_sgsi(id):
    doc = PoliticaSGSI.query.get_or_404(id)
    titulo = doc.titulo
    if doc.nombre_archivo:
        try:
            s3_client.delete_object(Bucket=doc.ruta_minio, Key=doc.nombre_archivo)
        except Exception as e:
            print(f"Error borrando de S3: {e}")
    db.session.delete(doc)
    db.session.commit()
    registrar_actividad('Eliminar documento', 'documentos', f'Documento eliminado: {titulo}')
    flash('Documento eliminado correctamente.', 'success')
    return redirect(url_for('documentos.listar_documentos_generados'))


@documentos_bp.route('/documentos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_politica(id):
    doc = PoliticaSGSI.query.get_or_404(id)

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        doc.titulo = titulo
        doc.codigo = request.form.get('codigo')
        doc.version = request.form.get('version')

        datos_actualizados = {
            'tipo_documento': doc.tipo.upper(),
            'titulo': titulo,
            'codigo': doc.codigo,
            'objetivo': request.form.get('objetivo'),
            'alcance': request.form.get('alcance'),
            'responsables': request.form.get('responsables'),
            'marco_legal': request.form.get('marco_legal'),
            'lineamientos': request.form.get('lineamientos'),
            'version': doc.version,
            'fecha': datetime.now().strftime('%d/%m/%Y'),
            'desc_cambio': request.form.get('desc_cambio'),
            'elaboro': {'nombre': request.form.get('elaboro_nombre'), 'cargo': request.form.get('elaboro_cargo')},
            'reviso': {'nombre': request.form.get('reviso_nombre'), 'cargo': request.form.get('reviso_cargo')},
            'aprobo': {'nombre': request.form.get('aprobo_nombre'), 'cargo': request.form.get('aprobo_cargo')},
            'autor': current_user.username
        }

        if 'logo_empresa' in request.files:
            file = request.files['logo_empresa']
            if file and file.filename != '':
                image_bytes = file.read()
                logo_b64 = base64.b64encode(image_bytes).decode('utf-8')
                mime = "image/png" if file.filename.lower().endswith('png') else "image/jpeg"
                datos_actualizados['logo'] = f"data:{mime};base64,{logo_b64}"

        html = render_template('plantilla_politica_pdf.html', data=datos_actualizados)
        pdf_buffer = BytesIO()
        pisa.CreatePDF(html, dest=pdf_buffer)
        pdf_buffer.seek(0)
        filename = f"{doc.tipo[:3].upper()}_{secure_filename(doc.codigo)}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        try:
            s3_client.upload_fileobj(pdf_buffer, S3_BUCKET_DOCS, filename, ExtraArgs={'ContentType': PDF_MIME_TYPE})
            doc.nombre_archivo = filename
            datos_para_bd = datos_actualizados.copy()
            datos_para_bd.pop('logo', None)
            doc.datos_formulario = json.dumps(datos_para_bd)
            db.session.commit()
            flash('Documento actualizado correctamente.', 'success')
            return redirect(url_for('documentos.listar_documentos_generados'))
        except Exception as e:
            flash(f'Error al actualizar: {e}', 'danger')

    datos_previos = {}
    if doc.datos_formulario:
        try:
            datos_previos = json.loads(doc.datos_formulario)
        except Exception as e:
            print(f"Error leyendo JSON: {e}")

    return render_template('crear_politica.html',
                           tipo_doc=doc.tipo,
                           fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                           data=datos_previos,
                           es_edicion=True,
                           doc_id=doc.id)


@documentos_bp.route('/documentos/descargar-doc/<int:id>')
@login_required
def descargar_documento_sgsi(id):
    doc = PoliticaSGSI.query.get_or_404(id)
    try:
        file_obj = s3_client.get_object(Bucket=doc.ruta_minio, Key=doc.nombre_archivo)
        return send_file(
            file_obj['Body'],
            download_name=doc.nombre_archivo,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"S3 Error: {e}")
        flash('Archivo no encontrado en el servidor.', 'danger')
        return redirect(url_for('documentos.listar_documentos_generados'))
