# Práctica: Orquestación y calidad de datos

## Propósito

En esta práctica se construirá un pipeline de datos reproducible que integre tres capacidades trabajadas durante el curso: perfilado de datos, validación de calidad de datos y orquestación.

El ejercicio utiliza Apache Airflow como orquestador, ydata-profiling para el perfilado y Great Expectations para la validación. El pipeline procesará lotes de datos de un catálogo de contenidos y deberá impedir que un lote que incumpla el contrato de datos llegue a la capa de consumo.

La práctica parte de una arquitectura base ya configurada. El objetivo no es instalar y configurar toda la plataforma desde cero, sino completar las partes necesarias del pipeline, tomar decisiones sobre las reglas de calidad y comprobar el comportamiento ante datos válidos y datos defectuosos.

## Resultado esperado

Al finalizar la práctica se deberá contar con un pipeline que permita:

1. Recibir un lote de datos en la capa RAW.
2. Preparar el lote en una capa STAGING.
3. Generar un perfil del lote.
4. Definir y ejecutar reglas de calidad mediante Great Expectations.
5. Impedir la publicación cuando la validación falle.
6. Publicar los datos validados en GOLD.
7. Enviar a cuarentena los lotes que no cumplan el contrato.
8. Observar la ejecución completa desde la interfaz de Airflow.

## Arquitectura

El flujo general del ejercicio es:

RAW → STAGING → PROFILING → VALIDATION → GOLD / QUARANTINE

Airflow coordina las tareas del flujo. El perfilado permite conocer las características del lote y descubrir posibles problemas. Great Expectations convierte las reglas seleccionadas en controles automatizables. La publicación en GOLD debe quedar condicionada al resultado de la validación.

## Organización del repositorio

- `.devcontainer/`: configuración del entorno de GitHub Codespaces.
- `data/raw/`: lotes recibidos desde la fuente.
- `data/staging/`: datos preparados para auditoría.
- `data/profiling/`: reportes generados durante el perfilado.
- `data/quarantine/`: lotes que no superan la validación.
- `data/gold/`: datos aprobados para consumo.
- `dags/`: definición del workflow de Airflow.
- `profiling/`: funciones relacionadas con el perfilado.
- `gx/`: configuración y artefactos de Great Expectations.
- `scripts/`: utilidades del ejercicio.

## Regla de trabajo

La práctica se plantea como un ejercicio de construcción. Las instrucciones indican qué comportamiento debe alcanzarse, pero no proporcionan la implementación final. Se espera consultar la documentación oficial de las herramientas, inspeccionar los archivos existentes y probar cada cambio en el entorno.

No se proporciona una solución de referencia dentro de la rama de trabajo.

## Etapas

### 1. Preparar el entorno

Abrir el repositorio mediante GitHub Codespaces.

Comprobar que el entorno haya instalado las dependencias y que Airflow pueda ejecutarse.

Iniciar Airflow según las instrucciones indicadas en esta guía.

### 2. Generar los lotes

Ejecutar:

```bash
python scripts/preparar_lotes.py
```

Comprobar que se hayan creado los archivos dentro de `data/raw/`.

Identificar cuál corresponde al escenario válido y cuál contiene anomalías introducidas deliberadamente.

### 3. Inspección inicial

Antes de ejecutar herramientas de perfilado, realizar una inspección básica del lote mediante Python y Pandas.

Responder:

- ¿Cuántas filas y columnas contiene?
- ¿Qué tipos de datos presenta cada columna?
- ¿Qué columnas contienen valores nulos?
- ¿Existen duplicados?
- ¿Qué valores o rangos parecen sospechosos?
- ¿Qué reglas de negocio podrían derivarse de la estructura observada?

Registrar estas observaciones antes de continuar.

### 4. Data profiling

Completar la funcionalidad de perfilado para generar un reporte del lote procesado.

El reporte deberá permitir revisar, como mínimo:

- estructura del conjunto;
- tipos de datos;
- valores faltantes;
- cardinalidad;
- distribuciones;
- valores mínimos y máximos cuando correspondan;
- advertencias relevantes.

Guardar el resultado en `data/profiling/`.

