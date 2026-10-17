# CONTEXTO TÉCNICO — SADI (Sistema de Auditorías y Diagnóstico ISO 27001)

> **Propósito de este archivo:** documento de contexto exhaustivo del aplicativo, pensado para ser cargado en Claude Desktop como insumo para generar la documentación de arquitectura del proyecto (PRD, documento de arquitectura, diseño de sistema, diagramas C4/ER/secuencia, ADRs, plan de mejora, etc.).
>
> Todo lo aquí descrito está extraído directamente del código fuente. Cuando algo es una inferencia o una observación de deuda técnica, está marcado explícitamente.
>
> **Fecha de extracción:** 2026-09-05
> **Tamaño del código:** ~9.755 líneas (Python + Jinja2 + CSS), 54 archivos.

---

## 1. RESUMEN EJECUTIVO

**SADI** es una aplicación web monolítica (Flask + PostgreSQL + MinIO) que digitaliza el ciclo de vida de un **SGSI (Sistema de Gestión de Seguridad de la Información)** bajo la norma **ISO/IEC 27001:2022**.

El sistema cubre seis capacidades funcionales:

| # | Capacidad | Descripción |
|---|-----------|-------------|
| 1 | **Catálogo de controles** | Los 93 controles del Anexo A de ISO 27001:2022, agrupados en 4 dominios (Organizacional, Personas, Físico, Tecnológico). CRUD completo. |
| 2 | **Auditorías / Evaluaciones** | Creación de auditorías seleccionando controles, registro de hallazgos con probabilidad × impacto, adjunto de evidencias, cierre con regla de bloqueo por riesgo crítico, y generación de informe PDF. |
| 3 | **Gestión de riesgos** | Matriz 5×5 (ISO 27005), análisis consolidado de riesgos altos/extremos y planes de tratamiento (mitigar / transferir / aceptar / evitar). |
| 4 | **Diagnóstico GAP** | Cuestionario de autoevaluación sobre las cláusulas 4 a 10 de ISO 27001 con puntuación en tiempo real (global y por cláusula). |
| 5 | **Gestión documental** | Declaración de Aplicabilidad (SoA) por dominio + generador de Políticas y Procedimientos SGSI en PDF, almacenados en MinIO. |
| 6 | **Administración** | Usuarios con 4 roles, bitácora de actividad (audit trail), papelera de reciclaje (soft delete), perfiles. |

**Naturaleza del proyecto:** parece ser un trabajo académico / de grado o un MVP profesional. Está dockerizado, tiene endurecimiento básico de contenedores, seeds de datos de demostración y un diseño de UI muy trabajado (tema oscuro "cyber" + modo claro).

---

## 2. STACK TECNOLÓGICO

### 2.1 Backend

| Componente | Versión | Rol |
|------------|---------|-----|
| Python | 3.11-slim | Runtime |
| Flask | 3.0.0 | Framework web (patrón Blueprints) |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| SQLAlchemy | 2.0.23 | Motor ORM |
| Flask-Migrate | 4.0.1 | Migraciones (Alembic) — *inicializado pero sin carpeta `migrations/` en el repo* |
| Flask-Login | 0.6.3 | Sesiones y autenticación |
| Werkzeug | 3.0.1 | `generate_password_hash` / `check_password_hash` / `secure_filename` |
| psycopg2-binary | 2.9.9 | Driver PostgreSQL |
| boto3 / botocore | latest | Cliente S3 hacia MinIO |
| xhtml2pdf (pisa) | latest | Renderizado HTML → PDF |
| python-dotenv | 1.0.0 | Carga de `.env` |

**Dependencias declaradas pero NO utilizadas en el código actual** (posible deuda o intención futura): `matplotlib`, `numpy`, `pandas`, `openpyxl`, `reportlab`, `pillow`, `requests`, `pytest`, `pytest-cov`.

### 2.2 Frontend

- **Renderizado del lado del servidor** con Jinja2 (no hay SPA, no hay build step, no hay `package.json`).
- **AdminLTE 3.2** (vía CDN jsdelivr) sobre **Bootstrap 4**.
- **Font Awesome 5.15.4** (CDN cdnjs).
- **Chart.js 4.4.1** (CDN) — gráficos del dashboard.
- **jQuery** (incluido con AdminLTE).
- CSS propio: variables CSS (`:root` + `body.light-mode`) para tema dual claro/oscuro; persistencia del tema en `localStorage`.
- JavaScript vanilla con `fetch()` para los endpoints tipo API.

### 2.3 Infraestructura

| Servicio | Imagen | Puertos | Notas |
|----------|--------|---------|-------|
| `web` | build local (Dockerfile) | `127.0.0.1:5000:5000` | Bind solo a localhost. Volumen `./app:/app` (modo desarrollo). |
| `db` | `postgres:15-alpine` | interno | Volumen `postgres_data`. Healthcheck `pg_isready`. |
| `minio` | `minio/minio:latest` | `9003:9009` (API S3), `9001:9001` (consola) | Volumen `minio_data`. Healthcheck `/minio/health/live`. |

Red: `iso-network` (bridge).

**Endurecimiento aplicado en `docker-compose.yml` y `Dockerfile`:**
- Usuario no-root (`appuser`/`appgroup`) en el contenedor web.
- `cap_drop: ALL` en `web`.
- `security_opt: no-new-privileges:true` en `web` y `db`.
- Límites de recursos: 0.50 CPU / 512 MB por contenedor.
- Healthchecks nativos en los tres servicios.
- `depends_on` con `condition: service_healthy`.

---

## 3. ESTRUCTURA DE DIRECTORIOS

```
ISO27001-Auditoria/
├── .env                      # secretos reales (git-ignored)
├── .env.example              # plantilla de variables
├── .gitignore
├── Dockerfile                # imagen del servicio web
├── docker-compose.yml        # orquestación de 3 servicios
├── requirements.txt
└── app/
    ├── __init__.py           # hack de alias de módulos (ver §4.1)
    ├── main.py               # application factory implícito: crea app, registra blueprints
    ├── models.py             # 13 modelos SQLAlchemy
    ├── extensions.py         # cliente S3/MinIO + creación de buckets
    ├── utils.py              # decoradores de rol, validaciones, audit log
    ├── seed_controles.py     # carga los 93 controles ISO 27001:2022
    ├── seed_auditorias.py    # genera 20 auditorías de demostración
    ├── routes/               # 10 blueprints
    │   ├── __init__.py       # (vacío)
    │   ├── auth.py           # login / logout
    │   ├── dashboard.py      # inicio + métricas KPI
    │   ├── usuarios.py       # gestión de usuarios y perfil
    │   ├── controles.py      # CRUD del catálogo ISO
    │   ├── auditoria.py      # ciclo de vida de auditorías (el más grande: 358 líneas)
    │   ├── riesgos.py        # hallazgos, matriz de riesgo, planes de tratamiento
    │   ├── documentos.py     # SoA + generador de políticas
    │   ├── diagnostico.py    # GAP analysis de cláusulas 4-10
    │   ├── admin.py          # reset de BD
    │   └── info.py           # metodología de riesgos + cláusulas ISO (datos hardcodeados)
    ├── static/
    │   ├── custom.css        # 473 líneas — estilos de login y componentes "cyber"
    │   └── uploads/          # carpeta local de subidas (vacía; el almacén real es MinIO)
    └── templates/            # 28 plantillas Jinja2
```

---

## 4. ARQUITECTURA DE LA APLICACIÓN

### 4.1 Bootstrap y el hack de `app/__init__.py`

`app/__init__.py` contiene un mecanismo poco convencional: registra manualmente en `sys.modules` alias de forma que `app.models`, `app.utils`, `app.extensions` y `app.routes` resuelvan al **mismo objeto módulo** que `models`, `utils`, `extensions` y `routes`.

**Motivo declarado en el docstring:** *"evitando instancias duplicadas de SQLAlchemy entre la app y los tests"*.

**Consecuencia arquitectónica:** todos los imports internos usan rutas planas (`from models import db`, `from routes.auth import auth_bp`) y no rutas de paquete. Esto funciona porque el `WORKDIR` del contenedor es `/app` y el código se copia con `COPY app/ .` (es decir, dentro del contenedor los módulos están en la raíz). **Esto acopla el código a la disposición del contenedor**: ejecutar `python app/main.py` desde la raíz del repo en el host fallaría sin ajustar `PYTHONPATH`.

### 4.2 `main.py` — composición de la aplicación

No hay *application factory* (`create_app()`); la instancia `app` es un objeto global de módulo. Secuencia:

