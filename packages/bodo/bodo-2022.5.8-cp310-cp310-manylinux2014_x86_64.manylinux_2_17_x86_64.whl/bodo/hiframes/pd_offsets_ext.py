"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        urgjj__citt = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, urgjj__citt)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    iwe__pup = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    lyct__wsdua = c.pyapi.long_from_longlong(iwe__pup.n)
    utvju__vnxiw = c.pyapi.from_native_value(types.boolean, iwe__pup.
        normalize, c.env_manager)
    oioal__sfxxl = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    uxfez__vne = c.pyapi.call_function_objargs(oioal__sfxxl, (lyct__wsdua,
        utvju__vnxiw))
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    c.pyapi.decref(oioal__sfxxl)
    return uxfez__vne


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    lyct__wsdua = c.pyapi.object_getattr_string(val, 'n')
    utvju__vnxiw = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(lyct__wsdua)
    normalize = c.pyapi.to_native_value(types.bool_, utvju__vnxiw).value
    iwe__pup = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    iwe__pup.n = n
    iwe__pup.normalize = normalize
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    ruqd__xzevn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iwe__pup._getvalue(), is_error=ruqd__xzevn)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        iwe__pup = cgutils.create_struct_proxy(typ)(context, builder)
        iwe__pup.n = args[0]
        iwe__pup.normalize = args[1]
        return iwe__pup._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        urgjj__citt = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, urgjj__citt)


