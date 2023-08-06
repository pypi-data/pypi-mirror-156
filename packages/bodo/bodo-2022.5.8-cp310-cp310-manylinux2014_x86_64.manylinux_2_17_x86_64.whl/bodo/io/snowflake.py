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
    orint__ytq = urlparse(conn_str)
    lta__jlzk = {}
    if orint__ytq.username:
        lta__jlzk['user'] = orint__ytq.username
    if orint__ytq.password:
        lta__jlzk['password'] = orint__ytq.password
    if orint__ytq.hostname:
        lta__jlzk['account'] = orint__ytq.hostname
    if orint__ytq.port:
        lta__jlzk['port'] = orint__ytq.port
    if orint__ytq.path:
        yfdrc__vbf = orint__ytq.path
        if yfdrc__vbf.startswith('/'):
            yfdrc__vbf = yfdrc__vbf[1:]
        xfsx__xjtiw, schema = yfdrc__vbf.split('/')
        lta__jlzk['database'] = xfsx__xjtiw
        if schema:
            lta__jlzk['schema'] = schema
    if orint__ytq.query:
        for skabt__vmonp, yhyjf__xkx in parse_qsl(orint__ytq.query):
            lta__jlzk[skabt__vmonp] = yhyjf__xkx
            if skabt__vmonp == 'session_parameters':
                lta__jlzk[skabt__vmonp] = json.loads(yhyjf__xkx)
    lta__jlzk['application'] = 'bodo'
    return lta__jlzk


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for eqdh__bwxwt in batches:
            eqdh__bwxwt._bodo_num_rows = eqdh__bwxwt.rowcount
            self._bodo_total_rows += eqdh__bwxwt._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    zajy__gut = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    hfsgm__vswq = MPI.COMM_WORLD
    jqevz__xkj = tracing.Event('snowflake_connect', is_parallel=False)
    ncb__crx = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**ncb__crx)
    jqevz__xkj.finalize()
    if bodo.get_rank() == 0:
        ifv__riwc = conn.cursor()
        xbk__dgt = tracing.Event('get_schema', is_parallel=False)
        kgqb__xfhg = f'select * from ({query}) x LIMIT {100}'
        qglqw__qoh = ifv__riwc.execute(kgqb__xfhg).fetch_arrow_all()
        if qglqw__qoh is None:
            ebc__xqtq = ifv__riwc.describe(query)
            mobd__qbdej = [pa.field(tdy__zsat.name, FIELD_TYPE_TO_PA_TYPE[
                tdy__zsat.type_code]) for tdy__zsat in ebc__xqtq]
            schema = pa.schema(mobd__qbdej)
        else:
            schema = qglqw__qoh.schema
        xbk__dgt.finalize()
        rdkv__nwgd = tracing.Event('execute_query', is_parallel=False)
        ifv__riwc.execute(query)
        rdkv__nwgd.finalize()
        batches = ifv__riwc.get_result_batches()
        hfsgm__vswq.bcast((batches, schema))
    else:
        batches, schema = hfsgm__vswq.bcast(None)
    xdwq__cqiv = SnowflakeDataset(batches, schema, conn)
    zajy__gut.finalize()
    return xdwq__cqiv
