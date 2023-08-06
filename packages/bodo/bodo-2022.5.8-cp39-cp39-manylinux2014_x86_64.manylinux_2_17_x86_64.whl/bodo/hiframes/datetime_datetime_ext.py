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
        dbene__zjab = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, dbene__zjab)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    djncf__bid = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mltrv__skazb = c.pyapi.long_from_longlong(djncf__bid.year)
    vpbvg__qdbc = c.pyapi.long_from_longlong(djncf__bid.month)
    qqai__vxm = c.pyapi.long_from_longlong(djncf__bid.day)
    tjjj__ekt = c.pyapi.long_from_longlong(djncf__bid.hour)
    nkibt__osydv = c.pyapi.long_from_longlong(djncf__bid.minute)
    kpoap__mxg = c.pyapi.long_from_longlong(djncf__bid.second)
    pynak__uwm = c.pyapi.long_from_longlong(djncf__bid.microsecond)
    whnth__wfzti = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    vei__houf = c.pyapi.call_function_objargs(whnth__wfzti, (mltrv__skazb,
        vpbvg__qdbc, qqai__vxm, tjjj__ekt, nkibt__osydv, kpoap__mxg,
        pynak__uwm))
    c.pyapi.decref(mltrv__skazb)
    c.pyapi.decref(vpbvg__qdbc)
    c.pyapi.decref(qqai__vxm)
    c.pyapi.decref(tjjj__ekt)
    c.pyapi.decref(nkibt__osydv)
    c.pyapi.decref(kpoap__mxg)
    c.pyapi.decref(pynak__uwm)
    c.pyapi.decref(whnth__wfzti)
    return vei__houf


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    mltrv__skazb = c.pyapi.object_getattr_string(val, 'year')
    vpbvg__qdbc = c.pyapi.object_getattr_string(val, 'month')
    qqai__vxm = c.pyapi.object_getattr_string(val, 'day')
    tjjj__ekt = c.pyapi.object_getattr_string(val, 'hour')
    nkibt__osydv = c.pyapi.object_getattr_string(val, 'minute')
    kpoap__mxg = c.pyapi.object_getattr_string(val, 'second')
    pynak__uwm = c.pyapi.object_getattr_string(val, 'microsecond')
    djncf__bid = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    djncf__bid.year = c.pyapi.long_as_longlong(mltrv__skazb)
    djncf__bid.month = c.pyapi.long_as_longlong(vpbvg__qdbc)
    djncf__bid.day = c.pyapi.long_as_longlong(qqai__vxm)
    djncf__bid.hour = c.pyapi.long_as_longlong(tjjj__ekt)
    djncf__bid.minute = c.pyapi.long_as_longlong(nkibt__osydv)
    djncf__bid.second = c.pyapi.long_as_longlong(kpoap__mxg)
    djncf__bid.microsecond = c.pyapi.long_as_longlong(pynak__uwm)
    c.pyapi.decref(mltrv__skazb)
    c.pyapi.decref(vpbvg__qdbc)
    c.pyapi.decref(qqai__vxm)
    c.pyapi.decref(tjjj__ekt)
    c.pyapi.decref(nkibt__osydv)
    c.pyapi.decref(kpoap__mxg)
    c.pyapi.decref(pynak__uwm)
    epz__wqrp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(djncf__bid._getvalue(), is_error=epz__wqrp)


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
        djncf__bid = cgutils.create_struct_proxy(typ)(context, builder)
        djncf__bid.year = args[0]
        djncf__bid.month = args[1]
        djncf__bid.day = args[2]
        djncf__bid.hour = args[3]
        djncf__bid.minute = args[4]
        djncf__bid.second = args[5]
        djncf__bid.microsecond = args[6]
        return djncf__bid._getvalue()
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
                y, rgqmy__rpi = lhs.year, rhs.year
                mojg__pskp, rwv__ears = lhs.month, rhs.month
                d, plr__jwrk = lhs.day, rhs.day
                sij__tpauj, akj__wionv = lhs.hour, rhs.hour
                dmlqb__opcaz, pipcu__qnvpy = lhs.minute, rhs.minute
                amy__gjqs, tdtu__zmitb = lhs.second, rhs.second
                dnli__uwbw, ljvsw__vulk = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, mojg__pskp, d, sij__tpauj, dmlqb__opcaz,
                    amy__gjqs, dnli__uwbw), (rgqmy__rpi, rwv__ears,
                    plr__jwrk, akj__wionv, pipcu__qnvpy, tdtu__zmitb,
                    ljvsw__vulk)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            doi__tjtkw = lhs.toordinal()
            ytly__uyu = rhs.toordinal()
            xsd__hose = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            pvjfh__tbvu = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            nqlv__nqu = datetime.timedelta(doi__tjtkw - ytly__uyu, 
                xsd__hose - pvjfh__tbvu, lhs.microsecond - rhs.microsecond)
            return nqlv__nqu
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    wem__etn = context.make_helper(builder, fromty, value=val)
    tzd__rpva = cgutils.as_bool_bit(builder, wem__etn.valid)
    with builder.if_else(tzd__rpva) as (vaotf__eqwmj, dhfcm__hxnit):
        with vaotf__eqwmj:
            zgeyj__facl = context.cast(builder, wem__etn.data, fromty.type,
                toty)
            peyy__srz = builder.block
        with dhfcm__hxnit:
            utag__rtqy = numba.np.npdatetime.NAT
            fkhtj__tmw = builder.block
    vei__houf = builder.phi(zgeyj__facl.type)
    vei__houf.add_incoming(zgeyj__facl, peyy__srz)
    vei__houf.add_incoming(utag__rtqy, fkhtj__tmw)
    return vei__houf
