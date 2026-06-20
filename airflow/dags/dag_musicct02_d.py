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
    load_lnd_artists=BashOperator(
        task_id="load_lnd_artists",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py artists landing lnd_artists"
    )
    load_lnd_releases=BashOperator(
        task_id="load_lnd_releases",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py releases landing lnd_releases "
    ) 
    load_lnd_recordings=BashOperator(
        task_id="load_lnd_recordings",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py recordings landing lnd_recordings"
    )
    load_lnd_urls=BashOperator(
        task_id="load_lnd_urls",
        cwd="/opt/project/loading",
        bash_command="python3 load_tables_landing.py urls landing lnd_urls"
    )
    extract_api_data >>[load_lnd_artists, load_lnd_releases, load_lnd_recordings, load_lnd_urls]

    