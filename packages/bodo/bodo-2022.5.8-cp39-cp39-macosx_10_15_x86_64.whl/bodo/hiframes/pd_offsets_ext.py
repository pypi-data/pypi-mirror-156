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
        wlk__lrj = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, wlk__lrj)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    tplay__xri = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ntj__sqlup = c.pyapi.long_from_longlong(tplay__xri.n)
    okomx__bmbxh = c.pyapi.from_native_value(types.boolean, tplay__xri.
        normalize, c.env_manager)
    olj__xmgqp = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    ronb__dhtjz = c.pyapi.call_function_objargs(olj__xmgqp, (ntj__sqlup,
        okomx__bmbxh))
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    c.pyapi.decref(olj__xmgqp)
    return ronb__dhtjz


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    ntj__sqlup = c.pyapi.object_getattr_string(val, 'n')
    okomx__bmbxh = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ntj__sqlup)
    normalize = c.pyapi.to_native_value(types.bool_, okomx__bmbxh).value
    tplay__xri = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tplay__xri.n = n
    tplay__xri.normalize = normalize
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    tcq__sgir = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tplay__xri._getvalue(), is_error=tcq__sgir)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        tplay__xri = cgutils.create_struct_proxy(typ)(context, builder)
        tplay__xri.n = args[0]
        tplay__xri.normalize = args[1]
        return tplay__xri._getvalue()
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
        wlk__lrj = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, wlk__lrj)


