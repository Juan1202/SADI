"""
Fixtures comunes de la suite de SADI.

Las pruebas corren dentro del contenedor web contra una base PostgreSQL
separada (sadi_test), para no tocar los datos del caso de demostracion y
para usar el mismo motor que produccion.

    docker compose exec web python -m pytest tests -v
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app as flask_app  # noqa: E402
from models import (  # noqa: E402
    CategoriaDiagnostico,
    Control,
    Diagnostico,
    Evaluacion,
    PlanTratamiento,
    PreguntaControl,
    PreguntaDiagnostico,
    RespuestaDiagnostico,
    ResultadoControl,
    Usuario,
    db,
)
from utils import ROL_ADMINISTRADOR, ROL_AUDITOR  # noqa: E402

TEST_DATABASE_URL = os.environ.get(
    'TEST_DATABASE_URL',
    (os.environ.get('DATABASE_URL') or '').rsplit('/', 1)[0] + '/sadi_test',
)

# De hijos a padres: el orden en que se pueden borrar sin violar claves foraneas.
# Se borran de hijo a padre: al reves las claves foraneas rechazan el borrado.
MODELOS_TRANSACCIONALES = (PlanTratamiento, PreguntaControl, ResultadoControl, Evaluacion,
                          RespuestaDiagnostico, PreguntaDiagnostico, Diagnostico,
                          CategoriaDiagnostico)


@pytest.fixture(scope='session')
def app():
    flask_app.config.update(
        SQLALCHEMY_DATABASE_URI=TEST_DATABASE_URL,
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    # Flask-SQLAlchemy 3.1 cachea el engine por aplicacion; hay que reconstruirlo
    # para que tome la URI de pruebas en vez de la de produccion.
    db._app_engines.pop(flask_app, None)
    flask_app.extensions.pop('sqlalchemy', None)
    db.init_app(flask_app)

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def contexto(app):
    """
    Un contexto de aplicacion por prueba.

    Debe ser por prueba y no de sesion: Flask solo empuja un contexto nuevo por
    peticion cuando no hay uno activo de la misma aplicacion, asi que un
    contexto compartido haria que `g` -y con el, el usuario que cachea
    Flask-Login- se arrastrara de una prueba a la siguiente.
    """
    with app.app_context():
        yield
        db.session.rollback()
        for modelo in MODELOS_TRANSACCIONALES:
            modelo.query.delete()
        db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auditor(app):
    return _usuario('auditor_test', ROL_AUDITOR)


@pytest.fixture
def administrador(app):
    return _usuario('admin_test', ROL_ADMINISTRADOR)


@pytest.fixture
def controles(app):
    """Un control por dominio, con los codigos reales del Anexo A."""
    datos = [
        ('5.15', 'Control de acceso', 'Organizacional'),
        ('6.3', 'Concienciacion en seguridad de la informacion', 'Personas'),
        ('7.2', 'Entrada fisica', 'Fisico'),
        ('8.8', 'Gestion de vulnerabilidades tecnicas', 'Tecnologico'),
    ]
    creados = {}
    for codigo, nombre, dominio in datos:
        ctrl = Control.query.filter_by(codigo=codigo).first()
        if not ctrl:
            ctrl = Control(codigo=codigo, nombre=nombre, descripcion=nombre, dominio=dominio)
            db.session.add(ctrl)
        creados[codigo] = ctrl
    db.session.commit()
    return creados


def _usuario(username, role):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        usuario = Usuario(username=username, role=role, is_active=True)
        usuario.set_password('Demo.Test.2026')
        db.session.add(usuario)
        db.session.commit()
    return usuario


def autenticar(client, usuario):
    """Deja la sesion de Flask-Login lista sin pasar por el formulario."""
    with client.session_transaction() as sesion:
        sesion['_user_id'] = str(usuario.id)
        sesion['_fresh'] = True
    return client


def crear_auditoria(usuario, controles, hallazgos, estado='En Proceso', eliminado=False,
                    codigo='AUD-TEST', titulo='[DEMO] Auditoria de prueba'):
    """
    Crea una auditoria con sus hallazgos.

    `hallazgos` es una lista de tuplas (codigo_control, probabilidad, impacto).
    """
    evaluacion = Evaluacion(
        codigo=codigo, titulo=titulo, evaluador=usuario.username,
        user_id=usuario.id, estado=estado, eliminado=eliminado,
    )
    db.session.add(evaluacion)
    db.session.flush()

    resultados = {}
    for codigo_control, prob, imp in hallazgos:
        control = controles[codigo_control]
        resultado = resultados.get(codigo_control)
        if resultado is None:
            resultado = ResultadoControl(
                evaluacion_id=evaluacion.id, control_id=control.id,
            )
            db.session.add(resultado)
            db.session.flush()
            resultados[codigo_control] = resultado
        db.session.add(PreguntaControl(
            resultado_control_id=resultado.id,
            texto_pregunta='Criterio evaluado de %s' % codigo_control,
            peso_porcentaje=0, tipo_respuesta='riesgo',
            probabilidad=prob, impacto=imp, nivel_riesgo=prob * imp,
            hallazgo='Hallazgo de prueba en %s' % codigo_control,
        ))
    db.session.commit()
    return evaluacion, resultados
