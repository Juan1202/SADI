# -*- coding: utf-8 -*-
"""
Definicion de las cinco auditorias del caso de demostracion.

DATOS SINTETICOS.

Las auditorias 2 y 3 reevaluan un dominio ya cubierto por la auditoria integral.
Los controles cuyo plan de tratamiento se cerro entre una y otra bajan de nivel;
esos cambios se declaran uno a uno en AJUSTES para que sean auditables, en vez de
aplicarse con una regla implicita.
"""
from .organizacion import (
    AUDITOR_1, AUDITOR_2, PREFIJO_AUDITORIA,
    FECHA_AUDITORIA_INTEGRAL, FECHA_AUDITORIA_TECNOLOGICA,
    FECHA_AUDITORIA_ORGANIZACIONAL, FECHA_AUDITORIA_PERSONAS,
    FECHA_AUDITORIA_VERIFICACION,
)

# Alcance: 'TODOS', 'DOMINIO' (con 'dominio') o 'CONTROLES' (con 'controles_alcance').
AUDITORIAS = [
    {
        'clave': 'integral',
        'titulo': '%s Auditoría interna integral del SGSI - 93 controles del Anexo A' % PREFIJO_AUDITORIA,
        'alcance': 'TODOS',
        'dominio': None,
        'propietario': AUDITOR_1,
        'fecha': FECHA_AUDITORIA_INTEGRAL,
        'estado_final': 'Finalizada',
        'eliminado': False,
        'descripcion': 'Primera auditoría interna completa del SGSI. Cubre los 93 controles del '
                       'Anexo A de ISO/IEC 27001:2022. Alimenta el tablero de métricas y el '
                       'informe PDF completo. DATOS Sintéticos DE Demostración.',
    },
    {
        'clave': 'tecnologica',
        'titulo': '%s Auditoría de seguimiento - Tema Tecnológico (A.8)' % PREFIJO_AUDITORIA,
        'alcance': 'DOMINIO',
        'dominio': 'Tecnológico',
        'propietario': AUDITOR_1,
        'fecha': FECHA_AUDITORIA_TECNOLOGICA,
        'estado_final': 'Finalizada',
        'eliminado': False,
        'descripcion': 'Seguimiento a los 34 controles tecnológicos dos meses despues de la '
                       'auditoría integral, para verificar la eficacia de los planes cerrados. '
                       'DATOS Sintéticos DE Demostración.',
    },
    {
        'clave': 'organizacional',
        'titulo': '%s Auditoría de seguimiento - Tema Organizacional (A.5)' % PREFIJO_AUDITORIA,
        'alcance': 'DOMINIO',
        'dominio': 'Organizacional',
        'propietario': AUDITOR_2,
        'fecha': FECHA_AUDITORIA_ORGANIZACIONAL,
        'estado_final': 'En Proceso',
        'eliminado': False,
        'descripcion': 'Seguimiento a los 37 controles organizacionales. Queda abierta a '
                       'propósito: conserva riesgos altos sin plan cerrado, de modo que la regla '
                       'de bloqueo impide finalizarla. DATOS Sintéticos DE Demostración.',
    },
    {
        'clave': 'personas',
        'titulo': '%s Auditoría de seguimiento - Tema Personas (A.6)' % PREFIJO_AUDITORIA,
        'alcance': 'DOMINIO',
        'dominio': 'Personas',
        'propietario': AUDITOR_2,
        'fecha': FECHA_AUDITORIA_PERSONAS,
        'estado_final': 'En Proceso',
        'eliminado': True,
        'descripcion': 'Auditoría anulada por reprogramación del cronograma. Se envia a la '
                       'papelera para mostrar el borrado lógico y la restauración. '
                       'DATOS Sintéticos DE Demostración.',
    },
    {
        'clave': 'verificacion_fisica',
        'titulo': '%s Verificación de cierre - Controles físicos remediados (A.7)' % PREFIJO_AUDITORIA,
        'alcance': 'CONTROLES',
        'dominio': None,
        'controles_alcance': ['7.1', '7.2', '7.3', '7.10', '7.11', '7.12', '7.14'],
        'propietario': AUDITOR_2,
        'fecha': FECHA_AUDITORIA_VERIFICACION,
        'estado_final': 'Finalizada',
        'eliminado': False,
        'descripcion': 'Verificación acotada a los siete controles físicos cuyos planes de '
                       'tratamiento se cerraron tras la auditoría integral. Todos quedan en zona '
                       'de riesgo Baja, de modo que la auditoría cierra sin activar la regla de '
                       'bloqueo. DATOS Sintéticos DE Demostración.',
    },
]