A partir del perfil generado, seleccionar las características que deberían convertirse en reglas de calidad.

### 5. Contrato de datos

Definir un contrato de datos para el dataset.

Como mínimo, el contrato deberá contemplar reglas relacionadas con:

- presencia de columnas requeridas;
- valores nulos;
- unicidad de una clave;
- valores permitidos para variables categóricas;
- rango lógico para una variable numérica.

Las reglas deberán estar justificadas a partir de la estructura observada en la etapa de profiling.

### 6. Great Expectations

Configurar Great Expectations para representar el contrato de datos.

Se deberá:

1. configurar la fuente de datos;
2. definir la Expectation Suite;
3. crear las Expectations seleccionadas;
4. configurar el mecanismo de validación;
5. crear un Checkpoint para ejecutar la auditoría.

El nombre del Checkpoint utilizado por el DAG deberá coincidir con el nombre definido para la práctica.

### 7. Integración con Airflow

Completar el DAG proporcionado para representar el flujo del proceso.

El DAG deberá incluir tareas con responsabilidades claramente separadas:

- preparación del lote;
- generación del perfil;
- validación de calidad;
- publicación;
- cuarentena.

Las dependencias deberán reflejar el orden lógico del proceso.

La publicación no debe ejecutarse cuando el lote no cumpla las reglas de calidad.

La cuarentena debe conservar el lote rechazado para su posterior inspección.

### 8. Prueba con datos válidos

Procesar el lote diseñado para cumplir las reglas.

Verificar desde la interfaz de Airflow:

- que las tareas se ejecuten en el orden esperado;
- que la validación finalice correctamente;
- que el lote sea publicado en `data/gold/`;
- que no se genere una salida de cuarentena para este caso.

Registrar evidencia de la ejecución.

### 9. Prueba con datos defectuosos

Procesar el lote con anomalías.

Verificar:

- qué Expectations fallan;
- cómo queda la ejecución en Airflow;
- que el lote no llegue a `data/gold/`;
- que el lote rechazado quede disponible en `data/quarantine/`;
- que el reporte de validación permita identificar los problemas encontrados.

Registrar evidencia de la ejecución y explicar la causa de cada fallo observado.

### 10. Resiliencia

Revisar las tareas del DAG y determinar cuáles deberían utilizar reintentos en un escenario real.

Documentar al menos:

- una tarea para la cual un retry tenga sentido;
- una tarea para la cual un retry no resuelva el problema;
- la razón técnica en cada caso.

### 11. Reflexión

Responder:

1. ¿Qué información aportó el profiling que no proporcionó una validación previamente definida?
2. ¿Cómo se transformaron los hallazgos del profiling en reglas de calidad?
3. ¿Qué diferencia existe entre que una tarea de validación termine correctamente y que el lote sea considerado válido?
4. ¿Por qué la publicación debe depender del resultado de la auditoría?
5. ¿Qué ventajas aporta que Airflow conserve el historial de ejecución del pipeline?
6. ¿Qué problemas adicionales deberían considerarse antes de llevar este diseño a un entorno productivo?

## Criterios de finalización

La práctica se considera completada cuando:

- el entorno de Codespaces funciona;
- Airflow detecta el DAG;
- el lote válido puede recorrer el flujo completo;
- el lote defectuoso es rechazado;
- existe un reporte de profiling;
- existe una Expectation Suite funcional;
- existe un Checkpoint ejecutable;
- GOLD contiene solamente datos aprobados;
- los datos rechazados se conservan en cuarentena;
- las evidencias y respuestas solicitadas quedan documentadas.

## Trabajo experimental

Durante la práctica se recomienda introducir deliberadamente una modificación que provoque un fallo adicional en la validación y observar cómo cambia la ejecución del DAG.

La modificación deberá ser documentada indicando:

- cambio realizado;
- regla afectada;
- comportamiento observado;
- diagnóstico;
- corrección aplicada.

## Referencias

- Documentación oficial de Apache Airflow.
- Documentación oficial de Great Expectations.
- Documentación oficial de ydata-profiling.
- Documentación oficial de Pandas.
