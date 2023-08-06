"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import DictionaryArrayType
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, check_unsupported_args, decode_if_dict_array, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_str_arr_type, raise_bodo_error, to_str_arr_if_dict_array
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)
max_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Max.value)
min_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Min.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._indices._null_bitmap, i) or bodo.libs.array_kernels.isna(arr.
            _data, arr._indices[i])
    if isinstance(arr, DatetimeArrayType):
        return lambda arr, i: np.isnat(arr._data[i])
    assert isinstance(arr, types.Array), f'Invalid array type in isna(): {arr}'
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        awgde__afp = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = awgde__afp
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        awgde__afp = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = awgde__afp
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, ind, int_nan_const=0: bodo.libs.array_kernels.setna(
            arr._indices, ind)
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            ztf__rqc = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ztf__rqc[ind + 1] = ztf__rqc[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            ztf__rqc = bodo.libs.array_item_arr_ext.get_offsets(arr)
            ztf__rqc[ind + 1] = ztf__rqc[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    siej__nqnlt = arr_tup.count
    oufgy__kzxm = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(siej__nqnlt):
        oufgy__kzxm += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    oufgy__kzxm += '  return\n'
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'setna': setna}, hkt__gxxtm)
    impl = hkt__gxxtm['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        prd__ztp = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(prd__ztp.start, prd__ztp.stop, prd__ztp.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        sva__qabox = 'n'
        pifxo__zrsl = 'n_pes'
        tbrm__obmu = 'min_op'
    else:
        sva__qabox = 'n-1, -1, -1'
        pifxo__zrsl = '-1'
        tbrm__obmu = 'max_op'
    oufgy__kzxm = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {pifxo__zrsl}
    for i in range({sva__qabox}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {tbrm__obmu}))
        if possible_valid_rank != {pifxo__zrsl}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, hkt__gxxtm)
    impl = hkt__gxxtm['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    fkjav__yvhuy = array_to_info(arr)
    _median_series_computation(res, fkjav__yvhuy, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(fkjav__yvhuy)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    fkjav__yvhuy = array_to_info(arr)
    _autocorr_series_computation(res, fkjav__yvhuy, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(fkjav__yvhuy)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    fkjav__yvhuy = array_to_info(arr)
    _compute_series_monotonicity(res, fkjav__yvhuy, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(fkjav__yvhuy)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    vwkd__mjpp = res[0] > 0.5
    return vwkd__mjpp


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        rjiqj__epm = '-'
        vslr__duyr = 'index_arr[0] > threshhold_date'
        sva__qabox = '1, n+1'
        eula__onbmg = 'index_arr[-i] <= threshhold_date'
        recdb__oss = 'i - 1'
    else:
        rjiqj__epm = '+'
        vslr__duyr = 'index_arr[-1] < threshhold_date'
        sva__qabox = 'n'
        eula__onbmg = 'index_arr[i] >= threshhold_date'
        recdb__oss = 'i'
    oufgy__kzxm = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        oufgy__kzxm += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        oufgy__kzxm += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            oufgy__kzxm += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            oufgy__kzxm += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            oufgy__kzxm += '    else:\n'
            oufgy__kzxm += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            oufgy__kzxm += (
                f'    threshhold_date = initial_date {rjiqj__epm} date_offset\n'
                )
    else:
        oufgy__kzxm += (
            f'  threshhold_date = initial_date {rjiqj__epm} offset\n')
    oufgy__kzxm += '  local_valid = 0\n'
    oufgy__kzxm += f'  n = len(index_arr)\n'
    oufgy__kzxm += f'  if n:\n'
    oufgy__kzxm += f'    if {vslr__duyr}:\n'
    oufgy__kzxm += '      loc_valid = n\n'
    oufgy__kzxm += '    else:\n'
    oufgy__kzxm += f'      for i in range({sva__qabox}):\n'
    oufgy__kzxm += f'        if {eula__onbmg}:\n'
    oufgy__kzxm += f'          loc_valid = {recdb__oss}\n'
    oufgy__kzxm += '          break\n'
    oufgy__kzxm += '  if is_parallel:\n'
    oufgy__kzxm += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    oufgy__kzxm += '    return total_valid\n'
    oufgy__kzxm += '  else:\n'
    oufgy__kzxm += '    return loc_valid\n'
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, hkt__gxxtm)
    return hkt__gxxtm['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    vsn__codd = numba_to_c_type(sig.args[0].dtype)
    ypd__qfwx = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), vsn__codd))
    dqh__plu = args[0]
    fyz__sjb = sig.args[0]
    if isinstance(fyz__sjb, (IntegerArrayType, BooleanArrayType)):
        dqh__plu = cgutils.create_struct_proxy(fyz__sjb)(context, builder,
            dqh__plu).data
        fyz__sjb = types.Array(fyz__sjb.dtype, 1, 'C')
    assert fyz__sjb.ndim == 1
    arr = make_array(fyz__sjb)(context, builder, dqh__plu)
    bqj__azuxx = builder.extract_value(arr.shape, 0)
    bid__djv = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        bqj__azuxx, args[1], builder.load(ypd__qfwx)]
    swkj__bkmp = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    ckdex__mpr = lir.FunctionType(lir.DoubleType(), swkj__bkmp)
    yjr__yotg = cgutils.get_or_insert_function(builder.module, ckdex__mpr,
        name='quantile_sequential')
    wvy__ajv = builder.call(yjr__yotg, bid__djv)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return wvy__ajv


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    vsn__codd = numba_to_c_type(sig.args[0].dtype)
    ypd__qfwx = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), vsn__codd))
    dqh__plu = args[0]
    fyz__sjb = sig.args[0]
    if isinstance(fyz__sjb, (IntegerArrayType, BooleanArrayType)):
        dqh__plu = cgutils.create_struct_proxy(fyz__sjb)(context, builder,
            dqh__plu).data
        fyz__sjb = types.Array(fyz__sjb.dtype, 1, 'C')
    assert fyz__sjb.ndim == 1
    arr = make_array(fyz__sjb)(context, builder, dqh__plu)
    bqj__azuxx = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        abnv__xaw = args[2]
    else:
        abnv__xaw = bqj__azuxx
    bid__djv = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        bqj__azuxx, abnv__xaw, args[1], builder.load(ypd__qfwx)]
    swkj__bkmp = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType
        (64), lir.DoubleType(), lir.IntType(32)]
    ckdex__mpr = lir.FunctionType(lir.DoubleType(), swkj__bkmp)
    yjr__yotg = cgutils.get_or_insert_function(builder.module, ckdex__mpr,
        name='quantile_parallel')
    wvy__ajv = builder.call(yjr__yotg, bid__djv)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return wvy__ajv


def rank(arr, method='average', na_option='keep', ascending=True, pct=False):
    return arr


