# Caso de demostración de SADI — resultados

> **DATOS SINTÉTICOS.** Todo lo que se describe en este documento es un caso de
> demostración construido para ejercitar SADI de extremo a extremo. Ninguna
> cifra, hallazgo, evidencia o documento corresponde a una organización real, ni
> a una auditoría realmente practicada.

Organización ficticia: **Organización Demo S.A.S. (caso de demostración)**.
Fecha base del caso: **2 de marzo de 2026**. Carga ejecutada el **22 de
septiembre de 2026**.

---

## 1. Qué quedó cargado

Todo se escribió por las rutas reales de la aplicación (`seed_demo_sgsi.py`),
autenticado con el rol que corresponde a cada paso. No se insertó nada
directamente en la base: por eso las reglas de negocio se aplicaron de verdad y
la bitácora quedó poblada.

| Módulo | Contenido |
|---|---|
| Usuarios | 5, cubriendo los cuatro roles |
| Diagnóstico GAP | 2 diagnósticos, 22 requisitos cada uno |
| Auditorías | 5 (una en la papelera), 93 + 34 + 37 + 8 + 7 controles |
| Hallazgos | 205 criterios evaluados con probabilidad e impacto |
| Evidencias | 7 archivos adjuntos (5 PDF, 2 imágenes) y 5 evidencias en texto |
| Planes de tratamiento | 26 |
| Declaración de Aplicabilidad | 93 controles justificados, 3 exclusiones |
| Documentación del SGSI | 2 políticas y 1 procedimiento, uno de ellos reeditado |

### Usuarios y contraseñas

Las contraseñas se generan con `secrets` en cada carga (16 caracteres, con
mayúscula, minúscula, dígito y símbolo) y se escriben solo en
`data/demo/credenciales.csv`, que está excluido del repositorio. No se
publican aquí: cada `--reset` genera otras.

| Usuario | Contraseña | Rol | Persona (ficticia) | Cargo |
|---|---|---|---|---|
| `lvargas` | *(en `credenciales.csv`)* | administrador | Liliana Vargas | Oficial de Seguridad de la Información (CISO) |
| `jcastano` | *(en `credenciales.csv`)* | auditor | Julián Castaño | Auditor Interno Líder |
| `pmurillo` | *(en `credenciales.csv`)* | auditor | Paola Murillo | Auditora Interna |
| `dsalcedo` | *(en `credenciales.csv`)* | consultor | Daniel Salcedo | Consultor del SGSI |
| `mrivas` | *(en `credenciales.csv`)* | lector | Mónica Rivas | Coordinación de Calidad |

Son credenciales de un entorno de demostración local. Si la instancia se expone
fuera del equipo de desarrollo, hay que rotarlas.

---

## 2. Qué cifra muestra cada módulo

### Diagnóstico GAP (cláusulas 4 a 10)

| Cláusula | D1 — 09/03/2026 | D2 — 14/09/2026 |
|---|---|---|
| 4. Contexto de la organización | 100,0 % | 100,0 % |
| 5. Liderazgo | 66,7 % | 100,0 % |
| 6. Planificación | 33,3 % | 66,7 % |
| 7. Apoyo | 37,5 % | 62,5 % |
| 8. Operación | 83,3 % | 100,0 % |
| 9. Evaluación del desempeño | 100,0 % | 100,0 % |
| 10. Mejora | 0,0 % | 75,0 % |
| **Global** | **65,0 %** | **86,4 %** |

El 0,0 % de la cláusula 10 en el primer diagnóstico es una medición real del
caso, no un gráfico vacío: los cuatro requisitos de mejora están en «no cumple».
El puntaje global excluye del denominador lo marcado como «no aplica» y «no
evaluado», siguiendo la fórmula `(cumple + 0,5 × parcial) / evaluadas`.

### Auditorías

