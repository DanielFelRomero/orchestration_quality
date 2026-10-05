# Arquitectura de la práctica

## Objetivo

La práctica utiliza una arquitectura local simplificada para representar un pipeline de datos que incorpora perfilado, validación de calidad y orquestación.

## Flujo

    RAW
      |
      v
    STAGING
      |
      +--------------------+
      |                    |
      v                    v
    PROFILING          VALIDATION
                           |
                    +------+------+
                    |             |
                  PASS          FAIL
                    |             |
                    v             v
                   GOLD       QUARANTINE

Airflow es responsable de coordinar las tareas y sus dependencias.

## Responsabilidad de cada componente

### RAW

Representa el lote recibido desde una fuente externa.

### STAGING

Representa una capa intermedia en la que se prepara el lote antes de su auditoría.

### PROFILING

Permite observar estructura, tipos, valores faltantes, cardinalidad, distribuciones y posibles anomalías. Los hallazgos de esta etapa sirven como insumo para seleccionar reglas de calidad.

### VALIDATION

Ejecuta el contrato de datos mediante Great Expectations. El resultado de esta etapa debe determinar si el lote puede publicarse.

### GOLD

Representa la salida aprobada para consumo analítico.

### QUARANTINE

Conserva el lote rechazado para su inspección.

## Principio de diseño

La validación de calidad no reemplaza la transformación y la transformación no reemplaza la validación. El flujo debe conservar una separación clara entre preparación, observación, auditoría y publicación.
