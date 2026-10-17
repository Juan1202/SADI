# -*- coding: utf-8 -*-
"""
Planes de tratamiento del caso de demostracion.

DATOS SINTETICOS.

Hay un plan por cada control con riesgo >= 9, que es el umbral que bloquea el
cierre de la auditoria. Los de las auditorias 1 y 2 quedan Cerrado, porque esas
auditorias se finalizan; los de la auditoria 3 quedan repartidos entre Cerrado,
En Progreso y Abierto, de forma que esa auditoria siga bloqueada y que las tres
situaciones sean visibles en pantalla.

Estructura:
    clave_auditoria -> codigo_control -> dict del plan
"""
from datetime import date

# Las cuatro estrategias de tratamiento quedan representadas:
#   Mitigar    -> la mayoria
#   Transferir -> 5.19 en la auditoria integral
#   Aceptar    -> 5.28 en la auditoria integral
#   Evitar     -> 8.19 en la auditoria integral y en la tecnologica

PLANES = {

    # ── Auditoria integral: 16 planes, todos cerrados ────────────────────────
    'integral': {
        '5.15': {
            'descripcion': 'Ausencia de política de control de acceso y de revisión periódica de '
                           'cuentas. Cuentas activas de personal retirado con perfil de aprobación '
                           'de órdenes de compra.',
            'proceso': 'Gestión de TI y Seguridad de la Información',
            'activos': 'ERP, directorio activo, archivo físico de contratos',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Elaborar y aprobar la política de control de acceso POL-SGSI-002. '
                        '2) Desactivar las 7 cuentas de personal retirado. '
                        '3) Implantar revisión trimestral de accesos con acta del dueño del proceso. '
                        '4) Actualizar la relación de tenedores de llave y cambiar la llave maestra.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 5, 29),
            'estado': 'Cerrado',
        },
        '8.8': {
            'descripcion': 'No se ejecutan pruebas de vulnerabilidad. El escaneo de la auditoría '
                           'reportó 3 vulnerabilidades críticas y 11 altas en el segmento de '
                           'servidores.',
            'proceso': 'Gestión de TI',
            'activos': 'Servidor ERP, servidor de archivos, servicio de escritorio remoto',
            'estrategia': 'Mitigar',
            'tipo_control': 'Detective',
            'acciones': '1) Contratar escaneo autenticado trimestral con proveedor externo. '
                        '2) Remediar las 3 vulnerabilidades críticas: deshabilitar SMBv1, cerrar el '
                        'escritorio remoto expuesto y aplicar los parches pendientes. '
                        '3) Designar responsable de remediación y definir plazos por criticidad.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 5, 15),
            'estado': 'Cerrado',
        },
        '5.19': {
            'descripcion': 'Acceso remoto permanente del proveedor del ERP con credenciales '
                           'compartidas y sin registro de sesiones. Entrega de datos de salud al '
                           'proveedor de nómina sin necesidad.',
            'proceso': 'Compras y Gestión de Proveedores',
            'activos': 'ERP, base de datos de nómina, canal de acceso remoto',
            'estrategia': 'Transferir',
            'tipo_control': 'Preventivo',
            'acciones': '1) Trasladar la responsabilidad por incidentes derivados del acceso remoto '
                        'al proveedor mediante otrosí contractual con cláusula de responsabilidad y '
                        'póliza de cumplimiento. '
                        '2) Exigir credenciales nominales por técnico y registro de sesiones. '
                        '3) Reducir el archivo entregado al proveedor de nómina a los campos de '
                        'liquidación.',
            'responsable': 'Gerencia Administrativa',
            'plazo': date(2026, 6, 12),
            'estado': 'Cerrado',
        },
        '5.28': {
            'descripcion': 'No hay procedimiento de recopilación y preservación de evidencias. '
                           'La evidencia del intento de fraude de enero de 2026 se perdió.',
            'proceso': 'Gestión de Incidentes',
            'activos': 'Estaciones de trabajo, registros del correo corporativo',
            'estrategia': 'Aceptar',
            'tipo_control': 'Correctivo',
            'acciones': 'La gerencia acepta el riesgo residual para la vigencia 2026: la capacidad '
                        'forense interna no es viable con la estructura actual. Como medida '
                        'compensatoria se contrata soporte forense por demanda con el proveedor de '
                        'TI y se documenta la aceptación en el acta ACT-GER-009. Se reevalúa en la '
                        'revisión por la dirección de 2027.',
            'responsable': 'Gerencia General',
            'plazo': date(2026, 6, 30),
            'estado': 'Cerrado',
        },
        '8.19': {
            'descripcion': 'Los 22 usuarios tienen privilegios de administrador local. Nueve '
                           'equipos con software descargado de internet, uno con adware.',
            'proceso': 'Gestión de TI',
            'activos': 'Estaciones de trabajo, portátiles de la fuerza comercial',
            'estrategia': 'Evitar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Eliminar la posibilidad misma de instalar: retirar los privilegios de '
                        'administrador local a todos los usuarios. '
                        '2) Publicar la lista de software autorizado y desinstalar lo no autorizado. '
                        '3) Canalizar toda instalación por solicitud a la mesa de servicio.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 5, 22),
            'estado': 'Cerrado',
        },
        '5.1': {
            'descripcion': 'La política de seguridad de la información lleva desde noviembre de '
                           '2025 en borrador, sin aprobar, sin versión y sin publicar.',
            'proceso': 'Dirección del SGSI',
            'activos': 'Documentación del SGSI',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Completar y aprobar la política POL-SGSI-001 en comité de gerencia. '
                        '2) Publicarla en la intranet y socializarla con todo el personal. '
                        '3) Definir el intervalo de revisión anual.',
            'responsable': 'Oficial de Seguridad de la Información',
            'plazo': date(2026, 6, 26),
            'estado': 'Cerrado',
        },
        '5.2': {
            'descripcion': 'Roles de seguridad enunciados pero no asignados nominalmente ni '
                           'comunicados. Sin responsable de gestión de incidentes.',
            'proceso': 'Dirección del SGSI',
            'activos': 'Manual de funciones, estructura organizacional',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Asignar nominalmente los roles del SGSI en acta de gerencia. '
                        '2) Actualizar el manual de funciones. '
                        '3) Comunicar por circular y recoger constancia de aceptación.',
            'responsable': 'Gestión Humana',
            'plazo': date(2026, 6, 19),
            'estado': 'Cerrado',
        },
        '5.5': {
            'descripcion': 'Sin puntos de contacto definidos con autoridades. Ante un incidente no '
                           'se sabría a quién notificar ni en qué plazo (Ley 1581).',
            'proceso': 'Gestión de Incidentes',
            'activos': 'Procedimiento de gestión de incidentes',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Establecer los contactos con el CAI Virtual de la Policía Nacional, la '
                        'SIC y el ColCERT. '
                        '2) Incorporarlos al procedimiento PR-TI-004 con plazos de notificación. '
                        '3) Verificar los contactos semestralmente.',
            'responsable': 'Oficial de Seguridad de la Información',
            'plazo': date(2026, 6, 5),
            'estado': 'Cerrado',
        },
        '5.14': {
            'descripcion': 'Archivos de cartera enviados por correo personal y WhatsApp sin cifrar '
                           'ni acuerdo. Respaldos transportados sin cifrado ni custodia.',
            'proceso': 'Cartera y Gestión de TI',
            'activos': 'Base de cartera, disco de respaldo, correo corporativo',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Habilitar un canal de transferencia cifrado para la empresa de cobranza. '
                        '2) Suscribir acuerdo de transferencia y confidencialidad específico. '
                        '3) Cifrar el disco de respaldo y llevar acta de custodia en cada traslado.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 6, 12),
            'estado': 'Cerrado',
        },
        '6.1': {
            'descripcion': 'No se verifican antecedentes en la contratación, ni siquiera en los '
                           'cargos con acceso a tesorería.',
            'proceso': 'Gestión Humana',
            'activos': 'Expedientes de personal, proceso de selección',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Incorporar al proceso de selección la consulta de antecedentes y la '
                        'verificación de referencias. '
                        '2) Definir criterio diferenciado por criticidad del cargo. '
                        '3) Regularizar los expedientes de los cargos críticos actuales.',
            'responsable': 'Gestión Humana',
            'plazo': date(2026, 6, 26),
            'estado': 'Cerrado',
        },
        '6.4': {
            'descripcion': 'No existe proceso disciplinario asociado a la seguridad de la '
                           'información. El reglamento interno no tipifica el incumplimiento.',
            'proceso': 'Gestión Humana',
            'activos': 'Reglamento interno de trabajo',
            'estrategia': 'Mitigar',
            'tipo_control': 'Disuasivo',
            'acciones': '1) Tipificar el incumplimiento de la política de seguridad como falta en '
                        'el reglamento interno, con revisión jurídica. '
                        '2) Surtir el trámite de modificación y publicación. '
                        '3) Comunicar el proceso disciplinario a todo el personal.',
            'responsable': 'Gestión Humana',
            'plazo': date(2026, 7, 10),
            'estado': 'Cerrado',
        },
        '7.10': {
            'descripcion': 'Catorce memorias USB sin inventariar, dos con la base de clientes sin '
                           'cifrar. Respaldo transportado en vehículo particular.',
            'proceso': 'Gestión de TI',
            'activos': 'Medios extraibles, disco de respaldo, base de clientes',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Inventariar y recoger los medios extraibles no autorizados. '
                        '2) Entregar medios cifrados únicamente a los cargos que lo justifiquen. '
                        '3) Formalizar el traslado del respaldo con estuche seguro y acta.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 6, 5),
            'estado': 'Cerrado',
        },
        '7.14': {
            'descripcion': 'Equipos dados de baja donados con los discos intactos; uno contenía la '
                           'carpeta de nómina de tres vigencias.',
            'proceso': 'Gestión de TI y Activos Fijos',
            'activos': 'Equipos dados de baja, discos duros',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Definir el procedimiento de borrado seguro y destrucción de medios. '
                        '2) Incluir acta de borrado obligatoria en el formato de baja de activos. '
                        '3) Intentar el recobro o la certificación de borrado de los 5 equipos '
                        'donados en 2025.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 6, 19),
            'estado': 'Cerrado',
        },
        '8.10': {
            'descripcion': 'Bases de datos de clientes exportadas desde 2019 conservadas sin '
                           'criterio de eliminación, con finalidad de tratamiento caducada.',
            'proceso': 'Gestión de TI y Protección de Datos',
            'activos': 'Carpeta compartida, exportaciones históricas de clientes',
            'estrategia': 'Mitigar',
            'tipo_control': 'Correctivo',
            'acciones': '1) Definir tabla de retención y criterios de eliminación por tipo de dato. '
                        '2) Depurar las exportaciones históricas previa validación jurídica. '
                        '3) Programar la depuración periódica.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 7, 3),
            'estado': 'Cerrado',
        },
        '8.20': {
            'descripcion': 'Sin diagrama de red actualizado desde 2022. Red inalámbrica corporativa '
                           'y de invitados con el mismo SSID y clave escrita en la recepción.',
            'proceso': 'Gestión de TI',
            'activos': 'Infraestructura de red, red inalámbrica',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Levantar y aprobar el diagrama de red y el inventario de activos. '
                        '2) Separar los SSID corporativo e invitados con claves distintas. '
                        '3) Definir la rotación periódica de la clave y retirarla de la recepción.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 5, 29),
            'estado': 'Cerrado',
        },
        '8.32': {
            'descripcion': 'Cambios aplicados por el proveedor directamente en producción, sin '
                           'solicitud ni plan de reversión. Un cambio dejo sin facturar dos días.',
            'proceso': 'Gestión de TI',
            'activos': 'ERP, entorno de producción',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Definir el procedimiento de gestión de cambios con solicitud, '
                        'aprobación, ventana y plan de reversión. '
                        '2) Incorporarlo al contrato con el proveedor del ERP. '
                        '3) Llevar bitácora de cambios aplicados.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 7, 3),
            'estado': 'Cerrado',
        },
    },

    # ── Auditoria tecnologica: 4 planes, todos cerrados ──────────────────────
    'tecnologica': {
        '8.8': {
            'descripcion': 'El escaneo trimestral ya se ejecuta, pero persisten 4 vulnerabilidades '
                           'altas sin remediar y el procedimiento no está formalizado.',
            'proceso': 'Gestión de TI',
            'activos': 'Servidor ERP, servidor de archivos',
            'estrategia': 'Mitigar',
            'tipo_control': 'Detective',
            'acciones': '1) Remediar las 4 vulnerabilidades altas pendientes. '
                        '2) Formalizar el procedimiento de gestión de vulnerabilidades con plazos '
                        'por criticidad. '
                        '3) Incorporar los plazos al contrato con el proveedor del ERP.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 7, 31),
            'estado': 'Cerrado',
        },
        '8.10': {
            'descripcion': 'La tabla de retención quedó definida pero la depuración de las bases '
                           'históricas no se ha ejecutado.',
            'proceso': 'Gestión de TI y Protección de Datos',
            'activos': 'Carpeta compartida, exportaciones históricas',
            'estrategia': 'Mitigar',
            'tipo_control': 'Correctivo',
            'acciones': '1) Ejecutar la depuración de las exportaciones anteriores a 2023. '
                        '2) Dejar acta de eliminación con validación jurídica. '
                        '3) Automatizar el aviso de vencimiento de retención.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 8, 14),
            'estado': 'Cerrado',
        },
        '8.19': {
            'descripcion': 'Quedan 8 equipos de la fuerza comercial con privilegios de '
                           'administrador local y el inventario de software instalado sin levantar.',
            'proceso': 'Gestión de TI',
            'activos': 'Portátiles de la fuerza comercial',
            'estrategia': 'Evitar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Retirar los privilegios de administrador local de los 8 equipos '
                        'restantes. '
                        '2) Levantar el inventario de software instalado y desinstalar lo no '
                        'autorizado.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 7, 24),
            'estado': 'Cerrado',
        },
        '8.32': {
            'descripcion': 'El procedimiento de gestión de cambios sigue en borrador y el proveedor '
                           'continúa aplicando cambios en producción sin solicitud formal.',
            'proceso': 'Gestión de TI',
            'activos': 'ERP, entorno de producción',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Aprobar y publicar el procedimiento de gestión de cambios. '
                        '2) Firmar el otrosí que lo hace exigible al proveedor. '
                        '3) Auditar la bitácora de cambios al cierre del trimestre.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 8, 28),
            'estado': 'Cerrado',
        },
    },

    # ── Auditoria organizacional: 6 planes, ninguno cierra el bloqueo ────────
    'organizacional': {
        '5.2': {
            'descripcion': 'Roles asignados en acta pero sin actualizar el manual de funciones y '
                           'sin constancia de aceptación de 17 empleados.',
            'proceso': 'Dirección del SGSI',
            'activos': 'Manual de funciones',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Actualizar el manual de funciones con los roles del SGSI. '
                        '2) Completar la recolección de constancias de aceptación.',
            'responsable': 'Gestión Humana',
            'plazo': date(2026, 9, 18),
            'estado': 'Cerrado',
        },
        '5.5': {
            'descripcion': 'Sin avance respecto de la auditoría integral: no se establecieron los '
                           'contactos con autoridades.',
            'proceso': 'Gestión de Incidentes',
            'activos': 'Procedimiento de gestión de incidentes',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Registrar los contactos del CAI Virtual, la SIC y el ColCERT en el '
                        'procedimiento PR-TI-004. '
                        '2) Divulgar el directorio de notificación al comité.',
            'responsable': 'Oficial de Seguridad de la Información',
            'plazo': date(2026, 9, 11),
            'estado': 'Cerrado',
        },
        '5.14': {
            'descripcion': 'La cartera se sigue enviando por canales personales y el respaldo viaja '
                           'sin cifrar.',
            'proceso': 'Cartera y Gestión de TI',
            'activos': 'Base de cartera, disco de respaldo',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Poner en producción el canal cifrado de transferencia. '
                        '2) Firmar el acuerdo de transferencia con la empresa de cobranza. '
                        '3) Habilitar el cifrado del disco de respaldo.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 10, 16),
            'estado': 'En Progreso',
        },
        '5.28': {
            'descripcion': 'Sin avance: no hay procedimiento de recopilación y preservación de '
                           'evidencias.',
            'proceso': 'Gestión de Incidentes',
            'activos': 'Estaciones de trabajo, registros del correo',
            'estrategia': 'Mitigar',
            'tipo_control': 'Correctivo',
            'acciones': '1) Redactar el procedimiento de preservación de evidencias con el soporte '
                        'forense contratado. '
                        '2) Capacitar a la mesa de servicio en la primera respuesta.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 10, 30),
            'estado': 'En Progreso',
        },
        '5.15': {
            'descripcion': 'La política de control de acceso sigue sin aprobar y persisten 2 '
                           'cuentas de personal retirado con perfil de aprobación.',
            'proceso': 'Gestión de TI y Seguridad de la Información',
            'activos': 'ERP, directorio activo',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Aprobar la política POL-SGSI-002 en comité de gerencia. '
                        '2) Desactivar las 2 cuentas pendientes. '
                        '3) Ejecutar la primera revisión trimestral de accesos.',
            'responsable': 'Coordinación de TI',
            'plazo': date(2026, 11, 13),
            'estado': 'Abierto',
        },
        '5.19': {
            'descripcion': 'Persisten las credenciales compartidas del proveedor del ERP y no hay '
                           'inventario de la información accesible a cada proveedor.',
            'proceso': 'Compras y Gestión de Proveedores',
            'activos': 'ERP, canal de acceso remoto, base de nómina',
            'estrategia': 'Mitigar',
            'tipo_control': 'Preventivo',
            'acciones': '1) Exigir al proveedor credenciales nominales por técnico. '
                        '2) Levantar el inventario de información accesible por proveedor. '
                        '3) Habilitar el registro de sesiones remotas.',
            'responsable': 'Gerencia Administrativa',
            'plazo': date(2026, 11, 27),
            'estado': 'Abierto',
        },
    },
}


def planes_de(clave_auditoria):
    return PLANES.get(clave_auditoria, {})
