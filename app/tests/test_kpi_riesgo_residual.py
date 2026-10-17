# -*- coding: utf-8 -*-
"""
El KPI "Estado de auditorias" del tablero debe medir riesgo RESIDUAL.

Antes leia Evaluacion.riesgo_maximo, que guarda el riesgo INHERENTE (el maximo
historico de los hallazgos). Con eso una auditoria que cerro todos sus planes
de riesgo alto seguia contando como critica, justo lo contrario de lo que
afirma la regla de bloqueo al dejarla finalizar.
"""
from models import db
from routes.dashboard import _calculate_risk_counts

from conftest import crear_auditoria


def _auditoria(usuario, controles, hallazgos, tratados=(), codigo='AUD-R'):
    """Crea una auditoria y marca como tratados los controles indicados."""
    evaluacion, resultados = crear_auditoria(
        usuario, controles, hallazgos, codigo=codigo,
        titulo='[DEMO] Auditoria %s' % codigo)
    # El riesgo inherente es lo que la aplicacion persiste al evaluar.
    evaluacion.riesgo_maximo = max(p * i for _, p, i in hallazgos)
    for codigo_control in tratados:
        resultados[codigo_control].riesgo_tratado = True
    db.session.commit()
    return evaluacion


def test_una_auditoria_con_sus_riesgos_altos_tratados_deja_de_ser_critica(
        app, auditor, controles):
    evaluacion = _auditoria(
        auditor, controles,
        [('5.15', 5, 5), ('6.3', 2, 2)],
        tratados=['5.15'])

    conteos, en_riesgo = _calculate_risk_counts([evaluacion])

    assert conteos['critico'] == 0, (
        'El riesgo 25 de 5.15 ya fue tratado; solo queda un riesgo residual de 4. '
        'Conteos: %s' % conteos)
    assert conteos['alerta'] == 1
    assert en_riesgo == []


def test_una_auditoria_con_un_riesgo_alto_sin_tratar_sigue_siendo_critica(
        app, auditor, controles):
    evaluacion = _auditoria(
        auditor, controles,
        [('5.15', 5, 5), ('6.3', 2, 2)],
        tratados=['6.3'])

    conteos, en_riesgo = _calculate_risk_counts([evaluacion])

    assert conteos['critico'] == 1, 'El riesgo 25 de 5.15 sigue sin tratar: %s' % conteos
    assert en_riesgo == [evaluacion]


def test_una_auditoria_solo_con_riesgos_bajos_es_optima(app, auditor, controles):
    evaluacion = _auditoria(auditor, controles, [('5.15', 1, 1), ('6.3', 1, 2)])

    conteos, _ = _calculate_risk_counts([evaluacion])

    assert conteos['optimo'] == 1, (
        'Un riesgo maximo de 2 esta en zona Baja: la auditoria es optima. %s' % conteos)


def test_el_riesgo_residual_es_el_maximo_de_los_controles_sin_tratar(
        app, auditor, controles):
    """No basta con mirar un control: se toma el peor de los que siguen abiertos."""
    evaluacion = _auditoria(
        auditor, controles,
        [('5.15', 5, 5), ('6.3', 3, 4), ('7.2', 1, 1)],
        tratados=['5.15'])

    conteos, _ = _calculate_risk_counts([evaluacion])

    assert conteos['critico'] == 1, (
        'Queda 6.3 sin tratar con riesgo 12, que es zona Alta. %s' % conteos)
