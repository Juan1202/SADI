# -*- coding: utf-8 -*-
"""
Prueba de humo del caso de demostracion: recorre todas las pantallas con el rol
que corresponde y comprueba las restricciones del rol lector.

    docker compose exec web python verificar_pantallas.py
"""
import csv
import io
import sys

sys.path.insert(0, '/app')

from main import app
from models import Evaluacion, PoliticaSGSI, PreguntaControl, ResultadoControl, SoADocument
from demo_loader.cliente import SesionSADI

CRED = '/data/demo/credenciales.csv'


def credenciales():
    with io.open(CRED, encoding='utf-8-sig', newline='') as f:
        filas = list(csv.reader(f, delimiter=';'))
    encabezado = filas[1]
    return {r[0]: r[1] for r in filas[2:] if r}, {r[0]: r[2] for r in filas[2:] if r}


def main():
    with app.app_context():
        claves, roles = credenciales()

        integral = Evaluacion.query.filter(Evaluacion.titulo.like('%integral%')).first()
        bloqueada = Evaluacion.query.filter(
            Evaluacion.titulo.like('%Organizacional%')).first()
        papelera = Evaluacion.query.filter_by(eliminado=True).first()
        soa = SoADocument.query.filter_by(dominio='Tecnológico').first()
        doc = PoliticaSGSI.query.first()
        evidencia = PreguntaControl.query.filter(
            PreguntaControl.archivo_evidencia.isnot(None)).first()
        resultado_alto = None
        for r in bloqueada.resultados:
            if not r.riesgo_tratado and any(
                    (p.probabilidad or 0) * (p.impacto or 0) >= 9 for p in r.preguntas):
                resultado_alto = r
                break

        rutas = [
            ('/', 'Inicio', 'todos'),
            ('/dashboard', 'Tablero de métricas', 'todos'),
            ('/controles', 'Catálogo de controles', 'todos'),
            ('/auditorias', 'Historial de auditorías', 'todos'),
            ('/analisis-riesgos', 'Análisis de riesgos', 'todos'),
            ('/documentos', 'Documentos y SoA', 'todos'),
            ('/documentos/repositorio', 'Repositorio documental', 'todos'),
            ('/metodologia-riesgos', 'Metodología de riesgos', 'todos'),
            ('/clausulas-iso', 'Cláusulas ISO', 'todos'),
            ('/perfil', 'Perfil y bitácora', 'todos'),
            ('/auditoria/%d' % integral.id, 'Detalle auditoría finalizada', 'todos'),
            ('/auditoria/%d' % bloqueada.id, 'Auditoría en ejecución', 'todos'),
            ('/auditoria/reporte/%d' % integral.id, 'Informe PDF de auditoría', 'todos'),
            ('/soa/%d/pdf' % soa.id, 'Informe PDF de SoA', 'todos'),
            ('/documentos/descargar-doc/%d' % doc.id, 'PDF de política', 'todos'),
            ('/uploads/%s' % evidencia.archivo_evidencia, 'Descarga de evidencia', 'todos'),
            ('/usuarios', 'Gestión de usuarios', 'administrador'),
            ('/papelera', 'Papelera', 'administrador'),
            ('/evaluacion/nueva', 'Nueva auditoría', 'auditor'),
            ('/soa/%d/editar/Tecnológico' % soa.id, 'Editor de SoA', 'auditor'),
            ('/documentos/crear-politica', 'Generador de políticas', 'auditor'),
            ('/tratamiento/resultado/%d' % resultado_alto.id, 'Plan de tratamiento', 'auditor'),
        ]

        print('%-46s %-14s %s' % ('PANTALLA', 'ROL', 'RESULTADO'))
        print('-' * 82)
        fallos = 0
        for ruta, nombre, exigido in rutas:
            usuario = {'administrador': 'lvargas', 'auditor': 'jcastano'}.get(exigido, 'mrivas')
            sesion = SesionSADI(app, usuario, claves[usuario])
            respuesta = sesion.cliente.get(ruta, follow_redirects=True)
            sesion.cerrar_sesion()
            ok = respuesta.status_code == 200
            if ok and ruta.endswith('pdf') or 'reporte' in ruta or 'descargar' in ruta:
                ok = ok and len(respuesta.data) > 1000
            estado = 'OK   %d' % respuesta.status_code
            if not ok:
                estado = 'FALLA %d' % respuesta.status_code
                fallos += 1
            print('%-46s %-14s %s' % (nombre, '%s (%s)' % (usuario, roles[usuario]), estado))

        print('-' * 82)
        print('Papelera contiene: %s' % papelera.codigo)
        print('%d fallos' % fallos)

        # El lector no debe poder entrar a lo restringido.
        print()
        print('Restricciones del rol lector:')
        sesion = SesionSADI(app, 'mrivas', claves['mrivas'])
        for ruta, nombre in (('/usuarios', 'Gestión de usuarios'),
                             ('/papelera', 'Papelera'),
                             ('/evaluacion/nueva', 'Nueva auditoría'),
                             ('/diagnostico/iniciar', 'Iniciar diagnóstico')):
            codigo = sesion.cliente.get(ruta, follow_redirects=False).status_code
            print('   %-28s -> %s %s' % (nombre, codigo,
                                         'bloqueado (correcto)' if codigo == 403 else 'PERMITIDO'))
        sesion.cerrar_sesion()
        return fallos


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
