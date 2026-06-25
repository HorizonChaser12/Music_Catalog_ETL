from utils.sparksession import get_spark_session
from utils.postgres_utils import read_table
from pyspark.sql.functions import from_json
from pyspark.sql.types import *

spark = get_spark_session("sanitize_artists")

artists_df = read_table(
    spark, "landing.lnd_artists"
)

#artists_df.printSchema() 
#artists_df.show(5)  

artists_df.select("payload").show(1, truncate=False) 

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
#artists_df.printSchema() 
#artists_df.select("artists_json").show(1) 

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

print("sanitised dataframe")

sanitised_artists.show(5) 