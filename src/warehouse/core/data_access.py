from psycopg2.extensions import cursor as Cursor
import logging
from psycopg2.extras import execute_values
import pandas as pd

class WarehouseDataAccess:

    def __init__(self, cursor: Cursor, schema: str = "core") -> None:
        """
        Initialize CRUDOperations with existing cursor.

        Args:
            cur (psycopg2.extensions.cursor): Cursor from a session/connection.
        """

        self._cursor = cursor
        self._schema = schema
        self._last_sync_date: None | str = None


    def _get_table(self, table: str) -> str:
        """ Return fully qualified table name."""
        return f"{self._schema}.{table}"


    def set_schema(self, schema: str) -> None:
        """
        Set or change the default schema for subsequent operations.

        Args:
            schema (str): Schema name to set
        """

        self._schema = schema


    def read(self, table: str, conditions: str | None = None) -> pd.DataFrame:
        """
        Read data from a table with optional filter conditions.

        Args:
            table (str): Table name in a schema.
            conditions (str | None):
                SQL WHERE clause (without 'WHERE'), e.g., "vector IS NULL"

        Returns:
            pd.DataFrame: Fetched data
        """
        table = self._get_table(table)

        sql = f"SELECT * FROM {table}"
        if conditions:
            sql += f" WHERE {conditions}"

        self._cursor.execute(sql)
        rows = self._cursor.fetchall()

        if rows:
            columns = [desc[0] for desc in self._cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            logging.info(f"Read data successfully from {table} (condition: {conditions})")
        else:
            df = pd.DataFrame()
            logging.info(f"No data found in {table} (condition: {conditions})")

        return df


    def upsert(self,
               table: str,
               data: pd.DataFrame,
               conflict_keys: list[str],
               update_cols: list[str] | None = None,
               batch_size: int = 100000,
               overwrite: bool = True) -> None:
        """
        Upsert data into a table.

        Args:
            table (str): target table (schema.table)
            data (pd.DataFrame): data to upsert
            conflict_keys (list[str]): columns to detect conflict
            update_cols (list[str]): columns to update on conflict
            batch_size (int): rows per batch
            overwrite (bool): True -> update on conflict, False -> do nothing
        """
        if data.empty:
            logging.info(f"No data to upsert into {table}")
            return

        table = self._get_table(table)

        columns = data.columns.to_list()
        conflict_target = ', '.join(conflict_keys)

        if update_cols is None:
            cols_to_update = [c for c in columns if c not in conflict_keys]
        else:
            cols_to_update = update_cols

        if overwrite and cols_to_update:
            update_set = ', '.join([f"{c} = EXCLUDED.{c}" for c in cols_to_update])
            conflict_action = f"DO UPDATE SET {update_set}"
        else:
            conflict_action = "DO NOTHING"

        sql = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES %s
        ON CONFLICT ({conflict_target})
        {conflict_action}
        """

        records = [tuple(row) for row in data.values]

        # Execute in batches
        total = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            execute_values(self._cursor, sql, batch)
            total += len(batch)

        logging.info(f"Upserted {total} rows into {table}")
        return


    def update(self,
               table: str,
               data: pd.DataFrame,
               key: str,
               update_cols: list[str],
               batch_size: int = 100000) -> pd.DataFrame:
        """
        Batch update multiple rows in a table from pandas DataFrame.

        Args:
            table (str): Target table name
            data (pd.DataFrame): DataFrame containing columns [key] + update_cols
            key (str): Column to match (e.g., doi)
            update_cols (list[str]): Columns to update
            batch_size (int): Number of rows per batch
        """

        if data.empty:
            logging.info(f"No data to update in {table}")
            return

        table = self._get_table(table)

        # Build SQL template
        cols_sql = ', '.join([f"{col} = v.{col}" for col in update_cols])
        value_cols = ', '.join([key] + update_cols)

        sql = f"""
        UPDATE {table} AS p
        SET {cols_sql}
        FROM (VALUES %s) AS v({value_cols})
        WHERE p.{key} = v.{key};
        """

        records = [tuple(row) for row in data[[key] + update_cols].itertuples(index=False)]

        total = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            execute_values(self._cursor, sql, batch)
            total += len(batch)

        logging.info(f"Updated {total} rows in {table}")


