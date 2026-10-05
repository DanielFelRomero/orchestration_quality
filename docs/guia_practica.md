# Guía de práctica: Orquestación y calidad de datos

## 1. Propósito

La práctica integra tres capacidades del proceso de ingeniería de datos:

- Data profiling.
- Data quality validation.
- Orquestación.

Se trabajará con Apache Airflow, ydata-profiling y Great Expectations sobre un entorno preparado en GitHub Codespaces.

El objetivo consiste en construir un pipeline capaz de recibir un lote, prepararlo, inspeccionarlo, validarlo y decidir si puede publicarse o debe enviarse a cuarentena.

Las secciones de "Ayuda de contingencia" son ayudas opcionales y plegables para desbloquear errores durante la práctica.

El ejercicio parte de una infraestructura base y de una plantilla parcial. La implementación de los componentes pendientes deberá ser realizada durante la práctica.

## 2. Escenario

Se dispone de un catálogo de contenidos audiovisuales.

El pipeline deberá procesar un archivo CSV recibido en la capa RAW y producir uno de dos resultados:

- GOLD: lote aprobado para consumo.
- QUARANTINE: lote rechazado por incumplimiento del contrato de datos.

El flujo conceptual es:

~~~text
RAW
  |
  v
STAGING
  |
  v
PROFILING
  |
  v
VALIDATION
  |
  +------------------+
  |                  |
 PASS               FAIL
  |                  |
  v                  v
GOLD            QUARANTINE
~~~

Airflow coordina las tareas. El perfilado permite conocer el estado de los datos. Great Expectations ejecuta las reglas de calidad.

## 3. Antes de comenzar

No se deberá modificar la estructura general del repositorio sin necesidad.

Los archivos que constituyen puntos principales de trabajo son:

- profiling/profile_data.py
- dags/pipeline_practica.py
- configuración de Great Expectations dentro de gx/

Los archivos de scripts/ proporcionan utilidades para preparar los datos, probar el perfilado e iniciar Airflow.

La presencia de NotImplementedError en algunos archivos es intencional.

## 4. Preparar GitHub Codespaces

<details>
<summary>Ayuda de contingencia</summary>

Si la creación del Codespace falla durante `postCreateCommand`, no se deberán cambiar versiones de Airflow, GX o ydata-profiling manualmente. Se deberá reconstruir el contenedor para que se ejecute nuevamente `.devcontainer/setup.sh`.

La configuración crea un entorno virtual en `.venv/` y lo agrega al `PATH`. Después de reconstruir, `which python` debería apuntar a una ruta dentro de `.venv/bin/`.

Si el entorno ya fue creado antes de este ajuste, utilizar **Codespaces/Dev Containers → Rebuild Container** y volver a comprobar las versiones.

</details>

1. Abrir el repositorio mediante GitHub Codespaces.
2. Esperar a que finalice la creación del entorno.
3. Comprobar la versión de Python:

~~~bash
python --version
~~~

4. Comprobar Airflow:

~~~bash
airflow version
~~~

5. Comprobar Great Expectations:

~~~bash
great_expectations --version
~~~

6. Comprobar ydata-profiling:

~~~bash
python -c "import ydata_profiling; print('ydata-profiling disponible')"
~~~

7. Comprobar las dependencias:

~~~bash
python -m pip check
~~~

Ante cualquier error de instalación, deberá revisarse primero la terminal de creación del Codespace antes de modificar las versiones del proyecto.

### Compatibilidad de ydata-profiling

La versión utilizada en esta práctica utiliza componentes que todavía dependen de `pkg_resources`. Por compatibilidad, el entorno fija `setuptools==80.9.0`, evitando `setuptools>=81`.

La instalación de Airflow se realiza por separado con las constraints oficiales de Airflow. Las dependencias adicionales se instalan después, siguiendo el modelo recomendado por Airflow para dependencias propias.

## 5. Iniciar Airflow

