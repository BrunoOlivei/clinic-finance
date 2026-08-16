import requests
from airflow.models import Variable


def notify_telegram_on_failure(context: dict) -> None:
    token = Variable.get("telegram_bot_token")
    chat_id = Variable.get("telegram_chat_id")

    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    log_url = context["task_instance"].log_url

    message = (
        f"❌ Falha na DAG {dag_id}\n"
        f"Task: {task_id}\n"
        f"Log: {log_url}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=10,
    )
    response.raise_for_status()