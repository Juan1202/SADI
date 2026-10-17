# -*- coding: utf-8 -*-
"""
Restaura las tildes del texto visible de los módulos del caso de demostración.

El texto se redactó inicialmente sin tildes. Como alimenta las pantallas y los
PDF que se usarán como figuras del artículo, aquí se corrige.

QUE SE TOCA Y QUE NO
--------------------
La sustitución se aplica solo a los literales de una comilla que **contienen al
menos un espacio** y **no van seguidos de dos puntos**. Con esas dos condiciones
quedan fuera, por construcción:

  * las claves de diccionario      ('descripcion': ...)   -> van seguidas de ':'
  * los nombres de archivo         ('EV-02_revision.pdf') -> no tienen espacios
  * los valores de enumeración     ('Cerrado', 'Mitigar') -> no tienen espacios
  * las claves de auditoría        ('tecnologica')        -> no tienen espacios
  * los dominios del catálogo      ('Organizacional')     -> no tienen espacios
  * los docstrings                                        -> van entre comillas dobles

Es idempotente: volver a ejecutarlo no cambia nada.

    python scripts/acentuar_datos_demo.py
"""
import glob
import io
import os
import re
import sys

# Palabras inequívocas. Se excluyen a propósito las ambiguas ('esta', 'continua',
# 'contrato', 'solo'), que se resuelven con las reglas de CONTEXTOS.
TILDES = {
    'accion': 'acción', 'aceptacion': 'aceptación', 'acepto': 'aceptó',
    'acompana': 'acompaña', 'acompanamiento': 'acompañamiento', 'acordo': 'acordó',
    'actuacion': 'actuación', 'actualizacion': 'actualización', 'adopto': 'adoptó',
    'adquisicion': 'adquisición', 'ademas': 'además', 'administracion': 'administración',
    'alli': 'allí', 'ambito': 'ámbito', 'analisis': 'análisis', 'aplicacion': 'aplicación',
    'apreciacion': 'apreciación', 'aprobacion': 'aprobación', 'area': 'área', 'areas': 'áreas',
    'asignacion': 'asignación', 'asigno': 'asignó', 'aun': 'aún',
    'auditoria': 'auditoría', 'auditorias': 'auditorías', 'autorizacion': 'autorización',
    'autenticacion': 'autenticación', 'automatico': 'automático', 'autonomia': 'autonomía',
    'basicas': 'básicas', 'bitacora': 'bitácora', 'buzon': 'buzón',
    'calculo': 'cálculo', 'califico': 'calificó', 'camaras': 'cámaras', 'campana': 'campaña',
    'castano': 'Castaño', 'certificacion': 'certificación', 'cesion': 'cesión',
    'circulacion': 'circulación', 'clasificacion': 'clasificación', 'clasifico': 'clasificó',
    'clausula': 'cláusula', 'clausulas': 'cláusulas', 'codificacion': 'codificación',
    'codigo': 'código', 'codigos': 'códigos', 'comite': 'comité', 'comites': 'comités',
    'comprobo': 'comprobó', 'comunicacion': 'comunicación', 'concienciacion': 'concienciación',
    'condicion': 'condición', 'configuracion': 'configuración', 'contencion': 'contención',
    'contenia': 'contenía', 'contrasena': 'contraseña', 'contratacion': 'contratación',
    'coordinacion': 'coordinación', 'criptografia': 'criptografía',
    'critica': 'crítica', 'criticas': 'críticas', 'critico': 'crítico', 'criticos': 'críticos',
    'decidio': 'decidió', 'decision': 'decisión', 'declaracion': 'declaración',
    'definicion': 'definición', 'definio': 'definió', 'demas': 'demás',
    'demostracion': 'demostración', 'depuracion': 'depuración', 'desconocia': 'desconocía',
    'descripcion': 'descripción', 'desempeno': 'desempeño', 'desvinculacion': 'desvinculación',
    'desviacion': 'desviación', 'deteccion': 'detección', 'detecto': 'detectó',
    'devolucion': 'devolución', 'dia': 'día', 'dias': 'días', 'diagnostico': 'diagnóstico',
    'diseno': 'diseño', 'direccion': 'dirección', 'distribucion': 'distribución',
    'documentacion': 'documentación', 'dueno': 'dueño', 'duenos': 'dueños',
    'duracion': 'duración', 'educacion': 'educación', 'ejecucion': 'ejecución',
    'ejecuto': 'ejecutó', 'electrica': 'eléctrica', 'eliminacion': 'eliminación',
    'emision': 'emisión', 'energia': 'energía', 'envian': 'envían',
    'erradicacion': 'erradicación', 'especifica': 'específica',
    'especificacion': 'especificación', 'especifico': 'específico', 'estan': 'están',
    'estandar': 'estándar', 'estandares': 'estándares', 'evalua': 'evalúa',
    'evaluacion': 'evaluación', 'evaluara': 'evaluará', 'evitacion': 'evitación',
    'exclusion': 'exclusión', 'exposicion': 'exposición', 'extension': 'extensión',
    'facturacion': 'facturación', 'fisica': 'física', 'fisicas': 'físicas', 'fisico': 'físico',
    'formacion': 'formación', 'funcion': 'función', 'generica': 'genérica',
    'gestion': 'gestión', 'grabacion': 'grabación', 'historicas': 'históricas',
    'identificacion': 'identificación', 'impidio': 'impidió', 'inalambrica': 'inalámbrica',
    'induccion': 'inducción', 'informacion': 'información', 'instalacion': 'instalación',
    'integracion': 'integración', 'interes': 'interés', 'interrupcion': 'interrupción',
    'julian': 'Julián', 'juridica': 'jurídica', 'leccion': 'lección', 'lider': 'líder',
    'liquidacion': 'liquidación', 'logico': 'lógico', 'manipulacion': 'manipulación',
    'metodo': 'método', 'metodologia': 'metodología', 'metricas': 'métricas',
    'minima': 'mínima', 'minimo': 'mínimo', 'modificacion': 'modificación',
    'modulo': 'módulo', 'navegacion': 'navegación', 'ningun': 'ningún', 'nomina': 'nómina',
    'notificacion': 'notificación', 'numero': 'número', 'obligacion': 'obligación',
    'observo': 'observó', 'operacion': 'operación', 'ordenes': 'órdenes',
    'organizacion': 'organización', 'otrosi': 'otrosí', 'parametro': 'parámetro',
    'perdida': 'pérdida', 'perdio': 'perdió', 'perimetro': 'perímetro',
    'perimetros': 'perímetros', 'periodica': 'periódica', 'periodicamente': 'periódicamente',
    'periodico': 'periódico', 'podria': 'podría', 'policia': 'policía', 'poliza': 'póliza',
    'politica': 'política', 'politicas': 'políticas', 'portatiles': 'portátiles',
    'preparacion': 'preparación', 'preservacion': 'preservación', 'prestacion': 'prestación',
    'prevencion': 'prevención', 'produccion': 'producción', 'prohibicion': 'prohibición',
    'proposito': 'propósito', 'proteccion': 'protección', 'proyeccion': 'proyección',
    'publica': 'pública', 'publicacion': 'publicación', 'publicas': 'públicas',
    'publico': 'público', 'quedo': 'quedó', 'raiz': 'raíz', 'recepcion': 'recepción',
    'recoleccion': 'recolección', 'recopilacion': 'recopilación',
    'recuperacion': 'recuperación', 'reduccion': 'reducción', 'redireccion': 'redirección',
    'reevalua': 'reevalúa', 'reinicio': 'reinició', 'relacion': 'relación',
    'remediacion': 'remediación', 'rendicion': 'rendición', 'repitio': 'repitió',
    'reporto': 'reportó', 'reprogramacion': 'reprogramación', 'restriccion': 'restricción',
    'retencion': 'retención', 'reunion': 'reunión', 'reutilizacion': 'reutilización',
    'reversion': 'reversión', 'revision': 'revisión', 'rotacion': 'rotación',
    'sabria': 'sabría', 'seccion': 'sección', 'segregacion': 'segregación',
    'segrego': 'segregó', 'segun': 'según', 'seleccion': 'selección',
    'sinteticos': 'sintéticos', 'socializacion': 'socialización', 'supervision': 'supervisión',
    'suscripcion': 'suscripción', 'tamano': 'tamaño', 'tecnicas': 'técnicas',
    'tecnico': 'técnico', 'tecnicos': 'técnicos', 'tecnologia': 'tecnología',
    'tecnologica': 'tecnológica', 'tecnologico': 'tecnológico',
    'tecnologicos': 'tecnológicos', 'telefono': 'teléfono', 'terminacion': 'terminación',
    'terminos': 'términos', 'tesoreria': 'tesorería', 'tramite': 'trámite',
    'transito': 'tránsito', 'traves': 'través', 'tuberia': 'tubería', 'tunel': 'túnel',
    'ubicacion': 'ubicación', 'ubico': 'ubicó', 'ultima': 'última', 'ultimas': 'últimas',
    'ultimo': 'último', 'ultimos': 'últimos', 'unicamente': 'únicamente',
    'validacion': 'validación', 'valoracion': 'valoración', 'vehiculo': 'vehículo',
    'verificacion': 'verificación', 'restauracion': 'restauración',
    'justificacion': 'justificación', 'planificacion': 'planificación',
    'sincronizacion': 'sincronización', 'destruccion': 'destrucción',
    'version': 'versión', 'via': 'vía',
}

