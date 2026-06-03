from postgres_connection import get_connection

def execute_sql_file(file_path):

    conn = get_connection()
    cursor = conn.cursor()

    with open(file_path,'r') as f:
        sql_Script=f.read()
    
    cursor.execute(sql_Script)
    print("SQL script executed successfully")
    conn.commit()
    cursor.close()
    conn.close()
    