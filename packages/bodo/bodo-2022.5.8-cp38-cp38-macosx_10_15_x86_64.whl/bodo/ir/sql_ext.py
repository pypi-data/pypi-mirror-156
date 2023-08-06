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
    jior__suy = urlparse(con_str)
    db_type = jior__suy.scheme
    pfe__gcxf = jior__suy.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', pfe__gcxf
    if db_type == 'mysql+pymysql':
        return 'mysql', pfe__gcxf
    return db_type, pfe__gcxf


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    bxwim__xcw = sql_node.out_vars[0].name
    fauf__jgy = sql_node.out_vars[1].name
    if bxwim__xcw not in lives and fauf__jgy not in lives:
        return None
    elif bxwim__xcw not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif fauf__jgy not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        hnzsi__exx = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        wam__dqtj = []
        rvvfc__wdj = []
        for zwzr__hnrcl in sql_node.out_used_cols:
            kcno__snlmz = sql_node.df_colnames[zwzr__hnrcl]
            wam__dqtj.append(kcno__snlmz)
            if isinstance(sql_node.out_types[zwzr__hnrcl], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                rvvfc__wdj.append(kcno__snlmz)
        if sql_node.index_column_name:
            wam__dqtj.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                rvvfc__wdj.append(sql_node.index_column_name)
        wnzdp__pmgs = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', hnzsi__exx,
            wnzdp__pmgs, wam__dqtj)
        if rvvfc__wdj:
            nes__uiyq = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', nes__uiyq,
                wnzdp__pmgs, rvvfc__wdj)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        dpqo__hpkqy = set(sql_node.unsupported_columns)
        ziwj__weij = set(sql_node.out_used_cols)
        kncjx__qxbz = ziwj__weij & dpqo__hpkqy
        if kncjx__qxbz:
            pai__qiwo = sorted(kncjx__qxbz)
            mgg__fsjzu = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            emui__qkf = 0
            for fdpu__etoyy in pai__qiwo:
                while sql_node.unsupported_columns[emui__qkf] != fdpu__etoyy:
                    emui__qkf += 1
                mgg__fsjzu.append(
                    f"Column '{sql_node.original_df_colnames[fdpu__etoyy]}' with unsupported arrow type {sql_node.unsupported_arrow_types[emui__qkf]}"
                    )
                emui__qkf += 1
            mdslb__geyi = '\n'.join(mgg__fsjzu)
            raise BodoError(mdslb__geyi, loc=sql_node.loc)
    tvolh__rlwp, iro__lxsml = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    xisx__htcu = ', '.join(tvolh__rlwp.values())
    frrk__fzybc = (
        f'def sql_impl(sql_request, conn, database_schema, {xisx__htcu}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        xhw__iirg = []
        for nnj__repz in sql_node.filters:
            yoowk__flm = [' '.join(['(', ato__ibxm[0], ato__ibxm[1], '{' +
                tvolh__rlwp[ato__ibxm[2].name] + '}' if isinstance(
                ato__ibxm[2], ir.Var) else ato__ibxm[2], ')']) for
                ato__ibxm in nnj__repz]
            xhw__iirg.append(' ( ' + ' AND '.join(yoowk__flm) + ' ) ')
        ybr__lqghc = ' WHERE ' + ' OR '.join(xhw__iirg)
        for zwzr__hnrcl, soaug__pawym in enumerate(tvolh__rlwp.values()):
            frrk__fzybc += (
                f'    {soaug__pawym} = get_sql_literal({soaug__pawym})\n')
        frrk__fzybc += f'    sql_request = f"{{sql_request}} {ybr__lqghc}"\n'
    xuftd__gsq = ''
    if sql_node.db_type == 'iceberg':
        xuftd__gsq = xisx__htcu
    frrk__fzybc += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {xuftd__gsq})
