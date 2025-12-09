import logging

from warehouse.core.session import postgres_session
from warehouse.core.data_access import WarehouseDataAccess

def run_embedding() -> None:
    with postgres_session() as pg_session:
        warehouse_access = WarehouseDataAccess(pg_session)

        """
        Firstly, read data from warehouse

        data = warehouse_access.read(table = 'paper_rcm_feature', conditions = 'vector IS NULL')
        """


        """ Embedding pipeline here """


        """
        Lastly, update vector into warehouse

        warehouse_access.update(table = 'paper',
                                data = data_after_embedding,
                                key = 'doi',
                                update_cols = ['vector'])
        """

