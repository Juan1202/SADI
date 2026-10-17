"""Conversion entre la escala de riesgo (1-25) y la de madurez (0-5), ADR-011."""
import pytest

from escalas import (
    madurez_desde_riesgo, riesgo_de_hallazgo, zona_riesgo,
    UMBRAL_RIESGO_BLOQUEANTE,
)


@pytest.mark.parametrize('riesgo, zona_esperada', [
    (1, 'Baja'), (2, 'Baja'),
    (3, 'Moderada'), (8, 'Moderada'),
    (9, 'Alta'), (16, 'Alta'),
    (20, 'Extrema'), (25, 'Extrema'),
])
def test_cada_nivel_de_riesgo_cae_en_su_zona_de_la_matriz(riesgo, zona_esperada):
    assert zona_riesgo(riesgo) == zona_esperada


@pytest.mark.parametrize('riesgo, madurez_esperada', [
    (1, 5.0), (2, 4.5),
    (3, 4.4), (8, 3.3),
    (9, 3.2), (16, 2.0),
    (20, 1.5), (25, 1.0),
])
def test_los_extremos_de_cada_zona_dan_la_madurez_documentada(riesgo, madurez_esperada):
    assert madurez_desde_riesgo(riesgo) == madurez_esperada


def test_la_madurez_decrece_cuando_el_riesgo_crece():
    niveles = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 20, 25]
    madureces = [madurez_desde_riesgo(n) for n in niveles]
    assert madureces == sorted(madureces, reverse=True)


def test_riesgo_cero_significa_control_sin_hallazgos():
    assert madurez_desde_riesgo(0) == 0.0
    assert zona_riesgo(0) == 'Sin evaluar'


def test_las_zonas_alta_y_extrema_quedan_bajo_el_umbral_de_cumplimiento():
    """Un riesgo bloqueante nunca puede presentarse como CUMPLE en el tablero."""
    for riesgo in (9, 10, 12, 15, 16, 20, 25):
        assert madurez_desde_riesgo(riesgo) <= 3.26


def test_las_zonas_baja_y_moderada_quedan_sobre_el_umbral_de_cumplimiento():
    for riesgo in (1, 2, 3, 4, 5, 6, 8):
        assert madurez_desde_riesgo(riesgo) > 3.26


@pytest.mark.parametrize('prob, imp, esperado', [
    (5, 5, 25), (3, 3, 9), (1, 1, 1), (4, 5, 20),
    (None, 3, 0), ('x', 2, 0), (99, 99, 25),
])
def test_el_riesgo_es_el_producto_acotado_a_la_matriz(prob, imp, esperado):
    assert riesgo_de_hallazgo(prob, imp) == esperado


def test_el_umbral_bloqueante_es_nueve_como_indica_la_metodologia():
    assert UMBRAL_RIESGO_BLOQUEANTE == 9
