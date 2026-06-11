from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import pendulum
import sys

sys.path.append("/opt/project")

from ingestion.ingestion_artists_etl_landing import main as landing_fetch

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
    dag_id="artists_etl_landing",
    default_args=default_args,
    description="Landing Layer for Music Analytics Warehouse",
    schedule="0 15 * * *",
    catchup=False,
    dagrun_timeout=timedelta(hours=1),
    max_active_runs=5,
) as dag:

    ingest_data = PythonOperator(
        task_id="ingest_artist_data",
        python_callable=landing_fetch
    )
    load_data = PythonOperator(
        task_id="load_artist_release_releasegroups_data",
        python_callable=landing_load
    )

    end = EmptyOperator(
        task_id="end"
    )

    #dependencies
    ingest_data >> end