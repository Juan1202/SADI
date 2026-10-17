from main import app, db
from models import Control, Usuario

CONTROLES = [
    # ORGANIZACIONAL (5.1 - 5.37)
    ('5.1',  'Políticas para la seguridad de la información', 'Las políticas de seguridad de la información y las políticas específicas del tema deben definirse, aprobarse por la dirección, publicarse, comunicarse y reconocerse por el personal pertinente y las partes interesadas pertinentes, revisarse a intervalos planificados y si ocurren cambios significativos.', 'Organizacional'),
    ('5.2',  'Roles y responsabilidades de seguridad de la información', 'Los roles y responsabilidades de seguridad de la información deben definirse y asignarse de acuerdo con las necesidades de la organización.', 'Organizacional'),
    ('5.3',  'Segregación de funciones', 'Deben segregarse las funciones en conflicto y las áreas de responsabilidad en conflicto.', 'Organizacional'),
    ('5.4',  'Responsabilidades de la dirección', 'La dirección debe exigir a todo el personal que aplique la seguridad de la información de acuerdo con las políticas, normas y procedimientos de seguridad de la información establecidos por la organización.', 'Organizacional'),
    ('5.5',  'Contacto con autoridades', 'La organización debe establecer y mantener contacto con las autoridades pertinentes.', 'Organizacional'),
    ('5.6',  'Contacto con grupos de interés especiales', 'La organización debe establecer y mantener contacto con grupos de interés especiales u otros foros de seguridad especializados y asociaciones profesionales.', 'Organizacional'),
    ('5.7',  'Inteligencia de amenazas', 'Se debe recopilar y analizar información relacionada con las amenazas a la seguridad de la información y producir inteligencia de amenazas.', 'Organizacional'),
    ('5.8',  'Seguridad de la información en la gestión de proyectos', 'La seguridad de la información debe integrarse en la gestión de proyectos.', 'Organizacional'),
    ('5.9',  'Inventario de información y otros activos asociados', 'Se debe identificar un inventario de información y otros activos asociados, incluidos los propietarios, y se debe elaborar y mantener.', 'Organizacional'),
    ('5.10', 'Uso aceptable de la información y otros activos asociados', 'Deben identificarse, documentarse e implementarse reglas para el uso aceptable y procedimientos para el manejo de la información y otros activos asociados.', 'Organizacional'),
    ('5.11', 'Devolución de activos', 'El personal y otras partes interesadas, según corresponda, deben devolver todos los activos de la organización en su posesión al terminar su empleo, contrato o acuerdo.', 'Organizacional'),
    ('5.12', 'Clasificación de la información', 'La información debe clasificarse de acuerdo con las necesidades de seguridad de la información de la organización en función de la confidencialidad, integridad, disponibilidad y requisitos relevantes de las partes interesadas.', 'Organizacional'),
    ('5.13', 'Etiquetado de la información', 'Se debe desarrollar e implementar un conjunto apropiado de procedimientos para el etiquetado de la información de acuerdo con el esquema de clasificación de la información adoptado por la organización.', 'Organizacional'),
    ('5.14', 'Transferencia de información', 'Deben existir reglas, procedimientos o acuerdos de transferencia de información para todos los tipos de instalaciones de transferencia dentro de la organización y entre la organización y otras partes.', 'Organizacional'),
    ('5.15', 'Control de acceso', 'Deben establecerse e implementarse reglas para controlar el acceso físico y lógico a la información y otros activos asociados en función de los requisitos de seguridad de la información y de negocio.', 'Organizacional'),
    ('5.16', 'Gestión de identidades', 'Debe gestionarse el ciclo de vida completo de las identidades.', 'Organizacional'),
    ('5.17', 'Información de autenticación', 'La asignación y gestión de la información de autenticación debe ser controlada por un proceso de gestión, incluyendo asesorar al personal sobre el manejo apropiado de la información de autenticación.', 'Organizacional'),
    ('5.18', 'Derechos de acceso', 'Los derechos de acceso a la información y otros activos asociados deben aprovisionarse, revisarse, modificarse y retirarse de acuerdo con la política de control de acceso y las reglas específicas del tema de la organización.', 'Organizacional'),
    ('5.19', 'Seguridad de la información en las relaciones con los proveedores', 'Se deben definir e implementar procesos y procedimientos para gestionar los riesgos de seguridad de la información asociados con el uso de los productos o servicios del proveedor.', 'Organizacional'),
    ('5.20', 'Abordar la seguridad de la información en los acuerdos con proveedores', 'Los requisitos de seguridad de la información pertinentes deben establecerse y acordarse con cada proveedor en función del tipo de relación con el proveedor.', 'Organizacional'),
    ('5.21', 'Gestión de la seguridad de la información en la cadena de suministro de TIC', 'Se deben definir e implementar procesos y procedimientos para gestionar los riesgos de seguridad de la información asociados con la cadena de suministro de productos y servicios de TIC.', 'Organizacional'),
    ('5.22', 'Seguimiento, revisión y gestión de cambios de los servicios de los proveedores', 'La organización debe monitorear, revisar, evaluar y gestionar regularmente el cambio en las prácticas de seguridad de la información del proveedor y la entrega de servicios.', 'Organizacional'),
    ('5.23', 'Seguridad de la información para el uso de servicios en la nube', 'Los procesos de adquisición, uso, gestión y salida de servicios en la nube deben establecerse de acuerdo con los requisitos de seguridad de la información de la organización.', 'Organizacional'),
    ('5.24', 'Planificación y preparación de la gestión de incidentes de seguridad de la información', 'La organización debe planificar y prepararse para gestionar los incidentes de seguridad de la información definiendo, estableciendo y comunicando procesos, roles y responsabilidades de gestión de incidentes de seguridad de la información.', 'Organizacional'),
    ('5.25', 'Evaluación y decisión sobre eventos de seguridad de la información', 'La organización debe evaluar los eventos de seguridad de la información y decidir si deben clasificarse como incidentes de seguridad de la información.', 'Organizacional'),
    ('5.26', 'Respuesta a incidentes de seguridad de la información', 'Los incidentes de seguridad de la información deben responderse de acuerdo con los procedimientos documentados.', 'Organizacional'),
    ('5.27', 'Aprender de los incidentes de seguridad de la información', 'El conocimiento obtenido de los incidentes de seguridad de la información debe utilizarse para fortalecer y mejorar los controles de seguridad de la información.', 'Organizacional'),
    ('5.28', 'Recopilación de evidencias', 'La organización debe establecer e implementar procedimientos para la identificación, recopilación, adquisición y preservación de evidencias relacionadas con eventos de seguridad de la información.', 'Organizacional'),
    ('5.29', 'Seguridad de la información durante la interrupción', 'La organización debe planificar cómo mantener la seguridad de la información en un nivel apropiado durante la interrupción.', 'Organizacional'),
    ('5.30', 'Preparación de TIC para la continuidad del negocio', 'La preparación de TIC debe planificarse, implementarse, mantenerse y probarse en función de los objetivos de continuidad del negocio y los requisitos de continuidad de TIC.', 'Organizacional'),
    ('5.31', 'Requisitos legales, estatutarios, reglamentarios y contractuales', 'Los requisitos legales, estatutarios, reglamentarios y contractuales relevantes para la seguridad de la información y el enfoque de la organización para cumplir estos requisitos deben identificarse, documentarse y mantenerse actualizados.', 'Organizacional'),
    ('5.32', 'Derechos de propiedad intelectual', 'La organización debe implementar procedimientos apropiados para proteger los derechos de propiedad intelectual.', 'Organizacional'),
    ('5.33', 'Protección de registros', 'Los registros deben protegerse contra pérdida, destrucción, falsificación, acceso no autorizado y divulgación no autorizada.', 'Organizacional'),
    ('5.34', 'Privacidad y protección de la información personal', 'La organización debe identificar y cumplir los requisitos relacionados con la preservación de la privacidad y la protección de la información personal de acuerdo con las leyes y regulaciones aplicables.', 'Organizacional'),
    ('5.35', 'Revisión independiente de la seguridad de la información', 'El enfoque de la organización para gestionar la seguridad de la información y su implementación, incluidas las personas, los procesos y las tecnologías, deben revisarse de forma independiente a intervalos planificados o cuando se produzcan cambios significativos.', 'Organizacional'),
    ('5.36', 'Cumplimiento de las políticas, reglas y estándares de seguridad de la información', 'El cumplimiento de la política de seguridad de la información, las políticas específicas del tema, las reglas y los estándares de la organización deben revisarse regularmente.', 'Organizacional'),
    ('5.37', 'Procedimientos de operación documentados', 'Los procedimientos de operación para las instalaciones de procesamiento de información deben documentarse y ponerse a disposición del personal que los necesite.', 'Organizacional'),
    # PERSONAS (6.1 - 6.8)
    ('6.1',  'Investigación de antecedentes', 'La verificación de antecedentes de todos los candidatos debe llevarse a cabo antes de unirse a la organización y de forma continua teniendo en cuenta las leyes, regulaciones y ética aplicables y ser proporcional a los requisitos del negocio, la clasificación de la información a la que se va a acceder y los riesgos percibidos.', 'Personas'),
    ('6.2',  'Términos y condiciones de empleo', 'Los acuerdos contractuales con el personal deben establecer sus responsabilidades y las de la organización en materia de seguridad de la información.', 'Personas'),
    ('6.3',  'Concienciación, educación y formación en seguridad de la información', 'El personal de la organización y las partes interesadas pertinentes deben recibir la concienciación, educación y formación adecuadas en seguridad de la información, y actualizaciones periódicas de la política de seguridad de la información de la organización, las políticas y procedimientos específicos del tema, según corresponda a su función laboral.', 'Personas'),
    ('6.4',  'Proceso disciplinario', 'Debe existir un proceso disciplinario y debe comunicarse y aplicarse para tomar medidas contra el personal y otras partes interesadas pertinentes que hayan cometido una violación de la política de seguridad de la información.', 'Personas'),
    ('6.5',  'Responsabilidades tras el cese o cambio de empleo', 'Las responsabilidades y obligaciones de seguridad de la información que siguen siendo válidas después del cese o cambio de empleo deben definirse, aplicarse y comunicarse al personal pertinente y otras partes interesadas.', 'Personas'),
    ('6.6',  'Acuerdos de confidencialidad o no divulgación', 'Los acuerdos de confidencialidad o no divulgación que reflejen las necesidades de la organización para la protección de la información deben identificarse, documentarse, revisarse regularmente y firmarse por el personal y otras partes interesadas pertinentes.', 'Personas'),
    ('6.7',  'Trabajo remoto', 'Se deben implementar medidas de seguridad cuando el personal trabaja de forma remota para proteger la información a la que se accede, se procesa o se almacena fuera de las instalaciones de la organización.', 'Personas'),
    ('6.8',  'Notificación de eventos de seguridad de la información', 'La organización debe proporcionar un mecanismo para que el personal notifique los eventos de seguridad de la información observados o sospechados a través de los canales apropiados de manera oportuna.', 'Personas'),
    # FISICO (7.1 - 7.14)
    ('7.1',  'Perímetros de seguridad física', 'Deben definirse y usarse perímetros de seguridad para proteger las áreas que contienen información y otros activos asociados.', 'Físico'),
    ('7.2',  'Entrada física', 'Las áreas seguras deben protegerse mediante controles de entrada apropiados y puntos de acceso.', 'Físico'),
    ('7.3',  'Seguridad de oficinas, salas e instalaciones', 'La seguridad física de las oficinas, salas e instalaciones debe diseñarse e implementarse.', 'Físico'),
    ('7.4',  'Monitoreo de la seguridad física', 'Las instalaciones deben monitorearse continuamente para detectar el acceso físico no autorizado.', 'Físico'),
    ('7.5',  'Protección contra amenazas físicas y ambientales', 'Debe diseñarse y aplicarse protección contra amenazas físicas y ambientales, como desastres naturales y otros desastres físicos intencionales o no intencionales a la infraestructura.', 'Físico'),
    ('7.6',  'Trabajo en áreas seguras', 'Deben diseñarse e implementarse medidas de seguridad para trabajar en áreas seguras.', 'Físico'),
    ('7.7',  'Escritorio limpio y pantalla limpia', 'Deben definirse e implementarse adecuadamente reglas de escritorio limpio para papeles y medios de almacenamiento extraíbles y reglas de pantalla limpia para las instalaciones de procesamiento de información.', 'Físico'),
    ('7.8',  'Ubicación y protección del equipo', 'El equipo debe ubicarse de forma segura y protegerse.', 'Físico'),
    ('7.9',  'Seguridad de los activos fuera de las instalaciones', 'Los activos fuera del sitio deben protegerse.', 'Físico'),
    ('7.10', 'Medios de almacenamiento', 'Los medios de almacenamiento deben gestionarse a lo largo de su ciclo de vida de adquisición, uso, transporte y eliminación de acuerdo con el esquema de clasificación y los requisitos de manejo de la organización.', 'Físico'),
    ('7.11', 'Servicios de suministro', 'Las instalaciones de procesamiento de información deben protegerse de fallos de energía y otras interrupciones causadas por fallos en los servicios de suministro.', 'Físico'),
    ('7.12', 'Seguridad del cableado', 'Los cables que transportan energía, datos o servicios de información de soporte deben protegerse contra interceptación, interferencia o daño.', 'Físico'),
    ('7.13', 'Mantenimiento de equipos', 'El equipo debe mantenerse correctamente para garantizar la disponibilidad, integridad y confidencialidad de la información.', 'Físico'),
    ('7.14', 'Eliminación o reutilización segura del equipo', 'Los elementos del equipo que contengan medios de almacenamiento deben verificarse para asegurar que los datos confidenciales y el software con licencia se hayan eliminado o sobrescrito de forma segura antes de su eliminación o reutilización.', 'Físico'),
    # TECNOLOGICO (8.1 - 8.34)
    ('8.1',  'Dispositivos de punto final del usuario', 'La información almacenada en, procesada por o accesible a través de dispositivos de punto final del usuario debe protegerse.', 'Tecnológico'),
    ('8.2',  'Derechos de acceso privilegiado', 'La asignación y el uso de derechos de acceso privilegiado deben restringirse y gestionarse.', 'Tecnológico'),
    ('8.3',  'Restricción de acceso a la información', 'El acceso a la información y otros activos asociados debe restringirse de acuerdo con la política de control de acceso establecida y específica del tema.', 'Tecnológico'),
    ('8.4',  'Acceso al código fuente', 'El acceso de lectura y escritura al código fuente, las herramientas de desarrollo y las bibliotecas de software debe gestionarse adecuadamente.', 'Tecnológico'),
    ('8.5',  'Autenticación segura', 'Se deben implementar tecnologías y procedimientos de autenticación segura basados en restricciones de acceso a la información y la política de control de acceso específica del tema.', 'Tecnológico'),
    ('8.6',  'Gestión de la capacidad', 'El uso de los recursos debe monitorearse y ajustarse en línea con los requisitos de capacidad actuales y esperados.', 'Tecnológico'),
    ('8.7',  'Protección contra malware', 'La protección contra malware debe implementarse y respaldarse mediante la concienciación adecuada del usuario.', 'Tecnológico'),
    ('8.8',  'Gestión de vulnerabilidades técnicas', 'Debe obtenerse información sobre las vulnerabilidades técnicas de los sistemas de información en uso, evaluarse la exposición de la organización a dichas vulnerabilidades y tomarse las medidas apropiadas.', 'Tecnológico'),
    ('8.9',  'Gestión de la configuración', 'Las configuraciones, incluidas las configuraciones de seguridad, del hardware, software, servicios y redes deben establecerse, documentarse, implementarse, monitorearse y revisarse.', 'Tecnológico'),
    ('8.10', 'Eliminación de información', 'La información almacenada en sistemas de información, dispositivos o en cualquier otro medio de almacenamiento debe eliminarse cuando ya no sea necesaria.', 'Tecnológico'),
    ('8.11', 'Enmascaramiento de datos', 'El enmascaramiento de datos debe usarse de acuerdo con la política de control de acceso específica del tema de la organización y otros requisitos específicos del tema relacionados, y los requisitos del negocio, teniendo en cuenta la legislación aplicable.', 'Tecnológico'),
    ('8.12', 'Prevención de fuga de datos', 'Las medidas de prevención de fuga de datos deben aplicarse a los sistemas, redes y otros dispositivos que procesan, almacenan o transmiten información sensible.', 'Tecnológico'),
    ('8.13', 'Copia de seguridad de la información', 'Las copias de seguridad de la información, el software y los sistemas deben mantenerse y probarse regularmente de acuerdo con la política de copia de seguridad acordada específica del tema.', 'Tecnológico'),
    ('8.14', 'Redundancia de las instalaciones de procesamiento de información', 'Las instalaciones de procesamiento de información deben implementarse con redundancia suficiente para cumplir los requisitos de disponibilidad.', 'Tecnológico'),
    ('8.15', 'Registro de actividad (logging)', 'Deben producirse, almacenarse, protegerse y analizarse registros que registren actividades, excepciones, fallas y otros eventos relevantes.', 'Tecnológico'),
    ('8.16', 'Actividades de monitoreo', 'Las redes, los sistemas y las aplicaciones deben monitorearse para detectar comportamientos anómalos y deben tomarse las acciones apropiadas para evaluar los posibles incidentes de seguridad de la información.', 'Tecnológico'),
    ('8.17', 'Sincronización del reloj', 'Los relojes de los sistemas de procesamiento de información utilizados por la organización deben sincronizarse con fuentes de tiempo de referencia aprobadas.', 'Tecnológico'),
    ('8.18', 'Uso de programas de utilidades privilegiados', 'El uso de programas de utilidades que puedan ser capaces de anular los controles del sistema y la aplicación debe restringirse y controlarse estrictamente.', 'Tecnológico'),
    ('8.19', 'Instalación de software en sistemas operativos', 'Deben implementarse procedimientos y medidas para gestionar de forma segura la instalación de software en los sistemas operativos.', 'Tecnológico'),
    ('8.20', 'Seguridad de redes', 'Las redes y los dispositivos de red deben protegerse, gestionarse y controlarse para proteger la información en los sistemas y aplicaciones.', 'Tecnológico'),
    ('8.21', 'Seguridad de los servicios de red', 'Los mecanismos de seguridad, los niveles de servicio y los requisitos de servicio de todos los servicios de red deben identificarse, implementarse y monitorearse.', 'Tecnológico'),
    ('8.22', 'Segregación de redes', 'Los grupos de servicios de información, usuarios y sistemas de información deben segregarse en las redes de la organización.', 'Tecnológico'),
    ('8.23', 'Filtrado web', 'El acceso a sitios web externos debe gestionarse para reducir la exposición a contenido malicioso.', 'Tecnológico'),
    ('8.24', 'Uso de criptografía', 'Deben definirse e implementarse reglas para el uso efectivo de la criptografía, incluida la gestión de claves criptográficas.', 'Tecnológico'),
    ('8.25', 'Ciclo de vida de desarrollo seguro', 'Deben establecerse e implementarse reglas para el desarrollo seguro de software y sistemas.', 'Tecnológico'),
    ('8.26', 'Requisitos de seguridad de las aplicaciones', 'Los requisitos de seguridad de la información deben identificarse, especificarse y aprobarse cuando se desarrollan o adquieren aplicaciones.', 'Tecnológico'),
    ('8.27', 'Principios de arquitectura de sistemas seguros', 'Los principios para diseñar sistemas seguros deben establecerse, documentarse, mantenerse y aplicarse a cualquier actividad de desarrollo de sistemas de información.', 'Tecnológico'),
    ('8.28', 'Codificación segura', 'Los principios de codificación segura deben aplicarse al desarrollo de software.', 'Tecnológico'),
    ('8.29', 'Pruebas de seguridad en desarrollo y aceptación', 'Los procesos de prueba de seguridad deben definirse e implementarse en el ciclo de vida del desarrollo.', 'Tecnológico'),
    ('8.30', 'Desarrollo subcontratado', 'La organización debe dirigir, monitorear y revisar las actividades relacionadas con el desarrollo de sistemas subcontratados.', 'Tecnológico'),
    ('8.31', 'Separación de los entornos de desarrollo, prueba y producción', 'Los entornos de desarrollo, prueba y producción deben separarse y asegurarse.', 'Tecnológico'),
    ('8.32', 'Gestión de cambios', 'Los cambios en las instalaciones de procesamiento de información y los sistemas de información deben estar sujetos a procedimientos de gestión de cambios.', 'Tecnológico'),
    ('8.33', 'Información de prueba', 'La información de prueba debe seleccionarse, protegerse y gestionarse adecuadamente.', 'Tecnológico'),
    ('8.34', 'Protección de los sistemas de información durante las pruebas de auditoría', 'Las pruebas de auditoría y otras actividades de aseguramiento que implican la evaluación de los sistemas operativos deben planificarse y acordarse entre el evaluador y la dirección apropiada.', 'Tecnológico'),
]

with app.app_context():
    # Corregir rol admin
    u = Usuario.query.filter_by(username='admin_sadi').first()
    if u and u.role != 'administrador':
        u.role = 'administrador'
        db.session.commit()
        print('Rol admin corregido a: administrador')
    else:
        print('Rol admin ya es correcto:', u.role if u else 'usuario no encontrado')

    # Cargar controles
    existentes = {c.codigo for c in Control.query.all()}
    nuevos = 0
    for codigo, nombre, descripcion, dominio in CONTROLES:
        if codigo not in existentes:
            c = Control(codigo=codigo, nombre=nombre, descripcion=descripcion, dominio=dominio)
            db.session.add(c)
            nuevos += 1
    db.session.commit()

    total = Control.query.count()
    print(f'Controles nuevos cargados: {nuevos}')
    print(f'Total controles en BD: {total}')
    por_dominio = {}
    for c in Control.query.all():
        por_dominio[c.dominio] = por_dominio.get(c.dominio, 0) + 1
    for dominio, cnt in sorted(por_dominio.items()):
        print(f'  {dominio}: {cnt}')
