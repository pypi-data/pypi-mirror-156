"""IR node for the join and merge"""
from collections import defaultdict
from typing import List, Literal, Union
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, hash_join_table, info_from_table, info_to_array
from bodo.libs.int_arr_ext import IntDtype
from bodo.libs.str_arr_ext import cp_str_list_to_array, to_list_if_immutable_arr
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.typing import BodoError, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, is_str_arr_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, debug_prints, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        mftz__qss = func.signature
        zte__fkzng = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        lurg__pcrve = cgutils.get_or_insert_function(builder.module,
            zte__fkzng, sym._literal_value)
        builder.call(lurg__pcrve, [context.get_constant_null(mftz__qss.args
            [0]), context.get_constant_null(mftz__qss.args[1]), context.
            get_constant_null(mftz__qss.args[2]), context.get_constant_null
            (mftz__qss.args[3]), context.get_constant_null(mftz__qss.args[4
            ]), context.get_constant_null(mftz__qss.args[5]), context.
            get_constant(types.int64, 0), context.get_constant(types.int64, 0)]
            )
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


HOW_OPTIONS = Literal['inner', 'left', 'right', 'outer', 'asof']


class Join(ir.Stmt):

    def __init__(self, df_out: str, left_df: str, right_df: str, left_keys:
        Union[List[str], str], right_keys: Union[List[str], str],
        out_data_vars: List[ir.Var], left_vars: List[ir.Var], right_vars:
        List[ir.Var], how: HOW_OPTIONS, suffix_left: str, suffix_right: str,
        loc: ir.Loc, is_left: bool, is_right: bool, is_join: bool,
        left_index: bool, right_index: bool, indicator: bool, is_na_equal:
        bool, gen_cond_expr: str):
        self.df_out = df_out
        self.left_df = left_df
        self.right_df = right_df
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.left_key_set = set(left_keys)
        self.right_key_set = set(right_keys)
        self.out_data_vars = out_data_vars
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.suffix_left = suffix_left
        self.suffix_right = suffix_right
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator = indicator
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        if gen_cond_expr:
            self.left_cond_cols = set(jkyh__gamf for jkyh__gamf in
                left_vars.keys() if f'(left.{jkyh__gamf})' in gen_cond_expr)
            self.right_cond_cols = set(jkyh__gamf for jkyh__gamf in
                right_vars.keys() if f'(right.{jkyh__gamf})' in gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        noqdz__dkdo = self.left_key_set & self.right_key_set
        prq__swok = set(left_vars.keys()) & set(right_vars.keys())
        lqqlk__qcsgj = prq__swok - noqdz__dkdo
        vect_same_key = []
        n_keys = len(left_keys)
        for iqqir__fhj in range(n_keys):
            ihtyl__wkyzr = left_keys[iqqir__fhj]
            sky__kwr = right_keys[iqqir__fhj]
            vect_same_key.append(ihtyl__wkyzr == sky__kwr)
        self.vect_same_key = vect_same_key
        self.column_origins = {}
        for jkyh__gamf in left_vars.keys():
            jovb__ueg = 'left', jkyh__gamf
            if jkyh__gamf in lqqlk__qcsgj:
                ynyaq__zpg = str(jkyh__gamf) + suffix_left
                self.column_origins[ynyaq__zpg] = jovb__ueg
                if (right_index and not left_index and jkyh__gamf in self.
                    left_key_set):
                    self.column_origins[jkyh__gamf] = jovb__ueg
            else:
                self.column_origins[jkyh__gamf] = jovb__ueg
        for jkyh__gamf in right_vars.keys():
            jovb__ueg = 'right', jkyh__gamf
            if jkyh__gamf in lqqlk__qcsgj:
                ncjg__ozw = str(jkyh__gamf) + suffix_right
                self.column_origins[ncjg__ozw] = jovb__ueg
                if (left_index and not right_index and jkyh__gamf in self.
                    right_key_set):
                    self.column_origins[jkyh__gamf] = jovb__ueg
            else:
                self.column_origins[jkyh__gamf] = jovb__ueg
        if '$_bodo_index_' in lqqlk__qcsgj:
            lqqlk__qcsgj.remove('$_bodo_index_')
        self.add_suffix = lqqlk__qcsgj

    def __repr__(self):
        bhv__fjfz = ''
        for jkyh__gamf, fdvx__ekc in self.out_data_vars.items():
            bhv__fjfz += "'{}':{}, ".format(jkyh__gamf, fdvx__ekc.name)
        zwxm__gzm = '{}{{{}}}'.format(self.df_out, bhv__fjfz)
        mjc__panl = ''
        for jkyh__gamf, fdvx__ekc in self.left_vars.items():
            mjc__panl += "'{}':{}, ".format(jkyh__gamf, fdvx__ekc.name)
        fkxqd__cpqe = '{}{{{}}}'.format(self.left_df, mjc__panl)
        mjc__panl = ''
        for jkyh__gamf, fdvx__ekc in self.right_vars.items():
            mjc__panl += "'{}':{}, ".format(jkyh__gamf, fdvx__ekc.name)
        pwwdo__nbycr = '{}{{{}}}'.format(self.right_df, mjc__panl)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, zwxm__gzm, fkxqd__cpqe, pwwdo__nbycr)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    hes__tmaei = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    eth__edyy = []
    nxct__sah = list(join_node.left_vars.values())
    for renz__tdt in nxct__sah:
        kcws__eywh = typemap[renz__tdt.name]
        kzh__havz = equiv_set.get_shape(renz__tdt)
        if kzh__havz:
            eth__edyy.append(kzh__havz[0])
    if len(eth__edyy) > 1:
        equiv_set.insert_equiv(*eth__edyy)
    eth__edyy = []
    nxct__sah = list(join_node.right_vars.values())
    for renz__tdt in nxct__sah:
        kcws__eywh = typemap[renz__tdt.name]
        kzh__havz = equiv_set.get_shape(renz__tdt)
        if kzh__havz:
            eth__edyy.append(kzh__havz[0])
    if len(eth__edyy) > 1:
        equiv_set.insert_equiv(*eth__edyy)
    eth__edyy = []
    for renz__tdt in join_node.out_data_vars.values():
        kcws__eywh = typemap[renz__tdt.name]
        aur__ugy = array_analysis._gen_shape_call(equiv_set, renz__tdt,
            kcws__eywh.ndim, None, hes__tmaei)
        equiv_set.insert_equiv(renz__tdt, aur__ugy)
        eth__edyy.append(aur__ugy[0])
        equiv_set.define(renz__tdt, set())
    if len(eth__edyy) > 1:
        equiv_set.insert_equiv(*eth__edyy)
    return [], hes__tmaei


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    ubdmg__pvinh = Distribution.OneD
    utp__ypg = Distribution.OneD
    for renz__tdt in join_node.left_vars.values():
        ubdmg__pvinh = Distribution(min(ubdmg__pvinh.value, array_dists[
            renz__tdt.name].value))
    for renz__tdt in join_node.right_vars.values():
        utp__ypg = Distribution(min(utp__ypg.value, array_dists[renz__tdt.
            name].value))
    sxr__xlm = Distribution.OneD_Var
    for renz__tdt in join_node.out_data_vars.values():
        if renz__tdt.name in array_dists:
            sxr__xlm = Distribution(min(sxr__xlm.value, array_dists[
                renz__tdt.name].value))
    raacc__qxkan = Distribution(min(sxr__xlm.value, ubdmg__pvinh.value))
    ryaxn__tblvg = Distribution(min(sxr__xlm.value, utp__ypg.value))
    sxr__xlm = Distribution(max(raacc__qxkan.value, ryaxn__tblvg.value))
    for renz__tdt in join_node.out_data_vars.values():
        array_dists[renz__tdt.name] = sxr__xlm
    if sxr__xlm != Distribution.OneD_Var:
        ubdmg__pvinh = sxr__xlm
        utp__ypg = sxr__xlm
    for renz__tdt in join_node.left_vars.values():
        array_dists[renz__tdt.name] = ubdmg__pvinh
    for renz__tdt in join_node.right_vars.values():
        array_dists[renz__tdt.name] = utp__ypg
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    for ltfaw__fbq, oajw__zau in join_node.out_data_vars.items():
        if join_node.indicator and ltfaw__fbq == '_merge':
            continue
        if not ltfaw__fbq in join_node.column_origins:
            raise BodoError('join(): The variable ' + ltfaw__fbq +
                ' is absent from the output')
        jdsh__dcv = join_node.column_origins[ltfaw__fbq]
        if jdsh__dcv[0] == 'left':
            renz__tdt = join_node.left_vars[jdsh__dcv[1]]
        else:
            renz__tdt = join_node.right_vars[jdsh__dcv[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=oajw__zau.
            name, src=renz__tdt.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for cyp__vfa in list(join_node.left_vars.keys()):
        join_node.left_vars[cyp__vfa] = visit_vars_inner(join_node.
            left_vars[cyp__vfa], callback, cbdata)
    for cyp__vfa in list(join_node.right_vars.keys()):
        join_node.right_vars[cyp__vfa] = visit_vars_inner(join_node.
            right_vars[cyp__vfa], callback, cbdata)
    for cyp__vfa in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[cyp__vfa] = visit_vars_inner(join_node.
            out_data_vars[cyp__vfa], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    nynxc__kfdx = []
    lrg__wluz = True
    for cyp__vfa, renz__tdt in join_node.out_data_vars.items():
        if renz__tdt.name in lives:
            lrg__wluz = False
            continue
        nynxc__kfdx.append(cyp__vfa)
        if join_node.indicator and cyp__vfa == '_merge':
            join_node.indicator = False
            continue
        if cyp__vfa == '$_bodo_index_':
            xoqsy__lrw = cyp__vfa
        else:
            kwji__xzkh, xoqsy__lrw = join_node.column_origins[cyp__vfa]
        if cyp__vfa == '$_bodo_index_' and cyp__vfa in join_node.left_vars:
            kwji__xzkh = 'left'
        if (kwji__xzkh == 'left' and xoqsy__lrw not in join_node.
            left_key_set and xoqsy__lrw not in join_node.left_cond_cols):
            join_node.left_vars.pop(xoqsy__lrw)
        if cyp__vfa == '$_bodo_index_' and cyp__vfa in join_node.right_vars:
            kwji__xzkh = 'right'
        if (kwji__xzkh == 'right' and xoqsy__lrw not in join_node.
            right_key_set and xoqsy__lrw not in join_node.right_cond_cols):
            join_node.right_vars.pop(xoqsy__lrw)
    for cname in nynxc__kfdx:
        join_node.out_data_vars.pop(cname)
    if lrg__wluz:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({fdvx__ekc.name for fdvx__ekc in join_node.left_vars.
        values()})
    use_set.update({fdvx__ekc.name for fdvx__ekc in join_node.right_vars.
        values()})
    def_set.update({fdvx__ekc.name for fdvx__ekc in join_node.out_data_vars
        .values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    tiyet__jwjza = set(fdvx__ekc.name for fdvx__ekc in join_node.
        out_data_vars.values())
    return set(), tiyet__jwjza


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for cyp__vfa in list(join_node.left_vars.keys()):
        join_node.left_vars[cyp__vfa] = replace_vars_inner(join_node.
            left_vars[cyp__vfa], var_dict)
    for cyp__vfa in list(join_node.right_vars.keys()):
        join_node.right_vars[cyp__vfa] = replace_vars_inner(join_node.
            right_vars[cyp__vfa], var_dict)
    for cyp__vfa in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[cyp__vfa] = replace_vars_inner(join_node.
            out_data_vars[cyp__vfa], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for renz__tdt in join_node.out_data_vars.values():
        definitions[renz__tdt.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    gnbrg__jhg = tuple(join_node.left_vars[jkyh__gamf] for jkyh__gamf in
        join_node.left_keys)
    yhfxs__yndwt = tuple(join_node.right_vars[jkyh__gamf] for jkyh__gamf in
        join_node.right_keys)
    edlo__thgey = ()
    pneau__zwu = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        riirj__zncgi = join_node.right_keys[0]
        if (riirj__zncgi in join_node.add_suffix and riirj__zncgi in
            join_node.out_data_vars):
            pneau__zwu = riirj__zncgi,
            edlo__thgey = join_node.right_vars[riirj__zncgi],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        riirj__zncgi = join_node.left_keys[0]
        if (riirj__zncgi in join_node.add_suffix and riirj__zncgi in
            join_node.out_data_vars):
            pneau__zwu = riirj__zncgi,
            edlo__thgey = join_node.left_vars[riirj__zncgi],
            optional_column = True
    ycn__aop = [join_node.out_data_vars[cname] for cname in pneau__zwu]
    zbqu__ysd = tuple(fdvx__ekc for pejh__ruwe, fdvx__ekc in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if pejh__ruwe
         not in join_node.left_key_set)
    mob__rwtn = tuple(fdvx__ekc for pejh__ruwe, fdvx__ekc in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if 
        pejh__ruwe not in join_node.right_key_set)
    ydwf__tslun = (edlo__thgey + gnbrg__jhg + yhfxs__yndwt + zbqu__ysd +
        mob__rwtn)
    nwi__occpp = tuple(typemap[fdvx__ekc.name] for fdvx__ekc in ydwf__tslun)
    rcbj__onb = tuple('opti_c' + str(bklq__ekvh) for bklq__ekvh in range(
        len(edlo__thgey)))
    left_other_names = tuple('t1_c' + str(bklq__ekvh) for bklq__ekvh in
        range(len(zbqu__ysd)))
    right_other_names = tuple('t2_c' + str(bklq__ekvh) for bklq__ekvh in
        range(len(mob__rwtn)))
    left_other_types = tuple([typemap[jkyh__gamf.name] for jkyh__gamf in
        zbqu__ysd])
    right_other_types = tuple([typemap[jkyh__gamf.name] for jkyh__gamf in
        mob__rwtn])
    left_key_names = tuple('t1_key' + str(bklq__ekvh) for bklq__ekvh in
        range(n_keys))
    right_key_names = tuple('t2_key' + str(bklq__ekvh) for bklq__ekvh in
        range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(rcbj__onb[0
        ]) if len(rcbj__onb) == 1 else '', ','.join(left_key_names), ','.
        join(right_key_names), ','.join(left_other_names), ',' if len(
        left_other_names) != 0 else '', ','.join(right_other_names))
    left_key_types = tuple(typemap[fdvx__ekc.name] for fdvx__ekc in gnbrg__jhg)
    right_key_types = tuple(typemap[fdvx__ekc.name] for fdvx__ekc in
        yhfxs__yndwt)
    for bklq__ekvh in range(n_keys):
        glbs[f'key_type_{bklq__ekvh}'] = _match_join_key_types(left_key_types
            [bklq__ekvh], right_key_types[bklq__ekvh], loc)
    func_text += '    t1_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({left_key_names[bklq__ekvh]}, key_type_{bklq__ekvh})'
         for bklq__ekvh in range(n_keys)))
    func_text += '    t2_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({right_key_names[bklq__ekvh]}, key_type_{bklq__ekvh})'
         for bklq__ekvh in range(n_keys)))
    func_text += '    data_left = ({}{})\n'.format(','.join(
        left_other_names), ',' if len(left_other_names) != 0 else '')
    func_text += '    data_right = ({}{})\n'.format(','.join(
        right_other_names), ',' if len(right_other_names) != 0 else '')
    left_key_in_output = []
    right_key_in_output = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            sgx__bzy = str(cname) + join_node.suffix_left
        else:
            sgx__bzy = cname
        if sgx__bzy in join_node.out_data_vars:
            ycn__aop.append(join_node.out_data_vars[sgx__bzy])
            qmc__jmft = 1
        else:
            qmc__jmft = 0
        left_key_in_output.append(qmc__jmft)
    for bklq__ekvh, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[bklq__ekvh] and not join_node.is_join:
            if cname in join_node.add_suffix:
                sgx__bzy = str(cname) + join_node.suffix_right
            else:
                sgx__bzy = cname
            if sgx__bzy in join_node.out_data_vars:
                ycn__aop.append(join_node.out_data_vars[sgx__bzy])
                qmc__jmft = 1
            else:
                qmc__jmft = 0
            right_key_in_output.append(qmc__jmft)

    def _get_out_col_name(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                sgx__bzy = str(cname) + join_node.suffix_left
            else:
                sgx__bzy = str(cname) + join_node.suffix_right
        else:
            sgx__bzy = cname
        return sgx__bzy

    def _get_out_col_var(cname, is_left):
        sgx__bzy = _get_out_col_name(cname, is_left)
        return join_node.out_data_vars[sgx__bzy]
    for pejh__ruwe in sorted(join_node.left_vars.keys(), key=lambda a: str(a)):
        if pejh__ruwe not in join_node.left_key_set:
            qmc__jmft = 1
            if pejh__ruwe in join_node.left_cond_cols:
                sgx__bzy = _get_out_col_name(pejh__ruwe, True)
                if sgx__bzy not in join_node.out_data_vars:
                    qmc__jmft = 0
                left_key_in_output.append(qmc__jmft)
            if qmc__jmft:
                ycn__aop.append(_get_out_col_var(pejh__ruwe, True))
    for pejh__ruwe in sorted(join_node.right_vars.keys(), key=lambda a: str(a)
        ):
        if pejh__ruwe not in join_node.right_key_set:
            qmc__jmft = 1
            if pejh__ruwe in join_node.right_cond_cols:
                sgx__bzy = _get_out_col_name(pejh__ruwe, False)
                if sgx__bzy not in join_node.out_data_vars:
                    qmc__jmft = 0
                right_key_in_output.append(qmc__jmft)
            if qmc__jmft:
                ycn__aop.append(_get_out_col_var(pejh__ruwe, False))
    if join_node.indicator:
        ycn__aop.append(_get_out_col_var('_merge', False))
    zjg__povv = [('t3_c' + str(bklq__ekvh)) for bklq__ekvh in range(len(
        ycn__aop))]
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel, 'pd.merge_asof requires both left and right to be replicated or distributed'
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(optional_column, left_key_names,
            right_key_names, left_key_types, right_key_types,
            left_other_names, right_other_names, left_other_types,
            right_other_types, join_node.vect_same_key, left_key_in_output,
            right_key_in_output, join_node.is_left, join_node.is_right,
            join_node.is_join, left_parallel, right_parallel, glbs, [
            typemap[fdvx__ekc.name] for fdvx__ekc in ycn__aop], join_node.
            loc, join_node.indicator, join_node.is_na_equal,
            general_cond_cfunc, left_col_nums, right_col_nums)
    if join_node.how == 'asof':
        for bklq__ekvh in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(bklq__ekvh,
                bklq__ekvh)
        for bklq__ekvh in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                bklq__ekvh, bklq__ekvh)
        for bklq__ekvh in range(n_keys):
            func_text += (
                f'    t1_keys_{bklq__ekvh} = out_t1_keys[{bklq__ekvh}]\n')
        for bklq__ekvh in range(n_keys):
            func_text += (
                f'    t2_keys_{bklq__ekvh} = out_t2_keys[{bklq__ekvh}]\n')
    idx = 0
    if optional_column:
        func_text += f'    {zjg__povv[idx]} = opti_0\n'
        idx += 1
    zmwn__qalod = 0
    vzbm__uyps = set(left_col_nums)
    ydfqc__igq = set(right_col_nums)
    for bklq__ekvh in range(n_keys):
        if left_key_in_output[bklq__ekvh]:
            func_text += f'    {zjg__povv[idx]} = t1_keys_{bklq__ekvh}\n'
            idx += 1
    for bklq__ekvh in range(n_keys):
        if not join_node.vect_same_key[bklq__ekvh] and not join_node.is_join:
            if right_key_in_output[zmwn__qalod]:
                func_text += f'    {zjg__povv[idx]} = t2_keys_{bklq__ekvh}\n'
                idx += 1
            zmwn__qalod += 1
    unx__wkyr = n_keys
    gngg__epr = unx__wkyr
    axg__nhxb = zmwn__qalod
    for bklq__ekvh in range(len(left_other_names)):
        aix__zmi = True
        if bklq__ekvh + gngg__epr in vzbm__uyps:
            aix__zmi = left_key_in_output[unx__wkyr]
            unx__wkyr += 1
        if aix__zmi:
            func_text += f'    {zjg__povv[idx]} = left_{bklq__ekvh}\n'
            idx += 1
    for bklq__ekvh in range(len(right_other_names)):
        aix__zmi = True
        if bklq__ekvh + axg__nhxb in ydfqc__igq:
            aix__zmi = right_key_in_output[zmwn__qalod]
            zmwn__qalod += 1
        if aix__zmi:
            func_text += f'    {zjg__povv[idx]} = right_{bklq__ekvh}\n'
            idx += 1
    if join_node.indicator:
        func_text += f'    {zjg__povv[idx]} = indicator_col\n'
        idx += 1
    tsqx__cvhlf = {}
    exec(func_text, {}, tsqx__cvhlf)
    rhdy__jmnt = tsqx__cvhlf['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr, 'key_in_output': np.array
        (left_key_in_output + right_key_in_output, dtype=np.bool_)})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    aghj__tzhz = compile_to_numba_ir(rhdy__jmnt, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=nwi__occpp, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(aghj__tzhz, ydwf__tslun)
    sojv__ygk = aghj__tzhz.body[:-3]
    for bklq__ekvh in range(len(ycn__aop)):
        sojv__ygk[-len(ycn__aop) + bklq__ekvh].target = ycn__aop[bklq__ekvh]
    return sojv__ygk


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    snec__qzfw = next_label()
    xgtc__lrchw = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    ojaib__vco = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{snec__qzfw}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        xgtc__lrchw, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        ojaib__vco, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    tsqx__cvhlf = {}
    exec(func_text, table_getitem_funcs, tsqx__cvhlf)
    gazoe__mdu = tsqx__cvhlf[f'bodo_join_gen_cond{snec__qzfw}']
    ags__kgy = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    jot__towea = numba.cfunc(ags__kgy, nopython=True)(gazoe__mdu)
    join_gen_cond_cfunc[jot__towea.native_name] = jot__towea
    join_gen_cond_cfunc_addr[jot__towea.native_name] = jot__towea.address
    return jot__towea, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    kjwyu__jxuu = []
    for jkyh__gamf, abeh__pulhj in col_to_ind.items():
        cname = f'({table_name}.{jkyh__gamf})'
        if cname not in expr:
            continue
        fsod__qqr = f'getitem_{table_name}_val_{abeh__pulhj}'
        nzzq__baid = f'_bodo_{table_name}_val_{abeh__pulhj}'
        ztt__ezwmb = typemap[col_vars[jkyh__gamf].name]
        if is_str_arr_type(ztt__ezwmb):
            func_text += f"""  {nzzq__baid}, {nzzq__baid}_size = {fsod__qqr}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {nzzq__baid} = bodo.libs.str_arr_ext.decode_utf8({nzzq__baid}, {nzzq__baid}_size)
"""
        else:
            func_text += (
                f'  {nzzq__baid} = {fsod__qqr}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[fsod__qqr
            ] = bodo.libs.array._gen_row_access_intrinsic(ztt__ezwmb,
            abeh__pulhj)
        expr = expr.replace(cname, nzzq__baid)
        uwao__uryd = f'({na_check_name}.{table_name}.{jkyh__gamf})'
        if uwao__uryd in expr:
            qca__lbgq = f'nacheck_{table_name}_val_{abeh__pulhj}'
            byj__zro = f'_bodo_isna_{table_name}_val_{abeh__pulhj}'
            if (isinstance(ztt__ezwmb, bodo.libs.int_arr_ext.
                IntegerArrayType) or ztt__ezwmb == bodo.libs.bool_arr_ext.
                boolean_array or is_str_arr_type(ztt__ezwmb)):
                func_text += f"""  {byj__zro} = {qca__lbgq}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {byj__zro} = {qca__lbgq}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[qca__lbgq
                ] = bodo.libs.array._gen_row_na_check_intrinsic(ztt__ezwmb,
                abeh__pulhj)
            expr = expr.replace(uwao__uryd, byj__zro)
        if abeh__pulhj >= n_keys:
            kjwyu__jxuu.append(abeh__pulhj)
    return expr, func_text, kjwyu__jxuu


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {jkyh__gamf: bklq__ekvh for bklq__ekvh, jkyh__gamf in
        enumerate(key_names)}
    bklq__ekvh = n_keys
    for jkyh__gamf in sorted(col_vars, key=lambda a: str(a)):
        if jkyh__gamf in col_to_ind:
            continue
        col_to_ind[jkyh__gamf] = bklq__ekvh
        bklq__ekvh += 1
    return col_to_ind


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as jhep__kwhz:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    kjes__syi = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[fdvx__ekc.name] in kjes__syi for
        fdvx__ekc in join_node.left_vars.values())
    right_parallel = all(array_dists[fdvx__ekc.name] in kjes__syi for
        fdvx__ekc in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[fdvx__ekc.name] in kjes__syi for
            fdvx__ekc in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[fdvx__ekc.name] in kjes__syi for
            fdvx__ekc in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[fdvx__ekc.name] in kjes__syi for fdvx__ekc in
            join_node.out_data_vars.values())
    return left_parallel, right_parallel


def _gen_local_hash_join(optional_column, left_key_names, right_key_names,
    left_key_types, right_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, vect_same_key, left_key_in_output,
    right_key_in_output, is_left, is_right, is_join, left_parallel,
    right_parallel, glbs, out_types, loc, indicator, is_na_equal,
    general_cond_cfunc, left_col_nums, right_col_nums):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    vzbm__uyps = set(left_col_nums)
    ydfqc__igq = set(right_col_nums)
    dcdc__mvb = []
    for bklq__ekvh in range(len(left_key_names)):
        if left_key_in_output[bklq__ekvh]:
            ezx__mulb = _match_join_key_types(left_key_types[bklq__ekvh],
                right_key_types[bklq__ekvh], loc)
            dcdc__mvb.append(needs_typechange(ezx__mulb, is_right,
                vect_same_key[bklq__ekvh]))
    nnlvx__ngzlq = len(left_key_names)
    alg__piu = 0
    gngg__epr = nnlvx__ngzlq
    for bklq__ekvh in range(len(left_other_names)):
        aix__zmi = True
        if bklq__ekvh + gngg__epr in vzbm__uyps:
            aix__zmi = left_key_in_output[nnlvx__ngzlq]
            nnlvx__ngzlq += 1
        if aix__zmi:
            dcdc__mvb.append(needs_typechange(left_other_types[bklq__ekvh],
                is_right, False))
    for bklq__ekvh in range(len(right_key_names)):
        if not vect_same_key[bklq__ekvh] and not is_join:
            if right_key_in_output[alg__piu]:
                ezx__mulb = _match_join_key_types(left_key_types[bklq__ekvh
                    ], right_key_types[bklq__ekvh], loc)
                dcdc__mvb.append(needs_typechange(ezx__mulb, is_left, False))
            alg__piu += 1
    axg__nhxb = alg__piu
    for bklq__ekvh in range(len(right_other_names)):
        aix__zmi = True
        if bklq__ekvh + axg__nhxb in ydfqc__igq:
            aix__zmi = right_key_in_output[alg__piu]
            alg__piu += 1
        if aix__zmi:
            dcdc__mvb.append(needs_typechange(right_other_types[bklq__ekvh],
                is_left, False))

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                vbvyt__fieyt = IntDtype(in_type.dtype).name
                assert vbvyt__fieyt.endswith('Dtype()')
                vbvyt__fieyt = vbvyt__fieyt[:-7]
                tebjd__fjqna = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{vbvyt__fieyt}"))
"""
                pih__fiawm = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                tebjd__fjqna = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                pih__fiawm = f'typ_{idx}'
        elif in_type == bodo.string_array_type:
            tebjd__fjqna = (
                f'    typ_{idx} = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)\n'
                )
            pih__fiawm = f'typ_{idx}'
        else:
            tebjd__fjqna = ''
            pih__fiawm = in_name
        return tebjd__fjqna, pih__fiawm
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    gvu__foy = []
    for bklq__ekvh in range(n_keys):
        gvu__foy.append('t1_keys[{}]'.format(bklq__ekvh))
    for bklq__ekvh in range(len(left_other_names)):
        gvu__foy.append('data_left[{}]'.format(bklq__ekvh))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in gvu__foy))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    nspct__awtup = []
    for bklq__ekvh in range(n_keys):
        nspct__awtup.append('t2_keys[{}]'.format(bklq__ekvh))
    for bklq__ekvh in range(len(right_other_names)):
        nspct__awtup.append('data_right[{}]'.format(bklq__ekvh))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in nspct__awtup))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        wluj__pknhh else '0' for wluj__pknhh in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if wluj__pknhh else '0' for wluj__pknhh in dcdc__mvb))
    func_text += f"""    left_table_cond_columns = np.array({left_col_nums if len(left_col_nums) > 0 else [-1]}, dtype=np.int64)
"""
    func_text += f"""    right_table_cond_columns = np.array({right_col_nums if len(right_col_nums) > 0 else [-1]}, dtype=np.int64)
"""
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, key_in_output.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {})
"""
        .format(left_parallel, right_parallel, n_keys, len(left_other_names
        ), len(right_other_names), is_left, is_right, is_join,
        optional_column, indicator, is_na_equal, len(left_col_nums), len(
        right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    idx = 0
    if optional_column:
        ueocz__lochv = get_out_type(idx, out_types[idx], 'opti_c0', False, 
            False)
        func_text += ueocz__lochv[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        func_text += f"""    opti_0 = info_to_array(info_from_table(out_table, {idx}), {ueocz__lochv[1]})