| Auditoría | Código | Auditor | Fecha | Controles | Madurez (0–5) | Estado |
|---|---|---|---|---|---|---|
| Interna integral del SGSI | `AUD-5.1-8.34` | Julián Castaño | 13/04/2026 | 93 | 3,86 | Finalizada |
| Seguimiento — Tecnológico (A.8) | `AUD-8.1-8.34` | Julián Castaño | 08/06/2026 | 34 | 4,07 | Finalizada |
| Verificación de cierre — Físico (A.7) | `AUD-7.1-7.14` | Paola Murillo | 20/07/2026 | 7 | 4,50 | Finalizada |
| Seguimiento — Organizacional (A.5) | `AUD-5.1-5.37` | Paola Murillo | 17/08/2026 | 37 | 3,83 | En proceso (bloqueada) |
| Seguimiento — Personas (A.6) | `AUD-6.1-6.8` | Paola Murillo | 11/05/2026 | 8 | — | En papelera |

Distribución de riesgo de la auditoría integral: **3 extremos, 13 altos, 33
moderados, 44 bajos**.

### Regla de bloqueo

La auditoría organizacional no se puede cerrar porque conserva cuatro controles
con riesgo alto o extremo sin tratar: **5.14, 5.15, 5.19 y 5.28**. El intento de
cierre lo rechaza la aplicación con este mensaje, que aparece en la captura
`09_regla_de_bloqueo.png`:

> `ALERTA: No se puede finalizar. El control 5.14 tiene Riesgo ALTO/EXTREMO (12). Trate el riesgo primero.`

Las auditorías 1, 2 y 3 sí cerraron, y solo después de que sus planes quedaran
en estado `Cerrado` por el flujo normal. En ningún momento se desactivó la regla.

### Planes de tratamiento

Estados: `Cerrado` 22, `En Progreso` 2, `Abierto` 2.
Estrategias: `Mitigar` 22, `Evitar` 2, `Transferir` 1, `Aceptar` 1.

### Tablero

- Auditorías ejecutadas: 4 (la de la papelera no cuenta).
- Auditorías con riesgo alto sin tratar: 1.
- Alcance del catálogo: 93 controles.
- Madurez por grupo: Gestión 3,81 · Técnicos 4,04 · Operacionales 3,83.
- Auditorías por riesgo residual: 1 crítica, 2 en alerta, 1 óptima.

### Declaración de Aplicabilidad

93 controles justificados; tres declarados no aplicables, los tres del tema
Tecnológico y respaldados por hallazgos de auditoría redactados en el mismo
sentido:

| Control | Motivo |
|---|---|
| 8.4 Acceso al código fuente | La organización no custodia ni mantiene código fuente propio. |
| 8.25 Ciclo de vida de desarrollo seguro | La organización no ejecuta actividades de desarrollo de software. |
| 8.31 Separación de entornos | No mantiene entornos de desarrollo ni de prueba propios. |

### Documentación

`POL-SGSI-001` (Política General de Seguridad de la Información), creada en
v1.0 y reeditada a **v2.0**; `POL-SGSI-002` (Política de Control de Acceso) y
`PR-SGSI-001` (Procedimiento de Gestión de Incidentes), ambos en v1.0.

---

## 3. De dónde sale cada dato

El caso se apoya en el instrumento de autodiagnóstico de 2019
(`4. INSUMO intrumento de AUTODIAGNOSTICO revisada24 (1).xlsx`) para que los
hallazgos tengan la textura de una organización real, y completa el resto donde
el instrumento no llega. Cada hallazgo y cada respuesta del diagnóstico lleva su
procedencia en los CSV, en la columna `origen`:

| | Derivado del instrumento 2019 | Generado para este caso |
|---|---|---|
| Controles con hallazgos | 62 de 93 | 31 de 93 |
| Respuestas del diagnóstico D1 | 20 de 22 | 2 de 22 |
| Respuestas del diagnóstico D2 | 12 de 22 | 10 de 22 |

`EXCEL:12.14` en la columna `origen` significa que el hallazgo se derivó de la
fila 12.14 del instrumento. `GENERADO` significa que no tiene correspondencia
allí y se redactó para este caso.

Lo generado por completo, sin base en el instrumento: la organización y sus
personas, las fechas, el segundo diagnóstico, las cinco auditorías y su
cronología, los 26 planes de tratamiento, la Declaración de Aplicabilidad, los
tres documentos del SGSI y los siete archivos de evidencia. Los archivos de
evidencia llevan impresa la marca `DOCUMENTO SINTÉTICO — caso de demostración de
SADI`.

