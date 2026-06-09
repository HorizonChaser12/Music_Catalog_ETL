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
    dag_id="dag_music_catalog_etl_d",
    description="DAG to perform ETL on music catalog data",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False
) as dag:
    extract_api_data=BashOperator(
        task_id="extract_api_data",
        bash_command="python3 /opt/project/loading/setup_database.py && python3 /opt/project/ingestion/fetch_all_data.py"
    )
    load_lnd_artists=BashOperator(
        task_id="load_lnd_artists",
        bash_command="python3 /opt/project/loading/load_artists.py"
    )
    load_lnd_releases=BashOperator(
        task_id="load_lnd_releases",
        bash_command="python3 /opt/project/loading/load_releases.py"
    ) 
    load_lnd_recordings=BashOperator(
        task_id="load_lnd_recordings",
        bash_command="python3 /opt/project/loading/load_recordings.py"
    )
    extract_api_data >>[load_lnd_artists, load_lnd_releases, load_lnd_recordings]

    