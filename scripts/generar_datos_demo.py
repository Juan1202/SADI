# -*- coding: utf-8 -*-
"""
Genera los CSV de entrada del caso de demostracion en data/demo/.

Los archivos se escriben antes de cargar nada al aplicativo, para que el equipo
pueda revisarlos y ajustarlos sin volver a ejecutar todo el proceso.

    python scripts/generar_datos_demo.py
"""
import csv
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from demo import auditorias as mod_auditorias  # noqa: E402
from demo import caso, documentos, gap, organizacion, planes, soa  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, 'data', 'demo')

ENCABEZADO_SINTETICO = ('DATOS SINTETICOS generados para probar el aplicativo SADI. '
                        'No corresponden a ninguna organizacion real.')


def escribir_csv(nombre, columnas, filas):
    ruta = os.path.join(DESTINO, nombre)
    with io.open(ruta, 'w', encoding='utf-8-sig', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, delimiter=';')
        escritor.writeheader()
        for fila in filas:
            escritor.writerow(fila)
    print('  %-28s %4d filas' % (nombre, len(filas)))
    return len(filas)


# --- Generadores por archivo -------------------------------------------------

def generar_usuarios():
    filas = [{
        'username': u['username'],
        'nombre': u['nombre'],
        'rol': u['role'],
        'cargo': u['cargo'],
        'email': u['email'],
        'proposito': u['descripcion'],
    } for u in organizacion.USUARIOS]
    return escribir_csv('usuarios.csv',
                        ['username', 'nombre', 'rol', 'cargo', 'email', 'proposito'], filas)


def generar_diagnostico():
    filas = []
    for numero, (etiqueta, respuestas, fecha) in enumerate([
        ('D1', gap.respuestas_diagnostico_1(), organizacion.FECHA_DIAGNOSTICO_1),
        ('D2', gap.respuestas_diagnostico_2(), organizacion.FECHA_DIAGNOSTICO_2),
    ], start=1):
        for requisito, valor, observacion, origen in respuestas:
            filas.append({
                'diagnostico': etiqueta,
                'fecha': fecha.isoformat(),
                'clausula': gap.CATEGORIA_DE[requisito],
                'nombre_clausula': gap.NOMBRE_CATEGORIA[gap.CATEGORIA_DE[requisito]],
                'requisito': requisito,
                'valor': valor,
                'observacion': observacion,
                'origen': origen,
            })
    return escribir_csv('diagnostico_gap.csv',
                        ['diagnostico', 'fecha', 'clausula', 'nombre_clausula', 'requisito',
                         'valor', 'observacion', 'origen'], filas)


def _texto_alcance(definicion):
    if definicion['alcance'] == 'TODOS':
        return 'Los 93 controles del Anexo A'
    if definicion['alcance'] == 'CONTROLES':
        return 'Controles %s' % ', '.join(definicion['controles_alcance'])
    return 'Dominio %s' % definicion['dominio']


def generar_auditorias():
    filas = []
    for definicion in mod_auditorias.AUDITORIAS:
        clave = definicion['clave']
        distribucion = caso.resumen_distribucion(clave)
        filas.append({
            'clave': clave,
            'titulo': definicion['titulo'],
            'alcance': _texto_alcance(definicion),
            # Version legible por maquina del alcance: el cargador resuelve por
            # aqui, no interpretando la prosa de la columna anterior.
            'controles_alcance': (','.join(definicion['controles_alcance'])
                                  if definicion['alcance'] == 'CONTROLES' else ''),
            'controles': len(caso.controles_de(clave)),
            'propietario': definicion['propietario'],
            'evaluador': organizacion.nombre_de(definicion['propietario']),
            'fecha': definicion['fecha'].isoformat(),
            'estado_final': definicion['estado_final'],
            'eliminado': 'si' if definicion['eliminado'] else 'no',
            'extrema': distribucion['Extrema'],
            'alta': distribucion['Alta'],
            'moderada': distribucion['Moderada'],
            'baja': distribucion['Baja'],
            'bloqueantes': len(caso.controles_bloqueantes(clave)),
            'planes': len(planes.planes_de(clave)),
            'descripcion': definicion['descripcion'],
        })
    return escribir_csv('auditorias.csv',
                        ['clave', 'titulo', 'alcance', 'controles_alcance', 'controles', 'propietario', 'evaluador',
                         'fecha', 'estado_final', 'eliminado', 'extrema', 'alta', 'moderada',
                         'baja', 'bloqueantes', 'planes', 'descripcion'], filas)


