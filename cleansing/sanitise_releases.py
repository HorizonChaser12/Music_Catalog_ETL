from utils.sparksession import get_spark_session
from utils.postgres_utils import read_table
from utils.postgres_utils import write_table
from pyspark.sql.functions import from_json
from pyspark.sql.functions import col
from pyspark.sql.types import *
import logging
import sys

source_schema = sys.argv[1]
source_table = sys.argv[2]

target_schema = sys.argv[3]
target_table = sys.argv[4]

spark = get_spark_session("sanitize_releases")
spark.sparkContext.setLogLevel("ERROR")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)


def read_sanitise_releases():
    logging.info("=" * 80)
    logging.info(f"Reading from table : {source_schema}.{source_table}")
    logging.info("=" * 80)
    releases_df = read_table(spark, f"{source_schema}.{source_table}")
    logging.info(f"Input Count : {releases_df.count()}")

    releases_df.show(5) 

    existing = read_table(spark,f"{target_schema}.{target_table}").select("release_id")
    

    releases_schema = StructType([
    StructField("id", StringType()),
    StructField("title", StringType()),
    StructField("status", StringType()),
    StructField("date", StringType()),
    StructField("country", StringType()),
    StructField("barcode", StringType()),
    StructField("queried_artist_id", StringType()),
    StructField("track-count", IntegerType()),
    StructField(
        "artist-credit",
        ArrayType(
            StructType([
                StructField(
                    "artist",
                    StructType([
                        StructField("id", StringType())
                    ])
                )
            ])
        )
    )
    ])
   
    releases_df = releases_df.withColumn(
        "releases_json",
        from_json("payload", releases_schema)
    )

    new_release = releases_df.select(
        col("releases_json.id").alias("release_id"),
        col("releases_json.title").alias("title"),
        col("releases_json.status").alias("status"),
        col("releases_json.date").alias("release_date"),
        col("releases_json.country").alias("country"),
        col("releases_json.barcode").alias("barcode"),
        col("releases_json") ["track-count"].alias("track_count"),
        col("queried_artist_id").alias("artist_id"),
        col("created_at"),
        col("updated_at")
    )
    new_release.show(5, truncate=False)
    sanitised_releases = new_release.join(existing, on="release_id",how="left_anti")
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
    logging.info("Release Sanitization Completed Successfully")
    logging.info("=" * 80)