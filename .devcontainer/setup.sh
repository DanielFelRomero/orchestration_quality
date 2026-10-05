#!/usr/bin/env bash
set -euo pipefail

export AIRFLOW_VERSION="2.8.3"
export PYTHON_VERSION="3.11"
export AIRFLOW_HOME="${AIRFLOW_HOME:-$(pwd)}"
export VENV_PATH="${AIRFLOW_HOME}/.venv"
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

echo "Creando entorno virtual en ${VENV_PATH}..."
python -m venv "${VENV_PATH}"

VENV_PYTHON="${VENV_PATH}/bin/python"

echo "Actualizando pip dentro del entorno virtual..."
"${VENV_PYTHON}" -m pip install --upgrade pip

echo "Instalando Apache Airflow con las constraints oficiales..."
"${VENV_PYTHON}" -m pip install \
  "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "${CONSTRAINT_URL}"

echo "Instalando dependencias de la práctica..."
"${VENV_PYTHON}" -m pip install \
  "great_expectations==0.18.19" \
  "airflow-provider-great-expectations==0.2.9" \
  "pandas" \
  "mlcroissant" \
  "ydata-profiling==4.16.1" \
  "setuptools==80.9.0"

echo "Comprobando dependencias..."
"${VENV_PYTHON}" -m pip check

echo "Entorno listo."
echo "Python: $("${VENV_PYTHON}" --version)"
echo "Airflow: $("${VENV_PYTHON}" -m airflow version)"