1. Crea `Flask(__name__)`.
2. Configura: `SQLALCHEMY_DATABASE_URI` (de `DATABASE_URL`), `SECRET_KEY` (de env), `UPLOAD_FOLDER` (`static/uploads`), `MAX_CONTENT_LENGTH = 16 MB`.
3. `db.init_app(app)` y `Migrate(app, db)`.
4. `LoginManager` con `login_view = 'auth.login'` y `user_loader` → `Usuario.query.get(int(user_id))`.
5. Importa y registra los **10 blueprints**.
6. `errorhandler(403)` → `403.html`.
7. Dentro de `app.app_context()`: `init_s3_bucket()` (crea los buckets si no existen) y `db.create_all()` en un `try/except`.
8. `app.run(host='0.0.0.0', port=5000, debug=True)` si se ejecuta como `__main__`.

**Observaciones de arquitectura:**
- Coexisten `db.create_all()` y Flask-Migrate → estrategia de esquema ambigua.
- `debug=True` está fijo en el código, y `docker-compose.yml` además define `FLASK_ENV=development` y `FLASK_DEBUG=1`. **No apto para producción** (consola de depuración de Werkzeug expuesta).
- Servidor de desarrollo de Flask, sin Gunicorn/uWSGI ni reverse proxy.
- No hay `CSRFProtect` / Flask-WTF: **ninguna ruta POST tiene protección CSRF**.

### 4.3 Patrón de capas

```
┌──────────────────────────────────────────────────────────┐
│  Presentación: Jinja2 (28 plantillas) + AdminLTE + JS     │
│  base.html define el layout, sidebar y sistema de temas    │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTP (form-encoded / JSON)
┌────────────────────────────▼─────────────────────────────┐
│  Rutas: 10 Blueprints en app/routes/                      │
│  - Contienen lógica de negocio (no hay capa de servicio)  │
│  - Helpers privados con prefijo _ dentro de cada módulo   │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│  Transversal: utils.py (decoradores de rol, audit log)    │
│               extensions.py (cliente S3)                  │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│  Datos: models.py (SQLAlchemy) → PostgreSQL               │
│         boto3 → MinIO (2 buckets)                         │
└──────────────────────────────────────────────────────────┘
```

**No existe capa de servicios ni de repositorios.** La lógica de negocio vive en las funciones de ruta, parcialmente extraída a funciones helper con prefijo `_` (p. ej. `_calculate_audit_score`, `_check_critical_risk`, `_collect_policy_form_data`).

---

## 5. MODELO DE DATOS

13 modelos en `app/models.py`. Todas las tablas usan `id` entero autoincremental como PK.

### 5.1 Diagrama de relaciones (textual)

```
Usuario (usuarios)
  │
  ├──1:N── Evaluacion (evaluaciones)          [user_id]
  ├──1:N── RegistroActividad (registros_actividad)
  ├──1:N── PoliticaSGSI (politicas_sgsi)
  └──1:N── Diagnostico (diagnosticos)

Control (controles)  ← catálogo maestro, 93 filas
  ├──1:N── ResultadoControl (resultados_control)
  ├──1:N── SoADetalle (soa_detalles)
  └──1:N── PlanTratamiento (planes_tratamiento)

Evaluacion (evaluaciones)
  └──1:N── ResultadoControl  [cascade delete-orphan]
              └──1:N── PreguntaControl (preguntas_control)  [cascade delete-orphan]
              └──1:1── PlanTratamiento (opcional)

SoADocument (soa_documents)
  └──1:N── SoADetalle  [cascade delete-orphan]

CategoriaDiagnostico (categorias_diagnostico)
  └──1:N── PreguntaDiagnostico (preguntas_diagnostico)  [cascade delete-orphan]

Diagnostico (diagnosticos)
  └──1:N── RespuestaDiagnostico (respuestas_diagnostico)  [cascade delete-orphan]
              └──N:1── PreguntaDiagnostico
```

### 5.2 Detalle de cada modelo

#### `Control` — tabla `controles`
Catálogo maestro del Anexo A.

| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | Integer PK | |
| `codigo` | String(20) UNIQUE NOT NULL | p. ej. `5.1`, `8.34` |
| `nombre` | String(200) NOT NULL | |
| `descripcion` | Text | Texto normativo del control |
| `dominio` | String(100) NOT NULL | `Organizacional` \| `Personas` \| `Físico` \| `Tecnológico` |

Relación: `resultados` → `ResultadoControl` (cascade all, delete-orphan).

**Distribución real de los 93 controles** (según `seed_controles.py`):
- Organizacional (5.1–5.37): **37**
- Personas (6.1–6.8): **8**
- Físico (7.1–7.14): **14**
- Tecnológico (8.1–8.34): **34**

#### `Evaluacion` — tabla `evaluaciones`
Cabecera de una auditoría.

| Campo | Tipo | Default | Notas |
|-------|------|---------|-------|
| `id` | Integer PK | | |
| `codigo` | String(20) UNIQUE | | Generado: `AUD-{primerControl}-{últimoControl}` con sufijo numérico si colisiona |
| `titulo` | String(200) | | |
| `fecha_inicio` | DateTime | `utcnow` | |
| `fecha_fin` | DateTime NULL | | Se fija al finalizar |
| `evaluador` | String(100) NOT NULL | | Nombre libre del auditor (no FK) |
| `estado` | String(20) | `'Iniciada'` | En la práctica: `'En Proceso'` \| `'Finalizada'` |
| `fecha_creacion` | DateTime | `utcnow` | |
| `descripcion` | Text NULL | | |
| `score_promedio` | Float | 0.0 | **Semántica ambigua — ver §7.4** |
| `user_id` | FK usuarios.id NULL | | Propietario |
| `eliminado` | Boolean | False | Soft delete → papelera |

#### `ResultadoControl` — tabla `resultados_control`
Fila de unión entre una auditoría y un control evaluado.

| Campo | Tipo | Notas |
|-------|------|-------|
| `evaluacion_id` | FK evaluaciones.id NOT NULL | |
| `control_id` | FK controles.id NOT NULL | |
| `nivel_cumplimiento` | Float, default 0.0 | **Campo sobrecargado — ver §7.4** |
| `evidencia_texto` | Text NULL | |
| `evidencia_archivo` | String(255) NULL | Clave del objeto en MinIO |
| `riesgo_tratado` | Boolean, default False | Se pone `True` cuando su plan de tratamiento pasa a `Cerrado` |

#### `PreguntaControl` — tabla `preguntas_control`
Criterio/hallazgo individual dentro de un control evaluado. Es la unidad atómica de la evaluación de riesgo.

| Campo | Tipo | Notas |
|-------|------|-------|
| `resultado_control_id` | FK resultados_control.id NOT NULL | |
| `texto_pregunta` | String(500) NOT NULL | Criterio evaluado |
| `peso_porcentaje` | Integer NOT NULL | Siempre se guarda `0` en el flujo actual |
| `tipo_respuesta` | String(20), default `'si_no'` | El flujo actual siempre escribe `'riesgo'` |
| `respuesta_bool` | Boolean NULL | **Nunca se escribe en el flujo actual** |
| `respuesta_texto` | Text NULL | **Nunca se escribe en el flujo actual** |
| `puntaje_obtenido` | Float, default 0.0 | No se usa |
| `hallazgo` | Text NULL | Descripción del hallazgo |
| `archivo_evidencia` | String(255) NULL | Clave en MinIO |
| `probabilidad` | Integer, default 1 | Escala 1–5 |
| `impacto` | Integer, default 1 | Escala 1–5 |
| `nivel_riesgo` | Integer, default 1 | Producto `probabilidad × impacto` (1–25) |

#### `PlanTratamiento` — tabla `planes_tratamiento`
Plan de tratamiento del riesgo. Puede colgar de un control (genérico) o de un `ResultadoControl` (específico de una auditoría).

| Campo | Tipo | Valores |
|-------|------|---------|
| `control_id` | FK controles.id NOT NULL | |
| `resultado_control_id` | FK resultados_control.id NULL | 1:1 (`uselist=False`) |
| `codigo_riesgo` | String(50) | Generado: `R-{codigoControl}-{NNN}` |
| `descripcion_riesgo` | Text | |
| `nivel_riesgo_inicial` | Integer | |
| `proceso_negocio` | String(100) | *(campo del formulario `proceso`, no se persiste en el POST actual)* |
| `activos_relacionados` | String(200) | *(campo del formulario `activos`, no se persiste en el POST actual)* |
| `estrategia` | String(50) | `Mitigar` \| `Transferir` \| `Aceptar` \| `Evitar` |
| `acciones` | Text | |
| `tipo_control` | String(50) | `Preventivo` \| `Detective` \| `Correctivo` \| `Disuasivo` *(no se persiste en el POST actual)* |
| `responsable` | String(100) | |
| `plazo` | Date | |
| `estado` | String(20), default `'Abierto'` | `Abierto` \| `En Progreso` \| `Cerrado` |
| `fecha_creacion` / `fecha_actualizacion` | DateTime | `onupdate=utcnow` |

