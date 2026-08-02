import logging

from pyspark.sql import SparkSession


def get_spark_session(app_name: str) -> SparkSession:
    """Create a SparkSession with reduced logging and common settings."""
    logging.getLogger("py4j").setLevel(logging.ERROR)
    logging.getLogger("pyspark").setLevel(logging.ERROR)
    logging.getLogger("pyspark.sql").setLevel(logging.ERROR)

    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.7")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")
    return spark