@box(MonthEndType)
def box_month_end(typ, val, c):
    yxwe__odedr = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    lyct__wsdua = c.pyapi.long_from_longlong(yxwe__odedr.n)
    utvju__vnxiw = c.pyapi.from_native_value(types.boolean, yxwe__odedr.
        normalize, c.env_manager)
    xlo__jssi = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    uxfez__vne = c.pyapi.call_function_objargs(xlo__jssi, (lyct__wsdua,
        utvju__vnxiw))
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    c.pyapi.decref(xlo__jssi)
    return uxfez__vne


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    lyct__wsdua = c.pyapi.object_getattr_string(val, 'n')
    utvju__vnxiw = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(lyct__wsdua)
    normalize = c.pyapi.to_native_value(types.bool_, utvju__vnxiw).value
    yxwe__odedr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxwe__odedr.n = n
    yxwe__odedr.normalize = normalize
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    ruqd__xzevn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(yxwe__odedr._getvalue(), is_error=ruqd__xzevn)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        yxwe__odedr = cgutils.create_struct_proxy(typ)(context, builder)
        yxwe__odedr.n = args[0]
        yxwe__odedr.normalize = args[1]
        return yxwe__odedr._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        yxwe__odedr = get_days_in_month(year, month)
        if yxwe__odedr > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        urgjj__citt = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, urgjj__citt)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    tyrmr__vkfrs = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    adhs__mzt = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for jkyzl__khqfq, spcg__zlk in enumerate(date_offset_fields):
        c.builder.store(getattr(tyrmr__vkfrs, spcg__zlk), c.builder.
            inttoptr(c.builder.add(c.builder.ptrtoint(adhs__mzt, lir.
            IntType(64)), lir.Constant(lir.IntType(64), 8 * jkyzl__khqfq)),
            lir.IntType(64).as_pointer()))
    syqju__xbjup = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    bebo__mtl = cgutils.get_or_insert_function(c.builder.module,
        syqju__xbjup, name='box_date_offset')
    kaxj__skxsy = c.builder.call(bebo__mtl, [tyrmr__vkfrs.n, tyrmr__vkfrs.
        normalize, adhs__mzt, tyrmr__vkfrs.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return kaxj__skxsy


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    lyct__wsdua = c.pyapi.object_getattr_string(val, 'n')
    utvju__vnxiw = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(lyct__wsdua)
    normalize = c.pyapi.to_native_value(types.bool_, utvju__vnxiw).value
    adhs__mzt = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    syqju__xbjup = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    qlrn__xuqxl = cgutils.get_or_insert_function(c.builder.module,
        syqju__xbjup, name='unbox_date_offset')
    has_kws = c.builder.call(qlrn__xuqxl, [val, adhs__mzt])
    tyrmr__vkfrs = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tyrmr__vkfrs.n = n
    tyrmr__vkfrs.normalize = normalize
    for jkyzl__khqfq, spcg__zlk in enumerate(date_offset_fields):
        setattr(tyrmr__vkfrs, spcg__zlk, c.builder.load(c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(adhs__mzt, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * jkyzl__khqfq)), lir.IntType(
            64).as_pointer())))
    tyrmr__vkfrs.has_kws = has_kws
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    ruqd__xzevn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tyrmr__vkfrs._getvalue(), is_error=ruqd__xzevn)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    mil__rztsr = [n, normalize]
    has_kws = False
    jbg__tazml = [0] * 9 + [-1] * 9
    for jkyzl__khqfq, spcg__zlk in enumerate(date_offset_fields):
        if hasattr(pyval, spcg__zlk):
            fjfb__mrv = context.get_constant(types.int64, getattr(pyval,
                spcg__zlk))
            has_kws = True
        else:
            fjfb__mrv = context.get_constant(types.int64, jbg__tazml[
                jkyzl__khqfq])
        mil__rztsr.append(fjfb__mrv)
    has_kws = context.get_constant(types.boolean, has_kws)
    mil__rztsr.append(has_kws)
    return lir.Constant.literal_struct(mil__rztsr)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    lzza__jllgv = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for vla__bapd in lzza__jllgv:
        if not is_overload_none(vla__bapd):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        tyrmr__vkfrs = cgutils.create_struct_proxy(typ)(context, builder)
        tyrmr__vkfrs.n = args[0]
        tyrmr__vkfrs.normalize = args[1]
        tyrmr__vkfrs.years = args[2]
        tyrmr__vkfrs.months = args[3]
        tyrmr__vkfrs.weeks = args[4]
        tyrmr__vkfrs.days = args[5]
        tyrmr__vkfrs.hours = args[6]
        tyrmr__vkfrs.minutes = args[7]
        tyrmr__vkfrs.seconds = args[8]
        tyrmr__vkfrs.microseconds = args[9]
        tyrmr__vkfrs.nanoseconds = args[10]
        tyrmr__vkfrs.year = args[11]
        tyrmr__vkfrs.month = args[12]
        tyrmr__vkfrs.day = args[13]
        tyrmr__vkfrs.weekday = args[14]
        tyrmr__vkfrs.hour = args[15]
        tyrmr__vkfrs.minute = args[16]
        tyrmr__vkfrs.second = args[17]
        tyrmr__vkfrs.microsecond = args[18]
        tyrmr__vkfrs.nanosecond = args[19]
        tyrmr__vkfrs.has_kws = args[20]
        return tyrmr__vkfrs._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        vix__rfigj = -1 if dateoffset.n < 0 else 1
        for evbh__dmf in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += vix__rfigj * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += vix__rfigj * dateoffset._months
            year, month, tnws__abye = calculate_month_end_date(year, month,
                day, 0)
            if day > tnws__abye:
                day = tnws__abye
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            if dateoffset._nanosecond != -1:
                nanosecond = dateoffset._nanosecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            xjdw__rwytg = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            xjdw__rwytg = xjdw__rwytg + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if vix__rfigj == -1:
                xjdw__rwytg = -xjdw__rwytg
            ts = ts + xjdw__rwytg
            if dateoffset._weekday != -1:
                uoxcx__ephv = ts.weekday()
                erumx__kuinc = (dateoffset._weekday - uoxcx__ephv) % 7
                ts = ts + pd.Timedelta(days=erumx__kuinc)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    elif lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    elif lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    elif lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    else:
        return
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        urgjj__citt = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, urgjj__citt)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        vgj__tcvyz = -1 if weekday is None else weekday
        return init_week(n, normalize, vgj__tcvyz)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        uttaw__hmhy = cgutils.create_struct_proxy(typ)(context, builder)
        uttaw__hmhy.n = args[0]
        uttaw__hmhy.normalize = args[1]
        uttaw__hmhy.weekday = args[2]
        return uttaw__hmhy._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    uttaw__hmhy = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    lyct__wsdua = c.pyapi.long_from_longlong(uttaw__hmhy.n)
    utvju__vnxiw = c.pyapi.from_native_value(types.boolean, uttaw__hmhy.
        normalize, c.env_manager)
    rto__htb = c.pyapi.long_from_longlong(uttaw__hmhy.weekday)
    suee__vrj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    zavq__nwq = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), -
        1), uttaw__hmhy.weekday)
    with c.builder.if_else(zavq__nwq) as (gnh__nucla, cus__yanl):
        with gnh__nucla:
            efywb__yhqyc = c.pyapi.call_function_objargs(suee__vrj, (
                lyct__wsdua, utvju__vnxiw, rto__htb))
            vegrd__tfyd = c.builder.block
        with cus__yanl:
            uwuq__wqmxi = c.pyapi.call_function_objargs(suee__vrj, (
                lyct__wsdua, utvju__vnxiw))
            myy__kpznn = c.builder.block
    uxfez__vne = c.builder.phi(efywb__yhqyc.type)
    uxfez__vne.add_incoming(efywb__yhqyc, vegrd__tfyd)
    uxfez__vne.add_incoming(uwuq__wqmxi, myy__kpznn)
    c.pyapi.decref(rto__htb)
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    c.pyapi.decref(suee__vrj)
    return uxfez__vne


