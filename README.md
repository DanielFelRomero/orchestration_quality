# Práctica: Orquestación y calidad de datos

## Propósito

Esta práctica integra tres capacidades trabajadas durante el curso: perfilado de datos, validación de calidad de datos y orquestación.

El ejercicio utiliza Apache Airflow como orquestador, ydata-profiling para el perfilado y Great Expectations para la validación. Se procesarán lotes de datos de un catálogo de contenidos y se establecerá un control que impida que un lote que incumpla el contrato de datos llegue a la capa de consumo.

La práctica parte de una arquitectura base previamente configurada. No se requiere construir la infraestructura desde cero. El trabajo se concentra en completar las partes del pipeline que se han dejado como puntos de implementación, establecer las reglas de calidad y comprobar el comportamiento del proceso ante datos válidos y datos defectuosos.

## Resultado esperado

Al finalizar la práctica, el pipeline deberá permitir:

1. Recibir un lote de datos en la capa RAW.
2. Preparar el lote en una capa STAGING.
3. Generar un perfil del lote.
4. Definir y ejecutar reglas de calidad mediante Great Expectations.
5. Impedir la publicación cuando la validación falle.
6. Publicar los datos validados en GOLD.
7. Conservar en cuarentena los lotes que no cumplan el contrato.
8. Observar la ejecución completa desde la interfaz de Airflow.

## Arquitectura

El flujo general está compuesto por las capas y procesos siguientes:

1. RAW.
2. STAGING.
3. PROFILING.
4. VALIDATION.
5. GOLD para lotes aprobados.
6. QUARANTINE para lotes rechazados.

Airflow coordina las tareas y sus dependencias. El perfilado permite conocer las características del lote y descubrir posibles problemas. Great Expectations representa las reglas de calidad y ejecuta la auditoría. La publicación en GOLD debe quedar condicionada al resultado de la validación.

La descripción ampliada de la arquitectura se encuentra en [docs/arquitectura.md](docs/arquitectura.md).

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
- `docs/`: documentación de apoyo.

## Regla de trabajo

La práctica se plantea como un ejercicio de construcción. Las instrucciones especifican el comportamiento esperado, pero no incluyen la implementación final.

Se espera utilizar la documentación oficial de las herramientas, inspeccionar los archivos existentes, interpretar los comentarios de las plantillas y probar cada cambio en el entorno.

No se proporciona una solución de referencia en este repositorio.

## 1. Preparación del entorno

El repositorio se deberá abrir mediante GitHub Codespaces.

Durante la creación del Codespace se instalarán las dependencias mediante `.devcontainer/setup.sh`.

La instalación utiliza Python 3.11. Las versiones de Airflow, Great Expectations, el proveedor de Airflow para Great Expectations y el perfilador se encuentran fijadas para conservar un entorno reproducible basado en el laboratorio anterior.

Después de finalizar la instalación, se podrá verificar el entorno mediante:

```bash
python --version
airflow version
great_expectations --version
python -c "import ydata_profiling; print('ydata-profiling disponible')"
python -m pip check
```

### Inicio de Airflow

La instancia de Airflow deberá iniciarse desde una terminal mediante:

```bash
bash scripts/start_airflow.sh
```

La terminal permanecerá ocupada mientras Airflow esté ejecutándose.

El modo standalone mostrará las credenciales de acceso en la terminal. El puerto 8080 deberá quedar disponible en la sección Ports de Codespaces para acceder a la interfaz web.

La terminal que mantiene Airflow en ejecución no deberá cerrarse durante la práctica.

## 2. Preparación de los lotes

En una segunda terminal se deberá ejecutar:

```bash
python scripts/preparar_lotes.py
```

El script generará dos archivos en `data/raw/`:

```text
lote_dia_1_bueno.csv
lote_dia_2_malo.csv
```

Uno representa un lote diseñado para completar el flujo. El otro contiene anomalías introducidas deliberadamente.

Antes de cada ejecución del DAG, el archivo elegido deberá copiarse a:

```text
data/raw/netflix_titles.csv
```

Para preparar el primer escenario se puede utilizar:

```bash
cp data/raw/lote_dia_1_bueno.csv data/raw/netflix_titles.csv
```

El segundo escenario se preparará mediante:

```bash
cp data/raw/lote_dia_2_malo.csv data/raw/netflix_titles.csv
```

## 3. Inspección inicial

Antes de ejecutar el perfilador, se deberá realizar una inspección básica del lote mediante Python y Pandas.

Se deberá determinar:

1. Número de filas y columnas.
2. Tipos de datos por columna.
3. Columnas con valores nulos.
4. Presencia de duplicados.
5. Valores o rangos sospechosos.
6. Posibles reglas de negocio que puedan derivarse de la estructura observada.

Las observaciones deberán registrarse antes de pasar a la etapa de profiling.

Esta etapa no sustituye al profiling. Su finalidad es establecer una primera hipótesis sobre el estado de los datos.

## 4. Data profiling

La función `generate_profile()`, ubicada en `profiling/profile_data.py`, constituye uno de los puntos de implementación de la práctica.

La función recibe:

- una ruta de entrada;
- una ruta de salida.

La implementación deberá generar un reporte HTML mediante la herramienta de perfilado seleccionada.

El reporte deberá permitir revisar como mínimo:

1. Estructura del conjunto.
2. Tipos de datos.
3. Valores faltantes.
4. Cardinalidad.
5. Distribuciones.
6. Valores mínimos y máximos cuando correspondan.
7. Advertencias relevantes.

La prueba inicial podrá realizarse fuera de Airflow mediante:

