import psycopg2

def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,
        database="postgres", #postgres for now, need to create project specific database later
        user="airflow",
        password="airflow"
    )
