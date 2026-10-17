"""
Comprueba que cada prueba de B1-B6 falla contra el codigo original.

Para cada defecto: revierte en el fuente exactamente la linea defectuosa,
ejecuta su prueba dentro del contenedor, restaura el fuente y vuelve a
ejecutarla. La prueba debe salir en ROJO antes y en VERDE despues.

    python scripts/verificar_defectos.py
"""
import io
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# (id, descripcion, [(archivo, texto_corregido, texto_original)], expresion -k)
DEFECTOS = [
    (
        'B1', 'El grafico GAP por dominios toma el segmento equivocado del codigo',
        [('app/routes/dashboard.py',
          "        dom_num_str = codigo.split('.')[0]",
          "        dom_num_str = codigo.split('.')[1]")],
        'b1_el_grafico',
    ),
    (
        'B2', 'El puntaje de la auditoria se calcula sobre campos que nunca se escriben',
        [('app/routes/auditoria.py',
          """    suma, conteo = 0.0, 0
    for res in evaluacion.resultados:
        riesgo = _calculate_max_risk_for_result(res)
        if riesgo <= 0:
            continue  # control sin hallazgos: no participa en el promedio
        suma += madurez_desde_riesgo(riesgo)
        conteo += 1
    return round(suma / conteo, 2) if conteo > 0 else 0.0""",
          """    total_score, count = 0, 0
    respuesta_valores = {'Parcialmente': 3, 'No Cumple': 1}
    for res in evaluacion.resultados:
        if not res.preguntas:
            continue
        sum_preg = sum(
            5 if p.respuesta_bool else respuesta_valores.get(p.respuesta_texto, 0)
            for p in res.preguntas
        )
        total_score += sum_preg / len(res.preguntas)
        count += 1
    return total_score / count if count > 0 else 0.0""")],
        'b2_finalizar',
    ),
    (
        'B3', 'La evidencia del detalle enlaza a static/uploads en vez de a MinIO',
        [('app/templates/detalle_evaluacion.html',
          "{{ url_for('auditoria.download_file', filename=p.archivo_evidencia) }}",
          "{{ url_for('static', filename='uploads/' + p.archivo_evidencia) }}")],
        'b3_la_evidencia',
    ),
    (
        'B4', 'El plan de tratamiento no persiste proceso, activos ni tipo de control',
        [('app/routes/riesgos.py',
          """        plan.proceso_negocio = request.form.get('proceso')
        plan.activos_relacionados = request.form.get('activos')
        plan.estrategia = request.form.get('estrategia')
        plan.acciones = request.form.get('acciones')
        plan.tipo_control = request.form.get('tipo_control')
""",
          """        plan.estrategia = request.form.get('estrategia')
        plan.acciones = request.form.get('acciones')
""")],
        'b4_el_plan',
    ),
    (
        'B5', 'El analisis de riesgos no filtra papelera ni propietario',
        [('app/routes/riesgos.py',
          """                 (PreguntaControl.probabilidad * PreguntaControl.impacto) >= UMBRAL_RIESGO_BLOQUEANTE,
                 Evaluacion.eliminado == False
             ))

    if current_user.role != ROL_ADMINISTRADOR:
        query = query.filter(Evaluacion.user_id == current_user.id)
""",
          """                 (PreguntaControl.probabilidad * PreguntaControl.impacto) >= UMBRAL_RIESGO_BLOQUEANTE,
             ))
""")],
        'b5_',
    ),
    (
        'B6', 'El analisis de riesgos enlaza al plan generico, que no desbloquea el cierre',
        [('app/templates/analisis_riesgos.html',
          "{{ url_for('riesgos.tratar_riesgo_auditoria', resultado_id=item.resultado.id) }}",
          "{{ url_for('riesgos.tratar_riesgo', control_id=item.control.id) }}")],
        'b6_el_analisis',
    ),
]


def aplicar(parches, invertir):
    for ruta, corregido, original in parches:
        archivo = RAIZ / ruta
        contenido = io.open(archivo, encoding='utf-8').read()
        desde, hacia = (corregido, original) if invertir else (original, corregido)
        if desde not in contenido:
            raise SystemExit('No se encontro el fragmento a sustituir en %s' % ruta)
        io.open(archivo, 'w', encoding='utf-8').write(contenido.replace(desde, hacia, 1))


def correr_prueba(filtro):
    proceso = subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'web',
         'python', '-m', 'pytest', 'tests/', '-q', '-k', filtro, '--no-header'],
        cwd=RAIZ, capture_output=True, text=True,
    )
    resumen = [l for l in proceso.stdout.splitlines() if 'passed' in l or 'failed' in l]
    return proceso.returncode, (resumen[-1].strip() if resumen else '(sin resumen)')


def main():
    print('Verificacion RED/GREEN de los defectos B1-B6\n' + '=' * 62)
    todo_ok = True

    for ident, descripcion, parches, filtro in DEFECTOS:
        print('\n%s  %s' % (ident, descripcion))

        aplicar(parches, invertir=True)
        codigo_rojo, resumen_rojo = correr_prueba(filtro)
        aplicar(parches, invertir=False)
        codigo_verde, resumen_verde = correr_prueba(filtro)

        rojo_ok = codigo_rojo != 0
        verde_ok = codigo_verde == 0
        todo_ok = todo_ok and rojo_ok and verde_ok

        print('   sin la correccion : %s  -> %s' % (resumen_rojo, 'ROJO (esperado)' if rojo_ok else 'VERDE (LA PRUEBA NO DETECTA EL DEFECTO)'))
        print('   con la correccion : %s  -> %s' % (resumen_verde, 'VERDE (esperado)' if verde_ok else 'ROJO (LA CORRECCION NO BASTA)'))

    print('\n' + '=' * 62)
    print('RESULTADO: %s' % ('todas las pruebas discriminan su defecto' if todo_ok
                             else 'hay pruebas que no discriminan su defecto'))
    return 0 if todo_ok else 1


if __name__ == '__main__':
    sys.exit(main())
