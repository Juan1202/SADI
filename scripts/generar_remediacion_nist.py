"""
Genera app/data/remediacion_nist.json: la base de conocimiento del modulo de
sugerencias de remediacion (app/remediacion.py).

El archivo se construye SOLO a partir de dos fuentes publicadas, sin
correspondencias redactadas a mano:

  1. Correspondencia ISO/IEC 27001:2022 <-> NIST SP 800-53 Rev. 5
     NIST OLIR, Informative Reference 155
     (sp800-53r5-to-iso-27001-mapping-2022-OLIR-2023-10-12-UPDATED.xlsx),
     en la version normalizada que distribuye CISO Assistant (intuitem):
     backend/library/libraries/mapping-nist-sp-800-53-rev5-to-iso27001-2022.yaml
     https://github.com/intuitem/ciso-assistant-community

  2. Catalogo oficial NIST SP 800-53 Rev. 5 en OSCAL (titulos y enunciados):
     https://github.com/usnistgov/oscal-content
     nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json

Uso:
    python scripts/generar_remediacion_nist.py \
        --mapeo mapping-nist-sp-800-53-rev5-to-iso27001-2022.yaml \
        --catalogo NIST_SP-800-53_rev5_catalog.json \
        --salida app/data/remediacion_nist.json

No se publica texto de la norma ISO (protegido por derechos de autor): solo
los identificadores de sus controles. El texto de NIST es de dominio publico.
"""
import argparse
import hashlib
import json
import re
from datetime import date

import yaml

FAMILIAS_ES = {
    'AC': 'Control de acceso',
    'AT': 'Concienciación y formación',
    'AU': 'Auditoría y trazabilidad',
    'CA': 'Evaluación, autorización y monitoreo',
    'CM': 'Gestión de la configuración',
    'CP': 'Planes de contingencia',
    'IA': 'Identificación y autenticación',
    'IR': 'Respuesta a incidentes',
    'MA': 'Mantenimiento',
    'MP': 'Protección de medios',
    'PE': 'Protección física y ambiental',
    'PL': 'Planificación',
    'PM': 'Gestión del programa',
    'PS': 'Seguridad del personal',
    'PT': 'Tratamiento de datos personales y transparencia',
    'RA': 'Evaluación de riesgos',
    'SA': 'Adquisición de sistemas y servicios',
    'SC': 'Protección de sistemas y comunicaciones',
    'SI': 'Integridad del sistema y de la información',
    'SR': 'Gestión del riesgo de la cadena de suministro',
}


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(65536), b''):
            h.update(bloque)
    return h.hexdigest()


def id_desde_oscal(oscal_id):
    """ac-2.12 -> AC-2(12)"""
    base, _, mejora = oscal_id.partition('.')
    base = base.upper()
    return f'{base}({mejora})' if mejora else base


def id_desde_mapeo(valor):
    """ac-2(12) -> AC-2(12)"""
    return valor.strip().upper()


def texto_parametro(param):
    if 'select' in param:
        sel = param['select']
        opciones = '; '.join(_limpiar(c) for c in sel.get('choice', []))
        cuantos = 'una o más' if sel.get('how-many') == 'one-or-more' else 'una'
        return f'[Selección ({cuantos}): {opciones}]'
    etiqueta = param.get('label') or param['id']
    return f'[Asignación: {_limpiar(etiqueta)}]'


def _limpiar(texto):
    return re.sub(r'\s+', ' ', str(texto)).strip()


def enunciado(control, params):
    """Concatena las partes 'statement' del control en texto plano."""
    lineas = []

    def sustituir(prosa):
        return re.sub(r'\{\{\s*insert:\s*param,\s*([^}\s]+)\s*\}\}',
                      lambda m: params.get(m.group(1), f'[{m.group(1)}]'), prosa)

    def recorrer(parte, nivel):
        etiqueta = next((p['value'] for p in parte.get('props', [])
                         if p['name'] == 'label'), '')
        prosa = parte.get('prose')
        if prosa:
            texto = re.sub(r'\s+([;,.:])', r'\1', _limpiar(sustituir(prosa)))
            lineas.append(('  ' * nivel) + (f'{etiqueta} ' if etiqueta else '') + texto)
        for sub in parte.get('parts', []):
            recorrer(sub, nivel + (1 if prosa else 0))

    for parte in control.get('parts', []):
        if parte.get('name') == 'statement':
            recorrer(parte, 0)
    return '\n'.join(lineas)


