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
        fmdg__doqb, nlzf__cont, qvx__sabqv = (bodo_iceberg_connector.
            get_iceberg_typing_schema(con, database_schema, table_name))
    except bodo_iceberg_connector.IcebergError as vsk__iiywz:
        if isinstance(vsk__iiywz, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{vsk__iiywz.message}:\n {vsk__iiywz.java_error.stacktrace()}'
                )
        else:
            raise BodoError(vsk__iiywz.message)
    jxerm__lmqu = [_get_numba_typ_from_pa_typ(mcmhq__syrzj, False, True,
        None)[0] for mcmhq__syrzj in nlzf__cont]
    return fmdg__doqb, jxerm__lmqu, qvx__sabqv


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters):
    import bodo_iceberg_connector
    import numba.core
    try:
        wwr__guayi = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as vsk__iiywz:
        if isinstance(vsk__iiywz, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{vsk__iiywz.message}:\n {vsk__iiywz.java_error.stacktrace()}'
                )
        else:
            raise BodoError(vsk__iiywz.message)
    return wwr__guayi


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
    ysfg__irxw = tracing.Event('get_iceberg_pq_dataset')
    from mpi4py import MPI
    anr__rggd = MPI.COMM_WORLD
    lrg__bzok = None
    if bodo.get_rank() == 0 or not is_parallel:
        xep__ipo = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            lrg__bzok = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                yrj__mjoh = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                xep__ipo.add_attribute('num_files', len(lrg__bzok))
                xep__ipo.add_attribute(f'first_{yrj__mjoh}_files', ', '.
                    join(lrg__bzok[:yrj__mjoh]))
        except Exception as vsk__iiywz:
            lrg__bzok = vsk__iiywz
        xep__ipo.finalize()
    if is_parallel:
        lrg__bzok = anr__rggd.bcast(lrg__bzok)
    if isinstance(lrg__bzok, Exception):
        loe__gjuez = lrg__bzok
        raise BodoError(
            f"""Error reading Iceberg Table: {type(loe__gjuez).__name__}: {str(loe__gjuez)}
"""
            )
    kpe__gbi = lrg__bzok
    if len(kpe__gbi) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(kpe__gbi,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema)
        except BodoError as vsk__iiywz:
            if re.search('Schema .* was different', str(vsk__iiywz), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{vsk__iiywz}"""
                    )
            else:
                raise
    bxrl__njwas = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    ysfg__irxw.finalize()
    return bxrl__njwas
