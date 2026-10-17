# -*- coding: utf-8 -*-
"""
Hallazgos del dominio Fisico (A.7.1 - A.7.14), 14 controles.

DATOS SINTETICOS. Ver hallazgos_organizacional.py para la estructura.
"""

FISICO = {

    # ── ALTOS ────────────────────────────────────────────────────────────────
    '7.10': ('EXCEL:12.9', [
        ('Gestión de los medios de almacenamiento durante su ciclo de vida',
         3, 3,
         'No hay control de medios extraibles. Se encontraron 14 memorias USB sin inventariar en '
         'los puestos de trabajo, dos de ellas con copias de la base de clientes sin cifrar.'),
        ('Protección de los medios durante el transporte',
         3, 3,
         'El disco de respaldo semanal viaja a la sede alterna en el vehículo particular de un '
         'empleado, sin cifrado, sin estuche seguro y sin acta de entrega.'),
    ]),

    '7.14': ('EXCEL:12.9', [
        ('Procedimiento de eliminación o reutilización segura de equipos',
         3, 4,
         'No existe procedimiento de borrado seguro. Los 5 equipos dados de baja en 2025 se '
         'donaron con los discos intactos; uno contenía la carpeta de nómina de tres vigencias.'),
    ]),

    # ── MODERADOS ────────────────────────────────────────────────────────────
    '7.4': ('GENERADO', [
        ('Monitoreo de la seguridad física de las instalaciones',
         2, 3,
         'El CCTV cubre el acceso principal y la bodega, pero no el cuarto de comunicaciones. La '
         'grabación se conserva 7 días, por debajo de los 30 que exige el contrato con el cliente '
         'principal.'),
    ]),

    '7.5': ('GENERADO', [
        ('Protección contra amenazas físicas y ambientales',
         2, 4,
         'El cuarto de comunicaciones no tiene detección de incendio ni extintor de agente limpio. '
         'Está bajo una tubería de agua del piso superior, sin bandeja de contención.'),
    ]),

    '7.6': ('GENERADO', [
        ('Reglas para el trabajo en áreas seguras',
         2, 3,
         'No hay reglas escritas para el cuarto de comunicaciones. Se observó personal de aseo '
         'trabajando allí sin acompañamiento y con la puerta abierta.'),
    ]),

    '7.7': ('GENERADO', [
        ('Política de escritorio limpio y pantalla limpia',
         2, 3,
         'En el recorrido del 13/04/2026 se encontraron 9 de 22 puestos con documentos de clientes '
         'a la vista y 4 sesiones desbloqueadas sin usuario presente. No hay bloqueo automático '
         'configurado por directiva.'),
    ]),

    '7.8': ('EXCEL:12.15', [
        ('Ubicación y protección del equipo frente a riesgos del entorno',
         2, 4,
         'El servidor principal está en un rack abierto dentro del área de contabilidad, expuesto '
         'a polvo, a manipulación accidental y a la circulación de personal no autorizado.'),
    ]),

    '7.9': ('EXCEL:12.15', [
        ('Seguridad de los activos fuera de las instalaciones',
         2, 4,
         'Los 7 portátiles asignados a la fuerza comercial no tienen cifrado de disco ni control '
         'de borrado remoto. En 2025 se perdió uno con la cartera de clientes de la zona norte y '
         'no se pudo verificar el alcance de la exposición.'),
    ]),

    '7.12': ('GENERADO', [
        ('Protección del cableado de energía y de telecomunicaciones',
         1, 2,
         'El cableado de red del área comercial corre por el piso sin canaleta en dos tramos y el '
         'patch panel no está rotulado, lo que dificulta la trazabilidad de los puntos.'),
    ]),

    '7.13': ('EXCEL:12.18', [
        ('Mantenimiento de equipos conforme a las recomendaciones del fabricante',
         2, 2,
         'Existe cronograma de mantenimiento preventivo, pero solo se ejecutó el 60 % de las '
         'actividades programadas en 2025 y no hay registro de las dos últimas intervenciones al '
         'servidor.'),
    ]),

    # ── BAJOS ────────────────────────────────────────────────────────────────
    '7.1': ('EXCEL:12.14', [
        ('Perímetros de seguridad física definidos',
         1, 2,
         'El perímetro esta definido y documentado en el plano PL-SEG-01, con tres zonas: pública, '
         'administrativa y restringida. Se verifico en recorrido.'),
    ]),

    '7.2': ('EXCEL:12.14', [
        ('Controles de entrada física a las áreas seguras',
         1, 2,
         'El ingreso a la zona administrativa se controla con carnet de proximidad y registro de '
         'visitantes con documento. Se reviso el libro de visitantes del último trimestre.'),
    ]),

    '7.3': ('EXCEL:12.14', [
        ('Seguridad de oficinas, salas e instalaciones',
         1, 2,
         'Las áreas de tesorería y archivo tienen acceso restringido con llave controlada y '
         'relación de tenedores actualizada.'),
    ]),

    '7.11': ('EXCEL:12.39', [
        ('Protección de los servicios de suministro',
         1, 2,
         'La UPS cubre el servidor y el cuarto de comunicaciones con autonomía probada de 45 '
         'minutos. La planta eléctrica se prueba mensualmente con registro.'),
    ]),
}
