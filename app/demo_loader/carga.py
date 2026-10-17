# -*- coding: utf-8 -*-
"""
Carga del caso de demostración por las rutas reales de SADI.

Ninguna cifra se escribe directamente en la base: todo pasa por las mismas
rutas HTTP que usa el navegador, autenticado con el rol que corresponda. Las
consultas al ORM son solo de lectura, para resolver identificadores que la
interfaz conoce y el cargador no (el id de un ResultadoControl, por ejemplo).
"""
import json

from models import (
    Control, Diagnostico, Evaluacion, PoliticaSGSI, PreguntaDiagnostico,
    RespuestaDiagnostico, ResultadoControl, SoADetalle, SoADocument, Usuario, db,
)

from . import evidencias, lectura
from .cliente import ErrorDeCarga, SesionSADI, mensajes_flash

DOMINIOS = ('Organizacional', 'Personas', 'Físico', 'Tecnológico')


class Contexto(object):
    """Estado que comparten los pasos de la carga."""

    def __init__(self, app, admin_usuario, admin_clave, credenciales, registro):
        self.app = app
        self.admin_usuario = admin_usuario
        self.admin_clave = admin_clave
        self.credenciales = credenciales      # {username: password}
        self.registro = registro              # función para imprimir progreso
        self.directorio_evidencias = None
        self.mensaje_bloqueo = None
        self.ids_auditorias = {}              # clave -> id de Evaluacion

    def sesion(self, username):
        clave = self.admin_clave if username == self.admin_usuario else self.credenciales[username]
        return SesionSADI(self.app, username, clave)


# --- Paso 1: usuarios --------------------------------------------------------

def cargar_usuarios(ctx):
    sesion = ctx.sesion(ctx.admin_usuario)
    creados = 0
    for fila in lectura.usuarios():
        username = fila['username']
        if Usuario.query.filter_by(username=username).first():
            ctx.registro('    %-12s ya existía, se omite' % username)
            continue
        sesion.post('/usuarios/crear', data={
            'username': username,
            'password': ctx.credenciales[username],
            'role': fila['rol'],
            'email': fila['email'],
            'cargo': fila['cargo'],
        })
        if not Usuario.query.filter_by(username=username).first():
            raise ErrorDeCarga('No se creó el usuario %s' % username)
        ctx.registro('    %-12s %-14s %s' % (username, fila['rol'], fila['nombre']))
        creados += 1
    sesion.cerrar_sesion()
    return creados


# --- Paso 2: diagnósticos GAP ------------------------------------------------

def cargar_diagnosticos(ctx, propietario):
    sesion = ctx.sesion(propietario)
    resultados = []

    for etiqueta, filas in sorted(lectura.diagnosticos().items()):
        sesion.get('/diagnostico/iniciar')
        diagnostico = (Diagnostico.query
                       .order_by(Diagnostico.id.desc())
                       .first())
        if diagnostico is None:
            raise ErrorDeCarga('No se creó el diagnóstico %s' % etiqueta)

        por_requisito = {
            r.pregunta.requisito: r
            for r in RespuestaDiagnostico.query.filter_by(diagnostico_id=diagnostico.id).all()
        }
        faltantes = [f['requisito'] for f in filas if f['requisito'] not in por_requisito]
        if faltantes:
            raise ErrorDeCarga('Requisitos sin pregunta en SADI: %s' % ', '.join(faltantes))

        puntaje = 0.0
        for fila in filas:
            respuesta = por_requisito[fila['requisito']]
            if fila['valor'] == 'no_evaluado':
                # Solo se guarda la observación: el valor queda como lo dejó la app.
                datos = {'respuesta_id': respuesta.id, 'observacion': fila['observacion']}
            else:
                datos = {'respuesta_id': respuesta.id, 'valor': fila['valor'],
                         'observacion': fila['observacion']}
            salida = sesion.post_json('/diagnostico/api/guardar', datos)
            if not salida or not salida.get('success'):
                raise ErrorDeCarga('Falló el guardado de %s' % fila['requisito'])
            puntaje = salida['puntaje_global']

        ctx.registro('    %s  #%d  puntaje global %.1f %%' % (etiqueta, diagnostico.id, puntaje))
        resultados.append((etiqueta, diagnostico.id, puntaje))

    sesion.cerrar_sesion()
    return resultados


# --- Paso 3: auditorías, hallazgos y evidencias ------------------------------

def _controles_del_alcance(fila_auditoria):
    codigos = fila_auditoria.get('controles_alcance') or []
    alcance = fila_auditoria['alcance']
    if codigos:
        consulta = Control.query.filter(Control.codigo.in_(codigos))
    elif alcance.startswith('Dominio '):
        dominio = alcance[len('Dominio '):].strip()
        consulta = Control.query.filter_by(dominio=dominio)
    else:
        consulta = Control.query
    controles = consulta.all()
    controles.sort(key=lambda c: [int(n) for n in c.codigo.replace('A.', '').split('.')
                                  if n.isdigit()])
    return controles


