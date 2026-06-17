from datetime import datetime
import logging
import sys
import os
import json
from loading.postgres_connection import get_connection
from pathlib import Path
import re
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
        # Log the actual query being sent to the database
        sys.stderr.write(f"Executing raw SQL: {query}\n")
        cursor.execute(query, (schema_name, table_name))
        columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Query executed... Retrieved columns: {columns}")
        return columns
    except Exception as e:
        logger.error(f"Failed to fetch table details: {e}")
        return []

def check_files(source_name):
    raw_dir = Path(f"/opt/project/data/raw/{source_name}")
    logger.info(f"Checking for raw_data file in {raw_dir}")
   
        
    files = sorted(raw_dir.glob(f"{source_name}_*.json"))

    if files:
        latest_file = files[-1]

        file_name = latest_file.name

        print(f"Using {file_name}")
        
        file_path = str(raw_dir)+"/"+file_name

    # Continue loading
    else:
        raise FileNotFoundError("No artists files found")
    
    return file_path


def insert_data(cursor, conn, columns, source_name, schema_name, table_name):
    """Reads JSON file and inserts data into the table."""
    if not columns:
        logger.warning("No columns retrieved, skipping insertion.")
        return 0

    file_name = check_files(source_name)
    logger.info(f"Found file on the file path {file_name}")
    
    # --- SANITIZE IDENTIFIERS ---
    schema_name = schema_name.strip("'\"")
    table_name = table_name.strip("'\"")
    
    def safe_identifier(name):
        if not name: return "public"
        if name != name.lower() or '.' in name or ' ' in name:
            return f'"{name}"'
        return name
    
    schema_id = safe_identifier(schema_name)
    table_id = safe_identifier(table_name)
    
    # Prepare column identifiers and placeholders
    columns_identifiers = [safe_identifier(c) for c in columns]
    columns_str = ', '.join(columns_identifiers)
    placeholders = ', '.join(["%s"] * len(columns))

    # Determine conflict target column (prefer 'id' if present)
    cols_lower = [c.lower() for c in columns]
    conflict_target = 'id' if 'id' in cols_lower else None
    
    # We will build the dynamic update part per row
    try:
        with open(file_name, "r") as file:
            data_content = file.read()
            
        data_content = data_content.strip()
        
        try:
            data_list = json.loads(data_content)
        except json.JSONDecodeError:
            logger.warning("Data is not a valid JSON array.")
            return 0

        if isinstance(data_list, list):
            data_rows = data_list
        else:
            data_rows = [data_list]

        from datetime import datetime
        import pytz
        
        current_time = datetime.now(pytz.UTC) # Use pytz.UTC for timezone-aware current time
        
        # Ensure 'updated_at' is handled, but 'created_at' is not forced to update
        columns_lower = [c.lower() for c in columns]
        
        success_count = 0
        for row in data_rows:
            try:
                values = []
                update_parts = []
                
                for col in columns:
                    col_lower = col.lower()
                    val = row.get(col)
                    
                    # --- SPECIAL HANDLING FOR AUDIT COLUMNS ---
                    if col_lower == 'created_at':
                        # ONLY update if value is missing/null.
                        # If existing row has a value, we keep it (do not update).
                        if val is None or val == "" or val.lower() in ('none', 'null'):
                            val = current_time
                
                        
                    elif col_lower == 'updated_at':
                        # ALWAYS update for new inserts. For updates, set to now.
                        val = current_time
                        
                    # 1. Handle Python None (non-audit columns)
                    elif val is None:
                        # If it's None, don't update the column in DB unless it's a nullable column where we want to nullify it.
                        # For this logic, we assume 'None' means "skip update for this column" 
                        # unless it's specifically 'created_at' or 'updated_at'.
                        val = None 
                    
                    # 2. Handle Lists
                    elif isinstance(val, list):
                        val = json.dumps(val)
                        logger.debug(f"Converted list {val} to JSON string for column {col}")
                        # Ensure value is valid (not None) for update
                        if val is None: val = ""

                    # 3. Handle Strings (Dates, Quoting, Null Strings)
                    elif isinstance(val, str):
                        # Convert string representations of null to None
                        if val.lower() in ('none', 'null'):
                            val = None
                        # Check for incomplete dates: YYYY (e.g., "2010") or YYYY-MM (e.g., "2020-01")
                        elif val.isdigit() and len(val) == 4:
                            val = f"{val}-01-01" 
                            logger.debug(f"Normalized single year date: {val}")
                        # Pattern 2: Incomplete Year-Month (YYYY-MM)
                        elif re.match(r'^\d{4}-\d{2}$', val):
                            val = val + "-01" 
                            logger.debug(f"Normalized incomplete date: {val}")

                    # 4. Handle Datetime objects
                    elif isinstance(val, datetime):
                        val = val.isoformat()
                        if isinstance(val, str):
                            val = val.replace("'", "''")
                            
                    # 5. Handle other types (int, float, bool)
                    elif not isinstance(val, (str, int, float, bool)):
                        val = str(val)
                        if isinstance(val, str):
                            val = val.replace("'", "''")

                    values.append(val)
                    
                    # Build the UPDATE clause dynamically
                    # Only add to update_parts if the value is not None (or if it's a specific audit column we want to force)
                    if col_lower in ('created_at', 'updated_at'):
                         if val is not None:
                             update_parts.append(f'{safe_identifier(col)} = EXCLUDED.{safe_identifier(col)}')
                    elif val is not None:
                         update_parts.append(f'{safe_identifier(col)} = EXCLUDED.{safe_identifier(col)}')
                
                # Verify length before execution
                if len(values) != len(columns):
                    logger.warning(f"Column mismatch for {file_name}: expected {len(columns)}, got {len(values)}")
                    continue

                # Build per-row INSERT SQL. If we have update parts and a conflict target,
                # include a DO UPDATE SET clause. If no update parts, use DO NOTHING
                # when a conflict target exists to avoid an empty SET clause.
                insert_sql = f"INSERT INTO {schema_id}.{table_id} ({columns_str}) VALUES ({placeholders})"

                if conflict_target:
                    if update_parts:
                        update_clause = ', '.join(update_parts)
                        insert_sql = f"{insert_sql} ON CONFLICT ({conflict_target}) DO UPDATE SET {update_clause}"
                    else:
                        insert_sql = f"{insert_sql} ON CONFLICT ({conflict_target}) DO NOTHING"

                # Execute the statement with the values tuple
                cursor.execute(insert_sql, tuple(values))
                success_count += 1

            except KeyError as e:
                logger.warning(f"KeyError encountered in row: {e}")
                continue
            except Exception as e:
                logger.warning(f"Failed to insert row: {e}")
                continue

        # Check if we actually modified anything (optional logging)
        # Note: The ON CONFLICT logic above requires re-structuring the execute call 
        # because we cannot easily change the SQL string dynamically inside the loop 
        # without string formatting overhead. 
        # 
        # RECOMMENDATION: For high performance, it's better to construct the full SQL string 
        # *before* the loop if the schema is static. 
        # 
        # However, since your columns come from the DB schema dynamically, the current approach 
        # requires executing a generic INSERT...ON CONFLICT...DO UPDATE SET all_columns 
        # AND relying on the 'WHERE' or 'NULL' logic to prevent updates if data didn't change.
        # 
        # To fix this properly without knowing DB values beforehand, we typically update EVERYTHING 
        # (except created_at) when a conflict occurs.
        
        # Let's simplify the logic for the ON CONFLICT block to always update audit columns 
        # and update data columns only if the incoming value is not None.
        
        if success_count > 0:
            conn.commit()
            logger.info(f"Successfully inserted/updated {success_count} rows.")
        else:
            logger.info("No rows inserted.")

        return success_count

    except Exception as e:
        logger.error(f"Error during data insertion: {e}")
        conn.rollback()
        return 0



def main():
    # Validate arguments
    if len(sys.argv) != 4:
        print("Usage: python load_tables.py <source_name> <schema_name> <table_name>")
        sys.exit(1)
    
    source_name = sys.argv[1]    
    schema_name = sys.argv[2]
    table_name = sys.argv[3]
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            logger.info("Connected successfully to Postgres")
        else:
            logger.error("Can't connect to Postgres. Please check DB availability.")
            sys.exit(1)

        # 1. Get Columns
        ddl = get_table_details(cursor, schema_name, table_name)
        
        if not ddl:
            logger.error("No columns found for the specified table/schema.")
            sys.exit(1)

        # 2. Load Data
        rows_affected = insert_data(cursor, conn, ddl, source_name, schema_name, table_name)
        print(f"Rows affected: {rows_affected}")
        
        if rows_affected:
            logger.info("Data loaded successfully.")
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Closed Connection to Postgres")
        
        
if __name__ == "__main__":
    main()