```bash
python scripts/run_profile.py
```

El archivo de entrada esperado es:

```text
data/raw/netflix_titles.csv
```

El reporte deberá quedar en:

```text
data/profiling/netflix_profile.html
```

A partir del perfil generado, deberán seleccionarse las características que posteriormente se convertirán en reglas de calidad.

## 5. Contrato de datos

Se deberá definir un contrato de datos para el dataset.

Como mínimo, el contrato deberá contemplar reglas relacionadas con:

1. Presencia de columnas requeridas.
2. Valores nulos.
3. Unicidad de una clave.
4. Valores permitidos para una variable categórica.
5. Rango lógico para una variable numérica.

Las reglas deberán justificarse a partir de la inspección inicial y del profiling.

## 6. Great Expectations

Great Expectations deberá utilizarse para representar el contrato de datos.

El trabajo deberá contemplar:

1. Inicialización de la configuración local.
2. Configuración de una fuente de datos adecuada.
3. Creación de una Expectation Suite.
4. Creación de las Expectations seleccionadas.
5. Ejecución de una validación de prueba.
6. Creación de un Checkpoint.

El Checkpoint deberá utilizar un nombre estable, debido a que posteriormente será utilizado desde Airflow.

No se establece en esta guía una lista cerrada de Expectations. Las reglas deberán derivarse del contrato definido.

Los artefactos de Great Expectations deberán quedar dentro del directorio `gx/`.

## 7. Integración con Airflow

El archivo `dags/pipeline_practica.py` contiene la estructura general del DAG y varios puntos de implementación.

El flujo deberá representar cinco responsabilidades:

1. Preparación del lote en STAGING.
2. Generación del perfil.
3. Validación de calidad.
4. Publicación del lote aprobado.
5. Conservación del lote rechazado.

Las dependencias deberán asegurar que el perfilado no se ejecute antes de preparar STAGING y que la validación no se ejecute antes del perfilado.

La publicación deberá ocurrir solamente cuando el lote sea aprobado.

Un lote rechazado no deberá llegar a GOLD.

El lote rechazado deberá quedar disponible en QUARANTINE.

La implementación deberá considerar el comportamiento de las tareas que dependen de una tarea que falla y utilizar de manera apropiada las reglas de ejecución de Airflow.

## 8. Prueba con el lote válido

El lote válido deberá copiarse a:

```text
data/raw/netflix_titles.csv
```

Después deberá ejecutarse el DAG desde la interfaz de Airflow.

La ejecución deberá permitir verificar:

1. El orden de las tareas.
2. La generación del perfil.
3. El resultado de la validación.
4. La publicación del lote en `data/gold/`.
5. La ausencia de publicación en cuarentena para este escenario.

La ejecución deberá conservar evidencia suficiente para demostrar el resultado.

## 9. Prueba con el lote defectuoso

El lote defectuoso deberá copiarse a:

```text
data/raw/netflix_titles.csv
```

Después deberá ejecutarse nuevamente el DAG.

Se deberá identificar:

1. Las Expectations que fallan.
2. El estado de cada tarea en Airflow.
3. La razón por la cual GOLD no debe recibir el lote.
4. La forma en que se conserva el lote rechazado.
5. La información disponible para diagnosticar el problema.

La ejecución deberá conservar evidencia suficiente para demostrar el resultado.

## 10. Resiliencia

Las tareas del DAG deberán revisarse para determinar cuáles deberían utilizar reintentos en un escenario real.

Se deberá documentar:

1. Una tarea para la cual un retry tenga sentido.
2. Una tarea para la cual un retry no resuelva el problema.
3. La justificación técnica de cada decisión.

El retry no deberá utilizarse como sustituto de una validación de calidad.

## 11. Experimento controlado

Se deberá introducir una anomalía adicional en uno de los lotes.

La anomalía deberá romper una regla de calidad existente o requerir una regla adicional.

Después de ejecutar nuevamente el DAG, se deberá:

1. Identificar el control afectado.
2. Observar el comportamiento de Airflow.
3. Explicar el diagnóstico.
4. Corregir la situación.
5. Repetir la ejecución y comprobar el resultado.

La modificación y sus resultados deberán quedar documentados.

## 12. Reflexión

Se deberán responder las siguientes preguntas:

1. ¿Qué información aportó el profiling que no proporcionó una validación previamente definida?
2. ¿Cómo se transformaron los hallazgos del profiling en reglas de calidad?
3. ¿Qué diferencia existe entre que una tarea de validación termine correctamente y que el lote sea considerado válido?
4. ¿Por qué la publicación debe depender del resultado de la auditoría?
5. ¿Qué ventajas aporta que Airflow conserve el historial de ejecución del pipeline?
6. ¿Qué problemas adicionales deberían considerarse antes de llevar este diseño a un entorno productivo?

## Criterios de finalización

La práctica se considerará completada cuando:

- el entorno de Codespaces funcione;
- Airflow detecte el DAG;
- el perfilado genere un reporte;
- exista una Expectation Suite funcional;
- exista un Checkpoint ejecutable;
- el lote válido pueda recorrer el flujo completo;
- el lote defectuoso sea rechazado;
- GOLD contenga únicamente datos aprobados;
- los datos rechazados se conserven en cuarentena;
- se documenten las pruebas y las reflexiones solicitadas.

## Evidencias

La organización sugerida para las evidencias se encuentra en [docs/entrega.md](docs/entrega.md).

## Referencias

- Documentación oficial de Apache Airflow.
- Documentación oficial de Great Expectations.
- Documentación oficial de ydata-profiling.
- Documentación oficial de Pandas.
