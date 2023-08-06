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
        ciwq__izh = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({ciwq__izh})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    yckf__dpl = 'def impl(df):\n'
    if df.has_runtime_cols:
        yckf__dpl += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        mrt__ivj = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        yckf__dpl += f'  return {mrt__ivj}'
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo}, zxnf__onesa)
    impl = zxnf__onesa['impl']
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
    kdet__bfnv = len(df.columns)
    cvhq__tyvq = set(i for i in range(kdet__bfnv) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in cvhq__tyvq else '') for i in
        range(kdet__bfnv))
    yckf__dpl = 'def f(df):\n'.format()
    yckf__dpl += '    return np.stack(({},), 1)\n'.format(data_args)
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'np': np}, zxnf__onesa)
    zuqqr__xkna = zxnf__onesa['f']
    return zuqqr__xkna


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
    qyo__lcsk = {'dtype': dtype, 'na_value': na_value}
    wgtjb__cbgw = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', qyo__lcsk, wgtjb__cbgw,
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
            uwwi__azyw = bodo.hiframes.table.compute_num_runtime_columns(t)
            return uwwi__azyw * len(t)
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
            uwwi__azyw = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), uwwi__azyw
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    yckf__dpl = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    gjlaz__jutr = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    yckf__dpl += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{gjlaz__jutr}), {index}, None)
"""
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo}, zxnf__onesa)
    impl = zxnf__onesa['impl']
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
    qyo__lcsk = {'copy': copy, 'errors': errors}
    wgtjb__cbgw = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', qyo__lcsk, wgtjb__cbgw,
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
        ldi__rqcnx = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        wcwj__rtitb = _bodo_object_typeref.instance_type
        assert isinstance(wcwj__rtitb, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in wcwj__rtitb.column_index:
                    idx = wcwj__rtitb.column_index[name]
                    arr_typ = wcwj__rtitb.data[idx]
                else:
                    arr_typ = df.data[i]
                ldi__rqcnx.append(arr_typ)
        else:
            extra_globals = {}
            kgwxw__dvr = {}
            for i, name in enumerate(wcwj__rtitb.columns):
                arr_typ = wcwj__rtitb.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    ndhrj__pisfa = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype
                        )
                elif arr_typ == boolean_array:
                    ndhrj__pisfa = boolean_dtype
                else:
                    ndhrj__pisfa = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = ndhrj__pisfa
                kgwxw__dvr[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {kgwxw__dvr[oyi__txn]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if oyi__txn in kgwxw__dvr else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, oyi__txn in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        uifj__tkt = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            uifj__tkt = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in uifj__tkt.items()}
            for i, name in enumerate(df.columns):
                if name in uifj__tkt:
                    arr_typ = uifj__tkt[name]
                else:
                    arr_typ = df.data[i]
                ldi__rqcnx.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(uifj__tkt[oyi__txn])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if oyi__txn in uifj__tkt else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, oyi__txn in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        ldi__rqcnx = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        tntpe__hgxy = bodo.TableType(tuple(ldi__rqcnx))
        extra_globals['out_table_typ'] = tntpe__hgxy
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
        pen__zhjlp = types.none
        extra_globals = {'output_arr_typ': pen__zhjlp}
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
        tsr__ibrzh = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                tsr__ibrzh.append(arr + '.copy()')
            elif is_overload_false(deep):
                tsr__ibrzh.append(arr)
            else:
                tsr__ibrzh.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(tsr__ibrzh)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    qyo__lcsk = {'index': index, 'level': level, 'errors': errors}
    wgtjb__cbgw = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', qyo__lcsk, wgtjb__cbgw,
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
        yougy__lmt = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        yougy__lmt = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    yzfy__ccu = tuple([yougy__lmt.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    ddlf__hpuir = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ddlf__hpuir = df.copy(columns=yzfy__ccu)
        pen__zhjlp = types.none
        extra_globals = {'output_arr_typ': pen__zhjlp}
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
        tsr__ibrzh = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                tsr__ibrzh.append(arr + '.copy()')
            elif is_overload_false(copy):
                tsr__ibrzh.append(arr)
            else:
                tsr__ibrzh.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(tsr__ibrzh)
    return _gen_init_df(header, yzfy__ccu, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    dalne__muer = not is_overload_none(items)
    qki__xrhz = not is_overload_none(like)
    lsuko__wfw = not is_overload_none(regex)
    bwg__bwy = dalne__muer ^ qki__xrhz ^ lsuko__wfw
    xwmsi__yszm = not (dalne__muer or qki__xrhz or lsuko__wfw)
    if xwmsi__yszm:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not bwg__bwy:
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
        csr__wklti = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        csr__wklti = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert csr__wklti in {0, 1}
    yckf__dpl = 'def impl(df, items=None, like=None, regex=None, axis=None):\n'
    if csr__wklti == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if csr__wklti == 1:
        ywwb__pyxge = []
        kie__nzeh = []
        piqck__hyg = []
        if dalne__muer:
            if is_overload_constant_list(items):
                bos__cvwy = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if qki__xrhz:
            if is_overload_constant_str(like):
                ktilv__bifsp = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if lsuko__wfw:
            if is_overload_constant_str(regex):
                jopc__yrm = get_overload_const_str(regex)
                iaedb__tzx = re.compile(jopc__yrm)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, oyi__txn in enumerate(df.columns):
            if not is_overload_none(items
                ) and oyi__txn in bos__cvwy or not is_overload_none(like
                ) and ktilv__bifsp in str(oyi__txn) or not is_overload_none(
                regex) and iaedb__tzx.search(str(oyi__txn)):
                kie__nzeh.append(oyi__txn)
                piqck__hyg.append(i)
        for i in piqck__hyg:
            var_name = f'data_{i}'
            ywwb__pyxge.append(var_name)
            yckf__dpl += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(ywwb__pyxge)
        return _gen_init_df(yckf__dpl, kie__nzeh, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ddlf__hpuir = None
    if df.is_table_format:
        pen__zhjlp = types.Array(types.bool_, 1, 'C')
        ddlf__hpuir = DataFrameType(tuple([pen__zhjlp] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': pen__zhjlp}
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
    wquwr__qsmk = is_overload_none(include)
    vocpj__sau = is_overload_none(exclude)
    jvl__cysdf = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if wquwr__qsmk and vocpj__sau:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not wquwr__qsmk:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            ipwk__oxl = [dtype_to_array_type(parse_dtype(elem, jvl__cysdf)) for
                elem in include]
        elif is_legal_input(include):
            ipwk__oxl = [dtype_to_array_type(parse_dtype(include, jvl__cysdf))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        ipwk__oxl = get_nullable_and_non_nullable_types(ipwk__oxl)
        chtn__ukro = tuple(oyi__txn for i, oyi__txn in enumerate(df.columns
            ) if df.data[i] in ipwk__oxl)
    else:
        chtn__ukro = df.columns
    if not vocpj__sau:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            xjhcz__sqx = [dtype_to_array_type(parse_dtype(elem, jvl__cysdf)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            xjhcz__sqx = [dtype_to_array_type(parse_dtype(exclude, jvl__cysdf))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        xjhcz__sqx = get_nullable_and_non_nullable_types(xjhcz__sqx)
        chtn__ukro = tuple(oyi__txn for oyi__txn in chtn__ukro if df.data[
            df.column_index[oyi__txn]] not in xjhcz__sqx)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[oyi__txn]})'
         for oyi__txn in chtn__ukro)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, chtn__ukro, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ddlf__hpuir = None
    if df.is_table_format:
        pen__zhjlp = types.Array(types.bool_, 1, 'C')
        ddlf__hpuir = DataFrameType(tuple([pen__zhjlp] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': pen__zhjlp}
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
    nvm__pynai = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in nvm__pynai:
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
    nvm__pynai = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in nvm__pynai:
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
    yckf__dpl = 'def impl(df, values):\n'
    pqy__lkr = {}
    uwgr__chq = False
    if isinstance(values, DataFrameType):
        uwgr__chq = True
        for i, oyi__txn in enumerate(df.columns):
            if oyi__txn in values.column_index:
                wsyxa__fdq = 'val{}'.format(i)
                yckf__dpl += f"""  {wsyxa__fdq} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[oyi__txn]})
