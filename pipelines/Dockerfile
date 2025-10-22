FROM apache/airflow:2.10.0-python3.11

USER airflow
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install -r /opt/airflow/requirements.txt
