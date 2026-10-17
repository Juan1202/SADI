# -*- coding: utf-8 -*-
"""
Hallazgos del dominio Personas (A.6.1 - A.6.8), 8 controles.

DATOS SINTETICOS. Ver hallazgos_organizacional.py para la estructura.
"""

PERSONAS = {

    # ── ALTOS ────────────────────────────────────────────────────────────────
    '6.1': ('EXCEL:12.5', [
        ('Verificación de antecedentes antes de la contratación',
         3, 3,
         'No se realiza verificación de antecedentes. En la muestra de 10 expedientes, ninguno '
         'incluye consulta de antecedentes judiciales ni verificación de referencias laborales, '
         'incluidos los dos cargos con acceso a tesorería.'),
        ('Proporcionalidad de la verificación según la criticidad del cargo',
         3, 3,
         'No hay criterio que diferencie los cargos con acceso a información sensible del resto. '
         'El auxiliar de bodega y el coordinador de TI siguen el mismo proceso de ingreso.'),
    ]),

    '6.4': ('EXCEL:12.7', [
        ('Proceso disciplinario formal ante incumplimientos de seguridad',
         3, 4,
         'No existe proceso disciplinario asociado a la seguridad de la información. El reglamento '
         'interno no tipifica el incumplimiento de la política como falta, por lo que la '
         'organización no podría sancionar una fuga deliberada de información.'),
        ('Comunicación previa del proceso disciplinario al personal',
         3, 3,
         'Al no existir el proceso, no hay comunicación. Los empleados entrevistados no conocen '
         'consecuencia alguna por incumplir la política de seguridad.'),
    ]),

    # ── MODERADOS ────────────────────────────────────────────────────────────
    '6.2': ('GENERADO', [
        ('Términos y condiciones de empleo que recogen las responsabilidades de seguridad',
         2, 3,
         'Los contratos incluyen cláusula de confidencialidad genérica, pero no detallan las '
         'responsabilidades de seguridad de la información ni su vigencia tras la terminación.'),
    ]),

    '6.5': ('GENERADO', [
        ('Responsabilidades que continuan tras el cese o el cambio de empleo',
         2, 3,
         'El paz y salvo cubre la devolución de activos pero no recuerda por escrito las '
         'obligaciones de confidencialidad posteriores al retiro. En los cambios internos de cargo '
         'no se revisan los accesos heredados.'),
    ]),

    '6.6': ('GENERADO', [
        ('Acuerdos de confidencialidad vigentes y revisados',
         1, 2,
         'Los acuerdos de confidencialidad del personal de planta están firmados, pero los 6 '
         'contratistas y practicantes activos no tienen acuerdo suscrito.'),
    ]),

    '6.8': ('GENERADO', [
        ('Canal definido para que el personal notifique eventos de seguridad',
         2, 3,
         'El canal de reporte es el teléfono personal del coordinador de TI. No hay buzón ni '
         'registro de los eventos reportados, y fuera del horario laboral no hay cobertura.'),
    ]),

    # ── BAJOS ────────────────────────────────────────────────────────────────
    '6.3': ('EXCEL:12.6', [
        ('Concienciación, educación y formación en seguridad de la información',
         1, 2,
         'La inducción incluye un módulo de seguridad de la información de dos horas con '
         'evaluación. Se verificaron las 11 inducciones de 2026, todas con constancia y nota.'),
    ]),

    '6.7': ('EXCEL:12.17', [
        ('Medidas de seguridad para el trabajo remoto',
         1, 2,
         'La política de teletrabajo exige VPN, equipo corporativo y prohibición de redes públicas '
         'sin túnel. Se verifico la configuración en los 5 equipos asignados a teletrabajo.'),
    ]),
}