<details>
<summary>Ayuda de contingencia</summary>

Si el comando `airflow` no se encuentra, comprobar primero `which airflow`. Debe apuntar a `.venv/bin/airflow`. Si no es así, el contenedor no tomó todavía la configuración actual y debe reconstruirse.

</details>

Desde una terminal:

~~~bash
bash scripts/start_airflow.sh
~~~

La terminal permanecerá ocupada mientras Airflow esté ejecutándose.

En la salida de la terminal aparecerán las credenciales necesarias para entrar en la interfaz.

En la pestaña Ports de Codespaces deberá localizarse el puerto 8080 y abrirse la interfaz de Airflow.

Deberá mantenerse esta terminal abierta durante la práctica.

## 6. Preparar los datos

<details>
<summary>Ayuda de contingencia</summary>

La ejecución esperada es `python scripts/preparar_lotes.py`. Los mensajes de advertencia provenientes de la descarga del dataset no implican por sí mismos un fallo si al final aparecen los dos archivos preparados.

</details>

En una segunda terminal:

~~~bash
python scripts/preparar_lotes.py
~~~

Deberán aparecer dos archivos:

~~~text
data/raw/lote_dia_1_bueno.csv
data/raw/lote_dia_2_malo.csv
~~~

El primer archivo representa un lote diseñado para cumplir el contrato que se definirá.

El segundo contiene anomalías introducidas deliberadamente.

Antes de ejecutar el DAG, uno de los archivos deberá copiarse como lote activo:

~~~bash
cp data/raw/lote_dia_1_bueno.csv data/raw/netflix_titles.csv
~~~

o:

~~~bash
cp data/raw/lote_dia_2_malo.csv data/raw/netflix_titles.csv
~~~

## 7. Inspección inicial

<details>
<summary>Ayuda de contingencia</summary>

Una revisión mínima puede hacerse con `df.shape`, `df.columns`, `df.dtypes`, `df.isna().sum()`, `df.duplicated().sum()`, `df.describe(include="all")` y la inspección de valores únicos de campos categóricos. La tabla de hallazgos debe distinguir observación de regla de calidad.

</details>

Antes de utilizar una herramienta automática de profiling, se deberá realizar una inspección básica con Pandas.

Para el lote seleccionado se deberá registrar:

- número de filas;
- número de columnas;
- nombres de columnas;
- tipos de datos;
- porcentaje o conteo de valores nulos;
- duplicados;
- valores mínimos y máximos cuando corresponda;
- valores categóricos observados;
- posibles anomalías.

No se deberán definir todavía todas las reglas de calidad a partir de intuiciones. Primero se deberá observar qué características presentan realmente los datos.

### Producto de esta etapa

Una tabla de análisis similar a:

| Campo | Hallazgo | Posible problema | Regla que podría derivarse |
|---|---|---|---|
| Campo 1 |  |  |  |
| Campo 2 |  |  |  |
| Campo 3 |  |  |  |

## 8. Implementar el data profiling

<details>
<summary>Ayuda de contingencia</summary>

La implementación mínima consiste en importar `pandas`, `Path` y `ProfileReport`, leer el CSV recibido, crear el reporte y ejecutar `profile.to_file(output_file)`. Para Codespaces pequeños puede utilizarse `minimal=True` para reducir cálculos costosos. No se debe cambiar la firma de `generate_profile(input_path, output_path)`.

</details>

Abrir:

~~~text
profiling/profile_data.py
~~~

La función a completar es:

~~~text
generate_profile(input_path, output_path)
~~~

La función deberá:

1. leer el CSV recibido;
2. construir un perfil mediante ydata-profiling;
3. crear el directorio de salida cuando sea necesario;
4. generar el reporte HTML en la ruta indicada.

La implementación deberá mantenerse dentro de la función proporcionada y utilizar las rutas recibidas como argumentos.

### Primera prueba

Preparar el lote:

