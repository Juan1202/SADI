"""
Una prueba por cada defecto funcional B1-B6 de CONTEXTO_SADI.md 10.1.

Cada prueba falla contra el codigo original y pasa con la correccion.
"""
from datetime import date

from models import db, Evaluacion, PlanTratamiento, ResultadoControl
from routes.auditoria import _calculate_audit_score, _calculate_max_audit_risk
from routes.dashboard import _calculate_domain_averages
from escalas import madurez_desde_riesgo

from conftest import autenticar, crear_auditoria


# --- B1 ---------------------------------------------------------------------

def test_b1_el_grafico_gap_por_dominios_deja_de_devolver_ceros(app, auditor, controles):
    """
    El dominio es el primer segmento del codigo ("5.15" -> 5). Tomando el
    segundo se obtenia "15", que no existe en el mapa de dominios, y las cuatro
    posiciones del grafico quedaban en cero.
    """
    _, resultados = crear_auditoria(auditor, controles, [
        ('5.15', 1, 1),   # riesgo 1  -> madurez 5.00
        ('6.3', 3, 3),    # riesgo 9  -> madurez 3.20
        ('7.2', 2, 2),    # riesgo 4  -> madurez 4.18
        ('8.8', 5, 5),    # riesgo 25 -> madurez 1.00
    ])
    for resultado in resultados.values():
        riesgo = max(p.probabilidad * p.impacto for p in resultado.preguntas)
        resultado.nivel_riesgo_max = riesgo
        resultado.nivel_madurez = madurez_desde_riesgo(riesgo)
    db.session.commit()

    promedios = _calculate_domain_averages()

    assert promedios != [0, 0, 0, 0], 'el grafico GAP por dominios sigue en cero'
    assert promedios == [5.0, 3.2, 4.18, 1.0]


def test_b1_los_controles_sin_evaluar_no_arrastran_el_promedio(app, auditor, controles):
    _, resultados = crear_auditoria(auditor, controles, [('5.15', 1, 1)])
    resultado = resultados['5.15']
    resultado.nivel_riesgo_max = 1
    resultado.nivel_madurez = 5.0
    # Un control del mismo dominio incluido en el alcance pero sin evaluar.
    db.session.add(ResultadoControl(
        evaluacion_id=resultado.evaluacion_id,
        control_id=controles['5.15'].id,
        nivel_riesgo_max=0, nivel_madurez=0.0,
    ))
    db.session.commit()

    assert _calculate_domain_averages()[0] == 5.0


# --- B2 ---------------------------------------------------------------------

def test_b2_finalizar_una_auditoria_ya_no_pone_el_puntaje_en_cero(app, auditor, controles):
    """
    _calculate_audit_score leia respuesta_bool y respuesta_texto, que el flujo
    de riesgos nunca escribe, de modo que toda auditoria finalizada quedaba en
    0.0 y el tablero la mostraba como NO CUMPLE.
    """
    evaluacion, _ = crear_auditoria(auditor, controles, [
        ('5.15', 1, 2),   # riesgo 2  -> madurez 4.50
        ('8.8', 3, 4),    # riesgo 12 -> madurez 2.69
    ])

    score = _calculate_audit_score(evaluacion)

    assert score > 0.0, 'el puntaje de la auditoria sigue calculandose en cero'
    assert score == round((4.50 + 2.69) / 2, 2)


def test_b2_el_riesgo_maximo_se_reporta_en_su_propia_escala(app, auditor, controles):
    evaluacion, _ = crear_auditoria(auditor, controles, [('5.15', 1, 2), ('8.8', 5, 4)])

    assert _calculate_max_audit_risk(evaluacion) == 20
    assert _calculate_audit_score(evaluacion) <= 5.0


def test_b2_una_auditoria_sin_hallazgos_no_divide_por_cero(app, auditor, controles):
    evaluacion = Evaluacion(codigo='AUD-VACIA', titulo='[DEMO] Sin hallazgos',
                            evaluador=auditor.username, user_id=auditor.id)
    db.session.add(evaluacion)
    db.session.commit()

    assert _calculate_audit_score(evaluacion) == 0.0
    assert _calculate_max_audit_risk(evaluacion) == 0


# --- B3 ---------------------------------------------------------------------

def test_b3_la_evidencia_del_detalle_apunta_a_minio_y_no_a_static(
        app, client, administrador, controles):
    """El enlace debe resolverse por auditoria.download_file, que lee de MinIO."""
    evaluacion, resultados = crear_auditoria(administrador, controles, [('8.8', 3, 3)],
                                             estado='Finalizada')
    pregunta = resultados['8.8'].preguntas[0]
    pregunta.archivo_evidencia = 'AUD-TEST_8.8_P0_informe_pentest.pdf'
    db.session.commit()

    autenticar(client, administrador)
    html = client.get('/auditoria/%d' % evaluacion.id).get_data(as_text=True)

    assert '/uploads/AUD-TEST_8.8_P0_informe_pentest.pdf' in html
    assert '/static/uploads/' not in html


