# -*- coding: utf-8 -*-
"""
El adjunto de un hallazgo debe mostrarse con su nombre original.

Al guardarlo, riesgos.py le antepone "{codigo_auditoria}_{control}_P{n}_". La
plantilla mostraba solo el ultimo fragmento separado por guion bajo, asi que
"AUD-5.1-8.34_5.1_P0_EV-05_borrador_politica_seguridad.pdf" se leia como
"seguridad.pdf" y el archivo dejaba de ser identificable.
"""
import pytest

from utils import nombre_original_evidencia


@pytest.mark.parametrize('almacenado, esperado', [
    ('AUD-5.1-8.34_5.1_P0_EV-05_borrador_politica_seguridad.pdf',
     'EV-05_borrador_politica_seguridad.pdf'),
    ('AUD-8.1-8.34_8.8_P1_EV-01_informe_escaneo_vulnerabilidades.pdf',
     'EV-01_informe_escaneo_vulnerabilidades.pdf'),
    ('AUD-7.1-7.14_7.2_P0_acta.pdf', 'acta.pdf'),
])
def test_se_quita_el_prefijo_que_anade_la_aplicacion(almacenado, esperado):
    assert nombre_original_evidencia(almacenado) == esperado


@pytest.mark.parametrize('sin_prefijo', ['acta.pdf', 'informe_anual.pdf', ''])
def test_un_nombre_sin_prefijo_se_deja_igual(sin_prefijo):
    """Los adjuntos cargados antes de que existiera el prefijo no deben mutilarse."""
    assert nombre_original_evidencia(sin_prefijo) == sin_prefijo


def test_tolera_la_ausencia_de_nombre():
    assert nombre_original_evidencia(None) == ''
