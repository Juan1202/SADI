# -*- coding: utf-8 -*-
"""
Validación del caso cargado, contra la base de datos.

Comprueba lo que el caso promete. Si algo no cuadra se reporta, no se arregla a
mano: hay que corregir los insumos o el cargador y volver a ejecutar.
"""
from sqlalchemy import func

from escalas import UMBRAL_RIESGO_BLOQUEANTE
from models import (
    Diagnostico, Evaluacion, PlanTratamiento, PoliticaSGSI, PreguntaControl,
    RegistroActividad, ResultadoControl, SoADetalle, Usuario, db,
)
from routes.dashboard import _calculate_domain_averages, _calculate_risk_counts

from . import lectura

ZONAS = (
    ('Extrema', 20, 26),
    ('Alta', UMBRAL_RIESGO_BLOQUEANTE, 20),
    ('Moderada', 3, UMBRAL_RIESGO_BLOQUEANTE),
    ('Baja', 1, 3),
)


class Resultado(object):
    def __init__(self):
        self.comprobaciones = []

    def revisar(self, descripcion, condicion, detalle=''):
        self.comprobaciones.append((bool(condicion), descripcion, detalle))
        return bool(condicion)

    @property
    def fallos(self):
        return [c for c in self.comprobaciones if not c[0]]

    @property
    def ok(self):
        return not self.fallos


def _auditoria(clave, filas_csv):
    titulo = next(f['titulo'] for f in filas_csv if f['clave'] == clave)
    return Evaluacion.query.filter_by(titulo=titulo).first()


