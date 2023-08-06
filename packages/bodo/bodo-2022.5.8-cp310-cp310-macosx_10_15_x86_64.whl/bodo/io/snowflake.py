from urllib.parse import parse_qsl, urlparse
import pyarrow as pa
import snowflake.connector
import bodo
from bodo.utils import tracing
FIELD_TYPE_TO_PA_TYPE = [pa.int64(), pa.float64(), pa.string(), pa.date32(),
    pa.timestamp('ns'), pa.string(), pa.timestamp('ns'), pa.timestamp('ns'),
    pa.timestamp('ns'), pa.string(), pa.string(), pa.binary(), pa.time64(
    'ns'), pa.bool_()]


def get_connection_params(conn_str):
    import json
    kfm__yhxv = urlparse(conn_str)
    tiq__neq = {}
    if kfm__yhxv.username:
        tiq__neq['user'] = kfm__yhxv.username
    if kfm__yhxv.password:
        tiq__neq['password'] = kfm__yhxv.password
    if kfm__yhxv.hostname:
        tiq__neq['account'] = kfm__yhxv.hostname
    if kfm__yhxv.port:
        tiq__neq['port'] = kfm__yhxv.port
    if kfm__yhxv.path:
        nhk__rhh = kfm__yhxv.path
        if nhk__rhh.startswith('/'):
            nhk__rhh = nhk__rhh[1:]
        elw__xgb, schema = nhk__rhh.split('/')
        tiq__neq['database'] = elw__xgb
        if schema:
            tiq__neq['schema'] = schema
    if kfm__yhxv.query:
        for cjok__tjtb, ckd__oivvm in parse_qsl(kfm__yhxv.query):
            tiq__neq[cjok__tjtb] = ckd__oivvm
            if cjok__tjtb == 'session_parameters':
                tiq__neq[cjok__tjtb] = json.loads(ckd__oivvm)
    tiq__neq['application'] = 'bodo'
    return tiq__neq


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for gjmoe__qjwb in batches:
            gjmoe__qjwb._bodo_num_rows = gjmoe__qjwb.rowcount
            self._bodo_total_rows += gjmoe__qjwb._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    dmt__ehj = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    wkb__rsn = MPI.COMM_WORLD
    dbi__dzun = tracing.Event('snowflake_connect', is_parallel=False)
    mdoo__cuw = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**mdoo__cuw)
    dbi__dzun.finalize()
    if bodo.get_rank() == 0:
        oyi__tlm = conn.cursor()
        lpfzm__bov = tracing.Event('get_schema', is_parallel=False)
        knkl__fsgor = f'select * from ({query}) x LIMIT {100}'
        ffckn__gph = oyi__tlm.execute(knkl__fsgor).fetch_arrow_all()
        if ffckn__gph is None:
            kijr__ymg = oyi__tlm.describe(query)
            vjucv__nzl = [pa.field(mqmv__hqtao.name, FIELD_TYPE_TO_PA_TYPE[
                mqmv__hqtao.type_code]) for mqmv__hqtao in kijr__ymg]
            schema = pa.schema(vjucv__nzl)
        else:
            schema = ffckn__gph.schema
        lpfzm__bov.finalize()
        uxdzx__anv = tracing.Event('execute_query', is_parallel=False)
        oyi__tlm.execute(query)
        uxdzx__anv.finalize()
        batches = oyi__tlm.get_result_batches()
        wkb__rsn.bcast((batches, schema))
    else:
        batches, schema = wkb__rsn.bcast(None)
    wqlc__thedu = SnowflakeDataset(batches, schema, conn)
    dmt__ehj.finalize()
    return wqlc__thedu
