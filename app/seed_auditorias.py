import random
from datetime import datetime, timedelta
from main import app, db
from models import Evaluacion, ResultadoControl, Control, Usuario

random.seed(42)

AUDITORIAS = [
    # (titulo, evaluador, dominio_filtro, estado, dias_atras, score_base, descripcion)
    ("Auditoría Inicial SGSI 2024",         "Carlos Mendoza",    None,              "Finalizada",  340, 2.1, "Evaluación diagnóstica inicial del Sistema de Gestión de Seguridad de la Información."),
    ("Revisión Dominio Organizacional Q1",  "Laura Pérez",       "Organizacional",  "Finalizada",  290, 3.4, "Auditoría trimestral de controles organizacionales — primer trimestre 2024."),
    ("Auditoría Infraestructura TI",        "Andrés Torres",     "Tecnológico",     "Finalizada",  260, 2.8, "Revisión de controles tecnológicos: redes, accesos y gestión de vulnerabilidades."),
    ("Evaluación Seguridad Física",         "María González",    "Físico",          "Finalizada",  240, 3.9, "Auditoría de perímetros físicos, cámaras y control de acceso a instalaciones."),
    ("Auditoría RRHH y Personas",           "Carlos Mendoza",    "Personas",        "Finalizada",  210, 4.2, "Evaluación de controles relacionados con personal: contratación, formación y cese."),
    ("Revisión Política de Accesos",        "Laura Pérez",       "Organizacional",  "Finalizada",  185, 3.1, "Revisión específica de controles 5.15 al 5.18: gestión de identidades y accesos."),
    ("Auditoría Gestión de Incidentes",     "Roberto Silva",     "Organizacional",  "Finalizada",  160, 2.5, "Evaluación de procesos de respuesta y gestión de incidentes de seguridad."),
    ("Revisión Continuidad del Negocio",    "Andrés Torres",     "Organizacional",  "Finalizada",  140, 3.7, "Auditoría de los controles 5.29 y 5.30 de continuidad del negocio y TIC."),
    ("Auditoría Cumplimiento Legal",        "María González",    "Organizacional",  "Finalizada",  120, 4.5, "Revisión de cumplimiento normativo: GDPR, propiedad intelectual y protección de datos."),
    ("Evaluación Seguridad en la Nube",     "Roberto Silva",     "Tecnológico",     "Finalizada",  100, 3.2, "Auditoría de controles aplicados a servicios en la nube y proveedores externos."),
    ("Revisión Dominio Tecnológico Q2",     "Carlos Mendoza",    "Tecnológico",     "Finalizada",   85, 3.6, "Auditoría trimestral de controles tecnológicos — segundo trimestre 2024."),
    ("Auditoría Criptografía y PKI",        "Laura Pérez",       "Tecnológico",     "Finalizada",   70, 4.1, "Revisión de controles de criptografía (8.24) y gestión de claves."),
    ("Evaluación Desarrollo Seguro",        "Andrés Torres",     "Tecnológico",     "Finalizada",   55, 3.0, "Auditoría del ciclo de vida de desarrollo seguro (SSDLC): controles 8.25 al 8.31."),
    ("Revisión Seguridad Física Q3",        "María González",    "Físico",          "Finalizada",   45, 4.4, "Segunda auditoría anual de controles físicos — tercer trimestre 2024."),
    ("Auditoría Integral SGSI Q3",          "Roberto Silva",     None,              "Finalizada",   35, 3.8, "Auditoría integral de todos los dominios — tercer trimestre 2024."),
    ("Evaluación Gestión Proveedores",      "Carlos Mendoza",    "Organizacional",  "Finalizada",   25, 2.9, "Revisión de controles 5.19 al 5.22 sobre gestión de la cadena de suministro."),
    ("Auditoría Monitoreo y Logs",          "Laura Pérez",       "Tecnológico",     "En Proceso",   15, 3.3, "Revisión de controles de logging, monitoreo y sincronización de relojes."),
    ("Revisión Controles de Personas Q4",  "Andrés Torres",     "Personas",        "En Proceso",    8, 0.0, "Auditoría trimestral de controles de personas — cuarto trimestre 2024."),
    ("Evaluación Endpoint y Malware",       "Roberto Silva",     "Tecnológico",     "En Proceso",    3, 0.0, "Revisión de seguridad en dispositivos de usuario y protección contra malware."),
    ("Auditoría Integral SGSI Q4",          "Carlos Mendoza",    None,              "En Proceso",    1, 0.0, "Auditoría integral de cierre de año — cuarto trimestre 2024."),
]

