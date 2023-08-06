"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_getattr, models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import DatetimeIndexType, RangeIndexType, StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array, boolean_dtype
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, parse_dtype, raise_bodo_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        xcwwk__vwbl = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({xcwwk__vwbl})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    hmxk__zpbx = 'def impl(df):\n'
    if df.has_runtime_cols:
        hmxk__zpbx += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        pqo__ikvz = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        hmxk__zpbx += f'  return {pqo__ikvz}'
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    qwwxc__cvzl = len(df.columns)
    pxu__kgc = set(i for i in range(qwwxc__cvzl) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in pxu__kgc else '') for i in range
        (qwwxc__cvzl))
    hmxk__zpbx = 'def f(df):\n'.format()
    hmxk__zpbx += '    return np.stack(({},), 1)\n'.format(data_args)
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'np': np}, xzs__zjb)
    ixpek__afser = xzs__zjb['f']
    return ixpek__afser


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    yhkh__heuqh = {'dtype': dtype, 'na_value': na_value}
    lrjt__qwwg = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', yhkh__heuqh, lrjt__qwwg,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            wkrlc__uui = bodo.hiframes.table.compute_num_runtime_columns(t)
            return wkrlc__uui * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@lower_getattr(DataFrameType, 'shape')
def lower_dataframe_shape(context, builder, typ, val):
    impl = overload_dataframe_shape(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            wkrlc__uui = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), wkrlc__uui
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    hmxk__zpbx = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    pcpk__yhq = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    hmxk__zpbx += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{pcpk__yhq}), {index}, None)
"""
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if type(dtype) in bodo.libs.int_arr_ext.pd_int_dtype_classes:
        return dtype.name
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if isinstance(dtype, types.PyObject) or dtype in (object, 'object'):
        return "'object'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True, _bodo_object_typeref=None):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.astype()')
    yhkh__heuqh = {'copy': copy, 'errors': errors}
    lrjt__qwwg = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', yhkh__heuqh, lrjt__qwwg,
        package_name='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    header = """def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True, _bodo_object_typeref=None):
"""
    if df.is_table_format:
        extra_globals = {}
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        tfvc__ufyod = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        xbfkh__ckhk = _bodo_object_typeref.instance_type
        assert isinstance(xbfkh__ckhk, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in xbfkh__ckhk.column_index:
                    idx = xbfkh__ckhk.column_index[name]
                    arr_typ = xbfkh__ckhk.data[idx]
                else:
                    arr_typ = df.data[i]
                tfvc__ufyod.append(arr_typ)
        else:
            extra_globals = {}
            bxal__uqf = {}
            for i, name in enumerate(xbfkh__ckhk.columns):
                arr_typ = xbfkh__ckhk.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    pnjb__oelra = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    pnjb__oelra = boolean_dtype
                else:
                    pnjb__oelra = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = pnjb__oelra
                bxal__uqf[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {bxal__uqf[wqcpl__ikv]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if wqcpl__ikv in bxal__uqf else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, wqcpl__ikv in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        ftggc__dfgm = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            ftggc__dfgm = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in ftggc__dfgm.items()}
            for i, name in enumerate(df.columns):
                if name in ftggc__dfgm:
                    arr_typ = ftggc__dfgm[name]
                else:
                    arr_typ = df.data[i]
                tfvc__ufyod.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(ftggc__dfgm[wqcpl__ikv])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if wqcpl__ikv in ftggc__dfgm else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, wqcpl__ikv in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        tfvc__ufyod = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        cvas__ghssc = bodo.TableType(tuple(tfvc__ufyod))
        extra_globals['out_table_typ'] = cvas__ghssc
        data_args = (
            'bodo.utils.table_utils.table_astype(table, out_table_typ, copy, _bodo_nan_to_str)'
            )
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    header = 'def impl(df, deep=True):\n'
    extra_globals = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        dtk__nbfvh = types.none
        extra_globals = {'output_arr_typ': dtk__nbfvh}
        if is_overload_false(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if deep else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        kanpc__iatf = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                kanpc__iatf.append(arr + '.copy()')
            elif is_overload_false(deep):
                kanpc__iatf.append(arr)
            else:
                kanpc__iatf.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(kanpc__iatf)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    yhkh__heuqh = {'index': index, 'level': level, 'errors': errors}
    lrjt__qwwg = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', yhkh__heuqh, lrjt__qwwg,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        ema__onh = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ema__onh = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    vyrx__yvj = tuple([ema__onh.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    nupz__henu = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        nupz__henu = df.copy(columns=vyrx__yvj)
        dtk__nbfvh = types.none
        extra_globals = {'output_arr_typ': dtk__nbfvh}
        if is_overload_false(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if copy else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        kanpc__iatf = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                kanpc__iatf.append(arr + '.copy()')
            elif is_overload_false(copy):
                kanpc__iatf.append(arr)
            else:
                kanpc__iatf.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(kanpc__iatf)
    return _gen_init_df(header, vyrx__yvj, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    dqoe__vymv = not is_overload_none(items)
    selxu__wxw = not is_overload_none(like)
    pyn__detqb = not is_overload_none(regex)
    cth__qxksz = dqoe__vymv ^ selxu__wxw ^ pyn__detqb
    aph__rpjgn = not (dqoe__vymv or selxu__wxw or pyn__detqb)
    if aph__rpjgn:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not cth__qxksz:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        rjh__unrct = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        rjh__unrct = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert rjh__unrct in {0, 1}
    hmxk__zpbx = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if rjh__unrct == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if rjh__unrct == 1:
        jtswo__eaws = []
        rdil__zzmm = []
        kqy__vsfgz = []
        if dqoe__vymv:
            if is_overload_constant_list(items):
                iocg__ifyx = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if selxu__wxw:
            if is_overload_constant_str(like):
                owtqe__jfws = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if pyn__detqb:
            if is_overload_constant_str(regex):
                ehke__iuang = get_overload_const_str(regex)
                uniw__evhl = re.compile(ehke__iuang)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, wqcpl__ikv in enumerate(df.columns):
            if not is_overload_none(items
                ) and wqcpl__ikv in iocg__ifyx or not is_overload_none(like
                ) and owtqe__jfws in str(wqcpl__ikv) or not is_overload_none(
                regex) and uniw__evhl.search(str(wqcpl__ikv)):
                rdil__zzmm.append(wqcpl__ikv)
                kqy__vsfgz.append(i)
        for i in kqy__vsfgz:
            var_name = f'data_{i}'
            jtswo__eaws.append(var_name)
            hmxk__zpbx += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(jtswo__eaws)
        return _gen_init_df(hmxk__zpbx, rdil__zzmm, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    nupz__henu = None
    if df.is_table_format:
        dtk__nbfvh = types.Array(types.bool_, 1, 'C')
        nupz__henu = DataFrameType(tuple([dtk__nbfvh] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': dtk__nbfvh}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    hqeku__xaet = is_overload_none(include)
    dohei__rsbms = is_overload_none(exclude)
    wze__nhij = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if hqeku__xaet and dohei__rsbms:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not hqeku__xaet:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            jvdko__zewe = [dtype_to_array_type(parse_dtype(elem, wze__nhij)
                ) for elem in include]
        elif is_legal_input(include):
            jvdko__zewe = [dtype_to_array_type(parse_dtype(include, wze__nhij))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        jvdko__zewe = get_nullable_and_non_nullable_types(jvdko__zewe)
        sxcjz__xbkj = tuple(wqcpl__ikv for i, wqcpl__ikv in enumerate(df.
            columns) if df.data[i] in jvdko__zewe)
    else:
        sxcjz__xbkj = df.columns
    if not dohei__rsbms:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            xdm__fkwt = [dtype_to_array_type(parse_dtype(elem, wze__nhij)) for
                elem in exclude]
        elif is_legal_input(exclude):
            xdm__fkwt = [dtype_to_array_type(parse_dtype(exclude, wze__nhij))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        xdm__fkwt = get_nullable_and_non_nullable_types(xdm__fkwt)
        sxcjz__xbkj = tuple(wqcpl__ikv for wqcpl__ikv in sxcjz__xbkj if df.
            data[df.column_index[wqcpl__ikv]] not in xdm__fkwt)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[wqcpl__ikv]})'
         for wqcpl__ikv in sxcjz__xbkj)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, sxcjz__xbkj, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    nupz__henu = None
    if df.is_table_format:
        dtk__nbfvh = types.Array(types.bool_, 1, 'C')
        nupz__henu = DataFrameType(tuple([dtk__nbfvh] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': dtk__nbfvh}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'~bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


def overload_dataframe_head(df, n=5):
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[:n]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[m:]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    zpk__kjsti = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in zpk__kjsti:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.first()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    zpk__kjsti = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in zpk__kjsti:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.last()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.isin()')
    hmxk__zpbx = 'def impl(df, values):\n'
    fox__mqn = {}
    hkjz__siz = False
    if isinstance(values, DataFrameType):
        hkjz__siz = True
        for i, wqcpl__ikv in enumerate(df.columns):
            if wqcpl__ikv in values.column_index:
                zarc__wsbn = 'val{}'.format(i)
                hmxk__zpbx += f"""  {zarc__wsbn} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[wqcpl__ikv]})
