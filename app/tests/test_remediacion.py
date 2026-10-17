"""
Sugerencias de remediacion basadas en NIST SP 800-53 Rev. 5 (app/remediacion.py).

Responde a la oportunidad de mejora de la evaluacion JCUN 2026: que el plan de
tratamiento no parta de una hoja en blanco, sino de controles NIST trazables.
"""
import json

from models import db
from remediacion import base_conocimiento, borrador_acciones, sugerir, tipo_control

from conftest import autenticar, crear_auditoria


# --- Base de conocimiento -------------------------------------------------

def test_la_base_cubre_91_de_los_93_controles_del_anexo_a():
    mapeo = base_conocimiento()['mapeo']
    assert len(mapeo) == 91
    # Los dos sin correspondencia publicada por NIST en OLIR 155.
    assert '7.6' not in mapeo
    assert '8.34' not in mapeo


def test_toda_correspondencia_apunta_a_un_control_nist_existente():
    datos = base_conocimiento()
    for iso, lista in datos['mapeo'].items():
        assert lista, iso
        for nist in lista:
            assert nist in datos['controles_nist'], (iso, nist)
            assert datos['controles_nist'][nist]['enunciado'], nist


def test_la_base_declara_su_procedencia():
    fuente = base_conocimiento()['fuente']
    assert 'OLIR' in fuente['mapeo']
    assert len(fuente['mapeo_sha256']) == 64
    assert len(fuente['catalogo_sha256']) == 64


def test_correspondencias_conocidas():
    mapeo = base_conocimiento()['mapeo']
    assert {'SC-12', 'SC-13'} <= set(mapeo['8.24'])          # criptografia
    assert {'RA-5', 'SI-2'} <= set(mapeo['8.8'])              # vulnerabilidades
    assert {'AC-3', 'AC-6'} <= set(mapeo['5.15'])             # control de acceso


# --- Motor de sugerencias -------------------------------------------------

def test_mas_riesgo_mas_profundidad_y_menos_plazo():
    baja = sugerir('5.2', 2)
    alta = sugerir('5.2', 12)
    extrema = sugerir('5.2', 25)
    assert len(baja['sugerencias']) < len(alta['sugerencias']) < len(extrema['sugerencias'])
    assert baja['plazo_dias'] > alta['plazo_dias'] > extrema['plazo_dias']
    assert extrema['prioridad'] == 'Inmediata'


def test_estrategias_siguen_la_metodologia_de_sadi():
    assert sugerir('8.8', 2)['estrategias'] == ['Aceptar']
    assert 'Mitigar' in sugerir('8.8', 6)['estrategias']
    alta = sugerir('8.8', 12)
    assert 'Aceptar' not in alta['estrategias']
    assert alta['estrategia_sugerida'] == 'Mitigar'


def test_prioriza_controles_especificos_sobre_politicas_genericas():
    sugerencias = [s['id'] for s in sugerir('5.15', 20)['sugerencias']]
    # AC-1 (politica y procedimientos) es el mas generico: va al final.
    assert sugerencias[-1] == 'AC-1'
    assert sugerencias.index('AC-3') < sugerencias.index('AC-1')


def test_acepta_codigo_con_prefijo_a():
    assert sugerir('A.8.24', 9)['control_iso'] == '8.24'
    assert sugerir('A.8.24', 9)['sugerencias']


def test_control_sin_correspondencia_no_inventa_sugerencias():
    resultado = sugerir('8.34', 16)
    assert resultado['sin_correspondencia'] is True
    assert resultado['sugerencias'] == []
    assert '27002' in borrador_acciones(resultado)


def test_tipo_de_control_segun_funcion_nist():
    assert tipo_control('SI-4') == 'Detective'
    assert tipo_control('AU-12') == 'Detective'
    assert tipo_control('IR-4(13)') == 'Correctivo'
    assert tipo_control('SI-2') == 'Correctivo'
    assert tipo_control('AC-3') == 'Preventivo'


def test_borrador_cita_cada_control_sugerido():
    sugerencia = sugerir('8.8', 15)
    texto = borrador_acciones(sugerencia)
    for s in sugerencia['sugerencias']:
        assert s['id'] in texto
    assert '90 días' in texto


# --- Integracion con la aplicacion ----------------------------------------

def test_el_plan_de_tratamiento_muestra_las_sugerencias(app, client, auditor, controles):
    _, resultados = crear_auditoria(auditor, controles, [('8.8', 4, 4)], codigo='AUD-REMED')
    resultado = resultados['8.8']
    resultado.nivel_riesgo_max = 16
    db.session.commit()

    autenticar(client, auditor)
    cuerpo = client.get('/tratamiento/resultado/%d' % resultado.id).get_data(as_text=True)

    assert 'Sugerencias de remediación' in cuerpo
    assert 'RA-5' in cuerpo
    assert 'Aplicar al plan' in cuerpo
    assert 'Zona <strong>Alta</strong>' in cuerpo


def test_api_de_remediacion(app, client, auditor, controles):
    autenticar(client, auditor)
    respuesta = client.get('/api/remediacion/8.8?riesgo=20')
    assert respuesta.status_code == 200
    datos = json.loads(respuesta.get_data(as_text=True))
    assert datos['zona'] == 'Extrema'
    assert any(s['id'] == 'RA-5' for s in datos['sugerencias'])
    assert 'RA-5' in datos['borrador_acciones']


def test_api_de_remediacion_exige_sesion(app, client, controles):
    respuesta = client.get('/api/remediacion/8.8?riesgo=20')
    assert respuesta.status_code in (302, 401)


def test_api_de_remediacion_control_inexistente(app, client, auditor, controles):
    autenticar(client, auditor)
    assert client.get('/api/remediacion/9.99?riesgo=20').status_code == 404
