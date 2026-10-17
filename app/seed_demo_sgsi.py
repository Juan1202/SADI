# -*- coding: utf-8 -*-
"""
Carga el caso de demostración de SADI leyendo únicamente de data/demo/.

DATOS SINTÉTICOS. Nada de lo que carga este script corresponde a una
organización real.

Todo se escribe por las rutas reales de la aplicación, autenticado con el rol
que corresponde a cada paso, de modo que se apliquen de verdad las reglas de
negocio y la bitácora quede poblada.

    docker compose exec web python seed_demo_sgsi.py --dry-run
    docker compose exec web python seed_demo_sgsi.py
    docker compose exec web python seed_demo_sgsi.py --reset

Es idempotente: sin --reset, si el caso ya está cargado no hace nada.
"""
import argparse
import csv
import io
import os
import secrets
import string
import sys

from main import app
from models import db

from demo_loader import carga, evidencias, lectura, limpieza, validacion
from demo_loader.cliente import ErrorDeCarga

ALFABETO_CLAVE = string.ascii_letters + string.digits
ARCHIVO_CREDENCIALES = 'credenciales.csv'
ENCABEZADO = 'DATOS SINTÉTICOS — caso de demostración de SADI'


def registro(mensaje=''):
    print(mensaje)
    sys.stdout.flush()


def titulo(texto):
    registro('')
    registro(texto)
    registro('-' * len(texto))


def generar_clave():
    """Contraseña fuerte: 16 caracteres con mayúscula, minúscula, dígito y símbolo."""
    while True:
        clave = ''.join(secrets.choice(ALFABETO_CLAVE) for _ in range(14))
        clave = clave + secrets.choice('.-_#$') + secrets.choice(string.digits)
        if (any(c.islower() for c in clave) and any(c.isupper() for c in clave)
                and any(c.isdigit() for c in clave)):
            return clave


def escribir_credenciales(credenciales):
    ruta = os.path.join(lectura.DIRECTORIO, ARCHIVO_CREDENCIALES)
    filas = {f['username']: f for f in lectura.usuarios()}
    with io.open(ruta, 'w', encoding='utf-8-sig', newline='') as f:
        escritor = csv.writer(f, delimiter=';')
        escritor.writerow(['# %s. Archivo excluido del repositorio.' % ENCABEZADO])
        escritor.writerow(['username', 'password', 'rol', 'nombre', 'cargo'])
        for username, clave in credenciales.items():
            fila = filas[username]
            escritor.writerow([username, clave, fila['rol'], fila['nombre'], fila['cargo']])
    return ruta


# --- Pasos -------------------------------------------------------------------

