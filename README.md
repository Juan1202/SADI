# SADI — Sistema de Auditorías y Diagnóstico ISO/IEC 27001:2022

[![devsecops](https://github.com/USUARIO/sadi/actions/workflows/devsecops.yml/badge.svg)](https://github.com/USUARIO/sadi/actions/workflows/devsecops.yml)

Aplicativo web de autodiagnóstico y auditoría del Sistema de Gestión de
Seguridad de la Información (SGSI) bajo ISO/IEC 27001:2022, pensado para
MIPYMES que no pueden pagar herramientas comerciales de GRC.

Proyecto del semillero de investigación de Ingeniería de Sistemas,
Corporación Universitaria Minuto de Dios (UNIMINUTO). Presentado en
**JCUN 2026** (póster, categoría *Gobierno y Cumplimiento*):
*«Modelo de validación e integración de la norma ISO/IEC 27001:2022 para
MIPYMES: SADI aplicativo web de autodiagnóstico»*.

## Qué hace

| Módulo | Descripción |
|---|---|
| Catálogo | Los 93 controles del Anexo A en sus cuatro temas |
| Diagnóstico GAP | 22 requisitos obligatorios de las cláusulas 4 a 10, puntaje `(cumple + 0,5 × parcial) / evaluadas` |
| Auditorías | Hallazgos con probabilidad × impacto (matriz 5 × 5, ISO/IEC 27005) y evidencias |
| **Regla de bloqueo** | Una auditoría no se puede cerrar mientras quede un hallazgo con riesgo ≥ 9 sin plan de tratamiento cerrado |
| **Remediación sugerida** | Para cada hallazgo, controles de NIST SP 800-53 Rev. 5 relacionados oficialmente (NIST OLIR 155), estrategia, plazo y tipo de control según la zona de riesgo |
| Documentación | Declaración de Aplicabilidad y generador de políticas y procedimientos en PDF |
| Administración | Cuatro roles, bitácora de actividad, papelera |

Stack: Python 3.11 · Flask 3.1 · PostgreSQL 15 · MinIO (S3) · Docker Compose.

## Puesta en marcha

```bash
cp .env.example .env                       # y cambiar todos los valores
docker compose up -d --build
docker compose exec web python bootstrap_admin.py
docker compose exec web python seed_controles.py
# opcional: caso de demostración con datos sintéticos
docker compose exec web python seed_demo_sgsi.py --reset
```

Aplicación en <http://localhost:5000>. Las credenciales del caso de
demostración quedan en `data/demo/credenciales.csv` (no versionado).

## Reproducibilidad

| Qué | Cómo reproducirlo |
|---|---|
| Pruebas (74) | `docker compose exec web python -m pytest tests -q` |
| Caso de demostración | `scripts/generar_datos_demo.py` → `seed_demo_sgsi.py --reset` (ver `data/demo/RESULTADOS_DEMO.md`) |
| Capturas del artículo y del póster | `scripts/capturar_evidencias.py` (Playwright) |
| Base de remediación NIST | `scripts/generar_remediacion_nist.py` a partir de NIST OLIR 155 y del catálogo OSCAL oficial; el JSON guarda el SHA-256 de ambas fuentes |
| Pipeline DevSecOps | `.github/workflows/devsecops.yml`; resultados en `docs/devsecops/` |

## Pipeline DevSecOps

Cada push pasa por: pruebas con cobertura, SAST (Bandit y Semgrep), SCA
(pip-audit), secretos (Gitleaks), contenedor e IaC (Trivy) y SBOM CycloneDX.
En la primera ejecución local pip-audit reportó 38 avisos de seguridad (37
vulnerabilidades distintas) en 8 dependencias; quedaron en 0 tras actualizarlas. Detalle en
[`docs/devsecops/README.md`](docs/devsecops/README.md).

## Estado de seguridad

SADI es un MVP académico. La evaluación de seguridad del propio código
identificó 14 hallazgos (S1–S14). Están corregidos el modo depuración fijo (S2)
y las dependencias vulnerables; siguen abiertos, entre otros, la falta de
protección CSRF (S1), operaciones destructivas por GET (S3) y controles de
autorización por rol y por objeto (S4–S6). **No lo despliegue expuesto a
Internet** hasta completar las olas 1 y 2 del plan de remediación.

## Fuentes y licencias de terceros

- Correspondencia ISO/IEC 27001:2022 ↔ NIST SP 800-53 Rev. 5: NIST OLIR
  Informative Reference 155 (2023-10-12), tomada de la versión normalizada de
  [CISO Assistant](https://github.com/intuitem/ciso-assistant-community).
  NIST advierte que las correspondencias indican cobertura general, no
  equivalencia uno a uno.
- Títulos y enunciados de NIST SP 800-53 Rev. 5: catálogo OSCAL oficial,
  [usnistgov/oscal-content](https://github.com/usnistgov/oscal-content)
  (dominio público).
- El texto de ISO/IEC 27001:2022 está protegido por derechos de autor; este
  repositorio usa solo identificadores de controles y descripciones propias.

## Autores

Zharick Duarte Hilamo · María Paula Gracia Torres · Juan Andrés Moya Moreno ·
Ing. Yasmín Becerra Romero (profesora). Facultad de Ingeniería, UNIMINUTO.

> Los datos de `data/demo/` son **sintéticos**: no corresponden a ninguna
> organización real.
