# -*- coding: utf-8 -*-
"""
Hallazgos del dominio Organizacional (A.5.1 - A.5.37), 37 controles.

DATOS SINTETICOS.

Estructura de cada entrada:
    'codigo': (origen, [(criterio, probabilidad, impacto, hallazgo), ...])

`origen` indica de donde sale la calificacion:
  * EXCEL:<pregunta>  la decidio una pregunta de la seccion 12 del instrumento
  * EXCEL-GAP:<req>   la decidio el diagnostico GAP derivado de las secciones 1-11
  * GENERADO          es una decision del caso de demostracion
"""

ORGANIZACIONAL = {

    # ── EXTREMOS ─────────────────────────────────────────────────────────────
    '5.15': ('EXCEL:12.10', [
        ('Existencia de una política de control de acceso aprobada y revisada',
         5, 5,
         'No existe política de control de acceso documentada ni aprobada. Las reglas de acceso '
         'se definen caso por caso por el contratista de TI, sin criterio escrito y sin '
         'aprobación de los dueños de la información.'),
        ('Revisión periódica de los accesos concedidos',
         5, 4,
         'No se ha ejecutado ninguna revisión de accesos desde el inicio de operaciones del ERP '
         'en 2023. Se identificaron 7 cuentas activas de personal retirado, dos de ellas con '
         'perfil de aprobación de órdenes de compra.'),
        ('Segregación entre el acceso lógico y el acceso físico a la información',
         4, 4,
         'El archivo físico de contratos de la bodega usa la misma llave maestra que la oficina '
         'de tesorería; la relación de tenedores de llave no está actualizada.'),
    ]),

    '5.19': ('EXCEL:12.32', [
        ('Proceso documentado para gestionar los riesgos de seguridad con proveedores',
         4, 5,
         'No hay proceso de gestión de riesgos de proveedores. El proveedor del ERP tiene acceso '
         'remoto permanente con credenciales de administrador compartidas entre tres técnicos, '
         'sin registro de sesiones ni ventana de mantenimiento acordada.'),
        ('Identificación de los activos de información accesibles a terceros',
         4, 4,
         'No existe inventario de qué información puede ver cada proveedor. El proveedor de '
         'nómina recibe el archivo completo de empleados, incluidos datos de salud, cuando solo '
         'requiere los campos de liquidación.'),
    ]),

    # ── ALTOS ────────────────────────────────────────────────────────────────
    '5.1': ('EXCEL-GAP:5.2', [
        ('Política de seguridad de la información aprobada por la dirección',
         3, 3,
         'La política existe como borrador desde noviembre de 2025 y no ha sido aprobada. No '
         'tiene número de versión, fecha de vigencia ni responsable de revisión.'),
        ('Comunicación y reconocimiento de la política por el personal',
         3, 3,
         'El borrador no se ha publicado. En la muestra de 8 empleados entrevistados, ninguno '
         'pudo indicar dónde consultarla.'),
    ]),

    '5.2': ('EXCEL-GAP:5.3', [
        ('Definición y asignación formal de roles de seguridad de la información',
         3, 3,
         'Los roles están enunciados en el manual de funciones pero no se asignaron nominalmente. '
         'No hay un responsable designado para la gestión de incidentes.'),
        ('Comunicación de las responsabilidades al personal involucrado',
         3, 3,
         'No hay evidencia de comunicación ni de aceptación de responsabilidades. El coordinador '
         'de TI desconocía que le corresponde reportar el desempeño del SGSI a la gerencia.'),
    ]),

    '5.5': ('EXCEL:12.4', [
        ('Contacto establecido y mantenido con las autoridades pertinentes',
         3, 3,
         'No hay puntos de contacto definidos con la Policía Nacional (CAI Virtual), la '
         'Superintendencia de Industria y Comercio ni el ColCERT. Ante un incidente no se sabría '
         'a quién notificar ni en qué plazo, pese a la obligación de la Ley 1581.'),
    ]),

    '5.14': ('EXCEL:12.27', [
        ('Reglas y acuerdos para la transferencia de información con terceros',
         3, 4,
         'No existen reglas de transferencia. Los archivos de cartera se envían a la empresa de '
         'cobranza por correo personal de Gmail y por WhatsApp, sin cifrado ni acuerdo de '
         'confidencialidad específico.'),
        ('Protección de la información durante la transferencia',
         3, 3,
         'Los respaldos que se llevan a la sede alterna viajan en un disco externo sin cifrar, '
         'en transporte público y sin registro de custodia.'),
    ]),

    '5.28': ('EXCEL:12.35', [
        ('Procedimientos para identificar, recopilar y preservar evidencias',
         3, 3,
         'No hay procedimiento de recopilación de evidencias. Tras el intento de fraude por '
         'correo de enero de 2026 se reinició el equipo afectado antes de preservar los registros, '
         'lo que impidió cualquier análisis posterior.'),
    ]),

    # ── MODERADOS ────────────────────────────────────────────────────────────
    '5.3': ('EXCEL-GAP:5.3', [
        ('Segregación de funciones en conflicto',
         2, 4,
         'La auxiliar contable registra las facturas, aprueba los pagos y concilia el extracto '
         'bancario. No hay control compensatorio documentado.'),
    ]),

    '5.6': ('EXCEL:12.4', [
        ('Contacto con grupos de interés especiales y foros de seguridad',
         2, 3,
         'La organización no participa en ningún foro sectorial ni recibe boletines de seguridad. '
         'La información sobre amenazas llega de forma incidental por redes sociales.'),
    ]),

    '5.7': ('GENERADO', [
        ('Recopilación y análisis de inteligencia de amenazas',
         2, 3,
         'No se recopila información de amenazas. No hay suscripción a avisos del proveedor del '
         'ERP ni a alertas de vulnerabilidades de los productos en uso.'),
    ]),

    '5.12': ('GENERADO', [
        ('Esquema de clasificación de la información definido y aplicado',
         2, 4,
         'No hay esquema de clasificación. La información comercial, la de nómina y la pública se '
         'guardan en la misma carpeta compartida con permisos de lectura para todo el dominio.'),
    ]),

    '5.13': ('GENERADO', [
        ('Procedimientos de etiquetado acordes al esquema de clasificación',
         2, 3,
         'Al no existir clasificación, tampoco hay etiquetado. Los documentos impresos con datos '
         'de clientes no llevan marca de confidencialidad.'),
    ]),

    '5.21': ('EXCEL:12.32', [
        ('Gestión de riesgos en la cadena de suministro de productos y servicios TIC',
         2, 4,
         'No se evalúa la seguridad de los proveedores antes de contratarlos. El hosting del sitio '
         'web se contrató por precio, sin revisar certificaciones ni ubicación de los datos.'),
    ]),

    '5.23': ('GENERADO', [
        ('Requisitos de seguridad para la adquisición y uso de servicios en la nube',
         2, 4,
         'Se usan Google Drive y Dropbox personales para documentos de trabajo, sin contrato '
         'empresarial, sin control de la organización sobre las cuentas y sin proceso de salida.'),
    ]),

    '5.25': ('EXCEL:12.35', [
        ('Evaluación de eventos y decisión sobre su clasificación como incidentes',
         2, 3,
         'Los eventos se atienden por teléfono con el contratista de TI. No hay criterio para '
         'decidir cuándo un evento es un incidente ni quién lo declara.'),
    ]),

    '5.27': ('GENERADO', [
        ('Uso del conocimiento de los incidentes para fortalecer los controles',
         2, 3,
         'Los dos incidentes de 2025 no generaron lección aprendida ni cambio en los controles. '
         'El mismo vector de correo fraudulento se repitió en enero de 2026.'),
    ]),

    '5.29': ('EXCEL:12.37', [
        ('Mantenimiento de la seguridad de la información durante la interrupción',
         2, 4,
         'El plan de continuidad cubre la operación comercial pero no define como se preserva la '
         'confidencialidad de la información cuando se opera desde la sede alterna.'),
    ]),

    '5.30': ('EXCEL:12.37', [
        ('Preparación de TIC para la continuidad del negocio, probada periódicamente',
         2, 4,
         'Existen objetivos de recuperación verbales (RTO de 4 horas) pero nunca se han probado. '
         'La última prueba de restauración documentada es de 2024.'),
    ]),

    '5.32': ('EXCEL:12.41', [
        ('Procedimientos para proteger los derechos de propiedad intelectual',
         2, 3,
         'No hay inventario de licencias. Se identificaron 6 equipos con software de diseño sin '
         'licencia vigente y una hoja de cálculo de gestión desarrollada por un exempleado sin '
         'acuerdo de cesión de derechos.'),
    ]),

    '5.34': ('EXCEL:12.41', [
        ('Cumplimiento de los requisitos de privacidad y protección de datos personales',
         2, 4,
         'No se ha registrado la base de datos de clientes ante el RNBD de la SIC. El aviso de '
         'privacidad del sitio web no describe las finalidades del tratamiento ni el procedimiento '
         'para ejercer los derechos del titular (Ley 1581 y Decreto 1377).'),
    ]),

    # ── BAJOS ────────────────────────────────────────────────────────────────
    '5.4': ('EXCEL:12.2', [
        ('La dirección exige la aplicación de la seguridad de la información',
         1, 2,
         'La gerencia trata la seguridad de la información como punto fijo del comité mensual. '
         'Se revisaron las actas de los últimos seis meses, todas con seguimiento a compromisos.'),
    ]),

    '5.8': ('EXCEL:12.5b', [
        ('Integración de la seguridad de la información en la gestión de proyectos',
         1, 2,
         'La plantilla de acta de inicio de proyecto incluye el apartado de requisitos de '
         'seguridad. Se verifico su diligenciamiento en los tres proyectos de 2026.'),
    ]),

    '5.9': ('EXCEL:12.8', [
        ('Inventario de información y otros activos asociados, con propietarios asignados',
         1, 2,
         'Inventario INV-ACT-2026 actualizado en febrero, con 132 activos y propietario asignado. '
         'Se verifico por muestreo de 12 activos, todos localizados.'),
    ]),

    '5.10': ('EXCEL:12.28', [
        ('Reglas de uso aceptable de la información y de los activos',
         1, 2,
         'El reglamento interno de trabajo incorpora las reglas de uso aceptable y se firma en la '
         'inducción. Se verificaron 10 expedientes, todos con la constancia firmada.'),
    ]),

    '5.11': ('GENERADO', [
        ('Devolución de activos al terminar el empleo o el contrato',
         1, 2,
         'El formato de paz y salvo incluye la devolución de equipos, carnet y llaves. Se revisaron '
         'las 4 desvinculaciones de 2026, todas con formato completo.'),
    ]),

    '5.16': ('EXCEL:12.11', [
        ('Gestión del ciclo de vida completo de las identidades',
         1, 2,
         'Existe procedimiento formal de alta y baja de usuarios con solicitud del jefe inmediato. '
         'Se verificaron las 11 altas de 2026.'),
    ]),

    '5.17': ('EXCEL:12.13', [
        ('Gestión controlada de la información de autenticación',
         1, 2,
         'Las credenciales iniciales se entregan en sobre cerrado con cambio obligatorio en el '
         'primer ingreso. Política de complejidad activa en el directorio.'),
    ]),

    '5.18': ('EXCEL:12.11', [
        ('Aprovisionamiento, revisión y retiro de derechos de acceso',
         1, 2,
         'El aprovisionamiento sigue la matriz de perfiles por cargo. El retiro esta cubierto por '
         'el procedimiento de desvinculación, con constancia en los 4 casos de 2026.'),
    ]),

    '5.20': ('EXCEL:12.33', [
        ('Requisitos de seguridad acordados en los contratos con proveedores',
         1, 2,
         'Los contratos de los cinco proveedores críticos incluyen cláusula de confidencialidad y '
         'de tratamiento de datos personales, revisada por el área jurídica.'),
    ]),

    '5.22': ('EXCEL:12.26', [
        ('Seguimiento y revisión de los servicios prestados por los proveedores',
         1, 2,
         'Se realizan comités trimestrales de servicio con el proveedor del ERP y del hosting, con '
         'acta y acuerdos de nivel de servicio revisados.'),
    ]),

    '5.24': ('EXCEL:12.34', [
        ('Planificación y preparación de la gestión de incidentes',
         1, 2,
         'Existe procedimiento de gestión de incidentes PR-TI-004 con roles, canal de reporte y '
         'escalamiento definidos.'),
    ]),

    '5.26': ('EXCEL:12.34', [
        ('Respuesta a incidentes conforme a los procedimientos documentados',
         1, 2,
         'Los dos incidentes registrados en 2026 se atendieron según el procedimiento, con '
         'registro de tiempos de detección y de cierre.'),
    ]),

    '5.31': ('EXCEL:12.40', [
        ('Identificación y actualización de los requisitos legales y contractuales',
         1, 2,
         'Matriz legal MAT-LEG-2026 actualizada, con Ley 1273, Ley 1581, Decreto 1377 y las '
         'obligaciones contractuales de los cinco clientes principales.'),
    ]),

    '5.33': ('GENERADO', [
        ('Protección de los registros contra pérdida y acceso no autorizado',
         1, 2,
         'Los registros contables y laborales se conservan con respaldo diario y acceso '
         'restringido al área correspondiente. Tabla de retención documental vigente.'),
    ]),

    '5.35': ('EXCEL:12.42', [
        ('Revisión independiente de la seguridad de la información',
         1, 2,
         'La revisión independiente la realiza la auditoría interna con el programa aprobado por '
         'la gerencia. Esta auditoría es parte de esa evidencia.'),
    ]),

    '5.36': ('EXCEL:12.42', [
        ('Cumplimiento de políticas, reglas y estándares de seguridad',
         1, 2,
         'El comité de seguridad revisa el cumplimiento a intervalos programados y deja constancia '
         'en acta. Se revisaron las actas de los últimos seis meses.'),
    ]),

    '5.37': ('EXCEL:12.1', [
        ('Procedimientos de operación documentados y disponibles',
         1, 2,
         'Los procedimientos de operación de TI están documentados y disponibles en la carpeta de '
         'calidad. Se verifico la vigencia de los seis procedimientos del proceso.'),
    ]),
}
