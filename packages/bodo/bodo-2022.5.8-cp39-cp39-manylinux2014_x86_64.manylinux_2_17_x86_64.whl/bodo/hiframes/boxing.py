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
    osmnx__jyvc = tuple(val.columns.to_list())
    bpke__gyn = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        mfvh__ctjqz = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        mfvh__ctjqz = numba.typeof(val.index)
    aeg__luuz = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    whmoi__mngg = len(bpke__gyn) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(bpke__gyn, mfvh__ctjqz, osmnx__jyvc, aeg__luuz,
        is_table_format=whmoi__mngg)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    aeg__luuz = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        eyo__bcofv = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        eyo__bcofv = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    gen__yse = dtype_to_array_type(dtype)
    if _use_dict_str_type and gen__yse == string_array_type:
        gen__yse = bodo.dict_str_arr_type
    return SeriesType(dtype, data=gen__yse, index=eyo__bcofv, name_typ=
        numba.typeof(val.name), dist=aeg__luuz)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    jfved__hexl = c.pyapi.object_getattr_string(val, 'index')
    juwh__fdpa = c.pyapi.to_native_value(typ.index, jfved__hexl).value
    c.pyapi.decref(jfved__hexl)
    if typ.is_table_format:
        ril__pbwud = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        ril__pbwud.parent = val
        for aiy__pmy, jmsk__atcdv in typ.table_type.type_to_blk.items():
            zuh__yra = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[jmsk__atcdv]))
            lzui__zaz, gou__psv = ListInstance.allocate_ex(c.context, c.
                builder, types.List(aiy__pmy), zuh__yra)
            gou__psv.size = zuh__yra
            setattr(ril__pbwud, f'block_{jmsk__atcdv}', gou__psv.value)
        fraz__dzltf = c.pyapi.call_method(val, '__len__', ())
        rubm__qtqxz = c.pyapi.long_as_longlong(fraz__dzltf)
        c.pyapi.decref(fraz__dzltf)
        ril__pbwud.len = rubm__qtqxz
        gtife__cfw = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [ril__pbwud._getvalue()])
    else:
        aqbrz__xsfjo = [c.context.get_constant_null(aiy__pmy) for aiy__pmy in
            typ.data]
        gtife__cfw = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            aqbrz__xsfjo)
    rxuok__zmbo = construct_dataframe(c.context, c.builder, typ, gtife__cfw,
        juwh__fdpa, val, None)
    return NativeValue(rxuok__zmbo)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        iknl__nmqz = df._bodo_meta['type_metadata'][1]
    else:
        iknl__nmqz = [None] * len(df.columns)
    xuw__dzfp = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=iknl__nmqz[i])) for i in range(len(df.columns))]
    xuw__dzfp = [(bodo.dict_str_arr_type if _use_dict_str_type and aiy__pmy ==
        string_array_type else aiy__pmy) for aiy__pmy in xuw__dzfp]
    return tuple(xuw__dzfp)


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
    blh__dlhub, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(blh__dlhub) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {blh__dlhub}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        jti__psxn, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return jti__psxn, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        jti__psxn, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return jti__psxn, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        fmhqn__yti = typ_enum_list[1]
        bgjw__tscyz = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(fmhqn__yti, bgjw__tscyz)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        ufu__fcsq = typ_enum_list[1]
        zcemn__nfkgl = tuple(typ_enum_list[2:2 + ufu__fcsq])
        lmmb__bym = typ_enum_list[2 + ufu__fcsq:]
        rhtry__lcs = []
        for i in range(ufu__fcsq):
            lmmb__bym, hgqel__nlz = _dtype_from_type_enum_list_recursor(
                lmmb__bym)
            rhtry__lcs.append(hgqel__nlz)
        return lmmb__bym, StructType(tuple(rhtry__lcs), zcemn__nfkgl)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        vif__fmaq = typ_enum_list[1]
        lmmb__bym = typ_enum_list[2:]
        return lmmb__bym, vif__fmaq
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        vif__fmaq = typ_enum_list[1]
        lmmb__bym = typ_enum_list[2:]
        return lmmb__bym, numba.types.literal(vif__fmaq)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        lmmb__bym, yzef__hmt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        lmmb__bym, edlkr__zijtz = _dtype_from_type_enum_list_recursor(lmmb__bym
            )
        lmmb__bym, ewtl__jok = _dtype_from_type_enum_list_recursor(lmmb__bym)
        lmmb__bym, yed__imlj = _dtype_from_type_enum_list_recursor(lmmb__bym)
        lmmb__bym, mtt__wxs = _dtype_from_type_enum_list_recursor(lmmb__bym)
        return lmmb__bym, PDCategoricalDtype(yzef__hmt, edlkr__zijtz,
            ewtl__jok, yed__imlj, mtt__wxs)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return lmmb__bym, DatetimeIndexType(drtg__ierof)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        lmmb__bym, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(lmmb__bym)
        lmmb__bym, yed__imlj = _dtype_from_type_enum_list_recursor(lmmb__bym)
        return lmmb__bym, NumericIndexType(dtype, drtg__ierof, yed__imlj)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        lmmb__bym, jsdsc__ppvwv = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(lmmb__bym)
        return lmmb__bym, PeriodIndexType(jsdsc__ppvwv, drtg__ierof)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        lmmb__bym, yed__imlj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(lmmb__bym)
        return lmmb__bym, CategoricalIndexType(yed__imlj, drtg__ierof)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return lmmb__bym, RangeIndexType(drtg__ierof)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return lmmb__bym, StringIndexType(drtg__ierof)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return lmmb__bym, BinaryIndexType(drtg__ierof)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        lmmb__bym, drtg__ierof = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return lmmb__bym, TimedeltaIndexType(drtg__ierof)
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
        yrukt__guvsv = get_overload_const_int(typ)
        if numba.types.maybe_literal(yrukt__guvsv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yrukt__guvsv]
    elif is_overload_constant_str(typ):
        yrukt__guvsv = get_overload_const_str(typ)
        if numba.types.maybe_literal(yrukt__guvsv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yrukt__guvsv]
    elif is_overload_constant_bool(typ):
        yrukt__guvsv = get_overload_const_bool(typ)
        if numba.types.maybe_literal(yrukt__guvsv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yrukt__guvsv]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        ofx__pibe = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for yfygk__puis in typ.names:
            ofx__pibe.append(yfygk__puis)
        for ost__zpezh in typ.data:
            ofx__pibe += _dtype_to_type_enum_list_recursor(ost__zpezh)
        return ofx__pibe
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        mfk__dabu = _dtype_to_type_enum_list_recursor(typ.categories)
        cmhpx__vvz = _dtype_to_type_enum_list_recursor(typ.elem_type)
        xbu__dztga = _dtype_to_type_enum_list_recursor(typ.ordered)
        tzby__zez = _dtype_to_type_enum_list_recursor(typ.data)
        hjm__tmjqz = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + mfk__dabu + cmhpx__vvz + xbu__dztga + tzby__zez + hjm__tmjqz
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                hipc__pjr = types.float64
                nfg__dgej = types.Array(hipc__pjr, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                hipc__pjr = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    nfg__dgej = IntegerArrayType(hipc__pjr)
                else:
                    nfg__dgej = types.Array(hipc__pjr, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                hipc__pjr = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    nfg__dgej = IntegerArrayType(hipc__pjr)
                else:
                    nfg__dgej = types.Array(hipc__pjr, 1, 'C')
            elif typ.dtype == types.bool_:
                hipc__pjr = typ.dtype
                nfg__dgej = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(hipc__pjr
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(nfg__dgej)
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
                qjugv__yingi = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(qjugv__yingi)
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
        hadm__delom = S.dtype.unit
        if hadm__delom != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        cvpem__ozak = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(cvpem__ozak)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    gqjtz__kvrao = cgutils.is_not_null(builder, parent_obj)
    hlq__dscg = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(gqjtz__kvrao):
        vdzs__vygi = pyapi.object_getattr_string(parent_obj, 'columns')
        fraz__dzltf = pyapi.call_method(vdzs__vygi, '__len__', ())
        builder.store(pyapi.long_as_longlong(fraz__dzltf), hlq__dscg)
        pyapi.decref(fraz__dzltf)
        pyapi.decref(vdzs__vygi)
    use_parent_obj = builder.and_(gqjtz__kvrao, builder.icmp_unsigned('==',
        builder.load(hlq__dscg), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        zhzvy__nit = df_typ.runtime_colname_typ
        context.nrt.incref(builder, zhzvy__nit, dataframe_payload.columns)
        return pyapi.from_native_value(zhzvy__nit, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        txh__wkgdn = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        txh__wkgdn = np.array(df_typ.columns, 'int64')
    else:
        txh__wkgdn = df_typ.columns
    xqplv__ydcdc = numba.typeof(txh__wkgdn)
    rdjwh__knli = context.get_constant_generic(builder, xqplv__ydcdc,
        txh__wkgdn)
    isiy__saeo = pyapi.from_native_value(xqplv__ydcdc, rdjwh__knli, c.
        env_manager)
    return isiy__saeo


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (xkav__wbru, varjq__mqr):
        with xkav__wbru:
            pyapi.incref(obj)
            kfqxz__uvv = context.insert_const_string(c.builder.module, 'numpy')
            dulj__ffhii = pyapi.import_module_noblock(kfqxz__uvv)
            if df_typ.has_runtime_cols:
                gvy__clq = 0
            else:
                gvy__clq = len(df_typ.columns)
            ngl__erl = pyapi.long_from_longlong(lir.Constant(lir.IntType(64
                ), gvy__clq))
            zvd__mew = pyapi.call_method(dulj__ffhii, 'arange', (ngl__erl,))
            pyapi.object_setattr_string(obj, 'columns', zvd__mew)
            pyapi.decref(dulj__ffhii)
            pyapi.decref(zvd__mew)
            pyapi.decref(ngl__erl)
        with varjq__mqr:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            kwey__qgot = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            kfqxz__uvv = context.insert_const_string(c.builder.module, 'pandas'
                )
            dulj__ffhii = pyapi.import_module_noblock(kfqxz__uvv)
            df_obj = pyapi.call_method(dulj__ffhii, 'DataFrame', (pyapi.
                borrow_none(), kwey__qgot))
            pyapi.decref(dulj__ffhii)
            pyapi.decref(kwey__qgot)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    ohe__ppxt = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = ohe__ppxt.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        emxmx__qdecq = typ.table_type
        ril__pbwud = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, emxmx__qdecq, ril__pbwud)
        yfuzt__dbtbg = box_table(emxmx__qdecq, ril__pbwud, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (fjc__keszx, pgea__jkcue):
            with fjc__keszx:
                xkonq__pbfsj = pyapi.object_getattr_string(yfuzt__dbtbg,
                    'arrays')
                khpok__vizxa = c.pyapi.make_none()
                if n_cols is None:
                    fraz__dzltf = pyapi.call_method(xkonq__pbfsj, '__len__', ()
                        )
                    zuh__yra = pyapi.long_as_longlong(fraz__dzltf)
                    pyapi.decref(fraz__dzltf)
                else:
                    zuh__yra = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, zuh__yra) as njek__kbngk:
                    i = njek__kbngk.index
                    rhk__uvg = pyapi.list_getitem(xkonq__pbfsj, i)
                    ljgbg__qzqjx = c.builder.icmp_unsigned('!=', rhk__uvg,
                        khpok__vizxa)
                    with builder.if_then(ljgbg__qzqjx):
                        cufsw__ppixr = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, cufsw__ppixr, rhk__uvg)
                        pyapi.decref(cufsw__ppixr)
                pyapi.decref(xkonq__pbfsj)
                pyapi.decref(khpok__vizxa)
            with pgea__jkcue:
                df_obj = builder.load(res)
                kwey__qgot = pyapi.object_getattr_string(df_obj, 'index')
                yixd__fbua = c.pyapi.call_method(yfuzt__dbtbg, 'to_pandas',
                    (kwey__qgot,))
                builder.store(yixd__fbua, res)
                pyapi.decref(df_obj)
                pyapi.decref(kwey__qgot)
        pyapi.decref(yfuzt__dbtbg)
    else:
        jppv__brzmy = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        vnr__ntzx = typ.data
        for i, oalx__pwnw, gen__yse in zip(range(n_cols), jppv__brzmy,
            vnr__ntzx):
            qreqi__hbc = cgutils.alloca_once_value(builder, oalx__pwnw)
            wrzaq__kbfr = cgutils.alloca_once_value(builder, context.
                get_constant_null(gen__yse))
            ljgbg__qzqjx = builder.not_(is_ll_eq(builder, qreqi__hbc,
                wrzaq__kbfr))
            pynmu__vquw = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, ljgbg__qzqjx))
            with builder.if_then(pynmu__vquw):
                cufsw__ppixr = pyapi.long_from_longlong(context.
                    get_constant(types.int64, i))
                context.nrt.incref(builder, gen__yse, oalx__pwnw)
                arr_obj = pyapi.from_native_value(gen__yse, oalx__pwnw, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, cufsw__ppixr, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(cufsw__ppixr)
    df_obj = builder.load(res)
    isiy__saeo = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', isiy__saeo)
    pyapi.decref(isiy__saeo)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    khpok__vizxa = pyapi.borrow_none()
    dgagq__lww = pyapi.unserialize(pyapi.serialize_object(slice))
    pxqdj__bcfqy = pyapi.call_function_objargs(dgagq__lww, [khpok__vizxa])
    lkuc__htfnj = pyapi.long_from_longlong(col_ind)
    bvc__uiw = pyapi.tuple_pack([pxqdj__bcfqy, lkuc__htfnj])
    yxw__jsvz = pyapi.object_getattr_string(df_obj, 'iloc')
    zpmsy__svlfh = pyapi.object_getitem(yxw__jsvz, bvc__uiw)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        mdqnl__eursu = pyapi.object_getattr_string(zpmsy__svlfh, 'array')
    else:
        mdqnl__eursu = pyapi.object_getattr_string(zpmsy__svlfh, 'values')
    if isinstance(data_typ, types.Array):
        ikfo__cvz = context.insert_const_string(builder.module, 'numpy')
        aycx__qvnyw = pyapi.import_module_noblock(ikfo__cvz)
        arr_obj = pyapi.call_method(aycx__qvnyw, 'ascontiguousarray', (
            mdqnl__eursu,))
        pyapi.decref(mdqnl__eursu)
        pyapi.decref(aycx__qvnyw)
    else:
        arr_obj = mdqnl__eursu
    pyapi.decref(dgagq__lww)
    pyapi.decref(pxqdj__bcfqy)
    pyapi.decref(lkuc__htfnj)
    pyapi.decref(bvc__uiw)
    pyapi.decref(yxw__jsvz)
    pyapi.decref(zpmsy__svlfh)
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
        ohe__ppxt = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            ohe__ppxt.parent, args[1], data_typ)
        zskg__lsj = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            ril__pbwud = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            jmsk__atcdv = df_typ.table_type.type_to_blk[data_typ]
            pthv__qeqg = getattr(ril__pbwud, f'block_{jmsk__atcdv}')
            svop__qce = ListInstance(c.context, c.builder, types.List(
                data_typ), pthv__qeqg)
            prv__ihs = context.get_constant(types.int64, df_typ.table_type.
                block_offsets[col_ind])
            svop__qce.inititem(prv__ihs, zskg__lsj.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, zskg__lsj.value, col_ind)
        tbeqh__axgco = DataFramePayloadType(df_typ)
        vskj__knvfg = context.nrt.meminfo_data(builder, ohe__ppxt.meminfo)
        tbh__sfa = context.get_value_type(tbeqh__axgco).as_pointer()
        vskj__knvfg = builder.bitcast(vskj__knvfg, tbh__sfa)
        builder.store(dataframe_payload._getvalue(), vskj__knvfg)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        mdqnl__eursu = c.pyapi.object_getattr_string(val, 'array')
    else:
        mdqnl__eursu = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        ikfo__cvz = c.context.insert_const_string(c.builder.module, 'numpy')
        aycx__qvnyw = c.pyapi.import_module_noblock(ikfo__cvz)
        arr_obj = c.pyapi.call_method(aycx__qvnyw, 'ascontiguousarray', (
            mdqnl__eursu,))
        c.pyapi.decref(mdqnl__eursu)
        c.pyapi.decref(aycx__qvnyw)
    else:
        arr_obj = mdqnl__eursu
    cpmzi__nehw = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    kwey__qgot = c.pyapi.object_getattr_string(val, 'index')
    juwh__fdpa = c.pyapi.to_native_value(typ.index, kwey__qgot).value
    hkhb__faavp = c.pyapi.object_getattr_string(val, 'name')
    hznwt__lwmt = c.pyapi.to_native_value(typ.name_typ, hkhb__faavp).value
    rpxse__kiqlu = bodo.hiframes.pd_series_ext.construct_series(c.context,
        c.builder, typ, cpmzi__nehw, juwh__fdpa, hznwt__lwmt)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(kwey__qgot)
    c.pyapi.decref(hkhb__faavp)
    return NativeValue(rpxse__kiqlu)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        ntg__jgo = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(ntg__jgo._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    kfqxz__uvv = c.context.insert_const_string(c.builder.module, 'pandas')
    odobf__lzqda = c.pyapi.import_module_noblock(kfqxz__uvv)
    kme__jha = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c.
        builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, kme__jha.data)
    c.context.nrt.incref(c.builder, typ.index, kme__jha.index)
    c.context.nrt.incref(c.builder, typ.name_typ, kme__jha.name)
    arr_obj = c.pyapi.from_native_value(typ.data, kme__jha.data, c.env_manager)
    kwey__qgot = c.pyapi.from_native_value(typ.index, kme__jha.index, c.
        env_manager)
    hkhb__faavp = c.pyapi.from_native_value(typ.name_typ, kme__jha.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(odobf__lzqda, 'Series', (arr_obj, kwey__qgot,
        dtype, hkhb__faavp))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(kwey__qgot)
    c.pyapi.decref(hkhb__faavp)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(odobf__lzqda)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    akw__its = []
    for cni__rws in typ_list:
        if isinstance(cni__rws, int) and not isinstance(cni__rws, bool):
            dkqn__loeup = pyapi.long_from_longlong(lir.Constant(lir.IntType
                (64), cni__rws))
        else:
            uks__isimm = numba.typeof(cni__rws)
            pitn__etk = context.get_constant_generic(builder, uks__isimm,
                cni__rws)
            dkqn__loeup = pyapi.from_native_value(uks__isimm, pitn__etk,
                env_manager)
        akw__its.append(dkqn__loeup)
    gyj__huokb = pyapi.list_pack(akw__its)
    for val in akw__its:
        pyapi.decref(val)
    return gyj__huokb


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    rrrbd__lfmcj = not typ.has_runtime_cols and (not typ.is_table_format or
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    njjkr__rims = 2 if rrrbd__lfmcj else 1
    jtf__jvva = pyapi.dict_new(njjkr__rims)
    wrw__hcx = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    pyapi.dict_setitem_string(jtf__jvva, 'dist', wrw__hcx)
    pyapi.decref(wrw__hcx)
    if rrrbd__lfmcj:
        jkzw__bhj = _dtype_to_type_enum_list(typ.index)
        if jkzw__bhj != None:
            iokq__iyhk = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, jkzw__bhj)
        else:
            iokq__iyhk = pyapi.make_none()
        fhaqq__vxq = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                gyj__huokb = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                gyj__huokb = pyapi.make_none()
            fhaqq__vxq.append(gyj__huokb)
        evt__ucqv = pyapi.list_pack(fhaqq__vxq)
        jfxh__tll = pyapi.list_pack([iokq__iyhk, evt__ucqv])
        for val in fhaqq__vxq:
            pyapi.decref(val)
        pyapi.dict_setitem_string(jtf__jvva, 'type_metadata', jfxh__tll)
    pyapi.object_setattr_string(obj, '_bodo_meta', jtf__jvva)
    pyapi.decref(jtf__jvva)


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
    jtf__jvva = pyapi.dict_new(2)
    wrw__hcx = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    jkzw__bhj = _dtype_to_type_enum_list(typ.index)
    if jkzw__bhj != None:
        iokq__iyhk = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, jkzw__bhj)
    else:
        iokq__iyhk = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            toxrk__zfc = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            toxrk__zfc = pyapi.make_none()
    else:
        toxrk__zfc = pyapi.make_none()
    mqsf__lrk = pyapi.list_pack([iokq__iyhk, toxrk__zfc])
    pyapi.dict_setitem_string(jtf__jvva, 'type_metadata', mqsf__lrk)
    pyapi.decref(mqsf__lrk)
    pyapi.dict_setitem_string(jtf__jvva, 'dist', wrw__hcx)
    pyapi.object_setattr_string(obj, '_bodo_meta', jtf__jvva)
    pyapi.decref(jtf__jvva)
    pyapi.decref(wrw__hcx)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as bzfnu__thkp:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    upyo__kxmls = numba.np.numpy_support.map_layout(val)
    epml__isury = not val.flags.writeable
    return types.Array(dtype, val.ndim, upyo__kxmls, readonly=epml__isury)


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
    gjru__avo = val[i]
    if isinstance(gjru__avo, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(gjru__avo, bytes):
        return binary_array_type
    elif isinstance(gjru__avo, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(gjru__avo, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(gjru__avo))
    elif isinstance(gjru__avo, (dict, Dict)) and all(isinstance(zogua__kjs,
        str) for zogua__kjs in gjru__avo.keys()):
        zcemn__nfkgl = tuple(gjru__avo.keys())
        tjw__fin = tuple(_get_struct_value_arr_type(v) for v in gjru__avo.
            values())
        return StructArrayType(tjw__fin, zcemn__nfkgl)
    elif isinstance(gjru__avo, (dict, Dict)):
        odqmy__fepz = numba.typeof(_value_to_array(list(gjru__avo.keys())))
        fdx__ubb = numba.typeof(_value_to_array(list(gjru__avo.values())))
        odqmy__fepz = to_str_arr_if_dict_array(odqmy__fepz)
        fdx__ubb = to_str_arr_if_dict_array(fdx__ubb)
        return MapArrayType(odqmy__fepz, fdx__ubb)
    elif isinstance(gjru__avo, tuple):
        tjw__fin = tuple(_get_struct_value_arr_type(v) for v in gjru__avo)
        return TupleArrayType(tjw__fin)
    if isinstance(gjru__avo, (list, np.ndarray, pd.arrays.BooleanArray, pd.
        arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(gjru__avo, list):
            gjru__avo = _value_to_array(gjru__avo)
        thcxw__azsr = numba.typeof(gjru__avo)
        thcxw__azsr = to_str_arr_if_dict_array(thcxw__azsr)
        return ArrayItemArrayType(thcxw__azsr)
    if isinstance(gjru__avo, datetime.date):
        return datetime_date_array_type
    if isinstance(gjru__avo, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(gjru__avo, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(gjru__avo, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {gjru__avo}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    rtxoe__bxgph = val.copy()
    rtxoe__bxgph.append(None)
    oalx__pwnw = np.array(rtxoe__bxgph, np.object_)
    if len(val) and isinstance(val[0], float):
        oalx__pwnw = np.array(val, np.float64)
    return oalx__pwnw


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
    gen__yse = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        gen__yse = to_nullable_type(gen__yse)
    return gen__yse
