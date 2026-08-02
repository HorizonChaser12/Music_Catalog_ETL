import os

# Centralized DB config for the project. Reads from environment variables
# for production deployments, with sane defaults for local development.
DB_CONFIG = {
    "url": os.getenv(
        "DB_URL", "jdbc:postgresql://postgres-etl:5432/music_catalog"
    ),
    "user": os.getenv("DB_USER", "etl"),
    "password": os.getenv("DB_PASSWORD", "etl"),
    "driver": os.getenv("DB_DRIVER", "org.postgresql.Driver"),
}