El conjunto de datos es reproducible: `scripts/generar_datos_demo.py` regenera
los ocho CSV de `data/demo/` y el cargador no conoce ninguna cifra del caso, solo
lee esos archivos.

---

## 4. Correcciones al código

### Defectos B1–B6, corregidos antes de poblar

Cada uno tiene una prueba que falla con el código anterior y pasa con el
corregido; `scripts/verificar_defectos.py` lo comprueba revirtiendo la línea de
cada arreglo y volviendo a ejecutar su prueba.

| | Defecto | Corrección |
|---|---|---|
| B1 | El gráfico GAP por dominios tomaba el segundo segmento del código del control (`5.1` → `1`), de modo que ninguna suma se acumulaba y el gráfico quedaba siempre en cero. | `codigo.split('.')[0]` en `dashboard._calculate_domain_averages`. |
| B2 | Un mismo campo, `score_promedio`, se leía en tres escalas distintas según la pantalla: riesgo 1–25, madurez 0–5 y porcentaje 0–100. | ADR-011: se separan en `nivel_riesgo_max` (1–25) y `nivel_madurez` (0–5), con `app/escalas.py` como única fuente de la conversión. |
| B3 | El enlace de descarga de una evidencia apuntaba a una ruta inexistente. | `auditoria.download_file` en `detalle_evaluacion.html`. |
| B4 | El nivel de riesgo calculado no se persistía al guardar los criterios de un control. | `riesgos.guardar_preguntas_control` escribe ambos campos. |
| B5 | Proceso de negocio, activos relacionados y tipo de control se perdían al guardar un plan. | Ambos manejadores de tratamiento los persisten. |
| B6 | El análisis de riesgos no decía de qué auditoría venía cada control, y su enlace de tratamiento no funcionaba. | `riesgos.analisis_riesgos` agrupa por resultado y expone la auditoría; nueva columna en la tabla. |

### Defectos encontrados al revisar las capturas

Los tres son de la misma familia que B1 y B2: un dato ya convertido que se
vuelve a convertir, o que solo existe en el navegador.

| | Defecto | Corrección |
|---|---|---|
| B7 | `dashboard_metrics.html` dividía entre 20 la madurez por dominio, suponiendo que llegaba como porcentaje 0–100. Las tres barras de «Análisis de Cumplimiento» quedaban en ~0,19 sobre un eje 0–5: visualmente planas. Además la dona rotulaba bandas de madurez cuando lo que grafica es el conteo de auditorías por riesgo. | Se elimina la división y se corrigen los rótulos. |
| B8 | La pantalla del diagnóstico solo calculaba los porcentajes en el navegador, con la respuesta del guardado por AJAX. Al reabrir un diagnóstico terminado, **todas las cláusulas aparecían en 0 %** y el global se imprimía sin redondear (`86.36363636363636 %`). | `diagnostico._puntaje`, usada tanto por la ruta como por el API para que no puedan divergir. |
| B9 | El nombre de un adjunto se recortaba al último fragmento separado por guion bajo, así que `…_EV-05_borrador_politica_seguridad.pdf` se leía como `seguridad.pdf`. | Filtro `nombre_evidencia`, que quita el prefijo interno y deja igual lo que no lo traiga. |

### KPI de estado de auditorías

La dona del tablero clasificaba por `Evaluacion.riesgo_maximo`, que guarda el
riesgo **inherente**: el máximo histórico de los hallazgos. Una auditoría que ya
había cerrado todos sus planes de riesgo alto seguía contando como crítica —
justo lo contrario de lo que afirma la regla de bloqueo al dejarla finalizar— y
el gráfico quedaba con un solo segmento (3 / 0 / 0). Ahora clasifica por el
riesgo **residual**: el mayor probabilidad × impacto que queda entre los
controles sin tratar.

### Otros ajustes

- `app/bootstrap_admin.py`: crea o repara el usuario administrador a partir de
  `ADMIN_USERNAME` y `ADMIN_PASSWORD`, en vez de depender de un usuario sembrado
  con contraseña conocida.
- `ver_usuario.html` leía `score_promedio` como un porcentaje 0–100; ahora lo
  presenta como madurez sobre 5.

