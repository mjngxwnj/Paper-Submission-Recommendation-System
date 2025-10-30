from airflow.hooks.base import BaseHook
from database.mongodb.connection import MongoDBConnector
from database.mongodb.helpers import insert_one, insert_many

def test_mongo(conn_id: str = "mongo_default"):

    doc1 = {"name": "Alice", "age": 25}
    docs = [
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 28},
    ]

    conn = BaseHook.get_connection(conn_id)

    connector = MongoDBConnector(
        host = conn.host,
        port = conn.port,
        db_name = conn.schema,
        username = conn.login,
        password = conn.password
    )

    db = connector.connect()
    collection = db['test']

    #insert data
    insert_one(collection, doc1)

    #insert many
    insert_many(collection, docs)
