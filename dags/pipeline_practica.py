"""DAG base de la práctica.

La estructura general del workflow se proporciona como punto de partida.
Las tareas de preparación, perfilado, validación y publicación permiten
integrar las herramientas trabajadas durante el curso.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from great_expectations_provider.operators.great_expectations import (
    GreatExpectationsOperator,
)

from datetime import timedelta
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]

RAW_PATH = BASE_PATH / "data/raw/netflix_titles.csv"
STAGING_PATH = BASE_PATH / "data/staging/netflix_staging.csv"
PROFILE_PATH = BASE_PATH / "data/profiling/netflix_profile.html"
GOLD_PATH = BASE_PATH / "data/gold/netflix_clean.csv"
QUARANTINE_PATH = BASE_PATH / "data/quarantine/netflix_failed.csv"
GX_PATH = BASE_PATH / "gx"

def prepare_staging():
    """Preparar el lote en STAGING."""
    import pandas as pd

    if not RAW_PATH.exists():
        raise FileNotFoundError(f"No existe el lote esperado: {RAW_PATH}")

    df = pd.read_csv(RAW_PATH)

    for column in ["director", "cast"]:
        if column in df.columns:
            df[column] = df[column].fillna("Desconocido")

    STAGING_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(STAGING_PATH, index=False)

def generate_profile_task():
    from profiling.profile_data import generate_profile

    generate_profile(str(STAGING_PATH), str(PROFILE_PATH))

def publish_gold():
    """Publicar el lote aprobado."""
    raise NotImplementedError("Completar la tarea de publicación.")

def quarantine_data():
    """Conservar el lote que no supera la validación."""
    raise NotImplementedError("Completar la tarea de cuarentena.")

default_args = {
    "owner": "estudiante",
    "depends_on_past": False,
    "retries": 0,
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

    validate = GreatExpectationsOperator(
        task_id="validate_data",
        data_context_root_dir=str(GX_PATH),
        checkpoint_name="netflix_checkpoint",
        fail_task_on_validation_failure=True,
    )

    publish = PythonOperator(
        task_id="publish_gold",
        python_callable=publish_gold,
        trigger_rule="all_success",
    )

    quarantine = PythonOperator(
        task_id="quarantine_data",
        python_callable=quarantine_data,
        trigger_rule="one_failed",
    )

    prepare >> profile >> validate
    validate >> [publish, quarantine]
