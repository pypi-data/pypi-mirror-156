"""Numba extension support for datetime.date objects and their arrays.
"""
import datetime
import operator
import warnings
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.typing.templates import AttributeTemplate, infer_getattr
from numba.core.utils import PYVERSION
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import DatetimeDatetimeType
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type, is_overload_int, is_overload_none
ll.add_symbol('box_datetime_date_array', hdatetime_ext.box_datetime_date_array)
ll.add_symbol('unbox_datetime_date_array', hdatetime_ext.
    unbox_datetime_date_array)
ll.add_symbol('get_isocalendar', hdatetime_ext.get_isocalendar)


class DatetimeDateType(types.Type):

    def __init__(self):
        super(DatetimeDateType, self).__init__(name='DatetimeDateType()')
        self.bitwidth = 64


datetime_date_type = DatetimeDateType()


@typeof_impl.register(datetime.date)
def typeof_datetime_date(val, c):
    return datetime_date_type


register_model(DatetimeDateType)(models.IntegerModel)


@infer_getattr
class DatetimeAttribute(AttributeTemplate):
    key = DatetimeDateType

    def resolve_year(self, typ):
        return types.int64

    def resolve_month(self, typ):
        return types.int64

    def resolve_day(self, typ):
        return types.int64


@lower_getattr(DatetimeDateType, 'year')
def datetime_get_year(context, builder, typ, val):
    return builder.lshr(val, lir.Constant(lir.IntType(64), 32))


@lower_getattr(DatetimeDateType, 'month')
def datetime_get_month(context, builder, typ, val):
    return builder.and_(builder.lshr(val, lir.Constant(lir.IntType(64), 16)
        ), lir.Constant(lir.IntType(64), 65535))


@lower_getattr(DatetimeDateType, 'day')
def datetime_get_day(context, builder, typ, val):
    return builder.and_(val, lir.Constant(lir.IntType(64), 65535))


@unbox(DatetimeDateType)
def unbox_datetime_date(typ, val, c):
    vvr__nrwj = c.pyapi.object_getattr_string(val, 'year')
    xhoo__yudnt = c.pyapi.object_getattr_string(val, 'month')
    fydr__kdjl = c.pyapi.object_getattr_string(val, 'day')
    dyya__mxg = c.pyapi.long_as_longlong(vvr__nrwj)
    abiit__fav = c.pyapi.long_as_longlong(xhoo__yudnt)
    mkssf__bgk = c.pyapi.long_as_longlong(fydr__kdjl)
    wlbfu__bsn = c.builder.add(mkssf__bgk, c.builder.add(c.builder.shl(
        dyya__mxg, lir.Constant(lir.IntType(64), 32)), c.builder.shl(
        abiit__fav, lir.Constant(lir.IntType(64), 16))))
    c.pyapi.decref(vvr__nrwj)
    c.pyapi.decref(xhoo__yudnt)
    c.pyapi.decref(fydr__kdjl)
    eplp__sxrit = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wlbfu__bsn, is_error=eplp__sxrit)


@lower_constant(DatetimeDateType)
def lower_constant_datetime_date(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    wlbfu__bsn = builder.add(day, builder.add(builder.shl(year, lir.
        Constant(lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir
        .IntType(64), 16))))
    return wlbfu__bsn


@box(DatetimeDateType)
def box_datetime_date(typ, val, c):
    vvr__nrwj = c.pyapi.long_from_longlong(c.builder.lshr(val, lir.Constant
        (lir.IntType(64), 32)))
    xhoo__yudnt = c.pyapi.long_from_longlong(c.builder.and_(c.builder.lshr(
        val, lir.Constant(lir.IntType(64), 16)), lir.Constant(lir.IntType(
        64), 65535)))
    fydr__kdjl = c.pyapi.long_from_longlong(c.builder.and_(val, lir.
        Constant(lir.IntType(64), 65535)))
    kdr__tkz = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.date))
    xae__bwi = c.pyapi.call_function_objargs(kdr__tkz, (vvr__nrwj,
        xhoo__yudnt, fydr__kdjl))
    c.pyapi.decref(vvr__nrwj)
    c.pyapi.decref(xhoo__yudnt)
    c.pyapi.decref(fydr__kdjl)
    c.pyapi.decref(kdr__tkz)
    return xae__bwi


@type_callable(datetime.date)
def type_datetime_date(context):

    def typer(year, month, day):
        return datetime_date_type
    return typer


