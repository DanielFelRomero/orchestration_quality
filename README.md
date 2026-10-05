# Práctica: Orquestación y calidad de datos

Esta práctica integra perfilado de datos, validación de calidad y orquestación mediante Apache Airflow, ydata-profiling y Great Expectations.

El repositorio proporciona la infraestructura base para trabajar en GitHub Codespaces y una plantilla parcial del pipeline. La implementación final queda a cargo de quien desarrolla la práctica.

## Inicio

La guía completa de trabajo se encuentra en docs/guia_practica.md.

La arquitectura conceptual se encuentra en docs/arquitectura.md.

Las evidencias requeridas se encuentran en docs/entrega.md.

## Resultado esperado

El pipeline deberá:

1. Preparar un lote en STAGING.
2. Generar un reporte de profiling.
3. Ejecutar un contrato de calidad mediante Great Expectations.
4. Publicar únicamente los lotes aprobados en GOLD.
5. Conservar los lotes rechazados en QUARANTINE.
6. Permitir observar el comportamiento completo desde Airflow.

## Estructura

- .devcontainer/: entorno de GitHub Codespaces.
- data/raw/: lotes de entrada.
- data/staging/: lote preparado para auditoría.
- data/profiling/: reportes de profiling.
- data/gold/: lotes aprobados.
- data/quarantine/: lotes rechazados.
- dags/: DAG de Airflow.
- profiling/: implementación del perfilado.
- gx/: proyecto de Great Expectations.
- scripts/: utilidades de la práctica.
- docs/: guía, arquitectura y evidencias.

## Regla de trabajo

La práctica no contiene una solución de referencia. Se espera que las decisiones de implementación sean tomadas a partir de los requerimientos, la inspección del código existente y la documentación de las herramientas.

No se deberá confundir la existencia de una plantilla funcional con una implementación terminada.