# Ajustes de probabilidad e impacto respecto de la auditoria integral.
#   clave_auditoria -> codigo_control -> [(probabilidad, impacto, nota), ...]
# La lista tiene una entrada por criterio del control, en el mismo orden.
AJUSTES = {
    'verificacion_fisica': {
        '7.10': [(1, 2, 'Bitácora de ingreso al cuarto de equipos diligenciada de forma completa '
                        'en las últimas ocho semanas.'),
                 (1, 2, 'Cerradura del cuarto de equipos reemplazada y llaves entregadas contra '
                        'acta a dos responsables.')],
        '7.14': [(1, 2, 'Procedimiento de baja de equipos aprobado; los tres últimos retiros se '
                        'documentaron con borrado seguro certificado.')],
    },
    'tecnologica': {
        '8.8':  [(4, 4, 'Escaneo trimestral contratado y ejecutado una vez; persisten 4 '
                        'vulnerabilidades altas sin remediar.'),
                 (4, 4, 'Se designo responsable de remediación y se aplicaron los parches '
                        'pendientes del servidor; falta formalizar el procedimiento.'),
                 (3, 4, 'Se acordaron plazos de remediación con el proveedor del ERP, aún sin '
                        'incorporar al contrato.')],
        '8.10': [(3, 3, 'Se definió la tabla de retención pero no se ha ejecutado la depuración '
                        'de las bases históricas.')],
        '8.19': [(3, 3, 'Se retiraron los privilegios de administrador local a 14 de 22 equipos; '
                        'faltan los 8 de la fuerza comercial.'),
                 (3, 3, 'Lista de software autorizado publicada; el inventario de lo instalado '
                        'sigue sin levantarse.')],
        '8.20': [(2, 4, 'Diagrama de red actualizado y aprobado en mayo de 2026.'),
                 (2, 4, 'Se separaron los SSID corporativo e invitados con claves distintas; falta '
                        'definir la rotación periódica.')],
        '8.32': [(3, 3, 'Procedimiento de gestión de cambios en borrador; el proveedor sigue '
                        'aplicando cambios en producción sin solicitud formal.')],
        '8.2':  [(2, 3, 'Se depuraron dos cuentas privilegiadas; quedan 4 para un equipo de 2 '
                        'personas.')],
        '8.5':  [(2, 3, 'Segundo factor habilitado para el acceso remoto; falta para el ERP y el '
                        'correo.')],
        '8.16': [(2, 3, 'Se activo la revisión semanal de registros del servidor; aún sin alertas '
                        'automaticas.')],
        '8.22': [(2, 3, 'Se segregó la red de invitados en una VLAN independiente; CCTV y '
                        'servidores siguen compartiendo segmento.')],
    },
    'organizacional': {
        '5.1':  [(2, 3, 'Política POL-SGSI-001 v2.0 aprobada el 24/06/2026; falta definir el '
                        'intervalo de revisión.'),
                 (2, 3, 'Política publicada en la intranet; la socialización cubre 31 de 48 '
                        'empleados.')],
        '5.2':  [(3, 3, 'Roles asignados nominalmente en acta; sin actualizar el manual de '
                        'funciones.'),
                 (3, 3, 'Comunicación enviada por circular; sin constancia de aceptación de 17 '
                        'empleados.')],
        '5.5':  [(3, 3, 'Sin avance: no se han establecido los puntos de contacto con autoridades.')],
        '5.14': [(3, 4, 'Sin avance: la cartera se sigue enviando por canales personales.'),
                 (3, 3, 'El disco de respaldo continúa viajando sin cifrar.')],
        '5.15': [(4, 5, 'Política de control de acceso en borrador avanzado, sin aprobar.'),
                 (4, 4, 'Se desactivaron 5 de las 7 cuentas de personal retirado; faltan 2 con '
                        'perfil de aprobación.'),
                 (3, 4, 'Se cambio la llave de tesorería; la relación de tenedores sigue sin '
                        'actualizar.')],
        '5.19': [(3, 5, 'Se acordó ventana de mantenimiento con el proveedor del ERP; persisten '
                        'las credenciales compartidas entre tres técnicos.'),
                 (3, 4, 'Sin avance: no hay inventario de la información accesible a cada '
                        'proveedor.')],
        '5.28': [(3, 3, 'Sin avance: no hay procedimiento de recopilación y preservación de '
                        'evidencias.')],
    },
}

# Controles que llevan evidencia en archivo (se sube por el flujo normal de la app).
# clave_auditoria -> codigo_control -> indice del criterio -> archivo de data/demo/evidencias
EVIDENCIAS_ARCHIVO = {
    'integral': {
        '8.8':  {0: 'EV-01_informe_escaneo_vulnerabilidades.pdf'},
        '5.15': {1: 'EV-02_revision_cuentas_activas.pdf'},
        '7.7':  {0: 'EV-03_recorrido_escritorio_limpio.png'},
        '8.20': {1: 'EV-04_configuracion_red_inalambrica.png'},
        '5.1':  {0: 'EV-05_borrador_politica_seguridad.pdf'},
        '6.4':  {0: 'EV-06_acta_comite_seguridad.pdf'},
    },
    'tecnologica': {
        '8.19': {0: 'EV-07_inventario_privilegios_locales.pdf'},
    },
}

# Controles que llevan evidencia solo en texto (campo evidencia_texto del resultado).
EVIDENCIAS_TEXTO = {
    'integral': {
        '5.9':  'Inventario INV-ACT-2026 en la carpeta de calidad, hoja "Activos", actualizado el '
                '27/02/2026. Verificado por muestreo de 12 activos durante la visita.',
        '8.13': 'Consola de respaldo del proveedor, reporte del 04/04/2026: restauración de prueba '
                'exitosa sobre la base del ERP, duración 38 minutos.',
        '7.11': 'Bitácora de pruebas de planta eléctrica BIT-MTO-2026, folios 11 a 16. Última '
                'prueba con carga: 28/03/2026, autonomía verificada de 45 minutos.',
        '5.31': 'Matriz legal MAT-LEG-2026, revisada con el área jurídica el 19/02/2026.',
    },
    'organizacional': {
        '5.1': 'Política POL-SGSI-001 v2.0, acta de aprobación ACT-GER-014 del 24/06/2026. '
               'Registro de socialización con 31 firmas de 48.',
    },
}


def auditoria(clave):
    for a in AUDITORIAS:
        if a['clave'] == clave:
            return a
    raise KeyError(clave)
