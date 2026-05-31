FROM apache/airflow:2.9.1

USER root
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

ENTRYPOINT ["/entrypoint.sh"]