@box(MonthEndType)
def box_month_end(typ, val, c):
    ifu__iktp = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ntj__sqlup = c.pyapi.long_from_longlong(ifu__iktp.n)
    okomx__bmbxh = c.pyapi.from_native_value(types.boolean, ifu__iktp.
        normalize, c.env_manager)
    rbg__wzujl = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    ronb__dhtjz = c.pyapi.call_function_objargs(rbg__wzujl, (ntj__sqlup,
        okomx__bmbxh))
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    c.pyapi.decref(rbg__wzujl)
    return ronb__dhtjz


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    ntj__sqlup = c.pyapi.object_getattr_string(val, 'n')
    okomx__bmbxh = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ntj__sqlup)
    normalize = c.pyapi.to_native_value(types.bool_, okomx__bmbxh).value
    ifu__iktp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ifu__iktp.n = n
    ifu__iktp.normalize = normalize
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    tcq__sgir = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ifu__iktp._getvalue(), is_error=tcq__sgir)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        ifu__iktp = cgutils.create_struct_proxy(typ)(context, builder)
        ifu__iktp.n = args[0]
        ifu__iktp.normalize = args[1]
        return ifu__iktp._getvalue()
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
        ifu__iktp = get_days_in_month(year, month)
        if ifu__iktp > day:
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
        wlk__lrj = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, wlk__lrj)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    eekj__swn = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mrtlj__cluc = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for qsgc__woz, tktkc__ooypd in enumerate(date_offset_fields):
        c.builder.store(getattr(eekj__swn, tktkc__ooypd), c.builder.
            inttoptr(c.builder.add(c.builder.ptrtoint(mrtlj__cluc, lir.
            IntType(64)), lir.Constant(lir.IntType(64), 8 * qsgc__woz)),
            lir.IntType(64).as_pointer()))
    khge__qjn = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    pgxs__dafov = cgutils.get_or_insert_function(c.builder.module,
        khge__qjn, name='box_date_offset')
    tbsy__nmlb = c.builder.call(pgxs__dafov, [eekj__swn.n, eekj__swn.
        normalize, mrtlj__cluc, eekj__swn.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return tbsy__nmlb


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    ntj__sqlup = c.pyapi.object_getattr_string(val, 'n')
    okomx__bmbxh = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ntj__sqlup)
    normalize = c.pyapi.to_native_value(types.bool_, okomx__bmbxh).value
    mrtlj__cluc = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    khge__qjn = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    odra__cqxl = cgutils.get_or_insert_function(c.builder.module, khge__qjn,
        name='unbox_date_offset')
    has_kws = c.builder.call(odra__cqxl, [val, mrtlj__cluc])
    eekj__swn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    eekj__swn.n = n
    eekj__swn.normalize = normalize
    for qsgc__woz, tktkc__ooypd in enumerate(date_offset_fields):
        setattr(eekj__swn, tktkc__ooypd, c.builder.load(c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(mrtlj__cluc, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * qsgc__woz)), lir.IntType(64).
            as_pointer())))
    eekj__swn.has_kws = has_kws
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    tcq__sgir = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(eekj__swn._getvalue(), is_error=tcq__sgir)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    dvp__luod = [n, normalize]
    has_kws = False
    drq__kmkon = [0] * 9 + [-1] * 9
    for qsgc__woz, tktkc__ooypd in enumerate(date_offset_fields):
        if hasattr(pyval, tktkc__ooypd):
            qae__qch = context.get_constant(types.int64, getattr(pyval,
                tktkc__ooypd))
            has_kws = True
        else:
            qae__qch = context.get_constant(types.int64, drq__kmkon[qsgc__woz])
        dvp__luod.append(qae__qch)
    has_kws = context.get_constant(types.boolean, has_kws)
    dvp__luod.append(has_kws)
    return lir.Constant.literal_struct(dvp__luod)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    zqnor__kso = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for zzuuv__hhr in zqnor__kso:
        if not is_overload_none(zzuuv__hhr):
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
        eekj__swn = cgutils.create_struct_proxy(typ)(context, builder)
        eekj__swn.n = args[0]
        eekj__swn.normalize = args[1]
        eekj__swn.years = args[2]
        eekj__swn.months = args[3]
        eekj__swn.weeks = args[4]
        eekj__swn.days = args[5]
        eekj__swn.hours = args[6]
        eekj__swn.minutes = args[7]
        eekj__swn.seconds = args[8]
        eekj__swn.microseconds = args[9]
        eekj__swn.nanoseconds = args[10]
        eekj__swn.year = args[11]
        eekj__swn.month = args[12]
        eekj__swn.day = args[13]
        eekj__swn.weekday = args[14]
        eekj__swn.hour = args[15]
        eekj__swn.minute = args[16]
        eekj__swn.second = args[17]
        eekj__swn.microsecond = args[18]
        eekj__swn.nanosecond = args[19]
        eekj__swn.has_kws = args[20]
        return eekj__swn._getvalue()
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
        lrjbc__wec = -1 if dateoffset.n < 0 else 1
        for zrabo__tef in range(np.abs(dateoffset.n)):
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
            year += lrjbc__wec * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += lrjbc__wec * dateoffset._months
            year, month, abys__das = calculate_month_end_date(year, month,
                day, 0)
            if day > abys__das:
                day = abys__das
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
            btccp__jyzkj = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            btccp__jyzkj = btccp__jyzkj + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if lrjbc__wec == -1:
                btccp__jyzkj = -btccp__jyzkj
            ts = ts + btccp__jyzkj
            if dateoffset._weekday != -1:
                ust__lkuw = ts.weekday()
                oaoaa__aub = (dateoffset._weekday - ust__lkuw) % 7
                ts = ts + pd.Timedelta(days=oaoaa__aub)
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
        wlk__lrj = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, wlk__lrj)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        ikft__kmu = -1 if weekday is None else weekday
        return init_week(n, normalize, ikft__kmu)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        hrjdy__hou = cgutils.create_struct_proxy(typ)(context, builder)
        hrjdy__hou.n = args[0]
        hrjdy__hou.normalize = args[1]
        hrjdy__hou.weekday = args[2]
        return hrjdy__hou._getvalue()
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
    hrjdy__hou = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ntj__sqlup = c.pyapi.long_from_longlong(hrjdy__hou.n)
    okomx__bmbxh = c.pyapi.from_native_value(types.boolean, hrjdy__hou.
        normalize, c.env_manager)
    mhj__epy = c.pyapi.long_from_longlong(hrjdy__hou.weekday)
    xkcvn__anoy = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    pmxmn__milt = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), hrjdy__hou.weekday)
    with c.builder.if_else(pmxmn__milt) as (kyhb__qgbw, farme__nkl):
        with kyhb__qgbw:
            ffpi__obj = c.pyapi.call_function_objargs(xkcvn__anoy, (
                ntj__sqlup, okomx__bmbxh, mhj__epy))
            ula__jpob = c.builder.block
        with farme__nkl:
            yms__oqbgr = c.pyapi.call_function_objargs(xkcvn__anoy, (
                ntj__sqlup, okomx__bmbxh))
            zqm__kmh = c.builder.block
    ronb__dhtjz = c.builder.phi(ffpi__obj.type)
    ronb__dhtjz.add_incoming(ffpi__obj, ula__jpob)
    ronb__dhtjz.add_incoming(yms__oqbgr, zqm__kmh)
    c.pyapi.decref(mhj__epy)
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    c.pyapi.decref(xkcvn__anoy)
    return ronb__dhtjz


