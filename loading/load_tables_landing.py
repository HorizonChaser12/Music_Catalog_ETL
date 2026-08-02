from datetime import datetime, timezone
import logging
import sys
import json

try:
    import pytz
except ImportError:  # pragma: no cover - fallback for minimal environments
    pytz = None

from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
LAYER_NAME = "landing"


def build_insert_sql(columns, schema_name, table_name):
    """Build an INSERT ... ON CONFLICT statement for landing tables."""
    columns_str = ', '.join(columns)
    placeholders = ', '.join(["%s"] * len(columns))
    cols_lower = [c.lower() for c in columns]

    conflict_targets = []
    if 'id' in cols_lower:
        conflict_targets.append('id')
    if 'etl_batch_id' in cols_lower:
        conflict_targets.append('etl_batch_id')

    conflict_target = f"({', '.join(conflict_targets)})" if conflict_targets else None

    update_set_parts = []
    for col in columns:
        col_lower = col.lower()
        if col_lower != 'created_at':
            update_set_parts.append(f'{col} = EXCLUDED.{col}')

    update_clause = ', '.join(update_set_parts)

    if conflict_target and update_clause:
        return f"INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT {conflict_target} DO UPDATE SET {update_clause}"
    if conflict_target:
        return f"INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT {conflict_target} DO NOTHING"
    return f"INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders})"


def get_table_details(cursor, schema_name, table_name):
    """Fetches column names from the database."""
    logger.info(f"[{LAYER_NAME}] Fetching table schema for {schema_name}.{table_name} from Postgres")
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
    logger.info(f"[{LAYER_NAME}] Locating latest raw JSON file for source '{source_name}' in {raw_dir}")
    
    files = sorted(raw_dir.glob(f"{source_name}_*.json"))

    if files:
        latest_file = files[-1]
        file_name = latest_file.name
        file_path = str(latest_file)
        logger.info(f"[{LAYER_NAME}] Selected latest raw file: {file_path}")
    else:
        raise FileNotFoundError(f"No {source_name} files found in {raw_dir}")
    
    return file_path


def insert_data(cursor, conn, columns, source_name, schema_name, table_name,etl_batch_id):
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

        current_time = datetime.now(pytz.UTC if pytz is not None else timezone.utc)
        success_count = 0
        
        # Build the INSERT statement
        insert_sql = build_insert_sql(columns, schema_name, table_name)
        
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

                    elif col_lower == "etl_batch_id":
                        val = etl_batch_id
                        logger.error(f"etl_batch_id value is {val}")
                    
                    else:
                        val = row.get(col)
                    
                    values.append(val)
                
                # Execute INSERT statement
                logger.debug(f"[{LAYER_NAME}] Inserting landing row with values: {values}")
                logger.error(insert_sql)
                logger.error(values)
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
    if len(sys.argv) != 5:
       print("Usage: python load_tables_landing.py "
        "<source_name> <schema_name> <table_name> <etl_batch_id>"
       )
       sys.exit(1)
    source_name = sys.argv[1]
    schema_name = sys.argv[2]
    table_name = sys.argv[3]
    etl_batch_id = sys.argv[4]
    
    conn = None
    cursor = None

    try:
        from loading.postgres_connection import get_connection

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
        #logger.info(f"table name is{table_name} and schema is {schema_name}")
        
        if not columns:
            logger.error("No columns found for the specified table/schema.")
            sys.exit(1)

        # Load and insert data
        logger.error(f"etl batch id before insert is {etl_batch_id}")
        rows_affected = insert_data(cursor,conn,columns,source_name,schema_name,table_name,etl_batch_id)
        logger.info(f"[{LAYER_NAME}] Completed landing load for {schema_name}.{table_name}: {rows_affected} rows inserted/updated")
        
    except Exception as e:
        logger.error(f"[{LAYER_NAME}] Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info(f"[{LAYER_NAME}] Closed connection to Postgres")

        
if __name__ == "__main__":
    main()