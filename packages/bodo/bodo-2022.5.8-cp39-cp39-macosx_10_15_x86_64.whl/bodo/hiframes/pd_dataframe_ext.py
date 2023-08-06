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
            irwcb__meg = f'{len(self.data)} columns of types {set(self.data)}'
            grei__dckq = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({irwcb__meg}, {self.index}, {grei__dckq}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {lxof__zun: i for i, lxof__zun in enumerate(self.columns)}

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
            kpk__gcbzk = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(xad__qkq.unify(typingctx, omii__xvy) if xad__qkq !=
                omii__xvy else xad__qkq for xad__qkq, omii__xvy in zip(self
                .data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if kpk__gcbzk is not None and None not in data:
                return DataFrameType(data, kpk__gcbzk, self.columns, dist,
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
        return all(xad__qkq.is_precise() for xad__qkq in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        nbvj__dovxb = self.columns.index(col_name)
        ofq__ppblh = tuple(list(self.data[:nbvj__dovxb]) + [new_type] +
            list(self.data[nbvj__dovxb + 1:]))
        return DataFrameType(ofq__ppblh, self.index, self.columns, self.
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
        rcpe__evp = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            rcpe__evp.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, rcpe__evp)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        rcpe__evp = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, rcpe__evp)


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
        mrwv__gfu = 'n',
        mtctb__hrthy = {'n': 5}
        pzt__gbe, iub__szx = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, mrwv__gfu, mtctb__hrthy)
        krxt__bkno = iub__szx[0]
        if not is_overload_int(krxt__bkno):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        mpr__vpiat = df.copy()
        return mpr__vpiat(*iub__szx).replace(pysig=pzt__gbe)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        vatfb__ullno = (df,) + args
        mrwv__gfu = 'df', 'method', 'min_periods'
        mtctb__hrthy = {'method': 'pearson', 'min_periods': 1}
        kzy__bibn = 'method',
        pzt__gbe, iub__szx = bodo.utils.typing.fold_typing_args(func_name,
            vatfb__ullno, kws, mrwv__gfu, mtctb__hrthy, kzy__bibn)
        jkn__jdhzs = iub__szx[2]
        if not is_overload_int(jkn__jdhzs):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        giynh__zllmx = []
        blha__vwj = []
        for lxof__zun, bzimj__hunp in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(bzimj__hunp.dtype):
                giynh__zllmx.append(lxof__zun)
                blha__vwj.append(types.Array(types.float64, 1, 'A'))
        if len(giynh__zllmx) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        blha__vwj = tuple(blha__vwj)
        giynh__zllmx = tuple(giynh__zllmx)
        index_typ = bodo.utils.typing.type_col_to_index(giynh__zllmx)
        mpr__vpiat = DataFrameType(blha__vwj, index_typ, giynh__zllmx)
        return mpr__vpiat(*iub__szx).replace(pysig=pzt__gbe)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        gtfn__pbkqe = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        uieep__zau = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        qlsor__meoy = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        lde__qigk = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        ikfyf__auw = dict(raw=uieep__zau, result_type=qlsor__meoy)
        dxa__kdr = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', ikfyf__auw, dxa__kdr,
            package_name='pandas', module_name='DataFrame')
        juvyu__yppk = True
        if types.unliteral(gtfn__pbkqe) == types.unicode_type:
            if not is_overload_constant_str(gtfn__pbkqe):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            juvyu__yppk = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        xxzey__nft = get_overload_const_int(axis)
        if juvyu__yppk and xxzey__nft != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif xxzey__nft not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        xsy__lui = []
        for arr_typ in df.data:
            zjur__dmt = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            nig__vbvox = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(zjur__dmt), types.int64), {}
                ).return_type
            xsy__lui.append(nig__vbvox)
        udr__pjven = types.none
        xvrwd__rjrw = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(lxof__zun) for lxof__zun in df.columns)), None)
        hpj__cuxtg = types.BaseTuple.from_types(xsy__lui)
        qtep__rghpw = types.Tuple([types.bool_] * len(hpj__cuxtg))
        lpsg__uno = bodo.NullableTupleType(hpj__cuxtg, qtep__rghpw)
        rshnm__etfx = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if rshnm__etfx == types.NPDatetime('ns'):
            rshnm__etfx = bodo.pd_timestamp_type
        if rshnm__etfx == types.NPTimedelta('ns'):
            rshnm__etfx = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(hpj__cuxtg):
            fggs__pvusy = HeterogeneousSeriesType(lpsg__uno, xvrwd__rjrw,
                rshnm__etfx)
        else:
            fggs__pvusy = SeriesType(hpj__cuxtg.dtype, lpsg__uno,
                xvrwd__rjrw, rshnm__etfx)
        jntf__lxar = fggs__pvusy,
        if lde__qigk is not None:
            jntf__lxar += tuple(lde__qigk.types)
        try:
            if not juvyu__yppk:
                sjul__cmdu = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(gtfn__pbkqe), self.context,
                    'DataFrame.apply', axis if xxzey__nft == 1 else None)
            else:
                sjul__cmdu = get_const_func_output_type(gtfn__pbkqe,
                    jntf__lxar, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as jco__tov:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', jco__tov))
        if juvyu__yppk:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(sjul__cmdu, (SeriesType, HeterogeneousSeriesType)
                ) and sjul__cmdu.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(sjul__cmdu, HeterogeneousSeriesType):
                dhwkv__eje, xxowm__aih = sjul__cmdu.const_info
                if isinstance(sjul__cmdu.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    ggtth__afhc = sjul__cmdu.data.tuple_typ.types
                elif isinstance(sjul__cmdu.data, types.Tuple):
                    ggtth__afhc = sjul__cmdu.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                yab__gfqg = tuple(to_nullable_type(dtype_to_array_type(
                    ogv__iluaf)) for ogv__iluaf in ggtth__afhc)
                ibldl__dztop = DataFrameType(yab__gfqg, df.index, xxowm__aih)
            elif isinstance(sjul__cmdu, SeriesType):
                eamgq__lgc, xxowm__aih = sjul__cmdu.const_info
                yab__gfqg = tuple(to_nullable_type(dtype_to_array_type(
                    sjul__cmdu.dtype)) for dhwkv__eje in range(eamgq__lgc))
                ibldl__dztop = DataFrameType(yab__gfqg, df.index, xxowm__aih)
            else:
                gun__gqti = get_udf_out_arr_type(sjul__cmdu)
                ibldl__dztop = SeriesType(gun__gqti.dtype, gun__gqti, df.
                    index, None)
        else:
            ibldl__dztop = sjul__cmdu
        bmjr__fodix = ', '.join("{} = ''".format(xad__qkq) for xad__qkq in
            kws.keys())
        zdr__efu = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {bmjr__fodix}):
"""
        zdr__efu += '    pass\n'
        iwwl__kzdi = {}
        exec(zdr__efu, {}, iwwl__kzdi)
        ryvum__hkc = iwwl__kzdi['apply_stub']
        pzt__gbe = numba.core.utils.pysignature(ryvum__hkc)
        xzf__fhvq = (gtfn__pbkqe, axis, uieep__zau, qlsor__meoy, lde__qigk
            ) + tuple(kws.values())
        return signature(ibldl__dztop, *xzf__fhvq).replace(pysig=pzt__gbe)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        mrwv__gfu = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        mtctb__hrthy = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        kzy__bibn = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        pzt__gbe, iub__szx = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, mrwv__gfu, mtctb__hrthy, kzy__bibn)
        debor__gsnbb = iub__szx[2]
        if not is_overload_constant_str(debor__gsnbb):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        gpm__unyl = iub__szx[0]
        if not is_overload_none(gpm__unyl) and not (is_overload_int(
            gpm__unyl) or is_overload_constant_str(gpm__unyl)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(gpm__unyl):
            uxq__fyex = get_overload_const_str(gpm__unyl)
            if uxq__fyex not in df.columns:
                raise BodoError(f'{func_name}: {uxq__fyex} column not found.')
        elif is_overload_int(gpm__unyl):
            xtaq__mar = get_overload_const_int(gpm__unyl)
            if xtaq__mar > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {xtaq__mar} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            gpm__unyl = df.columns[gpm__unyl]
        nxxz__igua = iub__szx[1]
        if not is_overload_none(nxxz__igua) and not (is_overload_int(
            nxxz__igua) or is_overload_constant_str(nxxz__igua)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(nxxz__igua):
            yxb__qgkja = get_overload_const_str(nxxz__igua)
            if yxb__qgkja not in df.columns:
                raise BodoError(f'{func_name}: {yxb__qgkja} column not found.')
        elif is_overload_int(nxxz__igua):
            hvxpk__qffp = get_overload_const_int(nxxz__igua)
            if hvxpk__qffp > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {hvxpk__qffp} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            nxxz__igua = df.columns[nxxz__igua]
        nsuu__zjh = iub__szx[3]
        if not is_overload_none(nsuu__zjh) and not is_tuple_like_type(nsuu__zjh
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        mzuh__ttjso = iub__szx[10]
        if not is_overload_none(mzuh__ttjso) and not is_overload_constant_str(
            mzuh__ttjso):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        whwu__pjk = iub__szx[12]
        if not is_overload_bool(whwu__pjk):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        szjk__bvqt = iub__szx[17]
        if not is_overload_none(szjk__bvqt) and not is_tuple_like_type(
            szjk__bvqt):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        xxyb__lii = iub__szx[18]
        if not is_overload_none(xxyb__lii) and not is_tuple_like_type(xxyb__lii
            ):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        wtsx__dav = iub__szx[22]
        if not is_overload_none(wtsx__dav) and not is_overload_int(wtsx__dav):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        jpdyj__tdyl = iub__szx[29]
        if not is_overload_none(jpdyj__tdyl) and not is_overload_constant_str(
            jpdyj__tdyl):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        vrvk__rvz = iub__szx[30]
        if not is_overload_none(vrvk__rvz) and not is_overload_constant_str(
            vrvk__rvz):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        mzip__gvjo = types.List(types.mpl_line_2d_type)
        debor__gsnbb = get_overload_const_str(debor__gsnbb)
        if debor__gsnbb == 'scatter':
            if is_overload_none(gpm__unyl) and is_overload_none(nxxz__igua):
                raise BodoError(
                    f'{func_name}: {debor__gsnbb} requires an x and y column.')
            elif is_overload_none(gpm__unyl):
                raise BodoError(
                    f'{func_name}: {debor__gsnbb} x column is missing.')
            elif is_overload_none(nxxz__igua):
                raise BodoError(
                    f'{func_name}: {debor__gsnbb} y column is missing.')
            mzip__gvjo = types.mpl_path_collection_type
        elif debor__gsnbb != 'line':
            raise BodoError(
                f'{func_name}: {debor__gsnbb} plot is not supported.')
        return signature(mzip__gvjo, *iub__szx).replace(pysig=pzt__gbe)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            xoqk__agm = df.columns.index(attr)
            arr_typ = df.data[xoqk__agm]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            cbs__hvfv = []
            ofq__ppblh = []
            eyh__kmo = False
            for i, lmfm__mcpy in enumerate(df.columns):
                if lmfm__mcpy[0] != attr:
                    continue
                eyh__kmo = True
                cbs__hvfv.append(lmfm__mcpy[1] if len(lmfm__mcpy) == 2 else
                    lmfm__mcpy[1:])
                ofq__ppblh.append(df.data[i])
            if eyh__kmo:
                return DataFrameType(tuple(ofq__ppblh), df.index, tuple(
                    cbs__hvfv))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        pwlp__rtd = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(pwlp__rtd)
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
        jph__qgz = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], jph__qgz)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    tbhl__kfraw = builder.module
    clccn__yfeq = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    wshrr__fdf = cgutils.get_or_insert_function(tbhl__kfraw, clccn__yfeq,
        name='.dtor.df.{}'.format(df_type))
    if not wshrr__fdf.is_declaration:
        return wshrr__fdf
    wshrr__fdf.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(wshrr__fdf.append_basic_block())
    fvqa__bcz = wshrr__fdf.args[0]
    rnsvb__ecmm = context.get_value_type(payload_type).as_pointer()
    ddxwr__qmoyw = builder.bitcast(fvqa__bcz, rnsvb__ecmm)
    payload = context.make_helper(builder, payload_type, ref=ddxwr__qmoyw)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        jlahf__uzb = context.get_python_api(builder)
        gbeo__clmqi = jlahf__uzb.gil_ensure()
        jlahf__uzb.decref(payload.parent)
        jlahf__uzb.gil_release(gbeo__clmqi)
    builder.ret_void()
    return wshrr__fdf


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    rmi__yfh = cgutils.create_struct_proxy(payload_type)(context, builder)
    rmi__yfh.data = data_tup
    rmi__yfh.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        rmi__yfh.columns = colnames
    hskwk__cpy = context.get_value_type(payload_type)
    muky__nrm = context.get_abi_sizeof(hskwk__cpy)
    sqsxh__oqhrx = define_df_dtor(context, builder, df_type, payload_type)
    grj__hyfdr = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, muky__nrm), sqsxh__oqhrx)
    ifee__mzxc = context.nrt.meminfo_data(builder, grj__hyfdr)
    zydy__ghdbp = builder.bitcast(ifee__mzxc, hskwk__cpy.as_pointer())
    npyuz__get = cgutils.create_struct_proxy(df_type)(context, builder)
    npyuz__get.meminfo = grj__hyfdr
    if parent is None:
        npyuz__get.parent = cgutils.get_null_value(npyuz__get.parent.type)
    else:
        npyuz__get.parent = parent
        rmi__yfh.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            jlahf__uzb = context.get_python_api(builder)
            gbeo__clmqi = jlahf__uzb.gil_ensure()
            jlahf__uzb.incref(parent)
            jlahf__uzb.gil_release(gbeo__clmqi)
    builder.store(rmi__yfh._getvalue(), zydy__ghdbp)
    return npyuz__get._getvalue()


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
        lxlan__gck = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        lxlan__gck = [ogv__iluaf for ogv__iluaf in data_typ.dtype.arr_types]
    vaza__xiac = DataFrameType(tuple(lxlan__gck + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        jaipd__ugq = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return jaipd__ugq
    sig = signature(vaza__xiac, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    eamgq__lgc = len(data_tup_typ.types)
    if eamgq__lgc == 0:
        column_names = ()
    swvvh__kwolr = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    if isinstance(swvvh__kwolr, ColNamesMetaType):
        assert isinstance(swvvh__kwolr.meta, tuple)
        column_names = swvvh__kwolr.meta
    elif isinstance(swvvh__kwolr, DataFrameType):
        column_names = swvvh__kwolr.columns
    else:
        column_names = get_const_tup_vals(swvvh__kwolr)
    if eamgq__lgc == 1 and isinstance(data_tup_typ.types[0], TableType):
        eamgq__lgc = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == eamgq__lgc, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    hqfn__rfmo = data_tup_typ.types
    if eamgq__lgc != 0 and isinstance(data_tup_typ.types[0], TableType):
        hqfn__rfmo = data_tup_typ.types[0].arr_types
        is_table_format = True
    vaza__xiac = DataFrameType(hqfn__rfmo, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            ohxon__ukvg = cgutils.create_struct_proxy(vaza__xiac.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = ohxon__ukvg.parent
        jaipd__ugq = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return jaipd__ugq
    sig = signature(vaza__xiac, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        npyuz__get = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, npyuz__get.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        rmi__yfh = get_dataframe_payload(context, builder, df_typ, args[0])
        lxcp__scukv = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[lxcp__scukv]
        if df_typ.is_table_format:
            ohxon__ukvg = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(rmi__yfh.data, 0))
            rqg__sdvzm = df_typ.table_type.type_to_blk[arr_typ]
            vfbl__untj = getattr(ohxon__ukvg, f'block_{rqg__sdvzm}')
            mnmm__hmz = ListInstance(context, builder, types.List(arr_typ),
                vfbl__untj)
            wzse__gjlq = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[lxcp__scukv])
            jph__qgz = mnmm__hmz.getitem(wzse__gjlq)
        else:
            jph__qgz = builder.extract_value(rmi__yfh.data, lxcp__scukv)
        skahl__fpwg = cgutils.alloca_once_value(builder, jph__qgz)
        tdg__ljvn = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, skahl__fpwg, tdg__ljvn)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    grj__hyfdr = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, grj__hyfdr)
    rnsvb__ecmm = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, rnsvb__ecmm)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    vaza__xiac = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        vaza__xiac = types.Tuple([TableType(df_typ.data)])
    sig = signature(vaza__xiac, df_typ)

    def codegen(context, builder, signature, args):
        rmi__yfh = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            rmi__yfh.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        rmi__yfh = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, rmi__yfh.index
            )
    vaza__xiac = df_typ.index
    sig = signature(vaza__xiac, df_typ)
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
        mpr__vpiat = df.data[i]
        return mpr__vpiat(*args)


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
        rmi__yfh = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(rmi__yfh.data, 0))
    return df_typ.table_type(df_typ), codegen


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        rmi__yfh = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, rmi__yfh.columns)
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
    hpj__cuxtg = self.typemap[data_tup.name]
    if any(is_tuple_like_type(ogv__iluaf) for ogv__iluaf in hpj__cuxtg.types):
        return None
    if equiv_set.has_shape(data_tup):
        nik__jkz = equiv_set.get_shape(data_tup)
        if len(nik__jkz) > 1:
            equiv_set.insert_equiv(*nik__jkz)
        if len(nik__jkz) > 0:
            xvrwd__rjrw = self.typemap[index.name]
            if not isinstance(xvrwd__rjrw, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(nik__jkz[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(nik__jkz[0], len(
                nik__jkz)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    dewa__rgjqk = args[0]
    data_types = self.typemap[dewa__rgjqk.name].data
    if any(is_tuple_like_type(ogv__iluaf) for ogv__iluaf in data_types):
        return None
    if equiv_set.has_shape(dewa__rgjqk):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            dewa__rgjqk)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    dewa__rgjqk = args[0]
    xvrwd__rjrw = self.typemap[dewa__rgjqk.name].index
    if isinstance(xvrwd__rjrw, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(dewa__rgjqk):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            dewa__rgjqk)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    dewa__rgjqk = args[0]
    if equiv_set.has_shape(dewa__rgjqk):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            dewa__rgjqk), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    dewa__rgjqk = args[0]
    if equiv_set.has_shape(dewa__rgjqk):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            dewa__rgjqk)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    lxcp__scukv = get_overload_const_int(c_ind_typ)
    if df_typ.data[lxcp__scukv] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        yppn__lrorx, dhwkv__eje, nsbri__ner = args
        rmi__yfh = get_dataframe_payload(context, builder, df_typ, yppn__lrorx)
        if df_typ.is_table_format:
            ohxon__ukvg = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(rmi__yfh.data, 0))
            rqg__sdvzm = df_typ.table_type.type_to_blk[arr_typ]
            vfbl__untj = getattr(ohxon__ukvg, f'block_{rqg__sdvzm}')
            mnmm__hmz = ListInstance(context, builder, types.List(arr_typ),
                vfbl__untj)
            wzse__gjlq = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[lxcp__scukv])
            mnmm__hmz.setitem(wzse__gjlq, nsbri__ner, True)
        else:
            jph__qgz = builder.extract_value(rmi__yfh.data, lxcp__scukv)
            context.nrt.decref(builder, df_typ.data[lxcp__scukv], jph__qgz)
            rmi__yfh.data = builder.insert_value(rmi__yfh.data, nsbri__ner,
                lxcp__scukv)
            context.nrt.incref(builder, arr_typ, nsbri__ner)
        npyuz__get = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=yppn__lrorx)
        payload_type = DataFramePayloadType(df_typ)
        ddxwr__qmoyw = context.nrt.meminfo_data(builder, npyuz__get.meminfo)
        rnsvb__ecmm = context.get_value_type(payload_type).as_pointer()
        ddxwr__qmoyw = builder.bitcast(ddxwr__qmoyw, rnsvb__ecmm)
        builder.store(rmi__yfh._getvalue(), ddxwr__qmoyw)
        return impl_ret_borrowed(context, builder, df_typ, yppn__lrorx)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        xam__fnq = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        xsxg__aezl = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=xam__fnq)
        gpevk__jhj = get_dataframe_payload(context, builder, df_typ, xam__fnq)
        npyuz__get = construct_dataframe(context, builder, signature.
            return_type, gpevk__jhj.data, index_val, xsxg__aezl.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), gpevk__jhj.data)
        return npyuz__get
    vaza__xiac = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(vaza__xiac, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    eamgq__lgc = len(df_type.columns)
    bnxyz__iqo = eamgq__lgc
    gvm__xlwo = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    iahd__bhg = col_name not in df_type.columns
    lxcp__scukv = eamgq__lgc
    if iahd__bhg:
        gvm__xlwo += arr_type,
        column_names += col_name,
        bnxyz__iqo += 1
    else:
        lxcp__scukv = df_type.columns.index(col_name)
        gvm__xlwo = tuple(arr_type if i == lxcp__scukv else gvm__xlwo[i] for
            i in range(eamgq__lgc))

    def codegen(context, builder, signature, args):
        yppn__lrorx, dhwkv__eje, nsbri__ner = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, yppn__lrorx)
        gvk__crzzr = cgutils.create_struct_proxy(df_type)(context, builder,
            value=yppn__lrorx)
        if df_type.is_table_format:
            tja__qmprh = df_type.table_type
            olmiw__qto = builder.extract_value(in_dataframe_payload.data, 0)
            hmct__eyabk = TableType(gvm__xlwo)
            aocdk__nqo = set_table_data_codegen(context, builder,
                tja__qmprh, olmiw__qto, hmct__eyabk, arr_type, nsbri__ner,
                lxcp__scukv, iahd__bhg)
            data_tup = context.make_tuple(builder, types.Tuple([hmct__eyabk
                ]), [aocdk__nqo])
        else:
            hqfn__rfmo = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != lxcp__scukv else nsbri__ner) for i in range(
                eamgq__lgc)]
            if iahd__bhg:
                hqfn__rfmo.append(nsbri__ner)
            for dewa__rgjqk, zsqdh__rfx in zip(hqfn__rfmo, gvm__xlwo):
                context.nrt.incref(builder, zsqdh__rfx, dewa__rgjqk)
            data_tup = context.make_tuple(builder, types.Tuple(gvm__xlwo),
                hqfn__rfmo)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        tvgv__apibq = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, gvk__crzzr.parent, None)
        if not iahd__bhg and arr_type == df_type.data[lxcp__scukv]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            ddxwr__qmoyw = context.nrt.meminfo_data(builder, gvk__crzzr.meminfo
                )
            rnsvb__ecmm = context.get_value_type(payload_type).as_pointer()
            ddxwr__qmoyw = builder.bitcast(ddxwr__qmoyw, rnsvb__ecmm)
            fujo__efrso = get_dataframe_payload(context, builder, df_type,
                tvgv__apibq)
            builder.store(fujo__efrso._getvalue(), ddxwr__qmoyw)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, hmct__eyabk, builder.
                    extract_value(data_tup, 0))
            else:
                for dewa__rgjqk, zsqdh__rfx in zip(hqfn__rfmo, gvm__xlwo):
                    context.nrt.incref(builder, zsqdh__rfx, dewa__rgjqk)
        has_parent = cgutils.is_not_null(builder, gvk__crzzr.parent)
        with builder.if_then(has_parent):
            jlahf__uzb = context.get_python_api(builder)
            gbeo__clmqi = jlahf__uzb.gil_ensure()
            bzzw__qwam = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, nsbri__ner)
            lxof__zun = numba.core.pythonapi._BoxContext(context, builder,
                jlahf__uzb, bzzw__qwam)
            lwl__ybii = lxof__zun.pyapi.from_native_value(arr_type,
                nsbri__ner, lxof__zun.env_manager)
            if isinstance(col_name, str):
                gby__clu = context.insert_const_string(builder.module, col_name
                    )
                ljt__ygqsf = jlahf__uzb.string_from_string(gby__clu)
            else:
                assert isinstance(col_name, int)
                ljt__ygqsf = jlahf__uzb.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            jlahf__uzb.object_setitem(gvk__crzzr.parent, ljt__ygqsf, lwl__ybii)
            jlahf__uzb.decref(lwl__ybii)
            jlahf__uzb.decref(ljt__ygqsf)
            jlahf__uzb.gil_release(gbeo__clmqi)
        return tvgv__apibq
    vaza__xiac = DataFrameType(gvm__xlwo, index_typ, column_names, df_type.
        dist, df_type.is_table_format)
    sig = signature(vaza__xiac, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    eamgq__lgc = len(pyval.columns)
    hqfn__rfmo = []
    for i in range(eamgq__lgc):
        zjn__vaax = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            lwl__ybii = zjn__vaax.array
        else:
            lwl__ybii = zjn__vaax.values
        hqfn__rfmo.append(lwl__ybii)
    hqfn__rfmo = tuple(hqfn__rfmo)
    if df_type.is_table_format:
        ohxon__ukvg = context.get_constant_generic(builder, df_type.
            table_type, Table(hqfn__rfmo))
        data_tup = lir.Constant.literal_struct([ohxon__ukvg])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], lmfm__mcpy) for 
            i, lmfm__mcpy in enumerate(hqfn__rfmo)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    ptq__fqhvu = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, ptq__fqhvu])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    pih__ijvdd = context.get_constant(types.int64, -1)
    ltep__xtk = context.get_constant_null(types.voidptr)
    grj__hyfdr = lir.Constant.literal_struct([pih__ijvdd, ltep__xtk,
        ltep__xtk, payload, pih__ijvdd])
    grj__hyfdr = cgutils.global_constant(builder, '.const.meminfo', grj__hyfdr
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([grj__hyfdr, ptq__fqhvu])


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
        kpk__gcbzk = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        kpk__gcbzk = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, kpk__gcbzk)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        ofq__ppblh = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                ofq__ppblh)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), ofq__ppblh)
    elif not fromty.is_table_format and toty.is_table_format:
        ofq__ppblh = _cast_df_data_to_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        ofq__ppblh = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        ofq__ppblh = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        ofq__ppblh = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, ofq__ppblh,
        kpk__gcbzk, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    deaoa__dwpxe = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        bki__ngu = get_index_data_arr_types(toty.index)[0]
        zsovf__uvaz = bodo.utils.transform.get_type_alloc_counts(bki__ngu) - 1
        wgy__pop = ', '.join('0' for dhwkv__eje in range(zsovf__uvaz))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(wgy__pop, ', ' if zsovf__uvaz == 1 else ''))
        deaoa__dwpxe['index_arr_type'] = bki__ngu
    ljzst__zmr = []
    for i, arr_typ in enumerate(toty.data):
        zsovf__uvaz = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        wgy__pop = ', '.join('0' for dhwkv__eje in range(zsovf__uvaz))
        fxcun__rsc = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, wgy__pop, ', ' if zsovf__uvaz == 1 else ''))
        ljzst__zmr.append(fxcun__rsc)
        deaoa__dwpxe[f'arr_type{i}'] = arr_typ
    ljzst__zmr = ', '.join(ljzst__zmr)
    zdr__efu = 'def impl():\n'
    pdn__gdcn = bodo.hiframes.dataframe_impl._gen_init_df(zdr__efu, toty.
        columns, ljzst__zmr, index, deaoa__dwpxe)
    df = context.compile_internal(builder, pdn__gdcn, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    xur__icqq = toty.table_type
    ohxon__ukvg = cgutils.create_struct_proxy(xur__icqq)(context, builder)
    ohxon__ukvg.parent = in_dataframe_payload.parent
    for ogv__iluaf, rqg__sdvzm in xur__icqq.type_to_blk.items():
        uttp__hic = context.get_constant(types.int64, len(xur__icqq.
            block_to_arr_ind[rqg__sdvzm]))
        dhwkv__eje, zjonn__zsa = ListInstance.allocate_ex(context, builder,
            types.List(ogv__iluaf), uttp__hic)
        zjonn__zsa.size = uttp__hic
        setattr(ohxon__ukvg, f'block_{rqg__sdvzm}', zjonn__zsa.value)
    for i, ogv__iluaf in enumerate(fromty.data):
        vix__rxym = toty.data[i]
        if ogv__iluaf != vix__rxym:
            saig__isesg = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*saig__isesg)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        jph__qgz = builder.extract_value(in_dataframe_payload.data, i)
        if ogv__iluaf != vix__rxym:
            pxsou__mtvb = context.cast(builder, jph__qgz, ogv__iluaf, vix__rxym
                )
            xgivw__wabq = False
        else:
            pxsou__mtvb = jph__qgz
            xgivw__wabq = True
        rqg__sdvzm = xur__icqq.type_to_blk[ogv__iluaf]
        vfbl__untj = getattr(ohxon__ukvg, f'block_{rqg__sdvzm}')
        mnmm__hmz = ListInstance(context, builder, types.List(ogv__iluaf),
            vfbl__untj)
        wzse__gjlq = context.get_constant(types.int64, xur__icqq.
            block_offsets[i])
        mnmm__hmz.setitem(wzse__gjlq, pxsou__mtvb, xgivw__wabq)
    data_tup = context.make_tuple(builder, types.Tuple([xur__icqq]), [
        ohxon__ukvg._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    hqfn__rfmo = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            saig__isesg = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*saig__isesg)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            jph__qgz = builder.extract_value(in_dataframe_payload.data, i)
            pxsou__mtvb = context.cast(builder, jph__qgz, fromty.data[i],
                toty.data[i])
            xgivw__wabq = False
        else:
            pxsou__mtvb = builder.extract_value(in_dataframe_payload.data, i)
            xgivw__wabq = True
        if xgivw__wabq:
            context.nrt.incref(builder, toty.data[i], pxsou__mtvb)
        hqfn__rfmo.append(pxsou__mtvb)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), hqfn__rfmo)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    tja__qmprh = fromty.table_type
    olmiw__qto = cgutils.create_struct_proxy(tja__qmprh)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    hmct__eyabk = toty.table_type
    aocdk__nqo = cgutils.create_struct_proxy(hmct__eyabk)(context, builder)
    aocdk__nqo.parent = in_dataframe_payload.parent
    for ogv__iluaf, rqg__sdvzm in hmct__eyabk.type_to_blk.items():
        uttp__hic = context.get_constant(types.int64, len(hmct__eyabk.
            block_to_arr_ind[rqg__sdvzm]))
        dhwkv__eje, zjonn__zsa = ListInstance.allocate_ex(context, builder,
            types.List(ogv__iluaf), uttp__hic)
        zjonn__zsa.size = uttp__hic
        setattr(aocdk__nqo, f'block_{rqg__sdvzm}', zjonn__zsa.value)
    for i in range(len(fromty.data)):
        yocyx__okqa = fromty.data[i]
        vix__rxym = toty.data[i]
        if yocyx__okqa != vix__rxym:
            saig__isesg = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*saig__isesg)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        peafg__oynah = tja__qmprh.type_to_blk[yocyx__okqa]
        gdhzv__jpwzg = getattr(olmiw__qto, f'block_{peafg__oynah}')
        wdzmo__zptb = ListInstance(context, builder, types.List(yocyx__okqa
            ), gdhzv__jpwzg)
        rcpm__ifr = context.get_constant(types.int64, tja__qmprh.
            block_offsets[i])
        jph__qgz = wdzmo__zptb.getitem(rcpm__ifr)
        if yocyx__okqa != vix__rxym:
            pxsou__mtvb = context.cast(builder, jph__qgz, yocyx__okqa,
                vix__rxym)
            xgivw__wabq = False
        else:
            pxsou__mtvb = jph__qgz
            xgivw__wabq = True
        bjcej__qddn = hmct__eyabk.type_to_blk[ogv__iluaf]
        zjonn__zsa = getattr(aocdk__nqo, f'block_{bjcej__qddn}')
        suso__nkjgw = ListInstance(context, builder, types.List(vix__rxym),
            zjonn__zsa)
        duqum__xhhhw = context.get_constant(types.int64, hmct__eyabk.
            block_offsets[i])
        suso__nkjgw.setitem(duqum__xhhhw, pxsou__mtvb, xgivw__wabq)
    data_tup = context.make_tuple(builder, types.Tuple([hmct__eyabk]), [
        aocdk__nqo._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    xur__icqq = fromty.table_type
    ohxon__ukvg = cgutils.create_struct_proxy(xur__icqq)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    hqfn__rfmo = []
    for i, ogv__iluaf in enumerate(toty.data):
        yocyx__okqa = fromty.data[i]
        if ogv__iluaf != yocyx__okqa:
            saig__isesg = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*saig__isesg)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        rqg__sdvzm = xur__icqq.type_to_blk[ogv__iluaf]
        vfbl__untj = getattr(ohxon__ukvg, f'block_{rqg__sdvzm}')
        mnmm__hmz = ListInstance(context, builder, types.List(ogv__iluaf),
            vfbl__untj)
        wzse__gjlq = context.get_constant(types.int64, xur__icqq.
            block_offsets[i])
        jph__qgz = mnmm__hmz.getitem(wzse__gjlq)
        if ogv__iluaf != yocyx__okqa:
            pxsou__mtvb = context.cast(builder, jph__qgz, yocyx__okqa,
                ogv__iluaf)
            xgivw__wabq = False
        else:
            pxsou__mtvb = jph__qgz
            xgivw__wabq = True
        if xgivw__wabq:
            context.nrt.incref(builder, ogv__iluaf, pxsou__mtvb)
        hqfn__rfmo.append(pxsou__mtvb)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), hqfn__rfmo)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    ead__fwu, ljzst__zmr, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    wny__lotqe = ColNamesMetaType(tuple(ead__fwu))
    zdr__efu = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    zdr__efu += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(ljzst__zmr, index_arg, wny__lotqe))
    iwwl__kzdi = {}
    exec(zdr__efu, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': wny__lotqe}, iwwl__kzdi)
    osu__tvv = iwwl__kzdi['_init_df']
    return osu__tvv


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    vaza__xiac = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(vaza__xiac, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    vaza__xiac = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(vaza__xiac, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    rjr__yhns = ''
    if not is_overload_none(dtype):
        rjr__yhns = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        eamgq__lgc = (len(data.types) - 1) // 2
        ehcy__fpup = [ogv__iluaf.literal_value for ogv__iluaf in data.types
            [1:eamgq__lgc + 1]]
        data_val_types = dict(zip(ehcy__fpup, data.types[eamgq__lgc + 1:]))
        hqfn__rfmo = ['data[{}]'.format(i) for i in range(eamgq__lgc + 1, 2 *
            eamgq__lgc + 1)]
        data_dict = dict(zip(ehcy__fpup, hqfn__rfmo))
        if is_overload_none(index):
            for i, ogv__iluaf in enumerate(data.types[eamgq__lgc + 1:]):
                if isinstance(ogv__iluaf, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(eamgq__lgc + 1 + i))
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
        ssrht__ekal = '.copy()' if copy else ''
        yujab__lxe = get_overload_const_list(columns)
        eamgq__lgc = len(yujab__lxe)
        data_val_types = {lxof__zun: data.copy(ndim=1) for lxof__zun in
            yujab__lxe}
        hqfn__rfmo = ['data[:,{}]{}'.format(i, ssrht__ekal) for i in range(
            eamgq__lgc)]
        data_dict = dict(zip(yujab__lxe, hqfn__rfmo))
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
    ljzst__zmr = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[lxof__zun], df_len, rjr__yhns) for lxof__zun in
        col_names))
    if len(col_names) == 0:
        ljzst__zmr = '()'
    return col_names, ljzst__zmr, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for lxof__zun in col_names:
        if lxof__zun in data_dict and is_iterable_type(data_val_types[
            lxof__zun]):
            df_len = 'len({})'.format(data_dict[lxof__zun])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(lxof__zun in data_dict for lxof__zun in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    gmhe__pvo = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for lxof__zun in col_names:
        if lxof__zun not in data_dict:
            data_dict[lxof__zun] = gmhe__pvo


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
            ogv__iluaf = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(ogv__iluaf)
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
        lhn__zpve = idx.literal_value
        if isinstance(lhn__zpve, int):
            mpr__vpiat = tup.types[lhn__zpve]
        elif isinstance(lhn__zpve, slice):
            mpr__vpiat = types.BaseTuple.from_types(tup.types[lhn__zpve])
        return signature(mpr__vpiat, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    caz__zopoi, idx = sig.args
    idx = idx.literal_value
    tup, dhwkv__eje = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(caz__zopoi)
        if not 0 <= idx < len(caz__zopoi):
            raise IndexError('cannot index at %d in %s' % (idx, caz__zopoi))
        qten__hlefj = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        fqxll__gcrw = cgutils.unpack_tuple(builder, tup)[idx]
        qten__hlefj = context.make_tuple(builder, sig.return_type, fqxll__gcrw)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, qten__hlefj)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, qflvc__fkroc, suffix_x,
            suffix_y, is_join, indicator, dhwkv__eje, dhwkv__eje) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        wriv__gthoj = {lxof__zun: i for i, lxof__zun in enumerate(left_on)}
        vgv__cna = {lxof__zun: i for i, lxof__zun in enumerate(right_on)}
        cvxuv__iseqn = set(left_on) & set(right_on)
        lge__vgf = set(left_df.columns) & set(right_df.columns)
        bhz__edz = lge__vgf - cvxuv__iseqn
        exwaw__fglx = '$_bodo_index_' in left_on
        rrh__cfyob = '$_bodo_index_' in right_on
        how = get_overload_const_str(qflvc__fkroc)
        loyeu__csick = how in {'left', 'outer'}
        mtf__fatlo = how in {'right', 'outer'}
        columns = []
        data = []
        if exwaw__fglx:
            lmrpx__wuda = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            lmrpx__wuda = left_df.data[left_df.column_index[left_on[0]]]
        if rrh__cfyob:
            oknk__zlzy = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            oknk__zlzy = right_df.data[right_df.column_index[right_on[0]]]
        if exwaw__fglx and not rrh__cfyob and not is_join.literal_value:
            bedz__lnkr = right_on[0]
            if bedz__lnkr in left_df.column_index:
                columns.append(bedz__lnkr)
                if (oknk__zlzy == bodo.dict_str_arr_type and lmrpx__wuda ==
                    bodo.string_array_type):
                    wpzq__flt = bodo.string_array_type
                else:
                    wpzq__flt = oknk__zlzy
                data.append(wpzq__flt)
        if rrh__cfyob and not exwaw__fglx and not is_join.literal_value:
            dgj__yac = left_on[0]
            if dgj__yac in right_df.column_index:
                columns.append(dgj__yac)
                if (lmrpx__wuda == bodo.dict_str_arr_type and oknk__zlzy ==
                    bodo.string_array_type):
                    wpzq__flt = bodo.string_array_type
                else:
                    wpzq__flt = lmrpx__wuda
                data.append(wpzq__flt)
        for yocyx__okqa, zjn__vaax in zip(left_df.data, left_df.columns):
            columns.append(str(zjn__vaax) + suffix_x.literal_value if 
                zjn__vaax in bhz__edz else zjn__vaax)
            if zjn__vaax in cvxuv__iseqn:
                if yocyx__okqa == bodo.dict_str_arr_type:
                    yocyx__okqa = right_df.data[right_df.column_index[
                        zjn__vaax]]
                data.append(yocyx__okqa)
            else:
                if (yocyx__okqa == bodo.dict_str_arr_type and zjn__vaax in
                    wriv__gthoj):
                    if rrh__cfyob:
                        yocyx__okqa = oknk__zlzy
                    else:
                        kah__ffq = wriv__gthoj[zjn__vaax]
                        ewjkb__svh = right_on[kah__ffq]
                        yocyx__okqa = right_df.data[right_df.column_index[
                            ewjkb__svh]]
                if mtf__fatlo:
                    yocyx__okqa = to_nullable_type(yocyx__okqa)
                data.append(yocyx__okqa)
        for yocyx__okqa, zjn__vaax in zip(right_df.data, right_df.columns):
            if zjn__vaax not in cvxuv__iseqn:
                columns.append(str(zjn__vaax) + suffix_y.literal_value if 
                    zjn__vaax in bhz__edz else zjn__vaax)
                if (yocyx__okqa == bodo.dict_str_arr_type and zjn__vaax in
                    vgv__cna):
                    if exwaw__fglx:
                        yocyx__okqa = lmrpx__wuda
                    else:
                        kah__ffq = vgv__cna[zjn__vaax]
                        ngaq__mkgv = left_on[kah__ffq]
                        yocyx__okqa = left_df.data[left_df.column_index[
                            ngaq__mkgv]]
                if loyeu__csick:
                    yocyx__okqa = to_nullable_type(yocyx__okqa)
                data.append(yocyx__okqa)
        entpp__nbofd = get_overload_const_bool(indicator)
        if entpp__nbofd:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        iea__umuuo = False
        if exwaw__fglx and rrh__cfyob and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            iea__umuuo = True
        elif exwaw__fglx and not rrh__cfyob:
            index_typ = right_df.index
            iea__umuuo = True
        elif rrh__cfyob and not exwaw__fglx:
            index_typ = left_df.index
            iea__umuuo = True
        if iea__umuuo and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        ctms__ltbb = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(ctms__ltbb, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    npyuz__get = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return npyuz__get._getvalue()


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
    ikfyf__auw = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    mtctb__hrthy = dict(join='outer', join_axes=None, keys=None, levels=
        None, names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', ikfyf__auw, mtctb__hrthy,
        package_name='pandas', module_name='General')
    zdr__efu = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        hsz__zkeax = 0
        ljzst__zmr = []
        names = []
        for i, axzz__vpt in enumerate(objs.types):
            assert isinstance(axzz__vpt, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(axzz__vpt, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(axzz__vpt
                , 'pandas.concat()')
            if isinstance(axzz__vpt, SeriesType):
                names.append(str(hsz__zkeax))
                hsz__zkeax += 1
                ljzst__zmr.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(axzz__vpt.columns)
                for khw__jtay in range(len(axzz__vpt.data)):
                    ljzst__zmr.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, khw__jtay))
        return bodo.hiframes.dataframe_impl._gen_init_df(zdr__efu, names,
            ', '.join(ljzst__zmr), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(ogv__iluaf, DataFrameType) for ogv__iluaf in
            objs.types)
        oovf__szjp = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            oovf__szjp.extend(df.columns)
        oovf__szjp = list(dict.fromkeys(oovf__szjp).keys())
        lxlan__gck = {}
        for hsz__zkeax, lxof__zun in enumerate(oovf__szjp):
            for i, df in enumerate(objs.types):
                if lxof__zun in df.column_index:
                    lxlan__gck[f'arr_typ{hsz__zkeax}'] = df.data[df.
                        column_index[lxof__zun]]
                    break
        assert len(lxlan__gck) == len(oovf__szjp)
        jes__uvjyv = []
        for hsz__zkeax, lxof__zun in enumerate(oovf__szjp):
            args = []
            for i, df in enumerate(objs.types):
                if lxof__zun in df.column_index:
                    lxcp__scukv = df.column_index[lxof__zun]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, lxcp__scukv))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, hsz__zkeax))
            zdr__efu += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'.
                format(hsz__zkeax, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(zdr__efu,
            oovf__szjp, ', '.join('A{}'.format(i) for i in range(len(
            oovf__szjp))), index, lxlan__gck)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(ogv__iluaf, SeriesType) for ogv__iluaf in
            objs.types)
        zdr__efu += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'.
            format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            zdr__efu += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            zdr__efu += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        zdr__efu += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        iwwl__kzdi = {}
        exec(zdr__efu, {'bodo': bodo, 'np': np, 'numba': numba}, iwwl__kzdi)
        return iwwl__kzdi['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for hsz__zkeax, lxof__zun in enumerate(df_type.columns):
            zdr__efu += '  arrs{} = []\n'.format(hsz__zkeax)
            zdr__efu += '  for i in range(len(objs)):\n'
            zdr__efu += '    df = objs[i]\n'
            zdr__efu += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(hsz__zkeax))
            zdr__efu += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(hsz__zkeax))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            zdr__efu += '  arrs_index = []\n'
            zdr__efu += '  for i in range(len(objs)):\n'
            zdr__efu += '    df = objs[i]\n'
            zdr__efu += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(zdr__efu, df_type.
            columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        zdr__efu += '  arrs = []\n'
        zdr__efu += '  for i in range(len(objs)):\n'
        zdr__efu += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        zdr__efu += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            zdr__efu += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            zdr__efu += '  arrs_index = []\n'
            zdr__efu += '  for i in range(len(objs)):\n'
            zdr__efu += '    S = objs[i]\n'
            zdr__efu += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            zdr__efu += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        zdr__efu += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        iwwl__kzdi = {}
        exec(zdr__efu, {'bodo': bodo, 'np': np, 'numba': numba}, iwwl__kzdi)
        return iwwl__kzdi['impl']
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
        vaza__xiac = df.copy(index=index, is_table_format=False)
        return signature(vaza__xiac, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    huv__zmxib = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return huv__zmxib._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    ikfyf__auw = dict(index=index, name=name)
    mtctb__hrthy = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', ikfyf__auw, mtctb__hrthy,
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
        lxlan__gck = (types.Array(types.int64, 1, 'C'),) + df.data
        bdjmv__mlct = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, lxlan__gck)
        return signature(bdjmv__mlct, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    huv__zmxib = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return huv__zmxib._getvalue()


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
    huv__zmxib = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return huv__zmxib._getvalue()


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
    huv__zmxib = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return huv__zmxib._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    fyry__xreoh = get_overload_const_bool(check_duplicates)
    qfvkk__pfgev = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    toyoc__cxne = len(value_names) > 1
    vwjm__ilkzz = None
    ums__piac = None
    gundr__fvueu = None
    agcd__xmf = None
    pcbtf__tec = isinstance(values_tup, types.UniTuple)
    if pcbtf__tec:
        ogax__volu = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        ogax__volu = [to_str_arr_if_dict_array(to_nullable_type(zsqdh__rfx)
            ) for zsqdh__rfx in values_tup]
    zdr__efu = 'def impl(\n'
    zdr__efu += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    zdr__efu += '):\n'
    zdr__efu += '    if parallel:\n'
    pri__xofbx = ', '.join([f'array_to_info(index_tup[{i}])' for i in range
        (len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    zdr__efu += f'        info_list = [{pri__xofbx}]\n'
    zdr__efu += '        cpp_table = arr_info_list_to_table(info_list)\n'
    zdr__efu += (
        f'        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)\n'
        )
    ruob__ocnw = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    icrsv__rvbe = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    bzalu__tkfgh = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    zdr__efu += f'        index_tup = ({ruob__ocnw},)\n'
    zdr__efu += f'        columns_tup = ({icrsv__rvbe},)\n'
    zdr__efu += f'        values_tup = ({bzalu__tkfgh},)\n'
    zdr__efu += '        delete_table(cpp_table)\n'
    zdr__efu += '        delete_table(out_cpp_table)\n'
    zdr__efu += '    columns_arr = columns_tup[0]\n'
    if pcbtf__tec:
        zdr__efu += '    values_arrs = [arr for arr in values_tup]\n'
    hbn__ekfv = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    zdr__efu += f'    new_index_tup = ({hbn__ekfv},)\n'
    zdr__efu += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    zdr__efu += '        new_index_tup\n'
    zdr__efu += '    )\n'
    zdr__efu += '    n_rows = len(unique_index_arr_tup[0])\n'
    zdr__efu += '    num_values_arrays = len(values_tup)\n'
    zdr__efu += '    n_unique_pivots = len(pivot_values)\n'
    if pcbtf__tec:
        zdr__efu += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        zdr__efu += '    n_cols = n_unique_pivots\n'
    zdr__efu += '    col_map = {}\n'
    zdr__efu += '    for i in range(n_unique_pivots):\n'
    zdr__efu += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    zdr__efu += '            raise ValueError(\n'
    zdr__efu += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    zdr__efu += '            )\n'
    zdr__efu += '        col_map[pivot_values[i]] = i\n'
    smq__msc = False
    for i, qis__qjpx in enumerate(ogax__volu):
        if is_str_arr_type(qis__qjpx):
            smq__msc = True
            zdr__efu += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            zdr__efu += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if smq__msc:
        if fyry__xreoh:
            zdr__efu += '    nbytes = (n_rows + 7) >> 3\n'
            zdr__efu += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        zdr__efu += '    for i in range(len(columns_arr)):\n'
        zdr__efu += '        col_name = columns_arr[i]\n'
        zdr__efu += '        pivot_idx = col_map[col_name]\n'
        zdr__efu += '        row_idx = row_vector[i]\n'
        if fyry__xreoh:
            zdr__efu += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            zdr__efu += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            zdr__efu += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            zdr__efu += '        else:\n'
            zdr__efu += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if pcbtf__tec:
            zdr__efu += '        for j in range(num_values_arrays):\n'
            zdr__efu += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            zdr__efu += '            len_arr = len_arrs_0[col_idx]\n'
            zdr__efu += '            values_arr = values_arrs[j]\n'
            zdr__efu += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            zdr__efu += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            zdr__efu += '                len_arr[row_idx] = str_val_len\n'
            zdr__efu += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, qis__qjpx in enumerate(ogax__volu):
                if is_str_arr_type(qis__qjpx):
                    zdr__efu += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    zdr__efu += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    zdr__efu += (
                        f'            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}\n'
                        )
                    zdr__efu += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, qis__qjpx in enumerate(ogax__volu):
        if is_str_arr_type(qis__qjpx):
            zdr__efu += f'    data_arrs_{i} = [\n'
            zdr__efu += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            zdr__efu += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            zdr__efu += '        )\n'
            zdr__efu += '        for i in range(n_cols)\n'
            zdr__efu += '    ]\n'
        else:
            zdr__efu += f'    data_arrs_{i} = [\n'
            zdr__efu += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            zdr__efu += '        for _ in range(n_cols)\n'
            zdr__efu += '    ]\n'
    if not smq__msc and fyry__xreoh:
        zdr__efu += '    nbytes = (n_rows + 7) >> 3\n'
        zdr__efu += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    zdr__efu += '    for i in range(len(columns_arr)):\n'
    zdr__efu += '        col_name = columns_arr[i]\n'
    zdr__efu += '        pivot_idx = col_map[col_name]\n'
    zdr__efu += '        row_idx = row_vector[i]\n'
    if not smq__msc and fyry__xreoh:
        zdr__efu += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        zdr__efu += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        zdr__efu += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        zdr__efu += '        else:\n'
        zdr__efu += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if pcbtf__tec:
        zdr__efu += '        for j in range(num_values_arrays):\n'
        zdr__efu += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        zdr__efu += '            col_arr = data_arrs_0[col_idx]\n'
        zdr__efu += '            values_arr = values_arrs[j]\n'
        zdr__efu += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        zdr__efu += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        zdr__efu += '            else:\n'
        zdr__efu += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, qis__qjpx in enumerate(ogax__volu):
            zdr__efu += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            zdr__efu += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            zdr__efu += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            zdr__efu += f'        else:\n'
            zdr__efu += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        zdr__efu += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        vwjm__ilkzz = index_names.meta[0]
    else:
        zdr__efu += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        vwjm__ilkzz = tuple(index_names.meta)
    if not qfvkk__pfgev:
        gundr__fvueu = columns_name.meta[0]
        if toyoc__cxne:
            zdr__efu += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            ums__piac = value_names.meta
            if all(isinstance(lxof__zun, str) for lxof__zun in ums__piac):
                ums__piac = pd.array(ums__piac, 'string')
            elif all(isinstance(lxof__zun, int) for lxof__zun in ums__piac):
                ums__piac = np.array(ums__piac, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(ums__piac.dtype, pd.StringDtype):
                zdr__efu += '    total_chars = 0\n'
                zdr__efu += f'    for i in range({len(value_names)}):\n'
                zdr__efu += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                zdr__efu += '        total_chars += value_name_str_len\n'
                zdr__efu += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                zdr__efu += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                zdr__efu += '    total_chars = 0\n'
                zdr__efu += '    for i in range(len(pivot_values)):\n'
                zdr__efu += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                zdr__efu += '        total_chars += pivot_val_str_len\n'
                zdr__efu += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                zdr__efu += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            zdr__efu += f'    for i in range({len(value_names)}):\n'
            zdr__efu += '        for j in range(len(pivot_values)):\n'
            zdr__efu += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            zdr__efu += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            zdr__efu += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            zdr__efu += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    xur__icqq = None
    if qfvkk__pfgev:
        if toyoc__cxne:
            voaa__ryrkq = []
            for rbk__cyaj in _constant_pivot_values.meta:
                for onzql__baj in value_names.meta:
                    voaa__ryrkq.append((rbk__cyaj, onzql__baj))
            column_names = tuple(voaa__ryrkq)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        agcd__xmf = ColNamesMetaType(column_names)
        lgi__qfcq = []
        for zsqdh__rfx in ogax__volu:
            lgi__qfcq.extend([zsqdh__rfx] * len(_constant_pivot_values))
        wfb__hjbi = tuple(lgi__qfcq)
        xur__icqq = TableType(wfb__hjbi)
        zdr__efu += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        zdr__efu += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, zsqdh__rfx in enumerate(ogax__volu):
            zdr__efu += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {xur__icqq.type_to_blk[zsqdh__rfx]})
"""
        zdr__efu += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        zdr__efu += '        (table,), index, columns_typ\n'
        zdr__efu += '    )\n'
    else:
        dvxij__pjo = ', '.join(f'data_arrs_{i}' for i in range(len(ogax__volu))
            )
        zdr__efu += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({dvxij__pjo},), n_rows)
