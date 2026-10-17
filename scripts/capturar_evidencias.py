# -*- coding: utf-8 -*-
"""
Recorrido del caso de demostración y captura de las pantallas para el artículo.

DATOS SINTÉTICOS. Las pantallas que captura este script muestran un caso de
demostración; no corresponden a ninguna organización real.

Se ejecuta en el equipo anfitrión, contra la aplicación levantada con Docker:

    python scripts/capturar_evidencias.py

Requiere `pip install playwright` y `python -m playwright install chromium`.
Las imágenes y los PDF quedan numerados en data/demo/evidencias_articulo/.
"""
import csv
import io
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get('SADI_URL', 'http://127.0.0.1:5000')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTORIO_DEMO = os.path.join(RAIZ, 'data', 'demo')
DESTINO = os.path.join(DIRECTORIO_DEMO, 'evidencias_articulo')

# Ancho de escritorio, suficiente para que el menú lateral no se colapse.
VIEWPORT = {'width': 1600, 'height': 1000}
ESPERA_RED = 'networkidle'

# Tope de altura de una captura de pagina completa. El detalle de la auditoria
# integral mide mas de 30 000 px: completa es inservible como figura, asi que se
# recorta por arriba, que es donde esta el encabezado y el resumen.
ALTURA_MAXIMA = 2400


def credenciales():
    """{username: (clave, rol)} desde el archivo que escribió el cargador."""
    ruta = os.path.join(DIRECTORIO_DEMO, 'credenciales.csv')
    with io.open(ruta, encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.reader(f, delimiter=';') if r]
    return {r[0]: (r[1], r[2]) for r in filas[2:]}


def identificadores():
    ruta = os.path.join(DIRECTORIO_DEMO, 'ids_capturas.json')
    with io.open(ruta, encoding='utf-8') as f:
        return json.load(f)


class Recorrido(object):
    def __init__(self, pagina, claves):
        self.pagina = pagina
        self.claves = claves
        self.usuario = None
        self.contador = 0
        self.capturas = []

    # --- sesión ---

    def entrar(self, usuario):
        if self.usuario == usuario:
            return
        if self.usuario is not None:
            self.pagina.goto('%s/logout' % BASE, wait_until=ESPERA_RED)
        self.pagina.goto('%s/login' % BASE, wait_until=ESPERA_RED)
        self.pagina.fill('input[name="username"]', usuario)
        self.pagina.fill('input[name="password"]', self.claves[usuario][0])
        self.pagina.click('button[type="submit"]')
        self.pagina.wait_for_load_state(ESPERA_RED)
        self.usuario = usuario

    def salir(self):
        if self.usuario is not None:
            self.pagina.goto('%s/logout' % BASE, wait_until=ESPERA_RED)
            self.usuario = None

    # --- captura ---

    def _ruta(self, nombre):
        self.contador += 1
        return os.path.join(DESTINO, '%02d_%s.png' % (self.contador, nombre))

    def capturar(self, nombre, descripcion, pagina_completa=True):
        ruta = self._ruta(nombre)
        opciones = {'path': ruta, 'full_page': pagina_completa}
        if pagina_completa:
            alto = self.pagina.evaluate('document.documentElement.scrollHeight')
            if alto > ALTURA_MAXIMA:
                opciones['clip'] = {'x': 0, 'y': 0,
                                    'width': VIEWPORT['width'], 'height': ALTURA_MAXIMA}
                descripcion += ' (recortada a %d px de alto)' % ALTURA_MAXIMA
        self.pagina.screenshot(**opciones)
        self.capturas.append((os.path.basename(ruta), descripcion))
        print('  %-42s %s' % (os.path.basename(ruta), descripcion))
        return ruta

    def visitar(self, ruta, nombre, descripcion, pagina_completa=True, espera=None):
        self.pagina.goto(BASE + ruta, wait_until=ESPERA_RED)
        if espera:
            self.pagina.wait_for_timeout(espera)
        return self.capturar(nombre, descripcion, pagina_completa)

    def descargar(self, ruta, nombre, descripcion):
        """Guarda un PDF servido por la aplicación, usando la sesión del navegador."""
        respuesta = self.pagina.request.get(BASE + ruta)
        if respuesta.status != 200:
            raise RuntimeError('%s devolvió %d' % (ruta, respuesta.status))
        cuerpo = respuesta.body()
        if cuerpo[:4] != b'%PDF':
            raise RuntimeError('%s no devolvió un PDF' % ruta)
        self.contador += 1
        destino = os.path.join(DESTINO, '%02d_%s.pdf' % (self.contador, nombre))
        with open(destino, 'wb') as f:
            f.write(cuerpo)
        self.capturas.append((os.path.basename(destino),
                              '%s (%d bytes)' % (descripcion, len(cuerpo))))
        print('  %-42s %s' % (os.path.basename(destino), descripcion))
        return destino


