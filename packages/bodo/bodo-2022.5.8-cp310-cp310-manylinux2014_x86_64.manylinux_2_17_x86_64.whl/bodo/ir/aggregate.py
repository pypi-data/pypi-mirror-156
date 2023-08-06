"""IR node for the groupby, pivot and cross_tabulation"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, pivot_groupby_and_aggregate
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, decode_if_dict_array, get_literal_value, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, list_cumulative, to_str_arr_if_dict_array
from bodo.utils.utils import debug_prints, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign, sanitize_varname, unliteral_all
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        sig = func.signature
        if sig == types.none(types.voidptr):
            spwpk__mlu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            wpsa__xys = cgutils.get_or_insert_function(builder.module,
                spwpk__mlu, sym._literal_value)
            builder.call(wpsa__xys, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            spwpk__mlu = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            wpsa__xys = cgutils.get_or_insert_function(builder.module,
                spwpk__mlu, sym._literal_value)
            builder.call(wpsa__xys, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            spwpk__mlu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            wpsa__xys = cgutils.get_or_insert_function(builder.module,
                spwpk__mlu, sym._literal_value)
            builder.call(wpsa__xys, [context.get_constant_null(sig.args[0]),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'head', 'transform', 'size', 'shift', 'sum',
    'count', 'nunique', 'median', 'cumsum', 'cumprod', 'cummin', 'cummax',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'idxmin', 'idxmax',
    'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        hjcj__jyfa = True
        nsz__dyts = 1
        olfte__ewit = -1
        if isinstance(rhs, ir.Expr):
            for xeut__aiwx in rhs.kws:
                if func_name in list_cumulative:
                    if xeut__aiwx[0] == 'skipna':
                        hjcj__jyfa = guard(find_const, func_ir, xeut__aiwx[1])
                        if not isinstance(hjcj__jyfa, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if xeut__aiwx[0] == 'dropna':
                        hjcj__jyfa = guard(find_const, func_ir, xeut__aiwx[1])
                        if not isinstance(hjcj__jyfa, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            nsz__dyts = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', nsz__dyts)
            nsz__dyts = guard(find_const, func_ir, nsz__dyts)
        if func_name == 'head':
            olfte__ewit = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(olfte__ewit, int):
                olfte__ewit = guard(find_const, func_ir, olfte__ewit)
            if olfte__ewit < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = hjcj__jyfa
        func.periods = nsz__dyts
        func.head_n = olfte__ewit
        if func_name == 'transform':
            kws = dict(rhs.kws)
            lvbi__gcvl = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            sgsjm__jpat = typemap[lvbi__gcvl.name]
            bkc__nxf = None
            if isinstance(sgsjm__jpat, str):
                bkc__nxf = sgsjm__jpat
            elif is_overload_constant_str(sgsjm__jpat):
                bkc__nxf = get_overload_const_str(sgsjm__jpat)
            elif bodo.utils.typing.is_builtin_function(sgsjm__jpat):
                bkc__nxf = bodo.utils.typing.get_builtin_function_name(
                    sgsjm__jpat)
            if bkc__nxf not in bodo.ir.aggregate.supported_transform_funcs[:]:
                raise BodoError(f'unsupported transform function {bkc__nxf}')
            func.transform_func = supported_agg_funcs.index(bkc__nxf)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    lvbi__gcvl = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if lvbi__gcvl == '':
        sgsjm__jpat = types.none
    else:
        sgsjm__jpat = typemap[lvbi__gcvl.name]
    if is_overload_constant_dict(sgsjm__jpat):
        rfvjb__bnm = get_overload_constant_dict(sgsjm__jpat)
        syvaf__wwvvp = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in rfvjb__bnm.values()]
        return syvaf__wwvvp
    if sgsjm__jpat == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(sgsjm__jpat, types.BaseTuple) or is_overload_constant_list(
        sgsjm__jpat):
        syvaf__wwvvp = []
        hhyq__ywdm = 0
        if is_overload_constant_list(sgsjm__jpat):
            zqnv__ptvf = get_overload_const_list(sgsjm__jpat)
        else:
            zqnv__ptvf = sgsjm__jpat.types
        for t in zqnv__ptvf:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                syvaf__wwvvp.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(zqnv__ptvf) > 1:
                    func.fname = '<lambda_' + str(hhyq__ywdm) + '>'
                    hhyq__ywdm += 1
                syvaf__wwvvp.append(func)
        return [syvaf__wwvvp]
    if is_overload_constant_str(sgsjm__jpat):
        func_name = get_overload_const_str(sgsjm__jpat)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(sgsjm__jpat):
        func_name = bodo.utils.typing.get_builtin_function_name(sgsjm__jpat)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        hhyq__ywdm = 0
        vjfmy__rbdm = []
        for gti__spv in f_val:
            func = get_agg_func_udf(func_ir, gti__spv, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{hhyq__ywdm}>'
                hhyq__ywdm += 1
            vjfmy__rbdm.append(func)
        return vjfmy__rbdm
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    bkc__nxf = code.co_name
    return bkc__nxf


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            dsd__rsuxb = types.DType(args[0])
            return signature(dsd__rsuxb, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    pyow__uwf = nobs_a + nobs_b
    zgo__ihrf = (nobs_a * mean_a + nobs_b * mean_b) / pyow__uwf
    bhz__qcq = mean_b - mean_a
    rtpsg__ghokw = (ssqdm_a + ssqdm_b + bhz__qcq * bhz__qcq * nobs_a *
        nobs_b / pyow__uwf)
    return rtpsg__ghokw, zgo__ihrf, pyow__uwf


def __special_combine(*args):
    return


@infer_global(__special_combine)
class SpecialCombineTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *unliteral_all(args))


@lower_builtin(__special_combine, types.VarArg(types.Any))
def lower_special_combine(context, builder, sig, args):
    return context.get_dummy_value()


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_key_vars, df_out_vars, df_in_vars, key_arrs, input_has_index,
        same_index, return_key, loc, func_name, dropna=True, pivot_arr=None,
        pivot_values=None, is_crosstab=False):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_key_vars = out_key_vars
        self.df_out_vars = df_out_vars
        self.df_in_vars = df_in_vars
        self.key_arrs = key_arrs
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self.pivot_arr = pivot_arr
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab

    def __repr__(self):
        orjh__qibl = ''
        for zbx__pjukk, ybl__bfxu in self.df_out_vars.items():
            orjh__qibl += "'{}':{}, ".format(zbx__pjukk, ybl__bfxu.name)
        ins__azvy = '{}{{{}}}'.format(self.df_out, orjh__qibl)
        xyzg__fozs = ''
        for zbx__pjukk, ybl__bfxu in self.df_in_vars.items():
            xyzg__fozs += "'{}':{}, ".format(zbx__pjukk, ybl__bfxu.name)
        sdxud__ptue = '{}{{{}}}'.format(self.df_in, xyzg__fozs)
        ykobv__dvyhf = 'pivot {}:{}'.format(self.pivot_arr.name, self.
            pivot_values) if self.pivot_arr is not None else ''
        key_names = ','.join([str(klfc__ebuom) for klfc__ebuom in self.
            key_names])
        yqkp__flg = ','.join([ybl__bfxu.name for ybl__bfxu in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(ins__azvy,
            sdxud__ptue, key_names, yqkp__flg, ykobv__dvyhf)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        hvbm__ebsh, tqn__gcq = self.gb_info_out.pop(out_col_name)
        if hvbm__ebsh is None and not self.is_crosstab:
            return
        umfm__xmqv = self.gb_info_in[hvbm__ebsh]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for evi__hhhaj, (func, orjh__qibl) in enumerate(umfm__xmqv):
                try:
                    orjh__qibl.remove(out_col_name)
                    if len(orjh__qibl) == 0:
                        umfm__xmqv.pop(evi__hhhaj)
                        break
                except ValueError as feev__wrl:
                    continue
        else:
            for evi__hhhaj, (func, pgwpe__ugqyn) in enumerate(umfm__xmqv):
                if pgwpe__ugqyn == out_col_name:
                    umfm__xmqv.pop(evi__hhhaj)
                    break
        if len(umfm__xmqv) == 0:
            self.gb_info_in.pop(hvbm__ebsh)
            self.df_in_vars.pop(hvbm__ebsh)


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({ybl__bfxu.name for ybl__bfxu in aggregate_node.key_arrs})
    use_set.update({ybl__bfxu.name for ybl__bfxu in aggregate_node.
        df_in_vars.values()})
    if aggregate_node.pivot_arr is not None:
        use_set.add(aggregate_node.pivot_arr.name)
    def_set.update({ybl__bfxu.name for ybl__bfxu in aggregate_node.
        df_out_vars.values()})
    if aggregate_node.out_key_vars is not None:
        def_set.update({ybl__bfxu.name for ybl__bfxu in aggregate_node.
            out_key_vars})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(aggregate_node, lives_no_aliases, lives,
    arg_aliases, alias_map, func_ir, typemap):
    hojzb__hrepq = [suzlj__wfpp for suzlj__wfpp, mrnlb__yne in
        aggregate_node.df_out_vars.items() if mrnlb__yne.name not in lives]
    for mgr__yxf in hojzb__hrepq:
        aggregate_node.remove_out_col(mgr__yxf)
    out_key_vars = aggregate_node.out_key_vars
    if out_key_vars is not None and all(ybl__bfxu.name not in lives for
        ybl__bfxu in out_key_vars):
        aggregate_node.out_key_vars = None
    if len(aggregate_node.df_out_vars
        ) == 0 and aggregate_node.out_key_vars is None:
        return None
    return aggregate_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    dfi__iqs = set(ybl__bfxu.name for ybl__bfxu in aggregate_node.
        df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        dfi__iqs.update({ybl__bfxu.name for ybl__bfxu in aggregate_node.
            out_key_vars})
    return set(), dfi__iqs


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for evi__hhhaj in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[evi__hhhaj] = replace_vars_inner(aggregate_node
            .key_arrs[evi__hhhaj], var_dict)
    for suzlj__wfpp in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[suzlj__wfpp] = replace_vars_inner(
            aggregate_node.df_in_vars[suzlj__wfpp], var_dict)
    for suzlj__wfpp in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[suzlj__wfpp] = replace_vars_inner(
            aggregate_node.df_out_vars[suzlj__wfpp], var_dict)
    if aggregate_node.out_key_vars is not None:
        for evi__hhhaj in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[evi__hhhaj] = replace_vars_inner(
                aggregate_node.out_key_vars[evi__hhhaj], var_dict)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = replace_vars_inner(aggregate_node.
            pivot_arr, var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    if debug_prints():
        print('visiting aggregate vars for:', aggregate_node)
        print('cbdata: ', sorted(cbdata.items()))
    for evi__hhhaj in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[evi__hhhaj] = visit_vars_inner(aggregate_node
            .key_arrs[evi__hhhaj], callback, cbdata)
    for suzlj__wfpp in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[suzlj__wfpp] = visit_vars_inner(
            aggregate_node.df_in_vars[suzlj__wfpp], callback, cbdata)
    for suzlj__wfpp in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[suzlj__wfpp] = visit_vars_inner(
            aggregate_node.df_out_vars[suzlj__wfpp], callback, cbdata)
    if aggregate_node.out_key_vars is not None:
        for evi__hhhaj in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[evi__hhhaj] = visit_vars_inner(
                aggregate_node.out_key_vars[evi__hhhaj], callback, cbdata)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = visit_vars_inner(aggregate_node.
            pivot_arr, callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    assert len(aggregate_node.df_out_vars
        ) > 0 or aggregate_node.out_key_vars is not None or aggregate_node.is_crosstab, 'empty aggregate in array analysis'
    vwah__ulzw = []
    for emg__xsfi in aggregate_node.key_arrs:
        cbt__waqjo = equiv_set.get_shape(emg__xsfi)
        if cbt__waqjo:
            vwah__ulzw.append(cbt__waqjo[0])
    if aggregate_node.pivot_arr is not None:
        cbt__waqjo = equiv_set.get_shape(aggregate_node.pivot_arr)
        if cbt__waqjo:
            vwah__ulzw.append(cbt__waqjo[0])
    for mrnlb__yne in aggregate_node.df_in_vars.values():
        cbt__waqjo = equiv_set.get_shape(mrnlb__yne)
        if cbt__waqjo:
            vwah__ulzw.append(cbt__waqjo[0])
    if len(vwah__ulzw) > 1:
        equiv_set.insert_equiv(*vwah__ulzw)
    wun__lciit = []
    vwah__ulzw = []
    hvj__hoicv = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        hvj__hoicv.extend(aggregate_node.out_key_vars)
    for mrnlb__yne in hvj__hoicv:
        readj__rlcj = typemap[mrnlb__yne.name]
        aoow__son = array_analysis._gen_shape_call(equiv_set, mrnlb__yne,
            readj__rlcj.ndim, None, wun__lciit)
        equiv_set.insert_equiv(mrnlb__yne, aoow__son)
        vwah__ulzw.append(aoow__son[0])
        equiv_set.define(mrnlb__yne, set())
    if len(vwah__ulzw) > 1:
        equiv_set.insert_equiv(*vwah__ulzw)
    return [], wun__lciit


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    fuu__hrdv = Distribution.OneD
    for mrnlb__yne in aggregate_node.df_in_vars.values():
        fuu__hrdv = Distribution(min(fuu__hrdv.value, array_dists[
            mrnlb__yne.name].value))
    for emg__xsfi in aggregate_node.key_arrs:
        fuu__hrdv = Distribution(min(fuu__hrdv.value, array_dists[emg__xsfi
            .name].value))
    if aggregate_node.pivot_arr is not None:
        fuu__hrdv = Distribution(min(fuu__hrdv.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = fuu__hrdv
    for mrnlb__yne in aggregate_node.df_in_vars.values():
        array_dists[mrnlb__yne.name] = fuu__hrdv
    for emg__xsfi in aggregate_node.key_arrs:
        array_dists[emg__xsfi.name] = fuu__hrdv
    dkppv__xbxr = Distribution.OneD_Var
    for mrnlb__yne in aggregate_node.df_out_vars.values():
        if mrnlb__yne.name in array_dists:
            dkppv__xbxr = Distribution(min(dkppv__xbxr.value, array_dists[
                mrnlb__yne.name].value))
    if aggregate_node.out_key_vars is not None:
        for mrnlb__yne in aggregate_node.out_key_vars:
            if mrnlb__yne.name in array_dists:
                dkppv__xbxr = Distribution(min(dkppv__xbxr.value,
                    array_dists[mrnlb__yne.name].value))
    dkppv__xbxr = Distribution(min(dkppv__xbxr.value, fuu__hrdv.value))
    for mrnlb__yne in aggregate_node.df_out_vars.values():
        array_dists[mrnlb__yne.name] = dkppv__xbxr
    if aggregate_node.out_key_vars is not None:
        for msnc__lrn in aggregate_node.out_key_vars:
            array_dists[msnc__lrn.name] = dkppv__xbxr
    if dkppv__xbxr != Distribution.OneD_Var:
        for emg__xsfi in aggregate_node.key_arrs:
            array_dists[emg__xsfi.name] = dkppv__xbxr
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = dkppv__xbxr
        for mrnlb__yne in aggregate_node.df_in_vars.values():
            array_dists[mrnlb__yne.name] = dkppv__xbxr


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for mrnlb__yne in agg_node.df_out_vars.values():
        definitions[mrnlb__yne.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for msnc__lrn in agg_node.out_key_vars:
            definitions[msnc__lrn.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for ybl__bfxu in (list(agg_node.df_in_vars.values()) + list(
            agg_node.df_out_vars.values()) + agg_node.key_arrs):
            if array_dists[ybl__bfxu.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ybl__bfxu.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    uqjyf__zfo = tuple(typemap[ybl__bfxu.name] for ybl__bfxu in agg_node.
        key_arrs)
    wruws__xtpmh = [ybl__bfxu for zep__ela, ybl__bfxu in agg_node.
        df_in_vars.items()]
    fvhe__dbgq = [ybl__bfxu for zep__ela, ybl__bfxu in agg_node.df_out_vars
        .items()]
    in_col_typs = []
    syvaf__wwvvp = []
    if agg_node.pivot_arr is not None:
        for hvbm__ebsh, umfm__xmqv in agg_node.gb_info_in.items():
            for func, tqn__gcq in umfm__xmqv:
                if hvbm__ebsh is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        hvbm__ebsh].name])
                syvaf__wwvvp.append(func)
    else:
        for hvbm__ebsh, func in agg_node.gb_info_out.values():
            if hvbm__ebsh is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[hvbm__ebsh].
                    name])
            syvaf__wwvvp.append(func)
    out_col_typs = tuple(typemap[ybl__bfxu.name] for ybl__bfxu in fvhe__dbgq)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(uqjyf__zfo + tuple(typemap[ybl__bfxu.name] for
        ybl__bfxu in wruws__xtpmh) + (pivot_typ,))
    in_col_typs = [to_str_arr_if_dict_array(t) for t in in_col_typs]
    vcbp__jkxzs = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for evi__hhhaj, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            vcbp__jkxzs.update({f'in_cat_dtype_{evi__hhhaj}': in_col_typ})
    for evi__hhhaj, duqie__mvvuy in enumerate(out_col_typs):
        if isinstance(duqie__mvvuy, bodo.CategoricalArrayType):
            vcbp__jkxzs.update({f'out_cat_dtype_{evi__hhhaj}': duqie__mvvuy})
    udf_func_struct = get_udf_func_struct(syvaf__wwvvp, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    sjl__gff = gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
        parallel, udf_func_struct)
    vcbp__jkxzs.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate,
        'pivot_groupby_and_aggregate': pivot_groupby_and_aggregate,
        'info_from_table': info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'decode_if_dict_array': decode_if_dict_array, 'out_typs': out_col_typs}
        )
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            vcbp__jkxzs.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            vcbp__jkxzs.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    khe__nugb = compile_to_numba_ir(sjl__gff, vcbp__jkxzs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    eyj__izoui = []
    if agg_node.pivot_arr is None:
        hdk__pxk = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        ldmm__orprc = ir.Var(hdk__pxk, mk_unique_var('dummy_none'), loc)
        typemap[ldmm__orprc.name] = types.none
        eyj__izoui.append(ir.Assign(ir.Const(None, loc), ldmm__orprc, loc))
        wruws__xtpmh.append(ldmm__orprc)
    else:
        wruws__xtpmh.append(agg_node.pivot_arr)
    replace_arg_nodes(khe__nugb, agg_node.key_arrs + wruws__xtpmh)
    xlq__boukg = khe__nugb.body[-3]
    assert is_assign(xlq__boukg) and isinstance(xlq__boukg.value, ir.Expr
        ) and xlq__boukg.value.op == 'build_tuple'
    eyj__izoui += khe__nugb.body[:-3]
    hvj__hoicv = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        hvj__hoicv += agg_node.out_key_vars
    for evi__hhhaj, pdyka__vquh in enumerate(hvj__hoicv):
        rjroc__sdy = xlq__boukg.value.items[evi__hhhaj]
        eyj__izoui.append(ir.Assign(rjroc__sdy, pdyka__vquh, pdyka__vquh.loc))
    return eyj__izoui


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def get_numba_set(dtype):
    pass


@infer_global(get_numba_set)
class GetNumbaSetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        gwhf__qrq = args[0]
        dtype = types.Tuple([t.dtype for t in gwhf__qrq.types]) if isinstance(
            gwhf__qrq, types.BaseTuple) else gwhf__qrq.dtype
        if isinstance(gwhf__qrq, types.BaseTuple) and len(gwhf__qrq.types
            ) == 1:
            dtype = gwhf__qrq.types[0].dtype
        return signature(types.Set(dtype), *args)


@lower_builtin(get_numba_set, types.Any)
def lower_get_numba_set(context, builder, sig, args):
    return numba.cpython.setobj.set_empty_constructor(context, builder, sig,
        args)


@infer_global(bool)
class BoolNoneTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        dtvf__fvrb = args[0]
        if dtvf__fvrb == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    qkq__irlt = context.compile_internal(builder, lambda a: False, sig, args)
    return qkq__irlt


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        fkmnl__qik = IntDtype(t.dtype).name
        assert fkmnl__qik.endswith('Dtype()')
        fkmnl__qik = fkmnl__qik[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{fkmnl__qik}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        eyf__tbnz = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {eyf__tbnz}_cat_dtype_{colnum})')
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    out_data_typs, do_combine, func_idx_to_in_col, label_suffix):
    cer__bqkjx = udf_func_struct.var_typs
    ghfv__wobrw = len(cer__bqkjx)
    cjq__ackn = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    cjq__ackn += '    if is_null_pointer(in_table):\n'
    cjq__ackn += '        return\n'
    cjq__ackn += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cer__bqkjx]), 
        ',' if len(cer__bqkjx) == 1 else '')
    ggp__tdecf = n_keys
    ufkos__eox = []
    redvar_offsets = []
    msg__bflpz = []
    if do_combine:
        for evi__hhhaj, gti__spv in enumerate(allfuncs):
            if gti__spv.ftype != 'udf':
                ggp__tdecf += gti__spv.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(ggp__tdecf, ggp__tdecf +
                    gti__spv.n_redvars))
                ggp__tdecf += gti__spv.n_redvars
                msg__bflpz.append(data_in_typs_[func_idx_to_in_col[evi__hhhaj]]
                    )
                ufkos__eox.append(func_idx_to_in_col[evi__hhhaj] + n_keys)
    else:
        for evi__hhhaj, gti__spv in enumerate(allfuncs):
            if gti__spv.ftype != 'udf':
                ggp__tdecf += gti__spv.ncols_post_shuffle
            else:
                redvar_offsets += list(range(ggp__tdecf + 1, ggp__tdecf + 1 +
                    gti__spv.n_redvars))
                ggp__tdecf += gti__spv.n_redvars + 1
                msg__bflpz.append(data_in_typs_[func_idx_to_in_col[evi__hhhaj]]
                    )
                ufkos__eox.append(func_idx_to_in_col[evi__hhhaj] + n_keys)
    assert len(redvar_offsets) == ghfv__wobrw
    ntvog__zhigu = len(msg__bflpz)
    qjyju__kbdi = []
    for evi__hhhaj, t in enumerate(msg__bflpz):
        qjyju__kbdi.append(_gen_dummy_alloc(t, evi__hhhaj, True))
    cjq__ackn += '    data_in_dummy = ({}{})\n'.format(','.join(qjyju__kbdi
        ), ',' if len(msg__bflpz) == 1 else '')
    cjq__ackn += """
    # initialize redvar cols
