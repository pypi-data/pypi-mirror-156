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
        mufi__fnsp = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        mufi__fnsp = False
    elif A == bodo.string_array_type:
        mufi__fnsp = ''
    elif A == bodo.binary_array_type:
        mufi__fnsp = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        zge__nlxs = 0
        for tnp__yim in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, tnp__yim):
                if A[tnp__yim] != mufi__fnsp:
                    zge__nlxs += 1
        return zge__nlxs != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        mufi__fnsp = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        mufi__fnsp = False
    elif A == bodo.string_array_type:
        mufi__fnsp = ''
    elif A == bodo.binary_array_type:
        mufi__fnsp = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        zge__nlxs = 0
        for tnp__yim in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, tnp__yim):
                if A[tnp__yim] == mufi__fnsp:
                    zge__nlxs += 1
        return zge__nlxs == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    ycxj__ksjt = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(ycxj__ksjt.ctypes,
        arr, parallel, skipna)
    return ycxj__ksjt[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        zkw__haxbd = len(arr)
        rwjw__frv = np.empty(zkw__haxbd, np.bool_)
        for tnp__yim in numba.parfors.parfor.internal_prange(zkw__haxbd):
            rwjw__frv[tnp__yim] = bodo.libs.array_kernels.isna(arr, tnp__yim)
        return rwjw__frv
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        zge__nlxs = 0
        for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
            bgxli__digo = 0
            if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                bgxli__digo = 1
            zge__nlxs += bgxli__digo
        ycxj__ksjt = zge__nlxs
        return ycxj__ksjt
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    jfg__ybd = array_op_count(arr)
    fwt__xfs = array_op_min(arr)
    say__larvg = array_op_max(arr)
    bljho__wxjw = array_op_mean(arr)
    rnbxp__ivagb = array_op_std(arr)
    nurgq__eyjxd = array_op_quantile(arr, 0.25)
    sjio__vcd = array_op_quantile(arr, 0.5)
    uftpl__bpv = array_op_quantile(arr, 0.75)
    return (jfg__ybd, bljho__wxjw, rnbxp__ivagb, fwt__xfs, nurgq__eyjxd,
        sjio__vcd, uftpl__bpv, say__larvg)


def array_op_describe_dt_impl(arr):
    jfg__ybd = array_op_count(arr)
    fwt__xfs = array_op_min(arr)
    say__larvg = array_op_max(arr)
    bljho__wxjw = array_op_mean(arr)
    nurgq__eyjxd = array_op_quantile(arr, 0.25)
    sjio__vcd = array_op_quantile(arr, 0.5)
    uftpl__bpv = array_op_quantile(arr, 0.75)
    return (jfg__ybd, bljho__wxjw, fwt__xfs, nurgq__eyjxd, sjio__vcd,
        uftpl__bpv, say__larvg)


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
            jgefm__jdayr = numba.cpython.builtins.get_type_max_value(np.int64)
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = jgefm__jdayr
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[tnp__yim]))
                    bgxli__digo = 1
                jgefm__jdayr = min(jgefm__jdayr, fod__hazw)
                zge__nlxs += bgxli__digo
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(jgefm__jdayr,
                zge__nlxs)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = numba.cpython.builtins.get_type_max_value(np.int64)
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = jgefm__jdayr
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[tnp__yim])
                    bgxli__digo = 1
                jgefm__jdayr = min(jgefm__jdayr, fod__hazw)
                zge__nlxs += bgxli__digo
            return bodo.hiframes.pd_index_ext._dti_val_finalize(jgefm__jdayr,
                zge__nlxs)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            jvnjc__rempi = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = numba.cpython.builtins.get_type_max_value(np.int64)
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(
                jvnjc__rempi)):
                dkopj__cqn = jvnjc__rempi[tnp__yim]
                if dkopj__cqn == -1:
                    continue
                jgefm__jdayr = min(jgefm__jdayr, dkopj__cqn)
                zge__nlxs += 1
            ycxj__ksjt = bodo.hiframes.series_kernels._box_cat_val(jgefm__jdayr
                , arr.dtype, zge__nlxs)
            return ycxj__ksjt
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = bodo.hiframes.series_kernels._get_date_max_value()
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = jgefm__jdayr
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = arr[tnp__yim]
                    bgxli__digo = 1
                jgefm__jdayr = min(jgefm__jdayr, fod__hazw)
                zge__nlxs += bgxli__digo
            ycxj__ksjt = bodo.hiframes.series_kernels._sum_handle_nan(
                jgefm__jdayr, zge__nlxs)
            return ycxj__ksjt
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jgefm__jdayr = bodo.hiframes.series_kernels._get_type_max_value(arr
            .dtype)
        zge__nlxs = 0
        for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
            fod__hazw = jgefm__jdayr
            bgxli__digo = 0
            if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                fod__hazw = arr[tnp__yim]
                bgxli__digo = 1
            jgefm__jdayr = min(jgefm__jdayr, fod__hazw)
            zge__nlxs += bgxli__digo
        ycxj__ksjt = bodo.hiframes.series_kernels._sum_handle_nan(jgefm__jdayr,
            zge__nlxs)
        return ycxj__ksjt
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = numba.cpython.builtins.get_type_min_value(np.int64)
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = jgefm__jdayr
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[tnp__yim]))
                    bgxli__digo = 1
                jgefm__jdayr = max(jgefm__jdayr, fod__hazw)
                zge__nlxs += bgxli__digo
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(jgefm__jdayr,
                zge__nlxs)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = numba.cpython.builtins.get_type_min_value(np.int64)
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = jgefm__jdayr
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[tnp__yim])
                    bgxli__digo = 1
                jgefm__jdayr = max(jgefm__jdayr, fod__hazw)
                zge__nlxs += bgxli__digo
            return bodo.hiframes.pd_index_ext._dti_val_finalize(jgefm__jdayr,
                zge__nlxs)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            jvnjc__rempi = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = -1
            for tnp__yim in numba.parfors.parfor.internal_prange(len(
                jvnjc__rempi)):
                jgefm__jdayr = max(jgefm__jdayr, jvnjc__rempi[tnp__yim])
            ycxj__ksjt = bodo.hiframes.series_kernels._box_cat_val(jgefm__jdayr
                , arr.dtype, 1)
            return ycxj__ksjt
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = bodo.hiframes.series_kernels._get_date_min_value()
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = jgefm__jdayr
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = arr[tnp__yim]
                    bgxli__digo = 1
                jgefm__jdayr = max(jgefm__jdayr, fod__hazw)
                zge__nlxs += bgxli__digo
            ycxj__ksjt = bodo.hiframes.series_kernels._sum_handle_nan(
                jgefm__jdayr, zge__nlxs)
            return ycxj__ksjt
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jgefm__jdayr = bodo.hiframes.series_kernels._get_type_min_value(arr
            .dtype)
        zge__nlxs = 0
        for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
            fod__hazw = jgefm__jdayr
            bgxli__digo = 0
            if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                fod__hazw = arr[tnp__yim]
                bgxli__digo = 1
            jgefm__jdayr = max(jgefm__jdayr, fod__hazw)
            zge__nlxs += bgxli__digo
        ycxj__ksjt = bodo.hiframes.series_kernels._sum_handle_nan(jgefm__jdayr,
            zge__nlxs)
        return ycxj__ksjt
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
    fkfig__cwb = types.float64
    ctdyi__gwxig = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        fkfig__cwb = types.float32
        ctdyi__gwxig = types.float32
    jqvf__dmg = fkfig__cwb(0)
    vnup__pitel = ctdyi__gwxig(0)
    izys__vfeb = ctdyi__gwxig(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jgefm__jdayr = jqvf__dmg
        zge__nlxs = vnup__pitel
        for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
            fod__hazw = jqvf__dmg
            bgxli__digo = vnup__pitel
            if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                fod__hazw = arr[tnp__yim]
                bgxli__digo = izys__vfeb
            jgefm__jdayr += fod__hazw
            zge__nlxs += bgxli__digo
        ycxj__ksjt = bodo.hiframes.series_kernels._mean_handle_nan(jgefm__jdayr
            , zge__nlxs)
        return ycxj__ksjt
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        ghs__bxem = 0.0
        ssdbr__vypi = 0.0
        zge__nlxs = 0
        for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
            fod__hazw = 0.0
            bgxli__digo = 0
            if not bodo.libs.array_kernels.isna(arr, tnp__yim) or not skipna:
                fod__hazw = arr[tnp__yim]
                bgxli__digo = 1
            ghs__bxem += fod__hazw
            ssdbr__vypi += fod__hazw * fod__hazw
            zge__nlxs += bgxli__digo
        ycxj__ksjt = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            ghs__bxem, ssdbr__vypi, zge__nlxs, ddof)
        return ycxj__ksjt
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
                rwjw__frv = np.empty(len(q), np.int64)
                for tnp__yim in range(len(q)):
                    zbs__rlm = np.float64(q[tnp__yim])
                    rwjw__frv[tnp__yim] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), zbs__rlm)
                return rwjw__frv.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            rwjw__frv = np.empty(len(q), np.float64)
            for tnp__yim in range(len(q)):
                zbs__rlm = np.float64(q[tnp__yim])
                rwjw__frv[tnp__yim] = bodo.libs.array_kernels.quantile(arr,
                    zbs__rlm)
            return rwjw__frv
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
        cpbl__wwniv = types.intp
    elif arr.dtype == types.bool_:
        cpbl__wwniv = np.int64
    else:
        cpbl__wwniv = arr.dtype
    kwzm__civ = cpbl__wwniv(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = kwzm__civ
            zkw__haxbd = len(arr)
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(zkw__haxbd):
                fod__hazw = kwzm__civ
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim
                    ) or not skipna:
                    fod__hazw = arr[tnp__yim]
                    bgxli__digo = 1
                jgefm__jdayr += fod__hazw
                zge__nlxs += bgxli__digo
            ycxj__ksjt = bodo.hiframes.series_kernels._var_handle_mincount(
                jgefm__jdayr, zge__nlxs, min_count)
            return ycxj__ksjt
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = kwzm__civ
            zkw__haxbd = len(arr)
            for tnp__yim in numba.parfors.parfor.internal_prange(zkw__haxbd):
                fod__hazw = kwzm__civ
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = arr[tnp__yim]
                jgefm__jdayr += fod__hazw
            return jgefm__jdayr
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    etsrk__ovy = arr.dtype(1)
    if arr.dtype == types.bool_:
        etsrk__ovy = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = etsrk__ovy
            zge__nlxs = 0
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = etsrk__ovy
                bgxli__digo = 0
                if not bodo.libs.array_kernels.isna(arr, tnp__yim
                    ) or not skipna:
                    fod__hazw = arr[tnp__yim]
                    bgxli__digo = 1
                zge__nlxs += bgxli__digo
                jgefm__jdayr *= fod__hazw
            ycxj__ksjt = bodo.hiframes.series_kernels._var_handle_mincount(
                jgefm__jdayr, zge__nlxs, min_count)
            return ycxj__ksjt
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jgefm__jdayr = etsrk__ovy
            for tnp__yim in numba.parfors.parfor.internal_prange(len(arr)):
                fod__hazw = etsrk__ovy
                if not bodo.libs.array_kernels.isna(arr, tnp__yim):
                    fod__hazw = arr[tnp__yim]
                jgefm__jdayr *= fod__hazw
            return jgefm__jdayr
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        tnp__yim = bodo.libs.array_kernels._nan_argmax(arr)
        return index[tnp__yim]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        tnp__yim = bodo.libs.array_kernels._nan_argmin(arr)
        return index[tnp__yim]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            nes__etgol = {}
            for gre__tswc in values:
                nes__etgol[bodo.utils.conversion.box_if_dt64(gre__tswc)] = 0
            return nes__etgol
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
        zkw__haxbd = len(arr)
        rwjw__frv = np.empty(zkw__haxbd, np.bool_)
        for tnp__yim in numba.parfors.parfor.internal_prange(zkw__haxbd):
            rwjw__frv[tnp__yim] = bodo.utils.conversion.box_if_dt64(arr[
                tnp__yim]) in values
        return rwjw__frv
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    ooln__cykqt = len(in_arr_tup) != 1
    tkjw__zrvx = list(in_arr_tup.types)
    jfkho__wgpuc = 'def impl(in_arr_tup):\n'
    jfkho__wgpuc += '  n = len(in_arr_tup[0])\n'
    if ooln__cykqt:
        izod__hog = ', '.join([f'in_arr_tup[{tnp__yim}][unused]' for
            tnp__yim in range(len(in_arr_tup))])
        bsdqn__owb = ', '.join(['False' for itfa__jhanr in range(len(
            in_arr_tup))])
        jfkho__wgpuc += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({izod__hog},), ({bsdqn__owb},)): 0 for unused in range(0)}}
