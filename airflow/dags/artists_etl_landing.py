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
    dag_id="catalog_core_v1_landing",
    default_args=default_args,
    description="Landing Layer for Music Analytics Warehouse",
    schedule="0 15 * * *",
    catchup=False,
    dagrun_timeout=timedelta(hours=1),
    max_active_runs=5,
) as dag:

    ingest_data = BashOperator(
        task_id="ingest_artist_data",
        bash_command="python /opt/project/ingestion/ingestion_artists_etl_landing.py",
    )
    load_data_artist = BashOperator(
        task_id="load_artist_data",
        bash_command=f"python /opt/project/loading/load_tables_landing.py artists landing lnd_artists",
    )
    load_data_release = BashOperator(
        task_id="load_release_data",
        bash_command=f"python /opt/project/loading/load_tables_landing.py releases landing lnd_releases",
    )
    load_data_release_groups = BashOperator(
        task_id = "load_release_groups_data",
        bash_command=f"python /opt/project/loading/load_tables_landing.py release_groups landing lnd_release_groups",
    )
    landing_anr_artist = BashOperator(
        task_id = "landing_anr_artist",
        bash_command=f"python /opt/project/loading/utils/landing_anr.py artists landing lnd_artists",
    )
    end = EmptyOperator(
        task_id="end"
    )
    landing_archival = BashOperator(
        task_id = "landing_archival_artists",
        bash_command=f"python /opt/project/loading/utils/landing_archival.py artists,releases,release_groups",
    )

    #dependencies
    ingest_data >> [load_data_artist >> load_data_release >> load_data_release_groups] >> landing_anr_artist >> landing_archival >> end