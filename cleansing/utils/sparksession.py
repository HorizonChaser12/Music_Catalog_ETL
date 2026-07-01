from pyspark.sql import SparkSession

def get_spark_session(app_name):

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("spark://spark-master:7077")
        .getOrCreate()
    )

    return spark
