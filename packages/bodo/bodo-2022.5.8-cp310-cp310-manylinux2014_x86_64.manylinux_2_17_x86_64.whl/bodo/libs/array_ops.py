"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero, is_str_arr_type


def array_op_any(arr, skipna=True):
    pass


@overload(array_op_any)
def overload_array_op_any(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        agag__gaai = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        agag__gaai = False
    elif A == bodo.string_array_type:
        agag__gaai = ''
    elif A == bodo.binary_array_type:
        agag__gaai = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        woai__nmaoc = 0
        for qbai__sav in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, qbai__sav):
                if A[qbai__sav] != agag__gaai:
                    woai__nmaoc += 1
        return woai__nmaoc != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        agag__gaai = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        agag__gaai = False
    elif A == bodo.string_array_type:
        agag__gaai = ''
    elif A == bodo.binary_array_type:
        agag__gaai = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        woai__nmaoc = 0
        for qbai__sav in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, qbai__sav):
                if A[qbai__sav] == agag__gaai:
                    woai__nmaoc += 1
        return woai__nmaoc == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    hlgd__eri = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(hlgd__eri.ctypes, arr,
        parallel, skipna)
    return hlgd__eri[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        huevw__ptxfk = len(arr)
        rxxm__znfc = np.empty(huevw__ptxfk, np.bool_)
        for qbai__sav in numba.parfors.parfor.internal_prange(huevw__ptxfk):
            rxxm__znfc[qbai__sav] = bodo.libs.array_kernels.isna(arr, qbai__sav
                )
        return rxxm__znfc
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        woai__nmaoc = 0
        for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
            ssfi__wnr = 0
            if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                ssfi__wnr = 1
            woai__nmaoc += ssfi__wnr
        hlgd__eri = woai__nmaoc
        return hlgd__eri
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    tgpjb__pskzh = array_op_count(arr)
    aiop__udwpl = array_op_min(arr)
    ndag__fifvq = array_op_max(arr)
    bnyza__kedjz = array_op_mean(arr)
    lib__mqm = array_op_std(arr)
    clqa__vjh = array_op_quantile(arr, 0.25)
    lyfxh__xob = array_op_quantile(arr, 0.5)
    shsx__rbs = array_op_quantile(arr, 0.75)
    return (tgpjb__pskzh, bnyza__kedjz, lib__mqm, aiop__udwpl, clqa__vjh,
        lyfxh__xob, shsx__rbs, ndag__fifvq)


def array_op_describe_dt_impl(arr):
    tgpjb__pskzh = array_op_count(arr)
    aiop__udwpl = array_op_min(arr)
    ndag__fifvq = array_op_max(arr)
    bnyza__kedjz = array_op_mean(arr)
    clqa__vjh = array_op_quantile(arr, 0.25)
    lyfxh__xob = array_op_quantile(arr, 0.5)
    shsx__rbs = array_op_quantile(arr, 0.75)
    return (tgpjb__pskzh, bnyza__kedjz, aiop__udwpl, clqa__vjh, lyfxh__xob,
        shsx__rbs, ndag__fifvq)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


@generated_jit(nopython=True)
def array_op_nbytes(arr):
    return array_op_nbytes_impl


def array_op_nbytes_impl(arr):
    return arr.nbytes


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = numba.cpython.builtins.get_type_max_value(np.int64)
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = bzzle__ifjo
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[qbai__sav]))
                    ssfi__wnr = 1
                bzzle__ifjo = min(bzzle__ifjo, tcz__orz)
                woai__nmaoc += ssfi__wnr
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(bzzle__ifjo,
                woai__nmaoc)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = numba.cpython.builtins.get_type_max_value(np.int64)
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = bzzle__ifjo
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[qbai__sav])
                    ssfi__wnr = 1
                bzzle__ifjo = min(bzzle__ifjo, tcz__orz)
                woai__nmaoc += ssfi__wnr
            return bodo.hiframes.pd_index_ext._dti_val_finalize(bzzle__ifjo,
                woai__nmaoc)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            oke__zcm = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = numba.cpython.builtins.get_type_max_value(np.int64)
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(oke__zcm)
                ):
                ovap__gvrp = oke__zcm[qbai__sav]
                if ovap__gvrp == -1:
                    continue
                bzzle__ifjo = min(bzzle__ifjo, ovap__gvrp)
                woai__nmaoc += 1
            hlgd__eri = bodo.hiframes.series_kernels._box_cat_val(bzzle__ifjo,
                arr.dtype, woai__nmaoc)
            return hlgd__eri
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = bodo.hiframes.series_kernels._get_date_max_value()
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = bzzle__ifjo
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = arr[qbai__sav]
                    ssfi__wnr = 1
                bzzle__ifjo = min(bzzle__ifjo, tcz__orz)
                woai__nmaoc += ssfi__wnr
            hlgd__eri = bodo.hiframes.series_kernels._sum_handle_nan(
                bzzle__ifjo, woai__nmaoc)
            return hlgd__eri
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        bzzle__ifjo = bodo.hiframes.series_kernels._get_type_max_value(arr.
            dtype)
        woai__nmaoc = 0
        for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
            tcz__orz = bzzle__ifjo
            ssfi__wnr = 0
            if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                tcz__orz = arr[qbai__sav]
                ssfi__wnr = 1
            bzzle__ifjo = min(bzzle__ifjo, tcz__orz)
            woai__nmaoc += ssfi__wnr
        hlgd__eri = bodo.hiframes.series_kernels._sum_handle_nan(bzzle__ifjo,
            woai__nmaoc)
        return hlgd__eri
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = numba.cpython.builtins.get_type_min_value(np.int64)
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = bzzle__ifjo
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[qbai__sav]))
                    ssfi__wnr = 1
                bzzle__ifjo = max(bzzle__ifjo, tcz__orz)
                woai__nmaoc += ssfi__wnr
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(bzzle__ifjo,
                woai__nmaoc)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = numba.cpython.builtins.get_type_min_value(np.int64)
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = bzzle__ifjo
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[qbai__sav])
                    ssfi__wnr = 1
                bzzle__ifjo = max(bzzle__ifjo, tcz__orz)
                woai__nmaoc += ssfi__wnr
            return bodo.hiframes.pd_index_ext._dti_val_finalize(bzzle__ifjo,
                woai__nmaoc)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            oke__zcm = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = -1
            for qbai__sav in numba.parfors.parfor.internal_prange(len(oke__zcm)
                ):
                bzzle__ifjo = max(bzzle__ifjo, oke__zcm[qbai__sav])
            hlgd__eri = bodo.hiframes.series_kernels._box_cat_val(bzzle__ifjo,
                arr.dtype, 1)
            return hlgd__eri
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = bodo.hiframes.series_kernels._get_date_min_value()
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = bzzle__ifjo
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = arr[qbai__sav]
                    ssfi__wnr = 1
                bzzle__ifjo = max(bzzle__ifjo, tcz__orz)
                woai__nmaoc += ssfi__wnr
            hlgd__eri = bodo.hiframes.series_kernels._sum_handle_nan(
                bzzle__ifjo, woai__nmaoc)
            return hlgd__eri
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        bzzle__ifjo = bodo.hiframes.series_kernels._get_type_min_value(arr.
            dtype)
        woai__nmaoc = 0
        for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
            tcz__orz = bzzle__ifjo
            ssfi__wnr = 0
            if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                tcz__orz = arr[qbai__sav]
                ssfi__wnr = 1
            bzzle__ifjo = max(bzzle__ifjo, tcz__orz)
            woai__nmaoc += ssfi__wnr
        hlgd__eri = bodo.hiframes.series_kernels._sum_handle_nan(bzzle__ifjo,
            woai__nmaoc)
        return hlgd__eri
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    kqrmg__woaq = types.float64
    hcsie__dbuz = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        kqrmg__woaq = types.float32
        hcsie__dbuz = types.float32
    nkbsj__ryu = kqrmg__woaq(0)
    mfehr__bkgi = hcsie__dbuz(0)
    wdqli__lcg = hcsie__dbuz(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        bzzle__ifjo = nkbsj__ryu
        woai__nmaoc = mfehr__bkgi
        for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
            tcz__orz = nkbsj__ryu
            ssfi__wnr = mfehr__bkgi
            if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                tcz__orz = arr[qbai__sav]
                ssfi__wnr = wdqli__lcg
            bzzle__ifjo += tcz__orz
            woai__nmaoc += ssfi__wnr
        hlgd__eri = bodo.hiframes.series_kernels._mean_handle_nan(bzzle__ifjo,
            woai__nmaoc)
        return hlgd__eri
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        vsex__ilt = 0.0
        ukbw__hifi = 0.0
        woai__nmaoc = 0
        for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
            tcz__orz = 0.0
            ssfi__wnr = 0
            if not bodo.libs.array_kernels.isna(arr, qbai__sav) or not skipna:
                tcz__orz = arr[qbai__sav]
                ssfi__wnr = 1
            vsex__ilt += tcz__orz
            ukbw__hifi += tcz__orz * tcz__orz
            woai__nmaoc += ssfi__wnr
        hlgd__eri = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            vsex__ilt, ukbw__hifi, woai__nmaoc, ddof)
        return hlgd__eri
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                rxxm__znfc = np.empty(len(q), np.int64)
                for qbai__sav in range(len(q)):
                    cdknc__blu = np.float64(q[qbai__sav])
                    rxxm__znfc[qbai__sav] = bodo.libs.array_kernels.quantile(
                        arr.view(np.int64), cdknc__blu)
                return rxxm__znfc.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            rxxm__znfc = np.empty(len(q), np.float64)
            for qbai__sav in range(len(q)):
                cdknc__blu = np.float64(q[qbai__sav])
                rxxm__znfc[qbai__sav] = bodo.libs.array_kernels.quantile(arr,
                    cdknc__blu)
            return rxxm__znfc
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        prvqh__ugmzu = types.intp
    elif arr.dtype == types.bool_:
        prvqh__ugmzu = np.int64
    else:
        prvqh__ugmzu = arr.dtype
    mbwco__pzes = prvqh__ugmzu(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = mbwco__pzes
            huevw__ptxfk = len(arr)
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(huevw__ptxfk
                ):
                tcz__orz = mbwco__pzes
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav
                    ) or not skipna:
                    tcz__orz = arr[qbai__sav]
                    ssfi__wnr = 1
                bzzle__ifjo += tcz__orz
                woai__nmaoc += ssfi__wnr
            hlgd__eri = bodo.hiframes.series_kernels._var_handle_mincount(
                bzzle__ifjo, woai__nmaoc, min_count)
            return hlgd__eri
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = mbwco__pzes
            huevw__ptxfk = len(arr)
            for qbai__sav in numba.parfors.parfor.internal_prange(huevw__ptxfk
                ):
                tcz__orz = mbwco__pzes
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = arr[qbai__sav]
                bzzle__ifjo += tcz__orz
            return bzzle__ifjo
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    kji__zsci = arr.dtype(1)
    if arr.dtype == types.bool_:
        kji__zsci = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = kji__zsci
            woai__nmaoc = 0
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = kji__zsci
                ssfi__wnr = 0
                if not bodo.libs.array_kernels.isna(arr, qbai__sav
                    ) or not skipna:
                    tcz__orz = arr[qbai__sav]
                    ssfi__wnr = 1
                woai__nmaoc += ssfi__wnr
                bzzle__ifjo *= tcz__orz
            hlgd__eri = bodo.hiframes.series_kernels._var_handle_mincount(
                bzzle__ifjo, woai__nmaoc, min_count)
            return hlgd__eri
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            bzzle__ifjo = kji__zsci
            for qbai__sav in numba.parfors.parfor.internal_prange(len(arr)):
                tcz__orz = kji__zsci
                if not bodo.libs.array_kernels.isna(arr, qbai__sav):
                    tcz__orz = arr[qbai__sav]
                bzzle__ifjo *= tcz__orz
            return bzzle__ifjo
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        qbai__sav = bodo.libs.array_kernels._nan_argmax(arr)
        return index[qbai__sav]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        qbai__sav = bodo.libs.array_kernels._nan_argmin(arr)
        return index[qbai__sav]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            jldn__woub = {}
            for egg__xvfm in values:
                jldn__woub[bodo.utils.conversion.box_if_dt64(egg__xvfm)] = 0
            return jldn__woub
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        huevw__ptxfk = len(arr)
        rxxm__znfc = np.empty(huevw__ptxfk, np.bool_)
        for qbai__sav in numba.parfors.parfor.internal_prange(huevw__ptxfk):
            rxxm__znfc[qbai__sav] = bodo.utils.conversion.box_if_dt64(arr[
                qbai__sav]) in values
        return rxxm__znfc
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    yhch__umne = len(in_arr_tup) != 1
    lmt__dvi = list(in_arr_tup.types)
    zig__qzdm = 'def impl(in_arr_tup):\n'
    zig__qzdm += '  n = len(in_arr_tup[0])\n'
    if yhch__umne:
        cpsv__vvs = ', '.join([f'in_arr_tup[{qbai__sav}][unused]' for
            qbai__sav in range(len(in_arr_tup))])
        xww__awntl = ', '.join(['False' for eecuk__brf in range(len(
            in_arr_tup))])
        zig__qzdm += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({cpsv__vvs},), ({xww__awntl},)): 0 for unused in range(0)}}