# Casos que dependen del contexto: interrogativos indirectos y verbos que se
# escriben igual que un sustantivo. No pueden resolverse palabra por palabra.
CONTEXTOS = [
    ('no esta ', 'no está '),
    ('servidor principal esta ', 'servidor principal está '),
    ('Esta bajo una', 'Está bajo una'),
    ('respaldo continua viajando', 'respaldo continúa viajando'),
    ('continua aplicando cambios', 'continúa aplicando cambios'),
    ('a quien notificar', 'a quién notificar'),
    ('ni en que plazo', 'ni en qué plazo'),
    ('de que información puede ver', 'de qué información puede ver'),
    ('decidir cuando un evento', 'decidir cuándo un evento'),
    ('ni quien lo declara', 'ni quién lo declara'),
    ('indicar donde consultarla', 'indicar dónde consultarla'),
    ('no sabe que aplicaciones', 'no sabe qué aplicaciones'),
    ('web se contrato por precio', 'web se contrató por precio'),
    ('Quien detecta el evento', 'Quien detecta el evento'),
    ('criterio para decidir', 'criterio para decidir'),
]

LITERAL = re.compile(r"'((?:[^'\\]|\\.)*)'")
SIGUE_DOS_PUNTOS = re.compile(r"\s*:")
PATRON_PALABRAS = re.compile(
    r'\b(?:%s)\b' % '|'.join(sorted(TILDES, key=len, reverse=True)), re.IGNORECASE)


