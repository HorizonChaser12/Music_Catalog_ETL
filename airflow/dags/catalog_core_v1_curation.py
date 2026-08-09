from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from generic_scripts import batch_log_insertion
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
    dag_id="catalog_core_v1_curation",
    default_args=default_args,
    description="Curated Layer for Music Analytics Warehouse",
    schedule="0 15 * * *",
    catchup=False,
    dagrun_timeout=timedelta(hours=1),
    max_active_runs=5,
) as dag:

    start = EmptyOperator(
        task_id="start"
    )
    
    cur_artist_discography_summary = SparkSubmitOperator(
    task_id="cur_artist_discography_summary",
    application="/opt/project/curation/catalog_core_v1/cur_artist_discography_summary.py",
    conn_id= "spark-default",
    packages="org.postgresql:postgresql:42.7.7",
    verbose=True
    )
    end = EmptyOperator(
        task_id="end"
    )

    #dependencies
    start >> cur_artist_discography_summary >> end