# -*- coding: utf-8 -*-
"""
Derivacion del diagnostico GAP (clausulas 4 a 10) desde el instrumento de 2019.

DATOS SINTETICOS.

REGLA DE MAPEO
--------------
El instrumento de 2019 tiene 132 preguntas y SADI tiene 22 requisitos. Cuando
varias preguntas del Excel caen en el mismo requisito de SADI se calcula el
promedio ponderado del grupo (cumple = 1, parcial = 0,5, no cumple = 0) y se
clasifica con estas bandas:

    promedio >= 0,75   -> cumple
    0,30 <= promedio   -> parcial
    promedio <  0,30   -> no_cumple

Las bandas se eligieron para que el puntaje global resultante (65,0 %) quede
cerca del que arrojan las secciones 1 a 11 del instrumento (61,2 %), sin
inventar un resultado mejor del que reporta el insumo.

EXCLUSION DOCUMENTADA
---------------------
Las filas 52 a 56 del Excel corresponden al requisito 6.1.1 de la norma
(acciones para tratar riesgos y oportunidades), que SADI no incluye entre sus
22 preguntas. No se reparten en otros requisitos para no diluir el resultado
de 6.1.2, que el instrumento califica de forma inequivoca en negativo.
"""

# (requisito SADI, filas del Excel que lo alimentan, promedio, valor, origen)
#
# `origen` indica de donde sale la decision: EXCEL:<filas> cuando se deriva del
# instrumento y GENERADO cuando es una decision del caso de demostracion.

MAPEO_DIAGNOSTICO_1 = [
    ('4.1',   'EXCEL:28,29',                 0.75,  'cumple'),
    ('4.2',   'EXCEL:30-34',                 0.80,  'cumple'),
    ('4.3',   'EXCEL:35-37',                 1.00,  'cumple'),
    ('4.4',   'EXCEL:24,25,26,27',           0.75,  'cumple'),

    ('5.1',   'EXCEL:38-43',                 0.833, 'cumple'),
    ('5.2',   'EXCEL:44-48',                 0.40,  'parcial'),
    ('5.3',   'EXCEL:49-51',                 0.333, 'parcial'),

    ('6.1.2', 'EXCEL:57-64',                 0.125, 'no_cumple'),
    ('6.1.3', 'EXCEL:65-73',                 0.556, 'parcial'),
    ('6.2',   'EXCEL:74-77',                 0.50,  'parcial'),

    ('7.1',   'EXCEL:41,78',                 0.25,  'no_cumple'),
    ('7.2',   'EXCEL:79,80,82',              0.50,  'parcial'),
    ('7.3',   'EXCEL:42,43,81',              0.667, 'parcial'),
    ('7.5',   'EXCEL:83,84,85',              0.333, 'parcial'),

    ('8.1',   'EXCEL:86-90',                 1.00,  'cumple'),
    ('8.2',   'EXCEL:91',                    1.00,  'cumple'),
    ('8.3',   'EXCEL:92,93',                 0.50,  'parcial'),

    ('9.1',   'EXCEL:94-97',                 0.75,  'cumple'),
    ('9.2',   'EXCEL:98-104',                1.00,  'cumple'),
    ('9.3',   'GENERADO',                    None,  'no_aplica'),

    ('10.1',  'GENERADO',                    None,  'no_evaluado'),
    ('10.2',  'EXCEL:108-111',               0.25,  'no_cumple'),
]

