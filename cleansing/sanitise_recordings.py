from utils.sparksession import get_spark_session
from utils.postgres_utils import read_table
from utils.postgres_utils import write_table
from pyspark.sql.functions import col, explode, from_json
from pyspark.sql.types import *
import logging
import sys

source_schema = sys.argv[1]
source_table = sys.argv[2]

target_schema = sys.argv[3]
target_table = sys.argv[4]

spark = get_spark_session("sanitise_recordings")
spark.sparkContext.setLogLevel("ERROR")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)


def read_sanitise_recordings():
    logging.info("=" * 80)
    logging.info(f"Reading from table : {source_schema}.{source_table}")
    logging.info("=" * 80)
    recordings_df = read_table(spark, f"{source_schema}.{source_table}")
    logging.info(f"Input Count : {recordings_df.count()}")

    recordings_df.show(5)

    existing = read_table(spark, f"{target_schema}.{target_table}").select("recording_id")
    existing_releases = read_table(spark, f"{target_schema}.san_releases").select("release_id")

    recordings_schema = StructType([
        StructField("id", StringType()),
        StructField(
            "media",
            ArrayType(
                StructType([
                    StructField(
                        "tracks",
                        ArrayType(
                            StructType([
                                StructField("id", StringType()),
                                StructField("title", StringType()),
                                StructField("number", StringType()),
                                StructField("position", IntegerType()),
                                StructField(
                                    "recording",
                                    StructType([
                                        StructField("id", StringType()),
                                        StructField("title", StringType()),
                                        StructField("length", IntegerType()),
                                        StructField("first-release-date", DateType()),
                                        StructField("video", BooleanType()),
                                    ]),
                                ),
                            ])
                        ),
                    )
                ])
            ),
        ),
    ])

    recordings_df = recordings_df.withColumn("recordings_json", from_json("payload", recordings_schema))

    media_df = recordings_df.select(
        col("recordings_json.id").alias("release_id"),
        explode(col("recordings_json.media")).alias("media"),
        col("created_at"),
        col("updated_at"),
    )

    tracks_df = media_df.select(
        col("release_id"),
        explode(col("media.tracks")).alias("track"),
        col("created_at"),
        col("updated_at"),
    )

    new_recordings = tracks_df.select(
        col("track.recording.id").alias("recording_id"),
        col("release_id"),
        col("track.id").alias("track_id"),
        col("track.position").cast("integer").alias("track_position"),
        col("track.number").cast("integer").alias("track_number"),
        col("track.recording.title").alias("recording_title"),
        col("track.title").alias("track_title"),
        col("track.recording.length").cast("integer").alias("recording_length_ms"),
        col("track.recording")["first-release-date"].alias("first_release_date"),
        col("track.recording.video").alias("is_video"),
        col("created_at"),
        col("updated_at"),
    )

    deduped_recordings = new_recordings.dropDuplicates(["recording_id"])

    sanitised_recordings = (
        deduped_recordings
        .join(existing_releases, on="release_id", how="inner")
        .join(existing, on="recording_id", how="left_anti")
    )

    logging.info(f"Rows to write after deduplication: {sanitised_recordings.count()}")
    return sanitised_recordings


def write_sanitised_recordings(recordings_df):
    logging.info("=" * 80)
    logging.info(f"Writing into table :  {target_schema}.{target_table}")
    logging.info("=" * 80)
    write_table(recordings_df, f"{target_schema}.{target_table}", mode="append")


if __name__ == "__main__":
    recordings_df = read_sanitise_recordings()
    write_sanitised_recordings(recordings_df)
    logging.info("=" * 80)
    logging.info("Recording Sanitization Completed Successfully")
    logging.info("=" * 80)