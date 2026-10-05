#!/usr/bin/env bash
set -e

export AIRFLOW_HOME="$(pwd)"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
export AIRFLOW__WEBSERVER__ENABLE_PROXY_FIX="True"

echo "Inicializando Airflow..."
airflow db migrate

echo "Iniciando Airflow standalone..."
exec airflow standalone
