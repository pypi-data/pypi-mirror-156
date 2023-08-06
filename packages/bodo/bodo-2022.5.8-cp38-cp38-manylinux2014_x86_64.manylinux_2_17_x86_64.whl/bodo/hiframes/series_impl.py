"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.transform import is_var_size_item_array_type
from bodo.utils.typing import BodoError, ColNamesMetaType, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_index_names, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, is_str_arr_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    if isinstance(s.data, bodo.DatetimeArrayType):

        def impl(s):
            mogj__nzg = bodo.hiframes.pd_series_ext.get_series_data(s)
            fbnha__ukph = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                mogj__nzg)
            return fbnha__ukph
        return impl
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s, 'Series.dtype'
        )
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s,
        'Series.dtypes')
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.tolist()')
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            dkzqh__itqiy = list()
            for nqahj__qewl in range(len(S)):
                dkzqh__itqiy.append(S.iat[nqahj__qewl])
            return dkzqh__itqiy
        return impl_float

    def impl(S):
        dkzqh__itqiy = list()
        for nqahj__qewl in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, nqahj__qewl):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            dkzqh__itqiy.append(S.iat[nqahj__qewl])
        return dkzqh__itqiy
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    czrpa__qjfud = dict(dtype=dtype, copy=copy, na_value=na_value)
    xjluw__afji = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    czrpa__qjfud = dict(name=name, inplace=inplace)
    xjluw__afji = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        nts__lcrtf = ', '.join(['index_arrs[{}]'.format(nqahj__qewl) for
            nqahj__qewl in range(S.index.nlevels)])
    else:
        nts__lcrtf = '    bodo.utils.conversion.index_to_array(index)\n'
    vcfgn__cra = 'index' if 'index' != series_name else 'level_0'
    plk__ujt = get_index_names(S.index, 'Series.reset_index()', vcfgn__cra)
    columns = [name for name in plk__ujt]
    columns.append(series_name)
    yds__hxrh = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    yds__hxrh += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    yds__hxrh += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        yds__hxrh += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    yds__hxrh += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    yds__hxrh += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({nts__lcrtf}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    yewkz__dysx = {}
    exec(yds__hxrh, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, yewkz__dysx)
    pxkrk__bhukw = yewkz__dysx['_impl']
    return pxkrk__bhukw


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.round()')

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        vbq__zzpgl = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[nqahj__qewl]):
                bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
            else:
                vbq__zzpgl[nqahj__qewl] = np.round(arr[nqahj__qewl], decimals)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sum()'
        )

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.product()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    czrpa__qjfud = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    xjluw__afji = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.any()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.equals()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.equals()')
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        npfh__rrt = bodo.hiframes.pd_series_ext.get_series_data(S)
        flvo__bqupn = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        qnosh__moyj = 0
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(npfh__rrt)
            ):
            rir__iewx = 0
            znwmh__cpife = bodo.libs.array_kernels.isna(npfh__rrt, nqahj__qewl)
            abb__iok = bodo.libs.array_kernels.isna(flvo__bqupn, nqahj__qewl)
            if znwmh__cpife and not abb__iok or not znwmh__cpife and abb__iok:
                rir__iewx = 1
            elif not znwmh__cpife:
                if npfh__rrt[nqahj__qewl] != flvo__bqupn[nqahj__qewl]:
                    rir__iewx = 1
            qnosh__moyj += rir__iewx
        return qnosh__moyj == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    czrpa__qjfud = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    xjluw__afji = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    czrpa__qjfud = dict(level=level)
    xjluw__afji = dict(level=None)
    check_unsupported_args('Series.mad', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    nfp__byny = types.float64
    ifp__adbaq = types.float64
    if S.dtype == types.float32:
        nfp__byny = types.float32
        ifp__adbaq = types.float32
    bbf__etj = nfp__byny(0)
    sma__fgkaz = ifp__adbaq(0)
    kgy__chq = ifp__adbaq(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        ufg__bnbm = bbf__etj
        qnosh__moyj = sma__fgkaz
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(A)):
            rir__iewx = bbf__etj
            zlpv__vopo = sma__fgkaz
            if not bodo.libs.array_kernels.isna(A, nqahj__qewl) or not skipna:
                rir__iewx = A[nqahj__qewl]
                zlpv__vopo = kgy__chq
            ufg__bnbm += rir__iewx
            qnosh__moyj += zlpv__vopo
        xzfi__kdafx = bodo.hiframes.series_kernels._mean_handle_nan(ufg__bnbm,
            qnosh__moyj)
        mcf__cqblg = bbf__etj
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(A)):
            rir__iewx = bbf__etj
            if not bodo.libs.array_kernels.isna(A, nqahj__qewl) or not skipna:
                rir__iewx = abs(A[nqahj__qewl] - xzfi__kdafx)
            mcf__cqblg += rir__iewx
        oqat__dcjk = bodo.hiframes.series_kernels._mean_handle_nan(mcf__cqblg,
            qnosh__moyj)
        return oqat__dcjk
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    czrpa__qjfud = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    xjluw__afji = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.mean()')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sem()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        oty__glhj = 0
        bpwgu__gdqci = 0
        qnosh__moyj = 0
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(A)):
            rir__iewx = 0
            zlpv__vopo = 0
            if not bodo.libs.array_kernels.isna(A, nqahj__qewl) or not skipna:
                rir__iewx = A[nqahj__qewl]
                zlpv__vopo = 1
            oty__glhj += rir__iewx
            bpwgu__gdqci += rir__iewx * rir__iewx
            qnosh__moyj += zlpv__vopo
        foy__wyuza = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            oty__glhj, bpwgu__gdqci, qnosh__moyj, ddof)
        ean__hdc = bodo.hiframes.series_kernels._sem_handle_nan(foy__wyuza,
            qnosh__moyj)
        return ean__hdc
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.kurtosis()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        oty__glhj = 0.0
        bpwgu__gdqci = 0.0
        lby__rlrn = 0.0
        asp__tlrs = 0.0
        qnosh__moyj = 0
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(A)):
            rir__iewx = 0.0
            zlpv__vopo = 0
            if not bodo.libs.array_kernels.isna(A, nqahj__qewl) or not skipna:
                rir__iewx = np.float64(A[nqahj__qewl])
                zlpv__vopo = 1
            oty__glhj += rir__iewx
            bpwgu__gdqci += rir__iewx ** 2
            lby__rlrn += rir__iewx ** 3
            asp__tlrs += rir__iewx ** 4
            qnosh__moyj += zlpv__vopo
        foy__wyuza = bodo.hiframes.series_kernels.compute_kurt(oty__glhj,
            bpwgu__gdqci, lby__rlrn, asp__tlrs, qnosh__moyj)
        return foy__wyuza
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.skew()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        oty__glhj = 0.0
        bpwgu__gdqci = 0.0
        lby__rlrn = 0.0
        qnosh__moyj = 0
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(A)):
            rir__iewx = 0.0
            zlpv__vopo = 0
            if not bodo.libs.array_kernels.isna(A, nqahj__qewl) or not skipna:
                rir__iewx = np.float64(A[nqahj__qewl])
                zlpv__vopo = 1
            oty__glhj += rir__iewx
            bpwgu__gdqci += rir__iewx ** 2
            lby__rlrn += rir__iewx ** 3
            qnosh__moyj += zlpv__vopo
        foy__wyuza = bodo.hiframes.series_kernels.compute_skew(oty__glhj,
            bpwgu__gdqci, lby__rlrn, qnosh__moyj)
        return foy__wyuza
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.var()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.std()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.dot()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.dot()')

    def impl(S, other):
        npfh__rrt = bodo.hiframes.pd_series_ext.get_series_data(S)
        flvo__bqupn = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        qgtmw__ghfm = 0
        for nqahj__qewl in numba.parfors.parfor.internal_prange(len(npfh__rrt)
            ):
            fky__jym = npfh__rrt[nqahj__qewl]
            chaar__sxcqc = flvo__bqupn[nqahj__qewl]
            qgtmw__ghfm += fky__jym * chaar__sxcqc
        return qgtmw__ghfm
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    czrpa__qjfud = dict(skipna=skipna)
    xjluw__afji = dict(skipna=True)
    check_unsupported_args('Series.cumsum', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumsum()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    czrpa__qjfud = dict(skipna=skipna)
    xjluw__afji = dict(skipna=True)
    check_unsupported_args('Series.cumprod', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumprod()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    czrpa__qjfud = dict(skipna=skipna)
    xjluw__afji = dict(skipna=True)
    check_unsupported_args('Series.cummin', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummin()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    czrpa__qjfud = dict(skipna=skipna)
    xjluw__afji = dict(skipna=True)
    check_unsupported_args('Series.cummax', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummax()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    czrpa__qjfud = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    xjluw__afji = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        lumsl__jtem = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, lumsl__jtem, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    czrpa__qjfud = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    xjluw__afji = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if is_overload_none(mapper) or not is_scalar_type(mapper):
        raise BodoError(
            "Series.rename_axis(): 'mapper' is required and must be a scalar type."
            )

    def impl(S, mapper=None, index=None, columns=None, axis=None, copy=True,
        inplace=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        index = index.rename(mapper)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.abs()'
        )

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    czrpa__qjfud = dict(level=level)
    xjluw__afji = dict(level=None)
    check_unsupported_args('Series.count', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    czrpa__qjfud = dict(method=method, min_periods=min_periods)
    xjluw__afji = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        gctck__hhkay = S.sum()
        vtq__mqn = other.sum()
        a = n * (S * other).sum() - gctck__hhkay * vtq__mqn
        gjb__pkizr = n * (S ** 2).sum() - gctck__hhkay ** 2
        zpvu__loa = n * (other ** 2).sum() - vtq__mqn ** 2
        return a / np.sqrt(gjb__pkizr * zpvu__loa)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    czrpa__qjfud = dict(min_periods=min_periods)
    xjluw__afji = dict(min_periods=None)
    check_unsupported_args('Series.cov', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        gctck__hhkay = S.mean()
        vtq__mqn = other.mean()
        wwzs__fbubh = ((S - gctck__hhkay) * (other - vtq__mqn)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(wwzs__fbubh, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            ivgx__pcb = np.sign(sum_val)
            return np.inf * ivgx__pcb
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    czrpa__qjfud = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    xjluw__afji = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.min()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    czrpa__qjfud = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    xjluw__afji = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.max()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    czrpa__qjfud = dict(axis=axis, skipna=skipna)
    xjluw__afji = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmin()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    czrpa__qjfud = dict(axis=axis, skipna=skipna)
    xjluw__afji = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmax()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_increasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_decreasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    czrpa__qjfud = dict(level=level, numeric_only=numeric_only)
    xjluw__afji = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dam__txf = arr[:n]
        mem__iuzi = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(dam__txf, mem__iuzi,
            name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        groy__vkl = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dam__txf = arr[groy__vkl:]
        mem__iuzi = index[groy__vkl:]
        return bodo.hiframes.pd_series_ext.init_series(dam__txf, mem__iuzi,
            name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    zxri__yxvq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in zxri__yxvq:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            bua__cgj = index[0]
            vptig__hnfjx = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, bua__cgj,
                False))
        else:
            vptig__hnfjx = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dam__txf = arr[:vptig__hnfjx]
        mem__iuzi = index[:vptig__hnfjx]
        return bodo.hiframes.pd_series_ext.init_series(dam__txf, mem__iuzi,
            name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    zxri__yxvq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in zxri__yxvq:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            qtx__nyz = index[-1]
            vptig__hnfjx = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, qtx__nyz,
                True))
        else:
            vptig__hnfjx = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dam__txf = arr[len(arr) - vptig__hnfjx:]
        mem__iuzi = index[len(arr) - vptig__hnfjx:]
        return bodo.hiframes.pd_series_ext.init_series(dam__txf, mem__iuzi,
            name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        rdi__oedzk = bodo.utils.conversion.index_to_array(index)
        fotd__vadep, hjtkd__xsdvy = (bodo.libs.array_kernels.
            first_last_valid_index(arr, rdi__oedzk))
        return hjtkd__xsdvy if fotd__vadep else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        rdi__oedzk = bodo.utils.conversion.index_to_array(index)
        fotd__vadep, hjtkd__xsdvy = (bodo.libs.array_kernels.
            first_last_valid_index(arr, rdi__oedzk, False))
        return hjtkd__xsdvy if fotd__vadep else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    czrpa__qjfud = dict(keep=keep)
    xjluw__afji = dict(keep='first')
    check_unsupported_args('Series.nlargest', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        rdi__oedzk = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl, yckf__apj = bodo.libs.array_kernels.nlargest(arr,
            rdi__oedzk, n, True, bodo.hiframes.series_kernels.gt_f)
        rpilp__tnu = bodo.utils.conversion.convert_to_index(yckf__apj)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
            rpilp__tnu, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    czrpa__qjfud = dict(keep=keep)
    xjluw__afji = dict(keep='first')
    check_unsupported_args('Series.nsmallest', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        rdi__oedzk = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl, yckf__apj = bodo.libs.array_kernels.nlargest(arr,
            rdi__oedzk, n, False, bodo.hiframes.series_kernels.lt_f)
        rpilp__tnu = bodo.utils.conversion.convert_to_index(yckf__apj)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
            rpilp__tnu, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
@overload_method(HeterogeneousSeriesType, 'astype', inline='always',
    no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    czrpa__qjfud = dict(errors=errors)
    xjluw__afji = dict(errors='raise')
    check_unsupported_args('Series.astype', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.astype()')

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    czrpa__qjfud = dict(axis=axis, is_copy=is_copy)
    xjluw__afji = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        upka__yfe = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[upka__yfe],
            index[upka__yfe], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    czrpa__qjfud = dict(axis=axis, kind=kind, order=order)
    xjluw__afji = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yjhek__cxtkx = S.notna().values
        if not yjhek__cxtkx.all():
            vbq__zzpgl = np.full(n, -1, np.int64)
            vbq__zzpgl[yjhek__cxtkx] = argsort(arr[yjhek__cxtkx])
        else:
            vbq__zzpgl = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    czrpa__qjfud = dict(axis=axis, numeric_only=numeric_only)
    xjluw__afji = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_str(method):
        raise BodoError(
            "Series.rank(): 'method' argument must be a constant string")
    if not is_overload_constant_str(na_option):
        raise BodoError(
            "Series.rank(): 'na_option' argument must be a constant string")

    def impl(S, axis=0, method='average', numeric_only=None, na_option=
        'keep', ascending=True, pct=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    czrpa__qjfud = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    xjluw__afji = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    klaul__dfczt = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        uwid__krzd = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, klaul__dfczt)
        fybna__hhq = uwid__krzd.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        vbq__zzpgl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            fybna__hhq, 0)
        rpilp__tnu = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            fybna__hhq)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
            rpilp__tnu, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    czrpa__qjfud = dict(axis=axis, inplace=inplace, kind=kind, ignore_index
        =ignore_index, key=key)
    xjluw__afji = dict(axis=0, inplace=False, kind='quicksort',
        ignore_index=False, key=None)
    check_unsupported_args('Series.sort_values', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    eyvgp__ufp = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        uwid__krzd = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, eyvgp__ufp)
        fybna__hhq = uwid__krzd.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        vbq__zzpgl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            fybna__hhq, 0)
        rpilp__tnu = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            fybna__hhq)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
            rpilp__tnu, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    pktzy__nyq = is_overload_true(is_nullable)
    yds__hxrh = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    yds__hxrh += '  numba.parfors.parfor.init_prange()\n'
    yds__hxrh += '  n = len(arr)\n'
    if pktzy__nyq:
        yds__hxrh += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        yds__hxrh += '  out_arr = np.empty(n, np.int64)\n'
    yds__hxrh += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    yds__hxrh += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if pktzy__nyq:
        yds__hxrh += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        yds__hxrh += '      out_arr[i] = -1\n'
    yds__hxrh += '      continue\n'
    yds__hxrh += '    val = arr[i]\n'
    yds__hxrh += '    if include_lowest and val == bins[0]:\n'
    yds__hxrh += '      ind = 1\n'
    yds__hxrh += '    else:\n'
    yds__hxrh += '      ind = np.searchsorted(bins, val)\n'
    yds__hxrh += '    if ind == 0 or ind == len(bins):\n'
    if pktzy__nyq:
        yds__hxrh += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        yds__hxrh += '      out_arr[i] = -1\n'
    yds__hxrh += '    else:\n'
    yds__hxrh += '      out_arr[i] = ind - 1\n'
    yds__hxrh += '  return out_arr\n'
    yewkz__dysx = {}
    exec(yds__hxrh, {'bodo': bodo, 'np': np, 'numba': numba}, yewkz__dysx)
    impl = yewkz__dysx['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        nfw__oupx, mqx__wqwxs = np.divmod(x, 1)
        if nfw__oupx == 0:
            tqdhx__ladpd = -int(np.floor(np.log10(abs(mqx__wqwxs)))
                ) - 1 + precision
        else:
            tqdhx__ladpd = precision
        return np.around(x, tqdhx__ladpd)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        agh__xyf = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(agh__xyf)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        rsy__zvmrm = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            wqpwy__ctnp = bins.copy()
            if right and include_lowest:
                wqpwy__ctnp[0] = wqpwy__ctnp[0] - rsy__zvmrm
            wcmmm__vro = bodo.libs.interval_arr_ext.init_interval_array(
                wqpwy__ctnp[:-1], wqpwy__ctnp[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(wcmmm__vro,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        wqpwy__ctnp = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            wqpwy__ctnp[0] = wqpwy__ctnp[0] - 10.0 ** -precision
        wcmmm__vro = bodo.libs.interval_arr_ext.init_interval_array(wqpwy__ctnp
            [:-1], wqpwy__ctnp[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(wcmmm__vro, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        uts__pfvdr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        tabz__acnlc = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        vbq__zzpgl = np.zeros(nbins, np.int64)
        for nqahj__qewl in range(len(uts__pfvdr)):
            vbq__zzpgl[tabz__acnlc[nqahj__qewl]] = uts__pfvdr[nqahj__qewl]
        return vbq__zzpgl
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            rqyli__aaic = (max_val - min_val) * 0.001
            if right:
                bins[0] -= rqyli__aaic
            else:
                bins[-1] += rqyli__aaic
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    czrpa__qjfud = dict(dropna=dropna)
    xjluw__afji = dict(dropna=True)
    check_unsupported_args('Series.value_counts', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    aryxn__vxve = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    yds__hxrh = 'def impl(\n'
    yds__hxrh += '    S,\n'
    yds__hxrh += '    normalize=False,\n'
    yds__hxrh += '    sort=True,\n'
    yds__hxrh += '    ascending=False,\n'
    yds__hxrh += '    bins=None,\n'
    yds__hxrh += '    dropna=True,\n'
    yds__hxrh += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    yds__hxrh += '):\n'
    yds__hxrh += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    yds__hxrh += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    yds__hxrh += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if aryxn__vxve:
        yds__hxrh += '    right = True\n'
        yds__hxrh += _gen_bins_handling(bins, S.dtype)
        yds__hxrh += '    arr = get_bin_inds(bins, arr)\n'
    yds__hxrh += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    yds__hxrh += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    yds__hxrh += '    )\n'
    yds__hxrh += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if aryxn__vxve:
        yds__hxrh += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        yds__hxrh += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        yds__hxrh += '    index = get_bin_labels(bins)\n'
    else:
        yds__hxrh += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        yds__hxrh += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        yds__hxrh += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        yds__hxrh += '    )\n'
        yds__hxrh += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    yds__hxrh += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        yds__hxrh += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        uvxo__lut = 'len(S)' if aryxn__vxve else 'count_arr.sum()'
        yds__hxrh += f'    res = res / float({uvxo__lut})\n'
    yds__hxrh += '    return res\n'
    yewkz__dysx = {}
    exec(yds__hxrh, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, yewkz__dysx)
    impl = yewkz__dysx['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    yds__hxrh = ''
    if isinstance(bins, types.Integer):
        yds__hxrh += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        yds__hxrh += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            yds__hxrh += '    min_val = min_val.value\n'
            yds__hxrh += '    max_val = max_val.value\n'
        yds__hxrh += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            yds__hxrh += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        yds__hxrh += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return yds__hxrh


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    czrpa__qjfud = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    xjluw__afji = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    yds__hxrh = 'def impl(\n'
    yds__hxrh += '    x,\n'
    yds__hxrh += '    bins,\n'
    yds__hxrh += '    right=True,\n'
    yds__hxrh += '    labels=None,\n'
    yds__hxrh += '    retbins=False,\n'
    yds__hxrh += '    precision=3,\n'
    yds__hxrh += '    include_lowest=False,\n'
    yds__hxrh += "    duplicates='raise',\n"
    yds__hxrh += '    ordered=True\n'
    yds__hxrh += '):\n'
    if isinstance(x, SeriesType):
        yds__hxrh += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        yds__hxrh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        yds__hxrh += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        yds__hxrh += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    yds__hxrh += _gen_bins_handling(bins, x.dtype)
    yds__hxrh += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    yds__hxrh += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    yds__hxrh += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    yds__hxrh += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        yds__hxrh += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        yds__hxrh += '    return res\n'
    else:
        yds__hxrh += '    return out_arr\n'
    yewkz__dysx = {}
    exec(yds__hxrh, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, yewkz__dysx)
    impl = yewkz__dysx['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.unique, inline='always', no_unliteral=True)
def overload_unique(values):
    if not is_series_type(values) and not (bodo.utils.utils.is_array_typ(
        values, False) and values.ndim == 1):
        raise BodoError(
            "pd.unique(): 'values' must be either a Series or a 1-d array")
    if is_series_type(values):

        def impl(values):
            arr = bodo.hiframes.pd_series_ext.get_series_data(values)
            return bodo.allgatherv(bodo.libs.array_kernels.unique(arr), False)
        return impl
    else:
        return lambda values: bodo.allgatherv(bodo.libs.array_kernels.
            unique(values), False)


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    czrpa__qjfud = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    xjluw__afji = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        zfn__zcfi = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, zfn__zcfi)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    czrpa__qjfud = dict(axis=axis, sort=sort, group_keys=group_keys,
        squeeze=squeeze, observed=observed, dropna=dropna)
    xjluw__afji = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )
        qcls__ghott = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            txwwn__omba = bodo.utils.conversion.coerce_to_array(index)
            uwid__krzd = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                txwwn__omba, arr), index, qcls__ghott)
            return uwid__krzd.groupby(' ')['']
        return impl_index
    hyc__klw = by
    if isinstance(by, SeriesType):
        hyc__klw = by.data
    if isinstance(hyc__klw, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    rpxkg__lla = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        txwwn__omba = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        uwid__krzd = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            txwwn__omba, arr), index, rpxkg__lla)
        return uwid__krzd.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    czrpa__qjfud = dict(verify_integrity=verify_integrity)
    xjluw__afji = dict(verify_integrity=False)
    check_unsupported_args('Series.append', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_append,
        'Series.append()')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.isin()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(values,
        'Series.isin()')
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            hcnhe__ixxa = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            vbq__zzpgl = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(vbq__zzpgl, A, hcnhe__ixxa, False)
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    czrpa__qjfud = dict(interpolation=interpolation)
    xjluw__afji = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            vbq__zzpgl = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        azk__psm = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(azk__psm, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    czrpa__qjfud = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    xjluw__afji = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.describe()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        ywm__fugu = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ywm__fugu = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    yds__hxrh = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {ywm__fugu}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    sej__olteg = dict()
    exec(yds__hxrh, {'bodo': bodo, 'numba': numba}, sej__olteg)
    drfnm__azjkc = sej__olteg['impl']
    return drfnm__azjkc


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        ywm__fugu = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ywm__fugu = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    yds__hxrh = 'def impl(S,\n'
    yds__hxrh += '     value=None,\n'
    yds__hxrh += '    method=None,\n'
    yds__hxrh += '    axis=None,\n'
    yds__hxrh += '    inplace=False,\n'
    yds__hxrh += '    limit=None,\n'
    yds__hxrh += '   downcast=None,\n'
    yds__hxrh += '):\n'
    yds__hxrh += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    yds__hxrh += '    n = len(in_arr)\n'
    yds__hxrh += f'    out_arr = {ywm__fugu}(n, -1)\n'
    yds__hxrh += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    yds__hxrh += '        s = in_arr[j]\n'
    yds__hxrh += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    yds__hxrh += '            s = value\n'
    yds__hxrh += '        out_arr[j] = s\n'
    yds__hxrh += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    sej__olteg = dict()
    exec(yds__hxrh, {'bodo': bodo, 'numba': numba}, sej__olteg)
    drfnm__azjkc = sej__olteg['impl']
    return drfnm__azjkc


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
    okn__uqc = bodo.hiframes.pd_series_ext.get_series_data(value)
    for nqahj__qewl in numba.parfors.parfor.internal_prange(len(yzh__zbchp)):
        s = yzh__zbchp[nqahj__qewl]
        if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl
            ) and not bodo.libs.array_kernels.isna(okn__uqc, nqahj__qewl):
            s = okn__uqc[nqahj__qewl]
        yzh__zbchp[nqahj__qewl] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
    for nqahj__qewl in numba.parfors.parfor.internal_prange(len(yzh__zbchp)):
        s = yzh__zbchp[nqahj__qewl]
        if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl):
            s = value
        yzh__zbchp[nqahj__qewl] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    okn__uqc = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(yzh__zbchp)
    vbq__zzpgl = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for bjve__tqp in numba.parfors.parfor.internal_prange(n):
        s = yzh__zbchp[bjve__tqp]
        if bodo.libs.array_kernels.isna(yzh__zbchp, bjve__tqp
            ) and not bodo.libs.array_kernels.isna(okn__uqc, bjve__tqp):
            s = okn__uqc[bjve__tqp]
        vbq__zzpgl[bjve__tqp] = s
        if bodo.libs.array_kernels.isna(yzh__zbchp, bjve__tqp
            ) and bodo.libs.array_kernels.isna(okn__uqc, bjve__tqp):
            bodo.libs.array_kernels.setna(vbq__zzpgl, bjve__tqp)
    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    okn__uqc = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(yzh__zbchp)
    vbq__zzpgl = bodo.utils.utils.alloc_type(n, yzh__zbchp.dtype, (-1,))
    for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
        s = yzh__zbchp[nqahj__qewl]
        if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl
            ) and not bodo.libs.array_kernels.isna(okn__uqc, nqahj__qewl):
            s = okn__uqc[nqahj__qewl]
        vbq__zzpgl[nqahj__qewl] = s
    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    czrpa__qjfud = dict(limit=limit, downcast=downcast)
    xjluw__afji = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    vqkke__kzkmg = not is_overload_none(value)
    tgg__ula = not is_overload_none(method)
    if vqkke__kzkmg and tgg__ula:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not vqkke__kzkmg and not tgg__ula:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if tgg__ula:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        ctbyv__egtsg = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(ctbyv__egtsg)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(ctbyv__egtsg)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    dnjct__dna = element_type(S.data)
    zyfyd__tegds = None
    if vqkke__kzkmg:
        zyfyd__tegds = element_type(types.unliteral(value))
    if zyfyd__tegds and not can_replace(dnjct__dna, zyfyd__tegds):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {zyfyd__tegds} with series type {dnjct__dna}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if S.data == bodo.dict_str_arr_type:
                raise_bodo_error(
                    "Series.fillna(): 'inplace' not supported for dictionary-encoded string arrays yet."
                    )
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        kme__ulgbb = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                okn__uqc = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(yzh__zbchp)
                vbq__zzpgl = bodo.utils.utils.alloc_type(n, kme__ulgbb, (-1,))
                for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl
                        ) and bodo.libs.array_kernels.isna(okn__uqc,
                        nqahj__qewl):
                        bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                        continue
                    if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl):
                        vbq__zzpgl[nqahj__qewl
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            okn__uqc[nqahj__qewl])
                        continue
                    vbq__zzpgl[nqahj__qewl
                        ] = bodo.utils.conversion.unbox_if_timestamp(yzh__zbchp
                        [nqahj__qewl])
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return fillna_series_impl
        if tgg__ula:
            xuzs__qgjcq = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(dnjct__dna, (types.Integer, types.Float)
                ) and dnjct__dna not in xuzs__qgjcq:
                raise BodoError(
                    f"Series.fillna(): series of type {dnjct__dna} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                vbq__zzpgl = bodo.libs.array_kernels.ffill_bfill_arr(yzh__zbchp
                    , method)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(yzh__zbchp)
            vbq__zzpgl = bodo.utils.utils.alloc_type(n, kme__ulgbb, (-1,))
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(yzh__zbchp[
                    nqahj__qewl])
                if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl):
                    s = value
                vbq__zzpgl[nqahj__qewl] = s
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        mfed__qsipt = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        czrpa__qjfud = dict(limit=limit, downcast=downcast)
        xjluw__afji = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', czrpa__qjfud,
            xjluw__afji, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        dnjct__dna = element_type(S.data)
        xuzs__qgjcq = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(dnjct__dna, (types.Integer, types.Float)
            ) and dnjct__dna not in xuzs__qgjcq:
            raise BodoError(
                f'Series.{overload_name}(): series of type {dnjct__dna} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            vbq__zzpgl = bodo.libs.array_kernels.ffill_bfill_arr(yzh__zbchp,
                mfed__qsipt)
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        dqdvw__snxt = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            dqdvw__snxt)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        dncv__bfnh = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(dncv__bfnh)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        dncv__bfnh = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(dncv__bfnh)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        dncv__bfnh = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(dncv__bfnh)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    czrpa__qjfud = dict(inplace=inplace, limit=limit, regex=regex, method=
        method)
    omoc__emt = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', czrpa__qjfud, omoc__emt,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    dnjct__dna = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        ibooq__zmfa = element_type(to_replace.key_type)
        zyfyd__tegds = element_type(to_replace.value_type)
    else:
        ibooq__zmfa = element_type(to_replace)
        zyfyd__tegds = element_type(value)
    ssb__sfy = None
    if dnjct__dna != types.unliteral(ibooq__zmfa):
        if bodo.utils.typing.equality_always_false(dnjct__dna, types.
            unliteral(ibooq__zmfa)
            ) or not bodo.utils.typing.types_equality_exists(dnjct__dna,
            ibooq__zmfa):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(dnjct__dna, (types.Float, types.Integer)
            ) or dnjct__dna == np.bool_:
            ssb__sfy = dnjct__dna
    if not can_replace(dnjct__dna, types.unliteral(zyfyd__tegds)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    oqqns__weygw = to_str_arr_if_dict_array(S.data)
    if isinstance(oqqns__weygw, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(yzh__zbchp.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(yzh__zbchp)
        vbq__zzpgl = bodo.utils.utils.alloc_type(n, oqqns__weygw, (-1,))
        wakak__qftl = build_replace_dict(to_replace, value, ssb__sfy)
        for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(yzh__zbchp, nqahj__qewl):
                bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                continue
            s = yzh__zbchp[nqahj__qewl]
            if s in wakak__qftl:
                s = wakak__qftl[s]
            vbq__zzpgl[nqahj__qewl] = s
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    djtil__yrw = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    vrp__bpmg = is_iterable_type(to_replace)
    fertu__fcneb = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    nkvxz__rbm = is_iterable_type(value)
    if djtil__yrw and fertu__fcneb:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                wakak__qftl = {}
                wakak__qftl[key_dtype_conv(to_replace)] = value
                return wakak__qftl
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            wakak__qftl = {}
            wakak__qftl[to_replace] = value
            return wakak__qftl
        return impl
    if vrp__bpmg and fertu__fcneb:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                wakak__qftl = {}
                for oupf__iee in to_replace:
                    wakak__qftl[key_dtype_conv(oupf__iee)] = value
                return wakak__qftl
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            wakak__qftl = {}
            for oupf__iee in to_replace:
                wakak__qftl[oupf__iee] = value
            return wakak__qftl
        return impl
    if vrp__bpmg and nkvxz__rbm:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                wakak__qftl = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for nqahj__qewl in range(len(to_replace)):
                    wakak__qftl[key_dtype_conv(to_replace[nqahj__qewl])
                        ] = value[nqahj__qewl]
                return wakak__qftl
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            wakak__qftl = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for nqahj__qewl in range(len(to_replace)):
                wakak__qftl[to_replace[nqahj__qewl]] = value[nqahj__qewl]
            return wakak__qftl
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.diff()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            vbq__zzpgl = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    czrpa__qjfud = dict(ignore_index=ignore_index)
    ddiam__wbeya = dict(ignore_index=False)
    check_unsupported_args('Series.explode', czrpa__qjfud, ddiam__wbeya,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rdi__oedzk = bodo.utils.conversion.index_to_array(index)
        vbq__zzpgl, jpm__kzyc = bodo.libs.array_kernels.explode(arr, rdi__oedzk
            )
        rpilp__tnu = bodo.utils.conversion.index_from_array(jpm__kzyc)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
            rpilp__tnu, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.digitize()')
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            yuke__etfp = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                yuke__etfp[nqahj__qewl] = np.argmax(a[nqahj__qewl])
            return yuke__etfp
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ocw__jxgko = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                ocw__jxgko[nqahj__qewl] = np.argmin(a[nqahj__qewl])
            return ocw__jxgko
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    czrpa__qjfud = dict(axis=axis, inplace=inplace, how=how)
    kuke__waix = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', czrpa__qjfud, kuke__waix,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            yjhek__cxtkx = S.notna().values
            rdi__oedzk = bodo.utils.conversion.extract_index_array(S)
            rpilp__tnu = bodo.utils.conversion.convert_to_index(rdi__oedzk[
                yjhek__cxtkx])
            vbq__zzpgl = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(yzh__zbchp))
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                rpilp__tnu, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            rdi__oedzk = bodo.utils.conversion.extract_index_array(S)
            yjhek__cxtkx = S.notna().values
            rpilp__tnu = bodo.utils.conversion.convert_to_index(rdi__oedzk[
                yjhek__cxtkx])
            vbq__zzpgl = yzh__zbchp[yjhek__cxtkx]
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                rpilp__tnu, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    czrpa__qjfud = dict(freq=freq, axis=axis, fill_value=fill_value)
    xjluw__afji = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.shift()')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    czrpa__qjfud = dict(fill_method=fill_method, limit=limit, freq=freq)
    xjluw__afji = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.pct_change()')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
            f'Series.{func_name}()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            f'Series.{func_name}()')
        _validate_arguments_mask_where(f'Series.{func_name}', 'Series', S,
            cond, other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            oamvf__eop = 'None'
        else:
            oamvf__eop = 'other'
        yds__hxrh = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            yds__hxrh += '  cond = ~cond\n'
        yds__hxrh += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        yds__hxrh += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        yds__hxrh += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        yds__hxrh += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {oamvf__eop})\n'
            )
        yds__hxrh += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        yewkz__dysx = {}
        exec(yds__hxrh, {'bodo': bodo, 'np': np}, yewkz__dysx)
        impl = yewkz__dysx['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        dqdvw__snxt = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(dqdvw__snxt)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    czrpa__qjfud = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    xjluw__afji = dict(inplace=False, level=None, errors='raise', try_cast=
        False)
    check_unsupported_args(f'{func_name}', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name=module_name)
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if isinstance(S, bodo.hiframes.pd_index_ext.RangeIndexType):
        arr = types.Array(types.int64, 1, 'C')
    else:
        arr = S.data
    if isinstance(other, SeriesType):
        _validate_self_other_mask_where(func_name, module_name, arr, other.data
            )
    else:
        _validate_self_other_mask_where(func_name, module_name, arr, other)
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )


def _validate_self_other_mask_where(func_name, module_name, arr, other,
    max_ndim=1, is_default=False):
    if not (isinstance(arr, types.Array) or isinstance(arr,
        BooleanArrayType) or isinstance(arr, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(arr, False) and arr.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() {module_name} data with type {arr} not yet supported'
            )
    fzyg__fyye = is_overload_constant_nan(other)
    if not (is_default or fzyg__fyye or is_scalar_type(other) or isinstance
        (other, types.Array) and other.ndim >= 1 and other.ndim <= max_ndim or
        isinstance(other, SeriesType) and (isinstance(arr, types.Array) or 
        arr.dtype in [bodo.string_type, bodo.bytes_type]) or 
        is_str_arr_type(other) and (arr.dtype == bodo.string_type or 
        isinstance(arr, bodo.CategoricalArrayType) and arr.dtype.elem_type ==
        bodo.string_type) or isinstance(other, BinaryArrayType) and (arr.
        dtype == bodo.bytes_type or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type == bodo.bytes_type) or
        (not (isinstance(other, (StringArrayType, BinaryArrayType)) or 
        other == bodo.dict_str_arr_type) and (isinstance(arr.dtype, types.
        Integer) and (bodo.utils.utils.is_array_typ(other) and isinstance(
        other.dtype, types.Integer) or is_series_type(other) and isinstance
        (other.dtype, types.Integer))) or (bodo.utils.utils.is_array_typ(
        other) and arr.dtype == other.dtype or is_series_type(other) and 
        arr.dtype == other.dtype)) and (isinstance(arr, BooleanArrayType) or
        isinstance(arr, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for {module_name}."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            cxsah__tjua = arr.dtype.elem_type
        else:
            cxsah__tjua = arr.dtype
        if is_iterable_type(other):
            twluz__kwx = other.dtype
        elif fzyg__fyye:
            twluz__kwx = types.float64
        else:
            twluz__kwx = types.unliteral(other)
        if not fzyg__fyye and not is_common_scalar_dtype([cxsah__tjua,
            twluz__kwx]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        czrpa__qjfud = dict(level=level, axis=axis)
        xjluw__afji = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__),
            czrpa__qjfud, xjluw__afji, package_name='pandas', module_name=
            'Series')
        tca__dapkf = other == string_type or is_overload_constant_str(other)
        iiyxs__hrzg = is_iterable_type(other) and other.dtype == string_type
        tdqd__ckdzi = S.dtype == string_type and (op == operator.add and (
            tca__dapkf or iiyxs__hrzg) or op == operator.mul and isinstance
            (other, types.Integer))
        htl__kxzk = S.dtype == bodo.timedelta64ns
        sug__zxrv = S.dtype == bodo.datetime64ns
        weyys__erz = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        uxy__pbx = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        jch__hdhe = htl__kxzk and (weyys__erz or uxy__pbx
            ) or sug__zxrv and weyys__erz
        jch__hdhe = jch__hdhe and op == operator.add
        if not (isinstance(S.dtype, types.Number) or tdqd__ckdzi or jch__hdhe):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        ekvg__xsi = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            oqqns__weygw = ekvg__xsi.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and oqqns__weygw == types.Array(types.bool_, 1, 'C'):
                oqqns__weygw = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                vbq__zzpgl = bodo.utils.utils.alloc_type(n, oqqns__weygw, (-1,)
                    )
                for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                    jsp__sdwy = bodo.libs.array_kernels.isna(arr, nqahj__qewl)
                    if jsp__sdwy:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(vbq__zzpgl,
                                nqahj__qewl)
                        else:
                            vbq__zzpgl[nqahj__qewl] = op(fill_value, other)
                    else:
                        vbq__zzpgl[nqahj__qewl] = op(arr[nqahj__qewl], other)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        oqqns__weygw = ekvg__xsi.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType
            ) and oqqns__weygw == types.Array(types.bool_, 1, 'C'):
            oqqns__weygw = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wnkcq__nfbix = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            vbq__zzpgl = bodo.utils.utils.alloc_type(n, oqqns__weygw, (-1,))
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                jsp__sdwy = bodo.libs.array_kernels.isna(arr, nqahj__qewl)
                sov__atpad = bodo.libs.array_kernels.isna(wnkcq__nfbix,
                    nqahj__qewl)
                if jsp__sdwy and sov__atpad:
                    bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                elif jsp__sdwy:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                    else:
                        vbq__zzpgl[nqahj__qewl] = op(fill_value,
                            wnkcq__nfbix[nqahj__qewl])
                elif sov__atpad:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                    else:
                        vbq__zzpgl[nqahj__qewl] = op(arr[nqahj__qewl],
                            fill_value)
                else:
                    vbq__zzpgl[nqahj__qewl] = op(arr[nqahj__qewl],
                        wnkcq__nfbix[nqahj__qewl])
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        ekvg__xsi = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            oqqns__weygw = ekvg__xsi.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and oqqns__weygw == types.Array(types.bool_, 1, 'C'):
                oqqns__weygw = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                vbq__zzpgl = bodo.utils.utils.alloc_type(n, oqqns__weygw, None)
                for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                    jsp__sdwy = bodo.libs.array_kernels.isna(arr, nqahj__qewl)
                    if jsp__sdwy:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(vbq__zzpgl,
                                nqahj__qewl)
                        else:
                            vbq__zzpgl[nqahj__qewl] = op(other, fill_value)
                    else:
                        vbq__zzpgl[nqahj__qewl] = op(other, arr[nqahj__qewl])
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        oqqns__weygw = ekvg__xsi.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType
            ) and oqqns__weygw == types.Array(types.bool_, 1, 'C'):
            oqqns__weygw = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wnkcq__nfbix = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            vbq__zzpgl = bodo.utils.utils.alloc_type(n, oqqns__weygw, None)
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                jsp__sdwy = bodo.libs.array_kernels.isna(arr, nqahj__qewl)
                sov__atpad = bodo.libs.array_kernels.isna(wnkcq__nfbix,
                    nqahj__qewl)
                vbq__zzpgl[nqahj__qewl] = op(wnkcq__nfbix[nqahj__qewl], arr
                    [nqahj__qewl])
                if jsp__sdwy and sov__atpad:
                    bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                elif jsp__sdwy:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                    else:
                        vbq__zzpgl[nqahj__qewl] = op(wnkcq__nfbix[
                            nqahj__qewl], fill_value)
                elif sov__atpad:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                    else:
                        vbq__zzpgl[nqahj__qewl] = op(fill_value, arr[
                            nqahj__qewl])
                else:
                    vbq__zzpgl[nqahj__qewl] = op(wnkcq__nfbix[nqahj__qewl],
                        arr[nqahj__qewl])
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, xvv__rybu in explicit_binop_funcs_two_ways.items():
        for name in xvv__rybu:
            dqdvw__snxt = create_explicit_binary_op_overload(op)
            vkk__gxr = create_explicit_binary_reverse_op_overload(op)
            ltkxu__sjy = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(dqdvw__snxt)
            overload_method(SeriesType, ltkxu__sjy, no_unliteral=True)(vkk__gxr
                )
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        dqdvw__snxt = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(dqdvw__snxt)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                pjdq__vrc = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                vbq__zzpgl = dt64_arr_sub(arr, pjdq__vrc)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                vbq__zzpgl = np.empty(n, np.dtype('datetime64[ns]'))
                for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, nqahj__qewl):
                        bodo.libs.array_kernels.setna(vbq__zzpgl, nqahj__qewl)
                        continue
                    mjekk__exhn = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[nqahj__qewl]))
                    aqwtk__laahf = op(mjekk__exhn, rhs)
                    vbq__zzpgl[nqahj__qewl
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        aqwtk__laahf.value)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    pjdq__vrc = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    vbq__zzpgl = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(pjdq__vrc))
                    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                pjdq__vrc = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                vbq__zzpgl = op(arr, pjdq__vrc)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    qah__rdn = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    vbq__zzpgl = op(bodo.utils.conversion.
                        unbox_if_timestamp(qah__rdn), arr)
                    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                qah__rdn = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                vbq__zzpgl = op(qah__rdn, arr)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        dqdvw__snxt = create_binary_op_overload(op)
        overload(op)(dqdvw__snxt)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    mpto__jixle = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, mpto__jixle)
        for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, nqahj__qewl
                ) or bodo.libs.array_kernels.isna(arg2, nqahj__qewl):
                bodo.libs.array_kernels.setna(S, nqahj__qewl)
                continue
            S[nqahj__qewl
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                nqahj__qewl]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[nqahj__qewl]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                wnkcq__nfbix = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, wnkcq__nfbix)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        dqdvw__snxt = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(dqdvw__snxt)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                vbq__zzpgl = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        dqdvw__snxt = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(dqdvw__snxt)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    vbq__zzpgl = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    wnkcq__nfbix = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    vbq__zzpgl = ufunc(arr, wnkcq__nfbix)
                    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    wnkcq__nfbix = bodo.hiframes.pd_series_ext.get_series_data(
                        S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    vbq__zzpgl = ufunc(arr, wnkcq__nfbix)
                    return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        dqdvw__snxt = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(dqdvw__snxt)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        pgmll__rnwl = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.
            copy(),))
        mogj__nzg = np.arange(n),
        bodo.libs.timsort.sort(pgmll__rnwl, 0, n, mogj__nzg)
        return mogj__nzg[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        brq__xbwg = get_overload_const_str(downcast)
        if brq__xbwg in ('integer', 'signed'):
            out_dtype = types.int64
        elif brq__xbwg == 'unsigned':
            out_dtype = types.uint64
        else:
            assert brq__xbwg == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            yzh__zbchp = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            vbq__zzpgl = pd.to_numeric(yzh__zbchp, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            nzx__jmm = np.empty(n, np.float64)
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, nqahj__qewl):
                    bodo.libs.array_kernels.setna(nzx__jmm, nqahj__qewl)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(nzx__jmm,
                        nqahj__qewl, arg_a, nqahj__qewl)
            return nzx__jmm
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            nzx__jmm = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, nqahj__qewl):
                    bodo.libs.array_kernels.setna(nzx__jmm, nqahj__qewl)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(nzx__jmm,
                        nqahj__qewl, arg_a, nqahj__qewl)
            return nzx__jmm
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        xci__fqtvm = if_series_to_array_type(args[0])
        if isinstance(xci__fqtvm, types.Array) and isinstance(xci__fqtvm.
            dtype, types.Integer):
            xci__fqtvm = types.Array(types.float64, 1, 'C')
        return xci__fqtvm(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(y,
        'numpy.where()')
    yvp__axot = bodo.utils.utils.is_array_typ(x, True)
    dwpk__akt = bodo.utils.utils.is_array_typ(y, True)
    yds__hxrh = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        yds__hxrh += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if yvp__axot and not bodo.utils.utils.is_array_typ(x, False):
        yds__hxrh += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if dwpk__akt and not bodo.utils.utils.is_array_typ(y, False):
        yds__hxrh += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    yds__hxrh += '  n = len(condition)\n'
    vmx__dop = x.dtype if yvp__axot else types.unliteral(x)
    nrrcq__kqltv = y.dtype if dwpk__akt else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        vmx__dop = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        nrrcq__kqltv = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    arh__osqty = get_data(x)
    ooiq__cse = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(mogj__nzg) for
        mogj__nzg in [arh__osqty, ooiq__cse])
    if ooiq__cse == types.none:
        if isinstance(vmx__dop, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif arh__osqty == ooiq__cse and not is_nullable:
        out_dtype = dtype_to_array_type(vmx__dop)
    elif vmx__dop == string_type or nrrcq__kqltv == string_type:
        out_dtype = bodo.string_array_type
    elif arh__osqty == bytes_type or (yvp__axot and vmx__dop == bytes_type
        ) and (ooiq__cse == bytes_type or dwpk__akt and nrrcq__kqltv ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(vmx__dop, bodo.PDCategoricalDtype):
        out_dtype = None
    elif vmx__dop in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(vmx__dop, 1, 'C')
    elif nrrcq__kqltv in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(nrrcq__kqltv, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(vmx__dop), numba.np.numpy_support.
            as_dtype(nrrcq__kqltv)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(vmx__dop, bodo.PDCategoricalDtype):
        mtp__oeqwn = 'x'
    else:
        mtp__oeqwn = 'out_dtype'
    yds__hxrh += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {mtp__oeqwn}, (-1,))\n')
    if isinstance(vmx__dop, bodo.PDCategoricalDtype):
        yds__hxrh += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        yds__hxrh += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    yds__hxrh += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    yds__hxrh += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if yvp__axot:
        yds__hxrh += '      if bodo.libs.array_kernels.isna(x, j):\n'
        yds__hxrh += '        setna(out_arr, j)\n'
        yds__hxrh += '        continue\n'
    if isinstance(vmx__dop, bodo.PDCategoricalDtype):
        yds__hxrh += '      out_codes[j] = x_codes[j]\n'
    else:
        yds__hxrh += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if yvp__axot else 'x'))
    yds__hxrh += '    else:\n'
    if dwpk__akt:
        yds__hxrh += '      if bodo.libs.array_kernels.isna(y, j):\n'
        yds__hxrh += '        setna(out_arr, j)\n'
        yds__hxrh += '        continue\n'
    if ooiq__cse == types.none:
        if isinstance(vmx__dop, bodo.PDCategoricalDtype):
            yds__hxrh += '      out_codes[j] = -1\n'
        else:
            yds__hxrh += '      setna(out_arr, j)\n'
    else:
        yds__hxrh += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if dwpk__akt else 'y'))
    yds__hxrh += '  return out_arr\n'
    yewkz__dysx = {}
    exec(yds__hxrh, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, yewkz__dysx)
    pxkrk__bhukw = yewkz__dysx['_impl']
    return pxkrk__bhukw


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        xem__ebz = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(xem__ebz, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(xem__ebz):
            klm__ssphb = xem__ebz.data.dtype
        else:
            klm__ssphb = xem__ebz.dtype
        if isinstance(klm__ssphb, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        esfr__hhuhj = xem__ebz
    else:
        lnh__qbm = []
        for xem__ebz in choicelist:
            if not bodo.utils.utils.is_array_typ(xem__ebz, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(xem__ebz):
                klm__ssphb = xem__ebz.data.dtype
            else:
                klm__ssphb = xem__ebz.dtype
            if isinstance(klm__ssphb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            lnh__qbm.append(klm__ssphb)
        if not is_common_scalar_dtype(lnh__qbm):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        esfr__hhuhj = choicelist[0]
    if is_series_type(esfr__hhuhj):
        esfr__hhuhj = esfr__hhuhj.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, esfr__hhuhj.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(esfr__hhuhj, types.Array) or isinstance(esfr__hhuhj,
        BooleanArrayType) or isinstance(esfr__hhuhj, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(esfr__hhuhj, False) and esfr__hhuhj.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {esfr__hhuhj} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    nrqrn__nalrk = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        pato__wcm = choicelist.dtype
    else:
        yja__puy = False
        lnh__qbm = []
        for xem__ebz in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(xem__ebz,
                'numpy.select()')
            if is_nullable_type(xem__ebz):
                yja__puy = True
            if is_series_type(xem__ebz):
                klm__ssphb = xem__ebz.data.dtype
            else:
                klm__ssphb = xem__ebz.dtype
            if isinstance(klm__ssphb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            lnh__qbm.append(klm__ssphb)
        exfh__soxnq, oghyl__zsv = get_common_scalar_dtype(lnh__qbm)
        if not oghyl__zsv:
            raise BodoError('Internal error in overload_np_select')
        ddca__tmjgv = dtype_to_array_type(exfh__soxnq)
        if yja__puy:
            ddca__tmjgv = to_nullable_type(ddca__tmjgv)
        pato__wcm = ddca__tmjgv
    if isinstance(pato__wcm, SeriesType):
        pato__wcm = pato__wcm.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        imahg__nudah = True
    else:
        imahg__nudah = False
    uasbq__iqb = False
    fvgjs__kis = False
    if imahg__nudah:
        if isinstance(pato__wcm.dtype, types.Number):
            pass
        elif pato__wcm.dtype == types.bool_:
            fvgjs__kis = True
        else:
            uasbq__iqb = True
            pato__wcm = to_nullable_type(pato__wcm)
    elif default == types.none or is_overload_constant_nan(default):
        uasbq__iqb = True
        pato__wcm = to_nullable_type(pato__wcm)
    yds__hxrh = 'def np_select_impl(condlist, choicelist, default=0):\n'
    yds__hxrh += '  if len(condlist) != len(choicelist):\n'
    yds__hxrh += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    yds__hxrh += '  output_len = len(choicelist[0])\n'
    yds__hxrh += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    yds__hxrh += '  for i in range(output_len):\n'
    if uasbq__iqb:
        yds__hxrh += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif fvgjs__kis:
        yds__hxrh += '    out[i] = False\n'
    else:
        yds__hxrh += '    out[i] = default\n'
    if nrqrn__nalrk:
        yds__hxrh += '  for i in range(len(condlist) - 1, -1, -1):\n'
        yds__hxrh += '    cond = condlist[i]\n'
        yds__hxrh += '    choice = choicelist[i]\n'
        yds__hxrh += '    out = np.where(cond, choice, out)\n'
    else:
        for nqahj__qewl in range(len(choicelist) - 1, -1, -1):
            yds__hxrh += f'  cond = condlist[{nqahj__qewl}]\n'
            yds__hxrh += f'  choice = choicelist[{nqahj__qewl}]\n'
            yds__hxrh += f'  out = np.where(cond, choice, out)\n'
    yds__hxrh += '  return out'
    yewkz__dysx = dict()
    exec(yds__hxrh, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': pato__wcm}, yewkz__dysx)
    impl = yewkz__dysx['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vbq__zzpgl = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    czrpa__qjfud = dict(subset=subset, keep=keep, inplace=inplace)
    xjluw__afji = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', czrpa__qjfud,
        xjluw__afji, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        kjn__yzr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (kjn__yzr,), rdi__oedzk = bodo.libs.array_kernels.drop_duplicates((
            kjn__yzr,), index, 1)
        index = bodo.utils.conversion.index_from_array(rdi__oedzk)
        return bodo.hiframes.pd_series_ext.init_series(kjn__yzr, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    qth__lxyk = element_type(S.data)
    if not is_common_scalar_dtype([qth__lxyk, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([qth__lxyk, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        vbq__zzpgl = np.empty(n, np.bool_)
        for nqahj__qewl in numba.parfors.parfor.internal_prange(n):
            rir__iewx = bodo.utils.conversion.box_if_dt64(arr[nqahj__qewl])
            if inclusive == 'both':
                vbq__zzpgl[nqahj__qewl
                    ] = rir__iewx <= right and rir__iewx >= left
            else:
                vbq__zzpgl[nqahj__qewl
                    ] = rir__iewx < right and rir__iewx > left
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    czrpa__qjfud = dict(axis=axis)
    xjluw__afji = dict(axis=None)
    check_unsupported_args('Series.repeat', czrpa__qjfud, xjluw__afji,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            rdi__oedzk = bodo.utils.conversion.index_to_array(index)
            vbq__zzpgl = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            jpm__kzyc = bodo.libs.array_kernels.repeat_kernel(rdi__oedzk,
                repeats)
            rpilp__tnu = bodo.utils.conversion.index_from_array(jpm__kzyc)
            return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
                rpilp__tnu, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rdi__oedzk = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        vbq__zzpgl = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        jpm__kzyc = bodo.libs.array_kernels.repeat_kernel(rdi__oedzk, repeats)
        rpilp__tnu = bodo.utils.conversion.index_from_array(jpm__kzyc)
        return bodo.hiframes.pd_series_ext.init_series(vbq__zzpgl,
            rpilp__tnu, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        mogj__nzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(mogj__nzg)
        joq__mrx = {}
        for nqahj__qewl in range(n):
            rir__iewx = bodo.utils.conversion.box_if_dt64(mogj__nzg[
                nqahj__qewl])
            joq__mrx[index[nqahj__qewl]] = rir__iewx
        return joq__mrx
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    ctbyv__egtsg = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            bhqmp__vyny = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(ctbyv__egtsg)
    elif is_literal_type(name):
        bhqmp__vyny = get_literal_value(name)
    else:
        raise_bodo_error(ctbyv__egtsg)
    bhqmp__vyny = 0 if bhqmp__vyny is None else bhqmp__vyny
    ecx__uul = ColNamesMetaType((bhqmp__vyny,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            ecx__uul)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