"""
                fox__mqn[wqcpl__ikv] = zarc__wsbn
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        fox__mqn = {wqcpl__ikv: 'values' for wqcpl__ikv in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        zarc__wsbn = 'data{}'.format(i)
        hmxk__zpbx += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(zarc__wsbn, i))
        data.append(zarc__wsbn)
    uasx__kytqk = ['out{}'.format(i) for i in range(len(df.columns))]
    xrt__gwts = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    ppp__fnyk = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    bqjz__cmzi = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, slbb__qzauk) in enumerate(zip(df.columns, data)):
        if cname in fox__mqn:
            wvcjo__wqsm = fox__mqn[cname]
            if hkjz__siz:
                hmxk__zpbx += xrt__gwts.format(slbb__qzauk, wvcjo__wqsm,
                    uasx__kytqk[i])
            else:
                hmxk__zpbx += ppp__fnyk.format(slbb__qzauk, wvcjo__wqsm,
                    uasx__kytqk[i])
        else:
            hmxk__zpbx += bqjz__cmzi.format(uasx__kytqk[i])
    return _gen_init_df(hmxk__zpbx, df.columns, ','.join(uasx__kytqk))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    qwwxc__cvzl = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(qwwxc__cvzl))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    nnbkf__sxskm = [wqcpl__ikv for wqcpl__ikv, cdhir__iptj in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        cdhir__iptj.dtype)]
    assert len(nnbkf__sxskm) != 0
    cktmw__jjo = ''
    if not any(cdhir__iptj == types.float64 for cdhir__iptj in df.data):
        cktmw__jjo = '.astype(np.float64)'
    mrkqb__vhv = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[wqcpl__ikv], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[wqcpl__ikv]], IntegerArrayType) or
        df.data[df.column_index[wqcpl__ikv]] == boolean_array else '') for
        wqcpl__ikv in nnbkf__sxskm)
    tqnc__dcudb = 'np.stack(({},), 1){}'.format(mrkqb__vhv, cktmw__jjo)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        nnbkf__sxskm)))
    index = f'{generate_col_to_index_func_text(nnbkf__sxskm)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(tqnc__dcudb)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, nnbkf__sxskm, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    tur__pktkj = dict(ddof=ddof)
    bjcn__xrhee = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    ulo__yov = '1' if is_overload_none(min_periods) else 'min_periods'
    nnbkf__sxskm = [wqcpl__ikv for wqcpl__ikv, cdhir__iptj in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        cdhir__iptj.dtype)]
    if len(nnbkf__sxskm) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    cktmw__jjo = ''
    if not any(cdhir__iptj == types.float64 for cdhir__iptj in df.data):
        cktmw__jjo = '.astype(np.float64)'
    mrkqb__vhv = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[wqcpl__ikv], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[wqcpl__ikv]], IntegerArrayType) or
        df.data[df.column_index[wqcpl__ikv]] == boolean_array else '') for
        wqcpl__ikv in nnbkf__sxskm)
    tqnc__dcudb = 'np.stack(({},), 1){}'.format(mrkqb__vhv, cktmw__jjo)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        nnbkf__sxskm)))
    index = f'pd.Index({nnbkf__sxskm})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(tqnc__dcudb)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        ulo__yov)
    return _gen_init_df(header, nnbkf__sxskm, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    tur__pktkj = dict(axis=axis, level=level, numeric_only=numeric_only)
    bjcn__xrhee = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    hmxk__zpbx = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    hmxk__zpbx += '  data = np.array([{}])\n'.format(data_args)
    pqo__ikvz = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    hmxk__zpbx += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {pqo__ikvz})\n'
        )
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'np': np}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    tur__pktkj = dict(axis=axis)
    bjcn__xrhee = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    hmxk__zpbx = 'def impl(df, axis=0, dropna=True):\n'
    hmxk__zpbx += '  data = np.asarray(({},))\n'.format(data_args)
    pqo__ikvz = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    hmxk__zpbx += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {pqo__ikvz})\n'
        )
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'np': np}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    tur__pktkj = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    bjcn__xrhee = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    tur__pktkj = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    bjcn__xrhee = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    tur__pktkj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bjcn__xrhee = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    tur__pktkj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bjcn__xrhee = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    tur__pktkj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bjcn__xrhee = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    tur__pktkj = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    bjcn__xrhee = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    tur__pktkj = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    bjcn__xrhee = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    tur__pktkj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bjcn__xrhee = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    tur__pktkj = dict(numeric_only=numeric_only, interpolation=interpolation)
    bjcn__xrhee = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    tur__pktkj = dict(axis=axis, skipna=skipna)
    bjcn__xrhee = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for eqv__oobph in df.data:
        if not (bodo.utils.utils.is_np_array_typ(eqv__oobph) and (
            eqv__oobph.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(eqv__oobph.dtype, (types.Number, types.Boolean))) or
            isinstance(eqv__oobph, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or eqv__oobph in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {eqv__oobph} not supported.'
                )
        if isinstance(eqv__oobph, bodo.CategoricalArrayType
            ) and not eqv__oobph.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    tur__pktkj = dict(axis=axis, skipna=skipna)
    bjcn__xrhee = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for eqv__oobph in df.data:
        if not (bodo.utils.utils.is_np_array_typ(eqv__oobph) and (
            eqv__oobph.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(eqv__oobph.dtype, (types.Number, types.Boolean))) or
            isinstance(eqv__oobph, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or eqv__oobph in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {eqv__oobph} not supported.'
                )
        if isinstance(eqv__oobph, bodo.CategoricalArrayType
            ) and not eqv__oobph.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        nnbkf__sxskm = tuple(wqcpl__ikv for wqcpl__ikv, cdhir__iptj in zip(
            df.columns, df.data) if bodo.utils.typing.
            _is_pandas_numeric_dtype(cdhir__iptj.dtype))
        out_colnames = nnbkf__sxskm
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            hzgyu__ehkfq = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[wqcpl__ikv]].dtype) for wqcpl__ikv in out_colnames
                ]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(hzgyu__ehkfq, []))
    except NotImplementedError as dmc__wbfdw:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    xlzv__pyynr = ''
    if func_name in ('sum', 'prod'):
        xlzv__pyynr = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    hmxk__zpbx = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, xlzv__pyynr))
    if func_name == 'quantile':
        hmxk__zpbx = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        hmxk__zpbx = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        hmxk__zpbx += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        hmxk__zpbx += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    befs__idnh = ''
    if func_name in ('min', 'max'):
        befs__idnh = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        befs__idnh = ', dtype=np.float32'
    wjgf__sqvpf = f'bodo.libs.array_ops.array_op_{func_name}'
    xir__ooo = ''
    if func_name in ['sum', 'prod']:
        xir__ooo = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        xir__ooo = 'index'
    elif func_name == 'quantile':
        xir__ooo = 'q'
    elif func_name in ['std', 'var']:
        xir__ooo = 'True, ddof'
    elif func_name == 'median':
        xir__ooo = 'True'
    data_args = ', '.join(
        f'{wjgf__sqvpf}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[wqcpl__ikv]}), {xir__ooo})'
         for wqcpl__ikv in out_colnames)
    hmxk__zpbx = ''
    if func_name in ('idxmax', 'idxmin'):
        hmxk__zpbx += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        hmxk__zpbx += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        hmxk__zpbx += '  data = np.asarray(({},){})\n'.format(data_args,
            befs__idnh)
    hmxk__zpbx += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return hmxk__zpbx


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    mbo__ftuu = [df_type.column_index[wqcpl__ikv] for wqcpl__ikv in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in mbo__ftuu)
    jzvzr__nolv = '\n        '.join(f'row[{i}] = arr_{mbo__ftuu[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    iasr__mmrc = f'len(arr_{mbo__ftuu[0]})'
    szkv__klaew = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in szkv__klaew:
        vmc__xuyko = szkv__klaew[func_name]
        aqw__yctl = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        hmxk__zpbx = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {iasr__mmrc}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{aqw__yctl})
    for i in numba.parfors.parfor.internal_prange(n):
        {jzvzr__nolv}
        A[i] = {vmc__xuyko}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return hmxk__zpbx
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    tur__pktkj = dict(fill_method=fill_method, limit=limit, freq=freq)
    bjcn__xrhee = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.pct_change()')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    tur__pktkj = dict(axis=axis, skipna=skipna)
    bjcn__xrhee = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumprod()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    tur__pktkj = dict(skipna=skipna)
    bjcn__xrhee = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumsum()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    tur__pktkj = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    bjcn__xrhee = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    nnbkf__sxskm = [wqcpl__ikv for wqcpl__ikv, cdhir__iptj in zip(df.
        columns, df.data) if _is_describe_type(cdhir__iptj)]
    if len(nnbkf__sxskm) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    jziit__pgfi = sum(df.data[df.column_index[wqcpl__ikv]].dtype == bodo.
        datetime64ns for wqcpl__ikv in nnbkf__sxskm)

    def _get_describe(col_ind):
        zywln__akjsr = df.data[col_ind].dtype == bodo.datetime64ns
        if jziit__pgfi and jziit__pgfi != len(nnbkf__sxskm):
            if zywln__akjsr:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for wqcpl__ikv in nnbkf__sxskm:
        col_ind = df.column_index[wqcpl__ikv]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[wqcpl__ikv]) for
        wqcpl__ikv in nnbkf__sxskm)
    sfii__yoizd = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if jziit__pgfi == len(nnbkf__sxskm):
        sfii__yoizd = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif jziit__pgfi:
        sfii__yoizd = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({sfii__yoizd})'
    return _gen_init_df(header, nnbkf__sxskm, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    tur__pktkj = dict(axis=axis, convert=convert, is_copy=is_copy)
    bjcn__xrhee = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    tur__pktkj = dict(freq=freq, axis=axis, fill_value=fill_value)
    bjcn__xrhee = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for glk__eoctx in df.data:
        if not is_supported_shift_array_type(glk__eoctx):
            raise BodoError(
                f'Dataframe.shift() column input type {glk__eoctx.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    tur__pktkj = dict(axis=axis)
    bjcn__xrhee = dict(axis=0)
    check_unsupported_args('DataFrame.diff', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for glk__eoctx in df.data:
        if not (isinstance(glk__eoctx, types.Array) and (isinstance(
            glk__eoctx.dtype, types.Number) or glk__eoctx.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {glk__eoctx.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'explode', inline='always', no_unliteral=True)
def overload_dataframe_explode(df, column, ignore_index=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.explode()')
    zjomt__mgjpt = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(zjomt__mgjpt)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        gqiux__byd = get_overload_const_list(column)
    else:
        gqiux__byd = [get_literal_value(column)]
    ikmz__nrl = [df.column_index[wqcpl__ikv] for wqcpl__ikv in gqiux__byd]
    for i in ikmz__nrl:
        if not isinstance(df.data[i], ArrayItemArrayType) and df.data[i
            ].dtype != string_array_split_view_type:
            raise BodoError(
                f'DataFrame.explode(): columns must have array-like entries')
    n = len(df.columns)
    header = 'def impl(df, column, ignore_index=False):\n'
    header += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    header += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    for i in range(n):
        header += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    header += (
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{ikmz__nrl[0]})\n'
        )
    for i in range(n):
        if i in ikmz__nrl:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.explode_no_index(data{i}, counts)\n'
                )
        else:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.repeat_kernel(data{i}, counts)\n'
                )
    header += (
        '  new_index = bodo.libs.array_kernels.repeat_kernel(index_arr, counts)\n'
        )
    data_args = ', '.join(f'out_data{i}' for i in range(n))
    index = 'bodo.utils.conversion.convert_to_index(new_index)'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    yhkh__heuqh = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    lrjt__qwwg = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', yhkh__heuqh, lrjt__qwwg,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    columns = tuple(wqcpl__ikv for wqcpl__ikv in df.columns if wqcpl__ikv !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    yhkh__heuqh = {'inplace': inplace}
    lrjt__qwwg = {'inplace': False}
    check_unsupported_args('query', yhkh__heuqh, lrjt__qwwg, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        gbl__wdag = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[gbl__wdag]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    yhkh__heuqh = {'subset': subset, 'keep': keep}
    lrjt__qwwg = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', yhkh__heuqh, lrjt__qwwg,
        package_name='pandas', module_name='DataFrame')
    qwwxc__cvzl = len(df.columns)
    hmxk__zpbx = "def impl(df, subset=None, keep='first'):\n"
    for i in range(qwwxc__cvzl):
        hmxk__zpbx += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    rqqx__gyfl = ', '.join(f'data_{i}' for i in range(qwwxc__cvzl))
    rqqx__gyfl += ',' if qwwxc__cvzl == 1 else ''
    hmxk__zpbx += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({rqqx__gyfl}))\n')
    hmxk__zpbx += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    hmxk__zpbx += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    yhkh__heuqh = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    lrjt__qwwg = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    jvh__fahy = []
    if is_overload_constant_list(subset):
        jvh__fahy = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        jvh__fahy = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        jvh__fahy = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    chsse__uulsv = []
    for col_name in jvh__fahy:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        chsse__uulsv.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', yhkh__heuqh,
        lrjt__qwwg, package_name='pandas', module_name='DataFrame')
    luts__mbltz = []
    if chsse__uulsv:
        for dhlfo__tsug in chsse__uulsv:
            if isinstance(df.data[dhlfo__tsug], bodo.MapArrayType):
                luts__mbltz.append(df.columns[dhlfo__tsug])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                luts__mbltz.append(col_name)
    if luts__mbltz:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {luts__mbltz} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    qwwxc__cvzl = len(df.columns)
    iah__taw = ['data_{}'.format(i) for i in chsse__uulsv]
    eou__uqu = ['data_{}'.format(i) for i in range(qwwxc__cvzl) if i not in
        chsse__uulsv]
    if iah__taw:
        owcsl__wti = len(iah__taw)
    else:
        owcsl__wti = qwwxc__cvzl
    zko__sldok = ', '.join(iah__taw + eou__uqu)
    data_args = ', '.join('data_{}'.format(i) for i in range(qwwxc__cvzl))
    hmxk__zpbx = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(qwwxc__cvzl):
        hmxk__zpbx += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    hmxk__zpbx += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(zko__sldok, index, owcsl__wti))
    hmxk__zpbx += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(hmxk__zpbx, df.columns, data_args, 'index')


def create_dataframe_mask_where_overload(func_name):

    def overload_dataframe_mask_where(df, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
            f'DataFrame.{func_name}()')
        _validate_arguments_mask_where(f'DataFrame.{func_name}', df, cond,
            other, inplace, axis, level, errors, try_cast)
        header = """def impl(df, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise', try_cast=False):
"""
        if func_name == 'mask':
            header += '  cond = ~cond\n'
        gen_all_false = [False]
        if cond.ndim == 1:
            cond_str = lambda i, _: 'cond'
        elif cond.ndim == 2:
            if isinstance(cond, DataFrameType):

                def cond_str(i, gen_all_false):
                    if df.columns[i] in cond.column_index:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {cond.column_index[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            ydrgt__vgcjt = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                ydrgt__vgcjt = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                ydrgt__vgcjt = lambda i: f'other[:,{i}]'
        qwwxc__cvzl = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {ydrgt__vgcjt(i)})'
             for i in range(qwwxc__cvzl))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        ujzvw__bxsdt = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(
            ujzvw__bxsdt)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    tur__pktkj = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    bjcn__xrhee = dict(inplace=False, level=None, errors='raise', try_cast=
        False)
    check_unsupported_args(f'{func_name}', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        (cond.ndim == 1 or cond.ndim == 2) and cond.dtype == types.bool_
        ) and not (isinstance(cond, DataFrameType) and cond.ndim == 2 and
        all(cond.data[i].dtype == types.bool_ for i in range(len(df.columns)))
        ):
        raise BodoError(
            f"{func_name}(): 'cond' argument must be a DataFrame, Series, 1- or 2-dimensional array of booleans"
            )
    qwwxc__cvzl = len(df.columns)
    if hasattr(other, 'ndim') and (other.ndim != 1 or other.ndim != 2):
        if other.ndim == 2:
            if not isinstance(other, (DataFrameType, types.Array)):
                raise BodoError(
                    f"{func_name}(): 'other', if 2-dimensional, must be a DataFrame or array."
                    )
        elif other.ndim != 1:
            raise BodoError(
                f"{func_name}(): 'other' must be either 1 or 2-dimensional")
    if isinstance(other, DataFrameType):
        for i in range(qwwxc__cvzl):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(qwwxc__cvzl):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(qwwxc__cvzl):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    avoku__gkgr = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    hmxk__zpbx = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    xzs__zjb = {}
    ffuu__bgdr = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': avoku__gkgr}
    ffuu__bgdr.update(extra_globals)
    exec(hmxk__zpbx, ffuu__bgdr, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        gbs__bqu = pd.Index(lhs.columns)
        vtqx__kvfa = pd.Index(rhs.columns)
        ukakz__cwkab, wynam__ojlo, vqg__bzduv = gbs__bqu.join(vtqx__kvfa,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(ukakz__cwkab), wynam__ojlo, vqg__bzduv
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        tqb__psa = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        uwz__ynu = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, tqb__psa)
        check_runtime_cols_unsupported(rhs, tqb__psa)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                ukakz__cwkab, wynam__ojlo, vqg__bzduv = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {aqaqg__htd}) {tqb__psa}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {ywra__onjrq})'
                     if aqaqg__htd != -1 and ywra__onjrq != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for aqaqg__htd, ywra__onjrq in zip(wynam__ojlo,
                    vqg__bzduv))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, ukakz__cwkab, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            vdu__uurnm = []
            bpdu__oaaww = []
            if op in uwz__ynu:
                for i, dmphz__gzgoy in enumerate(lhs.data):
                    if is_common_scalar_dtype([dmphz__gzgoy.dtype, rhs]):
                        vdu__uurnm.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {tqb__psa} rhs'
                            )
                    else:
                        phx__fyrpw = f'arr{i}'
                        bpdu__oaaww.append(phx__fyrpw)
                        vdu__uurnm.append(phx__fyrpw)
                data_args = ', '.join(vdu__uurnm)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {tqb__psa} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(bpdu__oaaww) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {phx__fyrpw} = np.empty(n, dtype=np.bool_)\n' for
                    phx__fyrpw in bpdu__oaaww)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(phx__fyrpw, 
                    op == operator.ne) for phx__fyrpw in bpdu__oaaww)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            vdu__uurnm = []
            bpdu__oaaww = []
            if op in uwz__ynu:
                for i, dmphz__gzgoy in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, dmphz__gzgoy.dtype]):
                        vdu__uurnm.append(
                            f'lhs {tqb__psa} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        phx__fyrpw = f'arr{i}'
                        bpdu__oaaww.append(phx__fyrpw)
                        vdu__uurnm.append(phx__fyrpw)
                data_args = ', '.join(vdu__uurnm)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, tqb__psa) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(bpdu__oaaww) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(phx__fyrpw) for phx__fyrpw in bpdu__oaaww)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(phx__fyrpw, 
                    op == operator.ne) for phx__fyrpw in bpdu__oaaww)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        ujzvw__bxsdt = create_binary_op_overload(op)
        overload(op)(ujzvw__bxsdt)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        tqb__psa = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, tqb__psa)
        check_runtime_cols_unsupported(right, tqb__psa)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                ukakz__cwkab, _, vqg__bzduv = _get_binop_columns(left,
                    right, True)
                hmxk__zpbx = 'def impl(left, right):\n'
                for i, ywra__onjrq in enumerate(vqg__bzduv):
                    if ywra__onjrq == -1:
                        hmxk__zpbx += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    hmxk__zpbx += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    hmxk__zpbx += f"""  df_arr{i} {tqb__psa} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {ywra__onjrq})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    ukakz__cwkab)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(hmxk__zpbx, ukakz__cwkab, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            hmxk__zpbx = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                hmxk__zpbx += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                hmxk__zpbx += '  df_arr{0} {1} right\n'.format(i, tqb__psa)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(hmxk__zpbx, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        ujzvw__bxsdt = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(ujzvw__bxsdt)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            tqb__psa = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, tqb__psa)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, tqb__psa) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        ujzvw__bxsdt = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(ujzvw__bxsdt)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            npq__uqiwd = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                npq__uqiwd[i] = bodo.libs.array_kernels.isna(obj, i)
            return npq__uqiwd
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            npq__uqiwd = np.empty(n, np.bool_)
            for i in range(n):
                npq__uqiwd[i] = pd.isna(obj[i])
            return npq__uqiwd
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if isinstance(obj, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, (DataFrameType, SeriesType)):
        return lambda obj: obj.notna()
    if isinstance(obj, (types.List, types.UniTuple)) or is_array_typ(obj,
        include_index_series=True):
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    yhkh__heuqh = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    lrjt__qwwg = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', yhkh__heuqh, lrjt__qwwg, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    quwg__met = str(expr_node)
    return quwg__met.startswith('left.') or quwg__met.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    scw__ggu = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (scw__ggu,))
    ndmn__lbm = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        gnvr__hid = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        aik__rcc = {('NOT_NA', ndmn__lbm(dmphz__gzgoy)): dmphz__gzgoy for
            dmphz__gzgoy in null_set}
        fwrm__jcdk, _, _ = _parse_query_expr(gnvr__hid, env, [], [], None,
            join_cleaned_cols=aik__rcc)
        jux__tuwse = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            bfjr__xuo = pd.core.computation.ops.BinOp('&', fwrm__jcdk,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = jux__tuwse
        return bfjr__xuo

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                opu__axib = set()
                nzkub__aga = set()
                sazyk__cyt = _insert_NA_cond_body(expr_node.lhs, opu__axib)
                kxcqk__pibc = _insert_NA_cond_body(expr_node.rhs, nzkub__aga)
                jbefo__csog = opu__axib.intersection(nzkub__aga)
                opu__axib.difference_update(jbefo__csog)
                nzkub__aga.difference_update(jbefo__csog)
                null_set.update(jbefo__csog)
                expr_node.lhs = append_null_checks(sazyk__cyt, opu__axib)
                expr_node.rhs = append_null_checks(kxcqk__pibc, nzkub__aga)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            pyxfn__vfeo = expr_node.name
            cfwjv__dnp, col_name = pyxfn__vfeo.split('.')
            if cfwjv__dnp == 'left':
                lbeb__jhr = left_columns
                data = left_data
            else:
                lbeb__jhr = right_columns
                data = right_data
            vocex__svhu = data[lbeb__jhr.index(col_name)]
            if bodo.utils.typing.is_nullable(vocex__svhu):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    vqqqy__bimfc = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        yqneu__tatd = str(expr_node.lhs)
        hxn__krsof = str(expr_node.rhs)
        if yqneu__tatd.startswith('left.') and hxn__krsof.startswith('left.'
            ) or yqneu__tatd.startswith('right.') and hxn__krsof.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [yqneu__tatd.split('.')[1]]
        right_on = [hxn__krsof.split('.')[1]]
        if yqneu__tatd.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        rjptc__hfn, uklzc__wsc, zgvjq__iiuxk = _extract_equal_conds(expr_node
            .lhs)
        ulax__kmn, fzg__xykgj, svbhe__udii = _extract_equal_conds(expr_node.rhs
            )
        left_on = rjptc__hfn + ulax__kmn
        right_on = uklzc__wsc + fzg__xykgj
        if zgvjq__iiuxk is None:
            return left_on, right_on, svbhe__udii
        if svbhe__udii is None:
            return left_on, right_on, zgvjq__iiuxk
        expr_node.lhs = zgvjq__iiuxk
        expr_node.rhs = svbhe__udii
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    scw__ggu = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (scw__ggu,))
    ema__onh = dict()
    ndmn__lbm = pd.core.computation.parsing.clean_column_name
    for name, teskl__vaezs in (('left', left_columns), ('right', right_columns)
        ):
        for dmphz__gzgoy in teskl__vaezs:
            kjvfj__cxmqh = ndmn__lbm(dmphz__gzgoy)
            gdf__rcc = name, kjvfj__cxmqh
            if gdf__rcc in ema__onh:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{dmphz__gzgoy}' and '{ema__onh[kjvfj__cxmqh]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ema__onh[gdf__rcc] = dmphz__gzgoy
    fax__nnfx, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ema__onh)
    left_on, right_on, nqwd__qufl = _extract_equal_conds(fax__nnfx.terms)
    return left_on, right_on, _insert_NA_cond(nqwd__qufl, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    tur__pktkj = dict(sort=sort, copy=copy, validate=validate)
    bjcn__xrhee = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    qbib__lie = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    ivdeq__pjqvp = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in qbib__lie and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, klwqe__wwsmz = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if klwqe__wwsmz is None:
                    ivdeq__pjqvp = ''
                else:
                    ivdeq__pjqvp = str(klwqe__wwsmz)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = qbib__lie
        right_keys = qbib__lie
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    phr__jtr = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        vtdjj__javf = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        vtdjj__javf = list(get_overload_const_list(suffixes))
    suffix_x = vtdjj__javf[0]
    suffix_y = vtdjj__javf[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    hmxk__zpbx = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    hmxk__zpbx += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    hmxk__zpbx += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    hmxk__zpbx += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, phr__jtr, ivdeq__pjqvp))
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo}, xzs__zjb)
    _impl = xzs__zjb['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType, bodo.
        DatetimeArrayType)
    khcn__tws = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    lzb__xqn = {get_overload_const_str(zyjsh__qhtzj) for zyjsh__qhtzj in (
        left_on, right_on, on) if is_overload_constant_str(zyjsh__qhtzj)}
    for df in (left, right):
        for i, dmphz__gzgoy in enumerate(df.data):
            if not isinstance(dmphz__gzgoy, valid_dataframe_column_types
                ) and dmphz__gzgoy not in khcn__tws:
                raise BodoError(
                    f'{name_func}(): use of column with {type(dmphz__gzgoy)} in merge unsupported'
                    )
            if df.columns[i] in lzb__xqn and isinstance(dmphz__gzgoy,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_bodo_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        vtdjj__javf = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        vtdjj__javf = list(get_overload_const_list(suffixes))
    if len(vtdjj__javf) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    qbib__lie = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        uodgo__pork = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            uodgo__pork = on_str not in qbib__lie and ('left.' in on_str or
                'right.' in on_str)
        if len(qbib__lie) == 0 and not uodgo__pork:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    fvvk__mql = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            vltmv__vxa = left.index
            qftt__lzkvh = isinstance(vltmv__vxa, StringIndexType)
            alpcd__yuyrt = right.index
            pxpy__tgiv = isinstance(alpcd__yuyrt, StringIndexType)
        elif is_overload_true(left_index):
            vltmv__vxa = left.index
            qftt__lzkvh = isinstance(vltmv__vxa, StringIndexType)
            alpcd__yuyrt = right.data[right.columns.index(right_keys[0])]
            pxpy__tgiv = alpcd__yuyrt.dtype == string_type
        elif is_overload_true(right_index):
            vltmv__vxa = left.data[left.columns.index(left_keys[0])]
            qftt__lzkvh = vltmv__vxa.dtype == string_type
            alpcd__yuyrt = right.index
            pxpy__tgiv = isinstance(alpcd__yuyrt, StringIndexType)
        if qftt__lzkvh and pxpy__tgiv:
            return
        vltmv__vxa = vltmv__vxa.dtype
        alpcd__yuyrt = alpcd__yuyrt.dtype
        try:
            sgptz__wovv = fvvk__mql.resolve_function_type(operator.eq, (
                vltmv__vxa, alpcd__yuyrt), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=vltmv__vxa, rk_dtype=alpcd__yuyrt))
    else:
        for fggx__kakxy, iuuyn__weg in zip(left_keys, right_keys):
            vltmv__vxa = left.data[left.columns.index(fggx__kakxy)].dtype
            ynt__kvhiv = left.data[left.columns.index(fggx__kakxy)]
            alpcd__yuyrt = right.data[right.columns.index(iuuyn__weg)].dtype
            vmg__nrdil = right.data[right.columns.index(iuuyn__weg)]
            if ynt__kvhiv == vmg__nrdil:
                continue
            ocsjx__lcij = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=fggx__kakxy, lk_dtype=vltmv__vxa, rk=iuuyn__weg,
                rk_dtype=alpcd__yuyrt))
            nvjvd__mmmgb = vltmv__vxa == string_type
            pks__xmvt = alpcd__yuyrt == string_type
            if nvjvd__mmmgb ^ pks__xmvt:
                raise_bodo_error(ocsjx__lcij)
            try:
                sgptz__wovv = fvvk__mql.resolve_function_type(operator.eq,
                    (vltmv__vxa, alpcd__yuyrt), {})
            except:
                raise_bodo_error(ocsjx__lcij)