"""
        zig__qzdm += '  map_vector = np.empty(n, np.int64)\n'
        for qbai__sav, uekte__sus in enumerate(lmt__dvi):
            zig__qzdm += f'  in_lst_{qbai__sav} = []\n'
            if is_str_arr_type(uekte__sus):
                zig__qzdm += f'  total_len_{qbai__sav} = 0\n'
            zig__qzdm += f'  null_in_lst_{qbai__sav} = []\n'
        zig__qzdm += '  for i in range(n):\n'
        jyr__dikg = ', '.join([f'in_arr_tup[{qbai__sav}][i]' for qbai__sav in
            range(len(lmt__dvi))])
        bbqci__ujw = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{qbai__sav}], i)' for
            qbai__sav in range(len(lmt__dvi))])
        zig__qzdm += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({jyr__dikg},), ({bbqci__ujw},))
"""
        zig__qzdm += '    if data_val not in arr_map:\n'
        zig__qzdm += '      set_val = len(arr_map)\n'
        zig__qzdm += '      values_tup = data_val._data\n'
        zig__qzdm += '      nulls_tup = data_val._null_values\n'
        for qbai__sav, uekte__sus in enumerate(lmt__dvi):
            zig__qzdm += (
                f'      in_lst_{qbai__sav}.append(values_tup[{qbai__sav}])\n')
            zig__qzdm += (
                f'      null_in_lst_{qbai__sav}.append(nulls_tup[{qbai__sav}])\n'
                )
            if is_str_arr_type(uekte__sus):
                zig__qzdm += f"""      total_len_{qbai__sav}  += nulls_tup[{qbai__sav}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{qbai__sav}], i)
"""
        zig__qzdm += '      arr_map[data_val] = len(arr_map)\n'
        zig__qzdm += '    else:\n'
        zig__qzdm += '      set_val = arr_map[data_val]\n'
        zig__qzdm += '    map_vector[i] = set_val\n'
        zig__qzdm += '  n_rows = len(arr_map)\n'
        for qbai__sav, uekte__sus in enumerate(lmt__dvi):
            if is_str_arr_type(uekte__sus):
                zig__qzdm += f"""  out_arr_{qbai__sav} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{qbai__sav})
"""
            else:
                zig__qzdm += f"""  out_arr_{qbai__sav} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{qbai__sav}], (-1,))
"""
        zig__qzdm += '  for j in range(len(arr_map)):\n'
        for qbai__sav in range(len(lmt__dvi)):
            zig__qzdm += f'    if null_in_lst_{qbai__sav}[j]:\n'
            zig__qzdm += (
                f'      bodo.libs.array_kernels.setna(out_arr_{qbai__sav}, j)\n'
                )
            zig__qzdm += '    else:\n'
            zig__qzdm += (
                f'      out_arr_{qbai__sav}[j] = in_lst_{qbai__sav}[j]\n')
        dtsn__xacb = ', '.join([f'out_arr_{qbai__sav}' for qbai__sav in
            range(len(lmt__dvi))])
        zig__qzdm += f'  return ({dtsn__xacb},), map_vector\n'
    else:
        zig__qzdm += '  in_arr = in_arr_tup[0]\n'
        zig__qzdm += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        zig__qzdm += '  map_vector = np.empty(n, np.int64)\n'
        zig__qzdm += '  is_na = 0\n'
        zig__qzdm += '  in_lst = []\n'
        zig__qzdm += '  na_idxs = []\n'
        if is_str_arr_type(lmt__dvi[0]):
            zig__qzdm += '  total_len = 0\n'
        zig__qzdm += '  for i in range(n):\n'
        zig__qzdm += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        zig__qzdm += '      is_na = 1\n'
        zig__qzdm += '      # Always put NA in the last location.\n'
        zig__qzdm += '      # We use -1 as a placeholder\n'
        zig__qzdm += '      set_val = -1\n'
        zig__qzdm += '      na_idxs.append(i)\n'
        zig__qzdm += '    else:\n'
        zig__qzdm += '      data_val = in_arr[i]\n'
        zig__qzdm += '      if data_val not in arr_map:\n'
        zig__qzdm += '        set_val = len(arr_map)\n'
        zig__qzdm += '        in_lst.append(data_val)\n'
        if is_str_arr_type(lmt__dvi[0]):
            zig__qzdm += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        zig__qzdm += '        arr_map[data_val] = len(arr_map)\n'
        zig__qzdm += '      else:\n'
        zig__qzdm += '        set_val = arr_map[data_val]\n'
        zig__qzdm += '    map_vector[i] = set_val\n'
        zig__qzdm += '  map_vector[na_idxs] = len(arr_map)\n'
        zig__qzdm += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(lmt__dvi[0]):
            zig__qzdm += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            zig__qzdm += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        zig__qzdm += '  for j in range(len(arr_map)):\n'
        zig__qzdm += '    out_arr[j] = in_lst[j]\n'
        zig__qzdm += '  if is_na:\n'
        zig__qzdm += '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n'
        zig__qzdm += f'  return (out_arr,), map_vector\n'
    cnxb__ubbs = {}
    exec(zig__qzdm, {'bodo': bodo, 'np': np}, cnxb__ubbs)
    impl = cnxb__ubbs['impl']
    return impl
