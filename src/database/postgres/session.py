from contextlib import contextmanager
import logging
from database.postgres.connection import PostgresConnector
from integration.airflow import get_postgres_conn

@contextmanager
def postgres_session(db_name: str | None = None, autocommit: bool = False):
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
    conn.autocommit = autocommit

    try:
        with conn.cursor() as cursor:
            yield cursor

        if not autocommit:
            conn.commit()

    except Exception as e:
        if not autocommit:
            conn.rollback()

        logging.error(f"Transaction rolled back: {e}")
        raise

    finally:
        pg.close()

