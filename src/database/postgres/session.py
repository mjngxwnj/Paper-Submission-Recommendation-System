from contextlib import contextmanager
import logging
from database.postgres.connection import PostgresConnector
from integration.airflow import get_postgres_conn

@contextmanager
def postgres_session():
    """
    Context manager to manage Postgres connection.

    - Automatically calls PostgresConnector.
    - Connect to DB and yields the conn cursor.
    - Ensures connection is closed after use.
    """

    pg = PostgresConnector(**get_postgres_conn())
    conn = pg.connect()
    cursor = conn.cursor()

    try:
        yield cursor

    except Exception as e:
        conn.rollback()
        logging.error(f"Transaction rolled back: {e}")
        raise

    finally:
        pg.close()

