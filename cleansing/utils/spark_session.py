from pyspark.sql import SparkSession

def get_spark_session(app_name):
    spark = SparkSession.builder \
    .config(
        "spark.jars.packages",
        "org.postgresql:postgresql:42.7.7"
    ) \
    .getOrCreate()
    return spark