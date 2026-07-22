from generic_scripts.utils.spark_session import get_spark_session
from generic_scripts.utils.postgres_utils import read_table
from generic_scripts.utils.postgres_utils import write_table
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType
import logging
import sys


spark = get_spark_session("sanitize_releases")
spark.sparkContext.setLogLevel("WARN")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    source_schema = sys.argv[1]
    source_table = sys.argv[2]

    target_schema = sys.argv[3]
    target_table = sys.argv[4]
except Exception as E:
    logging.info(f"Not all paramters are provided.ERROR.")




def read_sanitise_releases():
    logging.info("=" * 80)
    logging.info(f"Reading from table : {source_schema}.{source_table}")
    logging.info("=" * 80)
    releases_df = read_table(spark, f"{source_schema}.{source_table}")
    logging.info(f"Input Count : {releases_df.count()}")

    existing = read_table(spark,f"{target_schema}.{target_table}").select("release_id")
    

    releases_schema = StructType([
        StructField("id" , StringType()),
        StructField("country",  StringType()),
        StructField("title" , StringType()),
        StructField("packaging" , StringType()),
        StructField("packaging-id" , StringType()),
        StructField("status-id" , StringType()),
        StructField("status" , StringType()),
        StructField("date" , StringType()),
        StructField("barcode" ,StringType())
    ])

    releases_df = releases_df.withColumn("releases_json" , from_json("payload",releases_schema)) 
    new_releases = releases_df.select(
        releases_df.releases_json.id.alias("artist_id"),
        releases_df["releases_json"]["name"].alias("name"),
        releases_df.releases_json.gender.alias("gender"),
        releases_df.releases_json.country.alias("country"),
        releases_df.releases_json.type.alias("type"),
        releases_df.releases_json.area.id.alias("area_id"),
        releases_df["releases_json"]["area"]["name"].alias("area_name"),
        "created_at",
        "updated_at"
    )
    sanitised_releases = new_releases.join(existing, on="artist_id",how="left_anti")
    return sanitised_releases

def write_sanitised_releases(releases_df):
    logging.info("=" * 80)
    logging.info(f"Writing into table :  {target_schema}.{target_table}")
    logging.info("=" * 80)
    write_table(releases_df , f"{target_schema}.{target_table}" , mode="append") 

if __name__=="__main__":
    releases_df = read_sanitise_releases()
    write_sanitised_releases(releases_df)
    logging.info("=" * 80)  
    logging.info("Releases Sanitization Completed Successfully")
    logging.info("=" * 80)