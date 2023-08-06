"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
from functools import cached_property
from urllib.parse import quote
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, decode_if_dict_table, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import bcast_scalar
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import fix_arr_dtype, index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type, get_const_tup_vals
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_str_arr_type, is_tuple_like_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format}, {self.has_runtime_cols})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            udfp__dkrsd = f'{len(self.data)} columns of types {set(self.data)}'
            rhnbj__qhg = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({udfp__dkrsd}, {self.index}, {rhnbj__qhg}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @cached_property
    def column_index(self):
        return {ljeet__wmoxg: i for i, ljeet__wmoxg in enumerate(self.columns)}

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def runtime_data_types(self):
        return self.data[:-1] if self.has_runtime_cols else self.data

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            knqt__malq = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(liz__ipdq.unify(typingctx, endge__bujlw) if 
                liz__ipdq != endge__bujlw else liz__ipdq for liz__ipdq,
                endge__bujlw in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if knqt__malq is not None and None not in data:
                return DataFrameType(data, knqt__malq, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(liz__ipdq.is_precise() for liz__ipdq in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        bsmj__bfzxf = self.columns.index(col_name)
        wcacp__asnz = tuple(list(self.data[:bsmj__bfzxf]) + [new_type] +
            list(self.data[bsmj__bfzxf + 1:]))
        return DataFrameType(wcacp__asnz, self.index, self.columns, self.
            dist, self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        wos__xqm = [('data', data_typ), ('index', fe_type.df_type.index), (
            'parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            wos__xqm.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, wos__xqm)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        wos__xqm = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, wos__xqm)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        bbtq__xmoma = 'n',
        urpa__hnsiv = {'n': 5}
        zdq__mnex, wki__ecszj = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, bbtq__xmoma, urpa__hnsiv)
        kcj__ajsu = wki__ecszj[0]
        if not is_overload_int(kcj__ajsu):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        jkqfd__ywj = df.copy()
        return jkqfd__ywj(*wki__ecszj).replace(pysig=zdq__mnex)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        sxu__dlq = (df,) + args
        bbtq__xmoma = 'df', 'method', 'min_periods'
        urpa__hnsiv = {'method': 'pearson', 'min_periods': 1}
        aki__yjak = 'method',
        zdq__mnex, wki__ecszj = bodo.utils.typing.fold_typing_args(func_name,
            sxu__dlq, kws, bbtq__xmoma, urpa__hnsiv, aki__yjak)
        hgdp__jme = wki__ecszj[2]
        if not is_overload_int(hgdp__jme):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        mjwyz__fgl = []
        ddv__rbj = []
        for ljeet__wmoxg, kcynk__wpb in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(kcynk__wpb.dtype):
                mjwyz__fgl.append(ljeet__wmoxg)
                ddv__rbj.append(types.Array(types.float64, 1, 'A'))
        if len(mjwyz__fgl) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        ddv__rbj = tuple(ddv__rbj)
        mjwyz__fgl = tuple(mjwyz__fgl)
        index_typ = bodo.utils.typing.type_col_to_index(mjwyz__fgl)
        jkqfd__ywj = DataFrameType(ddv__rbj, index_typ, mjwyz__fgl)
        return jkqfd__ywj(*wki__ecszj).replace(pysig=zdq__mnex)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        lqyzp__lakdg = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        iwokc__fzfy = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        busl__pkp = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        lsgq__khrod = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        imzx__tpz = dict(raw=iwokc__fzfy, result_type=busl__pkp)
        fofjr__ljkz = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', imzx__tpz, fofjr__ljkz,
            package_name='pandas', module_name='DataFrame')
        wzzs__nefkr = True
        if types.unliteral(lqyzp__lakdg) == types.unicode_type:
            if not is_overload_constant_str(lqyzp__lakdg):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            wzzs__nefkr = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        jwan__otdv = get_overload_const_int(axis)
        if wzzs__nefkr and jwan__otdv != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif jwan__otdv not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        yhrd__tqii = []
        for arr_typ in df.data:
            jks__mtl = SeriesType(arr_typ.dtype, arr_typ, df.index, string_type
                )
            gweb__dkmg = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(jks__mtl), types.int64), {}
                ).return_type
            yhrd__tqii.append(gweb__dkmg)
        krjbi__wdrn = types.none
        zsbxk__irk = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(ljeet__wmoxg) for ljeet__wmoxg in df.
            columns)), None)
        hdt__ttyw = types.BaseTuple.from_types(yhrd__tqii)
        eyszx__iaots = types.Tuple([types.bool_] * len(hdt__ttyw))
        fzui__jxq = bodo.NullableTupleType(hdt__ttyw, eyszx__iaots)
        munf__zqwq = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if munf__zqwq == types.NPDatetime('ns'):
            munf__zqwq = bodo.pd_timestamp_type
        if munf__zqwq == types.NPTimedelta('ns'):
            munf__zqwq = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(hdt__ttyw):
            rjm__chjmh = HeterogeneousSeriesType(fzui__jxq, zsbxk__irk,
                munf__zqwq)
        else:
            rjm__chjmh = SeriesType(hdt__ttyw.dtype, fzui__jxq, zsbxk__irk,
                munf__zqwq)
        nbw__mzed = rjm__chjmh,
        if lsgq__khrod is not None:
            nbw__mzed += tuple(lsgq__khrod.types)
        try:
            if not wzzs__nefkr:
                rklnl__uasw = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(lqyzp__lakdg), self.context,
                    'DataFrame.apply', axis if jwan__otdv == 1 else None)
            else:
                rklnl__uasw = get_const_func_output_type(lqyzp__lakdg,
                    nbw__mzed, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as ecgl__tzguo:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                ecgl__tzguo))
        if wzzs__nefkr:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(rklnl__uasw, (SeriesType, HeterogeneousSeriesType)
                ) and rklnl__uasw.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(rklnl__uasw, HeterogeneousSeriesType):
                brulq__ywmaa, dir__aul = rklnl__uasw.const_info
                if isinstance(rklnl__uasw.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    mkb__dicaz = rklnl__uasw.data.tuple_typ.types
                elif isinstance(rklnl__uasw.data, types.Tuple):
                    mkb__dicaz = rklnl__uasw.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                rqbgg__jqta = tuple(to_nullable_type(dtype_to_array_type(
                    nrg__okfuq)) for nrg__okfuq in mkb__dicaz)
                farvb__ksg = DataFrameType(rqbgg__jqta, df.index, dir__aul)
            elif isinstance(rklnl__uasw, SeriesType):
                vcrr__gajln, dir__aul = rklnl__uasw.const_info
                rqbgg__jqta = tuple(to_nullable_type(dtype_to_array_type(
                    rklnl__uasw.dtype)) for brulq__ywmaa in range(vcrr__gajln))
                farvb__ksg = DataFrameType(rqbgg__jqta, df.index, dir__aul)
            else:
                ulxrn__zwnsp = get_udf_out_arr_type(rklnl__uasw)
                farvb__ksg = SeriesType(ulxrn__zwnsp.dtype, ulxrn__zwnsp,
                    df.index, None)
        else:
            farvb__ksg = rklnl__uasw
        dhifw__ltd = ', '.join("{} = ''".format(liz__ipdq) for liz__ipdq in
            kws.keys())
        npy__hxfq = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {dhifw__ltd}):
