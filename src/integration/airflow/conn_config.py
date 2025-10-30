from airflow.hooks.base import BaseHook
from typing import Dict


def get_mongo_conn(conn_id: str = "mongo_default") -> dict:
    """
    Retrieve MongoDB connection configuration from Airflow connection.

    Args:
        conn_id (str): Airflow connection ID (default: "mongo_default").

    Returns:
        dict: Dictionary containing MongoDB connection parameters including
              host, port, username, password,...
    """

    conn = BaseHook.get_connection(conn_id)


    mongo_config = {
        'host'     : conn.host,
        'port'     : conn.port,
        'db_name'  : conn.schema,
        'username' : conn.login,
        'password' : conn.password
    }

    return mongo_config
