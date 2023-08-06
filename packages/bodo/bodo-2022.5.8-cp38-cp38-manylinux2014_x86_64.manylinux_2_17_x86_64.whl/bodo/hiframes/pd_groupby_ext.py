"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_null_shuffle_info, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df_type,
            'pandas.groupby()')
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        efs__zbql = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, efs__zbql)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_bodo_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type=None,
    dropna_type=None):

    def codegen(context, builder, signature, args):
        joj__frbvg = args[0]
        tapo__vjk = signature.return_type
        librl__ogfg = cgutils.create_struct_proxy(tapo__vjk)(context, builder)
        librl__ogfg.obj = joj__frbvg
        context.nrt.incref(builder, signature.args[0], joj__frbvg)
        return librl__ogfg._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for gkk__hmiss in keys:
        selection.remove(gkk__hmiss)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    tapo__vjk = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return tapo__vjk(obj_type, by_type, as_index_type, dropna_type), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, xdc__mcmtm = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(xdc__mcmtm, (tuple, list)):
                if len(set(xdc__mcmtm).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(xdc__mcmtm).difference(set(grpby.
                        df_type.columns))))
                selection = xdc__mcmtm
            else:
                if xdc__mcmtm not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(xdc__mcmtm))
                selection = xdc__mcmtm,
                series_select = True
            gyqs__iwkxb = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(gyqs__iwkxb, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, xdc__mcmtm = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            xdc__mcmtm):
            gyqs__iwkxb = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(xdc__mcmtm)), {}).return_type
            return signature(gyqs__iwkxb, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    arr_type = to_str_arr_if_dict_array(arr_type)
    vhcq__puyg = arr_type == ArrayItemArrayType(string_array_type)
    cdkdy__vyjc = arr_type.dtype
    if isinstance(cdkdy__vyjc, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {cdkdy__vyjc} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(cdkdy__vyjc, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {cdkdy__vyjc} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(cdkdy__vyjc
        , (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(cdkdy__vyjc, (types.Integer, types.Float, types.Boolean)
        ):
        if vhcq__puyg or cdkdy__vyjc == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(cdkdy__vyjc, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not cdkdy__vyjc.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {cdkdy__vyjc} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(cdkdy__vyjc, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    cdkdy__vyjc = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(cdkdy__vyjc, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(cdkdy__vyjc, types.Integer):
            return IntDtype(cdkdy__vyjc)
        return cdkdy__vyjc
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        odozi__jdhp = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{odozi__jdhp}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for gkk__hmiss in grp.keys:
        if multi_level_names:
            zxfhb__fev = gkk__hmiss, ''
        else:
            zxfhb__fev = gkk__hmiss
        afau__yefg = grp.df_type.columns.index(gkk__hmiss)
        data = to_str_arr_if_dict_array(grp.df_type.data[afau__yefg])
        out_columns.append(zxfhb__fev)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name == 'head':
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name == 'head':
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        vfn__hkn = tuple(grp.df_type.column_index[grp.keys[naub__cbu]] for
            naub__cbu in range(len(grp.keys)))
        isup__jzd = tuple(grp.df_type.data[afau__yefg] for afau__yefg in
            vfn__hkn)
        isup__jzd = tuple(to_str_arr_if_dict_array(vdpw__ulzk) for
            vdpw__ulzk in isup__jzd)
        index = MultiIndexType(isup__jzd, tuple(types.StringLiteral(
            gkk__hmiss) for gkk__hmiss in grp.keys))
    else:
        afau__yefg = grp.df_type.column_index[grp.keys[0]]
        wup__gtfh = to_str_arr_if_dict_array(grp.df_type.data[afau__yefg])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(wup__gtfh,
            types.StringLiteral(grp.keys[0]))
    hnl__obuu = {}
    jahj__fhtnz = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        hnl__obuu[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for sjljn__yhvvm in columns:
            afau__yefg = grp.df_type.column_index[sjljn__yhvvm]
            data = grp.df_type.data[afau__yefg]
            data = to_str_arr_if_dict_array(data)
            vop__wvkez = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                vop__wvkez = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    eumb__emdf = SeriesType(data.dtype, data, None, string_type
                        )
                    dapn__rtd = get_const_func_output_type(func, (
                        eumb__emdf,), {}, typing_context, target_context)
                    if dapn__rtd != ArrayItemArrayType(string_array_type):
                        dapn__rtd = dtype_to_array_type(dapn__rtd)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=sjljn__yhvvm, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    qhdd__bwnci = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    aji__rbil = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    xfsg__mwkc = dict(numeric_only=qhdd__bwnci, min_count=
                        aji__rbil)
                    uktq__gdh = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xfsg__mwkc, uktq__gdh, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    qhdd__bwnci = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    aji__rbil = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    xfsg__mwkc = dict(numeric_only=qhdd__bwnci, min_count=
                        aji__rbil)
                    uktq__gdh = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xfsg__mwkc, uktq__gdh, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    qhdd__bwnci = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    xfsg__mwkc = dict(numeric_only=qhdd__bwnci)
                    uktq__gdh = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xfsg__mwkc, uktq__gdh, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    uprs__ivzbc = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    xxfix__yrzr = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    xfsg__mwkc = dict(axis=uprs__ivzbc, skipna=xxfix__yrzr)
                    uktq__gdh = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xfsg__mwkc, uktq__gdh, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    hlmln__dncdo = args[0] if len(args) > 0 else kws.pop('ddof'
                        , 1)
                    xfsg__mwkc = dict(ddof=hlmln__dncdo)
                    uktq__gdh = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xfsg__mwkc, uktq__gdh, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                dapn__rtd, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                huz__bfyqf = to_str_arr_if_dict_array(dapn__rtd)
                out_data.append(huz__bfyqf)
                out_columns.append(sjljn__yhvvm)
                if func_name == 'agg':
                    lgrup__lsago = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    hnl__obuu[sjljn__yhvvm, lgrup__lsago] = sjljn__yhvvm
                else:
                    hnl__obuu[sjljn__yhvvm, func_name] = sjljn__yhvvm
                out_column_type.append(vop__wvkez)
            else:
                jahj__fhtnz.append(err_msg)
    if func_name == 'sum':
        qkxun__yhz = any([(unn__jkns == ColumnType.NumericalColumn.value) for
            unn__jkns in out_column_type])
        if qkxun__yhz:
            out_data = [unn__jkns for unn__jkns, xbh__qqv in zip(out_data,
                out_column_type) if xbh__qqv != ColumnType.
                NonNumericalColumn.value]
            out_columns = [unn__jkns for unn__jkns, xbh__qqv in zip(
                out_columns, out_column_type) if xbh__qqv != ColumnType.
                NonNumericalColumn.value]
            hnl__obuu = {}
            for sjljn__yhvvm in out_columns:
                if grp.as_index is False and sjljn__yhvvm in grp.keys:
                    continue
                hnl__obuu[sjljn__yhvvm, func_name] = sjljn__yhvvm
    japy__foqy = len(jahj__fhtnz)
    if len(out_data) == 0:
        if japy__foqy == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(japy__foqy, ' was' if japy__foqy == 1 else 's were',
                ','.join(jahj__fhtnz)))
    bwu__pkvn = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            hxc__cyea = IntDtype(out_data[0].dtype)
        else:
            hxc__cyea = out_data[0].dtype
        mck__mmt = types.none if func_name == 'size' else types.StringLiteral(
            grp.selection[0])
        bwu__pkvn = SeriesType(hxc__cyea, index=index, name_typ=mck__mmt)
    return signature(bwu__pkvn, *args), hnl__obuu


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    jvcvz__heup = True
    if isinstance(f_val, str):
        jvcvz__heup = False
        vyj__qwh = f_val
    elif is_overload_constant_str(f_val):
        jvcvz__heup = False
        vyj__qwh = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        jvcvz__heup = False
        vyj__qwh = bodo.utils.typing.get_builtin_function_name(f_val)
    if not jvcvz__heup:
        if vyj__qwh not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {vyj__qwh}')
        gyqs__iwkxb = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(gyqs__iwkxb, (), vyj__qwh, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            nun__oaofi = types.functions.MakeFunctionLiteral(f_val)
        else:
            nun__oaofi = f_val
        validate_udf('agg', nun__oaofi)
        func = get_overload_const_func(nun__oaofi, None)
        mqw__nwpes = func.code if hasattr(func, 'code') else func.__code__
        vyj__qwh = mqw__nwpes.co_name
        gyqs__iwkxb = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(gyqs__iwkxb, (), 'agg', typing_context,
            target_context, nun__oaofi)[0].return_type
    return vyj__qwh, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    mbw__tssu = kws and all(isinstance(nyslt__elsfg, types.Tuple) and len(
        nyslt__elsfg) == 2 for nyslt__elsfg in kws.values())
    if is_overload_none(func) and not mbw__tssu:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not mbw__tssu:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    rtvl__ncj = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if mbw__tssu or is_overload_constant_dict(func):
        if mbw__tssu:
            yopci__xvry = [get_literal_value(tfsvb__fwtv) for tfsvb__fwtv,
                kkna__wdz in kws.values()]
            kwgml__tmcje = [get_literal_value(bwsd__lkqy) for kkna__wdz,
                bwsd__lkqy in kws.values()]
        else:
            opcqz__zkrx = get_overload_constant_dict(func)
            yopci__xvry = tuple(opcqz__zkrx.keys())
            kwgml__tmcje = tuple(opcqz__zkrx.values())
        if 'head' in kwgml__tmcje:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(sjljn__yhvvm not in grp.selection and sjljn__yhvvm not in
            grp.keys for sjljn__yhvvm in yopci__xvry):
            raise_bodo_error(
                f'Selected column names {yopci__xvry} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            kwgml__tmcje)
        if mbw__tssu and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        hnl__obuu = {}
        out_columns = []
        out_data = []
        out_column_type = []
        swnvc__kkk = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for pqo__siida, f_val in zip(yopci__xvry, kwgml__tmcje):
            if isinstance(f_val, (tuple, list)):
                fvc__ztsds = 0
                for nun__oaofi in f_val:
                    vyj__qwh, out_tp = get_agg_funcname_and_outtyp(grp,
                        pqo__siida, nun__oaofi, typing_context, target_context)
                    rtvl__ncj = vyj__qwh in list_cumulative
                    if vyj__qwh == '<lambda>' and len(f_val) > 1:
                        vyj__qwh = '<lambda_' + str(fvc__ztsds) + '>'
                        fvc__ztsds += 1
                    out_columns.append((pqo__siida, vyj__qwh))
                    hnl__obuu[pqo__siida, vyj__qwh] = pqo__siida, vyj__qwh
                    _append_out_type(grp, out_data, out_tp)
            else:
                vyj__qwh, out_tp = get_agg_funcname_and_outtyp(grp,
                    pqo__siida, f_val, typing_context, target_context)
                rtvl__ncj = vyj__qwh in list_cumulative
                if multi_level_names:
                    out_columns.append((pqo__siida, vyj__qwh))
                    hnl__obuu[pqo__siida, vyj__qwh] = pqo__siida, vyj__qwh
                elif not mbw__tssu:
                    out_columns.append(pqo__siida)
                    hnl__obuu[pqo__siida, vyj__qwh] = pqo__siida
                elif mbw__tssu:
                    swnvc__kkk.append(vyj__qwh)
                _append_out_type(grp, out_data, out_tp)
        if mbw__tssu:
            for naub__cbu, las__mzen in enumerate(kws.keys()):
                out_columns.append(las__mzen)
                hnl__obuu[yopci__xvry[naub__cbu], swnvc__kkk[naub__cbu]
                    ] = las__mzen
        if rtvl__ncj:
            index = grp.df_type.index
        else:
            index = out_tp.index
        bwu__pkvn = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(bwu__pkvn, *args), hnl__obuu
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            yahcz__xhyho = get_overload_const_list(func)
        else:
            yahcz__xhyho = func.types
        if len(yahcz__xhyho) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        fvc__ztsds = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        hnl__obuu = {}
        cfub__euqjf = grp.selection[0]
        for f_val in yahcz__xhyho:
            vyj__qwh, out_tp = get_agg_funcname_and_outtyp(grp, cfub__euqjf,
                f_val, typing_context, target_context)
            rtvl__ncj = vyj__qwh in list_cumulative
            if vyj__qwh == '<lambda>' and len(yahcz__xhyho) > 1:
                vyj__qwh = '<lambda_' + str(fvc__ztsds) + '>'
                fvc__ztsds += 1
            out_columns.append(vyj__qwh)
            hnl__obuu[cfub__euqjf, vyj__qwh] = vyj__qwh
            _append_out_type(grp, out_data, out_tp)
        if rtvl__ncj:
            index = grp.df_type.index
        else:
            index = out_tp.index
        bwu__pkvn = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(bwu__pkvn, *args), hnl__obuu
    vyj__qwh = ''
    if types.unliteral(func) == types.unicode_type:
        vyj__qwh = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        vyj__qwh = bodo.utils.typing.get_builtin_function_name(func)
    if vyj__qwh:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, vyj__qwh, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        uprs__ivzbc = args[0] if len(args) > 0 else kws.pop('axis', 0)
        qhdd__bwnci = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        xxfix__yrzr = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        xfsg__mwkc = dict(axis=uprs__ivzbc, numeric_only=qhdd__bwnci)
        uktq__gdh = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', xfsg__mwkc,
            uktq__gdh, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        mtswt__kwm = args[0] if len(args) > 0 else kws.pop('periods', 1)
        qkqag__dsh = args[1] if len(args) > 1 else kws.pop('freq', None)
        uprs__ivzbc = args[2] if len(args) > 2 else kws.pop('axis', 0)
        nmjj__whth = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        xfsg__mwkc = dict(freq=qkqag__dsh, axis=uprs__ivzbc, fill_value=
            nmjj__whth)
        uktq__gdh = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', xfsg__mwkc,
            uktq__gdh, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        ikjnt__rof = args[0] if len(args) > 0 else kws.pop('func', None)
        tzfkt__wiwr = kws.pop('engine', None)
        efl__uin = kws.pop('engine_kwargs', None)
        xfsg__mwkc = dict(engine=tzfkt__wiwr, engine_kwargs=efl__uin)
        uktq__gdh = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', xfsg__mwkc, uktq__gdh,
            package_name='pandas', module_name='GroupBy')
    hnl__obuu = {}
    for sjljn__yhvvm in grp.selection:
        out_columns.append(sjljn__yhvvm)
        hnl__obuu[sjljn__yhvvm, name_operation] = sjljn__yhvvm
        afau__yefg = grp.df_type.columns.index(sjljn__yhvvm)
        data = grp.df_type.data[afau__yefg]
        data = to_str_arr_if_dict_array(data)
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            dapn__rtd, err_msg = get_groupby_output_dtype(data,
                get_literal_value(ikjnt__rof), grp.df_type.index)
            if err_msg == 'ok':
                data = dapn__rtd
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    bwu__pkvn = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        bwu__pkvn = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(bwu__pkvn, *args), hnl__obuu


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        ymik__fhzie = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        icyeh__tec = isinstance(ymik__fhzie, (SeriesType,
            HeterogeneousSeriesType)
            ) and ymik__fhzie.const_info is not None or not isinstance(
            ymik__fhzie, (SeriesType, DataFrameType))
        if icyeh__tec:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                htfjm__cxr = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                vfn__hkn = tuple(grp.df_type.columns.index(grp.keys[
                    naub__cbu]) for naub__cbu in range(len(grp.keys)))
                isup__jzd = tuple(grp.df_type.data[afau__yefg] for
                    afau__yefg in vfn__hkn)
                isup__jzd = tuple(to_str_arr_if_dict_array(vdpw__ulzk) for
                    vdpw__ulzk in isup__jzd)
                htfjm__cxr = MultiIndexType(isup__jzd, tuple(types.literal(
                    gkk__hmiss) for gkk__hmiss in grp.keys))
            else:
                afau__yefg = grp.df_type.columns.index(grp.keys[0])
                wup__gtfh = grp.df_type.data[afau__yefg]
                wup__gtfh = to_str_arr_if_dict_array(wup__gtfh)
                htfjm__cxr = bodo.hiframes.pd_index_ext.array_type_to_index(
                    wup__gtfh, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            iidf__rto = tuple(grp.df_type.data[grp.df_type.columns.index(
                sjljn__yhvvm)] for sjljn__yhvvm in grp.keys)
            iidf__rto = tuple(to_str_arr_if_dict_array(vdpw__ulzk) for
                vdpw__ulzk in iidf__rto)
            bsu__jsf = tuple(types.literal(nyslt__elsfg) for nyslt__elsfg in
                grp.keys) + get_index_name_types(ymik__fhzie.index)
            if not grp.as_index:
                iidf__rto = types.Array(types.int64, 1, 'C'),
                bsu__jsf = (types.none,) + get_index_name_types(ymik__fhzie
                    .index)
            htfjm__cxr = MultiIndexType(iidf__rto +
                get_index_data_arr_types(ymik__fhzie.index), bsu__jsf)
        if icyeh__tec:
            if isinstance(ymik__fhzie, HeterogeneousSeriesType):
                kkna__wdz, yehxm__ehiy = ymik__fhzie.const_info
                if isinstance(ymik__fhzie.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    abg__xwma = ymik__fhzie.data.tuple_typ.types
                elif isinstance(ymik__fhzie.data, types.Tuple):
                    abg__xwma = ymik__fhzie.data.types
                fyfb__rhg = tuple(to_nullable_type(dtype_to_array_type(
                    vdpw__ulzk)) for vdpw__ulzk in abg__xwma)
                olf__zve = DataFrameType(out_data + fyfb__rhg, htfjm__cxr, 
                    out_columns + yehxm__ehiy)
            elif isinstance(ymik__fhzie, SeriesType):
                vgjx__wgbh, yehxm__ehiy = ymik__fhzie.const_info
                fyfb__rhg = tuple(to_nullable_type(dtype_to_array_type(
                    ymik__fhzie.dtype)) for kkna__wdz in range(vgjx__wgbh))
                olf__zve = DataFrameType(out_data + fyfb__rhg, htfjm__cxr, 
                    out_columns + yehxm__ehiy)
            else:
                yebq__eov = get_udf_out_arr_type(ymik__fhzie)
                if not grp.as_index:
                    olf__zve = DataFrameType(out_data + (yebq__eov,),
                        htfjm__cxr, out_columns + ('',))
                else:
                    olf__zve = SeriesType(yebq__eov.dtype, yebq__eov,
                        htfjm__cxr, None)
        elif isinstance(ymik__fhzie, SeriesType):
            olf__zve = SeriesType(ymik__fhzie.dtype, ymik__fhzie.data,
                htfjm__cxr, ymik__fhzie.name_typ)
        else:
            olf__zve = DataFrameType(ymik__fhzie.data, htfjm__cxr,
                ymik__fhzie.columns)
        ogs__oaqjy = gen_apply_pysig(len(f_args), kws.keys())
        jgg__momxl = (func, *f_args) + tuple(kws.values())
        return signature(olf__zve, *jgg__momxl).replace(pysig=ogs__oaqjy)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_bodo_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    ahp__hhp = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            pqo__siida = grp.selection[0]
            yebq__eov = ahp__hhp.data[ahp__hhp.columns.index(pqo__siida)]
            yebq__eov = to_str_arr_if_dict_array(yebq__eov)
            rky__gkgzm = SeriesType(yebq__eov.dtype, yebq__eov, ahp__hhp.
                index, types.literal(pqo__siida))
        else:
            mwjh__ucshi = tuple(ahp__hhp.data[ahp__hhp.columns.index(
                sjljn__yhvvm)] for sjljn__yhvvm in grp.selection)
            mwjh__ucshi = tuple(to_str_arr_if_dict_array(vdpw__ulzk) for
                vdpw__ulzk in mwjh__ucshi)
            rky__gkgzm = DataFrameType(mwjh__ucshi, ahp__hhp.index, tuple(
                grp.selection))
    else:
        rky__gkgzm = ahp__hhp
    frkje__ldona = rky__gkgzm,
    frkje__ldona += tuple(f_args)
    try:
        ymik__fhzie = get_const_func_output_type(func, frkje__ldona, kws,
            typing_context, target_context)
    except Exception as dmu__hqkd:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', dmu__hqkd),
            getattr(dmu__hqkd, 'loc', None))
    return ymik__fhzie


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    frkje__ldona = (grp,) + f_args
    try:
        ymik__fhzie = get_const_func_output_type(func, frkje__ldona, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as dmu__hqkd:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', dmu__hqkd),
            getattr(dmu__hqkd, 'loc', None))
    ogs__oaqjy = gen_apply_pysig(len(f_args), kws.keys())
    jgg__momxl = (func, *f_args) + tuple(kws.values())
    return signature(ymik__fhzie, *jgg__momxl).replace(pysig=ogs__oaqjy)


def gen_apply_pysig(n_args, kws):
    row__nzdls = ', '.join(f'arg{naub__cbu}' for naub__cbu in range(n_args))
    row__nzdls = row__nzdls + ', ' if row__nzdls else ''
    rqzu__gej = ', '.join(f"{acuj__moqp} = ''" for acuj__moqp in kws)
    hbjc__oqysq = f'def apply_stub(func, {row__nzdls}{rqzu__gej}):\n'
    hbjc__oqysq += '    pass\n'
    icyc__yxxvs = {}
    exec(hbjc__oqysq, {}, icyc__yxxvs)
    qibo__btj = icyc__yxxvs['apply_stub']
    return numba.core.utils.pysignature(qibo__btj)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        oti__ehhgv = types.Array(types.int64, 1, 'C')
        pfb__kuyxn = _pivot_values.meta
        nfz__ldhi = len(pfb__kuyxn)
        abmjf__shvtw = bodo.hiframes.pd_index_ext.array_type_to_index(
            to_str_arr_if_dict_array(index.data), types.StringLiteral('index'))
        eui__ujra = DataFrameType((oti__ehhgv,) * nfz__ldhi, abmjf__shvtw,
            tuple(pfb__kuyxn))
        return signature(eui__ujra, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    hbjc__oqysq = 'def impl(keys, dropna, _is_parallel):\n'
    hbjc__oqysq += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    hbjc__oqysq += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{naub__cbu}])' for naub__cbu in range(len(keys
        .types))))
    hbjc__oqysq += '    table = arr_info_list_to_table(info_list)\n'
    hbjc__oqysq += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    hbjc__oqysq += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    hbjc__oqysq += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    hbjc__oqysq += '    delete_table_decref_arrays(table)\n'
    hbjc__oqysq += '    ev.finalize()\n'
    hbjc__oqysq += '    return sort_idx, group_labels, ngroups\n'
    icyc__yxxvs = {}
    exec(hbjc__oqysq, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, icyc__yxxvs)
    pvq__vow = icyc__yxxvs['impl']
    return pvq__vow


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    tnu__wzr = len(labels)
    lydge__jlio = np.zeros(ngroups, dtype=np.int64)
    qqx__xuisn = np.zeros(ngroups, dtype=np.int64)
    sjqtc__oezyi = 0
    tsfo__gvqnc = 0
    for naub__cbu in range(tnu__wzr):
        jvm__jvr = labels[naub__cbu]
        if jvm__jvr < 0:
            sjqtc__oezyi += 1
        else:
            tsfo__gvqnc += 1
            if naub__cbu == tnu__wzr - 1 or jvm__jvr != labels[naub__cbu + 1]:
                lydge__jlio[jvm__jvr] = sjqtc__oezyi
                qqx__xuisn[jvm__jvr] = sjqtc__oezyi + tsfo__gvqnc
                sjqtc__oezyi += tsfo__gvqnc
                tsfo__gvqnc = 0
    return lydge__jlio, qqx__xuisn


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    pvq__vow, kkna__wdz = gen_shuffle_dataframe(df, keys, _is_parallel)
    return pvq__vow


def gen_shuffle_dataframe(df, keys, _is_parallel):
    vgjx__wgbh = len(df.columns)
    fwyss__idrsn = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    hbjc__oqysq = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        hbjc__oqysq += '  return df, keys, get_null_shuffle_info()\n'
        icyc__yxxvs = {}
        exec(hbjc__oqysq, {'get_null_shuffle_info': get_null_shuffle_info},
            icyc__yxxvs)
        pvq__vow = icyc__yxxvs['impl']
        return pvq__vow
    for naub__cbu in range(vgjx__wgbh):
        hbjc__oqysq += f"""  in_arr{naub__cbu} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {naub__cbu})
"""
    hbjc__oqysq += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    hbjc__oqysq += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{naub__cbu}])' for naub__cbu in range(
        fwyss__idrsn)), ', '.join(f'array_to_info(in_arr{naub__cbu})' for
        naub__cbu in range(vgjx__wgbh)), 'array_to_info(in_index_arr)')
    hbjc__oqysq += '  table = arr_info_list_to_table(info_list)\n'
    hbjc__oqysq += (
        f'  out_table = shuffle_table(table, {fwyss__idrsn}, _is_parallel, 1)\n'
        )
    for naub__cbu in range(fwyss__idrsn):
        hbjc__oqysq += f"""  out_key{naub__cbu} = info_to_array(info_from_table(out_table, {naub__cbu}), keys{naub__cbu}_typ)
"""
    for naub__cbu in range(vgjx__wgbh):
        hbjc__oqysq += f"""  out_arr{naub__cbu} = info_to_array(info_from_table(out_table, {naub__cbu + fwyss__idrsn}), in_arr{naub__cbu}_typ)
"""
    hbjc__oqysq += f"""  out_arr_index = info_to_array(info_from_table(out_table, {fwyss__idrsn + vgjx__wgbh}), ind_arr_typ)
"""
    hbjc__oqysq += '  shuffle_info = get_shuffle_info(out_table)\n'
    hbjc__oqysq += '  delete_table(out_table)\n'
    hbjc__oqysq += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{naub__cbu}' for naub__cbu in range(
        vgjx__wgbh))
    hbjc__oqysq += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    hbjc__oqysq += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    hbjc__oqysq += '  return out_df, ({},), shuffle_info\n'.format(', '.
        join(f'out_key{naub__cbu}' for naub__cbu in range(fwyss__idrsn)))
    vzo__fkevs = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    vzo__fkevs.update({f'keys{naub__cbu}_typ': keys.types[naub__cbu] for
        naub__cbu in range(fwyss__idrsn)})
    vzo__fkevs.update({f'in_arr{naub__cbu}_typ': df.data[naub__cbu] for
        naub__cbu in range(vgjx__wgbh)})
    icyc__yxxvs = {}
    exec(hbjc__oqysq, vzo__fkevs, icyc__yxxvs)
    pvq__vow = icyc__yxxvs['impl']
    return pvq__vow, vzo__fkevs


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ply__xsgqc = len(data.array_types)
        hbjc__oqysq = 'def impl(data, shuffle_info):\n'
        hbjc__oqysq += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{naub__cbu}])' for naub__cbu in
            range(ply__xsgqc)))
        hbjc__oqysq += '  table = arr_info_list_to_table(info_list)\n'
        hbjc__oqysq += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for naub__cbu in range(ply__xsgqc):
            hbjc__oqysq += f"""  out_arr{naub__cbu} = info_to_array(info_from_table(out_table, {naub__cbu}), data._data[{naub__cbu}])
"""
        hbjc__oqysq += '  delete_table(out_table)\n'
        hbjc__oqysq += '  delete_table(table)\n'
        hbjc__oqysq += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{naub__cbu}' for naub__cbu in range(
            ply__xsgqc))))
        icyc__yxxvs = {}
        exec(hbjc__oqysq, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, icyc__yxxvs)
        pvq__vow = icyc__yxxvs['impl']
        return pvq__vow
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            nhn__bqtbi = bodo.utils.conversion.index_to_array(data)
            huz__bfyqf = reverse_shuffle(nhn__bqtbi, shuffle_info)
            return bodo.utils.conversion.index_from_array(huz__bfyqf)
        return impl_index

    def impl_arr(data, shuffle_info):
        agyl__esys = [array_to_info(data)]
        zwn__env = arr_info_list_to_table(agyl__esys)
        jaf__luiq = reverse_shuffle_table(zwn__env, shuffle_info)
        huz__bfyqf = info_to_array(info_from_table(jaf__luiq, 0), data)
        delete_table(jaf__luiq)
        delete_table(zwn__env)
        return huz__bfyqf
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    xfsg__mwkc = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    uktq__gdh = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', xfsg__mwkc, uktq__gdh,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    foil__hcsum = get_overload_const_bool(ascending)
    bxhx__pny = grp.selection[0]
    hbjc__oqysq = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    bpzm__hclqa = (
        f"lambda S: S.value_counts(ascending={foil__hcsum}, _index_name='{bxhx__pny}')"
        )
    hbjc__oqysq += f'    return grp.apply({bpzm__hclqa})\n'
    icyc__yxxvs = {}
    exec(hbjc__oqysq, {'bodo': bodo}, icyc__yxxvs)
    pvq__vow = icyc__yxxvs['impl']
    return pvq__vow


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill',
    'ngroup', 'nth', 'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail',
    'corr', 'cov', 'describe', 'diff', 'fillna', 'filter', 'hist', 'mad',
    'plot', 'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupby_unsupported():
    for dihrp__qsy in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, dihrp__qsy, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{dihrp__qsy}'))
    for dihrp__qsy in groupby_unsupported:
        overload_method(DataFrameGroupByType, dihrp__qsy, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{dihrp__qsy}'))
    for dihrp__qsy in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, dihrp__qsy, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{dihrp__qsy}'))
    for dihrp__qsy in series_only_unsupported:
        overload_method(DataFrameGroupByType, dihrp__qsy, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{dihrp__qsy}'))
    for dihrp__qsy in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, dihrp__qsy, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{dihrp__qsy}'))


_install_groupby_unsupported()
