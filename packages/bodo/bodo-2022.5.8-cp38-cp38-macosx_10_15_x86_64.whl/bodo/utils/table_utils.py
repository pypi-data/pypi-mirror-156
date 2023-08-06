"""File containing utility functions for supporting DataFrame operations with Table Format."""
from collections import defaultdict
from typing import Dict, Set
import numba
import numpy as np
from numba.core import types
import bodo
from bodo.hiframes.table import TableType
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_mappable_table_func(table, func_name, out_arr_typ, is_method,
    used_cols=None):
    if not is_overload_constant_str(func_name) and not is_overload_none(
        func_name):
        raise_bodo_error(
            'generate_mappable_table_func(): func_name must be a constant string'
            )
    if not is_overload_constant_bool(is_method):
        raise_bodo_error(
            'generate_mappable_table_func(): is_method must be a constant boolean'
            )
    cnfi__trzen = not is_overload_none(func_name)
    if cnfi__trzen:
        func_name = get_overload_const_str(func_name)
        lzp__jlqb = get_overload_const_bool(is_method)
    xxyag__fovmc = out_arr_typ.instance_type if isinstance(out_arr_typ,
        types.TypeRef) else out_arr_typ
    fwyfu__gtsb = xxyag__fovmc == types.none
    eaizx__lqm = len(table.arr_types)
    if fwyfu__gtsb:
        fvfc__zuddz = table
    else:
        bgosr__izyk = tuple([xxyag__fovmc] * eaizx__lqm)
        fvfc__zuddz = TableType(bgosr__izyk)
    jae__lhjwr = {'bodo': bodo, 'lst_dtype': xxyag__fovmc, 'table_typ':
        fvfc__zuddz}
    jnwhv__gbz = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if fwyfu__gtsb:
        jnwhv__gbz += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        jnwhv__gbz += f'  l = len(table)\n'
    else:
        jnwhv__gbz += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({eaizx__lqm}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        usmt__hcr = used_cols.instance_type
        sqjv__ixu = np.array(usmt__hcr.meta, dtype=np.int64)
        jae__lhjwr['used_cols_glbl'] = sqjv__ixu
        kfz__uzgab = set([table.block_nums[rglhk__ooydu] for rglhk__ooydu in
            sqjv__ixu])
        jnwhv__gbz += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        jnwhv__gbz += f'  used_cols_set = None\n'
        sqjv__ixu = None
    jnwhv__gbz += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for hnb__nsnj in table.type_to_blk.values():
        jnwhv__gbz += f"""  blk_{hnb__nsnj} = bodo.hiframes.table.get_table_block(table, {hnb__nsnj})
"""
        if fwyfu__gtsb:
            jnwhv__gbz += f"""  out_list_{hnb__nsnj} = bodo.hiframes.table.alloc_list_like(blk_{hnb__nsnj}, len(blk_{hnb__nsnj}), False)
"""
            mhj__poanm = f'out_list_{hnb__nsnj}'
        else:
            mhj__poanm = 'out_list'
        if sqjv__ixu is None or hnb__nsnj in kfz__uzgab:
            jnwhv__gbz += f'  for i in range(len(blk_{hnb__nsnj})):\n'
            jae__lhjwr[f'col_indices_{hnb__nsnj}'] = np.array(table.
                block_to_arr_ind[hnb__nsnj], dtype=np.int64)
            jnwhv__gbz += f'    col_loc = col_indices_{hnb__nsnj}[i]\n'
            if sqjv__ixu is not None:
                jnwhv__gbz += f'    if col_loc not in used_cols_set:\n'
                jnwhv__gbz += f'        continue\n'
            if fwyfu__gtsb:
                tnr__keq = 'i'
            else:
                tnr__keq = 'col_loc'
            if not cnfi__trzen:
                jnwhv__gbz += (
                    f'    {mhj__poanm}[{tnr__keq}] = blk_{hnb__nsnj}[i]\n')
            elif lzp__jlqb:
                jnwhv__gbz += (
                    f'    {mhj__poanm}[{tnr__keq}] = blk_{hnb__nsnj}[i].{func_name}()\n'
                    )
            else:
                jnwhv__gbz += (
                    f'    {mhj__poanm}[{tnr__keq}] = {func_name}(blk_{hnb__nsnj}[i])\n'
                    )
        if fwyfu__gtsb:
            jnwhv__gbz += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {mhj__poanm}, {hnb__nsnj})
