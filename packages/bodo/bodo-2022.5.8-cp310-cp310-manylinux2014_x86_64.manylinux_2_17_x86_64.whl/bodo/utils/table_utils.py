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
    naxw__efg = not is_overload_none(func_name)
    if naxw__efg:
        func_name = get_overload_const_str(func_name)
        ilf__juf = get_overload_const_bool(is_method)
    wanhz__bxp = out_arr_typ.instance_type if isinstance(out_arr_typ, types
        .TypeRef) else out_arr_typ
    xedf__nvy = wanhz__bxp == types.none
    atph__jjrvs = len(table.arr_types)
    if xedf__nvy:
        osk__inc = table
    else:
        yks__jlo = tuple([wanhz__bxp] * atph__jjrvs)
        osk__inc = TableType(yks__jlo)
    zjtg__stnl = {'bodo': bodo, 'lst_dtype': wanhz__bxp, 'table_typ': osk__inc}
    evh__ydg = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if xedf__nvy:
        evh__ydg += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        evh__ydg += f'  l = len(table)\n'
    else:
        evh__ydg += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({atph__jjrvs}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        kqk__vfa = used_cols.instance_type
        chk__lozd = np.array(kqk__vfa.meta, dtype=np.int64)
        zjtg__stnl['used_cols_glbl'] = chk__lozd
        wvp__cxirc = set([table.block_nums[mru__grs] for mru__grs in chk__lozd]
            )
        evh__ydg += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        evh__ydg += f'  used_cols_set = None\n'
        chk__lozd = None
    evh__ydg += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for jlfst__vwouk in table.type_to_blk.values():
        evh__ydg += f"""  blk_{jlfst__vwouk} = bodo.hiframes.table.get_table_block(table, {jlfst__vwouk})
"""
        if xedf__nvy:
            evh__ydg += f"""  out_list_{jlfst__vwouk} = bodo.hiframes.table.alloc_list_like(blk_{jlfst__vwouk}, len(blk_{jlfst__vwouk}), False)
"""
            qota__ihyk = f'out_list_{jlfst__vwouk}'
        else:
            qota__ihyk = 'out_list'
        if chk__lozd is None or jlfst__vwouk in wvp__cxirc:
            evh__ydg += f'  for i in range(len(blk_{jlfst__vwouk})):\n'
            zjtg__stnl[f'col_indices_{jlfst__vwouk}'] = np.array(table.
                block_to_arr_ind[jlfst__vwouk], dtype=np.int64)
            evh__ydg += f'    col_loc = col_indices_{jlfst__vwouk}[i]\n'
            if chk__lozd is not None:
                evh__ydg += f'    if col_loc not in used_cols_set:\n'
                evh__ydg += f'        continue\n'
            if xedf__nvy:
                dzrd__ohjl = 'i'
            else:
                dzrd__ohjl = 'col_loc'
            if not naxw__efg:
                evh__ydg += (
                    f'    {qota__ihyk}[{dzrd__ohjl}] = blk_{jlfst__vwouk}[i]\n'
                    )
            elif ilf__juf:
                evh__ydg += f"""    {qota__ihyk}[{dzrd__ohjl}] = blk_{jlfst__vwouk}[i].{func_name}()
"""
            else:
                evh__ydg += (
                    f'    {qota__ihyk}[{dzrd__ohjl}] = {func_name}(blk_{jlfst__vwouk}[i])\n'
                    )
        if xedf__nvy:
            evh__ydg += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {qota__ihyk}, {jlfst__vwouk})
