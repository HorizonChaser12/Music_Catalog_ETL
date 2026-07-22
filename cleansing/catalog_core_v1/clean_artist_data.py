import datetime
import logging
import sys
import os

# Handle imports for both module and spark-submit execution
try:
    from ...generic_scripts.utils.spark_session import get_spark_session
    from ...generic_scripts.utils.postgres_utils import read_table, write_table
except ImportError:
    # When run via spark-submit, add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from generic_scripts.utils.spark_session import get_spark_session
    from generic_scripts.utils.postgres_utils import read_table, write_table

from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger_basic = logging.getLogger(__name__)




def get_table_details(spark, schema_name, table_name):
    """_summary_
    invokes a generic script to read table data from postgres using spark
    Args:
        spark (spark connection): gives the spark connectionto to connect with spark
        schema_name (text): Schema Part for the table to be fetched
        table_name (text): Table Part for the table to be fetched

    Returns:
        dataframe: returns a dataframe from the fetched data through pyspark
    """
    try:
        artists_df = read_table(
        spark, f"{schema_name}.{table_name}")
        logger_basic.info("Successfully fetched Landing/Raw Data...")
        artists_df.show()
    except Exception as e:
        logger_basic.error(f"Failed to fetch landing data:{e}")
            
    return artists_df 


def clean_artist_data(artists_df, logger_obj):
    artists_df.select("payload").show(1, truncate=False) 
    try:    
        artists_schema = StructType([
        StructField("id" , StringType()),
        StructField("name", StringType()),
        StructField("gender", StringType()),
        StructField("country",  StringType()),
        StructField("type" , StringType()),
        StructField(
            "area" , 
            StructType([
              StructField("id", StringType()),
              StructField("name",StringType())
            ])
        )
        ])
        artists_df = artists_df.withColumn("artists_json" , from_json("payload",artists_schema)) 

        sanitised_artists = artists_df.select(
            artists_df.artists_json.id.alias("artist_id"),
            artists_df["artists_json"]["name"].alias("artist_name"),
            artists_df.artists_json.gender.alias("gender"),
            artists_df.artists_json.country.alias("country"),
            artists_df.artists_json.type.alias("type"),
            artists_df.artists_json.area.id.alias("area_id"),
            artists_df["artists_json"]["area"]["name"].alias("area_name"),
            "created_at",
            "updated_at"
        )
        logger_obj.info("Successfully cleansed Artist Data..")
        logger_obj.info(f"Count = {sanitised_artists.count()}")
    except Exception as e:
        logger_basic.error(f"Unable to filter and clean the data: {e}")
        raise
    
    return sanitised_artists

def write_artist_table(artist_df, schema_name, table_name):
    table_name = schema_name+'.'+table_name
    logger_basic.info(f"writing Cleansed data into {table_name}")
    
    write_table(artist_df,table_name)

def main():
    # Initialize Spark session inside main() so it's only created when script is run directly
    spark = get_spark_session("sanitize_artists")
    logger = spark._jvm.org.apache.log4j.LogManager.getLogger(__name__)
    
    # Handle optional command-line arguments - default to landing/sanitised
    if len(sys.argv) == 1:
        # No arguments provided, use defaults
        lan_schema_name = "landing"
        lan_table_name = "lnd_artists"
        san_schema_name = "sanitised"
        san_table_name = "san_artists"
    elif len(sys.argv) == 5:
        # Arguments provided
        lan_schema_name = sys.argv[1]
        lan_table_name = sys.argv[2]
        san_schema_name = sys.argv[3]
        san_table_name = sys.argv[4]
    else:
        logger_basic.error("Usage: python clean_artist_data.py [lan_schema_name lan_table_name san_schema_name san_table_name]")
        sys.exit(1)

    now = datetime.datetime.now()
    logger_basic.info("Script Execution Started...")
    logger_basic.info(f'Program Start Time: {now.strftime("%H:%M:%S")}')
        
    select_table_df = get_table_details(spark, lan_schema_name, lan_table_name)
   
    cleaned_df = clean_artist_data(select_table_df, logger)
    
    write_artist_table(cleaned_df,san_schema_name, san_table_name)
    
    logger_basic.info("Script Successfully Executed...")
    
    logger_basic.info(f'Program End Time: {now.strftime("%H:%M:%S")}')
    
    


if __name__ == "__main__":
    main()