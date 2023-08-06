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
    ybmg__lmxlq = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    bskk__vbjbt = []
    for plrrd__iqmf in node.out_vars:
        typ = typemap[plrrd__iqmf.name]
        if typ == types.none:
            continue
        pmia__vsta = array_analysis._gen_shape_call(equiv_set, plrrd__iqmf,
            typ.ndim, None, ybmg__lmxlq)
        equiv_set.insert_equiv(plrrd__iqmf, pmia__vsta)
        bskk__vbjbt.append(pmia__vsta[0])
        equiv_set.define(plrrd__iqmf, set())
    if len(bskk__vbjbt) > 1:
        equiv_set.insert_equiv(*bskk__vbjbt)
    return [], ybmg__lmxlq


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        bsig__szn = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        bsig__szn = Distribution.OneD_Var
    else:
        bsig__szn = Distribution.OneD
    for kbos__pwhx in node.out_vars:
        if kbos__pwhx.name in array_dists:
            bsig__szn = Distribution(min(bsig__szn.value, array_dists[
                kbos__pwhx.name].value))
    for kbos__pwhx in node.out_vars:
        array_dists[kbos__pwhx.name] = bsig__szn


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
    for plrrd__iqmf, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(plrrd__iqmf.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    pkq__zyx = []
    for plrrd__iqmf in node.out_vars:
        ujxx__uyb = visit_vars_inner(plrrd__iqmf, callback, cbdata)
        pkq__zyx.append(ujxx__uyb)
    node.out_vars = pkq__zyx
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for zhziw__pmqt in node.filters:
            for jurs__kqt in range(len(zhziw__pmqt)):
                val = zhziw__pmqt[jurs__kqt]
                zhziw__pmqt[jurs__kqt] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({kbos__pwhx.name for kbos__pwhx in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for rxwz__vpnow in node.filters:
            for kbos__pwhx in rxwz__vpnow:
                if isinstance(kbos__pwhx[2], ir.Var):
                    use_set.add(kbos__pwhx[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    laxx__qfbe = set(kbos__pwhx.name for kbos__pwhx in node.out_vars)
    return set(), laxx__qfbe


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    pkq__zyx = []
    for plrrd__iqmf in node.out_vars:
        ujxx__uyb = replace_vars_inner(plrrd__iqmf, var_dict)
        pkq__zyx.append(ujxx__uyb)
    node.out_vars = pkq__zyx
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for zhziw__pmqt in node.filters:
            for jurs__kqt in range(len(zhziw__pmqt)):
                val = zhziw__pmqt[jurs__kqt]
                zhziw__pmqt[jurs__kqt] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for plrrd__iqmf in node.out_vars:
        hwtyx__ton = definitions[plrrd__iqmf.name]
        if node not in hwtyx__ton:
            hwtyx__ton.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        etr__pkfh = [kbos__pwhx[2] for rxwz__vpnow in filters for
            kbos__pwhx in rxwz__vpnow]
        utrd__nzp = set()
        for pfiu__hcc in etr__pkfh:
            if isinstance(pfiu__hcc, ir.Var):
                if pfiu__hcc.name not in utrd__nzp:
                    filter_vars.append(pfiu__hcc)
                utrd__nzp.add(pfiu__hcc.name)
        return {kbos__pwhx.name: f'f{jurs__kqt}' for jurs__kqt, kbos__pwhx in
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
    return {jurs__kqt for jurs__kqt in used_columns if jurs__kqt < num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    labw__zdfxo = {}
    for jurs__kqt, ynlx__edrkl in enumerate(df_type.data):
        if isinstance(ynlx__edrkl, bodo.IntegerArrayType):
            ihm__czd = ynlx__edrkl.get_pandas_scalar_type_instance
            if ihm__czd not in labw__zdfxo:
                labw__zdfxo[ihm__czd] = []
            labw__zdfxo[ihm__czd].append(df.columns[jurs__kqt])
    for typ, orzb__zmrm in labw__zdfxo.items():
        df[orzb__zmrm] = df[orzb__zmrm].astype(typ)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    szygr__ouzkm = node.out_vars[0].name
    assert isinstance(typemap[szygr__ouzkm], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, hne__rybpd, mad__awl = get_live_column_nums_block(
            column_live_map, equiv_vars, szygr__ouzkm)
        if not (hne__rybpd or mad__awl):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    bwu__xhci = False
    if array_dists is not None:
        jxf__hhos = node.out_vars[0].name
        bwu__xhci = array_dists[jxf__hhos] in (Distribution.OneD,
            Distribution.OneD_Var)
        xjy__matln = node.out_vars[1].name
        assert typemap[xjy__matln
            ] == types.none or not bwu__xhci or array_dists[xjy__matln] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return bwu__xhci


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg']) ->Tuple[str, str]:
    nrx__hwq = 'None'
    padu__wnr = 'None'
    if filters:
        ksplu__bwd = []
        ytskm__qcg = []
        lrfp__cllca = False
        orig_colname_map = {c: jurs__kqt for jurs__kqt, c in enumerate(
            col_names)}
        for zhziw__pmqt in filters:
            cmlog__fnzy = []
            vkaic__vqo = []
            for kbos__pwhx in zhziw__pmqt:
                if isinstance(kbos__pwhx[2], ir.Var):
                    vauzf__kyd, vwk__qlaf = determine_filter_cast(
                        original_out_types, typemap, kbos__pwhx,
                        orig_colname_map, partition_names, source)
                    if kbos__pwhx[1] == 'in':
                        vkaic__vqo.append(
                            f"(ds.field('{kbos__pwhx[0]}').isin({filter_map[kbos__pwhx[2].name]}))"
                            )
                    else:
                        vkaic__vqo.append(
                            f"(ds.field('{kbos__pwhx[0]}'){vauzf__kyd} {kbos__pwhx[1]} ds.scalar({filter_map[kbos__pwhx[2].name]}){vwk__qlaf})"
                            )
                else:
                    assert kbos__pwhx[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if kbos__pwhx[1] == 'is not':
                        ygfo__dwjr = '~'
                    else:
                        ygfo__dwjr = ''
                    vkaic__vqo.append(
                        f"({ygfo__dwjr}ds.field('{kbos__pwhx[0]}').is_null())")
                if not lrfp__cllca:
                    if kbos__pwhx[0] in partition_names and isinstance(
                        kbos__pwhx[2], ir.Var):
                        hruae__bzqxg = (
                            f"('{kbos__pwhx[0]}', '{kbos__pwhx[1]}', {filter_map[kbos__pwhx[2].name]})"
                            )
                        cmlog__fnzy.append(hruae__bzqxg)
                    elif kbos__pwhx[0] in partition_names and not isinstance(
                        kbos__pwhx[2], ir.Var) and source == 'iceberg':
                        hruae__bzqxg = (
                            f"('{kbos__pwhx[0]}', '{kbos__pwhx[1]}', '{kbos__pwhx[2]}')"
                            )
                        cmlog__fnzy.append(hruae__bzqxg)
            twsc__sxuqw = ''
            if cmlog__fnzy:
                twsc__sxuqw = ', '.join(cmlog__fnzy)
            else:
                lrfp__cllca = True
            zlcvs__khx = ' & '.join(vkaic__vqo)
            if twsc__sxuqw:
                ksplu__bwd.append(f'[{twsc__sxuqw}]')
            ytskm__qcg.append(f'({zlcvs__khx})')
        fsnvs__fotso = ', '.join(ksplu__bwd)
        uddok__pmox = ' | '.join(ytskm__qcg)
        if fsnvs__fotso and not lrfp__cllca:
            nrx__hwq = f'[{fsnvs__fotso}]'
        padu__wnr = f'({uddok__pmox})'
    return nrx__hwq, padu__wnr


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    mlhg__vueec = filter_val[0]
    jed__tnrcx = col_types[orig_colname_map[mlhg__vueec]]
    zjhib__wsmao = bodo.utils.typing.element_type(jed__tnrcx)
    if source == 'parquet' and mlhg__vueec in partition_names:
        if zjhib__wsmao == types.unicode_type:
            ddrd__wyu = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(zjhib__wsmao, types.Integer):
            ddrd__wyu = f'.cast(pyarrow.{zjhib__wsmao.name}(), safe=False)'
        else:
            ddrd__wyu = ''
    else:
        ddrd__wyu = ''
    got__vkwzc = typemap[filter_val[2].name]
    if isinstance(got__vkwzc, (types.List, types.Set)):
        two__kvu = got__vkwzc.dtype
    else:
        two__kvu = got__vkwzc
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(zjhib__wsmao,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(two__kvu,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([zjhib__wsmao, two__kvu]):
        if not bodo.utils.typing.is_safe_arrow_cast(zjhib__wsmao, two__kvu):
            raise BodoError(
                f'Unsupported Arrow cast from {zjhib__wsmao} to {two__kvu} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if zjhib__wsmao == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif zjhib__wsmao in (bodo.datetime64ns, bodo.pd_timestamp_type):
            if isinstance(got__vkwzc, (types.List, types.Set)):
                jyud__mgajp = 'list' if isinstance(got__vkwzc, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {jyud__mgajp} values with isin filter pushdown.'
                    )
            return ddrd__wyu, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return ddrd__wyu, ''
