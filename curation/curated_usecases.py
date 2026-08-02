import sys
from pyspark.sql.functions import lit
from generic_scripts_2.utils.spark_session import get_spark_session
from generic_scripts_2.utils.logger import get_logger
from generic_scripts_2.utils.postgres_utils import read_table, write_table

def read_sanitised_tables(spark, etl_batch_id):

    read_table(
        spark,
        "sanitised.san_artists"
    ).filter(
        f"etl_batch_id = '{etl_batch_id}'"
    ).createOrReplaceTempView("san_artists")

    read_table(
        spark,
        "sanitised.san_releases"
    ).filter(
        f"etl_batch_id = '{etl_batch_id}'"
    ).createOrReplaceTempView("san_releases")

    read_table(
        spark,
        "sanitised.san_recordings"
    ).filter(
        f"etl_batch_id = '{etl_batch_id}'"
    ).createOrReplaceTempView("san_recordings") 


def build_artist_track_summary(spark):
    return spark.sql("""
        select a.artist_id , a.name as artist_name , COUNT(rec.track_id) as total_tracks , a.created_at
        from san_artists  as a
        INNER JOIN san_releases as r
        ON a.artist_id=r.artist_id 
        JOIN san_recordings rec
        ON r.release_id=rec.release_id
        GROUP BY a.artist_id , a.name , a.created_at
    """)

def build_artists_release_summary(spark):
    return spark.sql("""
        select a.artist_id , a.name as artist_name , COUNT(r.release_id) as total_releases , a.created_at 
        from san_artists as a
        INNER JOIN san_releases as r
        ON a.artist_id = r.artist_id 
        GROUP BY a.artist_id,a.name,a.created_at
        order by total_releases DESC , a.name ASC 
        limit 10
    """)

def build_artist_duration_summary(spark):
    return spark.sql("""
        select a.artist_id, a.name as artist_name, COUNT(rec.track_id) as total_tracks , ROUND(AVG(rec.recording_length_ms)/60000,2) as average_track_length_ms, MAX(rec.recording_length_ms) as longest_track_ms , MIN(rec.recording_length_ms) as shortest_track_ms from san_artists as a
        INNER JOIN san_releases as r
        ON a.artist_id = r.artist_id
        INNER JOIN san_recordings as rec
        ON r.release_id = rec.release_id
        WHERE rec.recording_length_ms IS NOT NULL
        GROUP BY a.artist_id, a.name
        ORDER BY average_track_length_ms DESC, artist_name ASC
    """)
def get_release_year_summary_query():
    return """
        select cast(regexp_extract(trim(release_date), '^(\\d{4})', 1) as int) as release_year,
               count(*) as total_releases
        from san_releases
        where trim(release_date) is not null
          and trim(release_date) != ''
          and regexp_extract(trim(release_date), '^(\\d{4})', 1) != ''
        group by 1
        order by total_releases desc, release_year desc
    """


def build_release_year_summary(spark):
    return spark.sql(get_release_year_summary_query())

def build_artists_top_tracks(spark):
    return spark.sql("""
        WITH ranked_tracks AS (
        SELECT
        a.artist_id,
        a.name AS artist_name,
        r.title AS release_title,
        rec.recording_id,
        rec.track_title,
        rec.recording_length_ms,
        ROW_NUMBER() OVER (
            PARTITION BY a.artist_id
            ORDER BY rec.recording_length_ms DESC
        ) AS track_rank
        FROM san_artists a
        JOIN san_releases r
        ON r.artist_id = a.artist_id
        JOIN san_recordings rec
        ON rec.release_id = r.release_id
        WHERE rec.recording_length_ms IS NOT NULL
        )
        SELECT
        recording_id,
        artist_id,
        artist_name,
        release_title,
        track_title,
        recording_length_ms,
        track_rank
        FROM ranked_tracks
        WHERE track_rank <= 3
        ORDER BY artist_name,track_rank;
    """)

def main():
    logger = get_logger("Artist Track Summary")
    spark = get_spark_session("curated")
    
    if len(sys.argv) != 2:
        raise Exception("Usage: curated.py <etl_batch_id>")

    batch_id = sys.argv[1]
    read_sanitised_tables(spark, batch_id)
    
    artists_summary = (build_artist_track_summary(spark).withColumn("etl_batch_id", lit(batch_id)))
    write_table(artists_summary, "curated.cur_artist_track_summary" , mode="append")
    logger.info("Curated table curated.cur_artist_track_summary written successfully.")

    release_summary = (build_artists_release_summary(spark).withColumn("etl_batch_id", lit(batch_id)))
    write_table(release_summary , "curated.cur_artist_release_summary" , mode="append")
    logger.info("Curated table curated.cur_artist_release_summary written successfully.")

    duration_summary = (build_artist_duration_summary(spark).withColumn("etl_batch_id", lit(batch_id)))
    write_table(duration_summary, "curated.cur_artist_duration_summary" , mode="append")
    logger.info("Curated table curated.cur_artist_duration_summary written successfully.")

    year_summary = (build_release_year_summary(spark).withColumn("etl_batch_id", lit(batch_id)))
    write_table(year_summary, "curated.cur_release_year_summary" , mode="append")    
    logger.info("Curated table curated.cur_release_year_summary written successfully.")

    top_tracks_summary = (build_artists_top_tracks(spark).withColumn("etl_batch_id", lit(batch_id)))
    write_table(top_tracks_summary, "curated.cur_artist_top_tracks" , mode="append")
    logger.info("Curated table curated.cur_artist_top_tracks written successfully.")

if __name__ == "__main__":
    main() 