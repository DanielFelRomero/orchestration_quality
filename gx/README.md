# Great Expectations

La infraestructura de Great Expectations utilizada por la práctica ya está preparada.

## Archivos que no requieren construcción

- `great_expectations.yml`: configura el Data Context, datasource, stores y Data Docs.
- `checkpoints/netflix_checkpoint.yml`: ejecuta la validación sobre `data/staging/netflix_staging.csv` usando la suite `netflix_contract`.
- `plugins/`: directorio reservado para plugins de Great Expectations.

Estos archivos forman parte de la infraestructura base de la práctica.

## Único artefacto pendiente

El estudiante debe construir:

```text
expectations/netflix_contract.json
```

Existe un ejemplo mínimo en:

```text
expectations/netflix_contract.example.json
```

El ejemplo sirve únicamente para mostrar la estructura de una Expectation Suite. Las reglas del contrato deben definirse a partir de los hallazgos de la inspección y el profiling.

## Flujo de validación

```text
data/staging/netflix_staging.csv
        |
        v
netflix_checkpoint
        |
        v
netflix_contract
        |
        v
resultado de validación
```

El Checkpoint mantiene el nombre `netflix_checkpoint` porque el DAG de la práctica lo utiliza directamente.
