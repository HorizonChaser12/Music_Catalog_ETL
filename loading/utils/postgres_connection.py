import psycopg2

def get_connection():
    return psycopg2.connect(
        host="postgres-etl",
        port=5432,
        database="music_catalog",
        user="etl",
        password="etl"
    )