"""
    cjq__ackn += '    init_vals = __init_func()\n'
    for evi__hhhaj in range(ghfv__wobrw):
        cjq__ackn += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(evi__hhhaj, redvar_offsets[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(redvar_arr_{})\n'.format(evi__hhhaj)
        cjq__ackn += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            evi__hhhaj, evi__hhhaj)
    cjq__ackn += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(evi__hhhaj) for evi__hhhaj in range(ghfv__wobrw)]), ',' if 
        ghfv__wobrw == 1 else '')
    cjq__ackn += '\n'
    for evi__hhhaj in range(ntvog__zhigu):
        cjq__ackn += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(evi__hhhaj, ufkos__eox[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(data_in_{})\n'.format(evi__hhhaj)
    cjq__ackn += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(evi__hhhaj) for evi__hhhaj in range(ntvog__zhigu)]), ',' if 
        ntvog__zhigu == 1 else '')
    cjq__ackn += '\n'
    cjq__ackn += '    for i in range(len(data_in_0)):\n'
    cjq__ackn += '        w_ind = row_to_group[i]\n'
    cjq__ackn += '        if w_ind != -1:\n'
    cjq__ackn += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    pmxj__zzo = {}
    exec(cjq__ackn, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, pmxj__zzo)
    return pmxj__zzo['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    cer__bqkjx = udf_func_struct.var_typs
    ghfv__wobrw = len(cer__bqkjx)
    cjq__ackn = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    cjq__ackn += '    if is_null_pointer(in_table):\n'
    cjq__ackn += '        return\n'
    cjq__ackn += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cer__bqkjx]), 
        ',' if len(cer__bqkjx) == 1 else '')
    khc__sqv = n_keys
    impy__klnx = n_keys
    csh__fwb = []
    kbguy__yuze = []
    for gti__spv in allfuncs:
        if gti__spv.ftype != 'udf':
            khc__sqv += gti__spv.ncols_pre_shuffle
            impy__klnx += gti__spv.ncols_post_shuffle
        else:
            csh__fwb += list(range(khc__sqv, khc__sqv + gti__spv.n_redvars))
            kbguy__yuze += list(range(impy__klnx + 1, impy__klnx + 1 +
                gti__spv.n_redvars))
            khc__sqv += gti__spv.n_redvars
            impy__klnx += 1 + gti__spv.n_redvars
    assert len(csh__fwb) == ghfv__wobrw
    cjq__ackn += """
    # initialize redvar cols