"""
                pqy__lkr[oyi__txn] = wsyxa__fdq
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        pqy__lkr = {oyi__txn: 'values' for oyi__txn in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        wsyxa__fdq = 'data{}'.format(i)
        yckf__dpl += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(wsyxa__fdq, i))
        data.append(wsyxa__fdq)
    lgjc__ytuo = ['out{}'.format(i) for i in range(len(df.columns))]
    dzm__zwhnq = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    boyj__phc = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    bmy__paovx = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, zugn__zgt) in enumerate(zip(df.columns, data)):
        if cname in pqy__lkr:
            uufzi__lmz = pqy__lkr[cname]
            if uwgr__chq:
                yckf__dpl += dzm__zwhnq.format(zugn__zgt, uufzi__lmz,
                    lgjc__ytuo[i])
            else:
                yckf__dpl += boyj__phc.format(zugn__zgt, uufzi__lmz,
                    lgjc__ytuo[i])
        else:
            yckf__dpl += bmy__paovx.format(lgjc__ytuo[i])
    return _gen_init_df(yckf__dpl, df.columns, ','.join(lgjc__ytuo))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    kdet__bfnv = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(kdet__bfnv))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    gab__jylj = [oyi__txn for oyi__txn, jvp__ezidt in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(jvp__ezidt.dtype)]
    assert len(gab__jylj) != 0
    wdomi__sfb = ''
    if not any(jvp__ezidt == types.float64 for jvp__ezidt in df.data):
        wdomi__sfb = '.astype(np.float64)'
    klt__kbe = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[oyi__txn], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[oyi__txn]], IntegerArrayType) or
        df.data[df.column_index[oyi__txn]] == boolean_array else '') for
        oyi__txn in gab__jylj)
    vdbi__xdziu = 'np.stack(({},), 1){}'.format(klt__kbe, wdomi__sfb)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(gab__jylj)))
    index = f'{generate_col_to_index_func_text(gab__jylj)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(vdbi__xdziu)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, gab__jylj, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    pse__kzzv = dict(ddof=ddof)
    vpqk__coaq = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    gyzv__ygb = '1' if is_overload_none(min_periods) else 'min_periods'
    gab__jylj = [oyi__txn for oyi__txn, jvp__ezidt in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(jvp__ezidt.dtype)]
    if len(gab__jylj) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    wdomi__sfb = ''
    if not any(jvp__ezidt == types.float64 for jvp__ezidt in df.data):
        wdomi__sfb = '.astype(np.float64)'
    klt__kbe = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[oyi__txn], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[oyi__txn]], IntegerArrayType) or
        df.data[df.column_index[oyi__txn]] == boolean_array else '') for
        oyi__txn in gab__jylj)
    vdbi__xdziu = 'np.stack(({},), 1){}'.format(klt__kbe, wdomi__sfb)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(gab__jylj)))
    index = f'pd.Index({gab__jylj})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(vdbi__xdziu)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        gyzv__ygb)
    return _gen_init_df(header, gab__jylj, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    pse__kzzv = dict(axis=axis, level=level, numeric_only=numeric_only)
    vpqk__coaq = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    yckf__dpl = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    yckf__dpl += '  data = np.array([{}])\n'.format(data_args)
    mrt__ivj = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    yckf__dpl += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {mrt__ivj})\n'
        )
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'np': np}, zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    pse__kzzv = dict(axis=axis)
    vpqk__coaq = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    yckf__dpl = 'def impl(df, axis=0, dropna=True):\n'
    yckf__dpl += '  data = np.asarray(({},))\n'.format(data_args)
    mrt__ivj = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    yckf__dpl += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {mrt__ivj})\n'
        )
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'np': np}, zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    pse__kzzv = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    vpqk__coaq = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    pse__kzzv = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    vpqk__coaq = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    pse__kzzv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vpqk__coaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    pse__kzzv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vpqk__coaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    pse__kzzv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vpqk__coaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    pse__kzzv = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    vpqk__coaq = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    pse__kzzv = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    vpqk__coaq = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    pse__kzzv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vpqk__coaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    pse__kzzv = dict(numeric_only=numeric_only, interpolation=interpolation)
    vpqk__coaq = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    pse__kzzv = dict(axis=axis, skipna=skipna)
    vpqk__coaq = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for iudr__kyb in df.data:
        if not (bodo.utils.utils.is_np_array_typ(iudr__kyb) and (iudr__kyb.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            iudr__kyb.dtype, (types.Number, types.Boolean))) or isinstance(
            iudr__kyb, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            iudr__kyb in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {iudr__kyb} not supported.'
                )
        if isinstance(iudr__kyb, bodo.CategoricalArrayType
            ) and not iudr__kyb.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    pse__kzzv = dict(axis=axis, skipna=skipna)
    vpqk__coaq = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for iudr__kyb in df.data:
        if not (bodo.utils.utils.is_np_array_typ(iudr__kyb) and (iudr__kyb.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            iudr__kyb.dtype, (types.Number, types.Boolean))) or isinstance(
            iudr__kyb, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            iudr__kyb in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {iudr__kyb} not supported.'
                )
        if isinstance(iudr__kyb, bodo.CategoricalArrayType
            ) and not iudr__kyb.dtype.ordered:
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
        gab__jylj = tuple(oyi__txn for oyi__txn, jvp__ezidt in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (jvp__ezidt.dtype))
        out_colnames = gab__jylj
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            xhttr__htk = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[oyi__txn]].dtype) for oyi__txn in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(xhttr__htk, []))
    except NotImplementedError as vnt__seo:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    iae__unbuu = ''
    if func_name in ('sum', 'prod'):
        iae__unbuu = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    yckf__dpl = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, iae__unbuu))
    if func_name == 'quantile':
        yckf__dpl = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        yckf__dpl = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        yckf__dpl += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        yckf__dpl += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    ehpk__osiam = ''
    if func_name in ('min', 'max'):
        ehpk__osiam = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        ehpk__osiam = ', dtype=np.float32'
    xsfn__stfh = f'bodo.libs.array_ops.array_op_{func_name}'
    dxk__qww = ''
    if func_name in ['sum', 'prod']:
        dxk__qww = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        dxk__qww = 'index'
    elif func_name == 'quantile':
        dxk__qww = 'q'
    elif func_name in ['std', 'var']:
        dxk__qww = 'True, ddof'
    elif func_name == 'median':
        dxk__qww = 'True'
    data_args = ', '.join(
        f'{xsfn__stfh}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[oyi__txn]}), {dxk__qww})'
         for oyi__txn in out_colnames)
    yckf__dpl = ''
    if func_name in ('idxmax', 'idxmin'):
        yckf__dpl += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        yckf__dpl += ('  data = bodo.utils.conversion.coerce_to_array(({},))\n'
            .format(data_args))
    else:
        yckf__dpl += '  data = np.asarray(({},){})\n'.format(data_args,
            ehpk__osiam)
    yckf__dpl += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return yckf__dpl


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    yaz__lfay = [df_type.column_index[oyi__txn] for oyi__txn in out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in yaz__lfay)
    nckfx__eyc = '\n        '.join(f'row[{i}] = arr_{yaz__lfay[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    rcfxx__xit = f'len(arr_{yaz__lfay[0]})'
    vmyv__sglxs = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in vmyv__sglxs:
        xwe__lmvt = vmyv__sglxs[func_name]
        kjadc__ytdkl = 'float64' if func_name in ['mean', 'median', 'std',
            'var'] else comm_dtype
        yckf__dpl = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {rcfxx__xit}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{kjadc__ytdkl})
    for i in numba.parfors.parfor.internal_prange(n):
        {nckfx__eyc}
        A[i] = {xwe__lmvt}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return yckf__dpl
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    pse__kzzv = dict(fill_method=fill_method, limit=limit, freq=freq)
    vpqk__coaq = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', pse__kzzv, vpqk__coaq,
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
    pse__kzzv = dict(axis=axis, skipna=skipna)
    vpqk__coaq = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', pse__kzzv, vpqk__coaq,
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
    pse__kzzv = dict(skipna=skipna)
    vpqk__coaq = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', pse__kzzv, vpqk__coaq,
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
    pse__kzzv = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    vpqk__coaq = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    gab__jylj = [oyi__txn for oyi__txn, jvp__ezidt in zip(df.columns, df.
        data) if _is_describe_type(jvp__ezidt)]
    if len(gab__jylj) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    ovx__zvdx = sum(df.data[df.column_index[oyi__txn]].dtype == bodo.
        datetime64ns for oyi__txn in gab__jylj)

    def _get_describe(col_ind):
        kmdrw__sgl = df.data[col_ind].dtype == bodo.datetime64ns
        if ovx__zvdx and ovx__zvdx != len(gab__jylj):
            if kmdrw__sgl:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for oyi__txn in gab__jylj:
        col_ind = df.column_index[oyi__txn]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[oyi__txn]) for
        oyi__txn in gab__jylj)
    jdh__acf = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if ovx__zvdx == len(gab__jylj):
        jdh__acf = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif ovx__zvdx:
        jdh__acf = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({jdh__acf})'
    return _gen_init_df(header, gab__jylj, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    pse__kzzv = dict(axis=axis, convert=convert, is_copy=is_copy)
    vpqk__coaq = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', pse__kzzv, vpqk__coaq,
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
    pse__kzzv = dict(freq=freq, axis=axis, fill_value=fill_value)
    vpqk__coaq = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for qxw__agohw in df.data:
        if not is_supported_shift_array_type(qxw__agohw):
            raise BodoError(
                f'Dataframe.shift() column input type {qxw__agohw.dtype} not supported yet.'
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
    pse__kzzv = dict(axis=axis)
    vpqk__coaq = dict(axis=0)
    check_unsupported_args('DataFrame.diff', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for qxw__agohw in df.data:
        if not (isinstance(qxw__agohw, types.Array) and (isinstance(
            qxw__agohw.dtype, types.Number) or qxw__agohw.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {qxw__agohw.dtype} not supported.'
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
    droe__egq = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(droe__egq)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        yjtys__hvncg = get_overload_const_list(column)
    else:
        yjtys__hvncg = [get_literal_value(column)]
    ljs__ufen = [df.column_index[oyi__txn] for oyi__txn in yjtys__hvncg]
    for i in ljs__ufen:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{ljs__ufen[0]})\n'
        )
    for i in range(n):
        if i in ljs__ufen:
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
    qyo__lcsk = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    wgtjb__cbgw = {'inplace': False, 'append': False, 'verify_integrity': False
        }
    check_unsupported_args('DataFrame.set_index', qyo__lcsk, wgtjb__cbgw,
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
    columns = tuple(oyi__txn for oyi__txn in df.columns if oyi__txn != col_name
        )
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    qyo__lcsk = {'inplace': inplace}
    wgtjb__cbgw = {'inplace': False}
    check_unsupported_args('query', qyo__lcsk, wgtjb__cbgw, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        igjai__yyy = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[igjai__yyy]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    qyo__lcsk = {'subset': subset, 'keep': keep}
    wgtjb__cbgw = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', qyo__lcsk, wgtjb__cbgw,
        package_name='pandas', module_name='DataFrame')
    kdet__bfnv = len(df.columns)
    yckf__dpl = "def impl(df, subset=None, keep='first'):\n"
    for i in range(kdet__bfnv):
        yckf__dpl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    wjqy__ujgd = ', '.join(f'data_{i}' for i in range(kdet__bfnv))
    wjqy__ujgd += ',' if kdet__bfnv == 1 else ''
    yckf__dpl += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({wjqy__ujgd}))\n')
    yckf__dpl += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    yckf__dpl += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo}, zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    qyo__lcsk = {'keep': keep, 'inplace': inplace, 'ignore_index': ignore_index
        }
    wgtjb__cbgw = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    qnfsb__ursz = []
    if is_overload_constant_list(subset):
        qnfsb__ursz = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        qnfsb__ursz = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        qnfsb__ursz = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    baz__lill = []
    for col_name in qnfsb__ursz:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        baz__lill.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', qyo__lcsk,
        wgtjb__cbgw, package_name='pandas', module_name='DataFrame')
    csp__sascg = []
    if baz__lill:
        for gwme__foz in baz__lill:
            if isinstance(df.data[gwme__foz], bodo.MapArrayType):
                csp__sascg.append(df.columns[gwme__foz])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                csp__sascg.append(col_name)
    if csp__sascg:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {csp__sascg} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    kdet__bfnv = len(df.columns)
    spiaf__vgpa = ['data_{}'.format(i) for i in baz__lill]
    kem__mxry = ['data_{}'.format(i) for i in range(kdet__bfnv) if i not in
        baz__lill]
    if spiaf__vgpa:
        vlls__wmi = len(spiaf__vgpa)
    else:
        vlls__wmi = kdet__bfnv
    ekgry__vlj = ', '.join(spiaf__vgpa + kem__mxry)
    data_args = ', '.join('data_{}'.format(i) for i in range(kdet__bfnv))
    yckf__dpl = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(kdet__bfnv):
        yckf__dpl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    yckf__dpl += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(ekgry__vlj, index, vlls__wmi))
    yckf__dpl += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(yckf__dpl, df.columns, data_args, 'index')


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
            oxfdl__arr = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                oxfdl__arr = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                oxfdl__arr = lambda i: f'other[:,{i}]'
        kdet__bfnv = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {oxfdl__arr(i)})'
             for i in range(kdet__bfnv))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        npv__lpgho = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(npv__lpgho
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    pse__kzzv = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    vpqk__coaq = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', pse__kzzv, vpqk__coaq,
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
    kdet__bfnv = len(df.columns)
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
        for i in range(kdet__bfnv):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(kdet__bfnv):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(kdet__bfnv):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    wazu__vwl = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    yckf__dpl = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    zxnf__onesa = {}
    fidbr__onvt = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': wazu__vwl}
    fidbr__onvt.update(extra_globals)
    exec(yckf__dpl, fidbr__onvt, zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        asiq__lhpga = pd.Index(lhs.columns)
        sgfa__mqxb = pd.Index(rhs.columns)
        ktje__nxcu, ongel__bxn, aobv__wll = asiq__lhpga.join(sgfa__mqxb,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(ktje__nxcu), ongel__bxn, aobv__wll
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        grmzu__qwbyn = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        rpa__utxo = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, grmzu__qwbyn)
        check_runtime_cols_unsupported(rhs, grmzu__qwbyn)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                ktje__nxcu, ongel__bxn, aobv__wll = _get_binop_columns(lhs, rhs
                    )
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {orgp__oqv}) {grmzu__qwbyn}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {qbwrk__nhklc})'
                     if orgp__oqv != -1 and qbwrk__nhklc != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for orgp__oqv, qbwrk__nhklc in zip(ongel__bxn, aobv__wll))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, ktje__nxcu, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            fraqj__joi = []
            gbbif__bbdws = []
            if op in rpa__utxo:
                for i, jpx__yajsj in enumerate(lhs.data):
                    if is_common_scalar_dtype([jpx__yajsj.dtype, rhs]):
                        fraqj__joi.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {grmzu__qwbyn} rhs'
                            )
                    else:
                        ulsa__farq = f'arr{i}'
                        gbbif__bbdws.append(ulsa__farq)
                        fraqj__joi.append(ulsa__farq)
                data_args = ', '.join(fraqj__joi)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {grmzu__qwbyn} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(gbbif__bbdws) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {ulsa__farq} = np.empty(n, dtype=np.bool_)\n' for
                    ulsa__farq in gbbif__bbdws)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(ulsa__farq, 
                    op == operator.ne) for ulsa__farq in gbbif__bbdws)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            fraqj__joi = []
            gbbif__bbdws = []
            if op in rpa__utxo:
                for i, jpx__yajsj in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, jpx__yajsj.dtype]):
                        fraqj__joi.append(
                            f'lhs {grmzu__qwbyn} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        ulsa__farq = f'arr{i}'
                        gbbif__bbdws.append(ulsa__farq)
                        fraqj__joi.append(ulsa__farq)
                data_args = ', '.join(fraqj__joi)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, grmzu__qwbyn) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(gbbif__bbdws) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(ulsa__farq) for ulsa__farq in gbbif__bbdws)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(ulsa__farq, 
                    op == operator.ne) for ulsa__farq in gbbif__bbdws)
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
        npv__lpgho = create_binary_op_overload(op)
        overload(op)(npv__lpgho)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        grmzu__qwbyn = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, grmzu__qwbyn)
        check_runtime_cols_unsupported(right, grmzu__qwbyn)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                ktje__nxcu, _, aobv__wll = _get_binop_columns(left, right, True
                    )
                yckf__dpl = 'def impl(left, right):\n'
                for i, qbwrk__nhklc in enumerate(aobv__wll):
                    if qbwrk__nhklc == -1:
                        yckf__dpl += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    yckf__dpl += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    yckf__dpl += f"""  df_arr{i} {grmzu__qwbyn} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {qbwrk__nhklc})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    ktje__nxcu)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(yckf__dpl, ktje__nxcu, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            yckf__dpl = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                yckf__dpl += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                yckf__dpl += '  df_arr{0} {1} right\n'.format(i, grmzu__qwbyn)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(yckf__dpl, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        npv__lpgho = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(npv__lpgho)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            grmzu__qwbyn = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, grmzu__qwbyn)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, grmzu__qwbyn) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        npv__lpgho = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(npv__lpgho)


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
            vzdle__lql = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                vzdle__lql[i] = bodo.libs.array_kernels.isna(obj, i)
            return vzdle__lql
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
            vzdle__lql = np.empty(n, np.bool_)
            for i in range(n):
                vzdle__lql[i] = pd.isna(obj[i])
            return vzdle__lql
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
    qyo__lcsk = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    wgtjb__cbgw = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', qyo__lcsk, wgtjb__cbgw, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    sqvp__jvsiy = str(expr_node)
    return sqvp__jvsiy.startswith('left.') or sqvp__jvsiy.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    chhk__pung = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (chhk__pung,))
    cjkp__iywa = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        hink__aqz = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        fmx__ydn = {('NOT_NA', cjkp__iywa(jpx__yajsj)): jpx__yajsj for
            jpx__yajsj in null_set}
        iuyrm__tohp, _, _ = _parse_query_expr(hink__aqz, env, [], [], None,
            join_cleaned_cols=fmx__ydn)
        aaspg__uzwq = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            kpkhv__sqnq = pd.core.computation.ops.BinOp('&', iuyrm__tohp,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = aaspg__uzwq
        return kpkhv__sqnq

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                wrdpe__slco = set()
                zqnzi__snbjw = set()
                jojtd__yjjhe = _insert_NA_cond_body(expr_node.lhs, wrdpe__slco)
                clvn__txcq = _insert_NA_cond_body(expr_node.rhs, zqnzi__snbjw)
                zfh__jhkqe = wrdpe__slco.intersection(zqnzi__snbjw)
                wrdpe__slco.difference_update(zfh__jhkqe)
                zqnzi__snbjw.difference_update(zfh__jhkqe)
                null_set.update(zfh__jhkqe)
                expr_node.lhs = append_null_checks(jojtd__yjjhe, wrdpe__slco)
                expr_node.rhs = append_null_checks(clvn__txcq, zqnzi__snbjw)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            jkw__qdcov = expr_node.name
            hrdh__zernz, col_name = jkw__qdcov.split('.')
            if hrdh__zernz == 'left':
                olot__isy = left_columns
                data = left_data
            else:
                olot__isy = right_columns
                data = right_data
            udg__hae = data[olot__isy.index(col_name)]
            if bodo.utils.typing.is_nullable(udg__hae):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    ngm__cdl = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        plj__bwlmi = str(expr_node.lhs)
        ohvkr__jpkob = str(expr_node.rhs)
        if plj__bwlmi.startswith('left.') and ohvkr__jpkob.startswith('left.'
            ) or plj__bwlmi.startswith('right.') and ohvkr__jpkob.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [plj__bwlmi.split('.')[1]]
        right_on = [ohvkr__jpkob.split('.')[1]]
        if plj__bwlmi.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        yqtaj__felaw, mmtj__umhs, azpwc__ctcz = _extract_equal_conds(expr_node
            .lhs)
        mlsh__kupa, kxxgi__xzr, wgvjb__ynra = _extract_equal_conds(expr_node
            .rhs)
        left_on = yqtaj__felaw + mlsh__kupa
        right_on = mmtj__umhs + kxxgi__xzr
        if azpwc__ctcz is None:
            return left_on, right_on, wgvjb__ynra
        if wgvjb__ynra is None:
            return left_on, right_on, azpwc__ctcz
        expr_node.lhs = azpwc__ctcz
        expr_node.rhs = wgvjb__ynra
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    chhk__pung = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (chhk__pung,))
    yougy__lmt = dict()
    cjkp__iywa = pd.core.computation.parsing.clean_column_name
    for name, uynl__nkf in (('left', left_columns), ('right', right_columns)):
        for jpx__yajsj in uynl__nkf:
            rgkg__rbu = cjkp__iywa(jpx__yajsj)
            mijja__gvsf = name, rgkg__rbu
            if mijja__gvsf in yougy__lmt:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{jpx__yajsj}' and '{yougy__lmt[rgkg__rbu]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            yougy__lmt[mijja__gvsf] = jpx__yajsj
    hcgp__dwr, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=yougy__lmt)
    left_on, right_on, eoxuk__bpkk = _extract_equal_conds(hcgp__dwr.terms)
    return left_on, right_on, _insert_NA_cond(eoxuk__bpkk, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    pse__kzzv = dict(sort=sort, copy=copy, validate=validate)
    vpqk__coaq = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    snspm__iwgcf = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    trcpw__fqvbb = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in snspm__iwgcf and ('left.' in on_str or 
                'right.' in on_str):
                left_on, right_on, circb__zwrlx = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if circb__zwrlx is None:
                    trcpw__fqvbb = ''
                else:
                    trcpw__fqvbb = str(circb__zwrlx)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = snspm__iwgcf
        right_keys = snspm__iwgcf
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
    sqh__ujb = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        jdni__lmo = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        jdni__lmo = list(get_overload_const_list(suffixes))
    suffix_x = jdni__lmo[0]
    suffix_y = jdni__lmo[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    yckf__dpl = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    yckf__dpl += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    yckf__dpl += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    yckf__dpl += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, sqh__ujb, trcpw__fqvbb))
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo}, zxnf__onesa)
    _impl = zxnf__onesa['_impl']
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
    sch__usky = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    nbbd__mzz = {get_overload_const_str(camu__tnak) for camu__tnak in (
        left_on, right_on, on) if is_overload_constant_str(camu__tnak)}
    for df in (left, right):
        for i, jpx__yajsj in enumerate(df.data):
            if not isinstance(jpx__yajsj, valid_dataframe_column_types
                ) and jpx__yajsj not in sch__usky:
                raise BodoError(
                    f'{name_func}(): use of column with {type(jpx__yajsj)} in merge unsupported'
                    )
            if df.columns[i] in nbbd__mzz and isinstance(jpx__yajsj,
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
        jdni__lmo = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        jdni__lmo = list(get_overload_const_list(suffixes))
    if len(jdni__lmo) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    snspm__iwgcf = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        lifs__gwsm = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            lifs__gwsm = on_str not in snspm__iwgcf and ('left.' in on_str or
                'right.' in on_str)
        if len(snspm__iwgcf) == 0 and not lifs__gwsm:
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
    flbs__kiwf = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            uldc__lzt = left.index
            zob__mju = isinstance(uldc__lzt, StringIndexType)
            cbfur__qaa = right.index
            qzyg__opnfr = isinstance(cbfur__qaa, StringIndexType)
        elif is_overload_true(left_index):
            uldc__lzt = left.index
            zob__mju = isinstance(uldc__lzt, StringIndexType)
            cbfur__qaa = right.data[right.columns.index(right_keys[0])]
            qzyg__opnfr = cbfur__qaa.dtype == string_type
        elif is_overload_true(right_index):
            uldc__lzt = left.data[left.columns.index(left_keys[0])]
            zob__mju = uldc__lzt.dtype == string_type
            cbfur__qaa = right.index
            qzyg__opnfr = isinstance(cbfur__qaa, StringIndexType)
        if zob__mju and qzyg__opnfr:
            return
        uldc__lzt = uldc__lzt.dtype
        cbfur__qaa = cbfur__qaa.dtype
        try:
            jgixf__vbl = flbs__kiwf.resolve_function_type(operator.eq, (
                uldc__lzt, cbfur__qaa), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=uldc__lzt, rk_dtype=cbfur__qaa))
    else:
        for issb__dkdqp, zdb__yhw in zip(left_keys, right_keys):
            uldc__lzt = left.data[left.columns.index(issb__dkdqp)].dtype
            phn__qsb = left.data[left.columns.index(issb__dkdqp)]
            cbfur__qaa = right.data[right.columns.index(zdb__yhw)].dtype
            plxf__vyozd = right.data[right.columns.index(zdb__yhw)]
            if phn__qsb == plxf__vyozd:
                continue
            zshhe__ptd = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=issb__dkdqp, lk_dtype=uldc__lzt, rk=zdb__yhw,
                rk_dtype=cbfur__qaa))
            ucl__mnox = uldc__lzt == string_type
            fnh__vzijx = cbfur__qaa == string_type
            if ucl__mnox ^ fnh__vzijx:
                raise_bodo_error(zshhe__ptd)
            try:
                jgixf__vbl = flbs__kiwf.resolve_function_type(operator.eq,
                    (uldc__lzt, cbfur__qaa), {})
            except:
                raise_bodo_error(zshhe__ptd)