@unbox(WeekType)
def unbox_week(typ, val, c):
    ntj__sqlup = c.pyapi.object_getattr_string(val, 'n')
    okomx__bmbxh = c.pyapi.object_getattr_string(val, 'normalize')
    mhj__epy = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(ntj__sqlup)
    normalize = c.pyapi.to_native_value(types.bool_, okomx__bmbxh).value
    kexvi__sifk = c.pyapi.make_none()
    akfs__pqiy = c.builder.icmp_unsigned('==', mhj__epy, kexvi__sifk)
    with c.builder.if_else(akfs__pqiy) as (farme__nkl, kyhb__qgbw):
        with kyhb__qgbw:
            ffpi__obj = c.pyapi.long_as_longlong(mhj__epy)
            ula__jpob = c.builder.block
        with farme__nkl:
            yms__oqbgr = lir.Constant(lir.IntType(64), -1)
            zqm__kmh = c.builder.block
    ronb__dhtjz = c.builder.phi(ffpi__obj.type)
    ronb__dhtjz.add_incoming(ffpi__obj, ula__jpob)
    ronb__dhtjz.add_incoming(yms__oqbgr, zqm__kmh)
    hrjdy__hou = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hrjdy__hou.n = n
    hrjdy__hou.normalize = normalize
    hrjdy__hou.weekday = ronb__dhtjz
    c.pyapi.decref(ntj__sqlup)
    c.pyapi.decref(okomx__bmbxh)
    c.pyapi.decref(mhj__epy)
    tcq__sgir = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hrjdy__hou._getvalue(), is_error=tcq__sgir)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            zoukl__ymja = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                nbu__hlx = pd.Timestamp(year=rhs.year, month=rhs.month, day
                    =rhs.day)
            else:
                nbu__hlx = rhs
            return nbu__hlx + zoukl__ymja
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            zoukl__ymja = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                nbu__hlx = pd.Timestamp(year=rhs.year, month=rhs.month, day
                    =rhs.day)
            else:
                nbu__hlx = pd.Timestamp(year=rhs.year, month=rhs.month, day
                    =rhs.day, hour=rhs.hour, minute=rhs.minute, second=rhs.
                    second, microsecond=rhs.microsecond)
            return nbu__hlx + zoukl__ymja
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            zoukl__ymja = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            return rhs + zoukl__ymja
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
        efru__osbg = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=efru__osbg)


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
    for vvpd__xwjk in date_offset_unsupported_attrs:
        qfy__cpaz = 'pandas.tseries.offsets.DateOffset.' + vvpd__xwjk
        overload_attribute(DateOffsetType, vvpd__xwjk)(
            create_unsupported_overload(qfy__cpaz))
    for vvpd__xwjk in date_offset_unsupported:
        qfy__cpaz = 'pandas.tseries.offsets.DateOffset.' + vvpd__xwjk
        overload_method(DateOffsetType, vvpd__xwjk)(create_unsupported_overload
            (qfy__cpaz))


def _install_month_begin_unsupported():
    for vvpd__xwjk in month_begin_unsupported_attrs:
        qfy__cpaz = 'pandas.tseries.offsets.MonthBegin.' + vvpd__xwjk
        overload_attribute(MonthBeginType, vvpd__xwjk)(
            create_unsupported_overload(qfy__cpaz))
    for vvpd__xwjk in month_begin_unsupported:
        qfy__cpaz = 'pandas.tseries.offsets.MonthBegin.' + vvpd__xwjk
        overload_method(MonthBeginType, vvpd__xwjk)(create_unsupported_overload
            (qfy__cpaz))


def _install_month_end_unsupported():
    for vvpd__xwjk in date_offset_unsupported_attrs:
        qfy__cpaz = 'pandas.tseries.offsets.MonthEnd.' + vvpd__xwjk
        overload_attribute(MonthEndType, vvpd__xwjk)(
            create_unsupported_overload(qfy__cpaz))
    for vvpd__xwjk in date_offset_unsupported:
        qfy__cpaz = 'pandas.tseries.offsets.MonthEnd.' + vvpd__xwjk
        overload_method(MonthEndType, vvpd__xwjk)(create_unsupported_overload
            (qfy__cpaz))


def _install_week_unsupported():
    for vvpd__xwjk in week_unsupported_attrs:
        qfy__cpaz = 'pandas.tseries.offsets.Week.' + vvpd__xwjk
        overload_attribute(WeekType, vvpd__xwjk)(create_unsupported_overload
            (qfy__cpaz))
    for vvpd__xwjk in week_unsupported:
        qfy__cpaz = 'pandas.tseries.offsets.Week.' + vvpd__xwjk
        overload_method(WeekType, vvpd__xwjk)(create_unsupported_overload(
            qfy__cpaz))


def _install_offsets_unsupported():
    for qae__qch in offsets_unsupported:
        qfy__cpaz = 'pandas.tseries.offsets.' + qae__qch.__name__
        overload(qae__qch)(create_unsupported_overload(qfy__cpaz))


def _install_frequencies_unsupported():
    for qae__qch in frequencies_unsupported:
        qfy__cpaz = 'pandas.tseries.frequencies.' + qae__qch.__name__
        overload(qae__qch)(create_unsupported_overload(qfy__cpaz))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
