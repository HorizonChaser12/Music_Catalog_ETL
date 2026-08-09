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
    clean_release_data = SparkSubmitOperator(
        task_id="clean_release_data",
        application="/opt/project/cleansing/catalog_core_v1/clean_release_data.py",
        conn_id= "spark-default",
        packages="org.postgresql:postgresql:42.7.7",
        verbose=True
    )
    clean_urls_data = SparkSubmitOperator(
        task_id="clean_urls_data",
        application="/opt/project/cleansing/catalog_core_v1/clean_urls_data.py",
        conn_id= "spark-default",
        packages="org.postgresql:postgresql:42.7.7",
        verbose=True
    )   
    sanitised_anr_artist = BashOperator(
        task_id = "sanitised_anr_artist",
        bash_command=f"python /opt/project/generic_scripts/sanitised_anr.py landing lnd_artists sanitised san_artists cv1 group1",
    )
    sanitised_anr_releases = BashOperator(
        task_id = "sanitised_anr_releases",
        bash_command=f"python /opt/project/generic_scripts/sanitised_anr.py landing lnd_releases sanitised san_releases cv1 group1",
    )
    sanitised_anr_urls = BashOperator(
        task_id = "sanitised_anr_urls",
        bash_command=f"python /opt/project/generic_scripts/sanitised_anr.py landing lnd_urls sanitised san_urls cv1 group1",
    )
    batch_log_insertion = BashOperator(
        task_id = "batch_log_insertion_group_1",
        bash_command=f"python /opt/project/generic_scripts/batch_log_insertion.py group1 cv1",

    )
    end = EmptyOperator(
        task_id="end"
    )

    #dependencies
    start >> [
    clean_artist_data,
    clean_release_data,
    clean_urls_data
    ]
    clean_artist_data >> sanitised_anr_artist
    clean_release_data >> sanitised_anr_releases
    clean_urls_data >> sanitised_anr_urls
    [
    sanitised_anr_artist,
    sanitised_anr_releases,
    sanitised_anr_urls
    ] >> batch_log_insertion  
    batch_log_insertion >> end