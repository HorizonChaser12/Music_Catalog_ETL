from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum
from ingestion import ingest_country_data
from airflow.operators.empty import EmptyOperator


# Define the local timezone
local_tz = pendulum.timezone("Asia/Kolkata")

# Default Args
default_args = {
    "owner" : "dataengineers",
    "depends_on_past" : False,
    "email_on_failure" : True,
    "email_on_retry" : False,
    "email" : "suryakant.mangaraj@gmail.com",
    # "retries" : 1,
    "max_active_runs" : 5,
    "dagrun_timeout" : timedelta(hours=1),
    "start_date" : datetime(2026, 5, 1, tzinfo=local_tz),
    # "end_date" : 
}

with DAG(
    dag_id = "country_user_gen",
    default_args = default_args,
    description = 'DAG to find new users based on user location and country wise registration',
    schedule = '0 15 * * *',
    catchup = False,
 ) as dag:
    
    #ingestion of user data
    ingested_data = PythonOperator(
    task_id='ingest_country_data',
    python_callable=ingest_country_data.get_country_data  # or whatever function you want to call
    )
    empty_operator = EmptyOperator(task_id = 'end')
    
    # Dependencies
    ingested_data >> empty_operator


