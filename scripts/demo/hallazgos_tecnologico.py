# -*- coding: utf-8 -*-
"""
Hallazgos del dominio Tecnologico (A.8.1 - A.8.34), 34 controles.

DATOS SINTETICOS. Ver hallazgos_organizacional.py para la estructura.
"""

TECNOLOGICO = {

    # ── EXTREMO ──────────────────────────────────────────────────────────────
    '8.8': ('EXCEL:12.22', [
        ('Ejecución periódica de pruebas de vulnerabilidad sobre sistemas y aplicaciones',
         5, 5,
         'No se han ejecutado pruebas de vulnerabilidad desde la puesta en producción del ERP en '
         '2023. El escaneo puntual realizado durante esta auditoría sobre el segmento de '
         'servidores reportó 3 vulnerabilidades críticas y 11 altas, entre ellas SMBv1 habilitado '
         'y un servicio de escritorio remoto expuesto sin segundo factor.'),
        ('Proceso de gestión y remediación de las vulnerabilidades identificadas',
         5, 4,
         'No hay proceso de remediación ni responsable asignado. Las actualizaciones de seguridad '
         'del sistema operativo están en modo manual y el último parche aplicado al servidor es de '
         'septiembre de 2025.'),
        ('Definición de plazos de remediación según la criticidad',
         4, 4,
         'No existen acuerdos de plazo para remediar. Las vulnerabilidades reportadas por el '
         'proveedor del ERP en 2025 siguen abiertas sin fecha compromiso.'),
    ]),

    # ── ALTOS ────────────────────────────────────────────────────────────────
    '8.10': ('EXCEL:12.9', [
        ('Eliminación de la información cuando deja de ser necesaria',
         3, 3,
         'No hay criterio ni procedimiento de eliminación de información. La carpeta compartida '
         'conserva bases de datos de clientes exportadas desde 2019, con datos personales cuya '
         'finalidad de tratamiento ya caduco.'),
    ]),

    '8.19': ('EXCEL:12.24', [
        ('Reglas que regulen la instalación de software en los sistemas operativos',
         4, 3,
         'No hay restricción de instalación: los 22 usuarios tienen privilegios de administrador '
         'local. Se identificaron 9 equipos con software descargado de internet, incluido un gestor '
         'de descargas con adware reportado.'),
        ('Control sobre el software autorizado en la organización',
         3, 3,
         'No existe lista de software autorizado ni inventario de lo instalado. El área de TI no '
         'sabe que aplicaciones corren en los equipos de la fuerza comercial.'),
    ]),

    '8.20': ('EXCEL:12.25', [
        ('Documentación, gestión y control de la infraestructura de red',
         3, 4,
         'No existe diagrama de red actualizado ni inventario de equipos activos. El último '
         'diagrama es de 2022 y no refleja los dos switches ni el enlace de contingencia '
         'incorporados desde entonces.'),
        ('Protección de la información en tránsito por la red',
         3, 3,
         'La red inalámbrica corporativa y la de invitados comparten el mismo SSID y la misma '
         'clave, que no se cambia desde 2023 y esta escrita en la recepción.'),
    ]),

    '8.32': ('EXCEL:12.28b', [
        ('Gestión documentada de los cambios en los sistemas de información',
         3, 3,
         'No hay procedimiento de gestión de cambios. Las modificaciones al ERP las aplica el '
         'proveedor directamente en producción, sin solicitud formal, sin aprobación y sin plan '
         'de reversión. Un cambio de marzo de 2026 dejo sin facturar dos días.'),
    ]),

    # ── MODERADOS ────────────────────────────────────────────────────────────
    '8.2': ('GENERADO', [
        ('Restricción y control de los derechos de acceso privilegiado',
         2, 4,
         'Existen 6 cuentas con privilegios de administrador de dominio para un equipo de TI de '
         '2 personas. Dos pertenecen al proveedor y una no tiene responsable identificado.'),
    ]),

    '8.3': ('GENERADO', [
        ('Restricción del acceso a la información según la política de control de acceso',
         2, 4,
         'Los perfiles del ERP no siguen el principio de mínimo privilegio: el perfil comercial '
         'permite consultar la nómina y los costos de compra.'),
    ]),

    '8.5': ('GENERADO', [
        ('Uso de técnicas de autenticación segura',
         2, 4,
         'El acceso al ERP y al correo usa solo usuario y contraseña. No hay segundo factor ni '
         'siquiera para las cuentas administrativas ni para el acceso remoto.'),
    ]),

    '8.11': ('GENERADO', [
        ('Enmascaramiento de datos en entornos distintos de producción',
         2, 3,
         'El entorno de pruebas del ERP usa una copia integra de la base de producción con datos '
         'reales de clientes, accesible a los técnicos del proveedor.'),
    ]),

    '8.12': ('GENERADO', [
        ('Medidas de prevención de fuga de datos',
         2, 3,
         'No hay control sobre la salida de información: los puertos USB están habilitados sin '
         'restricción y el correo corporativo permite adjuntar archivos de cualquier tamaño a '
         'destinatarios externos sin alerta.'),
    ]),

    '8.16': ('GENERADO', [
        ('Actividades de monitoreo de la red y de los sistemas',
         2, 4,
         'No hay monitoreo de seguridad. Nadie revisa los registros y no existen alertas '
         'configuradas; los dos incidentes de 2025 los detectó un usuario, no un control.'),
    ]),

    '8.22': ('EXCEL:12.25', [
        ('Segregación de redes según criticidad y tipo de servicio',
         2, 4,
         'La red es plana: servidores, estaciones de trabajo, cámaras de CCTV y red de invitados '
         'comparten el mismo segmento y direccionamiento.'),
    ]),

    '8.23': ('GENERADO', [
        ('Filtrado del acceso a sitios web externos',
         2, 3,
         'No hay filtrado web. La navegación es libre desde todos los equipos, incluido el '
         'servidor, lo que amplia la superficie de exposición a descargas maliciosas.'),
    ]),

    '8.25': ('EXCEL:12.29', [
        ('Ciclo de vida de desarrollo seguro bajo responsabilidad de la organización',
         1, 1,
         'La organización no desarrolla software. Los ajustes a la medida sobre el ERP los ejecuta '
         'el proveedor bajo el contrato CT-2024-08; la exigencia de desarrollo seguro se gestiona '
         'por la vía contractual y se evalúa en el control 8.30. Se deja constancia para sustentar '
         'la decisión de aplicabilidad.'),
    ]),

    '8.28': ('EXCEL:12.29', [
        ('Aplicación de principios de codificación segura',
         2, 4,
         'El portal de consulta de pedidos, desarrollado por un tercero, no valida las entradas: '
         'se comprobó que el parámetro de número de pedido permite consultar pedidos de otros '
         'clientes cambiando el identificador en la URL.'),
    ]),

    '8.33': ('GENERADO', [
        ('Protección de la información utilizada para pruebas',
         2, 3,
         'La información de prueba se toma de producción sin selección, protección ni borrado '
         'posterior. No hay autorización registrada para su uso.'),
    ]),

    # ── BAJOS ────────────────────────────────────────────────────────────────
    '8.1': ('EXCEL:12.16', [
        ('Protección de los dispositivos de punto final del usuario',
         1, 2,
         'Política de dispositivos vigente, con antimalware gestionado y bloqueo de pantalla en '
         'los 22 equipos corporativos verificados.'),
    ]),

    '8.4': ('GENERADO', [
        ('Custodia y restricción del acceso al código fuente',
         1, 1,
         'La organización no custodia código fuente. El de los desarrollos a la medida reside en '
         'un repositorio privado del proveedor, con acceso nominal y registro de cambios; se '
         'verifico la lista de usuarios autorizados. Se deja constancia para la decisión de '
         'aplicabilidad.'),
    ]),

    '8.6': ('GENERADO', [
        ('Seguimiento y proyección de la capacidad de los recursos',
         1, 2,
         'Se monitorean el almacenamiento y la memoria del servidor con alertas al 80 %. La '
         'proyección de capacidad se revisa en el comité trimestral de TI.'),
    ]),

    '8.7': ('EXCEL:12.21', [
        ('Protección contra el software malicioso',
         1, 2,
         'Antimalware corporativo con consola centralizada, firmas actualizadas y análisis '
         'programado semanal. Se verifico el estado de los 22 equipos, todos al día.'),
    ]),

    '8.9': ('EXCEL:12.18', [
        ('Gestión de la configuración de los sistemas',
         1, 2,
         'Existen lineas base de configuración para estaciones y servidor, documentadas y '
         'aplicadas mediante plantilla de instalación.'),
    ]),

    '8.13': ('EXCEL:12.20', [
        ('Copias de seguridad realizadas y probadas',
         1, 2,
         'Respaldo diario incremental y semanal completo, con prueba de restauración mensual '
         'registrada. Se verifico la restauración del 04/04/2026, exitosa.'),
    ]),

    '8.14': ('EXCEL:12.38', [
        ('Redundancia de las instalaciones de procesamiento',
         1, 2,
         'El servidor tiene arreglo RAID 1 y fuente redundante. El enlace de internet cuenta con '
         'canal de contingencia de otro proveedor, probado en marzo de 2026.'),
    ]),

    '8.15': ('EXCEL:12.23', [
        ('Registro de eventos y actividades de los sistemas',
         1, 2,
         'El ERP y el directorio registran eventos de autenticación y cambios, con retención de '
         '90 días. Se verifico la disponibilidad de los registros del último trimestre.'),
    ]),

    '8.17': ('GENERADO', [
        ('Sincronización de relojes con una fuente de tiempo confiable',
         1, 2,
         'Servidor y estaciones sincronizan con el servicio NTP del proveedor de dominio. Se '
         'verifico la desviación en 5 equipos, inferior a un segundo.'),
    ]),

    '8.18': ('GENERADO', [
        ('Restricción del uso de programas de utilidad privilegiados',
         1, 2,
         'Las herramientas de administración están instaladas únicamente en el equipo del '
         'coordinador de TI, con inventario y justificación registrados.'),
    ]),

    '8.21': ('EXCEL:12.26', [
        ('Seguridad de los servicios de red contratados',
         1, 2,
         'Los servicios de red están soportados en contrato con acuerdos de nivel de servicio y '
         'cláusula de seguridad, revisados en el comité trimestral.'),
    ]),

    '8.24': ('EXCEL:12.13', [
        ('Política de uso de criptografía y gestión de claves',
         1, 2,
         'Política de criptografía vigente: TLS 1.2 o superior en los servicios publicados y '
         'cifrado del respaldo en la nube. Custodia de claves documentada.'),
    ]),

    '8.26': ('GENERADO', [
        ('Definición de los requisitos de seguridad de las aplicaciones',
         1, 2,
         'Los requisitos de seguridad se incorporan en la especificación funcional de los '
         'desarrollos. Se verifico en las dos solicitudes de cambio de 2026.'),
    ]),

    '8.27': ('GENERADO', [
        ('Principios de arquitectura de sistemas seguros',
         1, 2,
         'La arquitectura de la publicación web sigue el principio de mínima exposición: solo los '
         'puertos 443 y 80 con redirección, detras del servicio del proveedor de hosting.'),
    ]),

    '8.29': ('EXCEL:12.30', [
        ('Pruebas de seguridad durante el desarrollo y la aceptación',
         1, 2,
         'El protocolo de aceptación incluye pruebas de seguridad básicas y aprobación del dueño '
         'del proceso. Se verifico en los dos últimos pases a producción.'),
    ]),

    '8.30': ('EXCEL:12.31', [
        ('Supervisión del desarrollo contratado con externos',
         1, 2,
         'El desarrollo contratado se supervisa con entregables, revisión de avance quincenal y '
         'aceptación formal documentada.'),
    ]),

    '8.31': ('EXCEL:12.19', [
        ('Entornos de desarrollo y prueba mantenidos por la organización',
         1, 1,
         'La organización no mantiene entornos de desarrollo ni de prueba propios: los aloja y '
         'administra el proveedor del ERP, separados de producción en instancias distintas. Se '
         'verifico con el proveedor y se deja constancia para la decisión de aplicabilidad.'),
    ]),

    '8.34': ('GENERADO', [
        ('Protección de los sistemas durante las pruebas de auditoría',
         1, 2,
         'Las actividades de esta auditoría se acordaron previamente con TI, en ventana definida y '
         'con alcance de solo lectura sobre los sistemas productivos.'),
    ]),
}
