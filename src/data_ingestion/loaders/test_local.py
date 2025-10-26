from database.mongodb.connection import MongoDBConnector
from database.mongodb.helpers import insert_one, insert_many


HOST = 'localhost'
PORT = 27017
DB_NAME = 'test'
USER_NAME = 'admin'
PASSWORD = 'admin'


doc1 = {"_id": 1, "name": "Alice", "age": 25}
docs = [
    {"_id": 2, "name": "Bob", "age": 30},
    {"_id": 3, "name": "Charlie", "age": 28}
]


def main():
    connector = MongoDBConnector(
        host = HOST,
        port = PORT,
        db_name = DB_NAME,
        username = USER_NAME,
        password = PASSWORD
    )

    db = connector.connect()
    collection = db['test']

    #insert data
    insert_one(collection, doc1)


main()
