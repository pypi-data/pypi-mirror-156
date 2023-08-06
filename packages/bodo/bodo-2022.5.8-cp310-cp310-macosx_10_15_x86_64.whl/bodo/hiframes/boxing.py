"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType, PandasDatetimeTZDtype
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
ll.add_symbol('is_np_array', hstr_ext.is_np_array)
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20
_use_dict_str_type = False


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    fdms__pbchk = tuple(val.columns.to_list())
    qabk__plx = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        ucqk__jiqfa = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        ucqk__jiqfa = numba.typeof(val.index)
    dos__yvl = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    khna__ecgpd = len(qabk__plx) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(qabk__plx, ucqk__jiqfa, fdms__pbchk, dos__yvl,
        is_table_format=khna__ecgpd)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    dos__yvl = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        vlmvb__rtbi = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        vlmvb__rtbi = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    masx__fpx = dtype_to_array_type(dtype)
    if _use_dict_str_type and masx__fpx == string_array_type:
        masx__fpx = bodo.dict_str_arr_type
    return SeriesType(dtype, data=masx__fpx, index=vlmvb__rtbi, name_typ=
        numba.typeof(val.name), dist=dos__yvl)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    wtcu__nkzv = c.pyapi.object_getattr_string(val, 'index')
    gid__qfnrn = c.pyapi.to_native_value(typ.index, wtcu__nkzv).value
    c.pyapi.decref(wtcu__nkzv)
    if typ.is_table_format:
        axv__wnwc = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        axv__wnwc.parent = val
        for oynx__izw, lea__eve in typ.table_type.type_to_blk.items():
            rshk__uiye = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[lea__eve]))
            eaa__syifq, huf__ravug = ListInstance.allocate_ex(c.context, c.
                builder, types.List(oynx__izw), rshk__uiye)
            huf__ravug.size = rshk__uiye
            setattr(axv__wnwc, f'block_{lea__eve}', huf__ravug.value)
        drja__nxht = c.pyapi.call_method(val, '__len__', ())
        rtn__hpx = c.pyapi.long_as_longlong(drja__nxht)
        c.pyapi.decref(drja__nxht)
        axv__wnwc.len = rtn__hpx
        lszo__khbw = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [axv__wnwc._getvalue()])
    else:
        qycy__cke = [c.context.get_constant_null(oynx__izw) for oynx__izw in
            typ.data]
        lszo__khbw = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            qycy__cke)
    xoij__yyt = construct_dataframe(c.context, c.builder, typ, lszo__khbw,
        gid__qfnrn, val, None)
    return NativeValue(xoij__yyt)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        xawax__bbhp = df._bodo_meta['type_metadata'][1]
    else:
        xawax__bbhp = [None] * len(df.columns)
    sdto__bdb = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=xawax__bbhp[i])) for i in range(len(df.columns))]
    sdto__bdb = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        oynx__izw == string_array_type else oynx__izw) for oynx__izw in
        sdto__bdb]
    return tuple(sdto__bdb)


class SeriesDtypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    mgk__tqgub, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(mgk__tqgub) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {mgk__tqgub}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        xop__etwxv, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return xop__etwxv, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        xop__etwxv, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return xop__etwxv, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        vla__lgiv = typ_enum_list[1]
        nxfhn__bsyn = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(vla__lgiv, nxfhn__bsyn)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        jwfhr__nchns = typ_enum_list[1]
        ospj__holx = tuple(typ_enum_list[2:2 + jwfhr__nchns])
        jmn__xpgki = typ_enum_list[2 + jwfhr__nchns:]
        ron__hibd = []
        for i in range(jwfhr__nchns):
            jmn__xpgki, zfc__etyp = _dtype_from_type_enum_list_recursor(
                jmn__xpgki)
            ron__hibd.append(zfc__etyp)
        return jmn__xpgki, StructType(tuple(ron__hibd), ospj__holx)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hdqd__xjri = typ_enum_list[1]
        jmn__xpgki = typ_enum_list[2:]
        return jmn__xpgki, hdqd__xjri
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hdqd__xjri = typ_enum_list[1]
        jmn__xpgki = typ_enum_list[2:]
        return jmn__xpgki, numba.types.literal(hdqd__xjri)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        jmn__xpgki, aph__cllz = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        jmn__xpgki, gczm__fwd = _dtype_from_type_enum_list_recursor(jmn__xpgki)
        jmn__xpgki, ycd__lvn = _dtype_from_type_enum_list_recursor(jmn__xpgki)
        jmn__xpgki, wlc__vyxa = _dtype_from_type_enum_list_recursor(jmn__xpgki)
        jmn__xpgki, ehv__not = _dtype_from_type_enum_list_recursor(jmn__xpgki)
        return jmn__xpgki, PDCategoricalDtype(aph__cllz, gczm__fwd,
            ycd__lvn, wlc__vyxa, ehv__not)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return jmn__xpgki, DatetimeIndexType(fmqvb__tbe)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        jmn__xpgki, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(jmn__xpgki
            )
        jmn__xpgki, wlc__vyxa = _dtype_from_type_enum_list_recursor(jmn__xpgki)
        return jmn__xpgki, NumericIndexType(dtype, fmqvb__tbe, wlc__vyxa)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        jmn__xpgki, zrnpg__migs = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(jmn__xpgki
            )
        return jmn__xpgki, PeriodIndexType(zrnpg__migs, fmqvb__tbe)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        jmn__xpgki, wlc__vyxa = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(jmn__xpgki
            )
        return jmn__xpgki, CategoricalIndexType(wlc__vyxa, fmqvb__tbe)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return jmn__xpgki, RangeIndexType(fmqvb__tbe)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return jmn__xpgki, StringIndexType(fmqvb__tbe)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return jmn__xpgki, BinaryIndexType(fmqvb__tbe)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        jmn__xpgki, fmqvb__tbe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return jmn__xpgki, TimedeltaIndexType(fmqvb__tbe)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        bmek__tphic = get_overload_const_int(typ)
        if numba.types.maybe_literal(bmek__tphic) == typ:
            return [SeriesDtypeEnum.LiteralType.value, bmek__tphic]
    elif is_overload_constant_str(typ):
        bmek__tphic = get_overload_const_str(typ)
        if numba.types.maybe_literal(bmek__tphic) == typ:
            return [SeriesDtypeEnum.LiteralType.value, bmek__tphic]
    elif is_overload_constant_bool(typ):
        bmek__tphic = get_overload_const_bool(typ)
        if numba.types.maybe_literal(bmek__tphic) == typ:
            return [SeriesDtypeEnum.LiteralType.value, bmek__tphic]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        afxmk__thqbj = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for qxg__kgyp in typ.names:
            afxmk__thqbj.append(qxg__kgyp)
        for akig__hwt in typ.data:
            afxmk__thqbj += _dtype_to_type_enum_list_recursor(akig__hwt)
        return afxmk__thqbj
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        phar__cuqon = _dtype_to_type_enum_list_recursor(typ.categories)
        nzq__ffrt = _dtype_to_type_enum_list_recursor(typ.elem_type)
        fhs__tifr = _dtype_to_type_enum_list_recursor(typ.ordered)
        peh__tlydb = _dtype_to_type_enum_list_recursor(typ.data)
        osvss__hdnzn = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + phar__cuqon + nzq__ffrt + fhs__tifr + peh__tlydb + osvss__hdnzn
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                qmjz__mbf = types.float64
                ovl__wgi = types.Array(qmjz__mbf, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                qmjz__mbf = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    ovl__wgi = IntegerArrayType(qmjz__mbf)
                else:
                    ovl__wgi = types.Array(qmjz__mbf, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                qmjz__mbf = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    ovl__wgi = IntegerArrayType(qmjz__mbf)
                else:
                    ovl__wgi = types.Array(qmjz__mbf, 1, 'C')
            elif typ.dtype == types.bool_:
                qmjz__mbf = typ.dtype
                ovl__wgi = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(qmjz__mbf
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(ovl__wgi)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0:
            if array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
            elif hasattr(S, '_bodo_meta'
                ) and S._bodo_meta is not None and 'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None:
                xds__fslh = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(xds__fslh)
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        uufwp__ppu = S.dtype.unit
        if uufwp__ppu != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        flip__ooamc = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(flip__ooamc)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    mbxgu__ohri = cgutils.is_not_null(builder, parent_obj)
    pvg__wlldt = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(mbxgu__ohri):
        aok__ufxel = pyapi.object_getattr_string(parent_obj, 'columns')
        drja__nxht = pyapi.call_method(aok__ufxel, '__len__', ())
        builder.store(pyapi.long_as_longlong(drja__nxht), pvg__wlldt)
        pyapi.decref(drja__nxht)
        pyapi.decref(aok__ufxel)
    use_parent_obj = builder.and_(mbxgu__ohri, builder.icmp_unsigned('==',
        builder.load(pvg__wlldt), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        vqz__oddtq = df_typ.runtime_colname_typ
        context.nrt.incref(builder, vqz__oddtq, dataframe_payload.columns)
        return pyapi.from_native_value(vqz__oddtq, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        zwz__pyyu = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        zwz__pyyu = np.array(df_typ.columns, 'int64')
    else:
        zwz__pyyu = df_typ.columns
    jio__ndsna = numba.typeof(zwz__pyyu)
    ufmp__xlj = context.get_constant_generic(builder, jio__ndsna, zwz__pyyu)
    nxfto__zzjy = pyapi.from_native_value(jio__ndsna, ufmp__xlj, c.env_manager)
    return nxfto__zzjy


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (puqip__tulg, rzox__tjgen):
        with puqip__tulg:
            pyapi.incref(obj)
            zhs__enkuc = context.insert_const_string(c.builder.module, 'numpy')
            zxjec__hhm = pyapi.import_module_noblock(zhs__enkuc)
            if df_typ.has_runtime_cols:
                reyho__dndey = 0
            else:
                reyho__dndey = len(df_typ.columns)
            rbp__tgauq = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), reyho__dndey))
            qlv__tln = pyapi.call_method(zxjec__hhm, 'arange', (rbp__tgauq,))
            pyapi.object_setattr_string(obj, 'columns', qlv__tln)
            pyapi.decref(zxjec__hhm)
            pyapi.decref(qlv__tln)
            pyapi.decref(rbp__tgauq)
        with rzox__tjgen:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            iba__kxf = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            zhs__enkuc = context.insert_const_string(c.builder.module, 'pandas'
                )
            zxjec__hhm = pyapi.import_module_noblock(zhs__enkuc)
            df_obj = pyapi.call_method(zxjec__hhm, 'DataFrame', (pyapi.
                borrow_none(), iba__kxf))
            pyapi.decref(zxjec__hhm)
            pyapi.decref(iba__kxf)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    dpsbi__oifj = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = dpsbi__oifj.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        yyov__zlgx = typ.table_type
        axv__wnwc = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, yyov__zlgx, axv__wnwc)
        vkq__nck = box_table(yyov__zlgx, axv__wnwc, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (mak__tdmzr, okwnu__lqvy):
            with mak__tdmzr:
                yzwio__ncgwy = pyapi.object_getattr_string(vkq__nck, 'arrays')
                dib__zqhin = c.pyapi.make_none()
                if n_cols is None:
                    drja__nxht = pyapi.call_method(yzwio__ncgwy, '__len__', ())
                    rshk__uiye = pyapi.long_as_longlong(drja__nxht)
                    pyapi.decref(drja__nxht)
                else:
                    rshk__uiye = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, rshk__uiye) as zgklh__vggdi:
                    i = zgklh__vggdi.index
                    ukp__yul = pyapi.list_getitem(yzwio__ncgwy, i)
                    drz__rmj = c.builder.icmp_unsigned('!=', ukp__yul,
                        dib__zqhin)
                    with builder.if_then(drz__rmj):
                        hnmll__fji = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, hnmll__fji, ukp__yul)
                        pyapi.decref(hnmll__fji)
                pyapi.decref(yzwio__ncgwy)
                pyapi.decref(dib__zqhin)
            with okwnu__lqvy:
                df_obj = builder.load(res)
                iba__kxf = pyapi.object_getattr_string(df_obj, 'index')
                hbvx__ufyud = c.pyapi.call_method(vkq__nck, 'to_pandas', (
                    iba__kxf,))
                builder.store(hbvx__ufyud, res)
                pyapi.decref(df_obj)
                pyapi.decref(iba__kxf)
        pyapi.decref(vkq__nck)
    else:
        hovfa__qtax = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        ygqa__ewl = typ.data
        for i, hxy__kphij, masx__fpx in zip(range(n_cols), hovfa__qtax,
            ygqa__ewl):
            jsefh__gdxq = cgutils.alloca_once_value(builder, hxy__kphij)
            qcktw__myx = cgutils.alloca_once_value(builder, context.
                get_constant_null(masx__fpx))
            drz__rmj = builder.not_(is_ll_eq(builder, jsefh__gdxq, qcktw__myx))
            yluse__ptbse = builder.or_(builder.not_(use_parent_obj),
                builder.and_(use_parent_obj, drz__rmj))
            with builder.if_then(yluse__ptbse):
                hnmll__fji = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, masx__fpx, hxy__kphij)
                arr_obj = pyapi.from_native_value(masx__fpx, hxy__kphij, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, hnmll__fji, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(hnmll__fji)
    df_obj = builder.load(res)
    nxfto__zzjy = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', nxfto__zzjy)
    pyapi.decref(nxfto__zzjy)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    dib__zqhin = pyapi.borrow_none()
    ufd__gztv = pyapi.unserialize(pyapi.serialize_object(slice))
    bqvis__tnbeu = pyapi.call_function_objargs(ufd__gztv, [dib__zqhin])
    qffvx__pfvpq = pyapi.long_from_longlong(col_ind)
    nrowu__qndji = pyapi.tuple_pack([bqvis__tnbeu, qffvx__pfvpq])
    rhor__sux = pyapi.object_getattr_string(df_obj, 'iloc')
    ahty__ouyn = pyapi.object_getitem(rhor__sux, nrowu__qndji)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        zfsvn__lod = pyapi.object_getattr_string(ahty__ouyn, 'array')
    else:
        zfsvn__lod = pyapi.object_getattr_string(ahty__ouyn, 'values')
    if isinstance(data_typ, types.Array):
        maja__cwl = context.insert_const_string(builder.module, 'numpy')
        xpol__rwb = pyapi.import_module_noblock(maja__cwl)
        arr_obj = pyapi.call_method(xpol__rwb, 'ascontiguousarray', (
            zfsvn__lod,))
        pyapi.decref(zfsvn__lod)
        pyapi.decref(xpol__rwb)
    else:
        arr_obj = zfsvn__lod
    pyapi.decref(ufd__gztv)
    pyapi.decref(bqvis__tnbeu)
    pyapi.decref(qffvx__pfvpq)
    pyapi.decref(nrowu__qndji)
    pyapi.decref(rhor__sux)
    pyapi.decref(ahty__ouyn)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        dpsbi__oifj = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            dpsbi__oifj.parent, args[1], data_typ)
        zhets__esp = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            axv__wnwc = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            lea__eve = df_typ.table_type.type_to_blk[data_typ]
            zcqw__etjaz = getattr(axv__wnwc, f'block_{lea__eve}')
            ygum__gtfg = ListInstance(c.context, c.builder, types.List(
                data_typ), zcqw__etjaz)
            fzflx__lcg = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            ygum__gtfg.inititem(fzflx__lcg, zhets__esp.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, zhets__esp.value, col_ind)
        zhwfv__unu = DataFramePayloadType(df_typ)
        vzle__qohle = context.nrt.meminfo_data(builder, dpsbi__oifj.meminfo)
        jafvx__qowf = context.get_value_type(zhwfv__unu).as_pointer()
        vzle__qohle = builder.bitcast(vzle__qohle, jafvx__qowf)
        builder.store(dataframe_payload._getvalue(), vzle__qohle)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        zfsvn__lod = c.pyapi.object_getattr_string(val, 'array')
    else:
        zfsvn__lod = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        maja__cwl = c.context.insert_const_string(c.builder.module, 'numpy')
        xpol__rwb = c.pyapi.import_module_noblock(maja__cwl)
        arr_obj = c.pyapi.call_method(xpol__rwb, 'ascontiguousarray', (
            zfsvn__lod,))
        c.pyapi.decref(zfsvn__lod)
        c.pyapi.decref(xpol__rwb)
    else:
        arr_obj = zfsvn__lod
    cshjb__gtm = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    iba__kxf = c.pyapi.object_getattr_string(val, 'index')
    gid__qfnrn = c.pyapi.to_native_value(typ.index, iba__kxf).value
    qxk__ook = c.pyapi.object_getattr_string(val, 'name')
    ktb__ppsb = c.pyapi.to_native_value(typ.name_typ, qxk__ook).value
    byi__phv = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, cshjb__gtm, gid__qfnrn, ktb__ppsb)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(iba__kxf)
    c.pyapi.decref(qxk__ook)
    return NativeValue(byi__phv)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        kphp__xzhtw = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(kphp__xzhtw._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    zhs__enkuc = c.context.insert_const_string(c.builder.module, 'pandas')
    ycgvz__qdy = c.pyapi.import_module_noblock(zhs__enkuc)
    ellxa__jsp = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, ellxa__jsp.data)
    c.context.nrt.incref(c.builder, typ.index, ellxa__jsp.index)
    c.context.nrt.incref(c.builder, typ.name_typ, ellxa__jsp.name)
    arr_obj = c.pyapi.from_native_value(typ.data, ellxa__jsp.data, c.
        env_manager)
    iba__kxf = c.pyapi.from_native_value(typ.index, ellxa__jsp.index, c.
        env_manager)
    qxk__ook = c.pyapi.from_native_value(typ.name_typ, ellxa__jsp.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(ycgvz__qdy, 'Series', (arr_obj, iba__kxf,
        dtype, qxk__ook))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(iba__kxf)
    c.pyapi.decref(qxk__ook)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(ycgvz__qdy)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    yqbdd__tymag = []
    for xqzoy__rmid in typ_list:
        if isinstance(xqzoy__rmid, int) and not isinstance(xqzoy__rmid, bool):
            qqn__nwsgj = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), xqzoy__rmid))
        else:
            fhiy__ezvne = numba.typeof(xqzoy__rmid)
            awky__boak = context.get_constant_generic(builder, fhiy__ezvne,
                xqzoy__rmid)
            qqn__nwsgj = pyapi.from_native_value(fhiy__ezvne, awky__boak,
                env_manager)
        yqbdd__tymag.append(qqn__nwsgj)
    qivhd__njws = pyapi.list_pack(yqbdd__tymag)
    for val in yqbdd__tymag:
        pyapi.decref(val)
    return qivhd__njws


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    ckrx__todxn = not typ.has_runtime_cols and (not typ.is_table_format or 
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    wyl__ppgi = 2 if ckrx__todxn else 1
    lkm__lpl = pyapi.dict_new(wyl__ppgi)
    jhuxn__qquz = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(lkm__lpl, 'dist', jhuxn__qquz)
    pyapi.decref(jhuxn__qquz)
    if ckrx__todxn:
        fjttz__zkezm = _dtype_to_type_enum_list(typ.index)
        if fjttz__zkezm != None:
            itfou__zsfh = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, fjttz__zkezm)
        else:
            itfou__zsfh = pyapi.make_none()
        rdux__ksezt = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                qivhd__njws = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                qivhd__njws = pyapi.make_none()
            rdux__ksezt.append(qivhd__njws)
        jjz__uwm = pyapi.list_pack(rdux__ksezt)
        vjhco__uma = pyapi.list_pack([itfou__zsfh, jjz__uwm])
        for val in rdux__ksezt:
            pyapi.decref(val)
        pyapi.dict_setitem_string(lkm__lpl, 'type_metadata', vjhco__uma)
    pyapi.object_setattr_string(obj, '_bodo_meta', lkm__lpl)
    pyapi.decref(lkm__lpl)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    lkm__lpl = pyapi.dict_new(2)
    jhuxn__qquz = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    fjttz__zkezm = _dtype_to_type_enum_list(typ.index)
    if fjttz__zkezm != None:
        itfou__zsfh = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, fjttz__zkezm)
    else:
        itfou__zsfh = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            nry__wao = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            nry__wao = pyapi.make_none()
    else:
        nry__wao = pyapi.make_none()
    nye__anrg = pyapi.list_pack([itfou__zsfh, nry__wao])
    pyapi.dict_setitem_string(lkm__lpl, 'type_metadata', nye__anrg)
    pyapi.decref(nye__anrg)
    pyapi.dict_setitem_string(lkm__lpl, 'dist', jhuxn__qquz)
    pyapi.object_setattr_string(obj, '_bodo_meta', lkm__lpl)
    pyapi.decref(lkm__lpl)
    pyapi.decref(jhuxn__qquz)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as qba__vyedb:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    gnjc__zhx = numba.np.numpy_support.map_layout(val)
    cona__wown = not val.flags.writeable
    return types.Array(dtype, val.ndim, gnjc__zhx, readonly=cona__wown)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    xyybt__zzqe = val[i]
    if isinstance(xyybt__zzqe, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(xyybt__zzqe, bytes):
        return binary_array_type
    elif isinstance(xyybt__zzqe, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(xyybt__zzqe, (int, np.int8, np.int16, np.int32, np.
        int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(xyybt__zzqe)
            )
    elif isinstance(xyybt__zzqe, (dict, Dict)) and all(isinstance(yax__eput,
        str) for yax__eput in xyybt__zzqe.keys()):
        ospj__holx = tuple(xyybt__zzqe.keys())
        zzony__kzl = tuple(_get_struct_value_arr_type(v) for v in
            xyybt__zzqe.values())
        return StructArrayType(zzony__kzl, ospj__holx)
    elif isinstance(xyybt__zzqe, (dict, Dict)):
        qik__yanz = numba.typeof(_value_to_array(list(xyybt__zzqe.keys())))
        nemiq__izbj = numba.typeof(_value_to_array(list(xyybt__zzqe.values())))
        qik__yanz = to_str_arr_if_dict_array(qik__yanz)
        nemiq__izbj = to_str_arr_if_dict_array(nemiq__izbj)
        return MapArrayType(qik__yanz, nemiq__izbj)
    elif isinstance(xyybt__zzqe, tuple):
        zzony__kzl = tuple(_get_struct_value_arr_type(v) for v in xyybt__zzqe)
        return TupleArrayType(zzony__kzl)
    if isinstance(xyybt__zzqe, (list, np.ndarray, pd.arrays.BooleanArray,
        pd.arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(xyybt__zzqe, list):
            xyybt__zzqe = _value_to_array(xyybt__zzqe)
        zjtlx__omlnb = numba.typeof(xyybt__zzqe)
        zjtlx__omlnb = to_str_arr_if_dict_array(zjtlx__omlnb)
        return ArrayItemArrayType(zjtlx__omlnb)
    if isinstance(xyybt__zzqe, datetime.date):
        return datetime_date_array_type
    if isinstance(xyybt__zzqe, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(xyybt__zzqe, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(xyybt__zzqe, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {xyybt__zzqe}'
        )


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    tsmmo__cpa = val.copy()
    tsmmo__cpa.append(None)
    hxy__kphij = np.array(tsmmo__cpa, np.object_)
    if len(val) and isinstance(val[0], float):
        hxy__kphij = np.array(val, np.float64)
    return hxy__kphij


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    masx__fpx = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        masx__fpx = to_nullable_type(masx__fpx)
    return masx__fpx
