# -*- coding: utf-8 -*-
"""
Genera los archivos de evidencia del caso de demostración.

Son archivos reales (PDF con reportlab, imágenes con Pillow) con contenido
plausible. El cargador los sube después por el flujo normal de la aplicación,
no directamente a MinIO, para que pasen por la misma ruta que usaría un auditor.
"""
import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from PIL import Image, ImageDraw

MARCA = 'DOCUMENTO SINTÉTICO — caso de demostración de SADI. No corresponde a una organización real.'

# nombre de archivo -> (título, subtítulo, párrafos, tabla opcional)
PDFS = {
    'EV-01_informe_escaneo_vulnerabilidades.pdf': (
        'Informe de escaneo de vulnerabilidades',
        'Segmento de servidores · 10 de abril de 2026 · Ejecutado durante la auditoría interna',
        [
            'Se ejecutó un escaneo autenticado sobre el segmento 192.168.10.0/24 con el '
            'consentimiento de la Coordinación de TI, en ventana acordada y con alcance de solo '
            'lectura. Se cubrieron 4 activos: servidor ERP, servidor de archivos, controlador de '
            'dominio y el servicio de escritorio remoto publicado.',
            'El resultado confirma que no existe un proceso de gestión de vulnerabilidades: el '
            'último parche de seguridad aplicado al servidor ERP corresponde a septiembre de 2025 '
            'y las actualizaciones automáticas están deshabilitadas.',
        ],
        [
            ['Severidad', 'Cantidad', 'Ejemplo representativo'],
            ['Crítica', '3', 'SMBv1 habilitado en el servidor de archivos'],
            ['Alta', '11', 'Escritorio remoto expuesto sin segundo factor'],
            ['Media', '27', 'Cifrados TLS obsoletos en el portal de pedidos'],
            ['Baja', '42', 'Divulgación de versión en cabeceras HTTP'],
        ],
    ),
    'EV-02_revision_cuentas_activas.pdf': (
        'Revisión de cuentas activas en el ERP y el directorio',
        'Corte al 9 de abril de 2026 · Cruce contra la nómina vigente',
        [
            'Se cruzó el listado de cuentas activas del directorio y del ERP contra la nómina '
            'entregada por Gestión Humana. Se identificaron 7 cuentas pertenecientes a personal '
            'retirado que permanecen habilitadas.',
            'Dos de esas cuentas conservan el perfil de aprobación de órdenes de compra, lo que '
            'representa un riesgo directo sobre el proceso de compras. No se evidencia ninguna '
            'revisión de accesos desde la puesta en operación del ERP en 2023.',
        ],
        [
            ['Cuenta', 'Último ingreso', 'Perfil', 'Situación'],
            ['jrodriguez', '2025-11-14', 'Aprobador de compras', 'Retirado en 2025-11'],
            ['mtorres', '2025-08-02', 'Aprobador de compras', 'Retirado en 2025-07'],
            ['clopez', '2025-06-19', 'Consulta comercial', 'Retirado en 2025-06'],
            ['(otras 4 cuentas)', '2024-2025', 'Consulta', 'Personal retirado'],
        ],
    ),
    'EV-05_borrador_politica_seguridad.pdf': (
        'Borrador de la Política de Seguridad de la Información',
        'Sin número de versión · Sin fecha de vigencia · Sin aprobación',
        [
            'Extracto del archivo encontrado en la carpeta compartida durante la auditoría. El '
            'documento no tiene encabezado de control documental, no indica versión ni fecha de '
            'vigencia, y no registra responsable de revisión ni acta de aprobación.',
            '«La empresa reconoce la importancia de la información y procurará mantener medidas '
            'razonables de protección. El área de sistemas velará por el cumplimiento de esta '
            'política.» — Se observa que el texto es genérico, no define objetivos medibles ni '
            'asigna responsabilidades nominales.',
            'La última modificación del archivo es del 18 de noviembre de 2025. En la muestra de '
            '8 empleados entrevistados, ninguno pudo indicar dónde consultarla.',
        ],
        None,
    ),
    'EV-06_acta_comite_seguridad.pdf': (
        'Acta de comité de seguridad de la información',
        'ACT-SGSI-004 · 6 de abril de 2026',
        [
            'Asistentes: Gerencia General, Oficial de Seguridad de la Información, Coordinación '
            'de TI y Gestión Humana.',
            'Se revisó la ausencia de un proceso disciplinario asociado a la seguridad de la '
            'información. Gestión Humana informa que el reglamento interno de trabajo no tipifica '
            'el incumplimiento de la política de seguridad como falta, por lo que en el caso '
            'reportado en enero de 2026 no fue posible adelantar actuación alguna.',
            'Compromiso: someter a revisión jurídica la modificación del reglamento interno y '
            'surtir el trámite de publicación antes del cierre del primer semestre.',
        ],
        [
            ['Compromiso', 'Responsable', 'Plazo'],
            ['Tipificar la falta en el reglamento', 'Gestión Humana', '2026-07-10'],
            ['Revisión jurídica del texto', 'Asesoría jurídica externa', '2026-06-05'],
            ['Comunicación al personal', 'Gestión Humana', '2026-07-10'],
        ],
    ),
    'EV-07_inventario_privilegios_locales.pdf': (
        'Inventario de privilegios de administrador local',
        'Corte al 5 de junio de 2026 · Auditoría de seguimiento del Tema Tecnológico',
        [
            'Verificación del avance del plan de tratamiento del control A.8.19. Se retiraron los '
            'privilegios de administrador local en 14 de los 22 equipos corporativos.',
            'Los 8 equipos pendientes corresponden en su totalidad a la fuerza comercial, que '
            'trabaja fuera de la sede. La Coordinación de TI informa que el retiro se hará en la '
            'siguiente visita programada de mantenimiento.',
        ],
        [
            ['Área', 'Equipos', 'Sin privilegios', 'Pendientes'],
            ['Administrativa', '9', '9', '0'],
            ['Contabilidad y tesorería', '4', '4', '0'],
            ['Bodega', '1', '1', '0'],
            ['Fuerza comercial', '8', '0', '8'],
            ['TOTAL', '22', '14', '8'],
        ],
    ),
}

