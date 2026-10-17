"""
Escalas de riesgo y madurez del SGSI (ADR-011).

Este modulo es la unica fuente de verdad para la conversion entre las dos
escalas que conviven en SADI y que antes se mezclaban en un solo campo
(ver CONTEXTO_SADI.md 7.4):

  * RIESGO   : 1 a 25, producto probabilidad x impacto (ISO/IEC 27005).
  * MADUREZ  : 0 a 5, escala que interpretan el tablero y los informes.

La conversion es una interpolacion lineal dentro de cada zona de la matriz
5x5, de forma que las zonas de riesgo caigan en las bandas de madurez que
ya usa dashboard_metrics.html (CUMPLE > 3.26, PARCIAL 1.66-3.25, NO CUMPLE < 1.65).
"""

RIESGO_MINIMO = 1
RIESGO_MAXIMO = 25
MADUREZ_MINIMA = 0.0
MADUREZ_MAXIMA = 5.0

# Umbral a partir del cual un hallazgo bloquea el cierre de la auditoria.
UMBRAL_RIESGO_BLOQUEANTE = 9

# (riesgo_min, riesgo_max, madurez_en_riesgo_min, madurez_en_riesgo_max, zona)
ZONAS_RIESGO = (
    (1, 2, 5.0, 4.5, 'Baja'),
    (3, 8, 4.4, 3.3, 'Moderada'),
    (9, 16, 3.2, 2.0, 'Alta'),
    (20, 25, 1.5, 1.0, 'Extrema'),
)


def zona_riesgo(riesgo):
    """Devuelve el nombre de la zona de la matriz 5x5 para un nivel de riesgo."""
    riesgo = _normalizar_riesgo(riesgo)
    if riesgo < RIESGO_MINIMO:
        return 'Sin evaluar'
    zona_encontrada = ZONAS_RIESGO[0][4]
    for r_min, _r_max, _m_alta, _m_baja, nombre in ZONAS_RIESGO:
        if riesgo >= r_min:
            zona_encontrada = nombre
    return zona_encontrada


def madurez_desde_riesgo(riesgo):
    """
    Convierte un nivel de riesgo (1-25) en un nivel de madurez (0-5).

    Un riesgo de 0 significa 'control sin hallazgos registrados' y devuelve 0.0;
    quien calcula promedios debe excluir esos resultados en vez de promediarlos.
    """
    riesgo = _normalizar_riesgo(riesgo)
    if riesgo < RIESGO_MINIMO:
        return MADUREZ_MINIMA
    if riesgo >= RIESGO_MAXIMO:
        return ZONAS_RIESGO[-1][3]

    for r_min, r_max, m_alta, m_baja, _nombre in ZONAS_RIESGO:
        if r_min <= riesgo <= r_max:
            if r_max == r_min:
                return round(m_alta, 2)
            avance = (riesgo - r_min) / (r_max - r_min)
            return round(m_alta - (m_alta - m_baja) * avance, 2)

    # Los productos 17, 18 y 19 no existen en una matriz 5x5, pero si el dato
    # llegara corrupto se trata como el extremo peor de la zona Alta.
    return ZONAS_RIESGO[2][3]


def riesgo_de_hallazgo(probabilidad, impacto):
    """Nivel de riesgo de un hallazgo: probabilidad x impacto, acotado a 0-25."""
    prob = _entero_seguro(probabilidad)
    imp = _entero_seguro(impacto)
    return max(0, min(RIESGO_MAXIMO, prob * imp))


def _normalizar_riesgo(riesgo):
    valor = _entero_seguro(riesgo)
    return max(0, min(RIESGO_MAXIMO, valor))


def _entero_seguro(valor):
    try:
        return int(valor) if valor is not None else 0
    except (ValueError, TypeError):
        return 0
