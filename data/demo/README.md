# Conjunto de datos del caso de demostracion de SADI

> **DATOS SINTETICOS generados para probar el aplicativo SADI. No corresponden a ninguna organizacion real.**

Estos archivos son la entrada de `seed_demo_sgsi.py`. Se pueden revisar y editar
antes de cargarlos, sin volver a ejecutar el generador.

## Que es y que no es

Este conjunto de datos es una **demostracion funcional del aplicativo SADI**: sirve
para ver todos sus modulos operando con datos completos y coherentes entre si.

**No** son los resultados de ninguna organizacion real. En particular, no son los de
la Corporacion Community Network. El nivel medio de madurez que reporta el articulo
proviene del instrumento de autodiagnostico de 2019 aplicado a esa organizacion, y esa
cifra es independiente de la que produzca este caso.

## Como se derivo del instrumento de 2019

El archivo `4. INSUMO intrumento de AUTODIAGNOSTICO revisada24.xlsx` es una prueba del
formulario en Excel, no el levantamiento de una organizacion. Se uso como **base de
realismo**: sus proporciones de respuesta (79 cumple, 8 parcial, 45 no cumple sobre 132
preguntas, es decir 62,9 %) orientan que sale bien y que sale mal en el caso.

- Las **secciones 1 a 11** alimentan el diagnostico GAP de las clausulas 4 a 10.
- La **seccion 12** orienta que controles del Anexo A salen mal en la auditoria.

La columna `origen` de cada archivo dice de donde sale cada decision:

| Valor | Significado |
|---|---|
| `EXCEL:<pregunta>` | Lo decidio una pregunta de la seccion 12 del instrumento |
| `EXCEL:<filas>` | Lo decidieron esas filas del instrumento (diagnostico GAP) |
| `EXCEL-GAP:<req>` | Lo decidio un requisito del diagnostico GAP ya derivado |
| `SEGUIMIENTO` | Reevaluacion de un control en una auditoria posterior |
| `GENERADO` | Decision del caso de demostracion, sin respaldo en el instrumento |

## Organizacion del caso

| | |
|---|---|
| Organizacion | Organización Demo S.A.S. (caso de demostración) |
| Sector | Comercio al por mayor y servicios de distribución |
| Empleados | 48 |
| Fecha base | 2026-03-02 |

## Archivos

| Archivo | Filas | Contenido |
|---|---|---|
| `usuarios.csv` | 5 | Cinco usuarios, uno por rol y un segundo auditor |
| `diagnostico_gap.csv` | 44 | Dos diagnosticos de 22 requisitos cada uno |
| `auditorias.csv` | 5 | Las cuatro auditorias y su distribucion de riesgo |
| `hallazgos.csv` | 205 | Criterio, hallazgo, probabilidad, impacto y nivel |
| `evidencias_texto.csv` | 5 | Evidencia registrada como texto, no como archivo |
| `planes_tratamiento.csv` | 26 | Un plan por hallazgo con riesgo >= 9 |
| `soa.csv` | 93 | Declaracion de Aplicabilidad de los 93 controles |
| `documentos.csv` | 3 | Dos politicas y un procedimiento |

Todos los CSV usan separador `;` y codificacion UTF-8 con BOM, para que Excel los abra
directamente sin pasar por el asistente de importacion.

## Cifras que va a mostrar el aplicativo

### Diagnostico GAP

| | Diagnostico 1 (2026-03-09) | Diagnostico 2 (2026-09-14) |
|---|---|---|
| Puntaje global | **65.0 %** | **86.4 %** |
| Clausula 4. Contexto de la Organización | 100.0 % | 100.0 % |
| Clausula 5. Liderazgo | 66.7 % | 100.0 % |
| Clausula 6. Planificación | 33.3 % | 66.7 % |
| Clausula 7. Apoyo | 37.5 % | 62.5 % |
| Clausula 8. Operación | 83.3 % | 100.0 % |
| Clausula 9. Evaluación del Desempeño | 100.0 % | 100.0 % |
| Clausula 10. Mejora | 0.0 % | 75.0 % |

El primer diagnostico deja un requisito en `no_aplica` (9.3) y otro en `no_evaluado`
(10.1), para mostrar que la formula de SADI excluye ambos del denominador: se calcula
sobre 20 requisitos evaluados, no sobre 22.

### Distribucion de riesgo de la auditoria integral

| Zona | Nivel | Controles |
|---|---|---|
| Extrema | >= 20 | 3 |
| Alta | 9 a 16 | 13 |
| Moderada | 3 a 8 | 33 |
| Baja | 1 a 2 | 44 |
| **Total** | | **93** |

### Auditorias

| Auditoria | Controles | Estado | Proposito |
|---|---|---|---|
| [DEMO] Auditoría interna integral del SGSI - 93 controles del Anexo A | 93 | Finalizada | Primera auditoría interna completa del SGSI. |
| [DEMO] Auditoría de seguimiento - Tema Tecnológico (A.8) | 34 | Finalizada | Seguimiento a los 34 controles tecnológicos dos meses despues de la auditoría integral, para verificar la eficacia de los planes cerrados. |
| [DEMO] Auditoría de seguimiento - Tema Organizacional (A.5) | 37 | En Proceso (bloqueada) | Seguimiento a los 37 controles organizacionales. |
| [DEMO] Auditoría de seguimiento - Tema Personas (A.6) | 8 | En Proceso (papelera) | Auditoría anulada por reprogramación del cronograma. |
| [DEMO] Verificación de cierre - Controles físicos remediados (A.7) | 7 | Finalizada | Verificación acotada a los siete controles físicos cuyos planes de tratamiento se cerraron tras la auditoría integral. |

## Regla de mapeo del diagnostico GAP

El instrumento tiene 132 preguntas y SADI tiene 22 requisitos. Cuando varias preguntas
caen en el mismo requisito se promedia el grupo (cumple = 1, parcial = 0,5, no cumple = 0)
y se clasifica asi:

| Promedio del grupo | Valor en SADI |
|---|---|
| >= 0,75 | `cumple` |
| 0,30 a 0,74 | `parcial` |
| < 0,30 | `no_cumple` |

Las filas 52 a 56 del instrumento corresponden al requisito 6.1.1 de la norma, que SADI
no incluye entre sus 22 preguntas. Se documentan como excluidas en vez de repartirlas,
para no diluir el resultado de 6.1.2.

## Regeneracion

```bash
python scripts/generar_datos_demo.py            # reescribe estos CSV
docker compose exec web python seed_demo_sgsi.py --dry-run
docker compose exec web python seed_demo_sgsi.py
```
