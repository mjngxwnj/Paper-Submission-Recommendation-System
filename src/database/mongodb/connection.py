import pymongo
from pymongo import MongoClient


class MongoDBConnector:
    def __init__(self, host: str = 'localhost', port: int = 27017, 
                       db_name: str = 'default', username: str = None,
                       password: str = None):
        """
        Initialize class to manage connections.

        Args:
            host (str): MongoDB host, default is 'localhost'.
            port (int): MongoDB port, default is 27017.
            db_name (str | None): Database name to connect, default is 'default'.
            username (str | None): Username for authentication, optional.
            password (str | None): Password for authentication, optional.
        """

        self._host = host
        self._port = port
        self._db_name = db_name
        self._username = username
        self._password = password
        self._client = None
        self._db = None


    def connect(self) -> pymongo.database.Database:
        """
        Connect to MongoDB and return the database object.

        Returns:
            pymongo.database.Database: pymongo database object

        """

        if self._username and self._password:
            uri = f"mongodb://{self._username}:{self._password}@{self._host}:{self._port}/{self._db_name}?authSource=admin"
            self._client = MongoClient(uri)

        else:
            self._client = MongoClient(self._host, self._port)

        try:
            #Ping MongoDB to ensure it's reachable
            self._client.admin.command('ping')
            self._db = self._client[self._db_name]

            print(f"[INFO] Successfully connected to MongoDB: {self._host}:{self._port}, database: {self._db_name}")

            return self._db

        except pymongo.errors.ConnectionFailure as e:
            print(f"[ERROR] Cannot connect to MongoDB: {e}")

            self._client = None
            self._db = None

            raise


    def close(self) -> None:
        """
        Close connection to MongoDB
        """

        if self._client:
            self._client.close()

            print(f"[INFO] Connection closed: {self._host}:{self._port}, database: {self._db_name}")

            self._client = None
            self._db = None

        else:
            print("[WARN] No active connection to close")
