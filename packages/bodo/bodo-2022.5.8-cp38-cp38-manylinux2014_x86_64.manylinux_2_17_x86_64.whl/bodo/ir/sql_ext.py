"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
from typing import List
from urllib.parse import urlparse
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.table import Table, TableType
from bodo.io.helpers import PyArrowTableSchemaType, is_nullable
from bodo.io.parquet_pio import ParquetPredicateType
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc,
        unsupported_columns, unsupported_arrow_types, is_select_query,
        index_column_name, index_column_type, database_schema,
        pyarrow_table_schema=None):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None
        self.unsupported_columns = unsupported_columns
        self.unsupported_arrow_types = unsupported_arrow_types
        self.is_select_query = is_select_query
        self.index_column_name = index_column_name
        self.index_column_type = index_column_type
        self.out_used_cols = list(range(len(df_colnames)))
        self.database_schema = database_schema
        self.pyarrow_table_schema = pyarrow_table_schema

    def __repr__(self):
        return (
            f'{self.df_out} = ReadSql(sql_request={self.sql_request}, connection={self.connection}, col_names={self.df_colnames}, types={self.out_types}, vars={self.out_vars}, limit={self.limit}, unsupported_columns={self.unsupported_columns}, unsupported_arrow_types={self.unsupported_arrow_types}, is_select_query={self.is_select_query}, index_column_name={self.index_column_name}, index_column_type={self.index_column_type}, out_used_cols={self.out_used_cols}, database_schema={self.database_schema}, pyarrow_table_schema={self.pyarrow_table_schema})'
            )


def parse_dbtype(con_str):
    chh__nydtu = urlparse(con_str)
    db_type = chh__nydtu.scheme
    dpk__axhce = chh__nydtu.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', dpk__axhce
    if db_type == 'mysql+pymysql':
        return 'mysql', dpk__axhce
    return db_type, dpk__axhce


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    yhvz__kgyf = sql_node.out_vars[0].name
    esawk__nfmni = sql_node.out_vars[1].name
    if yhvz__kgyf not in lives and esawk__nfmni not in lives:
        return None
    elif yhvz__kgyf not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif esawk__nfmni not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        qlzxz__jjpd = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        ujyv__prue = []
        mfegk__tsq = []
        for ogb__zrztk in sql_node.out_used_cols:
            wza__gqf = sql_node.df_colnames[ogb__zrztk]
            ujyv__prue.append(wza__gqf)
            if isinstance(sql_node.out_types[ogb__zrztk], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                mfegk__tsq.append(wza__gqf)
        if sql_node.index_column_name:
            ujyv__prue.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                mfegk__tsq.append(sql_node.index_column_name)
        cgst__ilc = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', qlzxz__jjpd,
            cgst__ilc, ujyv__prue)
        if mfegk__tsq:
            gsudf__uqju = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                gsudf__uqju, cgst__ilc, mfegk__tsq)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        mlwe__mfmq = set(sql_node.unsupported_columns)
        lmce__qpt = set(sql_node.out_used_cols)
        dqo__krm = lmce__qpt & mlwe__mfmq
        if dqo__krm:
            aseb__jbnrj = sorted(dqo__krm)
            rhond__nkhss = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            xidc__pjkz = 0
            for zsiy__fgz in aseb__jbnrj:
                while sql_node.unsupported_columns[xidc__pjkz] != zsiy__fgz:
                    xidc__pjkz += 1
                rhond__nkhss.append(
                    f"Column '{sql_node.original_df_colnames[zsiy__fgz]}' with unsupported arrow type {sql_node.unsupported_arrow_types[xidc__pjkz]}"
                    )
                xidc__pjkz += 1
            mqc__tplx = '\n'.join(rhond__nkhss)
            raise BodoError(mqc__tplx, loc=sql_node.loc)
    utqke__frf, ujk__bzz = bodo.ir.connector.generate_filter_map(sql_node.
        filters)
    kwmv__kfqu = ', '.join(utqke__frf.values())
    jocg__ujjcc = (
        f'def sql_impl(sql_request, conn, database_schema, {kwmv__kfqu}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        yefb__famrh = []
        for rclzy__zaeo in sql_node.filters:
            fwk__lrb = [' '.join(['(', sgaec__tbmau[0], sgaec__tbmau[1], 
                '{' + utqke__frf[sgaec__tbmau[2].name] + '}' if isinstance(
                sgaec__tbmau[2], ir.Var) else sgaec__tbmau[2], ')']) for
                sgaec__tbmau in rclzy__zaeo]
            yefb__famrh.append(' ( ' + ' AND '.join(fwk__lrb) + ' ) ')
        rwjkg__vcnqv = ' WHERE ' + ' OR '.join(yefb__famrh)
        for ogb__zrztk, prkp__dmk in enumerate(utqke__frf.values()):
            jocg__ujjcc += f'    {prkp__dmk} = get_sql_literal({prkp__dmk})\n'
        jocg__ujjcc += f'    sql_request = f"{{sql_request}} {rwjkg__vcnqv}"\n'
    qtn__zviu = ''
    if sql_node.db_type == 'iceberg':
        qtn__zviu = kwmv__kfqu
    jocg__ujjcc += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {qtn__zviu})
