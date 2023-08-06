"""
File that contains the main functionality for the Iceberg
integration within the Bodo repo. This does not contain the
main IR transformation.
"""
import os
import re
import bodo
from bodo.utils import tracing
from bodo.utils.typing import BodoError


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    try:
        rue__mhrk, hynlr__lscc, etc__fem = (bodo_iceberg_connector.
            get_iceberg_typing_schema(con, database_schema, table_name))
    except bodo_iceberg_connector.IcebergError as czh__pbau:
        if isinstance(czh__pbau, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{czh__pbau.message}:\n {czh__pbau.java_error.stacktrace()}')
        else:
            raise BodoError(czh__pbau.message)
    tai__ppgb = [_get_numba_typ_from_pa_typ(uhe__ivkb, False, True, None)[0
        ] for uhe__ivkb in hynlr__lscc]
    return rue__mhrk, tai__ppgb, etc__fem


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters):
    import bodo_iceberg_connector
    import numba.core
    try:
        tfnl__krou = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as czh__pbau:
        if isinstance(czh__pbau, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{czh__pbau.message}:\n {czh__pbau.java_error.stacktrace()}')
        else:
            raise BodoError(czh__pbau.message)
    return tfnl__krou


class IcebergParquetDataset(object):

    def __init__(self, conn, database_schema, table_name, pa_table_schema,
        pq_dataset=None):
        self.pq_dataset = pq_dataset
        self.conn = conn
        self.database_schema = database_schema
        self.table_name = table_name
        self.schema = pa_table_schema
        self.pieces = []
        self._bodo_total_rows = 0
        self._prefix = ''
        if pq_dataset is not None:
            self.pieces = pq_dataset.pieces
            self._bodo_total_rows = pq_dataset._bodo_total_rows
            self._prefix = pq_dataset._prefix


def get_iceberg_pq_dataset(conn, database_schema, table_name,
    typing_pa_table_schema, dnf_filters=None, expr_filters=None,
    is_parallel=False):
    ksec__hty = tracing.Event('get_iceberg_pq_dataset')
    from mpi4py import MPI
    xskk__fcsm = MPI.COMM_WORLD
    zfk__qyls = None
    if bodo.get_rank() == 0 or not is_parallel:
        pba__klz = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            zfk__qyls = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                detnd__zkzuq = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                pba__klz.add_attribute('num_files', len(zfk__qyls))
                pba__klz.add_attribute(f'first_{detnd__zkzuq}_files', ', '.
                    join(zfk__qyls[:detnd__zkzuq]))
        except Exception as czh__pbau:
            zfk__qyls = czh__pbau
        pba__klz.finalize()
    if is_parallel:
        zfk__qyls = xskk__fcsm.bcast(zfk__qyls)
    if isinstance(zfk__qyls, Exception):
        ndohe__zatn = zfk__qyls
        raise BodoError(
            f"""Error reading Iceberg Table: {type(ndohe__zatn).__name__}: {str(ndohe__zatn)}
"""
            )
    sffl__kpouy = zfk__qyls
    if len(sffl__kpouy) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(sffl__kpouy,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema)
        except BodoError as czh__pbau:
            if re.search('Schema .* was different', str(czh__pbau), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{czh__pbau}"""
                    )
            else:
                raise
    esfm__uzsx = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    ksec__hty.finalize()
    return esfm__uzsx
