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
from pyspark.sql.types import StructType, StructField, StringType, ArrayType


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
        releases_df = read_table(
        spark, f"{schema_name}.{table_name}")
        logger_basic.info("Successfully fetched Landing/Raw Data...")
        releases_df.show()
    except Exception as e:
        logger_basic.error(f"Failed to fetch landing data:{e}")
            
    return releases_df 


def clean_release_data(releases_df, logger_obj):
    releases_df.select("payload").show(1, truncate=False) 
    try:    
        releases_schema = StructType([

            # Release identifiers
            StructField("id", StringType(), True),
            StructField("title", StringType(), True),
            StructField("status", StringType(), True),
            StructField("date", StringType(), True),
            StructField("country", StringType(), True),
            StructField("barcode", StringType(), True),


            # Text representation
            StructField(
                "text-representation",
                StructType([
                    StructField("language", StringType(), True),
                    StructField("script", StringType(), True)
                ]),
                True
            ),


            # Artist credits
            StructField(
                "artist-credit",
                ArrayType(
                    StructType([
                        StructField("name", StringType(), True),

                        StructField(
                            "artist",
                            StructType([
                                StructField("id", StringType(), True),
                                StructField("name", StringType(), True),
                                StructField("sort-name", StringType(), True)
                            ]),
                            True
                        )
                    ])
                ),
                True
            ),


            # Release group information
            StructField(
                "release-group",
                StructType([
                    StructField("id", StringType(), True),
                    StructField("title", StringType(), True),
                    StructField("primary-type", StringType(), True),

                    StructField(
                        "secondary-types",
                        ArrayType(StringType()),
                        True
                    )
                ]),
                True
            ),


            # Release country/area
            StructField(
                "area",
                StructType([
                    StructField("id", StringType(), True),
                    StructField("name", StringType(), True),
                    StructField("sort-name", StringType(), True)
                ]),
                True
            ),


            # Release events
            StructField(
                "release-events",
                ArrayType(
                    StructType([
                        StructField("date", StringType(), True),

                        StructField(
                            "area",
                            StructType([
                                StructField("id", StringType(), True),
                                StructField("name", StringType(), True),
                                StructField(
                                    "iso-3166-1-codes",
                                    ArrayType(StringType()),
                                    True
                                )
                            ]),
                            True
                        )
                    ])
                ),
                True
            ),


            # Labels
            StructField(
                "label-info",
                ArrayType(
                    StructType([
                        StructField(
                            "label",
                            StructType([
                                StructField("id", StringType(), True),
                                StructField("name", StringType(), True)
                            ]),
                            True
                        )
                    ])
                ),
                True
            ),


            # Media/discs
            StructField(
                "media",
                ArrayType(
                    StructType([
                        StructField("id", StringType(), True),
                        StructField("format", StringType(), True),
                        StructField("track-count", StringType(), True),
                        StructField("disc-count", StringType(), True)
                    ])
                ),
                True
            ),
            # Total tracks
            StructField("track-count", StringType(), True)

        ])
        releases_df = releases_df.withColumn("releases_json" , from_json("payload",releases_schema)) 

        sanitised_releases = releases_df.select(
            releases_df.releases_json.id.alias("release_id"),
            releases_df.releases_json.title.alias("release_title"),
            releases_df.releases_json.status.alias("release_status"),
            releases_df.releases_json.date.alias("release_date"),
            releases_df.releases_json.country.alias("release_country"),
            releases_df.releases_json.barcode.alias("barcode"),
            
            # Artist relationship
            releases_df["releases_json"]["artist-credit"][0]["artist"]["id"]
                .alias("artist_id"),
        
            releases_df["releases_json"]["artist-credit"][0]["artist"]["name"]
                .alias("artist_name"),
                
            # Release group relationship
            releases_df["releases_json"]["release-group"]["id"]
                .alias("release_group_id"),
        
            releases_df["releases_json"]["release-group"]["title"]
                .alias("release_group_title"),
        
            releases_df["releases_json"]["release-group"]["primary-type"]
                .alias("release_group_type"),
        
            # Area
            releases_df["releases_json"]["area"]["id"]
                .alias("area_id"),
        
            releases_df["releases_json"]["area"]["name"]
                .alias("area_name"),
                
            # Label (taking first label for now)
            releases_df["releases_json"]["label-info"][0]["label"]["id"]
                .alias("label_id"),
        
            releases_df["releases_json"]["label-info"][0]["label"]["name"]
                .alias("label_name"),
        
            # Media
            releases_df["releases_json"]["media"][0]["format"]
                .alias("format"),
        
            releases_df["releases_json"]["track-count"]
                .alias("track_count"),
                
            "created_at",
            "updated_at",
            "etl_batch_id"
        )
        logger_obj.info("Successfully cleansed Artist Data..")
        logger_obj.info(f"Count = {sanitised_releases.count()}")
    except Exception as e:
        logger_basic.error(f"Unable to filter and clean the data: {e}")
        raise
    
    return sanitised_releases

def write_release_table(release_df, schema_name, table_name):
    table_name = schema_name+'.'+table_name
    logger_basic.info(f"writing Cleansed data into {table_name}")
    
    write_table(release_df,table_name)

def main():
    # Initialize Spark session inside main() so it's only created when script is run directly
    spark = get_spark_session("sanitize_releases")
    logger = spark._jvm.org.apache.log4j.LogManager.getLogger(__name__)
    
    # Handle optional command-line arguments - default to landing/sanitised
    if len(sys.argv) == 1:
        # No arguments provided, use defaults
        lan_schema_name = "landing"
        lan_table_name = "lnd_releases"
        san_schema_name = "sanitised"
        san_table_name = "san_releases"
    elif len(sys.argv) == 5:
        # Arguments provided
        lan_schema_name = sys.argv[1]
        lan_table_name = sys.argv[2]
        san_schema_name = sys.argv[3]
        san_table_name = sys.argv[4]
    else:
        logger_basic.error("Usage: python clean_release_data.py [lan_schema_name lan_table_name san_schema_name san_table_name]")
        sys.exit(1)

    now = datetime.datetime.now()
    logger_basic.info("Script Execution Started...")
    logger_basic.info(f'Program Start Time: {now.strftime("%H:%M:%S")}')
        
    select_table_df = get_table_details(spark, lan_schema_name, lan_table_name)
   
    cleaned_df = clean_release_data(select_table_df, logger)
    
    write_release_table(cleaned_df,san_schema_name, san_table_name)
    
    logger_basic.info("Script Successfully Executed...")
    
    logger_basic.info(f'Program End Time: {now.strftime("%H:%M:%S")}')
    
    


if __name__ == "__main__":
    main()