def indexar_catalogo(catalogo):
    params = {}
    controles = {}

    def visitar(ctrl, familia):
        for p in ctrl.get('params', []):
            params[p['id']] = texto_parametro(p)
        retirado = any(p['name'] == 'status' and p['value'] == 'withdrawn'
                       for p in ctrl.get('props', []))
        controles[id_desde_oscal(ctrl['id'])] = {'ctrl': ctrl, 'familia': familia,
                                                  'retirado': retirado}
        for hijo in ctrl.get('controls', []):
            visitar(hijo, familia)

    for grupo in catalogo['groups']:
        for ctrl in grupo.get('controls', []):
            visitar(ctrl, grupo['id'].upper())
    return controles, params


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--mapeo', required=True)
    ap.add_argument('--catalogo', required=True)
    ap.add_argument('--salida', default='app/data/remediacion_nist.json')
    args = ap.parse_args()

    with open(args.mapeo, encoding='utf-8') as f:
        lib = yaml.safe_load(f)
    with open(args.catalogo, encoding='utf-8') as f:
        cat = json.load(f)['catalog']

    controles, params = indexar_catalogo(cat)

    filas = lib['objects']['requirement_mapping_sets'][0]['requirement_mappings']
    mapeo = {}
    usados = set()
    descartados = []
    for fila in filas:
        destino = fila['target_requirement_urn'].rsplit(':', 1)[-1]
        if not destino.startswith('a.'):
            continue  # clausulas 4-10: el modulo trabaja sobre el Anexo A
        iso = destino[2:]  # a.5.15 -> 5.15
        nist = id_desde_mapeo(fila['source_requirement_urn'].rsplit(':', 1)[-1])
        info = controles.get(nist)
        if info is None or info['retirado']:
            descartados.append(nist)
            continue
        mapeo.setdefault(iso, [])
        if nist not in mapeo[iso]:
            mapeo[iso].append(nist)
        usados.add(nist)

    def clave(codigo):
        return [int(n) for n in codigo.split('.')]

    controles_nist = {}
    for nist in sorted(usados):
        info = controles[nist]
        controles_nist[nist] = {
            'titulo': info['ctrl']['title'],
            'familia': info['familia'],
            'enunciado': enunciado(info['ctrl'], params),
        }

    salida = {
        'fuente': {
            'mapeo': 'NIST OLIR Informative Reference 155 — NIST SP 800-53 Rev. 5 to '
                     'ISO/IEC 27001:2022 (actualizado 2023-10-12), normalizado por '
                     'CISO Assistant (intuitem)',
            'mapeo_url': 'https://csrc.nist.gov/projects/olir/informative-reference-catalog/'
                         'details?referenceId=155',
            'mapeo_sha256': sha256(args.mapeo),
            'catalogo': cat['metadata']['title'],
            'catalogo_version': cat['metadata'].get('version'),
            'catalogo_url': 'https://github.com/usnistgov/oscal-content',
            'catalogo_sha256': sha256(args.catalogo),
            'generado': date.today().isoformat(),
            'advertencia': 'NIST indica que las correspondencias dan una idea general de '
                           'cobertura; no son equivalencias uno a uno.',
        },
        'familias': FAMILIAS_ES,
        'controles_nist': controles_nist,
        'mapeo': {k: mapeo[k] for k in sorted(mapeo, key=clave)},
    }

    with open(args.salida, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)

    print(f'Controles del Anexo A con correspondencia: {len(mapeo)} de 93')
    print(f'Controles NIST distintos: {len(controles_nist)}')
    print(f'Filas descartadas (retiradas o inexistentes): {len(descartados)} {sorted(set(descartados))}')


if __name__ == '__main__':
    main()