# nombre de archivo -> (título, líneas del cuerpo)
IMAGENES = {
    'EV-03_recorrido_escritorio_limpio.png': (
        'Recorrido de verificación — escritorio limpio',
        [
            'Fecha: 13/04/2026    Hora: 19:40    Auditor: J. Castaño',
            '',
            'Puestos verificados .................. 22',
            'Con documentos a la vista ............  9',
            'Sesiones desbloqueadas sin usuario ...  4',
            'Con credenciales anotadas ............  2',
            '',
            'Bloqueo automático por directiva: NO CONFIGURADO',
            '',
            '[ Registro fotográfico omitido por tratarse',
            '  de un caso de demostración ]',
        ],
    ),
    'EV-04_configuracion_red_inalambrica.png': (
        'Configuración de la red inalámbrica',
        [
            'Captura del panel de administración — 13/04/2026',
            '',
            'SSID ................ DEMO-CORP',
            'Seguridad ........... WPA2-PSK',
            'Clave ............... (compartida con invitados)',
            'Último cambio ....... 2023-02-11',
            'VLAN de invitados ... NO CONFIGURADA',
            '',
            'Observación del auditor: la clave se encuentra',
            'escrita en una hoja pegada en la recepción.',
        ],
    ),
}


def _estilos():
    hojas = getSampleStyleSheet()
    return {
        'titulo': ParagraphStyle('t', parent=hojas['Heading1'], fontSize=15, spaceAfter=6),
        'subtitulo': ParagraphStyle('s', parent=hojas['Normal'], fontSize=9,
                                    textColor=colors.HexColor('#555555'), spaceAfter=14),
        'cuerpo': ParagraphStyle('c', parent=hojas['Normal'], fontSize=10, leading=15,
                                 spaceAfter=10),
        'marca': ParagraphStyle('m', parent=hojas['Normal'], fontSize=7.5,
                                textColor=colors.HexColor('#8a6d3b'), spaceAfter=12),
    }


def _construir_pdf(ruta, titulo, subtitulo, parrafos, tabla):
    estilos = _estilos()
    documento = SimpleDocTemplate(ruta, pagesize=letter,
                                  leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                                  topMargin=2 * cm, bottomMargin=2 * cm)
    partes = [
        Paragraph(MARCA, estilos['marca']),
        Paragraph(titulo, estilos['titulo']),
        Paragraph(subtitulo, estilos['subtitulo']),
    ]
    for parrafo in parrafos:
        partes.append(Paragraph(parrafo, estilos['cuerpo']))

    if tabla:
        partes.append(Spacer(1, 6))
        objeto = Table(tabla, hAlign='LEFT')
        objeto.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2f3640')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#999999')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        partes.append(objeto)

    documento.build(partes)


def _construir_imagen(ruta, titulo, lineas):
    ancho, alto = 900, 560
    lienzo = Image.new('RGB', (ancho, alto), '#111820')
    dibujo = ImageDraw.Draw(lienzo)

    dibujo.rectangle([0, 0, ancho, 64], fill='#1b2735')
    dibujo.text((24, 24), titulo, fill='#7fd1ff')
    dibujo.text((24, 86), MARCA, fill='#c0a16b')

    y = 130
    for linea in lineas:
        dibujo.text((32, y), linea, fill='#d6e2ea')
        y += 30

    dibujo.rectangle([0, alto - 34, ancho, alto], fill='#1b2735')
    dibujo.text((24, alto - 24), 'SADI · caso de demostración · datos sintéticos', fill='#6f8596')
    lienzo.save(ruta, 'PNG')


def generar(directorio):
    """Crea los archivos que no existan. Devuelve la lista de rutas."""
    if not os.path.isdir(directorio):
        os.makedirs(directorio)

    rutas = []
    for nombre, (titulo, subtitulo, parrafos, tabla) in PDFS.items():
        ruta = os.path.join(directorio, nombre)
        if not os.path.isfile(ruta):
            _construir_pdf(ruta, titulo, subtitulo, parrafos, tabla)
        rutas.append(ruta)

    for nombre, (titulo, lineas) in IMAGENES.items():
        ruta = os.path.join(directorio, nombre)
        if not os.path.isfile(ruta):
            _construir_imagen(ruta, titulo, lineas)
        rutas.append(ruta)

    return rutas


def abrir(directorio, nombre):
    """Devuelve (BytesIO, nombre) listo para adjuntar a una petición."""
    ruta = os.path.join(directorio, nombre)
    with open(ruta, 'rb') as f:
        return io.BytesIO(f.read()), nombre
