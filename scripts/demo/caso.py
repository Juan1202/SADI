# -*- coding: utf-8 -*-
"""
Ensamblado del caso de demostracion.

DATOS SINTETICOS.

Reune el catalogo de controles, los hallazgos por dominio y los ajustes por
auditoria en una sola estructura, que usan tanto el generador de CSV como el
cargador seed_demo_sgsi.py. De esta forma el archivo que revisa el equipo y lo
que se carga al aplicativo salen del mismo sitio.
"""
from .auditorias import AUDITORIAS, AJUSTES, EVIDENCIAS_ARCHIVO, EVIDENCIAS_TEXTO
from .hallazgos_organizacional import ORGANIZACIONAL
from .hallazgos_personas import PERSONAS
from .hallazgos_fisico import FISICO
from .hallazgos_tecnologico import TECNOLOGICO

UMBRAL_BLOQUEANTE = 9

DOMINIO_DE_PREFIJO = {
    '5': 'Organizacional',
    '6': 'Personas',
    '7': 'Físico',
    '8': 'Tecnológico',
}

HALLAZGOS_BASE = {}
for _tabla in (ORGANIZACIONAL, PERSONAS, FISICO, TECNOLOGICO):
    HALLAZGOS_BASE.update(_tabla)


def dominio_de(codigo):
    return DOMINIO_DE_PREFIJO[codigo.split('.')[0]]


def orden_de(codigo):
    return [int(n) for n in codigo.replace('A.', '').split('.') if n.isdigit()]


def zona_de(nivel):
    if nivel >= 20:
        return 'Extrema'
    if nivel >= UMBRAL_BLOQUEANTE:
        return 'Alta'
    if nivel >= 3:
        return 'Moderada'
    return 'Baja'


def controles_de(clave_auditoria):
    """Codigos de control en el alcance de una auditoria, ordenados."""
    definicion = next(a for a in AUDITORIAS if a['clave'] == clave_auditoria)
    if definicion['alcance'] == 'TODOS':
        codigos = list(HALLAZGOS_BASE)
    elif definicion['alcance'] == 'CONTROLES':
        codigos = list(definicion['controles_alcance'])
        desconocidos = [c for c in codigos if c not in HALLAZGOS_BASE]
        if desconocidos:
            raise ValueError('Controles fuera del catalogo en %s: %s'
                             % (clave_auditoria, ', '.join(desconocidos)))
    else:
        codigos = [c for c in HALLAZGOS_BASE if dominio_de(c) == definicion['dominio']]
    return sorted(codigos, key=orden_de)


def hallazgos_de(clave_auditoria):
    """
    [(codigo, indice, criterio, probabilidad, impacto, nivel, zona, hallazgo,
      origen, archivo_evidencia)] de una auditoria.

    Aplica los ajustes declarados en auditorias.AJUSTES cuando la auditoria
    reevalua un control ya cubierto por la auditoria integral.
    """
    ajustes = AJUSTES.get(clave_auditoria, {})
    archivos = EVIDENCIAS_ARCHIVO.get(clave_auditoria, {})
    salida = []

    for codigo in controles_de(clave_auditoria):
        origen, criterios = HALLAZGOS_BASE[codigo]
        ajuste = ajustes.get(codigo)

        for indice, (criterio, prob, imp, hallazgo) in enumerate(criterios):
            if ajuste and indice < len(ajuste):
                prob, imp, hallazgo = ajuste[indice]
                origen_fila = 'SEGUIMIENTO'
            else:
                origen_fila = origen
            nivel = prob * imp
            salida.append({
                'auditoria': clave_auditoria,
                'control': codigo,
                'dominio': dominio_de(codigo),
                'indice': indice,
                'criterio': criterio,
                'hallazgo': hallazgo,
                'probabilidad': prob,
                'impacto': imp,
                'nivel': nivel,
                'zona': zona_de(nivel),
                'origen': origen_fila,
                'archivo_evidencia': archivos.get(codigo, {}).get(indice, ''),
            })
    return salida


def riesgo_por_control(clave_auditoria):
    """{codigo: riesgo maximo} de una auditoria."""
    maximos = {}
    for fila in hallazgos_de(clave_auditoria):
        codigo = fila['control']
        maximos[codigo] = max(maximos.get(codigo, 0), fila['nivel'])
    return maximos


def controles_bloqueantes(clave_auditoria):
    """Codigos con riesgo >= 9, que exigen plan cerrado para poder finalizar."""
    maximos = riesgo_por_control(clave_auditoria)
    return sorted([c for c, n in maximos.items() if n >= UMBRAL_BLOQUEANTE], key=orden_de)


def evidencias_texto_de(clave_auditoria):
    return EVIDENCIAS_TEXTO.get(clave_auditoria, {})


def resumen_distribucion(clave_auditoria):
    """{zona: cantidad de controles} de una auditoria."""
    conteo = {'Extrema': 0, 'Alta': 0, 'Moderada': 0, 'Baja': 0}
    for nivel in riesgo_por_control(clave_auditoria).values():
        conteo[zona_de(nivel)] += 1
    return conteo
