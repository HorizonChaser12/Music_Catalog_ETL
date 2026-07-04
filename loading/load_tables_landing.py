from datetime import datetime
import logging
import sys
import json
import pytz
from loading.utils.postgres_connection import get_connection
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_table_details(cursor, schema_name, table_name):
    """Fetches column names from the database."""
    logger.info(f"Getting table information for {table_name} from Postgres...")
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position
    """
    try:
        cursor.execute(query, (schema_name, table_name))
        columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Retrieved columns: {columns}")
        return columns
    except Exception as e:
        logger.error(f"Failed to fetch table details: {e}")
        return []


def check_files(source_name):
    """Find the latest JSON file for the given source."""
    raw_dir = Path(f"/opt/project/data/raw/{source_name}")
    logger.info(f"Checking for raw_data file in {raw_dir}")
    
    files = sorted(raw_dir.glob(f"{source_name}_*.json"))

    if files:
        latest_file = files[-1]
        file_name = latest_file.name
        logger.info(f"Using {file_name}")
        file_path = str(raw_dir) + "/" + file_name
    else:
        raise FileNotFoundError(f"No {source_name} files found in {raw_dir}")
    
    return file_path


def insert_data(cursor, conn, columns, source_name, schema_name, table_name):
    """Reads JSON file and inserts data into the table with 4 columns: id, payload, created_at, updated_at."""
    if not columns:
        logger.warning("No columns retrieved, skipping insertion.")
        return 0

    file_name = check_files(source_name)
    logger.info(f"Found file: {file_name}")
    
    try:
        with open(file_name, "r") as file:
            data_content = file.read().strip()
        
        # Parse JSON
        try:
            data_list = json.loads(data_content)
        except json.JSONDecodeError:
            logger.warning("Data is not a valid JSON array.")
            return 0

        if isinstance(data_list, list):
            data_rows = data_list
        else:
            data_rows = [data_list]

        current_time = datetime.now(pytz.UTC)
        success_count = 0
        
        # Build column list for INSERT
        columns_str = ', '.join(columns)
        placeholders = ', '.join(["%s"] * len(columns))
        
        # Determine conflict target column (prefer 'id' if present)
        cols_lower = [c.lower() for c in columns]
        conflict_target = 'id' if 'id' in cols_lower else None
        
        # Build update clause for ON CONFLICT (update all except created_at)
        update_set_parts = []
        for col in columns:
            col_lower = col.lower()
            if col_lower != 'created_at':
                update_set_parts.append(f'{col} = EXCLUDED.{col}')
        
        update_clause = ', '.join(update_set_parts)
        
        # Build the INSERT statement
        if conflict_target and update_clause:
            insert_sql = f"INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT ({conflict_target}) DO UPDATE SET {update_clause}"
        elif conflict_target:
            insert_sql = f"INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT ({conflict_target}) DO NOTHING"
        else:
            insert_sql = f"INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders})"
        
        # INSERT each row
        for row in data_rows:
            try:
                values = []
                
                for col in columns:
                    col_lower = col.lower()
                    
                    # Handle artist_id / id column
                    if col_lower in ('id', 'artist_id'):
                        val = row.get('id') or row.get('artist_id')
                    
                    # Handle payload column
                    elif col_lower == 'payload':
                        val = json.dumps(row)
                    
                    # Handle created_at - only set if null
                    elif col_lower == 'created_at':
                        existing_val = row.get('created_at')
                        if existing_val is None or existing_val == "" or (isinstance(existing_val, str) and existing_val.lower() in ('none', 'null')):
                            val = current_time
                        else:
                            val = existing_val
                    
                    # Handle updated_at - always set to current time
                    elif col_lower == 'updated_at':
                        val = current_time
                    
                    else:
                        val = row.get(col)
                    
                    values.append(val)
                
                # Execute INSERT statement
                logger.debug(f"Inserting row with values: {values}")
                cursor.execute(insert_sql, tuple(values))
                success_count += 1

            except Exception as e:
                logger.warning(f"Failed to insert row: {e}")
                continue
        
        # Commit all rows
        if success_count > 0:
            conn.commit()
            logger.info(f"Successfully inserted/updated {success_count} rows into {table_name}.")
        else:
            logger.info("No rows inserted.")

        return success_count

    except Exception as e:
        logger.error(f"Error during data insertion: {e}")
        conn.rollback()
        return 0


def main():
    """Main entry point for loading landing tables."""
    # Validate arguments
    if len(sys.argv) != 4:
        print("Usage: python load_tables_landing.py <source_name> <schema_name> <table_name>")
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
        columns = get_table_details(cursor, schema_name, table_name)
        
        if not columns:
            logger.error("No columns found for the specified table/schema.")
            sys.exit(1)

        # Load and insert data
        rows_affected = insert_data(cursor, conn, columns, source_name, schema_name, table_name)
        logger.info(f"Rows affected: {rows_affected}")
        
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