def crear_auditoria(ctx, fila):
    sesion = ctx.sesion(fila['propietario'])
    controles = _controles_del_alcance(fila)
    if len(controles) != fila['controles']:
        raise ErrorDeCarga('El alcance de %s esperaba %d controles y hay %d'
                           % (fila['clave'], fila['controles'], len(controles)))

    sesion.post('/evaluacion/preparar', data={
        'controles': [str(c.id) for c in controles],
        'auditor': fila['evaluador'],
        'titulo': fila['titulo'],
    })

    evaluacion = Evaluacion.query.filter_by(titulo=fila['titulo']).first()
    if evaluacion is None:
        raise ErrorDeCarga('No se creó la auditoría %s' % fila['clave'])
    ctx.ids_auditorias[fila['clave']] = evaluacion.id

    sesion.post('/auditorias/editar/%d' % evaluacion.id, data={
        'evaluador': fila['evaluador'],
        'descripcion': fila['descripcion'],
        'fecha': fila['fecha'],
    })

    ctx.registro('    %-15s %-14s %2d controles  propietario %s'
                 % (fila['clave'], evaluacion.codigo, len(controles), fila['propietario']))
    sesion.cerrar_sesion()
    return evaluacion.id


def cargar_hallazgos(ctx, fila):
    """Guarda los criterios de cada control por la API de riesgos, con evidencias."""
    sesion = ctx.sesion(fila['propietario'])
    evaluacion_id = ctx.ids_auditorias[fila['clave']]
    agrupados = lectura.hallazgos_por_auditoria(fila['clave'])

    resultados = {
        r.control.codigo: r
        for r in ResultadoControl.query.filter_by(evaluacion_id=evaluacion_id).all()
    }

    total_criterios, total_archivos = 0, 0
    for codigo, criterios in agrupados.items():
        resultado = resultados.get(codigo)
        if resultado is None:
            raise ErrorDeCarga('El control %s no está en el alcance de %s'
                               % (codigo, fila['clave']))

        carga, adjuntos = [], {}
        for indice, criterio in enumerate(criterios):
            carga.append({
                'texto': criterio['criterio'],
                'probabilidad': criterio['probabilidad'],
                'impacto': criterio['impacto'],
                'hallazgo': criterio['hallazgo'],
                'archivo_previo': None,
            })
            if criterio['archivo']:
                adjuntos['file_%d' % indice] = evidencias.abrir(
                    ctx.directorio_evidencias, criterio['archivo'])
                total_archivos += 1

        datos = {'data': json.dumps(carga)}
        datos.update(adjuntos)
        respuesta = sesion.post('/api/control/%d/guardar_preguntas' % resultado.id,
                                data=datos, content_type='multipart/form-data',
                                follow_redirects=False)
        salida = respuesta.get_json()
        esperado = max(c['nivel'] for c in criterios)
        if not salida or salida.get('riesgo_real') != esperado:
            raise ErrorDeCarga('El riesgo guardado en %s no coincide: esperado %d, obtenido %s'
                               % (codigo, esperado, salida))
        total_criterios += len(criterios)

    sesion.cerrar_sesion()
    return total_criterios, total_archivos


def cargar_evidencia_texto(ctx, fila, evidencias_texto):
    """Escribe evidencia_texto por el formulario clásico de la auditoría."""
    if not evidencias_texto:
        return 0
    sesion = ctx.sesion(fila['propietario'])
    evaluacion_id = ctx.ids_auditorias[fila['clave']]
    resultados = {
        r.control.codigo: r
        for r in ResultadoControl.query.filter_by(evaluacion_id=evaluacion_id).all()
    }
    datos = {}
    for codigo, texto in evidencias_texto.items():
        if codigo in resultados:
            datos['evidencia_%d' % resultados[codigo].id] = texto
    if datos:
        sesion.post('/evaluacion/actualizar/%d' % evaluacion_id, data=datos)
    sesion.cerrar_sesion()
    return len(datos)


# --- Paso 4: la regla de bloqueo ---------------------------------------------

def intentar_finalizar(ctx, fila):
    """
    Intenta finalizar la auditoría y devuelve (finalizada, mensajes).

    En el primer intento de la auditoría integral esto DEBE fallar: es la
    evidencia de que la regla de bloqueo funciona.
    """
    sesion = ctx.sesion(fila['propietario'])
    evaluacion_id = ctx.ids_auditorias[fila['clave']]
    evaluacion = Evaluacion.query.get(evaluacion_id)

    respuesta = sesion.post('/auditoria/finalizar',
                            data={'codigo_auditoria_final': evaluacion.codigo})
    mensajes = mensajes_flash(respuesta)
    sesion.cerrar_sesion()

    db.session.expire_all()
    evaluacion = Evaluacion.query.get(evaluacion_id)
    return evaluacion.estado == 'Finalizada', mensajes


# --- Paso 5: planes de tratamiento -------------------------------------------

