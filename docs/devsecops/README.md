# Resultados del pipeline DevSecOps — ejecución local del 17/10/2026

Responde a la oportunidad de mejora de la evaluación JCUN 2026 («integrar el
modelo DevSecOps»). El pipeline está en `.github/workflows/devsecops.yml` y
corre en cada push y pull request. Antes de publicarlo se ejecutaron en local
las compuertas que no dependen de GitHub; estas son sus cifras.

| Compuerta | Herramienta | Antes | Después | Evidencia |
|---|---|---|---|---|
| Pruebas | pytest + pytest-cov | 57 pruebas | **74 pruebas en verde**, cobertura de líneas 44 % | — |
| SAST | Bandit 1.9.4 | 6 hallazgos: 1 alto (B201, depuración activa), 1 medio (B104), 4 bajos | **0 altos, 0 medios**; 4 bajos aceptados | `bandit_antes.json`, `bandit_despues.json` |
| SCA | pip-audit | **38 avisos en 8 paquetes** (37 vulnerabilidades distintas: dos avisos de Werkzeug son el mismo CVE-2024-49767) (Werkzeug, Flask, Pillow, urllib3, requests, idna, python-dotenv, pytest) | **0** | `pip-audit_antes.json`, `pip-audit_despues.json` |
| Secretos | Gitleaks 8.21.2 | 0 fugas en el historial (9 commits) | 0 | — |
| SBOM | CycloneDX 1.6 | — | 36 componentes, todos con versión fijada | `sbom.cdx.json` |
| SAST | Semgrep (OWASP Top 10) | se ejecuta en GitHub Actions | | |
| Contenedor e IaC | Trivy v0.69.3 | se ejecuta en GitHub Actions | | |

## Qué se corrigió

- **S2 — modo depuración fijo en el código** (`app/main.py`). La consola
  interactiva de Werkzeug ya no se activa siempre: solo si `FLASK_DEBUG=1`.
  El `docker-compose.yml` de desarrollo la sigue activando; un despliegue
  productivo no debe definir esa variable.
- **Dependencias vulnerables.** Se actualizaron a la primera versión sin
  vulnerabilidades conocidas: Flask 3.1.3, Werkzeug 3.1.9, Pillow 12.3.0,
  urllib3 2.8.0, requests 2.33.0, idna 3.15, python-dotenv 1.2.2,
  pytest 9.0.3 (y pytest-cov 7.0.0). Las pruebas pasan con las nuevas versiones.
- **Reproducibilidad.** `boto3`, `botocore` y `xhtml2pdf` no tenían versión
  fijada; ahora sí, para que el SBOM y la imagen sean deterministas.

## Hallazgos bajos aceptados

| Regla | Dónde | Por qué se acepta |
|---|---|---|
| B311 (`random`) ×3 | `seed_auditorias.py` | Genera datos de demostración con semilla fija; no es un uso criptográfico. |
| B110 (`try/except/pass`) | `utils.registrar_actividad` | Es el hallazgo S13 de la evaluación de seguridad: queda en el plan de remediación. |
| B104 (bind 0.0.0.0) | `main.py` | Necesario dentro del contenedor; compose publica el puerto solo en 127.0.0.1. Marcado con `# nosec B104`. |

## Lo que el pipeline todavía no resuelve

Los hallazgos de diseño de la evaluación de seguridad (SADI-DOC-06) siguen
abiertos y no los detecta un escáner: **S1** (sin protección CSRF), **S3**
(operaciones destructivas por GET), **S4–S6** (autorización por rol y por
objeto), **S7–S9** (contraseñas, fuerza bruta, cabeceras). Son la ola 1–2 del
plan de remediación.

## Cadena de suministro del propio pipeline

En marzo de 2026 se comprometieron 76 de las 77 etiquetas de
`aquasecurity/trivy-action` y el binario Trivy v0.69.4 (CVE-2026-33634). El
pipeline usa `trivy-action@v0.35.0` y Trivy `v0.69.3`, versiones señaladas
como seguras. El siguiente paso es fijar cada acción a su SHA completo.
