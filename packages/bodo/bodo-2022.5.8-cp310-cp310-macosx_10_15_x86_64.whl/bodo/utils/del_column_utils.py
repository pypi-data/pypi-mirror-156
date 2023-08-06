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
        yuxw__sxqny = typemap[call_expr.args[1].name].literal_value
        return {yuxw__sxqny}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        evouz__jahtd = dict(call_expr.kws)
        if 'used_cols' in evouz__jahtd:
            gfx__ilphm = evouz__jahtd['used_cols']
            uqg__doyt = typemap[gfx__ilphm.name]
            uqg__doyt = uqg__doyt.instance_type
            return set(uqg__doyt.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        gfx__ilphm = call_expr.args[1]
        uqg__doyt = typemap[gfx__ilphm.name]
        uqg__doyt = uqg__doyt.instance_type
        return set(uqg__doyt.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        rthm__dlyc = call_expr.args[1]
        dwnaa__dor = typemap[rthm__dlyc.name]
        dwnaa__dor = dwnaa__dor.instance_type
        wbgca__pari = dwnaa__dor.meta
        evouz__jahtd = dict(call_expr.kws)
        if 'used_cols' in evouz__jahtd:
            gfx__ilphm = evouz__jahtd['used_cols']
            uqg__doyt = typemap[gfx__ilphm.name]
            uqg__doyt = uqg__doyt.instance_type
            mvdh__egczm = set(uqg__doyt.meta)
            ooxr__jsxca = set()
            for wqiu__pbbg, gdwx__hncbi in enumerate(wbgca__pari):
                if wqiu__pbbg in mvdh__egczm:
                    ooxr__jsxca.add(gdwx__hncbi)
            return ooxr__jsxca
        else:
            return set(wbgca__pari)
    return None