~~~bash
cp data/raw/lote_dia_1_bueno.csv data/raw/netflix_titles.csv
~~~

Ejecutar:

~~~bash
python -m scripts.run_profile
~~~

Comprobar que se genere:

~~~text
data/profiling/netflix_profile.html
~~~

Abrir el reporte y comparar sus resultados con las observaciones de la inspección inicial.

### Preguntas

- ¿Qué problemas fueron evidentes desde la inspección manual?
- ¿Qué problemas fueron más fáciles de detectar mediante el perfil?
- ¿Qué información adicional aporta el reporte?
- ¿Qué hallazgos son realmente problemas de calidad y cuáles son solamente características estadísticas?

## 9. Definir el contrato de datos

<details>
<summary>Ayuda de contingencia</summary>

Una solución razonable puede derivar reglas de los campos problemáticos observados en el lote defectuoso: existencia de columnas, ausencia de identificadores nulos, valores categóricos permitidos y un rango lógico para `release_year`. La clave es justificar cada regla con un hallazgo previo.

</details>

A partir de la inspección y del profiling, se deberá definir qué condiciones debe cumplir un lote para poder publicarse.

El contrato deberá contemplar como mínimo:

### Estructura

Deberá comprobarse que las columnas necesarias existan.

### Completitud

Deberán seleccionarse campos que no puedan estar vacíos.

### Unicidad

Deberá identificarse una clave o atributo que deba ser único.

### Validez categórica

Deberá seleccionarse al menos una variable cuyo conjunto de valores permitidos pueda definirse.

### Validez numérica

Deberá seleccionarse al menos una variable sobre la cual pueda establecerse un rango lógico.

El contrato deberá quedar documentado.

### Regla importante

Una regla deberá tener una justificación. No se deberán agregar Expectations únicamente para aumentar el número de validaciones.

## 10. Configurar Great Expectations

<details>
<summary>Ayuda de contingencia</summary>

El camino esperado es: Data Source → Data Asset/Batch → Expectation Suite → Expectations → Checkpoint. El Checkpoint debe llamarse `netflix_checkpoint`, porque ese es el nombre que utiliza el DAG base. La configuración se guarda dentro de `gx/`.

</details>

Great Expectations deberá utilizarse para representar el contrato de datos.

El trabajo deberá contemplar:

1. inicialización de la configuración local;
2. configuración de una fuente de datos adecuada;
3. creación de una Expectation Suite;
4. creación de las Expectations seleccionadas;
5. ejecución de una validación de prueba;
6. creación de un Checkpoint.

El Checkpoint deberá utilizar un nombre estable, debido a que posteriormente será utilizado desde Airflow.

La configuración deberá permitir validar el lote preparado en:

~~~text
data/staging/netflix_staging.csv
~~~

No se proporciona en esta guía una lista cerrada de Expectations. Las reglas deberán derivarse del contrato definido.

Los artefactos de Great Expectations deberán quedar dentro de gx/.

## 11. Completar el DAG

<details>
<summary>Ayuda de contingencia</summary>

La estructura del DAG ya contiene las tareas principales. Sólo deben completarse las operaciones pendientes de publicación y cuarentena y mantenerse las dependencias proporcionadas. `GreatExpectationsOperator` debe ejecutar `netflix_checkpoint` con `fail_task_on_validation_failure=True`.

</details>

Abrir:

~~~text
dags/pipeline_practica.py
~~~

La estructura general del DAG ya está creada.

La validación utiliza GreatExpectationsOperator.

El operador deberá utilizar el Data Context ubicado en gx/ y el Checkpoint creado en la etapa anterior. La configuración deberá hacer que un resultado de validación fallido sea tratado como fallo de la tarea de Airflow. El proveedor utilizado por esta práctica permite ejecutar Checkpoints desde Airflow y controlar este comportamiento mediante fail_task_on_validation_failure. 

El flujo requerido es:

~~~text
prepare_staging
      |
      v