@unbox(WeekType)
def unbox_week(typ, val, c):
    lyct__wsdua = c.pyapi.object_getattr_string(val, 'n')
    utvju__vnxiw = c.pyapi.object_getattr_string(val, 'normalize')
    rto__htb = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(lyct__wsdua)
    normalize = c.pyapi.to_native_value(types.bool_, utvju__vnxiw).value
    fxdn__nelu = c.pyapi.make_none()
    fmjlw__gqo = c.builder.icmp_unsigned('==', rto__htb, fxdn__nelu)
    with c.builder.if_else(fmjlw__gqo) as (cus__yanl, gnh__nucla):
        with gnh__nucla:
            efywb__yhqyc = c.pyapi.long_as_longlong(rto__htb)
            vegrd__tfyd = c.builder.block
        with cus__yanl:
            uwuq__wqmxi = lir.Constant(lir.IntType(64), -1)
            myy__kpznn = c.builder.block
    uxfez__vne = c.builder.phi(efywb__yhqyc.type)
    uxfez__vne.add_incoming(efywb__yhqyc, vegrd__tfyd)
    uxfez__vne.add_incoming(uwuq__wqmxi, myy__kpznn)
    uttaw__hmhy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uttaw__hmhy.n = n
    uttaw__hmhy.normalize = normalize
    uttaw__hmhy.weekday = uxfez__vne
    c.pyapi.decref(lyct__wsdua)
    c.pyapi.decref(utvju__vnxiw)
    c.pyapi.decref(rto__htb)
    ruqd__xzevn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uttaw__hmhy._getvalue(), is_error=ruqd__xzevn)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            nuym__wlcn = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                emmnc__moumz = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                emmnc__moumz = rhs
            return emmnc__moumz + nuym__wlcn
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            nuym__wlcn = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                emmnc__moumz = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                emmnc__moumz = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return emmnc__moumz + nuym__wlcn
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            nuym__wlcn = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + nuym__wlcn
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        dap__jcp = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=dap__jcp)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for flyhg__lsq in date_offset_unsupported_attrs:
        iwiud__gaer = 'pandas.tseries.offsets.DateOffset.' + flyhg__lsq
        overload_attribute(DateOffsetType, flyhg__lsq)(
            create_unsupported_overload(iwiud__gaer))
    for flyhg__lsq in date_offset_unsupported:
        iwiud__gaer = 'pandas.tseries.offsets.DateOffset.' + flyhg__lsq
        overload_method(DateOffsetType, flyhg__lsq)(create_unsupported_overload
            (iwiud__gaer))


def _install_month_begin_unsupported():
    for flyhg__lsq in month_begin_unsupported_attrs:
        iwiud__gaer = 'pandas.tseries.offsets.MonthBegin.' + flyhg__lsq
        overload_attribute(MonthBeginType, flyhg__lsq)(
            create_unsupported_overload(iwiud__gaer))
    for flyhg__lsq in month_begin_unsupported:
        iwiud__gaer = 'pandas.tseries.offsets.MonthBegin.' + flyhg__lsq
        overload_method(MonthBeginType, flyhg__lsq)(create_unsupported_overload
            (iwiud__gaer))


def _install_month_end_unsupported():
    for flyhg__lsq in date_offset_unsupported_attrs:
        iwiud__gaer = 'pandas.tseries.offsets.MonthEnd.' + flyhg__lsq
        overload_attribute(MonthEndType, flyhg__lsq)(
            create_unsupported_overload(iwiud__gaer))
    for flyhg__lsq in date_offset_unsupported:
        iwiud__gaer = 'pandas.tseries.offsets.MonthEnd.' + flyhg__lsq
        overload_method(MonthEndType, flyhg__lsq)(create_unsupported_overload
            (iwiud__gaer))


def _install_week_unsupported():
    for flyhg__lsq in week_unsupported_attrs:
        iwiud__gaer = 'pandas.tseries.offsets.Week.' + flyhg__lsq
        overload_attribute(WeekType, flyhg__lsq)(create_unsupported_overload
            (iwiud__gaer))
    for flyhg__lsq in week_unsupported:
        iwiud__gaer = 'pandas.tseries.offsets.Week.' + flyhg__lsq
        overload_method(WeekType, flyhg__lsq)(create_unsupported_overload(
            iwiud__gaer))


def _install_offsets_unsupported():
    for fjfb__mrv in offsets_unsupported:
        iwiud__gaer = 'pandas.tseries.offsets.' + fjfb__mrv.__name__
        overload(fjfb__mrv)(create_unsupported_overload(iwiud__gaer))


def _install_frequencies_unsupported():
    for fjfb__mrv in frequencies_unsupported:
        iwiud__gaer = 'pandas.tseries.frequencies.' + fjfb__mrv.__name__
        overload(fjfb__mrv)(create_unsupported_overload(iwiud__gaer))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
