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
        qjmkw__eoxa = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, qjmkw__eoxa)


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
        krsrb__qic = args[0]
        xvndt__qbl = signature.return_type
        kqd__cnrd = cgutils.create_struct_proxy(xvndt__qbl)(context, builder)
        kqd__cnrd.obj = krsrb__qic
        context.nrt.incref(builder, signature.args[0], krsrb__qic)
        return kqd__cnrd._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for sqpzv__eqjvu in keys:
        selection.remove(sqpzv__eqjvu)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    xvndt__qbl = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return xvndt__qbl(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, xxjcq__fcbs = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(xxjcq__fcbs, (tuple, list)):
                if len(set(xxjcq__fcbs).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(xxjcq__fcbs).difference(set(grpby.
                        df_type.columns))))
                selection = xxjcq__fcbs
            else:
                if xxjcq__fcbs not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(xxjcq__fcbs))
                selection = xxjcq__fcbs,
                series_select = True
            rnkdv__qvjcw = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(rnkdv__qvjcw, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, xxjcq__fcbs = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            xxjcq__fcbs):
            rnkdv__qvjcw = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(xxjcq__fcbs)), {}).return_type
            return signature(rnkdv__qvjcw, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    arr_type = to_str_arr_if_dict_array(arr_type)
    ukr__sfqaq = arr_type == ArrayItemArrayType(string_array_type)
    srpu__vjyzd = arr_type.dtype
    if isinstance(srpu__vjyzd, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {srpu__vjyzd} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(srpu__vjyzd, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {srpu__vjyzd} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(srpu__vjyzd
        , (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(srpu__vjyzd, (types.Integer, types.Float, types.Boolean)
        ):
        if ukr__sfqaq or srpu__vjyzd == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(srpu__vjyzd, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not srpu__vjyzd.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {srpu__vjyzd} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(srpu__vjyzd, types.Boolean) and func_name in {'cumsum',
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
    srpu__vjyzd = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(srpu__vjyzd, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(srpu__vjyzd, types.Integer):
            return IntDtype(srpu__vjyzd)
        return srpu__vjyzd
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        hxer__mpw = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{hxer__mpw}'."
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
    for sqpzv__eqjvu in grp.keys:
        if multi_level_names:
            rdcq__xrq = sqpzv__eqjvu, ''
        else:
            rdcq__xrq = sqpzv__eqjvu
        vci__rvdi = grp.df_type.columns.index(sqpzv__eqjvu)
        data = to_str_arr_if_dict_array(grp.df_type.data[vci__rvdi])
        out_columns.append(rdcq__xrq)
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
        jdyyy__cqbz = tuple(grp.df_type.column_index[grp.keys[eggm__huhv]] for
            eggm__huhv in range(len(grp.keys)))
        lxj__oivk = tuple(grp.df_type.data[vci__rvdi] for vci__rvdi in
            jdyyy__cqbz)
        lxj__oivk = tuple(to_str_arr_if_dict_array(yau__fqe) for yau__fqe in
            lxj__oivk)
        index = MultiIndexType(lxj__oivk, tuple(types.StringLiteral(
            sqpzv__eqjvu) for sqpzv__eqjvu in grp.keys))
    else:
        vci__rvdi = grp.df_type.column_index[grp.keys[0]]
        zmpkb__nxk = to_str_arr_if_dict_array(grp.df_type.data[vci__rvdi])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(zmpkb__nxk,
            types.StringLiteral(grp.keys[0]))
    sded__cdlpx = {}
    jei__glf = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        sded__cdlpx[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for yadcv__iiupu in columns:
            vci__rvdi = grp.df_type.column_index[yadcv__iiupu]
            data = grp.df_type.data[vci__rvdi]
            data = to_str_arr_if_dict_array(data)
            cvr__lycq = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                cvr__lycq = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    okbam__brbb = SeriesType(data.dtype, data, None,
                        string_type)
                    wnhn__ewayl = get_const_func_output_type(func, (
                        okbam__brbb,), {}, typing_context, target_context)
                    if wnhn__ewayl != ArrayItemArrayType(string_array_type):
                        wnhn__ewayl = dtype_to_array_type(wnhn__ewayl)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=yadcv__iiupu, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    tshy__son = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    ggu__jcfkx = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    ocn__nemm = dict(numeric_only=tshy__son, min_count=
                        ggu__jcfkx)
                    yffm__hcw = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ocn__nemm, yffm__hcw, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    tshy__son = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    ggu__jcfkx = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    ocn__nemm = dict(numeric_only=tshy__son, min_count=
                        ggu__jcfkx)
                    yffm__hcw = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ocn__nemm, yffm__hcw, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    tshy__son = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    ocn__nemm = dict(numeric_only=tshy__son)
                    yffm__hcw = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ocn__nemm, yffm__hcw, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    goxjk__xuo = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    bcdu__isq = args[1] if len(args) > 1 else kws.pop('skipna',
                        True)
                    ocn__nemm = dict(axis=goxjk__xuo, skipna=bcdu__isq)
                    yffm__hcw = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ocn__nemm, yffm__hcw, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    oqs__cjy = args[0] if len(args) > 0 else kws.pop('ddof', 1)
                    ocn__nemm = dict(ddof=oqs__cjy)
                    yffm__hcw = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        ocn__nemm, yffm__hcw, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                wnhn__ewayl, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                nfju__uacsc = to_str_arr_if_dict_array(wnhn__ewayl)
                out_data.append(nfju__uacsc)
                out_columns.append(yadcv__iiupu)
                if func_name == 'agg':
                    xsb__fsu = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    sded__cdlpx[yadcv__iiupu, xsb__fsu] = yadcv__iiupu
                else:
                    sded__cdlpx[yadcv__iiupu, func_name] = yadcv__iiupu
                out_column_type.append(cvr__lycq)
            else:
                jei__glf.append(err_msg)
    if func_name == 'sum':
        tgdk__ixmzu = any([(gobuo__kju == ColumnType.NumericalColumn.value) for
            gobuo__kju in out_column_type])
        if tgdk__ixmzu:
            out_data = [gobuo__kju for gobuo__kju, mdg__pbvy in zip(
                out_data, out_column_type) if mdg__pbvy != ColumnType.
                NonNumericalColumn.value]
            out_columns = [gobuo__kju for gobuo__kju, mdg__pbvy in zip(
                out_columns, out_column_type) if mdg__pbvy != ColumnType.
                NonNumericalColumn.value]
            sded__cdlpx = {}
            for yadcv__iiupu in out_columns:
                if grp.as_index is False and yadcv__iiupu in grp.keys:
                    continue
                sded__cdlpx[yadcv__iiupu, func_name] = yadcv__iiupu
    okbsv__bbqwl = len(jei__glf)
    if len(out_data) == 0:
        if okbsv__bbqwl == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(okbsv__bbqwl, ' was' if okbsv__bbqwl == 1 else
                's were', ','.join(jei__glf)))
    fqyia__qts = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            hubi__wqhyg = IntDtype(out_data[0].dtype)
        else:
            hubi__wqhyg = out_data[0].dtype
        wxnhf__yksk = (types.none if func_name == 'size' else types.
            StringLiteral(grp.selection[0]))
        fqyia__qts = SeriesType(hubi__wqhyg, index=index, name_typ=wxnhf__yksk)
    return signature(fqyia__qts, *args), sded__cdlpx


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    xnf__lojbp = True
    if isinstance(f_val, str):
        xnf__lojbp = False
        czh__choag = f_val
    elif is_overload_constant_str(f_val):
        xnf__lojbp = False
        czh__choag = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        xnf__lojbp = False
        czh__choag = bodo.utils.typing.get_builtin_function_name(f_val)
    if not xnf__lojbp:
        if czh__choag not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {czh__choag}')
        rnkdv__qvjcw = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(rnkdv__qvjcw, (), czh__choag, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            unxk__eex = types.functions.MakeFunctionLiteral(f_val)
        else:
            unxk__eex = f_val
        validate_udf('agg', unxk__eex)
        func = get_overload_const_func(unxk__eex, None)
        kdgj__nez = func.code if hasattr(func, 'code') else func.__code__
        czh__choag = kdgj__nez.co_name
        rnkdv__qvjcw = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(rnkdv__qvjcw, (), 'agg', typing_context,
            target_context, unxk__eex)[0].return_type
    return czh__choag, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    tfd__eoa = kws and all(isinstance(kdc__qpe, types.Tuple) and len(
        kdc__qpe) == 2 for kdc__qpe in kws.values())
    if is_overload_none(func) and not tfd__eoa:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not tfd__eoa:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    wskh__vrcf = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if tfd__eoa or is_overload_constant_dict(func):
        if tfd__eoa:
            pvaxq__vwrry = [get_literal_value(zucaj__djcvd) for 
                zucaj__djcvd, pzfik__pbu in kws.values()]
            hex__muc = [get_literal_value(nek__ogbp) for pzfik__pbu,
                nek__ogbp in kws.values()]
        else:
            blxt__mau = get_overload_constant_dict(func)
            pvaxq__vwrry = tuple(blxt__mau.keys())
            hex__muc = tuple(blxt__mau.values())
        if 'head' in hex__muc:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(yadcv__iiupu not in grp.selection and yadcv__iiupu not in
            grp.keys for yadcv__iiupu in pvaxq__vwrry):
            raise_bodo_error(
                f'Selected column names {pvaxq__vwrry} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            hex__muc)
        if tfd__eoa and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        sded__cdlpx = {}
        out_columns = []
        out_data = []
        out_column_type = []
        hhue__geyje = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for yyctu__fyacl, f_val in zip(pvaxq__vwrry, hex__muc):
            if isinstance(f_val, (tuple, list)):
                mtbi__tgfi = 0
                for unxk__eex in f_val:
                    czh__choag, out_tp = get_agg_funcname_and_outtyp(grp,
                        yyctu__fyacl, unxk__eex, typing_context, target_context
                        )
                    wskh__vrcf = czh__choag in list_cumulative
                    if czh__choag == '<lambda>' and len(f_val) > 1:
                        czh__choag = '<lambda_' + str(mtbi__tgfi) + '>'
                        mtbi__tgfi += 1
                    out_columns.append((yyctu__fyacl, czh__choag))
                    sded__cdlpx[yyctu__fyacl, czh__choag
                        ] = yyctu__fyacl, czh__choag
                    _append_out_type(grp, out_data, out_tp)
            else:
                czh__choag, out_tp = get_agg_funcname_and_outtyp(grp,
                    yyctu__fyacl, f_val, typing_context, target_context)
                wskh__vrcf = czh__choag in list_cumulative
                if multi_level_names:
                    out_columns.append((yyctu__fyacl, czh__choag))
                    sded__cdlpx[yyctu__fyacl, czh__choag
                        ] = yyctu__fyacl, czh__choag
                elif not tfd__eoa:
                    out_columns.append(yyctu__fyacl)
                    sded__cdlpx[yyctu__fyacl, czh__choag] = yyctu__fyacl
                elif tfd__eoa:
                    hhue__geyje.append(czh__choag)
                _append_out_type(grp, out_data, out_tp)
        if tfd__eoa:
            for eggm__huhv, bqqc__onvq in enumerate(kws.keys()):
                out_columns.append(bqqc__onvq)
                sded__cdlpx[pvaxq__vwrry[eggm__huhv], hhue__geyje[eggm__huhv]
                    ] = bqqc__onvq
        if wskh__vrcf:
            index = grp.df_type.index
        else:
            index = out_tp.index
        fqyia__qts = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(fqyia__qts, *args), sded__cdlpx
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            ypv__hveu = get_overload_const_list(func)
        else:
            ypv__hveu = func.types
        if len(ypv__hveu) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        mtbi__tgfi = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        sded__cdlpx = {}
        trko__kwvv = grp.selection[0]
        for f_val in ypv__hveu:
            czh__choag, out_tp = get_agg_funcname_and_outtyp(grp,
                trko__kwvv, f_val, typing_context, target_context)
            wskh__vrcf = czh__choag in list_cumulative
            if czh__choag == '<lambda>' and len(ypv__hveu) > 1:
                czh__choag = '<lambda_' + str(mtbi__tgfi) + '>'
                mtbi__tgfi += 1
            out_columns.append(czh__choag)
            sded__cdlpx[trko__kwvv, czh__choag] = czh__choag
            _append_out_type(grp, out_data, out_tp)
        if wskh__vrcf:
            index = grp.df_type.index
        else:
            index = out_tp.index
        fqyia__qts = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(fqyia__qts, *args), sded__cdlpx
    czh__choag = ''
    if types.unliteral(func) == types.unicode_type:
        czh__choag = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        czh__choag = bodo.utils.typing.get_builtin_function_name(func)
    if czh__choag:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, czh__choag, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        goxjk__xuo = args[0] if len(args) > 0 else kws.pop('axis', 0)
        tshy__son = args[1] if len(args) > 1 else kws.pop('numeric_only', False
            )
        bcdu__isq = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        ocn__nemm = dict(axis=goxjk__xuo, numeric_only=tshy__son)
        yffm__hcw = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', ocn__nemm,
            yffm__hcw, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        axgnm__zhkh = args[0] if len(args) > 0 else kws.pop('periods', 1)
        bvp__wmenj = args[1] if len(args) > 1 else kws.pop('freq', None)
        goxjk__xuo = args[2] if len(args) > 2 else kws.pop('axis', 0)
        ijy__cugg = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        ocn__nemm = dict(freq=bvp__wmenj, axis=goxjk__xuo, fill_value=ijy__cugg
            )
        yffm__hcw = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', ocn__nemm,
            yffm__hcw, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        brsw__fcq = args[0] if len(args) > 0 else kws.pop('func', None)
        gqv__issps = kws.pop('engine', None)
        jmjd__ntj = kws.pop('engine_kwargs', None)
        ocn__nemm = dict(engine=gqv__issps, engine_kwargs=jmjd__ntj)
        yffm__hcw = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', ocn__nemm, yffm__hcw,
            package_name='pandas', module_name='GroupBy')
    sded__cdlpx = {}
    for yadcv__iiupu in grp.selection:
        out_columns.append(yadcv__iiupu)
        sded__cdlpx[yadcv__iiupu, name_operation] = yadcv__iiupu
        vci__rvdi = grp.df_type.columns.index(yadcv__iiupu)
        data = grp.df_type.data[vci__rvdi]
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
            wnhn__ewayl, err_msg = get_groupby_output_dtype(data,
                get_literal_value(brsw__fcq), grp.df_type.index)
            if err_msg == 'ok':
                data = wnhn__ewayl
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    fqyia__qts = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        fqyia__qts = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(fqyia__qts, *args), sded__cdlpx


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
        vpwg__fvanx = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        ghug__gnloy = isinstance(vpwg__fvanx, (SeriesType,
            HeterogeneousSeriesType)
            ) and vpwg__fvanx.const_info is not None or not isinstance(
            vpwg__fvanx, (SeriesType, DataFrameType))
        if ghug__gnloy:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                hbmcd__fdx = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                jdyyy__cqbz = tuple(grp.df_type.columns.index(grp.keys[
                    eggm__huhv]) for eggm__huhv in range(len(grp.keys)))
                lxj__oivk = tuple(grp.df_type.data[vci__rvdi] for vci__rvdi in
                    jdyyy__cqbz)
                lxj__oivk = tuple(to_str_arr_if_dict_array(yau__fqe) for
                    yau__fqe in lxj__oivk)
                hbmcd__fdx = MultiIndexType(lxj__oivk, tuple(types.literal(
                    sqpzv__eqjvu) for sqpzv__eqjvu in grp.keys))
            else:
                vci__rvdi = grp.df_type.columns.index(grp.keys[0])
                zmpkb__nxk = grp.df_type.data[vci__rvdi]
                zmpkb__nxk = to_str_arr_if_dict_array(zmpkb__nxk)
                hbmcd__fdx = bodo.hiframes.pd_index_ext.array_type_to_index(
                    zmpkb__nxk, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            nrkdd__xxd = tuple(grp.df_type.data[grp.df_type.columns.index(
                yadcv__iiupu)] for yadcv__iiupu in grp.keys)
            nrkdd__xxd = tuple(to_str_arr_if_dict_array(yau__fqe) for
                yau__fqe in nrkdd__xxd)
            oyu__qciro = tuple(types.literal(kdc__qpe) for kdc__qpe in grp.keys
                ) + get_index_name_types(vpwg__fvanx.index)
            if not grp.as_index:
                nrkdd__xxd = types.Array(types.int64, 1, 'C'),
                oyu__qciro = (types.none,) + get_index_name_types(vpwg__fvanx
                    .index)
            hbmcd__fdx = MultiIndexType(nrkdd__xxd +
                get_index_data_arr_types(vpwg__fvanx.index), oyu__qciro)
        if ghug__gnloy:
            if isinstance(vpwg__fvanx, HeterogeneousSeriesType):
                pzfik__pbu, coc__swwqq = vpwg__fvanx.const_info
                if isinstance(vpwg__fvanx.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    dbv__iko = vpwg__fvanx.data.tuple_typ.types
                elif isinstance(vpwg__fvanx.data, types.Tuple):
                    dbv__iko = vpwg__fvanx.data.types
                kcfu__nsktn = tuple(to_nullable_type(dtype_to_array_type(
                    yau__fqe)) for yau__fqe in dbv__iko)
                ygr__xavh = DataFrameType(out_data + kcfu__nsktn,
                    hbmcd__fdx, out_columns + coc__swwqq)
            elif isinstance(vpwg__fvanx, SeriesType):
                fgxrl__ogn, coc__swwqq = vpwg__fvanx.const_info
                kcfu__nsktn = tuple(to_nullable_type(dtype_to_array_type(
                    vpwg__fvanx.dtype)) for pzfik__pbu in range(fgxrl__ogn))
                ygr__xavh = DataFrameType(out_data + kcfu__nsktn,
                    hbmcd__fdx, out_columns + coc__swwqq)
            else:
                ctyol__afbk = get_udf_out_arr_type(vpwg__fvanx)
                if not grp.as_index:
                    ygr__xavh = DataFrameType(out_data + (ctyol__afbk,),
                        hbmcd__fdx, out_columns + ('',))
                else:
                    ygr__xavh = SeriesType(ctyol__afbk.dtype, ctyol__afbk,
                        hbmcd__fdx, None)
        elif isinstance(vpwg__fvanx, SeriesType):
            ygr__xavh = SeriesType(vpwg__fvanx.dtype, vpwg__fvanx.data,
                hbmcd__fdx, vpwg__fvanx.name_typ)
        else:
            ygr__xavh = DataFrameType(vpwg__fvanx.data, hbmcd__fdx,
                vpwg__fvanx.columns)
        gzs__nmmk = gen_apply_pysig(len(f_args), kws.keys())
        vnd__bcxbc = (func, *f_args) + tuple(kws.values())
        return signature(ygr__xavh, *vnd__bcxbc).replace(pysig=gzs__nmmk)

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
    azuj__wik = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            yyctu__fyacl = grp.selection[0]
            ctyol__afbk = azuj__wik.data[azuj__wik.columns.index(yyctu__fyacl)]
            ctyol__afbk = to_str_arr_if_dict_array(ctyol__afbk)
            kzf__thz = SeriesType(ctyol__afbk.dtype, ctyol__afbk, azuj__wik
                .index, types.literal(yyctu__fyacl))
        else:
            vtpu__jisal = tuple(azuj__wik.data[azuj__wik.columns.index(
                yadcv__iiupu)] for yadcv__iiupu in grp.selection)
            vtpu__jisal = tuple(to_str_arr_if_dict_array(yau__fqe) for
                yau__fqe in vtpu__jisal)
            kzf__thz = DataFrameType(vtpu__jisal, azuj__wik.index, tuple(
                grp.selection))
    else:
        kzf__thz = azuj__wik
    fsp__zse = kzf__thz,
    fsp__zse += tuple(f_args)
    try:
        vpwg__fvanx = get_const_func_output_type(func, fsp__zse, kws,
            typing_context, target_context)
    except Exception as nyu__maxaj:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', nyu__maxaj),
            getattr(nyu__maxaj, 'loc', None))
    return vpwg__fvanx


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    fsp__zse = (grp,) + f_args
    try:
        vpwg__fvanx = get_const_func_output_type(func, fsp__zse, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as nyu__maxaj:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', nyu__maxaj
            ), getattr(nyu__maxaj, 'loc', None))
    gzs__nmmk = gen_apply_pysig(len(f_args), kws.keys())
    vnd__bcxbc = (func, *f_args) + tuple(kws.values())
    return signature(vpwg__fvanx, *vnd__bcxbc).replace(pysig=gzs__nmmk)


def gen_apply_pysig(n_args, kws):
    pprce__zad = ', '.join(f'arg{eggm__huhv}' for eggm__huhv in range(n_args))
    pprce__zad = pprce__zad + ', ' if pprce__zad else ''
    ltxb__idj = ', '.join(f"{zqkr__evm} = ''" for zqkr__evm in kws)
    xwzp__cxt = f'def apply_stub(func, {pprce__zad}{ltxb__idj}):\n'
    xwzp__cxt += '    pass\n'
    peksr__lzj = {}
    exec(xwzp__cxt, {}, peksr__lzj)
    bavfa__zwib = peksr__lzj['apply_stub']
    return numba.core.utils.pysignature(bavfa__zwib)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        kmu__dklfx = types.Array(types.int64, 1, 'C')
        giq__gygrg = _pivot_values.meta
        pva__foxab = len(giq__gygrg)
        qgqnd__klwcj = bodo.hiframes.pd_index_ext.array_type_to_index(
            to_str_arr_if_dict_array(index.data), types.StringLiteral('index'))
        gmtc__rsdja = DataFrameType((kmu__dklfx,) * pva__foxab,
            qgqnd__klwcj, tuple(giq__gygrg))
        return signature(gmtc__rsdja, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    xwzp__cxt = 'def impl(keys, dropna, _is_parallel):\n'
    xwzp__cxt += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    xwzp__cxt += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{eggm__huhv}])' for eggm__huhv in range(len(
        keys.types))))
    xwzp__cxt += '    table = arr_info_list_to_table(info_list)\n'
    xwzp__cxt += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    xwzp__cxt += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    xwzp__cxt += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    xwzp__cxt += '    delete_table_decref_arrays(table)\n'
    xwzp__cxt += '    ev.finalize()\n'
    xwzp__cxt += '    return sort_idx, group_labels, ngroups\n'
    peksr__lzj = {}
    exec(xwzp__cxt, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, peksr__lzj)
    sxl__itkz = peksr__lzj['impl']
    return sxl__itkz


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    nfi__guqo = len(labels)
    mleo__nxfjk = np.zeros(ngroups, dtype=np.int64)
    xkqvb__yarw = np.zeros(ngroups, dtype=np.int64)
    ieaf__lyc = 0
    xiadb__gzdhn = 0
    for eggm__huhv in range(nfi__guqo):
        kbzzw__xsxic = labels[eggm__huhv]
        if kbzzw__xsxic < 0:
            ieaf__lyc += 1
        else:
            xiadb__gzdhn += 1
            if eggm__huhv == nfi__guqo - 1 or kbzzw__xsxic != labels[
                eggm__huhv + 1]:
                mleo__nxfjk[kbzzw__xsxic] = ieaf__lyc
                xkqvb__yarw[kbzzw__xsxic] = ieaf__lyc + xiadb__gzdhn
                ieaf__lyc += xiadb__gzdhn
                xiadb__gzdhn = 0
    return mleo__nxfjk, xkqvb__yarw


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    sxl__itkz, pzfik__pbu = gen_shuffle_dataframe(df, keys, _is_parallel)
    return sxl__itkz


def gen_shuffle_dataframe(df, keys, _is_parallel):
    fgxrl__ogn = len(df.columns)
    ocn__nbx = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    xwzp__cxt = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        xwzp__cxt += '  return df, keys, get_null_shuffle_info()\n'
        peksr__lzj = {}
        exec(xwzp__cxt, {'get_null_shuffle_info': get_null_shuffle_info},
            peksr__lzj)
        sxl__itkz = peksr__lzj['impl']
        return sxl__itkz
    for eggm__huhv in range(fgxrl__ogn):
        xwzp__cxt += f"""  in_arr{eggm__huhv} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {eggm__huhv})
"""
    xwzp__cxt += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    xwzp__cxt += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{eggm__huhv}])' for eggm__huhv in range(
        ocn__nbx)), ', '.join(f'array_to_info(in_arr{eggm__huhv})' for
        eggm__huhv in range(fgxrl__ogn)), 'array_to_info(in_index_arr)')
    xwzp__cxt += '  table = arr_info_list_to_table(info_list)\n'
    xwzp__cxt += (
        f'  out_table = shuffle_table(table, {ocn__nbx}, _is_parallel, 1)\n')
    for eggm__huhv in range(ocn__nbx):
        xwzp__cxt += f"""  out_key{eggm__huhv} = info_to_array(info_from_table(out_table, {eggm__huhv}), keys{eggm__huhv}_typ)
"""
    for eggm__huhv in range(fgxrl__ogn):
        xwzp__cxt += f"""  out_arr{eggm__huhv} = info_to_array(info_from_table(out_table, {eggm__huhv + ocn__nbx}), in_arr{eggm__huhv}_typ)
"""
    xwzp__cxt += f"""  out_arr_index = info_to_array(info_from_table(out_table, {ocn__nbx + fgxrl__ogn}), ind_arr_typ)
"""
    xwzp__cxt += '  shuffle_info = get_shuffle_info(out_table)\n'
    xwzp__cxt += '  delete_table(out_table)\n'
    xwzp__cxt += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{eggm__huhv}' for eggm__huhv in range(
        fgxrl__ogn))
    xwzp__cxt += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    xwzp__cxt += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    xwzp__cxt += '  return out_df, ({},), shuffle_info\n'.format(', '.join(
        f'out_key{eggm__huhv}' for eggm__huhv in range(ocn__nbx)))
    wbpsb__tdeo = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    wbpsb__tdeo.update({f'keys{eggm__huhv}_typ': keys.types[eggm__huhv] for
        eggm__huhv in range(ocn__nbx)})
    wbpsb__tdeo.update({f'in_arr{eggm__huhv}_typ': df.data[eggm__huhv] for
        eggm__huhv in range(fgxrl__ogn)})
    peksr__lzj = {}
    exec(xwzp__cxt, wbpsb__tdeo, peksr__lzj)
    sxl__itkz = peksr__lzj['impl']
    return sxl__itkz, wbpsb__tdeo


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ejv__ekxc = len(data.array_types)
        xwzp__cxt = 'def impl(data, shuffle_info):\n'
        xwzp__cxt += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{eggm__huhv}])' for eggm__huhv in
            range(ejv__ekxc)))
        xwzp__cxt += '  table = arr_info_list_to_table(info_list)\n'
        xwzp__cxt += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for eggm__huhv in range(ejv__ekxc):
            xwzp__cxt += f"""  out_arr{eggm__huhv} = info_to_array(info_from_table(out_table, {eggm__huhv}), data._data[{eggm__huhv}])
"""
        xwzp__cxt += '  delete_table(out_table)\n'
        xwzp__cxt += '  delete_table(table)\n'
        xwzp__cxt += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{eggm__huhv}' for eggm__huhv in range
            (ejv__ekxc))))
        peksr__lzj = {}
        exec(xwzp__cxt, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, peksr__lzj)
        sxl__itkz = peksr__lzj['impl']
        return sxl__itkz
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            yyu__xcdh = bodo.utils.conversion.index_to_array(data)
            nfju__uacsc = reverse_shuffle(yyu__xcdh, shuffle_info)
            return bodo.utils.conversion.index_from_array(nfju__uacsc)
        return impl_index

    def impl_arr(data, shuffle_info):
        ndhcp__gti = [array_to_info(data)]
        tss__thso = arr_info_list_to_table(ndhcp__gti)
        blwax__owkvr = reverse_shuffle_table(tss__thso, shuffle_info)
        nfju__uacsc = info_to_array(info_from_table(blwax__owkvr, 0), data)
        delete_table(blwax__owkvr)
        delete_table(tss__thso)
        return nfju__uacsc
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    ocn__nemm = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    yffm__hcw = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', ocn__nemm, yffm__hcw,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    xjm__vwthg = get_overload_const_bool(ascending)
    xlyl__akh = grp.selection[0]
    xwzp__cxt = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    jlk__xpi = (
        f"lambda S: S.value_counts(ascending={xjm__vwthg}, _index_name='{xlyl__akh}')"
        )
    xwzp__cxt += f'    return grp.apply({jlk__xpi})\n'
    peksr__lzj = {}
    exec(xwzp__cxt, {'bodo': bodo}, peksr__lzj)
    sxl__itkz = peksr__lzj['impl']
    return sxl__itkz


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
    for zvfa__gpq in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, zvfa__gpq, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{zvfa__gpq}'))
    for zvfa__gpq in groupby_unsupported:
        overload_method(DataFrameGroupByType, zvfa__gpq, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{zvfa__gpq}'))
    for zvfa__gpq in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, zvfa__gpq, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{zvfa__gpq}'))
    for zvfa__gpq in series_only_unsupported:
        overload_method(DataFrameGroupByType, zvfa__gpq, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{zvfa__gpq}'))
    for zvfa__gpq in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, zvfa__gpq, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{zvfa__gpq}'))


_install_groupby_unsupported()