def get_controles(dominio_filtro, max_controles=None):
    if dominio_filtro:
        controles = Control.query.filter_by(dominio=dominio_filtro).all()
    else:
        controles = Control.query.all()
    if max_controles:
        controles = random.sample(controles, min(max_controles, len(controles)))
    return controles

def make_nivel(score_base):
    v = score_base + random.uniform(-1.0, 1.0)
    return round(max(0.0, min(5.0, v)), 2)

def make_evidencia(codigo, nivel):
    if nivel >= 4.0:
        return f"Control {codigo} implementado y verificado. Se revisaron políticas, procedimientos y evidencias documentales. Cumplimiento satisfactorio."
    elif nivel >= 2.5:
        return f"Control {codigo} parcialmente implementado. Se identificaron oportunidades de mejora en la documentación y aplicación práctica."
    elif nivel > 0:
        return f"Control {codigo} con incumplimientos detectados. Se requieren acciones correctivas prioritarias."
    return ""

with app.app_context():
    usuario = Usuario.query.filter_by(username='admin_sadi').first()
    if not usuario:
        print("ERROR: usuario admin_sadi no encontrado")
        exit(1)

    creadas = 0
    for titulo, evaluador, dominio_filtro, estado, dias_atras, score_base, descripcion in AUDITORIAS:
        fecha_creacion = datetime.now() - timedelta(days=dias_atras)

        # Determinar controles según dominio
        if dominio_filtro is None:
            # Auditoría integral: 15-25 controles de todos los dominios
            controles = get_controles(None, max_controles=random.randint(15, 25))
        else:
            controles = get_controles(dominio_filtro)

        # Generar código único
        primero = controles[0].codigo if controles else "GEN"
        ultimo  = controles[-1].codigo if len(controles) > 1 else primero
        base_code = f"AUD-{primero}-{ultimo}" if primero != ultimo else f"AUD-{primero}"
        codigo_final, n = base_code, 1
        while Evaluacion.query.filter_by(codigo=codigo_final).first():
            codigo_final = f"{base_code}-{n}"
            n += 1

        ev = Evaluacion(
            codigo=codigo_final,
            titulo=titulo,
            evaluador=evaluador,
            descripcion=descripcion,
            estado=estado,
            fecha_creacion=fecha_creacion,
            fecha_fin=datetime.now() - timedelta(days=max(0, dias_atras - 5)) if estado == "Finalizada" else None,
            user_id=usuario.id,
            score_promedio=0.0,
        )
        db.session.add(ev)
        db.session.flush()

        suma_score, total = 0.0, 0
        for control in controles:
            nivel = make_nivel(score_base) if estado == "Finalizada" else 0.0
            evidencia = make_evidencia(control.codigo, nivel) if estado == "Finalizada" else ""
            res = ResultadoControl(
                evaluacion_id=ev.id,
                control_id=control.id,
                nivel_cumplimiento=nivel,
                evidencia_texto=evidencia,
            )
            db.session.add(res)
            suma_score += nivel
            total += 1

        ev.score_promedio = round(suma_score / total, 2) if total > 0 else 0.0
        db.session.commit()
        creadas += 1
        estado_sym = "✓" if estado == "Finalizada" else "⏳"
        print(f"  {estado_sym} [{ev.codigo}] {titulo[:45]} — score: {ev.score_promedio} ({total} controles)")

    print(f"\nTotal auditorías creadas: {creadas}")
    total_bd = Evaluacion.query.filter_by(eliminado=False).count()
    finalizadas = Evaluacion.query.filter_by(estado='Finalizada', eliminado=False).count()
    en_proceso  = Evaluacion.query.filter_by(estado='En Proceso', eliminado=False).count()
    print(f"Estado en BD — Total: {total_bd} | Finalizadas: {finalizadas} | En Proceso: {en_proceso}")