def comprobar_porcentajes(pagina):
    """Falla si el diagnóstico pinta todas sus cláusulas en cero."""
    textos = pagina.locator('[id^="cat-text-"]').all_inner_texts()
    valores = [float(v.replace('%', '').replace(',', '.')) for v in textos if v.strip()]
    if not valores:
        raise RuntimeError('No se encontraron los porcentajes por cláusula')
    if not any(v > 0 for v in valores):
        raise RuntimeError('Todas las cláusulas del diagnóstico quedaron en cero: %s' % valores)
    print('  [ok] porcentajes por cláusula %s' % valores)



def comprobar_graficas(pagina, canvas):
    """
    Falla si alguna grafica del tablero quedo plana.

    Un gráfico en cero no rompe la página: se dibuja igual, solo que vacío. Por
    eso se comprueba leyendo los datos que Chart.js tiene cargados, y no la
    apariencia de la captura.
    """
    for identificador in canvas:
        valores = pagina.evaluate(
            """(id) => {
                const gr = Chart.getChart(id);
                if (!gr) { return null; }
                return gr.data.datasets.flatMap(d => d.data).map(Number);
            }""", identificador)
        if valores is None:
            raise RuntimeError('No se encontró la gráfica %s en el tablero' % identificador)
        if not any(v > 0 for v in valores):
            raise RuntimeError('La gráfica %s quedó plana: %s' % (identificador, valores))
        print('  [ok] gráfica %-12s %s' % (identificador, valores))


def ejecutar(recorrido, ids):
    r = recorrido

    # 1. Portada e ingreso.
    r.salir()
    r.pagina.goto('%s/login' % BASE, wait_until=ESPERA_RED)
    r.capturar('login', 'Pantalla de ingreso')

    # 2. Tablero de métricas, con el rol administrador.
    r.entrar('lvargas')
    # Las gráficas se dibujan con Chart.js; hay que dejarlas terminar.
    r.visitar('/dashboard', 'tablero_metricas',
              'Tablero: KPI, GAP por grupos, dona de estado y detalle por control',
              espera=2500)
    comprobar_graficas(r.pagina, ['gapChart', 'statusChart'])

    # 3. Catálogo de los 93 controles.
    r.visitar('/controles', 'catalogo_controles', 'Catálogo de los 93 controles del Anexo A')
    # El filtro por dominio se resuelve en el servidor, por query string; es el
    # mismo enlace de las tarjetas de dominio de la cabecera.
    r.visitar('/controles?dominio=Tecnol%C3%B3gico', 'catalogo_filtrado',
              'Catálogo filtrado por el tema Tecnológico (A.8)')

    # 4. Diagnóstico GAP.
    r.visitar('/diagnostico/ejecutar/%d' % ids['diagnostico_1'], 'diagnostico_gap_1',
              'Primer diagnóstico GAP (línea base)', espera=1500)
    r.visitar('/diagnostico/ejecutar/%d' % ids['diagnostico_2'], 'diagnostico_gap_2',
              'Segundo diagnóstico GAP, con la mejora por cláusula', espera=1500)
    comprobar_porcentajes(r.pagina)

    # 5. Auditoría en ejecución: rejilla y modal con el cálculo de riesgo en vivo.
    r.entrar('pmurillo')
    r.visitar('/auditoria/%d' % ids['bloqueada'], 'auditoria_rejilla',
              'Auditoría en ejecución: rejilla de controles')
    tarjeta = r.pagina.locator('.control-card').first
    tarjeta.click()
    r.pagina.wait_for_timeout(900)
    r.capturar('auditoria_modal_riesgo',
               'Modal de evaluación: criterios, probabilidad x impacto y nivel calculado',
               pagina_completa=False)

    # 6. Regla de bloqueo.
    r.pagina.goto('%s/auditoria/%d' % (BASE, ids['bloqueada']), wait_until=ESPERA_RED)
    finalizar = r.pagina.locator('a, button').filter(has_text='Finalizar').first
    if finalizar.count() == 0:
        raise RuntimeError('No se encontró el botón de finalizar en la auditoría bloqueada')
    finalizar.click()
    r.pagina.wait_for_load_state(ESPERA_RED)
    r.pagina.wait_for_timeout(600)
    r.capturar('regla_de_bloqueo',
               'La regla de bloqueo impide cerrar la auditoría con riesgos altos sin tratar',
               pagina_completa=False)

    # 7. Análisis de riesgos. Como administrador se ve consolidado; un auditor
    # solo ve los controles de sus propias auditorías, así que se capturan ambos.
    r.entrar('lvargas')
    r.visitar('/analisis-riesgos', 'analisis_riesgos_consolidado',
              'Análisis de riesgos consolidado (administrador): riesgos altos de todas '
              'las auditorías, con la auditoría de origen de cada control')
    r.entrar('pmurillo')
    r.visitar('/analisis-riesgos', 'analisis_riesgos_auditor',
              'El mismo análisis visto por una auditora: solo sus propias auditorías')

    # 8. Plan de tratamiento, abierto y cerrado.
    r.visitar('/tratamiento/resultado/%d' % ids['plan_abierto'], 'plan_tratamiento_abierto',
              'Plan de tratamiento en estado %s (antes del cierre)' % ids['plan_abierto_estado'])
    r.entrar('jcastano')
    r.visitar('/tratamiento/resultado/%d' % ids['plan_cerrado'], 'plan_tratamiento_cerrado',
              'Plan de tratamiento ya cerrado, que es lo que libera el cierre de la auditoría')

    # 9. Auditoría finalizada, con sus evidencias.
    r.visitar('/auditoria/%d' % ids['integral'], 'auditoria_finalizada',
              'Detalle de la auditoría integral finalizada, con evidencias adjuntas')
    r.visitar('/auditoria/%d' % ids['verificacion'], 'auditoria_verificacion',
              'Verificación de cierre sobre controles físicos ya remediados')

    # 10. Declaración de Aplicabilidad.
    r.visitar('/documentos', 'soa_resumen', 'Declaración de Aplicabilidad por tema')
    r.visitar('/soa/%d/editar/Tecnológico' % ids['soa'], 'soa_editor',
              'Editor de la SoA: controles aplicables, exclusiones y justificación')

    # 11. Documentación del SGSI.
    r.visitar('/documentos/crear-politica', 'generador_politicas',
              'Generador de políticas y procedimientos del SGSI')
    r.visitar('/documentos/repositorio', 'repositorio_documental',
              'Repositorio documental con el versionado de POL-SGSI-001')

    # 12. Administración: usuarios, bitácora y papelera.
    r.entrar('lvargas')
    r.visitar('/usuarios', 'usuarios', 'Gestión de usuarios y roles')
    r.visitar('/perfil', 'bitacora', 'Perfil del usuario y bitácora de actividad')
    r.visitar('/papelera', 'papelera', 'Papelera: borrado lógico y restauración')

    # 13. Los tres PDF que produce la aplicación.
    r.descargar('/auditoria/reporte/%d' % ids['integral'], 'informe_auditoria',
                'Informe PDF de la auditoría integral')
    r.descargar('/soa/%d/pdf' % ids['soa'], 'informe_soa',
                'Informe PDF de la Declaración de Aplicabilidad')
    r.descargar('/documentos/descargar-doc/%d' % ids['documento'], 'politica_sgsi',
                'PDF de la política POL-SGSI-001 v2.0')


