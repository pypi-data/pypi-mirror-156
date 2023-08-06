"""IR node for the data sorting"""
from collections import defaultdict
from typing import List, Set, Tuple, Union
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, mk_unique_var, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
import bodo.libs.timsort
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, sort_values_table
from bodo.libs.str_arr_ext import cp_str_list_to_array, to_list_if_immutable_arr
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.utils import gen_getitem


class Sort(ir.Stmt):

    def __init__(self, df_in: str, df_out: str, in_vars: List[ir.Var],
        out_vars: List[ir.Var], key_inds: Tuple[int], inplace: bool, loc:
        ir.Loc, ascending_list: Union[List[bool], bool]=True, na_position:
        Union[List[str], str]='last'):
        self.df_in = df_in
        self.df_out = df_out
        self.in_vars = in_vars
        self.out_vars = out_vars
        self.key_inds = key_inds
        self.inplace = inplace
        self.dead_var_inds: Set[int] = set()
        self.dead_key_var_inds: Set[int] = set()
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_inds)
            else:
                self.na_position_b = (False,) * len(key_inds)
        else:
            self.na_position_b = tuple([(True if umnmd__iwhv == 'last' else
                False) for umnmd__iwhv in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        xrhlg__nnqe = ', '.join(cwm__vhj.name for zsvj__zfrlx, cwm__vhj in
            enumerate(self.in_vars) if zsvj__zfrlx not in self.dead_var_inds)
        ciau__mity = f'{self.df_in}{{{xrhlg__nnqe}}}'
        lacgb__gshl = ', '.join(cwm__vhj.name for zsvj__zfrlx, cwm__vhj in
            enumerate(self.out_vars) if zsvj__zfrlx not in self.
            dead_var_inds and zsvj__zfrlx not in self.dead_key_var_inds)
        xvaap__obmgn = f'{self.df_out}{{{lacgb__gshl}}}'
        return f'Sort (keys: {self.key_inds}): {ciau__mity} {xvaap__obmgn}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    udfu__kurl = []
    for zsvj__zfrlx, kon__scyk in enumerate(sort_node.in_vars):
        if zsvj__zfrlx in sort_node.dead_var_inds:
            continue
        wnvm__ucv = equiv_set.get_shape(kon__scyk)
        if wnvm__ucv is not None:
            udfu__kurl.append(wnvm__ucv[0])
    if len(udfu__kurl) > 1:
        equiv_set.insert_equiv(*udfu__kurl)
    wavvc__odhrz = []
    udfu__kurl = []
    for zsvj__zfrlx, kon__scyk in enumerate(sort_node.out_vars):
        if (zsvj__zfrlx in sort_node.dead_var_inds or zsvj__zfrlx in
            sort_node.dead_key_var_inds):
            continue
        pafa__aount = typemap[kon__scyk.name]
        tfgq__vri = array_analysis._gen_shape_call(equiv_set, kon__scyk,
            pafa__aount.ndim, None, wavvc__odhrz)
        equiv_set.insert_equiv(kon__scyk, tfgq__vri)
        udfu__kurl.append(tfgq__vri[0])
        equiv_set.define(kon__scyk, set())
    if len(udfu__kurl) > 1:
        equiv_set.insert_equiv(*udfu__kurl)
    return [], wavvc__odhrz


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    dlsa__npts = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node
        .in_vars) if zsvj__zfrlx not in sort_node.dead_var_inds]
    vej__mqtb = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.
        out_vars) if zsvj__zfrlx not in sort_node.dead_var_inds and 
        zsvj__zfrlx not in sort_node.dead_key_var_inds]
    fre__otq = Distribution.OneD
    for kon__scyk in dlsa__npts:
        fre__otq = Distribution(min(fre__otq.value, array_dists[kon__scyk.
            name].value))
    krvt__dkk = Distribution(min(fre__otq.value, Distribution.OneD_Var.value))
    for kon__scyk in vej__mqtb:
        if kon__scyk.name in array_dists:
            krvt__dkk = Distribution(min(krvt__dkk.value, array_dists[
                kon__scyk.name].value))
    if krvt__dkk != Distribution.OneD_Var:
        fre__otq = krvt__dkk
    for kon__scyk in dlsa__npts:
        array_dists[kon__scyk.name] = fre__otq
    for kon__scyk in vej__mqtb:
        array_dists[kon__scyk.name] = krvt__dkk


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    in_vars = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.
        in_vars) if zsvj__zfrlx not in sort_node.dead_var_inds and 
        zsvj__zfrlx not in sort_node.dead_key_var_inds]
    out_vars = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.
        out_vars) if zsvj__zfrlx not in sort_node.dead_var_inds and 
        zsvj__zfrlx not in sort_node.dead_key_var_inds]
    for nloix__jaqh, icei__vldg in zip(in_vars, out_vars):
        typeinferer.constraints.append(typeinfer.Propagate(dst=icei__vldg.
            name, src=nloix__jaqh.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for zsvj__zfrlx, kon__scyk in enumerate(sort_node.out_vars):
            if (zsvj__zfrlx in sort_node.dead_var_inds or zsvj__zfrlx in
                sort_node.dead_key_var_inds):
                continue
            definitions[kon__scyk.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for zsvj__zfrlx in range(len(sort_node.in_vars)):
        if zsvj__zfrlx in sort_node.dead_var_inds:
            continue
        sort_node.in_vars[zsvj__zfrlx] = visit_vars_inner(sort_node.in_vars
            [zsvj__zfrlx], callback, cbdata)
        if zsvj__zfrlx in sort_node.dead_key_var_inds:
            continue
        sort_node.out_vars[zsvj__zfrlx] = visit_vars_inner(sort_node.
            out_vars[zsvj__zfrlx], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.out_vars):
        if cwm__vhj.name not in lives:
            if zsvj__zfrlx in sort_node.key_inds:
                sort_node.dead_key_var_inds.add(zsvj__zfrlx)
            else:
                sort_node.dead_var_inds.add(zsvj__zfrlx)
    if len(sort_node.dead_var_inds) + len(sort_node.dead_key_var_inds) == len(
        sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({cwm__vhj.name for zsvj__zfrlx, cwm__vhj in enumerate(
        sort_node.in_vars) if zsvj__zfrlx not in sort_node.dead_var_inds})
    if not sort_node.inplace:
        def_set.update({cwm__vhj.name for zsvj__zfrlx, cwm__vhj in
            enumerate(sort_node.out_vars) if zsvj__zfrlx not in sort_node.
            dead_var_inds and zsvj__zfrlx not in sort_node.dead_key_var_inds})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    teh__hxf = set()
    if not sort_node.inplace:
        teh__hxf.update({cwm__vhj.name for zsvj__zfrlx, cwm__vhj in
            enumerate(sort_node.out_vars) if zsvj__zfrlx not in sort_node.
            dead_var_inds and zsvj__zfrlx not in sort_node.dead_key_var_inds})
    return set(), teh__hxf


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for zsvj__zfrlx in range(len(sort_node.in_vars)):
        if zsvj__zfrlx in sort_node.dead_var_inds:
            continue
        sort_node.in_vars[zsvj__zfrlx] = replace_vars_inner(sort_node.
            in_vars[zsvj__zfrlx], var_dict)
        if zsvj__zfrlx in sort_node.dead_key_var_inds:
            continue
        sort_node.out_vars[zsvj__zfrlx] = replace_vars_inner(sort_node.
            out_vars[zsvj__zfrlx], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.
        in_vars) if zsvj__zfrlx not in sort_node.dead_var_inds]
    out_vars = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.
        out_vars) if zsvj__zfrlx not in sort_node.dead_var_inds and 
        zsvj__zfrlx not in sort_node.dead_key_var_inds]
    if array_dists is not None:
        parallel = True
        for cwm__vhj in (in_vars + out_vars):
            if array_dists[cwm__vhj.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                cwm__vhj.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    loc = sort_node.loc
    zgn__vvare = sort_node.in_vars[0].scope
    fqbgr__hcnl = [sort_node.in_vars[zsvj__zfrlx] for zsvj__zfrlx in
        sort_node.key_inds]
    qkj__xumw = [cwm__vhj for zsvj__zfrlx, cwm__vhj in enumerate(sort_node.
        in_vars) if zsvj__zfrlx not in sort_node.key_inds and zsvj__zfrlx
         not in sort_node.dead_var_inds]
    nodes = []
    if not sort_node.inplace:
        wdsqs__idu = []
        for cwm__vhj in fqbgr__hcnl:
            tkzfq__mptpd = _copy_array_nodes(cwm__vhj, nodes, typingctx,
                targetctx, typemap, calltypes)
            wdsqs__idu.append(tkzfq__mptpd)
        fqbgr__hcnl = wdsqs__idu
        ncz__wmvhf = []
        for cwm__vhj in qkj__xumw:
            tkzfq__mptpd = _copy_array_nodes(cwm__vhj, nodes, typingctx,
                targetctx, typemap, calltypes)
            ncz__wmvhf.append(tkzfq__mptpd)
        qkj__xumw = ncz__wmvhf
    key_name_args = [f'key{zsvj__zfrlx}' for zsvj__zfrlx in range(len(
        fqbgr__hcnl))]
    anyxy__vbei = ', '.join(key_name_args)
    col_name_args = [f'c{zsvj__zfrlx}' for zsvj__zfrlx in range(len(qkj__xumw))
        ]
    qzskr__hypl = ', '.join(col_name_args)
    uqph__amjt = f'def f({anyxy__vbei}, {qzskr__hypl}):\n'
    rblhg__dsoii = {oepo__gaofz: zsvj__zfrlx for zsvj__zfrlx, oepo__gaofz in
        enumerate(sort_node.key_inds)}
    dead_keys = {rblhg__dsoii[zsvj__zfrlx] for zsvj__zfrlx in sort_node.
        dead_key_var_inds}
    uqph__amjt += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, dead_keys, parallel)
    uqph__amjt += '  return key_arrs, data\n'
    vnsj__sqn = {}
    exec(uqph__amjt, {}, vnsj__sqn)
    fiaw__pxw = vnsj__sqn['f']
    xflx__ixwwx = compile_to_numba_ir(fiaw__pxw, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(typemap[cwm__vhj.name] for cwm__vhj in 
        fqbgr__hcnl + qkj__xumw), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(xflx__ixwwx, fqbgr__hcnl + qkj__xumw)
    nodes += xflx__ixwwx.body[:-2]
    sqsk__ifpm = nodes[-1].target
    thh__xzki = ir.Var(zgn__vvare, mk_unique_var('key_data'), loc)
    typemap[thh__xzki.name] = types.Tuple([typemap[cwm__vhj.name] for 
        zsvj__zfrlx, cwm__vhj in enumerate(fqbgr__hcnl) if zsvj__zfrlx not in
        dead_keys])
    gen_getitem(thh__xzki, sqsk__ifpm, 0, calltypes, nodes)
    lftyv__bzpl = ir.Var(zgn__vvare, mk_unique_var('sort_data'), loc)
    typemap[lftyv__bzpl.name] = types.Tuple([typemap[cwm__vhj.name] for
        cwm__vhj in qkj__xumw])
    gen_getitem(lftyv__bzpl, sqsk__ifpm, 1, calltypes, nodes)
    zew__btai = 0
    for zsvj__zfrlx in sort_node.key_inds:
        if zsvj__zfrlx in sort_node.dead_key_var_inds:
            continue
        var = sort_node.out_vars[zsvj__zfrlx]
        gen_getitem(var, thh__xzki, zew__btai, calltypes, nodes)
        zew__btai += 1
    qovb__upwvj = 0
    for zsvj__zfrlx, var in enumerate(sort_node.out_vars):
        if (zsvj__zfrlx in sort_node.dead_var_inds or zsvj__zfrlx in
            sort_node.key_inds):
            continue
        gen_getitem(var, lftyv__bzpl, qovb__upwvj, calltypes, nodes)
        qovb__upwvj += 1
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    xflx__ixwwx = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(xflx__ixwwx, [var])
    nodes += xflx__ixwwx.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, dead_keys, parallel):
    uqph__amjt = ''
    mnfz__baq = len(key_name_args)
    fnel__tii = [f'array_to_info({crf__otv})' for crf__otv in key_name_args
        ] + [f'array_to_info({crf__otv})' for crf__otv in col_name_args]
    uqph__amjt += '  info_list_total = [{}]\n'.format(','.join(fnel__tii))
    uqph__amjt += '  table_total = arr_info_list_to_table(info_list_total)\n'
    uqph__amjt += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if jnldl__tojgp else '0' for jnldl__tojgp in ascending_list))
    uqph__amjt += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if jnldl__tojgp else '0' for jnldl__tojgp in na_position_b))
    uqph__amjt += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if zsvj__zfrlx in dead_keys else '0' for zsvj__zfrlx in
        range(mnfz__baq)))
    uqph__amjt += f"""  out_table = sort_values_table(table_total, {mnfz__baq}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, {parallel})
"""
    lff__yzllr = 0
    rtr__dvx = []
    for zsvj__zfrlx, crf__otv in enumerate(key_name_args):
        if zsvj__zfrlx in dead_keys:
            continue
        rtr__dvx.append(
            f'info_to_array(info_from_table(out_table, {lff__yzllr}), {crf__otv})'
            )
        lff__yzllr += 1
    uqph__amjt += '  key_arrs = ({}{})\n'.format(','.join(rtr__dvx), ',' if
        len(rtr__dvx) == 1 else '')
    pti__xoudc = []
    for crf__otv in col_name_args:
        pti__xoudc.append(
            f'info_to_array(info_from_table(out_table, {lff__yzllr}), {crf__otv})'
            )
        lff__yzllr += 1
    if len(pti__xoudc) > 0:
        uqph__amjt += '  data = ({},)\n'.format(','.join(pti__xoudc))
    else:
        uqph__amjt += '  data = ()\n'
    uqph__amjt += '  delete_table(out_table)\n'
    uqph__amjt += '  delete_table(table_total)\n'
    return uqph__amjt