def validate_keys(keys, df):
    gwtc__cxra = set(keys).difference(set(df.columns))
    if len(gwtc__cxra) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in gwtc__cxra:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {gwtc__cxra} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    pse__kzzv = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    vpqk__coaq = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', pse__kzzv, vpqk__coaq,
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
    yckf__dpl = "def _impl(left, other, on=None, how='left',\n"
    yckf__dpl += "    lsuffix='', rsuffix='', sort=False):\n"
    yckf__dpl += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo}, zxnf__onesa)
    _impl = zxnf__onesa['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        csabs__fgxi = get_overload_const_list(on)
        validate_keys(csabs__fgxi, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    snspm__iwgcf = tuple(set(left.columns) & set(other.columns))
    if len(snspm__iwgcf) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=snspm__iwgcf))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    fkuay__ldzy = set(left_keys) & set(right_keys)
    fial__ded = set(left_columns) & set(right_columns)
    gvujp__wjn = fial__ded - fkuay__ldzy
    xqttm__zqxml = set(left_columns) - fial__ded
    tfuv__nlxds = set(right_columns) - fial__ded
    tld__yfy = {}

    def insertOutColumn(col_name):
        if col_name in tld__yfy:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        tld__yfy[col_name] = 0
    for jgtt__nuo in fkuay__ldzy:
        insertOutColumn(jgtt__nuo)
    for jgtt__nuo in gvujp__wjn:
        lufb__ahne = str(jgtt__nuo) + suffix_x
        xmau__qex = str(jgtt__nuo) + suffix_y
        insertOutColumn(lufb__ahne)
        insertOutColumn(xmau__qex)
    for jgtt__nuo in xqttm__zqxml:
        insertOutColumn(jgtt__nuo)
    for jgtt__nuo in tfuv__nlxds:
        insertOutColumn(jgtt__nuo)
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
    snspm__iwgcf = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = snspm__iwgcf
        right_keys = snspm__iwgcf
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
        jdni__lmo = suffixes
    if is_overload_constant_list(suffixes):
        jdni__lmo = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        jdni__lmo = suffixes.value
    suffix_x = jdni__lmo[0]
    suffix_y = jdni__lmo[1]
    yckf__dpl = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    yckf__dpl += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    yckf__dpl += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    yckf__dpl += "    allow_exact_matches=True, direction='backward'):\n"
    yckf__dpl += '  suffix_x = suffixes[0]\n'
    yckf__dpl += '  suffix_y = suffixes[1]\n'
    yckf__dpl += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo}, zxnf__onesa)
    _impl = zxnf__onesa['_impl']
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
    pse__kzzv = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    mqpj__gwhhm = dict(sort=False, group_keys=True, squeeze=False, observed
        =True)
    check_unsupported_args('Dataframe.groupby', pse__kzzv, mqpj__gwhhm,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    egd__umrm = func_name == 'DataFrame.pivot_table'
    if egd__umrm:
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
    okgyg__lrb = get_literal_value(columns)
    if isinstance(okgyg__lrb, (list, tuple)):
        if len(okgyg__lrb) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {okgyg__lrb}"
                )
        okgyg__lrb = okgyg__lrb[0]
    if okgyg__lrb not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {okgyg__lrb} not found in DataFrame {df}."
            )
    tzaqh__jhu = df.column_index[okgyg__lrb]
    if is_overload_none(index):
        osxn__ovne = []
        lubtb__qjmc = []
    else:
        lubtb__qjmc = get_literal_value(index)
        if not isinstance(lubtb__qjmc, (list, tuple)):
            lubtb__qjmc = [lubtb__qjmc]
        osxn__ovne = []
        for index in lubtb__qjmc:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            osxn__ovne.append(df.column_index[index])
    if not (all(isinstance(oyi__txn, int) for oyi__txn in lubtb__qjmc) or
        all(isinstance(oyi__txn, str) for oyi__txn in lubtb__qjmc)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        lpvmw__mwmg = []
        vzwba__fje = []
        susij__okq = osxn__ovne + [tzaqh__jhu]
        for i, oyi__txn in enumerate(df.columns):
            if i not in susij__okq:
                lpvmw__mwmg.append(i)
                vzwba__fje.append(oyi__txn)
    else:
        vzwba__fje = get_literal_value(values)
        if not isinstance(vzwba__fje, (list, tuple)):
            vzwba__fje = [vzwba__fje]
        lpvmw__mwmg = []
        for val in vzwba__fje:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            lpvmw__mwmg.append(df.column_index[val])
    okdgb__svj = set(lpvmw__mwmg) | set(osxn__ovne) | {tzaqh__jhu}
    if len(okdgb__svj) != len(lpvmw__mwmg) + len(osxn__ovne) + 1:
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
    if len(osxn__ovne) == 0:
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
        for thn__kydj in osxn__ovne:
            index_column = df.data[thn__kydj]
            check_valid_index_typ(index_column)
    uglrd__mdc = df.data[tzaqh__jhu]
    if isinstance(uglrd__mdc, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(uglrd__mdc, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for yheb__cwi in lpvmw__mwmg:
        ctazk__rwhif = df.data[yheb__cwi]
        if isinstance(ctazk__rwhif, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or ctazk__rwhif == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (lubtb__qjmc, okgyg__lrb, vzwba__fje, osxn__ovne, tzaqh__jhu,
        lpvmw__mwmg)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (lubtb__qjmc, okgyg__lrb, vzwba__fje, thn__kydj, tzaqh__jhu, myoq__ypz) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(lubtb__qjmc) == 0:
        if is_overload_none(data.index.name_typ):
            pexb__rnb = None,
        else:
            pexb__rnb = get_literal_value(data.index.name_typ),
    else:
        pexb__rnb = tuple(lubtb__qjmc)
    lubtb__qjmc = ColNamesMetaType(pexb__rnb)
    vzwba__fje = ColNamesMetaType(tuple(vzwba__fje))
    okgyg__lrb = ColNamesMetaType((okgyg__lrb,))
    yckf__dpl = 'def impl(data, index=None, columns=None, values=None):\n'
    yckf__dpl += f'    pivot_values = data.iloc[:, {tzaqh__jhu}].unique()\n'
    yckf__dpl += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(thn__kydj) == 0:
        yckf__dpl += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        yckf__dpl += '        (\n'
        for uyg__cslp in thn__kydj:
            yckf__dpl += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {uyg__cslp}),
"""
        yckf__dpl += '        ),\n'
    yckf__dpl += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {tzaqh__jhu}),),
"""
    yckf__dpl += '        (\n'
    for yheb__cwi in myoq__ypz:
        yckf__dpl += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {yheb__cwi}),
"""
    yckf__dpl += '        ),\n'
    yckf__dpl += '        pivot_values,\n'
    yckf__dpl += '        index_lit,\n'
    yckf__dpl += '        columns_lit,\n'
    yckf__dpl += '        values_lit,\n'
    yckf__dpl += '    )\n'
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'index_lit': lubtb__qjmc, 'columns_lit':
        okgyg__lrb, 'values_lit': vzwba__fje}, zxnf__onesa)
    impl = zxnf__onesa['impl']
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
    pse__kzzv = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    vpqk__coaq = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (lubtb__qjmc, okgyg__lrb, vzwba__fje, thn__kydj, tzaqh__jhu, myoq__ypz) = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    sqs__agk = lubtb__qjmc
    lubtb__qjmc = ColNamesMetaType(tuple(lubtb__qjmc))
    vzwba__fje = ColNamesMetaType(tuple(vzwba__fje))
    qkhf__cyj = okgyg__lrb
    okgyg__lrb = ColNamesMetaType((okgyg__lrb,))
    yckf__dpl = 'def impl(\n'
    yckf__dpl += '    data,\n'
    yckf__dpl += '    values=None,\n'
    yckf__dpl += '    index=None,\n'
    yckf__dpl += '    columns=None,\n'
    yckf__dpl += '    aggfunc="mean",\n'
    yckf__dpl += '    fill_value=None,\n'
    yckf__dpl += '    margins=False,\n'
    yckf__dpl += '    dropna=True,\n'
    yckf__dpl += '    margins_name="All",\n'
    yckf__dpl += '    observed=False,\n'
    yckf__dpl += '    sort=True,\n'
    yckf__dpl += '    _pivot_values=None,\n'
    yckf__dpl += '):\n'
    xhg__obzxb = thn__kydj + [tzaqh__jhu] + myoq__ypz
    yckf__dpl += f'    data = data.iloc[:, {xhg__obzxb}]\n'
    nps__kkq = sqs__agk + [qkhf__cyj]
    if not is_overload_none(_pivot_values):
        pkj__ojcx = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(pkj__ojcx)
        yckf__dpl += '    pivot_values = _pivot_values_arr\n'
        yckf__dpl += (
            f'    data = data[data.iloc[:, {len(thn__kydj)}].isin(pivot_values)]\n'
            )
        if all(isinstance(oyi__txn, str) for oyi__txn in pkj__ojcx):
            wlels__mgs = pd.array(pkj__ojcx, 'string')
        elif all(isinstance(oyi__txn, int) for oyi__txn in pkj__ojcx):
            wlels__mgs = np.array(pkj__ojcx, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        wlels__mgs = None
    yckf__dpl += (
        f'    data = data.groupby({nps__kkq!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        yckf__dpl += (
            f'    pivot_values = data.iloc[:, {len(thn__kydj)}].unique()\n')
    yckf__dpl += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    yckf__dpl += '        (\n'
    for i in range(0, len(thn__kydj)):
        yckf__dpl += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    yckf__dpl += '        ),\n'
    yckf__dpl += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(thn__kydj)}),),
"""
    yckf__dpl += '        (\n'
    for i in range(len(thn__kydj) + 1, len(myoq__ypz) + len(thn__kydj) + 1):
        yckf__dpl += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    yckf__dpl += '        ),\n'
    yckf__dpl += '        pivot_values,\n'
    yckf__dpl += '        index_lit,\n'
    yckf__dpl += '        columns_lit,\n'
    yckf__dpl += '        values_lit,\n'
    yckf__dpl += '        check_duplicates=False,\n'
    yckf__dpl += '        _constant_pivot_values=_constant_pivot_values,\n'
    yckf__dpl += '    )\n'
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'numba': numba, 'index_lit': lubtb__qjmc,
        'columns_lit': okgyg__lrb, 'values_lit': vzwba__fje,
        '_pivot_values_arr': wlels__mgs, '_constant_pivot_values':
        _pivot_values}, zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    pse__kzzv = dict(col_level=col_level, ignore_index=ignore_index)
    vpqk__coaq = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', pse__kzzv, vpqk__coaq,
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
    axklx__agovz = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(axklx__agovz, (list, tuple)):
        axklx__agovz = [axklx__agovz]
    for oyi__txn in axklx__agovz:
        if oyi__txn not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {oyi__txn} not found in {frame}."
                )
    kte__vql = [frame.column_index[i] for i in axklx__agovz]
    if is_overload_none(value_vars):
        wep__iksse = []
        unofl__uzai = []
        for i, oyi__txn in enumerate(frame.columns):
            if i not in kte__vql:
                wep__iksse.append(i)
                unofl__uzai.append(oyi__txn)
    else:
        unofl__uzai = get_literal_value(value_vars)
        if not isinstance(unofl__uzai, (list, tuple)):
            unofl__uzai = [unofl__uzai]
        unofl__uzai = [v for v in unofl__uzai if v not in axklx__agovz]
        if not unofl__uzai:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        wep__iksse = []
        for val in unofl__uzai:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            wep__iksse.append(frame.column_index[val])
    for oyi__txn in unofl__uzai:
        if oyi__txn not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {oyi__txn} not found in {frame}."
                )
    if not (all(isinstance(oyi__txn, int) for oyi__txn in unofl__uzai) or
        all(isinstance(oyi__txn, str) for oyi__txn in unofl__uzai)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    bclr__jrgqd = frame.data[wep__iksse[0]]
    gra__axft = [frame.data[i].dtype for i in wep__iksse]
    wep__iksse = np.array(wep__iksse, dtype=np.int64)
    kte__vql = np.array(kte__vql, dtype=np.int64)
    _, bzvfu__jbaz = bodo.utils.typing.get_common_scalar_dtype(gra__axft)
    if not bzvfu__jbaz:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': unofl__uzai, 'val_type':
        bclr__jrgqd}
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
    if frame.is_table_format and all(v == bclr__jrgqd.dtype for v in gra__axft
        ):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            wep__iksse))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(unofl__uzai) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {wep__iksse[0]})
