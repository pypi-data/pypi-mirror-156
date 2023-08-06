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
            uekco__xgft = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            fmol__lihq = cgutils.get_or_insert_function(builder.module,
                uekco__xgft, sym._literal_value)
            builder.call(fmol__lihq, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            uekco__xgft = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            fmol__lihq = cgutils.get_or_insert_function(builder.module,
                uekco__xgft, sym._literal_value)
            builder.call(fmol__lihq, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            uekco__xgft = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            fmol__lihq = cgutils.get_or_insert_function(builder.module,
                uekco__xgft, sym._literal_value)
            builder.call(fmol__lihq, [context.get_constant_null(sig.args[0]
                ), context.get_constant_null(sig.args[1]), context.
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
        oztrs__liu = True
        vtdjm__dap = 1
        irs__hpip = -1
        if isinstance(rhs, ir.Expr):
            for ocnwt__sdles in rhs.kws:
                if func_name in list_cumulative:
                    if ocnwt__sdles[0] == 'skipna':
                        oztrs__liu = guard(find_const, func_ir, ocnwt__sdles[1]
                            )
                        if not isinstance(oztrs__liu, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if ocnwt__sdles[0] == 'dropna':
                        oztrs__liu = guard(find_const, func_ir, ocnwt__sdles[1]
                            )
                        if not isinstance(oztrs__liu, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            vtdjm__dap = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', vtdjm__dap)
            vtdjm__dap = guard(find_const, func_ir, vtdjm__dap)
        if func_name == 'head':
            irs__hpip = get_call_expr_arg('head', rhs.args, dict(rhs.kws), 
                0, 'n', 5)
            if not isinstance(irs__hpip, int):
                irs__hpip = guard(find_const, func_ir, irs__hpip)
            if irs__hpip < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = oztrs__liu
        func.periods = vtdjm__dap
        func.head_n = irs__hpip
        if func_name == 'transform':
            kws = dict(rhs.kws)
            svs__xdbc = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            fobxv__nvq = typemap[svs__xdbc.name]
            efrhc__pwmhm = None
            if isinstance(fobxv__nvq, str):
                efrhc__pwmhm = fobxv__nvq
            elif is_overload_constant_str(fobxv__nvq):
                efrhc__pwmhm = get_overload_const_str(fobxv__nvq)
            elif bodo.utils.typing.is_builtin_function(fobxv__nvq):
                efrhc__pwmhm = bodo.utils.typing.get_builtin_function_name(
                    fobxv__nvq)
            if efrhc__pwmhm not in bodo.ir.aggregate.supported_transform_funcs[
                :]:
                raise BodoError(
                    f'unsupported transform function {efrhc__pwmhm}')
            func.transform_func = supported_agg_funcs.index(efrhc__pwmhm)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    svs__xdbc = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if svs__xdbc == '':
        fobxv__nvq = types.none
    else:
        fobxv__nvq = typemap[svs__xdbc.name]
    if is_overload_constant_dict(fobxv__nvq):
        ucrzx__jwlkm = get_overload_constant_dict(fobxv__nvq)
        dnj__skxv = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in ucrzx__jwlkm.values()]
        return dnj__skxv
    if fobxv__nvq == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(fobxv__nvq, types.BaseTuple) or is_overload_constant_list(
        fobxv__nvq):
        dnj__skxv = []
        puqw__vmt = 0
        if is_overload_constant_list(fobxv__nvq):
            fbp__cdj = get_overload_const_list(fobxv__nvq)
        else:
            fbp__cdj = fobxv__nvq.types
        for t in fbp__cdj:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                dnj__skxv.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(fbp__cdj) > 1:
                    func.fname = '<lambda_' + str(puqw__vmt) + '>'
                    puqw__vmt += 1
                dnj__skxv.append(func)
        return [dnj__skxv]
    if is_overload_constant_str(fobxv__nvq):
        func_name = get_overload_const_str(fobxv__nvq)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(fobxv__nvq):
        func_name = bodo.utils.typing.get_builtin_function_name(fobxv__nvq)
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
        puqw__vmt = 0
        blw__pzzdy = []
        for vxwt__bmgl in f_val:
            func = get_agg_func_udf(func_ir, vxwt__bmgl, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{puqw__vmt}>'
                puqw__vmt += 1
            blw__pzzdy.append(func)
        return blw__pzzdy
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
    efrhc__pwmhm = code.co_name
    return efrhc__pwmhm


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
            knbrn__cpxn = types.DType(args[0])
            return signature(knbrn__cpxn, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    zpxo__mpmph = nobs_a + nobs_b
    lcrk__wuarj = (nobs_a * mean_a + nobs_b * mean_b) / zpxo__mpmph
    maoze__rzhd = mean_b - mean_a
    jjnzw__eqqu = (ssqdm_a + ssqdm_b + maoze__rzhd * maoze__rzhd * nobs_a *
        nobs_b / zpxo__mpmph)
    return jjnzw__eqqu, lcrk__wuarj, zpxo__mpmph


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
        cdlw__pyzux = ''
        for drj__cluxw, jfg__xmtd in self.df_out_vars.items():
            cdlw__pyzux += "'{}':{}, ".format(drj__cluxw, jfg__xmtd.name)
        eom__kxtc = '{}{{{}}}'.format(self.df_out, cdlw__pyzux)
        nsz__jqk = ''
        for drj__cluxw, jfg__xmtd in self.df_in_vars.items():
            nsz__jqk += "'{}':{}, ".format(drj__cluxw, jfg__xmtd.name)
        stxnm__qret = '{}{{{}}}'.format(self.df_in, nsz__jqk)
        hqk__xig = 'pivot {}:{}'.format(self.pivot_arr.name, self.pivot_values
            ) if self.pivot_arr is not None else ''
        key_names = ','.join([str(biss__cqr) for biss__cqr in self.key_names])
        vegm__bmzhi = ','.join([jfg__xmtd.name for jfg__xmtd in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(eom__kxtc,
            stxnm__qret, key_names, vegm__bmzhi, hqk__xig)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        yajw__piiw, tpx__rcr = self.gb_info_out.pop(out_col_name)
        if yajw__piiw is None and not self.is_crosstab:
            return
        ioq__xpi = self.gb_info_in[yajw__piiw]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for ocob__gnw, (func, cdlw__pyzux) in enumerate(ioq__xpi):
                try:
                    cdlw__pyzux.remove(out_col_name)
                    if len(cdlw__pyzux) == 0:
                        ioq__xpi.pop(ocob__gnw)
                        break
                except ValueError as hwu__xhtr:
                    continue
        else:
            for ocob__gnw, (func, ryl__fnx) in enumerate(ioq__xpi):
                if ryl__fnx == out_col_name:
                    ioq__xpi.pop(ocob__gnw)
                    break
        if len(ioq__xpi) == 0:
            self.gb_info_in.pop(yajw__piiw)
            self.df_in_vars.pop(yajw__piiw)


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({jfg__xmtd.name for jfg__xmtd in aggregate_node.key_arrs})
    use_set.update({jfg__xmtd.name for jfg__xmtd in aggregate_node.
        df_in_vars.values()})
    if aggregate_node.pivot_arr is not None:
        use_set.add(aggregate_node.pivot_arr.name)
    def_set.update({jfg__xmtd.name for jfg__xmtd in aggregate_node.
        df_out_vars.values()})
    if aggregate_node.out_key_vars is not None:
        def_set.update({jfg__xmtd.name for jfg__xmtd in aggregate_node.
            out_key_vars})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(aggregate_node, lives_no_aliases, lives,
    arg_aliases, alias_map, func_ir, typemap):
    amll__hdtj = [swu__riasu for swu__riasu, hleu__wvxf in aggregate_node.
        df_out_vars.items() if hleu__wvxf.name not in lives]
    for btu__wjed in amll__hdtj:
        aggregate_node.remove_out_col(btu__wjed)
    out_key_vars = aggregate_node.out_key_vars
    if out_key_vars is not None and all(jfg__xmtd.name not in lives for
        jfg__xmtd in out_key_vars):
        aggregate_node.out_key_vars = None
    if len(aggregate_node.df_out_vars
        ) == 0 and aggregate_node.out_key_vars is None:
        return None
    return aggregate_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    tmpo__haoh = set(jfg__xmtd.name for jfg__xmtd in aggregate_node.
        df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        tmpo__haoh.update({jfg__xmtd.name for jfg__xmtd in aggregate_node.
            out_key_vars})
    return set(), tmpo__haoh


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for ocob__gnw in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[ocob__gnw] = replace_vars_inner(aggregate_node
            .key_arrs[ocob__gnw], var_dict)
    for swu__riasu in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[swu__riasu] = replace_vars_inner(
            aggregate_node.df_in_vars[swu__riasu], var_dict)
    for swu__riasu in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[swu__riasu] = replace_vars_inner(
            aggregate_node.df_out_vars[swu__riasu], var_dict)
    if aggregate_node.out_key_vars is not None:
        for ocob__gnw in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[ocob__gnw] = replace_vars_inner(
                aggregate_node.out_key_vars[ocob__gnw], var_dict)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = replace_vars_inner(aggregate_node.
            pivot_arr, var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    if debug_prints():
        print('visiting aggregate vars for:', aggregate_node)
        print('cbdata: ', sorted(cbdata.items()))
    for ocob__gnw in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[ocob__gnw] = visit_vars_inner(aggregate_node
            .key_arrs[ocob__gnw], callback, cbdata)
    for swu__riasu in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[swu__riasu] = visit_vars_inner(aggregate_node
            .df_in_vars[swu__riasu], callback, cbdata)
    for swu__riasu in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[swu__riasu] = visit_vars_inner(
            aggregate_node.df_out_vars[swu__riasu], callback, cbdata)
    if aggregate_node.out_key_vars is not None:
        for ocob__gnw in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[ocob__gnw] = visit_vars_inner(
                aggregate_node.out_key_vars[ocob__gnw], callback, cbdata)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = visit_vars_inner(aggregate_node.
            pivot_arr, callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    assert len(aggregate_node.df_out_vars
        ) > 0 or aggregate_node.out_key_vars is not None or aggregate_node.is_crosstab, 'empty aggregate in array analysis'
    ctwg__iwsru = []
    for ldd__crds in aggregate_node.key_arrs:
        pab__zabv = equiv_set.get_shape(ldd__crds)
        if pab__zabv:
            ctwg__iwsru.append(pab__zabv[0])
    if aggregate_node.pivot_arr is not None:
        pab__zabv = equiv_set.get_shape(aggregate_node.pivot_arr)
        if pab__zabv:
            ctwg__iwsru.append(pab__zabv[0])
    for hleu__wvxf in aggregate_node.df_in_vars.values():
        pab__zabv = equiv_set.get_shape(hleu__wvxf)
        if pab__zabv:
            ctwg__iwsru.append(pab__zabv[0])
    if len(ctwg__iwsru) > 1:
        equiv_set.insert_equiv(*ctwg__iwsru)
    lqu__bxeon = []
    ctwg__iwsru = []
    bha__slvv = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        bha__slvv.extend(aggregate_node.out_key_vars)
    for hleu__wvxf in bha__slvv:
        ynyz__klp = typemap[hleu__wvxf.name]
        uoaw__ebist = array_analysis._gen_shape_call(equiv_set, hleu__wvxf,
            ynyz__klp.ndim, None, lqu__bxeon)
        equiv_set.insert_equiv(hleu__wvxf, uoaw__ebist)
        ctwg__iwsru.append(uoaw__ebist[0])
        equiv_set.define(hleu__wvxf, set())
    if len(ctwg__iwsru) > 1:
        equiv_set.insert_equiv(*ctwg__iwsru)
    return [], lqu__bxeon


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    rsgc__ycb = Distribution.OneD
    for hleu__wvxf in aggregate_node.df_in_vars.values():
        rsgc__ycb = Distribution(min(rsgc__ycb.value, array_dists[
            hleu__wvxf.name].value))
    for ldd__crds in aggregate_node.key_arrs:
        rsgc__ycb = Distribution(min(rsgc__ycb.value, array_dists[ldd__crds
            .name].value))
    if aggregate_node.pivot_arr is not None:
        rsgc__ycb = Distribution(min(rsgc__ycb.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = rsgc__ycb
    for hleu__wvxf in aggregate_node.df_in_vars.values():
        array_dists[hleu__wvxf.name] = rsgc__ycb
    for ldd__crds in aggregate_node.key_arrs:
        array_dists[ldd__crds.name] = rsgc__ycb
    jsx__izeme = Distribution.OneD_Var
    for hleu__wvxf in aggregate_node.df_out_vars.values():
        if hleu__wvxf.name in array_dists:
            jsx__izeme = Distribution(min(jsx__izeme.value, array_dists[
                hleu__wvxf.name].value))
    if aggregate_node.out_key_vars is not None:
        for hleu__wvxf in aggregate_node.out_key_vars:
            if hleu__wvxf.name in array_dists:
                jsx__izeme = Distribution(min(jsx__izeme.value, array_dists
                    [hleu__wvxf.name].value))
    jsx__izeme = Distribution(min(jsx__izeme.value, rsgc__ycb.value))
    for hleu__wvxf in aggregate_node.df_out_vars.values():
        array_dists[hleu__wvxf.name] = jsx__izeme
    if aggregate_node.out_key_vars is not None:
        for mikxs__yfizx in aggregate_node.out_key_vars:
            array_dists[mikxs__yfizx.name] = jsx__izeme
    if jsx__izeme != Distribution.OneD_Var:
        for ldd__crds in aggregate_node.key_arrs:
            array_dists[ldd__crds.name] = jsx__izeme
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = jsx__izeme
        for hleu__wvxf in aggregate_node.df_in_vars.values():
            array_dists[hleu__wvxf.name] = jsx__izeme


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for hleu__wvxf in agg_node.df_out_vars.values():
        definitions[hleu__wvxf.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for mikxs__yfizx in agg_node.out_key_vars:
            definitions[mikxs__yfizx.name].append(agg_node)
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
        for jfg__xmtd in (list(agg_node.df_in_vars.values()) + list(
            agg_node.df_out_vars.values()) + agg_node.key_arrs):
            if array_dists[jfg__xmtd.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                jfg__xmtd.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    xwn__kjf = tuple(typemap[jfg__xmtd.name] for jfg__xmtd in agg_node.key_arrs
        )
    oirs__tuc = [jfg__xmtd for mmzo__jbfs, jfg__xmtd in agg_node.df_in_vars
        .items()]
    cdlv__wck = [jfg__xmtd for mmzo__jbfs, jfg__xmtd in agg_node.
        df_out_vars.items()]
    in_col_typs = []
    dnj__skxv = []
    if agg_node.pivot_arr is not None:
        for yajw__piiw, ioq__xpi in agg_node.gb_info_in.items():
            for func, tpx__rcr in ioq__xpi:
                if yajw__piiw is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        yajw__piiw].name])
                dnj__skxv.append(func)
    else:
        for yajw__piiw, func in agg_node.gb_info_out.values():
            if yajw__piiw is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[yajw__piiw].
                    name])
            dnj__skxv.append(func)
    out_col_typs = tuple(typemap[jfg__xmtd.name] for jfg__xmtd in cdlv__wck)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(xwn__kjf + tuple(typemap[jfg__xmtd.name] for jfg__xmtd in
        oirs__tuc) + (pivot_typ,))
    in_col_typs = [to_str_arr_if_dict_array(t) for t in in_col_typs]
    cnysp__qpst = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for ocob__gnw, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            cnysp__qpst.update({f'in_cat_dtype_{ocob__gnw}': in_col_typ})
    for ocob__gnw, ktndr__efng in enumerate(out_col_typs):
        if isinstance(ktndr__efng, bodo.CategoricalArrayType):
            cnysp__qpst.update({f'out_cat_dtype_{ocob__gnw}': ktndr__efng})
    udf_func_struct = get_udf_func_struct(dnj__skxv, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    ecntt__elkhu = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, parallel, udf_func_struct)
    cnysp__qpst.update({'pd': pd, 'pre_alloc_string_array':
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
            cnysp__qpst.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            cnysp__qpst.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    zgljp__lld = compile_to_numba_ir(ecntt__elkhu, cnysp__qpst, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    xzvpv__kssrd = []
    if agg_node.pivot_arr is None:
        ryia__iser = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        drd__ekkn = ir.Var(ryia__iser, mk_unique_var('dummy_none'), loc)
        typemap[drd__ekkn.name] = types.none
        xzvpv__kssrd.append(ir.Assign(ir.Const(None, loc), drd__ekkn, loc))
        oirs__tuc.append(drd__ekkn)
    else:
        oirs__tuc.append(agg_node.pivot_arr)
    replace_arg_nodes(zgljp__lld, agg_node.key_arrs + oirs__tuc)
    dgs__fbez = zgljp__lld.body[-3]
    assert is_assign(dgs__fbez) and isinstance(dgs__fbez.value, ir.Expr
        ) and dgs__fbez.value.op == 'build_tuple'
    xzvpv__kssrd += zgljp__lld.body[:-3]
    bha__slvv = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        bha__slvv += agg_node.out_key_vars
    for ocob__gnw, xctd__fciju in enumerate(bha__slvv):
        tnz__krg = dgs__fbez.value.items[ocob__gnw]
        xzvpv__kssrd.append(ir.Assign(tnz__krg, xctd__fciju, xctd__fciju.loc))
    return xzvpv__kssrd


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def get_numba_set(dtype):
    pass


@infer_global(get_numba_set)
class GetNumbaSetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        geuey__exysa = args[0]
        dtype = types.Tuple([t.dtype for t in geuey__exysa.types]
            ) if isinstance(geuey__exysa, types.BaseTuple
            ) else geuey__exysa.dtype
        if isinstance(geuey__exysa, types.BaseTuple) and len(geuey__exysa.types
            ) == 1:
            dtype = geuey__exysa.types[0].dtype
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
        lxo__oxunt = args[0]
        if lxo__oxunt == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    kii__rxj = context.compile_internal(builder, lambda a: False, sig, args)
    return kii__rxj


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        ugve__uygd = IntDtype(t.dtype).name
        assert ugve__uygd.endswith('Dtype()')
        ugve__uygd = ugve__uygd[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{ugve__uygd}'))"
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
        lms__bivj = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {lms__bivj}_cat_dtype_{colnum})')
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
    cae__yxt = udf_func_struct.var_typs
    jhc__czcpy = len(cae__yxt)
    ayvcj__ewp = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    ayvcj__ewp += '    if is_null_pointer(in_table):\n'
    ayvcj__ewp += '        return\n'
    ayvcj__ewp += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cae__yxt]), ',' if
        len(cae__yxt) == 1 else '')
    iawb__dbdx = n_keys
    kceu__uccyc = []
    redvar_offsets = []
    pwmio__edhaf = []
    if do_combine:
        for ocob__gnw, vxwt__bmgl in enumerate(allfuncs):
            if vxwt__bmgl.ftype != 'udf':
                iawb__dbdx += vxwt__bmgl.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(iawb__dbdx, iawb__dbdx +
                    vxwt__bmgl.n_redvars))
                iawb__dbdx += vxwt__bmgl.n_redvars
                pwmio__edhaf.append(data_in_typs_[func_idx_to_in_col[
                    ocob__gnw]])
                kceu__uccyc.append(func_idx_to_in_col[ocob__gnw] + n_keys)
    else:
        for ocob__gnw, vxwt__bmgl in enumerate(allfuncs):
            if vxwt__bmgl.ftype != 'udf':
                iawb__dbdx += vxwt__bmgl.ncols_post_shuffle
            else:
                redvar_offsets += list(range(iawb__dbdx + 1, iawb__dbdx + 1 +
                    vxwt__bmgl.n_redvars))
                iawb__dbdx += vxwt__bmgl.n_redvars + 1
                pwmio__edhaf.append(data_in_typs_[func_idx_to_in_col[
                    ocob__gnw]])
                kceu__uccyc.append(func_idx_to_in_col[ocob__gnw] + n_keys)
    assert len(redvar_offsets) == jhc__czcpy
    gbadx__ywpdj = len(pwmio__edhaf)
    fiau__djdmv = []
    for ocob__gnw, t in enumerate(pwmio__edhaf):
        fiau__djdmv.append(_gen_dummy_alloc(t, ocob__gnw, True))
    ayvcj__ewp += '    data_in_dummy = ({}{})\n'.format(','.join(
        fiau__djdmv), ',' if len(pwmio__edhaf) == 1 else '')
    ayvcj__ewp += """
    # initialize redvar cols
"""
    ayvcj__ewp += '    init_vals = __init_func()\n'
    for ocob__gnw in range(jhc__czcpy):
        ayvcj__ewp += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(ocob__gnw, redvar_offsets[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(redvar_arr_{})\n'.format(ocob__gnw)
        ayvcj__ewp += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            ocob__gnw, ocob__gnw)
    ayvcj__ewp += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(ocob__gnw) for ocob__gnw in range(jhc__czcpy)]), ',' if 
        jhc__czcpy == 1 else '')
    ayvcj__ewp += '\n'
    for ocob__gnw in range(gbadx__ywpdj):
        ayvcj__ewp += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(ocob__gnw, kceu__uccyc[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(data_in_{})\n'.format(ocob__gnw)
    ayvcj__ewp += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(ocob__gnw) for ocob__gnw in range(gbadx__ywpdj)]), ',' if 
        gbadx__ywpdj == 1 else '')
    ayvcj__ewp += '\n'
    ayvcj__ewp += '    for i in range(len(data_in_0)):\n'
    ayvcj__ewp += '        w_ind = row_to_group[i]\n'
    ayvcj__ewp += '        if w_ind != -1:\n'
    ayvcj__ewp += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    oxs__ilyv = {}
    exec(ayvcj__ewp, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, oxs__ilyv)
    return oxs__ilyv['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    cae__yxt = udf_func_struct.var_typs
    jhc__czcpy = len(cae__yxt)
    ayvcj__ewp = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    ayvcj__ewp += '    if is_null_pointer(in_table):\n'
    ayvcj__ewp += '        return\n'
    ayvcj__ewp += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cae__yxt]), ',' if
        len(cae__yxt) == 1 else '')
    xjy__iqx = n_keys
    myba__wwc = n_keys
    bozc__ogucx = []
    khw__eiubr = []
    for vxwt__bmgl in allfuncs:
        if vxwt__bmgl.ftype != 'udf':
            xjy__iqx += vxwt__bmgl.ncols_pre_shuffle
            myba__wwc += vxwt__bmgl.ncols_post_shuffle
        else:
            bozc__ogucx += list(range(xjy__iqx, xjy__iqx + vxwt__bmgl.
                n_redvars))
            khw__eiubr += list(range(myba__wwc + 1, myba__wwc + 1 +
                vxwt__bmgl.n_redvars))
            xjy__iqx += vxwt__bmgl.n_redvars
            myba__wwc += 1 + vxwt__bmgl.n_redvars
    assert len(bozc__ogucx) == jhc__czcpy
    ayvcj__ewp += """
    # initialize redvar cols
"""
    ayvcj__ewp += '    init_vals = __init_func()\n'
    for ocob__gnw in range(jhc__czcpy):
        ayvcj__ewp += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(ocob__gnw, khw__eiubr[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(redvar_arr_{})\n'.format(ocob__gnw)
        ayvcj__ewp += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            ocob__gnw, ocob__gnw)
    ayvcj__ewp += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(ocob__gnw) for ocob__gnw in range(jhc__czcpy)]), ',' if 
        jhc__czcpy == 1 else '')
    ayvcj__ewp += '\n'
    for ocob__gnw in range(jhc__czcpy):
        ayvcj__ewp += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(ocob__gnw, bozc__ogucx[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(recv_redvar_arr_{})\n'.format(ocob__gnw)
    ayvcj__ewp += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(ocob__gnw) for ocob__gnw in range(
        jhc__czcpy)]), ',' if jhc__czcpy == 1 else '')
    ayvcj__ewp += '\n'
    if jhc__czcpy:
        ayvcj__ewp += '    for i in range(len(recv_redvar_arr_0)):\n'
        ayvcj__ewp += '        w_ind = row_to_group[i]\n'
        ayvcj__ewp += """        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)
"""
    oxs__ilyv = {}
    exec(ayvcj__ewp, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, oxs__ilyv)
    return oxs__ilyv['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    cae__yxt = udf_func_struct.var_typs
    jhc__czcpy = len(cae__yxt)
    iawb__dbdx = n_keys
    redvar_offsets = []
    lllya__fzpyk = []
    out_data_typs = []
    for ocob__gnw, vxwt__bmgl in enumerate(allfuncs):
        if vxwt__bmgl.ftype != 'udf':
            iawb__dbdx += vxwt__bmgl.ncols_post_shuffle
        else:
            lllya__fzpyk.append(iawb__dbdx)
            redvar_offsets += list(range(iawb__dbdx + 1, iawb__dbdx + 1 +
                vxwt__bmgl.n_redvars))
            iawb__dbdx += 1 + vxwt__bmgl.n_redvars
            out_data_typs.append(out_data_typs_[ocob__gnw])
    assert len(redvar_offsets) == jhc__czcpy
    gbadx__ywpdj = len(out_data_typs)
    ayvcj__ewp = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    ayvcj__ewp += '    if is_null_pointer(table):\n'
    ayvcj__ewp += '        return\n'
    ayvcj__ewp += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cae__yxt]), ',' if
        len(cae__yxt) == 1 else '')
    ayvcj__ewp += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for ocob__gnw in range(jhc__czcpy):
        ayvcj__ewp += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(ocob__gnw, redvar_offsets[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(redvar_arr_{})\n'.format(ocob__gnw)
    ayvcj__ewp += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(ocob__gnw) for ocob__gnw in range(jhc__czcpy)]), ',' if 
        jhc__czcpy == 1 else '')
    ayvcj__ewp += '\n'
    for ocob__gnw in range(gbadx__ywpdj):
        ayvcj__ewp += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(ocob__gnw, lllya__fzpyk[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(data_out_{})\n'.format(ocob__gnw)
    ayvcj__ewp += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(ocob__gnw) for ocob__gnw in range(gbadx__ywpdj)]), ',' if 
        gbadx__ywpdj == 1 else '')
    ayvcj__ewp += '\n'
    ayvcj__ewp += '    for i in range(len(data_out_0)):\n'
    ayvcj__ewp += '        __eval_res(redvars, data_out, i)\n'
    oxs__ilyv = {}
    exec(ayvcj__ewp, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, oxs__ilyv)
    return oxs__ilyv['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    iawb__dbdx = n_keys
    gltns__bdab = []
    for ocob__gnw, vxwt__bmgl in enumerate(allfuncs):
        if vxwt__bmgl.ftype == 'gen_udf':
            gltns__bdab.append(iawb__dbdx)
            iawb__dbdx += 1
        elif vxwt__bmgl.ftype != 'udf':
            iawb__dbdx += vxwt__bmgl.ncols_post_shuffle
        else:
            iawb__dbdx += vxwt__bmgl.n_redvars + 1
    ayvcj__ewp = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    ayvcj__ewp += '    if num_groups == 0:\n'
    ayvcj__ewp += '        return\n'
    for ocob__gnw, func in enumerate(udf_func_struct.general_udf_funcs):
        ayvcj__ewp += '    # col {}\n'.format(ocob__gnw)
        ayvcj__ewp += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(gltns__bdab[ocob__gnw], ocob__gnw))
        ayvcj__ewp += '    incref(out_col)\n'
        ayvcj__ewp += '    for j in range(num_groups):\n'
        ayvcj__ewp += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(ocob__gnw, ocob__gnw))
        ayvcj__ewp += '        incref(in_col)\n'
        ayvcj__ewp += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(ocob__gnw))
    cnysp__qpst = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    ukj__wwq = 0
    for ocob__gnw, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[ukj__wwq]
        cnysp__qpst['func_{}'.format(ukj__wwq)] = func
        cnysp__qpst['in_col_{}_typ'.format(ukj__wwq)] = in_col_typs[
            func_idx_to_in_col[ocob__gnw]]
        cnysp__qpst['out_col_{}_typ'.format(ukj__wwq)] = out_col_typs[ocob__gnw
            ]
        ukj__wwq += 1
    oxs__ilyv = {}
    exec(ayvcj__ewp, cnysp__qpst, oxs__ilyv)
    vxwt__bmgl = oxs__ilyv['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    qwor__snqv = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(qwor__snqv, nopython=True)(vxwt__bmgl)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    tnkd__bcli = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        gbop__hzyu = 1
    else:
        gbop__hzyu = len(agg_node.pivot_values)
    tpz__jahud = tuple('key_' + sanitize_varname(drj__cluxw) for drj__cluxw in
        agg_node.key_names)
    sljgq__vqgp = {drj__cluxw: 'in_{}'.format(sanitize_varname(drj__cluxw)) for
        drj__cluxw in agg_node.gb_info_in.keys() if drj__cluxw is not None}
    jnmfb__iwjg = {drj__cluxw: ('out_' + sanitize_varname(drj__cluxw)) for
        drj__cluxw in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    ulb__hbj = ', '.join(tpz__jahud)
    mnax__eufrd = ', '.join(sljgq__vqgp.values())
    if mnax__eufrd != '':
        mnax__eufrd = ', ' + mnax__eufrd
    ayvcj__ewp = 'def agg_top({}{}{}, pivot_arr):\n'.format(ulb__hbj,
        mnax__eufrd, ', index_arg' if agg_node.input_has_index else '')
    for a in (tpz__jahud + tuple(sljgq__vqgp.values())):
        ayvcj__ewp += f'    {a} = decode_if_dict_array({a})\n'
    if tnkd__bcli:
        ayvcj__ewp += f'    pivot_arr = decode_if_dict_array(pivot_arr)\n'
        vfkuw__bmdz = []
        for yajw__piiw, ioq__xpi in agg_node.gb_info_in.items():
            if yajw__piiw is not None:
                for func, tpx__rcr in ioq__xpi:
                    vfkuw__bmdz.append(sljgq__vqgp[yajw__piiw])
    else:
        vfkuw__bmdz = tuple(sljgq__vqgp[yajw__piiw] for yajw__piiw,
            tpx__rcr in agg_node.gb_info_out.values() if yajw__piiw is not None
            )
    oodqm__oef = tpz__jahud + tuple(vfkuw__bmdz)
    ayvcj__ewp += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in oodqm__oef), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    ayvcj__ewp += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    wpsj__qmcvq = []
    func_idx_to_in_col = []
    agn__noy = []
    oztrs__liu = False
    jap__irnu = 1
    irs__hpip = -1
    rlcf__wrhp = 0
    whwt__thjd = 0
    if not tnkd__bcli:
        dnj__skxv = [func for tpx__rcr, func in agg_node.gb_info_out.values()]
    else:
        dnj__skxv = [func for func, tpx__rcr in ioq__xpi for ioq__xpi in
            agg_node.gb_info_in.values()]
    for wrpa__lsz, func in enumerate(dnj__skxv):
        wpsj__qmcvq.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            rlcf__wrhp += 1
        if hasattr(func, 'skipdropna'):
            oztrs__liu = func.skipdropna
        if func.ftype == 'shift':
            jap__irnu = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            whwt__thjd = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            irs__hpip = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(wrpa__lsz)
        if func.ftype == 'udf':
            agn__noy.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            agn__noy.append(0)
            do_combine = False
    wpsj__qmcvq.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == gbop__hzyu, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * gbop__hzyu, 'invalid number of groupby outputs'
    if rlcf__wrhp > 0:
        if rlcf__wrhp != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    for ocob__gnw, drj__cluxw in enumerate(agg_node.gb_info_out.keys()):
        cyvql__nghue = jnmfb__iwjg[drj__cluxw] + '_dummy'
        ktndr__efng = out_col_typs[ocob__gnw]
        yajw__piiw, func = agg_node.gb_info_out[drj__cluxw]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(ktndr__efng, bodo.
            CategoricalArrayType):
            ayvcj__ewp += '    {} = {}\n'.format(cyvql__nghue, sljgq__vqgp[
                yajw__piiw])
        elif udf_func_struct is not None:
            ayvcj__ewp += '    {} = {}\n'.format(cyvql__nghue,
                _gen_dummy_alloc(ktndr__efng, ocob__gnw, False))
    if udf_func_struct is not None:
        rdh__gsyh = next_label()
        if udf_func_struct.regular_udfs:
            qwor__snqv = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            itf__uvwrz = numba.cfunc(qwor__snqv, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, rdh__gsyh))
            bvv__acqc = numba.cfunc(qwor__snqv, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, rdh__gsyh))
            byeyj__jqerz = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_col_typs,
                rdh__gsyh))
            udf_func_struct.set_regular_cfuncs(itf__uvwrz, bvv__acqc,
                byeyj__jqerz)
            for vok__fiaka in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[vok__fiaka.native_name] = vok__fiaka
                gb_agg_cfunc_addr[vok__fiaka.native_name] = vok__fiaka.address
        if udf_func_struct.general_udfs:
            xrmwr__hhbu = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col,
                rdh__gsyh)
            udf_func_struct.set_general_cfunc(xrmwr__hhbu)
        yxxq__edmt = []
        olbi__euex = 0
        ocob__gnw = 0
        for cyvql__nghue, vxwt__bmgl in zip(jnmfb__iwjg.values(), allfuncs):
            if vxwt__bmgl.ftype in ('udf', 'gen_udf'):
                yxxq__edmt.append(cyvql__nghue + '_dummy')
                for rrtd__vsk in range(olbi__euex, olbi__euex + agn__noy[
                    ocob__gnw]):
                    yxxq__edmt.append('data_redvar_dummy_' + str(rrtd__vsk))
                olbi__euex += agn__noy[ocob__gnw]
                ocob__gnw += 1
        if udf_func_struct.regular_udfs:
            cae__yxt = udf_func_struct.var_typs
            for ocob__gnw, t in enumerate(cae__yxt):
                ayvcj__ewp += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(ocob__gnw, _get_np_dtype(t)))
        ayvcj__ewp += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in yxxq__edmt))
        ayvcj__ewp += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            ayvcj__ewp += ("    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".
                format(itf__uvwrz.native_name))
            ayvcj__ewp += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(bvv__acqc.native_name))
            ayvcj__ewp += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                byeyj__jqerz.native_name)
            ayvcj__ewp += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(itf__uvwrz.native_name))
            ayvcj__ewp += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(bvv__acqc.native_name))
            ayvcj__ewp += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(byeyj__jqerz.native_name))
        else:
            ayvcj__ewp += '    cpp_cb_update_addr = 0\n'
            ayvcj__ewp += '    cpp_cb_combine_addr = 0\n'
            ayvcj__ewp += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            vok__fiaka = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[vok__fiaka.native_name] = vok__fiaka
            gb_agg_cfunc_addr[vok__fiaka.native_name] = vok__fiaka.address
            ayvcj__ewp += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(vok__fiaka.native_name))
            ayvcj__ewp += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(vok__fiaka.native_name))
        else:
            ayvcj__ewp += '    cpp_cb_general_addr = 0\n'
    else:
        ayvcj__ewp += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        ayvcj__ewp += '    cpp_cb_update_addr = 0\n'
        ayvcj__ewp += '    cpp_cb_combine_addr = 0\n'
        ayvcj__ewp += '    cpp_cb_eval_addr = 0\n'
        ayvcj__ewp += '    cpp_cb_general_addr = 0\n'
    ayvcj__ewp += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(vxwt__bmgl.ftype)) for
        vxwt__bmgl in allfuncs] + ['0']))
    ayvcj__ewp += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(
        str(wpsj__qmcvq))
    if len(agn__noy) > 0:
        ayvcj__ewp += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(agn__noy))
    else:
        ayvcj__ewp += '    udf_ncols = np.array([0], np.int32)\n'
    if tnkd__bcli:
        ayvcj__ewp += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        ayvcj__ewp += '    arr_info = array_to_info(arr_type)\n'
        ayvcj__ewp += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        ayvcj__ewp += '    pivot_info = array_to_info(pivot_arr)\n'
        ayvcj__ewp += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        ayvcj__ewp += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, oztrs__liu, agg_node.return_key, agg_node.same_index))
        ayvcj__ewp += '    delete_info_decref_array(pivot_info)\n'
        ayvcj__ewp += '    delete_info_decref_array(arr_info)\n'
    else:
        ayvcj__ewp += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, oztrs__liu,
            jap__irnu, whwt__thjd, irs__hpip, agg_node.return_key, agg_node
            .same_index, agg_node.dropna))
    jrf__hivg = 0
    if agg_node.return_key:
        for ocob__gnw, blhml__toq in enumerate(tpz__jahud):
            ayvcj__ewp += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(blhml__toq, jrf__hivg, blhml__toq))
            jrf__hivg += 1
    for ocob__gnw, cyvql__nghue in enumerate(jnmfb__iwjg.values()):
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(ktndr__efng, bodo.
            CategoricalArrayType):
            ayvcj__ewp += f"""    {cyvql__nghue} = info_to_array(info_from_table(out_table, {jrf__hivg}), {cyvql__nghue + '_dummy'})
"""
        else:
            ayvcj__ewp += f"""    {cyvql__nghue} = info_to_array(info_from_table(out_table, {jrf__hivg}), out_typs[{ocob__gnw}])
"""
        jrf__hivg += 1
    if agg_node.same_index:
        ayvcj__ewp += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(jrf__hivg))
        jrf__hivg += 1
    ayvcj__ewp += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    ayvcj__ewp += '    delete_table_decref_arrays(table)\n'
    ayvcj__ewp += '    delete_table_decref_arrays(udf_table_dummy)\n'
    ayvcj__ewp += '    delete_table(out_table)\n'
    ayvcj__ewp += f'    ev_clean.finalize()\n'
    bcwjm__jlos = tuple(jnmfb__iwjg.values())
    if agg_node.return_key:
        bcwjm__jlos += tuple(tpz__jahud)
    ayvcj__ewp += '    return ({},{})\n'.format(', '.join(bcwjm__jlos), 
        ' out_index_arg,' if agg_node.same_index else '')
    oxs__ilyv = {}
    exec(ayvcj__ewp, {'out_typs': out_col_typs}, oxs__ilyv)
    lnud__ahsfn = oxs__ilyv['agg_top']
    return lnud__ahsfn


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for ouieg__pafb in block.body:
            if is_call_assign(ouieg__pafb) and find_callname(f_ir,
                ouieg__pafb.value) == ('len', 'builtins'
                ) and ouieg__pafb.value.args[0].name == f_ir.arg_names[0]:
                wihi__yxx = get_definition(f_ir, ouieg__pafb.value.func)
                wihi__yxx.name = 'dummy_agg_count'
                wihi__yxx.value = dummy_agg_count
    tyqf__xxvr = get_name_var_table(f_ir.blocks)
    byyzt__gzlgq = {}
    for name, tpx__rcr in tyqf__xxvr.items():
        byyzt__gzlgq[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, byyzt__gzlgq)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    adnqa__eyw = numba.core.compiler.Flags()
    adnqa__eyw.nrt = True
    yfrzy__ztfu = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, adnqa__eyw)
    yfrzy__ztfu.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, tsop__sepsf, calltypes, tpx__rcr = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    gwmya__hql = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    oti__izud = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    vpua__pgwpq = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    cvnrp__wkw = vpua__pgwpq(typemap, calltypes)
    pm = oti__izud(typingctx, targetctx, None, f_ir, typemap, tsop__sepsf,
        calltypes, cvnrp__wkw, {}, adnqa__eyw, None)
    nwbzu__jcnp = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = oti__izud(typingctx, targetctx, None, f_ir, typemap, tsop__sepsf,
        calltypes, cvnrp__wkw, {}, adnqa__eyw, nwbzu__jcnp)
    jyj__gyh = numba.core.typed_passes.InlineOverloads()
    jyj__gyh.run_pass(pm)
    rscyj__rzdu = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    rscyj__rzdu.run()
    for block in f_ir.blocks.values():
        for ouieg__pafb in block.body:
            if is_assign(ouieg__pafb) and isinstance(ouieg__pafb.value, (ir
                .Arg, ir.Var)) and isinstance(typemap[ouieg__pafb.target.
                name], SeriesType):
                ynyz__klp = typemap.pop(ouieg__pafb.target.name)
                typemap[ouieg__pafb.target.name] = ynyz__klp.data
            if is_call_assign(ouieg__pafb) and find_callname(f_ir,
                ouieg__pafb.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[ouieg__pafb.target.name].remove(ouieg__pafb
                    .value)
                ouieg__pafb.value = ouieg__pafb.value.args[0]
                f_ir._definitions[ouieg__pafb.target.name].append(ouieg__pafb
                    .value)
            if is_call_assign(ouieg__pafb) and find_callname(f_ir,
                ouieg__pafb.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[ouieg__pafb.target.name].remove(ouieg__pafb
                    .value)
                ouieg__pafb.value = ir.Const(False, ouieg__pafb.loc)
                f_ir._definitions[ouieg__pafb.target.name].append(ouieg__pafb
                    .value)
            if is_call_assign(ouieg__pafb) and find_callname(f_ir,
                ouieg__pafb.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[ouieg__pafb.target.name].remove(ouieg__pafb
                    .value)
                ouieg__pafb.value = ir.Const(False, ouieg__pafb.loc)
                f_ir._definitions[ouieg__pafb.target.name].append(ouieg__pafb
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    zcfmv__cda = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, gwmya__hql)
    zcfmv__cda.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    rbcon__ezih = numba.core.compiler.StateDict()
    rbcon__ezih.func_ir = f_ir
    rbcon__ezih.typemap = typemap
    rbcon__ezih.calltypes = calltypes
    rbcon__ezih.typingctx = typingctx
    rbcon__ezih.targetctx = targetctx
    rbcon__ezih.return_type = tsop__sepsf
    numba.core.rewrites.rewrite_registry.apply('after-inference', rbcon__ezih)
    nnrrp__qqsp = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        tsop__sepsf, typingctx, targetctx, gwmya__hql, adnqa__eyw, {})
    nnrrp__qqsp.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            ehupu__zpqz = ctypes.pythonapi.PyCell_Get
            ehupu__zpqz.restype = ctypes.py_object
            ehupu__zpqz.argtypes = ctypes.py_object,
            ucrzx__jwlkm = tuple(ehupu__zpqz(vkw__ycbj) for vkw__ycbj in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            ucrzx__jwlkm = closure.items
        assert len(code.co_freevars) == len(ucrzx__jwlkm)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks,
            ucrzx__jwlkm)


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
        ymi__fsh = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (ymi__fsh,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        lhw__moj, arr_var = _rm_arg_agg_block(block, pm.typemap)
        kldv__cbtag = -1
        for ocob__gnw, ouieg__pafb in enumerate(lhw__moj):
            if isinstance(ouieg__pafb, numba.parfors.parfor.Parfor):
                assert kldv__cbtag == -1, 'only one parfor for aggregation function'
                kldv__cbtag = ocob__gnw
        parfor = None
        if kldv__cbtag != -1:
            parfor = lhw__moj[kldv__cbtag]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = lhw__moj[:kldv__cbtag] + parfor.init_block.body
        eval_nodes = lhw__moj[kldv__cbtag + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for ouieg__pafb in init_nodes:
            if is_assign(ouieg__pafb) and ouieg__pafb.target.name in redvars:
                ind = redvars.index(ouieg__pafb.target.name)
                reduce_vars[ind] = ouieg__pafb.target
        var_types = [pm.typemap[jfg__xmtd] for jfg__xmtd in redvars]
        apc__hwqhk = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        vvbj__dur = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        yatl__rnqqe = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(yatl__rnqqe)
        self.all_update_funcs.append(vvbj__dur)
        self.all_combine_funcs.append(apc__hwqhk)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        hjmuh__dauo = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        dpzq__yueso = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        uoxko__nyuw = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        lkbdb__fdgnz = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, hjmuh__dauo, dpzq__yueso, uoxko__nyuw,
            lkbdb__fdgnz)


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
    uvj__tzffd = []
    for t, vxwt__bmgl in zip(in_col_types, agg_func):
        uvj__tzffd.append((t, vxwt__bmgl))
    nflu__expm = RegularUDFGenerator(in_col_types, out_col_types, pivot_typ,
        pivot_values, is_crosstab, typingctx, targetctx)
    hdgd__lyx = GeneralUDFGenerator()
    for in_col_typ, func in uvj__tzffd:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            nflu__expm.add_udf(in_col_typ, func)
        except:
            hdgd__lyx.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = nflu__expm.gen_all_func()
    general_udf_funcs = hdgd__lyx.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    yol__ojf = compute_use_defs(parfor.loop_body)
    vjkji__htuiy = set()
    for itz__kqlqw in yol__ojf.usemap.values():
        vjkji__htuiy |= itz__kqlqw
    nge__jsagp = set()
    for itz__kqlqw in yol__ojf.defmap.values():
        nge__jsagp |= itz__kqlqw
    ekxnm__dxq = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    ekxnm__dxq.body = eval_nodes
    gxla__qtnoy = compute_use_defs({(0): ekxnm__dxq})
    lbqwl__inqwj = gxla__qtnoy.usemap[0]
    pusj__hxbm = set()
    nwa__mvmb = []
    htd__ifwbc = []
    for ouieg__pafb in reversed(init_nodes):
        qypmh__qaap = {jfg__xmtd.name for jfg__xmtd in ouieg__pafb.list_vars()}
        if is_assign(ouieg__pafb):
            jfg__xmtd = ouieg__pafb.target.name
            qypmh__qaap.remove(jfg__xmtd)
            if (jfg__xmtd in vjkji__htuiy and jfg__xmtd not in pusj__hxbm and
                jfg__xmtd not in lbqwl__inqwj and jfg__xmtd not in nge__jsagp):
                htd__ifwbc.append(ouieg__pafb)
                vjkji__htuiy |= qypmh__qaap
                nge__jsagp.add(jfg__xmtd)
                continue
        pusj__hxbm |= qypmh__qaap
        nwa__mvmb.append(ouieg__pafb)
    htd__ifwbc.reverse()
    nwa__mvmb.reverse()
    usk__uhc = min(parfor.loop_body.keys())
    baxsf__ajqp = parfor.loop_body[usk__uhc]
    baxsf__ajqp.body = htd__ifwbc + baxsf__ajqp.body
    return nwa__mvmb


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    crlkv__mdxg = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    ada__pvn = set()
    duiyb__jukzt = []
    for ouieg__pafb in init_nodes:
        if is_assign(ouieg__pafb) and isinstance(ouieg__pafb.value, ir.Global
            ) and isinstance(ouieg__pafb.value.value, pytypes.FunctionType
            ) and ouieg__pafb.value.value in crlkv__mdxg:
            ada__pvn.add(ouieg__pafb.target.name)
        elif is_call_assign(ouieg__pafb
            ) and ouieg__pafb.value.func.name in ada__pvn:
            pass
        else:
            duiyb__jukzt.append(ouieg__pafb)
    init_nodes = duiyb__jukzt
    xavqa__hemk = types.Tuple(var_types)
    fsqzo__jjjp = lambda : None
    f_ir = compile_to_numba_ir(fsqzo__jjjp, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    kjqzv__hxnjp = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    zdk__cprs = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        kjqzv__hxnjp, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [zdk__cprs] + block.body
    block.body[-2].value.value = kjqzv__hxnjp
    xgo__whdic = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        xavqa__hemk, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xglbg__acve = numba.core.target_extension.dispatcher_registry[cpu_target](
        fsqzo__jjjp)
    xglbg__acve.add_overload(xgo__whdic)
    return xglbg__acve


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    nzgp__jfw = len(update_funcs)
    omvlr__pzena = len(in_col_types)
    if pivot_values is not None:
        assert omvlr__pzena == 1
    ayvcj__ewp = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        ncsw__ztc = redvar_offsets[omvlr__pzena]
        ayvcj__ewp += '  pv = pivot_arr[i]\n'
        for rrtd__vsk, leuf__lqrhw in enumerate(pivot_values):
            pws__nkeq = 'el' if rrtd__vsk != 0 else ''
            ayvcj__ewp += "  {}if pv == '{}':\n".format(pws__nkeq, leuf__lqrhw)
            tebm__pvf = ncsw__ztc * rrtd__vsk
            vyll__hdmk = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                ocob__gnw) for ocob__gnw in range(tebm__pvf +
                redvar_offsets[0], tebm__pvf + redvar_offsets[1])])
            ggvw__uoib = 'data_in[0][i]'
            if is_crosstab:
                ggvw__uoib = '0'
            ayvcj__ewp += '    {} = update_vars_0({}, {})\n'.format(vyll__hdmk,
                vyll__hdmk, ggvw__uoib)
    else:
        for rrtd__vsk in range(nzgp__jfw):
            vyll__hdmk = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                ocob__gnw) for ocob__gnw in range(redvar_offsets[rrtd__vsk],
                redvar_offsets[rrtd__vsk + 1])])
            if vyll__hdmk:
                ayvcj__ewp += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(vyll__hdmk, rrtd__vsk, vyll__hdmk, 0 if 
                    omvlr__pzena == 1 else rrtd__vsk))
    ayvcj__ewp += '  return\n'
    cnysp__qpst = {}
    for ocob__gnw, vxwt__bmgl in enumerate(update_funcs):
        cnysp__qpst['update_vars_{}'.format(ocob__gnw)] = vxwt__bmgl
    oxs__ilyv = {}
    exec(ayvcj__ewp, cnysp__qpst, oxs__ilyv)
    slj__cruw = oxs__ilyv['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(slj__cruw)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    busob__nsm = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    arg_typs = busob__nsm, busob__nsm, types.intp, types.intp, pivot_typ
    kqoc__dmkla = len(redvar_offsets) - 1
    ncsw__ztc = redvar_offsets[kqoc__dmkla]
    ayvcj__ewp = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert kqoc__dmkla == 1
        for biss__cqr in range(len(pivot_values)):
            tebm__pvf = ncsw__ztc * biss__cqr
            vyll__hdmk = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                ocob__gnw) for ocob__gnw in range(tebm__pvf +
                redvar_offsets[0], tebm__pvf + redvar_offsets[1])])
            xat__ddx = ', '.join(['recv_arrs[{}][i]'.format(ocob__gnw) for
                ocob__gnw in range(tebm__pvf + redvar_offsets[0], tebm__pvf +
                redvar_offsets[1])])
            ayvcj__ewp += '  {} = combine_vars_0({}, {})\n'.format(vyll__hdmk,
                vyll__hdmk, xat__ddx)
    else:
        for rrtd__vsk in range(kqoc__dmkla):
            vyll__hdmk = ', '.join(['redvar_arrs[{}][w_ind]'.format(
                ocob__gnw) for ocob__gnw in range(redvar_offsets[rrtd__vsk],
                redvar_offsets[rrtd__vsk + 1])])
            xat__ddx = ', '.join(['recv_arrs[{}][i]'.format(ocob__gnw) for
                ocob__gnw in range(redvar_offsets[rrtd__vsk],
                redvar_offsets[rrtd__vsk + 1])])
            if xat__ddx:
                ayvcj__ewp += '  {} = combine_vars_{}({}, {})\n'.format(
                    vyll__hdmk, rrtd__vsk, vyll__hdmk, xat__ddx)
    ayvcj__ewp += '  return\n'
    cnysp__qpst = {}
    for ocob__gnw, vxwt__bmgl in enumerate(combine_funcs):
        cnysp__qpst['combine_vars_{}'.format(ocob__gnw)] = vxwt__bmgl
    oxs__ilyv = {}
    exec(ayvcj__ewp, cnysp__qpst, oxs__ilyv)
    zrs__rigyp = oxs__ilyv['combine_all_f']
    f_ir = compile_to_numba_ir(zrs__rigyp, cnysp__qpst)
    uoxko__nyuw = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xglbg__acve = numba.core.target_extension.dispatcher_registry[cpu_target](
        zrs__rigyp)
    xglbg__acve.add_overload(uoxko__nyuw)
    return xglbg__acve


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    busob__nsm = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    out_col_typs = types.Tuple(out_col_typs)
    kqoc__dmkla = len(redvar_offsets) - 1
    ncsw__ztc = redvar_offsets[kqoc__dmkla]
    ayvcj__ewp = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert kqoc__dmkla == 1
        for rrtd__vsk in range(len(pivot_values)):
            tebm__pvf = ncsw__ztc * rrtd__vsk
            vyll__hdmk = ', '.join(['redvar_arrs[{}][j]'.format(ocob__gnw) for
                ocob__gnw in range(tebm__pvf + redvar_offsets[0], tebm__pvf +
                redvar_offsets[1])])
            ayvcj__ewp += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                rrtd__vsk, vyll__hdmk)
    else:
        for rrtd__vsk in range(kqoc__dmkla):
            vyll__hdmk = ', '.join(['redvar_arrs[{}][j]'.format(ocob__gnw) for
                ocob__gnw in range(redvar_offsets[rrtd__vsk],
                redvar_offsets[rrtd__vsk + 1])])
            ayvcj__ewp += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                rrtd__vsk, rrtd__vsk, vyll__hdmk)
    ayvcj__ewp += '  return\n'
    cnysp__qpst = {}
    for ocob__gnw, vxwt__bmgl in enumerate(eval_funcs):
        cnysp__qpst['eval_vars_{}'.format(ocob__gnw)] = vxwt__bmgl
    oxs__ilyv = {}
    exec(ayvcj__ewp, cnysp__qpst, oxs__ilyv)
    rajju__kpoi = oxs__ilyv['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(rajju__kpoi)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    ifyqf__jewv = len(var_types)
    tuijk__soo = [f'in{ocob__gnw}' for ocob__gnw in range(ifyqf__jewv)]
    xavqa__hemk = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    urkyn__jqaog = xavqa__hemk(0)
    ayvcj__ewp = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        tuijk__soo))
    oxs__ilyv = {}
    exec(ayvcj__ewp, {'_zero': urkyn__jqaog}, oxs__ilyv)
    yax__nxlx = oxs__ilyv['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(yax__nxlx, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': urkyn__jqaog}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    fkwyj__flaw = []
    for ocob__gnw, jfg__xmtd in enumerate(reduce_vars):
        fkwyj__flaw.append(ir.Assign(block.body[ocob__gnw].target,
            jfg__xmtd, jfg__xmtd.loc))
        for xym__doc in jfg__xmtd.versioned_names:
            fkwyj__flaw.append(ir.Assign(jfg__xmtd, ir.Var(jfg__xmtd.scope,
                xym__doc, jfg__xmtd.loc), jfg__xmtd.loc))
    block.body = block.body[:ifyqf__jewv] + fkwyj__flaw + eval_nodes
    yatl__rnqqe = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        xavqa__hemk, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xglbg__acve = numba.core.target_extension.dispatcher_registry[cpu_target](
        yax__nxlx)
    xglbg__acve.add_overload(yatl__rnqqe)
    return xglbg__acve


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    ifyqf__jewv = len(redvars)
    linb__vfdb = [f'v{ocob__gnw}' for ocob__gnw in range(ifyqf__jewv)]
    tuijk__soo = [f'in{ocob__gnw}' for ocob__gnw in range(ifyqf__jewv)]
    ayvcj__ewp = 'def agg_combine({}):\n'.format(', '.join(linb__vfdb +
        tuijk__soo))
    hhv__jql = wrap_parfor_blocks(parfor)
    mov__lcxr = find_topo_order(hhv__jql)
    mov__lcxr = mov__lcxr[1:]
    unwrap_parfor_blocks(parfor)
    oyhx__jbsx = {}
    mcm__swijr = []
    for zkg__jmes in mov__lcxr:
        kegas__gewq = parfor.loop_body[zkg__jmes]
        for ouieg__pafb in kegas__gewq.body:
            if is_call_assign(ouieg__pafb) and guard(find_callname, f_ir,
                ouieg__pafb.value) == ('__special_combine', 'bodo.ir.aggregate'
                ):
                args = ouieg__pafb.value.args
                ldyv__wtvtq = []
                vno__xnnlh = []
                for jfg__xmtd in args[:-1]:
                    ind = redvars.index(jfg__xmtd.name)
                    mcm__swijr.append(ind)
                    ldyv__wtvtq.append('v{}'.format(ind))
                    vno__xnnlh.append('in{}'.format(ind))
                iav__szcw = '__special_combine__{}'.format(len(oyhx__jbsx))
                ayvcj__ewp += '    ({},) = {}({})\n'.format(', '.join(
                    ldyv__wtvtq), iav__szcw, ', '.join(ldyv__wtvtq +
                    vno__xnnlh))
                halb__uev = ir.Expr.call(args[-1], [], (), kegas__gewq.loc)
                rnup__qrn = guard(find_callname, f_ir, halb__uev)
                assert rnup__qrn == ('_var_combine', 'bodo.ir.aggregate')
                rnup__qrn = bodo.ir.aggregate._var_combine
                oyhx__jbsx[iav__szcw] = rnup__qrn
            if is_assign(ouieg__pafb) and ouieg__pafb.target.name in redvars:
                wttuo__xeyp = ouieg__pafb.target.name
                ind = redvars.index(wttuo__xeyp)
                if ind in mcm__swijr:
                    continue
                if len(f_ir._definitions[wttuo__xeyp]) == 2:
                    var_def = f_ir._definitions[wttuo__xeyp][0]
                    ayvcj__ewp += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[wttuo__xeyp][1]
                    ayvcj__ewp += _match_reduce_def(var_def, f_ir, ind)
    ayvcj__ewp += '    return {}'.format(', '.join(['v{}'.format(ocob__gnw) for
        ocob__gnw in range(ifyqf__jewv)]))
    oxs__ilyv = {}
    exec(ayvcj__ewp, {}, oxs__ilyv)
    ryve__tie = oxs__ilyv['agg_combine']
    arg_typs = tuple(2 * var_types)
    cnysp__qpst = {'numba': numba, 'bodo': bodo, 'np': np}
    cnysp__qpst.update(oyhx__jbsx)
    f_ir = compile_to_numba_ir(ryve__tie, cnysp__qpst, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    xavqa__hemk = pm.typemap[block.body[-1].value.name]
    apc__hwqhk = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        xavqa__hemk, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xglbg__acve = numba.core.target_extension.dispatcher_registry[cpu_target](
        ryve__tie)
    xglbg__acve.add_overload(apc__hwqhk)
    return xglbg__acve


def _match_reduce_def(var_def, f_ir, ind):
    ayvcj__ewp = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        ayvcj__ewp = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        rzey__epzw = guard(find_callname, f_ir, var_def)
        if rzey__epzw == ('min', 'builtins'):
            ayvcj__ewp = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if rzey__epzw == ('max', 'builtins'):
            ayvcj__ewp = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return ayvcj__ewp


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    ifyqf__jewv = len(redvars)
    tckjz__jsse = 1
    dfc__redp = []
    for ocob__gnw in range(tckjz__jsse):
        ufh__ikvfp = ir.Var(arr_var.scope, f'$input{ocob__gnw}', arr_var.loc)
        dfc__redp.append(ufh__ikvfp)
    luaqk__njuj = parfor.loop_nests[0].index_variable
    ghaft__dqpie = [0] * ifyqf__jewv
    for kegas__gewq in parfor.loop_body.values():
        fficu__kyrz = []
        for ouieg__pafb in kegas__gewq.body:
            if is_var_assign(ouieg__pafb
                ) and ouieg__pafb.value.name == luaqk__njuj.name:
                continue
            if is_getitem(ouieg__pafb
                ) and ouieg__pafb.value.value.name == arr_var.name:
                ouieg__pafb.value = dfc__redp[0]
            if is_call_assign(ouieg__pafb) and guard(find_callname, pm.
                func_ir, ouieg__pafb.value) == ('isna',
                'bodo.libs.array_kernels') and ouieg__pafb.value.args[0
                ].name == arr_var.name:
                ouieg__pafb.value = ir.Const(False, ouieg__pafb.target.loc)
            if is_assign(ouieg__pafb) and ouieg__pafb.target.name in redvars:
                ind = redvars.index(ouieg__pafb.target.name)
                ghaft__dqpie[ind] = ouieg__pafb.target
            fficu__kyrz.append(ouieg__pafb)
        kegas__gewq.body = fficu__kyrz
    linb__vfdb = ['v{}'.format(ocob__gnw) for ocob__gnw in range(ifyqf__jewv)]
    tuijk__soo = ['in{}'.format(ocob__gnw) for ocob__gnw in range(tckjz__jsse)]
    ayvcj__ewp = 'def agg_update({}):\n'.format(', '.join(linb__vfdb +
        tuijk__soo))
    ayvcj__ewp += '    __update_redvars()\n'
    ayvcj__ewp += '    return {}'.format(', '.join(['v{}'.format(ocob__gnw) for
        ocob__gnw in range(ifyqf__jewv)]))
    oxs__ilyv = {}
    exec(ayvcj__ewp, {}, oxs__ilyv)
    ufj__smgic = oxs__ilyv['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * tckjz__jsse)
    f_ir = compile_to_numba_ir(ufj__smgic, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    bshy__abbjg = f_ir.blocks.popitem()[1].body
    xavqa__hemk = pm.typemap[bshy__abbjg[-1].value.name]
    hhv__jql = wrap_parfor_blocks(parfor)
    mov__lcxr = find_topo_order(hhv__jql)
    mov__lcxr = mov__lcxr[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    baxsf__ajqp = f_ir.blocks[mov__lcxr[0]]
    atuwu__kjbc = f_ir.blocks[mov__lcxr[-1]]
    qoxyq__nkmas = bshy__abbjg[:ifyqf__jewv + tckjz__jsse]
    if ifyqf__jewv > 1:
        cka__zul = bshy__abbjg[-3:]
        assert is_assign(cka__zul[0]) and isinstance(cka__zul[0].value, ir.Expr
            ) and cka__zul[0].value.op == 'build_tuple'
    else:
        cka__zul = bshy__abbjg[-2:]
    for ocob__gnw in range(ifyqf__jewv):
        hmmet__djn = bshy__abbjg[ocob__gnw].target
        gtv__ulzd = ir.Assign(hmmet__djn, ghaft__dqpie[ocob__gnw],
            hmmet__djn.loc)
        qoxyq__nkmas.append(gtv__ulzd)
    for ocob__gnw in range(ifyqf__jewv, ifyqf__jewv + tckjz__jsse):
        hmmet__djn = bshy__abbjg[ocob__gnw].target
        gtv__ulzd = ir.Assign(hmmet__djn, dfc__redp[ocob__gnw - ifyqf__jewv
            ], hmmet__djn.loc)
        qoxyq__nkmas.append(gtv__ulzd)
    baxsf__ajqp.body = qoxyq__nkmas + baxsf__ajqp.body
    vziab__mtci = []
    for ocob__gnw in range(ifyqf__jewv):
        hmmet__djn = bshy__abbjg[ocob__gnw].target
        gtv__ulzd = ir.Assign(ghaft__dqpie[ocob__gnw], hmmet__djn,
            hmmet__djn.loc)
        vziab__mtci.append(gtv__ulzd)
    atuwu__kjbc.body += vziab__mtci + cka__zul
    jlq__wtz = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        xavqa__hemk, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xglbg__acve = numba.core.target_extension.dispatcher_registry[cpu_target](
        ufj__smgic)
    xglbg__acve.add_overload(jlq__wtz)
    return xglbg__acve


def _rm_arg_agg_block(block, typemap):
    lhw__moj = []
    arr_var = None
    for ocob__gnw, ouieg__pafb in enumerate(block.body):
        if is_assign(ouieg__pafb) and isinstance(ouieg__pafb.value, ir.Arg):
            arr_var = ouieg__pafb.target
            yrzgc__sir = typemap[arr_var.name]
            if not isinstance(yrzgc__sir, types.ArrayCompatible):
                lhw__moj += block.body[ocob__gnw + 1:]
                break
            qkr__mjq = block.body[ocob__gnw + 1]
            assert is_assign(qkr__mjq) and isinstance(qkr__mjq.value, ir.Expr
                ) and qkr__mjq.value.op == 'getattr' and qkr__mjq.value.attr == 'shape' and qkr__mjq.value.value.name == arr_var.name
            yix__kedbz = qkr__mjq.target
            spbtu__nve = block.body[ocob__gnw + 2]
            assert is_assign(spbtu__nve) and isinstance(spbtu__nve.value,
                ir.Expr
                ) and spbtu__nve.value.op == 'static_getitem' and spbtu__nve.value.value.name == yix__kedbz.name
            lhw__moj += block.body[ocob__gnw + 3:]
            break
        lhw__moj.append(ouieg__pafb)
    return lhw__moj, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    hhv__jql = wrap_parfor_blocks(parfor)
    mov__lcxr = find_topo_order(hhv__jql)
    mov__lcxr = mov__lcxr[1:]
    unwrap_parfor_blocks(parfor)
    for zkg__jmes in reversed(mov__lcxr):
        for ouieg__pafb in reversed(parfor.loop_body[zkg__jmes].body):
            if isinstance(ouieg__pafb, ir.Assign) and (ouieg__pafb.target.
                name in parfor_params or ouieg__pafb.target.name in
                var_to_param):
                yqdj__abg = ouieg__pafb.target.name
                rhs = ouieg__pafb.value
                gjsgj__bbr = (yqdj__abg if yqdj__abg in parfor_params else
                    var_to_param[yqdj__abg])
                gitih__vwguo = []
                if isinstance(rhs, ir.Var):
                    gitih__vwguo = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    gitih__vwguo = [jfg__xmtd.name for jfg__xmtd in
                        ouieg__pafb.value.list_vars()]
                param_uses[gjsgj__bbr].extend(gitih__vwguo)
                for jfg__xmtd in gitih__vwguo:
                    var_to_param[jfg__xmtd] = gjsgj__bbr
            if isinstance(ouieg__pafb, Parfor):
                get_parfor_reductions(ouieg__pafb, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for isut__clu, gitih__vwguo in param_uses.items():
        if isut__clu in gitih__vwguo and isut__clu not in reduce_varnames:
            reduce_varnames.append(isut__clu)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