OBSERVACIONES_DIAGNOSTICO_1 = {
    '4.1': 'Se identificaron cuestiones internas y externas en el acta del comité del 26/02/2026, '
           'pero el análisis no se ha revisado desde entonces.',
    '4.2': 'Matriz de partes interesadas vigente. Faltan los requisitos reglamentarios de la '
           'Superintendencia de Industria y Comercio asociados a la Ley 1581.',
    '4.3': 'Alcance documentado en el acta ACT-SGSI-001: sede principal, bodega y servicios de TI '
           'tercerizados. Aprobado por la gerencia.',
    '4.4': 'El SGSI existe como iniciativa pero no hay evidencia de mantenimiento periódico. '
           'La dirección desconoce la Política Nacional de Seguridad Digital.',
    '5.1': 'La gerencia asiste al comité y aprueba el presupuesto, pero no asegura los recursos '
           'comprometidos para el SGSI.',
    '5.2': 'Existe un borrador de política sin aprobación formal ni fecha de revisión. No esta '
           'publicada en un medio accesible a todo el personal.',
    '5.3': 'Los roles están definidos en el documento de cargos, pero no se comunicaron al personal '
           'ni se asignaron autoridades para reportar el desempeño del SGSI.',
    '6.1.2': 'No existe metodología de apreciación de riesgos. No se identifican riesgos de '
             'confidencialidad, integridad y disponibilidad, ni se determinan niveles ni criterios.',
    '6.1.3': 'Hay un proceso informal de tratamiento y un plan formulado, pero no se elaboro la '
             'Declaración de Aplicabilidad ni se aceptaron los riesgos residuales.',
    '6.2': 'Los objetivos se comunican en la reunión anual pero no son cuantificables ni están '
           'documentados.',
    '7.1': 'No hay asignación presupuestal específica para el SGSI en la vigencia 2026.',
    '7.2': 'El personal es competente por experiencia, pero no se definieron las competencias '
           'requeridas ni se conservan evidencias completas.',
    '7.3': 'Se comunica la importancia del SGSI en la inducción. No hay campaña de concienciación '
           'periódica ni acciones para aumentar competencias.',
    '7.5': 'La información documentada existe pero no está identificada, revisada ni aprobada bajo '
           'control de cambios.',
    '8.1': 'Los procesos operativos están planificados y documentados, con control de cambios '
           'planificados y no previstos, y control de procesos subcontratados.',
    '8.2': 'Se realizan apreciaciones de riesgo ante cambios significativos y quedan documentadas.',
    '8.3': 'El plan de tratamiento se implementa, pero no se conserva información documentada de '
           'sus resultados.',
    '9.1': 'Se evalúa el desempeño y la eficacia del SGSI, aunque no se definió formalmente que '
           'medir, cuando ni con que método.',
    '9.2': 'Programa de auditoría interna vigente, con criterios, alcance, auditores imparciales e '
           'informes conservados.',
    '9.3': 'NO APLICA en este primer diagnóstico: el SGSI no ha completado el intervalo planificado '
           'para la primera revisión por la dirección. Se evaluará en el siguiente diagnóstico. '
           '(Decisión del caso de demostración, sirve para mostrar que el cálculo excluye no_aplica.)',
    '10.1': 'NO EVALUADO: pendiente la entrevista con el responsable de mejora continua. '
            '(Decisión del caso de demostración.)',
    '10.2': 'No hay procedimiento de no conformidades. No se determinan causas ni se evaluan '
            'acciones para evitar recurrencia.',
}

# Segundo diagnostico, posterior al cierre de los planes de tratamiento.
# Solo se listan los requisitos que cambian; el resto conserva el valor de D1.
CAMBIOS_DIAGNOSTICO_2 = {
    '5.2':   ('cumple',
              'Política POL-SGSI-001 v2.0 aprobada por la gerencia el 24/06/2026, publicada en la '
              'intranet y socializada. Cierra el plan del control 5.1.'),
    '5.3':   ('cumple',
              'Roles y responsabilidades comunicados mediante circular interna y aceptados por firma. '
              'Cierra el plan del control 5.2.'),
    '6.1.2': ('parcial',
              'Se adoptó la metodología de apreciación de riesgos de SADI (matriz 5x5 de ISO/IEC '
              '27005). Falta definir formalmente los criterios de aceptación del riesgo residual.'),
    '6.1.3': ('cumple',
              'Declaración de Aplicabilidad elaborada en SADI para los cuatro dominios, con '
              'justificación por control y tres exclusiones documentadas.'),
    '7.1':   ('parcial',
              'La gerencia asignó presupuesto para el segundo semestre de 2026. Aún no cubre la '
              'vigencia completa.'),
    '7.3':   ('cumple',
              'Campaña de concienciación ejecutada en julio de 2026 con 44 de 48 asistentes y '
              'evaluación posterior. Cierra el plan del control 6.3.'),
    '8.3':   ('cumple',
              'Los resultados del tratamiento quedan documentados en SADI: 18 planes con estado, '
              'responsable, plazo y acciones verificadas.'),
    '9.3':   ('cumple',
              'Primera revisión por la dirección realizada el 31/08/2026, con acta y decisiones '
              'sobre recursos y objetivos. Ya no aplica la exclusión del primer diagnóstico.'),
    '10.1':  ('cumple',
              'La mejora continua se evidencia en el cierre de 11 planes de tratamiento y en la '
              'mejora del puntaje GAP entre marzo y septiembre de 2026.'),
    '10.2':  ('parcial',
              'Procedimiento de no conformidades y acciones correctivas en versión borrador, '
              'pendiente de aprobación.'),
}

