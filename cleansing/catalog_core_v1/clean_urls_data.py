import datetime
import logging
import sys
import os

# Handle imports for both module and spark-submit execution
try:
    from ...generic_scripts.utils.spark_session import get_spark_session
    from ...generic_scripts.utils.postgres_utils import read_table, write_table
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from generic_scripts.utils.spark_session import get_spark_session
    from generic_scripts.utils.postgres_utils import read_table, write_table

from pyspark.sql.functions import from_json, col, regexp_extract, lower, explode
from pyspark.sql.types import StructType, StructField, StringType, ArrayType

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger_basic = logging.getLogger(__name__)


def get_table_details(spark, schema_name, table_name):
    """Reads landing URL data from postgres."""
    try:
        urls_df = read_table(spark, f"{schema_name}.{table_name}")
        logger_basic.info("Successfully fetched Landing URL Data...")
        urls_df.show(5, truncate=False)
        return urls_df

    except Exception as e:
        logger_basic.error(f"Failed to fetch landing URL data: {e}")
        raise


def clean_url_data(urls_df, logger_obj):
    """
    Cleans MusicBrainz URL landing data.

    Grain:
        1 row = 1 URL relationship
    """
    urls_df.select("payload").show(1, truncate=False)

    # Schema describing the JSON stored in the `payload` column
    urls_schema = StructType([
        StructField("relations", ArrayType(
            StructType([
                StructField("type", StringType(), True),
                StructField("url", StructType([
                    StructField("id", StringType(), True),
                    StructField("resource", StringType(), True),
                ]), True),
            ])
        ), True),
    ])

    try:
        # Parse the raw JSON string in `payload` into a struct, THEN explode it.
        # (This step was missing — `payload` is a string until from_json runs,
        # so there is no `urls_json` column to reference beforehand.)
        urls_df = urls_df.withColumn(
            "urls_json", from_json(col("payload"), urls_schema)
        ).withColumn(
            "relation", explode(col("urls_json.relations"))
        )

        sanitised_urls = urls_df.select(
            col("relation.url.id").alias("url_id"),
            col("relation.url.resource").alias("url"),
            col("relation.type").alias("url_type"),
            regexp_extract(
                lower(col("relation.url.resource")),
                r"https?://(?:www\.)?([^/]+)",
                1,
            ).alias("domain"),
            "created_at",
            "updated_at",
            "etl_batch_id",
        )

        logger_obj.info("Successfully cleansed URL Data...")
        logger_obj.info(f"Count = {sanitised_urls.count()}")

    except Exception as e:
        logger_basic.error(f"Unable to filter and clean URL data: {e}")
        raise

    return sanitised_urls


def write_url_table(url_df, schema_name, table_name):
    full_table_name = f"{schema_name}.{table_name}"
    logger_basic.info(f"Writing cleansed URL data into {full_table_name}")
    write_table(url_df, full_table_name)


def main():
    spark = get_spark_session("sanitize_urls")
    logger = spark._jvm.org.apache.log4j.LogManager.getLogger(__name__)

    if len(sys.argv) == 1:
        landing_schema = "landing"
        landing_table = "lnd_urls"
        sanitised_schema = "sanitised"
        sanitised_table = "san_urls"

    elif len(sys.argv) == 5:
        landing_schema = sys.argv[1]
        landing_table = sys.argv[2]
        sanitised_schema = sys.argv[3]
        sanitised_table = sys.argv[4]

    else:
        logger_basic.error(
            "Usage: python sanitize_urls.py "
            "[landing_schema landing_table sanitised_schema sanitised_table]"
        )
        sys.exit(1)

    start_time = datetime.datetime.now()
    logger_basic.info("URL Sanitisation Started...")
    logger_basic.info(f"Program Start Time: {start_time.strftime('%H:%M:%S')}")

    landing_df = get_table_details(spark, landing_schema, landing_table)
    cleaned_df = clean_url_data(landing_df, logger)
    write_url_table(cleaned_df, sanitised_schema, sanitised_table)

    end_time = datetime.datetime.now()
    logger_basic.info("URL Sanitisation Completed Successfully...")
    logger_basic.info(f"Program End Time: {end_time.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()