# -*- coding: utf-8 -*-
"""
Lectura de los CSV del caso de demostración.

El cargador no conoce ninguna cifra del caso: todo sale de data/demo/. Así el
equipo puede editar los CSV y volver a cargar sin tocar código.
"""
import csv
import io
import os

DIRECTORIO = os.environ.get('DEMO_DATA_DIR', '/data/demo')

ARCHIVOS = (
    'usuarios.csv',
    'diagnostico_gap.csv',
    'auditorias.csv',
    'hallazgos.csv',
    'evidencias_texto.csv',
    'planes_tratamiento.csv',
    'soa.csv',
    'documentos.csv',
)


class InsumoFaltante(Exception):
    pass


def ruta(nombre):
    return os.path.join(DIRECTORIO, nombre)


def verificar_insumos():
    """Falla temprano y con un mensaje claro si falta algún archivo."""
    if not os.path.isdir(DIRECTORIO):
        raise InsumoFaltante(
            'No existe el directorio de insumos %s. Dentro del contenedor debe estar '
            'montado ./data como /data (ver docker-compose.yml).' % DIRECTORIO)
    faltantes = [n for n in ARCHIVOS if not os.path.isfile(ruta(n))]
    if faltantes:
        raise InsumoFaltante(
            'Faltan insumos en %s: %s. Genérelos con: python scripts/generar_datos_demo.py'
            % (DIRECTORIO, ', '.join(faltantes)))


def leer(nombre):
    with io.open(ruta(nombre), encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def usuarios():
    return leer('usuarios.csv')


def auditorias():
    filas = leer('auditorias.csv')
    for fila in filas:
        fila['eliminado'] = fila['eliminado'].strip().lower() == 'si'
        fila['controles'] = int(fila['controles'])
        fila['controles_alcance'] = [c.strip() for c in
                                     fila.get('controles_alcance', '').split(',') if c.strip()]
    return filas


def hallazgos_por_auditoria(clave):
    filas = [f for f in leer('hallazgos.csv') if f['auditoria'] == clave]
    agrupados = {}
    for fila in filas:
        entrada = agrupados.setdefault(fila['control'], [])
        entrada.append({
            'criterio': fila['criterio'],
            'hallazgo': fila['hallazgo'],
            'probabilidad': int(fila['probabilidad']),
            'impacto': int(fila['impacto']),
            'nivel': int(fila['nivel']),
            'zona': fila['zona'],
            'archivo': fila['evidencia_archivo'].strip(),
        })
    return agrupados


def evidencias_texto_por_auditoria(clave):
    return {f['control']: f['evidencia_texto']
            for f in leer('evidencias_texto.csv') if f['auditoria'] == clave}


def planes_por_auditoria(clave):
    return {f['control']: f for f in leer('planes_tratamiento.csv') if f['auditoria'] == clave}


def diagnosticos():
    """{'D1': [filas], 'D2': [filas]} en el orden del archivo."""
    agrupados = {}
    for fila in leer('diagnostico_gap.csv'):
        agrupados.setdefault(fila['diagnostico'], []).append(fila)
    return agrupados


def soa():
    filas = leer('soa.csv')
    for fila in filas:
        fila['aplicable'] = fila['aplicable'].strip().lower() == 'si'
    return filas


def documentos():
    return leer('documentos.csv')
