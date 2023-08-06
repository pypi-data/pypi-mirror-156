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
            self.na_position_b = tuple([(True if iwczt__jztk == 'last' else
                False) for iwczt__jztk in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        oeypj__lbp = ', '.join(xece__dmubc.name for dendh__thj, xece__dmubc in
            enumerate(self.in_vars) if dendh__thj not in self.dead_var_inds)
        jpn__cgjvd = f'{self.df_in}{{{oeypj__lbp}}}'
        lil__neoh = ', '.join(xece__dmubc.name for dendh__thj, xece__dmubc in
            enumerate(self.out_vars) if dendh__thj not in self.
            dead_var_inds and dendh__thj not in self.dead_key_var_inds)
        dneyf__xkj = f'{self.df_out}{{{lil__neoh}}}'
        return f'Sort (keys: {self.key_inds}): {jpn__cgjvd} {dneyf__xkj}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    hqfy__zmn = []
    for dendh__thj, bxi__gofis in enumerate(sort_node.in_vars):
        if dendh__thj in sort_node.dead_var_inds:
            continue
        zqdnj__rtfti = equiv_set.get_shape(bxi__gofis)
        if zqdnj__rtfti is not None:
            hqfy__zmn.append(zqdnj__rtfti[0])
    if len(hqfy__zmn) > 1:
        equiv_set.insert_equiv(*hqfy__zmn)
    vfv__ebf = []
    hqfy__zmn = []
    for dendh__thj, bxi__gofis in enumerate(sort_node.out_vars):
        if (dendh__thj in sort_node.dead_var_inds or dendh__thj in
            sort_node.dead_key_var_inds):
            continue
        jfjz__cxmh = typemap[bxi__gofis.name]
        vmcfk__zafub = array_analysis._gen_shape_call(equiv_set, bxi__gofis,
            jfjz__cxmh.ndim, None, vfv__ebf)
        equiv_set.insert_equiv(bxi__gofis, vmcfk__zafub)
        hqfy__zmn.append(vmcfk__zafub[0])
        equiv_set.define(bxi__gofis, set())
    if len(hqfy__zmn) > 1:
        equiv_set.insert_equiv(*hqfy__zmn)
    return [], vfv__ebf


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    xxfx__tuaa = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.in_vars) if dendh__thj not in sort_node.dead_var_inds]
    bfp__sqgn = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.out_vars) if dendh__thj not in sort_node.dead_var_inds and
        dendh__thj not in sort_node.dead_key_var_inds]
    pvbx__ivvfv = Distribution.OneD
    for bxi__gofis in xxfx__tuaa:
        pvbx__ivvfv = Distribution(min(pvbx__ivvfv.value, array_dists[
            bxi__gofis.name].value))
    ytn__tuhgs = Distribution(min(pvbx__ivvfv.value, Distribution.OneD_Var.
        value))
    for bxi__gofis in bfp__sqgn:
        if bxi__gofis.name in array_dists:
            ytn__tuhgs = Distribution(min(ytn__tuhgs.value, array_dists[
                bxi__gofis.name].value))
    if ytn__tuhgs != Distribution.OneD_Var:
        pvbx__ivvfv = ytn__tuhgs
    for bxi__gofis in xxfx__tuaa:
        array_dists[bxi__gofis.name] = pvbx__ivvfv
    for bxi__gofis in bfp__sqgn:
        array_dists[bxi__gofis.name] = ytn__tuhgs


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    in_vars = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.in_vars) if dendh__thj not in sort_node.dead_var_inds and
        dendh__thj not in sort_node.dead_key_var_inds]
    out_vars = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.out_vars) if dendh__thj not in sort_node.dead_var_inds and
        dendh__thj not in sort_node.dead_key_var_inds]
    for jrv__bzgf, aszqp__garuk in zip(in_vars, out_vars):
        typeinferer.constraints.append(typeinfer.Propagate(dst=aszqp__garuk
            .name, src=jrv__bzgf.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for dendh__thj, bxi__gofis in enumerate(sort_node.out_vars):
            if (dendh__thj in sort_node.dead_var_inds or dendh__thj in
                sort_node.dead_key_var_inds):
                continue
            definitions[bxi__gofis.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for dendh__thj in range(len(sort_node.in_vars)):
        if dendh__thj in sort_node.dead_var_inds:
            continue
        sort_node.in_vars[dendh__thj] = visit_vars_inner(sort_node.in_vars[
            dendh__thj], callback, cbdata)
        if dendh__thj in sort_node.dead_key_var_inds:
            continue
        sort_node.out_vars[dendh__thj] = visit_vars_inner(sort_node.
            out_vars[dendh__thj], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    for dendh__thj, xece__dmubc in enumerate(sort_node.out_vars):
        if xece__dmubc.name not in lives:
            if dendh__thj in sort_node.key_inds:
                sort_node.dead_key_var_inds.add(dendh__thj)
            else:
                sort_node.dead_var_inds.add(dendh__thj)
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
    use_set.update({xece__dmubc.name for dendh__thj, xece__dmubc in
        enumerate(sort_node.in_vars) if dendh__thj not in sort_node.
        dead_var_inds})
    if not sort_node.inplace:
        def_set.update({xece__dmubc.name for dendh__thj, xece__dmubc in
            enumerate(sort_node.out_vars) if dendh__thj not in sort_node.
            dead_var_inds and dendh__thj not in sort_node.dead_key_var_inds})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    ksn__eaf = set()
    if not sort_node.inplace:
        ksn__eaf.update({xece__dmubc.name for dendh__thj, xece__dmubc in
            enumerate(sort_node.out_vars) if dendh__thj not in sort_node.
            dead_var_inds and dendh__thj not in sort_node.dead_key_var_inds})
    return set(), ksn__eaf


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for dendh__thj in range(len(sort_node.in_vars)):
        if dendh__thj in sort_node.dead_var_inds:
            continue
        sort_node.in_vars[dendh__thj] = replace_vars_inner(sort_node.
            in_vars[dendh__thj], var_dict)
        if dendh__thj in sort_node.dead_key_var_inds:
            continue
        sort_node.out_vars[dendh__thj] = replace_vars_inner(sort_node.
            out_vars[dendh__thj], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.in_vars) if dendh__thj not in sort_node.dead_var_inds]
    out_vars = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.out_vars) if dendh__thj not in sort_node.dead_var_inds and
        dendh__thj not in sort_node.dead_key_var_inds]
    if array_dists is not None:
        parallel = True
        for xece__dmubc in (in_vars + out_vars):
            if array_dists[xece__dmubc.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                xece__dmubc.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    loc = sort_node.loc
    paak__kkmb = sort_node.in_vars[0].scope
    cnn__bmuri = [sort_node.in_vars[dendh__thj] for dendh__thj in sort_node
        .key_inds]
    uvxhl__pqy = [xece__dmubc for dendh__thj, xece__dmubc in enumerate(
        sort_node.in_vars) if dendh__thj not in sort_node.key_inds and 
        dendh__thj not in sort_node.dead_var_inds]
    nodes = []
    if not sort_node.inplace:
        gnk__xfb = []
        for xece__dmubc in cnn__bmuri:
            ihmxm__zfj = _copy_array_nodes(xece__dmubc, nodes, typingctx,
                targetctx, typemap, calltypes)
            gnk__xfb.append(ihmxm__zfj)
        cnn__bmuri = gnk__xfb
        kdt__plgpi = []
        for xece__dmubc in uvxhl__pqy:
            ihmxm__zfj = _copy_array_nodes(xece__dmubc, nodes, typingctx,
                targetctx, typemap, calltypes)
            kdt__plgpi.append(ihmxm__zfj)
        uvxhl__pqy = kdt__plgpi
    key_name_args = [f'key{dendh__thj}' for dendh__thj in range(len(
        cnn__bmuri))]
    qhqv__hecce = ', '.join(key_name_args)
    col_name_args = [f'c{dendh__thj}' for dendh__thj in range(len(uvxhl__pqy))]
    xnxdz__tgkuk = ', '.join(col_name_args)
    jsnu__azdx = f'def f({qhqv__hecce}, {xnxdz__tgkuk}):\n'
    ejqj__tfubu = {ygwvn__rrtxr: dendh__thj for dendh__thj, ygwvn__rrtxr in
        enumerate(sort_node.key_inds)}
    dead_keys = {ejqj__tfubu[dendh__thj] for dendh__thj in sort_node.
        dead_key_var_inds}
    jsnu__azdx += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, dead_keys, parallel)
    jsnu__azdx += '  return key_arrs, data\n'
    xwwv__huz = {}
    exec(jsnu__azdx, {}, xwwv__huz)
    wgt__jhwu = xwwv__huz['f']
    qozn__kja = compile_to_numba_ir(wgt__jhwu, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(typemap[xece__dmubc.name] for xece__dmubc in
        cnn__bmuri + uvxhl__pqy), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(qozn__kja, cnn__bmuri + uvxhl__pqy)
    nodes += qozn__kja.body[:-2]
    cbi__thh = nodes[-1].target
    oow__ubtd = ir.Var(paak__kkmb, mk_unique_var('key_data'), loc)
    typemap[oow__ubtd.name] = types.Tuple([typemap[xece__dmubc.name] for 
        dendh__thj, xece__dmubc in enumerate(cnn__bmuri) if dendh__thj not in
        dead_keys])
    gen_getitem(oow__ubtd, cbi__thh, 0, calltypes, nodes)
    pyz__dpu = ir.Var(paak__kkmb, mk_unique_var('sort_data'), loc)
    typemap[pyz__dpu.name] = types.Tuple([typemap[xece__dmubc.name] for
        xece__dmubc in uvxhl__pqy])
    gen_getitem(pyz__dpu, cbi__thh, 1, calltypes, nodes)
    bzrwl__phv = 0
    for dendh__thj in sort_node.key_inds:
        if dendh__thj in sort_node.dead_key_var_inds:
            continue
        var = sort_node.out_vars[dendh__thj]
        gen_getitem(var, oow__ubtd, bzrwl__phv, calltypes, nodes)
        bzrwl__phv += 1
    gyaxk__heap = 0
    for dendh__thj, var in enumerate(sort_node.out_vars):
        if (dendh__thj in sort_node.dead_var_inds or dendh__thj in
            sort_node.key_inds):
            continue
        gen_getitem(var, pyz__dpu, gyaxk__heap, calltypes, nodes)
        gyaxk__heap += 1
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    qozn__kja = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(qozn__kja, [var])
    nodes += qozn__kja.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, dead_keys, parallel):
    jsnu__azdx = ''
    rnpys__npns = len(key_name_args)
    glc__azif = [f'array_to_info({jll__tubx})' for jll__tubx in key_name_args
        ] + [f'array_to_info({jll__tubx})' for jll__tubx in col_name_args]
    jsnu__azdx += '  info_list_total = [{}]\n'.format(','.join(glc__azif))
    jsnu__azdx += '  table_total = arr_info_list_to_table(info_list_total)\n'
    jsnu__azdx += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if cxysa__ynpcs else '0' for cxysa__ynpcs in ascending_list))
    jsnu__azdx += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if cxysa__ynpcs else '0' for cxysa__ynpcs in na_position_b))
    jsnu__azdx += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if dendh__thj in dead_keys else '0' for dendh__thj in
        range(rnpys__npns)))
    jsnu__azdx += f"""  out_table = sort_values_table(table_total, {rnpys__npns}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, {parallel})
"""
    dszwd__zwtuo = 0
    vamzl__mljw = []
    for dendh__thj, jll__tubx in enumerate(key_name_args):
        if dendh__thj in dead_keys:
            continue
        vamzl__mljw.append(
            f'info_to_array(info_from_table(out_table, {dszwd__zwtuo}), {jll__tubx})'
            )
        dszwd__zwtuo += 1
    jsnu__azdx += '  key_arrs = ({}{})\n'.format(','.join(vamzl__mljw), ',' if
        len(vamzl__mljw) == 1 else '')
    ghm__cxbl = []
    for jll__tubx in col_name_args:
        ghm__cxbl.append(
            f'info_to_array(info_from_table(out_table, {dszwd__zwtuo}), {jll__tubx})'
            )
        dszwd__zwtuo += 1
    if len(ghm__cxbl) > 0:
        jsnu__azdx += '  data = ({},)\n'.format(','.join(ghm__cxbl))
    else:
        jsnu__azdx += '  data = ()\n'
    jsnu__azdx += '  delete_table(out_table)\n'
    jsnu__azdx += '  delete_table(table_total)\n'
    return jsnu__azdx