def ejecutar_carga(ctx):
    filas = lectura.auditorias()
    por_clave = {f['clave']: f for f in filas}
    resumen = {}

    titulo('1. Usuarios')
    resumen['usuarios'] = carga.cargar_usuarios(ctx)

    titulo('2. Diagnósticos GAP')
    resumen['diagnosticos'] = carga.cargar_diagnosticos(ctx, 'jcastano')

    titulo('3. Auditorías, hallazgos y evidencias')
    total_criterios, total_archivos, total_textos = 0, 0, 0
    for fila in filas:
        carga.crear_auditoria(ctx, fila)
        textos = lectura.evidencias_texto_por_auditoria(fila['clave'])
        total_textos += carga.cargar_evidencia_texto(ctx, fila, textos)
        criterios, archivos = carga.cargar_hallazgos(ctx, fila)
        total_criterios += criterios
        total_archivos += archivos
        registro('        %d criterios, %d evidencias en archivo' % (criterios, archivos))
    resumen['criterios'] = total_criterios
    resumen['archivos'] = total_archivos
    resumen['evidencias_texto'] = total_textos

    titulo('4. Regla de bloqueo (debe impedir el cierre)')
    finalizada, mensajes = carga.intentar_finalizar(ctx, por_clave['integral'])
    if finalizada:
        raise ErrorDeCarga(
            'La auditoría integral se finalizó sin tratar sus riesgos altos. '
            'La regla de bloqueo no actuó: revise _check_critical_risk.')
    bloqueo = [m for m in mensajes if 'No se puede finalizar' in m]
    if not bloqueo:
        raise ErrorDeCarga('No se capturó el mensaje de bloqueo. Mensajes: %s' % mensajes)
    ctx.mensaje_bloqueo = bloqueo[0]
    registro('    Intento rechazado, como se esperaba:')
    registro('    > %s' % ctx.mensaje_bloqueo)

    titulo('5. Planes de tratamiento')
    for fila in filas:
        estados = carga.cargar_planes(ctx, fila)
        if estados:
            registro('    %-15s %s' % (fila['clave'],
                                       '  '.join('%s=%d' % kv for kv in sorted(estados.items()))))
        resumen.setdefault('planes', {})
        for estado, cantidad in estados.items():
            resumen['planes'][estado] = resumen['planes'].get(estado, 0) + cantidad

    titulo('6. Cierre de auditorías')
    for fila in filas:
        if fila['eliminado']:
            continue
        finalizada, _ = carga.intentar_finalizar(ctx, fila)
        esperada = fila['estado_final'] == 'Finalizada'
        if finalizada != esperada:
            raise ErrorDeCarga(
                'La auditoría %s debía quedar en %s y %s.'
                % (fila['clave'], fila['estado_final'],
                   'se finalizó' if finalizada else 'no se pudo finalizar'))
        registro('    %-22s %s' % (
            fila['clave'],
            'Finalizada' if finalizada else 'sigue bloqueada, como se esperaba'))

    titulo('7. Papelera')
    codigo = carga.enviar_a_papelera(ctx, por_clave['personas'])
    registro('    %s enviada a la papelera' % codigo)

    titulo('8. Declaración de Aplicabilidad')
    for dominio, (total, excluidos) in sorted(carga.cargar_soa(ctx, 'lvargas').items()):
        registro('    %-16s %2d controles, %d no aplicables' % (dominio, total, excluidos))

    titulo('9. Documentos del SGSI')
    creados, editados = carga.cargar_documentos(ctx, 'lvargas')
    for _id, codigo, tipo, version in creados:
        registro('    %-14s %-14s v%s' % (codigo, tipo, version))
    for codigo, antes, despues in editados:
        registro('    %-14s reeditado: v%s -> v%s' % (codigo, antes, despues))
    resumen['documentos'] = len(creados)

    return resumen


def mostrar_validacion(resultado, encabezado):
    titulo(encabezado)
    for ok, descripcion, detalle in resultado.comprobaciones:
        marca = 'OK  ' if ok else 'FALLA'
        sufijo = ('   (%s)' % detalle) if detalle else ''
        registro('    [%s] %s%s' % (marca, descripcion, sufijo))
    return resultado.ok


def plan_de_carga():
    titulo('Plan de carga (--dry-run, no se escribe nada)')
    registro('    Insumos en: %s' % lectura.DIRECTORIO)
    registro('')
    registro('    %-26s %s' % ('usuarios.csv', '%d usuarios' % len(lectura.usuarios())))
    diagnosticos = lectura.diagnosticos()
    registro('    %-26s %s' % ('diagnostico_gap.csv', '%d diagnósticos, %d respuestas' % (
        len(diagnosticos), sum(len(v) for v in diagnosticos.values()))))

    filas = lectura.auditorias()
    registro('    %-26s %d auditorías' % ('auditorias.csv', len(filas)))
    for fila in filas:
        hallazgos = lectura.hallazgos_por_auditoria(fila['clave'])
        criterios = sum(len(v) for v in hallazgos.values())
        planes = lectura.planes_por_auditoria(fila['clave'])
        estados = {}
        for plan in planes.values():
            estados[plan['estado']] = estados.get(plan['estado'], 0) + 1
        registro('        %-15s %2d controles, %3d criterios, %2d planes %s -> %s%s' % (
            fila['clave'], fila['controles'], criterios, len(planes),
            ('(' + ', '.join('%s=%d' % kv for kv in sorted(estados.items())) + ')') if estados else '',
            fila['estado_final'], ' + papelera' if fila['eliminado'] else ''))

    soa = lectura.soa()
    registro('    %-26s %d controles, %d no aplicables' % (
        'soa.csv', len(soa), sum(1 for f in soa if not f['aplicable'])))
    documentos = lectura.documentos()
    registro('    %-26s %d documentos, %d con reedición' % (
        'documentos.csv', len(documentos),
        sum(1 for f in documentos if f['se_edita'] == 'si')))
    registro('')
    registro('    Archivos de evidencia que se generarían: %d PDF y %d imágenes' % (
        len(evidencias.PDFS), len(evidencias.IMAGENES)))
    registro('')
    registro('    Estado actual de la base: %s' % limpieza.resumen_actual())