generate_profile
      |
      v
validate_data
      |
   +--+--+
   |     |
   v     v
publish quarantine
~~~

Las dependencias deberán asegurar que:

- no se perfile un archivo que todavía no se haya preparado;
- no se valide un lote antes de su perfilado;
- no se publique un lote si la validación falla;
- un lote rechazado quede en cuarentena.

No se deberá reemplazar la validación mediante una función Python que ejecute manualmente Great Expectations. La validación deberá continuar siendo responsabilidad de GreatExpectationsOperator.

## 12. Configurar los reintentos

<details>
<summary>Ayuda de contingencia</summary>

La configuración base `retries=0` es válida. Una justificación típica es no reintentar automáticamente un fallo determinístico de calidad. Si se decide usar retry, debe hacerse sólo en una tarea donde una causa transitoria sea plausible y explicarse por qué.

</details>

El default_args del DAG parte de retries = 0.

Esto es intencional.

Cada tarea deberá analizarse individualmente para determinar si necesita reintentos.

Se deberá decidir:

- qué tarea podría fallar por una causa transitoria;
- qué tarea podría fallar por un problema permanente;
- qué tarea no se beneficiaría de un retry.

La decisión deberá implementarse mediante configuración específica de cada tarea cuando corresponda.

Un error de calidad reproducible no deberá resolverse mediante reintentos automáticos.

## 13. Ejecutar el escenario de datos válidos

<details>
<summary>Ayuda de contingencia</summary>

El recorrido esperado es `prepare_staging → generate_profile → validate_data → publish_gold`. La tarea de cuarentena no debe convertirse en el resultado normal del lote válido. Debe existir `data/gold/netflix_clean.csv` después de una ejecución aprobada.

</details>

Preparar:

~~~bash
cp data/raw/lote_dia_1_bueno.csv data/raw/netflix_titles.csv
~~~

Abrir Airflow y ejecutar el DAG:

~~~text
orchestration_quality_practice
~~~

Deberá comprobarse en la interfaz:

- orden de las tareas;
- estado de cada tarea;
- resultado de la validación;
- generación del perfil;
- publicación en GOLD.

También deberá comprobarse físicamente:

~~~text
data/gold/netflix_clean.csv
~~~

### Evidencia

Deberá conservarse una captura en la que se observe el DAG ejecutado y otra que permita comprobar el resultado en GOLD.

## 14. Ejecutar el escenario de datos defectuosos

<details>
<summary>Ayuda de contingencia</summary>

El lote defectuoso debe provocar al menos una Expectation fallida. Como la validación está configurada para fallar la tarea de Airflow, `publish_gold` no debe ejecutarse y `quarantine` debe quedar habilitada por su `trigger_rule="one_failed"`. El resultado esperado es conservar el lote rechazado en `data/quarantine/`.

</details>

Preparar:

~~~bash
cp data/raw/lote_dia_2_malo.csv data/raw/netflix_titles.csv
~~~

Ejecutar nuevamente el DAG.

Se deberá identificar:

1. cuáles Expectations fallaron;
2. cuál fue el estado de la tarea de validación;
3. qué ocurrió con la tarea de publicación;
4. qué ocurrió con la tarea de cuarentena;
5. qué archivo terminó en data/quarantine/.

### Evidencia

Deberá conservarse evidencia del resultado de la validación, del estado del DAG, del lote rechazado y de la ausencia de publicación válida.

## 15. Analizar el comportamiento de Airflow

<details>
<summary>Ayuda de contingencia</summary>

Un error transitorio de infraestructura puede justificar retry; una Expectation que falla siempre con el mismo lote no. En este diseño, un fallo de calidad debe impedir GOLD y dirigir el flujo hacia QUARANTINE.

</details>

La ejecución deberá utilizarse para analizar la diferencia entre:

### Error de ejecución

Ejemplo conceptual: la tarea no pudo conectarse a una fuente.