"""
    fvv__zqbdv = {}
    exec(frrk__fzybc, {}, fvv__zqbdv)
    tvz__bbvfn = fvv__zqbdv['sql_impl']
    qgaam__qkv = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        sql_node.limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    vxbtr__ljr = (types.none if sql_node.database_schema is None else
        string_type)
    gtj__upzo = compile_to_numba_ir(tvz__bbvfn, {'_sql_reader_py':
        qgaam__qkv, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, vxbtr__ljr
        ) + tuple(typemap[qmswm__yez.name] for qmswm__yez in iro__lxsml),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        jwlc__zmal = [sql_node.df_colnames[zwzr__hnrcl] for zwzr__hnrcl in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            jwlc__zmal.append(sql_node.index_column_name)
        punwr__zxts = escape_column_names(jwlc__zmal, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            mgi__xecfo = ('SELECT ' + punwr__zxts + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            mgi__xecfo = ('SELECT ' + punwr__zxts + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        mgi__xecfo = sql_node.sql_request
    replace_arg_nodes(gtj__upzo, [ir.Const(mgi__xecfo, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + iro__lxsml)
    iyg__tdei = gtj__upzo.body[:-3]
    iyg__tdei[-2].target = sql_node.out_vars[0]
    iyg__tdei[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        iyg__tdei.pop(-1)
    elif not sql_node.out_used_cols:
        iyg__tdei.pop(-2)
    return iyg__tdei


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        jwlc__zmal = [(dhcoj__dfo.upper() if dhcoj__dfo in
            converted_colnames else dhcoj__dfo) for dhcoj__dfo in col_names]
        punwr__zxts = ', '.join([f'"{dhcoj__dfo}"' for dhcoj__dfo in
            jwlc__zmal])
    elif db_type == 'mysql':
        punwr__zxts = ', '.join([f'`{dhcoj__dfo}`' for dhcoj__dfo in col_names]
            )
    else:
        punwr__zxts = ', '.join([f'"{dhcoj__dfo}"' for dhcoj__dfo in col_names]
            )
    return punwr__zxts


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    zzbd__vzfym = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(zzbd__vzfym,
        'Filter pushdown')
    if zzbd__vzfym == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(zzbd__vzfym, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif zzbd__vzfym == bodo.pd_timestamp_type:

        def impl(filter_value):
            nmpa__gectc = filter_value.nanosecond
            fifo__jmj = ''
            if nmpa__gectc < 10:
                fifo__jmj = '00'
            elif nmpa__gectc < 100:
                fifo__jmj = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{fifo__jmj}{nmpa__gectc}'"
                )
        return impl
    elif zzbd__vzfym == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {zzbd__vzfym} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    oouv__imc = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    zzbd__vzfym = types.unliteral(filter_value)
    if isinstance(zzbd__vzfym, types.List) and (isinstance(zzbd__vzfym.
        dtype, scalar_isinstance) or zzbd__vzfym.dtype in oouv__imc):

        def impl(filter_value):
            pmdxp__rqp = ', '.join([_get_snowflake_sql_literal_scalar(
                dhcoj__dfo) for dhcoj__dfo in filter_value])
            return f'({pmdxp__rqp})'
        return impl
    elif isinstance(zzbd__vzfym, scalar_isinstance
        ) or zzbd__vzfym in oouv__imc:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {zzbd__vzfym} used in filter pushdown.'
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
    except ImportError as vcx__ajqg:
        nvn__wcp = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(nvn__wcp)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as vcx__ajqg:
        nvn__wcp = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(nvn__wcp)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as vcx__ajqg:
        nvn__wcp = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(nvn__wcp)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as vcx__ajqg:
        nvn__wcp = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(nvn__wcp)


def req_limit(sql_request):
    import re
    szt__xwac = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    dak__hsfvg = szt__xwac.search(sql_request)
    if dak__hsfvg:
        return int(dak__hsfvg.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    jpb__vhwr = next_label()
    jwlc__zmal = [col_names[zwzr__hnrcl] for zwzr__hnrcl in out_used_cols]
    vbpzc__vjjgt = [col_typs[zwzr__hnrcl] for zwzr__hnrcl in out_used_cols]
    if index_column_name:
        jwlc__zmal.append(index_column_name)
        vbpzc__vjjgt.append(index_column_type)
    fdks__bhvwh = None
    zxmdf__snkf = None
    nvwu__gop = TableType(tuple(col_typs)) if out_used_cols else types.none
    xuftd__gsq = ''
    tvolh__rlwp = {}
    iro__lxsml = []
    if filters and db_type == 'iceberg':
        tvolh__rlwp, iro__lxsml = bodo.ir.connector.generate_filter_map(filters
            )
        xuftd__gsq = ', '.join(tvolh__rlwp.values())
    frrk__fzybc = (
        f'def sql_reader_py(sql_request, conn, database_schema, {xuftd__gsq}):\n'
        )
    if db_type == 'iceberg':
        qyyp__davui, bvq__mqlrl = bodo.ir.connector.generate_arrow_filters(
            filters, tvolh__rlwp, iro__lxsml, col_names, col_names,
            col_typs, typemap, 'iceberg')
        eyf__etioq: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[zwzr__hnrcl]) for zwzr__hnrcl in out_used_cols]
        lhbf__qjj = {vic__uwdvh: zwzr__hnrcl for zwzr__hnrcl, vic__uwdvh in
            enumerate(eyf__etioq)}
        gbiug__yem = [int(is_nullable(col_typs[zwzr__hnrcl])) for
            zwzr__hnrcl in eyf__etioq]
        hyvb__jzen = ',' if xuftd__gsq else ''
        frrk__fzybc += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        frrk__fzybc += f"""  dnf_filters, expr_filters = get_filters_pyobject("{qyyp__davui}", "{bvq__mqlrl}", ({xuftd__gsq}{hyvb__jzen}))