"""
    else:
        olb__rbq = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in wep__iksse)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({olb__rbq},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in kte__vql:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(unofl__uzai)})\n'
            )
    gohv__znnxs = ', '.join(f'out_id{i}' for i in kte__vql) + (', ' if len(
        kte__vql) > 0 else '')
    data_args = gohv__znnxs + 'var_col, val_col'
    columns = tuple(axklx__agovz + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(unofl__uzai)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    pse__kzzv = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    vpqk__coaq = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', pse__kzzv, vpqk__coaq,
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
    pse__kzzv = dict(ignore_index=ignore_index, key=key)
    vpqk__coaq = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', pse__kzzv, vpqk__coaq,
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
    woz__dbzi = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        woz__dbzi.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        pfy__rwqxu = [get_overload_const_tuple(by)]
    else:
        pfy__rwqxu = get_overload_const_list(by)
    pfy__rwqxu = set((k, '') if (k, '') in woz__dbzi else k for k in pfy__rwqxu
        )
    if len(pfy__rwqxu.difference(woz__dbzi)) > 0:
        krii__tvtil = list(set(get_overload_const_list(by)).difference(
            woz__dbzi))
        raise_bodo_error(f'sort_values(): invalid keys {krii__tvtil} for by.')
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
        wrl__hxei = get_overload_const_list(na_position)
        for na_position in wrl__hxei:
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
    pse__kzzv = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    vpqk__coaq = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', pse__kzzv, vpqk__coaq,
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
    pse__kzzv = dict(limit=limit, downcast=downcast)
    vpqk__coaq = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', pse__kzzv, vpqk__coaq,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    xivhs__ybusl = not is_overload_none(value)
    jmo__gyi = not is_overload_none(method)
    if xivhs__ybusl and jmo__gyi:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not xivhs__ybusl and not jmo__gyi:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if xivhs__ybusl:
        ywpf__tbwlz = 'value=value'
    else:
        ywpf__tbwlz = 'method=method'
    data_args = [(
        f"df['{oyi__txn}'].fillna({ywpf__tbwlz}, inplace=inplace)" if
        isinstance(oyi__txn, str) else
        f'df[{oyi__txn}].fillna({ywpf__tbwlz}, inplace=inplace)') for
        oyi__txn in df.columns]
    yckf__dpl = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        yckf__dpl += '  ' + '  \n'.join(data_args) + '\n'
        zxnf__onesa = {}
        exec(yckf__dpl, {}, zxnf__onesa)
        impl = zxnf__onesa['impl']
        return impl
    else:
        return _gen_init_df(yckf__dpl, df.columns, ', '.join(jvp__ezidt +
            '.values' for jvp__ezidt in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    pse__kzzv = dict(col_level=col_level, col_fill=col_fill)
    vpqk__coaq = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', pse__kzzv, vpqk__coaq,
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
    yckf__dpl = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    yckf__dpl += (
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
        nalv__fav = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            nalv__fav)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            yckf__dpl += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            wrvn__rvcej = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = wrvn__rvcej + data_args
        else:
            oleql__vjcff = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [oleql__vjcff] + data_args
    return _gen_init_df(yckf__dpl, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    biec__rzmy = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and biec__rzmy == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(biec__rzmy))


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
        dfkh__linwo = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        csp__znttc = get_overload_const_list(subset)
        dfkh__linwo = []
        for ylfnr__qjzz in csp__znttc:
            if ylfnr__qjzz not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{ylfnr__qjzz}' not in data frame columns {df}"
                    )
            dfkh__linwo.append(df.column_index[ylfnr__qjzz])
    kdet__bfnv = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(kdet__bfnv))
    yckf__dpl = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(kdet__bfnv):
        yckf__dpl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    yckf__dpl += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in dfkh__linwo)))
    yckf__dpl += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(yckf__dpl, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    pse__kzzv = dict(index=index, level=level, errors=errors)
    vpqk__coaq = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', pse__kzzv, vpqk__coaq,
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
            kexe__wnpui = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            kexe__wnpui = get_overload_const_list(labels)
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
            kexe__wnpui = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            kexe__wnpui = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for oyi__txn in kexe__wnpui:
        if oyi__txn not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(oyi__txn, df.columns))
    if len(set(kexe__wnpui)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    yzfy__ccu = tuple(oyi__txn for oyi__txn in df.columns if oyi__txn not in
        kexe__wnpui)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[oyi__txn], '.copy()' if not inplace else '') for
        oyi__txn in yzfy__ccu)
    yckf__dpl = 'def impl(df, labels=None, axis=0, index=None, columns=None,\n'
    yckf__dpl += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(yckf__dpl, yzfy__ccu, data_args, index)


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
    pse__kzzv = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    evy__mkge = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', pse__kzzv, evy__mkge,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    kdet__bfnv = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(kdet__bfnv))
    qnfsr__gbfkv = ', '.join('rhs_data_{}'.format(i) for i in range(kdet__bfnv)
        )
    yckf__dpl = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    yckf__dpl += '  if (frac == 1 or n == len(df)) and not replace:\n'
    yckf__dpl += '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n'
    for i in range(kdet__bfnv):
        yckf__dpl += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    yckf__dpl += '  if frac is None:\n'
    yckf__dpl += '    frac_d = -1.0\n'
    yckf__dpl += '  else:\n'
    yckf__dpl += '    frac_d = frac\n'
    yckf__dpl += '  if n is None:\n'
    yckf__dpl += '    n_i = 0\n'
    yckf__dpl += '  else:\n'
    yckf__dpl += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    yckf__dpl += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({qnfsr__gbfkv},), {index}, n_i, frac_d, replace)
"""
    yckf__dpl += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(yckf__dpl, df.columns,
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
    qyo__lcsk = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    wgtjb__cbgw = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', qyo__lcsk, wgtjb__cbgw,
        package_name='pandas', module_name='DataFrame')
    och__ruwyz = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            uoxa__spx = och__ruwyz + '\n'
            uoxa__spx += 'Index: 0 entries\n'
            uoxa__spx += 'Empty DataFrame'
            print(uoxa__spx)
        return _info_impl
    else:
        yckf__dpl = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        yckf__dpl += '    ncols = df.shape[1]\n'
        yckf__dpl += f'    lines = "{och__ruwyz}\\n"\n'
        yckf__dpl += f'    lines += "{df.index}: "\n'
        yckf__dpl += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            yckf__dpl += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            yckf__dpl += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            yckf__dpl += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        yckf__dpl += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        yckf__dpl += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        yckf__dpl += '    column_width = max(space, 7)\n'
        yckf__dpl += '    column= "Column"\n'
        yckf__dpl += '    underl= "------"\n'
        yckf__dpl += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        yckf__dpl += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        yckf__dpl += '    mem_size = 0\n'
        yckf__dpl += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        yckf__dpl += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        yckf__dpl += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        juey__tzj = dict()
        for i in range(len(df.columns)):
            yckf__dpl += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            ras__lgyb = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                ras__lgyb = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                gtdb__ixubb = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                ras__lgyb = f'{gtdb__ixubb[:-7]}'
            yckf__dpl += f'    col_dtype[{i}] = "{ras__lgyb}"\n'
            if ras__lgyb in juey__tzj:
                juey__tzj[ras__lgyb] += 1
            else:
                juey__tzj[ras__lgyb] = 1
            yckf__dpl += f'    col_name[{i}] = "{df.columns[i]}"\n'
            yckf__dpl += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        yckf__dpl += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        yckf__dpl += '    for i in column_info:\n'
        yckf__dpl += "        lines += f'{i}\\n'\n"
        eoxb__sxan = ', '.join(f'{k}({juey__tzj[k]})' for k in sorted(
            juey__tzj))
        yckf__dpl += f"    lines += 'dtypes: {eoxb__sxan}\\n'\n"
        yckf__dpl += '    mem_size += df.index.nbytes\n'
        yckf__dpl += '    total_size = _sizeof_fmt(mem_size)\n'
        yckf__dpl += "    lines += f'memory usage: {total_size}'\n"
        yckf__dpl += '    print(lines)\n'
        zxnf__onesa = {}
        exec(yckf__dpl, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo': bodo,
            'np': np}, zxnf__onesa)
        _info_impl = zxnf__onesa['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    yckf__dpl = 'def impl(df, index=True, deep=False):\n'
    vso__npowa = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    lont__yfq = is_overload_true(index)
    columns = df.columns
    if lont__yfq:
        columns = ('Index',) + columns
    if len(columns) == 0:
        fokzw__ycu = ()
    elif all(isinstance(oyi__txn, int) for oyi__txn in columns):
        fokzw__ycu = np.array(columns, 'int64')
    elif all(isinstance(oyi__txn, str) for oyi__txn in columns):
        fokzw__ycu = pd.array(columns, 'string')
    else:
        fokzw__ycu = columns
    if df.is_table_format and len(df.columns) > 0:
        uht__gice = int(lont__yfq)
        uwwi__azyw = len(columns)
        yckf__dpl += f'  nbytes_arr = np.empty({uwwi__azyw}, np.int64)\n'
        yckf__dpl += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        yckf__dpl += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {uht__gice})