@overload(rank, no_unliteral=True, inline='always')
def overload_rank(arr, method='average', na_option='keep', ascending=True,
    pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_str(na_option):
        raise_bodo_error(
            "Series.rank(): 'na_option' argument must be a constant string")
    na_option = get_overload_const_str(na_option)
    if not is_overload_constant_bool(ascending):
        raise_bodo_error(
            "Series.rank(): 'ascending' argument must be a constant boolean")
    ascending = get_overload_const_bool(ascending)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    if method == 'first' and not ascending:
        raise BodoError(
            "Series.rank(): method='first' with ascending=False is currently unsupported."
            )
    oufgy__kzxm = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    oufgy__kzxm += '  na_idxs = pd.isna(arr)\n'
    oufgy__kzxm += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    oufgy__kzxm += '  nas = sum(na_idxs)\n'
    if not ascending:
        oufgy__kzxm += '  if nas and nas < (sorter.size - 1):\n'
        oufgy__kzxm += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        oufgy__kzxm += '  else:\n'
        oufgy__kzxm += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        oufgy__kzxm += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    oufgy__kzxm += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    oufgy__kzxm += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        oufgy__kzxm += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        oufgy__kzxm += '    inv,\n'
        oufgy__kzxm += '    new_dtype=np.float64,\n'
        oufgy__kzxm += '    copy=True,\n'
        oufgy__kzxm += '    nan_to_str=False,\n'
        oufgy__kzxm += '    from_series=True,\n'
        oufgy__kzxm += '    ) + 1\n'
    else:
        oufgy__kzxm += '  arr = arr[sorter]\n'
        oufgy__kzxm += '  sorted_nas = np.nonzero(pd.isna(arr))[0]\n'
        oufgy__kzxm += '  eq_arr_na = arr[1:] != arr[:-1]\n'
        oufgy__kzxm += '  eq_arr_na[pd.isna(eq_arr_na)] = False\n'
        oufgy__kzxm += '  eq_arr = eq_arr_na.astype(np.bool_)\n'
        oufgy__kzxm += '  obs = np.concatenate((np.array([True]), eq_arr))\n'
        oufgy__kzxm += '  if sorted_nas.size:\n'
        oufgy__kzxm += (
            '    first_na, rep_nas = sorted_nas[0], sorted_nas[1:]\n')
        oufgy__kzxm += '    obs[first_na] = True\n'
        oufgy__kzxm += '    obs[rep_nas] = False\n'
        oufgy__kzxm += (
            '    if rep_nas.size and (rep_nas[-1] + 1) < obs.size:\n')
        oufgy__kzxm += '      obs[rep_nas[-1] + 1] = True\n'
        oufgy__kzxm += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            oufgy__kzxm += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            oufgy__kzxm += '    dense,\n'
            oufgy__kzxm += '    new_dtype=np.float64,\n'
            oufgy__kzxm += '    copy=True,\n'
            oufgy__kzxm += '    nan_to_str=False,\n'
            oufgy__kzxm += '    from_series=True,\n'
            oufgy__kzxm += '  )\n'
        else:
            oufgy__kzxm += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            oufgy__kzxm += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                oufgy__kzxm += '  ret = count_float[dense]\n'
            elif method == 'min':
                oufgy__kzxm += '  ret = count_float[dense - 1] + 1\n'
            else:
                oufgy__kzxm += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                oufgy__kzxm += '  ret[na_idxs] = -1\n'
            oufgy__kzxm += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            oufgy__kzxm += '  div_val = arr.size - nas\n'
        else:
            oufgy__kzxm += '  div_val = arr.size\n'
        oufgy__kzxm += '  for i in range(len(ret)):\n'
        oufgy__kzxm += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        oufgy__kzxm += '  ret[na_idxs] = np.nan\n'
    oufgy__kzxm += '  return ret\n'
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'np': np, 'pd': pd, 'bodo': bodo}, hkt__gxxtm)
    return hkt__gxxtm['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    mzyc__htj = start
    uyllp__nfbnt = 2 * start + 1
    hfc__jba = 2 * start + 2
    if uyllp__nfbnt < n and not cmp_f(arr[uyllp__nfbnt], arr[mzyc__htj]):
        mzyc__htj = uyllp__nfbnt
    if hfc__jba < n and not cmp_f(arr[hfc__jba], arr[mzyc__htj]):
        mzyc__htj = hfc__jba
    if mzyc__htj != start:
        arr[start], arr[mzyc__htj] = arr[mzyc__htj], arr[start]
        ind_arr[start], ind_arr[mzyc__htj] = ind_arr[mzyc__htj], ind_arr[start]
        min_heapify(arr, ind_arr, n, mzyc__htj, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        hsztt__dvan = np.empty(k, A.dtype)
        cbrsf__algx = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                hsztt__dvan[ind] = A[i]
                cbrsf__algx[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            hsztt__dvan = hsztt__dvan[:ind]
            cbrsf__algx = cbrsf__algx[:ind]
        return hsztt__dvan, cbrsf__algx, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        jscrp__fbkp = np.sort(A)
        ayy__pqbxv = index_arr[np.argsort(A)]
        nvbjb__jbf = pd.Series(jscrp__fbkp).notna().values
        jscrp__fbkp = jscrp__fbkp[nvbjb__jbf]
        ayy__pqbxv = ayy__pqbxv[nvbjb__jbf]
        if is_largest:
            jscrp__fbkp = jscrp__fbkp[::-1]
            ayy__pqbxv = ayy__pqbxv[::-1]
        return np.ascontiguousarray(jscrp__fbkp), np.ascontiguousarray(
            ayy__pqbxv)
    hsztt__dvan, cbrsf__algx, start = select_k_nonan(A, index_arr, m, k)
    cbrsf__algx = cbrsf__algx[hsztt__dvan.argsort()]
    hsztt__dvan.sort()
    if not is_largest:
        hsztt__dvan = np.ascontiguousarray(hsztt__dvan[::-1])
        cbrsf__algx = np.ascontiguousarray(cbrsf__algx[::-1])
    for i in range(start, m):
        if cmp_f(A[i], hsztt__dvan[0]):
            hsztt__dvan[0] = A[i]
            cbrsf__algx[0] = index_arr[i]
            min_heapify(hsztt__dvan, cbrsf__algx, k, 0, cmp_f)
    cbrsf__algx = cbrsf__algx[hsztt__dvan.argsort()]
    hsztt__dvan.sort()
    if is_largest:
        hsztt__dvan = hsztt__dvan[::-1]
        cbrsf__algx = cbrsf__algx[::-1]
    return np.ascontiguousarray(hsztt__dvan), np.ascontiguousarray(cbrsf__algx)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    hirv__pvfc = bodo.libs.distributed_api.get_rank()
    lod__yynkd, vhlds__xfcv = nlargest(A, I, k, is_largest, cmp_f)
    ytcjr__ntb = bodo.libs.distributed_api.gatherv(lod__yynkd)
    vcd__bhjkr = bodo.libs.distributed_api.gatherv(vhlds__xfcv)
    if hirv__pvfc == MPI_ROOT:
        res, canc__pklu = nlargest(ytcjr__ntb, vcd__bhjkr, k, is_largest, cmp_f
            )
    else:
        res = np.empty(k, A.dtype)
        canc__pklu = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(canc__pklu)
    return res, canc__pklu


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    qawkp__uycp, czbv__gazo = mat.shape
    ehcw__ybspw = np.empty((czbv__gazo, czbv__gazo), dtype=np.float64)
    for afua__dzma in range(czbv__gazo):
        for dppsh__yqom in range(afua__dzma + 1):
            hwxh__ijfr = 0
            zczm__andef = ormiy__jbzad = ffqn__jzpl = shpb__yzaw = 0.0
            for i in range(qawkp__uycp):
                if np.isfinite(mat[i, afua__dzma]) and np.isfinite(mat[i,
                    dppsh__yqom]):
                    gzbn__tqwhy = mat[i, afua__dzma]
                    jcp__kiu = mat[i, dppsh__yqom]
                    hwxh__ijfr += 1
                    ffqn__jzpl += gzbn__tqwhy
                    shpb__yzaw += jcp__kiu
            if parallel:
                hwxh__ijfr = bodo.libs.distributed_api.dist_reduce(hwxh__ijfr,
                    sum_op)
                ffqn__jzpl = bodo.libs.distributed_api.dist_reduce(ffqn__jzpl,
                    sum_op)
                shpb__yzaw = bodo.libs.distributed_api.dist_reduce(shpb__yzaw,
                    sum_op)
            if hwxh__ijfr < minpv:
                ehcw__ybspw[afua__dzma, dppsh__yqom] = ehcw__ybspw[
                    dppsh__yqom, afua__dzma] = np.nan
            else:
                wam__bcap = ffqn__jzpl / hwxh__ijfr
                tcuht__lub = shpb__yzaw / hwxh__ijfr
                ffqn__jzpl = 0.0
                for i in range(qawkp__uycp):
                    if np.isfinite(mat[i, afua__dzma]) and np.isfinite(mat[
                        i, dppsh__yqom]):
                        gzbn__tqwhy = mat[i, afua__dzma] - wam__bcap
                        jcp__kiu = mat[i, dppsh__yqom] - tcuht__lub
                        ffqn__jzpl += gzbn__tqwhy * jcp__kiu
                        zczm__andef += gzbn__tqwhy * gzbn__tqwhy
                        ormiy__jbzad += jcp__kiu * jcp__kiu
                if parallel:
                    ffqn__jzpl = bodo.libs.distributed_api.dist_reduce(
                        ffqn__jzpl, sum_op)
                    zczm__andef = bodo.libs.distributed_api.dist_reduce(
                        zczm__andef, sum_op)
                    ormiy__jbzad = bodo.libs.distributed_api.dist_reduce(
                        ormiy__jbzad, sum_op)
                wah__vqkfq = hwxh__ijfr - 1.0 if cov else sqrt(zczm__andef *
                    ormiy__jbzad)
                if wah__vqkfq != 0.0:
                    ehcw__ybspw[afua__dzma, dppsh__yqom] = ehcw__ybspw[
                        dppsh__yqom, afua__dzma] = ffqn__jzpl / wah__vqkfq
                else:
                    ehcw__ybspw[afua__dzma, dppsh__yqom] = ehcw__ybspw[
                        dppsh__yqom, afua__dzma] = np.nan
    return ehcw__ybspw


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    hrp__jggr = n != 1
    oufgy__kzxm = 'def impl(data, parallel=False):\n'
    oufgy__kzxm += '  if parallel:\n'
    oau__lunc = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    oufgy__kzxm += f'    cpp_table = arr_info_list_to_table([{oau__lunc}])\n'
    oufgy__kzxm += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    gfdjm__awrh = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    oufgy__kzxm += f'    data = ({gfdjm__awrh},)\n'
    oufgy__kzxm += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    oufgy__kzxm += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    oufgy__kzxm += '    bodo.libs.array.delete_table(cpp_table)\n'
    oufgy__kzxm += '  n = len(data[0])\n'
    oufgy__kzxm += '  out = np.empty(n, np.bool_)\n'
    oufgy__kzxm += '  uniqs = dict()\n'
    if hrp__jggr:
        oufgy__kzxm += '  for i in range(n):\n'
        unpzu__yng = ', '.join(f'data[{i}][i]' for i in range(n))
        nfvl__inl = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        oufgy__kzxm += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({unpzu__yng},), ({nfvl__inl},))
"""
        oufgy__kzxm += '    if val in uniqs:\n'
        oufgy__kzxm += '      out[i] = True\n'
        oufgy__kzxm += '    else:\n'
        oufgy__kzxm += '      out[i] = False\n'
        oufgy__kzxm += '      uniqs[val] = 0\n'
    else:
        oufgy__kzxm += '  data = data[0]\n'
        oufgy__kzxm += '  hasna = False\n'
        oufgy__kzxm += '  for i in range(n):\n'
        oufgy__kzxm += '    if bodo.libs.array_kernels.isna(data, i):\n'
        oufgy__kzxm += '      out[i] = hasna\n'
        oufgy__kzxm += '      hasna = True\n'
        oufgy__kzxm += '    else:\n'
        oufgy__kzxm += '      val = data[i]\n'
        oufgy__kzxm += '      if val in uniqs:\n'
        oufgy__kzxm += '        out[i] = True\n'
        oufgy__kzxm += '      else:\n'
        oufgy__kzxm += '        out[i] = False\n'
        oufgy__kzxm += '        uniqs[val] = 0\n'
    oufgy__kzxm += '  if parallel:\n'
    oufgy__kzxm += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    oufgy__kzxm += '  return out\n'
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        hkt__gxxtm)
    impl = hkt__gxxtm['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    siej__nqnlt = len(data)
    oufgy__kzxm = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    oufgy__kzxm += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        siej__nqnlt)))
    oufgy__kzxm += '  table_total = arr_info_list_to_table(info_list_total)\n'
    oufgy__kzxm += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(siej__nqnlt))
    for zdo__gdwfy in range(siej__nqnlt):
        oufgy__kzxm += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(zdo__gdwfy, zdo__gdwfy, zdo__gdwfy))
    oufgy__kzxm += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(siej__nqnlt))
    oufgy__kzxm += '  delete_table(out_table)\n'
    oufgy__kzxm += '  delete_table(table_total)\n'
    oufgy__kzxm += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(siej__nqnlt)))
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, hkt__gxxtm)
    impl = hkt__gxxtm['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    siej__nqnlt = len(data)
    oufgy__kzxm = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    oufgy__kzxm += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        siej__nqnlt)))
    oufgy__kzxm += '  table_total = arr_info_list_to_table(info_list_total)\n'
    oufgy__kzxm += '  keep_i = 0\n'
    oufgy__kzxm += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for zdo__gdwfy in range(siej__nqnlt):
        oufgy__kzxm += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(zdo__gdwfy, zdo__gdwfy, zdo__gdwfy))
    oufgy__kzxm += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(siej__nqnlt))
    oufgy__kzxm += '  delete_table(out_table)\n'
    oufgy__kzxm += '  delete_table(table_total)\n'
    oufgy__kzxm += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(siej__nqnlt)))
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, hkt__gxxtm)
    impl = hkt__gxxtm['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        huxrt__tpr = [array_to_info(data_arr)]
        ltfp__bjc = arr_info_list_to_table(huxrt__tpr)
        kqc__gqowa = 0
        abwd__glh = drop_duplicates_table(ltfp__bjc, parallel, 1,
            kqc__gqowa, False, True)
        cfl__plnoh = info_to_array(info_from_table(abwd__glh, 0), data_arr)
        delete_table(abwd__glh)
        delete_table(ltfp__bjc)
        return cfl__plnoh
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    rkgp__goc = len(data.types)
    tdphm__fgg = [('out' + str(i)) for i in range(rkgp__goc)]
    aqb__ffcvs = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    bisd__iexlu = ['isna(data[{}], i)'.format(i) for i in aqb__ffcvs]
    yvwwi__kmiwj = 'not ({})'.format(' or '.join(bisd__iexlu))
    if not is_overload_none(thresh):
        yvwwi__kmiwj = '(({}) <= ({}) - thresh)'.format(' + '.join(
            bisd__iexlu), rkgp__goc - 1)
    elif how == 'all':
        yvwwi__kmiwj = 'not ({})'.format(' and '.join(bisd__iexlu))
    oufgy__kzxm = 'def _dropna_imp(data, how, thresh, subset):\n'
    oufgy__kzxm += '  old_len = len(data[0])\n'
    oufgy__kzxm += '  new_len = 0\n'
    oufgy__kzxm += '  for i in range(old_len):\n'
    oufgy__kzxm += '    if {}:\n'.format(yvwwi__kmiwj)
    oufgy__kzxm += '      new_len += 1\n'
    for i, out in enumerate(tdphm__fgg):
        if isinstance(data[i], bodo.CategoricalArrayType):
            oufgy__kzxm += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            oufgy__kzxm += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    oufgy__kzxm += '  curr_ind = 0\n'
    oufgy__kzxm += '  for i in range(old_len):\n'
    oufgy__kzxm += '    if {}:\n'.format(yvwwi__kmiwj)
    for i in range(rkgp__goc):
        oufgy__kzxm += '      if isna(data[{}], i):\n'.format(i)
        oufgy__kzxm += '        setna({}, curr_ind)\n'.format(tdphm__fgg[i])
        oufgy__kzxm += '      else:\n'
        oufgy__kzxm += '        {}[curr_ind] = data[{}][i]\n'.format(tdphm__fgg
            [i], i)
    oufgy__kzxm += '      curr_ind += 1\n'
    oufgy__kzxm += '  return {}\n'.format(', '.join(tdphm__fgg))
    hkt__gxxtm = {}
    mkal__hdcl = {'t{}'.format(i): vrixv__poscl for i, vrixv__poscl in
        enumerate(data.types)}
    mkal__hdcl.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(oufgy__kzxm, mkal__hdcl, hkt__gxxtm)
    dhbc__ykeqx = hkt__gxxtm['_dropna_imp']
    return dhbc__ykeqx


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        fyz__sjb = arr.dtype
        ymnj__iyrm = fyz__sjb.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            atmgg__pgx = init_nested_counts(ymnj__iyrm)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                atmgg__pgx = add_nested_counts(atmgg__pgx, val[ind])
            cfl__plnoh = bodo.utils.utils.alloc_type(n, fyz__sjb, atmgg__pgx)
            for mfpbv__xzav in range(n):
                if bodo.libs.array_kernels.isna(arr, mfpbv__xzav):
                    setna(cfl__plnoh, mfpbv__xzav)
                    continue
                val = arr[mfpbv__xzav]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(cfl__plnoh, mfpbv__xzav)
                    continue
                cfl__plnoh[mfpbv__xzav] = val[ind]
            return cfl__plnoh
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    jetr__vwtd = _to_readonly(arr_types.types[0])
    return all(isinstance(vrixv__poscl, CategoricalArrayType) and 
        _to_readonly(vrixv__poscl) == jetr__vwtd for vrixv__poscl in
        arr_types.types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arr_list.
        dtype, 'bodo.concat()')
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        giy__mkjt = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            alfqd__vvex = 0
            xxqia__ang = []
            for A in arr_list:
                itf__kthr = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                xxqia__ang.append(bodo.libs.array_item_arr_ext.get_data(A))
                alfqd__vvex += itf__kthr
            jvpjg__sgid = np.empty(alfqd__vvex + 1, offset_type)
            mut__bqsp = bodo.libs.array_kernels.concat(xxqia__ang)
            actq__dqn = np.empty(alfqd__vvex + 7 >> 3, np.uint8)
            bbhkn__yzn = 0
            dfe__fjie = 0
            for A in arr_list:
                rxz__vyod = bodo.libs.array_item_arr_ext.get_offsets(A)
                xnv__wgth = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                itf__kthr = len(A)
                qhom__uir = rxz__vyod[itf__kthr]
                for i in range(itf__kthr):
                    jvpjg__sgid[i + bbhkn__yzn] = rxz__vyod[i] + dfe__fjie
                    tvrt__fzrko = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        xnv__wgth, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(actq__dqn, i +
                        bbhkn__yzn, tvrt__fzrko)
                bbhkn__yzn += itf__kthr
                dfe__fjie += qhom__uir
            jvpjg__sgid[bbhkn__yzn] = dfe__fjie
            cfl__plnoh = bodo.libs.array_item_arr_ext.init_array_item_array(
                alfqd__vvex, mut__bqsp, jvpjg__sgid, actq__dqn)
            return cfl__plnoh
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        zgmgn__alcvz = arr_list.dtype.names
        oufgy__kzxm = 'def struct_array_concat_impl(arr_list):\n'
        oufgy__kzxm += f'    n_all = 0\n'
        for i in range(len(zgmgn__alcvz)):
            oufgy__kzxm += f'    concat_list{i} = []\n'
        oufgy__kzxm += '    for A in arr_list:\n'
        oufgy__kzxm += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(zgmgn__alcvz)):
            oufgy__kzxm += f'        concat_list{i}.append(data_tuple[{i}])\n'
        oufgy__kzxm += '        n_all += len(A)\n'
        oufgy__kzxm += '    n_bytes = (n_all + 7) >> 3\n'
        oufgy__kzxm += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        oufgy__kzxm += '    curr_bit = 0\n'
        oufgy__kzxm += '    for A in arr_list:\n'
        oufgy__kzxm += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        oufgy__kzxm += '        for j in range(len(A)):\n'
        oufgy__kzxm += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        oufgy__kzxm += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        oufgy__kzxm += '            curr_bit += 1\n'
        oufgy__kzxm += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        sclu__ozon = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(zgmgn__alcvz))])
        oufgy__kzxm += f'        ({sclu__ozon},),\n'
        oufgy__kzxm += '        new_mask,\n'
        oufgy__kzxm += f'        {zgmgn__alcvz},\n'
        oufgy__kzxm += '    )\n'
        hkt__gxxtm = {}
        exec(oufgy__kzxm, {'bodo': bodo, 'np': np}, hkt__gxxtm)
        return hkt__gxxtm['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            kgspf__uar = 0
            for A in arr_list:
                kgspf__uar += len(A)
            obi__pbp = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(kgspf__uar))
            cgfh__oyuw = 0
            for A in arr_list:
                for i in range(len(A)):
                    obi__pbp._data[i + cgfh__oyuw] = A._data[i]
                    tvrt__fzrko = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(obi__pbp.
                        _null_bitmap, i + cgfh__oyuw, tvrt__fzrko)
                cgfh__oyuw += len(A)
            return obi__pbp
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            kgspf__uar = 0
            for A in arr_list:
                kgspf__uar += len(A)
            obi__pbp = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(kgspf__uar))
            cgfh__oyuw = 0
            for A in arr_list:
                for i in range(len(A)):
                    obi__pbp._days_data[i + cgfh__oyuw] = A._days_data[i]
                    obi__pbp._seconds_data[i + cgfh__oyuw] = A._seconds_data[i]
                    obi__pbp._microseconds_data[i + cgfh__oyuw
                        ] = A._microseconds_data[i]
                    tvrt__fzrko = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(obi__pbp.
                        _null_bitmap, i + cgfh__oyuw, tvrt__fzrko)
                cgfh__oyuw += len(A)
            return obi__pbp
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        huk__gyjk = arr_list.dtype.precision
        aclf__zmcpq = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            kgspf__uar = 0
            for A in arr_list:
                kgspf__uar += len(A)
            obi__pbp = bodo.libs.decimal_arr_ext.alloc_decimal_array(kgspf__uar
                , huk__gyjk, aclf__zmcpq)
            cgfh__oyuw = 0
            for A in arr_list:
                for i in range(len(A)):
                    obi__pbp._data[i + cgfh__oyuw] = A._data[i]
                    tvrt__fzrko = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(obi__pbp.
                        _null_bitmap, i + cgfh__oyuw, tvrt__fzrko)
                cgfh__oyuw += len(A)
            return obi__pbp
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        vrixv__poscl) for vrixv__poscl in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            icdp__dlfqs = arr_list.types[0]
        else:
            icdp__dlfqs = arr_list.dtype
        icdp__dlfqs = to_str_arr_if_dict_array(icdp__dlfqs)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            wbzb__rhm = 0
            lsdy__mvz = 0
            for A in arr_list:
                arr = A
                wbzb__rhm += len(arr)
                lsdy__mvz += bodo.libs.str_arr_ext.num_total_chars(arr)
            cfl__plnoh = bodo.utils.utils.alloc_type(wbzb__rhm, icdp__dlfqs,
                (lsdy__mvz,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(cfl__plnoh, -1)
            cnqy__duf = 0
            xru__vlf = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(cfl__plnoh,
                    arr, cnqy__duf, xru__vlf)
                cnqy__duf += len(arr)
                xru__vlf += bodo.libs.str_arr_ext.num_total_chars(arr)
            return cfl__plnoh
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(vrixv__poscl.dtype, types.Integer) for
        vrixv__poscl in arr_list.types) and any(isinstance(vrixv__poscl,
        IntegerArrayType) for vrixv__poscl in arr_list.types):

        def impl_int_arr_list(arr_list):
            hglrj__xruhy = convert_to_nullable_tup(arr_list)
            rdo__vdrxo = []
            ovymf__gsti = 0
            for A in hglrj__xruhy:
                rdo__vdrxo.append(A._data)
                ovymf__gsti += len(A)
            mut__bqsp = bodo.libs.array_kernels.concat(rdo__vdrxo)
            uqjs__ike = ovymf__gsti + 7 >> 3
            mpzox__kifvj = np.empty(uqjs__ike, np.uint8)
            zljs__gwc = 0
            for A in hglrj__xruhy:
                jjs__mpl = A._null_bitmap
                for mfpbv__xzav in range(len(A)):
                    tvrt__fzrko = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        jjs__mpl, mfpbv__xzav)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mpzox__kifvj,
                        zljs__gwc, tvrt__fzrko)
                    zljs__gwc += 1
            return bodo.libs.int_arr_ext.init_integer_array(mut__bqsp,
                mpzox__kifvj)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(vrixv__poscl.dtype == types.bool_ for
        vrixv__poscl in arr_list.types) and any(vrixv__poscl ==
        boolean_array for vrixv__poscl in arr_list.types):

        def impl_bool_arr_list(arr_list):
            hglrj__xruhy = convert_to_nullable_tup(arr_list)
            rdo__vdrxo = []
            ovymf__gsti = 0
            for A in hglrj__xruhy:
                rdo__vdrxo.append(A._data)
                ovymf__gsti += len(A)
            mut__bqsp = bodo.libs.array_kernels.concat(rdo__vdrxo)
            uqjs__ike = ovymf__gsti + 7 >> 3
            mpzox__kifvj = np.empty(uqjs__ike, np.uint8)
            zljs__gwc = 0
            for A in hglrj__xruhy:
                jjs__mpl = A._null_bitmap
                for mfpbv__xzav in range(len(A)):
                    tvrt__fzrko = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        jjs__mpl, mfpbv__xzav)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mpzox__kifvj,
                        zljs__gwc, tvrt__fzrko)
                    zljs__gwc += 1
            return bodo.libs.bool_arr_ext.init_bool_array(mut__bqsp,
                mpzox__kifvj)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            lme__imx = []
            for A in arr_list:
                lme__imx.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                lme__imx), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        dglox__rslr = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        oufgy__kzxm = 'def impl(arr_list):\n'
        oufgy__kzxm += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({dglox__rslr},)), arr_list[0].dtype)
"""
        zmluo__gbsl = {}
        exec(oufgy__kzxm, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, zmluo__gbsl)
        return zmluo__gbsl['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            ovymf__gsti = 0
            for A in arr_list:
                ovymf__gsti += len(A)
            cfl__plnoh = np.empty(ovymf__gsti, dtype)
            xqlzx__xns = 0
            for A in arr_list:
                n = len(A)
                cfl__plnoh[xqlzx__xns:xqlzx__xns + n] = A
                xqlzx__xns += n
            return cfl__plnoh
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(
        vrixv__poscl, (types.Array, IntegerArrayType)) and isinstance(
        vrixv__poscl.dtype, types.Integer) for vrixv__poscl in arr_list.types
        ) and any(isinstance(vrixv__poscl, types.Array) and isinstance(
        vrixv__poscl.dtype, types.Float) for vrixv__poscl in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            qrpt__hsld = []
            for A in arr_list:
                qrpt__hsld.append(A._data)
            ruf__pfrev = bodo.libs.array_kernels.concat(qrpt__hsld)
            ehcw__ybspw = bodo.libs.map_arr_ext.init_map_arr(ruf__pfrev)
            return ehcw__ybspw
        return impl_map_arr_list
    for oziv__ssv in arr_list:
        if not isinstance(oziv__ssv, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(vrixv__poscl.astype(np.float64) for vrixv__poscl in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    siej__nqnlt = len(arr_tup.types)
    oufgy__kzxm = 'def f(arr_tup):\n'
    oufgy__kzxm += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        siej__nqnlt)), ',' if siej__nqnlt == 1 else '')
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'np': np}, hkt__gxxtm)
    nnlmz__ombj = hkt__gxxtm['f']
    return nnlmz__ombj


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    siej__nqnlt = len(arr_tup.types)
    uein__rfgm = find_common_np_dtype(arr_tup.types)
    ymnj__iyrm = None
    rwdd__ohfq = ''
    if isinstance(uein__rfgm, types.Integer):
        ymnj__iyrm = bodo.libs.int_arr_ext.IntDtype(uein__rfgm)
        rwdd__ohfq = '.astype(out_dtype, False)'
    oufgy__kzxm = 'def f(arr_tup):\n'
    oufgy__kzxm += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, rwdd__ohfq) for i in range(siej__nqnlt)), ',' if 
        siej__nqnlt == 1 else '')
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'bodo': bodo, 'out_dtype': ymnj__iyrm}, hkt__gxxtm)
    rnqg__itho = hkt__gxxtm['f']
    return rnqg__itho


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, zhuhw__fpu = build_set_seen_na(A)
        return len(s) + int(not dropna and zhuhw__fpu)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        dlcp__kslsz = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        efy__wwn = len(dlcp__kslsz)
        return bodo.libs.distributed_api.dist_reduce(efy__wwn, np.int32(sum_op)
            )
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([ltwf__dtgkr for ltwf__dtgkr in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        spntn__lzlvw = np.finfo(A.dtype(1).dtype).max
    else:
        spntn__lzlvw = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        cfl__plnoh = np.empty(n, A.dtype)
        dtai__tqc = spntn__lzlvw
        for i in range(n):
            dtai__tqc = min(dtai__tqc, A[i])
            cfl__plnoh[i] = dtai__tqc
        return cfl__plnoh
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        spntn__lzlvw = np.finfo(A.dtype(1).dtype).min
    else:
        spntn__lzlvw = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        cfl__plnoh = np.empty(n, A.dtype)
        dtai__tqc = spntn__lzlvw
        for i in range(n):
            dtai__tqc = max(dtai__tqc, A[i])
            cfl__plnoh[i] = dtai__tqc
        return cfl__plnoh
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        kgmm__kvsyo = arr_info_list_to_table([array_to_info(A)])
        jnt__wst = 1
        kqc__gqowa = 0
        abwd__glh = drop_duplicates_table(kgmm__kvsyo, parallel, jnt__wst,
            kqc__gqowa, dropna, True)
        cfl__plnoh = info_to_array(info_from_table(abwd__glh, 0), A)
        delete_table(kgmm__kvsyo)
        delete_table(abwd__glh)
        return cfl__plnoh
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    giy__mkjt = bodo.utils.typing.to_nullable_type(arr.dtype)
    yzj__wny = index_arr
    ojw__ahb = yzj__wny.dtype

    def impl(arr, index_arr):
        n = len(arr)
        atmgg__pgx = init_nested_counts(giy__mkjt)
        bpau__vahl = init_nested_counts(ojw__ahb)
        for i in range(n):
            tex__jjd = index_arr[i]
            if isna(arr, i):
                atmgg__pgx = (atmgg__pgx[0] + 1,) + atmgg__pgx[1:]
                bpau__vahl = add_nested_counts(bpau__vahl, tex__jjd)
                continue
            vqgom__nodf = arr[i]
            if len(vqgom__nodf) == 0:
                atmgg__pgx = (atmgg__pgx[0] + 1,) + atmgg__pgx[1:]
                bpau__vahl = add_nested_counts(bpau__vahl, tex__jjd)
                continue
            atmgg__pgx = add_nested_counts(atmgg__pgx, vqgom__nodf)
            for qcanz__ijzkl in range(len(vqgom__nodf)):
                bpau__vahl = add_nested_counts(bpau__vahl, tex__jjd)
        cfl__plnoh = bodo.utils.utils.alloc_type(atmgg__pgx[0], giy__mkjt,
            atmgg__pgx[1:])
        opr__koa = bodo.utils.utils.alloc_type(atmgg__pgx[0], yzj__wny,
            bpau__vahl)
        dfe__fjie = 0
        for i in range(n):
            if isna(arr, i):
                setna(cfl__plnoh, dfe__fjie)
                opr__koa[dfe__fjie] = index_arr[i]
                dfe__fjie += 1
                continue
            vqgom__nodf = arr[i]
            qhom__uir = len(vqgom__nodf)
            if qhom__uir == 0:
                setna(cfl__plnoh, dfe__fjie)
                opr__koa[dfe__fjie] = index_arr[i]
                dfe__fjie += 1
                continue
            cfl__plnoh[dfe__fjie:dfe__fjie + qhom__uir] = vqgom__nodf
            opr__koa[dfe__fjie:dfe__fjie + qhom__uir] = index_arr[i]
            dfe__fjie += qhom__uir
        return cfl__plnoh, opr__koa
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    giy__mkjt = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        atmgg__pgx = init_nested_counts(giy__mkjt)
        for i in range(n):
            if isna(arr, i):
                atmgg__pgx = (atmgg__pgx[0] + 1,) + atmgg__pgx[1:]
                sekb__owz = 1
            else:
                vqgom__nodf = arr[i]
                vlgot__djbj = len(vqgom__nodf)
                if vlgot__djbj == 0:
                    atmgg__pgx = (atmgg__pgx[0] + 1,) + atmgg__pgx[1:]
                    sekb__owz = 1
                    continue
                else:
                    atmgg__pgx = add_nested_counts(atmgg__pgx, vqgom__nodf)
                    sekb__owz = vlgot__djbj
            if counts[i] != sekb__owz:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        cfl__plnoh = bodo.utils.utils.alloc_type(atmgg__pgx[0], giy__mkjt,
            atmgg__pgx[1:])
        dfe__fjie = 0
        for i in range(n):
            if isna(arr, i):
                setna(cfl__plnoh, dfe__fjie)
                dfe__fjie += 1
                continue
            vqgom__nodf = arr[i]
            qhom__uir = len(vqgom__nodf)
            if qhom__uir == 0:
                setna(cfl__plnoh, dfe__fjie)
                dfe__fjie += 1
                continue
            cfl__plnoh[dfe__fjie:dfe__fjie + qhom__uir] = vqgom__nodf
            dfe__fjie += qhom__uir
        return cfl__plnoh
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(ztp__cvad) for ztp__cvad in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        cjzpt__prfyb = 'np.empty(n, np.int64)'
        hte__fawrv = 'out_arr[i] = 1'
        xbiw__lgr = 'max(len(arr[i]), 1)'
    else:
        cjzpt__prfyb = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        hte__fawrv = 'bodo.libs.array_kernels.setna(out_arr, i)'
        xbiw__lgr = 'len(arr[i])'
    oufgy__kzxm = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {cjzpt__prfyb}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {hte__fawrv}
        else:
            out_arr[i] = {xbiw__lgr}
    return out_arr
    """
    hkt__gxxtm = {}
    exec(oufgy__kzxm, {'bodo': bodo, 'numba': numba, 'np': np}, hkt__gxxtm)
    impl = hkt__gxxtm['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    yzj__wny = index_arr
    ojw__ahb = yzj__wny.dtype

    def impl(arr, pat, n, index_arr):
        qfo__pvus = pat is not None and len(pat) > 1
        if qfo__pvus:
            mmyzf__rpcmn = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        inkx__nvuy = len(arr)
        wbzb__rhm = 0
        lsdy__mvz = 0
        bpau__vahl = init_nested_counts(ojw__ahb)
        for i in range(inkx__nvuy):
            tex__jjd = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                wbzb__rhm += 1
                bpau__vahl = add_nested_counts(bpau__vahl, tex__jjd)
                continue
            if qfo__pvus:
                kxxug__fyznp = mmyzf__rpcmn.split(arr[i], maxsplit=n)
            else:
                kxxug__fyznp = arr[i].split(pat, n)
            wbzb__rhm += len(kxxug__fyznp)
            for s in kxxug__fyznp:
                bpau__vahl = add_nested_counts(bpau__vahl, tex__jjd)
                lsdy__mvz += bodo.libs.str_arr_ext.get_utf8_size(s)
        cfl__plnoh = bodo.libs.str_arr_ext.pre_alloc_string_array(wbzb__rhm,
            lsdy__mvz)
        opr__koa = bodo.utils.utils.alloc_type(wbzb__rhm, yzj__wny, bpau__vahl)
        vlmk__colz = 0
        for mfpbv__xzav in range(inkx__nvuy):
            if isna(arr, mfpbv__xzav):
                cfl__plnoh[vlmk__colz] = ''
                bodo.libs.array_kernels.setna(cfl__plnoh, vlmk__colz)
                opr__koa[vlmk__colz] = index_arr[mfpbv__xzav]
                vlmk__colz += 1
                continue
            if qfo__pvus:
                kxxug__fyznp = mmyzf__rpcmn.split(arr[mfpbv__xzav], maxsplit=n)
            else:
                kxxug__fyznp = arr[mfpbv__xzav].split(pat, n)
            okha__cef = len(kxxug__fyznp)
            cfl__plnoh[vlmk__colz:vlmk__colz + okha__cef] = kxxug__fyznp
            opr__koa[vlmk__colz:vlmk__colz + okha__cef] = index_arr[mfpbv__xzav
                ]
            vlmk__colz += okha__cef
        return cfl__plnoh, opr__koa
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if not isinstance(arr, IntegerArrayType) and isinstance(dtype, (types.
        Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr):
            numba.parfors.parfor.init_prange()
            cfl__plnoh = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                cfl__plnoh[i] = np.nan
            return cfl__plnoh
        return impl_float
    rcevq__djlg = to_str_arr_if_dict_array(arr)

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        cfl__plnoh = bodo.utils.utils.alloc_type(n, rcevq__djlg, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(cfl__plnoh, i)
        return cfl__plnoh
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.resize_and_copy()')
    ohz__xteo = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            cfl__plnoh = bodo.utils.utils.alloc_type(new_len, ohz__xteo)
            bodo.libs.str_arr_ext.str_copy_ptr(cfl__plnoh.ctypes, 0, A.
                ctypes, old_size)
            return cfl__plnoh
        return impl_char

    def impl(A, old_size, new_len):
        cfl__plnoh = bodo.utils.utils.alloc_type(new_len, ohz__xteo, (-1,))
        cfl__plnoh[:old_size] = A[:old_size]
        return cfl__plnoh
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    enkyj__dzh = math.ceil((stop - start) / step)
    return int(max(enkyj__dzh, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(ltwf__dtgkr, types.Complex) for ltwf__dtgkr in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            vnbls__xkp = (stop - start) / step
            enkyj__dzh = math.ceil(vnbls__xkp.real)
            ycc__clpoz = math.ceil(vnbls__xkp.imag)
            rad__osv = int(max(min(ycc__clpoz, enkyj__dzh), 0))
            arr = np.empty(rad__osv, dtype)
            for i in numba.parfors.parfor.internal_prange(rad__osv):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            rad__osv = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(rad__osv, dtype)
            for i in numba.parfors.parfor.internal_prange(rad__osv):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        ktxfg__ltjp = arr,
        if not inplace:
            ktxfg__ltjp = arr.copy(),
        lyqb__jlsq = bodo.libs.str_arr_ext.to_list_if_immutable_arr(ktxfg__ltjp
            )
        ebnpj__rio = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(lyqb__jlsq, 0, n, ebnpj__rio)
        if not ascending:
            bodo.libs.timsort.reverseRange(lyqb__jlsq, 0, n, ebnpj__rio)
        bodo.libs.str_arr_ext.cp_str_list_to_array(ktxfg__ltjp, lyqb__jlsq)
        return ktxfg__ltjp[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.nonzero()')
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        ehcw__ybspw = []
        for i in range(n):
            if A[i]:
                ehcw__ybspw.append(i + offset)
        return np.array(ehcw__ybspw, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    ohz__xteo = element_type(A)
    if ohz__xteo == types.unicode_type:
        null_value = '""'
    elif ohz__xteo == types.bool_:
        null_value = 'False'
    elif ohz__xteo == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif ohz__xteo == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    vlmk__colz = 'i'
    enxr__vjp = False
    aibg__qygmu = get_overload_const_str(method)
    if aibg__qygmu in ('ffill', 'pad'):
        xlo__hux = 'n'
        send_right = True
    elif aibg__qygmu in ('backfill', 'bfill'):
        xlo__hux = 'n-1, -1, -1'
        send_right = False
        if ohz__xteo == types.unicode_type:
            vlmk__colz = '(n - 1) - i'
            enxr__vjp = True
    oufgy__kzxm = 'def impl(A, method, parallel=False):\n'
    oufgy__kzxm += '  A = decode_if_dict_array(A)\n'
    oufgy__kzxm += '  has_last_value = False\n'
    oufgy__kzxm += f'  last_value = {null_value}\n'
    oufgy__kzxm += '  if parallel:\n'
    oufgy__kzxm += '    rank = bodo.libs.distributed_api.get_rank()\n'
    oufgy__kzxm += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    oufgy__kzxm += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    oufgy__kzxm += '  n = len(A)\n'
    oufgy__kzxm += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    oufgy__kzxm += f'  for i in range({xlo__hux}):\n'
    oufgy__kzxm += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    oufgy__kzxm += (
        f'      bodo.libs.array_kernels.setna(out_arr, {vlmk__colz})\n')
    oufgy__kzxm += '      continue\n'
    oufgy__kzxm += '    s = A[i]\n'
    oufgy__kzxm += '    if bodo.libs.array_kernels.isna(A, i):\n'
    oufgy__kzxm += '      s = last_value\n'
    oufgy__kzxm += f'    out_arr[{vlmk__colz}] = s\n'
    oufgy__kzxm += '    last_value = s\n'
    oufgy__kzxm += '    has_last_value = True\n'
    if enxr__vjp:
        oufgy__kzxm += '  return out_arr[::-1]\n'
    else:
        oufgy__kzxm += '  return out_arr\n'
    uov__rga = {}
    exec(oufgy__kzxm, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, uov__rga)
    impl = uov__rga['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        urg__ygbht = 0
        sae__bfnua = n_pes - 1
        rhjxi__zic = np.int32(rank + 1)
        cmdnx__idrc = np.int32(rank - 1)
        puqe__fuu = len(in_arr) - 1
        curuw__gio = -1
        lgwok__acbsk = -1
    else:
        urg__ygbht = n_pes - 1
        sae__bfnua = 0
        rhjxi__zic = np.int32(rank - 1)
        cmdnx__idrc = np.int32(rank + 1)
        puqe__fuu = 0
        curuw__gio = len(in_arr)
        lgwok__acbsk = 1
    nufje__kztc = np.int32(bodo.hiframes.rolling.comm_border_tag)
    oiqm__bwfyc = np.empty(1, dtype=np.bool_)
    ozjh__yszqp = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    yyyy__jex = np.empty(1, dtype=np.bool_)
    cvo__piah = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    mghy__fhy = False
    fsbmc__iob = null_value
    for i in range(puqe__fuu, curuw__gio, lgwok__acbsk):
        if not isna(in_arr, i):
            mghy__fhy = True
            fsbmc__iob = in_arr[i]
            break
    if rank != urg__ygbht:
        wlf__mbm = bodo.libs.distributed_api.irecv(oiqm__bwfyc, 1,
            cmdnx__idrc, nufje__kztc, True)
        bodo.libs.distributed_api.wait(wlf__mbm, True)
        rci__wku = bodo.libs.distributed_api.irecv(ozjh__yszqp, 1,
            cmdnx__idrc, nufje__kztc, True)
        bodo.libs.distributed_api.wait(rci__wku, True)
        tvls__bvw = oiqm__bwfyc[0]
        yed__vmbsf = ozjh__yszqp[0]
    else:
        tvls__bvw = False
        yed__vmbsf = null_value
    if mghy__fhy:
        yyyy__jex[0] = mghy__fhy
        cvo__piah[0] = fsbmc__iob
    else:
        yyyy__jex[0] = tvls__bvw
        cvo__piah[0] = yed__vmbsf
    if rank != sae__bfnua:
        xfqlk__guk = bodo.libs.distributed_api.isend(yyyy__jex, 1,
            rhjxi__zic, nufje__kztc, True)
        sjqps__wqk = bodo.libs.distributed_api.isend(cvo__piah, 1,
            rhjxi__zic, nufje__kztc, True)
    return tvls__bvw, yed__vmbsf


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    wsd__vgl = {'axis': axis, 'kind': kind, 'order': order}
    zdqzm__ldjn = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', wsd__vgl, zdqzm__ldjn, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    ohz__xteo = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            inkx__nvuy = len(A)
            cfl__plnoh = bodo.utils.utils.alloc_type(inkx__nvuy * repeats,
                ohz__xteo, (-1,))
            for i in range(inkx__nvuy):
                vlmk__colz = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for mfpbv__xzav in range(repeats):
                        bodo.libs.array_kernels.setna(cfl__plnoh, 
                            vlmk__colz + mfpbv__xzav)
                else:
                    cfl__plnoh[vlmk__colz:vlmk__colz + repeats] = A[i]
            return cfl__plnoh
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        inkx__nvuy = len(A)
        cfl__plnoh = bodo.utils.utils.alloc_type(repeats.sum(), ohz__xteo,
            (-1,))
        vlmk__colz = 0
        for i in range(inkx__nvuy):
            hnju__eapx = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for mfpbv__xzav in range(hnju__eapx):
                    bodo.libs.array_kernels.setna(cfl__plnoh, vlmk__colz +
                        mfpbv__xzav)
            else:
                cfl__plnoh[vlmk__colz:vlmk__colz + hnju__eapx] = A[i]
            vlmk__colz += hnju__eapx
        return cfl__plnoh
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@numba.generated_jit
def repeat_like(A, dist_like_arr):
    if not bodo.utils.utils.is_array_typ(A, False
        ) or not bodo.utils.utils.is_array_typ(dist_like_arr, False):
        raise BodoError('Both A and dist_like_arr must be array-like.')

    def impl(A, dist_like_arr):
        return bodo.libs.array_kernels.repeat_kernel(A, len(dist_like_arr))
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        lntg__wyyu = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(lntg__wyyu, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        tzx__uft = bodo.libs.array_kernels.concat([A1, A2])
        pfav__mhyk = bodo.libs.array_kernels.unique(tzx__uft)
        return pd.Series(pfav__mhyk).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    wsd__vgl = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    zdqzm__ldjn = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', wsd__vgl, zdqzm__ldjn, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        lvi__kpqb = bodo.libs.array_kernels.unique(A1)
        yjl__slqj = bodo.libs.array_kernels.unique(A2)
        tzx__uft = bodo.libs.array_kernels.concat([lvi__kpqb, yjl__slqj])
        pmht__webjc = pd.Series(tzx__uft).sort_values().values
        return slice_array_intersect1d(pmht__webjc)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    nvbjb__jbf = arr[1:] == arr[:-1]
    return arr[:-1][nvbjb__jbf]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    nufje__kztc = np.int32(bodo.hiframes.rolling.comm_border_tag)
    mcag__pdkit = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        velg__kdhrm = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), nufje__kztc, True)
        bodo.libs.distributed_api.wait(velg__kdhrm, True)
    if rank == n_pes - 1:
        return None
    else:
        jejsu__xygio = bodo.libs.distributed_api.irecv(mcag__pdkit, 1, np.
            int32(rank + 1), nufje__kztc, True)
        bodo.libs.distributed_api.wait(jejsu__xygio, True)
        return mcag__pdkit[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    nvbjb__jbf = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            nvbjb__jbf[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        siqfr__omxx = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == siqfr__omxx:
            nvbjb__jbf[n - 1] = True
    return nvbjb__jbf


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    wsd__vgl = {'assume_unique': assume_unique}
    zdqzm__ldjn = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', wsd__vgl, zdqzm__ldjn, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        lvi__kpqb = bodo.libs.array_kernels.unique(A1)
        yjl__slqj = bodo.libs.array_kernels.unique(A2)
        nvbjb__jbf = calculate_mask_setdiff1d(lvi__kpqb, yjl__slqj)
        return pd.Series(lvi__kpqb[nvbjb__jbf]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    nvbjb__jbf = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        nvbjb__jbf &= A1 != A2[i]
    return nvbjb__jbf


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    wsd__vgl = {'retstep': retstep, 'axis': axis}
    zdqzm__ldjn = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', wsd__vgl, zdqzm__ldjn, 'numpy')
    ndr__zwt = False
    if is_overload_none(dtype):
        ohz__xteo = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            ndr__zwt = True
        ohz__xteo = numba.np.numpy_support.as_dtype(dtype).type
    if ndr__zwt:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            drkm__prp = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            cfl__plnoh = np.empty(num, ohz__xteo)
            for i in numba.parfors.parfor.internal_prange(num):
                cfl__plnoh[i] = ohz__xteo(np.floor(start + i * drkm__prp))
            return cfl__plnoh
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            drkm__prp = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            cfl__plnoh = np.empty(num, ohz__xteo)
            for i in numba.parfors.parfor.internal_prange(num):
                cfl__plnoh[i] = ohz__xteo(start + i * drkm__prp)
            return cfl__plnoh
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'np.contains()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        siej__nqnlt = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                siej__nqnlt += A[i] == val
        return siej__nqnlt > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    wsd__vgl = {'axis': axis, 'out': out, 'keepdims': keepdims}
    zdqzm__ldjn = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', wsd__vgl, zdqzm__ldjn, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        siej__nqnlt = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                siej__nqnlt += int(bool(A[i]))
        return siej__nqnlt > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    wsd__vgl = {'axis': axis, 'out': out, 'keepdims': keepdims}
    zdqzm__ldjn = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', wsd__vgl, zdqzm__ldjn, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        siej__nqnlt = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                siej__nqnlt += int(bool(A[i]))
        return siej__nqnlt == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    wsd__vgl = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    zdqzm__ldjn = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', wsd__vgl, zdqzm__ldjn, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        atcqs__flev = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            cfl__plnoh = np.empty(n, atcqs__flev)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(cfl__plnoh, i)
                    continue
                cfl__plnoh[i] = np_cbrt_scalar(A[i], atcqs__flev)
            return cfl__plnoh
        return impl_arr
    atcqs__flev = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, atcqs__flev)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    hxntm__ygw = x < 0
    if hxntm__ygw:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if hxntm__ygw:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    iebpd__axfwy = isinstance(tup, (types.BaseTuple, types.List))
    kijl__trjb = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for oziv__ssv in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(oziv__ssv
                , 'numpy.hstack()')
            iebpd__axfwy = iebpd__axfwy and bodo.utils.utils.is_array_typ(
                oziv__ssv, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        iebpd__axfwy = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif kijl__trjb:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        jjr__cycmi = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for oziv__ssv in jjr__cycmi.types:
            kijl__trjb = kijl__trjb and bodo.utils.utils.is_array_typ(oziv__ssv
                , False)
    if not (iebpd__axfwy or kijl__trjb):
        return
    if kijl__trjb:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    wsd__vgl = {'check_valid': check_valid, 'tol': tol}
    zdqzm__ldjn = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', wsd__vgl,
        zdqzm__ldjn, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        qawkp__uycp = mean.shape[0]
        jzw__rskil = size, qawkp__uycp
        wzbbe__hup = np.random.standard_normal(jzw__rskil)
        cov = cov.astype(np.float64)
        vcgc__avw, s, pbu__txg = np.linalg.svd(cov)
        res = np.dot(wzbbe__hup, np.sqrt(s).reshape(qawkp__uycp, 1) * pbu__txg)
        wjyb__celu = res + mean
        return wjyb__celu
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            pifxo__zrsl = bodo.hiframes.series_kernels._get_type_max_value(arr)
            nqa__epox = typing.builtins.IndexValue(-1, pifxo__zrsl)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ktm__rghgt = typing.builtins.IndexValue(i, arr[i])
                nqa__epox = min(nqa__epox, ktm__rghgt)
            return nqa__epox.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        mvj__fpu = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            sbd__eid = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            pifxo__zrsl = mvj__fpu(len(arr.dtype.categories) + 1)
            nqa__epox = typing.builtins.IndexValue(-1, pifxo__zrsl)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ktm__rghgt = typing.builtins.IndexValue(i, sbd__eid[i])
                nqa__epox = min(nqa__epox, ktm__rghgt)
            return nqa__epox.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            pifxo__zrsl = bodo.hiframes.series_kernels._get_type_min_value(arr)
            nqa__epox = typing.builtins.IndexValue(-1, pifxo__zrsl)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ktm__rghgt = typing.builtins.IndexValue(i, arr[i])
                nqa__epox = max(nqa__epox, ktm__rghgt)
            return nqa__epox.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        mvj__fpu = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            sbd__eid = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            pifxo__zrsl = mvj__fpu(-1)
            nqa__epox = typing.builtins.IndexValue(-1, pifxo__zrsl)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                ktm__rghgt = typing.builtins.IndexValue(i, sbd__eid[i])
                nqa__epox = max(nqa__epox, ktm__rghgt)
            return nqa__epox.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