"""
    cjq__ackn += '    init_vals = __init_func()\n'
    for evi__hhhaj in range(ghfv__wobrw):
        cjq__ackn += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(evi__hhhaj, kbguy__yuze[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(redvar_arr_{})\n'.format(evi__hhhaj)
        cjq__ackn += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            evi__hhhaj, evi__hhhaj)
    cjq__ackn += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(evi__hhhaj) for evi__hhhaj in range(ghfv__wobrw)]), ',' if 
        ghfv__wobrw == 1 else '')
    cjq__ackn += '\n'
    for evi__hhhaj in range(ghfv__wobrw):
        cjq__ackn += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(evi__hhhaj, csh__fwb[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(recv_redvar_arr_{})\n'.format(evi__hhhaj)
    cjq__ackn += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(evi__hhhaj) for evi__hhhaj in range(
        ghfv__wobrw)]), ',' if ghfv__wobrw == 1 else '')
    cjq__ackn += '\n'
    if ghfv__wobrw:
        cjq__ackn += '    for i in range(len(recv_redvar_arr_0)):\n'
        cjq__ackn += '        w_ind = row_to_group[i]\n'
        cjq__ackn += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)\n'
            )
    pmxj__zzo = {}
    exec(cjq__ackn, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, pmxj__zzo)
    return pmxj__zzo['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    cer__bqkjx = udf_func_struct.var_typs
    ghfv__wobrw = len(cer__bqkjx)
    ggp__tdecf = n_keys
    redvar_offsets = []
    acuv__cyszf = []
    out_data_typs = []
    for evi__hhhaj, gti__spv in enumerate(allfuncs):
        if gti__spv.ftype != 'udf':
            ggp__tdecf += gti__spv.ncols_post_shuffle
        else:
            acuv__cyszf.append(ggp__tdecf)
            redvar_offsets += list(range(ggp__tdecf + 1, ggp__tdecf + 1 +
                gti__spv.n_redvars))
            ggp__tdecf += 1 + gti__spv.n_redvars
            out_data_typs.append(out_data_typs_[evi__hhhaj])
    assert len(redvar_offsets) == ghfv__wobrw
    ntvog__zhigu = len(out_data_typs)
    cjq__ackn = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    cjq__ackn += '    if is_null_pointer(table):\n'
    cjq__ackn += '        return\n'
    cjq__ackn += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cer__bqkjx]), 
        ',' if len(cer__bqkjx) == 1 else '')
    cjq__ackn += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for evi__hhhaj in range(ghfv__wobrw):
        cjq__ackn += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(evi__hhhaj, redvar_offsets[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(redvar_arr_{})\n'.format(evi__hhhaj)
    cjq__ackn += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(evi__hhhaj) for evi__hhhaj in range(ghfv__wobrw)]), ',' if 
        ghfv__wobrw == 1 else '')
    cjq__ackn += '\n'
    for evi__hhhaj in range(ntvog__zhigu):
        cjq__ackn += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(evi__hhhaj, acuv__cyszf[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(data_out_{})\n'.format(evi__hhhaj)
    cjq__ackn += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(evi__hhhaj) for evi__hhhaj in range(ntvog__zhigu)]), ',' if 
        ntvog__zhigu == 1 else '')
    cjq__ackn += '\n'
    cjq__ackn += '    for i in range(len(data_out_0)):\n'
    cjq__ackn += '        __eval_res(redvars, data_out, i)\n'
    pmxj__zzo = {}
    exec(cjq__ackn, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, pmxj__zzo)
    return pmxj__zzo['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    ggp__tdecf = n_keys
    esxiy__rfii = []
    for evi__hhhaj, gti__spv in enumerate(allfuncs):
        if gti__spv.ftype == 'gen_udf':
            esxiy__rfii.append(ggp__tdecf)
            ggp__tdecf += 1
        elif gti__spv.ftype != 'udf':
            ggp__tdecf += gti__spv.ncols_post_shuffle
        else:
            ggp__tdecf += gti__spv.n_redvars + 1
    cjq__ackn = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    cjq__ackn += '    if num_groups == 0:\n'
    cjq__ackn += '        return\n'
    for evi__hhhaj, func in enumerate(udf_func_struct.general_udf_funcs):
        cjq__ackn += '    # col {}\n'.format(evi__hhhaj)
        cjq__ackn += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(esxiy__rfii[evi__hhhaj], evi__hhhaj))
        cjq__ackn += '    incref(out_col)\n'
        cjq__ackn += '    for j in range(num_groups):\n'
        cjq__ackn += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(evi__hhhaj, evi__hhhaj))
        cjq__ackn += '        incref(in_col)\n'
        cjq__ackn += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(evi__hhhaj))
    vcbp__jkxzs = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    zuwot__fnyky = 0
    for evi__hhhaj, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[zuwot__fnyky]
        vcbp__jkxzs['func_{}'.format(zuwot__fnyky)] = func
        vcbp__jkxzs['in_col_{}_typ'.format(zuwot__fnyky)] = in_col_typs[
            func_idx_to_in_col[evi__hhhaj]]
        vcbp__jkxzs['out_col_{}_typ'.format(zuwot__fnyky)] = out_col_typs[
            evi__hhhaj]
        zuwot__fnyky += 1
    pmxj__zzo = {}
    exec(cjq__ackn, vcbp__jkxzs, pmxj__zzo)
    gti__spv = pmxj__zzo['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    cgk__tlers = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(cgk__tlers, nopython=True)(gti__spv)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    chv__zygad = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        fyfs__xuidd = 1
    else:
        fyfs__xuidd = len(agg_node.pivot_values)
    dao__cqc = tuple('key_' + sanitize_varname(zbx__pjukk) for zbx__pjukk in
        agg_node.key_names)
    osns__hpjau = {zbx__pjukk: 'in_{}'.format(sanitize_varname(zbx__pjukk)) for
        zbx__pjukk in agg_node.gb_info_in.keys() if zbx__pjukk is not None}
    pozrb__okgys = {zbx__pjukk: ('out_' + sanitize_varname(zbx__pjukk)) for
        zbx__pjukk in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    lrg__tgv = ', '.join(dao__cqc)
    bdh__dnyd = ', '.join(osns__hpjau.values())
    if bdh__dnyd != '':
        bdh__dnyd = ', ' + bdh__dnyd
    cjq__ackn = 'def agg_top({}{}{}, pivot_arr):\n'.format(lrg__tgv,
        bdh__dnyd, ', index_arg' if agg_node.input_has_index else '')
    for a in (dao__cqc + tuple(osns__hpjau.values())):
        cjq__ackn += f'    {a} = decode_if_dict_array({a})\n'
    if chv__zygad:
        cjq__ackn += f'    pivot_arr = decode_if_dict_array(pivot_arr)\n'
        qasmc__brvtd = []
        for hvbm__ebsh, umfm__xmqv in agg_node.gb_info_in.items():
            if hvbm__ebsh is not None:
                for func, tqn__gcq in umfm__xmqv:
                    qasmc__brvtd.append(osns__hpjau[hvbm__ebsh])
    else:
        qasmc__brvtd = tuple(osns__hpjau[hvbm__ebsh] for hvbm__ebsh,
            tqn__gcq in agg_node.gb_info_out.values() if hvbm__ebsh is not None
            )
    fkd__xjnua = dao__cqc + tuple(qasmc__brvtd)
    cjq__ackn += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in fkd__xjnua), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    cjq__ackn += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    hmam__nwvee = []
    func_idx_to_in_col = []
    mvkar__zpq = []
    hjcj__jyfa = False
    jypuh__figbp = 1
    olfte__ewit = -1
    bqyi__gvrmu = 0
    ioyn__xmup = 0
    if not chv__zygad:
        syvaf__wwvvp = [func for tqn__gcq, func in agg_node.gb_info_out.
            values()]
    else:
        syvaf__wwvvp = [func for func, tqn__gcq in umfm__xmqv for
            umfm__xmqv in agg_node.gb_info_in.values()]
    for cqzo__nqrw, func in enumerate(syvaf__wwvvp):
        hmam__nwvee.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            bqyi__gvrmu += 1
        if hasattr(func, 'skipdropna'):
            hjcj__jyfa = func.skipdropna
        if func.ftype == 'shift':
            jypuh__figbp = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            ioyn__xmup = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            olfte__ewit = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(cqzo__nqrw)
        if func.ftype == 'udf':
            mvkar__zpq.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            mvkar__zpq.append(0)
            do_combine = False
    hmam__nwvee.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == fyfs__xuidd, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * fyfs__xuidd, 'invalid number of groupby outputs'
    if bqyi__gvrmu > 0:
        if bqyi__gvrmu != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    for evi__hhhaj, zbx__pjukk in enumerate(agg_node.gb_info_out.keys()):
        erto__ccj = pozrb__okgys[zbx__pjukk] + '_dummy'
        duqie__mvvuy = out_col_typs[evi__hhhaj]
        hvbm__ebsh, func = agg_node.gb_info_out[zbx__pjukk]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(duqie__mvvuy, bodo.
            CategoricalArrayType):
            cjq__ackn += '    {} = {}\n'.format(erto__ccj, osns__hpjau[
                hvbm__ebsh])
        elif udf_func_struct is not None:
            cjq__ackn += '    {} = {}\n'.format(erto__ccj, _gen_dummy_alloc
                (duqie__mvvuy, evi__hhhaj, False))
    if udf_func_struct is not None:
        gbwm__lsn = next_label()
        if udf_func_struct.regular_udfs:
            cgk__tlers = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            oqfdi__brbjj = numba.cfunc(cgk__tlers, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, gbwm__lsn))
            oyf__ruy = numba.cfunc(cgk__tlers, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, gbwm__lsn))
            wyao__zbnfc = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_col_typs,
                gbwm__lsn))
            udf_func_struct.set_regular_cfuncs(oqfdi__brbjj, oyf__ruy,
                wyao__zbnfc)
            for dnrnm__sderp in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[dnrnm__sderp.native_name] = dnrnm__sderp
                gb_agg_cfunc_addr[dnrnm__sderp.native_name
                    ] = dnrnm__sderp.address
        if udf_func_struct.general_udfs:
            cyn__asuk = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col,
                gbwm__lsn)
            udf_func_struct.set_general_cfunc(cyn__asuk)
        rvaj__zmk = []
        gytzr__exrw = 0
        evi__hhhaj = 0
        for erto__ccj, gti__spv in zip(pozrb__okgys.values(), allfuncs):
            if gti__spv.ftype in ('udf', 'gen_udf'):
                rvaj__zmk.append(erto__ccj + '_dummy')
                for zfp__oln in range(gytzr__exrw, gytzr__exrw + mvkar__zpq
                    [evi__hhhaj]):
                    rvaj__zmk.append('data_redvar_dummy_' + str(zfp__oln))
                gytzr__exrw += mvkar__zpq[evi__hhhaj]
                evi__hhhaj += 1
        if udf_func_struct.regular_udfs:
            cer__bqkjx = udf_func_struct.var_typs
            for evi__hhhaj, t in enumerate(cer__bqkjx):
                cjq__ackn += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(evi__hhhaj, _get_np_dtype(t)))
        cjq__ackn += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in rvaj__zmk))
        cjq__ackn += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            cjq__ackn += "    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".format(
                oqfdi__brbjj.native_name)
            cjq__ackn += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(oyf__ruy.native_name))
            cjq__ackn += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                wyao__zbnfc.native_name)
            cjq__ackn += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(oqfdi__brbjj.native_name))
            cjq__ackn += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(oyf__ruy.native_name))
            cjq__ackn += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(wyao__zbnfc.native_name))
        else:
            cjq__ackn += '    cpp_cb_update_addr = 0\n'
            cjq__ackn += '    cpp_cb_combine_addr = 0\n'
            cjq__ackn += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            dnrnm__sderp = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[dnrnm__sderp.native_name] = dnrnm__sderp
            gb_agg_cfunc_addr[dnrnm__sderp.native_name] = dnrnm__sderp.address
            cjq__ackn += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(dnrnm__sderp.native_name))
            cjq__ackn += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(dnrnm__sderp.native_name))
        else:
            cjq__ackn += '    cpp_cb_general_addr = 0\n'
    else:
        cjq__ackn += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        cjq__ackn += '    cpp_cb_update_addr = 0\n'
        cjq__ackn += '    cpp_cb_combine_addr = 0\n'
        cjq__ackn += '    cpp_cb_eval_addr = 0\n'
        cjq__ackn += '    cpp_cb_general_addr = 0\n'
    cjq__ackn += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(gti__spv.ftype)) for gti__spv in
        allfuncs] + ['0']))
    cjq__ackn += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(str
        (hmam__nwvee))
    if len(mvkar__zpq) > 0:
        cjq__ackn += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(mvkar__zpq))
    else:
        cjq__ackn += '    udf_ncols = np.array([0], np.int32)\n'
    if chv__zygad:
        cjq__ackn += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        cjq__ackn += '    arr_info = array_to_info(arr_type)\n'
        cjq__ackn += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        cjq__ackn += '    pivot_info = array_to_info(pivot_arr)\n'
        cjq__ackn += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        cjq__ackn += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, hjcj__jyfa, agg_node.return_key, agg_node.same_index))
        cjq__ackn += '    delete_info_decref_array(pivot_info)\n'
        cjq__ackn += '    delete_info_decref_array(arr_info)\n'
    else:
        cjq__ackn += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, hjcj__jyfa,
            jypuh__figbp, ioyn__xmup, olfte__ewit, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    rroqu__jgikz = 0
    if agg_node.return_key:
        for evi__hhhaj, wxdbc__ylr in enumerate(dao__cqc):
            cjq__ackn += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(wxdbc__ylr, rroqu__jgikz, wxdbc__ylr))
            rroqu__jgikz += 1
    for evi__hhhaj, erto__ccj in enumerate(pozrb__okgys.values()):
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(duqie__mvvuy, bodo.
            CategoricalArrayType):
            cjq__ackn += f"""    {erto__ccj} = info_to_array(info_from_table(out_table, {rroqu__jgikz}), {erto__ccj + '_dummy'})
