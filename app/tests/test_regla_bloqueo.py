"""
Regla de negocio central de SADI: no se finaliza una auditoria mientras exista
un hallazgo con nivel de riesgo >= 9 cuyo plan de tratamiento no este cerrado.

Es la regla que el articulo IEEE describe como control de cierre, asi que
conviene tenerla cubierta de forma explicita y no solo a traves de los defectos.
"""
from models import db, Evaluacion

from conftest import autenticar, crear_auditoria


def _finalizar(client, evaluacion):
    return client.post('/auditoria/finalizar',
                       data={'codigo_auditoria_final': evaluacion.codigo},
                       follow_redirects=True)


def test_no_se_finaliza_con_un_riesgo_alto_sin_tratar(app, client, auditor, controles):
    evaluacion, _ = crear_auditoria(auditor, controles, [
        ('5.15', 1, 2),   # riesgo 2, no bloquea
        ('8.8', 3, 3),    # riesgo 9, bloquea
    ], codigo='AUD-BLOQUEO')

    autenticar(client, auditor)
    respuesta = _finalizar(client, evaluacion)

    db.session.refresh(evaluacion)
    assert evaluacion.estado == 'En Proceso'
    assert evaluacion.fecha_fin is None
    cuerpo = respuesta.get_data(as_text=True)
    assert 'No se puede finalizar' in cuerpo
    assert '8.8' in cuerpo


def test_al_cerrar_el_plan_la_auditoria_se_puede_finalizar(app, client, auditor, controles):
    evaluacion, resultados = crear_auditoria(auditor, controles, [('8.8', 3, 3)],
                                             codigo='AUD-DESBLOQUEO')
    autenticar(client, auditor)
    assert _finalizar(client, evaluacion) is not None
    db.session.refresh(evaluacion)
    assert evaluacion.estado == 'En Proceso', 'la regla de bloqueo no actuo'

    # El desbloqueo solo ocurre por el flujo normal: cerrar el plan.
    client.post('/tratamiento/resultado/%d' % resultados['8.8'].id, data={
        'descripcion': 'Sin escaneo de vulnerabilidades periodico.',
        'nivel_riesgo': '9', 'proceso': 'Gestion de TI', 'activos': 'Servidores',
        'estrategia': 'Mitigar', 'acciones': 'Escaneo trimestral contratado y verificado.',
        'tipo_control': 'Detective', 'responsable': 'Jefe de TI',
        'estado': 'Cerrado', 'plazo': '2026-08-31',
    })

    _finalizar(client, evaluacion)

    db.session.refresh(evaluacion)
    assert evaluacion.estado == 'Finalizada'
    assert evaluacion.fecha_fin is not None
    assert evaluacion.score_promedio > 0.0
    assert evaluacion.riesgo_maximo == 9


def test_una_auditoria_solo_con_riesgos_moderados_se_finaliza_sin_plan(
        app, client, auditor, controles):
    evaluacion, _ = crear_auditoria(auditor, controles, [
        ('5.15', 2, 2),   # riesgo 4
        ('7.2', 2, 4),    # riesgo 8
    ], codigo='AUD-SIN-BLOQUEO')

    autenticar(client, auditor)
    _finalizar(client, evaluacion)

    db.session.refresh(evaluacion)
    assert evaluacion.estado == 'Finalizada'
    assert evaluacion.riesgo_maximo == 8


def test_un_plan_abierto_no_desbloquea_el_cierre(app, client, auditor, controles):
    evaluacion, resultados = crear_auditoria(auditor, controles, [('8.8', 5, 5)],
                                             codigo='AUD-PLAN-ABIERTO')
    autenticar(client, auditor)
    client.post('/tratamiento/resultado/%d' % resultados['8.8'].id, data={
        'descripcion': 'Riesgo extremo identificado.', 'nivel_riesgo': '25',
        'proceso': 'Gestion de TI', 'activos': 'Servidores',
        'estrategia': 'Mitigar', 'acciones': 'Plan formulado, aun sin ejecutar.',
        'tipo_control': 'Preventivo', 'responsable': 'Jefe de TI',
        'estado': 'En Progreso', 'plazo': '2026-12-31',
    })

    _finalizar(client, evaluacion)

    db.session.refresh(evaluacion)
    assert evaluacion.estado == 'En Proceso'
    assert resultados['8.8'].riesgo_tratado is False


def test_la_ruta_de_cierre_de_ciclo_tambien_respeta_la_regla(app, client, auditor, controles):
    """Hallazgo de la revision previa a JCUN 2026: /auditoria/cerrar/<id> omitia la regla."""
    evaluacion, _ = crear_auditoria(auditor, controles, [('8.8', 4, 4)], codigo='AUD-CIERRE-CICLO')
    autenticar(client, auditor)
    respuesta = client.post('/auditoria/cerrar/%d' % evaluacion.id, follow_redirects=True)

    db.session.refresh(evaluacion)
    assert evaluacion.estado != 'Finalizada'
    assert 'No se puede finalizar' in respuesta.get_data(as_text=True)


def test_el_mensaje_de_bloqueo_nombra_el_peor_riesgo(app, client, auditor, controles):
    evaluacion, _ = crear_auditoria(auditor, controles, [
        ('5.15', 3, 3),   # riesgo 9
        ('8.8', 5, 4),    # riesgo 20: el que debe nombrarse
    ], codigo='AUD-PEOR')
    autenticar(client, auditor)
    cuerpo = _finalizar(client, evaluacion).get_data(as_text=True)
    assert 'El control 8.8 tiene Riesgo ALTO/EXTREMO (20)' in cuerpo
