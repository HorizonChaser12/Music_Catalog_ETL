from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import pendulum
import sys

sys.path.append("/opt/project")

local_tz = pendulum.timezone("Asia/Kolkata")

default_args = {
    "owner": "dataengineers",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "email": "suryakant.mangaraj@gmail.com",
    "start_date": datetime(2026, 5, 1, tzinfo=local_tz),
}

with DAG(
    dag_id="artists_etl_sanitised",
    default_args=default_args,
    description="Sanitised Layer for Music Analytics Warehouse",
    schedule="0 15 * * *",
    catchup=False,
    dagrun_timeout=timedelta(hours=1),
    max_active_runs=5,
) as dag:

    clean_artist_data = BashOperator(
        task_id="clean_artist_data",
        bash_command="python /opt/project/cleansing/clean_artist_data.py landing lnd_artists sanitised san_artists",
    )

    end = EmptyOperator(
        task_id="end"
    )

    #dependencies
    clean_artist_data>>end