def generar_hallazgos():
    filas = []
    for definicion in mod_auditorias.AUDITORIAS:
        for h in caso.hallazgos_de(definicion['clave']):
            filas.append({
                'auditoria': h['auditoria'],
                'control': h['control'],
                'dominio': h['dominio'],
                'criterio': h['criterio'],
                'hallazgo': h['hallazgo'],
                'probabilidad': h['probabilidad'],
                'impacto': h['impacto'],
                'nivel': h['nivel'],
                'zona': h['zona'],
                'evidencia_archivo': h['archivo_evidencia'],
                'origen': h['origen'],
            })
    return escribir_csv('hallazgos.csv',
                        ['auditoria', 'control', 'dominio', 'criterio', 'hallazgo', 'probabilidad',
                         'impacto', 'nivel', 'zona', 'evidencia_archivo', 'origen'], filas)


def generar_evidencias_texto():
    """Evidencia que se registra como texto en el resultado, no como archivo."""
    filas = []
    for definicion in mod_auditorias.AUDITORIAS:
        clave = definicion['clave']
        for codigo, texto in sorted(caso.evidencias_texto_de(clave).items(),
                                    key=lambda kv: caso.orden_de(kv[0])):
            filas.append({'auditoria': clave, 'control': codigo, 'evidencia_texto': texto})
    return escribir_csv('evidencias_texto.csv',
                        ['auditoria', 'control', 'evidencia_texto'], filas)


def generar_planes():
    filas = []
    for definicion in mod_auditorias.AUDITORIAS:
        clave = definicion['clave']
        riesgos = caso.riesgo_por_control(clave)
        for codigo, plan in sorted(planes.planes_de(clave).items(), key=lambda kv: caso.orden_de(kv[0])):
            filas.append({
                'auditoria': clave,
                'control': codigo,
                'nivel_riesgo_inicial': riesgos[codigo],
                'zona': caso.zona_de(riesgos[codigo]),
                'descripcion_riesgo': plan['descripcion'],
                'proceso_negocio': plan['proceso'],
                'activos_relacionados': plan['activos'],
                'estrategia': plan['estrategia'],
                'tipo_control': plan['tipo_control'],
                'acciones': plan['acciones'],
                'responsable': plan['responsable'],
                'plazo': plan['plazo'].isoformat(),
                'estado': plan['estado'],
            })
    return escribir_csv('planes_tratamiento.csv',
                        ['auditoria', 'control', 'nivel_riesgo_inicial', 'zona',
                         'descripcion_riesgo', 'proceso_negocio', 'activos_relacionados',
                         'estrategia', 'tipo_control', 'acciones', 'responsable', 'plazo',
                         'estado'], filas)


def generar_soa():
    riesgos = caso.riesgo_por_control('integral')
    filas = []
    for codigo in sorted(caso.HALLAZGOS_BASE, key=caso.orden_de):
        nivel = riesgos.get(codigo, 0)
        aplicable, justificacion = soa.detalle(codigo, nivel)
        filas.append({
            'control': codigo,
            'dominio': caso.dominio_de(codigo),
            'aplicable': 'si' if aplicable else 'no',
            'nivel_riesgo': nivel,
            'zona': caso.zona_de(nivel),
            'justificacion': justificacion,
        })
    return escribir_csv('soa.csv',
                        ['control', 'dominio', 'aplicable', 'nivel_riesgo', 'zona',
                         'justificacion'], filas)


def generar_documentos():
    """
    Exporta el documento completo, no solo sus metadatos: el cargador debe poder
    diligenciar el formulario del generador de politicas leyendo unicamente de
    data/demo/, sin importar nada de scripts/.
    """
    edicion = documentos.EDICION
    filas = []
    for doc in documentos.DOCUMENTOS:
        se_edita = doc['clave'] == edicion['clave']
        filas.append({
            'clave': doc['clave'],
            'tipo': doc['tipo'],
            'codigo': doc['codigo'],
            'titulo': doc['titulo'],
            'version': doc['version'],
            'fecha_version': doc['fecha_version'],
            'desc_cambio': doc['desc_cambio'],
            'objetivo': doc['objetivo'],
            'alcance': doc['alcance'],
            'responsables': doc['responsables'],
            'marco_legal': doc['marco_legal'],
            'lineamientos': doc['lineamientos'],
            'elaboro_nombre': doc['elaboro'][0],
            'elaboro_cargo': doc['elaboro'][1],
            'reviso_nombre': doc['reviso'][0],
            'reviso_cargo': doc['reviso'][1],
            'aprobo_nombre': doc['aprobo'][0],
            'aprobo_cargo': doc['aprobo'][1],
            'se_edita': 'si' if se_edita else 'no',
            'version_editada': edicion['version'] if se_edita else '',
            'desc_cambio_edicion': edicion['desc_cambio'] if se_edita else '',
            'lineamientos_editados': (doc['lineamientos'] + edicion['lineamientos_extra']
                                      if se_edita else ''),
        })
    return escribir_csv('documentos.csv',
                        ['clave', 'tipo', 'codigo', 'titulo', 'version', 'fecha_version',
                         'desc_cambio', 'objetivo', 'alcance', 'responsables', 'marco_legal',
                         'lineamientos', 'elaboro_nombre', 'elaboro_cargo', 'reviso_nombre',
                         'reviso_cargo', 'aprobo_nombre', 'aprobo_cargo', 'se_edita',
                         'version_editada', 'desc_cambio_edicion', 'lineamientos_editados'],
                        filas)


