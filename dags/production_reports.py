from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from alerts import notify_telegram_on_failure

with DAG(
    dag_id="ProductionReports",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    task_extract_production = BashOperator(
        task_id="extract_production",
        execution_timeout=timedelta(minutes=30),
        bash_command=(
            "docker exec -w /workspace "
            '$(docker ps -q --filter "label=com.docker.compose.service=app") '
            "uv run python -m src.savi.production_reports"
        ),
    )

    task_dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "docker exec -w /workspace/dbt -e PYTHONPATH=. "
            '$(docker ps -q --filter "label=com.docker.compose.service=app") '
            "uv run dbt build --select stg_production_reports+"
        ),
        on_failure_callback=notify_telegram_on_failure,
    )

    task_extract_production >> task_dbt_build
