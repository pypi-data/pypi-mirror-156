import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        caf__puvm = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, caf__puvm)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    tzrn__zucyp = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    qqkg__wjli = c.pyapi.long_from_longlong(tzrn__zucyp.year)
    yvl__gbk = c.pyapi.long_from_longlong(tzrn__zucyp.month)
    boxy__xfqir = c.pyapi.long_from_longlong(tzrn__zucyp.day)
    qmjk__rku = c.pyapi.long_from_longlong(tzrn__zucyp.hour)
    eeyt__advm = c.pyapi.long_from_longlong(tzrn__zucyp.minute)
    mjzw__vbxj = c.pyapi.long_from_longlong(tzrn__zucyp.second)
    sqei__rvmjm = c.pyapi.long_from_longlong(tzrn__zucyp.microsecond)
    clk__wdu = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.datetime))
    ijfa__cqxms = c.pyapi.call_function_objargs(clk__wdu, (qqkg__wjli,
        yvl__gbk, boxy__xfqir, qmjk__rku, eeyt__advm, mjzw__vbxj, sqei__rvmjm))
    c.pyapi.decref(qqkg__wjli)
    c.pyapi.decref(yvl__gbk)
    c.pyapi.decref(boxy__xfqir)
    c.pyapi.decref(qmjk__rku)
    c.pyapi.decref(eeyt__advm)
    c.pyapi.decref(mjzw__vbxj)
    c.pyapi.decref(sqei__rvmjm)
    c.pyapi.decref(clk__wdu)
    return ijfa__cqxms


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    qqkg__wjli = c.pyapi.object_getattr_string(val, 'year')
    yvl__gbk = c.pyapi.object_getattr_string(val, 'month')
    boxy__xfqir = c.pyapi.object_getattr_string(val, 'day')
    qmjk__rku = c.pyapi.object_getattr_string(val, 'hour')
    eeyt__advm = c.pyapi.object_getattr_string(val, 'minute')
    mjzw__vbxj = c.pyapi.object_getattr_string(val, 'second')
    sqei__rvmjm = c.pyapi.object_getattr_string(val, 'microsecond')
    tzrn__zucyp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tzrn__zucyp.year = c.pyapi.long_as_longlong(qqkg__wjli)
    tzrn__zucyp.month = c.pyapi.long_as_longlong(yvl__gbk)
    tzrn__zucyp.day = c.pyapi.long_as_longlong(boxy__xfqir)
    tzrn__zucyp.hour = c.pyapi.long_as_longlong(qmjk__rku)
    tzrn__zucyp.minute = c.pyapi.long_as_longlong(eeyt__advm)
    tzrn__zucyp.second = c.pyapi.long_as_longlong(mjzw__vbxj)
    tzrn__zucyp.microsecond = c.pyapi.long_as_longlong(sqei__rvmjm)
    c.pyapi.decref(qqkg__wjli)
    c.pyapi.decref(yvl__gbk)
    c.pyapi.decref(boxy__xfqir)
    c.pyapi.decref(qmjk__rku)
    c.pyapi.decref(eeyt__advm)
    c.pyapi.decref(mjzw__vbxj)
    c.pyapi.decref(sqei__rvmjm)
    wjak__eqfy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tzrn__zucyp._getvalue(), is_error=wjak__eqfy)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        tzrn__zucyp = cgutils.create_struct_proxy(typ)(context, builder)
        tzrn__zucyp.year = args[0]
        tzrn__zucyp.month = args[1]
        tzrn__zucyp.day = args[2]
        tzrn__zucyp.hour = args[3]
        tzrn__zucyp.minute = args[4]
        tzrn__zucyp.second = args[5]
        tzrn__zucyp.microsecond = args[6]
        return tzrn__zucyp._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, hsmw__tfo = lhs.year, rhs.year
                ikls__qjru, fkh__ggo = lhs.month, rhs.month
                d, gmqfp__csu = lhs.day, rhs.day
                rqbgt__ugfic, evll__sghsx = lhs.hour, rhs.hour
                nqq__dgyjh, gsv__gnuu = lhs.minute, rhs.minute
                jfz__tyzxh, anivo__bxr = lhs.second, rhs.second
                tnsie__qjskk, ntmy__lydz = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, ikls__qjru, d, rqbgt__ugfic, nqq__dgyjh,
                    jfz__tyzxh, tnsie__qjskk), (hsmw__tfo, fkh__ggo,
                    gmqfp__csu, evll__sghsx, gsv__gnuu, anivo__bxr,
                    ntmy__lydz)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            jttr__caol = lhs.toordinal()
            fryx__vuq = rhs.toordinal()
            ias__eiz = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            hdji__xwuf = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            enpuh__mgels = datetime.timedelta(jttr__caol - fryx__vuq, 
                ias__eiz - hdji__xwuf, lhs.microsecond - rhs.microsecond)
            return enpuh__mgels
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    qkich__ede = context.make_helper(builder, fromty, value=val)
    polf__turul = cgutils.as_bool_bit(builder, qkich__ede.valid)
    with builder.if_else(polf__turul) as (fqok__fwciq, dkwox__sbdkl):
        with fqok__fwciq:
            mvu__nyk = context.cast(builder, qkich__ede.data, fromty.type, toty
                )
            aagkb__ualj = builder.block
        with dkwox__sbdkl:
            zry__uugtc = numba.np.npdatetime.NAT
            rle__use = builder.block
    ijfa__cqxms = builder.phi(mvu__nyk.type)
    ijfa__cqxms.add_incoming(mvu__nyk, aagkb__ualj)
    ijfa__cqxms.add_incoming(zry__uugtc, rle__use)
    return ijfa__cqxms
