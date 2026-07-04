from execute_sql_file import execute_sql_file
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Starting database setup")
logging.info(f"Executing SQL file: /opt/project/sql/landing/create_landing_tables.sql")
execute_sql_file("/opt/project/sql/landing/create_landing_tables.sql")
logging.info("Landing tables setup completed successfully") 

logging.info(f"Executing SQL file: /opt/project/sql/sanitised/create_sanitised_tables.sql")
execute_sql_file("/opt/project/sql/sanitised/create_sanitised_tables.sql")
logging.info("Sanitised tables setup completed successfully")