def validar(ctx):
    resultado = Resultado()
    filas = lectura.auditorias()

    # --- Usuarios y bitácora ---
    esperados = {f['username'] for f in lectura.usuarios()}
    existentes = {u.username for u in Usuario.query.all()}
    resultado.revisar('Los %d usuarios de demostración existen' % len(esperados),
                      esperados.issubset(existentes),
                      'faltan: %s' % ', '.join(sorted(esperados - existentes)))

    roles = {u.role for u in Usuario.query.filter(Usuario.username.in_(esperados)).all()}
    resultado.revisar('Están representados los cuatro roles',
                      roles == {'administrador', 'auditor', 'consultor', 'lector'},
                      'roles encontrados: %s' % ', '.join(sorted(roles)))

    actividad = (db.session.query(RegistroActividad.user_id, func.count(RegistroActividad.id))
                 .group_by(RegistroActividad.user_id).all())
    resultado.revisar('La bitácora registra actividad de más de un usuario',
                      len(actividad) > 1,
                      '%d usuarios con actividad' % len(actividad))

    # --- Diagnósticos ---
    diagnosticos = Diagnostico.query.order_by(Diagnostico.id).all()
    resultado.revisar('Hay dos diagnósticos GAP', len(diagnosticos) == 2,
                      '%d encontrados' % len(diagnosticos))
    if len(diagnosticos) == 2:
        primero, segundo = diagnosticos[0].puntaje_global, diagnosticos[1].puntaje_global
        resultado.revisar('El segundo diagnóstico mejora al primero', segundo > primero,
                          '%.1f %% -> %.1f %%' % (primero, segundo))

    # --- Auditorías ---
    for fila in filas:
        evaluacion = _auditoria(fila['clave'], filas)
        if evaluacion is None:
            resultado.revisar('Existe la auditoría %s' % fila['clave'], False)
            continue
        resultado.revisar('La auditoría %s quedó en estado %s'
                          % (fila['clave'], fila['estado_final']),
                          evaluacion.estado == fila['estado_final'],
                          'estado real: %s' % evaluacion.estado)
        resultado.revisar('La auditoría %s tiene eliminado=%s'
                          % (fila['clave'], fila['eliminado']),
                          evaluacion.eliminado == fila['eliminado'],
                          'eliminado real: %s' % evaluacion.eliminado)
        if fila['estado_final'] == 'Finalizada':
            resultado.revisar('La auditoría %s tiene puntaje mayor que cero' % fila['clave'],
                              (evaluacion.score_promedio or 0) > 0,
                              'score_promedio = %s' % evaluacion.score_promedio)

    # --- Regla de bloqueo, verificada contra la base ---
    bloqueada = _auditoria('organizacional', filas)
    if bloqueada is not None:
        sin_tratar = [
            res.control.codigo
            for res in bloqueada.resultados
            if not res.riesgo_tratado and any(
                (p.probabilidad or 0) * (p.impacto or 0) >= UMBRAL_RIESGO_BLOQUEANTE
                for p in res.preguntas)
        ]
        resultado.revisar('La auditoría organizacional sigue bloqueada por riesgos sin tratar',
                          bool(sin_tratar) and bloqueada.estado == 'En Proceso',
                          'controles bloqueantes: %s' % ', '.join(sorted(sin_tratar)))

    resultado.revisar('Se capturó el mensaje de la regla de bloqueo',
                      bool(ctx.mensaje_bloqueo),
                      ctx.mensaje_bloqueo or 'no se capturó')

    # --- Zonas de riesgo ---
    niveles = [p.probabilidad * p.impacto for p in
               PreguntaControl.query.join(ResultadoControl).join(Evaluacion)
               .filter(Evaluacion.eliminado == False).all()]
    for nombre, minimo, maximo in ZONAS:
        cantidad = sum(1 for n in niveles if minimo <= n < maximo)
        resultado.revisar('Hay al menos un hallazgo en la zona %s' % nombre, cantidad > 0,
                          '%d hallazgos' % cantidad)

    # --- Tablero ---
    promedios = _calculate_domain_averages()
    resultado.revisar('El gráfico GAP por dominios no muestra ceros',
                      all(p > 0 for p in promedios),
                      'promedios por dominio: %s' % promedios)

    activas = Evaluacion.query.filter_by(eliminado=False).all()
    conteos, _ = _calculate_risk_counts(activas)
    resultado.revisar('El tablero identifica auditorías en riesgo crítico',
                      conteos['critico'] > 0,
                      'crítico=%(critico)d alerta=%(alerta)d óptimo=%(optimo)d' % conteos)
    resultado.revisar('La dona de estado de auditorías no tiene segmentos en cero',
                      all(v > 0 for v in conteos.values()),
                      'crítico=%(critico)d alerta=%(alerta)d óptimo=%(optimo)d' % conteos)

    # --- Planes ---
    estados = dict(db.session.query(PlanTratamiento.estado, func.count(PlanTratamiento.id))
                   .group_by(PlanTratamiento.estado).all())
    resultado.revisar('Los planes cubren los tres estados',
                      set(estados) == {'Cerrado', 'En Progreso', 'Abierto'},
                      'estados: %s' % estados)

    estrategias = dict(db.session.query(PlanTratamiento.estrategia, func.count(PlanTratamiento.id))
                       .group_by(PlanTratamiento.estrategia).all())
    resultado.revisar('Los planes cubren las cuatro estrategias',
                      set(estrategias) == {'Mitigar', 'Transferir', 'Aceptar', 'Evitar'},
                      'estrategias: %s' % estrategias)

    incompletos = PlanTratamiento.query.filter(
        (PlanTratamiento.proceso_negocio.is_(None)) |
        (PlanTratamiento.activos_relacionados.is_(None)) |
        (PlanTratamiento.tipo_control.is_(None))).count()
    resultado.revisar('Todos los planes guardaron proceso, activos y tipo de control',
                      incompletos == 0, '%d planes incompletos' % incompletos)

    # --- Evidencias ---
    con_archivo = PreguntaControl.query.filter(
        PreguntaControl.archivo_evidencia.isnot(None)).count()
    resultado.revisar('Hay hallazgos con evidencia en archivo', con_archivo > 0,
                      '%d archivos adjuntos' % con_archivo)

    con_texto = ResultadoControl.query.filter(
        ResultadoControl.evidencia_texto.isnot(None),
        ResultadoControl.evidencia_texto != '').count()
    resultado.revisar('Hay controles con evidencia solo en texto', con_texto > 0,
                      '%d resultados con evidencia textual' % con_texto)

    # --- SoA y documentos ---
    excluidos = SoADetalle.query.filter_by(aplicable=False).count()
    resultado.revisar('La SoA tiene al menos tres controles no aplicables', excluidos >= 3,
                      '%d exclusiones' % excluidos)

    sin_justificar = SoADetalle.query.filter(
        (SoADetalle.justificacion.is_(None)) | (SoADetalle.justificacion == '')).count()
    resultado.revisar('Todos los controles de la SoA tienen justificación',
                      sin_justificar == 0, '%d sin justificar' % sin_justificar)

    documentos = PoliticaSGSI.query.all()
    resultado.revisar('Se generaron los tres documentos del SGSI', len(documentos) == 3,
                      '%d documentos' % len(documentos))
    versionados = [d for d in documentos if d.version != '1.0']
    resultado.revisar('Al menos un documento quedó en una versión posterior',
                      bool(versionados),
                      ', '.join('%s v%s' % (d.codigo, d.version) for d in documentos))

    return resultado


def validar_pdfs(ctx):
    """Comprueba que los tres tipos de PDF se generan sin error."""
    resultado = Resultado()
    filas = lectura.auditorias()
    sesion = ctx.sesion(ctx.admin_usuario)

    integral = _auditoria('integral', filas)
    if integral is not None:
        respuesta = sesion.get('/auditoria/reporte/%d' % integral.id)
        resultado.revisar('El informe PDF de la auditoría integral se genera',
                          respuesta.status_code == 200 and respuesta.data[:4] == b'%PDF',
                          '%d bytes' % len(respuesta.data))

    from models import SoADocument
    soa = SoADocument.query.first()
    if soa is not None:
        respuesta = sesion.get('/soa/%d/pdf' % soa.id)
        resultado.revisar('El informe PDF de la SoA se genera',
                          respuesta.status_code == 200 and respuesta.data[:4] == b'%PDF',
                          '%d bytes' % len(respuesta.data))

    documento = PoliticaSGSI.query.first()
    if documento is not None:
        respuesta = sesion.get('/documentos/descargar-doc/%d' % documento.id)
        resultado.revisar('El PDF de una política se descarga desde MinIO',
                          respuesta.status_code == 200 and respuesta.data[:4] == b'%PDF',
                          '%d bytes' % len(respuesta.data))

    sesion.cerrar_sesion()
    return resultado