#### `SoADocument` — tabla `soa_documents`
Declaración de Aplicabilidad. **Se crea automáticamente una por dominio** la primera vez que se abre `/documentos`.

| Campo | Tipo | Notas |
|-------|------|-------|
| `codigo` | String(50) | `SOA-{año}-{3 primeras letras del dominio en mayúsculas}` |
| `version` | String(10), default `"1.0"` | |
| `dominio` | String(50), default `"General"` | Uno de los 4 dominios |
| `fecha_creacion` / `fecha_actualizacion` | DateTime | |
| `estado` | String(20), default `'Borrador'` | |

#### `SoADetalle` — tabla `soa_detalles`
| Campo | Tipo | Notas |
|-------|------|-------|
| `soa_id` | FK soa_documents.id NOT NULL | |
| `control_id` | FK controles.id NOT NULL | |
| `aplicable` | Boolean, default True | Sí/No |
| `justificacion` | Text NULL | Justificación de inclusión/exclusión |

#### `Usuario` — tabla `usuarios` (hereda `UserMixin`)
| Campo | Tipo | Notas |
|-------|------|-------|
| `username` | String(50) UNIQUE NOT NULL | |
| `password_hash` | String(256) NOT NULL | `werkzeug.generate_password_hash` (PBKDF2 por defecto) |
| `role` | String(20), default `'consultor'` | `administrador` \| `auditor` \| `consultor` \| `lector` |
| `activo` | Boolean, default True | Expuesto como propiedad `is_active` con getter/setter |
| `email` | String(120) NULL | |
| `cargo` | String(100) NULL | |

Métodos: `set_password()`, `check_password()`.

#### `RegistroActividad` — tabla `registros_actividad`
Bitácora de auditoría interna (audit trail).

| Campo | Tipo |
|-------|------|
| `user_id` | FK usuarios.id NOT NULL |
| `accion` | String(100) NOT NULL |
| `modulo` | String(50) NOT NULL |
| `detalle` | Text NULL (truncado a 500 caracteres) |
| `ip_address` | String(45) NULL (`request.remote_addr`) |
| `fecha` | DateTime NOT NULL, default `utcnow` |

#### `PoliticaSGSI` — tabla `politicas_sgsi`
Metadatos de los documentos normativos generados.

| Campo | Tipo | Notas |
|-------|------|-------|
| `codigo` | String(50) NOT NULL | |
| `titulo` | String(200) NOT NULL | |
| `version` | String(10), default `"1.0"` | |
| `tipo` | String(50), default `"política"` | `Política` \| `Procedimiento` |
| `nombre_archivo` | String(255) | Clave del PDF en MinIO |
| `ruta_minio` | String(255) | Nombre del bucket |
| `fecha_creacion` | DateTime | |
| `user_id` | FK usuarios.id | |
| `datos_formulario` | Text NULL | **JSON serializado** de todos los campos del formulario (sin el logo) — permite reeditar el documento |

#### Módulo de diagnóstico (3 modelos)

**`CategoriaDiagnostico`** — `numero` (String(10), p. ej. `"4"`), `nombre` (String(100)).
**`PreguntaDiagnostico`** — `categoria_id` FK, `requisito` (String(20), p. ej. `"6.1.2"`), `texto` (Text).
**`Diagnostico`** — `fecha_creacion`, `fecha_actualizacion`, `estado` (default `'En progreso'`), `puntaje_global` (Float), `user_id` FK.
**`RespuestaDiagnostico`** — `diagnostico_id` FK, `pregunta_id` FK, `valor` (String(20), default `'no_evaluado'`; valores: `cumple` \| `parcial` \| `no_cumple` \| `no_aplica`), `observacion` (Text).

---

## 6. INVENTARIO COMPLETO DE RUTAS

10 blueprints, 41 rutas. Los decoradores de autorización están en `utils.py`.

### 6.1 Decoradores de seguridad (`utils.py`)

```python
admin_required          # exige current_user.role == 'administrador', si no → abort(403)
role_required(*roles)   # exige current_user.role in roles, si no → abort(403)
login_required          # de Flask-Login
```

Constantes de rol: `administrador`, `auditor`, `consultor`, `lector`.
Constantes de dominio: `Organizacional`, `Personas`, `Físico`, `Tecnológico`.
Extensiones permitidas para subida: `txt, pdf, png, jpg, jpeg, xlsx, xls, docx, doc`.

### 6.2 Tabla de rutas

| Blueprint | Método(s) | Ruta | Función | Autorización |
|-----------|-----------|------|---------|--------------|
| **auth** | GET/POST | `/login` | `login` | pública |
| auth | GET | `/logout` | `logout` | login |
| **dashboard** | GET | `/` | `home` | login |
| dashboard | GET | `/dashboard` | `dashboard_metrics` | login |
| **usuarios** | GET | `/usuarios` | `gestion_usuarios` | admin |
| usuarios | POST | `/usuarios/crear` | `crear_usuario` | admin |
| usuarios | POST | `/usuarios/eliminar/<int:id>` | `eliminar_usuario` | admin |
| usuarios | GET | `/usuarios/ver/<int:id>` | `ver_usuario_detalle` | admin |
| usuarios | POST | `/usuarios/editar_guardar/<int:id>` | `guardar_edicion_usuario` | admin |
| usuarios | POST | `/usuarios/toggle/<int:id>` | `toggle_usuario` | admin |
| usuarios | GET | `/perfil` | `mi_perfil` | login |
| **controles** | GET | `/controles` | `listar_controles` | login |
| controles | POST | `/controles/nuevo` | `nuevo_control` | admin, auditor |
| controles | **GET** | `/controles/eliminar/<int:id>` | `eliminar_control` | admin |
| controles | POST | `/controles/editar/<int:id>` | `editar_control` | admin, auditor |
| **auditoria** | GET | `/evaluacion/nueva` | `vista_nueva_evaluacion` | admin, auditor |
| auditoria | POST | `/evaluacion/preparar` | `preparar_auditoria` | admin, auditor |
| auditoria | POST | `/auditoria/finalizar` | `finalizar_auditoria` | admin, auditor |
| auditoria | GET | `/auditoria/<int:id>` | `ver_evaluacion` | login |
| auditoria | GET | `/auditorias` | `listar_auditorias` | login (+ filtro por propietario si no es admin) |
| auditoria | POST | `/auditorias/editar/<int:id>` | `editar_auditoria` | login + verificación de propiedad |
| auditoria | **GET**/POST | `/auditorias/eliminar/<int:id>` | `eliminar_auditoria` (soft delete) | login + propiedad |
| auditoria | POST | `/evaluacion/actualizar/<int:id>` | `actualizar_auditoria` | admin, auditor |
| auditoria | GET | `/uploads/<path:filename>` | `download_file` (desde MinIO) | login |
| auditoria | GET | `/auditoria/reporte/<int:evaluacion_id>` | `generar_pdf` | login |
| auditoria | POST | `/auditoria/cerrar/<int:id>` | `cerrar_ciclo_auditoria` | login + propiedad |
| auditoria | GET | `/papelera` | `ver_papelera` | admin |
| auditoria | POST | `/auditoria/restaurar/<int:id>` | `restaurar_auditoria` | admin |
| auditoria | POST | `/auditoria/eliminar_definitivo/<int:id>` | `eliminar_auditoria_definitivo` | admin |
| **riesgos** | GET | `/api/control/<int:control_id>/obtener_preguntas` | `obtener_preguntas` (JSON) | login |
| riesgos | POST | `/api/control/<int:control_id>/guardar_preguntas` | `guardar_preguntas_control` (JSON) | login |
| riesgos | GET | `/analisis-riesgos` | `analisis_riesgos` | login |
| riesgos | GET/POST | `/tratamiento/resultado/<int:resultado_id>` | `tratar_riesgo_auditoria` | admin, auditor |
| riesgos | GET/POST | `/tratamiento/control/<int:control_id>` | `tratar_riesgo` | login |
| **documentos** | GET | `/documentos` | `vista_documentos` (auto-crea SoAs) | login |
| documentos | GET/POST | `/soa/<int:id>/editar/<dominio>` | `editar_soa_dominio` | admin, auditor |
| documentos | GET | `/soa/<int:id>/pdf` | `generar_pdf_soa` | login |
| documentos | GET | `/documentos/tipo` | `seleccionar_tipo_documento` | login |
| documentos | GET/POST | `/documentos/crear-politica` | `crear_politica` | admin, auditor |
| documentos | GET | `/documentos/repositorio` | `listar_documentos_generados` | login |
| documentos | POST | `/documentos/eliminar/<int:id>` | `eliminar_documento_sgsi` | admin |
| documentos | GET/POST | `/documentos/editar/<int:id>` | `editar_politica` | **login (cualquier rol)** |
| documentos | GET | `/documentos/descargar-doc/<int:id>` | `descargar_documento_sgsi` | login |
| **diagnostico** | GET | `/diagnostico/iniciar` | `iniciar_diagnostico` (auto-seed del cuestionario) | admin, auditor |
| diagnostico | GET | `/diagnostico/ejecutar/<int:id>` | `ejecutar_diagnostico` | login + propiedad o admin |
| diagnostico | POST | `/diagnostico/api/guardar` | `api_guardar_diagnostico` (JSON) | login |
| **admin** | **GET** | `/admin/reset-db` | `reset_db` (**borra** resultados, evaluaciones y controles) | admin |
| **info** | GET | `/metodologia-riesgos` | `metodologia_riesgos` | login |
| info | GET | `/clausulas-iso` | `clausulas_iso` | login |

