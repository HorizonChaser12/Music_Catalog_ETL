from generic_scripts_2.utils.db_config import DB_CONFIG


def read_table(spark, table_name):
    return (
        spark.read
        .format("jdbc")
        .option("url", DB_CONFIG["url"])
        .option("dbtable", table_name)
        .option("user", DB_CONFIG["user"])
        .option("password", DB_CONFIG["password"])
        .option("driver", DB_CONFIG["driver"])
        .load()
    )


def write_table(df, table_name, mode="append"):
    (
        df.write
        .format("jdbc")
        .option("url", DB_CONFIG["url"])
        .option("dbtable", table_name)
        .option("user", DB_CONFIG["user"])
        .option("password", DB_CONFIG["password"])
        .option("driver", DB_CONFIG["driver"])
        .mode(mode)
        .save()
    )
