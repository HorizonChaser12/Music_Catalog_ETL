import psycopg2

def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,
        database="music_catalog",
        user="airflow",
        password="airflow"
    )