from utils.sparksession import get_spark_session
from utils.logger import get_logger
from utils.postgres_utils import read_table, write_table

def read_sanitised_tables(spark):
    read_table(spark, "sanitised.san_artists").createOrReplaceTempView("san_artists")
    read_table(spark, "sanitised.san_releases").createOrReplaceTempView("san_releases")
    read_table(spark, "sanitised.san_recordings").createOrReplaceTempView("san_recordings") 


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
        select a.artist_id , a.name , COUNT(r.release_id) as total_releases , a.created_at 
        from san_artists as a
        INNER JOIN san_releases as r
        ON a.artist_id = r.artist_id 
        GROUP BY a.artist_id,a.name,a.created_at
        order by total_releases DESC , a.name ASC 
        limit 10
    """)

def main():
    logger = get_logger("Artist Track Summary")
    spark = get_spark_session("curated")
    read_sanitised_tables(spark) 
    artists_summary = build_artist_track_summary(spark)
    write_table(artists_summary, "curated.cur_artist_track_summary" , mode="overwrite")
    logger.info("Curated table curated.cur_artist_track_summary written successfully.")

    release_summary = build_artists_release_summary(spark)
    write_table(release_summary , "curated.cur_artist_release_summary" , mode="overwrite")
    logger.info("Curated table curated.cur_artist_release_summary written successfully.")

if __name__ == "__main__":
    main() 