"""
        idx += 1
    for bklq__ekvh, zoy__fncy in enumerate(left_key_names):
        if left_key_in_output[bklq__ekvh]:
            ezx__mulb = _match_join_key_types(left_key_types[bklq__ekvh],
                right_key_types[bklq__ekvh], loc)
            ueocz__lochv = get_out_type(idx, ezx__mulb,
                f't1_keys[{bklq__ekvh}]', is_right, vect_same_key[bklq__ekvh])
            func_text += ueocz__lochv[0]
            glbs[f'out_type_{idx}'] = out_types[idx]
            if ezx__mulb != left_key_types[bklq__ekvh] and left_key_types[
                bklq__ekvh] != bodo.dict_str_arr_type:
                func_text += f"""    t1_keys_{bklq__ekvh} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {ueocz__lochv[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t1_keys_{bklq__ekvh} = info_to_array(info_from_table(out_table, {idx}), {ueocz__lochv[1]})
"""
            idx += 1
    unx__wkyr = len(left_key_names)
    zmwn__qalod = 0
    for bklq__ekvh, zoy__fncy in enumerate(left_other_names):
        aix__zmi = True
        if bklq__ekvh + gngg__epr in vzbm__uyps:
            aix__zmi = left_key_in_output[unx__wkyr]
            unx__wkyr += 1
        if aix__zmi:
            ueocz__lochv = get_out_type(idx, left_other_types[bklq__ekvh],
                zoy__fncy, is_right, False)
            func_text += ueocz__lochv[0]
            func_text += (
                '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(bklq__ekvh, idx, ueocz__lochv[1]))
            idx += 1
    for bklq__ekvh, zoy__fncy in enumerate(right_key_names):
        if not vect_same_key[bklq__ekvh] and not is_join:
            if right_key_in_output[zmwn__qalod]:
                ezx__mulb = _match_join_key_types(left_key_types[bklq__ekvh
                    ], right_key_types[bklq__ekvh], loc)
                ueocz__lochv = get_out_type(idx, ezx__mulb,
                    f't2_keys[{bklq__ekvh}]', is_left, False)
                func_text += ueocz__lochv[0]
                glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)
                    ]
                if ezx__mulb != right_key_types[bklq__ekvh
                    ] and right_key_types[bklq__ekvh
                    ] != bodo.dict_str_arr_type:
                    func_text += f"""    t2_keys_{bklq__ekvh} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {ueocz__lochv[1]}), out_type_{idx})
