from airflow import DAG
from airflow.operators.bash import BashOperator 
from datetime import datetime, timedelta

# Default Args
default_args = {
    "owner" : "dataengineers",
    "depends_on_past" : False,
    "email_on_failure" : True,
    "email_on_retry" : False,
    "email" : "bartakkepranoti14@gmail.com",
    # "retries" : 1,
    "max_active_runs" : 5,
    "dagrun_timeout" : timedelta(hours=1),
}

with DAG(
    dag_id="dag_musicct02_d",
    description="DAG to perform ETL on music catalog data",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False
) as dag:
    extract_api_data=BashOperator(
        task_id="extract_api_data",
        bash_command="python3 /opt/project/loading/setup_database.py && python3 /opt/project/ingestion/fetch_all_data.py"
    )
    lnd_artists_load=BashOperator(
        task_id="lnd_artists_load",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py artists landing lnd_artists"
    )
    lnd_releases_load=BashOperator(
        task_id="lnd_releases_load",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py releases landing lnd_releases "
    ) 
    lnd_recordings_load=BashOperator(
        task_id="lnd_recordings_load",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py recordings landing lnd_recordings"
    )
    lnd_urls_load=BashOperator(
        task_id="lnd_urls_load",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py urls landing lnd_urls"
    )
    san_artists_load = BashOperator(
        task_id='san_artists_load',
        bash_command="""
        /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        /opt/project/transformation/sanitize_artists.py
        """
    )
    extract_api_data >>[lnd_artists_load, lnd_releases_load, lnd_recordings_load, lnd_urls_load,san_artists_load]

    