### Error de calidad

Ejemplo conceptual: el lote fue procesado, pero no cumple una regla.

Responder:

- ¿Cuál de estos errores podría justificar un retry?
- ¿Cuál debería detener la publicación?
- ¿Cuál debería llevar el lote a cuarentena?

## 16. Experimento controlado

<details>
<summary>Ayuda de contingencia</summary>

Una forma sencilla es modificar deliberadamente `release_year`, `type` o `show_id` para romper una regla ya definida. Después se debe comprobar que el fallo aparece en la validación y observar el efecto sobre las tareas downstream.

</details>

Se deberá modificar deliberadamente uno de los lotes.

La modificación deberá producir una anomalía que rompa una Expectation existente o requiera una nueva regla.

Después de realizar el cambio:

1. ejecutar nuevamente el pipeline;
2. localizar el fallo;
3. relacionarlo con la regla correspondiente;
4. observar el comportamiento downstream;
5. corregir el dato o la regla;
6. volver a ejecutar el pipeline.

El experimento deberá quedar documentado.

## 17. Evidencias finales

<details>
<summary>Ayuda de contingencia</summary>

Las evidencias mínimas deben permitir reconstruir el recorrido completo sin depender de explicaciones verbales: entorno, DAG, perfil, contrato, suite/checkpoint, ejecución válida, ejecución defectuosa, GOLD y QUARANTINE.

</details>

La evidencia deberá demostrar el funcionamiento de extremo a extremo.

Como mínimo deberá incluirse:

1. entorno de Codespaces funcionando;
2. DAG visible en Airflow;
3. reporte de profiling;
4. contrato de datos;
5. Expectation Suite;
6. Checkpoint;
7. ejecución exitosa con el lote válido;
8. ejecución fallida con el lote defectuoso;
9. publicación en GOLD;
10. conservación en QUARANTINE;
11. análisis de retries;
12. experimento controlado.

Las capturas deberán mostrar suficiente contexto para interpretar el resultado.

## 18. Reflexión final

<details>
<summary>Ayuda de contingencia</summary>

Las respuestas deberían conectar conceptos, no limitarse a definiciones: profiling describe y ayuda a descubrir; validation determina cumplimiento; Airflow coordina; GX expresa y ejecuta reglas; retry responde a fallos transitorios, no corrige datos inválidos.

</details>

Responder:

1. ¿Qué diferencia existe entre profiling y data quality validation?
2. ¿Cómo se pasó de un hallazgo estadístico a una regla de calidad?
3. ¿Por qué una transformación no reemplaza una validación?
4. ¿Por qué Airflow no debería encargarse directamente de definir las reglas de calidad?
5. ¿Por qué GreatExpectationsOperator resulta apropiado para integrar GX con Airflow?
6. ¿Por qué no se establece un retry global para todas las tareas?
7. ¿Qué tipo de fallos justificarían un retry?
8. ¿Qué debería ocurrir con un lote que falla por una regla determinística de calidad?
9. ¿Qué diferencia existe entre que una tarea finalice y que los datos sean aptos para consumo?
10. ¿Qué componentes adicionales serían necesarios para llevar este diseño a una arquitectura productiva?

## 19. Criterio de terminación

<details>
<summary>Ayuda de contingencia</summary>

El criterio práctico se cumple cuando se pueden demostrar dos ejecuciones diferentes: lote válido terminado en GOLD y lote defectuoso terminado en QUARANTINE, con la validación actuando como punto de decisión entre ambos.

</details>

La práctica se considera terminada cuando el pipeline demuestra ambos recorridos:

### Lote válido

~~~text
RAW → STAGING → PROFILING → VALIDATION → GOLD
~~~

### Lote defectuoso

~~~text
RAW → STAGING → PROFILING → VALIDATION → QUARANTINE
~~~

Además, las decisiones sobre el contrato de datos y sobre los reintentos deberán estar justificadas y documentadas.
