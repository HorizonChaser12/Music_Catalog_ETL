import datetime
import logging
import sys
from utils.spark_session import get_spark_session
from utils.postgres_utils import read_table
from pyspark.sql.functions import from_json
from pyspark.sql.types import *
from utils.postgres_utils import write_table




# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)




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
        logger.info("Successfully fetched Landing/Raw Data...")
        artists_df.show()
    except Exception as e:
        logger.error(f"Failed to fetch landing data:{e}")
            
    return artists_df 


def clean_artist_data(artists_df):
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
    except Exception as e:
        logger.error(f"Unable to filter and clean the data: {e}")    

    logger.info("Successfully cleansed Artist Data..")
    
    return sanitised_artists

def write_artist_table(artist_df, schema_name, table_name):
    table_name = schema_name+'.'+table_name
    logger.info(f"writing Cleansed data into {table_name}")
    
    write_table(artist_df,table_name)

def main():
    if len(sys.argv) != 5:
        logger.error("Usage: python clean_artist_data.py <lan_schema_name> <lan_table_name> <san_schema_name> <lan_schema_name>")
        sys.exit(1)

    now = datetime.datetime.now()
    lan_schema_name = sys.argv[1]
    lan_table_name = sys.argv[2]
    san_schema_name = sys.argv[3]
    san_table_name = sys.argv[4]
    
    spark = get_spark_session("sanitize_artists")

    logger.info("Script Execution Started...")
    logger.info(f"Program Start Time: {now.strftime("%H:%M:%S")}")
        
    select_table_df = get_table_details(spark, lan_schema_name, lan_table_name)
   
    cleaned_df = clean_artist_data(select_table_df)
    
    write_artist_table(cleaned_df,san_schema_name, san_table_name)
    
    logger.info("Script Successfully Executed...")
    
    logger.info(f"Program End Time: {now.strftime("%H:%M:%S")}")
    
    


if __name__ == "__main__":
    main()