"""
        npy__hxfq += '    pass\n'
        bfr__lpy = {}
        exec(npy__hxfq, {}, bfr__lpy)
        viqyp__qszm = bfr__lpy['apply_stub']
        zdq__mnex = numba.core.utils.pysignature(viqyp__qszm)
        xwafy__gthup = (lqyzp__lakdg, axis, iwokc__fzfy, busl__pkp, lsgq__khrod
            ) + tuple(kws.values())
        return signature(farvb__ksg, *xwafy__gthup).replace(pysig=zdq__mnex)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        bbtq__xmoma = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        urpa__hnsiv = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        aki__yjak = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        zdq__mnex, wki__ecszj = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, bbtq__xmoma, urpa__hnsiv, aki__yjak)
        fcp__xtjtm = wki__ecszj[2]
        if not is_overload_constant_str(fcp__xtjtm):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        qheb__geje = wki__ecszj[0]
        if not is_overload_none(qheb__geje) and not (is_overload_int(
            qheb__geje) or is_overload_constant_str(qheb__geje)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(qheb__geje):
            dmuxi__edj = get_overload_const_str(qheb__geje)
            if dmuxi__edj not in df.columns:
                raise BodoError(f'{func_name}: {dmuxi__edj} column not found.')
        elif is_overload_int(qheb__geje):
            xeqmb__qne = get_overload_const_int(qheb__geje)
            if xeqmb__qne > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {xeqmb__qne} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            qheb__geje = df.columns[qheb__geje]
        dgp__vbni = wki__ecszj[1]
        if not is_overload_none(dgp__vbni) and not (is_overload_int(
            dgp__vbni) or is_overload_constant_str(dgp__vbni)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(dgp__vbni):
            lkmf__lvl = get_overload_const_str(dgp__vbni)
            if lkmf__lvl not in df.columns:
                raise BodoError(f'{func_name}: {lkmf__lvl} column not found.')
        elif is_overload_int(dgp__vbni):
            yyn__avlpa = get_overload_const_int(dgp__vbni)
            if yyn__avlpa > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {yyn__avlpa} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            dgp__vbni = df.columns[dgp__vbni]
        mgm__awuz = wki__ecszj[3]
        if not is_overload_none(mgm__awuz) and not is_tuple_like_type(mgm__awuz
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        kzc__eco = wki__ecszj[10]
        if not is_overload_none(kzc__eco) and not is_overload_constant_str(
            kzc__eco):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        dxjcy__moxrp = wki__ecszj[12]
        if not is_overload_bool(dxjcy__moxrp):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        xpp__ofvu = wki__ecszj[17]
        if not is_overload_none(xpp__ofvu) and not is_tuple_like_type(xpp__ofvu
            ):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        onk__kihgl = wki__ecszj[18]
        if not is_overload_none(onk__kihgl) and not is_tuple_like_type(
            onk__kihgl):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        ipd__njo = wki__ecszj[22]
        if not is_overload_none(ipd__njo) and not is_overload_int(ipd__njo):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        aqtu__xocya = wki__ecszj[29]
        if not is_overload_none(aqtu__xocya) and not is_overload_constant_str(
            aqtu__xocya):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        quv__thha = wki__ecszj[30]
        if not is_overload_none(quv__thha) and not is_overload_constant_str(
            quv__thha):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        sid__mdlaw = types.List(types.mpl_line_2d_type)
        fcp__xtjtm = get_overload_const_str(fcp__xtjtm)
        if fcp__xtjtm == 'scatter':
            if is_overload_none(qheb__geje) and is_overload_none(dgp__vbni):
                raise BodoError(
                    f'{func_name}: {fcp__xtjtm} requires an x and y column.')
            elif is_overload_none(qheb__geje):
                raise BodoError(
                    f'{func_name}: {fcp__xtjtm} x column is missing.')
            elif is_overload_none(dgp__vbni):
                raise BodoError(
                    f'{func_name}: {fcp__xtjtm} y column is missing.')
            sid__mdlaw = types.mpl_path_collection_type
        elif fcp__xtjtm != 'line':
            raise BodoError(f'{func_name}: {fcp__xtjtm} plot is not supported.'
                )
        return signature(sid__mdlaw, *wki__ecszj).replace(pysig=zdq__mnex)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            fnr__nik = df.columns.index(attr)
            arr_typ = df.data[fnr__nik]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            uxmus__pnoyu = []
            wcacp__asnz = []
            dbi__hjrc = False
            for i, jywkw__jio in enumerate(df.columns):
                if jywkw__jio[0] != attr:
                    continue
                dbi__hjrc = True
                uxmus__pnoyu.append(jywkw__jio[1] if len(jywkw__jio) == 2 else
                    jywkw__jio[1:])
                wcacp__asnz.append(df.data[i])
            if dbi__hjrc:
                return DataFrameType(tuple(wcacp__asnz), df.index, tuple(
                    uxmus__pnoyu))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        huqru__mml = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(huqru__mml)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        kpmwn__opnsm = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], kpmwn__opnsm)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    dpnc__xhel = builder.module
    gpuh__jwnf = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    xhx__rhus = cgutils.get_or_insert_function(dpnc__xhel, gpuh__jwnf, name
        ='.dtor.df.{}'.format(df_type))
    if not xhx__rhus.is_declaration:
        return xhx__rhus
    xhx__rhus.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(xhx__rhus.append_basic_block())
    eev__olka = xhx__rhus.args[0]
    viv__qzn = context.get_value_type(payload_type).as_pointer()
    ytibu__ykqoj = builder.bitcast(eev__olka, viv__qzn)
    payload = context.make_helper(builder, payload_type, ref=ytibu__ykqoj)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        cvlq__ukz = context.get_python_api(builder)
        rhg__yzk = cvlq__ukz.gil_ensure()
        cvlq__ukz.decref(payload.parent)
        cvlq__ukz.gil_release(rhg__yzk)
    builder.ret_void()
    return xhx__rhus


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    qjtzg__dfkb = cgutils.create_struct_proxy(payload_type)(context, builder)
    qjtzg__dfkb.data = data_tup
    qjtzg__dfkb.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        qjtzg__dfkb.columns = colnames
    mxhbe__rwbh = context.get_value_type(payload_type)
    qhfz__dqt = context.get_abi_sizeof(mxhbe__rwbh)
    dux__grd = define_df_dtor(context, builder, df_type, payload_type)
    yii__adg = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, qhfz__dqt), dux__grd)
    dhm__tuw = context.nrt.meminfo_data(builder, yii__adg)
    dvy__wke = builder.bitcast(dhm__tuw, mxhbe__rwbh.as_pointer())
    pjq__cwt = cgutils.create_struct_proxy(df_type)(context, builder)
    pjq__cwt.meminfo = yii__adg
    if parent is None:
        pjq__cwt.parent = cgutils.get_null_value(pjq__cwt.parent.type)
    else:
        pjq__cwt.parent = parent
        qjtzg__dfkb.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            cvlq__ukz = context.get_python_api(builder)
            rhg__yzk = cvlq__ukz.gil_ensure()
            cvlq__ukz.incref(parent)
            cvlq__ukz.gil_release(rhg__yzk)
    builder.store(qjtzg__dfkb._getvalue(), dvy__wke)
    return pjq__cwt._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        hwbk__qjeqe = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype
            .arr_types)
    else:
        hwbk__qjeqe = [nrg__okfuq for nrg__okfuq in data_typ.dtype.arr_types]
    obg__wmr = DataFrameType(tuple(hwbk__qjeqe + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        dwlib__xto = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return dwlib__xto
    sig = signature(obg__wmr, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    vcrr__gajln = len(data_tup_typ.types)
    if vcrr__gajln == 0:
        column_names = ()
    jbmid__tpj = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    if isinstance(jbmid__tpj, ColNamesMetaType):
        assert isinstance(jbmid__tpj.meta, tuple)
        column_names = jbmid__tpj.meta
    elif isinstance(jbmid__tpj, DataFrameType):
        column_names = jbmid__tpj.columns
    else:
        column_names = get_const_tup_vals(jbmid__tpj)
    if vcrr__gajln == 1 and isinstance(data_tup_typ.types[0], TableType):
        vcrr__gajln = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == vcrr__gajln, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    tfxy__cew = data_tup_typ.types
    if vcrr__gajln != 0 and isinstance(data_tup_typ.types[0], TableType):
        tfxy__cew = data_tup_typ.types[0].arr_types
        is_table_format = True
    obg__wmr = DataFrameType(tfxy__cew, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            mts__zxn = cgutils.create_struct_proxy(obg__wmr.table_type)(context
                , builder, builder.extract_value(data_tup, 0))
            parent = mts__zxn.parent
        dwlib__xto = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return dwlib__xto
    sig = signature(obg__wmr, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        pjq__cwt = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, pjq__cwt.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        qjtzg__dfkb = get_dataframe_payload(context, builder, df_typ, args[0])
        xaw__mpk = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[xaw__mpk]
        if df_typ.is_table_format:
            mts__zxn = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(qjtzg__dfkb.data, 0))
            oymr__eky = df_typ.table_type.type_to_blk[arr_typ]
            gtq__arulf = getattr(mts__zxn, f'block_{oymr__eky}')
            umd__mkomw = ListInstance(context, builder, types.List(arr_typ),
                gtq__arulf)
            mneo__zap = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[xaw__mpk])
            kpmwn__opnsm = umd__mkomw.getitem(mneo__zap)
        else:
            kpmwn__opnsm = builder.extract_value(qjtzg__dfkb.data, xaw__mpk)
        rer__ruu = cgutils.alloca_once_value(builder, kpmwn__opnsm)
        ddf__mlyet = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, rer__ruu, ddf__mlyet)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    yii__adg = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, yii__adg)
    viv__qzn = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, viv__qzn)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    obg__wmr = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        obg__wmr = types.Tuple([TableType(df_typ.data)])
    sig = signature(obg__wmr, df_typ)

    def codegen(context, builder, signature, args):
        qjtzg__dfkb = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            qjtzg__dfkb.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        qjtzg__dfkb = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index,
            qjtzg__dfkb.index)
    obg__wmr = df_typ.index
    sig = signature(obg__wmr, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        jkqfd__ywj = df.data[i]
        return jkqfd__ywj(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        qjtzg__dfkb = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(qjtzg__dfkb.data, 0))
    return df_typ.table_type(df_typ), codegen


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        qjtzg__dfkb = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, qjtzg__dfkb.columns)
    return df_typ.runtime_colname_typ(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    hdt__ttyw = self.typemap[data_tup.name]
    if any(is_tuple_like_type(nrg__okfuq) for nrg__okfuq in hdt__ttyw.types):
        return None
    if equiv_set.has_shape(data_tup):
        tqbyr__dbaci = equiv_set.get_shape(data_tup)
        if len(tqbyr__dbaci) > 1:
            equiv_set.insert_equiv(*tqbyr__dbaci)
        if len(tqbyr__dbaci) > 0:
            zsbxk__irk = self.typemap[index.name]
            if not isinstance(zsbxk__irk, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(tqbyr__dbaci[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(tqbyr__dbaci[0], len(
                tqbyr__dbaci)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ttf__nngi = args[0]
    data_types = self.typemap[ttf__nngi.name].data
    if any(is_tuple_like_type(nrg__okfuq) for nrg__okfuq in data_types):
        return None
    if equiv_set.has_shape(ttf__nngi):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ttf__nngi)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    ttf__nngi = args[0]
    zsbxk__irk = self.typemap[ttf__nngi.name].index
    if isinstance(zsbxk__irk, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(ttf__nngi):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ttf__nngi)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ttf__nngi = args[0]
    if equiv_set.has_shape(ttf__nngi):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ttf__nngi), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ttf__nngi = args[0]
    if equiv_set.has_shape(ttf__nngi):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ttf__nngi)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    xaw__mpk = get_overload_const_int(c_ind_typ)
    if df_typ.data[xaw__mpk] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        tytkc__dzezx, brulq__ywmaa, wjspl__oqejy = args
        qjtzg__dfkb = get_dataframe_payload(context, builder, df_typ,
            tytkc__dzezx)
        if df_typ.is_table_format:
            mts__zxn = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(qjtzg__dfkb.data, 0))
            oymr__eky = df_typ.table_type.type_to_blk[arr_typ]
            gtq__arulf = getattr(mts__zxn, f'block_{oymr__eky}')
            umd__mkomw = ListInstance(context, builder, types.List(arr_typ),
                gtq__arulf)
            mneo__zap = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[xaw__mpk])
            umd__mkomw.setitem(mneo__zap, wjspl__oqejy, True)
        else:
            kpmwn__opnsm = builder.extract_value(qjtzg__dfkb.data, xaw__mpk)
            context.nrt.decref(builder, df_typ.data[xaw__mpk], kpmwn__opnsm)
            qjtzg__dfkb.data = builder.insert_value(qjtzg__dfkb.data,
                wjspl__oqejy, xaw__mpk)
            context.nrt.incref(builder, arr_typ, wjspl__oqejy)
        pjq__cwt = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=tytkc__dzezx)
        payload_type = DataFramePayloadType(df_typ)
        ytibu__ykqoj = context.nrt.meminfo_data(builder, pjq__cwt.meminfo)
        viv__qzn = context.get_value_type(payload_type).as_pointer()
        ytibu__ykqoj = builder.bitcast(ytibu__ykqoj, viv__qzn)
        builder.store(qjtzg__dfkb._getvalue(), ytibu__ykqoj)
        return impl_ret_borrowed(context, builder, df_typ, tytkc__dzezx)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        fuq__ukxv = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        pfzw__fgjn = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=fuq__ukxv)
        zxml__qgzj = get_dataframe_payload(context, builder, df_typ, fuq__ukxv)
        pjq__cwt = construct_dataframe(context, builder, signature.
            return_type, zxml__qgzj.data, index_val, pfzw__fgjn.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), zxml__qgzj.data)
        return pjq__cwt
    obg__wmr = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(obg__wmr, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    vcrr__gajln = len(df_type.columns)
    krsr__mjbo = vcrr__gajln
    uid__fqew = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    uuiyz__yeikh = col_name not in df_type.columns
    xaw__mpk = vcrr__gajln
    if uuiyz__yeikh:
        uid__fqew += arr_type,
        column_names += col_name,
        krsr__mjbo += 1
    else:
        xaw__mpk = df_type.columns.index(col_name)
        uid__fqew = tuple(arr_type if i == xaw__mpk else uid__fqew[i] for i in
            range(vcrr__gajln))

    def codegen(context, builder, signature, args):
        tytkc__dzezx, brulq__ywmaa, wjspl__oqejy = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, tytkc__dzezx)
        yqa__vix = cgutils.create_struct_proxy(df_type)(context, builder,
            value=tytkc__dzezx)
        if df_type.is_table_format:
            cqx__qmh = df_type.table_type
            ojequ__ffemw = builder.extract_value(in_dataframe_payload.data, 0)
            mqk__qwn = TableType(uid__fqew)
            nmx__grqjm = set_table_data_codegen(context, builder, cqx__qmh,
                ojequ__ffemw, mqk__qwn, arr_type, wjspl__oqejy, xaw__mpk,
                uuiyz__yeikh)
            data_tup = context.make_tuple(builder, types.Tuple([mqk__qwn]),
                [nmx__grqjm])
        else:
            tfxy__cew = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != xaw__mpk else wjspl__oqejy) for i in range(
                vcrr__gajln)]
            if uuiyz__yeikh:
                tfxy__cew.append(wjspl__oqejy)
            for ttf__nngi, rwye__vrfzf in zip(tfxy__cew, uid__fqew):
                context.nrt.incref(builder, rwye__vrfzf, ttf__nngi)
            data_tup = context.make_tuple(builder, types.Tuple(uid__fqew),
                tfxy__cew)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        ggs__nhfb = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, yqa__vix.parent, None)
        if not uuiyz__yeikh and arr_type == df_type.data[xaw__mpk]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            ytibu__ykqoj = context.nrt.meminfo_data(builder, yqa__vix.meminfo)
            viv__qzn = context.get_value_type(payload_type).as_pointer()
            ytibu__ykqoj = builder.bitcast(ytibu__ykqoj, viv__qzn)
            xkp__uoct = get_dataframe_payload(context, builder, df_type,
                ggs__nhfb)
            builder.store(xkp__uoct._getvalue(), ytibu__ykqoj)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, mqk__qwn, builder.extract_value
                    (data_tup, 0))
            else:
                for ttf__nngi, rwye__vrfzf in zip(tfxy__cew, uid__fqew):
                    context.nrt.incref(builder, rwye__vrfzf, ttf__nngi)
        has_parent = cgutils.is_not_null(builder, yqa__vix.parent)
        with builder.if_then(has_parent):
            cvlq__ukz = context.get_python_api(builder)
            rhg__yzk = cvlq__ukz.gil_ensure()
            gocv__rfrdd = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, wjspl__oqejy)
            ljeet__wmoxg = numba.core.pythonapi._BoxContext(context,
                builder, cvlq__ukz, gocv__rfrdd)
            lzgn__tdz = ljeet__wmoxg.pyapi.from_native_value(arr_type,
                wjspl__oqejy, ljeet__wmoxg.env_manager)
            if isinstance(col_name, str):
                row__ftj = context.insert_const_string(builder.module, col_name
                    )
                artn__exiwu = cvlq__ukz.string_from_string(row__ftj)
            else:
                assert isinstance(col_name, int)
                artn__exiwu = cvlq__ukz.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            cvlq__ukz.object_setitem(yqa__vix.parent, artn__exiwu, lzgn__tdz)
            cvlq__ukz.decref(lzgn__tdz)
            cvlq__ukz.decref(artn__exiwu)
            cvlq__ukz.gil_release(rhg__yzk)
        return ggs__nhfb
    obg__wmr = DataFrameType(uid__fqew, index_typ, column_names, df_type.
        dist, df_type.is_table_format)
    sig = signature(obg__wmr, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    vcrr__gajln = len(pyval.columns)
    tfxy__cew = []
    for i in range(vcrr__gajln):
        xdiyb__ptvs = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            lzgn__tdz = xdiyb__ptvs.array
        else:
            lzgn__tdz = xdiyb__ptvs.values
        tfxy__cew.append(lzgn__tdz)
    tfxy__cew = tuple(tfxy__cew)
    if df_type.is_table_format:
        mts__zxn = context.get_constant_generic(builder, df_type.table_type,
            Table(tfxy__cew))
        data_tup = lir.Constant.literal_struct([mts__zxn])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], jywkw__jio) for 
            i, jywkw__jio in enumerate(tfxy__cew)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    xsoog__xefbp = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, xsoog__xefbp])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    cpc__gqn = context.get_constant(types.int64, -1)
    thp__irao = context.get_constant_null(types.voidptr)
    yii__adg = lir.Constant.literal_struct([cpc__gqn, thp__irao, thp__irao,
        payload, cpc__gqn])
    yii__adg = cgutils.global_constant(builder, '.const.meminfo', yii__adg
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([yii__adg, xsoog__xefbp])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if len(fromty.data) != len(toty.data) or fromty.data != toty.data and any(
        context.typing_context.unify_pairs(fromty.data[i], toty.data[i]) is
        None for i in range(len(fromty.data))
        ) or fromty.has_runtime_cols != toty.has_runtime_cols:
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        knqt__malq = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        knqt__malq = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, knqt__malq)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        wcacp__asnz = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                wcacp__asnz)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), wcacp__asnz)
    elif not fromty.is_table_format and toty.is_table_format:
        wcacp__asnz = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        wcacp__asnz = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        wcacp__asnz = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        wcacp__asnz = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, wcacp__asnz,
        knqt__malq, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    wit__mrxp = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        iiexe__amali = get_index_data_arr_types(toty.index)[0]
        efes__hdsz = bodo.utils.transform.get_type_alloc_counts(iiexe__amali
            ) - 1
        tkw__tdb = ', '.join('0' for brulq__ywmaa in range(efes__hdsz))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(tkw__tdb, ', ' if efes__hdsz == 1 else ''))
        wit__mrxp['index_arr_type'] = iiexe__amali
    rnqzk__kqwx = []
    for i, arr_typ in enumerate(toty.data):
        efes__hdsz = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        tkw__tdb = ', '.join('0' for brulq__ywmaa in range(efes__hdsz))
        guttz__iit = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, tkw__tdb, ', ' if efes__hdsz == 1 else ''))
        rnqzk__kqwx.append(guttz__iit)
        wit__mrxp[f'arr_type{i}'] = arr_typ
    rnqzk__kqwx = ', '.join(rnqzk__kqwx)
    npy__hxfq = 'def impl():\n'
    bia__gebgz = bodo.hiframes.dataframe_impl._gen_init_df(npy__hxfq, toty.
        columns, rnqzk__kqwx, index, wit__mrxp)
    df = context.compile_internal(builder, bia__gebgz, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    zcm__xemvj = toty.table_type
    mts__zxn = cgutils.create_struct_proxy(zcm__xemvj)(context, builder)
    mts__zxn.parent = in_dataframe_payload.parent
    for nrg__okfuq, oymr__eky in zcm__xemvj.type_to_blk.items():
        qbvy__hte = context.get_constant(types.int64, len(zcm__xemvj.
            block_to_arr_ind[oymr__eky]))
        brulq__ywmaa, cgim__krjcw = ListInstance.allocate_ex(context,
            builder, types.List(nrg__okfuq), qbvy__hte)
        cgim__krjcw.size = qbvy__hte
        setattr(mts__zxn, f'block_{oymr__eky}', cgim__krjcw.value)
    for i, nrg__okfuq in enumerate(fromty.data):
        zgcj__dfyt = toty.data[i]
        if nrg__okfuq != zgcj__dfyt:
            avrv__sofi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*avrv__sofi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        kpmwn__opnsm = builder.extract_value(in_dataframe_payload.data, i)
        if nrg__okfuq != zgcj__dfyt:
            kqaj__sdhe = context.cast(builder, kpmwn__opnsm, nrg__okfuq,
                zgcj__dfyt)
            nsa__kau = False
        else:
            kqaj__sdhe = kpmwn__opnsm
            nsa__kau = True
        oymr__eky = zcm__xemvj.type_to_blk[nrg__okfuq]
        gtq__arulf = getattr(mts__zxn, f'block_{oymr__eky}')
        umd__mkomw = ListInstance(context, builder, types.List(nrg__okfuq),
            gtq__arulf)
        mneo__zap = context.get_constant(types.int64, zcm__xemvj.
            block_offsets[i])
        umd__mkomw.setitem(mneo__zap, kqaj__sdhe, nsa__kau)
    data_tup = context.make_tuple(builder, types.Tuple([zcm__xemvj]), [
        mts__zxn._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    tfxy__cew = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            avrv__sofi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*avrv__sofi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            kpmwn__opnsm = builder.extract_value(in_dataframe_payload.data, i)
            kqaj__sdhe = context.cast(builder, kpmwn__opnsm, fromty.data[i],
                toty.data[i])
            nsa__kau = False
        else:
            kqaj__sdhe = builder.extract_value(in_dataframe_payload.data, i)
            nsa__kau = True
        if nsa__kau:
            context.nrt.incref(builder, toty.data[i], kqaj__sdhe)
        tfxy__cew.append(kqaj__sdhe)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tfxy__cew)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    cqx__qmh = fromty.table_type
    ojequ__ffemw = cgutils.create_struct_proxy(cqx__qmh)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    mqk__qwn = toty.table_type
    nmx__grqjm = cgutils.create_struct_proxy(mqk__qwn)(context, builder)
    nmx__grqjm.parent = in_dataframe_payload.parent
    for nrg__okfuq, oymr__eky in mqk__qwn.type_to_blk.items():
        qbvy__hte = context.get_constant(types.int64, len(mqk__qwn.
            block_to_arr_ind[oymr__eky]))
        brulq__ywmaa, cgim__krjcw = ListInstance.allocate_ex(context,
            builder, types.List(nrg__okfuq), qbvy__hte)
        cgim__krjcw.size = qbvy__hte
        setattr(nmx__grqjm, f'block_{oymr__eky}', cgim__krjcw.value)
    for i in range(len(fromty.data)):
        eju__esblf = fromty.data[i]
        zgcj__dfyt = toty.data[i]
        if eju__esblf != zgcj__dfyt:
            avrv__sofi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*avrv__sofi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        xot__iqs = cqx__qmh.type_to_blk[eju__esblf]
        dlw__wolya = getattr(ojequ__ffemw, f'block_{xot__iqs}')
        tkn__cxzj = ListInstance(context, builder, types.List(eju__esblf),
            dlw__wolya)
        vhlad__fknx = context.get_constant(types.int64, cqx__qmh.
            block_offsets[i])
        kpmwn__opnsm = tkn__cxzj.getitem(vhlad__fknx)
        if eju__esblf != zgcj__dfyt:
            kqaj__sdhe = context.cast(builder, kpmwn__opnsm, eju__esblf,
                zgcj__dfyt)
            nsa__kau = False
        else:
            kqaj__sdhe = kpmwn__opnsm
            nsa__kau = True
        mvxo__tasyp = mqk__qwn.type_to_blk[nrg__okfuq]
        cgim__krjcw = getattr(nmx__grqjm, f'block_{mvxo__tasyp}')
        hrrv__aif = ListInstance(context, builder, types.List(zgcj__dfyt),
            cgim__krjcw)
        dzul__sit = context.get_constant(types.int64, mqk__qwn.block_offsets[i]
            )
        hrrv__aif.setitem(dzul__sit, kqaj__sdhe, nsa__kau)
    data_tup = context.make_tuple(builder, types.Tuple([mqk__qwn]), [
        nmx__grqjm._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    zcm__xemvj = fromty.table_type
    mts__zxn = cgutils.create_struct_proxy(zcm__xemvj)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    tfxy__cew = []
    for i, nrg__okfuq in enumerate(toty.data):
        eju__esblf = fromty.data[i]
        if nrg__okfuq != eju__esblf:
            avrv__sofi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*avrv__sofi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        oymr__eky = zcm__xemvj.type_to_blk[nrg__okfuq]
        gtq__arulf = getattr(mts__zxn, f'block_{oymr__eky}')
        umd__mkomw = ListInstance(context, builder, types.List(nrg__okfuq),
            gtq__arulf)
        mneo__zap = context.get_constant(types.int64, zcm__xemvj.
            block_offsets[i])
        kpmwn__opnsm = umd__mkomw.getitem(mneo__zap)
        if nrg__okfuq != eju__esblf:
            kqaj__sdhe = context.cast(builder, kpmwn__opnsm, eju__esblf,
                nrg__okfuq)
            nsa__kau = False
        else:
            kqaj__sdhe = kpmwn__opnsm
            nsa__kau = True
        if nsa__kau:
            context.nrt.incref(builder, nrg__okfuq, kqaj__sdhe)
        tfxy__cew.append(kqaj__sdhe)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tfxy__cew)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    toux__taw, rnqzk__kqwx, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    gkd__dmj = ColNamesMetaType(tuple(toux__taw))
    npy__hxfq = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    npy__hxfq += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(rnqzk__kqwx, index_arg, gkd__dmj))
    bfr__lpy = {}
    exec(npy__hxfq, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': gkd__dmj}, bfr__lpy)
    ekikb__bwltd = bfr__lpy['_init_df']
    return ekikb__bwltd


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    obg__wmr = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ.
        index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(obg__wmr, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    obg__wmr = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ.
        index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(obg__wmr, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    ivcw__sxlpe = ''
    if not is_overload_none(dtype):
        ivcw__sxlpe = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        vcrr__gajln = (len(data.types) - 1) // 2
        dizm__kan = [nrg__okfuq.literal_value for nrg__okfuq in data.types[
            1:vcrr__gajln + 1]]
        data_val_types = dict(zip(dizm__kan, data.types[vcrr__gajln + 1:]))
        tfxy__cew = ['data[{}]'.format(i) for i in range(vcrr__gajln + 1, 2 *
            vcrr__gajln + 1)]
        data_dict = dict(zip(dizm__kan, tfxy__cew))
        if is_overload_none(index):
            for i, nrg__okfuq in enumerate(data.types[vcrr__gajln + 1:]):
                if isinstance(nrg__okfuq, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(vcrr__gajln + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        bodil__afp = '.copy()' if copy else ''
        qvgtu__oam = get_overload_const_list(columns)
        vcrr__gajln = len(qvgtu__oam)
        data_val_types = {ljeet__wmoxg: data.copy(ndim=1) for ljeet__wmoxg in
            qvgtu__oam}
        tfxy__cew = ['data[:,{}]{}'.format(i, bodil__afp) for i in range(
            vcrr__gajln)]
        data_dict = dict(zip(qvgtu__oam, tfxy__cew))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    rnqzk__kqwx = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[ljeet__wmoxg], df_len, ivcw__sxlpe) for
        ljeet__wmoxg in col_names))
    if len(col_names) == 0:
        rnqzk__kqwx = '()'
    return col_names, rnqzk__kqwx, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for ljeet__wmoxg in col_names:
        if ljeet__wmoxg in data_dict and is_iterable_type(data_val_types[
            ljeet__wmoxg]):
            df_len = 'len({})'.format(data_dict[ljeet__wmoxg])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(ljeet__wmoxg in data_dict for ljeet__wmoxg in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    ykqiy__nad = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for ljeet__wmoxg in col_names:
        if ljeet__wmoxg not in data_dict:
            data_dict[ljeet__wmoxg] = ykqiy__nad


@infer_global(len)
class LenTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        if isinstance(args[0], (DataFrameType, bodo.TableType)):
            return types.int64(*args)


@lower_builtin(len, DataFrameType)
def table_len_lower(context, builder, sig, args):
    impl = df_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            nrg__okfuq = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(nrg__okfuq)
        return impl
    if len(df.columns) == 0:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
        return impl

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        ker__xuli = idx.literal_value
        if isinstance(ker__xuli, int):
            jkqfd__ywj = tup.types[ker__xuli]
        elif isinstance(ker__xuli, slice):
            jkqfd__ywj = types.BaseTuple.from_types(tup.types[ker__xuli])
        return signature(jkqfd__ywj, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    ysm__llu, idx = sig.args
    idx = idx.literal_value
    tup, brulq__ywmaa = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(ysm__llu)
        if not 0 <= idx < len(ysm__llu):
            raise IndexError('cannot index at %d in %s' % (idx, ysm__llu))
        mjw__tas = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        gtc__qfjx = cgutils.unpack_tuple(builder, tup)[idx]
        mjw__tas = context.make_tuple(builder, sig.return_type, gtc__qfjx)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, mjw__tas)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, xmxon__ftfkd, suffix_x,
            suffix_y, is_join, indicator, brulq__ywmaa, brulq__ywmaa) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        rmza__fsy = {ljeet__wmoxg: i for i, ljeet__wmoxg in enumerate(left_on)}
        rfh__oeczr = {ljeet__wmoxg: i for i, ljeet__wmoxg in enumerate(
            right_on)}
        ghfm__qmklq = set(left_on) & set(right_on)
        mniv__ezt = set(left_df.columns) & set(right_df.columns)
        dhis__qfwyp = mniv__ezt - ghfm__qmklq
        xkzjq__anea = '$_bodo_index_' in left_on
        ket__gegjg = '$_bodo_index_' in right_on
        how = get_overload_const_str(xmxon__ftfkd)
        wys__qgr = how in {'left', 'outer'}
        mbuqt__piyi = how in {'right', 'outer'}
        columns = []
        data = []
        if xkzjq__anea:
            obxj__yzlk = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            obxj__yzlk = left_df.data[left_df.column_index[left_on[0]]]
        if ket__gegjg:
            asg__lcp = bodo.utils.typing.get_index_data_arr_types(right_df.
                index)[0]
        else:
            asg__lcp = right_df.data[right_df.column_index[right_on[0]]]
        if xkzjq__anea and not ket__gegjg and not is_join.literal_value:
            pqjxp__nwm = right_on[0]
            if pqjxp__nwm in left_df.column_index:
                columns.append(pqjxp__nwm)
                if (asg__lcp == bodo.dict_str_arr_type and obxj__yzlk ==
                    bodo.string_array_type):
                    yoas__nspdt = bodo.string_array_type
                else:
                    yoas__nspdt = asg__lcp
                data.append(yoas__nspdt)
        if ket__gegjg and not xkzjq__anea and not is_join.literal_value:
            cgwss__lkeb = left_on[0]
            if cgwss__lkeb in right_df.column_index:
                columns.append(cgwss__lkeb)
                if (obxj__yzlk == bodo.dict_str_arr_type and asg__lcp ==
                    bodo.string_array_type):
                    yoas__nspdt = bodo.string_array_type
                else:
                    yoas__nspdt = obxj__yzlk
                data.append(yoas__nspdt)
        for eju__esblf, xdiyb__ptvs in zip(left_df.data, left_df.columns):
            columns.append(str(xdiyb__ptvs) + suffix_x.literal_value if 
                xdiyb__ptvs in dhis__qfwyp else xdiyb__ptvs)
            if xdiyb__ptvs in ghfm__qmklq:
                if eju__esblf == bodo.dict_str_arr_type:
                    eju__esblf = right_df.data[right_df.column_index[
                        xdiyb__ptvs]]
                data.append(eju__esblf)
            else:
                if (eju__esblf == bodo.dict_str_arr_type and xdiyb__ptvs in
                    rmza__fsy):
                    if ket__gegjg:
                        eju__esblf = asg__lcp
                    else:
                        gbfm__dhit = rmza__fsy[xdiyb__ptvs]
                        ldgy__bniqw = right_on[gbfm__dhit]
                        eju__esblf = right_df.data[right_df.column_index[
                            ldgy__bniqw]]
                if mbuqt__piyi:
                    eju__esblf = to_nullable_type(eju__esblf)
                data.append(eju__esblf)
        for eju__esblf, xdiyb__ptvs in zip(right_df.data, right_df.columns):
            if xdiyb__ptvs not in ghfm__qmklq:
                columns.append(str(xdiyb__ptvs) + suffix_y.literal_value if
                    xdiyb__ptvs in dhis__qfwyp else xdiyb__ptvs)
                if (eju__esblf == bodo.dict_str_arr_type and xdiyb__ptvs in
                    rfh__oeczr):
                    if xkzjq__anea:
                        eju__esblf = obxj__yzlk
                    else:
                        gbfm__dhit = rfh__oeczr[xdiyb__ptvs]
                        fduh__fac = left_on[gbfm__dhit]
                        eju__esblf = left_df.data[left_df.column_index[
                            fduh__fac]]
                if wys__qgr:
                    eju__esblf = to_nullable_type(eju__esblf)
                data.append(eju__esblf)
        apszw__lwd = get_overload_const_bool(indicator)
        if apszw__lwd:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        awz__fzfwz = False
        if xkzjq__anea and ket__gegjg and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            awz__fzfwz = True
        elif xkzjq__anea and not ket__gegjg:
            index_typ = right_df.index
            awz__fzfwz = True
        elif ket__gegjg and not xkzjq__anea:
            index_typ = left_df.index
            awz__fzfwz = True
        if awz__fzfwz and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        lla__mjzv = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(lla__mjzv, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    pjq__cwt = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return pjq__cwt._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    imzx__tpz = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    urpa__hnsiv = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', imzx__tpz, urpa__hnsiv,
        package_name='pandas', module_name='General')
    npy__hxfq = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        cuuw__bgio = 0
        rnqzk__kqwx = []
        names = []
        for i, elfbk__ryrn in enumerate(objs.types):
            assert isinstance(elfbk__ryrn, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(elfbk__ryrn, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                elfbk__ryrn, 'pandas.concat()')
            if isinstance(elfbk__ryrn, SeriesType):
                names.append(str(cuuw__bgio))
                cuuw__bgio += 1
                rnqzk__kqwx.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(elfbk__ryrn.columns)
                for oiut__kskh in range(len(elfbk__ryrn.data)):
                    rnqzk__kqwx.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, oiut__kskh))
        return bodo.hiframes.dataframe_impl._gen_init_df(npy__hxfq, names,
            ', '.join(rnqzk__kqwx), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(nrg__okfuq, DataFrameType) for nrg__okfuq in
            objs.types)
        vcixc__jvzh = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            vcixc__jvzh.extend(df.columns)
        vcixc__jvzh = list(dict.fromkeys(vcixc__jvzh).keys())
        hwbk__qjeqe = {}
        for cuuw__bgio, ljeet__wmoxg in enumerate(vcixc__jvzh):
            for i, df in enumerate(objs.types):
                if ljeet__wmoxg in df.column_index:
                    hwbk__qjeqe[f'arr_typ{cuuw__bgio}'] = df.data[df.
                        column_index[ljeet__wmoxg]]
                    break
        assert len(hwbk__qjeqe) == len(vcixc__jvzh)
        racwi__irsob = []
        for cuuw__bgio, ljeet__wmoxg in enumerate(vcixc__jvzh):
            args = []
            for i, df in enumerate(objs.types):
                if ljeet__wmoxg in df.column_index:
                    xaw__mpk = df.column_index[ljeet__wmoxg]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, xaw__mpk))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, cuuw__bgio))
            npy__hxfq += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(cuuw__bgio, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(npy__hxfq,
            vcixc__jvzh, ', '.join('A{}'.format(i) for i in range(len(
            vcixc__jvzh))), index, hwbk__qjeqe)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(nrg__okfuq, SeriesType) for nrg__okfuq in
            objs.types)
        npy__hxfq += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            npy__hxfq += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            npy__hxfq += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        npy__hxfq += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        bfr__lpy = {}
        exec(npy__hxfq, {'bodo': bodo, 'np': np, 'numba': numba}, bfr__lpy)
        return bfr__lpy['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for cuuw__bgio, ljeet__wmoxg in enumerate(df_type.columns):
            npy__hxfq += '  arrs{} = []\n'.format(cuuw__bgio)
            npy__hxfq += '  for i in range(len(objs)):\n'
            npy__hxfq += '    df = objs[i]\n'
            npy__hxfq += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(cuuw__bgio))
            npy__hxfq += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(cuuw__bgio))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            npy__hxfq += '  arrs_index = []\n'
            npy__hxfq += '  for i in range(len(objs)):\n'
            npy__hxfq += '    df = objs[i]\n'
            npy__hxfq += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(npy__hxfq, df_type
            .columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        npy__hxfq += '  arrs = []\n'
        npy__hxfq += '  for i in range(len(objs)):\n'
        npy__hxfq += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        npy__hxfq += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            npy__hxfq += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            npy__hxfq += '  arrs_index = []\n'
            npy__hxfq += '  for i in range(len(objs)):\n'
            npy__hxfq += '    S = objs[i]\n'
            npy__hxfq += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            npy__hxfq += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        npy__hxfq += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        bfr__lpy = {}
        exec(npy__hxfq, {'bodo': bodo, 'np': np, 'numba': numba}, bfr__lpy)
        return bfr__lpy['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        obg__wmr = df.copy(index=index, is_table_format=False)
        return signature(obg__wmr, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    hhnc__txu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hhnc__txu._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    imzx__tpz = dict(index=index, name=name)
    urpa__hnsiv = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', imzx__tpz, urpa__hnsiv,
        package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        hwbk__qjeqe = (types.Array(types.int64, 1, 'C'),) + df.data
        apsxa__gwoxl = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, hwbk__qjeqe)
        return signature(apsxa__gwoxl, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    hhnc__txu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hhnc__txu._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    hhnc__txu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hhnc__txu._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    hhnc__txu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hhnc__txu._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    slva__dkxz = get_overload_const_bool(check_duplicates)
    rphh__ajdee = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    eacl__ayjy = len(value_names) > 1
    vrvbk__ychlz = None
    yurns__cxro = None
    xpyl__wfq = None
    kad__usie = None
    xlfz__ouzai = isinstance(values_tup, types.UniTuple)
    if xlfz__ouzai:
        qqm__auw = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        qqm__auw = [to_str_arr_if_dict_array(to_nullable_type(rwye__vrfzf)) for
            rwye__vrfzf in values_tup]
    npy__hxfq = 'def impl(\n'
    npy__hxfq += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    npy__hxfq += '):\n'
    npy__hxfq += '    if parallel:\n'
    mldt__uyi = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    npy__hxfq += f'        info_list = [{mldt__uyi}]\n'
    npy__hxfq += '        cpp_table = arr_info_list_to_table(info_list)\n'
    npy__hxfq += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    uhyyg__nhgkp = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    giyre__qelrc = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    erb__fkk = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    npy__hxfq += f'        index_tup = ({uhyyg__nhgkp},)\n'
    npy__hxfq += f'        columns_tup = ({giyre__qelrc},)\n'
    npy__hxfq += f'        values_tup = ({erb__fkk},)\n'
    npy__hxfq += '        delete_table(cpp_table)\n'
    npy__hxfq += '        delete_table(out_cpp_table)\n'
    npy__hxfq += '    columns_arr = columns_tup[0]\n'
    if xlfz__ouzai:
        npy__hxfq += '    values_arrs = [arr for arr in values_tup]\n'
    eecqe__pzfc = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    npy__hxfq += f'    new_index_tup = ({eecqe__pzfc},)\n'
    npy__hxfq += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    npy__hxfq += '        new_index_tup\n'
    npy__hxfq += '    )\n'
    npy__hxfq += '    n_rows = len(unique_index_arr_tup[0])\n'
    npy__hxfq += '    num_values_arrays = len(values_tup)\n'
    npy__hxfq += '    n_unique_pivots = len(pivot_values)\n'
    if xlfz__ouzai:
        npy__hxfq += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        npy__hxfq += '    n_cols = n_unique_pivots\n'
    npy__hxfq += '    col_map = {}\n'
    npy__hxfq += '    for i in range(n_unique_pivots):\n'
    npy__hxfq += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    npy__hxfq += '            raise ValueError(\n'
    npy__hxfq += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    npy__hxfq += '            )\n'
    npy__hxfq += '        col_map[pivot_values[i]] = i\n'
    yai__cggxr = False
    for i, kcem__sug in enumerate(qqm__auw):
        if is_str_arr_type(kcem__sug):
            yai__cggxr = True
            npy__hxfq += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            npy__hxfq += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if yai__cggxr:
        if slva__dkxz:
            npy__hxfq += '    nbytes = (n_rows + 7) >> 3\n'
            npy__hxfq += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        npy__hxfq += '    for i in range(len(columns_arr)):\n'
        npy__hxfq += '        col_name = columns_arr[i]\n'
        npy__hxfq += '        pivot_idx = col_map[col_name]\n'
        npy__hxfq += '        row_idx = row_vector[i]\n'
        if slva__dkxz:
            npy__hxfq += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            npy__hxfq += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            npy__hxfq += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            npy__hxfq += '        else:\n'
            npy__hxfq += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if xlfz__ouzai:
            npy__hxfq += '        for j in range(num_values_arrays):\n'
            npy__hxfq += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            npy__hxfq += '            len_arr = len_arrs_0[col_idx]\n'
            npy__hxfq += '            values_arr = values_arrs[j]\n'
            npy__hxfq += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            npy__hxfq += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            npy__hxfq += '                len_arr[row_idx] = str_val_len\n'
            npy__hxfq += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, kcem__sug in enumerate(qqm__auw):
                if is_str_arr_type(kcem__sug):
                    npy__hxfq += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    npy__hxfq += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    npy__hxfq += (
                        f'            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}\n'
                        )
                    npy__hxfq += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, kcem__sug in enumerate(qqm__auw):
        if is_str_arr_type(kcem__sug):
            npy__hxfq += f'    data_arrs_{i} = [\n'
            npy__hxfq += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            npy__hxfq += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            npy__hxfq += '        )\n'
            npy__hxfq += '        for i in range(n_cols)\n'
            npy__hxfq += '    ]\n'
        else:
            npy__hxfq += f'    data_arrs_{i} = [\n'
            npy__hxfq += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            npy__hxfq += '        for _ in range(n_cols)\n'
            npy__hxfq += '    ]\n'
    if not yai__cggxr and slva__dkxz:
        npy__hxfq += '    nbytes = (n_rows + 7) >> 3\n'
        npy__hxfq += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    npy__hxfq += '    for i in range(len(columns_arr)):\n'
    npy__hxfq += '        col_name = columns_arr[i]\n'
    npy__hxfq += '        pivot_idx = col_map[col_name]\n'
    npy__hxfq += '        row_idx = row_vector[i]\n'
    if not yai__cggxr and slva__dkxz:
        npy__hxfq += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        npy__hxfq += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        npy__hxfq += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        npy__hxfq += '        else:\n'
        npy__hxfq += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if xlfz__ouzai:
        npy__hxfq += '        for j in range(num_values_arrays):\n'
        npy__hxfq += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        npy__hxfq += '            col_arr = data_arrs_0[col_idx]\n'
        npy__hxfq += '            values_arr = values_arrs[j]\n'
        npy__hxfq += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        npy__hxfq += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        npy__hxfq += '            else:\n'
        npy__hxfq += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, kcem__sug in enumerate(qqm__auw):
            npy__hxfq += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            npy__hxfq += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            npy__hxfq += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            npy__hxfq += f'        else:\n'
            npy__hxfq += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        npy__hxfq += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        vrvbk__ychlz = index_names.meta[0]
    else:
        npy__hxfq += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        vrvbk__ychlz = tuple(index_names.meta)
    if not rphh__ajdee:
        xpyl__wfq = columns_name.meta[0]
        if eacl__ayjy:
            npy__hxfq += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            yurns__cxro = value_names.meta
            if all(isinstance(ljeet__wmoxg, str) for ljeet__wmoxg in
                yurns__cxro):
                yurns__cxro = pd.array(yurns__cxro, 'string')
            elif all(isinstance(ljeet__wmoxg, int) for ljeet__wmoxg in
                yurns__cxro):
                yurns__cxro = np.array(yurns__cxro, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(yurns__cxro.dtype, pd.StringDtype):
                npy__hxfq += '    total_chars = 0\n'
                npy__hxfq += f'    for i in range({len(value_names)}):\n'
                npy__hxfq += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                npy__hxfq += '        total_chars += value_name_str_len\n'
                npy__hxfq += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                npy__hxfq += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                npy__hxfq += '    total_chars = 0\n'
                npy__hxfq += '    for i in range(len(pivot_values)):\n'
                npy__hxfq += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                npy__hxfq += '        total_chars += pivot_val_str_len\n'
                npy__hxfq += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                npy__hxfq += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            npy__hxfq += f'    for i in range({len(value_names)}):\n'
            npy__hxfq += '        for j in range(len(pivot_values)):\n'
            npy__hxfq += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            npy__hxfq += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            npy__hxfq += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            npy__hxfq += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    zcm__xemvj = None
    if rphh__ajdee:
        if eacl__ayjy:
            lekz__fefho = []
            for rzj__qqra in _constant_pivot_values.meta:
                for jsn__bvt in value_names.meta:
                    lekz__fefho.append((rzj__qqra, jsn__bvt))
            column_names = tuple(lekz__fefho)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        kad__usie = ColNamesMetaType(column_names)
        hkjsb__nzqr = []
        for rwye__vrfzf in qqm__auw:
            hkjsb__nzqr.extend([rwye__vrfzf] * len(_constant_pivot_values))
        sag__fhsej = tuple(hkjsb__nzqr)
        zcm__xemvj = TableType(sag__fhsej)
        npy__hxfq += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        npy__hxfq += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, rwye__vrfzf in enumerate(qqm__auw):
            npy__hxfq += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {zcm__xemvj.type_to_blk[rwye__vrfzf]})
"""
        npy__hxfq += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        npy__hxfq += '        (table,), index, columns_typ\n'
        npy__hxfq += '    )\n'
    else:
        skj__umvi = ', '.join(f'data_arrs_{i}' for i in range(len(qqm__auw)))
        npy__hxfq += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({skj__umvi},), n_rows)
