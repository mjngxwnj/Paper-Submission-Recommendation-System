import re
import psycopg
from psycopg import sql
import logging


def create_database(cur: psycopg.Connection.cursor, db_name: str):
    """
    Create database if not exists using cursor.

    Args:
        cur (psycopg.Connection.cursor): Cursor with autocommit = True.
        db_name (str): Name of the database to create.
    """
    try:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            logging.info(f"Created database: {db_name}")

        else:
            logging.info(f"Database {db_name} already exists")

    except Exception as e:
        logging.error(f"Failed to create database {db_name}: {e}")

        raise


def create_schema(cur: psycopg.Connection.cursor, schema_name: str):
    """
    Create a schema in the current database if it does not exists.

    Args:
        cur (psycopg.Connection.cursor): Active database cursor.
        schema_name (str): Name of the schema to create.
    """
    try:
        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))
        logging.info(f"Created schema {schema_name}")

    except Exception as e:
        logging.error(f"Failed to create schema {schema_name}: {e}")

        raise


def create_table(cur):
    pass