### Pruebas

**57 pruebas**, todas en verde:

```
docker compose exec web python -m pytest tests -q
```

| Archivo | Cubre |
|---|---|
| `test_escalas.py` (28) | Conversión riesgo ↔ madurez, zonas y umbral |
| `test_defectos_b1_b6.py` (11) | Un caso por defecto B1–B6 |
| `test_regla_bloqueo.py` (4) | Que la auditoría no cierre con riesgo alto sin tratar, y que el plan cerrado la libere |
| `test_kpi_riesgo_residual.py` (4) | Que el KPI mida riesgo residual |
| `test_diagnostico_puntajes.py` (3) | Porcentajes por cláusula y redondeo del global |
| `test_nombre_evidencia.py` (7) | Nombre de los adjuntos |

Además, `app/verificar_pantallas.py` recorre 22 pantallas con el rol que
corresponde y comprueba que el rol lector reciba 403 donde debe, y el recorrido
de capturas falla por su cuenta si alguna gráfica o algún porcentaje por cláusula
queda en cero.

---

## 5. Capturas

`data/demo/evidencias_articulo/` contiene 22 imágenes y 3 PDF numerados, con su
`INDICE.md`. Las genera `scripts/capturar_evidencias.py`, que recorre la
aplicación con Playwright autenticándose con cada rol; no son montajes.

Para reproducir el conjunto completo desde cero:

```bash
python scripts/generar_datos_demo.py                        # CSV en data/demo/
docker compose exec web python bootstrap_admin.py
docker compose exec web python seed_demo_sgsi.py --reset    # carga por las rutas reales
docker compose exec web python exportar_ids_demo.py
python scripts/capturar_evidencias.py                       # capturas y PDF
```

---

## 6. Advertencia para el artículo

Las cifras de este documento y las pantallas de `evidencias_articulo/` son una
**demostración funcional de SADI**, y **no son resultados de la Corporación
Community Network** ni de ninguna otra organización real. Cualquier captura que
se lleve al artículo debe ir acompañada de un pie que indique que corresponde a
un caso de demostración con datos sintéticos. El resultado de «nivel medio de
madurez» que el artículo reporta para la Corporación Community Network proviene
del instrumento de autodiagnóstico original de 2019, **no de este caso de
demostración**, y las dos cosas no deben presentarse como si fueran la misma
medición.

---

## 7. Observaciones y limitaciones conocidas

Se reportan en vez de corregirse a mano en la base.

1. **La fecha del informe de auditoría es la del cierre real.** El encabezado del
   reporte muestra `fecha_fin`, que es el día en que se ejecutó la carga
   (22/09/2026), mientras que el listado muestra la fecha declarada de la
   auditoría (13/04/2026 para la integral). No hay forma de fijar `fecha_fin`
   desde la interfaz, y forzarla habría exigido cambiar el comportamiento de la
   finalización por un motivo cosmético.
2. **(Corregido el 17/10/2026) El mensaje de bloqueo nombraba el primer control que encontraba, no el peor.**
   `_check_critical_risk` devuelve la primera coincidencia. En la auditoría
   organizacional informa el 5.14 (riesgo 12) aunque el 5.15 tiene riesgo 20.
3. **La madurez promedio puede quedar en banda «CUMPLE» conviviendo con riesgos
   extremos.** La auditoría integral marca 3,86 porque la media la dominan sus
   44 controles en zona Baja, pese a tener 3 riesgos extremos. Es el
   comportamiento esperado de un promedio, pero conviene leer la madurez junto
   al conteo de riesgos, no en su lugar.
4. **La paleta de colores de las zonas de riesgo no es consistente entre
   pantallas.** En la rejilla de ejecución «MODERADO» es amarillo; en el detalle
   de la auditoría finalizada, verde.
5. **`--reset` no borra los objetos de MinIO.** Las evidencias y los PDF de
   cargas anteriores quedan huérfanos en el bucket y se sobrescriben en la
   siguiente carga.
6. **`data/demo/credenciales.csv` y `data/demo/ids_capturas.json` no se
   versionan.** El primero porque contiene contraseñas; el segundo porque sus
   identificadores cambian en cada recarga.