def validate_keys(keys, df):
    rlloi__tchqk = set(keys).difference(set(df.columns))
    if len(rlloi__tchqk) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in rlloi__tchqk:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {rlloi__tchqk} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    tur__pktkj = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    bjcn__xrhee = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    hmxk__zpbx = "def _impl(left, other, on=None, how='left',\n"
    hmxk__zpbx += "    lsuffix='', rsuffix='', sort=False):\n"
    hmxk__zpbx += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo}, xzs__zjb)
    _impl = xzs__zjb['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        tjqlb__fziq = get_overload_const_list(on)
        validate_keys(tjqlb__fziq, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    qbib__lie = tuple(set(left.columns) & set(other.columns))
    if len(qbib__lie) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=qbib__lie))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    jav__lowb = set(left_keys) & set(right_keys)
    lmpt__iex = set(left_columns) & set(right_columns)
    fwkld__ebzre = lmpt__iex - jav__lowb
    oagzr__nwvhk = set(left_columns) - lmpt__iex
    bkkcz__kae = set(right_columns) - lmpt__iex
    dyjn__rndog = {}

    def insertOutColumn(col_name):
        if col_name in dyjn__rndog:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        dyjn__rndog[col_name] = 0
    for uzarv__zgrd in jav__lowb:
        insertOutColumn(uzarv__zgrd)
    for uzarv__zgrd in fwkld__ebzre:
        ugb__jwd = str(uzarv__zgrd) + suffix_x
        kaqoe__gzfw = str(uzarv__zgrd) + suffix_y
        insertOutColumn(ugb__jwd)
        insertOutColumn(kaqoe__gzfw)
    for uzarv__zgrd in oagzr__nwvhk:
        insertOutColumn(uzarv__zgrd)
    for uzarv__zgrd in bkkcz__kae:
        insertOutColumn(uzarv__zgrd)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    qbib__lie = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = qbib__lie
        right_keys = qbib__lie
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        vtdjj__javf = suffixes
    if is_overload_constant_list(suffixes):
        vtdjj__javf = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        vtdjj__javf = suffixes.value
    suffix_x = vtdjj__javf[0]
    suffix_y = vtdjj__javf[1]
    hmxk__zpbx = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    hmxk__zpbx += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    hmxk__zpbx += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    hmxk__zpbx += "    allow_exact_matches=True, direction='backward'):\n"
    hmxk__zpbx += '  suffix_x = suffixes[0]\n'
    hmxk__zpbx += '  suffix_y = suffixes[1]\n'
    hmxk__zpbx += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo}, xzs__zjb)
    _impl = xzs__zjb['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_bodo_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_bodo_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_bodo_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_bodo_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    tur__pktkj = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    tay__clapu = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', tur__pktkj, tay__clapu,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    ehosg__gdlm = func_name == 'DataFrame.pivot_table'
    if ehosg__gdlm:
        if is_overload_none(index) or not is_literal_type(index):
            raise_bodo_error(
                f"DataFrame.pivot_table(): 'index' argument is required and must be constant column labels"
                )
    elif not is_overload_none(index) and not is_literal_type(index):
        raise_bodo_error(
            f"{func_name}(): if 'index' argument is provided it must be constant column labels"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise_bodo_error(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise_bodo_error(
            f"{func_name}(): if 'values' argument is provided it must be constant column labels"
            )
    anf__akdu = get_literal_value(columns)
    if isinstance(anf__akdu, (list, tuple)):
        if len(anf__akdu) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {anf__akdu}"
                )
        anf__akdu = anf__akdu[0]
    if anf__akdu not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {anf__akdu} not found in DataFrame {df}."
            )
    wgn__ucxrv = df.column_index[anf__akdu]
    if is_overload_none(index):
        ybsdz__qjr = []
        czi__unt = []
    else:
        czi__unt = get_literal_value(index)
        if not isinstance(czi__unt, (list, tuple)):
            czi__unt = [czi__unt]
        ybsdz__qjr = []
        for index in czi__unt:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            ybsdz__qjr.append(df.column_index[index])
    if not (all(isinstance(wqcpl__ikv, int) for wqcpl__ikv in czi__unt) or
        all(isinstance(wqcpl__ikv, str) for wqcpl__ikv in czi__unt)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        okuex__okur = []
        aykb__jawm = []
        nbxo__ohfd = ybsdz__qjr + [wgn__ucxrv]
        for i, wqcpl__ikv in enumerate(df.columns):
            if i not in nbxo__ohfd:
                okuex__okur.append(i)
                aykb__jawm.append(wqcpl__ikv)
    else:
        aykb__jawm = get_literal_value(values)
        if not isinstance(aykb__jawm, (list, tuple)):
            aykb__jawm = [aykb__jawm]
        okuex__okur = []
        for val in aykb__jawm:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            okuex__okur.append(df.column_index[val])
    tkr__hsgw = set(okuex__okur) | set(ybsdz__qjr) | {wgn__ucxrv}
    if len(tkr__hsgw) != len(okuex__okur) + len(ybsdz__qjr) + 1:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )

    def check_valid_index_typ(index_column):
        if isinstance(index_column, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType, bodo.
            IntervalArrayType)):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column must have scalar rows"
                )
        if isinstance(index_column, bodo.CategoricalArrayType):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column does not support categorical data"
                )
    if len(ybsdz__qjr) == 0:
        index = df.index
        if isinstance(index, MultiIndexType):
            raise BodoError(
                f"{func_name}(): 'index' cannot be None with a DataFrame with a multi-index"
                )
        if not isinstance(index, RangeIndexType):
            check_valid_index_typ(index.data)
        if not is_literal_type(df.index.name_typ):
            raise BodoError(
                f"{func_name}(): If 'index' is None, the name of the DataFrame's Index must be constant at compile-time"
                )
    else:
        for hyv__cfqyy in ybsdz__qjr:
            index_column = df.data[hyv__cfqyy]
            check_valid_index_typ(index_column)
    zvxo__kdo = df.data[wgn__ucxrv]
    if isinstance(zvxo__kdo, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(zvxo__kdo, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for vru__azdaq in okuex__okur:
        gdvyg__tubl = df.data[vru__azdaq]
        if isinstance(gdvyg__tubl, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or gdvyg__tubl == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return czi__unt, anf__akdu, aykb__jawm, ybsdz__qjr, wgn__ucxrv, okuex__okur


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    czi__unt, anf__akdu, aykb__jawm, hyv__cfqyy, wgn__ucxrv, lbx__swkqa = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(czi__unt) == 0:
        if is_overload_none(data.index.name_typ):
            qdkks__prns = None,
        else:
            qdkks__prns = get_literal_value(data.index.name_typ),
    else:
        qdkks__prns = tuple(czi__unt)
    czi__unt = ColNamesMetaType(qdkks__prns)
    aykb__jawm = ColNamesMetaType(tuple(aykb__jawm))
    anf__akdu = ColNamesMetaType((anf__akdu,))
    hmxk__zpbx = 'def impl(data, index=None, columns=None, values=None):\n'
    hmxk__zpbx += f'    pivot_values = data.iloc[:, {wgn__ucxrv}].unique()\n'
    hmxk__zpbx += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(hyv__cfqyy) == 0:
        hmxk__zpbx += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        hmxk__zpbx += '        (\n'
        for cpe__tet in hyv__cfqyy:
            hmxk__zpbx += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {cpe__tet}),
"""
        hmxk__zpbx += '        ),\n'
    hmxk__zpbx += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {wgn__ucxrv}),),
"""
    hmxk__zpbx += '        (\n'
    for vru__azdaq in lbx__swkqa:
        hmxk__zpbx += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {vru__azdaq}),
"""
    hmxk__zpbx += '        ),\n'
    hmxk__zpbx += '        pivot_values,\n'
    hmxk__zpbx += '        index_lit,\n'
    hmxk__zpbx += '        columns_lit,\n'
    hmxk__zpbx += '        values_lit,\n'
    hmxk__zpbx += '    )\n'
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'index_lit': czi__unt, 'columns_lit':
        anf__akdu, 'values_lit': aykb__jawm}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot_table()')
    tur__pktkj = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    bjcn__xrhee = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    czi__unt, anf__akdu, aykb__jawm, hyv__cfqyy, wgn__ucxrv, lbx__swkqa = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    wpnh__jpyl = czi__unt
    czi__unt = ColNamesMetaType(tuple(czi__unt))
    aykb__jawm = ColNamesMetaType(tuple(aykb__jawm))
    cmaz__xui = anf__akdu
    anf__akdu = ColNamesMetaType((anf__akdu,))
    hmxk__zpbx = 'def impl(\n'
    hmxk__zpbx += '    data,\n'
    hmxk__zpbx += '    values=None,\n'
    hmxk__zpbx += '    index=None,\n'
    hmxk__zpbx += '    columns=None,\n'
    hmxk__zpbx += '    aggfunc="mean",\n'
    hmxk__zpbx += '    fill_value=None,\n'
    hmxk__zpbx += '    margins=False,\n'
    hmxk__zpbx += '    dropna=True,\n'
    hmxk__zpbx += '    margins_name="All",\n'
    hmxk__zpbx += '    observed=False,\n'
    hmxk__zpbx += '    sort=True,\n'
    hmxk__zpbx += '    _pivot_values=None,\n'
    hmxk__zpbx += '):\n'
    cbft__imas = hyv__cfqyy + [wgn__ucxrv] + lbx__swkqa
    hmxk__zpbx += f'    data = data.iloc[:, {cbft__imas}]\n'
    jymg__bbaw = wpnh__jpyl + [cmaz__xui]
    if not is_overload_none(_pivot_values):
        wext__ylb = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(wext__ylb)
        hmxk__zpbx += '    pivot_values = _pivot_values_arr\n'
        hmxk__zpbx += (
            f'    data = data[data.iloc[:, {len(hyv__cfqyy)}].isin(pivot_values)]\n'
            )
        if all(isinstance(wqcpl__ikv, str) for wqcpl__ikv in wext__ylb):
            sywww__eaqta = pd.array(wext__ylb, 'string')
        elif all(isinstance(wqcpl__ikv, int) for wqcpl__ikv in wext__ylb):
            sywww__eaqta = np.array(wext__ylb, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        sywww__eaqta = None
    hmxk__zpbx += (
        f'    data = data.groupby({jymg__bbaw!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        hmxk__zpbx += (
            f'    pivot_values = data.iloc[:, {len(hyv__cfqyy)}].unique()\n')
    hmxk__zpbx += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    hmxk__zpbx += '        (\n'
    for i in range(0, len(hyv__cfqyy)):
        hmxk__zpbx += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    hmxk__zpbx += '        ),\n'
    hmxk__zpbx += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(hyv__cfqyy)}),),
"""
    hmxk__zpbx += '        (\n'
    for i in range(len(hyv__cfqyy) + 1, len(lbx__swkqa) + len(hyv__cfqyy) + 1):
        hmxk__zpbx += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    hmxk__zpbx += '        ),\n'
    hmxk__zpbx += '        pivot_values,\n'
    hmxk__zpbx += '        index_lit,\n'
    hmxk__zpbx += '        columns_lit,\n'
    hmxk__zpbx += '        values_lit,\n'
    hmxk__zpbx += '        check_duplicates=False,\n'
    hmxk__zpbx += '        _constant_pivot_values=_constant_pivot_values,\n'
    hmxk__zpbx += '    )\n'
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'numba': numba, 'index_lit': czi__unt,
        'columns_lit': anf__akdu, 'values_lit': aykb__jawm,
        '_pivot_values_arr': sywww__eaqta, '_constant_pivot_values':
        _pivot_values}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    tur__pktkj = dict(col_level=col_level, ignore_index=ignore_index)
    bjcn__xrhee = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(frame, DataFrameType):
        raise BodoError("pandas.melt(): 'frame' argument must be a DataFrame.")
    if not is_overload_none(id_vars) and not is_literal_type(id_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'id_vars', if specified, must be a literal.")
    if not is_overload_none(value_vars) and not is_literal_type(value_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'value_vars', if specified, must be a literal.")
    if not is_overload_none(var_name) and not (is_literal_type(var_name) and
        (is_scalar_type(var_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'var_name', if specified, must be a literal.")
    if value_name != 'value' and not (is_literal_type(value_name) and (
        is_scalar_type(value_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'value_name', if specified, must be a literal.")
    var_name = get_literal_value(var_name) if not is_overload_none(var_name
        ) else 'variable'
    value_name = get_literal_value(value_name
        ) if value_name != 'value' else 'value'
    cooq__pjhe = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(cooq__pjhe, (list, tuple)):
        cooq__pjhe = [cooq__pjhe]
    for wqcpl__ikv in cooq__pjhe:
        if wqcpl__ikv not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {wqcpl__ikv} not found in {frame}."
                )
    rzsxo__ssng = [frame.column_index[i] for i in cooq__pjhe]
    if is_overload_none(value_vars):
        mqx__mux = []
        nukl__oju = []
        for i, wqcpl__ikv in enumerate(frame.columns):
            if i not in rzsxo__ssng:
                mqx__mux.append(i)
                nukl__oju.append(wqcpl__ikv)
    else:
        nukl__oju = get_literal_value(value_vars)
        if not isinstance(nukl__oju, (list, tuple)):
            nukl__oju = [nukl__oju]
        nukl__oju = [v for v in nukl__oju if v not in cooq__pjhe]
        if not nukl__oju:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        mqx__mux = []
        for val in nukl__oju:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            mqx__mux.append(frame.column_index[val])
    for wqcpl__ikv in nukl__oju:
        if wqcpl__ikv not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {wqcpl__ikv} not found in {frame}."
                )
    if not (all(isinstance(wqcpl__ikv, int) for wqcpl__ikv in nukl__oju) or
        all(isinstance(wqcpl__ikv, str) for wqcpl__ikv in nukl__oju)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    srxjj__cooq = frame.data[mqx__mux[0]]
    gel__otk = [frame.data[i].dtype for i in mqx__mux]
    mqx__mux = np.array(mqx__mux, dtype=np.int64)
    rzsxo__ssng = np.array(rzsxo__ssng, dtype=np.int64)
    _, wyji__tunq = bodo.utils.typing.get_common_scalar_dtype(gel__otk)
    if not wyji__tunq:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': nukl__oju, 'val_type': srxjj__cooq}
    header = 'def impl(\n'
    header += '  frame,\n'
    header += '  id_vars=None,\n'
    header += '  value_vars=None,\n'
    header += '  var_name=None,\n'
    header += "  value_name='value',\n"
    header += '  col_level=None,\n'
    header += '  ignore_index=True,\n'
    header += '):\n'
    header += (
        '  dummy_id = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, 0)\n'
        )
    if frame.is_table_format and all(v == srxjj__cooq.dtype for v in gel__otk):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            mqx__mux))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(nukl__oju) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {mqx__mux[0]})
"""
    else:
        bnh__cmrqv = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in mqx__mux)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({bnh__cmrqv},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in rzsxo__ssng:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(nukl__oju)})\n'
            )
    qcek__ypjst = ', '.join(f'out_id{i}' for i in rzsxo__ssng) + (', ' if 
        len(rzsxo__ssng) > 0 else '')
    data_args = qcek__ypjst + 'var_col, val_col'
    columns = tuple(cooq__pjhe + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(nukl__oju)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    tur__pktkj = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    bjcn__xrhee = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(index,
        'pandas.crosstab()')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    tur__pktkj = dict(ignore_index=ignore_index, key=key)
    bjcn__xrhee = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_bodo_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    btu__rimx = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        btu__rimx.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        iwnc__kufc = [get_overload_const_tuple(by)]
    else:
        iwnc__kufc = get_overload_const_list(by)
    iwnc__kufc = set((k, '') if (k, '') in btu__rimx else k for k in iwnc__kufc
        )
    if len(iwnc__kufc.difference(btu__rimx)) > 0:
        vsbl__zqvtj = list(set(get_overload_const_list(by)).difference(
            btu__rimx))
        raise_bodo_error(f'sort_values(): invalid keys {vsbl__zqvtj} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        fbi__kuctj = get_overload_const_list(na_position)
        for na_position in fbi__kuctj:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_bodo_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    tur__pktkj = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    bjcn__xrhee = dict(axis=0, level=None, kind='quicksort', sort_remaining
        =True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    tur__pktkj = dict(limit=limit, downcast=downcast)
    bjcn__xrhee = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    mglp__ldvou = not is_overload_none(value)
    opvnk__tlyyo = not is_overload_none(method)
    if mglp__ldvou and opvnk__tlyyo:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not mglp__ldvou and not opvnk__tlyyo:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if mglp__ldvou:
        clsf__tozw = 'value=value'
    else:
        clsf__tozw = 'method=method'
    data_args = [(
        f"df['{wqcpl__ikv}'].fillna({clsf__tozw}, inplace=inplace)" if
        isinstance(wqcpl__ikv, str) else
        f'df[{wqcpl__ikv}].fillna({clsf__tozw}, inplace=inplace)') for
        wqcpl__ikv in df.columns]
    hmxk__zpbx = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        hmxk__zpbx += '  ' + '  \n'.join(data_args) + '\n'
        xzs__zjb = {}
        exec(hmxk__zpbx, {}, xzs__zjb)
        impl = xzs__zjb['impl']
        return impl
    else:
        return _gen_init_df(hmxk__zpbx, df.columns, ', '.join(cdhir__iptj +
            '.values' for cdhir__iptj in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    tur__pktkj = dict(col_level=col_level, col_fill=col_fill)
    bjcn__xrhee = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    hmxk__zpbx = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    hmxk__zpbx += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        bnyrx__dxay = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            bnyrx__dxay)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            hmxk__zpbx += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            qce__zkjd = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = qce__zkjd + data_args
        else:
            ydkw__slk = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [ydkw__slk] + data_args
    return _gen_init_df(hmxk__zpbx, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    qrjms__uxos = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and qrjms__uxos == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(qrjms__uxos))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        moeu__apylt = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        akc__lfz = get_overload_const_list(subset)
        moeu__apylt = []
        for aae__evxkj in akc__lfz:
            if aae__evxkj not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{aae__evxkj}' not in data frame columns {df}"
                    )
            moeu__apylt.append(df.column_index[aae__evxkj])
    qwwxc__cvzl = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(qwwxc__cvzl))
    hmxk__zpbx = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(qwwxc__cvzl):
        hmxk__zpbx += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    hmxk__zpbx += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in moeu__apylt)))
    hmxk__zpbx += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(hmxk__zpbx, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    tur__pktkj = dict(index=index, level=level, errors=errors)
    bjcn__xrhee = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', tur__pktkj, bjcn__xrhee,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            szafh__jko = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            szafh__jko = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            szafh__jko = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            szafh__jko = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for wqcpl__ikv in szafh__jko:
        if wqcpl__ikv not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(wqcpl__ikv, df.columns))
    if len(set(szafh__jko)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    vyrx__yvj = tuple(wqcpl__ikv for wqcpl__ikv in df.columns if wqcpl__ikv
         not in szafh__jko)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[wqcpl__ikv], '.copy()' if not inplace else
        '') for wqcpl__ikv in vyrx__yvj)
    hmxk__zpbx = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    hmxk__zpbx += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(hmxk__zpbx, vyrx__yvj, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sample()')
    tur__pktkj = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    aijum__xgc = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', tur__pktkj, aijum__xgc,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    qwwxc__cvzl = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(qwwxc__cvzl))
    ruoep__vnd = ', '.join('rhs_data_{}'.format(i) for i in range(qwwxc__cvzl))
    hmxk__zpbx = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    hmxk__zpbx += '  if (frac == 1 or n == len(df)) and not replace:\n'
    hmxk__zpbx += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(qwwxc__cvzl):
        hmxk__zpbx += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    hmxk__zpbx += '  if frac is None:\n'
    hmxk__zpbx += '    frac_d = -1.0\n'
    hmxk__zpbx += '  else:\n'
    hmxk__zpbx += '    frac_d = frac\n'
    hmxk__zpbx += '  if n is None:\n'
    hmxk__zpbx += '    n_i = 0\n'
    hmxk__zpbx += '  else:\n'
    hmxk__zpbx += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    hmxk__zpbx += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({ruoep__vnd},), {index}, n_i, frac_d, replace)
"""
    hmxk__zpbx += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(hmxk__zpbx, df.columns,
        data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    yhkh__heuqh = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    lrjt__qwwg = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', yhkh__heuqh, lrjt__qwwg,
        package_name='pandas', module_name='DataFrame')
    hhxgs__ivgc = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            hrmvt__ntmar = hhxgs__ivgc + '\n'
            hrmvt__ntmar += 'Index: 0 entries\n'
            hrmvt__ntmar += 'Empty DataFrame'
            print(hrmvt__ntmar)
        return _info_impl
    else:
        hmxk__zpbx = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        hmxk__zpbx += '    ncols = df.shape[1]\n'
        hmxk__zpbx += f'    lines = "{hhxgs__ivgc}\\n"\n'
        hmxk__zpbx += f'    lines += "{df.index}: "\n'
        hmxk__zpbx += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            hmxk__zpbx += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            hmxk__zpbx += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            hmxk__zpbx += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        hmxk__zpbx += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        hmxk__zpbx += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        hmxk__zpbx += '    column_width = max(space, 7)\n'
        hmxk__zpbx += '    column= "Column"\n'
        hmxk__zpbx += '    underl= "------"\n'
        hmxk__zpbx += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        hmxk__zpbx += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        hmxk__zpbx += '    mem_size = 0\n'
        hmxk__zpbx += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        hmxk__zpbx += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        hmxk__zpbx += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        dzgm__yljz = dict()
        for i in range(len(df.columns)):
            hmxk__zpbx += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            vooo__guhty = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                vooo__guhty = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                dtdib__wuul = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                vooo__guhty = f'{dtdib__wuul[:-7]}'
            hmxk__zpbx += f'    col_dtype[{i}] = "{vooo__guhty}"\n'
            if vooo__guhty in dzgm__yljz:
                dzgm__yljz[vooo__guhty] += 1
            else:
                dzgm__yljz[vooo__guhty] = 1
            hmxk__zpbx += f'    col_name[{i}] = "{df.columns[i]}"\n'
            hmxk__zpbx += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        hmxk__zpbx += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        hmxk__zpbx += '    for i in column_info:\n'
        hmxk__zpbx += "        lines += f'{i}\\n'\n"
        pfr__dqbw = ', '.join(f'{k}({dzgm__yljz[k]})' for k in sorted(
            dzgm__yljz))
        hmxk__zpbx += f"    lines += 'dtypes: {pfr__dqbw}\\n'\n"
        hmxk__zpbx += '    mem_size += df.index.nbytes\n'
        hmxk__zpbx += '    total_size = _sizeof_fmt(mem_size)\n'
        hmxk__zpbx += "    lines += f'memory usage: {total_size}'\n"
        hmxk__zpbx += '    print(lines)\n'
        xzs__zjb = {}
        exec(hmxk__zpbx, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, xzs__zjb)
        _info_impl = xzs__zjb['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    hmxk__zpbx = 'def impl(df, index=True, deep=False):\n'
    kspj__jxb = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes'
    pyrdy__kqi = is_overload_true(index)
    columns = df.columns
    if pyrdy__kqi:
        columns = ('Index',) + columns
    if len(columns) == 0:
        ztmr__xkfsw = ()
    elif all(isinstance(wqcpl__ikv, int) for wqcpl__ikv in columns):
        ztmr__xkfsw = np.array(columns, 'int64')
    elif all(isinstance(wqcpl__ikv, str) for wqcpl__ikv in columns):
        ztmr__xkfsw = pd.array(columns, 'string')
    else:
        ztmr__xkfsw = columns
    if df.is_table_format and len(df.columns) > 0:
        dtq__xlm = int(pyrdy__kqi)
        wkrlc__uui = len(columns)
        hmxk__zpbx += f'  nbytes_arr = np.empty({wkrlc__uui}, np.int64)\n'
        hmxk__zpbx += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        hmxk__zpbx += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {dtq__xlm})
"""
        if pyrdy__kqi:
            hmxk__zpbx += f'  nbytes_arr[0] = {kspj__jxb}\n'
        hmxk__zpbx += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if pyrdy__kqi:
            data = f'{kspj__jxb},{data}'
        else:
            pcpk__yhq = ',' if len(columns) == 1 else ''
            data = f'{data}{pcpk__yhq}'
        hmxk__zpbx += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        ztmr__xkfsw}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    ukc__jlfd = 'read_excel_df{}'.format(next_label())
    setattr(types, ukc__jlfd, df_type)
    amqee__zyci = False
    if is_overload_constant_list(parse_dates):
        amqee__zyci = get_overload_const_list(parse_dates)
    epjy__sffg = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    hmxk__zpbx = f"""
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{ukc__jlfd}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{epjy__sffg}}},
            engine=engine,
            converters=converters,
            true_values=true_values,
            false_values=false_values,
            skiprows=skiprows,
            nrows=nrows,
            na_values=na_values,
            keep_default_na=keep_default_na,
            na_filter=na_filter,
            verbose=verbose,
            parse_dates={amqee__zyci},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    xzs__zjb = {}
    exec(hmxk__zpbx, globals(), xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as dmc__wbfdw:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    hmxk__zpbx = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    hmxk__zpbx += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    hmxk__zpbx += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        hmxk__zpbx += '   fig, ax = plt.subplots()\n'
    else:
        hmxk__zpbx += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        hmxk__zpbx += '   fig.set_figwidth(figsize[0])\n'
        hmxk__zpbx += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        hmxk__zpbx += '   xlabel = x\n'
    hmxk__zpbx += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        hmxk__zpbx += '   ylabel = y\n'
    else:
        hmxk__zpbx += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        hmxk__zpbx += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        hmxk__zpbx += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    hmxk__zpbx += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            hmxk__zpbx += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            mujv__qzgiy = get_overload_const_str(x)
            nbent__guyvn = df.columns.index(mujv__qzgiy)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if nbent__guyvn != i:
                        hmxk__zpbx += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            hmxk__zpbx += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        hmxk__zpbx += '   ax.scatter(df[x], df[y], s=20)\n'
        hmxk__zpbx += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        hmxk__zpbx += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        hmxk__zpbx += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        hmxk__zpbx += '   ax.legend()\n'
    hmxk__zpbx += '   return ax\n'
    xzs__zjb = {}
    exec(hmxk__zpbx, {'bodo': bodo, 'plt': plt}, xzs__zjb)
    impl = xzs__zjb['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for chwdt__qcm in df_typ.data:
        if not (isinstance(chwdt__qcm, IntegerArrayType) or isinstance(
            chwdt__qcm.dtype, types.Number) or chwdt__qcm.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        wjwcn__qtrkx = args[0]
        ebiik__uink = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        kaikh__hln = wjwcn__qtrkx
        check_runtime_cols_unsupported(wjwcn__qtrkx, 'set_df_col()')
        if isinstance(wjwcn__qtrkx, DataFrameType):
            index = wjwcn__qtrkx.index
            if len(wjwcn__qtrkx.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(wjwcn__qtrkx.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if ebiik__uink in wjwcn__qtrkx.columns:
                vyrx__yvj = wjwcn__qtrkx.columns
                dqwt__oqt = wjwcn__qtrkx.columns.index(ebiik__uink)
                otf__gslba = list(wjwcn__qtrkx.data)
                otf__gslba[dqwt__oqt] = val
                otf__gslba = tuple(otf__gslba)
            else:
                vyrx__yvj = wjwcn__qtrkx.columns + (ebiik__uink,)
                otf__gslba = wjwcn__qtrkx.data + (val,)
            kaikh__hln = DataFrameType(otf__gslba, index, vyrx__yvj,
                wjwcn__qtrkx.dist, wjwcn__qtrkx.is_table_format)
        return kaikh__hln(*args)


SetDfColInfer.prefer_literal = True


def __bodosql_replace_columns_dummy(df, col_names_to_replace,
    cols_to_replace_with):
    for i in range(len(col_names_to_replace)):
        df[col_names_to_replace[i]] = cols_to_replace_with[i]


@infer_global(__bodosql_replace_columns_dummy)
class BodoSQLReplaceColsInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 3
        assert is_overload_constant_tuple(args[1])
        assert isinstance(args[2], types.BaseTuple)
        fjku__zjw = args[0]
        assert isinstance(fjku__zjw, DataFrameType) and len(fjku__zjw.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        qrz__gfrs = args[2]
        assert len(col_names_to_replace) == len(qrz__gfrs
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(fjku__zjw.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in fjku__zjw.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(fjku__zjw,
            '__bodosql_replace_columns_dummy()')
        index = fjku__zjw.index
        vyrx__yvj = fjku__zjw.columns
        otf__gslba = list(fjku__zjw.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            bxei__lca = qrz__gfrs[i]
            assert isinstance(bxei__lca, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(bxei__lca, SeriesType):
                bxei__lca = bxei__lca.data
            dhlfo__tsug = fjku__zjw.column_index[col_name]
            otf__gslba[dhlfo__tsug] = bxei__lca
        otf__gslba = tuple(otf__gslba)
        kaikh__hln = DataFrameType(otf__gslba, index, vyrx__yvj, fjku__zjw.
            dist, fjku__zjw.is_table_format)
        return kaikh__hln(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    tezua__ymunu = {}

    def _rewrite_membership_op(self, node, left, right):
        eeca__qpvdm = node.op
        op = self.visit(eeca__qpvdm)
        return op, eeca__qpvdm, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    nbj__gvhz = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in nbj__gvhz:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in nbj__gvhz:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        tvol__dfaw = node.attr
        value = node.value
        qtv__jizll = pd.core.computation.ops.LOCAL_TAG
        if tvol__dfaw in ('str', 'dt'):
            try:
                buqrd__ydupz = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as vvuk__kevjm:
                col_name = vvuk__kevjm.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            buqrd__ydupz = str(self.visit(value))
        gdf__rcc = buqrd__ydupz, tvol__dfaw
        if gdf__rcc in join_cleaned_cols:
            tvol__dfaw = join_cleaned_cols[gdf__rcc]
        name = buqrd__ydupz + '.' + tvol__dfaw
        if name.startswith(qtv__jizll):
            name = name[len(qtv__jizll):]
        if tvol__dfaw in ('str', 'dt'):
            sccpv__ahog = columns[cleaned_columns.index(buqrd__ydupz)]
            tezua__ymunu[sccpv__ahog] = buqrd__ydupz
            self.env.scope[name] = 0
            return self.term_type(qtv__jizll + name, self.env)
        nbj__gvhz.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in nbj__gvhz:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        ttbe__hyxf = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        ebiik__uink = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(ttbe__hyxf), ebiik__uink))

    def op__str__(self):
        pkfy__iayy = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            miin__bvj)) for miin__bvj in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(pkfy__iayy)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(pkfy__iayy)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(pkfy__iayy))
    nmtr__uizk = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    gpbmd__hasg = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_evaluate_binop)
    eurp__ytbw = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    ymw__bjrqy = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    ijp__sjlq = pd.core.computation.ops.Term.__str__
    bjiuq__bbhgj = pd.core.computation.ops.MathCall.__str__
    fpqz__ldsmv = pd.core.computation.ops.Op.__str__
    jux__tuwse = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        fax__nnfx = pd.core.computation.expr.Expr(expr, env=env)
        hodl__tixz = str(fax__nnfx)
    except pd.core.computation.ops.UndefinedVariableError as vvuk__kevjm:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == vvuk__kevjm.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {vvuk__kevjm}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            nmtr__uizk)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            gpbmd__hasg)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = eurp__ytbw
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = ymw__bjrqy
        pd.core.computation.ops.Term.__str__ = ijp__sjlq
        pd.core.computation.ops.MathCall.__str__ = bjiuq__bbhgj
        pd.core.computation.ops.Op.__str__ = fpqz__ldsmv
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            jux__tuwse)
    rav__dcav = pd.core.computation.parsing.clean_column_name
    tezua__ymunu.update({wqcpl__ikv: rav__dcav(wqcpl__ikv) for wqcpl__ikv in
        columns if rav__dcav(wqcpl__ikv) in fax__nnfx.names})
    return fax__nnfx, hodl__tixz, tezua__ymunu


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        khigc__ajdny = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(khigc__ajdny))
        peq__kwfei = namedtuple('Pandas', col_names)
        pvtj__hlhe = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], peq__kwfei)
        super(DataFrameTupleIterator, self).__init__(name, pvtj__hlhe)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        vkoot__igwj = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        vkoot__igwj = [types.Array(types.int64, 1, 'C')] + vkoot__igwj
        kkbs__nurhy = DataFrameTupleIterator(col_names, vkoot__igwj)
        return kkbs__nurhy(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zivci__cyj = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            zivci__cyj)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    mwvqz__glps = args[len(args) // 2:]
    yyblg__mtbnz = sig.args[len(sig.args) // 2:]
    rvcvs__bavf = context.make_helper(builder, sig.return_type)
    joqy__ssc = context.get_constant(types.intp, 0)
    wphb__jnref = cgutils.alloca_once_value(builder, joqy__ssc)
    rvcvs__bavf.index = wphb__jnref
    for i, arr in enumerate(mwvqz__glps):
        setattr(rvcvs__bavf, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(mwvqz__glps, yyblg__mtbnz):
        context.nrt.incref(builder, arr_typ, arr)
    res = rvcvs__bavf._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    uycvf__bct, = sig.args
    gywqh__nesil, = args
    rvcvs__bavf = context.make_helper(builder, uycvf__bct, value=gywqh__nesil)
    jejgy__aqc = signature(types.intp, uycvf__bct.array_types[1])
    qwp__lixrg = context.compile_internal(builder, lambda a: len(a),
        jejgy__aqc, [rvcvs__bavf.array0])
    index = builder.load(rvcvs__bavf.index)
    josh__jhys = builder.icmp_signed('<', index, qwp__lixrg)
    result.set_valid(josh__jhys)
    with builder.if_then(josh__jhys):
        values = [index]
        for i, arr_typ in enumerate(uycvf__bct.array_types[1:]):
            ahu__pofib = getattr(rvcvs__bavf, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                cyjb__rml = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    cyjb__rml, [ahu__pofib, index])
            else:
                cyjb__rml = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    cyjb__rml, [ahu__pofib, index])
            values.append(val)
        value = context.make_tuple(builder, uycvf__bct.yield_type, values)
        result.yield_(value)
        fur__lvq = cgutils.increment_index(builder, index)
        builder.store(fur__lvq, rvcvs__bavf.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    wvs__uxlo = ir.Assign(rhs, lhs, expr.loc)
    lefdq__kgeu = lhs
    fhs__mckwu = []
    gka__igweg = []
    vprh__mng = typ.count
    for i in range(vprh__mng):
        sgd__mqixm = ir.Var(lefdq__kgeu.scope, mk_unique_var('{}_size{}'.
            format(lefdq__kgeu.name, i)), lefdq__kgeu.loc)
        amwbm__isy = ir.Expr.static_getitem(lhs, i, None, lefdq__kgeu.loc)
        self.calltypes[amwbm__isy] = None
        fhs__mckwu.append(ir.Assign(amwbm__isy, sgd__mqixm, lefdq__kgeu.loc))
        self._define(equiv_set, sgd__mqixm, types.intp, amwbm__isy)
        gka__igweg.append(sgd__mqixm)
    hzo__tsp = tuple(gka__igweg)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        hzo__tsp, pre=[wvs__uxlo] + fhs__mckwu)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
