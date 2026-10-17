# -*- coding: utf-8 -*-
"""
La pantalla del diagnostico GAP debe mostrar los puntajes que ya estan guardados.

Antes solo se calculaban en el navegador, con la respuesta del guardado por AJAX:
al reabrir un diagnostico terminado, todas las clausulas aparecian en 0 % y el
global se imprimia sin redondear (86.36363636363636 %).
"""
import re

from models import (
    CategoriaDiagnostico, Diagnostico, PreguntaDiagnostico, RespuestaDiagnostico, db,
)

from conftest import autenticar


def _porcentaje_mostrado(cuerpo, categoria_id):
    """Texto del contador de una clausula, sin depender del orden de los atributos."""
    patron = r'id="cat-text-%d"[^>]*>([^<]+)<' % categoria_id
    encontrado = re.search(patron, cuerpo)
    assert encontrado, 'No se encontró el contador de la cláusula %d' % categoria_id
    return encontrado.group(1).strip()


def _diagnostico(usuario, valores_por_categoria):
    """
    Crea un diagnostico con una categoria por entrada.

    `valores_por_categoria` es {numero_clausula: [valor, ...]}.
    """
    diagnostico = Diagnostico(user_id=usuario.id, estado='Completado')
    db.session.add(diagnostico)
    db.session.flush()

    categorias = {}
    for numero, valores in sorted(valores_por_categoria.items()):
        categoria = CategoriaDiagnostico(numero=str(numero), nombre='Cláusula %s' % numero)
        db.session.add(categoria)
        db.session.flush()
        categorias[numero] = categoria
        for indice, valor in enumerate(valores):
            pregunta = PreguntaDiagnostico(
                categoria_id=categoria.id, requisito='%s.%d' % (numero, indice + 1),
                texto='Requisito %s.%d' % (numero, indice + 1))
            db.session.add(pregunta)
            db.session.flush()
            db.session.add(RespuestaDiagnostico(
                diagnostico_id=diagnostico.id, pregunta_id=pregunta.id, valor=valor))

    db.session.commit()
    return diagnostico, categorias


def test_cada_clausula_muestra_su_propio_puntaje(app, client, administrador):
    diagnostico, categorias = _diagnostico(administrador, {
        4: ['cumple', 'cumple', 'cumple', 'cumple'],     # 100 %
        6: ['cumple', 'no_cumple', 'parcial'],           # 50 %
    })
    autenticar(client, administrador)

    respuesta = client.get('/diagnostico/ejecutar/%d' % diagnostico.id)
    cuerpo = respuesta.data.decode('utf-8')

    assert respuesta.status_code == 200
    assert _porcentaje_mostrado(cuerpo, categorias[4].id) == '100.0%', (
        'La cláusula 4 tiene sus cuatro requisitos en cumple: debe mostrar 100 %.')
    assert _porcentaje_mostrado(cuerpo, categorias[6].id) == '50.0%', (
        'La cláusula 6 suma 1 + 0 + 0,5 sobre 3 requisitos: debe mostrar 50 %.')


def test_una_clausula_sin_evaluar_se_queda_en_cero(app, client, administrador):
    """El cero solo es legitimo cuando de verdad no hay nada evaluado."""
    diagnostico, categorias = _diagnostico(administrador, {
        4: ['cumple'],
        9: ['no_evaluado', 'no_aplica'],
    })
    autenticar(client, administrador)

    cuerpo = client.get('/diagnostico/ejecutar/%d' % diagnostico.id).data.decode('utf-8')

    assert _porcentaje_mostrado(cuerpo, categorias[9].id) == '0.0%'


def test_el_cumplimiento_global_se_muestra_redondeado(app, client, administrador):
    diagnostico, _ = _diagnostico(administrador, {
        4: ['cumple', 'cumple', 'cumple', 'cumple', 'cumple', 'cumple', 'cumple',
            'cumple', 'cumple', 'no_cumple', 'parcial'],
    })
    autenticar(client, administrador)

    cuerpo = client.get('/diagnostico/ejecutar/%d' % diagnostico.id).data.decode('utf-8')

    # 9,5 sobre 11 = 86.36363636...
    assert '86.4%' in cuerpo
    assert '86.36363636' not in cuerpo, 'El puntaje global se está imprimiendo sin redondear.'