"""
        jfkho__wgpuc += '  map_vector = np.empty(n, np.int64)\n'
        for tnp__yim, dplau__zoqz in enumerate(tkjw__zrvx):
            jfkho__wgpuc += f'  in_lst_{tnp__yim} = []\n'
            if is_str_arr_type(dplau__zoqz):
                jfkho__wgpuc += f'  total_len_{tnp__yim} = 0\n'
            jfkho__wgpuc += f'  null_in_lst_{tnp__yim} = []\n'
        jfkho__wgpuc += '  for i in range(n):\n'
        znia__ciz = ', '.join([f'in_arr_tup[{tnp__yim}][i]' for tnp__yim in
            range(len(tkjw__zrvx))])
        fms__pskb = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{tnp__yim}], i)' for
            tnp__yim in range(len(tkjw__zrvx))])
        jfkho__wgpuc += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({znia__ciz},), ({fms__pskb},))
"""
        jfkho__wgpuc += '    if data_val not in arr_map:\n'
        jfkho__wgpuc += '      set_val = len(arr_map)\n'
        jfkho__wgpuc += '      values_tup = data_val._data\n'
        jfkho__wgpuc += '      nulls_tup = data_val._null_values\n'
        for tnp__yim, dplau__zoqz in enumerate(tkjw__zrvx):
            jfkho__wgpuc += (
                f'      in_lst_{tnp__yim}.append(values_tup[{tnp__yim}])\n')
            jfkho__wgpuc += (
                f'      null_in_lst_{tnp__yim}.append(nulls_tup[{tnp__yim}])\n'
                )
            if is_str_arr_type(dplau__zoqz):
                jfkho__wgpuc += f"""      total_len_{tnp__yim}  += nulls_tup[{tnp__yim}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{tnp__yim}], i)
"""
        jfkho__wgpuc += '      arr_map[data_val] = len(arr_map)\n'
        jfkho__wgpuc += '    else:\n'
        jfkho__wgpuc += '      set_val = arr_map[data_val]\n'
        jfkho__wgpuc += '    map_vector[i] = set_val\n'
        jfkho__wgpuc += '  n_rows = len(arr_map)\n'
        for tnp__yim, dplau__zoqz in enumerate(tkjw__zrvx):
            if is_str_arr_type(dplau__zoqz):
                jfkho__wgpuc += f"""  out_arr_{tnp__yim} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{tnp__yim})
"""
            else:
                jfkho__wgpuc += f"""  out_arr_{tnp__yim} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{tnp__yim}], (-1,))
"""
        jfkho__wgpuc += '  for j in range(len(arr_map)):\n'
        for tnp__yim in range(len(tkjw__zrvx)):
            jfkho__wgpuc += f'    if null_in_lst_{tnp__yim}[j]:\n'
            jfkho__wgpuc += (
                f'      bodo.libs.array_kernels.setna(out_arr_{tnp__yim}, j)\n'
                )
            jfkho__wgpuc += '    else:\n'
            jfkho__wgpuc += (
                f'      out_arr_{tnp__yim}[j] = in_lst_{tnp__yim}[j]\n')
        rde__qly = ', '.join([f'out_arr_{tnp__yim}' for tnp__yim in range(
            len(tkjw__zrvx))])
        jfkho__wgpuc += f'  return ({rde__qly},), map_vector\n'
    else:
        jfkho__wgpuc += '  in_arr = in_arr_tup[0]\n'
        jfkho__wgpuc += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        jfkho__wgpuc += '  map_vector = np.empty(n, np.int64)\n'
        jfkho__wgpuc += '  is_na = 0\n'
        jfkho__wgpuc += '  in_lst = []\n'
        jfkho__wgpuc += '  na_idxs = []\n'
        if is_str_arr_type(tkjw__zrvx[0]):
            jfkho__wgpuc += '  total_len = 0\n'
        jfkho__wgpuc += '  for i in range(n):\n'
        jfkho__wgpuc += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        jfkho__wgpuc += '      is_na = 1\n'
        jfkho__wgpuc += '      # Always put NA in the last location.\n'
        jfkho__wgpuc += '      # We use -1 as a placeholder\n'
        jfkho__wgpuc += '      set_val = -1\n'
        jfkho__wgpuc += '      na_idxs.append(i)\n'
        jfkho__wgpuc += '    else:\n'
        jfkho__wgpuc += '      data_val = in_arr[i]\n'
        jfkho__wgpuc += '      if data_val not in arr_map:\n'
        jfkho__wgpuc += '        set_val = len(arr_map)\n'
        jfkho__wgpuc += '        in_lst.append(data_val)\n'
        if is_str_arr_type(tkjw__zrvx[0]):
            jfkho__wgpuc += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        jfkho__wgpuc += '        arr_map[data_val] = len(arr_map)\n'
        jfkho__wgpuc += '      else:\n'
        jfkho__wgpuc += '        set_val = arr_map[data_val]\n'
        jfkho__wgpuc += '    map_vector[i] = set_val\n'
        jfkho__wgpuc += '  map_vector[na_idxs] = len(arr_map)\n'
        jfkho__wgpuc += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(tkjw__zrvx[0]):
            jfkho__wgpuc += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            jfkho__wgpuc += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        jfkho__wgpuc += '  for j in range(len(arr_map)):\n'
        jfkho__wgpuc += '    out_arr[j] = in_lst[j]\n'
        jfkho__wgpuc += '  if is_na:\n'
        jfkho__wgpuc += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        jfkho__wgpuc += f'  return (out_arr,), map_vector\n'
    wnnkp__gbn = {}
    exec(jfkho__wgpuc, {'bodo': bodo, 'np': np}, wnnkp__gbn)
    impl = wnnkp__gbn['impl']
    return impl
