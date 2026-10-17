import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, Usuario
from extensions import init_s3_bucket

app = Flask(__name__)

# --- CONFIGURACIÓN GENERAL ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- INICIALIZACIÓN DE EXTENSIONES ---
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# --- REGISTRO DE BLUEPRINTS ---
from utils import nombre_original_evidencia

# Las plantillas mostraban el nombre de un adjunto recortandolo a mano; el
# filtro deja esa regla en un solo sitio, con pruebas.
app.add_template_filter(nombre_original_evidencia, 'nombre_evidencia')

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.usuarios import usuarios_bp
from routes.controles import controles_bp
from routes.auditoria import auditoria_bp
from routes.riesgos import riesgos_bp
from routes.documentos import documentos_bp
from routes.diagnostico import diagnostico_bp
from routes.admin import admin_bp
from routes.info import info_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(controles_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(riesgos_bp)
app.register_blueprint(documentos_bp)
app.register_blueprint(diagnostico_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(info_bp)


# --- ERROR HANDLERS ---
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


# --- INICIALIZACIÓN DE BASE DE DATOS Y S3 ---
with app.app_context():
    init_s3_bucket()
    try:
        db.create_all()
        print("Tablas verificadas en PostgreSQL")
    except Exception as e:
        print(f"Error creando tablas: {e}")


if __name__ == '__main__':
    # S2: el modo depuracion (consola interactiva de Werkzeug) ya no esta fijo en
    # el codigo; solo se activa si el entorno lo pide de forma explicita.
    modo_depuracion = os.environ.get('FLASK_DEBUG', '0') == '1'
    # 0.0.0.0 es necesario dentro del contenedor; docker-compose publica el
    # puerto solo en 127.0.0.1.
    app.run(host='0.0.0.0', port=5000, debug=modo_depuracion)  # nosec B104