# --- README ------------------------------------------------------------------

def generar_readme(conteos):
    d1 = gap.respuestas_diagnostico_1()
    d2 = gap.respuestas_diagnostico_2()
    dist = caso.resumen_distribucion('integral')

    lineas = [
        '# Conjunto de datos del caso de demostracion de SADI',
        '',
        '> **%s**' % ENCABEZADO_SINTETICO,
        '',
        'Estos archivos son la entrada de `seed_demo_sgsi.py`. Se pueden revisar y editar',
        'antes de cargarlos, sin volver a ejecutar el generador.',
        '',
        '## Que es y que no es',
        '',
        'Este conjunto de datos es una **demostracion funcional del aplicativo SADI**: sirve',
        'para ver todos sus modulos operando con datos completos y coherentes entre si.',
        '',
        '**No** son los resultados de ninguna organizacion real. En particular, no son los de',
        'la Corporacion Community Network. El nivel medio de madurez que reporta el articulo',
        'proviene del instrumento de autodiagnostico de 2019 aplicado a esa organizacion, y esa',
        'cifra es independiente de la que produzca este caso.',
        '',
        '## Como se derivo del instrumento de 2019',
        '',
        'El archivo `4. INSUMO intrumento de AUTODIAGNOSTICO revisada24.xlsx` es una prueba del',
        'formulario en Excel, no el levantamiento de una organizacion. Se uso como **base de',
        'realismo**: sus proporciones de respuesta (79 cumple, 8 parcial, 45 no cumple sobre 132',
        'preguntas, es decir 62,9 %) orientan que sale bien y que sale mal en el caso.',
        '',
        '- Las **secciones 1 a 11** alimentan el diagnostico GAP de las clausulas 4 a 10.',
        '- La **seccion 12** orienta que controles del Anexo A salen mal en la auditoria.',
        '',
        'La columna `origen` de cada archivo dice de donde sale cada decision:',
        '',
        '| Valor | Significado |',
        '|---|---|',
        '| `EXCEL:<pregunta>` | Lo decidio una pregunta de la seccion 12 del instrumento |',
        '| `EXCEL:<filas>` | Lo decidieron esas filas del instrumento (diagnostico GAP) |',
        '| `EXCEL-GAP:<req>` | Lo decidio un requisito del diagnostico GAP ya derivado |',
        '| `SEGUIMIENTO` | Reevaluacion de un control en una auditoria posterior |',
        '| `GENERADO` | Decision del caso de demostracion, sin respaldo en el instrumento |',
        '',
        '## Organizacion del caso',
        '',
        '| | |',
        '|---|---|',
        '| Organizacion | %s |' % organizacion.ORGANIZACION,
        '| Sector | %s |' % organizacion.SECTOR,
        '| Empleados | %d |' % organizacion.EMPLEADOS,
        '| Fecha base | %s |' % organizacion.FECHA_BASE.isoformat(),
        '',
        '## Archivos',
        '',
        '| Archivo | Filas | Contenido |',
        '|---|---|---|',
        '| `usuarios.csv` | %d | Cinco usuarios, uno por rol y un segundo auditor |' % conteos['usuarios'],
        '| `diagnostico_gap.csv` | %d | Dos diagnosticos de 22 requisitos cada uno |' % conteos['diagnostico'],
        '| `auditorias.csv` | %d | Las cuatro auditorias y su distribucion de riesgo |' % conteos['auditorias'],
        '| `hallazgos.csv` | %d | Criterio, hallazgo, probabilidad, impacto y nivel |' % conteos['hallazgos'],
        '| `evidencias_texto.csv` | %d | Evidencia registrada como texto, no como archivo |' % conteos['evidencias_texto'],
        '| `planes_tratamiento.csv` | %d | Un plan por hallazgo con riesgo >= 9 |' % conteos['planes'],
        '| `soa.csv` | %d | Declaracion de Aplicabilidad de los 93 controles |' % conteos['soa'],
        '| `documentos.csv` | %d | Dos politicas y un procedimiento |' % conteos['documentos'],
        '',
        'Todos los CSV usan separador `;` y codificacion UTF-8 con BOM, para que Excel los abra',
        'directamente sin pasar por el asistente de importacion.',
        '',
        '## Cifras que va a mostrar el aplicativo',
        '',
        '### Diagnostico GAP',
        '',
        '| | Diagnostico 1 (%s) | Diagnostico 2 (%s) |' % (
            organizacion.FECHA_DIAGNOSTICO_1.isoformat(), organizacion.FECHA_DIAGNOSTICO_2.isoformat()),
        '|---|---|---|',
        '| Puntaje global | **%.1f %%** | **%.1f %%** |' % (gap.puntaje(d1), gap.puntaje(d2)),
    ]

    cat1 = gap.puntaje_por_categoria(d1)
    cat2 = gap.puntaje_por_categoria(d2)
    for numero in sorted(cat1, key=int):
        lineas.append('| Clausula %s. %s | %.1f %% | %.1f %% |' % (
            numero, gap.NOMBRE_CATEGORIA[numero], cat1[numero], cat2[numero]))

    lineas += [
        '',
        'El primer diagnostico deja un requisito en `no_aplica` (9.3) y otro en `no_evaluado`',
        '(10.1), para mostrar que la formula de SADI excluye ambos del denominador: se calcula',
        'sobre 20 requisitos evaluados, no sobre 22.',
        '',
        '### Distribucion de riesgo de la auditoria integral',
        '',
        '| Zona | Nivel | Controles |',
        '|---|---|---|',
        '| Extrema | >= 20 | %d |' % dist['Extrema'],
        '| Alta | 9 a 16 | %d |' % dist['Alta'],
        '| Moderada | 3 a 8 | %d |' % dist['Moderada'],
        '| Baja | 1 a 2 | %d |' % dist['Baja'],
        '| **Total** | | **%d** |' % sum(dist.values()),
        '',
        '### Auditorias',
        '',
        '| Auditoria | Controles | Estado | Proposito |',
        '|---|---|---|---|',
    ]
    for definicion in mod_auditorias.AUDITORIAS:
        estado = definicion['estado_final']
        if definicion['eliminado']:
            estado += ' (papelera)'
        elif estado == 'En Proceso':
            estado += ' (bloqueada)'
        lineas.append('| %s | %d | %s | %s |' % (
            definicion['titulo'], len(caso.controles_de(definicion['clave'])), estado,
            definicion['descripcion'].split('.')[0] + '.'))

    lineas += [
        '',
        '## Regla de mapeo del diagnostico GAP',
        '',
        'El instrumento tiene 132 preguntas y SADI tiene 22 requisitos. Cuando varias preguntas',
        'caen en el mismo requisito se promedia el grupo (cumple = 1, parcial = 0,5, no cumple = 0)',
        'y se clasifica asi:',
        '',
        '| Promedio del grupo | Valor en SADI |',
        '|---|---|',
        '| >= 0,75 | `cumple` |',
        '| 0,30 a 0,74 | `parcial` |',
        '| < 0,30 | `no_cumple` |',
        '',
        'Las filas 52 a 56 del instrumento corresponden al requisito 6.1.1 de la norma, que SADI',
        'no incluye entre sus 22 preguntas. Se documentan como excluidas en vez de repartirlas,',
        'para no diluir el resultado de 6.1.2.',
        '',
        '## Regeneracion',
        '',
        '```bash',
        'python scripts/generar_datos_demo.py            # reescribe estos CSV',
        'docker compose exec web python seed_demo_sgsi.py --dry-run',
        'docker compose exec web python seed_demo_sgsi.py',
        '```',
        '',
    ]

    ruta = os.path.join(DESTINO, 'README.md')
    io.open(ruta, 'w', encoding='utf-8').write('\n'.join(lineas))
    print('  %-28s %4d lineas' % ('README.md', len(lineas)))


def main():
    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)

    print('Generando el conjunto de datos del caso de demostracion')
    print('  destino: %s\n' % DESTINO)

    conteos = {
        'usuarios': generar_usuarios(),
        'diagnostico': generar_diagnostico(),
        'auditorias': generar_auditorias(),
        'hallazgos': generar_hallazgos(),
        'evidencias_texto': generar_evidencias_texto(),
        'planes': generar_planes(),
        'soa': generar_soa(),
        'documentos': generar_documentos(),
    }
    generar_readme(conteos)

    print('\nListo. %d filas en total.' % sum(conteos.values()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
