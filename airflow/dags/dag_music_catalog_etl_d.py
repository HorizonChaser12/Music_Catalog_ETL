from airflow import DAG
from airflow.operators.bash import BashOperator 
from datetime import datetime

with DAG(
    dag_id="dag_music_catalog_etl_d",
    description="DAG to perform ETL on music catalog data",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False
) as dag:
    extract_api_data=BashOperator(
        task_id="extract_api_data",
        bash_command="python3 /opt/project/ingestion/fetch_artists.py && python3 /opt/project/ingestion/fetch_release.py"
    )
    load_lnd_artists=BashOperator(
        task_id="load_lnd_artists",
        bash_command="python3 /opt/project/loading/load_artists.py"
    ) 
    extract_api_data >> load_lnd_artists
    