"""
    nda__ukm = {}
    exec(jocg__ujjcc, {}, nda__ukm)
    cwm__ccu = nda__ukm['sql_impl']
    ituu__rkh = _gen_sql_reader_py(sql_node.df_colnames, sql_node.out_types,
        sql_node.index_column_name, sql_node.index_column_type, sql_node.
        out_used_cols, typingctx, targetctx, sql_node.db_type, sql_node.
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    tfo__citaf = (types.none if sql_node.database_schema is None else
        string_type)
    qus__ewq = compile_to_numba_ir(cwm__ccu, {'_sql_reader_py': ituu__rkh,
        'bcast_scalar': bcast_scalar, 'bcast': bcast, 'get_sql_literal':
        _get_snowflake_sql_literal}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(string_type, string_type, tfo__citaf) + tuple(
        typemap[wqd__vyuht.name] for wqd__vyuht in ujk__bzz), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        uvrq__uwkw = [sql_node.df_colnames[ogb__zrztk] for ogb__zrztk in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            uvrq__uwkw.append(sql_node.index_column_name)
        utrfg__byps = escape_column_names(uvrq__uwkw, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            vjt__urof = ('SELECT ' + utrfg__byps + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            vjt__urof = ('SELECT ' + utrfg__byps + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        vjt__urof = sql_node.sql_request
    replace_arg_nodes(qus__ewq, [ir.Const(vjt__urof, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + ujk__bzz)
    ydjjr__wwdg = qus__ewq.body[:-3]
    ydjjr__wwdg[-2].target = sql_node.out_vars[0]
    ydjjr__wwdg[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        ydjjr__wwdg.pop(-1)
    elif not sql_node.out_used_cols:
        ydjjr__wwdg.pop(-2)
    return ydjjr__wwdg


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        uvrq__uwkw = [(gexet__bdu.upper() if gexet__bdu in
            converted_colnames else gexet__bdu) for gexet__bdu in col_names]
        utrfg__byps = ', '.join([f'"{gexet__bdu}"' for gexet__bdu in
            uvrq__uwkw])
    elif db_type == 'mysql':
        utrfg__byps = ', '.join([f'`{gexet__bdu}`' for gexet__bdu in col_names]
            )
    else:
        utrfg__byps = ', '.join([f'"{gexet__bdu}"' for gexet__bdu in col_names]
            )
    return utrfg__byps


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    reglw__nki = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(reglw__nki,
        'Filter pushdown')
    if reglw__nki == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(reglw__nki, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif reglw__nki == bodo.pd_timestamp_type:

        def impl(filter_value):
            nlatw__jtzz = filter_value.nanosecond
            mfrz__qda = ''
            if nlatw__jtzz < 10:
                mfrz__qda = '00'
            elif nlatw__jtzz < 100:
                mfrz__qda = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{mfrz__qda}{nlatw__jtzz}'"
                )
        return impl
    elif reglw__nki == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {reglw__nki} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    kelmn__ulcve = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    reglw__nki = types.unliteral(filter_value)
    if isinstance(reglw__nki, types.List) and (isinstance(reglw__nki.dtype,
        scalar_isinstance) or reglw__nki.dtype in kelmn__ulcve):

        def impl(filter_value):
            vebug__majv = ', '.join([_get_snowflake_sql_literal_scalar(
                gexet__bdu) for gexet__bdu in filter_value])
            return f'({vebug__majv})'
        return impl
    elif isinstance(reglw__nki, scalar_isinstance
        ) or reglw__nki in kelmn__ulcve:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {reglw__nki} used in filter pushdown.'
            )


def sql_remove_dead_column(sql_node, column_live_map, equiv_vars, typemap):
    return bodo.ir.connector.base_connector_remove_dead_columns(sql_node,
        column_live_map, equiv_vars, typemap, 'SQLReader', sql_node.df_colnames
        )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
remove_dead_column_extensions[SqlReader] = sql_remove_dead_column
ir_extension_table_column_use[SqlReader
    ] = bodo.ir.connector.connector_table_column_use
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as hijs__mnbmc:
        djkz__wurq = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(djkz__wurq)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as hijs__mnbmc:
        djkz__wurq = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(djkz__wurq)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as hijs__mnbmc:
        djkz__wurq = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(djkz__wurq)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as hijs__mnbmc:
        djkz__wurq = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(djkz__wurq)


def req_limit(sql_request):
    import re
    engo__ihl = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    tpqbs__bzj = engo__ihl.search(sql_request)
    if tpqbs__bzj:
        return int(tpqbs__bzj.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    bhv__cszck = next_label()
    uvrq__uwkw = [col_names[ogb__zrztk] for ogb__zrztk in out_used_cols]
    nsl__qepl = [col_typs[ogb__zrztk] for ogb__zrztk in out_used_cols]
    if index_column_name:
        uvrq__uwkw.append(index_column_name)
        nsl__qepl.append(index_column_type)
    uhxg__bluc = None
    sefyi__wsxbg = None
    xaxq__omej = TableType(tuple(col_typs)) if out_used_cols else types.none
    qtn__zviu = ''
    utqke__frf = {}
    ujk__bzz = []
    if filters and db_type == 'iceberg':
        utqke__frf, ujk__bzz = bodo.ir.connector.generate_filter_map(filters)
        qtn__zviu = ', '.join(utqke__frf.values())
    jocg__ujjcc = (
        f'def sql_reader_py(sql_request, conn, database_schema, {qtn__zviu}):\n'
        )
    if db_type == 'iceberg':
        mtri__pnh, jmdoq__wsn = bodo.ir.connector.generate_arrow_filters(
            filters, utqke__frf, ujk__bzz, col_names, col_names, col_typs,
            typemap, 'iceberg')
        qytbx__bstm: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[ogb__zrztk]) for ogb__zrztk in out_used_cols]
        fndqi__ozmlx = {nzyoc__npl: ogb__zrztk for ogb__zrztk, nzyoc__npl in
            enumerate(qytbx__bstm)}
        pfpwg__coy = [int(is_nullable(col_typs[ogb__zrztk])) for ogb__zrztk in
            qytbx__bstm]
        maf__lqc = ',' if qtn__zviu else ''
        jocg__ujjcc += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        jocg__ujjcc += f"""  dnf_filters, expr_filters = get_filters_pyobject("{mtri__pnh}", "{jmdoq__wsn}", ({qtn__zviu}{maf__lqc}))