def escribir_indice(capturas):
    ruta = os.path.join(DESTINO, 'INDICE.md')
    with io.open(ruta, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Capturas del caso de demostración\n\n')
        f.write('**DATOS SINTÉTICOS.** Todas las pantallas de esta carpeta corresponden a un '
                'caso de demostración construido para ejercitar SADI. No son resultados de '
                'ninguna organización real. Cualquier figura que se lleve al artículo debe '
                'llevar un pie que lo indique.\n\n')
        f.write('| Archivo | Qué muestra |\n|---|---|\n')
        for nombre, descripcion in capturas:
            f.write('| `%s` | %s |\n' % (nombre, descripcion))
    return ruta


def main():
    if not os.path.isdir(DIRECTORIO_DEMO):
        print('No existe %s. Ejecute antes scripts/generar_datos_demo.py' % DIRECTORIO_DEMO)
        return 1
    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)
    else:
        # Sin esto, una corrida que renumera las capturas deja las anteriores
        # mezcladas con las nuevas y el índice deja de corresponder.
        for nombre in sorted(os.listdir(DESTINO)):
            if nombre.lower().endswith(('.png', '.pdf')):
                os.remove(os.path.join(DESTINO, nombre))

    claves = credenciales()
    ids = identificadores()

    print('Recorrido del caso de demostración en %s' % BASE)
    print('Destino: %s\n' % DESTINO)

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport=VIEWPORT, locale='es-CO')
        pagina = contexto.new_page()
        recorrido = Recorrido(pagina, claves)
        try:
            ejecutar(recorrido, ids)
        finally:
            recorrido.salir()
            contexto.close()
            navegador.close()

    ruta_indice = escribir_indice(recorrido.capturas)
    print('\n%d archivos. Índice en %s' % (len(recorrido.capturas), ruta_indice))
    return 0


if __name__ == '__main__':
    sys.exit(main())
