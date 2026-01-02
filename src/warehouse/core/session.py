from contextlib import contextmanager
import logging
from warehouse.core.connection import PostgresConnector
from integration.airflow.conn_config import get_postgres_conn

@contextmanager
def postgres_session(db_name: str | None = None):
    """
    Context manager to manage Postgres connection and cursor.

    Args:
        db_name (str | None): Database to connect. If None, use default from Airflow connection.
        autocommit (bool): Whether to run in autocommit mode.
            + True: each statement is committed immediately (need for create database).
            + False: statements are in a transaction block, can rollback on error (safe for schema/table/insert).
    """

    pg = PostgresConnector(**get_postgres_conn())
    conn = pg.connect(db_name)

    try:
        with conn.cursor() as cursor:
            yield cursor

        conn.commit()

    except Exception as e:
        conn.rollback()
        logging.error(f"Transaction rolled back: {e}")
        raise

    finally:
        pg.close()