def main():
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument('--dry-run', action='store_true',
                            help='Muestra lo que se cargaría, sin escribir nada.')
    analizador.add_argument('--reset', action='store_true',
                            help='Borra el caso de demostración antes de cargarlo de nuevo.')
    analizador.add_argument('--solo-reset', action='store_true',
                            help='Borra el caso y termina, sin volver a cargarlo.')
    argumentos = analizador.parse_args()

    registro('=' * 78)
    registro('SADI — carga del caso de demostración')
    registro(ENCABEZADO)
    registro('=' * 78)

    with app.app_context():
        try:
            lectura.verificar_insumos()
        except lectura.InsumoFaltante as error:
            registro('\nERROR: %s' % error)
            return 1

        if argumentos.dry_run:
            plan_de_carga()
            registro('\nNada se escribió. Quite --dry-run para cargar.')
            return 0

        if argumentos.reset or argumentos.solo_reset:
            titulo('0. Limpieza del caso anterior')
            limpieza.limpiar(registro)
            if argumentos.solo_reset:
                registro('\nCaso de demostración eliminado.')
                return 0

        if limpieza.hay_datos_cargados():
            registro('\nEl caso de demostración ya está cargado: %s' % limpieza.resumen_actual())
            registro('Use --reset para recargarlo desde cero, o --solo-reset para borrarlo.')
            return 0

        admin_usuario = os.environ.get('ADMIN_USERNAME')
        admin_clave = os.environ.get('ADMIN_PASSWORD')
        if not admin_usuario or not admin_clave:
            registro('\nERROR: faltan ADMIN_USERNAME o ADMIN_PASSWORD en el entorno. '
                     'Ejecute antes: python bootstrap_admin.py')
            return 1

        credenciales = {f['username']: generar_clave() for f in lectura.usuarios()}
        contexto = carga.Contexto(app, admin_usuario, admin_clave, credenciales, registro)
        contexto.directorio_evidencias = os.path.join(lectura.DIRECTORIO, 'evidencias')

        titulo('Preparación')
        rutas = evidencias.generar(contexto.directorio_evidencias)
        registro('    %d archivos de evidencia en %s' % (len(rutas), contexto.directorio_evidencias))
        ruta_credenciales = escribir_credenciales(credenciales)
        registro('    Credenciales escritas en %s' % ruta_credenciales)

        try:
            resumen = ejecutar_carga(contexto)
        except ErrorDeCarga as error:
            db.session.rollback()
            registro('\nERROR DE CARGA: %s' % error)
            registro('No se corrige a mano: ajuste los insumos o el cargador y vuelva a ejecutar '
                     'con --reset.')
            return 1

        todo_ok = mostrar_validacion(validacion.validar(contexto), '10. Validación contra la base')
        pdf_ok = mostrar_validacion(validacion.validar_pdfs(contexto), '11. Generación de PDF')

        titulo('Resumen')
        for clave, valor in sorted(resumen.items()):
            registro('    %-20s %s' % (clave, valor))

        registro('')
        if todo_ok and pdf_ok:
            registro('CARGA COMPLETA. Todas las comprobaciones pasaron.')
            return 0
        registro('CARGA COMPLETA CON OBSERVACIONES. Revise las comprobaciones marcadas FALLA.')
        return 2


if __name__ == '__main__':
    sys.exit(main())