"""
        else:
            cjq__ackn += f"""    {erto__ccj} = info_to_array(info_from_table(out_table, {rroqu__jgikz}), out_typs[{evi__hhhaj}])
"""
        rroqu__jgikz += 1
    if agg_node.same_index:
        cjq__ackn += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(rroqu__jgikz))
        rroqu__jgikz += 1
    cjq__ackn += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    cjq__ackn += '    delete_table_decref_arrays(table)\n'
    cjq__ackn += '    delete_table_decref_arrays(udf_table_dummy)\n'
    cjq__ackn += '    delete_table(out_table)\n'
    cjq__ackn += f'    ev_clean.finalize()\n'
    rnr__vscqy = tuple(pozrb__okgys.values())
    if agg_node.return_key:
        rnr__vscqy += tuple(dao__cqc)
    cjq__ackn += '    return ({},{})\n'.format(', '.join(rnr__vscqy), 
        ' out_index_arg,' if agg_node.same_index else '')
    pmxj__zzo = {}
    exec(cjq__ackn, {'out_typs': out_col_typs}, pmxj__zzo)
    rfly__jfm = pmxj__zzo['agg_top']
    return rfly__jfm


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for xwn__toy in block.body:
            if is_call_assign(xwn__toy) and find_callname(f_ir, xwn__toy.value
                ) == ('len', 'builtins') and xwn__toy.value.args[0
                ].name == f_ir.arg_names[0]:
                tom__dfamp = get_definition(f_ir, xwn__toy.value.func)
                tom__dfamp.name = 'dummy_agg_count'
                tom__dfamp.value = dummy_agg_count
    ihq__sro = get_name_var_table(f_ir.blocks)
    buids__rosh = {}
    for name, tqn__gcq in ihq__sro.items():
        buids__rosh[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, buids__rosh)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    uvfe__kcs = numba.core.compiler.Flags()
    uvfe__kcs.nrt = True
    nroiy__bvl = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, uvfe__kcs)
    nroiy__bvl.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, wsjad__fmkn, calltypes, tqn__gcq = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    uvze__wyu = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    wdhky__biagh = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    kuep__mdz = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    bab__mvs = kuep__mdz(typemap, calltypes)
    pm = wdhky__biagh(typingctx, targetctx, None, f_ir, typemap,
        wsjad__fmkn, calltypes, bab__mvs, {}, uvfe__kcs, None)
    ppc__vscbo = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = wdhky__biagh(typingctx, targetctx, None, f_ir, typemap,
        wsjad__fmkn, calltypes, bab__mvs, {}, uvfe__kcs, ppc__vscbo)
    vyxh__gwl = numba.core.typed_passes.InlineOverloads()
    vyxh__gwl.run_pass(pm)
    qmpn__ibbzy = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    qmpn__ibbzy.run()
    for block in f_ir.blocks.values():
        for xwn__toy in block.body:
            if is_assign(xwn__toy) and isinstance(xwn__toy.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[xwn__toy.target.name],
                SeriesType):
                readj__rlcj = typemap.pop(xwn__toy.target.name)
                typemap[xwn__toy.target.name] = readj__rlcj.data
            if is_call_assign(xwn__toy) and find_callname(f_ir, xwn__toy.value
                ) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[xwn__toy.target.name].remove(xwn__toy.value)
                xwn__toy.value = xwn__toy.value.args[0]
                f_ir._definitions[xwn__toy.target.name].append(xwn__toy.value)
            if is_call_assign(xwn__toy) and find_callname(f_ir, xwn__toy.value
                ) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[xwn__toy.target.name].remove(xwn__toy.value)
                xwn__toy.value = ir.Const(False, xwn__toy.loc)
                f_ir._definitions[xwn__toy.target.name].append(xwn__toy.value)
            if is_call_assign(xwn__toy) and find_callname(f_ir, xwn__toy.value
                ) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[xwn__toy.target.name].remove(xwn__toy.value)
                xwn__toy.value = ir.Const(False, xwn__toy.loc)
                f_ir._definitions[xwn__toy.target.name].append(xwn__toy.value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    kkmz__pwezi = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, uvze__wyu)
    kkmz__pwezi.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    mgo__esjaq = numba.core.compiler.StateDict()
    mgo__esjaq.func_ir = f_ir
    mgo__esjaq.typemap = typemap
    mgo__esjaq.calltypes = calltypes
    mgo__esjaq.typingctx = typingctx
    mgo__esjaq.targetctx = targetctx
    mgo__esjaq.return_type = wsjad__fmkn
    numba.core.rewrites.rewrite_registry.apply('after-inference', mgo__esjaq)
    lxjh__blr = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        wsjad__fmkn, typingctx, targetctx, uvze__wyu, uvfe__kcs, {})
    lxjh__blr.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            ulkq__gmcgy = ctypes.pythonapi.PyCell_Get
            ulkq__gmcgy.restype = ctypes.py_object
            ulkq__gmcgy.argtypes = ctypes.py_object,
            rfvjb__bnm = tuple(ulkq__gmcgy(jbsc__ljc) for jbsc__ljc in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            rfvjb__bnm = closure.items
        assert len(code.co_freevars) == len(rfvjb__bnm)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, rfvjb__bnm
            )


class RegularUDFGenerator(object):

    def __init__(self, in_col_types, out_col_types, pivot_typ, pivot_values,
        is_crosstab, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.out_col_types = out_col_types
        self.pivot_typ = pivot_typ
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        xxo__srshk = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type
            )
        f_ir, pm = compile_to_optimized_ir(func, (xxo__srshk,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        xiwv__aoad, arr_var = _rm_arg_agg_block(block, pm.typemap)
        mjcor__chmi = -1
        for evi__hhhaj, xwn__toy in enumerate(xiwv__aoad):
            if isinstance(xwn__toy, numba.parfors.parfor.Parfor):
                assert mjcor__chmi == -1, 'only one parfor for aggregation function'
                mjcor__chmi = evi__hhhaj
        parfor = None
        if mjcor__chmi != -1:
            parfor = xiwv__aoad[mjcor__chmi]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = xiwv__aoad[:mjcor__chmi] + parfor.init_block.body
        eval_nodes = xiwv__aoad[mjcor__chmi + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for xwn__toy in init_nodes:
            if is_assign(xwn__toy) and xwn__toy.target.name in redvars:
                ind = redvars.index(xwn__toy.target.name)
                reduce_vars[ind] = xwn__toy.target
        var_types = [pm.typemap[ybl__bfxu] for ybl__bfxu in redvars]
        uoi__ert = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        grzm__wfgaa = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        tawtj__bbx = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(tawtj__bbx)
        self.all_update_funcs.append(grzm__wfgaa)
        self.all_combine_funcs.append(uoi__ert)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        qxiw__ygwc = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        nii__yyrn = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        nofhj__lwvcm = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        moly__oph = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, qxiw__ygwc, nii__yyrn, nofhj__lwvcm,
            moly__oph)


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, input_has_index, in_col_types,
    out_col_types, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab):
    if is_crosstab and len(in_col_types) == 0:
        in_col_types = [types.Array(types.intp, 1, 'C')]
    nsxa__mmaeg = []
    for t, gti__spv in zip(in_col_types, agg_func):
        nsxa__mmaeg.append((t, gti__spv))
    flwu__eutw = RegularUDFGenerator(in_col_types, out_col_types, pivot_typ,
        pivot_values, is_crosstab, typingctx, targetctx)
    haqt__hmdop = GeneralUDFGenerator()
    for in_col_typ, func in nsxa__mmaeg:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            flwu__eutw.add_udf(in_col_typ, func)
        except:
            haqt__hmdop.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = flwu__eutw.gen_all_func()
    general_udf_funcs = haqt__hmdop.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    rydgu__eub = compute_use_defs(parfor.loop_body)
    qtxr__ejm = set()
    for bnvb__akm in rydgu__eub.usemap.values():
        qtxr__ejm |= bnvb__akm
    fdi__ucna = set()
    for bnvb__akm in rydgu__eub.defmap.values():
        fdi__ucna |= bnvb__akm
    pgz__fqe = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    pgz__fqe.body = eval_nodes
    ypztb__uhx = compute_use_defs({(0): pgz__fqe})
    tdm__qlaa = ypztb__uhx.usemap[0]
    plfv__djww = set()
    bsvfa__sgi = []
    rwa__ycf = []
    for xwn__toy in reversed(init_nodes):
        luxk__syw = {ybl__bfxu.name for ybl__bfxu in xwn__toy.list_vars()}
        if is_assign(xwn__toy):
            ybl__bfxu = xwn__toy.target.name
            luxk__syw.remove(ybl__bfxu)
            if (ybl__bfxu in qtxr__ejm and ybl__bfxu not in plfv__djww and 
                ybl__bfxu not in tdm__qlaa and ybl__bfxu not in fdi__ucna):
                rwa__ycf.append(xwn__toy)
                qtxr__ejm |= luxk__syw
                fdi__ucna.add(ybl__bfxu)
                continue
        plfv__djww |= luxk__syw
        bsvfa__sgi.append(xwn__toy)
    rwa__ycf.reverse()
    bsvfa__sgi.reverse()
    qzz__fxl = min(parfor.loop_body.keys())
    xmzut__yrtbb = parfor.loop_body[qzz__fxl]
    xmzut__yrtbb.body = rwa__ycf + xmzut__yrtbb.body
    return bsvfa__sgi


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    xewlt__xwg = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    hkuj__oxc = set()
    qkdo__dsccv = []
    for xwn__toy in init_nodes:
        if is_assign(xwn__toy) and isinstance(xwn__toy.value, ir.Global
            ) and isinstance(xwn__toy.value.value, pytypes.FunctionType
            ) and xwn__toy.value.value in xewlt__xwg:
            hkuj__oxc.add(xwn__toy.target.name)
        elif is_call_assign(xwn__toy
            ) and xwn__toy.value.func.name in hkuj__oxc:
            pass
        else:
            qkdo__dsccv.append(xwn__toy)
    init_nodes = qkdo__dsccv
    hhist__yts = types.Tuple(var_types)
    kwgg__pvn = lambda : None
    f_ir = compile_to_numba_ir(kwgg__pvn, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    wjirb__sxo = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    rofvs__ihxdg = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        wjirb__sxo, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [rofvs__ihxdg] + block.body
    block.body[-2].value.value = wjirb__sxo
    oixs__newl = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        hhist__yts, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sxyz__nmii = numba.core.target_extension.dispatcher_registry[cpu_target](
        kwgg__pvn)
    sxyz__nmii.add_overload(oixs__newl)
    return sxyz__nmii


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    jmt__houy = len(update_funcs)
    ihklc__jimf = len(in_col_types)
    if pivot_values is not None:
        assert ihklc__jimf == 1
    cjq__ackn = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        sov__gmn = redvar_offsets[ihklc__jimf]
        cjq__ackn += '  pv = pivot_arr[i]\n'
        for zfp__oln, ajy__jjiwk in enumerate(pivot_values):
            qitav__rvn = 'el' if zfp__oln != 0 else ''
            cjq__ackn += "  {}if pv == '{}':\n".format(qitav__rvn, ajy__jjiwk)
            ysy__upfwl = sov__gmn * zfp__oln
            vozmc__bho = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                evi__hhhaj) for evi__hhhaj in range(ysy__upfwl +
                redvar_offsets[0], ysy__upfwl + redvar_offsets[1])])
            hffd__mfhjy = 'data_in[0][i]'
            if is_crosstab:
                hffd__mfhjy = '0'
            cjq__ackn += '    {} = update_vars_0({}, {})\n'.format(vozmc__bho,
                vozmc__bho, hffd__mfhjy)
    else:
        for zfp__oln in range(jmt__houy):
            vozmc__bho = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                evi__hhhaj) for evi__hhhaj in range(redvar_offsets[zfp__oln
                ], redvar_offsets[zfp__oln + 1])])
            if vozmc__bho:
                cjq__ackn += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(vozmc__bho, zfp__oln, vozmc__bho, 0 if 
                    ihklc__jimf == 1 else zfp__oln))
    cjq__ackn += '  return\n'
    vcbp__jkxzs = {}
    for evi__hhhaj, gti__spv in enumerate(update_funcs):
        vcbp__jkxzs['update_vars_{}'.format(evi__hhhaj)] = gti__spv
    pmxj__zzo = {}
    exec(cjq__ackn, vcbp__jkxzs, pmxj__zzo)
    qzev__ymqr = pmxj__zzo['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(qzev__ymqr)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    ypp__nwlp = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    arg_typs = ypp__nwlp, ypp__nwlp, types.intp, types.intp, pivot_typ
    iqmjt__jvom = len(redvar_offsets) - 1
    sov__gmn = redvar_offsets[iqmjt__jvom]
    cjq__ackn = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert iqmjt__jvom == 1
        for klfc__ebuom in range(len(pivot_values)):
            ysy__upfwl = sov__gmn * klfc__ebuom
            vozmc__bho = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                evi__hhhaj) for evi__hhhaj in range(ysy__upfwl +
                redvar_offsets[0], ysy__upfwl + redvar_offsets[1])])
            jppt__imvx = ', '.join(['recv_arrs[{}][i]'.format(evi__hhhaj) for
                evi__hhhaj in range(ysy__upfwl + redvar_offsets[0], 
                ysy__upfwl + redvar_offsets[1])])
            cjq__ackn += '  {} = combine_vars_0({}, {})\n'.format(vozmc__bho,
                vozmc__bho, jppt__imvx)
    else:
        for zfp__oln in range(iqmjt__jvom):
            vozmc__bho = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                evi__hhhaj) for evi__hhhaj in range(redvar_offsets[zfp__oln
                ], redvar_offsets[zfp__oln + 1])])
            jppt__imvx = ', '.join(['recv_arrs[{}][i]'.format(evi__hhhaj) for
                evi__hhhaj in range(redvar_offsets[zfp__oln],
                redvar_offsets[zfp__oln + 1])])
            if jppt__imvx:
                cjq__ackn += '  {} = combine_vars_{}({}, {})\n'.format(
                    vozmc__bho, zfp__oln, vozmc__bho, jppt__imvx)
    cjq__ackn += '  return\n'
    vcbp__jkxzs = {}
    for evi__hhhaj, gti__spv in enumerate(combine_funcs):
        vcbp__jkxzs['combine_vars_{}'.format(evi__hhhaj)] = gti__spv
    pmxj__zzo = {}
    exec(cjq__ackn, vcbp__jkxzs, pmxj__zzo)
    ouz__uft = pmxj__zzo['combine_all_f']
    f_ir = compile_to_numba_ir(ouz__uft, vcbp__jkxzs)
    nofhj__lwvcm = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sxyz__nmii = numba.core.target_extension.dispatcher_registry[cpu_target](
        ouz__uft)
    sxyz__nmii.add_overload(nofhj__lwvcm)
    return sxyz__nmii


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    ypp__nwlp = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    out_col_typs = types.Tuple(out_col_typs)
    iqmjt__jvom = len(redvar_offsets) - 1
    sov__gmn = redvar_offsets[iqmjt__jvom]
    cjq__ackn = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert iqmjt__jvom == 1
        for zfp__oln in range(len(pivot_values)):
            ysy__upfwl = sov__gmn * zfp__oln
            vozmc__bho = ', '.join(['redvar_arrs[{}][j]'.format(evi__hhhaj) for
                evi__hhhaj in range(ysy__upfwl + redvar_offsets[0], 
                ysy__upfwl + redvar_offsets[1])])
            cjq__ackn += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                zfp__oln, vozmc__bho)
    else:
        for zfp__oln in range(iqmjt__jvom):
            vozmc__bho = ', '.join(['redvar_arrs[{}][j]'.format(evi__hhhaj) for
                evi__hhhaj in range(redvar_offsets[zfp__oln],
                redvar_offsets[zfp__oln + 1])])
            cjq__ackn += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                zfp__oln, zfp__oln, vozmc__bho)
    cjq__ackn += '  return\n'
    vcbp__jkxzs = {}
    for evi__hhhaj, gti__spv in enumerate(eval_funcs):
        vcbp__jkxzs['eval_vars_{}'.format(evi__hhhaj)] = gti__spv
    pmxj__zzo = {}
    exec(cjq__ackn, vcbp__jkxzs, pmxj__zzo)
    uicm__qzlp = pmxj__zzo['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(uicm__qzlp)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    ldtdr__dcfuo = len(var_types)
    oeum__ertmj = [f'in{evi__hhhaj}' for evi__hhhaj in range(ldtdr__dcfuo)]
    hhist__yts = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    ypme__ixgm = hhist__yts(0)
    cjq__ackn = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        oeum__ertmj))
    pmxj__zzo = {}
    exec(cjq__ackn, {'_zero': ypme__ixgm}, pmxj__zzo)
    tit__yjl = pmxj__zzo['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(tit__yjl, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': ypme__ixgm}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    fnecz__aes = []
    for evi__hhhaj, ybl__bfxu in enumerate(reduce_vars):
        fnecz__aes.append(ir.Assign(block.body[evi__hhhaj].target,
            ybl__bfxu, ybl__bfxu.loc))
        for mkz__yygh in ybl__bfxu.versioned_names:
            fnecz__aes.append(ir.Assign(ybl__bfxu, ir.Var(ybl__bfxu.scope,
                mkz__yygh, ybl__bfxu.loc), ybl__bfxu.loc))
    block.body = block.body[:ldtdr__dcfuo] + fnecz__aes + eval_nodes
    tawtj__bbx = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        hhist__yts, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sxyz__nmii = numba.core.target_extension.dispatcher_registry[cpu_target](
        tit__yjl)
    sxyz__nmii.add_overload(tawtj__bbx)
    return sxyz__nmii


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    ldtdr__dcfuo = len(redvars)
    jga__mbd = [f'v{evi__hhhaj}' for evi__hhhaj in range(ldtdr__dcfuo)]
    oeum__ertmj = [f'in{evi__hhhaj}' for evi__hhhaj in range(ldtdr__dcfuo)]
    cjq__ackn = 'def agg_combine({}):\n'.format(', '.join(jga__mbd +
        oeum__ertmj))
    kvaxx__usm = wrap_parfor_blocks(parfor)
    opsrh__vrel = find_topo_order(kvaxx__usm)
    opsrh__vrel = opsrh__vrel[1:]
    unwrap_parfor_blocks(parfor)
    xen__dffn = {}
    wgbl__yvo = []
    for srlaa__hvuq in opsrh__vrel:
        xigq__axfm = parfor.loop_body[srlaa__hvuq]
        for xwn__toy in xigq__axfm.body:
            if is_call_assign(xwn__toy) and guard(find_callname, f_ir,
                xwn__toy.value) == ('__special_combine', 'bodo.ir.aggregate'):
                args = xwn__toy.value.args
                jnol__xlxrm = []
                eqmvo__rpeus = []
                for ybl__bfxu in args[:-1]:
                    ind = redvars.index(ybl__bfxu.name)
                    wgbl__yvo.append(ind)
                    jnol__xlxrm.append('v{}'.format(ind))
                    eqmvo__rpeus.append('in{}'.format(ind))
                vyaz__ebly = '__special_combine__{}'.format(len(xen__dffn))
                cjq__ackn += '    ({},) = {}({})\n'.format(', '.join(
                    jnol__xlxrm), vyaz__ebly, ', '.join(jnol__xlxrm +
                    eqmvo__rpeus))
                dzghq__quan = ir.Expr.call(args[-1], [], (), xigq__axfm.loc)
                ucola__sfbmh = guard(find_callname, f_ir, dzghq__quan)
                assert ucola__sfbmh == ('_var_combine', 'bodo.ir.aggregate')
                ucola__sfbmh = bodo.ir.aggregate._var_combine
                xen__dffn[vyaz__ebly] = ucola__sfbmh
            if is_assign(xwn__toy) and xwn__toy.target.name in redvars:
                tnxq__xxk = xwn__toy.target.name
                ind = redvars.index(tnxq__xxk)
                if ind in wgbl__yvo:
                    continue
                if len(f_ir._definitions[tnxq__xxk]) == 2:
                    var_def = f_ir._definitions[tnxq__xxk][0]
                    cjq__ackn += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[tnxq__xxk][1]
                    cjq__ackn += _match_reduce_def(var_def, f_ir, ind)
    cjq__ackn += '    return {}'.format(', '.join(['v{}'.format(evi__hhhaj) for
        evi__hhhaj in range(ldtdr__dcfuo)]))
    pmxj__zzo = {}
    exec(cjq__ackn, {}, pmxj__zzo)
    pbtma__sdhn = pmxj__zzo['agg_combine']
    arg_typs = tuple(2 * var_types)
    vcbp__jkxzs = {'numba': numba, 'bodo': bodo, 'np': np}
    vcbp__jkxzs.update(xen__dffn)
    f_ir = compile_to_numba_ir(pbtma__sdhn, vcbp__jkxzs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=pm.
        typemap, calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    hhist__yts = pm.typemap[block.body[-1].value.name]
    uoi__ert = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        hhist__yts, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sxyz__nmii = numba.core.target_extension.dispatcher_registry[cpu_target](
        pbtma__sdhn)
    sxyz__nmii.add_overload(uoi__ert)
    return sxyz__nmii


def _match_reduce_def(var_def, f_ir, ind):
    cjq__ackn = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        cjq__ackn = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        bojde__ddztq = guard(find_callname, f_ir, var_def)
        if bojde__ddztq == ('min', 'builtins'):
            cjq__ackn = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if bojde__ddztq == ('max', 'builtins'):
            cjq__ackn = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return cjq__ackn


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    ldtdr__dcfuo = len(redvars)
    lco__prws = 1
    xndja__daar = []
    for evi__hhhaj in range(lco__prws):
        qqk__hoau = ir.Var(arr_var.scope, f'$input{evi__hhhaj}', arr_var.loc)
        xndja__daar.append(qqk__hoau)
    iot__uaye = parfor.loop_nests[0].index_variable
    xzmja__geg = [0] * ldtdr__dcfuo
    for xigq__axfm in parfor.loop_body.values():
        jztfk__dess = []
        for xwn__toy in xigq__axfm.body:
            if is_var_assign(xwn__toy
                ) and xwn__toy.value.name == iot__uaye.name:
                continue
            if is_getitem(xwn__toy
                ) and xwn__toy.value.value.name == arr_var.name:
                xwn__toy.value = xndja__daar[0]
            if is_call_assign(xwn__toy) and guard(find_callname, pm.func_ir,
                xwn__toy.value) == ('isna', 'bodo.libs.array_kernels'
                ) and xwn__toy.value.args[0].name == arr_var.name:
                xwn__toy.value = ir.Const(False, xwn__toy.target.loc)
            if is_assign(xwn__toy) and xwn__toy.target.name in redvars:
                ind = redvars.index(xwn__toy.target.name)
                xzmja__geg[ind] = xwn__toy.target
            jztfk__dess.append(xwn__toy)
        xigq__axfm.body = jztfk__dess
    jga__mbd = ['v{}'.format(evi__hhhaj) for evi__hhhaj in range(ldtdr__dcfuo)]
    oeum__ertmj = ['in{}'.format(evi__hhhaj) for evi__hhhaj in range(lco__prws)
        ]
    cjq__ackn = 'def agg_update({}):\n'.format(', '.join(jga__mbd +
        oeum__ertmj))
    cjq__ackn += '    __update_redvars()\n'
    cjq__ackn += '    return {}'.format(', '.join(['v{}'.format(evi__hhhaj) for
        evi__hhhaj in range(ldtdr__dcfuo)]))
    pmxj__zzo = {}
    exec(cjq__ackn, {}, pmxj__zzo)
    sctuz__nyg = pmxj__zzo['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * lco__prws)
    f_ir = compile_to_numba_ir(sctuz__nyg, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    ezb__ijwt = f_ir.blocks.popitem()[1].body
    hhist__yts = pm.typemap[ezb__ijwt[-1].value.name]
    kvaxx__usm = wrap_parfor_blocks(parfor)
    opsrh__vrel = find_topo_order(kvaxx__usm)
    opsrh__vrel = opsrh__vrel[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    xmzut__yrtbb = f_ir.blocks[opsrh__vrel[0]]
    wmw__yvr = f_ir.blocks[opsrh__vrel[-1]]
    pimz__uxue = ezb__ijwt[:ldtdr__dcfuo + lco__prws]
    if ldtdr__dcfuo > 1:
        vmnsz__yoooh = ezb__ijwt[-3:]
        assert is_assign(vmnsz__yoooh[0]) and isinstance(vmnsz__yoooh[0].
            value, ir.Expr) and vmnsz__yoooh[0].value.op == 'build_tuple'
    else:
        vmnsz__yoooh = ezb__ijwt[-2:]
    for evi__hhhaj in range(ldtdr__dcfuo):
        oxie__zjro = ezb__ijwt[evi__hhhaj].target
        itot__feoo = ir.Assign(oxie__zjro, xzmja__geg[evi__hhhaj],
            oxie__zjro.loc)
        pimz__uxue.append(itot__feoo)
    for evi__hhhaj in range(ldtdr__dcfuo, ldtdr__dcfuo + lco__prws):
        oxie__zjro = ezb__ijwt[evi__hhhaj].target
        itot__feoo = ir.Assign(oxie__zjro, xndja__daar[evi__hhhaj -
            ldtdr__dcfuo], oxie__zjro.loc)
        pimz__uxue.append(itot__feoo)
    xmzut__yrtbb.body = pimz__uxue + xmzut__yrtbb.body
    vxqi__thmdx = []
    for evi__hhhaj in range(ldtdr__dcfuo):
        oxie__zjro = ezb__ijwt[evi__hhhaj].target
        itot__feoo = ir.Assign(xzmja__geg[evi__hhhaj], oxie__zjro,
            oxie__zjro.loc)
        vxqi__thmdx.append(itot__feoo)
    wmw__yvr.body += vxqi__thmdx + vmnsz__yoooh
    dlrjg__teeb = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        hhist__yts, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sxyz__nmii = numba.core.target_extension.dispatcher_registry[cpu_target](
        sctuz__nyg)
    sxyz__nmii.add_overload(dlrjg__teeb)
    return sxyz__nmii


def _rm_arg_agg_block(block, typemap):
    xiwv__aoad = []
    arr_var = None
    for evi__hhhaj, xwn__toy in enumerate(block.body):
        if is_assign(xwn__toy) and isinstance(xwn__toy.value, ir.Arg):
            arr_var = xwn__toy.target
            ast__nti = typemap[arr_var.name]
            if not isinstance(ast__nti, types.ArrayCompatible):
                xiwv__aoad += block.body[evi__hhhaj + 1:]
                break
            jiykn__zko = block.body[evi__hhhaj + 1]
            assert is_assign(jiykn__zko) and isinstance(jiykn__zko.value,
                ir.Expr
                ) and jiykn__zko.value.op == 'getattr' and jiykn__zko.value.attr == 'shape' and jiykn__zko.value.value.name == arr_var.name
            zofeo__dmrwk = jiykn__zko.target
            xlcyr__lymdt = block.body[evi__hhhaj + 2]
            assert is_assign(xlcyr__lymdt) and isinstance(xlcyr__lymdt.
                value, ir.Expr
                ) and xlcyr__lymdt.value.op == 'static_getitem' and xlcyr__lymdt.value.value.name == zofeo__dmrwk.name
            xiwv__aoad += block.body[evi__hhhaj + 3:]
            break
        xiwv__aoad.append(xwn__toy)
    return xiwv__aoad, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    kvaxx__usm = wrap_parfor_blocks(parfor)
    opsrh__vrel = find_topo_order(kvaxx__usm)
    opsrh__vrel = opsrh__vrel[1:]
    unwrap_parfor_blocks(parfor)
    for srlaa__hvuq in reversed(opsrh__vrel):
        for xwn__toy in reversed(parfor.loop_body[srlaa__hvuq].body):
            if isinstance(xwn__toy, ir.Assign) and (xwn__toy.target.name in
                parfor_params or xwn__toy.target.name in var_to_param):
                vutcq__spbb = xwn__toy.target.name
                rhs = xwn__toy.value
                xsp__kdm = (vutcq__spbb if vutcq__spbb in parfor_params else
                    var_to_param[vutcq__spbb])
                pegg__qdq = []
                if isinstance(rhs, ir.Var):
                    pegg__qdq = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    pegg__qdq = [ybl__bfxu.name for ybl__bfxu in xwn__toy.
                        value.list_vars()]
                param_uses[xsp__kdm].extend(pegg__qdq)
                for ybl__bfxu in pegg__qdq:
                    var_to_param[ybl__bfxu] = xsp__kdm
            if isinstance(xwn__toy, Parfor):
                get_parfor_reductions(xwn__toy, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for ydd__rtnz, pegg__qdq in param_uses.items():
        if ydd__rtnz in pegg__qdq and ydd__rtnz not in reduce_varnames:
            reduce_varnames.append(ydd__rtnz)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