"""
        zdr__efu += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        zdr__efu += '        (table,), index, column_index\n'
        zdr__efu += '    )\n'
    iwwl__kzdi = {}
    ybhz__bfl = {f'data_arr_typ_{i}': qis__qjpx for i, qis__qjpx in
        enumerate(ogax__volu)}
    ketf__phuy = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        xur__icqq, 'columns_typ': agcd__xmf, 'index_names_lit': vwjm__ilkzz,
        'value_names_lit': ums__piac, 'columns_name_lit': gundr__fvueu, **
        ybhz__bfl}
    exec(zdr__efu, ketf__phuy, iwwl__kzdi)
    impl = iwwl__kzdi['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    zzx__pqwmp = {}
    zzx__pqwmp['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, gao__esn in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        rjthz__oyvip = None
        if isinstance(gao__esn, bodo.DatetimeArrayType):
            fkq__vrycu = 'datetimetz'
            fiivt__pmj = 'datetime64[ns]'
            if isinstance(gao__esn.tz, int):
                alxbx__qgz = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(gao__esn.tz))
            else:
                alxbx__qgz = pd.DatetimeTZDtype(tz=gao__esn.tz).tz
            rjthz__oyvip = {'timezone': pa.lib.tzinfo_to_string(alxbx__qgz)}
        elif isinstance(gao__esn, types.Array) or gao__esn == boolean_array:
            fkq__vrycu = fiivt__pmj = gao__esn.dtype.name
            if fiivt__pmj.startswith('datetime'):
                fkq__vrycu = 'datetime'
        elif is_str_arr_type(gao__esn):
            fkq__vrycu = 'unicode'
            fiivt__pmj = 'object'
        elif gao__esn == binary_array_type:
            fkq__vrycu = 'bytes'
            fiivt__pmj = 'object'
        elif isinstance(gao__esn, DecimalArrayType):
            fkq__vrycu = fiivt__pmj = 'object'
        elif isinstance(gao__esn, IntegerArrayType):
            wkdop__iii = gao__esn.dtype.name
            if wkdop__iii.startswith('int'):
                fkq__vrycu = 'Int' + wkdop__iii[3:]
            elif wkdop__iii.startswith('uint'):
                fkq__vrycu = 'UInt' + wkdop__iii[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, gao__esn))
            fiivt__pmj = gao__esn.dtype.name
        elif gao__esn == datetime_date_array_type:
            fkq__vrycu = 'datetime'
            fiivt__pmj = 'object'
        elif isinstance(gao__esn, (StructArrayType, ArrayItemArrayType)):
            fkq__vrycu = 'object'
            fiivt__pmj = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, gao__esn))
        luvo__xdkpf = {'name': col_name, 'field_name': col_name,
            'pandas_type': fkq__vrycu, 'numpy_type': fiivt__pmj, 'metadata':
            rjthz__oyvip}
        zzx__pqwmp['columns'].append(luvo__xdkpf)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            zwsfx__ubcb = '__index_level_0__'
            cmrh__fbwe = None
        else:
            zwsfx__ubcb = '%s'
            cmrh__fbwe = '%s'
        zzx__pqwmp['index_columns'] = [zwsfx__ubcb]
        zzx__pqwmp['columns'].append({'name': cmrh__fbwe, 'field_name':
            zwsfx__ubcb, 'pandas_type': index.pandas_type_name,
            'numpy_type': index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        zzx__pqwmp['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        zzx__pqwmp['index_columns'] = []
    zzx__pqwmp['pandas_version'] = pd.__version__
    return zzx__pqwmp


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
        elwup__hghe = []
        for sltsm__cmwvh in partition_cols:
            try:
                idx = df.columns.index(sltsm__cmwvh)
            except ValueError as sxzsg__mfivy:
                raise BodoError(
                    f'Partition column {sltsm__cmwvh} is not in dataframe')
            elwup__hghe.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    dafh__flvc = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    ydd__shyxy = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not dafh__flvc)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not dafh__flvc or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and dafh__flvc and not is_overload_true(_is_parallel)
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
        xkn__segmq = df.runtime_data_types
        npuet__dyf = len(xkn__segmq)
        rjthz__oyvip = gen_pandas_parquet_metadata([''] * npuet__dyf,
            xkn__segmq, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        vsb__udyyp = rjthz__oyvip['columns'][:npuet__dyf]
        rjthz__oyvip['columns'] = rjthz__oyvip['columns'][npuet__dyf:]
        vsb__udyyp = [json.dumps(gpm__unyl).replace('""', '{0}') for
            gpm__unyl in vsb__udyyp]
        vqoiy__caagg = json.dumps(rjthz__oyvip)
        flrru__tyw = '"columns": ['
        mhds__nyaqi = vqoiy__caagg.find(flrru__tyw)
        if mhds__nyaqi == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        lfd__pgaj = mhds__nyaqi + len(flrru__tyw)
        oxr__xxdbc = vqoiy__caagg[:lfd__pgaj]
        vqoiy__caagg = vqoiy__caagg[lfd__pgaj:]
        fgni__kgaeg = len(rjthz__oyvip['columns'])
    else:
        vqoiy__caagg = json.dumps(gen_pandas_parquet_metadata(df.columns,
            df.data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and dafh__flvc:
        vqoiy__caagg = vqoiy__caagg.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            vqoiy__caagg = vqoiy__caagg.replace('"%s"', '%s')
    if not df.is_table_format:
        ljzst__zmr = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    zdr__efu = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _is_parallel=False):
"""
    if df.is_table_format:
        zdr__efu += '    py_table = get_dataframe_table(df)\n'
        zdr__efu += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        zdr__efu += '    info_list = [{}]\n'.format(ljzst__zmr)
        zdr__efu += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        zdr__efu += '    columns_index = get_dataframe_column_names(df)\n'
        zdr__efu += '    names_arr = index_to_array(columns_index)\n'
        zdr__efu += '    col_names = array_to_info(names_arr)\n'
    else:
        zdr__efu += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and ydd__shyxy:
        zdr__efu += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        shzit__cor = True
    else:
        zdr__efu += '    index_col = array_to_info(np.empty(0))\n'
        shzit__cor = False
    if df.has_runtime_cols:
        zdr__efu += '    columns_lst = []\n'
        zdr__efu += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            zdr__efu += f'    for _ in range(len(py_table.block_{i})):\n'
            zdr__efu += f"""        columns_lst.append({vsb__udyyp[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            zdr__efu += '        num_cols += 1\n'
        if fgni__kgaeg:
            zdr__efu += "    columns_lst.append('')\n"
        zdr__efu += '    columns_str = ", ".join(columns_lst)\n'
        zdr__efu += ('    metadata = """' + oxr__xxdbc +
            '""" + columns_str + """' + vqoiy__caagg + '"""\n')
    else:
        zdr__efu += '    metadata = """' + vqoiy__caagg + '"""\n'
    zdr__efu += '    if compression is None:\n'
    zdr__efu += "        compression = 'none'\n"
    zdr__efu += '    if df.index.name is not None:\n'
    zdr__efu += '        name_ptr = df.index.name\n'
    zdr__efu += '    else:\n'
    zdr__efu += "        name_ptr = 'null'\n"
    zdr__efu += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    gimob__adbrr = None
    if partition_cols:
        gimob__adbrr = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        brfo__pnlx = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in elwup__hghe)
        if brfo__pnlx:
            zdr__efu += '    cat_info_list = [{}]\n'.format(brfo__pnlx)
            zdr__efu += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            zdr__efu += '    cat_table = table\n'
        zdr__efu += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        zdr__efu += (
            f'    part_cols_idxs = np.array({elwup__hghe}, dtype=np.int32)\n')
        zdr__efu += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        zdr__efu += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        zdr__efu += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        zdr__efu += (
            '                            unicode_to_utf8(compression),\n')
        zdr__efu += '                            _is_parallel,\n'
        zdr__efu += (
            '                            unicode_to_utf8(bucket_region),\n')
        zdr__efu += '                            row_group_size)\n'
        zdr__efu += '    delete_table_decref_arrays(table)\n'
        zdr__efu += '    delete_info_decref_array(index_col)\n'
        zdr__efu += '    delete_info_decref_array(col_names_no_partitions)\n'
        zdr__efu += '    delete_info_decref_array(col_names)\n'
        if brfo__pnlx:
            zdr__efu += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        zdr__efu += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        zdr__efu += (
            '                            table, col_names, index_col,\n')
        zdr__efu += '                            ' + str(shzit__cor) + ',\n'
        zdr__efu += '                            unicode_to_utf8(metadata),\n'
        zdr__efu += (
            '                            unicode_to_utf8(compression),\n')
        zdr__efu += (
            '                            _is_parallel, 1, df.index.start,\n')
        zdr__efu += (
            '                            df.index.stop, df.index.step,\n')
        zdr__efu += '                            unicode_to_utf8(name_ptr),\n'
        zdr__efu += (
            '                            unicode_to_utf8(bucket_region),\n')
        zdr__efu += '                            row_group_size)\n'
        zdr__efu += '    delete_table_decref_arrays(table)\n'
        zdr__efu += '    delete_info_decref_array(index_col)\n'
        zdr__efu += '    delete_info_decref_array(col_names)\n'
    else:
        zdr__efu += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        zdr__efu += (
            '                            table, col_names, index_col,\n')
        zdr__efu += '                            ' + str(shzit__cor) + ',\n'
        zdr__efu += '                            unicode_to_utf8(metadata),\n'
        zdr__efu += (
            '                            unicode_to_utf8(compression),\n')
        zdr__efu += '                            _is_parallel, 0, 0, 0, 0,\n'
        zdr__efu += '                            unicode_to_utf8(name_ptr),\n'
        zdr__efu += (
            '                            unicode_to_utf8(bucket_region),\n')
        zdr__efu += '                            row_group_size)\n'
        zdr__efu += '    delete_table_decref_arrays(table)\n'
        zdr__efu += '    delete_info_decref_array(index_col)\n'
        zdr__efu += '    delete_info_decref_array(col_names)\n'
    iwwl__kzdi = {}
    if df.has_runtime_cols:
        clq__wsnn = None
    else:
        for zjn__vaax in df.columns:
            if not isinstance(zjn__vaax, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        clq__wsnn = pd.array(df.columns)
    exec(zdr__efu, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': clq__wsnn,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': gimob__adbrr,
        'get_dataframe_column_names': get_dataframe_column_names,
        'fix_arr_dtype': fix_arr_dtype, 'decode_if_dict_array':
        decode_if_dict_array, 'decode_if_dict_table': decode_if_dict_table},
        iwwl__kzdi)
    yee__cimf = iwwl__kzdi['df_to_parquet']
    return yee__cimf


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    ffq__wnbx = 'all_ok'
    tawmg__rxqg, rzfte__tjmk = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        evd__hfnz = 100
        if chunksize is None:
            jadpu__modne = evd__hfnz
        else:
            jadpu__modne = min(chunksize, evd__hfnz)
        if _is_table_create:
            df = df.iloc[:jadpu__modne, :]
        else:
            df = df.iloc[jadpu__modne:, :]
            if len(df) == 0:
                return ffq__wnbx
    nwa__zkzut = df.columns
    try:
        if tawmg__rxqg == 'snowflake':
            if rzfte__tjmk and con.count(rzfte__tjmk) == 1:
                con = con.replace(rzfte__tjmk, quote(rzfte__tjmk))
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
                df.columns = [(lxof__zun.upper() if lxof__zun.islower() else
                    lxof__zun) for lxof__zun in df.columns]
            except ImportError as sxzsg__mfivy:
                ffq__wnbx = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return ffq__wnbx
        if tawmg__rxqg == 'oracle':
            import sqlalchemy as sa
            exsza__mpvk = bodo.typeof(df)
            lfopw__bbyyr = {}
            for lxof__zun, oiq__xbh in zip(exsza__mpvk.columns, exsza__mpvk
                .data):
                if df[lxof__zun].dtype == 'object':
                    if oiq__xbh == datetime_date_array_type:
                        lfopw__bbyyr[lxof__zun] = sa.types.Date
                    elif oiq__xbh == bodo.string_array_type:
                        lfopw__bbyyr[lxof__zun] = sa.types.VARCHAR(df[
                            lxof__zun].str.len().max())
            dtype = lfopw__bbyyr
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as jco__tov:
            ffq__wnbx = jco__tov.args[0]
        return ffq__wnbx
    finally:
        df.columns = nwa__zkzut


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
        aug__kee = bodo.libs.distributed_api.get_rank()
        ffq__wnbx = 'unset'
        if aug__kee != 0:
            ffq__wnbx = bcast_scalar(ffq__wnbx)
        elif aug__kee == 0:
            ffq__wnbx = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                True, _is_parallel)
            ffq__wnbx = bcast_scalar(ffq__wnbx)
        if_exists = 'append'
        if _is_parallel and ffq__wnbx == 'all_ok':
            ffq__wnbx = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                False, _is_parallel)
        if ffq__wnbx != 'all_ok':
            print('err_msg=', ffq__wnbx)
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
        mkbnu__irwb = get_overload_const_str(path_or_buf)
        if mkbnu__irwb.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        rysqx__zssjj = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(rysqx__zssjj))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(rysqx__zssjj))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    bnyw__yhuh = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    hvx__cxvr = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', bnyw__yhuh, hvx__cxvr,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    zdr__efu = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        fzmb__who = data.data.dtype.categories
        zdr__efu += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        fzmb__who = data.dtype.categories
        zdr__efu += '  data_values = data\n'
    eamgq__lgc = len(fzmb__who)
    zdr__efu += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    zdr__efu += '  numba.parfors.parfor.init_prange()\n'
    zdr__efu += '  n = len(data_values)\n'
    for i in range(eamgq__lgc):
        zdr__efu += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    zdr__efu += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    zdr__efu += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for khw__jtay in range(eamgq__lgc):
        zdr__efu += '          data_arr_{}[i] = 0\n'.format(khw__jtay)
    zdr__efu += '      else:\n'
    for ixckt__qao in range(eamgq__lgc):
        zdr__efu += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            ixckt__qao)
    ljzst__zmr = ', '.join(f'data_arr_{i}' for i in range(eamgq__lgc))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(fzmb__who[0], np.datetime64):
        fzmb__who = tuple(pd.Timestamp(lxof__zun) for lxof__zun in fzmb__who)
    elif isinstance(fzmb__who[0], np.timedelta64):
        fzmb__who = tuple(pd.Timedelta(lxof__zun) for lxof__zun in fzmb__who)
    return bodo.hiframes.dataframe_impl._gen_init_df(zdr__efu, fzmb__who,
        ljzst__zmr, index)


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
    for wketb__vafh in pd_unsupported:
        natde__xego = mod_name + '.' + wketb__vafh.__name__
        overload(wketb__vafh, no_unliteral=True)(create_unsupported_overload
            (natde__xego))


def _install_dataframe_unsupported():
    for cakf__vkrms in dataframe_unsupported_attrs:
        mojz__vhui = 'DataFrame.' + cakf__vkrms
        overload_attribute(DataFrameType, cakf__vkrms)(
            create_unsupported_overload(mojz__vhui))
    for natde__xego in dataframe_unsupported:
        mojz__vhui = 'DataFrame.' + natde__xego + '()'
        overload_method(DataFrameType, natde__xego)(create_unsupported_overload
            (mojz__vhui))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