"""
    if xedf__nvy:
        evh__ydg += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        evh__ydg += '  return out_table\n'
    else:
        evh__ydg += (
            '  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)\n'
            )
    vzoo__xpu = {}
    exec(evh__ydg, zjtg__stnl, vzoo__xpu)
    return vzoo__xpu['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    zjtg__stnl = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    evh__ydg = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    evh__ydg += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for jlfst__vwouk in table.type_to_blk.values():
        evh__ydg += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {jlfst__vwouk})\n'
            )
        zjtg__stnl[f'col_indices_{jlfst__vwouk}'] = np.array(table.
            block_to_arr_ind[jlfst__vwouk], dtype=np.int64)
        evh__ydg += '  for i in range(len(blk)):\n'
        evh__ydg += f'    col_loc = col_indices_{jlfst__vwouk}[i]\n'
        evh__ydg += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    evh__ydg += '  if parallel:\n'
    evh__ydg += '    for i in range(start_offset, len(out_arr)):\n'
    evh__ydg += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    vzoo__xpu = {}
    exec(evh__ydg, zjtg__stnl, vzoo__xpu)
    return vzoo__xpu['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    wuqbo__uhyih = table.type_to_blk[arr_type]
    zjtg__stnl = {'bodo': bodo}
    zjtg__stnl['col_indices'] = np.array(table.block_to_arr_ind[
        wuqbo__uhyih], dtype=np.int64)
    qxpe__oplic = col_nums_meta.instance_type
    zjtg__stnl['col_nums'] = np.array(qxpe__oplic.meta, np.int64)
    evh__ydg = 'def impl(table, col_nums_meta, arr_type):\n'
    evh__ydg += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {wuqbo__uhyih})\n'
        )
    evh__ydg += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    evh__ydg += '  n = len(table)\n'
    lws__sva = bodo.utils.typing.is_str_arr_type(arr_type)
    if lws__sva:
        evh__ydg += '  total_chars = 0\n'
        evh__ydg += '  for c in col_nums:\n'
        evh__ydg += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        evh__ydg += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        evh__ydg += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        evh__ydg += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        evh__ydg += (
            '  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))\n'
            )
    evh__ydg += '  for i in range(len(col_nums)):\n'
    evh__ydg += '    c = col_nums[i]\n'
    if not lws__sva:
        evh__ydg += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    evh__ydg += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    evh__ydg += '    off = i * n\n'
    evh__ydg += '    for j in range(len(arr)):\n'
    evh__ydg += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    evh__ydg += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    evh__ydg += '      else:\n'
    evh__ydg += '        out_arr[off+j] = arr[j]\n'
    evh__ydg += '  return out_arr\n'
    cnh__aalj = {}
    exec(evh__ydg, zjtg__stnl, cnh__aalj)
    ucmgs__hnvvs = cnh__aalj['impl']
    return ucmgs__hnvvs


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    qnu__ukg = not is_overload_false(copy)
    ftdv__ehr = is_overload_true(copy)
    zjtg__stnl = {'bodo': bodo}
    ymcao__plb = table.arr_types
    rvdxr__yutrb = new_table_typ.arr_types
    iqthn__sid: Set[int] = set()
    sfvb__sjkgt: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    jfpvr__itv: Set[types.Type] = set()
    for mru__grs, tploh__udqvb in enumerate(ymcao__plb):
        sqtz__egn = rvdxr__yutrb[mru__grs]
        if tploh__udqvb == sqtz__egn:
            jfpvr__itv.add(tploh__udqvb)
        else:
            iqthn__sid.add(mru__grs)
            sfvb__sjkgt[sqtz__egn].add(tploh__udqvb)
    evh__ydg = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    evh__ydg += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    evh__ydg += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    oik__cvajn = set(range(len(ymcao__plb)))
    orwg__niopl = oik__cvajn - iqthn__sid
    if not is_overload_none(used_cols):
        kqk__vfa = used_cols.instance_type
        vwgdp__kjoz = set(kqk__vfa.meta)
        iqthn__sid = iqthn__sid & vwgdp__kjoz
        orwg__niopl = orwg__niopl & vwgdp__kjoz
        wvp__cxirc = set([table.block_nums[mru__grs] for mru__grs in
            vwgdp__kjoz])
    else:
        vwgdp__kjoz = None
    zjtg__stnl['cast_cols'] = np.array(list(iqthn__sid), dtype=np.int64)
    zjtg__stnl['copied_cols'] = np.array(list(orwg__niopl), dtype=np.int64)
    evh__ydg += f'  copied_cols_set = set(copied_cols)\n'
    evh__ydg += f'  cast_cols_set = set(cast_cols)\n'
    for ohgfw__nqp, jlfst__vwouk in new_table_typ.type_to_blk.items():
        zjtg__stnl[f'typ_list_{jlfst__vwouk}'] = types.List(ohgfw__nqp)
        evh__ydg += f"""  out_arr_list_{jlfst__vwouk} = bodo.hiframes.table.alloc_list_like(typ_list_{jlfst__vwouk}, {len(new_table_typ.block_to_arr_ind[jlfst__vwouk])}, False)
"""
        if ohgfw__nqp in jfpvr__itv:
            hcyk__fybbd = table.type_to_blk[ohgfw__nqp]
            if vwgdp__kjoz is None or hcyk__fybbd in wvp__cxirc:
                gji__cgv = table.block_to_arr_ind[hcyk__fybbd]
                ewa__gct = [new_table_typ.block_offsets[ixk__jgqx] for
                    ixk__jgqx in gji__cgv]
                zjtg__stnl[f'new_idx_{hcyk__fybbd}'] = np.array(ewa__gct,
                    np.int64)
                zjtg__stnl[f'orig_arr_inds_{hcyk__fybbd}'] = np.array(gji__cgv,
                    np.int64)
                evh__ydg += f"""  arr_list_{hcyk__fybbd} = bodo.hiframes.table.get_table_block(table, {hcyk__fybbd})
