# -*- coding: utf-8 -*-
"""
Exporta los identificadores que necesita el recorrido de capturas.

Solo lectura. Se ejecuta dentro del contenedor, despues de cargar el caso:

    docker compose exec web python exportar_ids_demo.py
    python scripts/capturar_evidencias.py
"""
import io
import json
import sys

sys.path.insert(0, '/app')
from main import app
from models import (Diagnostico, Evaluacion, PlanTratamiento, PoliticaSGSI,
                    PreguntaControl, SoADocument)

with app.app_context():
    integral = Evaluacion.query.filter(Evaluacion.titulo.like('%integral%')).first()
    bloqueada = Evaluacion.query.filter(Evaluacion.titulo.like('%Organizacional%')).first()
    verificacion = Evaluacion.query.filter(Evaluacion.titulo.like('%Verificaci%')).first()
    diagnosticos = [d.id for d in Diagnostico.query.order_by(Diagnostico.id).all()]
    soa = SoADocument.query.filter_by(dominio='Tecnológico').first()
    doc = PoliticaSGSI.query.filter_by(codigo='POL-SGSI-001').first()

    plan_abierto = (PlanTratamiento.query.filter_by(estado='Abierto').first()
                    or PlanTratamiento.query.filter_by(estado='En Progreso').first())
    plan_cerrado = PlanTratamiento.query.filter_by(estado='Cerrado').first()

    # Un control sin tratar con riesgo alto, para el modal y el plan.
    resultado_alto = next(
        r for r in bloqueada.resultados
        if not r.riesgo_tratado and any((p.probabilidad or 0) * (p.impacto or 0) >= 9
                                        for p in r.preguntas))
    # Un control de la integral con evidencia en archivo.
    con_evidencia = PreguntaControl.query.filter(
        PreguntaControl.archivo_evidencia.isnot(None)).first()

    datos = {
        'integral': integral.id,
        'integral_codigo': integral.codigo,
        'bloqueada': bloqueada.id,
        'bloqueada_codigo': bloqueada.codigo,
        'verificacion': verificacion.id,
        'diagnostico_1': diagnosticos[0],
        'diagnostico_2': diagnosticos[1],
        'soa': soa.id,
        'documento': doc.id,
        'plan_abierto': plan_abierto.resultado_control_id,
        'plan_abierto_estado': plan_abierto.estado,
        'plan_cerrado': plan_cerrado.resultado_control_id,
        'resultado_alto': resultado_alto.id,
        'control_alto': resultado_alto.control.codigo,
        'archivo_evidencia': con_evidencia.archivo_evidencia,
    }
    with io.open('/data/demo/ids_capturas.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(datos, indent=2, ensure_ascii=False))
    print(json.dumps(datos, indent=2, ensure_ascii=False))