"""
        npy__hxfq += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        npy__hxfq += '        (table,), index, column_index\n'
        npy__hxfq += '    )\n'
    bfr__lpy = {}
    rjwj__qmdh = {f'data_arr_typ_{i}': kcem__sug for i, kcem__sug in
        enumerate(qqm__auw)}
    gqdd__bek = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        zcm__xemvj, 'columns_typ': kad__usie, 'index_names_lit':
        vrvbk__ychlz, 'value_names_lit': yurns__cxro, 'columns_name_lit':
        xpyl__wfq, **rjwj__qmdh}
    exec(npy__hxfq, gqdd__bek, bfr__lpy)
    impl = bfr__lpy['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    fdhwy__sje = {}
    fdhwy__sje['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, rjxw__yqm in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        kesf__lhh = None
        if isinstance(rjxw__yqm, bodo.DatetimeArrayType):
            bcpoo__fsl = 'datetimetz'
            jqpqa__bfzg = 'datetime64[ns]'
            if isinstance(rjxw__yqm.tz, int):
                wwv__cstw = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(rjxw__yqm.tz))
            else:
                wwv__cstw = pd.DatetimeTZDtype(tz=rjxw__yqm.tz).tz
            kesf__lhh = {'timezone': pa.lib.tzinfo_to_string(wwv__cstw)}
        elif isinstance(rjxw__yqm, types.Array) or rjxw__yqm == boolean_array:
            bcpoo__fsl = jqpqa__bfzg = rjxw__yqm.dtype.name
            if jqpqa__bfzg.startswith('datetime'):
                bcpoo__fsl = 'datetime'
        elif is_str_arr_type(rjxw__yqm):
            bcpoo__fsl = 'unicode'
            jqpqa__bfzg = 'object'
        elif rjxw__yqm == binary_array_type:
            bcpoo__fsl = 'bytes'
            jqpqa__bfzg = 'object'
        elif isinstance(rjxw__yqm, DecimalArrayType):
            bcpoo__fsl = jqpqa__bfzg = 'object'
        elif isinstance(rjxw__yqm, IntegerArrayType):
            gfnpy__xxgd = rjxw__yqm.dtype.name
            if gfnpy__xxgd.startswith('int'):
                bcpoo__fsl = 'Int' + gfnpy__xxgd[3:]
            elif gfnpy__xxgd.startswith('uint'):
                bcpoo__fsl = 'UInt' + gfnpy__xxgd[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, rjxw__yqm))
            jqpqa__bfzg = rjxw__yqm.dtype.name
        elif rjxw__yqm == datetime_date_array_type:
            bcpoo__fsl = 'datetime'
            jqpqa__bfzg = 'object'
        elif isinstance(rjxw__yqm, (StructArrayType, ArrayItemArrayType)):
            bcpoo__fsl = 'object'
            jqpqa__bfzg = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, rjxw__yqm))
        atn__gqo = {'name': col_name, 'field_name': col_name, 'pandas_type':
            bcpoo__fsl, 'numpy_type': jqpqa__bfzg, 'metadata': kesf__lhh}
        fdhwy__sje['columns'].append(atn__gqo)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            gfpcz__qmfo = '__index_level_0__'
            ifpt__vvdz = None
        else:
            gfpcz__qmfo = '%s'
            ifpt__vvdz = '%s'
        fdhwy__sje['index_columns'] = [gfpcz__qmfo]
        fdhwy__sje['columns'].append({'name': ifpt__vvdz, 'field_name':
            gfpcz__qmfo, 'pandas_type': index.pandas_type_name,
            'numpy_type': index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        fdhwy__sje['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        fdhwy__sje['index_columns'] = []
    fdhwy__sje['pandas_version'] = pd.__version__
    return fdhwy__sje


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, path, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, row_group_size=-
    1, _is_parallel=False):
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if df.has_runtime_cols and not is_overload_none(partition_cols):
        raise BodoError(
            f"DataFrame.to_parquet(): Providing 'partition_cols' on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information."
            )
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        vkjz__bwmg = []
        for rdnm__ktafl in partition_cols:
            try:
                idx = df.columns.index(rdnm__ktafl)
            except ValueError as ytfg__ddgc:
                raise BodoError(
                    f'Partition column {rdnm__ktafl} is not in dataframe')
            vkjz__bwmg.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    pekx__ksd = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    cjpbb__wwq = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not pekx__ksd)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not pekx__ksd or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and pekx__ksd and not is_overload_true(_is_parallel)
    if df.has_runtime_cols:
        if isinstance(df.runtime_colname_typ, MultiIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): Not supported with MultiIndex runtime column names. Please return the DataFrame to regular Python to update typing information.'
                )
        if not isinstance(df.runtime_colname_typ, bodo.hiframes.
            pd_index_ext.StringIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): parquet must have string column names. Please return the DataFrame with runtime column names to regular Python to modify column names.'
                )
        sty__iuzau = df.runtime_data_types
        sxaya__rieha = len(sty__iuzau)
        kesf__lhh = gen_pandas_parquet_metadata([''] * sxaya__rieha,
            sty__iuzau, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        uejy__rbqp = kesf__lhh['columns'][:sxaya__rieha]
        kesf__lhh['columns'] = kesf__lhh['columns'][sxaya__rieha:]
        uejy__rbqp = [json.dumps(qheb__geje).replace('""', '{0}') for
            qheb__geje in uejy__rbqp]
        tygzk__ybcs = json.dumps(kesf__lhh)
        zldo__rjvo = '"columns": ['
        scfpo__qvei = tygzk__ybcs.find(zldo__rjvo)
        if scfpo__qvei == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        aybh__ooy = scfpo__qvei + len(zldo__rjvo)
        fxx__yizki = tygzk__ybcs[:aybh__ooy]
        tygzk__ybcs = tygzk__ybcs[aybh__ooy:]
        trwl__wzodd = len(kesf__lhh['columns'])
    else:
        tygzk__ybcs = json.dumps(gen_pandas_parquet_metadata(df.columns, df
            .data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and pekx__ksd:
        tygzk__ybcs = tygzk__ybcs.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            tygzk__ybcs = tygzk__ybcs.replace('"%s"', '%s')
    if not df.is_table_format:
        rnqzk__kqwx = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    npy__hxfq = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _is_parallel=False):
"""
    if df.is_table_format:
        npy__hxfq += '    py_table = get_dataframe_table(df)\n'
        npy__hxfq += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        npy__hxfq += '    info_list = [{}]\n'.format(rnqzk__kqwx)
        npy__hxfq += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        npy__hxfq += '    columns_index = get_dataframe_column_names(df)\n'
        npy__hxfq += '    names_arr = index_to_array(columns_index)\n'
        npy__hxfq += '    col_names = array_to_info(names_arr)\n'
    else:
        npy__hxfq += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and cjpbb__wwq:
        npy__hxfq += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        lnuzh__dyrdj = True
    else:
        npy__hxfq += '    index_col = array_to_info(np.empty(0))\n'
        lnuzh__dyrdj = False
    if df.has_runtime_cols:
        npy__hxfq += '    columns_lst = []\n'
        npy__hxfq += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            npy__hxfq += f'    for _ in range(len(py_table.block_{i})):\n'
            npy__hxfq += f"""        columns_lst.append({uejy__rbqp[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            npy__hxfq += '        num_cols += 1\n'
        if trwl__wzodd:
            npy__hxfq += "    columns_lst.append('')\n"
        npy__hxfq += '    columns_str = ", ".join(columns_lst)\n'
        npy__hxfq += ('    metadata = """' + fxx__yizki +
            '""" + columns_str + """' + tygzk__ybcs + '"""\n')
    else:
        npy__hxfq += '    metadata = """' + tygzk__ybcs + '"""\n'
    npy__hxfq += '    if compression is None:\n'
    npy__hxfq += "        compression = 'none'\n"
    npy__hxfq += '    if df.index.name is not None:\n'
    npy__hxfq += '        name_ptr = df.index.name\n'
    npy__hxfq += '    else:\n'
    npy__hxfq += "        name_ptr = 'null'\n"
    npy__hxfq += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    wul__urw = None
    if partition_cols:
        wul__urw = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        uajy__okw = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in vkjz__bwmg)
        if uajy__okw:
            npy__hxfq += '    cat_info_list = [{}]\n'.format(uajy__okw)
            npy__hxfq += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            npy__hxfq += '    cat_table = table\n'
        npy__hxfq += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        npy__hxfq += (
            f'    part_cols_idxs = np.array({vkjz__bwmg}, dtype=np.int32)\n')
        npy__hxfq += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        npy__hxfq += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        npy__hxfq += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        npy__hxfq += (
            '                            unicode_to_utf8(compression),\n')
        npy__hxfq += '                            _is_parallel,\n'
        npy__hxfq += (
            '                            unicode_to_utf8(bucket_region),\n')
        npy__hxfq += '                            row_group_size)\n'
        npy__hxfq += '    delete_table_decref_arrays(table)\n'
        npy__hxfq += '    delete_info_decref_array(index_col)\n'
        npy__hxfq += '    delete_info_decref_array(col_names_no_partitions)\n'
        npy__hxfq += '    delete_info_decref_array(col_names)\n'
        if uajy__okw:
            npy__hxfq += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        npy__hxfq += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        npy__hxfq += (
            '                            table, col_names, index_col,\n')
        npy__hxfq += '                            ' + str(lnuzh__dyrdj) + ',\n'
        npy__hxfq += '                            unicode_to_utf8(metadata),\n'
        npy__hxfq += (
            '                            unicode_to_utf8(compression),\n')
        npy__hxfq += (
            '                            _is_parallel, 1, df.index.start,\n')
        npy__hxfq += (
            '                            df.index.stop, df.index.step,\n')
        npy__hxfq += '                            unicode_to_utf8(name_ptr),\n'
        npy__hxfq += (
            '                            unicode_to_utf8(bucket_region),\n')
        npy__hxfq += '                            row_group_size)\n'
        npy__hxfq += '    delete_table_decref_arrays(table)\n'
        npy__hxfq += '    delete_info_decref_array(index_col)\n'
        npy__hxfq += '    delete_info_decref_array(col_names)\n'
    else:
        npy__hxfq += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        npy__hxfq += (
            '                            table, col_names, index_col,\n')
        npy__hxfq += '                            ' + str(lnuzh__dyrdj) + ',\n'
        npy__hxfq += '                            unicode_to_utf8(metadata),\n'
        npy__hxfq += (
            '                            unicode_to_utf8(compression),\n')
        npy__hxfq += '                            _is_parallel, 0, 0, 0, 0,\n'
        npy__hxfq += '                            unicode_to_utf8(name_ptr),\n'
        npy__hxfq += (
            '                            unicode_to_utf8(bucket_region),\n')
        npy__hxfq += '                            row_group_size)\n'
        npy__hxfq += '    delete_table_decref_arrays(table)\n'
        npy__hxfq += '    delete_info_decref_array(index_col)\n'
        npy__hxfq += '    delete_info_decref_array(col_names)\n'
    bfr__lpy = {}
    if df.has_runtime_cols:
        ujoaq__tsky = None
    else:
        for xdiyb__ptvs in df.columns:
            if not isinstance(xdiyb__ptvs, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        ujoaq__tsky = pd.array(df.columns)
    exec(npy__hxfq, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': ujoaq__tsky,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': wul__urw, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, bfr__lpy)
    lygmx__xvd = bfr__lpy['df_to_parquet']
    return lygmx__xvd


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    lrj__nwxo = 'all_ok'
    ddxvt__aeuu, fsfil__vzs = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        svm__yxacu = 100
        if chunksize is None:
            usjn__vlw = svm__yxacu
        else:
            usjn__vlw = min(chunksize, svm__yxacu)
        if _is_table_create:
            df = df.iloc[:usjn__vlw, :]
        else:
            df = df.iloc[usjn__vlw:, :]
            if len(df) == 0:
                return lrj__nwxo
    gbdbx__izj = df.columns
    try:
        if ddxvt__aeuu == 'snowflake':
            if fsfil__vzs and con.count(fsfil__vzs) == 1:
                con = con.replace(fsfil__vzs, quote(fsfil__vzs))
            try:
                from snowflake.connector.pandas_tools import pd_writer
                from bodo import snowflake_sqlalchemy_compat
                if method is not None and _is_table_create and bodo.get_rank(
                    ) == 0:
                    import warnings
                    from bodo.utils.typing import BodoWarning
                    warnings.warn(BodoWarning(
                        'DataFrame.to_sql(): method argument is not supported with Snowflake. Bodo always uses snowflake.connector.pandas_tools.pd_writer to write data.'
                        ))
                method = pd_writer
                df.columns = [(ljeet__wmoxg.upper() if ljeet__wmoxg.islower
                    () else ljeet__wmoxg) for ljeet__wmoxg in df.columns]
            except ImportError as ytfg__ddgc:
                lrj__nwxo = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return lrj__nwxo
        if ddxvt__aeuu == 'oracle':
            import sqlalchemy as sa
            xsv__eotc = bodo.typeof(df)
            xjo__krocs = {}
            for ljeet__wmoxg, etnz__saczg in zip(xsv__eotc.columns,
                xsv__eotc.data):
                if df[ljeet__wmoxg].dtype == 'object':
                    if etnz__saczg == datetime_date_array_type:
                        xjo__krocs[ljeet__wmoxg] = sa.types.Date
                    elif etnz__saczg == bodo.string_array_type:
                        xjo__krocs[ljeet__wmoxg] = sa.types.VARCHAR(df[
                            ljeet__wmoxg].str.len().max())
            dtype = xjo__krocs
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as ecgl__tzguo:
            lrj__nwxo = ecgl__tzguo.args[0]
        return lrj__nwxo
    finally:
        df.columns = gbdbx__izj


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None, _is_table_create=False, _is_parallel=False):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method, _is_table_create,
            _is_parallel)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    if is_overload_none(schema):
        if bodo.get_rank() == 0:
            import warnings
            warnings.warn(BodoWarning(
                f'DataFrame.to_sql(): schema argument is recommended to avoid permission issues when writing the table.'
                ))
    if not (is_overload_none(chunksize) or isinstance(chunksize, types.Integer)
        ):
        raise BodoError(
            "DataFrame.to_sql(): 'chunksize' argument must be an integer if provided."
            )

    def _impl(df, name, con, schema=None, if_exists='fail', index=True,
        index_label=None, chunksize=None, dtype=None, method=None,
        _is_parallel=False):
        ohfqz__giv = bodo.libs.distributed_api.get_rank()
        lrj__nwxo = 'unset'
        if ohfqz__giv != 0:
            lrj__nwxo = bcast_scalar(lrj__nwxo)
        elif ohfqz__giv == 0:
            lrj__nwxo = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                True, _is_parallel)
            lrj__nwxo = bcast_scalar(lrj__nwxo)
        if_exists = 'append'
        if _is_parallel and lrj__nwxo == 'all_ok':
            lrj__nwxo = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                False, _is_parallel)
        if lrj__nwxo != 'all_ok':
            print('err_msg=', lrj__nwxo)
            raise ValueError('error in to_sql() operation')
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        prp__bex = get_overload_const_str(path_or_buf)
        if prp__bex.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if not (is_overload_none(columns) or isinstance(columns, (types.List,
        types.Tuple))):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must be list a or tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='records', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=True, compression='infer', index=True,
    indent=None, storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='records', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=True, compression='infer', index=
            True, indent=None, storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='records', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=True, compression='infer', index=True,
        indent=None, storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        cvqzc__dhaw = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(cvqzc__dhaw))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(cvqzc__dhaw))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    yvb__pire = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    fjrhf__qwh = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', yvb__pire, fjrhf__qwh,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    npy__hxfq = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        poc__arjfr = data.data.dtype.categories
        npy__hxfq += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        poc__arjfr = data.dtype.categories
        npy__hxfq += '  data_values = data\n'
    vcrr__gajln = len(poc__arjfr)
    npy__hxfq += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    npy__hxfq += '  numba.parfors.parfor.init_prange()\n'
    npy__hxfq += '  n = len(data_values)\n'
    for i in range(vcrr__gajln):
        npy__hxfq += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    npy__hxfq += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    npy__hxfq += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for oiut__kskh in range(vcrr__gajln):
        npy__hxfq += '          data_arr_{}[i] = 0\n'.format(oiut__kskh)
    npy__hxfq += '      else:\n'
    for wvz__bln in range(vcrr__gajln):
        npy__hxfq += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            wvz__bln)
    rnqzk__kqwx = ', '.join(f'data_arr_{i}' for i in range(vcrr__gajln))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(poc__arjfr[0], np.datetime64):
        poc__arjfr = tuple(pd.Timestamp(ljeet__wmoxg) for ljeet__wmoxg in
            poc__arjfr)
    elif isinstance(poc__arjfr[0], np.timedelta64):
        poc__arjfr = tuple(pd.Timedelta(ljeet__wmoxg) for ljeet__wmoxg in
            poc__arjfr)
    return bodo.hiframes.dataframe_impl._gen_init_df(npy__hxfq, poc__arjfr,
        rnqzk__kqwx, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_query, pd.read_gbq, pd.read_stata, pd.ExcelWriter, pd.
    json_normalize, pd.merge_ordered, pd.factorize, pd.wide_to_long, pd.
    bdate_range, pd.period_range, pd.infer_freq, pd.interval_range, pd.eval,
    pd.test, pd.Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'lt', 'gt', 'le', 'ge', 'ne', 'eq', 'combine', 'combine_first',
    'subtract', 'divide', 'multiply', 'applymap', 'agg', 'aggregate',
    'transform', 'expanding', 'ewm', 'all', 'any', 'clip', 'corrwith',
    'cummax', 'cummin', 'eval', 'kurt', 'kurtosis', 'mad', 'mode', 'rank',
    'round', 'sem', 'skew', 'value_counts', 'add_prefix', 'add_suffix',
    'align', 'at_time', 'between_time', 'equals', 'reindex', 'reindex_like',
    'rename_axis', 'set_axis', 'truncate', 'backfill', 'bfill', 'ffill',
    'interpolate', 'pad', 'droplevel', 'reorder_levels', 'nlargest',
    'nsmallest', 'swaplevel', 'stack', 'unstack', 'swapaxes', 'squeeze',
    'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq', 'asof',
    'slice_shift', 'tshift', 'first_valid_index', 'last_valid_index',
    'resample', 'to_period', 'to_timestamp', 'tz_convert', 'tz_localize',
    'boxplot', 'hist', 'from_dict', 'from_records', 'to_pickle', 'to_hdf',
    'to_dict', 'to_excel', 'to_html', 'to_feather', 'to_latex', 'to_stata',
    'to_gbq', 'to_records', 'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for wozay__nowng in pd_unsupported:
        qcrg__urph = mod_name + '.' + wozay__nowng.__name__
        overload(wozay__nowng, no_unliteral=True)(create_unsupported_overload
            (qcrg__urph))


def _install_dataframe_unsupported():
    for gbaee__igmg in dataframe_unsupported_attrs:
        qai__qom = 'DataFrame.' + gbaee__igmg
        overload_attribute(DataFrameType, gbaee__igmg)(
            create_unsupported_overload(qai__qom))
    for qcrg__urph in dataframe_unsupported:
        qai__qom = 'DataFrame.' + qcrg__urph + '()'
        overload_method(DataFrameType, qcrg__urph)(create_unsupported_overload
            (qai__qom))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
