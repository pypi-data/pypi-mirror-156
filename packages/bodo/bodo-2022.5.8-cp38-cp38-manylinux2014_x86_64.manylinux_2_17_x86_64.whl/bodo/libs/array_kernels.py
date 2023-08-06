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
        lboun__xbn = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = lboun__xbn
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        lboun__xbn = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = lboun__xbn
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
            xvkow__xtzay = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            xvkow__xtzay[ind + 1] = xvkow__xtzay[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            xvkow__xtzay = bodo.libs.array_item_arr_ext.get_offsets(arr)
            xvkow__xtzay[ind + 1] = xvkow__xtzay[ind]
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
    mnkb__wlnq = arr_tup.count
    qcvp__mia = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(mnkb__wlnq):
        qcvp__mia += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    qcvp__mia += '  return\n'
    nbz__gimo = {}
    exec(qcvp__mia, {'setna': setna}, nbz__gimo)
    impl = nbz__gimo['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        welm__ddh = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(welm__ddh.start, welm__ddh.stop, welm__ddh.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        auv__mqesx = 'n'
        wdczh__dmls = 'n_pes'
        rrw__dmkm = 'min_op'
    else:
        auv__mqesx = 'n-1, -1, -1'
        wdczh__dmls = '-1'
        rrw__dmkm = 'max_op'
    qcvp__mia = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {wdczh__dmls}
    for i in range({auv__mqesx}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {rrw__dmkm}))
        if possible_valid_rank != {wdczh__dmls}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    nbz__gimo = {}
    exec(qcvp__mia, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op': max_op,
        'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.box_if_dt64},
        nbz__gimo)
    impl = nbz__gimo['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    umg__ohpwr = array_to_info(arr)
    _median_series_computation(res, umg__ohpwr, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(umg__ohpwr)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    umg__ohpwr = array_to_info(arr)
    _autocorr_series_computation(res, umg__ohpwr, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(umg__ohpwr)


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
    umg__ohpwr = array_to_info(arr)
    _compute_series_monotonicity(res, umg__ohpwr, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(umg__ohpwr)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    iad__tang = res[0] > 0.5
    return iad__tang


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        wjsot__mbyy = '-'
        lam__lild = 'index_arr[0] > threshhold_date'
        auv__mqesx = '1, n+1'
        buifq__szd = 'index_arr[-i] <= threshhold_date'
        epn__bud = 'i - 1'
    else:
        wjsot__mbyy = '+'
        lam__lild = 'index_arr[-1] < threshhold_date'
        auv__mqesx = 'n'
        buifq__szd = 'index_arr[i] >= threshhold_date'
        epn__bud = 'i'
    qcvp__mia = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        qcvp__mia += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        qcvp__mia += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            qcvp__mia += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            qcvp__mia += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            qcvp__mia += '    else:\n'
            qcvp__mia += '      threshhold_date = initial_date + date_offset\n'
        else:
            qcvp__mia += (
                f'    threshhold_date = initial_date {wjsot__mbyy} date_offset\n'
                )
    else:
        qcvp__mia += f'  threshhold_date = initial_date {wjsot__mbyy} offset\n'
    qcvp__mia += '  local_valid = 0\n'
    qcvp__mia += f'  n = len(index_arr)\n'
    qcvp__mia += f'  if n:\n'
    qcvp__mia += f'    if {lam__lild}:\n'
    qcvp__mia += '      loc_valid = n\n'
    qcvp__mia += '    else:\n'
    qcvp__mia += f'      for i in range({auv__mqesx}):\n'
    qcvp__mia += f'        if {buifq__szd}:\n'
    qcvp__mia += f'          loc_valid = {epn__bud}\n'
    qcvp__mia += '          break\n'
    qcvp__mia += '  if is_parallel:\n'
    qcvp__mia += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    qcvp__mia += '    return total_valid\n'
    qcvp__mia += '  else:\n'
    qcvp__mia += '    return loc_valid\n'
    nbz__gimo = {}
    exec(qcvp__mia, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, nbz__gimo)
    return nbz__gimo['impl']


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
    mciiq__woshe = numba_to_c_type(sig.args[0].dtype)
    mnabt__ihajv = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), mciiq__woshe))
    fvsu__ezsrg = args[0]
    qhtet__rvdx = sig.args[0]
    if isinstance(qhtet__rvdx, (IntegerArrayType, BooleanArrayType)):
        fvsu__ezsrg = cgutils.create_struct_proxy(qhtet__rvdx)(context,
            builder, fvsu__ezsrg).data
        qhtet__rvdx = types.Array(qhtet__rvdx.dtype, 1, 'C')
    assert qhtet__rvdx.ndim == 1
    arr = make_array(qhtet__rvdx)(context, builder, fvsu__ezsrg)
    ban__ziiv = builder.extract_value(arr.shape, 0)
    zwp__zsuv = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        ban__ziiv, args[1], builder.load(mnabt__ihajv)]
    fpnxe__mmzz = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    nqatk__whl = lir.FunctionType(lir.DoubleType(), fpnxe__mmzz)
    uqd__qts = cgutils.get_or_insert_function(builder.module, nqatk__whl,
        name='quantile_sequential')
    brot__wbg = builder.call(uqd__qts, zwp__zsuv)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return brot__wbg


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    mciiq__woshe = numba_to_c_type(sig.args[0].dtype)
    mnabt__ihajv = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), mciiq__woshe))
    fvsu__ezsrg = args[0]
    qhtet__rvdx = sig.args[0]
    if isinstance(qhtet__rvdx, (IntegerArrayType, BooleanArrayType)):
        fvsu__ezsrg = cgutils.create_struct_proxy(qhtet__rvdx)(context,
            builder, fvsu__ezsrg).data
        qhtet__rvdx = types.Array(qhtet__rvdx.dtype, 1, 'C')
    assert qhtet__rvdx.ndim == 1
    arr = make_array(qhtet__rvdx)(context, builder, fvsu__ezsrg)
    ban__ziiv = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        ilxf__zgkla = args[2]
    else:
        ilxf__zgkla = ban__ziiv
    zwp__zsuv = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        ban__ziiv, ilxf__zgkla, args[1], builder.load(mnabt__ihajv)]
    fpnxe__mmzz = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        IntType(64), lir.DoubleType(), lir.IntType(32)]
    nqatk__whl = lir.FunctionType(lir.DoubleType(), fpnxe__mmzz)
    uqd__qts = cgutils.get_or_insert_function(builder.module, nqatk__whl,
        name='quantile_parallel')
    brot__wbg = builder.call(uqd__qts, zwp__zsuv)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return brot__wbg


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
    qcvp__mia = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    qcvp__mia += '  na_idxs = pd.isna(arr)\n'
    qcvp__mia += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    qcvp__mia += '  nas = sum(na_idxs)\n'
    if not ascending:
        qcvp__mia += '  if nas and nas < (sorter.size - 1):\n'
        qcvp__mia += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        qcvp__mia += '  else:\n'
        qcvp__mia += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        qcvp__mia += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    qcvp__mia += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    qcvp__mia += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        qcvp__mia += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        qcvp__mia += '    inv,\n'
        qcvp__mia += '    new_dtype=np.float64,\n'
        qcvp__mia += '    copy=True,\n'
        qcvp__mia += '    nan_to_str=False,\n'
        qcvp__mia += '    from_series=True,\n'
        qcvp__mia += '    ) + 1\n'
    else:
        qcvp__mia += '  arr = arr[sorter]\n'
        qcvp__mia += '  sorted_nas = np.nonzero(pd.isna(arr))[0]\n'
        qcvp__mia += '  eq_arr_na = arr[1:] != arr[:-1]\n'
        qcvp__mia += '  eq_arr_na[pd.isna(eq_arr_na)] = False\n'
        qcvp__mia += '  eq_arr = eq_arr_na.astype(np.bool_)\n'
        qcvp__mia += '  obs = np.concatenate((np.array([True]), eq_arr))\n'
        qcvp__mia += '  if sorted_nas.size:\n'
        qcvp__mia += '    first_na, rep_nas = sorted_nas[0], sorted_nas[1:]\n'
        qcvp__mia += '    obs[first_na] = True\n'
        qcvp__mia += '    obs[rep_nas] = False\n'
        qcvp__mia += '    if rep_nas.size and (rep_nas[-1] + 1) < obs.size:\n'
        qcvp__mia += '      obs[rep_nas[-1] + 1] = True\n'
        qcvp__mia += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            qcvp__mia += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            qcvp__mia += '    dense,\n'
            qcvp__mia += '    new_dtype=np.float64,\n'
            qcvp__mia += '    copy=True,\n'
            qcvp__mia += '    nan_to_str=False,\n'
            qcvp__mia += '    from_series=True,\n'
            qcvp__mia += '  )\n'
        else:
            qcvp__mia += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            qcvp__mia += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                qcvp__mia += '  ret = count_float[dense]\n'
            elif method == 'min':
                qcvp__mia += '  ret = count_float[dense - 1] + 1\n'
            else:
                qcvp__mia += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                qcvp__mia += '  ret[na_idxs] = -1\n'
            qcvp__mia += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            qcvp__mia += '  div_val = arr.size - nas\n'
        else:
            qcvp__mia += '  div_val = arr.size\n'
        qcvp__mia += '  for i in range(len(ret)):\n'
        qcvp__mia += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        qcvp__mia += '  ret[na_idxs] = np.nan\n'
    qcvp__mia += '  return ret\n'
    nbz__gimo = {}
    exec(qcvp__mia, {'np': np, 'pd': pd, 'bodo': bodo}, nbz__gimo)
    return nbz__gimo['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    otjo__mri = start
    zqfru__xrier = 2 * start + 1
    qnm__uxswt = 2 * start + 2
    if zqfru__xrier < n and not cmp_f(arr[zqfru__xrier], arr[otjo__mri]):
        otjo__mri = zqfru__xrier
    if qnm__uxswt < n and not cmp_f(arr[qnm__uxswt], arr[otjo__mri]):
        otjo__mri = qnm__uxswt
    if otjo__mri != start:
        arr[start], arr[otjo__mri] = arr[otjo__mri], arr[start]
        ind_arr[start], ind_arr[otjo__mri] = ind_arr[otjo__mri], ind_arr[start]
        min_heapify(arr, ind_arr, n, otjo__mri, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        pgnf__pzoa = np.empty(k, A.dtype)
        rbpsz__vntjr = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                pgnf__pzoa[ind] = A[i]
                rbpsz__vntjr[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            pgnf__pzoa = pgnf__pzoa[:ind]
            rbpsz__vntjr = rbpsz__vntjr[:ind]
        return pgnf__pzoa, rbpsz__vntjr, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        ijxk__isy = np.sort(A)
        cmav__jfps = index_arr[np.argsort(A)]
        zqg__awp = pd.Series(ijxk__isy).notna().values
        ijxk__isy = ijxk__isy[zqg__awp]
        cmav__jfps = cmav__jfps[zqg__awp]
        if is_largest:
            ijxk__isy = ijxk__isy[::-1]
            cmav__jfps = cmav__jfps[::-1]
        return np.ascontiguousarray(ijxk__isy), np.ascontiguousarray(cmav__jfps
            )
    pgnf__pzoa, rbpsz__vntjr, start = select_k_nonan(A, index_arr, m, k)
    rbpsz__vntjr = rbpsz__vntjr[pgnf__pzoa.argsort()]
    pgnf__pzoa.sort()
    if not is_largest:
        pgnf__pzoa = np.ascontiguousarray(pgnf__pzoa[::-1])
        rbpsz__vntjr = np.ascontiguousarray(rbpsz__vntjr[::-1])
    for i in range(start, m):
        if cmp_f(A[i], pgnf__pzoa[0]):
            pgnf__pzoa[0] = A[i]
            rbpsz__vntjr[0] = index_arr[i]
            min_heapify(pgnf__pzoa, rbpsz__vntjr, k, 0, cmp_f)
    rbpsz__vntjr = rbpsz__vntjr[pgnf__pzoa.argsort()]
    pgnf__pzoa.sort()
    if is_largest:
        pgnf__pzoa = pgnf__pzoa[::-1]
        rbpsz__vntjr = rbpsz__vntjr[::-1]
    return np.ascontiguousarray(pgnf__pzoa), np.ascontiguousarray(rbpsz__vntjr)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    yjz__mte = bodo.libs.distributed_api.get_rank()
    achx__fsvmz, amr__lbvb = nlargest(A, I, k, is_largest, cmp_f)
    xaw__xexkc = bodo.libs.distributed_api.gatherv(achx__fsvmz)
    wmlkb__zucbi = bodo.libs.distributed_api.gatherv(amr__lbvb)
    if yjz__mte == MPI_ROOT:
        res, hvyy__swym = nlargest(xaw__xexkc, wmlkb__zucbi, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        hvyy__swym = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(hvyy__swym)
    return res, hvyy__swym


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    gbs__wmys, segc__jmsm = mat.shape
    pbvj__zrzl = np.empty((segc__jmsm, segc__jmsm), dtype=np.float64)
    for brrh__nyaq in range(segc__jmsm):
        for jvsoo__tll in range(brrh__nyaq + 1):
            wuuh__kfb = 0
            uxlpw__rktqt = ettmm__qvz = kho__hsqgk = betn__gno = 0.0
            for i in range(gbs__wmys):
                if np.isfinite(mat[i, brrh__nyaq]) and np.isfinite(mat[i,
                    jvsoo__tll]):
                    gsezc__abjv = mat[i, brrh__nyaq]
                    aaxml__lfhrl = mat[i, jvsoo__tll]
                    wuuh__kfb += 1
                    kho__hsqgk += gsezc__abjv
                    betn__gno += aaxml__lfhrl
            if parallel:
                wuuh__kfb = bodo.libs.distributed_api.dist_reduce(wuuh__kfb,
                    sum_op)
                kho__hsqgk = bodo.libs.distributed_api.dist_reduce(kho__hsqgk,
                    sum_op)
                betn__gno = bodo.libs.distributed_api.dist_reduce(betn__gno,
                    sum_op)
            if wuuh__kfb < minpv:
                pbvj__zrzl[brrh__nyaq, jvsoo__tll] = pbvj__zrzl[jvsoo__tll,
                    brrh__nyaq] = np.nan
            else:
                idsow__tec = kho__hsqgk / wuuh__kfb
                octu__xnpq = betn__gno / wuuh__kfb
                kho__hsqgk = 0.0
                for i in range(gbs__wmys):
                    if np.isfinite(mat[i, brrh__nyaq]) and np.isfinite(mat[
                        i, jvsoo__tll]):
                        gsezc__abjv = mat[i, brrh__nyaq] - idsow__tec
                        aaxml__lfhrl = mat[i, jvsoo__tll] - octu__xnpq
                        kho__hsqgk += gsezc__abjv * aaxml__lfhrl
                        uxlpw__rktqt += gsezc__abjv * gsezc__abjv
                        ettmm__qvz += aaxml__lfhrl * aaxml__lfhrl
                if parallel:
                    kho__hsqgk = bodo.libs.distributed_api.dist_reduce(
                        kho__hsqgk, sum_op)
                    uxlpw__rktqt = bodo.libs.distributed_api.dist_reduce(
                        uxlpw__rktqt, sum_op)
                    ettmm__qvz = bodo.libs.distributed_api.dist_reduce(
                        ettmm__qvz, sum_op)
                aorsy__wzh = wuuh__kfb - 1.0 if cov else sqrt(uxlpw__rktqt *
                    ettmm__qvz)
                if aorsy__wzh != 0.0:
                    pbvj__zrzl[brrh__nyaq, jvsoo__tll] = pbvj__zrzl[
                        jvsoo__tll, brrh__nyaq] = kho__hsqgk / aorsy__wzh
                else:
                    pbvj__zrzl[brrh__nyaq, jvsoo__tll] = pbvj__zrzl[
                        jvsoo__tll, brrh__nyaq] = np.nan
    return pbvj__zrzl


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    qaui__twg = n != 1
    qcvp__mia = 'def impl(data, parallel=False):\n'
    qcvp__mia += '  if parallel:\n'
    djpn__zruz = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    qcvp__mia += f'    cpp_table = arr_info_list_to_table([{djpn__zruz}])\n'
    qcvp__mia += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    qjaxw__oxkrw = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    qcvp__mia += f'    data = ({qjaxw__oxkrw},)\n'
    qcvp__mia += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    qcvp__mia += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    qcvp__mia += '    bodo.libs.array.delete_table(cpp_table)\n'
    qcvp__mia += '  n = len(data[0])\n'
    qcvp__mia += '  out = np.empty(n, np.bool_)\n'
    qcvp__mia += '  uniqs = dict()\n'
    if qaui__twg:
        qcvp__mia += '  for i in range(n):\n'
        stbq__ubm = ', '.join(f'data[{i}][i]' for i in range(n))
        hhto__zsbxo = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        qcvp__mia += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({stbq__ubm},), ({hhto__zsbxo},))
"""
        qcvp__mia += '    if val in uniqs:\n'
        qcvp__mia += '      out[i] = True\n'
        qcvp__mia += '    else:\n'
        qcvp__mia += '      out[i] = False\n'
        qcvp__mia += '      uniqs[val] = 0\n'
    else:
        qcvp__mia += '  data = data[0]\n'
        qcvp__mia += '  hasna = False\n'
        qcvp__mia += '  for i in range(n):\n'
        qcvp__mia += '    if bodo.libs.array_kernels.isna(data, i):\n'
        qcvp__mia += '      out[i] = hasna\n'
        qcvp__mia += '      hasna = True\n'
        qcvp__mia += '    else:\n'
        qcvp__mia += '      val = data[i]\n'
        qcvp__mia += '      if val in uniqs:\n'
        qcvp__mia += '        out[i] = True\n'
        qcvp__mia += '      else:\n'
        qcvp__mia += '        out[i] = False\n'
        qcvp__mia += '        uniqs[val] = 0\n'
    qcvp__mia += '  if parallel:\n'
    qcvp__mia += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    qcvp__mia += '  return out\n'
    nbz__gimo = {}
    exec(qcvp__mia, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, nbz__gimo)
    impl = nbz__gimo['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    mnkb__wlnq = len(data)
    qcvp__mia = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    qcvp__mia += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        mnkb__wlnq)))
    qcvp__mia += '  table_total = arr_info_list_to_table(info_list_total)\n'
    qcvp__mia += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(mnkb__wlnq))
    for tfps__veguk in range(mnkb__wlnq):
        qcvp__mia += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(tfps__veguk, tfps__veguk, tfps__veguk))
    qcvp__mia += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(mnkb__wlnq))
    qcvp__mia += '  delete_table(out_table)\n'
    qcvp__mia += '  delete_table(table_total)\n'
    qcvp__mia += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(mnkb__wlnq)))
    nbz__gimo = {}
    exec(qcvp__mia, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, nbz__gimo)
    impl = nbz__gimo['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    mnkb__wlnq = len(data)
    qcvp__mia = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    qcvp__mia += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        mnkb__wlnq)))
    qcvp__mia += '  table_total = arr_info_list_to_table(info_list_total)\n'
    qcvp__mia += '  keep_i = 0\n'
    qcvp__mia += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for tfps__veguk in range(mnkb__wlnq):
        qcvp__mia += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(tfps__veguk, tfps__veguk, tfps__veguk))
    qcvp__mia += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(mnkb__wlnq))
    qcvp__mia += '  delete_table(out_table)\n'
    qcvp__mia += '  delete_table(table_total)\n'
    qcvp__mia += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(mnkb__wlnq)))
    nbz__gimo = {}
    exec(qcvp__mia, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, nbz__gimo)
    impl = nbz__gimo['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        hzt__meoqj = [array_to_info(data_arr)]
        gbow__hizlo = arr_info_list_to_table(hzt__meoqj)
        ihh__tgq = 0
        fka__scgom = drop_duplicates_table(gbow__hizlo, parallel, 1,
            ihh__tgq, False, True)
        ipr__uocug = info_to_array(info_from_table(fka__scgom, 0), data_arr)
        delete_table(fka__scgom)
        delete_table(gbow__hizlo)
        return ipr__uocug
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    ctuvn__lvcu = len(data.types)
    ajb__ezzyd = [('out' + str(i)) for i in range(ctuvn__lvcu)]
    yvui__rgm = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    cyrqu__nfnyz = ['isna(data[{}], i)'.format(i) for i in yvui__rgm]
    hvmis__avsc = 'not ({})'.format(' or '.join(cyrqu__nfnyz))
    if not is_overload_none(thresh):
        hvmis__avsc = '(({}) <= ({}) - thresh)'.format(' + '.join(
            cyrqu__nfnyz), ctuvn__lvcu - 1)
    elif how == 'all':
        hvmis__avsc = 'not ({})'.format(' and '.join(cyrqu__nfnyz))
    qcvp__mia = 'def _dropna_imp(data, how, thresh, subset):\n'
    qcvp__mia += '  old_len = len(data[0])\n'
    qcvp__mia += '  new_len = 0\n'
    qcvp__mia += '  for i in range(old_len):\n'
    qcvp__mia += '    if {}:\n'.format(hvmis__avsc)
    qcvp__mia += '      new_len += 1\n'
    for i, out in enumerate(ajb__ezzyd):
        if isinstance(data[i], bodo.CategoricalArrayType):
            qcvp__mia += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            qcvp__mia += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    qcvp__mia += '  curr_ind = 0\n'
    qcvp__mia += '  for i in range(old_len):\n'
    qcvp__mia += '    if {}:\n'.format(hvmis__avsc)
    for i in range(ctuvn__lvcu):
        qcvp__mia += '      if isna(data[{}], i):\n'.format(i)
        qcvp__mia += '        setna({}, curr_ind)\n'.format(ajb__ezzyd[i])
        qcvp__mia += '      else:\n'
        qcvp__mia += '        {}[curr_ind] = data[{}][i]\n'.format(ajb__ezzyd
            [i], i)
    qcvp__mia += '      curr_ind += 1\n'
    qcvp__mia += '  return {}\n'.format(', '.join(ajb__ezzyd))
    nbz__gimo = {}
    qma__nlzkk = {'t{}'.format(i): ptov__dpow for i, ptov__dpow in
        enumerate(data.types)}
    qma__nlzkk.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(qcvp__mia, qma__nlzkk, nbz__gimo)
    tzfoc__hqd = nbz__gimo['_dropna_imp']
    return tzfoc__hqd


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        qhtet__rvdx = arr.dtype
        jzlcz__uopzj = qhtet__rvdx.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            woe__ekh = init_nested_counts(jzlcz__uopzj)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                woe__ekh = add_nested_counts(woe__ekh, val[ind])
            ipr__uocug = bodo.utils.utils.alloc_type(n, qhtet__rvdx, woe__ekh)
            for lykgl__hrg in range(n):
                if bodo.libs.array_kernels.isna(arr, lykgl__hrg):
                    setna(ipr__uocug, lykgl__hrg)
                    continue
                val = arr[lykgl__hrg]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(ipr__uocug, lykgl__hrg)
                    continue
                ipr__uocug[lykgl__hrg] = val[ind]
            return ipr__uocug
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    bytc__yfifb = _to_readonly(arr_types.types[0])
    return all(isinstance(ptov__dpow, CategoricalArrayType) and 
        _to_readonly(ptov__dpow) == bytc__yfifb for ptov__dpow in arr_types
        .types)


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
        rprq__deae = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            pjiie__fnl = 0
            pxw__icr = []
            for A in arr_list:
                qpot__ygezj = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                pxw__icr.append(bodo.libs.array_item_arr_ext.get_data(A))
                pjiie__fnl += qpot__ygezj
            znpa__uqou = np.empty(pjiie__fnl + 1, offset_type)
            rilb__fzk = bodo.libs.array_kernels.concat(pxw__icr)
            cljn__tbd = np.empty(pjiie__fnl + 7 >> 3, np.uint8)
            uuyk__rlpf = 0
            oex__wgsob = 0
            for A in arr_list:
                btbvp__hqsf = bodo.libs.array_item_arr_ext.get_offsets(A)
                hojv__yban = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                qpot__ygezj = len(A)
                iatot__zqpo = btbvp__hqsf[qpot__ygezj]
                for i in range(qpot__ygezj):
                    znpa__uqou[i + uuyk__rlpf] = btbvp__hqsf[i] + oex__wgsob
                    vvv__eoqbq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        hojv__yban, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cljn__tbd, i +
                        uuyk__rlpf, vvv__eoqbq)
                uuyk__rlpf += qpot__ygezj
                oex__wgsob += iatot__zqpo
            znpa__uqou[uuyk__rlpf] = oex__wgsob
            ipr__uocug = bodo.libs.array_item_arr_ext.init_array_item_array(
                pjiie__fnl, rilb__fzk, znpa__uqou, cljn__tbd)
            return ipr__uocug
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        drag__onp = arr_list.dtype.names
        qcvp__mia = 'def struct_array_concat_impl(arr_list):\n'
        qcvp__mia += f'    n_all = 0\n'
        for i in range(len(drag__onp)):
            qcvp__mia += f'    concat_list{i} = []\n'
        qcvp__mia += '    for A in arr_list:\n'
        qcvp__mia += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(drag__onp)):
            qcvp__mia += f'        concat_list{i}.append(data_tuple[{i}])\n'
        qcvp__mia += '        n_all += len(A)\n'
        qcvp__mia += '    n_bytes = (n_all + 7) >> 3\n'
        qcvp__mia += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        qcvp__mia += '    curr_bit = 0\n'
        qcvp__mia += '    for A in arr_list:\n'
        qcvp__mia += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        qcvp__mia += '        for j in range(len(A)):\n'
        qcvp__mia += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        qcvp__mia += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        qcvp__mia += '            curr_bit += 1\n'
        qcvp__mia += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        qxadq__sqzwq = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(drag__onp))])
        qcvp__mia += f'        ({qxadq__sqzwq},),\n'
        qcvp__mia += '        new_mask,\n'
        qcvp__mia += f'        {drag__onp},\n'
        qcvp__mia += '    )\n'
        nbz__gimo = {}
        exec(qcvp__mia, {'bodo': bodo, 'np': np}, nbz__gimo)
        return nbz__gimo['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            wrxao__hasyf = 0
            for A in arr_list:
                wrxao__hasyf += len(A)
            mvr__nrkhz = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(wrxao__hasyf))
            pjzp__fdcbp = 0
            for A in arr_list:
                for i in range(len(A)):
                    mvr__nrkhz._data[i + pjzp__fdcbp] = A._data[i]
                    vvv__eoqbq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mvr__nrkhz.
                        _null_bitmap, i + pjzp__fdcbp, vvv__eoqbq)
                pjzp__fdcbp += len(A)
            return mvr__nrkhz
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            wrxao__hasyf = 0
            for A in arr_list:
                wrxao__hasyf += len(A)
            mvr__nrkhz = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(wrxao__hasyf))
            pjzp__fdcbp = 0
            for A in arr_list:
                for i in range(len(A)):
                    mvr__nrkhz._days_data[i + pjzp__fdcbp] = A._days_data[i]
                    mvr__nrkhz._seconds_data[i + pjzp__fdcbp
                        ] = A._seconds_data[i]
                    mvr__nrkhz._microseconds_data[i + pjzp__fdcbp
                        ] = A._microseconds_data[i]
                    vvv__eoqbq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mvr__nrkhz.
                        _null_bitmap, i + pjzp__fdcbp, vvv__eoqbq)
                pjzp__fdcbp += len(A)
            return mvr__nrkhz
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        xrt__njjhq = arr_list.dtype.precision
        rwyz__zus = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            wrxao__hasyf = 0
            for A in arr_list:
                wrxao__hasyf += len(A)
            mvr__nrkhz = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                wrxao__hasyf, xrt__njjhq, rwyz__zus)
            pjzp__fdcbp = 0
            for A in arr_list:
                for i in range(len(A)):
                    mvr__nrkhz._data[i + pjzp__fdcbp] = A._data[i]
                    vvv__eoqbq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mvr__nrkhz.
                        _null_bitmap, i + pjzp__fdcbp, vvv__eoqbq)
                pjzp__fdcbp += len(A)
            return mvr__nrkhz
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        ptov__dpow) for ptov__dpow in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            gdrfg__oblw = arr_list.types[0]
        else:
            gdrfg__oblw = arr_list.dtype
        gdrfg__oblw = to_str_arr_if_dict_array(gdrfg__oblw)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            drs__zwsw = 0
            udy__tfpen = 0
            for A in arr_list:
                arr = A
                drs__zwsw += len(arr)
                udy__tfpen += bodo.libs.str_arr_ext.num_total_chars(arr)
            ipr__uocug = bodo.utils.utils.alloc_type(drs__zwsw, gdrfg__oblw,
                (udy__tfpen,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(ipr__uocug, -1)
            tkd__tioyv = 0
            pfoy__twk = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(ipr__uocug,
                    arr, tkd__tioyv, pfoy__twk)
                tkd__tioyv += len(arr)
                pfoy__twk += bodo.libs.str_arr_ext.num_total_chars(arr)
            return ipr__uocug
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(ptov__dpow.dtype, types.Integer) for
        ptov__dpow in arr_list.types) and any(isinstance(ptov__dpow,
        IntegerArrayType) for ptov__dpow in arr_list.types):

        def impl_int_arr_list(arr_list):
            hojzp__rfs = convert_to_nullable_tup(arr_list)
            nvah__awkj = []
            tqmv__mydss = 0
            for A in hojzp__rfs:
                nvah__awkj.append(A._data)
                tqmv__mydss += len(A)
            rilb__fzk = bodo.libs.array_kernels.concat(nvah__awkj)
            gsh__xacg = tqmv__mydss + 7 >> 3
            jlagl__zpv = np.empty(gsh__xacg, np.uint8)
            hto__zrpw = 0
            for A in hojzp__rfs:
                ssw__ffcof = A._null_bitmap
                for lykgl__hrg in range(len(A)):
                    vvv__eoqbq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ssw__ffcof, lykgl__hrg)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jlagl__zpv,
                        hto__zrpw, vvv__eoqbq)
                    hto__zrpw += 1
            return bodo.libs.int_arr_ext.init_integer_array(rilb__fzk,
                jlagl__zpv)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(ptov__dpow.dtype == types.bool_ for ptov__dpow in
        arr_list.types) and any(ptov__dpow == boolean_array for ptov__dpow in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            hojzp__rfs = convert_to_nullable_tup(arr_list)
            nvah__awkj = []
            tqmv__mydss = 0
            for A in hojzp__rfs:
                nvah__awkj.append(A._data)
                tqmv__mydss += len(A)
            rilb__fzk = bodo.libs.array_kernels.concat(nvah__awkj)
            gsh__xacg = tqmv__mydss + 7 >> 3
            jlagl__zpv = np.empty(gsh__xacg, np.uint8)
            hto__zrpw = 0
            for A in hojzp__rfs:
                ssw__ffcof = A._null_bitmap
                for lykgl__hrg in range(len(A)):
                    vvv__eoqbq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ssw__ffcof, lykgl__hrg)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jlagl__zpv,
                        hto__zrpw, vvv__eoqbq)
                    hto__zrpw += 1
            return bodo.libs.bool_arr_ext.init_bool_array(rilb__fzk, jlagl__zpv
                )
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            fvb__hpoj = []
            for A in arr_list:
                fvb__hpoj.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                fvb__hpoj), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        qqh__xqnl = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        qcvp__mia = 'def impl(arr_list):\n'
        qcvp__mia += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({qqh__xqnl},)), arr_list[0].dtype)
"""
        almdw__vbb = {}
        exec(qcvp__mia, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, almdw__vbb)
        return almdw__vbb['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            tqmv__mydss = 0
            for A in arr_list:
                tqmv__mydss += len(A)
            ipr__uocug = np.empty(tqmv__mydss, dtype)
            ttx__bjwek = 0
            for A in arr_list:
                n = len(A)
                ipr__uocug[ttx__bjwek:ttx__bjwek + n] = A
                ttx__bjwek += n
            return ipr__uocug
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(ptov__dpow,
        (types.Array, IntegerArrayType)) and isinstance(ptov__dpow.dtype,
        types.Integer) for ptov__dpow in arr_list.types) and any(isinstance
        (ptov__dpow, types.Array) and isinstance(ptov__dpow.dtype, types.
        Float) for ptov__dpow in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            hqakc__eadv = []
            for A in arr_list:
                hqakc__eadv.append(A._data)
            xnoei__acjv = bodo.libs.array_kernels.concat(hqakc__eadv)
            pbvj__zrzl = bodo.libs.map_arr_ext.init_map_arr(xnoei__acjv)
            return pbvj__zrzl
        return impl_map_arr_list
    for xngd__hvru in arr_list:
        if not isinstance(xngd__hvru, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(ptov__dpow.astype(np.float64) for ptov__dpow in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    mnkb__wlnq = len(arr_tup.types)
    qcvp__mia = 'def f(arr_tup):\n'
    qcvp__mia += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        mnkb__wlnq)), ',' if mnkb__wlnq == 1 else '')
    nbz__gimo = {}
    exec(qcvp__mia, {'np': np}, nbz__gimo)
    dyq__peqj = nbz__gimo['f']
    return dyq__peqj


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    mnkb__wlnq = len(arr_tup.types)
    yghlo__ckl = find_common_np_dtype(arr_tup.types)
    jzlcz__uopzj = None
    wkqm__pmvhk = ''
    if isinstance(yghlo__ckl, types.Integer):
        jzlcz__uopzj = bodo.libs.int_arr_ext.IntDtype(yghlo__ckl)
        wkqm__pmvhk = '.astype(out_dtype, False)'
    qcvp__mia = 'def f(arr_tup):\n'
    qcvp__mia += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, wkqm__pmvhk) for i in range(mnkb__wlnq)), ',' if 
        mnkb__wlnq == 1 else '')
    nbz__gimo = {}
    exec(qcvp__mia, {'bodo': bodo, 'out_dtype': jzlcz__uopzj}, nbz__gimo)
    qgv__xymfo = nbz__gimo['f']
    return qgv__xymfo


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, vjjq__nsd = build_set_seen_na(A)
        return len(s) + int(not dropna and vjjq__nsd)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        tqvjz__nmc = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        hhy__rct = len(tqvjz__nmc)
        return bodo.libs.distributed_api.dist_reduce(hhy__rct, np.int32(sum_op)
            )
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([yyynb__djng for yyynb__djng in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        kbyyo__wxazg = np.finfo(A.dtype(1).dtype).max
    else:
        kbyyo__wxazg = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        ipr__uocug = np.empty(n, A.dtype)
        mngf__rmoy = kbyyo__wxazg
        for i in range(n):
            mngf__rmoy = min(mngf__rmoy, A[i])
            ipr__uocug[i] = mngf__rmoy
        return ipr__uocug
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        kbyyo__wxazg = np.finfo(A.dtype(1).dtype).min
    else:
        kbyyo__wxazg = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        ipr__uocug = np.empty(n, A.dtype)
        mngf__rmoy = kbyyo__wxazg
        for i in range(n):
            mngf__rmoy = max(mngf__rmoy, A[i])
            ipr__uocug[i] = mngf__rmoy
        return ipr__uocug
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        pje__vdv = arr_info_list_to_table([array_to_info(A)])
        nipdv__ovwr = 1
        ihh__tgq = 0
        fka__scgom = drop_duplicates_table(pje__vdv, parallel, nipdv__ovwr,
            ihh__tgq, dropna, True)
        ipr__uocug = info_to_array(info_from_table(fka__scgom, 0), A)
        delete_table(pje__vdv)
        delete_table(fka__scgom)
        return ipr__uocug
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    rprq__deae = bodo.utils.typing.to_nullable_type(arr.dtype)
    dzekq__lluc = index_arr
    zvwnj__ayp = dzekq__lluc.dtype

    def impl(arr, index_arr):
        n = len(arr)
        woe__ekh = init_nested_counts(rprq__deae)
        qtn__idbc = init_nested_counts(zvwnj__ayp)
        for i in range(n):
            iqg__aiau = index_arr[i]
            if isna(arr, i):
                woe__ekh = (woe__ekh[0] + 1,) + woe__ekh[1:]
                qtn__idbc = add_nested_counts(qtn__idbc, iqg__aiau)
                continue
            nom__npp = arr[i]
            if len(nom__npp) == 0:
                woe__ekh = (woe__ekh[0] + 1,) + woe__ekh[1:]
                qtn__idbc = add_nested_counts(qtn__idbc, iqg__aiau)
                continue
            woe__ekh = add_nested_counts(woe__ekh, nom__npp)
            for ldy__hrbci in range(len(nom__npp)):
                qtn__idbc = add_nested_counts(qtn__idbc, iqg__aiau)
        ipr__uocug = bodo.utils.utils.alloc_type(woe__ekh[0], rprq__deae,
            woe__ekh[1:])
        lrkda__raqkn = bodo.utils.utils.alloc_type(woe__ekh[0], dzekq__lluc,
            qtn__idbc)
        oex__wgsob = 0
        for i in range(n):
            if isna(arr, i):
                setna(ipr__uocug, oex__wgsob)
                lrkda__raqkn[oex__wgsob] = index_arr[i]
                oex__wgsob += 1
                continue
            nom__npp = arr[i]
            iatot__zqpo = len(nom__npp)
            if iatot__zqpo == 0:
                setna(ipr__uocug, oex__wgsob)
                lrkda__raqkn[oex__wgsob] = index_arr[i]
                oex__wgsob += 1
                continue
            ipr__uocug[oex__wgsob:oex__wgsob + iatot__zqpo] = nom__npp
            lrkda__raqkn[oex__wgsob:oex__wgsob + iatot__zqpo] = index_arr[i]
            oex__wgsob += iatot__zqpo
        return ipr__uocug, lrkda__raqkn
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    rprq__deae = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        woe__ekh = init_nested_counts(rprq__deae)
        for i in range(n):
            if isna(arr, i):
                woe__ekh = (woe__ekh[0] + 1,) + woe__ekh[1:]
                xpg__wghb = 1
            else:
                nom__npp = arr[i]
                cns__xhsl = len(nom__npp)
                if cns__xhsl == 0:
                    woe__ekh = (woe__ekh[0] + 1,) + woe__ekh[1:]
                    xpg__wghb = 1
                    continue
                else:
                    woe__ekh = add_nested_counts(woe__ekh, nom__npp)
                    xpg__wghb = cns__xhsl
            if counts[i] != xpg__wghb:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        ipr__uocug = bodo.utils.utils.alloc_type(woe__ekh[0], rprq__deae,
            woe__ekh[1:])
        oex__wgsob = 0
        for i in range(n):
            if isna(arr, i):
                setna(ipr__uocug, oex__wgsob)
                oex__wgsob += 1
                continue
            nom__npp = arr[i]
            iatot__zqpo = len(nom__npp)
            if iatot__zqpo == 0:
                setna(ipr__uocug, oex__wgsob)
                oex__wgsob += 1
                continue
            ipr__uocug[oex__wgsob:oex__wgsob + iatot__zqpo] = nom__npp
            oex__wgsob += iatot__zqpo
        return ipr__uocug
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(jmv__ytujz) for jmv__ytujz in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        dte__hxg = 'np.empty(n, np.int64)'
        egc__caco = 'out_arr[i] = 1'
        cjhm__rrl = 'max(len(arr[i]), 1)'
    else:
        dte__hxg = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        egc__caco = 'bodo.libs.array_kernels.setna(out_arr, i)'
        cjhm__rrl = 'len(arr[i])'
    qcvp__mia = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {dte__hxg}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {egc__caco}
        else:
            out_arr[i] = {cjhm__rrl}
    return out_arr
    """
    nbz__gimo = {}
    exec(qcvp__mia, {'bodo': bodo, 'numba': numba, 'np': np}, nbz__gimo)
    impl = nbz__gimo['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    dzekq__lluc = index_arr
    zvwnj__ayp = dzekq__lluc.dtype

    def impl(arr, pat, n, index_arr):
        udte__ywneh = pat is not None and len(pat) > 1
        if udte__ywneh:
            qakj__aykpi = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        sal__dvqtq = len(arr)
        drs__zwsw = 0
        udy__tfpen = 0
        qtn__idbc = init_nested_counts(zvwnj__ayp)
        for i in range(sal__dvqtq):
            iqg__aiau = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                drs__zwsw += 1
                qtn__idbc = add_nested_counts(qtn__idbc, iqg__aiau)
                continue
            if udte__ywneh:
                cinqq__tsmfw = qakj__aykpi.split(arr[i], maxsplit=n)
            else:
                cinqq__tsmfw = arr[i].split(pat, n)
            drs__zwsw += len(cinqq__tsmfw)
            for s in cinqq__tsmfw:
                qtn__idbc = add_nested_counts(qtn__idbc, iqg__aiau)
                udy__tfpen += bodo.libs.str_arr_ext.get_utf8_size(s)
        ipr__uocug = bodo.libs.str_arr_ext.pre_alloc_string_array(drs__zwsw,
            udy__tfpen)
        lrkda__raqkn = bodo.utils.utils.alloc_type(drs__zwsw, dzekq__lluc,
            qtn__idbc)
        nskvz__nzt = 0
        for lykgl__hrg in range(sal__dvqtq):
            if isna(arr, lykgl__hrg):
                ipr__uocug[nskvz__nzt] = ''
                bodo.libs.array_kernels.setna(ipr__uocug, nskvz__nzt)
                lrkda__raqkn[nskvz__nzt] = index_arr[lykgl__hrg]
                nskvz__nzt += 1
                continue
            if udte__ywneh:
                cinqq__tsmfw = qakj__aykpi.split(arr[lykgl__hrg], maxsplit=n)
            else:
                cinqq__tsmfw = arr[lykgl__hrg].split(pat, n)
            xwcmn__bdp = len(cinqq__tsmfw)
            ipr__uocug[nskvz__nzt:nskvz__nzt + xwcmn__bdp] = cinqq__tsmfw
            lrkda__raqkn[nskvz__nzt:nskvz__nzt + xwcmn__bdp] = index_arr[
                lykgl__hrg]
            nskvz__nzt += xwcmn__bdp
        return ipr__uocug, lrkda__raqkn
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
            ipr__uocug = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                ipr__uocug[i] = np.nan
            return ipr__uocug
        return impl_float
    ivhqq__dngx = to_str_arr_if_dict_array(arr)

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        ipr__uocug = bodo.utils.utils.alloc_type(n, ivhqq__dngx, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(ipr__uocug, i)
        return ipr__uocug
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
    yhl__llxyw = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            ipr__uocug = bodo.utils.utils.alloc_type(new_len, yhl__llxyw)
            bodo.libs.str_arr_ext.str_copy_ptr(ipr__uocug.ctypes, 0, A.
                ctypes, old_size)
            return ipr__uocug
        return impl_char

    def impl(A, old_size, new_len):
        ipr__uocug = bodo.utils.utils.alloc_type(new_len, yhl__llxyw, (-1,))
        ipr__uocug[:old_size] = A[:old_size]
        return ipr__uocug
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    lidqi__wcxv = math.ceil((stop - start) / step)
    return int(max(lidqi__wcxv, 0))


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
    if any(isinstance(yyynb__djng, types.Complex) for yyynb__djng in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            rti__zis = (stop - start) / step
            lidqi__wcxv = math.ceil(rti__zis.real)
            zfyzt__lpu = math.ceil(rti__zis.imag)
            dliai__ahw = int(max(min(zfyzt__lpu, lidqi__wcxv), 0))
            arr = np.empty(dliai__ahw, dtype)
            for i in numba.parfors.parfor.internal_prange(dliai__ahw):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            dliai__ahw = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(dliai__ahw, dtype)
            for i in numba.parfors.parfor.internal_prange(dliai__ahw):
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
        qgn__oexd = arr,
        if not inplace:
            qgn__oexd = arr.copy(),
        vbuc__fpu = bodo.libs.str_arr_ext.to_list_if_immutable_arr(qgn__oexd)
        hlrzf__eon = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(vbuc__fpu, 0, n, hlrzf__eon)
        if not ascending:
            bodo.libs.timsort.reverseRange(vbuc__fpu, 0, n, hlrzf__eon)
        bodo.libs.str_arr_ext.cp_str_list_to_array(qgn__oexd, vbuc__fpu)
        return qgn__oexd[0]
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
        pbvj__zrzl = []
        for i in range(n):
            if A[i]:
                pbvj__zrzl.append(i + offset)
        return np.array(pbvj__zrzl, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    yhl__llxyw = element_type(A)
    if yhl__llxyw == types.unicode_type:
        null_value = '""'
    elif yhl__llxyw == types.bool_:
        null_value = 'False'
    elif yhl__llxyw == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif yhl__llxyw == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    nskvz__nzt = 'i'
    cuz__uobk = False
    qwswx__gtiq = get_overload_const_str(method)
    if qwswx__gtiq in ('ffill', 'pad'):
        lkm__buv = 'n'
        send_right = True
    elif qwswx__gtiq in ('backfill', 'bfill'):
        lkm__buv = 'n-1, -1, -1'
        send_right = False
        if yhl__llxyw == types.unicode_type:
            nskvz__nzt = '(n - 1) - i'
            cuz__uobk = True
    qcvp__mia = 'def impl(A, method, parallel=False):\n'
    qcvp__mia += '  A = decode_if_dict_array(A)\n'
    qcvp__mia += '  has_last_value = False\n'
    qcvp__mia += f'  last_value = {null_value}\n'
    qcvp__mia += '  if parallel:\n'
    qcvp__mia += '    rank = bodo.libs.distributed_api.get_rank()\n'
    qcvp__mia += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    qcvp__mia += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    qcvp__mia += '  n = len(A)\n'
    qcvp__mia += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    qcvp__mia += f'  for i in range({lkm__buv}):\n'
    qcvp__mia += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    qcvp__mia += (
        f'      bodo.libs.array_kernels.setna(out_arr, {nskvz__nzt})\n')
    qcvp__mia += '      continue\n'
    qcvp__mia += '    s = A[i]\n'
    qcvp__mia += '    if bodo.libs.array_kernels.isna(A, i):\n'
    qcvp__mia += '      s = last_value\n'
    qcvp__mia += f'    out_arr[{nskvz__nzt}] = s\n'
    qcvp__mia += '    last_value = s\n'
    qcvp__mia += '    has_last_value = True\n'
    if cuz__uobk:
        qcvp__mia += '  return out_arr[::-1]\n'
    else:
        qcvp__mia += '  return out_arr\n'
    kktuj__biyok = {}
    exec(qcvp__mia, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, kktuj__biyok)
    impl = kktuj__biyok['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        vidr__hanp = 0
        mhrls__oyohb = n_pes - 1
        xckq__qpcc = np.int32(rank + 1)
        tmuvo__oxze = np.int32(rank - 1)
        olgb__rgueh = len(in_arr) - 1
        uwdg__qdwh = -1
        zfl__tzb = -1
    else:
        vidr__hanp = n_pes - 1
        mhrls__oyohb = 0
        xckq__qpcc = np.int32(rank - 1)
        tmuvo__oxze = np.int32(rank + 1)
        olgb__rgueh = 0
        uwdg__qdwh = len(in_arr)
        zfl__tzb = 1
    qlj__fdf = np.int32(bodo.hiframes.rolling.comm_border_tag)
    tin__slboq = np.empty(1, dtype=np.bool_)
    lwc__xkacw = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    olodh__xft = np.empty(1, dtype=np.bool_)
    vrg__lrau = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    qcbqk__iufvw = False
    gfc__sgfzo = null_value
    for i in range(olgb__rgueh, uwdg__qdwh, zfl__tzb):
        if not isna(in_arr, i):
            qcbqk__iufvw = True
            gfc__sgfzo = in_arr[i]
            break
    if rank != vidr__hanp:
        mgu__jnobj = bodo.libs.distributed_api.irecv(tin__slboq, 1,
            tmuvo__oxze, qlj__fdf, True)
        bodo.libs.distributed_api.wait(mgu__jnobj, True)
        rfvzg__oora = bodo.libs.distributed_api.irecv(lwc__xkacw, 1,
            tmuvo__oxze, qlj__fdf, True)
        bodo.libs.distributed_api.wait(rfvzg__oora, True)
        grdh__ujyg = tin__slboq[0]
        wzkqm__cau = lwc__xkacw[0]
    else:
        grdh__ujyg = False
        wzkqm__cau = null_value
    if qcbqk__iufvw:
        olodh__xft[0] = qcbqk__iufvw
        vrg__lrau[0] = gfc__sgfzo
    else:
        olodh__xft[0] = grdh__ujyg
        vrg__lrau[0] = wzkqm__cau
    if rank != mhrls__oyohb:
        ksvor__gvrof = bodo.libs.distributed_api.isend(olodh__xft, 1,
            xckq__qpcc, qlj__fdf, True)
        oyw__xvmc = bodo.libs.distributed_api.isend(vrg__lrau, 1,
            xckq__qpcc, qlj__fdf, True)
    return grdh__ujyg, wzkqm__cau


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    qayv__aacp = {'axis': axis, 'kind': kind, 'order': order}
    tlpab__dpl = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', qayv__aacp, tlpab__dpl, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    yhl__llxyw = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            sal__dvqtq = len(A)
            ipr__uocug = bodo.utils.utils.alloc_type(sal__dvqtq * repeats,
                yhl__llxyw, (-1,))
            for i in range(sal__dvqtq):
                nskvz__nzt = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for lykgl__hrg in range(repeats):
                        bodo.libs.array_kernels.setna(ipr__uocug, 
                            nskvz__nzt + lykgl__hrg)
                else:
                    ipr__uocug[nskvz__nzt:nskvz__nzt + repeats] = A[i]
            return ipr__uocug
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        sal__dvqtq = len(A)
        ipr__uocug = bodo.utils.utils.alloc_type(repeats.sum(), yhl__llxyw,
            (-1,))
        nskvz__nzt = 0
        for i in range(sal__dvqtq):
            ovtw__rib = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for lykgl__hrg in range(ovtw__rib):
                    bodo.libs.array_kernels.setna(ipr__uocug, nskvz__nzt +
                        lykgl__hrg)
            else:
                ipr__uocug[nskvz__nzt:nskvz__nzt + ovtw__rib] = A[i]
            nskvz__nzt += ovtw__rib
        return ipr__uocug
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
        gzhi__uku = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(gzhi__uku, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        ceek__kbna = bodo.libs.array_kernels.concat([A1, A2])
        xrm__wty = bodo.libs.array_kernels.unique(ceek__kbna)
        return pd.Series(xrm__wty).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    qayv__aacp = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    tlpab__dpl = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', qayv__aacp, tlpab__dpl, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        tmgc__wcuuj = bodo.libs.array_kernels.unique(A1)
        xsrxa__uumt = bodo.libs.array_kernels.unique(A2)
        ceek__kbna = bodo.libs.array_kernels.concat([tmgc__wcuuj, xsrxa__uumt])
        qmcdl__suf = pd.Series(ceek__kbna).sort_values().values
        return slice_array_intersect1d(qmcdl__suf)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    zqg__awp = arr[1:] == arr[:-1]
    return arr[:-1][zqg__awp]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    qlj__fdf = np.int32(bodo.hiframes.rolling.comm_border_tag)
    zbdpa__lwy = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        heej__quc = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), qlj__fdf, True)
        bodo.libs.distributed_api.wait(heej__quc, True)
    if rank == n_pes - 1:
        return None
    else:
        vjwzp__iausu = bodo.libs.distributed_api.irecv(zbdpa__lwy, 1, np.
            int32(rank + 1), qlj__fdf, True)
        bodo.libs.distributed_api.wait(vjwzp__iausu, True)
        return zbdpa__lwy[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    zqg__awp = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            zqg__awp[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        sfe__ewcgq = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == sfe__ewcgq:
            zqg__awp[n - 1] = True
    return zqg__awp


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    qayv__aacp = {'assume_unique': assume_unique}
    tlpab__dpl = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', qayv__aacp, tlpab__dpl, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        tmgc__wcuuj = bodo.libs.array_kernels.unique(A1)
        xsrxa__uumt = bodo.libs.array_kernels.unique(A2)
        zqg__awp = calculate_mask_setdiff1d(tmgc__wcuuj, xsrxa__uumt)
        return pd.Series(tmgc__wcuuj[zqg__awp]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    zqg__awp = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        zqg__awp &= A1 != A2[i]
    return zqg__awp


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    qayv__aacp = {'retstep': retstep, 'axis': axis}
    tlpab__dpl = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', qayv__aacp, tlpab__dpl, 'numpy')
    vjrsy__dmsb = False
    if is_overload_none(dtype):
        yhl__llxyw = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            vjrsy__dmsb = True
        yhl__llxyw = numba.np.numpy_support.as_dtype(dtype).type
    if vjrsy__dmsb:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            crbh__giain = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            ipr__uocug = np.empty(num, yhl__llxyw)
            for i in numba.parfors.parfor.internal_prange(num):
                ipr__uocug[i] = yhl__llxyw(np.floor(start + i * crbh__giain))
            return ipr__uocug
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            crbh__giain = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            ipr__uocug = np.empty(num, yhl__llxyw)
            for i in numba.parfors.parfor.internal_prange(num):
                ipr__uocug[i] = yhl__llxyw(start + i * crbh__giain)
            return ipr__uocug
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
        mnkb__wlnq = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                mnkb__wlnq += A[i] == val
        return mnkb__wlnq > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    qayv__aacp = {'axis': axis, 'out': out, 'keepdims': keepdims}
    tlpab__dpl = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', qayv__aacp, tlpab__dpl, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        mnkb__wlnq = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                mnkb__wlnq += int(bool(A[i]))
        return mnkb__wlnq > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    qayv__aacp = {'axis': axis, 'out': out, 'keepdims': keepdims}
    tlpab__dpl = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', qayv__aacp, tlpab__dpl, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        mnkb__wlnq = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                mnkb__wlnq += int(bool(A[i]))
        return mnkb__wlnq == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    qayv__aacp = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    tlpab__dpl = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', qayv__aacp, tlpab__dpl, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        iduv__kqu = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            ipr__uocug = np.empty(n, iduv__kqu)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(ipr__uocug, i)
                    continue
                ipr__uocug[i] = np_cbrt_scalar(A[i], iduv__kqu)
            return ipr__uocug
        return impl_arr
    iduv__kqu = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, iduv__kqu)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    crdny__cgc = x < 0
    if crdny__cgc:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if crdny__cgc:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    bphb__mqui = isinstance(tup, (types.BaseTuple, types.List))
    oepv__cffla = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for xngd__hvru in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                xngd__hvru, 'numpy.hstack()')
            bphb__mqui = bphb__mqui and bodo.utils.utils.is_array_typ(
                xngd__hvru, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        bphb__mqui = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif oepv__cffla:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        ule__eagn = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for xngd__hvru in ule__eagn.types:
            oepv__cffla = oepv__cffla and bodo.utils.utils.is_array_typ(
                xngd__hvru, False)
    if not (bphb__mqui or oepv__cffla):
        return
    if oepv__cffla:

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
    qayv__aacp = {'check_valid': check_valid, 'tol': tol}
    tlpab__dpl = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', qayv__aacp,
        tlpab__dpl, 'numpy')
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
        gbs__wmys = mean.shape[0]
        pdg__rvxf = size, gbs__wmys
        byy__jyq = np.random.standard_normal(pdg__rvxf)
        cov = cov.astype(np.float64)
        joubf__obh, s, unpa__mnvf = np.linalg.svd(cov)
        res = np.dot(byy__jyq, np.sqrt(s).reshape(gbs__wmys, 1) * unpa__mnvf)
        epso__gofz = res + mean
        return epso__gofz
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
            wdczh__dmls = bodo.hiframes.series_kernels._get_type_max_value(arr)
            yesgj__fyjcc = typing.builtins.IndexValue(-1, wdczh__dmls)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                gcgp__ggvsa = typing.builtins.IndexValue(i, arr[i])
                yesgj__fyjcc = min(yesgj__fyjcc, gcgp__ggvsa)
            return yesgj__fyjcc.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        zclbt__jyl = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            qhczb__bkisv = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            wdczh__dmls = zclbt__jyl(len(arr.dtype.categories) + 1)
            yesgj__fyjcc = typing.builtins.IndexValue(-1, wdczh__dmls)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                gcgp__ggvsa = typing.builtins.IndexValue(i, qhczb__bkisv[i])
                yesgj__fyjcc = min(yesgj__fyjcc, gcgp__ggvsa)
            return yesgj__fyjcc.index
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
            wdczh__dmls = bodo.hiframes.series_kernels._get_type_min_value(arr)
            yesgj__fyjcc = typing.builtins.IndexValue(-1, wdczh__dmls)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                gcgp__ggvsa = typing.builtins.IndexValue(i, arr[i])
                yesgj__fyjcc = max(yesgj__fyjcc, gcgp__ggvsa)
            return yesgj__fyjcc.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        zclbt__jyl = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            qhczb__bkisv = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            wdczh__dmls = zclbt__jyl(-1)
            yesgj__fyjcc = typing.builtins.IndexValue(-1, wdczh__dmls)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                gcgp__ggvsa = typing.builtins.IndexValue(i, qhczb__bkisv[i])
                yesgj__fyjcc = max(yesgj__fyjcc, gcgp__ggvsa)
            return yesgj__fyjcc.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