---

## 7. LÓGICA DE NEGOCIO CLAVE

### 7.1 Flujo completo de una auditoría

```
1. GET /evaluacion/nueva
   → Lista los 93 controles, ordenados numéricamente por código
     (key = [int(n) for n in codigo.replace('A.','').split('.') if n.isdigit()])
   → El auditor marca los controles a auditar, escribe título y nombre del auditor

2. POST /evaluacion/preparar
   → Genera código único:  base = "AUD-{primerCodigo}-{ultimoCodigo}"
                           (o "AUD-{codigo}" si es un solo control,
                            o "AUD-{YYYYMM}" si no hay controles)
                           + sufijo -1, -2, ... hasta que no colisione
   → Crea Evaluacion(estado='En Proceso', user_id=current_user.id)
   → Crea un ResultadoControl por cada control seleccionado (nivel_cumplimiento=0.0)
   → Renderiza ejecutar_auditoria.html

3. Ejecución (SPA-like dentro de ejecutar_auditoria.html)
   Por cada tarjeta de control el auditor abre un modal ("evaluador"):
   → GET  /api/control/<resultado_id>/obtener_preguntas   (carga criterios previos)
   → El auditor añade N filas: texto del criterio, probabilidad (1-5),
     impacto (1-5), hallazgo, archivo de evidencia
   → El JS calcula el nivel de riesgo en tiempo real (obtenerMatrizRiesgo)
   → POST /api/control/<resultado_id>/guardar_preguntas
        · Borra TODAS las PreguntaControl previas de ese resultado (delete + recreate)
        · Sube cada archivo a MinIO con clave:
          "{codigoAuditoria}_{codigoControl}_P{index}_{nombreSeguro}"
        · Calcula riesgo = probabilidad * impacto por fila
        · resultado.nivel_cumplimiento = MAX(riesgo de todas las filas)   ← ver §7.4
        · Llama a actualizar_promedio_auditoria()

4. POST /auditoria/finalizar
   → REGLA DE BLOQUEO (_check_critical_risk):
     Si existe alguna PreguntaControl con probabilidad*impacto >= 9
     en un ResultadoControl cuyo riesgo_tratado == False
     → NO se permite finalizar. Estado vuelve a 'En Proceso'.
     → flash de error indicando el control bloqueante y su nivel.
   → Si pasa: estado='Finalizada', fecha_fin=utcnow,
              score_promedio = _calculate_audit_score(evaluacion)
   → Redirige a /dashboard

5. Tratamiento del bloqueo
   → GET/POST /tratamiento/resultado/<resultado_id>
   → Se crea/actualiza un PlanTratamiento con codigo_riesgo "R-{control}-{NNN}"
   → Si plan.estado == 'Cerrado' → resultado.riesgo_tratado = True
   → Ahora la auditoría se puede finalizar

6. GET /auditoria/reporte/<id>  → PDF (xhtml2pdf sobre reporte_pdf.html)
```

### 7.2 Matriz de riesgo 5×5 (ISO 27005)

Definida de forma **redundante en dos lugares**: en JS (`ejecutar_auditoria.html::obtenerMatrizRiesgo`) y como tabla estática en `metodologia_riesgos.html`.

**Escala de probabilidad:**

| Nivel | Descriptor | Frecuencia |
|-------|-----------|------------|
| 1 | Raro | No presentado en los últimos 3 años |
| 2 | Improbable | Al menos una vez en los últimos 3 años |
| 3 | Posible | Al menos una vez en los últimos 2 años |
| 4 | Probable | Al menos una vez en el último año |
| 5 | Casi Seguro | Más de una vez al año |

**Escala de impacto:**

| Nivel | Descriptor | Efecto |
|-------|-----------|--------|
| 1 | Insignificante | Consecuencias mínimas |
| 2 | Menor | Bajo impacto |
| 3 | Dañino | Medianas consecuencias |
| 4 | Severo | Altas consecuencias |
| 5 | Crítico | Consecuencias desastrosas |

**Matriz de zonas** (eje Y = probabilidad, eje X = impacto; el número es el producto):

| P \ I | 1 Insignif. | 2 Menor | 3 Dañino | 4 Severo | 5 Crítico |
|-------|-------------|---------|----------|----------|-----------|
| **5 Casi Seguro** | M (5) | M (10) | A (15) | E (20) | E (25) |
| **4 Probable** | M (4) | M (8) | A (12) | A (16) | E (20) |
| **3 Posible** | M (3) | M (6) | A (9) | A (12) | A (15) |
| **2 Improbable** | B (2) | M (4) | M (6) | M (8) | M (10) |
| **1 Raro** | B (1) | B (2) | M (3) | M (4) | M (5) |

**Acciones por zona:**
- **B — Baja:** asumir el riesgo.
- **M — Moderada:** asumir, evaluar o reducir el riesgo.
- **A — Alta:** reducir, evitar, compartir o transferir.
- **E — Extrema:** reducir, evitar, compartir o transferir — **prioridad inmediata**.

**Umbrales usados en el código:**
- Backend (`_check_critical_risk`, `analisis_riesgos`): `probabilidad * impacto >= 9` ⇒ riesgo alto/extremo, **bloquea el cierre de la auditoría**.
- JS de tarjetas (`actualizarTarjetaGrid`): `>= 20` EXTREMO, `>= 9` ALTO, `>= 4` MODERADO, resto BAJO.
- JS del modal (`obtenerMatrizRiesgo`): reglas por combinación exacta de (p, i), no por producto — **ligera divergencia con la tabla de la metodología** (véase §10).

### 7.3 Modelo de madurez GAP (dashboard)

Escala 0–5 con tres bandas:

| Puntaje | Clasificación | Descripción |
|---------|--------------|-------------|
| > 3.26 | **CUMPLE** (verde/índigo) | Cumple con los requisitos ISO 27001 |
| 1.66 – 3.25 | **PARCIAL** (amarillo) | Cumplimiento parcial con hallazgos |
| < 1.65 | **NO CUMPLE** (rojo) | No cumple requisitos. Crítico |

**Agrupación de dominios para el gráfico GAP** (definida en el modal del dashboard):

| Grupo | Dominios incluidos |
|-------|--------------------|
| Controles de Gestión | Organizacional (A.5) |
| Controles Técnicos | Físico (C.7) + Tecnológico (D.8) — promediados |
| Controles Operacionales | Personas (B.6) |

**Retrocompatibilidad de escala:** la tabla del dashboard contiene lógica Jinja que, si `score_promedio > 5`, divide entre 20 asumiendo que es una escala antigua 0–100.

### 7.4 ⚠️ Semántica sobrecargada de `nivel_cumplimiento` y `score_promedio`

Este es el punto de arquitectura más delicado del sistema y debe documentarse explícitamente:

**`ResultadoControl.nivel_cumplimiento` tiene dos significados incompatibles según qué flujo lo escriba:**

| Escritor | Valor almacenado | Escala |
|----------|------------------|--------|
| `riesgos.guardar_preguntas_control` (flujo principal) | `MAX(probabilidad × impacto)` de sus preguntas | **1 – 25** (riesgo) |
| `auditoria.actualizar_auditoria` (formulario clásico `cumplimiento_<id>`) | valor del formulario | **0 – 5** (madurez) |
| `seed_auditorias.py` | `make_nivel()` acotado a [0, 5] | **0 – 5** (madurez) |