"""
                else:
                    func_text += f"""    t2_keys_{bklq__ekvh} = info_to_array(info_from_table(out_table, {idx}), {ueocz__lochv[1]})
"""
                idx += 1
            zmwn__qalod += 1
    for bklq__ekvh, zoy__fncy in enumerate(right_other_names):
        aix__zmi = True
        if bklq__ekvh + axg__nhxb in ydfqc__igq:
            aix__zmi = right_key_in_output[zmwn__qalod]
            zmwn__qalod += 1
        if aix__zmi:
            ueocz__lochv = get_out_type(idx, right_other_types[bklq__ekvh],
                zoy__fncy, is_left, False)
            func_text += ueocz__lochv[0]
            func_text += (
                '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(bklq__ekvh, idx, ueocz__lochv[1]))
            idx += 1
    if indicator:
        func_text += f"""    typ_{idx} = pd.Categorical(values=['both'], categories=('left_only', 'right_only', 'both'))
"""
        func_text += f"""    indicator_col = info_to_array(info_from_table(out_table, {idx}), typ_{idx})
"""
        idx += 1
    func_text += '    delete_table(out_table)\n'
    return func_text


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    mmqe__dan = bodo.libs.distributed_api.get_size()
    msazg__kqkew = np.empty(mmqe__dan, left_key_arrs[0].dtype)
    latgk__rlwzc = np.empty(mmqe__dan, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(msazg__kqkew, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(latgk__rlwzc, left_key_arrs[0][-1])
    vny__nao = np.zeros(mmqe__dan, np.int32)
    dsdu__cdu = np.zeros(mmqe__dan, np.int32)
    laasg__qxn = np.zeros(mmqe__dan, np.int32)
    hymtw__sixlt = right_key_arrs[0][0]
    dnbd__ach = right_key_arrs[0][-1]
    scz__qyy = -1
    bklq__ekvh = 0
    while bklq__ekvh < mmqe__dan - 1 and latgk__rlwzc[bklq__ekvh
        ] < hymtw__sixlt:
        bklq__ekvh += 1
    while bklq__ekvh < mmqe__dan and msazg__kqkew[bklq__ekvh] <= dnbd__ach:
        scz__qyy, jsts__vdi = _count_overlap(right_key_arrs[0],
            msazg__kqkew[bklq__ekvh], latgk__rlwzc[bklq__ekvh])
        if scz__qyy != 0:
            scz__qyy -= 1
            jsts__vdi += 1
        vny__nao[bklq__ekvh] = jsts__vdi
        dsdu__cdu[bklq__ekvh] = scz__qyy
        bklq__ekvh += 1
    while bklq__ekvh < mmqe__dan:
        vny__nao[bklq__ekvh] = 1
        dsdu__cdu[bklq__ekvh] = len(right_key_arrs[0]) - 1
        bklq__ekvh += 1
    bodo.libs.distributed_api.alltoall(vny__nao, laasg__qxn, 1)
    mqygf__zusrk = laasg__qxn.sum()
    xzhzn__mnadm = np.empty(mqygf__zusrk, right_key_arrs[0].dtype)
    xsgfz__ryk = alloc_arr_tup(mqygf__zusrk, right_data)
    pekqr__ecab = bodo.ir.join.calc_disp(laasg__qxn)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], xzhzn__mnadm,
        vny__nao, laasg__qxn, dsdu__cdu, pekqr__ecab)
    bodo.libs.distributed_api.alltoallv_tup(right_data, xsgfz__ryk,
        vny__nao, laasg__qxn, dsdu__cdu, pekqr__ecab)
    return (xzhzn__mnadm,), xsgfz__ryk


@numba.njit
def _count_overlap(r_key_arr, start, end):
    jsts__vdi = 0
    scz__qyy = 0
    irghq__hoq = 0
    while irghq__hoq < len(r_key_arr) and r_key_arr[irghq__hoq] < start:
        scz__qyy += 1
        irghq__hoq += 1
    while irghq__hoq < len(r_key_arr) and start <= r_key_arr[irghq__hoq
        ] <= end:
        irghq__hoq += 1
        jsts__vdi += 1
    return scz__qyy, jsts__vdi


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    rmo__mjk = np.empty_like(arr)
    rmo__mjk[0] = 0
    for bklq__ekvh in range(1, len(arr)):
        rmo__mjk[bklq__ekvh] = rmo__mjk[bklq__ekvh - 1] + arr[bklq__ekvh - 1]
    return rmo__mjk


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    glq__rtmk = len(left_keys[0])
    uef__yanco = len(right_keys[0])
    pghi__pup = alloc_arr_tup(glq__rtmk, left_keys)
    ankvu__ogfrm = alloc_arr_tup(glq__rtmk, right_keys)
    ozv__bwo = alloc_arr_tup(glq__rtmk, data_left)
    wje__ykg = alloc_arr_tup(glq__rtmk, data_right)
    jzk__ezvg = 0
    lig__wmsbs = 0
    for jzk__ezvg in range(glq__rtmk):
        if lig__wmsbs < 0:
            lig__wmsbs = 0
        while lig__wmsbs < uef__yanco and getitem_arr_tup(right_keys,
            lig__wmsbs) <= getitem_arr_tup(left_keys, jzk__ezvg):
            lig__wmsbs += 1
        lig__wmsbs -= 1
        setitem_arr_tup(pghi__pup, jzk__ezvg, getitem_arr_tup(left_keys,
            jzk__ezvg))
        setitem_arr_tup(ozv__bwo, jzk__ezvg, getitem_arr_tup(data_left,
            jzk__ezvg))
        if lig__wmsbs >= 0:
            setitem_arr_tup(ankvu__ogfrm, jzk__ezvg, getitem_arr_tup(
                right_keys, lig__wmsbs))
            setitem_arr_tup(wje__ykg, jzk__ezvg, getitem_arr_tup(data_right,
                lig__wmsbs))
        else:
            bodo.libs.array_kernels.setna_tup(ankvu__ogfrm, jzk__ezvg)
            bodo.libs.array_kernels.setna_tup(wje__ykg, jzk__ezvg)
    return pghi__pup, ankvu__ogfrm, ozv__bwo, wje__ykg
