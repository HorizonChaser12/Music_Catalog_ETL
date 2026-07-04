from datetime import datetime
import logging
import sys
import os
import json
from loading.utils.postgres_connection import get_connection
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_table_count(cursor, schema_name, table_name):
    """Fetches count of tables in landing"""
    logger.info(f"Getting table count for {table_name} from Postgres...")
    query = f"""
        SELECT COUNT(*) FROM {schema_name}.{table_name} WHERE DATE(updated_at) = CURRENT_DATE;
    """
    try:
        cursor.execute(query)
        table_count = cursor.fetchone()[0]
        logger.info(f"Count for {schema_name}.{table_name}: {table_count}")
        return table_count
    except Exception as e:
        logger.error(f"Failed to fetch table details: {e}")
        return []


def get_source_file_count(source_name):
    """Find the latest JSON file for the given source and find the no. of rows"""
    raw_dir = Path(f"/opt/project/data/raw/{source_name}")
    logger.info(f"Checking for raw_data file in {raw_dir}")
    
    files = sorted(raw_dir.glob(f"{source_name}_*.json"))

    if files:
        latest_file = files[-1]
        file_name = latest_file.name
        logger.info(f"Using {file_name}")
        file_path = str(raw_dir)
    else:
        raise FileNotFoundError(f"No {source_name} files found in {raw_dir}")
    
    try:
        os.chdir(file_path)
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)

        row_count = len(data)

        logger.info(f"Number of records: {row_count}")

    except Exception as e:
        logger.error(f"Couldn't read the file: {e}")
    
    return row_count


def main():
    """Main entry point for landing anr"""
    # Validate arguments
    if len(sys.argv) != 4:
        print("Usage: python landing_anr.py <source_name> <schema_name> <table_name>")
        sys.exit(1)
    
    source_name = sys.argv[1]    
    schema_name = sys.argv[2]
    table_name = sys.argv[3]
    
    conn = None
    cursor = None

    try:
        # Connect to database
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            logger.info("Connected successfully to Postgres")
        else:
            logger.error("Can't connect to Postgres. Please check DB availability.")
            sys.exit(1)

        # Get table columns
        landing_table_count = get_table_count(cursor, schema_name, table_name)
        
        source_file_count = get_source_file_count(source_name)
        
        if not landing_table_count :
            logger.error("No data found for the specified table/schema.")
            sys.exit(1)
        if not source_file_count :
            logger.error("No data found for the source file")
            sys.exit(1)
        
        error_count = abs(landing_table_count - source_file_count)
        logger.info(f"Error count for the table {schema_name}.{table_name} : {error_count}")
        
        if error_count>0:
            logger.info(f"Audit has failed with error count : {error_count}")
            sys.exit(1)
        elif error_count==0:
            logger.info(f"Audit is successful for the table {schema_name}.{table_name}")    
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Closed Connection to Postgres")

        
if __name__ == "__main__":
    main()