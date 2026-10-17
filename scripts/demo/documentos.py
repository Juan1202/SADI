# -*- coding: utf-8 -*-
"""
Documentos del SGSI que genera el modulo de politicas y procedimientos.

DATOS SINTETICOS.

Se generan dos politicas y un procedimiento. La politica general se edita
despues de crearse, para dejar visible el control de versiones del modulo:
la version 1.0 queda registrada en el historial y el PDF se regenera como 2.0.
"""

DOCUMENTOS = [
    {
        'clave': 'politica_general',
        'tipo': 'Política',
        'codigo': 'POL-SGSI-001',
        'titulo': 'Política General de Seguridad de la Información',
        'version': '1.0',
        'fecha_version': '2026-06-24',
        'desc_cambio': 'Emisión inicial aprobada por la gerencia.',
        'objetivo':
            'Establecer el compromiso de la dirección de Organización Demo S.A.S. con la '
            'protección de la confidencialidad, la integridad y la disponibilidad de la '
            'información, definiendo el marco de referencia para el establecimiento de objetivos '
            'de seguridad y para el cumplimiento de los requisitos legales, reglamentarios y '
            'contractuales aplicables, conforme a ISO/IEC 27001:2022.',
        'alcance':
            'Aplica a toda la información que la organización crea, recibe, procesa, almacena o '
            'transmite, en cualquier soporte, y a todo el personal vinculado, contratistas, '
            'practicantes y proveedores con acceso a los activos de información. Cubre la sede '
            'principal, la bodega y los servicios de tecnología tercerizados, según el alcance '
            'del SGSI documentado en el acta ACT-SGSI-001.',
        'responsables':
            'La Gerencia General aprueba la política y asigna los recursos. El Oficial de '
            'Seguridad de la Información mantiene el SGSI, coordina la apreciación de riesgos y '
            'reporta el desempeño. La Coordinación de TI implementa los controles técnicos. '
            'Gestión Humana gestiona los controles de personas. Los dueños de proceso responden '
            'por la información de su ámbito. Todo el personal debe cumplir la política y '
            'reportar los eventos de seguridad.',
        'marco_legal':
            'ISO/IEC 27001:2022 - Sistemas de gestión de seguridad de la información. '
            'ISO/IEC 27005:2022 - Gestión de riesgos de seguridad de la información. '
            'Ley 1273 de 2009 - Protección de la información y de los datos. '
            'Ley 1581 de 2012 y Decreto 1377 de 2013 - Protección de datos personales. '
            'CONPES 3854 de 2016 - Política Nacional de Seguridad Digital. '
            'CONPES 3995 de 2020 - Política Nacional de Confianza y Seguridad Digital.',
        'lineamientos':
            '1. La información es un activo de la organización y debe protegerse con controles '
            'proporcionales al riesgo, valorado con la matriz de probabilidad e impacto de 5x5 '
            'adoptada del estándar ISO/IEC 27005.\n'
            '2. El acceso a la información se concede bajo los principios de mínimo privilegio y '
            'necesidad de conocer, y se revisa al menos trimestralmente.\n'
            '3. Todo incidente o evento de seguridad debe reportarse por el canal definido en el '
            'procedimiento PR-SGSI-001, dentro de las cuatro horas siguientes a su detección.\n'
            '4. La información se clasifica como pública, interna o confidencial, y se etiqueta y '
            'maneja conforme a esa clasificación.\n'
            '5. Los riesgos con nivel igual o superior a 9 requieren un plan de tratamiento '
            'formal con responsable y plazo, y no pueden darse por cerrados sin evidencia de la '
            'eficacia de las acciones.\n'
            '6. Los proveedores con acceso a información de la organización deben suscribir '
            'acuerdos de confidencialidad y cláusulas de seguridad, y son objeto de seguimiento '
            'periodico.\n'
            '7. El incumplimiento de esta política se trata conforme al proceso disciplinario '
            'previsto en el reglamento interno de trabajo.\n'
            '8. Esta política se revisa anualmente y cuando ocurran cambios significativos en el '
            'contexto, en los riesgos o en los requisitos legales.',
        'elaboro': ('Liliana Vargas', 'Oficial de Seguridad de la Información'),
        'reviso': ('Julián Castaño', 'Auditor Interno Líder'),
        'aprobo': ('Dirección General', 'Gerente General'),
    },
    {
        'clave': 'politica_acceso',
        'tipo': 'Política',
        'codigo': 'POL-SGSI-002',
        'titulo': 'Política de Control de Acceso a la Información',
        'version': '1.0',
        'fecha_version': '2026-07-08',
        'desc_cambio': 'Emisión inicial. Responde al plan de tratamiento del control A.5.15, '
                       'clasificado en zona de riesgo Extrema (25) en la auditoría integral.',
        'objetivo':
            'Definir las reglas para conceder, modificar, revisar y retirar el acceso lógico y '
            'físico a la información y a los activos asociados de Organización Demo S.A.S., de '
            'modo que cada persona disponga únicamente de los permisos que su función requiere.',
        'alcance':
            'Aplica a todos los sistemas de información (ERP, correo corporativo, carpetas '
            'compartidas, portal de pedidos), a la red de datos y a las áreas físicas '
            'restringidas: cuarto de comunicaciones, tesorería y archivo de contratos. Cobija al '
            'personal vinculado, a los contratistas y a los técnicos de proveedores con acceso '
            'remoto.',
        'responsables':
            'Los dueños de proceso autorizan los accesos a la información de su ámbito. La '
            'Coordinación de TI ejecuta el aprovisionamiento y el retiro y conserva la evidencia. '
            'Gestión Humana notifica ingresos, cambios de cargo y retiros el mismo día en que se '
            'producen. El Oficial de Seguridad de la Información coordina la revisión trimestral '
            'y reporta las desviaciones al comité.',
        'marco_legal':
            'ISO/IEC 27001:2022, controles A.5.15, A.5.16, A.5.17, A.5.18, A.8.2, A.8.3 y A.8.5. '
            'Ley 1581 de 2012 y Decreto 1377 de 2013, en lo relativo al acceso a datos '
            'personales. Contratos de prestación de servicios CT-2024-08 y CT-2025-03.',
        'lineamientos':
            '1. Todo acceso se solicita por escrito a través de la mesa de servicio, con '
            'autorización del jefe inmediato y del dueño de la información.\n'
            '2. Los perfiles se definen por cargo en la matriz de perfiles MAT-ACC-2026 y siguen '
            'el principio de mínimo privilegio.\n'
            '3. Las credenciales son personales e intransferibles. Queda prohibido el uso de '
            'cuentas compartidas, incluidas las de los técnicos de proveedores.\n'
            '4. Los accesos privilegiados se conceden a cuentas nominales distintas de la cuenta '
            'de uso diario, se registran en el inventario de privilegios y se revisan '
            'mensualmente.\n'
            '5. El acceso remoto exige VPN y segundo factor de autenticación, y se registra en '
            'bitácora de sesiones.\n'
            '6. Los accesos se revisan trimestralmente con acta firmada por el dueño del proceso. '
            'Toda cuenta sin uso durante 60 días se suspende.\n'
            '7. El retiro de accesos se ejecuta el mismo día de la desvinculación o del cambio de '
            'cargo, y queda constancia en el formato de paz y salvo.\n'
            '8. El acceso físico a las áreas restringidas se controla con carnet de proximidad y '
            'llave controlada, con relación de tenedores actualizada semestralmente.',
        'elaboro': ('Liliana Vargas', 'Oficial de Seguridad de la Información'),
        'reviso': ('Paola Murillo', 'Auditora Interna'),
        'aprobo': ('Dirección General', 'Gerente General'),
    },
    {
        'clave': 'procedimiento_incidentes',
        'tipo': 'Procedimiento',
        'codigo': 'PR-SGSI-001',
        'titulo': 'Procedimiento de Gestión de Incidentes de Seguridad de la Información',
        'version': '1.0',
        'fecha_version': '2026-07-22',
        'desc_cambio': 'Emisión inicial. Incorpora los puntos de contacto con autoridades '
                       'derivados del plan de tratamiento del control A.5.5.',
        'objetivo':
            'Establecer las actividades para detectar, reportar, evaluar, responder y cerrar los '
            'incidentes de seguridad de la información, y para aprovechar el conocimiento '
            'obtenido en el fortalecimiento de los controles.',
        'alcance':
            'Cubre cualquier evento que comprometa o pueda comprometer la confidencialidad, la '
            'integridad o la disponibilidad de la información de la organización, sea de origen '
            'técnico, humano o ambiental, reportado por personal propio, por contratistas o por '
            'terceros.',
        'responsables':
            'Quien detecta el evento lo reporta. La mesa de servicio registra y realiza la '
            'primera clasificación. El Oficial de Seguridad de la Información decide si el evento '
            'se declara incidente y dirige la respuesta. La Coordinación de TI ejecuta la '
            'contención y la recuperación. La Gerencia General autoriza las notificaciones '
            'externas y a las autoridades.',
        'marco_legal':
            'ISO/IEC 27001:2022, controles A.5.24 a A.5.28 y A.6.8. Ley 1273 de 2009. '
            'Ley 1581 de 2012, articulo 17 literal n), sobre el deber de informar a la '
            'Superintendencia de Industria y Comercio las violaciones a los códigos de seguridad.',
        'lineamientos':
            '1. Reporte: el evento se reporta al buzón incidentes@organizaciondemo.example o a la '
            'extensión 120 dentro de las cuatro horas siguientes a su detección. Queda prohibido '
            'apagar, reiniciar o limpiar el equipo afectado antes de la valoración.\n'
            '2. Registro y clasificación: la mesa de servicio abre el caso con fecha, hora, '
            'origen, activos afectados y primera descripción.\n'
            '3. Evaluación: el Oficial de Seguridad determina si el evento constituye incidente y '
            'le asigna nivel de riesgo con la matriz de 5x5. Un nivel igual o superior a 9 activa '
            'la notificación inmediata a la Gerencia General.\n'
            '4. Contención: se aislan los activos afectados preservando los registros. La '
            'evidencia se recopila conforme al control A.5.28 con el apoyo forense contratado.\n'
            '5. Erradicación y recuperación: se elimina la causa, se restablece el servicio desde '
            'copias verificadas y se comprueba la ausencia de persistencia.\n'
            '6. Notificación externa: cuando el incidente afecte datos personales se notifica a la '
            'Superintendencia de Industria y Comercio y a los titulares en los términos de la Ley '
            '1581. Los contactos con el CAI Virtual de la Policía Nacional y el ColCERT figuran '
            'en el anexo 1.\n'
            '7. Cierre y lección aprendida: todo incidente se cierra con informe que identifica la '
            'causa raíz y propone al menos una acción de mejora, que se registra como plan de '
            'tratamiento en SADI.\n'
            '8. Revisión: el comité de seguridad revisa trimestralmente los incidentes del periodo '
            'y la eficacia de las acciones adoptadas.',
        'elaboro': ('Julián Castaño', 'Auditor Interno Líder'),
        'reviso': ('Liliana Vargas', 'Oficial de Seguridad de la Información'),
        'aprobo': ('Dirección General', 'Gerente General'),
    },
]

# Edicion posterior de la politica general, para mostrar el control de versiones.
EDICION = {
    'clave': 'politica_general',
    'version': '2.0',
    'desc_cambio': 'Se incorpora el numeral 9 sobre el uso de servicios en la nube y se actualiza '
                   'el numeral 2 con la periodicidad trimestral de revisión de accesos, conforme '
                   'a los hallazgos de la auditoría de seguimiento del Tema Tecnológico.',
    'lineamientos_extra':
        '\n9. Los servicios en la nube que traten información de la organización deben contratarse '
        'a nombre de la empresa, con acuerdo de nivel de servicio, ubicación de los datos '
        'declarada y procedimiento de salida documentado. Queda prohibido el uso de cuentas '
        'personales de almacenamiento para información de trabajo.',
}
