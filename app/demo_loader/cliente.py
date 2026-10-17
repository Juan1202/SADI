# -*- coding: utf-8 -*-
"""
Cliente HTTP sobre las rutas reales de SADI.

La carga del caso de demostración no escribe en la base directamente: usa el
cliente de pruebas de Flask contra las mismas rutas que usa el navegador, con
un usuario autenticado en cada paso. Así se aplican de verdad las reglas de
negocio (la regla de bloqueo, el cálculo de puntajes) y la bitácora queda
poblada con actividad real de cada rol.
"""
import re

ETIQUETA_HTML = re.compile(r'<[^>]+>')


class ErrorDeCarga(Exception):
    """Una ruta respondió algo distinto de lo esperado."""


class SesionSADI(object):
    """Un usuario autenticado contra la aplicación."""

    def __init__(self, app, username, password):
        self.app = app
        self.username = username
        self.cliente = app.test_client()
        self._iniciar_sesion(password)

    def _iniciar_sesion(self, password):
        respuesta = self.cliente.post(
            '/login',
            data={'username': self.username, 'password': password},
            follow_redirects=True,
        )
        if respuesta.status_code != 200:
            raise ErrorDeCarga('Login de %s devolvió %s' % (self.username, respuesta.status_code))
        cuerpo = respuesta.get_data(as_text=True)
        if 'incorrectos' in cuerpo or 'ACCESO DENEGADO' in cuerpo:
            raise ErrorDeCarga('Credenciales rechazadas para %s' % self.username)

    def get(self, ruta, **kwargs):
        kwargs.setdefault('follow_redirects', True)
        return self._verificar('GET', ruta, self.cliente.get(ruta, **kwargs))

    def post(self, ruta, **kwargs):
        kwargs.setdefault('follow_redirects', True)
        return self._verificar('POST', ruta, self.cliente.post(ruta, **kwargs))

    def post_json(self, ruta, carga):
        respuesta = self.cliente.post(ruta, json=carga)
        self._verificar('POST', ruta, respuesta)
        return respuesta.get_json()

    def cerrar_sesion(self):
        self.cliente.get('/logout', follow_redirects=True)

    def _verificar(self, metodo, ruta, respuesta):
        if respuesta.status_code >= 400:
            raise ErrorDeCarga('%s %s como %s devolvió %s' % (
                metodo, ruta, self.username, respuesta.status_code))
        return respuesta


def mensajes_flash(respuesta):
    """
    Extrae el texto de las alertas que dibuja base.html.

    Se usa para capturar el mensaje de la regla de bloqueo, que es una de las
    evidencias que pide el caso.
    """
    cuerpo = respuesta.get_data(as_text=True)
    mensajes = []
    for bloque in re.findall(r'<div class="alert[^"]*"[^>]*>(.*?)</div>', cuerpo, re.S):
        # El bloque incluye el boton de cierre de AdminLTE; solo interesa el texto.
        texto = bloque.split('<button')[0]
        texto = ' '.join(ETIQUETA_HTML.sub(' ', texto).split())
        if texto:
            mensajes.append(texto)
    return mensajes


def contiene(respuesta, fragmento):
    return fragmento in respuesta.get_data(as_text=True)
