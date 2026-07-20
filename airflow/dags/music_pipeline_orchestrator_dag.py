from airflow import DAG
from airflow.operators.bash import BashOperator 
from datetime import datetime, timedelta
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator

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
    dag_id="music_pipeline_orchestrator_d",
    description="DAG to perform ETL on music catalog data",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False
) as dag:
    start_pipeline = EmptyOperator(
    task_id="start_pipeline"
    )
    extract_musicbrainz_data=BashOperator(
        task_id="extract_musicbrainz_data",
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
    san_artists_load = SparkSubmitOperator(
    task_id="san_artists_load",
    conn_id="spark_default",
    application="/opt/project/cleansing/sanitise_artists.py",
    application_args=[
        "landing",
        "lnd_artists",
        "sanitised",
        "san_artists"
    ],
    packages="org.postgresql:postgresql:42.7.7",
    verbose=False,
    conf={"spark.driver.extraJavaOptions": "-Dlog4j.configuration=file:/opt/project/configs/log4j.properties"},
    )
    san_releases_load = SparkSubmitOperator(
    task_id="san_releases_load",
    conn_id="spark_default",
    application="/opt/project/cleansing/sanitise_releases.py",
    application_args=[
        "landing",
        "lnd_releases",
        "sanitised",
        "san_releases"
    ],
    packages="org.postgresql:postgresql:42.7.7",
    verbose=False,
    conf={"spark.driver.extraJavaOptions": "-Dlog4j.configuration=file:/opt/project/configs/log4j.properties"},
    )
    san_recordings_load = SparkSubmitOperator(
    task_id="san_recordings_load",
    conn_id="spark_default",
    application="/opt/project/cleansing/sanitise_recordings.py",
    application_args=[
        "landing",
        "lnd_recordings",
        "sanitised",
        "san_recordings"
    ],
    packages="org.postgresql:postgresql:42.7.7",
    verbose=False,
    conf={"spark.driver.extraJavaOptions": "-Dlog4j.configuration=file:/opt/project/configs/log4j.properties"},
    )
    curate_data_load = SparkSubmitOperator(
        task_id="curate_data_load",
        conn_id="spark_default",
        application="/opt/project/curation/curated_usecases.py",
        packages="org.postgresql:postgresql:42.7.7",
        verbose=False,
        conf={"spark.driver.extraJavaOptions": "-Dlog4j.configuration=file:/opt/project/configs/log4j.properties"},
    )
    end_pipeline = EmptyOperator(
    task_id="end_pipeline"
    )


    
start_pipeline >> extract_musicbrainz_data

extract_musicbrainz_data >> [
    lnd_artists_load,
    lnd_releases_load,
    lnd_recordings_load,
    lnd_urls_load
]

lnd_artists_load >> san_artists_load

lnd_releases_load >> san_releases_load
lnd_recordings_load >> san_recordings_load

# Foreign-key ordering
san_artists_load >> san_releases_load
san_releases_load >> san_recordings_load

[san_recordings_load,lnd_urls_load] >> curate_data_load >> end_pipeline