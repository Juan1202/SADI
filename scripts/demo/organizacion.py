# -*- coding: utf-8 -*-
"""
Datos de cabecera del caso de demostracion: organizacion, fechas y usuarios.

DATOS SINTETICOS. Nada de lo que hay aqui corresponde a una organizacion real.
"""
from datetime import date

# --- Organizacion -----------------------------------------------------------

ORGANIZACION = 'Organización Demo S.A.S. (caso de demostración)'
ORGANIZACION_CORTA = 'Organización Demo S.A.S.'
NIT = '900.000.000-0 (ficticio)'
SECTOR = 'Comercio al por mayor y servicios de distribución'
EMPLEADOS = 48

# Fecha base del caso, acordada con el equipo.
FECHA_BASE = date(2026, 3, 2)

# Hitos del caso, todos derivados de la fecha base.
FECHA_DIAGNOSTICO_1 = date(2026, 3, 9)
FECHA_AUDITORIA_INTEGRAL = date(2026, 4, 13)
FECHA_AUDITORIA_TECNOLOGICA = date(2026, 6, 8)
FECHA_AUDITORIA_ORGANIZACIONAL = date(2026, 8, 17)
FECHA_AUDITORIA_PERSONAS = date(2026, 5, 11)
FECHA_AUDITORIA_VERIFICACION = date(2026, 7, 20)
FECHA_DIAGNOSTICO_2 = date(2026, 9, 14)

# Marca visible en todo lo que se carga al aplicativo.
PREFIJO_AUDITORIA = '[DEMO]'


# --- Usuarios ---------------------------------------------------------------
# La contrasena NO se escribe aqui: seed_demo_sgsi.py la genera al cargar y la
# deja en data/demo/credenciales.csv, que esta en .gitignore.

USUARIOS = [
    {
        'username': 'lvargas',
        'nombre': 'Liliana Vargas',
        'role': 'administrador',
        'cargo': 'Oficial de Seguridad de la Información (CISO)',
        'email': 'lvargas@organizaciondemo.example',
        'descripcion': 'Administra el SGSI, los usuarios y la papelera.',
    },
    {
        'username': 'jcastano',
        'nombre': 'Julián Castaño',
        'role': 'auditor',
        'cargo': 'Auditor Interno Líder',
        'email': 'jcastano@organizaciondemo.example',
        'descripcion': 'Ejecuta la auditoría integral y la del tema Tecnológico.',
    },
    {
        'username': 'pmurillo',
        'nombre': 'Paola Murillo',
        'role': 'auditor',
        'cargo': 'Auditora Interna',
        'email': 'pmurillo@organizaciondemo.example',
        'descripcion': 'Ejecuta la auditoría del tema Organizacional y la de Personas. '
                       'Su presencia permite ver el filtrado por propietario.',
    },
    {
        'username': 'dsalcedo',
        'nombre': 'Daniel Salcedo',
        'role': 'consultor',
        'cargo': 'Consultor del SGSI',
        'email': 'dsalcedo@organizaciondemo.example',
        'descripcion': 'Acompaña el diagnóstico GAP y la Declaración de Aplicabilidad.',
    },
    {
        'username': 'mrivas',
        'nombre': 'Monica Rivas',
        'role': 'lector',
        'cargo': 'Coordinación de Calidad',
        'email': 'mrivas@organizaciondemo.example',
        'descripcion': 'Solo consulta. Sirve para mostrar la matriz de permisos.',
    },
]

# Atajos para el resto de los modulos del generador.
ADMIN = 'lvargas'
AUDITOR_1 = 'jcastano'
AUDITOR_2 = 'pmurillo'
CONSULTOR = 'dsalcedo'
LECTOR = 'mrivas'


def usuario(username):
    for u in USUARIOS:
        if u['username'] == username:
            return u
    raise KeyError(username)


def nombre_de(username):
    return usuario(username)['nombre']