def _acentuar(texto):
    def reemplazar(coincidencia):
        palabra = coincidencia.group(0)
        acentuada = TILDES.get(palabra.lower())
        if acentuada is None:
            return palabra
        if palabra[0].isupper():
            return acentuada[0].upper() + acentuada[1:]
        return acentuada[0].lower() + acentuada[1:] if acentuada[0].isupper() else acentuada

    texto = PATRON_PALABRAS.sub(reemplazar, texto)
    for origen, destino in CONTEXTOS:
        texto = texto.replace(origen, destino)
    return texto


def _es_prosa(contenido, resto):
    """Un literal es prosa si tiene espacios y no es la clave de un diccionario."""
    if ' ' not in contenido:
        return False
    return not SIGUE_DOS_PUNTOS.match(resto)


def procesar(ruta):
    original = io.open(ruta, encoding='utf-8').read()
    piezas = []
    posicion = 0

    for coincidencia in LITERAL.finditer(original):
        piezas.append(original[posicion:coincidencia.start()])
        contenido = coincidencia.group(1)
        resto = original[coincidencia.end():coincidencia.end() + 4]
        if _es_prosa(contenido, resto):
            piezas.append("'%s'" % _acentuar(contenido))
        else:
            piezas.append(coincidencia.group(0))
        posicion = coincidencia.end()

    piezas.append(original[posicion:])
    nuevo = ''.join(piezas)

    if nuevo == original:
        return 0
    io.open(ruta, 'w', encoding='utf-8').write(nuevo)
    return sum(1 for a, b in zip(original.split('\n'), nuevo.split('\n')) if a != b)


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    archivos = sorted(glob.glob(os.path.join(raiz, 'scripts', 'demo', '*.py')))
    total = 0
    print('Restaurando tildes en el texto del caso de demostracion\n')
    for ruta in archivos:
        cambios = procesar(ruta)
        total += cambios
        print('  %-34s %3d lineas' % (os.path.basename(ruta), cambios))
    print('\n%d lineas modificadas.' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
