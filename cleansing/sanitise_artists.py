from generic_scripts.utils.spark_session import get_spark_session
from generic_scripts.utils.postgres_utils import read_table
from generic_scripts.utils.postgres_utils import write_table
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType
import logging
import sys

source_schema = sys.argv[1]
source_table = sys.argv[2]

target_schema = sys.argv[3]
target_table = sys.argv[4]

spark = get_spark_session("sanitize_artists")
spark.sparkContext.setLogLevel("WARN")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def read_sanitise_artists():
    logging.info("=" * 80)
    logging.info(f"Reading from table : {source_schema}.{source_table}")
    logging.info("=" * 80)
    artists_df = read_table(spark, f"{source_schema}.{source_table}")
    logging.info(f"Input Count : {artists_df.count()}")

    existing = read_table(spark,f"{target_schema}.{target_table}").select("artist_id")
    

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
    new_artists = artists_df.select(
        artists_df.artists_json.id.alias("artist_id"),
        artists_df["artists_json"]["name"].alias("name"),
        artists_df.artists_json.gender.alias("gender"),
        artists_df.artists_json.country.alias("country"),
        artists_df.artists_json.type.alias("type"),
        artists_df.artists_json.area.id.alias("area_id"),
        artists_df["artists_json"]["area"]["name"].alias("area_name"),
        "created_at",
        "updated_at"
    )
    sanitised_artists = new_artists.join(existing, on="artist_id",how="left_anti")
    return sanitised_artists

def write_sanitised_artists(artists_df):
    logging.info("=" * 80)
    logging.info(f"Writing into table :  {target_schema}.{target_table}")
    logging.info("=" * 80)
    write_table(artists_df , f"{target_schema}.{target_table}" , mode="append") 

if __name__=="__main__":
    artists_df = read_sanitise_artists()
    write_sanitised_artists(artists_df)
    logging.info("=" * 80)  
    logging.info("Artist Sanitization Completed Successfully")
    logging.info("=" * 80)