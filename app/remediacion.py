"""
Sugerencias automaticas de remediacion para hallazgos de auditoria.

Dado un control del Anexo A de ISO/IEC 27001:2022 y el nivel de riesgo de su
hallazgo (1-25), propone:

  * los controles de NIST SP 800-53 Rev. 5 que NIST relaciona oficialmente con
    ese control (OLIR 155), ordenados del mas especifico al mas general;
  * las estrategias de tratamiento que la metodologia de SADI admite para la
    zona de riesgo (metodologia_riesgos.html);
  * un plazo y un tipo de control sugeridos, que el auditor puede cambiar;
  * un borrador de acciones listo para el campo 'acciones' del plan.

Es un motor determinista y trazable: cada sugerencia cita el control NIST del
que sale. No reemplaza el juicio del auditor; solo le evita partir de una hoja
en blanco. La base de conocimiento (app/data/remediacion_nist.json) se
regenera con scripts/generar_remediacion_nist.py.
"""
import json
import os
from collections import Counter
from functools import lru_cache

from escalas import zona_riesgo

RUTA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'data', 'remediacion_nist.json')

# Estrategias por zona, tal como las enuncia metodologia_riesgos.html,
# expresadas con los valores que admite PlanTratamiento.estrategia.
ESTRATEGIAS_POR_ZONA = {
    'Baja': ['Aceptar'],
    'Moderada': ['Aceptar', 'Mitigar'],
    'Alta': ['Mitigar', 'Evitar', 'Transferir'],
    'Extrema': ['Mitigar', 'Evitar', 'Transferir'],
}

# Plazo sugerido (dias calendario) para cerrar el plan. Parametro de la
# organizacion, no un requisito de la norma: se puede ajustar aqui.
PLAZO_DIAS_POR_ZONA = {'Baja': 365, 'Moderada': 180, 'Alta': 90, 'Extrema': 30}

# Cuantas sugerencias mostrar por zona: mas riesgo, mas profundidad.
MAX_SUGERENCIAS_POR_ZONA = {'Baja': 2, 'Moderada': 3, 'Alta': 5, 'Extrema': 6}

PRIORIDAD_POR_ZONA = {'Baja': 'Baja', 'Moderada': 'Media', 'Alta': 'Alta',
                      'Extrema': 'Inmediata'}

# Clasificacion del tipo de control segun su funcion en NIST.
_DETECTIVOS = {'AU', 'CA-7', 'SI-4', 'SI-3', 'RA-5', 'PE-6', 'IR-5', 'SI-7', 'AC-2(12)',
               'AU-6', 'AU-13'}
_CORRECTIVOS = {'IR', 'CP', 'SI-2', 'SI-5', 'MA', 'RA-7'}


@lru_cache(maxsize=1)
def base_conocimiento():
    with open(RUTA_DATOS, encoding='utf-8') as f:
        datos = json.load(f)
    # Cuantos controles del Anexo A comparte cada control NIST: cuanto menos,
    # mas especifico y mas accionable es como sugerencia.
    alcance = Counter(n for lista in datos['mapeo'].values() for n in lista)
    datos['_alcance'] = dict(alcance)
    return datos


def normalizar_codigo(codigo):
    """'A.5.15', 'a.5.15' o '5.15' -> '5.15'."""
    codigo = (codigo or '').strip()
    if codigo[:2].lower() == 'a.':
        codigo = codigo[2:]
    return codigo


def tipo_control(nist_id):
    familia = nist_id.split('-')[0]
    base = nist_id.split('(')[0]
    if nist_id in _DETECTIVOS or base in _DETECTIVOS or familia in _DETECTIVOS:
        return 'Detective'
    if base in _CORRECTIVOS or familia in _CORRECTIVOS:
        return 'Correctivo'
    return 'Preventivo'


def _orden(nist_id, alcance):
    es_mejora = '(' in nist_id
    es_politica = nist_id.split('(')[0].endswith('-1')  # XX-1: politicas y procedimientos
    return (es_politica, es_mejora, alcance.get(nist_id, 99), nist_id)


def sugerir(codigo_control, riesgo):
    """
    Devuelve un dict con la sugerencia de remediacion para un control y riesgo.

    Siempre devuelve una estructura valida: si el control no tiene
    correspondencia publicada por NIST, 'sugerencias' queda vacia y
    'sin_correspondencia' es True.
    """
    datos = base_conocimiento()
    codigo = normalizar_codigo(codigo_control)
    zona = zona_riesgo(riesgo)
    if zona not in ESTRATEGIAS_POR_ZONA:
        zona_calculo = 'Baja'
    else:
        zona_calculo = zona

    candidatos = sorted(datos['mapeo'].get(codigo, []),
                        key=lambda n: _orden(n, datos['_alcance']))
    total = len(candidatos)
    limite = MAX_SUGERENCIAS_POR_ZONA[zona_calculo]

    sugerencias = []
    for nist_id in candidatos[:limite]:
        ctrl = datos['controles_nist'][nist_id]
        sugerencias.append({
            'id': nist_id,
            'titulo': ctrl['titulo'],
            'familia': ctrl['familia'],
            'familia_es': datos['familias'].get(ctrl['familia'], ctrl['familia']),
            'enunciado': ctrl['enunciado'],
            'tipo_control': tipo_control(nist_id),
        })

    tipos = Counter(s['tipo_control'] for s in sugerencias)
    tipo_sugerido = tipos.most_common(1)[0][0] if tipos else 'Preventivo'

    return {
        'control_iso': codigo,
        'riesgo': riesgo,
        'zona': zona,
        'prioridad': PRIORIDAD_POR_ZONA[zona_calculo],
        'estrategias': ESTRATEGIAS_POR_ZONA[zona_calculo],
        'estrategia_sugerida': ESTRATEGIAS_POR_ZONA[zona_calculo][0],
        'plazo_dias': PLAZO_DIAS_POR_ZONA[zona_calculo],
        'tipo_control_sugerido': tipo_sugerido,
        'sugerencias': sugerencias,
        'total_correspondencias': total,
        'sin_correspondencia': total == 0,
        'fuente': datos['fuente']['mapeo'],
        'advertencia': datos['fuente']['advertencia'],
    }


def borrador_acciones(sugerencia):
    """Texto en espanol para precargar el campo 'acciones' del plan."""
    if sugerencia['sin_correspondencia']:
        return ('NIST no publica correspondencia para el control '
                f"{sugerencia['control_iso']}. Definir las acciones a partir de la guía "
                'de ISO/IEC 27002:2022 para este control.')
    lineas = [f"Prioridad {sugerencia['prioridad'].lower()} — zona de riesgo "
              f"{sugerencia['zona'].lower()} (nivel {sugerencia['riesgo']}). "
              f"Cierre sugerido en {sugerencia['plazo_dias']} días.",
              'Acciones de referencia (NIST SP 800-53 Rev. 5):']
    for i, s in enumerate(sugerencia['sugerencias'], 1):
        lineas.append(f"{i}. Implementar o reforzar {s['id']} «{s['titulo']}» "
                      f"({s['familia_es']}; control {s['tipo_control'].lower()}).")
    lineas.append('Registrar la evidencia de cada acción y verificar su eficacia antes '
                  'de cerrar el plan.')
    return '\n'.join(lineas)
