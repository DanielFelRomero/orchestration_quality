"""DAG base de la práctica.

Las tareas principales y parte de la integración se encuentran
preparadas para que el estudiante complete las piezas solicitadas.
"""

from datetime import timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


BASE_PATH = Path(__file__).resolve().parents[1]

RAW_PATH = BASE_PATH / "data/raw/netflix_titles.csv"
STAGING_PATH = BASE_PATH / "data/staging/netflix_staging.csv"
PROFILE_PATH = BASE_PATH / "data/profiling/netflix_profile.html"
GOLD_PATH = BASE_PATH / "data/gold/netflix_clean.csv"
QUARANTINE_PATH = BASE_PATH / "data/quarantine/netflix_failed.csv"


def prepare_staging():
    """Preparar el lote en STAGING."""
    import pandas as pd

    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"No existe el lote esperado: {RAW_PATH}"
        )

    df = pd.read_csv(RAW_PATH)

    for column in ["director", "cast"]:
        if column in df.columns:
            df[column] = df[column].fillna("Desconocido")

    STAGING_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(STAGING_PATH, index=False)


def generate_profile_task():
    from profiling.profile_data import generate_profile

    generate_profile(
        str(STAGING_PATH),
        str(PROFILE_PATH),
    )


def publish_gold():
    """Publicar el lote aprobado."""
    raise NotImplementedError("Completar la tarea de publicación.")


def quarantine_data():
    """Conservar el lote que no supera la validación."""
    raise NotImplementedError("Completar la tarea de cuarentena.")


def validate_data():
    """Ejecutar la validación definida mediante Great Expectations."""
    raise NotImplementedError("Completar la tarea de validación.")


default_args = {
    "owner": "estudiante",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    dag_id="orchestration_quality_practice",
    default_args=default_args,
    description="Práctica integradora de perfilado, calidad y orquestación",
    schedule=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["practice", "profiling", "quality", "orchestration"],
) as dag:

    prepare = PythonOperator(
        task_id="prepare_staging",
        python_callable=prepare_staging,
    )

    profile = PythonOperator(
        task_id="generate_profile",
        python_callable=generate_profile_task,
    )

    validate = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    publish = PythonOperator(
        task_id="publish_gold",
        python_callable=publish_gold,
    )

    quarantine = PythonOperator(
        task_id="quarantine_data",
        python_callable=quarantine_data,
    )

    prepare >> profile >> validate
    validate >> [publish, quarantine]
