from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from models import db, Control
from utils import role_required, registrar_actividad, ROL_ADMINISTRADOR, ROL_AUDITOR, DOMINIO_FISICO, DOMINIO_TECNOLOGICO, DOMINIO_ORGANIZACIONAL, DOMINIO_PERSONAS

controles_bp = Blueprint('controles', __name__)


@controles_bp.route('/controles')
@login_required
def listar_controles():
    page   = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    dominio = request.args.get('dominio', '')
    query  = Control.query
    if search:
        query = query.filter((Control.codigo.ilike(f'%{search}%')) | (Control.nombre.ilike(f'%{search}%')))
    if dominio:
        query = query.filter(Control.dominio == dominio)
    pagination = query.order_by(func.substr(Control.codigo, 1, 1), func.length(Control.codigo), Control.codigo).paginate(page=page, per_page=10)
    conteo = {d: Control.query.filter_by(dominio=d).count() for d in [DOMINIO_ORGANIZACIONAL, DOMINIO_PERSONAS, DOMINIO_FISICO, DOMINIO_TECNOLOGICO]}
    return render_template('controles.html', pagination=pagination, search=search, dominio=dominio, conteo=conteo)


@controles_bp.route('/controles/nuevo', methods=['POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def nuevo_control():
    control = Control(
        codigo=request.form.get('codigo'),
        nombre=request.form.get('nombre'),
        descripcion=request.form.get('descripcion'),
        dominio=request.form.get('dominio')
    )
    db.session.add(control)
    db.session.commit()
    registrar_actividad('Crear control', 'controles', f'Control creado: {control.codigo} — {control.nombre}')
    return redirect(url_for('controles.listar_controles'))


@controles_bp.route('/controles/eliminar/<int:id>')
@role_required(ROL_ADMINISTRADOR)
def eliminar_control(id):
    control = Control.query.get_or_404(id)
    codigo  = control.codigo
    db.session.delete(control)
    db.session.commit()
    registrar_actividad('Eliminar control', 'controles', f'Control eliminado: {codigo}')
    return redirect(url_for('controles.listar_controles'))


@controles_bp.route('/controles/editar/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR, ROL_AUDITOR)
def editar_control(id):
    control = Control.query.get_or_404(id)
    try:
        control.codigo      = request.form.get('codigo')
        control.nombre      = request.form.get('nombre')
        control.descripcion = request.form.get('descripcion')
        control.dominio     = request.form.get('dominio')
        db.session.commit()
        registrar_actividad('Editar control', 'controles', f'Control editado: {control.codigo}')
        flash('Control actualizado correctamente.', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Error: Ya existe un control con ese código. El código debe ser único.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error inesperado al editar el control: {str(e)}', 'danger')
    return redirect(url_for('controles.listar_controles'))
