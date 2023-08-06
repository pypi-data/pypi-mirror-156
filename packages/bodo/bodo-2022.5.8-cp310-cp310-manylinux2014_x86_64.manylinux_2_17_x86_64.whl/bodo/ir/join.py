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
        yeb__ntqm = func.signature
        yjfa__xcwsi = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        wggo__enwip = cgutils.get_or_insert_function(builder.module,
            yjfa__xcwsi, sym._literal_value)
        builder.call(wggo__enwip, [context.get_constant_null(yeb__ntqm.args
            [0]), context.get_constant_null(yeb__ntqm.args[1]), context.
            get_constant_null(yeb__ntqm.args[2]), context.get_constant_null
            (yeb__ntqm.args[3]), context.get_constant_null(yeb__ntqm.args[4
            ]), context.get_constant_null(yeb__ntqm.args[5]), context.
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
            self.left_cond_cols = set(lpq__uhnky for lpq__uhnky in
                left_vars.keys() if f'(left.{lpq__uhnky})' in gen_cond_expr)
            self.right_cond_cols = set(lpq__uhnky for lpq__uhnky in
                right_vars.keys() if f'(right.{lpq__uhnky})' in gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        gsxyo__yxp = self.left_key_set & self.right_key_set
        puw__fxpxo = set(left_vars.keys()) & set(right_vars.keys())
        ttqfc__jrxdu = puw__fxpxo - gsxyo__yxp
        vect_same_key = []
        n_keys = len(left_keys)
        for hfkg__fhgvd in range(n_keys):
            iboi__yqtb = left_keys[hfkg__fhgvd]
            qbsh__qlff = right_keys[hfkg__fhgvd]
            vect_same_key.append(iboi__yqtb == qbsh__qlff)
        self.vect_same_key = vect_same_key
        self.column_origins = {}
        for lpq__uhnky in left_vars.keys():
            ehnp__sfqw = 'left', lpq__uhnky
            if lpq__uhnky in ttqfc__jrxdu:
                vivb__qpk = str(lpq__uhnky) + suffix_left
                self.column_origins[vivb__qpk] = ehnp__sfqw
                if (right_index and not left_index and lpq__uhnky in self.
                    left_key_set):
                    self.column_origins[lpq__uhnky] = ehnp__sfqw
            else:
                self.column_origins[lpq__uhnky] = ehnp__sfqw
        for lpq__uhnky in right_vars.keys():
            ehnp__sfqw = 'right', lpq__uhnky
            if lpq__uhnky in ttqfc__jrxdu:
                dij__uhlyx = str(lpq__uhnky) + suffix_right
                self.column_origins[dij__uhlyx] = ehnp__sfqw
                if (left_index and not right_index and lpq__uhnky in self.
                    right_key_set):
                    self.column_origins[lpq__uhnky] = ehnp__sfqw
            else:
                self.column_origins[lpq__uhnky] = ehnp__sfqw
        if '$_bodo_index_' in ttqfc__jrxdu:
            ttqfc__jrxdu.remove('$_bodo_index_')
        self.add_suffix = ttqfc__jrxdu

    def __repr__(self):
        dheok__ylc = ''
        for lpq__uhnky, cwsr__dfnvc in self.out_data_vars.items():
            dheok__ylc += "'{}':{}, ".format(lpq__uhnky, cwsr__dfnvc.name)
        wbnjg__vfetp = '{}{{{}}}'.format(self.df_out, dheok__ylc)
        nxmu__mexs = ''
        for lpq__uhnky, cwsr__dfnvc in self.left_vars.items():
            nxmu__mexs += "'{}':{}, ".format(lpq__uhnky, cwsr__dfnvc.name)
        jjn__tpmet = '{}{{{}}}'.format(self.left_df, nxmu__mexs)
        nxmu__mexs = ''
        for lpq__uhnky, cwsr__dfnvc in self.right_vars.items():
            nxmu__mexs += "'{}':{}, ".format(lpq__uhnky, cwsr__dfnvc.name)
        okpfe__hxd = '{}{{{}}}'.format(self.right_df, nxmu__mexs)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, wbnjg__vfetp, jjn__tpmet, okpfe__hxd)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    idpf__ymsw = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    phovm__ffrad = []
    rxld__jdwv = list(join_node.left_vars.values())
    for niwd__sillt in rxld__jdwv:
        ndbx__ous = typemap[niwd__sillt.name]
        ekh__jnxk = equiv_set.get_shape(niwd__sillt)
        if ekh__jnxk:
            phovm__ffrad.append(ekh__jnxk[0])
    if len(phovm__ffrad) > 1:
        equiv_set.insert_equiv(*phovm__ffrad)
    phovm__ffrad = []
    rxld__jdwv = list(join_node.right_vars.values())
    for niwd__sillt in rxld__jdwv:
        ndbx__ous = typemap[niwd__sillt.name]
        ekh__jnxk = equiv_set.get_shape(niwd__sillt)
        if ekh__jnxk:
            phovm__ffrad.append(ekh__jnxk[0])
    if len(phovm__ffrad) > 1:
        equiv_set.insert_equiv(*phovm__ffrad)
    phovm__ffrad = []
    for niwd__sillt in join_node.out_data_vars.values():
        ndbx__ous = typemap[niwd__sillt.name]
        uvmb__mcmpd = array_analysis._gen_shape_call(equiv_set, niwd__sillt,
            ndbx__ous.ndim, None, idpf__ymsw)
        equiv_set.insert_equiv(niwd__sillt, uvmb__mcmpd)
        phovm__ffrad.append(uvmb__mcmpd[0])
        equiv_set.define(niwd__sillt, set())
    if len(phovm__ffrad) > 1:
        equiv_set.insert_equiv(*phovm__ffrad)
    return [], idpf__ymsw


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    pzy__mlwmo = Distribution.OneD
    jfb__conkj = Distribution.OneD
    for niwd__sillt in join_node.left_vars.values():
        pzy__mlwmo = Distribution(min(pzy__mlwmo.value, array_dists[
            niwd__sillt.name].value))
    for niwd__sillt in join_node.right_vars.values():
        jfb__conkj = Distribution(min(jfb__conkj.value, array_dists[
            niwd__sillt.name].value))
    jagw__mkzl = Distribution.OneD_Var
    for niwd__sillt in join_node.out_data_vars.values():
        if niwd__sillt.name in array_dists:
            jagw__mkzl = Distribution(min(jagw__mkzl.value, array_dists[
                niwd__sillt.name].value))
    plah__qdy = Distribution(min(jagw__mkzl.value, pzy__mlwmo.value))
    imvpa__vhnbu = Distribution(min(jagw__mkzl.value, jfb__conkj.value))
    jagw__mkzl = Distribution(max(plah__qdy.value, imvpa__vhnbu.value))
    for niwd__sillt in join_node.out_data_vars.values():
        array_dists[niwd__sillt.name] = jagw__mkzl
    if jagw__mkzl != Distribution.OneD_Var:
        pzy__mlwmo = jagw__mkzl
        jfb__conkj = jagw__mkzl
    for niwd__sillt in join_node.left_vars.values():
        array_dists[niwd__sillt.name] = pzy__mlwmo
    for niwd__sillt in join_node.right_vars.values():
        array_dists[niwd__sillt.name] = jfb__conkj
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    for bsu__spe, ejnrw__bst in join_node.out_data_vars.items():
        if join_node.indicator and bsu__spe == '_merge':
            continue
        if not bsu__spe in join_node.column_origins:
            raise BodoError('join(): The variable ' + bsu__spe +
                ' is absent from the output')
        mih__euiu = join_node.column_origins[bsu__spe]
        if mih__euiu[0] == 'left':
            niwd__sillt = join_node.left_vars[mih__euiu[1]]
        else:
            niwd__sillt = join_node.right_vars[mih__euiu[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=ejnrw__bst.
            name, src=niwd__sillt.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for pwda__mbldw in list(join_node.left_vars.keys()):
        join_node.left_vars[pwda__mbldw] = visit_vars_inner(join_node.
            left_vars[pwda__mbldw], callback, cbdata)
    for pwda__mbldw in list(join_node.right_vars.keys()):
        join_node.right_vars[pwda__mbldw] = visit_vars_inner(join_node.
            right_vars[pwda__mbldw], callback, cbdata)
    for pwda__mbldw in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[pwda__mbldw] = visit_vars_inner(join_node.
            out_data_vars[pwda__mbldw], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    uped__efp = []
    sgj__jwz = True
    for pwda__mbldw, niwd__sillt in join_node.out_data_vars.items():
        if niwd__sillt.name in lives:
            sgj__jwz = False
            continue
        uped__efp.append(pwda__mbldw)
        if join_node.indicator and pwda__mbldw == '_merge':
            join_node.indicator = False
            continue
        if pwda__mbldw == '$_bodo_index_':
            jmlz__nat = pwda__mbldw
        else:
            mey__nlqef, jmlz__nat = join_node.column_origins[pwda__mbldw]
        if (pwda__mbldw == '$_bodo_index_' and pwda__mbldw in join_node.
            left_vars):
            mey__nlqef = 'left'
        if (mey__nlqef == 'left' and jmlz__nat not in join_node.
            left_key_set and jmlz__nat not in join_node.left_cond_cols):
            join_node.left_vars.pop(jmlz__nat)
        if (pwda__mbldw == '$_bodo_index_' and pwda__mbldw in join_node.
            right_vars):
            mey__nlqef = 'right'
        if (mey__nlqef == 'right' and jmlz__nat not in join_node.
            right_key_set and jmlz__nat not in join_node.right_cond_cols):
            join_node.right_vars.pop(jmlz__nat)
    for cname in uped__efp:
        join_node.out_data_vars.pop(cname)
    if sgj__jwz:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({cwsr__dfnvc.name for cwsr__dfnvc in join_node.left_vars
        .values()})
    use_set.update({cwsr__dfnvc.name for cwsr__dfnvc in join_node.
        right_vars.values()})
    def_set.update({cwsr__dfnvc.name for cwsr__dfnvc in join_node.
        out_data_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    tyzg__vyzsw = set(cwsr__dfnvc.name for cwsr__dfnvc in join_node.
        out_data_vars.values())
    return set(), tyzg__vyzsw


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for pwda__mbldw in list(join_node.left_vars.keys()):
        join_node.left_vars[pwda__mbldw] = replace_vars_inner(join_node.
            left_vars[pwda__mbldw], var_dict)
    for pwda__mbldw in list(join_node.right_vars.keys()):
        join_node.right_vars[pwda__mbldw] = replace_vars_inner(join_node.
            right_vars[pwda__mbldw], var_dict)
    for pwda__mbldw in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[pwda__mbldw] = replace_vars_inner(join_node
            .out_data_vars[pwda__mbldw], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for niwd__sillt in join_node.out_data_vars.values():
        definitions[niwd__sillt.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    urq__ypcx = tuple(join_node.left_vars[lpq__uhnky] for lpq__uhnky in
        join_node.left_keys)
    tng__wwaq = tuple(join_node.right_vars[lpq__uhnky] for lpq__uhnky in
        join_node.right_keys)
    duiri__uejij = ()
    xkiz__tmopq = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        vju__khj = join_node.right_keys[0]
        if (vju__khj in join_node.add_suffix and vju__khj in join_node.
            out_data_vars):
            xkiz__tmopq = vju__khj,
            duiri__uejij = join_node.right_vars[vju__khj],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        vju__khj = join_node.left_keys[0]
        if (vju__khj in join_node.add_suffix and vju__khj in join_node.
            out_data_vars):
            xkiz__tmopq = vju__khj,
            duiri__uejij = join_node.left_vars[vju__khj],
            optional_column = True
    pdjk__kmkjq = [join_node.out_data_vars[cname] for cname in xkiz__tmopq]
    loh__bumgf = tuple(cwsr__dfnvc for baqn__lwbyk, cwsr__dfnvc in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if 
        baqn__lwbyk not in join_node.left_key_set)
    qpzi__yueic = tuple(cwsr__dfnvc for baqn__lwbyk, cwsr__dfnvc in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if 
        baqn__lwbyk not in join_node.right_key_set)
    tsr__rma = duiri__uejij + urq__ypcx + tng__wwaq + loh__bumgf + qpzi__yueic
    hmlq__vpupz = tuple(typemap[cwsr__dfnvc.name] for cwsr__dfnvc in tsr__rma)
    yrwih__ysr = tuple('opti_c' + str(zkyc__ftnhb) for zkyc__ftnhb in range
        (len(duiri__uejij)))
    left_other_names = tuple('t1_c' + str(zkyc__ftnhb) for zkyc__ftnhb in
        range(len(loh__bumgf)))
    right_other_names = tuple('t2_c' + str(zkyc__ftnhb) for zkyc__ftnhb in
        range(len(qpzi__yueic)))
    left_other_types = tuple([typemap[lpq__uhnky.name] for lpq__uhnky in
        loh__bumgf])
    right_other_types = tuple([typemap[lpq__uhnky.name] for lpq__uhnky in
        qpzi__yueic])
    left_key_names = tuple('t1_key' + str(zkyc__ftnhb) for zkyc__ftnhb in
        range(n_keys))
    right_key_names = tuple('t2_key' + str(zkyc__ftnhb) for zkyc__ftnhb in
        range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(yrwih__ysr[
        0]) if len(yrwih__ysr) == 1 else '', ','.join(left_key_names), ','.
        join(right_key_names), ','.join(left_other_names), ',' if len(
        left_other_names) != 0 else '', ','.join(right_other_names))
    left_key_types = tuple(typemap[cwsr__dfnvc.name] for cwsr__dfnvc in
        urq__ypcx)
    right_key_types = tuple(typemap[cwsr__dfnvc.name] for cwsr__dfnvc in
        tng__wwaq)
    for zkyc__ftnhb in range(n_keys):
        glbs[f'key_type_{zkyc__ftnhb}'] = _match_join_key_types(left_key_types
            [zkyc__ftnhb], right_key_types[zkyc__ftnhb], loc)
    func_text += '    t1_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({left_key_names[zkyc__ftnhb]}, key_type_{zkyc__ftnhb})'
         for zkyc__ftnhb in range(n_keys)))
    func_text += '    t2_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({right_key_names[zkyc__ftnhb]}, key_type_{zkyc__ftnhb})'
         for zkyc__ftnhb in range(n_keys)))
    func_text += '    data_left = ({}{})\n'.format(','.join(
        left_other_names), ',' if len(left_other_names) != 0 else '')
    func_text += '    data_right = ({}{})\n'.format(','.join(
        right_other_names), ',' if len(right_other_names) != 0 else '')
    left_key_in_output = []
    right_key_in_output = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            rlcfh__hox = str(cname) + join_node.suffix_left
        else:
            rlcfh__hox = cname
        if rlcfh__hox in join_node.out_data_vars:
            pdjk__kmkjq.append(join_node.out_data_vars[rlcfh__hox])
            oxsz__tfta = 1
        else:
            oxsz__tfta = 0
        left_key_in_output.append(oxsz__tfta)
    for zkyc__ftnhb, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[zkyc__ftnhb] and not join_node.is_join:
            if cname in join_node.add_suffix:
                rlcfh__hox = str(cname) + join_node.suffix_right
            else:
                rlcfh__hox = cname
            if rlcfh__hox in join_node.out_data_vars:
                pdjk__kmkjq.append(join_node.out_data_vars[rlcfh__hox])
                oxsz__tfta = 1
            else:
                oxsz__tfta = 0
            right_key_in_output.append(oxsz__tfta)

    def _get_out_col_name(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                rlcfh__hox = str(cname) + join_node.suffix_left
            else:
                rlcfh__hox = str(cname) + join_node.suffix_right
        else:
            rlcfh__hox = cname
        return rlcfh__hox

    def _get_out_col_var(cname, is_left):
        rlcfh__hox = _get_out_col_name(cname, is_left)
        return join_node.out_data_vars[rlcfh__hox]
    for baqn__lwbyk in sorted(join_node.left_vars.keys(), key=lambda a: str(a)
        ):
        if baqn__lwbyk not in join_node.left_key_set:
            oxsz__tfta = 1
            if baqn__lwbyk in join_node.left_cond_cols:
                rlcfh__hox = _get_out_col_name(baqn__lwbyk, True)
                if rlcfh__hox not in join_node.out_data_vars:
                    oxsz__tfta = 0
                left_key_in_output.append(oxsz__tfta)
            if oxsz__tfta:
                pdjk__kmkjq.append(_get_out_col_var(baqn__lwbyk, True))
    for baqn__lwbyk in sorted(join_node.right_vars.keys(), key=lambda a: str(a)
        ):
        if baqn__lwbyk not in join_node.right_key_set:
            oxsz__tfta = 1
            if baqn__lwbyk in join_node.right_cond_cols:
                rlcfh__hox = _get_out_col_name(baqn__lwbyk, False)
                if rlcfh__hox not in join_node.out_data_vars:
                    oxsz__tfta = 0
                right_key_in_output.append(oxsz__tfta)
            if oxsz__tfta:
                pdjk__kmkjq.append(_get_out_col_var(baqn__lwbyk, False))
    if join_node.indicator:
        pdjk__kmkjq.append(_get_out_col_var('_merge', False))
    evan__ljx = [('t3_c' + str(zkyc__ftnhb)) for zkyc__ftnhb in range(len(
        pdjk__kmkjq))]
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
            typemap[cwsr__dfnvc.name] for cwsr__dfnvc in pdjk__kmkjq],
            join_node.loc, join_node.indicator, join_node.is_na_equal,
            general_cond_cfunc, left_col_nums, right_col_nums)
    if join_node.how == 'asof':
        for zkyc__ftnhb in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(zkyc__ftnhb
                , zkyc__ftnhb)
        for zkyc__ftnhb in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                zkyc__ftnhb, zkyc__ftnhb)
        for zkyc__ftnhb in range(n_keys):
            func_text += (
                f'    t1_keys_{zkyc__ftnhb} = out_t1_keys[{zkyc__ftnhb}]\n')
        for zkyc__ftnhb in range(n_keys):
            func_text += (
                f'    t2_keys_{zkyc__ftnhb} = out_t2_keys[{zkyc__ftnhb}]\n')
    idx = 0
    if optional_column:
        func_text += f'    {evan__ljx[idx]} = opti_0\n'
        idx += 1
    kat__gwbp = 0
    laylv__bvy = set(left_col_nums)
    kwimu__yvojd = set(right_col_nums)
    for zkyc__ftnhb in range(n_keys):
        if left_key_in_output[zkyc__ftnhb]:
            func_text += f'    {evan__ljx[idx]} = t1_keys_{zkyc__ftnhb}\n'
            idx += 1
    for zkyc__ftnhb in range(n_keys):
        if not join_node.vect_same_key[zkyc__ftnhb] and not join_node.is_join:
            if right_key_in_output[kat__gwbp]:
                func_text += f'    {evan__ljx[idx]} = t2_keys_{zkyc__ftnhb}\n'
                idx += 1
            kat__gwbp += 1
    tnye__tsqb = n_keys
    lxxds__ssw = tnye__tsqb
    xtvk__klfm = kat__gwbp
    for zkyc__ftnhb in range(len(left_other_names)):
        jgr__yrec = True
        if zkyc__ftnhb + lxxds__ssw in laylv__bvy:
            jgr__yrec = left_key_in_output[tnye__tsqb]
            tnye__tsqb += 1
        if jgr__yrec:
            func_text += f'    {evan__ljx[idx]} = left_{zkyc__ftnhb}\n'
            idx += 1
    for zkyc__ftnhb in range(len(right_other_names)):
        jgr__yrec = True
        if zkyc__ftnhb + xtvk__klfm in kwimu__yvojd:
            jgr__yrec = right_key_in_output[kat__gwbp]
            kat__gwbp += 1
        if jgr__yrec:
            func_text += f'    {evan__ljx[idx]} = right_{zkyc__ftnhb}\n'
            idx += 1
    if join_node.indicator:
        func_text += f'    {evan__ljx[idx]} = indicator_col\n'
        idx += 1
    okdg__mzeqi = {}
    exec(func_text, {}, okdg__mzeqi)
    dahxf__xted = okdg__mzeqi['f']
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
    amzo__uvfy = compile_to_numba_ir(dahxf__xted, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=hmlq__vpupz, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(amzo__uvfy, tsr__rma)
    zah__vjl = amzo__uvfy.body[:-3]
    for zkyc__ftnhb in range(len(pdjk__kmkjq)):
        zah__vjl[-len(pdjk__kmkjq) + zkyc__ftnhb].target = pdjk__kmkjq[
            zkyc__ftnhb]
    return zah__vjl


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    lfu__ichyt = next_label()
    oeu__tiqc = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    dgt__ubtr = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{lfu__ichyt}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        oeu__tiqc, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        dgt__ubtr, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    okdg__mzeqi = {}
    exec(func_text, table_getitem_funcs, okdg__mzeqi)
    wxuj__uqsyc = okdg__mzeqi[f'bodo_join_gen_cond{lfu__ichyt}']
    miqdh__wnaop = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    qlss__xztjw = numba.cfunc(miqdh__wnaop, nopython=True)(wxuj__uqsyc)
    join_gen_cond_cfunc[qlss__xztjw.native_name] = qlss__xztjw
    join_gen_cond_cfunc_addr[qlss__xztjw.native_name] = qlss__xztjw.address
    return qlss__xztjw, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    nyg__kcik = []
    for lpq__uhnky, vxwp__lqxlj in col_to_ind.items():
        cname = f'({table_name}.{lpq__uhnky})'
        if cname not in expr:
            continue
        jndgw__bvyr = f'getitem_{table_name}_val_{vxwp__lqxlj}'
        mkm__tpy = f'_bodo_{table_name}_val_{vxwp__lqxlj}'
        xmzs__pab = typemap[col_vars[lpq__uhnky].name]
        if is_str_arr_type(xmzs__pab):
            func_text += f"""  {mkm__tpy}, {mkm__tpy}_size = {jndgw__bvyr}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {mkm__tpy} = bodo.libs.str_arr_ext.decode_utf8({mkm__tpy}, {mkm__tpy}_size)
"""
        else:
            func_text += (
                f'  {mkm__tpy} = {jndgw__bvyr}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[jndgw__bvyr
            ] = bodo.libs.array._gen_row_access_intrinsic(xmzs__pab,
            vxwp__lqxlj)
        expr = expr.replace(cname, mkm__tpy)
        fqnzw__dza = f'({na_check_name}.{table_name}.{lpq__uhnky})'
        if fqnzw__dza in expr:
            bqz__fslqo = f'nacheck_{table_name}_val_{vxwp__lqxlj}'
            mpzq__alkv = f'_bodo_isna_{table_name}_val_{vxwp__lqxlj}'
            if (isinstance(xmzs__pab, bodo.libs.int_arr_ext.
                IntegerArrayType) or xmzs__pab == bodo.libs.bool_arr_ext.
                boolean_array or is_str_arr_type(xmzs__pab)):
                func_text += f"""  {mpzq__alkv} = {bqz__fslqo}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {mpzq__alkv} = {bqz__fslqo}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[bqz__fslqo
                ] = bodo.libs.array._gen_row_na_check_intrinsic(xmzs__pab,
                vxwp__lqxlj)
            expr = expr.replace(fqnzw__dza, mpzq__alkv)
        if vxwp__lqxlj >= n_keys:
            nyg__kcik.append(vxwp__lqxlj)
    return expr, func_text, nyg__kcik


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {lpq__uhnky: zkyc__ftnhb for zkyc__ftnhb, lpq__uhnky in
        enumerate(key_names)}
    zkyc__ftnhb = n_keys
    for lpq__uhnky in sorted(col_vars, key=lambda a: str(a)):
        if lpq__uhnky in col_to_ind:
            continue
        col_to_ind[lpq__uhnky] = zkyc__ftnhb
        zkyc__ftnhb += 1
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
    except Exception as trs__uxj:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    ocz__pbkta = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[cwsr__dfnvc.name] in ocz__pbkta for
        cwsr__dfnvc in join_node.left_vars.values())
    right_parallel = all(array_dists[cwsr__dfnvc.name] in ocz__pbkta for
        cwsr__dfnvc in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[cwsr__dfnvc.name] in ocz__pbkta for
            cwsr__dfnvc in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[cwsr__dfnvc.name] in ocz__pbkta for
            cwsr__dfnvc in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[cwsr__dfnvc.name] in ocz__pbkta for
            cwsr__dfnvc in join_node.out_data_vars.values())
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
    laylv__bvy = set(left_col_nums)
    kwimu__yvojd = set(right_col_nums)
    lrxa__sfuad = []
    for zkyc__ftnhb in range(len(left_key_names)):
        if left_key_in_output[zkyc__ftnhb]:
            dqap__jnsc = _match_join_key_types(left_key_types[zkyc__ftnhb],
                right_key_types[zkyc__ftnhb], loc)
            lrxa__sfuad.append(needs_typechange(dqap__jnsc, is_right,
                vect_same_key[zkyc__ftnhb]))
    vil__sxmw = len(left_key_names)
    ezz__xgvf = 0
    lxxds__ssw = vil__sxmw
    for zkyc__ftnhb in range(len(left_other_names)):
        jgr__yrec = True
        if zkyc__ftnhb + lxxds__ssw in laylv__bvy:
            jgr__yrec = left_key_in_output[vil__sxmw]
            vil__sxmw += 1
        if jgr__yrec:
            lrxa__sfuad.append(needs_typechange(left_other_types[
                zkyc__ftnhb], is_right, False))
    for zkyc__ftnhb in range(len(right_key_names)):
        if not vect_same_key[zkyc__ftnhb] and not is_join:
            if right_key_in_output[ezz__xgvf]:
                dqap__jnsc = _match_join_key_types(left_key_types[
                    zkyc__ftnhb], right_key_types[zkyc__ftnhb], loc)
                lrxa__sfuad.append(needs_typechange(dqap__jnsc, is_left, False)
                    )
            ezz__xgvf += 1
    xtvk__klfm = ezz__xgvf
    for zkyc__ftnhb in range(len(right_other_names)):
        jgr__yrec = True
        if zkyc__ftnhb + xtvk__klfm in kwimu__yvojd:
            jgr__yrec = right_key_in_output[ezz__xgvf]
            ezz__xgvf += 1
        if jgr__yrec:
            lrxa__sfuad.append(needs_typechange(right_other_types[
                zkyc__ftnhb], is_left, False))

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                lqat__ebt = IntDtype(in_type.dtype).name
                assert lqat__ebt.endswith('Dtype()')
                lqat__ebt = lqat__ebt[:-7]
                jhcml__ujfs = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{lqat__ebt}"))
"""
                deiw__hhsu = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                jhcml__ujfs = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                deiw__hhsu = f'typ_{idx}'
        elif in_type == bodo.string_array_type:
            jhcml__ujfs = (
                f'    typ_{idx} = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)\n'
                )
            deiw__hhsu = f'typ_{idx}'
        else:
            jhcml__ujfs = ''
            deiw__hhsu = in_name
        return jhcml__ujfs, deiw__hhsu
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    cczi__syeoo = []
    for zkyc__ftnhb in range(n_keys):
        cczi__syeoo.append('t1_keys[{}]'.format(zkyc__ftnhb))
    for zkyc__ftnhb in range(len(left_other_names)):
        cczi__syeoo.append('data_left[{}]'.format(zkyc__ftnhb))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in cczi__syeoo))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    kwq__qjn = []
    for zkyc__ftnhb in range(n_keys):
        kwq__qjn.append('t2_keys[{}]'.format(zkyc__ftnhb))
    for zkyc__ftnhb in range(len(right_other_names)):
        kwq__qjn.append('data_right[{}]'.format(zkyc__ftnhb))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in kwq__qjn))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        vfc__fwo else '0' for vfc__fwo in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if vfc__fwo else '0' for vfc__fwo in lrxa__sfuad))
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
        krfz__svqg = get_out_type(idx, out_types[idx], 'opti_c0', False, False)
        func_text += krfz__svqg[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        func_text += f"""    opti_0 = info_to_array(info_from_table(out_table, {idx}), {krfz__svqg[1]})
"""
        idx += 1
    for zkyc__ftnhb, sdoze__xhp in enumerate(left_key_names):
        if left_key_in_output[zkyc__ftnhb]:
            dqap__jnsc = _match_join_key_types(left_key_types[zkyc__ftnhb],
                right_key_types[zkyc__ftnhb], loc)
            krfz__svqg = get_out_type(idx, dqap__jnsc,
                f't1_keys[{zkyc__ftnhb}]', is_right, vect_same_key[zkyc__ftnhb]
                )
            func_text += krfz__svqg[0]
            glbs[f'out_type_{idx}'] = out_types[idx]
            if dqap__jnsc != left_key_types[zkyc__ftnhb] and left_key_types[
                zkyc__ftnhb] != bodo.dict_str_arr_type:
                func_text += f"""    t1_keys_{zkyc__ftnhb} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {krfz__svqg[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t1_keys_{zkyc__ftnhb} = info_to_array(info_from_table(out_table, {idx}), {krfz__svqg[1]})
"""
            idx += 1
    tnye__tsqb = len(left_key_names)
    kat__gwbp = 0
    for zkyc__ftnhb, sdoze__xhp in enumerate(left_other_names):
        jgr__yrec = True
        if zkyc__ftnhb + lxxds__ssw in laylv__bvy:
            jgr__yrec = left_key_in_output[tnye__tsqb]
            tnye__tsqb += 1
        if jgr__yrec:
            krfz__svqg = get_out_type(idx, left_other_types[zkyc__ftnhb],
                sdoze__xhp, is_right, False)
            func_text += krfz__svqg[0]
            func_text += (
                '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(zkyc__ftnhb, idx, krfz__svqg[1]))
            idx += 1
    for zkyc__ftnhb, sdoze__xhp in enumerate(right_key_names):
        if not vect_same_key[zkyc__ftnhb] and not is_join:
            if right_key_in_output[kat__gwbp]:
                dqap__jnsc = _match_join_key_types(left_key_types[
                    zkyc__ftnhb], right_key_types[zkyc__ftnhb], loc)
                krfz__svqg = get_out_type(idx, dqap__jnsc,
                    f't2_keys[{zkyc__ftnhb}]', is_left, False)
                func_text += krfz__svqg[0]
                glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)
                    ]
                if dqap__jnsc != right_key_types[zkyc__ftnhb
                    ] and right_key_types[zkyc__ftnhb
                    ] != bodo.dict_str_arr_type:
                    func_text += f"""    t2_keys_{zkyc__ftnhb} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {krfz__svqg[1]}), out_type_{idx})
"""
                else:
                    func_text += f"""    t2_keys_{zkyc__ftnhb} = info_to_array(info_from_table(out_table, {idx}), {krfz__svqg[1]})
"""
                idx += 1
            kat__gwbp += 1
    for zkyc__ftnhb, sdoze__xhp in enumerate(right_other_names):
        jgr__yrec = True
        if zkyc__ftnhb + xtvk__klfm in kwimu__yvojd:
            jgr__yrec = right_key_in_output[kat__gwbp]
            kat__gwbp += 1
        if jgr__yrec:
            krfz__svqg = get_out_type(idx, right_other_types[zkyc__ftnhb],
                sdoze__xhp, is_left, False)
            func_text += krfz__svqg[0]
            func_text += (
                '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(zkyc__ftnhb, idx, krfz__svqg[1]))
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
    nwrxu__dco = bodo.libs.distributed_api.get_size()
    qae__bzmi = np.empty(nwrxu__dco, left_key_arrs[0].dtype)
    edbf__yxxp = np.empty(nwrxu__dco, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(qae__bzmi, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(edbf__yxxp, left_key_arrs[0][-1])
    oqam__zrvjp = np.zeros(nwrxu__dco, np.int32)
    wyglc__jpu = np.zeros(nwrxu__dco, np.int32)
    rwke__lauut = np.zeros(nwrxu__dco, np.int32)
    beo__ddesw = right_key_arrs[0][0]
    qlb__hmnht = right_key_arrs[0][-1]
    psr__npd = -1
    zkyc__ftnhb = 0
    while zkyc__ftnhb < nwrxu__dco - 1 and edbf__yxxp[zkyc__ftnhb
        ] < beo__ddesw:
        zkyc__ftnhb += 1
    while zkyc__ftnhb < nwrxu__dco and qae__bzmi[zkyc__ftnhb] <= qlb__hmnht:
        psr__npd, cjz__oxphl = _count_overlap(right_key_arrs[0], qae__bzmi[
            zkyc__ftnhb], edbf__yxxp[zkyc__ftnhb])
        if psr__npd != 0:
            psr__npd -= 1
            cjz__oxphl += 1
        oqam__zrvjp[zkyc__ftnhb] = cjz__oxphl
        wyglc__jpu[zkyc__ftnhb] = psr__npd
        zkyc__ftnhb += 1
    while zkyc__ftnhb < nwrxu__dco:
        oqam__zrvjp[zkyc__ftnhb] = 1
        wyglc__jpu[zkyc__ftnhb] = len(right_key_arrs[0]) - 1
        zkyc__ftnhb += 1
    bodo.libs.distributed_api.alltoall(oqam__zrvjp, rwke__lauut, 1)
    frp__qnm = rwke__lauut.sum()
    ewmmw__dnys = np.empty(frp__qnm, right_key_arrs[0].dtype)
    ukk__ftn = alloc_arr_tup(frp__qnm, right_data)
    xpllp__vfni = bodo.ir.join.calc_disp(rwke__lauut)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], ewmmw__dnys,
        oqam__zrvjp, rwke__lauut, wyglc__jpu, xpllp__vfni)
    bodo.libs.distributed_api.alltoallv_tup(right_data, ukk__ftn,
        oqam__zrvjp, rwke__lauut, wyglc__jpu, xpllp__vfni)
    return (ewmmw__dnys,), ukk__ftn


@numba.njit
def _count_overlap(r_key_arr, start, end):
    cjz__oxphl = 0
    psr__npd = 0
    yop__jhf = 0
    while yop__jhf < len(r_key_arr) and r_key_arr[yop__jhf] < start:
        psr__npd += 1
        yop__jhf += 1
    while yop__jhf < len(r_key_arr) and start <= r_key_arr[yop__jhf] <= end:
        yop__jhf += 1
        cjz__oxphl += 1
    return psr__npd, cjz__oxphl


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    loiyd__oprj = np.empty_like(arr)
    loiyd__oprj[0] = 0
    for zkyc__ftnhb in range(1, len(arr)):
        loiyd__oprj[zkyc__ftnhb] = loiyd__oprj[zkyc__ftnhb - 1] + arr[
            zkyc__ftnhb - 1]
    return loiyd__oprj


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    udik__aldl = len(left_keys[0])
    jtw__cdkhp = len(right_keys[0])
    uqopa__muhca = alloc_arr_tup(udik__aldl, left_keys)
    csbj__rzxp = alloc_arr_tup(udik__aldl, right_keys)
    rtin__txezi = alloc_arr_tup(udik__aldl, data_left)
    xutpq__noirw = alloc_arr_tup(udik__aldl, data_right)
    qzcvm__nyrs = 0
    jmzj__ftzyr = 0
    for qzcvm__nyrs in range(udik__aldl):
        if jmzj__ftzyr < 0:
            jmzj__ftzyr = 0
        while jmzj__ftzyr < jtw__cdkhp and getitem_arr_tup(right_keys,
            jmzj__ftzyr) <= getitem_arr_tup(left_keys, qzcvm__nyrs):
            jmzj__ftzyr += 1
        jmzj__ftzyr -= 1
        setitem_arr_tup(uqopa__muhca, qzcvm__nyrs, getitem_arr_tup(
            left_keys, qzcvm__nyrs))
        setitem_arr_tup(rtin__txezi, qzcvm__nyrs, getitem_arr_tup(data_left,
            qzcvm__nyrs))
        if jmzj__ftzyr >= 0:
            setitem_arr_tup(csbj__rzxp, qzcvm__nyrs, getitem_arr_tup(
                right_keys, jmzj__ftzyr))
            setitem_arr_tup(xutpq__noirw, qzcvm__nyrs, getitem_arr_tup(
                data_right, jmzj__ftzyr))
        else:
            bodo.libs.array_kernels.setna_tup(csbj__rzxp, qzcvm__nyrs)
            bodo.libs.array_kernels.setna_tup(xutpq__noirw, qzcvm__nyrs)
    return uqopa__muhca, csbj__rzxp, rtin__txezi, xutpq__noirw
