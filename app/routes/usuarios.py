from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Usuario, Evaluacion, RegistroActividad
from utils import admin_required, role_required, registrar_actividad, validar_seguridad_password, ROL_ADMINISTRADOR

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/usuarios')
@admin_required
def gestion_usuarios():
    usuarios_lista = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios_lista)


@usuarios_bp.route('/usuarios/crear', methods=['POST'])
@role_required(ROL_ADMINISTRADOR)
def crear_usuario():
    username = request.form.get('username')
    password = request.form.get('password')
    role     = request.form.get('role')
    email    = request.form.get('email')
    cargo    = request.form.get('cargo')

    es_valida, mensaje = validar_seguridad_password(password)
    if not es_valida:
        flash(mensaje, 'danger')
        return redirect(url_for('usuarios.gestion_usuarios'))

    if Usuario.query.filter_by(username=username).first():
        flash('El usuario ya existe.', 'danger')
    else:
        new_user = Usuario(username=username, role=role, email=email, cargo=cargo, is_active=True)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        registrar_actividad('Crear usuario', 'usuarios', f'Usuario creado: {username} (rol: {role})')
        flash('Usuario creado.', 'success')
    return redirect(url_for('usuarios.gestion_usuarios'))


@usuarios_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR)
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id or usuario.username == 'admin_sadi':
        flash('No puedes eliminar este usuario.', 'danger')
    else:
        nombre = usuario.username
        db.session.delete(usuario)
        db.session.commit()
        registrar_actividad('Eliminar usuario', 'usuarios', f'Usuario eliminado: {nombre}')
        flash('Usuario eliminado.', 'success')
    return redirect(url_for('usuarios.gestion_usuarios'))


@usuarios_bp.route('/usuarios/ver/<int:id>')
@admin_required
def ver_usuario_detalle(id):
    usuario   = Usuario.query.get_or_404(id)
    auditorias = Evaluacion.query.filter_by(user_id=usuario.id).order_by(Evaluacion.fecha_creacion.desc()).all()
    page       = request.args.get('page', 1, type=int)
    actividades = (RegistroActividad.query
                   .filter_by(user_id=usuario.id)
                   .order_by(RegistroActividad.fecha.desc())
                   .paginate(page=page, per_page=15, error_out=False))
    return render_template('ver_usuario.html', usuario=usuario, auditorias=auditorias, actividades=actividades)


@usuarios_bp.route('/usuarios/editar_guardar/<int:id>', methods=['POST'])
@admin_required
def guardar_edicion_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.email = request.form.get('email')
    usuario.cargo = request.form.get('cargo')
    usuario.role  = request.form.get('role')

    nueva_pass = request.form.get('password')
    if nueva_pass and nueva_pass.strip():
        es_valida, mensaje = validar_seguridad_password(nueva_pass)
        if not es_valida:
            flash(f"Error al cambiar contraseña: {mensaje}", 'danger')
            return redirect(url_for('usuarios.ver_usuario_detalle', id=id))
        usuario.set_password(nueva_pass)

    db.session.commit()
    registrar_actividad('Editar usuario', 'usuarios', f'Perfil editado: {usuario.username}')
    flash('Perfil actualizado.', 'success')
    return redirect(url_for('usuarios.ver_usuario_detalle', id=id))


@usuarios_bp.route('/usuarios/toggle/<int:id>', methods=['POST'])
@role_required(ROL_ADMINISTRADOR)
def toggle_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id or usuario.username == 'admin_sadi':
        return redirect(url_for('usuarios.gestion_usuarios'))
    usuario.activo = not usuario.activo
    db.session.commit()
    estado = 'activado' if usuario.activo else 'desactivado'
    registrar_actividad('Toggle usuario', 'usuarios', f'Usuario {estado}: {usuario.username}')
    return redirect(url_for('usuarios.gestion_usuarios'))


@usuarios_bp.route('/perfil')
@login_required
def mi_perfil():
    """Perfil propio: cualquier usuario ve sus datos y su historial."""
    page = request.args.get('page', 1, type=int)
    actividades = (RegistroActividad.query
                   .filter_by(user_id=current_user.id)
                   .order_by(RegistroActividad.fecha.desc())
                   .paginate(page=page, per_page=15, error_out=False))
    return render_template('perfil.html', usuario=current_user, actividades=actividades)