"""
        jocg__ujjcc += f'  out_table = iceberg_read(\n'
        jocg__ujjcc += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        jocg__ujjcc += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        jocg__ujjcc += (
            f'    expr_filters, selected_cols_arr_{bhv__cszck}.ctypes,\n')
        jocg__ujjcc += (
            f'    {len(qytbx__bstm)}, nullable_cols_arr_{bhv__cszck}.ctypes,\n'
            )
        jocg__ujjcc += f'    pyarrow_table_schema_{bhv__cszck},\n'
        jocg__ujjcc += f'  )\n'
        jocg__ujjcc += f'  check_and_propagate_cpp_exception()\n'
        gqyr__lpxi = not out_used_cols
        xaxq__omej = TableType(tuple(col_typs))
        if gqyr__lpxi:
            xaxq__omej = types.none
        esawk__nfmni = 'None'
        if index_column_name is not None:
            sdgm__sqqxo = len(out_used_cols) + 1 if not gqyr__lpxi else 0
            esawk__nfmni = (
                f'info_to_array(info_from_table(out_table, {sdgm__sqqxo}), index_col_typ)'
                )
        jocg__ujjcc += f'  index_var = {esawk__nfmni}\n'
        uhxg__bluc = None
        if not gqyr__lpxi:
            uhxg__bluc = []
            htb__skk = 0
            for ogb__zrztk in range(len(col_names)):
                if htb__skk < len(out_used_cols
                    ) and ogb__zrztk == out_used_cols[htb__skk]:
                    uhxg__bluc.append(fndqi__ozmlx[ogb__zrztk])
                    htb__skk += 1
                else:
                    uhxg__bluc.append(-1)
            uhxg__bluc = np.array(uhxg__bluc, dtype=np.int64)
        if gqyr__lpxi:
            jocg__ujjcc += '  table_var = None\n'
        else:
            jocg__ujjcc += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{bhv__cszck}, py_table_type_{bhv__cszck})
"""
        jocg__ujjcc += f'  delete_table(out_table)\n'
        jocg__ujjcc += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        jocg__ujjcc += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        pfpwg__coy = [int(is_nullable(col_typs[ogb__zrztk])) for ogb__zrztk in
            out_used_cols]
        if index_column_name:
            pfpwg__coy.append(int(is_nullable(index_column_type)))
        jocg__ujjcc += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(pfpwg__coy)}, np.array({pfpwg__coy}, dtype=np.int32).ctypes)