"""
    if fwyfu__gtsb:
        jnwhv__gbz += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        jnwhv__gbz += '  return out_table\n'
    else:
        jnwhv__gbz += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    vgzdf__dtidy = {}
    exec(jnwhv__gbz, jae__lhjwr, vgzdf__dtidy)
    return vgzdf__dtidy['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    jae__lhjwr = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    jnwhv__gbz = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    jnwhv__gbz += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for hnb__nsnj in table.type_to_blk.values():
        jnwhv__gbz += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {hnb__nsnj})\n'
            )
        jae__lhjwr[f'col_indices_{hnb__nsnj}'] = np.array(table.
            block_to_arr_ind[hnb__nsnj], dtype=np.int64)
        jnwhv__gbz += '  for i in range(len(blk)):\n'
        jnwhv__gbz += f'    col_loc = col_indices_{hnb__nsnj}[i]\n'
        jnwhv__gbz += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    jnwhv__gbz += '  if parallel:\n'
    jnwhv__gbz += '    for i in range(start_offset, len(out_arr)):\n'
    jnwhv__gbz += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    vgzdf__dtidy = {}
    exec(jnwhv__gbz, jae__lhjwr, vgzdf__dtidy)
    return vgzdf__dtidy['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    oehzu__qnpxe = table.type_to_blk[arr_type]
    jae__lhjwr = {'bodo': bodo}
    jae__lhjwr['col_indices'] = np.array(table.block_to_arr_ind[
        oehzu__qnpxe], dtype=np.int64)
    mvjqp__hrwam = col_nums_meta.instance_type
    jae__lhjwr['col_nums'] = np.array(mvjqp__hrwam.meta, np.int64)
    jnwhv__gbz = 'def impl(table, col_nums_meta, arr_type):\n'
    jnwhv__gbz += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {oehzu__qnpxe})\n'
        )
    jnwhv__gbz += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    jnwhv__gbz += '  n = len(table)\n'
    emel__awgns = bodo.utils.typing.is_str_arr_type(arr_type)
    if emel__awgns:
        jnwhv__gbz += '  total_chars = 0\n'
        jnwhv__gbz += '  for c in col_nums:\n'
        jnwhv__gbz += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        jnwhv__gbz += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        jnwhv__gbz += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        jnwhv__gbz += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        jnwhv__gbz += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    jnwhv__gbz += '  for i in range(len(col_nums)):\n'
    jnwhv__gbz += '    c = col_nums[i]\n'
    if not emel__awgns:
        jnwhv__gbz += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    jnwhv__gbz += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    jnwhv__gbz += '    off = i * n\n'
    jnwhv__gbz += '    for j in range(len(arr)):\n'
    jnwhv__gbz += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    jnwhv__gbz += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    jnwhv__gbz += '      else:\n'
    jnwhv__gbz += '        out_arr[off+j] = arr[j]\n'
    jnwhv__gbz += '  return out_arr\n'
    kxi__pgbkv = {}
    exec(jnwhv__gbz, jae__lhjwr, kxi__pgbkv)
    qmcyh__koc = kxi__pgbkv['impl']
    return qmcyh__koc


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    wkn__scb = not is_overload_false(copy)
    iqdyg__tui = is_overload_true(copy)
    jae__lhjwr = {'bodo': bodo}
    rqi__qgd = table.arr_types
    tqbsd__nnsfw = new_table_typ.arr_types
    qfjdo__gxrq: Set[int] = set()
    fwa__bxva: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    xtzpg__ryotf: Set[types.Type] = set()
    for rglhk__ooydu, svwst__njd in enumerate(rqi__qgd):
        ztaw__edlz = tqbsd__nnsfw[rglhk__ooydu]
        if svwst__njd == ztaw__edlz:
            xtzpg__ryotf.add(svwst__njd)
        else:
            qfjdo__gxrq.add(rglhk__ooydu)
            fwa__bxva[ztaw__edlz].add(svwst__njd)
    jnwhv__gbz = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    jnwhv__gbz += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    jnwhv__gbz += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    hnj__acx = set(range(len(rqi__qgd)))
    rqyg__bgij = hnj__acx - qfjdo__gxrq
    if not is_overload_none(used_cols):
        usmt__hcr = used_cols.instance_type
        ohwat__lqk = set(usmt__hcr.meta)
        qfjdo__gxrq = qfjdo__gxrq & ohwat__lqk
        rqyg__bgij = rqyg__bgij & ohwat__lqk
        kfz__uzgab = set([table.block_nums[rglhk__ooydu] for rglhk__ooydu in
            ohwat__lqk])
    else:
        ohwat__lqk = None
    jae__lhjwr['cast_cols'] = np.array(list(qfjdo__gxrq), dtype=np.int64)
    jae__lhjwr['copied_cols'] = np.array(list(rqyg__bgij), dtype=np.int64)
    jnwhv__gbz += f'  copied_cols_set = set(copied_cols)\n'
    jnwhv__gbz += f'  cast_cols_set = set(cast_cols)\n'
    for zbt__bcui, hnb__nsnj in new_table_typ.type_to_blk.items():
        jae__lhjwr[f'typ_list_{hnb__nsnj}'] = types.List(zbt__bcui)
        jnwhv__gbz += f"""  out_arr_list_{hnb__nsnj} = bodo.hiframes.table.alloc_list_like(typ_list_{hnb__nsnj}, {len(new_table_typ.block_to_arr_ind[hnb__nsnj])}, False)