"""
        frrk__fzybc += f'  out_table = iceberg_read(\n'
        frrk__fzybc += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        frrk__fzybc += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        frrk__fzybc += (
            f'    expr_filters, selected_cols_arr_{jpb__vhwr}.ctypes,\n')
        frrk__fzybc += (
            f'    {len(eyf__etioq)}, nullable_cols_arr_{jpb__vhwr}.ctypes,\n')
        frrk__fzybc += f'    pyarrow_table_schema_{jpb__vhwr},\n'
        frrk__fzybc += f'  )\n'
        frrk__fzybc += f'  check_and_propagate_cpp_exception()\n'
        yasxn__hmcqi = not out_used_cols
        nvwu__gop = TableType(tuple(col_typs))
        if yasxn__hmcqi:
            nvwu__gop = types.none
        fauf__jgy = 'None'
        if index_column_name is not None:
            spd__hdgm = len(out_used_cols) + 1 if not yasxn__hmcqi else 0
            fauf__jgy = (
                f'info_to_array(info_from_table(out_table, {spd__hdgm}), index_col_typ)'
                )
        frrk__fzybc += f'  index_var = {fauf__jgy}\n'
        fdks__bhvwh = None
        if not yasxn__hmcqi:
            fdks__bhvwh = []
            jnki__hty = 0
            for zwzr__hnrcl in range(len(col_names)):
                if jnki__hty < len(out_used_cols
                    ) and zwzr__hnrcl == out_used_cols[jnki__hty]:
                    fdks__bhvwh.append(lhbf__qjj[zwzr__hnrcl])
                    jnki__hty += 1
                else:
                    fdks__bhvwh.append(-1)
            fdks__bhvwh = np.array(fdks__bhvwh, dtype=np.int64)
        if yasxn__hmcqi:
            frrk__fzybc += '  table_var = None\n'
        else:
            frrk__fzybc += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{jpb__vhwr}, py_table_type_{jpb__vhwr})
"""
        frrk__fzybc += f'  delete_table(out_table)\n'
        frrk__fzybc += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        frrk__fzybc += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        gbiug__yem = [int(is_nullable(col_typs[zwzr__hnrcl])) for
            zwzr__hnrcl in out_used_cols]
        if index_column_name:
            gbiug__yem.append(int(is_nullable(index_column_type)))
        frrk__fzybc += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(gbiug__yem)}, np.array({gbiug__yem}, dtype=np.int32).ctypes)