@lower_builtin(datetime.date, types.IntegerLiteral, types.IntegerLiteral,
    types.IntegerLiteral)
@lower_builtin(datetime.date, types.int64, types.int64, types.int64)
def impl_ctor_datetime_date(context, builder, sig, args):
    year, month, day = args
    wlbfu__bsn = builder.add(day, builder.add(builder.shl(year, lir.
        Constant(lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir
        .IntType(64), 16))))
    return wlbfu__bsn


@intrinsic
def cast_int_to_datetime_date(typingctx, val=None):
    assert val == types.int64

    def codegen(context, builder, signature, args):
        return args[0]
    return datetime_date_type(types.int64), codegen


@intrinsic
def cast_datetime_date_to_int(typingctx, val=None):
    assert val == datetime_date_type

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(datetime_date_type), codegen


"""
Following codes are copied from
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""
_MAXORDINAL = 3652059
_DAYS_IN_MONTH = np.array([-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 
    31], dtype=np.int64)
_DAYS_BEFORE_MONTH = np.array([-1, 0, 31, 59, 90, 120, 151, 181, 212, 243, 
    273, 304, 334], dtype=np.int64)


@register_jitable
def _is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


@register_jitable
def _days_before_year(year):
    y = year - 1
    return y * 365 + y // 4 - y // 100 + y // 400


@register_jitable
def _days_in_month(year, month):
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


@register_jitable
def _days_before_month(year, month):
    return _DAYS_BEFORE_MONTH[month] + (month > 2 and _is_leap(year))


_DI400Y = _days_before_year(401)
_DI100Y = _days_before_year(101)
_DI4Y = _days_before_year(5)


@register_jitable
def _ymd2ord(year, month, day):
    jevp__fcgji = _days_in_month(year, month)
    return _days_before_year(year) + _days_before_month(year, month) + day


@register_jitable
def _ord2ymd(n):
    n -= 1
    eey__posi, n = divmod(n, _DI400Y)
    year = eey__posi * 400 + 1
    ssysn__iwj, n = divmod(n, _DI100Y)
    lrr__qvgw, n = divmod(n, _DI4Y)
    poype__bxj, n = divmod(n, 365)
    year += ssysn__iwj * 100 + lrr__qvgw * 4 + poype__bxj
    if poype__bxj == 4 or ssysn__iwj == 4:
        return year - 1, 12, 31
    giw__nuir = poype__bxj == 3 and (lrr__qvgw != 24 or ssysn__iwj == 3)
    month = n + 50 >> 5
    lnb__ypye = _DAYS_BEFORE_MONTH[month] + (month > 2 and giw__nuir)
    if lnb__ypye > n:
        month -= 1
        lnb__ypye -= _DAYS_IN_MONTH[month] + (month == 2 and giw__nuir)
    n -= lnb__ypye
    return year, month, n + 1


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@intrinsic
def get_isocalendar(typingctx, dt_year, dt_month, dt_day):

    def codegen(context, builder, sig, args):
        year = cgutils.alloca_once(builder, lir.IntType(64))
        kwdh__cqw = cgutils.alloca_once(builder, lir.IntType(64))
        hspnv__uzrrv = cgutils.alloca_once(builder, lir.IntType(64))
        hmnb__ubb = lir.FunctionType(lir.VoidType(), [lir.IntType(64), lir.
            IntType(64), lir.IntType(64), lir.IntType(64).as_pointer(), lir
            .IntType(64).as_pointer(), lir.IntType(64).as_pointer()])
        sayr__frcu = cgutils.get_or_insert_function(builder.module,
            hmnb__ubb, name='get_isocalendar')
        builder.call(sayr__frcu, [args[0], args[1], args[2], year,
            kwdh__cqw, hspnv__uzrrv])
        return cgutils.pack_array(builder, [builder.load(year), builder.
            load(kwdh__cqw), builder.load(hspnv__uzrrv)])
    xae__bwi = types.Tuple([types.int64, types.int64, types.int64])(types.
        int64, types.int64, types.int64), codegen
    return xae__bwi


types.datetime_date_type = datetime_date_type


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_date_type'):
        d = datetime.date.today()
    return d


@register_jitable
def fromordinal_impl(n):
    y, ljg__jvwzx, d = _ord2ymd(n)
    return datetime.date(y, ljg__jvwzx, d)


@overload_method(DatetimeDateType, 'replace')
def replace_overload(date, year=None, month=None, day=None):
    if not is_overload_none(year) and not is_overload_int(year):
        raise BodoError('date.replace(): year must be an integer')
    elif not is_overload_none(month) and not is_overload_int(month):
        raise BodoError('date.replace(): month must be an integer')
    elif not is_overload_none(day) and not is_overload_int(day):
        raise BodoError('date.replace(): day must be an integer')

    def impl(date, year=None, month=None, day=None):
        gju__idn = date.year if year is None else year
        zzdbx__awmi = date.month if month is None else month
        hgjmb__tyifc = date.day if day is None else day
        return datetime.date(gju__idn, zzdbx__awmi, hgjmb__tyifc)
    return impl


@overload_method(DatetimeDatetimeType, 'toordinal', no_unliteral=True)
@overload_method(DatetimeDateType, 'toordinal', no_unliteral=True)
def toordinal(date):

    def impl(date):
        return _ymd2ord(date.year, date.month, date.day)
    return impl


@overload_method(DatetimeDatetimeType, 'weekday', no_unliteral=True)
@overload_method(DatetimeDateType, 'weekday', no_unliteral=True)
def weekday(date):

    def impl(date):
        return (date.toordinal() + 6) % 7
    return impl


@overload_method(DatetimeDateType, 'isocalendar', no_unliteral=True)
def overload_pd_timestamp_isocalendar(date):

    def impl(date):
        year, kwdh__cqw, xegqd__xekpm = get_isocalendar(date.year, date.
            month, date.day)
        return year, kwdh__cqw, xegqd__xekpm
    return impl


def overload_add_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ghjxi__ucmwm = lhs.toordinal() + rhs.days
            if 0 < ghjxi__ucmwm <= _MAXORDINAL:
                return fromordinal_impl(ghjxi__ucmwm)
            raise OverflowError('result out of range')
        return impl
    elif lhs == datetime_timedelta_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            ghjxi__ucmwm = lhs.days + rhs.toordinal()
            if 0 < ghjxi__ucmwm <= _MAXORDINAL:
                return fromordinal_impl(ghjxi__ucmwm)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + datetime.timedelta(-rhs.days)
        return impl
    elif lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            strg__rsk = lhs.toordinal()
            bsa__piq = rhs.toordinal()
            return datetime.timedelta(strg__rsk - bsa__piq)
        return impl
    if lhs == datetime_date_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            xfh__nnjs = lhs
            numba.parfors.parfor.init_prange()
            n = len(xfh__nnjs)
            A = alloc_datetime_date_array(n)
            for zylyf__xkmra in numba.parfors.parfor.internal_prange(n):
                A[zylyf__xkmra] = xfh__nnjs[zylyf__xkmra] - rhs
            return A
        return impl


@overload(min, no_unliteral=True)
def date_min(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@overload(max, no_unliteral=True)
def date_max(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload_method(DatetimeDateType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        owgq__cglap = np.uint8(td.year // 256)
        rpunv__jvbh = np.uint8(td.year % 256)
        month = np.uint8(td.month)
        day = np.uint8(td.day)
        ildzu__ckgxd = owgq__cglap, rpunv__jvbh, month, day
        return hash(ildzu__ckgxd)
    return impl


@overload(bool, inline='always', no_unliteral=True)
def date_to_bool(date):
    if date != datetime_date_type:
        return

    def impl(date):
        return True
    return impl


if PYVERSION >= (3, 9):
    IsoCalendarDate = datetime.date(2011, 1, 1).isocalendar().__class__


    class IsoCalendarDateType(types.Type):

        def __init__(self):
            super(IsoCalendarDateType, self).__init__(name=
                'IsoCalendarDateType()')
    iso_calendar_date_type = DatetimeDateType()

    @typeof_impl.register(IsoCalendarDate)
    def typeof_datetime_date(val, c):
        return iso_calendar_date_type


class DatetimeDateArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeDateArrayType, self).__init__(name=
            'DatetimeDateArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_date_type

    def copy(self):
        return DatetimeDateArrayType()


datetime_date_array_type = DatetimeDateArrayType()
types.datetime_date_array_type = datetime_date_array_type
data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeDateArrayType)
class DatetimeDateArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ximw__sgxtm = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ximw__sgxtm)


make_attribute_wrapper(DatetimeDateArrayType, 'data', '_data')
make_attribute_wrapper(DatetimeDateArrayType, 'null_bitmap', '_null_bitmap')


@overload_method(DatetimeDateArrayType, 'copy', no_unliteral=True)
def overload_datetime_date_arr_copy(A):
    return lambda A: bodo.hiframes.datetime_date_ext.init_datetime_date_array(A
        ._data.copy(), A._null_bitmap.copy())


@overload_attribute(DatetimeDateArrayType, 'dtype')
def overload_datetime_date_arr_dtype(A):
    return lambda A: np.object_


@unbox(DatetimeDateArrayType)
def unbox_datetime_date_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    wypub__ioci = types.Array(types.intp, 1, 'C')
    vdpkx__faz = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        wypub__ioci, [n])
    cmv__grmu = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    mgxe__rlrq = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [cmv__grmu])
    hmnb__ubb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer()])
    ffb__jitr = cgutils.get_or_insert_function(c.builder.module, hmnb__ubb,
        name='unbox_datetime_date_array')
    c.builder.call(ffb__jitr, [val, n, vdpkx__faz.data, mgxe__rlrq.data])
    itdrg__szqm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    itdrg__szqm.data = vdpkx__faz._getvalue()
    itdrg__szqm.null_bitmap = mgxe__rlrq._getvalue()
    eplp__sxrit = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(itdrg__szqm._getvalue(), is_error=eplp__sxrit)


def int_to_datetime_date_python(ia):
    return datetime.date(ia >> 32, ia >> 16 & 65535, ia & 65535)


def int_array_to_datetime_date(ia):
    return np.vectorize(int_to_datetime_date_python, otypes=[object])(ia)


@box(DatetimeDateArrayType)
def box_datetime_date_array(typ, val, c):
    xfh__nnjs = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    vdpkx__faz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xfh__nnjs.data)
    qwzo__yyt = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, xfh__nnjs.null_bitmap).data
    n = c.builder.extract_value(vdpkx__faz.shape, 0)
    hmnb__ubb = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(8).as_pointer()])
    zqti__zjjf = cgutils.get_or_insert_function(c.builder.module, hmnb__ubb,
        name='box_datetime_date_array')
    hvs__vmdl = c.builder.call(zqti__zjjf, [n, vdpkx__faz.data, qwzo__yyt])
    c.context.nrt.decref(c.builder, typ, val)
    return hvs__vmdl


@intrinsic
def init_datetime_date_array(typingctx, data, nulls=None):
    assert data == types.Array(types.int64, 1, 'C') or data == types.Array(
        types.NPDatetime('ns'), 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        pfva__jjtod, lcfut__vuou = args
        edcr__nehj = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        edcr__nehj.data = pfva__jjtod
        edcr__nehj.null_bitmap = lcfut__vuou
        context.nrt.incref(builder, signature.args[0], pfva__jjtod)
        context.nrt.incref(builder, signature.args[1], lcfut__vuou)
        return edcr__nehj._getvalue()
    sig = datetime_date_array_type(data, nulls)
    return sig, codegen


@lower_constant(DatetimeDateArrayType)
def lower_constant_datetime_date_arr(context, builder, typ, pyval):
    n = len(pyval)
    rmvy__pau = (1970 << 32) + (1 << 16) + 1
    vdpkx__faz = np.full(n, rmvy__pau, np.int64)
    pshor__mlbvf = np.empty(n + 7 >> 3, np.uint8)
    for zylyf__xkmra, effe__mhe in enumerate(pyval):
        egsx__ioyv = pd.isna(effe__mhe)
        bodo.libs.int_arr_ext.set_bit_to_arr(pshor__mlbvf, zylyf__xkmra,
            int(not egsx__ioyv))
        if not egsx__ioyv:
            vdpkx__faz[zylyf__xkmra] = (effe__mhe.year << 32) + (effe__mhe.
                month << 16) + effe__mhe.day
    meg__qix = context.get_constant_generic(builder, data_type, vdpkx__faz)
    geaum__shuc = context.get_constant_generic(builder, nulls_type,
        pshor__mlbvf)
    return lir.Constant.literal_struct([meg__qix, geaum__shuc])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_date_array(n):
    vdpkx__faz = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_date_array(vdpkx__faz, nulls)


def alloc_datetime_date_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_date_ext_alloc_datetime_date_array
    ) = alloc_datetime_date_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_date_arr_getitem(A, ind):
    if A != datetime_date_array_type:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: cast_int_to_datetime_date(A._data[ind])
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            sjmvl__erzx, scq__tbr = array_getitem_bool_index(A, ind)
            return init_datetime_date_array(sjmvl__erzx, scq__tbr)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            sjmvl__erzx, scq__tbr = array_getitem_int_index(A, ind)
            return init_datetime_date_array(sjmvl__erzx, scq__tbr)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            sjmvl__erzx, scq__tbr = array_getitem_slice_index(A, ind)
            return init_datetime_date_array(sjmvl__erzx, scq__tbr)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeDateArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_date_arr_setitem(A, idx, val):
    if A != datetime_date_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    mpcib__uuoc = (
        f"setitem for DatetimeDateArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == datetime_date_type:

            def impl(A, idx, val):
                A._data[idx] = cast_datetime_date_to_int(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl
        else:
            raise BodoError(mpcib__uuoc)
    if not (is_iterable_type(val) and val.dtype == bodo.datetime_date_type or
        types.unliteral(val) == datetime_date_type):
        raise BodoError(mpcib__uuoc)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_int_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_arr_ind(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_bool_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_slice_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeDateArray with indexing type {idx} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_date_arr(A):
    if A == datetime_date_array_type:
        return lambda A: len(A._data)


@overload_attribute(DatetimeDateArrayType, 'shape')
def overload_datetime_date_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(DatetimeDateArrayType, 'nbytes')
def datetime_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


def create_cmp_op_overload(op):

    def overload_date_cmp(lhs, rhs):
        if lhs == datetime_date_type and rhs == datetime_date_type:

            def impl(lhs, rhs):
                y, hjjux__bticd = lhs.year, rhs.year
                ljg__jvwzx, umkxr__iysmt = lhs.month, rhs.month
                d, kqmov__otuv = lhs.day, rhs.day
                return op(_cmp((y, ljg__jvwzx, d), (hjjux__bticd,
                    umkxr__iysmt, kqmov__otuv)), 0)
            return impl
    return overload_date_cmp


def create_datetime_date_cmp_op_overload(op):

    def overload_cmp(lhs, rhs):
        ron__yzvhp = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[op]} {rhs} is always {op == operator.ne} in Python. If this is unexpected there may be a bug in your code.'
            )
        warnings.warn(ron__yzvhp, bodo.utils.typing.BodoWarning)
        if op == operator.eq:
            return lambda lhs, rhs: False
        elif op == operator.ne:
            return lambda lhs, rhs: True
    return overload_cmp


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            abd__nhtus = True
        else:
            abd__nhtus = False
        if lhs == datetime_date_array_type and rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                fnpb__axsgg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for zylyf__xkmra in numba.parfors.parfor.internal_prange(n):
                    hckt__sns = bodo.libs.array_kernels.isna(lhs, zylyf__xkmra)
                    wltx__yhmsg = bodo.libs.array_kernels.isna(rhs,
                        zylyf__xkmra)
                    if hckt__sns or wltx__yhmsg:
                        vxod__hfcw = abd__nhtus
                    else:
                        vxod__hfcw = op(lhs[zylyf__xkmra], rhs[zylyf__xkmra])
                    fnpb__axsgg[zylyf__xkmra] = vxod__hfcw
                return fnpb__axsgg
            return impl
        elif lhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                fnpb__axsgg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for zylyf__xkmra in numba.parfors.parfor.internal_prange(n):
                    qfev__dpk = bodo.libs.array_kernels.isna(lhs, zylyf__xkmra)
                    if qfev__dpk:
                        vxod__hfcw = abd__nhtus
                    else:
                        vxod__hfcw = op(lhs[zylyf__xkmra], rhs)
                    fnpb__axsgg[zylyf__xkmra] = vxod__hfcw
                return fnpb__axsgg
            return impl
        elif rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                fnpb__axsgg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for zylyf__xkmra in numba.parfors.parfor.internal_prange(n):
                    qfev__dpk = bodo.libs.array_kernels.isna(rhs, zylyf__xkmra)
                    if qfev__dpk:
                        vxod__hfcw = abd__nhtus
                    else:
                        vxod__hfcw = op(lhs, rhs[zylyf__xkmra])
                    fnpb__axsgg[zylyf__xkmra] = vxod__hfcw
                return fnpb__axsgg
            return impl
    return overload_date_arr_cmp