**`Evaluacion.score_promedio` hereda la ambigüedad:**

| Escritor | Fórmula |
|----------|---------|
| `actualizar_promedio_auditoria()` | media de `nivel_cumplimiento` sobre resultados con preguntas o nivel > 0 → **escala de riesgo** |
| `actualizar_auditoria()` | `suma(nivel_cumplimiento) / total_controles` → **escala de madurez** |
| `finalizar_auditoria()` → `_calculate_audit_score()` | usa `respuesta_bool` / `respuesta_texto` con el mapa `{True: 5, 'Parcialmente': 3, 'No Cumple': 1}` → **escala de madurez 0–5** |

Y luego se lee con dos interpretaciones distintas **en la misma pantalla**:
- `dashboard._calculate_risk_counts()`: `score >= 9` → crítico, `>= 3` → alerta, resto → óptimo (**interpretación de riesgo**).
- `dashboard_metrics.html` (tabla): `< 1.65` NO CUMPLE, `< 3.26` PARCIAL, resto CUMPLE (**interpretación de madurez**, con el ajuste `/20` si `> 5`).

**Implicación para la documentación de arquitectura:** esto es un *design smell* de primer orden. La recomendación natural sería separar en dos campos: `nivel_madurez` (0–5) y `nivel_riesgo_max` (1–25), o normalizar todo a una sola escala con un enum explícito.

### 7.5 Diagnóstico GAP (cláusulas 4–10)

- **Auto-seeding:** la primera vez que se llama a `/diagnostico/iniciar`, si `CategoriaDiagnostico` está vacía, se insertan las **7 categorías** y **22 preguntas** hardcodeadas en `diagnostico.py`:

| Cláusula | Nombre | Preguntas |
|----------|--------|-----------|
| 4 | Contexto de la Organización | 4.1, 4.2, 4.3, 4.4 |
| 5 | Liderazgo | 5.1, 5.2, 5.3 |
| 6 | Planificación | 6.1.2, 6.1.3, 6.2 |
| 7 | Apoyo | 7.1, 7.2, 7.3, 7.5 |
| 8 | Operación | 8.1, 8.2, 8.3 |
| 9 | Evaluación del Desempeño | 9.1, 9.2, 9.3 |
| 10 | Mejora | 10.1, 10.2 |

- Cada llamada a `/diagnostico/iniciar` crea un **nuevo** `Diagnostico` y precrea una `RespuestaDiagnostico` (`valor='no_evaluado'`) por cada pregunta existente.
- **Cálculo del puntaje** (`api_guardar_diagnostico`, ejecutado en cada cambio vía AJAX):
  ```
  total_evaluadas = count(valor in ['cumple','parcial','no_cumple'])   # 'no_aplica' se excluye
  puntos          = count(valor=='cumple') * 1  +  count(valor=='parcial') * 0.5
  puntaje_global  = puntos / total_evaluadas * 100
  ```
  Se calcula igual a nivel de categoría y se devuelve `{success, puntaje_global, cat_id, cat_score}` para actualizar las barras de progreso sin recargar.

### 7.6 SoA (Declaración de Aplicabilidad)

- `GET /documentos` es **idempotente y auto-reparador**: para cada uno de los 4 dominios, si no existe un `SoADocument` lo crea, y luego **sincroniza** los `SoADetalle` faltantes (controles nuevos añadidos al catálogo se incorporan automáticamente con `aplicable=True`).
- El editor por dominio (`/soa/<id>/editar/<dominio>`) presenta radio Sí/No + justificación por control, ordenados numéricamente.
- Exportación a PDF vía `reporte_soa_pdf.html` (código, dominio, fecha de actualización, estado + tabla de controles con aplicabilidad y justificación).

### 7.7 Generador documental (Políticas / Procedimientos)

Pipeline en `documentos.crear_politica`:

```
1. _collect_policy_form_data(tipo_doc)
   → dict con: tipo_documento, titulo, codigo, objetivo, alcance, responsables,
     marco_legal, lineamientos, version, desc_cambio, fecha (dd/mm/aaaa),
     elaboro{nombre,cargo}, reviso{nombre,cargo}, aprobo{nombre,cargo}, autor

2. _process_logo_upload()
   → lee el archivo de logo, lo codifica en base64 y lo convierte en data-URI
     (image/png o image/jpeg) para incrustarlo en el PDF

3. _generate_policy_pdf(data)
   → render_template('plantilla_politica_pdf.html') → pisa.CreatePDF → BytesIO

4. _save_policy_to_db_and_s3()
   → clave S3: "{TIP}_{codigoSeguro}_{YYYYMMDD_HHMM}.pdf"  (TIP = 3 primeras letras del tipo)
   → sube a bucket sadi-documentacion
   → guarda PoliticaSGSI con datos_formulario = json.dumps(datos sin logo)
```

**Estructura del PDF generado** (`plantilla_politica_pdf.html`): cabecera con logo + código/versión/fecha, luego secciones numeradas — 1. Objetivo, 2. Alcance, 3. Responsables, 4. Marco Legal y Normativo, 5. Lineamientos, 6. Control de Versiones (tabla), 7. Aprobación (bloque de firmas Elaboró / Revisó / Aprobó).

La reedición (`/documentos/editar/<id>`) rehidrata el formulario desde `datos_formulario` (JSON), regenera el PDF completo y lo sube con una **nueva clave** en S3 (el PDF antiguo queda huérfano en el bucket — ver §10).

### 7.8 Audit trail (`registrar_actividad`)

```python
registrar_actividad(accion, modulo, detalle='')
```
Se invoca **solo en operaciones de escritura**. Captura `current_user.id`, la acción, el módulo, un detalle truncado a 500 caracteres y `request.remote_addr`. Todo el cuerpo está envuelto en `try/except: pass` con el comentario *"El log nunca debe romper el flujo principal"* — es decir, **fallos de auditoría silenciosos por diseño**.

Acciones registradas: crear/editar/eliminar/toggle usuario, crear/editar/eliminar control, crear/editar/actualizar/finalizar/cerrar/eliminar/restaurar/eliminar-definitivo auditoría, tratar riesgo, editar SOA, crear/eliminar documento, iniciar diagnóstico.

Se visualiza paginado (15 por página) en `/perfil` (propio) y `/usuarios/ver/<id>` (admin).

### 7.9 Papelera (soft delete)

- `Evaluacion.eliminado = True` en lugar de borrado físico.
- Un usuario no-admin **no puede** eliminar una auditoría en estado `Finalizada`.
- `/papelera` (solo admin) permite restaurar (`eliminado=False`) o eliminar definitivamente (`db.session.delete` con cascada a `ResultadoControl` → `PreguntaControl`).
- Todas las consultas de listado y de métricas filtran por `eliminado == False`. **Excepción:** `analisis_riesgos` no filtra (ver §10).

---

## 8. ALMACENAMIENTO DE OBJETOS (MinIO / S3)

`extensions.py` construye un cliente boto3 con:
- `endpoint_url` = `S3_ENDPOINT` (default `http://minio:9000`; en compose se pasa `http://minio:9009`)
- `signature_version='s3v4'`, `connect_timeout=3`, `read_timeout=3`, `retries={'max_attempts': 1}`

**Dos buckets**, creados automáticamente al arrancar (`init_s3_bucket`):

| Bucket | Contenido | Convención de claves |
|--------|-----------|----------------------|
| `sadi-evidencias` | Evidencias de auditoría | `{codigoAuditoria}_{codigoControl}_P{index}_{archivo}` (flujo de riesgos)<br>`ev_{evaluacionId}_ctrl_{controlId}_{archivo}` (flujo clásico) |
| `sadi-documentacion` | PDFs de políticas y procedimientos | `{TIP}_{codigo}_{YYYYMMDD_HHMM}.pdf` |

**Descarga:** `/uploads/<filename>` hace `s3_client.get_object()` y devuelve el stream vía `send_file`. Los archivos **nunca se sirven directamente desde MinIO al navegador**: siempre pasan por Flask (lo que permite aplicar `@login_required`, aunque no hay verificación de que el archivo pertenezca a una auditoría que el usuario pueda ver).

`app/static/uploads/` existe y se crea en el arranque, pero está **vacío** — es un remanente del almacenamiento local previo a la migración a MinIO.

---

## 9. CAPA DE PRESENTACIÓN

### 9.1 Layout base (`base.html`, 360 líneas)

