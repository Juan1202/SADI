from functools import wraps
from flask import abort, request
from flask_login import current_user

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'xls', 'docx', 'doc'}
PDF_MIME_TYPE = 'application/pdf'
DOMINIO_FISICO = 'Físico'
DOMINIO_TECNOLOGICO = 'Tecnológico'
DOMINIO_ORGANIZACIONAL = 'Organizacional'
DOMINIO_PERSONAS = 'Personas'

# Roles válidos del sistema (en minúsculas)
ROL_ADMINISTRADOR = 'administrador'
ROL_AUDITOR       = 'auditor'
ROL_CONSULTOR     = 'consultor'
ROL_LECTOR        = 'lector'
ROLES_VALIDOS     = {ROL_ADMINISTRADOR, ROL_AUDITOR, ROL_CONSULTOR, ROL_LECTOR}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Acceso exclusivo para administradores."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROL_ADMINISTRADOR:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorador que permite el acceso solo si current_user.role está en `roles`.
    Uso: @role_required('administrador', 'auditor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def registrar_actividad(accion, modulo, detalle=''):
    """
    Registra una acción del usuario autenticado en la tabla registros_actividad.
    Solo se llama en operaciones de escritura (crear, editar, eliminar).
    """
    try:
        from models import db, RegistroActividad  # import lazy para evitar circularidad
        ip = request.remote_addr
        entrada = RegistroActividad(
            user_id=current_user.id,
            accion=accion,
            modulo=modulo,
            detalle=detalle[:500] if detalle else '',
            ip_address=ip,
        )
        db.session.add(entrada)
        db.session.commit()
    except Exception:
        pass  # El log nunca debe romper el flujo principal


def validar_seguridad_password(password):
    """Retorna (True, None) si es válida o (False, mensaje) si no."""
    if not password or len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    return True, None


# Prefijo que riesgos.py antepone al guardar un adjunto:
# "{codigo_auditoria}_{codigo_control}_P{indice}_{nombre_original}".
PARTES_PREFIJO_EVIDENCIA = 3


def nombre_original_evidencia(almacenado):
    """
    Nombre con el que el auditor subio un adjunto, sin el prefijo interno.

    Se deja igual lo que no traiga el prefijo, para no mutilar los adjuntos
    cargados antes de que existiera.
    """
    if not almacenado:
        return ''
    partes = almacenado.split('_')
    if len(partes) <= PARTES_PREFIJO_EVIDENCIA:
        return almacenado
    if not partes[PARTES_PREFIJO_EVIDENCIA - 1].startswith('P'):
        return almacenado
    return '_'.join(partes[PARTES_PREFIJO_EVIDENCIA:])
