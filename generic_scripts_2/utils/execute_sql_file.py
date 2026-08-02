from generic_scripts_2.utils.postgres_connection import get_connection


def execute_sql_file(file_path):
    conn = get_connection()
    cursor = conn.cursor()

    with open(file_path, "r") as file:
        sql_script = file.read()

    cursor.execute(sql_script)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Executed {file_path}")
