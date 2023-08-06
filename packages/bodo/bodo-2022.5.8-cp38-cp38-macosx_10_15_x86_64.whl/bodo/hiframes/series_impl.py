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
            ars__krbeg = bodo.hiframes.pd_series_ext.get_series_data(s)
            wcpj__ghjlg = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                ars__krbeg)
            return wcpj__ghjlg
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
            yrw__crjo = list()
            for fti__prxr in range(len(S)):
                yrw__crjo.append(S.iat[fti__prxr])
            return yrw__crjo
        return impl_float

    def impl(S):
        yrw__crjo = list()
        for fti__prxr in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, fti__prxr):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            yrw__crjo.append(S.iat[fti__prxr])
        return yrw__crjo
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    bcy__acsx = dict(dtype=dtype, copy=copy, na_value=na_value)
    qobb__gjvj = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    bcy__acsx = dict(name=name, inplace=inplace)
    qobb__gjvj = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', bcy__acsx, qobb__gjvj,
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
        bbs__jds = ', '.join(['index_arrs[{}]'.format(fti__prxr) for
            fti__prxr in range(S.index.nlevels)])
    else:
        bbs__jds = '    bodo.utils.conversion.index_to_array(index)\n'
    jpqv__ccex = 'index' if 'index' != series_name else 'level_0'
    jba__vrt = get_index_names(S.index, 'Series.reset_index()', jpqv__ccex)
    columns = [name for name in jba__vrt]
    columns.append(series_name)
    wqk__wnv = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    wqk__wnv += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wqk__wnv += '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        wqk__wnv += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    wqk__wnv += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    wqk__wnv += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({bbs__jds}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    ihzp__zvugs = {}
    exec(wqk__wnv, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, ihzp__zvugs)
    boz__yxlc = ihzp__zvugs['_impl']
    return boz__yxlc


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        oedgu__ngfy = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
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
        oedgu__ngfy = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for fti__prxr in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[fti__prxr]):
                bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
            else:
                oedgu__ngfy[fti__prxr] = np.round(arr[fti__prxr], decimals)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    qobb__gjvj = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', bcy__acsx, qobb__gjvj,
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
        pyu__fppf = bodo.hiframes.pd_series_ext.get_series_data(S)
        bqi__xrfr = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        avf__irh = 0
        for fti__prxr in numba.parfors.parfor.internal_prange(len(pyu__fppf)):
            cndw__ejias = 0
            eoxbv__snh = bodo.libs.array_kernels.isna(pyu__fppf, fti__prxr)
            vwlyj__pttb = bodo.libs.array_kernels.isna(bqi__xrfr, fti__prxr)
            if (eoxbv__snh and not vwlyj__pttb or not eoxbv__snh and
                vwlyj__pttb):
                cndw__ejias = 1
            elif not eoxbv__snh:
                if pyu__fppf[fti__prxr] != bqi__xrfr[fti__prxr]:
                    cndw__ejias = 1
            avf__irh += cndw__ejias
        return avf__irh == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    bcy__acsx = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    qobb__gjvj = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    bcy__acsx = dict(level=level)
    qobb__gjvj = dict(level=None)
    check_unsupported_args('Series.mad', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    oair__bfcn = types.float64
    gwop__eesmf = types.float64
    if S.dtype == types.float32:
        oair__bfcn = types.float32
        gwop__eesmf = types.float32
    msk__jan = oair__bfcn(0)
    dch__bur = gwop__eesmf(0)
    dpk__inok = gwop__eesmf(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        chwf__mrhp = msk__jan
        avf__irh = dch__bur
        for fti__prxr in numba.parfors.parfor.internal_prange(len(A)):
            cndw__ejias = msk__jan
            mpeq__dkjyq = dch__bur
            if not bodo.libs.array_kernels.isna(A, fti__prxr) or not skipna:
                cndw__ejias = A[fti__prxr]
                mpeq__dkjyq = dpk__inok
            chwf__mrhp += cndw__ejias
            avf__irh += mpeq__dkjyq
        hxaa__mwalr = bodo.hiframes.series_kernels._mean_handle_nan(chwf__mrhp,
            avf__irh)
        pxtm__eeb = msk__jan
        for fti__prxr in numba.parfors.parfor.internal_prange(len(A)):
            cndw__ejias = msk__jan
            if not bodo.libs.array_kernels.isna(A, fti__prxr) or not skipna:
                cndw__ejias = abs(A[fti__prxr] - hxaa__mwalr)
            pxtm__eeb += cndw__ejias
        otv__ambcu = bodo.hiframes.series_kernels._mean_handle_nan(pxtm__eeb,
            avf__irh)
        return otv__ambcu
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    bcy__acsx = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', bcy__acsx, qobb__gjvj,
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
        ielht__nddb = 0
        dkiz__kjzvr = 0
        avf__irh = 0
        for fti__prxr in numba.parfors.parfor.internal_prange(len(A)):
            cndw__ejias = 0
            mpeq__dkjyq = 0
            if not bodo.libs.array_kernels.isna(A, fti__prxr) or not skipna:
                cndw__ejias = A[fti__prxr]
                mpeq__dkjyq = 1
            ielht__nddb += cndw__ejias
            dkiz__kjzvr += cndw__ejias * cndw__ejias
            avf__irh += mpeq__dkjyq
        sspzm__heo = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            ielht__nddb, dkiz__kjzvr, avf__irh, ddof)
        dwjl__zqk = bodo.hiframes.series_kernels._sem_handle_nan(sspzm__heo,
            avf__irh)
        return dwjl__zqk
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', bcy__acsx, qobb__gjvj,
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
        ielht__nddb = 0.0
        dkiz__kjzvr = 0.0
        zydv__zkr = 0.0
        ricy__pxd = 0.0
        avf__irh = 0
        for fti__prxr in numba.parfors.parfor.internal_prange(len(A)):
            cndw__ejias = 0.0
            mpeq__dkjyq = 0
            if not bodo.libs.array_kernels.isna(A, fti__prxr) or not skipna:
                cndw__ejias = np.float64(A[fti__prxr])
                mpeq__dkjyq = 1
            ielht__nddb += cndw__ejias
            dkiz__kjzvr += cndw__ejias ** 2
            zydv__zkr += cndw__ejias ** 3
            ricy__pxd += cndw__ejias ** 4
            avf__irh += mpeq__dkjyq
        sspzm__heo = bodo.hiframes.series_kernels.compute_kurt(ielht__nddb,
            dkiz__kjzvr, zydv__zkr, ricy__pxd, avf__irh)
        return sspzm__heo
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', bcy__acsx, qobb__gjvj,
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
        ielht__nddb = 0.0
        dkiz__kjzvr = 0.0
        zydv__zkr = 0.0
        avf__irh = 0
        for fti__prxr in numba.parfors.parfor.internal_prange(len(A)):
            cndw__ejias = 0.0
            mpeq__dkjyq = 0
            if not bodo.libs.array_kernels.isna(A, fti__prxr) or not skipna:
                cndw__ejias = np.float64(A[fti__prxr])
                mpeq__dkjyq = 1
            ielht__nddb += cndw__ejias
            dkiz__kjzvr += cndw__ejias ** 2
            zydv__zkr += cndw__ejias ** 3
            avf__irh += mpeq__dkjyq
        sspzm__heo = bodo.hiframes.series_kernels.compute_skew(ielht__nddb,
            dkiz__kjzvr, zydv__zkr, avf__irh)
        return sspzm__heo
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', bcy__acsx, qobb__gjvj,
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
        pyu__fppf = bodo.hiframes.pd_series_ext.get_series_data(S)
        bqi__xrfr = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        ficn__qgk = 0
        for fti__prxr in numba.parfors.parfor.internal_prange(len(pyu__fppf)):
            zpmvw__exsg = pyu__fppf[fti__prxr]
            ort__egcj = bqi__xrfr[fti__prxr]
            ficn__qgk += zpmvw__exsg * ort__egcj
        return ficn__qgk
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    bcy__acsx = dict(skipna=skipna)
    qobb__gjvj = dict(skipna=True)
    check_unsupported_args('Series.cumsum', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(skipna=skipna)
    qobb__gjvj = dict(skipna=True)
    check_unsupported_args('Series.cumprod', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(skipna=skipna)
    qobb__gjvj = dict(skipna=True)
    check_unsupported_args('Series.cummin', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(skipna=skipna)
    qobb__gjvj = dict(skipna=True)
    check_unsupported_args('Series.cummax', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    qobb__gjvj = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        jfus__zha = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, jfus__zha, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    bcy__acsx = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    qobb__gjvj = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(level=level)
    qobb__gjvj = dict(level=None)
    check_unsupported_args('Series.count', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    bcy__acsx = dict(method=method, min_periods=min_periods)
    qobb__gjvj = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        prq__hizp = S.sum()
        utld__clpq = other.sum()
        a = n * (S * other).sum() - prq__hizp * utld__clpq
        nteiq__wluet = n * (S ** 2).sum() - prq__hizp ** 2
        qkhed__wig = n * (other ** 2).sum() - utld__clpq ** 2
        return a / np.sqrt(nteiq__wluet * qkhed__wig)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    bcy__acsx = dict(min_periods=min_periods)
    qobb__gjvj = dict(min_periods=None)
    check_unsupported_args('Series.cov', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        prq__hizp = S.mean()
        utld__clpq = other.mean()
        ykba__vdd = ((S - prq__hizp) * (other - utld__clpq)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(ykba__vdd, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            qgl__nehh = np.sign(sum_val)
            return np.inf * qgl__nehh
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    bcy__acsx = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(axis=axis, skipna=skipna)
    qobb__gjvj = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(axis=axis, skipna=skipna)
    qobb__gjvj = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', bcy__acsx, qobb__gjvj,
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
    bcy__acsx = dict(level=level, numeric_only=numeric_only)
    qobb__gjvj = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', bcy__acsx, qobb__gjvj,
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
        intqt__kli = arr[:n]
        gska__gfsk = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(intqt__kli,
            gska__gfsk, name)
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
        ixqga__esojc = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        intqt__kli = arr[ixqga__esojc:]
        gska__gfsk = index[ixqga__esojc:]
        return bodo.hiframes.pd_series_ext.init_series(intqt__kli,
            gska__gfsk, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    dnhj__gxwkt = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in dnhj__gxwkt:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            bzw__gtlp = index[0]
            chrq__pjxlu = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, bzw__gtlp,
                False))
        else:
            chrq__pjxlu = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        intqt__kli = arr[:chrq__pjxlu]
        gska__gfsk = index[:chrq__pjxlu]
        return bodo.hiframes.pd_series_ext.init_series(intqt__kli,
            gska__gfsk, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    dnhj__gxwkt = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in dnhj__gxwkt:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            xea__vtq = index[-1]
            chrq__pjxlu = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, xea__vtq,
                True))
        else:
            chrq__pjxlu = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        intqt__kli = arr[len(arr) - chrq__pjxlu:]
        gska__gfsk = index[len(arr) - chrq__pjxlu:]
        return bodo.hiframes.pd_series_ext.init_series(intqt__kli,
            gska__gfsk, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        gmwp__qtxmb = bodo.utils.conversion.index_to_array(index)
        omku__hdxir, sojbj__mhy = (bodo.libs.array_kernels.
            first_last_valid_index(arr, gmwp__qtxmb))
        return sojbj__mhy if omku__hdxir else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        gmwp__qtxmb = bodo.utils.conversion.index_to_array(index)
        omku__hdxir, sojbj__mhy = (bodo.libs.array_kernels.
            first_last_valid_index(arr, gmwp__qtxmb, False))
        return sojbj__mhy if omku__hdxir else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    bcy__acsx = dict(keep=keep)
    qobb__gjvj = dict(keep='first')
    check_unsupported_args('Series.nlargest', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        gmwp__qtxmb = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        oedgu__ngfy, vauuv__ohr = bodo.libs.array_kernels.nlargest(arr,
            gmwp__qtxmb, n, True, bodo.hiframes.series_kernels.gt_f)
        hhhl__fwhxa = bodo.utils.conversion.convert_to_index(vauuv__ohr)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
            hhhl__fwhxa, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    bcy__acsx = dict(keep=keep)
    qobb__gjvj = dict(keep='first')
    check_unsupported_args('Series.nsmallest', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        gmwp__qtxmb = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        oedgu__ngfy, vauuv__ohr = bodo.libs.array_kernels.nlargest(arr,
            gmwp__qtxmb, n, False, bodo.hiframes.series_kernels.lt_f)
        hhhl__fwhxa = bodo.utils.conversion.convert_to_index(vauuv__ohr)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
            hhhl__fwhxa, name)
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
    bcy__acsx = dict(errors=errors)
    qobb__gjvj = dict(errors='raise')
    check_unsupported_args('Series.astype', bcy__acsx, qobb__gjvj,
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
        oedgu__ngfy = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    bcy__acsx = dict(axis=axis, is_copy=is_copy)
    qobb__gjvj = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        anwv__dga = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[anwv__dga],
            index[anwv__dga], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    bcy__acsx = dict(axis=axis, kind=kind, order=order)
    qobb__gjvj = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        vhcj__gpyz = S.notna().values
        if not vhcj__gpyz.all():
            oedgu__ngfy = np.full(n, -1, np.int64)
            oedgu__ngfy[vhcj__gpyz] = argsort(arr[vhcj__gpyz])
        else:
            oedgu__ngfy = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    bcy__acsx = dict(axis=axis, numeric_only=numeric_only)
    qobb__gjvj = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', bcy__acsx, qobb__gjvj,
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
        oedgu__ngfy = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    bcy__acsx = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    qobb__gjvj = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    isq__ypa = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        aos__kcpdf = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, isq__ypa)
        zyeqy__xgj = aos__kcpdf.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        oedgu__ngfy = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            zyeqy__xgj, 0)
        hhhl__fwhxa = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            zyeqy__xgj)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
            hhhl__fwhxa, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    bcy__acsx = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    qobb__gjvj = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    aso__otkb = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        aos__kcpdf = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, aso__otkb)
        zyeqy__xgj = aos__kcpdf.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        oedgu__ngfy = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            zyeqy__xgj, 0)
        hhhl__fwhxa = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            zyeqy__xgj)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
            hhhl__fwhxa, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    idzq__adbsb = is_overload_true(is_nullable)
    wqk__wnv = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    wqk__wnv += '  numba.parfors.parfor.init_prange()\n'
    wqk__wnv += '  n = len(arr)\n'
    if idzq__adbsb:
        wqk__wnv += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        wqk__wnv += '  out_arr = np.empty(n, np.int64)\n'
    wqk__wnv += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    wqk__wnv += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if idzq__adbsb:
        wqk__wnv += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        wqk__wnv += '      out_arr[i] = -1\n'
    wqk__wnv += '      continue\n'
    wqk__wnv += '    val = arr[i]\n'
    wqk__wnv += '    if include_lowest and val == bins[0]:\n'
    wqk__wnv += '      ind = 1\n'
    wqk__wnv += '    else:\n'
    wqk__wnv += '      ind = np.searchsorted(bins, val)\n'
    wqk__wnv += '    if ind == 0 or ind == len(bins):\n'
    if idzq__adbsb:
        wqk__wnv += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        wqk__wnv += '      out_arr[i] = -1\n'
    wqk__wnv += '    else:\n'
    wqk__wnv += '      out_arr[i] = ind - 1\n'
    wqk__wnv += '  return out_arr\n'
    ihzp__zvugs = {}
    exec(wqk__wnv, {'bodo': bodo, 'np': np, 'numba': numba}, ihzp__zvugs)
    impl = ihzp__zvugs['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        hvgth__sase, zhy__jia = np.divmod(x, 1)
        if hvgth__sase == 0:
            szm__mboh = -int(np.floor(np.log10(abs(zhy__jia)))) - 1 + precision
        else:
            szm__mboh = precision
        return np.around(x, szm__mboh)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        haelx__hfndg = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(haelx__hfndg)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        qtiix__pdib = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            zgopg__quzwe = bins.copy()
            if right and include_lowest:
                zgopg__quzwe[0] = zgopg__quzwe[0] - qtiix__pdib
            blynj__kxdan = bodo.libs.interval_arr_ext.init_interval_array(
                zgopg__quzwe[:-1], zgopg__quzwe[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(blynj__kxdan,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        zgopg__quzwe = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            zgopg__quzwe[0] = zgopg__quzwe[0] - 10.0 ** -precision
        blynj__kxdan = bodo.libs.interval_arr_ext.init_interval_array(
            zgopg__quzwe[:-1], zgopg__quzwe[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(blynj__kxdan,
            None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        gbk__agfri = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        ciolm__rtoap = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        oedgu__ngfy = np.zeros(nbins, np.int64)
        for fti__prxr in range(len(gbk__agfri)):
            oedgu__ngfy[ciolm__rtoap[fti__prxr]] = gbk__agfri[fti__prxr]
        return oedgu__ngfy
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
            wdaux__qcixq = (max_val - min_val) * 0.001
            if right:
                bins[0] -= wdaux__qcixq
            else:
                bins[-1] += wdaux__qcixq
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    bcy__acsx = dict(dropna=dropna)
    qobb__gjvj = dict(dropna=True)
    check_unsupported_args('Series.value_counts', bcy__acsx, qobb__gjvj,
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
    uebj__xds = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    wqk__wnv = 'def impl(\n'
    wqk__wnv += '    S,\n'
    wqk__wnv += '    normalize=False,\n'
    wqk__wnv += '    sort=True,\n'
    wqk__wnv += '    ascending=False,\n'
    wqk__wnv += '    bins=None,\n'
    wqk__wnv += '    dropna=True,\n'
    wqk__wnv += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    wqk__wnv += '):\n'
    wqk__wnv += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wqk__wnv += '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    wqk__wnv += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if uebj__xds:
        wqk__wnv += '    right = True\n'
        wqk__wnv += _gen_bins_handling(bins, S.dtype)
        wqk__wnv += '    arr = get_bin_inds(bins, arr)\n'
    wqk__wnv += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    wqk__wnv += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    wqk__wnv += '    )\n'
    wqk__wnv += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if uebj__xds:
        wqk__wnv += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        wqk__wnv += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        wqk__wnv += '    index = get_bin_labels(bins)\n'
    else:
        wqk__wnv += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        wqk__wnv += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        wqk__wnv += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        wqk__wnv += '    )\n'
        wqk__wnv += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    wqk__wnv += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        wqk__wnv += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        jzj__eee = 'len(S)' if uebj__xds else 'count_arr.sum()'
        wqk__wnv += f'    res = res / float({jzj__eee})\n'
    wqk__wnv += '    return res\n'
    ihzp__zvugs = {}
    exec(wqk__wnv, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, ihzp__zvugs)
    impl = ihzp__zvugs['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    wqk__wnv = ''
    if isinstance(bins, types.Integer):
        wqk__wnv += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        wqk__wnv += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            wqk__wnv += '    min_val = min_val.value\n'
            wqk__wnv += '    max_val = max_val.value\n'
        wqk__wnv += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            wqk__wnv += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        wqk__wnv += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return wqk__wnv


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    bcy__acsx = dict(right=right, labels=labels, retbins=retbins, precision
        =precision, duplicates=duplicates, ordered=ordered)
    qobb__gjvj = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    wqk__wnv = 'def impl(\n'
    wqk__wnv += '    x,\n'
    wqk__wnv += '    bins,\n'
    wqk__wnv += '    right=True,\n'
    wqk__wnv += '    labels=None,\n'
    wqk__wnv += '    retbins=False,\n'
    wqk__wnv += '    precision=3,\n'
    wqk__wnv += '    include_lowest=False,\n'
    wqk__wnv += "    duplicates='raise',\n"
    wqk__wnv += '    ordered=True\n'
    wqk__wnv += '):\n'
    if isinstance(x, SeriesType):
        wqk__wnv += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        wqk__wnv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        wqk__wnv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        wqk__wnv += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    wqk__wnv += _gen_bins_handling(bins, x.dtype)
    wqk__wnv += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    wqk__wnv += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    wqk__wnv += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    wqk__wnv += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        wqk__wnv += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        wqk__wnv += '    return res\n'
    else:
        wqk__wnv += '    return out_arr\n'
    ihzp__zvugs = {}
    exec(wqk__wnv, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, ihzp__zvugs)
    impl = ihzp__zvugs['impl']
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
    bcy__acsx = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    qobb__gjvj = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        tcel__oxisw = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, tcel__oxisw)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    bcy__acsx = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    qobb__gjvj = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', bcy__acsx, qobb__gjvj,
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
        dxbc__usp = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            luyg__tyud = bodo.utils.conversion.coerce_to_array(index)
            aos__kcpdf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                luyg__tyud, arr), index, dxbc__usp)
            return aos__kcpdf.groupby(' ')['']
        return impl_index
    dab__kvy = by
    if isinstance(by, SeriesType):
        dab__kvy = by.data
    if isinstance(dab__kvy, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    eyyjs__truav = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        luyg__tyud = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        aos__kcpdf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            luyg__tyud, arr), index, eyyjs__truav)
        return aos__kcpdf.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    bcy__acsx = dict(verify_integrity=verify_integrity)
    qobb__gjvj = dict(verify_integrity=False)
    check_unsupported_args('Series.append', bcy__acsx, qobb__gjvj,
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
            xif__bzjmt = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            oedgu__ngfy = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(oedgu__ngfy, A, xif__bzjmt, False)
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        oedgu__ngfy = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    bcy__acsx = dict(interpolation=interpolation)
    qobb__gjvj = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            oedgu__ngfy = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
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
        ykdib__oavtm = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(ykdib__oavtm, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    bcy__acsx = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    qobb__gjvj = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', bcy__acsx, qobb__gjvj,
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
        jxmg__pnlo = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        jxmg__pnlo = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    wqk__wnv = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {jxmg__pnlo}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    hkkhx__xls = dict()
    exec(wqk__wnv, {'bodo': bodo, 'numba': numba}, hkkhx__xls)
    fvmn__xka = hkkhx__xls['impl']
    return fvmn__xka


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        jxmg__pnlo = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        jxmg__pnlo = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    wqk__wnv = 'def impl(S,\n'
    wqk__wnv += '     value=None,\n'
    wqk__wnv += '    method=None,\n'
    wqk__wnv += '    axis=None,\n'
    wqk__wnv += '    inplace=False,\n'
    wqk__wnv += '    limit=None,\n'
    wqk__wnv += '   downcast=None,\n'
    wqk__wnv += '):\n'
    wqk__wnv += '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wqk__wnv += '    n = len(in_arr)\n'
    wqk__wnv += f'    out_arr = {jxmg__pnlo}(n, -1)\n'
    wqk__wnv += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    wqk__wnv += '        s = in_arr[j]\n'
    wqk__wnv += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    wqk__wnv += '            s = value\n'
    wqk__wnv += '        out_arr[j] = s\n'
    wqk__wnv += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    hkkhx__xls = dict()
    exec(wqk__wnv, {'bodo': bodo, 'numba': numba}, hkkhx__xls)
    fvmn__xka = hkkhx__xls['impl']
    return fvmn__xka


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
    ajis__zhv = bodo.hiframes.pd_series_ext.get_series_data(value)
    for fti__prxr in numba.parfors.parfor.internal_prange(len(qxqag__vvd)):
        s = qxqag__vvd[fti__prxr]
        if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr
            ) and not bodo.libs.array_kernels.isna(ajis__zhv, fti__prxr):
            s = ajis__zhv[fti__prxr]
        qxqag__vvd[fti__prxr] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
    for fti__prxr in numba.parfors.parfor.internal_prange(len(qxqag__vvd)):
        s = qxqag__vvd[fti__prxr]
        if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr):
            s = value
        qxqag__vvd[fti__prxr] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    ajis__zhv = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(qxqag__vvd)
    oedgu__ngfy = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for zyku__qoq in numba.parfors.parfor.internal_prange(n):
        s = qxqag__vvd[zyku__qoq]
        if bodo.libs.array_kernels.isna(qxqag__vvd, zyku__qoq
            ) and not bodo.libs.array_kernels.isna(ajis__zhv, zyku__qoq):
            s = ajis__zhv[zyku__qoq]
        oedgu__ngfy[zyku__qoq] = s
        if bodo.libs.array_kernels.isna(qxqag__vvd, zyku__qoq
            ) and bodo.libs.array_kernels.isna(ajis__zhv, zyku__qoq):
            bodo.libs.array_kernels.setna(oedgu__ngfy, zyku__qoq)
    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    ajis__zhv = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(qxqag__vvd)
    oedgu__ngfy = bodo.utils.utils.alloc_type(n, qxqag__vvd.dtype, (-1,))
    for fti__prxr in numba.parfors.parfor.internal_prange(n):
        s = qxqag__vvd[fti__prxr]
        if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr
            ) and not bodo.libs.array_kernels.isna(ajis__zhv, fti__prxr):
            s = ajis__zhv[fti__prxr]
        oedgu__ngfy[fti__prxr] = s
    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    bcy__acsx = dict(limit=limit, downcast=downcast)
    qobb__gjvj = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')
    mgte__pmx = not is_overload_none(value)
    its__rad = not is_overload_none(method)
    if mgte__pmx and its__rad:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not mgte__pmx and not its__rad:
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
    if its__rad:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        wht__nmatd = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(wht__nmatd)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(wht__nmatd)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    ufqr__vnr = element_type(S.data)
    xoca__hfgo = None
    if mgte__pmx:
        xoca__hfgo = element_type(types.unliteral(value))
    if xoca__hfgo and not can_replace(ufqr__vnr, xoca__hfgo):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {xoca__hfgo} with series type {ufqr__vnr}'
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
        vmh__end = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                ajis__zhv = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(qxqag__vvd)
                oedgu__ngfy = bodo.utils.utils.alloc_type(n, vmh__end, (-1,))
                for fti__prxr in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr
                        ) and bodo.libs.array_kernels.isna(ajis__zhv, fti__prxr
                        ):
                        bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                        continue
                    if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr):
                        oedgu__ngfy[fti__prxr
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            ajis__zhv[fti__prxr])
                        continue
                    oedgu__ngfy[fti__prxr
                        ] = bodo.utils.conversion.unbox_if_timestamp(qxqag__vvd
                        [fti__prxr])
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return fillna_series_impl
        if its__rad:
            yfu__zro = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(ufqr__vnr, (types.Integer, types.Float)
                ) and ufqr__vnr not in yfu__zro:
                raise BodoError(
                    f"Series.fillna(): series of type {ufqr__vnr} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                oedgu__ngfy = bodo.libs.array_kernels.ffill_bfill_arr(
                    qxqag__vvd, method)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(qxqag__vvd)
            oedgu__ngfy = bodo.utils.utils.alloc_type(n, vmh__end, (-1,))
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(qxqag__vvd[
                    fti__prxr])
                if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr):
                    s = value
                oedgu__ngfy[fti__prxr] = s
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        yazip__vzqds = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        bcy__acsx = dict(limit=limit, downcast=downcast)
        qobb__gjvj = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', bcy__acsx,
            qobb__gjvj, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        ufqr__vnr = element_type(S.data)
        yfu__zro = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(ufqr__vnr, (types.Integer, types.Float)
            ) and ufqr__vnr not in yfu__zro:
            raise BodoError(
                f'Series.{overload_name}(): series of type {ufqr__vnr} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            oedgu__ngfy = bodo.libs.array_kernels.ffill_bfill_arr(qxqag__vvd,
                yazip__vzqds)
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        ljg__xkkee = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            ljg__xkkee)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        soh__mhq = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(soh__mhq)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        soh__mhq = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(soh__mhq)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        soh__mhq = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(soh__mhq)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    bcy__acsx = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    gcyfg__omxbw = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', bcy__acsx, gcyfg__omxbw,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    ufqr__vnr = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        kgta__ddn = element_type(to_replace.key_type)
        xoca__hfgo = element_type(to_replace.value_type)
    else:
        kgta__ddn = element_type(to_replace)
        xoca__hfgo = element_type(value)
    tbgua__jrglr = None
    if ufqr__vnr != types.unliteral(kgta__ddn):
        if bodo.utils.typing.equality_always_false(ufqr__vnr, types.
            unliteral(kgta__ddn)
            ) or not bodo.utils.typing.types_equality_exists(ufqr__vnr,
            kgta__ddn):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(ufqr__vnr, (types.Float, types.Integer)
            ) or ufqr__vnr == np.bool_:
            tbgua__jrglr = ufqr__vnr
    if not can_replace(ufqr__vnr, types.unliteral(xoca__hfgo)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    twzcn__ixh = to_str_arr_if_dict_array(S.data)
    if isinstance(twzcn__ixh, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(qxqag__vvd.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(qxqag__vvd)
        oedgu__ngfy = bodo.utils.utils.alloc_type(n, twzcn__ixh, (-1,))
        amw__gnpx = build_replace_dict(to_replace, value, tbgua__jrglr)
        for fti__prxr in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(qxqag__vvd, fti__prxr):
                bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                continue
            s = qxqag__vvd[fti__prxr]
            if s in amw__gnpx:
                s = amw__gnpx[s]
            oedgu__ngfy[fti__prxr] = s
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    agy__otpsf = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    ofz__ihs = is_iterable_type(to_replace)
    hdi__uwubb = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    janer__tayg = is_iterable_type(value)
    if agy__otpsf and hdi__uwubb:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                amw__gnpx = {}
                amw__gnpx[key_dtype_conv(to_replace)] = value
                return amw__gnpx
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            amw__gnpx = {}
            amw__gnpx[to_replace] = value
            return amw__gnpx
        return impl
    if ofz__ihs and hdi__uwubb:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                amw__gnpx = {}
                for kyryt__kkj in to_replace:
                    amw__gnpx[key_dtype_conv(kyryt__kkj)] = value
                return amw__gnpx
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            amw__gnpx = {}
            for kyryt__kkj in to_replace:
                amw__gnpx[kyryt__kkj] = value
            return amw__gnpx
        return impl
    if ofz__ihs and janer__tayg:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                amw__gnpx = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for fti__prxr in range(len(to_replace)):
                    amw__gnpx[key_dtype_conv(to_replace[fti__prxr])] = value[
                        fti__prxr]
                return amw__gnpx
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            amw__gnpx = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for fti__prxr in range(len(to_replace)):
                amw__gnpx[to_replace[fti__prxr]] = value[fti__prxr]
            return amw__gnpx
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
            oedgu__ngfy = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        oedgu__ngfy = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    bcy__acsx = dict(ignore_index=ignore_index)
    svg__nnfsa = dict(ignore_index=False)
    check_unsupported_args('Series.explode', bcy__acsx, svg__nnfsa,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gmwp__qtxmb = bodo.utils.conversion.index_to_array(index)
        oedgu__ngfy, xoma__fdns = bodo.libs.array_kernels.explode(arr,
            gmwp__qtxmb)
        hhhl__fwhxa = bodo.utils.conversion.index_from_array(xoma__fdns)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
            hhhl__fwhxa, name)
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
            qsvx__mtple = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                qsvx__mtple[fti__prxr] = np.argmax(a[fti__prxr])
            return qsvx__mtple
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ngwj__mctm = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                ngwj__mctm[fti__prxr] = np.argmin(a[fti__prxr])
            return ngwj__mctm
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
    bcy__acsx = dict(axis=axis, inplace=inplace, how=how)
    rxhpy__yfhf = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', bcy__acsx, rxhpy__yfhf,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            vhcj__gpyz = S.notna().values
            gmwp__qtxmb = bodo.utils.conversion.extract_index_array(S)
            hhhl__fwhxa = bodo.utils.conversion.convert_to_index(gmwp__qtxmb
                [vhcj__gpyz])
            oedgu__ngfy = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(qxqag__vvd))
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                hhhl__fwhxa, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            gmwp__qtxmb = bodo.utils.conversion.extract_index_array(S)
            vhcj__gpyz = S.notna().values
            hhhl__fwhxa = bodo.utils.conversion.convert_to_index(gmwp__qtxmb
                [vhcj__gpyz])
            oedgu__ngfy = qxqag__vvd[vhcj__gpyz]
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                hhhl__fwhxa, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    bcy__acsx = dict(freq=freq, axis=axis, fill_value=fill_value)
    qobb__gjvj = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', bcy__acsx, qobb__gjvj,
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
        oedgu__ngfy = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    bcy__acsx = dict(fill_method=fill_method, limit=limit, freq=freq)
    qobb__gjvj = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', bcy__acsx, qobb__gjvj,
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
        oedgu__ngfy = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
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
            izb__sjh = 'None'
        else:
            izb__sjh = 'other'
        wqk__wnv = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            wqk__wnv += '  cond = ~cond\n'
        wqk__wnv += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        wqk__wnv += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wqk__wnv += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
        wqk__wnv += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {izb__sjh})\n'
            )
        wqk__wnv += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        ihzp__zvugs = {}
        exec(wqk__wnv, {'bodo': bodo, 'np': np}, ihzp__zvugs)
        impl = ihzp__zvugs['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        ljg__xkkee = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(ljg__xkkee)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    bcy__acsx = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    qobb__gjvj = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', bcy__acsx, qobb__gjvj,
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
    dbsmr__vdj = is_overload_constant_nan(other)
    if not (is_default or dbsmr__vdj or is_scalar_type(other) or isinstance
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
            spfv__wwaav = arr.dtype.elem_type
        else:
            spfv__wwaav = arr.dtype
        if is_iterable_type(other):
            owwe__twmxj = other.dtype
        elif dbsmr__vdj:
            owwe__twmxj = types.float64
        else:
            owwe__twmxj = types.unliteral(other)
        if not dbsmr__vdj and not is_common_scalar_dtype([spfv__wwaav,
            owwe__twmxj]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        bcy__acsx = dict(level=level, axis=axis)
        qobb__gjvj = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), bcy__acsx,
            qobb__gjvj, package_name='pandas', module_name='Series')
        omwn__svolp = other == string_type or is_overload_constant_str(other)
        zup__jbsy = is_iterable_type(other) and other.dtype == string_type
        qsd__pfe = S.dtype == string_type and (op == operator.add and (
            omwn__svolp or zup__jbsy) or op == operator.mul and isinstance(
            other, types.Integer))
        ciuha__kqxpq = S.dtype == bodo.timedelta64ns
        hibcp__bmf = S.dtype == bodo.datetime64ns
        lfvz__uxa = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        zif__eov = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        cry__vnc = ciuha__kqxpq and (lfvz__uxa or zif__eov
            ) or hibcp__bmf and lfvz__uxa
        cry__vnc = cry__vnc and op == operator.add
        if not (isinstance(S.dtype, types.Number) or qsd__pfe or cry__vnc):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        qhbw__zhgg = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            twzcn__ixh = qhbw__zhgg.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and twzcn__ixh == types.Array(types.bool_, 1, 'C'):
                twzcn__ixh = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                oedgu__ngfy = bodo.utils.utils.alloc_type(n, twzcn__ixh, (-1,))
                for fti__prxr in numba.parfors.parfor.internal_prange(n):
                    bsss__lcm = bodo.libs.array_kernels.isna(arr, fti__prxr)
                    if bsss__lcm:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(oedgu__ngfy,
                                fti__prxr)
                        else:
                            oedgu__ngfy[fti__prxr] = op(fill_value, other)
                    else:
                        oedgu__ngfy[fti__prxr] = op(arr[fti__prxr], other)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        twzcn__ixh = qhbw__zhgg.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and twzcn__ixh == types.Array(
            types.bool_, 1, 'C'):
            twzcn__ixh = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            atxrf__ixo = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            oedgu__ngfy = bodo.utils.utils.alloc_type(n, twzcn__ixh, (-1,))
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                bsss__lcm = bodo.libs.array_kernels.isna(arr, fti__prxr)
                hljq__hqj = bodo.libs.array_kernels.isna(atxrf__ixo, fti__prxr)
                if bsss__lcm and hljq__hqj:
                    bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                elif bsss__lcm:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                    else:
                        oedgu__ngfy[fti__prxr] = op(fill_value, atxrf__ixo[
                            fti__prxr])
                elif hljq__hqj:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                    else:
                        oedgu__ngfy[fti__prxr] = op(arr[fti__prxr], fill_value)
                else:
                    oedgu__ngfy[fti__prxr] = op(arr[fti__prxr], atxrf__ixo[
                        fti__prxr])
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
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
        qhbw__zhgg = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            twzcn__ixh = qhbw__zhgg.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and twzcn__ixh == types.Array(types.bool_, 1, 'C'):
                twzcn__ixh = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                oedgu__ngfy = bodo.utils.utils.alloc_type(n, twzcn__ixh, None)
                for fti__prxr in numba.parfors.parfor.internal_prange(n):
                    bsss__lcm = bodo.libs.array_kernels.isna(arr, fti__prxr)
                    if bsss__lcm:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(oedgu__ngfy,
                                fti__prxr)
                        else:
                            oedgu__ngfy[fti__prxr] = op(other, fill_value)
                    else:
                        oedgu__ngfy[fti__prxr] = op(other, arr[fti__prxr])
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        twzcn__ixh = qhbw__zhgg.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and twzcn__ixh == types.Array(
            types.bool_, 1, 'C'):
            twzcn__ixh = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            atxrf__ixo = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            oedgu__ngfy = bodo.utils.utils.alloc_type(n, twzcn__ixh, None)
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                bsss__lcm = bodo.libs.array_kernels.isna(arr, fti__prxr)
                hljq__hqj = bodo.libs.array_kernels.isna(atxrf__ixo, fti__prxr)
                oedgu__ngfy[fti__prxr] = op(atxrf__ixo[fti__prxr], arr[
                    fti__prxr])
                if bsss__lcm and hljq__hqj:
                    bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                elif bsss__lcm:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                    else:
                        oedgu__ngfy[fti__prxr] = op(atxrf__ixo[fti__prxr],
                            fill_value)
                elif hljq__hqj:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                    else:
                        oedgu__ngfy[fti__prxr] = op(fill_value, arr[fti__prxr])
                else:
                    oedgu__ngfy[fti__prxr] = op(atxrf__ixo[fti__prxr], arr[
                        fti__prxr])
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
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
    for op, xhlr__yhlsj in explicit_binop_funcs_two_ways.items():
        for name in xhlr__yhlsj:
            ljg__xkkee = create_explicit_binary_op_overload(op)
            pigh__rna = create_explicit_binary_reverse_op_overload(op)
            vwmrq__tgh = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(ljg__xkkee)
            overload_method(SeriesType, vwmrq__tgh, no_unliteral=True)(
                pigh__rna)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        ljg__xkkee = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(ljg__xkkee)
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
                lse__qtor = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                oedgu__ngfy = dt64_arr_sub(arr, lse__qtor)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
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
                oedgu__ngfy = np.empty(n, np.dtype('datetime64[ns]'))
                for fti__prxr in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, fti__prxr):
                        bodo.libs.array_kernels.setna(oedgu__ngfy, fti__prxr)
                        continue
                    bgck__bzy = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[fti__prxr]))
                    lfgt__tzxj = op(bgck__bzy, rhs)
                    oedgu__ngfy[fti__prxr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        lfgt__tzxj.value)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
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
                    lse__qtor = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    oedgu__ngfy = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(lse__qtor))
                    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lse__qtor = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                oedgu__ngfy = op(arr, lse__qtor)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    wns__psk = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    oedgu__ngfy = op(bodo.utils.conversion.
                        unbox_if_timestamp(wns__psk), arr)
                    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wns__psk = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                oedgu__ngfy = op(wns__psk, arr)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        ljg__xkkee = create_binary_op_overload(op)
        overload(op)(ljg__xkkee)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    alglo__ijfvp = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, alglo__ijfvp)
        for fti__prxr in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, fti__prxr
                ) or bodo.libs.array_kernels.isna(arg2, fti__prxr):
                bodo.libs.array_kernels.setna(S, fti__prxr)
                continue
            S[fti__prxr
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                fti__prxr]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[fti__prxr]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                atxrf__ixo = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, atxrf__ixo)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        ljg__xkkee = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(ljg__xkkee)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                oedgu__ngfy = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        ljg__xkkee = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(ljg__xkkee)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    oedgu__ngfy = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
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
                    atxrf__ixo = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    oedgu__ngfy = ufunc(arr, atxrf__ixo)
                    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    atxrf__ixo = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    oedgu__ngfy = ufunc(arr, atxrf__ixo)
                    return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        ljg__xkkee = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(ljg__xkkee)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        cxq__ckxcc = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        ars__krbeg = np.arange(n),
        bodo.libs.timsort.sort(cxq__ckxcc, 0, n, ars__krbeg)
        return ars__krbeg[0]
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
        gtnqg__gpne = get_overload_const_str(downcast)
        if gtnqg__gpne in ('integer', 'signed'):
            out_dtype = types.int64
        elif gtnqg__gpne == 'unsigned':
            out_dtype = types.uint64
        else:
            assert gtnqg__gpne == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            qxqag__vvd = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            oedgu__ngfy = pd.to_numeric(qxqag__vvd, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            shvo__env = np.empty(n, np.float64)
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, fti__prxr):
                    bodo.libs.array_kernels.setna(shvo__env, fti__prxr)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(shvo__env,
                        fti__prxr, arg_a, fti__prxr)
            return shvo__env
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            shvo__env = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for fti__prxr in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, fti__prxr):
                    bodo.libs.array_kernels.setna(shvo__env, fti__prxr)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(shvo__env,
                        fti__prxr, arg_a, fti__prxr)
            return shvo__env
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        kdk__umxxf = if_series_to_array_type(args[0])
        if isinstance(kdk__umxxf, types.Array) and isinstance(kdk__umxxf.
            dtype, types.Integer):
            kdk__umxxf = types.Array(types.float64, 1, 'C')
        return kdk__umxxf(*args)


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
    ydoth__bmmwj = bodo.utils.utils.is_array_typ(x, True)
    sztmu__lyq = bodo.utils.utils.is_array_typ(y, True)
    wqk__wnv = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        wqk__wnv += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if ydoth__bmmwj and not bodo.utils.utils.is_array_typ(x, False):
        wqk__wnv += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if sztmu__lyq and not bodo.utils.utils.is_array_typ(y, False):
        wqk__wnv += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    wqk__wnv += '  n = len(condition)\n'
    uyq__btdm = x.dtype if ydoth__bmmwj else types.unliteral(x)
    oat__deb = y.dtype if sztmu__lyq else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        uyq__btdm = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        oat__deb = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    lazca__moysy = get_data(x)
    raude__dvy = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(ars__krbeg) for
        ars__krbeg in [lazca__moysy, raude__dvy])
    if raude__dvy == types.none:
        if isinstance(uyq__btdm, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif lazca__moysy == raude__dvy and not is_nullable:
        out_dtype = dtype_to_array_type(uyq__btdm)
    elif uyq__btdm == string_type or oat__deb == string_type:
        out_dtype = bodo.string_array_type
    elif lazca__moysy == bytes_type or (ydoth__bmmwj and uyq__btdm ==
        bytes_type) and (raude__dvy == bytes_type or sztmu__lyq and 
        oat__deb == bytes_type):
        out_dtype = binary_array_type
    elif isinstance(uyq__btdm, bodo.PDCategoricalDtype):
        out_dtype = None
    elif uyq__btdm in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(uyq__btdm, 1, 'C')
    elif oat__deb in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(oat__deb, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(uyq__btdm), numba.np.numpy_support.
            as_dtype(oat__deb)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(uyq__btdm, bodo.PDCategoricalDtype):
        xgu__wxoru = 'x'
    else:
        xgu__wxoru = 'out_dtype'
    wqk__wnv += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {xgu__wxoru}, (-1,))\n')
    if isinstance(uyq__btdm, bodo.PDCategoricalDtype):
        wqk__wnv += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        wqk__wnv += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    wqk__wnv += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    wqk__wnv += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if ydoth__bmmwj:
        wqk__wnv += '      if bodo.libs.array_kernels.isna(x, j):\n'
        wqk__wnv += '        setna(out_arr, j)\n'
        wqk__wnv += '        continue\n'
    if isinstance(uyq__btdm, bodo.PDCategoricalDtype):
        wqk__wnv += '      out_codes[j] = x_codes[j]\n'
    else:
        wqk__wnv += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if ydoth__bmmwj else 'x'))
    wqk__wnv += '    else:\n'
    if sztmu__lyq:
        wqk__wnv += '      if bodo.libs.array_kernels.isna(y, j):\n'
        wqk__wnv += '        setna(out_arr, j)\n'
        wqk__wnv += '        continue\n'
    if raude__dvy == types.none:
        if isinstance(uyq__btdm, bodo.PDCategoricalDtype):
            wqk__wnv += '      out_codes[j] = -1\n'
        else:
            wqk__wnv += '      setna(out_arr, j)\n'
    else:
        wqk__wnv += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if sztmu__lyq else 'y'))
    wqk__wnv += '  return out_arr\n'
    ihzp__zvugs = {}
    exec(wqk__wnv, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, ihzp__zvugs)
    boz__yxlc = ihzp__zvugs['_impl']
    return boz__yxlc


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
        fmdhb__oaegc = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(fmdhb__oaegc, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(fmdhb__oaegc):
            kyg__aijdw = fmdhb__oaegc.data.dtype
        else:
            kyg__aijdw = fmdhb__oaegc.dtype
        if isinstance(kyg__aijdw, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        gma__tqmzk = fmdhb__oaegc
    else:
        mwwf__vgsxq = []
        for fmdhb__oaegc in choicelist:
            if not bodo.utils.utils.is_array_typ(fmdhb__oaegc, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(fmdhb__oaegc):
                kyg__aijdw = fmdhb__oaegc.data.dtype
            else:
                kyg__aijdw = fmdhb__oaegc.dtype
            if isinstance(kyg__aijdw, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mwwf__vgsxq.append(kyg__aijdw)
        if not is_common_scalar_dtype(mwwf__vgsxq):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        gma__tqmzk = choicelist[0]
    if is_series_type(gma__tqmzk):
        gma__tqmzk = gma__tqmzk.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, gma__tqmzk.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(gma__tqmzk, types.Array) or isinstance(gma__tqmzk,
        BooleanArrayType) or isinstance(gma__tqmzk, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(gma__tqmzk, False) and gma__tqmzk.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {gma__tqmzk} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    pvur__wuklg = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        rewy__lfne = choicelist.dtype
    else:
        epw__tiwn = False
        mwwf__vgsxq = []
        for fmdhb__oaegc in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                fmdhb__oaegc, 'numpy.select()')
            if is_nullable_type(fmdhb__oaegc):
                epw__tiwn = True
            if is_series_type(fmdhb__oaegc):
                kyg__aijdw = fmdhb__oaegc.data.dtype
            else:
                kyg__aijdw = fmdhb__oaegc.dtype
            if isinstance(kyg__aijdw, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mwwf__vgsxq.append(kyg__aijdw)
        qzcmm__lhwww, acy__squ = get_common_scalar_dtype(mwwf__vgsxq)
        if not acy__squ:
            raise BodoError('Internal error in overload_np_select')
        mxjf__wbmeu = dtype_to_array_type(qzcmm__lhwww)
        if epw__tiwn:
            mxjf__wbmeu = to_nullable_type(mxjf__wbmeu)
        rewy__lfne = mxjf__wbmeu
    if isinstance(rewy__lfne, SeriesType):
        rewy__lfne = rewy__lfne.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        mzcv__kpbp = True
    else:
        mzcv__kpbp = False
    elg__bzp = False
    mfe__febfe = False
    if mzcv__kpbp:
        if isinstance(rewy__lfne.dtype, types.Number):
            pass
        elif rewy__lfne.dtype == types.bool_:
            mfe__febfe = True
        else:
            elg__bzp = True
            rewy__lfne = to_nullable_type(rewy__lfne)
    elif default == types.none or is_overload_constant_nan(default):
        elg__bzp = True
        rewy__lfne = to_nullable_type(rewy__lfne)
    wqk__wnv = 'def np_select_impl(condlist, choicelist, default=0):\n'
    wqk__wnv += '  if len(condlist) != len(choicelist):\n'
    wqk__wnv += (
        "    raise ValueError('list of cases must be same length as list of conditions')\n"
        )
    wqk__wnv += '  output_len = len(choicelist[0])\n'
    wqk__wnv += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    wqk__wnv += '  for i in range(output_len):\n'
    if elg__bzp:
        wqk__wnv += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif mfe__febfe:
        wqk__wnv += '    out[i] = False\n'
    else:
        wqk__wnv += '    out[i] = default\n'
    if pvur__wuklg:
        wqk__wnv += '  for i in range(len(condlist) - 1, -1, -1):\n'
        wqk__wnv += '    cond = condlist[i]\n'
        wqk__wnv += '    choice = choicelist[i]\n'
        wqk__wnv += '    out = np.where(cond, choice, out)\n'
    else:
        for fti__prxr in range(len(choicelist) - 1, -1, -1):
            wqk__wnv += f'  cond = condlist[{fti__prxr}]\n'
            wqk__wnv += f'  choice = choicelist[{fti__prxr}]\n'
            wqk__wnv += f'  out = np.where(cond, choice, out)\n'
    wqk__wnv += '  return out'
    ihzp__zvugs = dict()
    exec(wqk__wnv, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': rewy__lfne}, ihzp__zvugs)
    impl = ihzp__zvugs['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        oedgu__ngfy = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    bcy__acsx = dict(subset=subset, keep=keep, inplace=inplace)
    qobb__gjvj = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', bcy__acsx, qobb__gjvj,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        tywt__zzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (tywt__zzg,), gmwp__qtxmb = bodo.libs.array_kernels.drop_duplicates((
            tywt__zzg,), index, 1)
        index = bodo.utils.conversion.index_from_array(gmwp__qtxmb)
        return bodo.hiframes.pd_series_ext.init_series(tywt__zzg, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    qrbgn__dpa = element_type(S.data)
    if not is_common_scalar_dtype([qrbgn__dpa, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([qrbgn__dpa, right]):
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
        oedgu__ngfy = np.empty(n, np.bool_)
        for fti__prxr in numba.parfors.parfor.internal_prange(n):
            cndw__ejias = bodo.utils.conversion.box_if_dt64(arr[fti__prxr])
            if inclusive == 'both':
                oedgu__ngfy[fti__prxr
                    ] = cndw__ejias <= right and cndw__ejias >= left
            else:
                oedgu__ngfy[fti__prxr
                    ] = cndw__ejias < right and cndw__ejias > left
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy, index, name
            )
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    bcy__acsx = dict(axis=axis)
    qobb__gjvj = dict(axis=None)
    check_unsupported_args('Series.repeat', bcy__acsx, qobb__gjvj,
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
            gmwp__qtxmb = bodo.utils.conversion.index_to_array(index)
            oedgu__ngfy = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            xoma__fdns = bodo.libs.array_kernels.repeat_kernel(gmwp__qtxmb,
                repeats)
            hhhl__fwhxa = bodo.utils.conversion.index_from_array(xoma__fdns)
            return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
                hhhl__fwhxa, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gmwp__qtxmb = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        oedgu__ngfy = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        xoma__fdns = bodo.libs.array_kernels.repeat_kernel(gmwp__qtxmb, repeats
            )
        hhhl__fwhxa = bodo.utils.conversion.index_from_array(xoma__fdns)
        return bodo.hiframes.pd_series_ext.init_series(oedgu__ngfy,
            hhhl__fwhxa, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        ars__krbeg = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(ars__krbeg)
        ptcc__ljp = {}
        for fti__prxr in range(n):
            cndw__ejias = bodo.utils.conversion.box_if_dt64(ars__krbeg[
                fti__prxr])
            ptcc__ljp[index[fti__prxr]] = cndw__ejias
        return ptcc__ljp
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    wht__nmatd = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            zip__csdj = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(wht__nmatd)
    elif is_literal_type(name):
        zip__csdj = get_literal_value(name)
    else:
        raise_bodo_error(wht__nmatd)
    zip__csdj = 0 if zip__csdj is None else zip__csdj
    efsfq__lhes = ColNamesMetaType((zip__csdj,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            efsfq__lhes)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
