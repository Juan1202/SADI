# -*- coding: utf-8 -*-
"""
Limpieza del caso de demostración (--reset).

Esto no es lógica de negocio sino mantenimiento del entorno de pruebas, así que
sí borra por el ORM: hacerlo por la interfaz exigiría recorrer la papelera
control por control y dejaría el estado a medias si algo fallara.

No toca el catálogo de los 93 controles, ni el usuario administrador, ni los
SoADocument: de estos últimos solo se revierten los detalles a su estado
inicial (aplicable, sin justificación), que es como los crea la aplicación.
"""
from models import (
    Diagnostico, Evaluacion, PlanTratamiento, PoliticaSGSI, PreguntaControl,
    RegistroActividad, RespuestaDiagnostico, ResultadoControl, SoADetalle, Usuario, db,
)

from . import lectura


def _ids_usuarios_demo():
    nombres = [f['username'] for f in lectura.usuarios()]
    return [u.id for u in Usuario.query.filter(Usuario.username.in_(nombres)).all()], nombres


def hay_datos_cargados():
    nombres = [f['username'] for f in lectura.usuarios()]
    return Usuario.query.filter(Usuario.username.in_(nombres)).count() > 0


def resumen_actual():
    ids, _ = _ids_usuarios_demo()
    titulos = [f['titulo'] for f in lectura.auditorias()]
    return {
        'usuarios': len(ids),
        'auditorias': Evaluacion.query.filter(Evaluacion.titulo.in_(titulos)).count(),
        'diagnosticos': Diagnostico.query.filter(Diagnostico.user_id.in_(ids)).count() if ids else 0,
        'documentos': PoliticaSGSI.query.count(),
    }


def limpiar(registro):
    """Borra el caso de demostración. Devuelve un resumen de lo eliminado."""
    ids_usuarios, nombres = _ids_usuarios_demo()
    titulos = [f['titulo'] for f in lectura.auditorias()]
    borrado = {}

    # 1. Auditorías del caso, con sus planes, hallazgos y resultados.
    evaluaciones = Evaluacion.query.filter(Evaluacion.titulo.in_(titulos)).all()
    ids_evaluaciones = [e.id for e in evaluaciones]
    if ids_evaluaciones:
        ids_resultados = [r.id for r in ResultadoControl.query.filter(
            ResultadoControl.evaluacion_id.in_(ids_evaluaciones)).all()]
        if ids_resultados:
            borrado['planes'] = PlanTratamiento.query.filter(
                PlanTratamiento.resultado_control_id.in_(ids_resultados)).delete(
                    synchronize_session=False)
            borrado['hallazgos'] = PreguntaControl.query.filter(
                PreguntaControl.resultado_control_id.in_(ids_resultados)).delete(
                    synchronize_session=False)
        borrado['resultados'] = ResultadoControl.query.filter(
            ResultadoControl.evaluacion_id.in_(ids_evaluaciones)).delete(
                synchronize_session=False)
        borrado['auditorias'] = Evaluacion.query.filter(
            Evaluacion.id.in_(ids_evaluaciones)).delete(synchronize_session=False)
        db.session.commit()

    # 2. Diagnósticos de los usuarios del caso.
    if ids_usuarios:
        ids_diagnosticos = [d.id for d in Diagnostico.query.filter(
            Diagnostico.user_id.in_(ids_usuarios)).all()]
        if ids_diagnosticos:
            borrado['respuestas_diagnostico'] = RespuestaDiagnostico.query.filter(
                RespuestaDiagnostico.diagnostico_id.in_(ids_diagnosticos)).delete(
                    synchronize_session=False)
            borrado['diagnosticos'] = Diagnostico.query.filter(
                Diagnostico.id.in_(ids_diagnosticos)).delete(synchronize_session=False)
        db.session.commit()

    # 3. Documentos del SGSI generados por el caso.
    codigos = [f['codigo'] for f in lectura.documentos()]
    borrado['documentos'] = PoliticaSGSI.query.filter(
        PoliticaSGSI.codigo.in_(codigos)).delete(synchronize_session=False)

    # 4. Declaración de Aplicabilidad: se revierte, no se borra.
    borrado['soa_revertidos'] = SoADetalle.query.update(
        {'aplicable': True, 'justificacion': None}, synchronize_session=False)

    # 5. Bitácora y usuarios del caso.
    if ids_usuarios:
        borrado['bitacora'] = RegistroActividad.query.filter(
            RegistroActividad.user_id.in_(ids_usuarios)).delete(synchronize_session=False)
        borrado['usuarios'] = Usuario.query.filter(
            Usuario.id.in_(ids_usuarios)).delete(synchronize_session=False)

    db.session.commit()

    for clave, cantidad in sorted(borrado.items()):
        if cantidad:
            registro('    %-24s %4d' % (clave, cantidad))

    registro('    Nota: los objetos en MinIO (evidencias y PDF) no se borran; '
             'quedan huérfanos y se sobrescriben en la siguiente carga.')
    return borrado