def cargar_planes(ctx, fila):
    sesion = ctx.sesion(fila['propietario'])
    evaluacion_id = ctx.ids_auditorias[fila['clave']]
    resultados = {
        r.control.codigo: r
        for r in ResultadoControl.query.filter_by(evaluacion_id=evaluacion_id).all()
    }

    por_estado = {}
    for codigo, plan in lectura.planes_por_auditoria(fila['clave']).items():
        resultado = resultados.get(codigo)
        if resultado is None:
            raise ErrorDeCarga('El plan de %s apunta a un control fuera del alcance' % codigo)
        sesion.post('/tratamiento/resultado/%d' % resultado.id, data={
            'descripcion': plan['descripcion_riesgo'],
            'nivel_riesgo': plan['nivel_riesgo_inicial'],
            'proceso': plan['proceso_negocio'],
            'activos': plan['activos_relacionados'],
            'estrategia': plan['estrategia'],
            'acciones': plan['acciones'],
            'tipo_control': plan['tipo_control'],
            'responsable': plan['responsable'],
            'plazo': plan['plazo'],
            'estado': plan['estado'],
        })
        por_estado[plan['estado']] = por_estado.get(plan['estado'], 0) + 1

    sesion.cerrar_sesion()
    return por_estado


# --- Paso 6: papelera --------------------------------------------------------

def enviar_a_papelera(ctx, fila):
    sesion = ctx.sesion(fila['propietario'])
    evaluacion_id = ctx.ids_auditorias[fila['clave']]
    sesion.post('/auditorias/eliminar/%d' % evaluacion_id)
    sesion.cerrar_sesion()

    db.session.expire_all()
    evaluacion = Evaluacion.query.get(evaluacion_id)
    if not evaluacion.eliminado:
        raise ErrorDeCarga('La auditoría %s no quedó en la papelera' % fila['clave'])
    return evaluacion.codigo


# --- Paso 7: Declaración de Aplicabilidad ------------------------------------

def cargar_soa(ctx, propietario):
    sesion = ctx.sesion(propietario)
    sesion.get('/documentos')  # crea los cuatro SoA y sincroniza sus detalles

    por_control = {f['control']: f for f in lectura.soa()}
    resumen = {}

    for dominio in DOMINIOS:
        documento = SoADocument.query.filter_by(dominio=dominio).first()
        if documento is None:
            raise ErrorDeCarga('No se creó el SoA del dominio %s' % dominio)

        detalles = (SoADetalle.query.join(Control)
                    .filter(SoADetalle.soa_id == documento.id, Control.dominio == dominio)
                    .all())
        datos, excluidos = {}, 0
        for detalle in detalles:
            fila = por_control.get(detalle.control.codigo)
            if fila is None:
                continue
            datos['aplicable_%d' % detalle.id] = 'si' if fila['aplicable'] else 'no'
            datos['justificacion_%d' % detalle.id] = fila['justificacion']
            if not fila['aplicable']:
                excluidos += 1

        sesion.post('/soa/%d/editar/%s' % (documento.id, dominio), data=datos)
        resumen[dominio] = (len(detalles), excluidos)

    sesion.cerrar_sesion()
    return resumen


# --- Paso 8: documentos del SGSI ---------------------------------------------

def _formulario_documento(fila, version, desc_cambio, lineamientos):
    return {
        'codigo': fila['codigo'],
        'titulo': fila['titulo'],
        'objetivo': fila['objetivo'],
        'alcance': fila['alcance'],
        'responsables': fila['responsables'],
        'marco_legal': fila['marco_legal'],
        'lineamientos': lineamientos,
        'version': version,
        'fecha_version': fila['fecha_version'],
        'desc_cambio': desc_cambio,
        'elaboro_nombre': fila['elaboro_nombre'],
        'elaboro_cargo': fila['elaboro_cargo'],
        'reviso_nombre': fila['reviso_nombre'],
        'reviso_cargo': fila['reviso_cargo'],
        'aprobo_nombre': fila['aprobo_nombre'],
        'aprobo_cargo': fila['aprobo_cargo'],
    }


def cargar_documentos(ctx, propietario):
    sesion = ctx.sesion(propietario)
    creados, editados = [], []

    for fila in lectura.documentos():
        formulario = _formulario_documento(
            fila, fila['version'], fila['desc_cambio'], fila['lineamientos'])
        sesion.post('/documentos/crear-politica?tipo=%s' % fila['tipo'], data=formulario)

        documento = PoliticaSGSI.query.filter_by(codigo=fila['codigo']).first()
        if documento is None:
            raise ErrorDeCarga('No se creó el documento %s' % fila['codigo'])
        creados.append((documento.id, fila['codigo'], fila['tipo'], documento.version))

        if fila['se_edita'] == 'si':
            edicion = _formulario_documento(
                fila, fila['version_editada'], fila['desc_cambio_edicion'],
                fila['lineamientos_editados'])
            sesion.post('/documentos/editar/%d' % documento.id, data=edicion)
            db.session.expire_all()
            documento = PoliticaSGSI.query.get(documento.id)
            if documento.version != fila['version_editada']:
                raise ErrorDeCarga('No se actualizó la versión de %s' % fila['codigo'])
            editados.append((fila['codigo'], fila['version'], documento.version))

    sesion.cerrar_sesion()
    return creados, editados