"""
        if lont__yfq:
            yckf__dpl += f'  nbytes_arr[0] = {vso__npowa}\n'
        yckf__dpl += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if lont__yfq:
            data = f'{vso__npowa},{data}'
        else:
            gjlaz__jutr = ',' if len(columns) == 1 else ''
            data = f'{data}{gjlaz__jutr}'
        yckf__dpl += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        fokzw__ycu}, zxnf__onesa)
    impl = zxnf__onesa['impl']
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
    kpfcf__wfygm = 'read_excel_df{}'.format(next_label())
    setattr(types, kpfcf__wfygm, df_type)
    lqass__fivf = False
    if is_overload_constant_list(parse_dates):
        lqass__fivf = get_overload_const_list(parse_dates)
    iugud__pfio = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    yckf__dpl = f"""
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
    with numba.objmode(df="{kpfcf__wfygm}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{iugud__pfio}}},
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
            parse_dates={lqass__fivf},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    zxnf__onesa = {}
    exec(yckf__dpl, globals(), zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as vnt__seo:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    yckf__dpl = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    yckf__dpl += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    yckf__dpl += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        yckf__dpl += '   fig, ax = plt.subplots()\n'
    else:
        yckf__dpl += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        yckf__dpl += '   fig.set_figwidth(figsize[0])\n'
        yckf__dpl += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        yckf__dpl += '   xlabel = x\n'
    yckf__dpl += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        yckf__dpl += '   ylabel = y\n'
    else:
        yckf__dpl += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        yckf__dpl += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        yckf__dpl += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    yckf__dpl += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            yckf__dpl += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            qxrhq__umv = get_overload_const_str(x)
            tfqg__fwv = df.columns.index(qxrhq__umv)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if tfqg__fwv != i:
                        yckf__dpl += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            yckf__dpl += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        yckf__dpl += '   ax.scatter(df[x], df[y], s=20)\n'
        yckf__dpl += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        yckf__dpl += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        yckf__dpl += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        yckf__dpl += '   ax.legend()\n'
    yckf__dpl += '   return ax\n'
    zxnf__onesa = {}
    exec(yckf__dpl, {'bodo': bodo, 'plt': plt}, zxnf__onesa)
    impl = zxnf__onesa['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for lmmqy__xszbl in df_typ.data:
        if not (isinstance(lmmqy__xszbl, IntegerArrayType) or isinstance(
            lmmqy__xszbl.dtype, types.Number) or lmmqy__xszbl.dtype in (
            bodo.datetime64ns, bodo.timedelta64ns)):
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
        rbgt__elzt = args[0]
        evo__fcyx = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        qqmx__lmhs = rbgt__elzt
        check_runtime_cols_unsupported(rbgt__elzt, 'set_df_col()')
        if isinstance(rbgt__elzt, DataFrameType):
            index = rbgt__elzt.index
            if len(rbgt__elzt.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(rbgt__elzt.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if evo__fcyx in rbgt__elzt.columns:
                yzfy__ccu = rbgt__elzt.columns
                wqqn__rgfvb = rbgt__elzt.columns.index(evo__fcyx)
                kyh__fbd = list(rbgt__elzt.data)
                kyh__fbd[wqqn__rgfvb] = val
                kyh__fbd = tuple(kyh__fbd)
            else:
                yzfy__ccu = rbgt__elzt.columns + (evo__fcyx,)
                kyh__fbd = rbgt__elzt.data + (val,)
            qqmx__lmhs = DataFrameType(kyh__fbd, index, yzfy__ccu,
                rbgt__elzt.dist, rbgt__elzt.is_table_format)
        return qqmx__lmhs(*args)


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
        qepa__zdmd = args[0]
        assert isinstance(qepa__zdmd, DataFrameType) and len(qepa__zdmd.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        ffe__ugozn = args[2]
        assert len(col_names_to_replace) == len(ffe__ugozn
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(qepa__zdmd.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in qepa__zdmd.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(qepa__zdmd,
            '__bodosql_replace_columns_dummy()')
        index = qepa__zdmd.index
        yzfy__ccu = qepa__zdmd.columns
        kyh__fbd = list(qepa__zdmd.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            hmylc__tzinp = ffe__ugozn[i]
            assert isinstance(hmylc__tzinp, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(hmylc__tzinp, SeriesType):
                hmylc__tzinp = hmylc__tzinp.data
            gwme__foz = qepa__zdmd.column_index[col_name]
            kyh__fbd[gwme__foz] = hmylc__tzinp
        kyh__fbd = tuple(kyh__fbd)
        qqmx__lmhs = DataFrameType(kyh__fbd, index, yzfy__ccu, qepa__zdmd.
            dist, qepa__zdmd.is_table_format)
        return qqmx__lmhs(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    uiiib__vsxn = {}

    def _rewrite_membership_op(self, node, left, right):
        ggr__kqmg = node.op
        op = self.visit(ggr__kqmg)
        return op, ggr__kqmg, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    clnwn__vfzyq = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in clnwn__vfzyq:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in clnwn__vfzyq:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        spvlh__bimjs = node.attr
        value = node.value
        vpzar__yetts = pd.core.computation.ops.LOCAL_TAG
        if spvlh__bimjs in ('str', 'dt'):
            try:
                mlgk__pwndo = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as qugry__ron:
                col_name = qugry__ron.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            mlgk__pwndo = str(self.visit(value))
        mijja__gvsf = mlgk__pwndo, spvlh__bimjs
        if mijja__gvsf in join_cleaned_cols:
            spvlh__bimjs = join_cleaned_cols[mijja__gvsf]
        name = mlgk__pwndo + '.' + spvlh__bimjs
        if name.startswith(vpzar__yetts):
            name = name[len(vpzar__yetts):]
        if spvlh__bimjs in ('str', 'dt'):
            nkh__cxwao = columns[cleaned_columns.index(mlgk__pwndo)]
            uiiib__vsxn[nkh__cxwao] = mlgk__pwndo
            self.env.scope[name] = 0
            return self.term_type(vpzar__yetts + name, self.env)
        clnwn__vfzyq.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in clnwn__vfzyq:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        lcy__hgdct = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        evo__fcyx = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(lcy__hgdct), evo__fcyx))

    def op__str__(self):
        ekyx__flmex = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            xllq__iyni)) for xllq__iyni in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(ekyx__flmex)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(ekyx__flmex)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(ekyx__flmex))
    hnk__skn = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    cwm__dvq = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    degib__xlfj = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    qyaio__avpf = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    onx__jgket = pd.core.computation.ops.Term.__str__
    rsbf__mnv = pd.core.computation.ops.MathCall.__str__
    lsx__sflu = pd.core.computation.ops.Op.__str__
    aaspg__uzwq = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        hcgp__dwr = pd.core.computation.expr.Expr(expr, env=env)
        tbp__rvj = str(hcgp__dwr)
    except pd.core.computation.ops.UndefinedVariableError as qugry__ron:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == qugry__ron.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {qugry__ron}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            hnk__skn)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            cwm__dvq)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = degib__xlfj
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = qyaio__avpf
        pd.core.computation.ops.Term.__str__ = onx__jgket
        pd.core.computation.ops.MathCall.__str__ = rsbf__mnv
        pd.core.computation.ops.Op.__str__ = lsx__sflu
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            aaspg__uzwq)
    iwd__wrkq = pd.core.computation.parsing.clean_column_name
    uiiib__vsxn.update({oyi__txn: iwd__wrkq(oyi__txn) for oyi__txn in
        columns if iwd__wrkq(oyi__txn) in hcgp__dwr.names})
    return hcgp__dwr, tbp__rvj, uiiib__vsxn


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        tyyfv__zjgq = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(tyyfv__zjgq))
        nva__wti = namedtuple('Pandas', col_names)
        crxm__hcje = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], nva__wti)
        super(DataFrameTupleIterator, self).__init__(name, crxm__hcje)

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
        gkoio__wigxe = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        gkoio__wigxe = [types.Array(types.int64, 1, 'C')] + gkoio__wigxe
        mbo__exiiy = DataFrameTupleIterator(col_names, gkoio__wigxe)
        return mbo__exiiy(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fln__ksvg = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            fln__ksvg)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    isr__xnui = args[len(args) // 2:]
    ccn__meq = sig.args[len(sig.args) // 2:]
    rwq__dgrms = context.make_helper(builder, sig.return_type)
    iww__nykv = context.get_constant(types.intp, 0)
    ancd__ddwx = cgutils.alloca_once_value(builder, iww__nykv)
    rwq__dgrms.index = ancd__ddwx
    for i, arr in enumerate(isr__xnui):
        setattr(rwq__dgrms, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(isr__xnui, ccn__meq):
        context.nrt.incref(builder, arr_typ, arr)
    res = rwq__dgrms._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    omtnz__gaz, = sig.args
    ypmdd__pgnq, = args
    rwq__dgrms = context.make_helper(builder, omtnz__gaz, value=ypmdd__pgnq)
    mwkct__jzv = signature(types.intp, omtnz__gaz.array_types[1])
    ctzrj__barcv = context.compile_internal(builder, lambda a: len(a),
        mwkct__jzv, [rwq__dgrms.array0])
    index = builder.load(rwq__dgrms.index)
    yhxuq__chs = builder.icmp_signed('<', index, ctzrj__barcv)
    result.set_valid(yhxuq__chs)
    with builder.if_then(yhxuq__chs):
        values = [index]
        for i, arr_typ in enumerate(omtnz__gaz.array_types[1:]):
            pyra__yjccp = getattr(rwq__dgrms, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                jchy__cci = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    jchy__cci, [pyra__yjccp, index])
            else:
                jchy__cci = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    jchy__cci, [pyra__yjccp, index])
            values.append(val)
        value = context.make_tuple(builder, omtnz__gaz.yield_type, values)
        result.yield_(value)
        gia__wwt = cgutils.increment_index(builder, index)
        builder.store(gia__wwt, rwq__dgrms.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    ipw__idik = ir.Assign(rhs, lhs, expr.loc)
    sbyet__jec = lhs
    gddk__mfzd = []
    bsy__cqi = []
    awygb__ljhof = typ.count
    for i in range(awygb__ljhof):
        dpedj__frc = ir.Var(sbyet__jec.scope, mk_unique_var('{}_size{}'.
            format(sbyet__jec.name, i)), sbyet__jec.loc)
        wlwz__hrdyi = ir.Expr.static_getitem(lhs, i, None, sbyet__jec.loc)
        self.calltypes[wlwz__hrdyi] = None
        gddk__mfzd.append(ir.Assign(wlwz__hrdyi, dpedj__frc, sbyet__jec.loc))
        self._define(equiv_set, dpedj__frc, types.intp, wlwz__hrdyi)
        bsy__cqi.append(dpedj__frc)
    biosb__mim = tuple(bsy__cqi)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        biosb__mim, pre=[ipw__idik] + gddk__mfzd)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