- **Sistema de temas dual** mediante variables CSS en `:root` (oscuro por defecto: `--bg-body: #050505`, acento `#6366f1` índigo) y `body.light-mode` (claro). Toggle en la navbar, persistido en `localStorage`.
- **Sidebar AdminLTE tipo acordeón** con tres grupos, con visibilidad condicionada por rol:

```
GENERAL
  ├── Inicio                    (todos)
  ├── Métricas / KPIs           (todos)
  └── Metodología               (todos)
OPERACIÓN
  ├── Nueva auditoría           (administrador, auditor)
  ├── Historial                 (todos)
  ├── Análisis de Riesgos       (administrador, auditor, consultor)
  ├── Catálogo ISO              (todos)
  ├── Cláusulas ISO             (todos)
  ├── Documentos                (todos)
  └── Diagnóstico ISO           (administrador, auditor)
SISTEMA                         (solo administrador)
  ├── Usuarios
  └── Papelera
Mi Perfil                       (todos)
```

- Footer fijo del sidebar con el botón "Cerrar sesión".
- Bloque de flash messages con categorías Bootstrap (`success`, `danger`, `warning`, `info`, `error`).

### 9.2 Inventario de plantillas (28)

| Plantilla | Líneas | Propósito |
|-----------|--------|-----------|
| `base.html` | 360 | Layout, sidebar, temas |
| `login.html` | 282 | Login (diseño "cyber" a pantalla completa, usa `custom.css`) |
| `index.html` | 344 | Portada: "Pilares de la Seguridad" (modales de Confidencialidad / Integridad / Disponibilidad), CTA a nueva auditoría |
| `dashboard_metrics.html` | 566 | Tablero GAP: 4 KPIs, gráfico de barras (GAP por grupos), gráfico de dona (distribución), gráfico de detalle por control con filtros, tabla paginada de evaluaciones, modal de metodología |
| `controles.html` | 578 | Catálogo: 4 tarjetas de dominio, secciones por dominio, buscador, filtro, alta/edición/borrado, tabla paginada (10/pág.) |
| `nueva_evaluacion.html` | 356 | Selector de controles con checkboxes + contadores por dominio |
| `ejecutar_auditoria.html` | 568 | **Pantalla central de trabajo**: rejilla de tarjetas de control + modal evaluador con filas de criterio (prob./impacto/hallazgo/archivo), cálculo de riesgo en vivo, guardado AJAX |
| `detalle_evaluacion.html` | 406 | Vista de solo lectura de una auditoría finalizada + enlace al PDF |
| `auditorias.html` | 294 | Historial con búsqueda, badge de nivel de riesgo, editar/eliminar |
| `papelera.html` | 177 | Auditorías eliminadas, restaurar / borrado permanente con modal de confirmación |
| `analisis_riesgos.html` | 73 | Consolidado de controles con riesgo ≥ 9 y estado de tratamiento |
| `plan_tratamiento.html` | 154 | Plan de tratamiento genérico (por control) |
| `plan_tratamiento_auditoria.html` | 193 | Plan de tratamiento ligado a un `ResultadoControl` |
| `metodologia_riesgos.html` | 296 | Tablas de probabilidad/impacto + matriz de calor 5×5 + leyenda de acciones |
| `clausulas.html` | 243 | Cláusulas 4–10 con subpuntos, en tarjetas con modal de detalle |
| `ejecutar_diagnostico.html` | 281 | Acordeón por cláusula, botonera Cumple/Parcial/No Cumple/N/A, guardado AJAX, barras de progreso |
| `documentos.html` | 303 | Hub documental: tarjetas SoA por dominio + accesos a biblioteca |
| `soa_dominios.html` | 85 | Selector de dominio dentro de un SoA |
| `soa_editor.html` | 252 | Editor SoA: aplicabilidad (radio) + justificación por control |
| `seleccionar_doc.html` | 48 | Elección Política vs. Procedimiento |
| `crear_politica.html` | 213 | Formulario del generador documental (logo, código, título, objetivo, alcance, responsables, marco legal, lineamientos, versión, firmas) |
| `listar_documentos.html` | 151 | Repositorio: tabla con editar / descargar / eliminar |
| `usuarios.html` | 300 | Gestión de usuarios (alta, rol, activar/desactivar) |
| `ver_usuario.html` | 309 | Ficha de usuario: datos, auditorías, bitácora paginada |
| `perfil.html` | 140 | Perfil propio + bitácora |
| `reporte_pdf.html` | 174 | **Plantilla PDF** del informe de auditoría |
| `reporte_soa_pdf.html` | 94 | **Plantilla PDF** de la Declaración de Aplicabilidad |
| `plantilla_politica_pdf.html` | 194 | **Plantilla PDF** de políticas/procedimientos |
| `403.html` | 9 | Acceso denegado |

### 9.3 Endpoints tipo API consumidos por el frontend

Aunque no hay una API REST formal, tres endpoints devuelven/consumen JSON:

| Endpoint | Método | Entrada | Salida |
|----------|--------|---------|--------|
| `/api/control/<control_id>/obtener_preguntas` | GET | — | `[{id, texto, peso, tipo, respuesta_bool, respuesta_texto, hallazgo, archivo, probabilidad, impacto}]` |
| `/api/control/<control_id>/guardar_preguntas` | POST | `multipart/form-data`: campo `data` (JSON string) + `file_0..file_N` | `{message, riesgo_real}` |
| `/diagnostico/api/guardar` | POST | JSON `{respuesta_id, valor, observacion}` | `{success, puntaje_global, cat_id, cat_score}` |

Nota: `<control_id>` en las dos primeras rutas es en realidad un **`ResultadoControl.id`**, no un `Control.id` — nombre engañoso del parámetro.

---

## 10. DEUDA TÉCNICA, BUGS Y RIESGOS IDENTIFICADOS

> Esta sección es material de primera para los ADRs y el plan de mejora de la documentación de arquitectura. Todos los puntos están verificados contra el código.

### 10.1 Bugs funcionales confirmados

| # | Ubicación | Descripción |
|---|-----------|-------------|
| **B1** | `dashboard.py::_calculate_domain_averages` | Extrae el dominio con `res.control.codigo.split('.')[1]`. Con códigos del tipo `"5.1"` eso devuelve `"1"`, no `"5"`. Como `dom_sums` solo tiene claves 5–8, **ninguna suma se acumula nunca** y `data_dom` siempre devuelve `[0, 0, 0, 0]`. El gráfico "Análisis GAP (Grupos)" del dashboard muestra siempre cero. El índice correcto es `[0]`. |
| **B2** | `auditoria.py::_calculate_audit_score` | Calcula el score a partir de `respuesta_bool` y `respuesta_texto`, campos que **el flujo de riesgos nunca escribe** (siempre `None`). Por tanto, al finalizar una auditoría, `score_promedio` se recalcula a **0.0**, destruyendo el valor que había calculado `actualizar_promedio_auditoria()`. |
| **B3** | `detalle_evaluacion.html:378` | El enlace a la evidencia apunta a `url_for('static', filename='uploads/' + archivo)`, pero los archivos están en **MinIO**, no en `static/uploads/`. Enlace roto. Debería usar `url_for('auditoria.download_file', filename=...)` como sí hace `reporte_pdf.html`. |
| **B4** | `riesgos.py::tratar_riesgo_auditoria` y `tratar_riesgo` | El formulario envía `proceso`, `activos` y `tipo_control`, pero el handler **no los lee ni los persiste**. Los campos `proceso_negocio`, `activos_relacionados` y `tipo_control` de `PlanTratamiento` quedan siempre nulos. |
| **B5** | `riesgos.py::analisis_riesgos` | No filtra por `Evaluacion.eliminado == False` ni por propietario: muestra riesgos de auditorías que están en la papelera y de auditorías de otros usuarios. |
| **B6** | `riesgos.py::analisis_riesgos` | Enlaza a `tratar_riesgo(control_id)` (plan genérico por control) en vez de a `tratar_riesgo_auditoria(resultado_id)`, por lo que el plan creado desde esa pantalla **no marca `riesgo_tratado`** y no desbloquea el cierre de la auditoría. |
| **B7** | `ejecutar_auditoria.html::obtenerMatrizRiesgo` | La lógica JS por combinación exacta de (p, i) no coincide del todo con la tabla de `metodologia_riesgos.html`. Ejemplo: p=5, i=4 → el JS devuelve EXTREMO; p=4, i=4 → el JS devuelve ALTO y la tabla también A(16) ✓; pero p=1,i=3 el JS entra en la rama moderada ✓. La divergencia real está en la duplicación misma: **dos fuentes de verdad para la misma matriz**. |
| **B8** | `riesgos.py::guardar_preguntas_control` | Estrategia *delete-all + recreate* de las `PreguntaControl`. Si la subida de un archivo a MinIO falla (capturada con `print`), la pregunta se recrea sin evidencia y **el archivo previo se pierde** salvo que el frontend reenvíe `archivo_previo`. |

