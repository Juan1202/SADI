from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializamos la extensión de base de datos
db = SQLAlchemy()

# 1. El Catálogo Maestro de Controles
class Control(db.Model):
    __tablename__ = 'controles'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    dominio = db.Column(db.String(100), nullable=False)

    resultados = db.relationship('ResultadoControl', backref='control', cascade="all, delete-orphan")

class ResultadoControl(db.Model):
    __tablename__ = 'resultados_control'
    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('controles.id'), nullable=False)
    # DEPRECADO (ADR-011): se mantiene sincronizado con nivel_riesgo_max por
    # compatibilidad con plantillas antiguas. Usar los dos campos explicitos.
    nivel_cumplimiento = db.Column(db.Float, default=0.0)
    # Riesgo maximo de los hallazgos del control (1-25, ISO/IEC 27005).
    nivel_riesgo_max = db.Column(db.Integer, default=0)
    # Madurez derivada del riesgo (0-5). Ver app/escalas.py.
    nivel_madurez = db.Column(db.Float, default=0.0)
    evidencia_texto = db.Column(db.Text, nullable=True)
    evidencia_archivo = db.Column(db.String(255), nullable=True)
    riesgo_tratado = db.Column(db.Boolean, default=False)

class Evaluacion(db.Model):
    __tablename__ = 'evaluaciones'

    id = db.Column(db.Integer, primary_key=True)

    # Campos de Identificación
    codigo = db.Column(db.String(20), unique=True)
    titulo = db.Column(db.String(200))

    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    evaluador = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default='Iniciada')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=True)
    # Madurez promedio de la auditoria (0-5). Es lo que interpretan el tablero
    # y los informes PDF.
    score_promedio = db.Column(db.Float, default=0.0)
    # Riesgo maximo encontrado en la auditoria (1-25). Es lo que usa el KPI de
    # auditorias criticas del tablero.
    riesgo_maximo = db.Column(db.Integer, default=0)

    # Relación con Usuario
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    # Soft Delete (Papelera de reciclaje)
    eliminado = db.Column(db.Boolean, default=False)

    # Relación con resultados
    resultados = db.relationship('ResultadoControl', backref='evaluacion', cascade="all, delete-orphan")


class SoADocument(db.Model):
    __tablename__ = 'soa_documents'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    version = db.Column(db.String(10), default="1.0")
    dominio = db.Column(db.String(50), default="General")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='Borrador')

    # Relación
    detalles = db.relationship('SoADetalle', backref='documento', cascade="all, delete-orphan")

class SoADetalle(db.Model):
    __tablename__ = 'soa_detalles'

    id = db.Column(db.Integer, primary_key=True)
    soa_id = db.Column(db.Integer, db.ForeignKey('soa_documents.id'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('controles.id'), nullable=False)

    aplicable = db.Column(db.Boolean, default=True)
    justificacion = db.Column(db.Text, nullable=True)

    control = db.relationship('Control')

class PreguntaControl(db.Model):
    __tablename__ = 'preguntas_control'

    id = db.Column(db.Integer, primary_key=True)
    resultado_control_id = db.Column(db.Integer, db.ForeignKey('resultados_control.id'), nullable=False)

    texto_pregunta = db.Column(db.String(500), nullable=False)
    peso_porcentaje = db.Column(db.Integer, nullable=False)
    tipo_respuesta = db.Column(db.String(20), default='si_no')

    # Respuestas
    respuesta_bool = db.Column(db.Boolean, nullable=True)
    respuesta_texto = db.Column(db.Text, nullable=True)

    puntaje_obtenido = db.Column(db.Float, default=0.0)

    hallazgo = db.Column(db.Text, nullable=True)
    archivo_evidencia = db.Column(db.String(255), nullable=True)

    probabilidad = db.Column(db.Integer, default=1)
    impacto = db.Column(db.Integer, default=1)
    nivel_riesgo = db.Column(db.Integer, default=1)
    resultado = db.relationship('ResultadoControl', backref=db.backref('preguntas', lazy=True, cascade="all, delete-orphan"))


class PlanTratamiento(db.Model):
    __tablename__ = 'planes_tratamiento'

    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.Integer, db.ForeignKey('controles.id'), nullable=False)
    resultado_control_id = db.Column(db.Integer, db.ForeignKey('resultados_control.id'), nullable=True)

    # Campos de la Plantilla
    codigo_riesgo = db.Column(db.String(50))
    descripcion_riesgo = db.Column(db.Text)
    nivel_riesgo_inicial = db.Column(db.Integer)

    proceso_negocio = db.Column(db.String(100))
    activos_relacionados = db.Column(db.String(200))

    estrategia = db.Column(db.String(50))
    acciones = db.Column(db.Text)

    tipo_control = db.Column(db.String(50))
    responsable = db.Column(db.String(100))
    plazo = db.Column(db.Date)

    estado = db.Column(db.String(20), default='Abierto')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    control = db.relationship('Control', backref='planes')
    resultado_control = db.relationship('ResultadoControl', backref='plan_tratamiento', uselist=False)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='consultor')
    activo = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(120), nullable=True)
    cargo = db.Column(db.String(100), nullable=True)

    auditorias = db.relationship('Evaluacion', backref='usuario_rel', lazy=True)
    @property
    def is_active(self):
        return self.activo

    @is_active.setter
    def is_active(self, value):
        self.activo = value

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RegistroActividad(db.Model):
    __tablename__ = 'registros_actividad'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion     = db.Column(db.String(100), nullable=False)
    modulo     = db.Column(db.String(50),  nullable=False)
    detalle    = db.Column(db.Text,        nullable=True)
    ip_address = db.Column(db.String(45),  nullable=True)
    fecha      = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', backref='actividades')


class PoliticaSGSI(db.Model):
    __tablename__ = 'politicas_sgsi'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(10), default="1.0")

    tipo = db.Column(db.String(50), default="política")

    nombre_archivo = db.Column(db.String(255))
    ruta_minio = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    datos_formulario = db.Column(db.Text, nullable=True)
    usuario = db.relationship('Usuario', backref='politicas_politicas_creadas')


# ==========================================
#  MÓDULO DE DIAGNÓSTICO (GAP ANALYSIS)
# ==========================================

class CategoriaDiagnostico(db.Model):
    __tablename__ = 'categorias_diagnostico'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10))
    nombre = db.Column(db.String(100))

    preguntas = db.relationship('PreguntaDiagnostico', backref='categoria', cascade="all, delete-orphan")

class PreguntaDiagnostico(db.Model):
    __tablename__ = 'preguntas_diagnostico'
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_diagnostico.id'), nullable=False)
    requisito = db.Column(db.String(20))
    texto = db.Column(db.Text, nullable=False)

class Diagnostico(db.Model):
    __tablename__ = 'diagnosticos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estado = db.Column(db.String(20), default='En progreso')
    puntaje_global = db.Column(db.Float, default=0.0)

    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', backref='diagnosticos_realizados')

    respuestas = db.relationship('RespuestaDiagnostico', backref='diagnostico', cascade="all, delete-orphan")

class RespuestaDiagnostico(db.Model):
    __tablename__ = 'respuestas_diagnostico'
    id = db.Column(db.Integer, primary_key=True)
    diagnostico_id = db.Column(db.Integer, db.ForeignKey('diagnosticos.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_diagnostico.id'), nullable=False)

    valor = db.Column(db.String(20), default='no_evaluado')
    observacion = db.Column(db.Text, nullable=True)

    pregunta = db.relationship('PreguntaDiagnostico')