"""
        jocg__ujjcc += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            jocg__ujjcc += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            jocg__ujjcc += '  index_var = None\n'
        if out_used_cols:
            xidc__pjkz = []
            htb__skk = 0
            for ogb__zrztk in range(len(col_names)):
                if htb__skk < len(out_used_cols
                    ) and ogb__zrztk == out_used_cols[htb__skk]:
                    xidc__pjkz.append(htb__skk)
                    htb__skk += 1
                else:
                    xidc__pjkz.append(-1)
            uhxg__bluc = np.array(xidc__pjkz, dtype=np.int64)
            jocg__ujjcc += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{bhv__cszck}, py_table_type_{bhv__cszck})
"""
        else:
            jocg__ujjcc += '  table_var = None\n'
        jocg__ujjcc += '  delete_table(out_table)\n'
        jocg__ujjcc += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            jocg__ujjcc += f"""  type_usecols_offsets_arr_{bhv__cszck}_2 = type_usecols_offsets_arr_{bhv__cszck}
"""
            sefyi__wsxbg = np.array(out_used_cols, dtype=np.int64)
        jocg__ujjcc += '  df_typeref_2 = df_typeref\n'
        jocg__ujjcc += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            jocg__ujjcc += '  pymysql_check()\n'
        elif db_type == 'oracle':
            jocg__ujjcc += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            jocg__ujjcc += '  psycopg2_check()\n'
        if parallel:
            jocg__ujjcc += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                jocg__ujjcc += f'  nb_row = {limit}\n'
            else:
                jocg__ujjcc += '  with objmode(nb_row="int64"):\n'
                jocg__ujjcc += f'     if rank == {MPI_ROOT}:\n'
                jocg__ujjcc += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                jocg__ujjcc += '         frame = pd.read_sql(sql_cons, conn)\n'
                jocg__ujjcc += '         nb_row = frame.iat[0,0]\n'
                jocg__ujjcc += '     else:\n'
                jocg__ujjcc += '         nb_row = 0\n'
                jocg__ujjcc += '  nb_row = bcast_scalar(nb_row)\n'
            jocg__ujjcc += f"""  with objmode(table_var=py_table_type_{bhv__cszck}, index_var=index_col_typ):
"""
            jocg__ujjcc += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                jocg__ujjcc += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                jocg__ujjcc += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            jocg__ujjcc += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            jocg__ujjcc += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            jocg__ujjcc += f"""  with objmode(table_var=py_table_type_{bhv__cszck}, index_var=index_col_typ):
"""
            jocg__ujjcc += '    df_ret = pd.read_sql(sql_request, conn)\n'
            jocg__ujjcc += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            jocg__ujjcc += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            jocg__ujjcc += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            jocg__ujjcc += '    index_var = None\n'
        if out_used_cols:
            jocg__ujjcc += f'    arrs = []\n'
            jocg__ujjcc += f'    for i in range(df_ret.shape[1]):\n'
            jocg__ujjcc += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            jocg__ujjcc += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{bhv__cszck}_2, {len(col_names)})
"""
        else:
            jocg__ujjcc += '    table_var = None\n'
    jocg__ujjcc += '  return (table_var, index_var)\n'
    dnxpl__cod = globals()
    dnxpl__cod.update({'bodo': bodo, f'py_table_type_{bhv__cszck}':
        xaxq__omej, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        dnxpl__cod.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{bhv__cszck}': uhxg__bluc})
    if db_type == 'iceberg':
        dnxpl__cod.update({f'selected_cols_arr_{bhv__cszck}': np.array(
            qytbx__bstm, np.int32), f'nullable_cols_arr_{bhv__cszck}': np.
            array(pfpwg__coy, np.int32), f'py_table_type_{bhv__cszck}':
            xaxq__omej, f'pyarrow_table_schema_{bhv__cszck}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        dnxpl__cod.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        dnxpl__cod.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(nsl__qepl), bodo.RangeIndexType(None),
            tuple(uvrq__uwkw)), 'Table': Table,
            f'type_usecols_offsets_arr_{bhv__cszck}': sefyi__wsxbg})
    nda__ukm = {}
    exec(jocg__ujjcc, dnxpl__cod, nda__ukm)
    ituu__rkh = nda__ukm['sql_reader_py']
    dawz__rfm = numba.njit(ituu__rkh)
    compiled_funcs.append(dawz__rfm)
    return dawz__rfm


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
parquet_predicate_type = ParquetPredicateType()
pyarrow_table_schema_type = PyArrowTableSchemaType()
_iceberg_read = types.ExternalFunction('iceberg_pq_read', table_type(types.
    voidptr, types.voidptr, types.voidptr, types.boolean,
    parquet_predicate_type, parquet_predicate_type, types.voidptr, types.
    int32, types.voidptr, pyarrow_table_schema_type))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
ll.add_symbol('iceberg_pq_read', arrow_cpp.iceberg_pq_read)