"""
        if zbt__bcui in xtzpg__ryotf:
            komy__oiob = table.type_to_blk[zbt__bcui]
            if ohwat__lqk is None or komy__oiob in kfz__uzgab:
                dzr__wwfg = table.block_to_arr_ind[komy__oiob]
                mnnnh__pst = [new_table_typ.block_offsets[tgo__bxtfc] for
                    tgo__bxtfc in dzr__wwfg]
                jae__lhjwr[f'new_idx_{komy__oiob}'] = np.array(mnnnh__pst,
                    np.int64)
                jae__lhjwr[f'orig_arr_inds_{komy__oiob}'] = np.array(dzr__wwfg,
                    np.int64)
                jnwhv__gbz += f"""  arr_list_{komy__oiob} = bodo.hiframes.table.get_table_block(table, {komy__oiob})
"""
                jnwhv__gbz += (
                    f'  for i in range(len(arr_list_{komy__oiob})):\n')
                jnwhv__gbz += (
                    f'    arr_ind_{komy__oiob} = orig_arr_inds_{komy__oiob}[i]\n'
                    )
                jnwhv__gbz += (
                    f'    if arr_ind_{komy__oiob} not in copied_cols_set:\n')
                jnwhv__gbz += f'      continue\n'
                jnwhv__gbz += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{komy__oiob}, i, arr_ind_{komy__oiob})
"""
                jnwhv__gbz += (
                    f'    out_idx_{hnb__nsnj}_{komy__oiob} = new_idx_{komy__oiob}[i]\n'
                    )
                jnwhv__gbz += (
                    f'    arr_val_{komy__oiob} = arr_list_{komy__oiob}[i]\n')
                if iqdyg__tui:
                    jnwhv__gbz += (
                        f'    arr_val_{komy__oiob} = arr_val_{komy__oiob}.copy()\n'
                        )
                elif wkn__scb:
                    jnwhv__gbz += f"""    arr_val_{komy__oiob} = arr_val_{komy__oiob}.copy() if copy else arr_val_{hnb__nsnj}
"""
                jnwhv__gbz += f"""    out_arr_list_{hnb__nsnj}[out_idx_{hnb__nsnj}_{komy__oiob}] = arr_val_{komy__oiob}
"""
    gckwo__hkyn = set()
    for zbt__bcui, hnb__nsnj in new_table_typ.type_to_blk.items():
        if zbt__bcui in fwa__bxva:
            if isinstance(zbt__bcui, bodo.IntegerArrayType):
                gcllz__eox = zbt__bcui.get_pandas_scalar_type_instance.name
            else:
                gcllz__eox = zbt__bcui.dtype
            jae__lhjwr[f'typ_{hnb__nsnj}'] = gcllz__eox
            kzgb__yfqvs = fwa__bxva[zbt__bcui]
            for addl__qyoph in kzgb__yfqvs:
                komy__oiob = table.type_to_blk[addl__qyoph]
                if ohwat__lqk is None or komy__oiob in kfz__uzgab:
                    if (addl__qyoph not in xtzpg__ryotf and addl__qyoph not in
                        gckwo__hkyn):
                        dzr__wwfg = table.block_to_arr_ind[komy__oiob]
                        mnnnh__pst = [new_table_typ.block_offsets[
                            tgo__bxtfc] for tgo__bxtfc in dzr__wwfg]
                        jae__lhjwr[f'new_idx_{komy__oiob}'] = np.array(
                            mnnnh__pst, np.int64)
                        jae__lhjwr[f'orig_arr_inds_{komy__oiob}'] = np.array(
                            dzr__wwfg, np.int64)
                        jnwhv__gbz += f"""  arr_list_{komy__oiob} = bodo.hiframes.table.get_table_block(table, {komy__oiob})
"""
                    gckwo__hkyn.add(addl__qyoph)
                    jnwhv__gbz += (
                        f'  for i in range(len(arr_list_{komy__oiob})):\n')
                    jnwhv__gbz += (
                        f'    arr_ind_{komy__oiob} = orig_arr_inds_{komy__oiob}[i]\n'
                        )
                    jnwhv__gbz += (
                        f'    if arr_ind_{komy__oiob} not in cast_cols_set:\n')
                    jnwhv__gbz += f'      continue\n'
                    jnwhv__gbz += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{komy__oiob}, i, arr_ind_{komy__oiob})
"""
                    jnwhv__gbz += f"""    out_idx_{hnb__nsnj}_{komy__oiob} = new_idx_{komy__oiob}[i]
"""
                    jnwhv__gbz += f"""    arr_val_{hnb__nsnj} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{komy__oiob}[i], typ_{hnb__nsnj}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    jnwhv__gbz += f"""    out_arr_list_{hnb__nsnj}[out_idx_{hnb__nsnj}_{komy__oiob}] = arr_val_{hnb__nsnj}
"""
        jnwhv__gbz += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{hnb__nsnj}, {hnb__nsnj})
"""
    jnwhv__gbz += '  return out_table\n'
    vgzdf__dtidy = {}
    exec(jnwhv__gbz, jae__lhjwr, vgzdf__dtidy)
    return vgzdf__dtidy['impl']
