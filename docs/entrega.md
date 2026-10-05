# Evidencias de la práctica

La entrega deberá contener evidencia suficiente para demostrar que el pipeline fue construido y probado.

La secuencia de trabajo y los productos esperados se encuentran en [docs/guia_practica.md](guia_practica.md).

## Evidencias mínimas

1. Estructura del repositorio y entorno de Codespaces.
2. DAG visible en Airflow.
3. Reporte de profiling.
4. Contrato de datos documentado.
5. Expectation Suite configurada.
6. Checkpoint configurado.
7. Ejecución con el lote válido.
8. Ejecución con el lote defectuoso.
9. Resultado de los datos publicados en GOLD.
10. Resultado de los datos conservados en QUARANTINE.
11. Justificación de las decisiones sobre reintentos.
12. Evidencia del experimento controlado.
13. Respuestas de la reflexión final.

## Criterio de evidencia

Las capturas deberán mostrar el contexto necesario para interpretar el resultado. Una captura aislada de un fragmento de código no constituye evidencia suficiente de que el pipeline completo funcione.

Cuando se muestre la interfaz de Airflow, deberá ser posible identificar el DAG, la ejecución y el estado de las tareas relevantes.

Cuando se presente el resultado de Great Expectations, deberá poder identificarse la suite o el checkpoint utilizado y el resultado de la validación.

## Organización sugerida

La evidencia puede mantenerse dentro de una carpeta local de trabajo o en el documento de entrega.

No se deberán versionar archivos generados de gran tamaño dentro del repositorio salvo que se indique expresamente.

## Consideración sobre la implementación

El repositorio proporciona una plantilla y una infraestructura base, pero no contiene una solución de referencia. Las decisiones de implementación deberán surgir del análisis del problema y de la documentación de las herramientas.
