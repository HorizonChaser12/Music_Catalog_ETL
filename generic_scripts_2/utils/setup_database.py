import logging

from generic_scripts_2.utils.execute_sql_file import execute_sql_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Starting database setup")

logging.info("Executing SQL file: /opt/project/sql/audit/batch_log.sql")
execute_sql_file("/opt/project/sql/audit/batch_log.sql")
logging.info("Audit tables setup completed successfully")

logging.info("Executing SQL file: /opt/project/sql/landing/create_landing_tables.sql")
execute_sql_file("/opt/project/sql/landing/create_landing_tables.sql")
logging.info("Landing tables setup completed successfully")

logging.info("Executing SQL file: /opt/project/sql/sanitised/create_sanitised_tables.sql")
execute_sql_file("/opt/project/sql/sanitised/create_sanitised_tables.sql")
logging.info("Sanitised tables setup completed successfully")

logging.info("Executing SQL file: /opt/project/sql/curated/create_curated_tables.sql")
execute_sql_file("/opt/project/sql/curated/create_curated_tables.sql")
logging.info("Curated tables setup completed successfully")

logging.infor("Executing SQL file: /opt/project/sql/audit/batch_log.sql")
execute_sql_file("/opt/project/sql/audit/batch_log.sql")
logging.info("Audit tables setup completed successfully")

