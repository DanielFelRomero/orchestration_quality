#!/usr/bin/env bash
set -e

export AIRFLOW_VERSION="2.8.3"
export PYTHON_VERSION="3.11"
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

python -m pip install --upgrade pip

python -m pip install \
  "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "${CONSTRAINT_URL}"

python -m pip install \
  "great_expectations==0.18.19" \
  "airflow-provider-great-expectations==0.2.9" \
  "pandas" \
  "mlcroissant" \
  "ydata-profiling==4.16.1"

python -m pip check
