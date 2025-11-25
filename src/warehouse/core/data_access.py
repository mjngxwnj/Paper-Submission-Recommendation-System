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


    def _get_last_sync_date(self,
                            table: str = 'papers',
                            column: str = 'created_at') -> None | str:
        """
        Get the last synced value (used for incremental read & load).
        Cached after first call to avoid repeated DB queries.

        Args:
            table (str): Table name without schema.
            column (str): Column to get max value.

        Returns:
            Any | None: Last synced value or None if table is empty.
        """

        if self._last_sync_date is not None:
            return self._last_sync_date

        sql = f"SELECT MAX({column}) FROM {table}"

        self._cursor.execute(sql)
        result = self._cursor.fetchone()
        self._last_sync_date = result[0] if result else None

        return self._last_sync_date


    def set_schema(self, schema: str) -> None:
        """
        Set or change the default schema for subsequent operations.

        Args:
            schema (str): Schema name to set
        """

        self._schema = schema


    def read(self, table: str, only_new: bool = False) -> pd.DataFrame:
        """
        Read data from a table.

        Args:
            table (str): Table name in a schema.
            only_new (bool):
                True  -> fetch only rows not yet present in feature schema.
                False -> fetch full table.

        Returns:
            pd.DataFrame: Fetched data
        """

        table = self._get_table(table)
        last_sync = self._get_last_sync_date() if only_new else None

        sql = f"SELECT * FROM {table}" + (f" WHERE created_at > %s" if last_sync else "")
        params = (last_sync,) if last_sync else None

        self._cursor.execute(sql, params)
        rows = self._cursor.fetchall()

        if rows:
            columns = [desc[0] for desc in self._cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            logging.info(f"Read data sucessfully from {table}")
        else:
            df = pd.DataFrame()
            logging.info(f"No data found in {table}")

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