"""
        frrk__fzybc += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            frrk__fzybc += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            frrk__fzybc += '  index_var = None\n'
        if out_used_cols:
            emui__qkf = []
            jnki__hty = 0
            for zwzr__hnrcl in range(len(col_names)):
                if jnki__hty < len(out_used_cols
                    ) and zwzr__hnrcl == out_used_cols[jnki__hty]:
                    emui__qkf.append(jnki__hty)
                    jnki__hty += 1
                else:
                    emui__qkf.append(-1)
            fdks__bhvwh = np.array(emui__qkf, dtype=np.int64)
            frrk__fzybc += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{jpb__vhwr}, py_table_type_{jpb__vhwr})
"""
        else:
            frrk__fzybc += '  table_var = None\n'
        frrk__fzybc += '  delete_table(out_table)\n'
        frrk__fzybc += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            frrk__fzybc += f"""  type_usecols_offsets_arr_{jpb__vhwr}_2 = type_usecols_offsets_arr_{jpb__vhwr}
"""
            zxmdf__snkf = np.array(out_used_cols, dtype=np.int64)
        frrk__fzybc += '  df_typeref_2 = df_typeref\n'
        frrk__fzybc += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            frrk__fzybc += '  pymysql_check()\n'
        elif db_type == 'oracle':
            frrk__fzybc += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            frrk__fzybc += '  psycopg2_check()\n'
        if parallel:
            frrk__fzybc += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                frrk__fzybc += f'  nb_row = {limit}\n'
            else:
                frrk__fzybc += '  with objmode(nb_row="int64"):\n'
                frrk__fzybc += f'     if rank == {MPI_ROOT}:\n'
                frrk__fzybc += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                frrk__fzybc += '         frame = pd.read_sql(sql_cons, conn)\n'
                frrk__fzybc += '         nb_row = frame.iat[0,0]\n'
                frrk__fzybc += '     else:\n'
                frrk__fzybc += '         nb_row = 0\n'
                frrk__fzybc += '  nb_row = bcast_scalar(nb_row)\n'
            frrk__fzybc += f"""  with objmode(table_var=py_table_type_{jpb__vhwr}, index_var=index_col_typ):
"""
            frrk__fzybc += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                frrk__fzybc += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                frrk__fzybc += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            frrk__fzybc += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            frrk__fzybc += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            frrk__fzybc += f"""  with objmode(table_var=py_table_type_{jpb__vhwr}, index_var=index_col_typ):
"""
            frrk__fzybc += '    df_ret = pd.read_sql(sql_request, conn)\n'
            frrk__fzybc += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            frrk__fzybc += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            frrk__fzybc += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            frrk__fzybc += '    index_var = None\n'
        if out_used_cols:
            frrk__fzybc += f'    arrs = []\n'
            frrk__fzybc += f'    for i in range(df_ret.shape[1]):\n'
            frrk__fzybc += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            frrk__fzybc += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{jpb__vhwr}_2, {len(col_names)})
"""
        else:
            frrk__fzybc += '    table_var = None\n'
    frrk__fzybc += '  return (table_var, index_var)\n'
    izgvs__zdqr = globals()
    izgvs__zdqr.update({'bodo': bodo, f'py_table_type_{jpb__vhwr}':
        nvwu__gop, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        izgvs__zdqr.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{jpb__vhwr}': fdks__bhvwh})
    if db_type == 'iceberg':
        izgvs__zdqr.update({f'selected_cols_arr_{jpb__vhwr}': np.array(
            eyf__etioq, np.int32), f'nullable_cols_arr_{jpb__vhwr}': np.
            array(gbiug__yem, np.int32), f'py_table_type_{jpb__vhwr}':
            nvwu__gop, f'pyarrow_table_schema_{jpb__vhwr}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        izgvs__zdqr.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        izgvs__zdqr.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(vbpzc__vjjgt), bodo.RangeIndexType(
            None), tuple(jwlc__zmal)), 'Table': Table,
            f'type_usecols_offsets_arr_{jpb__vhwr}': zxmdf__snkf})
    fvv__zqbdv = {}
    exec(frrk__fzybc, izgvs__zdqr, fvv__zqbdv)
    qgaam__qkv = fvv__zqbdv['sql_reader_py']
    ofm__nkfox = numba.njit(qgaam__qkv)
    compiled_funcs.append(ofm__nkfox)
    return ofm__nkfox


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