"""
                evh__ydg += f'  for i in range(len(arr_list_{hcyk__fybbd})):\n'
                evh__ydg += (
                    f'    arr_ind_{hcyk__fybbd} = orig_arr_inds_{hcyk__fybbd}[i]\n'
                    )
                evh__ydg += (
                    f'    if arr_ind_{hcyk__fybbd} not in copied_cols_set:\n')
                evh__ydg += f'      continue\n'
                evh__ydg += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{hcyk__fybbd}, i, arr_ind_{hcyk__fybbd})
"""
                evh__ydg += (
                    f'    out_idx_{jlfst__vwouk}_{hcyk__fybbd} = new_idx_{hcyk__fybbd}[i]\n'
                    )
                evh__ydg += (
                    f'    arr_val_{hcyk__fybbd} = arr_list_{hcyk__fybbd}[i]\n')
                if ftdv__ehr:
                    evh__ydg += (
                        f'    arr_val_{hcyk__fybbd} = arr_val_{hcyk__fybbd}.copy()\n'
                        )
                elif qnu__ukg:
                    evh__ydg += f"""    arr_val_{hcyk__fybbd} = arr_val_{hcyk__fybbd}.copy() if copy else arr_val_{jlfst__vwouk}
"""
                evh__ydg += f"""    out_arr_list_{jlfst__vwouk}[out_idx_{jlfst__vwouk}_{hcyk__fybbd}] = arr_val_{hcyk__fybbd}
"""
    ieejg__bawx = set()
    for ohgfw__nqp, jlfst__vwouk in new_table_typ.type_to_blk.items():
        if ohgfw__nqp in sfvb__sjkgt:
            if isinstance(ohgfw__nqp, bodo.IntegerArrayType):
                qet__uwjjr = ohgfw__nqp.get_pandas_scalar_type_instance.name
            else:
                qet__uwjjr = ohgfw__nqp.dtype
            zjtg__stnl[f'typ_{jlfst__vwouk}'] = qet__uwjjr
            tgv__rhtr = sfvb__sjkgt[ohgfw__nqp]
            for zpswq__gcq in tgv__rhtr:
                hcyk__fybbd = table.type_to_blk[zpswq__gcq]
                if vwgdp__kjoz is None or hcyk__fybbd in wvp__cxirc:
                    if (zpswq__gcq not in jfpvr__itv and zpswq__gcq not in
                        ieejg__bawx):
                        gji__cgv = table.block_to_arr_ind[hcyk__fybbd]
                        ewa__gct = [new_table_typ.block_offsets[ixk__jgqx] for
                            ixk__jgqx in gji__cgv]
                        zjtg__stnl[f'new_idx_{hcyk__fybbd}'] = np.array(
                            ewa__gct, np.int64)
                        zjtg__stnl[f'orig_arr_inds_{hcyk__fybbd}'] = np.array(
                            gji__cgv, np.int64)
                        evh__ydg += f"""  arr_list_{hcyk__fybbd} = bodo.hiframes.table.get_table_block(table, {hcyk__fybbd})
"""
                    ieejg__bawx.add(zpswq__gcq)
                    evh__ydg += (
                        f'  for i in range(len(arr_list_{hcyk__fybbd})):\n')
                    evh__ydg += (
                        f'    arr_ind_{hcyk__fybbd} = orig_arr_inds_{hcyk__fybbd}[i]\n'
                        )
                    evh__ydg += (
                        f'    if arr_ind_{hcyk__fybbd} not in cast_cols_set:\n'
                        )
                    evh__ydg += f'      continue\n'
                    evh__ydg += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{hcyk__fybbd}, i, arr_ind_{hcyk__fybbd})
"""
                    evh__ydg += f"""    out_idx_{jlfst__vwouk}_{hcyk__fybbd} = new_idx_{hcyk__fybbd}[i]
"""
                    evh__ydg += f"""    arr_val_{jlfst__vwouk} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{hcyk__fybbd}[i], typ_{jlfst__vwouk}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    evh__ydg += f"""    out_arr_list_{jlfst__vwouk}[out_idx_{jlfst__vwouk}_{hcyk__fybbd}] = arr_val_{jlfst__vwouk}
"""
        evh__ydg += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{jlfst__vwouk}, {jlfst__vwouk})
"""
    evh__ydg += '  return out_table\n'
    vzoo__xpu = {}
    exec(evh__ydg, zjtg__stnl, vzoo__xpu)
    return vzoo__xpu['impl']
