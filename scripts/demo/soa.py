# -*- coding: utf-8 -*-
"""
Declaracion de Aplicabilidad del caso de demostracion.

DATOS SINTETICOS.

SADI crea un SoADocument por dominio y un SoADetalle por control. Aqui se define
la aplicabilidad y la justificacion de cada uno de los 93 controles.

La justificacion sigue el criterio de ISO/IEC 27001:2022, clausula 6.1.3 d):
se justifica la inclusion por su origen (resultado de la apreciacion de riesgos,
requisito legal o contractual) y la exclusion por la razon de no aplicabilidad.
"""

# Tres controles excluidos, con la razon de la exclusion.
EXCLUSIONES = {
    '8.4': 'NO APLICABLE. La organización no custodia ni mantiene código fuente propio. Los '
           'desarrollos a la medida sobre el ERP son propiedad del proveedor y residen en su '
           'repositorio, según el contrato CT-2024-08. El riesgo asociado se gestiona a través '
           'de los controles 5.20 y 8.30. Verificado en la auditoría integral del 13/04/2026.',
    '8.25': 'NO APLICABLE. La organización no ejecuta actividades de desarrollo de software. El '
            'ciclo de vida de desarrollo seguro es obligación contractual del proveedor del ERP '
            'y su cumplimiento se verifica mediante el control 8.30. Exclusión aprobada en el '
            'comité del 07/09/2026.',
    '8.31': 'NO APLICABLE. La organización no mantiene entornos de desarrollo ni de prueba '
            'propios. Los aloja y administra el proveedor del ERP en instancias separadas de '
            'producción, condición verificada en la auditoría integral y exigible por el control '
            '5.22. Exclusión aprobada en el comité del 07/09/2026.',
}

# Justificacion redactada a mano para los controles con riesgo alto o extremo,
# que son los que sustentan la mayor parte de las decisiones del SGSI.
JUSTIFICACIONES = {
    '5.1': 'APLICABLE. Requisito de la cláusula 5.2 de la norma y base de todo el SGSI. La '
           'apreciación de riesgos lo calificó en zona Alta (9) por la ausencia de política '
           'aprobada. Cubierto por la política POL-SGSI-001 v2.0, aprobada el 24/06/2026.',
    '5.2': 'APLICABLE. Requisito de la cláusula 5.3. Riesgo Alto (9) por roles sin asignar ni '
           'comunicar. Se mantiene para asegurar la rendición de cuentas del SGSI.',
    '5.5': 'APLICABLE. Necesario para cumplir los plazos de notificación de la Ley 1581 de 2012 '
           'ante la Superintendencia de Industria y Comercio. Riesgo Alto (9).',
    '5.14': 'APLICABLE. Riesgo Alto (12): la información de cartera se transfiere a terceros. '
            'Exigido además por los acuerdos de confidencialidad con los clientes principales.',
    '5.15': 'APLICABLE. Control de mayor criticidad de la apreciación de riesgos: zona Extrema '
            '(25) por ausencia de política de control de acceso y cuentas activas de personal '
            'retirado. Es la base de los controles 5.16, 5.17, 5.18 y 8.3.',
    '5.19': 'APLICABLE. Zona Extrema (20). La organización depende de proveedores con acceso '
            'remoto a sistemas que tratan datos personales, lo que la hace responsable frente a '
            'la Ley 1581 y al Decreto 1377.',
    '5.28': 'APLICABLE. Riesgo Alto (9). Necesario para sustentar cualquier actuación legal o '
            'disciplinaria derivada de un incidente. La gerencia aceptó el riesgo residual para '
            '2026 con soporte forense contratado por demanda.',
    '6.1': 'APLICABLE. Riesgo Alto (9). Hay cargos con acceso a tesorería y a datos personales, '
           'lo que exige verificación proporcional a la criticidad del puesto.',
    '6.4': 'APLICABLE. Riesgo Alto (12). Sin proceso disciplinario la organización no puede hacer '
           'exigible la política de seguridad, lo que debilita todos los demás controles.',
    '7.10': 'APLICABLE. Riesgo Alto (9). Se usan medios extraibles y se transportan respaldos '
            'fuera de las instalaciones.',
    '7.14': 'APLICABLE. Riesgo Alto (12). La organización da de baja y dona equipos que han '
            'tratado datos personales y de nómina.',
    '8.8': 'APLICABLE. Control de mayor criticidad junto con 5.15: zona Extrema (25). Sustenta '
           'la detección oportuna de debilidades técnicas en el ERP y en la infraestructura '
           'expuesta a internet.',
    '8.10': 'APLICABLE. Riesgo Alto (9). Exigido por el principio de temporalidad del tratamiento '
            'de datos personales (Ley 1581 y Decreto 1377).',
    '8.19': 'APLICABLE. Riesgo Alto (12). El control se refuerza con la estrategia de evitación: '
            'retiro de privilegios de administrador local a todos los usuarios.',
    '8.20': 'APLICABLE. Riesgo Alto (12). Toda la operación depende de la red interna y del enlace '
            'con el proveedor del ERP.',
    '8.32': 'APLICABLE. Riesgo Alto (9). Un cambio no controlado en el ERP ya provoco dos días sin '
            'facturación en marzo de 2026.',
}

# Plantillas por zona de riesgo para los controles restantes. El generador les
# anade el nombre del control y el nivel de riesgo que arrojo la auditoria.
PLANTILLA_POR_ZONA = {
    'Moderada': 'APLICABLE. La apreciación de riesgos del 13/04/2026 lo ubicó en zona Moderada '
                '({nivel}) por debilidades verificadas en la auditoría integral. Se mantiene en '
                'el alcance con tratamiento de reducción progresiva.',
    'Baja': 'APLICABLE. La apreciación de riesgos del 13/04/2026 lo ubicó en zona Baja ({nivel}): '
            'el control opera y se verifico su evidencia. Se mantiene en el alcance para sostener '
            'el nivel alcanzado.',
}


def zona_de(nivel):
    if nivel >= 20:
        return 'Extrema'
    if nivel >= 9:
        return 'Alta'
    if nivel >= 3:
        return 'Moderada'
    return 'Baja'


def detalle(codigo, nivel_riesgo):
    """Devuelve (aplicable, justificacion) para un control del SoA."""
    if codigo in EXCLUSIONES:
        return False, EXCLUSIONES[codigo]
    if codigo in JUSTIFICACIONES:
        return True, JUSTIFICACIONES[codigo]
    zona = zona_de(nivel_riesgo)
    plantilla = PLANTILLA_POR_ZONA.get(zona, PLANTILLA_POR_ZONA['Baja'])
    return True, plantilla.format(nivel=nivel_riesgo)
