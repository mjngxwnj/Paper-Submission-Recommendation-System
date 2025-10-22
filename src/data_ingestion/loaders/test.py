from airflow.hooks.base import BaseHook
from database.mongodb.connection import MongoDBConnector


def test_mongo(conn_id: str = "mongo_default"):
    conn = BaseHook.get_connection(conn_id)

    connector = MongoDBConnector(
        host = conn.host,
        port = conn.port,
        db_name = conn.schema,
        username = conn.login,
        password = conn.password
    )

    db = connector.connect()
    data = db['test'].find()
    for i in data:
        print(i)
    connector.close()

