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


def curate_artists_data(spark):
    """
    Use Transformation on MusicBrainz Artist sanitised data.

    Grain:
        1 row = 1 Artist relationship
    """
    return spark.sql("""
            select
                a.artist_id,
                a.artist_name,
                count(r.release_id) as total_releases,
                count(distinct r.release_group_id) as distinct_release_groups,
                avg(r.track_count) as avg_track_count,
                max(r.release_date) as latest_release_date,
                min(r.release_date) as earliest_release_date,
                a.etl_batch_id as etl_batch_id
            from san_artists a
            left join san_releases r
                on a.artist_id = r.artist_id
               and a.etl_batch_id = r.etl_batch_id
            group by a.artist_id, a.artist_name, a.etl_batch_id
            """)
    


def write_artists_table(artists_df, schema_name, table_name):
    full_table_name = f"{schema_name}.{table_name}"
    logger_basic.info(f"Writing curated Artist_Release data into {full_table_name}")
    write_table(artists_df, full_table_name, mode = "overwrite")


def main():
    spark = get_spark_session("curated_artists_releases")
    logger = spark._jvm.org.apache.log4j.LogManager.getLogger(__name__)

    if len(sys.argv) == 1:
        curated_schema = "curated"
        curated_table = "cur_artist_discography_summary"

    elif len(sys.argv) == 5:
        curated_schema = sys.argv[3]
        curated_table = sys.argv[4]

    else:
        logger_basic.error(
            "Usage: python cur_artist_discography_summary.py "
            "[curated_schema curated_table]"
        )
        sys.exit(1)

    start_time = datetime.datetime.now()
    logger_basic.info("Artist Curation Started...")
    logger_basic.info(f"Program Start Time: {start_time.strftime('%H:%M:%S')}")

    artists_df = read_table(spark, "sanitised.san_artists")
    artists_df.createOrReplaceTempView("san_artists")
    releases_df = read_table(spark, "sanitised.san_releases")
    releases_df.createOrReplaceTempView("san_releases")
    curated_df = curate_artists_data(spark)
    write_artists_table(curated_df, curated_schema, curated_table)

    end_time = datetime.datetime.now()
    logger_basic.info("Artist Curation Completed Successfully...")
    logger_basic.info(f"Program End Time: {end_time.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()