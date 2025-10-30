import psycopg
import time
import logging

class PostgresConnector:
    def __init__(self, host: str = 'localhost',
                       port: int = 5432,
                       db_name: str = 'default',
                       username: str | None = None,
                       password: str | None = None,
                       connect_timeout: int = 5):
        """
        Initialize class to manage connections.

        Args:
            host (str): Postgres host, default is 'localhost'.
            port (int): Postgres port, default is 5432.
            db_name (str | None): Database name to connect, default is 'default'.
            username (str | None): Username for authentication, optional.
            password (str | None): Password for authentication, optional.
        """

        self._host = host
        self._port = port
        self._db_name = db_name
        self._username = username
        self._password = password
        self._connect_timeout = connect_timeout

        self._conn = None


    def connect(self):
        """
        Connect to Postgres and return psycopg connection.
        """

        try:
            start_time = time.time()
            self._conn = psycopg.connect(
                host = self._host,
                port = self._port,
                dbname = self._db_name,
                user = self._username,
                password = self._password,
                connect_timeout = self._connect_timeout
            )

            with self._conn.cursor() as cur:
                cur.execute("SELECT 1;")
            end_time = time.time()

            logging.info(
                f"Connected to PostgreSQL {self._host}:{self._port}, "
                f"database: {self._db_name} (connect took {end_time - start_time:.4f}s)"
            )

            return self._conn
        except Exception as e:
            logging.error(f"Cannot connect to PostgreSQL: {e}")

            if self._conn:
                self._conn.close()

            self._conn = None

            raise


    def close(self):
        """
        Close connection to PostgreSQL
        """

        if self._conn:
            self._conn.close()

            logging.info(f"Connection closed: {self._host}:{self._port}, database: {self._db_name}")

            self._conn = None

        else:
            logging.info("No active connection to close")
