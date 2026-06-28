FROM apache/airflow:2.9.1

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        netcat-openbsd \
        openjdk-17-jdk-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

COPY requirements.txt /tmp/requirements.txt

USER airflow

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

USER root

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

ENTRYPOINT ["/entrypoint.sh"]