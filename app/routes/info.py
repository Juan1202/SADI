from flask import Blueprint, render_template
from flask_login import login_required

info_bp = Blueprint('info', __name__)


@info_bp.route('/metodologia-riesgos')
@login_required
def metodologia_riesgos():
    return render_template('metodologia_riesgos.html')


@info_bp.route('/clausulas-iso')
@login_required
def clausulas_iso():
    clausulas_data = [
        {
            "id": 4,
            "titulo": "Contexto de la Organización",
            "icono": "fas fa-globe",
            "resumen": "Determinar los factores internos y externos, partes interesadas y el alcance del SGSI.",
            "subpuntos": [
                {"cod": "4.1", "nombre": "Comprensión de la organización y su contexto", "desc": "Determinar cuestiones externas e internas pertinentes para el propósito de la organización."},
                {"cod": "4.2", "nombre": "Comprensión de las necesidades y expectativas de las partes interesadas", "desc": "Identificar quiénes son los interesados y cuáles son sus requisitos de seguridad."},
                {"cod": "4.3", "nombre": "Determinación del alcance del SGSI", "desc": "Definir los límites y la aplicabilidad del sistema de gestión."},
                {"cod": "4.4", "nombre": "Sistema de gestión de la seguridad de la información", "desc": "Establecer, implementar, mantener y mejorar continuamente el SGSI."}
            ]
        },
        {
            "id": 5,
            "titulo": "Liderazgo",
            "icono": "fas fa-chess-king",
            "resumen": "Compromiso de la alta dirección, política de seguridad y roles organizacionales.",
            "subpuntos": [
                {"cod": "5.1", "nombre": "Liderazgo y compromiso", "desc": "La alta dirección debe demostrar liderazgo y compromiso con respecto al SGSI."},
                {"cod": "5.2", "nombre": "Política", "desc": "Establecer una política de seguridad de la información adecuada y disponible."},
                {"cod": "5.3", "nombre": "Roles, responsabilidades y autoridades", "desc": "Asignar y comunicar las responsabilidades y autoridades para los roles pertinentes."}
            ]
        },
        {
            "id": 6,
            "titulo": "Planificación",
            "icono": "fas fa-tasks",
            "resumen": "Acciones para tratar riesgos y oportunidades, y objetivos de seguridad.",
            "subpuntos": [
                {"cod": "6.1", "nombre": "Acciones para tratar riesgos y oportunidades", "desc": "Planificar acciones para abordar los riesgos (6.1.2) y oportunidades identificados."},
                {"cod": "6.2", "nombre": "Objetivos de seguridad de la información", "desc": "Establecer objetivos medibles y planificar cómo lograrlos."},
                {"cod": "6.3", "nombre": "Planificación de los cambios", "desc": "Los cambios en el SGSI deben llevarse a cabo de manera planificada."}
            ]
        },
        {
            "id": 7,
            "titulo": "Apoyo (Soporte)",
            "icono": "fas fa-hands-helping",
            "resumen": "Recursos, competencia, concienciación, comunicación e información documentada.",
            "subpuntos": [
                {"cod": "7.1", "nombre": "Recursos", "desc": "Determinar y proporcionar los recursos necesarios para el SGSI."},
                {"cod": "7.2", "nombre": "Competencia", "desc": "Asegurar que las personas sean competentes basándose en educación, formación o experiencia."},
                {"cod": "7.3", "nombre": "Concienciación", "desc": "Las personas deben ser conscientes de la política y su contribución al SGSI."},
                {"cod": "7.4", "nombre": "Comunicación", "desc": "Determinar qué, cuándo, a quién y cómo comunicar temas del SGSI."},
                {"cod": "7.5", "nombre": "Información documentada", "desc": "Crear y actualizar la documentación requerida y controlarla adecuadamente."}
            ]
        },
        {
            "id": 8,
            "titulo": "Operación",
            "icono": "fas fa-cogs",
            "resumen": "Planificación y control operacional, apreciación y tratamiento de riesgos.",
            "subpuntos": [
                {"cod": "8.1", "nombre": "Planificación y control operacional", "desc": "Implementar y controlar los procesos necesarios para cumplir los requisitos."},
                {"cod": "8.2", "nombre": "Apreciación de riesgos de seguridad", "desc": "Ejecutar el proceso de apreciación de riesgos a intervalos planificados."},
                {"cod": "8.3", "nombre": "Tratamiento de riesgos de seguridad", "desc": "Implementar el plan de tratamiento de riesgos."}
            ]
        },
        {
            "id": 9,
            "titulo": "Evaluación del Desempeño",
            "icono": "fas fa-chart-line",
            "resumen": "Seguimiento, medición, análisis, auditoría interna y revisión por la dirección.",
            "subpuntos": [
                {"cod": "9.1", "nombre": "Seguimiento, medición, análisis y evaluación", "desc": "Evaluar el desempeño de la seguridad y la eficacia del SGSI."},
                {"cod": "9.2", "nombre": "Auditoría interna", "desc": "Realizar auditorías internas a intervalos planificados."},
                {"cod": "9.3", "nombre": "Revisión por la dirección", "desc": "La alta dirección debe revisar el SGSI a intervalos planificados."}
            ]
        },
        {
            "id": 10,
            "titulo": "Mejora",
            "icono": "fas fa-level-up-alt",
            "resumen": "Mejora continua y tratamiento de no conformidades y acciones correctivas.",
            "subpuntos": [
                {"cod": "10.1", "nombre": "Mejora continua", "desc": "Mejorar continuamente la idoneidad, adecuación y eficacia del SGSI."},
                {"cod": "10.2", "nombre": "No conformidad y acción correctiva", "desc": "Reaccionar ante no conformidades, evaluar la necesidad de acciones y corregirlas."}
            ]
        }
    ]
    return render_template('clausulas.html', clausulas=clausulas_data)