VALORES_EVALUADOS = ('cumple', 'parcial', 'no_cumple')
PUNTOS = {'cumple': 1.0, 'parcial': 0.5, 'no_cumple': 0.0}

# Categoria a la que pertenece cada requisito, segun diagnostico.py de SADI.
CATEGORIA_DE = {
    '4.1': '4', '4.2': '4', '4.3': '4', '4.4': '4',
    '5.1': '5', '5.2': '5', '5.3': '5',
    '6.1.2': '6', '6.1.3': '6', '6.2': '6',
    '7.1': '7', '7.2': '7', '7.3': '7', '7.5': '7',
    '8.1': '8', '8.2': '8', '8.3': '8',
    '9.1': '9', '9.2': '9', '9.3': '9',
    '10.1': '10', '10.2': '10',
}

NOMBRE_CATEGORIA = {
    '4': 'Contexto de la Organización',
    '5': 'Liderazgo',
    '6': 'Planificación',
    '7': 'Apoyo',
    '8': 'Operación',
    '9': 'Evaluación del Desempeño',
    '10': 'Mejora',
}


def respuestas_diagnostico_1():
    """[(requisito, valor, observacion, origen)] del primer diagnostico."""
    return [
        (req, valor, OBSERVACIONES_DIAGNOSTICO_1[req], origen)
        for req, origen, _promedio, valor in MAPEO_DIAGNOSTICO_1
    ]


def respuestas_diagnostico_2():
    """[(requisito, valor, observacion, origen)] del segundo diagnostico."""
    salida = []
    for req, origen, _promedio, valor in MAPEO_DIAGNOSTICO_1:
        if req in CAMBIOS_DIAGNOSTICO_2:
            nuevo_valor, observacion = CAMBIOS_DIAGNOSTICO_2[req]
            salida.append((req, nuevo_valor, observacion, 'GENERADO'))
        else:
            salida.append((req, valor, OBSERVACIONES_DIAGNOSTICO_1[req], origen))
    return salida


def puntaje(respuestas):
    """Aplica la formula de SADI: (cumple*1 + parcial*0,5) / evaluadas * 100."""
    evaluadas = [r for r in respuestas if r[1] in VALORES_EVALUADOS]
    if not evaluadas:
        return 0.0
    puntos = sum(PUNTOS[r[1]] for r in evaluadas)
    return round(puntos / len(evaluadas) * 100, 1)


def puntaje_por_categoria(respuestas):
    """{numero_categoria: puntaje} con la misma formula, por cada clausula."""
    acumulado = {}
    for requisito, valor, _obs, _origen in respuestas:
        categoria = CATEGORIA_DE[requisito]
        entrada = acumulado.setdefault(categoria, {'puntos': 0.0, 'evaluadas': 0})
        if valor in VALORES_EVALUADOS:
            entrada['puntos'] += PUNTOS[valor]
            entrada['evaluadas'] += 1
    return {
        categoria: (round(datos['puntos'] / datos['evaluadas'] * 100, 1)
                    if datos['evaluadas'] else 0.0)
        for categoria, datos in acumulado.items()
    }
