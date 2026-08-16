from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="PendingReports",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    task_extract_pending = BashOperator(
        task_id="extract_pending",
        execution_timeout=timedelta(minutes=120),
        bash_command=(
            "docker exec -w /workspace "
            '$(docker ps -q --filter "label=com.docker.compose.service=app") '
            "uv run python -m src.savi.pending_reports"
        ),
    )

    task_dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "docker exec -w /workspace/dbt -e PYTHONPATH=. "
            '$(docker ps -q --filter "label=com.docker.compose.service=app") '
            "uv run dbt build --select stg_pending_reports+"
        ),
    )

    task_extract_pending >> task_dbt_build