# --- B4 ---------------------------------------------------------------------

def test_b4_el_plan_de_tratamiento_guarda_proceso_activos_y_tipo_de_control(
        app, client, auditor, controles):
    """Los tres campos viajaban en el formulario pero el manejador los ignoraba."""
    _, resultados = crear_auditoria(auditor, controles, [('8.8', 4, 4)])
    resultado = resultados['8.8']

    autenticar(client, auditor)
    client.post('/tratamiento/resultado/%d' % resultado.id, data={
        'descripcion': 'No se ejecutan pruebas de vulnerabilidad periodicas.',
        'nivel_riesgo': '16',
        'proceso': 'Gestion de TI',
        'activos': 'Servidor de aplicaciones, base de datos de clientes',
        'estrategia': 'Mitigar',
        'acciones': 'Contratar escaneo trimestral autenticado.',
        'tipo_control': 'Detective',
        'responsable': 'Jefe de TI',
        'estado': 'En Progreso',
        'plazo': '2026-08-31',
    }, follow_redirects=False)

    plan = PlanTratamiento.query.filter_by(resultado_control_id=resultado.id).first()
    assert plan is not None
    assert plan.proceso_negocio == 'Gestion de TI'
    assert plan.activos_relacionados == 'Servidor de aplicaciones, base de datos de clientes'
    assert plan.tipo_control == 'Detective'
    assert plan.plazo == date(2026, 8, 31)


# --- B5 ---------------------------------------------------------------------

def test_b5_el_analisis_de_riesgos_no_muestra_auditorias_de_la_papelera(
        app, client, administrador, controles):
    crear_auditoria(administrador, controles, [('5.15', 5, 5)],
                    codigo='AUD-PAPELERA', eliminado=True,
                    titulo='[DEMO] Auditoria eliminada')
    crear_auditoria(administrador, controles, [('8.8', 4, 3)],
                    codigo='AUD-ACTIVA', titulo='[DEMO] Auditoria activa')

    autenticar(client, administrador)
    html = client.get('/analisis-riesgos').get_data(as_text=True)

    assert 'AUD-ACTIVA' in html
    assert 'AUD-PAPELERA' not in html, 'siguen apareciendo riesgos de la papelera'


def test_b5_un_auditor_no_ve_los_riesgos_de_otro_propietario(
        app, client, auditor, administrador, controles):
    crear_auditoria(administrador, controles, [('5.15', 5, 5)],
                    codigo='AUD-DE-OTRO', titulo='[DEMO] De otro usuario')
    crear_auditoria(auditor, controles, [('8.8', 4, 3)],
                    codigo='AUD-PROPIA', titulo='[DEMO] Propia')

    autenticar(client, auditor)
    html = client.get('/analisis-riesgos').get_data(as_text=True)

    assert 'AUD-PROPIA' in html
    assert 'AUD-DE-OTRO' not in html


# --- B6 ---------------------------------------------------------------------

def test_b6_el_analisis_de_riesgos_enlaza_al_plan_que_desbloquea_el_cierre(
        app, client, administrador, controles):
    """
    Enlazaba al plan generico por control (/tratamiento/control/<id>), que no
    marca riesgo_tratado y por tanto no desbloquea la finalizacion.
    """
    _, resultados = crear_auditoria(administrador, controles, [('8.8', 4, 4)])
    resultado = resultados['8.8']

    autenticar(client, administrador)
    html = client.get('/analisis-riesgos').get_data(as_text=True)

    assert '/tratamiento/resultado/%d' % resultado.id in html
    assert '/tratamiento/control/%d' % controles['8.8'].id not in html


def test_b6_el_plan_creado_desde_el_analisis_marca_el_riesgo_como_tratado(
        app, client, auditor, controles):
    _, resultados = crear_auditoria(auditor, controles, [('8.8', 4, 4)])
    resultado = resultados['8.8']

    autenticar(client, auditor)
    client.post('/tratamiento/resultado/%d' % resultado.id, data={
        'descripcion': 'Riesgo alto sin tratamiento.', 'nivel_riesgo': '16',
        'proceso': 'Gestion de TI', 'activos': 'Servidores',
        'estrategia': 'Mitigar', 'acciones': 'Plan ejecutado y verificado.',
        'tipo_control': 'Correctivo', 'responsable': 'Jefe de TI',
        'estado': 'Cerrado', 'plazo': '2026-08-31',
    })

    db.session.refresh(resultado)
    assert resultado.riesgo_tratado is True
