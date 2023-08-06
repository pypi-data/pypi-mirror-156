"""Helper information to keep table column deletion
pass organized. This contains information about all
table operations for optimizations.
"""
from typing import Dict, Tuple
from numba.core import ir, types
table_usecol_funcs = {('get_table_data', 'bodo.hiframes.table'), (
    'table_filter', 'bodo.hiframes.table'), ('table_subset',
    'bodo.hiframes.table'), ('set_table_data', 'bodo.hiframes.table'), (
    'set_table_data_null', 'bodo.hiframes.table'), (
    'generate_mappable_table_func', 'bodo.utils.table_utils'), (
    'table_astype', 'bodo.utils.table_utils'), ('generate_table_nbytes',
    'bodo.utils.table_utils'), ('table_concat', 'bodo.utils.table_utils')}


def is_table_use_column_ops(fdef: Tuple[str, str]):
    return fdef in table_usecol_funcs


def get_table_used_columns(fdef: Tuple[str, str], call_expr: ir.Expr,
    typemap: Dict[str, types.Type]):
    if fdef == ('get_table_data', 'bodo.hiframes.table'):
        dea__iqni = typemap[call_expr.args[1].name].literal_value
        return {dea__iqni}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        bjzd__ousi = dict(call_expr.kws)
        if 'used_cols' in bjzd__ousi:
            raq__hmqj = bjzd__ousi['used_cols']
            rqamd__fgfhv = typemap[raq__hmqj.name]
            rqamd__fgfhv = rqamd__fgfhv.instance_type
            return set(rqamd__fgfhv.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        raq__hmqj = call_expr.args[1]
        rqamd__fgfhv = typemap[raq__hmqj.name]
        rqamd__fgfhv = rqamd__fgfhv.instance_type
        return set(rqamd__fgfhv.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        lwa__zhp = call_expr.args[1]
        mqqat__wqfg = typemap[lwa__zhp.name]
        mqqat__wqfg = mqqat__wqfg.instance_type
        ytqkb__ylhru = mqqat__wqfg.meta
        bjzd__ousi = dict(call_expr.kws)
        if 'used_cols' in bjzd__ousi:
            raq__hmqj = bjzd__ousi['used_cols']
            rqamd__fgfhv = typemap[raq__hmqj.name]
            rqamd__fgfhv = rqamd__fgfhv.instance_type
            vjfrk__znf = set(rqamd__fgfhv.meta)
            iqpp__pbpl = set()
            for dpac__qgtz, mrgmf__lbz in enumerate(ytqkb__ylhru):
                if dpac__qgtz in vjfrk__znf:
                    iqpp__pbpl.add(mrgmf__lbz)
            return iqpp__pbpl
        else:
            return set(ytqkb__ylhru)
    return None
