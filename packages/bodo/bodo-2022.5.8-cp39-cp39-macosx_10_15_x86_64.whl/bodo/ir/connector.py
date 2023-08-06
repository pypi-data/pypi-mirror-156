"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
from collections import defaultdict
from typing import Literal, Set, Tuple
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from numba.extending import box, models, register_model
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import get_live_column_nums_block
from bodo.utils.typing import BodoError
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    nesi__qit = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    igu__ectpy = []
    for depvc__ealbn in node.out_vars:
        typ = typemap[depvc__ealbn.name]
        if typ == types.none:
            continue
        afks__zdw = array_analysis._gen_shape_call(equiv_set, depvc__ealbn,
            typ.ndim, None, nesi__qit)
        equiv_set.insert_equiv(depvc__ealbn, afks__zdw)
        igu__ectpy.append(afks__zdw[0])
        equiv_set.define(depvc__ealbn, set())
    if len(igu__ectpy) > 1:
        equiv_set.insert_equiv(*igu__ectpy)
    return [], nesi__qit


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        rwau__hjzqv = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        rwau__hjzqv = Distribution.OneD_Var
    else:
        rwau__hjzqv = Distribution.OneD
    for yoxw__ywi in node.out_vars:
        if yoxw__ywi.name in array_dists:
            rwau__hjzqv = Distribution(min(rwau__hjzqv.value, array_dists[
                yoxw__ywi.name].value))
    for yoxw__ywi in node.out_vars:
        array_dists[yoxw__ywi.name] = rwau__hjzqv


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ in ('parquet', 'sql'):
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for depvc__ealbn, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(depvc__ealbn.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    buh__imiy = []
    for depvc__ealbn in node.out_vars:
        wfout__zlozn = visit_vars_inner(depvc__ealbn, callback, cbdata)
        buh__imiy.append(wfout__zlozn)
    node.out_vars = buh__imiy
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for rdcuo__ztyh in node.filters:
            for awzd__nmcc in range(len(rdcuo__ztyh)):
                val = rdcuo__ztyh[awzd__nmcc]
                rdcuo__ztyh[awzd__nmcc] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({yoxw__ywi.name for yoxw__ywi in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for fskh__fitrl in node.filters:
            for yoxw__ywi in fskh__fitrl:
                if isinstance(yoxw__ywi[2], ir.Var):
                    use_set.add(yoxw__ywi[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    japnv__kgqv = set(yoxw__ywi.name for yoxw__ywi in node.out_vars)
    return set(), japnv__kgqv


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    buh__imiy = []
    for depvc__ealbn in node.out_vars:
        wfout__zlozn = replace_vars_inner(depvc__ealbn, var_dict)
        buh__imiy.append(wfout__zlozn)
    node.out_vars = buh__imiy
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for rdcuo__ztyh in node.filters:
            for awzd__nmcc in range(len(rdcuo__ztyh)):
                val = rdcuo__ztyh[awzd__nmcc]
                rdcuo__ztyh[awzd__nmcc] = val[0], val[1], replace_vars_inner(
                    val[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for depvc__ealbn in node.out_vars:
        fqd__waebi = definitions[depvc__ealbn.name]
        if node not in fqd__waebi:
            fqd__waebi.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        del__vzn = [yoxw__ywi[2] for fskh__fitrl in filters for yoxw__ywi in
            fskh__fitrl]
        lgq__ovm = set()
        for blc__bwbs in del__vzn:
            if isinstance(blc__bwbs, ir.Var):
                if blc__bwbs.name not in lgq__ovm:
                    filter_vars.append(blc__bwbs)
                lgq__ovm.add(blc__bwbs.name)
        return {yoxw__ywi.name: f'f{awzd__nmcc}' for awzd__nmcc, yoxw__ywi in
            enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


class StreamReaderType(types.Opaque):

    def __init__(self):
        super(StreamReaderType, self).__init__(name='StreamReaderType')


stream_reader_type = StreamReaderType()
register_model(StreamReaderType)(models.OpaqueModel)


@box(StreamReaderType)
def box_stream_reader(typ, val, c):
    c.pyapi.incref(val)
    return val


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {awzd__nmcc for awzd__nmcc in used_columns if awzd__nmcc <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    ieudg__flq = {}
    for awzd__nmcc, rhcge__ruce in enumerate(df_type.data):
        if isinstance(rhcge__ruce, bodo.IntegerArrayType):
            txmos__own = rhcge__ruce.get_pandas_scalar_type_instance
            if txmos__own not in ieudg__flq:
                ieudg__flq[txmos__own] = []
            ieudg__flq[txmos__own].append(df.columns[awzd__nmcc])
    for typ, npozm__zlv in ieudg__flq.items():
        df[npozm__zlv] = df[npozm__zlv].astype(typ)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    krxeo__gsff = node.out_vars[0].name
    assert isinstance(typemap[krxeo__gsff], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, dhvom__eyjoy, ljjoo__imlv = get_live_column_nums_block(
            column_live_map, equiv_vars, krxeo__gsff)
        if not (dhvom__eyjoy or ljjoo__imlv):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    htpn__fcbz = False
    if array_dists is not None:
        tcwvq__rez = node.out_vars[0].name
        htpn__fcbz = array_dists[tcwvq__rez] in (Distribution.OneD,
            Distribution.OneD_Var)
        kvnyp__gljcf = node.out_vars[1].name
        assert typemap[kvnyp__gljcf
            ] == types.none or not htpn__fcbz or array_dists[kvnyp__gljcf] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return htpn__fcbz


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg']) ->Tuple[str, str]:
    wgthv__doru = 'None'
    scvf__jkecq = 'None'
    if filters:
        nejhe__kko = []
        zedzl__nai = []
        zzwav__uyw = False
        orig_colname_map = {c: awzd__nmcc for awzd__nmcc, c in enumerate(
            col_names)}
        for rdcuo__ztyh in filters:
            lxwcn__pdnk = []
            oxq__vwx = []
            for yoxw__ywi in rdcuo__ztyh:
                if isinstance(yoxw__ywi[2], ir.Var):
                    xhx__tnaps, tuu__bfr = determine_filter_cast(
                        original_out_types, typemap, yoxw__ywi,
                        orig_colname_map, partition_names, source)
                    if yoxw__ywi[1] == 'in':
                        oxq__vwx.append(
                            f"(ds.field('{yoxw__ywi[0]}').isin({filter_map[yoxw__ywi[2].name]}))"
                            )
                    else:
                        oxq__vwx.append(
                            f"(ds.field('{yoxw__ywi[0]}'){xhx__tnaps} {yoxw__ywi[1]} ds.scalar({filter_map[yoxw__ywi[2].name]}){tuu__bfr})"
                            )
                else:
                    assert yoxw__ywi[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if yoxw__ywi[1] == 'is not':
                        mof__vcku = '~'
                    else:
                        mof__vcku = ''
                    oxq__vwx.append(
                        f"({mof__vcku}ds.field('{yoxw__ywi[0]}').is_null())")
                if not zzwav__uyw:
                    if yoxw__ywi[0] in partition_names and isinstance(yoxw__ywi
                        [2], ir.Var):
                        tlia__ytf = (
                            f"('{yoxw__ywi[0]}', '{yoxw__ywi[1]}', {filter_map[yoxw__ywi[2].name]})"
                            )
                        lxwcn__pdnk.append(tlia__ytf)
                    elif yoxw__ywi[0] in partition_names and not isinstance(
                        yoxw__ywi[2], ir.Var) and source == 'iceberg':
                        tlia__ytf = (
                            f"('{yoxw__ywi[0]}', '{yoxw__ywi[1]}', '{yoxw__ywi[2]}')"
                            )
                        lxwcn__pdnk.append(tlia__ytf)
            fekbu__byvc = ''
            if lxwcn__pdnk:
                fekbu__byvc = ', '.join(lxwcn__pdnk)
            else:
                zzwav__uyw = True
            rlfx__zjkha = ' & '.join(oxq__vwx)
            if fekbu__byvc:
                nejhe__kko.append(f'[{fekbu__byvc}]')
            zedzl__nai.append(f'({rlfx__zjkha})')
        lvty__kelm = ', '.join(nejhe__kko)
        obtkh__ylfy = ' | '.join(zedzl__nai)
        if lvty__kelm and not zzwav__uyw:
            wgthv__doru = f'[{lvty__kelm}]'
        scvf__jkecq = f'({obtkh__ylfy})'
    return wgthv__doru, scvf__jkecq


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    hlm__plm = filter_val[0]
    alxwg__uyb = col_types[orig_colname_map[hlm__plm]]
    wxikl__gqdt = bodo.utils.typing.element_type(alxwg__uyb)
    if source == 'parquet' and hlm__plm in partition_names:
        if wxikl__gqdt == types.unicode_type:
            kxzvf__pqbkj = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(wxikl__gqdt, types.Integer):
            kxzvf__pqbkj = f'.cast(pyarrow.{wxikl__gqdt.name}(), safe=False)'
        else:
            kxzvf__pqbkj = ''
    else:
        kxzvf__pqbkj = ''
    rpso__zdjym = typemap[filter_val[2].name]
    if isinstance(rpso__zdjym, (types.List, types.Set)):
        duv__umfmp = rpso__zdjym.dtype
    else:
        duv__umfmp = rpso__zdjym
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(wxikl__gqdt,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(duv__umfmp,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([wxikl__gqdt, duv__umfmp]):
        if not bodo.utils.typing.is_safe_arrow_cast(wxikl__gqdt, duv__umfmp):
            raise BodoError(
                f'Unsupported Arrow cast from {wxikl__gqdt} to {duv__umfmp} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if wxikl__gqdt == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif wxikl__gqdt in (bodo.datetime64ns, bodo.pd_timestamp_type):
            if isinstance(rpso__zdjym, (types.List, types.Set)):
                yeavc__ruba = 'list' if isinstance(rpso__zdjym, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {yeavc__ruba} values with isin filter pushdown.'
                    )
            return kxzvf__pqbkj, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return kxzvf__pqbkj, ''