### 10.2 Seguridad

| # | Severidad | Hallazgo |
|---|-----------|----------|
| **S1** | **CRÍTICA** | **No hay protección CSRF** en ninguna ruta. No se usa Flask-WTF ni `CSRFProtect`. Todas las mutaciones (crear usuario, eliminar auditoría, cambiar contraseñas) son vulnerables a CSRF. |
| **S2** | **CRÍTICA** | **Modo debug activo**: `app.run(debug=True)` + `FLASK_DEBUG=1` + `FLASK_ENV=development` en compose. La consola interactiva de Werkzeug permite **ejecución remota de código** si se filtra el PIN. |
| **S3** | **ALTA** | **Operaciones destructivas por GET**: `/admin/reset-db` (borra resultados, evaluaciones y **todo el catálogo de controles**), `/controles/eliminar/<id>`, y `/auditorias/eliminar/<id>` aceptan GET. Combinado con S1, basta con que un admin cargue una imagen `<img src="/admin/reset-db">`. |
| **S4** | **ALTA** | **Escalada de privilegios funcional**: `/api/control/<id>/guardar_preguntas` solo exige `@login_required`. Un usuario con rol `lector` o `consultor` puede **crear, modificar y borrar hallazgos** de cualquier auditoría, y subir archivos a MinIO. |
| **S5** | **ALTA** | `/documentos/editar/<id>` solo exige `@login_required`: cualquier rol puede **reescribir políticas y procedimientos del SGSI**, mientras que crearlos y borrarlos sí está restringido a admin/auditor. Inconsistencia de autorización. |
| **S6** | **MEDIA** | **IDOR / falta de control de acceso a nivel de objeto**: `/auditoria/<id>` (`ver_evaluacion`), `/auditoria/reporte/<id>`, `/uploads/<filename>` y `/documentos/descargar-doc/<id>` no verifican propiedad. Cualquier usuario autenticado puede ver cualquier auditoría, descargar cualquier informe PDF y cualquier evidencia si conoce/adivina el ID o el nombre del archivo. (`listar_auditorias` sí filtra por propietario, pero solo en el listado.) |
| **S7** | **MEDIA** | **Política de contraseñas muy laxa**: `validar_seguridad_password` solo exige longitud ≥ 8. Sin requisitos de complejidad, sin lista de contraseñas comunes, sin rotación. |
| **S8** | **MEDIA** | **Sin rate limiting ni bloqueo de cuenta** en `/login`. Fuerza bruta libre. Tampoco hay registro de intentos fallidos en la bitácora. |
| **S9** | **MEDIA** | **Sin cabeceras de seguridad**: no hay CSP, HSTS, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`. La app además carga JS y CSS desde tres CDNs externos **sin SRI** (jsdelivr AdminLTE, cdnjs Font Awesome, jsdelivr Chart.js). |
| **S10** | **MEDIA** | **Sin bootstrap del usuario administrador**: `ADMIN_USERNAME` y `ADMIN_PASSWORD` se declaran en `.env.example` y se inyectan en el contenedor `web`, pero **ningún archivo del código los lee**. El usuario `admin_sadi` (referenciado como usuario protegido en `usuarios.py` y requerido por ambos seeds) tiene que crearse manualmente por un mecanismo que no está en el repositorio. |
| **S11** | **BAJA** | `allowed_file()` valida solo por extensión, no por tipo MIME real ni por contenido. Se aceptan `.doc`, `.docx`, `.xls`, `.xlsx` (vectores potenciales de macro). El `ContentType` se toma de `archivo.content_type` (controlado por el cliente). |
| **S12** | **BAJA** | El logo de la empresa se procesa con `base64.b64encode(file.read())` **sin validar tamaño ni tipo** antes de incrustarlo en el PDF y en la BD (solo limita el `MAX_CONTENT_LENGTH` global de 16 MB). |
| **S13** | **BAJA** | La bitácora de actividad falla en silencio (`except: pass`). Un fallo persistente de la BD dejaría al sistema **sin trazas de auditoría sin que nadie se entere** — problemático precisamente en una herramienta de cumplimiento. |
| **S14** | **BAJA** | `SECRET_KEY` se lee de env sin validación: si falta, `app.config['SECRET_KEY'] = None` y las sesiones fallan de forma poco clara. No hay *fail-fast* de configuración. |

### 10.3 Arquitectura y mantenibilidad

| # | Observación |
|---|-------------|
| **A1** | **Sin capa de servicios ni repositorios.** La lógica de negocio (cálculo de scores, reglas de bloqueo, generación de códigos) vive en las funciones de ruta. Dificulta el testing y la reutilización. |
| **A2** | **Sin tests.** No existe carpeta `tests/`, pese a que `pytest` y `pytest-cov` están en `requirements.txt` y `app/__init__.py` menciona explícitamente los tests como motivo de su hack de módulos. Cobertura actual: **0%**. |
| **A3** | **Sin application factory.** `app` es un global de módulo, lo que impide crear instancias con configuración distinta (test/dev/prod) y obliga a los seeds a hacer `from main import app`. |
| **A4** | **Estrategia de esquema dual**: `db.create_all()` en el arranque **y** Flask-Migrate. No hay carpeta `migrations/` versionada, por lo que en la práctica el esquema se crea con `create_all()` y **no hay ruta de migración para cambios de columnas**. |
| **A5** | **Hack de `sys.modules` en `app/__init__.py`**: acopla el código a la disposición de archivos dentro del contenedor y hace frágiles los imports fuera de Docker. |
| **A6** | **Datos de negocio hardcodeados en el código**: las 22 preguntas del diagnóstico (`diagnostico.py`), las cláusulas ISO con sus subpuntos (`info.py`), las escalas y la matriz de riesgo (`metodologia_riesgos.html` + JS). Cambiar el cuestionario requiere tocar código y desplegar. |
| **A7** | **Duplicación de la lógica de ordenación de códigos**: la expresión `[int(n) for n in codigo.replace('A.','').split('.') if n.isdigit()]` aparece **cuatro veces** (auditoria.py ×2, documentos.py ×2). |
| **A8** | **Duplicación del pipeline de generación de PDF**: `crear_politica` usa helpers (`_generate_policy_pdf`, `_save_policy_to_db_and_s3`), pero `editar_politica` **reimplementa todo inline** (~50 líneas duplicadas). |
| **A9** | **Objetos huérfanos en MinIO**: al reeditar una política se sube un PDF con nueva clave y **no se borra el anterior**. Al eliminar una auditoría (incluso definitivamente) **no se borran sus evidencias** del bucket. No hay política de ciclo de vida. |
| **A10** | **Estados de `Evaluacion` sin enum**: el default del modelo es `'Iniciada'`, pero el código solo usa `'En Proceso'` y `'Finalizada'`. Igual ocurre con `estrategia`, `tipo_control`, `estado` de plan, `valor` de respuesta y `role` — todos strings libres. |
| **A11** | **Atributos dinámicos en objetos ORM**: `_prepare_in_progress_evaluation` inyecta `riesgo_calculado_temp` y `plan_tratamiento_temp` con `setattr` sobre instancias de SQLAlchemy para pasarlos a la plantilla. Funciona, pero es frágil y opaco. |
| **A12** | **N+1 queries**: `_calculate_domain_averages` carga todos los `ResultadoControl` y luego accede a `res.control` uno por uno. `_prepare_in_progress_evaluation` hace una consulta de `PlanTratamiento` por cada resultado. `analisis_riesgos` hace una consulta por control. (Nota: `_get_all_controls_details` **sí** está bien optimizada con una subconsulta agregada.) |
| **A13** | **Sin paginación en varias vistas**: `/papelera`, `/usuarios`, `/documentos/repositorio` y `/analisis-riesgos` cargan todos los registros sin límite. |
| **A14** | **Plantillas muy grandes con CSS y JS embebidos**: `controles.html` (578), `ejecutar_auditoria.html` (568), `dashboard_metrics.html` (566). Cada una lleva su propio bloque `<style>` de 100–200 líneas. Superan el umbral de 400 líneas recomendable para plantillas. |
| **A15** | **Sin i18n**: todo el texto está en español, embebido en plantillas y código. |
| **A16** | **Sin logging estructurado**: se usa `print()` para errores (MinIO, PDF, JSON, conexión a BD). No hay módulo `logging`, ni niveles, ni correlación de peticiones. |
| **A17** | **Volumen `./app:/app` en compose** sobrescribe el código de la imagen. Es correcto para desarrollo, pero el mismo `docker-compose.yml` no distingue entornos: no hay `docker-compose.prod.yml` ni perfiles. |
| **A18** | **Servidor de desarrollo en producción**: no hay Gunicorn/uWSGI ni reverse proxy (nginx/Traefik), ni TLS. El bind a `127.0.0.1` mitiga parcialmente pero limita el despliegue real. |
| **A19** | **Sin CI/CD**: no hay `.github/workflows/`, ni linters (`ruff`/`flake8`/`black`), ni escaneo de seguridad (bandit, safety, trivy). |
| **A20** | **Sin healthcheck de aplicación diferenciado**: el healthcheck golpea `/`, que exige login → devuelve 302, y `curl -f` trata 3xx como éxito. Funciona por accidente, pero no verifica realmente la salud de la BD ni de MinIO. |

---

## 11. DATOS SEMILLA (SEEDS)

Ambos scripts se ejecutan manualmente dentro del contenedor (`python seed_controles.py`).

### `seed_controles.py`
- Corrige el rol de `admin_sadi` a `administrador` si hace falta.
- Inserta los **93 controles del Anexo A de ISO 27001:2022** con código, nombre, descripción normativa completa en español y dominio. Idempotente: solo inserta los códigos que no existan.
- Imprime resumen por dominio.

### `seed_auditorias.py`
- `random.seed(42)` → determinista.
- Genera **20 auditorías de demostración** (16 `Finalizada`, 4 `En Proceso`) con 5 auditores ficticios (Carlos Mendoza, Laura Pérez, Andrés Torres, María González, Roberto Silva), repartidas en el tiempo (de 340 a 1 días atrás).
- Para auditorías de dominio concreto usa todos los controles de ese dominio; para las "integrales" toma una muestra aleatoria de 15–25 controles.
- Genera `nivel_cumplimiento` con `score_base ± 1.0` acotado a [0, 5] y texto de evidencia según la banda de cumplimiento.
- **Requiere que el usuario `admin_sadi` exista previamente** (falla con `exit(1)` si no).

---

## 12. VARIABLES DE ENTORNO

| Variable | Consumida por | Uso |
|----------|---------------|-----|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | compose (servicio `db`) | Credenciales de PostgreSQL; también componen `DATABASE_URL` |
| `DATABASE_URL` | `main.py` | URI de SQLAlchemy (`postgresql://user:pass@db:5432/dbname`) |
| `SECRET_KEY` | `main.py` | Firma de la cookie de sesión |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | compose (inyectadas en `web`) | **Declaradas pero nunca leídas por el código** (ver S10) |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | compose | Credenciales de MinIO; se mapean a `S3_ACCESS_KEY` / `S3_SECRET_KEY` |
| `S3_ENDPOINT` | `extensions.py` | Default `http://minio:9000`; compose pasa `http://minio:9009` |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | `extensions.py` | Defaults inseguros `minioadmin`/`minioadmin` si faltan |
| `S3_BUCKET` | `extensions.py` | Default `sadi-evidencias` |
| `S3_BUCKET_DOCS` | `extensions.py` | Default `sadi-documentacion` |
| `FLASK_APP` / `FLASK_ENV` / `FLASK_DEBUG` | compose | `main.py` / `development` / `1` |

