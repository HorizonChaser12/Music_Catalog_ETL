from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import pendulum
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
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
    dag_id="catalog_core_v1_sanitised",
    default_args=default_args,
    description="Sanitised Layer for Music Analytics Warehouse",
    schedule="0 15 * * *",
    catchup=False,
    dagrun_timeout=timedelta(hours=1),
    max_active_runs=5,
) as dag:

    start = EmptyOperator(
        task_id="start"
    )
    
    clean_artist_data = SparkSubmitOperator(
    task_id="clean_artist_data",
    application="/opt/project/cleansing/catalog_core_v1/clean_artist_data.py",
    conn_id= "spark-default",
    packages="org.postgresql:postgresql:42.7.7",
    verbose=True
    ) 

    sanitised_anr_artist = BashOperator(
        task_id = "sanitised_anr_artist",
        bash_command=f"python /opt/project/generic_scripts/sanitised_anr.py landing lnd_artists sanitised san_artists",
    )
    end = EmptyOperator(
        task_id="end"
    )

    #dependencies
    start >> clean_artist_data>> sanitised_anr_artist >> end