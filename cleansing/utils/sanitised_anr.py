from datetime import datetime
import logging
import sys
import os
import json
from loading.utils.postgres_connection import get_connection

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


def main():
    """Main entry point for sanitised anr"""
    # Validate arguments
    if len(sys.argv) != 5:
        print("Usage: python sanitised_anr.py <schema_name_lan> <table_name_lan> <schema_name_san> <table_name_san>")
        sys.exit(1)
    
      
    schema_name_lan = sys.argv[1]
    table_name_lan = sys.argv[2]
    schema_name_san = sys.argv[3]
    table_name_san = sys.argv[4]
    
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
        landing_table_count = get_table_count(cursor, schema_name_lan, table_name_lan)
        
        sanitised_table_count = get_table_count(cursor, schema_name_san, table_name_san)
        
        if not landing_table_count and sanitised_table_count:
            logger.error("No data found for the specified table/schema.")
            sys.exit(1)
       
        
        error_count = abs(landing_table_count - sanitised_table_count)
        logger.info(f"Error count for the table {schema_name_lan}.{table_name_lan} / {schema_name_san}.{table_name_san} : {error_count}")
        
        if error_count>0:
            logger.info(f"Audit has failed with error count : {error_count}")
            sys.exit(1)
        elif error_count==0:
            logger.info(f"Audit is successful for the table {schema_name_lan}.{table_name_lan} / {schema_name_san}.{table_name_san} ")    
            
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