---

## 13. PUESTA EN MARCHA (flujo actual)

```bash
# 1. Configurar variables
cp .env.example .env      # y editar los valores

# 2. Levantar la plataforma
docker compose up -d --build

# 3. Crear el usuario administrador  ← paso NO cubierto por el repositorio
#    (los seeds requieren que exista 'admin_sadi' con rol 'administrador')

# 4. Cargar el catálogo de controles
docker compose exec web python seed_controles.py

# 5. (Opcional) Cargar auditorías de demostración
docker compose exec web python seed_auditorias.py

# 6. Acceder
#    App:            http://localhost:5000
#    Consola MinIO:  http://localhost:9001
```

---

## 14. MATRIZ DE ROLES Y PERMISOS (consolidada)

| Funcionalidad | administrador | auditor | consultor | lector |
|---------------|:-------------:|:-------:|:---------:|:------:|
| Ver inicio / métricas / metodología / cláusulas | ✅ | ✅ | ✅ | ✅ |
| Ver catálogo de controles | ✅ | ✅ | ✅ | ✅ |
| Crear / editar control | ✅ | ✅ | ❌ | ❌ |
| Eliminar control | ✅ | ❌ | ❌ | ❌ |
| Crear auditoría | ✅ | ✅ | ❌ | ❌ |
| Ver historial de auditorías | todas | propias | propias | propias |
| Ver detalle de auditoría (por ID directo) | ✅ | ✅ | ✅ | ✅ ⚠️ *(sin control de propiedad — ver S6)* |
| Guardar hallazgos / subir evidencias (API) | ✅ | ✅ | ✅ ⚠️ | ✅ ⚠️ *(ver S4)* |
| Actualizar / finalizar auditoría | ✅ | ✅ | ❌ | ❌ |
| Eliminar auditoría (papelera) | ✅ | propias | propias | propias |
| Eliminar auditoría finalizada | ✅ | ❌ | ❌ | ❌ |
| Papelera / restaurar / borrado definitivo | ✅ | ❌ | ❌ | ❌ |
| Análisis de riesgos (menú) | ✅ | ✅ | ✅ | ❌ *(oculto en sidebar; la ruta admite cualquier login)* |
| Plan de tratamiento (desde auditoría) | ✅ | ✅ | ❌ | ❌ |
| Plan de tratamiento (genérico por control) | ✅ | ✅ | ✅ ⚠️ | ✅ ⚠️ |
| Ver documentos / SoA | ✅ | ✅ | ✅ | ✅ |
| Editar SoA | ✅ | ✅ | ❌ | ❌ |
| Crear política / procedimiento | ✅ | ✅ | ❌ | ❌ |
| Editar política | ✅ | ✅ | ✅ ⚠️ | ✅ ⚠️ *(ver S5)* |
| Eliminar documento | ✅ | ❌ | ❌ | ❌ |
| Iniciar diagnóstico GAP | ✅ | ✅ | ❌ | ❌ |
| Responder diagnóstico | ✅ | ✅ | ✅ ⚠️ | ✅ ⚠️ |
| Gestión de usuarios | ✅ | ❌ | ❌ | ❌ |
| Ver perfil propio y bitácora | ✅ | ✅ | ✅ | ✅ |
| Reset de BD | ✅ | ❌ | ❌ | ❌ |

⚠️ = permiso concedido de facto por el uso de `@login_required` en lugar de `@role_required`, probablemente no intencional.

---

## 15. NOTAS PARA LA GENERACIÓN DE DOCUMENTACIÓN DE ARQUITECTURA

Elementos que conviene cubrir a partir de este contexto:

1. **Diagramas C4**: Contexto (usuarios por rol ↔ SADI ↔ PostgreSQL/MinIO), Contenedores (web/db/minio + red), Componentes (los 10 blueprints y sus dependencias con `models`/`utils`/`extensions`).
2. **Modelo entidad-relación** completo a partir de §5.
3. **Diagramas de secuencia** para: (a) ciclo completo de auditoría con la regla de bloqueo, (b) guardado AJAX de hallazgos con subida a MinIO, (c) generación y persistencia de una política en PDF.
4. **Diagrama de estados** de `Evaluacion` (Iniciada → En Proceso → Finalizada, con la transición bloqueada por riesgo ≥ 9 y el ramal a `eliminado`) y de `PlanTratamiento` (Abierto → En Progreso → Cerrado).
5. **ADRs recomendados**: monolito Flask vs. servicios; SSR con Jinja2 vs. SPA; MinIO como almacén de objetos vs. filesystem; soft delete; ausencia de capa de servicios; `create_all()` vs. Alembic; matriz de riesgo duplicada en frontend y documentación.
6. **Plan de remediación priorizado** usando §10 (severidad crítica → alta → media → baja), con estimación de esfuerzo.
7. **Trazabilidad ISO 27001**: el propio sistema debería cumplir los controles que audita — especialmente A.5.15 (control de acceso), A.8.2 (privilegios), A.8.5 (autenticación segura), A.8.15 (logging), A.8.24 (criptografía), A.8.28 (codificación segura). Es un ángulo interesante para el documento.
8. **Roadmap de evolución**: capa de servicios, tests (0% → 80%), CI/CD, separación de escalas madurez/riesgo, catálogo de preguntas parametrizable en BD, API REST formal, multi-tenant / multi-organización.
