"""Numba extension support for datetime.timedelta objects and their arrays.
"""
import datetime
import operator
from collections import namedtuple
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import get_new_null_mask_bool_index, get_new_null_mask_int_index, get_new_null_mask_slice_index, setitem_slice_index_null_bits
from bodo.utils.typing import BodoError, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_str
ll.add_symbol('box_datetime_timedelta_array', hdatetime_ext.
    box_datetime_timedelta_array)
ll.add_symbol('unbox_datetime_timedelta_array', hdatetime_ext.
    unbox_datetime_timedelta_array)


class NoInput:
    pass


_no_input = NoInput()


class NoInputType(types.Type):

    def __init__(self):
        super(NoInputType, self).__init__(name='NoInput')


register_model(NoInputType)(models.OpaqueModel)


@typeof_impl.register(NoInput)
def _typ_no_input(val, c):
    return NoInputType()


@lower_constant(NoInputType)
def constant_no_input(context, builder, ty, pyval):
    return context.get_dummy_value()


class PDTimeDeltaType(types.Type):

    def __init__(self):
        super(PDTimeDeltaType, self).__init__(name='PDTimeDeltaType()')


pd_timedelta_type = PDTimeDeltaType()
types.pd_timedelta_type = pd_timedelta_type


@typeof_impl.register(pd.Timedelta)
def typeof_pd_timedelta(val, c):
    return pd_timedelta_type


@register_model(PDTimeDeltaType)
class PDTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dfcha__fku = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, dfcha__fku)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    uoopd__mua = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    tft__qve = c.pyapi.long_from_longlong(uoopd__mua.value)
    ohyh__vrvwx = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(ohyh__vrvwx, (tft__qve,))
    c.pyapi.decref(tft__qve)
    c.pyapi.decref(ohyh__vrvwx)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    tft__qve = c.pyapi.object_getattr_string(val, 'value')
    dysbu__haa = c.pyapi.long_as_longlong(tft__qve)
    uoopd__mua = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uoopd__mua.value = dysbu__haa
    c.pyapi.decref(tft__qve)
    ikclu__bfpg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uoopd__mua._getvalue(), is_error=ikclu__bfpg)


@lower_constant(PDTimeDeltaType)
def lower_constant_pd_timedelta(context, builder, ty, pyval):
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct([value])


@overload(pd.Timedelta, no_unliteral=True)
def pd_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
    microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    if value == _no_input:

        def impl_timedelta_kw(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            days += weeks * 7
            hours += days * 24
            minutes += 60 * hours
            seconds += 60 * minutes
            milliseconds += 1000 * seconds
            microseconds += 1000 * milliseconds
            lufn__wihm = 1000 * microseconds
            return init_pd_timedelta(lufn__wihm)
        return impl_timedelta_kw
    if value == bodo.string_type or is_overload_constant_str(value):

        def impl_str(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            with numba.objmode(res='pd_timedelta_type'):
                res = pd.Timedelta(value)
            return res
        return impl_str
    if value == pd_timedelta_type:
        return (lambda value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0: value)
    if value == datetime_timedelta_type:

        def impl_timedelta_datetime(value=_no_input, unit='ns', days=0,
            seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0,
            weeks=0):
            days = value.days
            seconds = 60 * 60 * 24 * days + value.seconds
            microseconds = 1000 * 1000 * seconds + value.microseconds
            lufn__wihm = 1000 * microseconds
            return init_pd_timedelta(lufn__wihm)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    sku__wlti, iiir__qdavd = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * sku__wlti)
    return impl_timedelta


@intrinsic
def init_pd_timedelta(typingctx, value):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.value = args[0]
        return timedelta._getvalue()
    return PDTimeDeltaType()(value), codegen


make_attribute_wrapper(PDTimeDeltaType, 'value', '_value')


@overload_attribute(PDTimeDeltaType, 'value')
@overload_attribute(PDTimeDeltaType, 'delta')
def pd_timedelta_get_value(td):

    def impl(td):
        return td._value
    return impl


@overload_attribute(PDTimeDeltaType, 'days')
def pd_timedelta_get_days(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000 * 60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'seconds')
def pd_timedelta_get_seconds(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000) % (60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'microseconds')
def pd_timedelta_get_microseconds(td):

    def impl(td):
        return td._value // 1000 % 1000000
    return impl


@overload_attribute(PDTimeDeltaType, 'nanoseconds')
def pd_timedelta_get_nanoseconds(td):

    def impl(td):
        return td._value % 1000
    return impl


@register_jitable
def _to_hours_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60 * 60) % 24


@register_jitable
def _to_minutes_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60) % 60


@register_jitable
def _to_seconds_pd_td(td):
    return td._value // (1000 * 1000 * 1000) % 60


@register_jitable
def _to_milliseconds_pd_td(td):
    return td._value // (1000 * 1000) % 1000


@register_jitable
def _to_microseconds_pd_td(td):
    return td._value // 1000 % 1000


Components = namedtuple('Components', ['days', 'hours', 'minutes',
    'seconds', 'milliseconds', 'microseconds', 'nanoseconds'], defaults=[0,
    0, 0, 0, 0, 0, 0])


@overload_attribute(PDTimeDeltaType, 'components', no_unliteral=True)
def pd_timedelta_get_components(td):

    def impl(td):
        a = Components(td.days, _to_hours_pd_td(td), _to_minutes_pd_td(td),
            _to_seconds_pd_td(td), _to_milliseconds_pd_td(td),
            _to_microseconds_pd_td(td), td.nanoseconds)
        return a
    return impl


@overload_method(PDTimeDeltaType, '__hash__', no_unliteral=True)
def pd_td___hash__(td):

    def impl(td):
        return hash(td._value)
    return impl


@overload_method(PDTimeDeltaType, 'to_numpy', no_unliteral=True)
@overload_method(PDTimeDeltaType, 'to_timedelta64', no_unliteral=True)
def pd_td_to_numpy(td):
    from bodo.hiframes.pd_timestamp_ext import integer_to_timedelta64

    def impl(td):
        return integer_to_timedelta64(td.value)
    return impl


@overload_method(PDTimeDeltaType, 'to_pytimedelta', no_unliteral=True)
def pd_td_to_pytimedelta(td):

    def impl(td):
        return datetime.timedelta(microseconds=np.int64(td._value / 1000))
    return impl


@overload_method(PDTimeDeltaType, 'total_seconds', no_unliteral=True)
def pd_td_total_seconds(td):

    def impl(td):
        return td._value // 1000 / 10 ** 6
    return impl


def overload_add_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            val = lhs.value + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            cfz__wdy = (rhs.microseconds + (rhs.seconds + rhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + cfz__wdy
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            atqm__vyn = (lhs.microseconds + (lhs.seconds + lhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = atqm__vyn + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            tku__twu = rhs.toordinal()
            tbs__lpbaa = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            hdsj__nynab = rhs.microsecond
            kpjvz__ypn = lhs.value // 1000
            jdxay__jwlwc = lhs.nanoseconds
            vzrr__azdww = hdsj__nynab + kpjvz__ypn
            vaz__zlcz = 1000000 * (tku__twu * 86400 + tbs__lpbaa) + vzrr__azdww
            kba__xrm = jdxay__jwlwc
            return compute_pd_timestamp(vaz__zlcz, kba__xrm)
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + rhs.to_pytimedelta()
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days + rhs.days
            s = lhs.seconds + rhs.seconds
            us = lhs.microseconds + rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            bqi__wnkjr = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            bqi__wnkjr = bqi__wnkjr + lhs
            qyya__xcg, zfss__plbi = divmod(bqi__wnkjr.seconds, 3600)
            cfqkd__zjr, iir__thqv = divmod(zfss__plbi, 60)
            if 0 < bqi__wnkjr.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(bqi__wnkjr
                    .days)
                return datetime.datetime(d.year, d.month, d.day, qyya__xcg,
                    cfqkd__zjr, iir__thqv, bqi__wnkjr.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            bqi__wnkjr = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            bqi__wnkjr = bqi__wnkjr + rhs
            qyya__xcg, zfss__plbi = divmod(bqi__wnkjr.seconds, 3600)
            cfqkd__zjr, iir__thqv = divmod(zfss__plbi, 60)
            if 0 < bqi__wnkjr.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(bqi__wnkjr
                    .days)
                return datetime.datetime(d.year, d.month, d.day, qyya__xcg,
                    cfqkd__zjr, iir__thqv, bqi__wnkjr.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ouf__nvmn = lhs.value - rhs.value
            return pd.Timedelta(ouf__nvmn)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days - rhs.days
            s = lhs.seconds - rhs.seconds
            us = lhs.microseconds - rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            cdjb__jmwyk = lhs
            numba.parfors.parfor.init_prange()
            n = len(cdjb__jmwyk)
            A = alloc_datetime_timedelta_array(n)
            for snj__xxvaj in numba.parfors.parfor.internal_prange(n):
                A[snj__xxvaj] = cdjb__jmwyk[snj__xxvaj] - rhs
            return A
        return impl


def overload_mul_operator_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value * rhs)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(rhs.value * lhs)
        return impl
    if lhs == datetime_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            d = lhs.days * rhs
            s = lhs.seconds * rhs
            us = lhs.microseconds * rhs
            return datetime.timedelta(d, s, us)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs * rhs.days
            s = lhs * rhs.seconds
            us = lhs * rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl


def overload_floordiv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value // rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value // rhs)
        return impl


def overload_truediv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value / rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(int(lhs.value / rhs))
        return impl


def overload_mod_operator_timedeltas(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value % rhs.value)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            syat__hno = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, syat__hno)
        return impl


def pd_create_cmp_op_overload(op):

    def overload_pd_timedelta_cmp(lhs, rhs):
        if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

            def impl(lhs, rhs):
                return op(lhs.value, rhs.value)
            return impl
        if lhs == pd_timedelta_type and rhs == bodo.timedelta64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(lhs.value), rhs)
        if lhs == bodo.timedelta64ns and rhs == pd_timedelta_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(rhs.value))
    return overload_pd_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def pd_timedelta_neg(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return pd.Timedelta(-lhs.value)
        return impl


@overload(operator.pos, no_unliteral=True)
def pd_timedelta_pos(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def pd_timedelta_divmod(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ubnq__syo, syat__hno = divmod(lhs.value, rhs.value)
            return ubnq__syo, pd.Timedelta(syat__hno)
        return impl


@overload(abs, no_unliteral=True)
def pd_timedelta_abs(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            if lhs.value < 0:
                return -lhs
            else:
                return lhs
        return impl


class DatetimeTimeDeltaType(types.Type):

    def __init__(self):
        super(DatetimeTimeDeltaType, self).__init__(name=
            'DatetimeTimeDeltaType()')


datetime_timedelta_type = DatetimeTimeDeltaType()


@typeof_impl.register(datetime.timedelta)
def typeof_datetime_timedelta(val, c):
    return datetime_timedelta_type


@register_model(DatetimeTimeDeltaType)
class DatetimeTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dfcha__fku = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, dfcha__fku)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    uoopd__mua = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    aakvn__zxx = c.pyapi.long_from_longlong(uoopd__mua.days)
    jzdx__gtu = c.pyapi.long_from_longlong(uoopd__mua.seconds)
    oboo__odwx = c.pyapi.long_from_longlong(uoopd__mua.microseconds)
    ohyh__vrvwx = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(ohyh__vrvwx, (aakvn__zxx, jzdx__gtu,
        oboo__odwx))
    c.pyapi.decref(aakvn__zxx)
    c.pyapi.decref(jzdx__gtu)
    c.pyapi.decref(oboo__odwx)
    c.pyapi.decref(ohyh__vrvwx)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    aakvn__zxx = c.pyapi.object_getattr_string(val, 'days')
    jzdx__gtu = c.pyapi.object_getattr_string(val, 'seconds')
    oboo__odwx = c.pyapi.object_getattr_string(val, 'microseconds')
    lau__sjgh = c.pyapi.long_as_longlong(aakvn__zxx)
    yqdwx__byb = c.pyapi.long_as_longlong(jzdx__gtu)
    tuh__jeqo = c.pyapi.long_as_longlong(oboo__odwx)
    uoopd__mua = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uoopd__mua.days = lau__sjgh
    uoopd__mua.seconds = yqdwx__byb
    uoopd__mua.microseconds = tuh__jeqo
    c.pyapi.decref(aakvn__zxx)
    c.pyapi.decref(jzdx__gtu)
    c.pyapi.decref(oboo__odwx)
    ikclu__bfpg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uoopd__mua._getvalue(), is_error=ikclu__bfpg)


@lower_constant(DatetimeTimeDeltaType)
def lower_constant_datetime_timedelta(context, builder, ty, pyval):
    days = context.get_constant(types.int64, pyval.days)
    seconds = context.get_constant(types.int64, pyval.seconds)
    microseconds = context.get_constant(types.int64, pyval.microseconds)
    return lir.Constant.literal_struct([days, seconds, microseconds])


@overload(datetime.timedelta, no_unliteral=True)
def datetime_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    minutes=0, hours=0, weeks=0):

    def impl_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
        minutes=0, hours=0, weeks=0):
        d = s = us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        d = days
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += int(seconds)
        seconds, us = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += seconds
        return init_timedelta(d, s, us)
    return impl_timedelta


@intrinsic
def init_timedelta(typingctx, d, s, us):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.days = args[0]
        timedelta.seconds = args[1]
        timedelta.microseconds = args[2]
        return timedelta._getvalue()
    return DatetimeTimeDeltaType()(d, s, us), codegen


make_attribute_wrapper(DatetimeTimeDeltaType, 'days', '_days')
make_attribute_wrapper(DatetimeTimeDeltaType, 'seconds', '_seconds')
make_attribute_wrapper(DatetimeTimeDeltaType, 'microseconds', '_microseconds')


@overload_attribute(DatetimeTimeDeltaType, 'days')
def timedelta_get_days(td):

    def impl(td):
        return td._days
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'seconds')
def timedelta_get_seconds(td):

    def impl(td):
        return td._seconds
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'microseconds')
def timedelta_get_microseconds(td):

    def impl(td):
        return td._microseconds
    return impl


@overload_method(DatetimeTimeDeltaType, 'total_seconds', no_unliteral=True)
def total_seconds(td):

    def impl(td):
        return ((td._days * 86400 + td._seconds) * 10 ** 6 + td._microseconds
            ) / 10 ** 6
    return impl


@overload_method(DatetimeTimeDeltaType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        return hash((td._days, td._seconds, td._microseconds))
    return impl


@register_jitable
def _to_nanoseconds(td):
    return np.int64(((td._days * 86400 + td._seconds) * 1000000 + td.
        _microseconds) * 1000)


@register_jitable
def _to_microseconds(td):
    return (td._days * (24 * 3600) + td._seconds) * 1000000 + td._microseconds


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@register_jitable
def _getstate(td):
    return td._days, td._seconds, td._microseconds


@register_jitable
def _divide_and_round(a, b):
    ubnq__syo, syat__hno = divmod(a, b)
    syat__hno *= 2
    zcwn__gqa = syat__hno > b if b > 0 else syat__hno < b
    if zcwn__gqa or syat__hno == b and ubnq__syo % 2 == 1:
        ubnq__syo += 1
    return ubnq__syo


_MAXORDINAL = 3652059


def overload_floordiv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us // _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, us // rhs)
        return impl


def overload_truediv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us / _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, _divide_and_round(us, rhs))
        return impl


def create_cmp_op_overload(op):

    def overload_timedelta_cmp(lhs, rhs):
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

            def impl(lhs, rhs):
                jflif__pyg = _cmp(_getstate(lhs), _getstate(rhs))
                return op(jflif__pyg, 0)
            return impl
    return overload_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def timedelta_neg(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return datetime.timedelta(-lhs.days, -lhs.seconds, -lhs.
                microseconds)
        return impl


@overload(operator.pos, no_unliteral=True)
def timedelta_pos(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def timedelta_divmod(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ubnq__syo, syat__hno = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return ubnq__syo, datetime.timedelta(0, 0, syat__hno)
        return impl


@overload(abs, no_unliteral=True)
def timedelta_abs(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            if lhs.days < 0:
                return -lhs
            else:
                return lhs
        return impl


@intrinsic
def cast_numpy_timedelta_to_int(typingctx, val=None):
    assert val in (types.NPTimedelta('ns'), types.int64)

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


@overload(bool, no_unliteral=True)
def timedelta_to_bool(timedelta):
    if timedelta != datetime_timedelta_type:
        return
    dpj__zmk = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != dpj__zmk
    return impl


class DatetimeTimeDeltaArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeTimeDeltaArrayType, self).__init__(name=
            'DatetimeTimeDeltaArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_timedelta_type

    def copy(self):
        return DatetimeTimeDeltaArrayType()


datetime_timedelta_array_type = DatetimeTimeDeltaArrayType()
types.datetime_timedelta_array_type = datetime_timedelta_array_type
days_data_type = types.Array(types.int64, 1, 'C')
seconds_data_type = types.Array(types.int64, 1, 'C')
microseconds_data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeTimeDeltaArrayType)
class DatetimeTimeDeltaArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dfcha__fku = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, dfcha__fku)


make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'days_data', '_days_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'seconds_data',
    '_seconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'microseconds_data',
    '_microseconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'null_bitmap',
    '_null_bitmap')


@overload_method(DatetimeTimeDeltaArrayType, 'copy', no_unliteral=True)
def overload_datetime_timedelta_arr_copy(A):
    return (lambda A: bodo.hiframes.datetime_timedelta_ext.
        init_datetime_timedelta_array(A._days_data.copy(), A._seconds_data.
        copy(), A._microseconds_data.copy(), A._null_bitmap.copy()))


@unbox(DatetimeTimeDeltaArrayType)
def unbox_datetime_timedelta_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    bnmrw__ljpkt = types.Array(types.intp, 1, 'C')
    bbxa__cezc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        bnmrw__ljpkt, [n])
    ficx__jvxzf = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        bnmrw__ljpkt, [n])
    vwh__ounv = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        bnmrw__ljpkt, [n])
    kxcg__pqd = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    ovqxz__vcefi = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [kxcg__pqd])
    vyiv__bxj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer()])
    iywyk__mxbyq = cgutils.get_or_insert_function(c.builder.module,
        vyiv__bxj, name='unbox_datetime_timedelta_array')
    c.builder.call(iywyk__mxbyq, [val, n, bbxa__cezc.data, ficx__jvxzf.data,
        vwh__ounv.data, ovqxz__vcefi.data])
    hgtt__rtt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hgtt__rtt.days_data = bbxa__cezc._getvalue()
    hgtt__rtt.seconds_data = ficx__jvxzf._getvalue()
    hgtt__rtt.microseconds_data = vwh__ounv._getvalue()
    hgtt__rtt.null_bitmap = ovqxz__vcefi._getvalue()
    ikclu__bfpg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hgtt__rtt._getvalue(), is_error=ikclu__bfpg)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    cdjb__jmwyk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    bbxa__cezc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, cdjb__jmwyk.days_data)
    ficx__jvxzf = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, cdjb__jmwyk.seconds_data).data
    vwh__ounv = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, cdjb__jmwyk.microseconds_data).data
    mcgvs__teom = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, cdjb__jmwyk.null_bitmap).data
    n = c.builder.extract_value(bbxa__cezc.shape, 0)
    vyiv__bxj = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    wkbb__mjf = cgutils.get_or_insert_function(c.builder.module, vyiv__bxj,
        name='box_datetime_timedelta_array')
    iqfgm__vyyvt = c.builder.call(wkbb__mjf, [n, bbxa__cezc.data,
        ficx__jvxzf, vwh__ounv, mcgvs__teom])
    c.context.nrt.decref(c.builder, typ, val)
    return iqfgm__vyyvt


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        phc__ovld, hhki__exepj, hbdzy__nixjl, qqk__sddxr = args
        inzdy__qaz = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        inzdy__qaz.days_data = phc__ovld
        inzdy__qaz.seconds_data = hhki__exepj
        inzdy__qaz.microseconds_data = hbdzy__nixjl
        inzdy__qaz.null_bitmap = qqk__sddxr
        context.nrt.incref(builder, signature.args[0], phc__ovld)
        context.nrt.incref(builder, signature.args[1], hhki__exepj)
        context.nrt.incref(builder, signature.args[2], hbdzy__nixjl)
        context.nrt.incref(builder, signature.args[3], qqk__sddxr)
        return inzdy__qaz._getvalue()
    jaq__wxmf = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return jaq__wxmf, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    bbxa__cezc = np.empty(n, np.int64)
    ficx__jvxzf = np.empty(n, np.int64)
    vwh__ounv = np.empty(n, np.int64)
    ajf__stev = np.empty(n + 7 >> 3, np.uint8)
    for snj__xxvaj, s in enumerate(pyval):
        rmw__nvjnw = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ajf__stev, snj__xxvaj, int(not
            rmw__nvjnw))
        if not rmw__nvjnw:
            bbxa__cezc[snj__xxvaj] = s.days
            ficx__jvxzf[snj__xxvaj] = s.seconds
            vwh__ounv[snj__xxvaj] = s.microseconds
    qqh__czvw = context.get_constant_generic(builder, days_data_type,
        bbxa__cezc)
    ckoyx__zixgo = context.get_constant_generic(builder, seconds_data_type,
        ficx__jvxzf)
    wwm__wbzkm = context.get_constant_generic(builder,
        microseconds_data_type, vwh__ounv)
    bltc__eceph = context.get_constant_generic(builder, nulls_type, ajf__stev)
    return lir.Constant.literal_struct([qqh__czvw, ckoyx__zixgo, wwm__wbzkm,
        bltc__eceph])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    bbxa__cezc = np.empty(n, dtype=np.int64)
    ficx__jvxzf = np.empty(n, dtype=np.int64)
    vwh__ounv = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(bbxa__cezc, ficx__jvxzf, vwh__ounv,
        nulls)


def alloc_datetime_timedelta_array_equiv(self, scope, equiv_set, loc, args, kws
    ):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_timedelta_ext_alloc_datetime_timedelta_array
    ) = alloc_datetime_timedelta_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_timedelta_arr_getitem(A, ind):
    if A != datetime_timedelta_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl_int(A, ind):
            return datetime.timedelta(days=A._days_data[ind], seconds=A.
                _seconds_data[ind], microseconds=A._microseconds_data[ind])
        return impl_int
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            vqv__uokeq = bodo.utils.conversion.coerce_to_ndarray(ind)
            hzknt__kfez = A._null_bitmap
            buovl__yuv = A._days_data[vqv__uokeq]
            eaum__bzlot = A._seconds_data[vqv__uokeq]
            sds__mip = A._microseconds_data[vqv__uokeq]
            n = len(buovl__yuv)
            kmwqv__uqmgf = get_new_null_mask_bool_index(hzknt__kfez, ind, n)
            return init_datetime_timedelta_array(buovl__yuv, eaum__bzlot,
                sds__mip, kmwqv__uqmgf)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            vqv__uokeq = bodo.utils.conversion.coerce_to_ndarray(ind)
            hzknt__kfez = A._null_bitmap
            buovl__yuv = A._days_data[vqv__uokeq]
            eaum__bzlot = A._seconds_data[vqv__uokeq]
            sds__mip = A._microseconds_data[vqv__uokeq]
            n = len(buovl__yuv)
            kmwqv__uqmgf = get_new_null_mask_int_index(hzknt__kfez,
                vqv__uokeq, n)
            return init_datetime_timedelta_array(buovl__yuv, eaum__bzlot,
                sds__mip, kmwqv__uqmgf)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            hzknt__kfez = A._null_bitmap
            buovl__yuv = np.ascontiguousarray(A._days_data[ind])
            eaum__bzlot = np.ascontiguousarray(A._seconds_data[ind])
            sds__mip = np.ascontiguousarray(A._microseconds_data[ind])
            kmwqv__uqmgf = get_new_null_mask_slice_index(hzknt__kfez, ind, n)
            return init_datetime_timedelta_array(buovl__yuv, eaum__bzlot,
                sds__mip, kmwqv__uqmgf)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_timedelta_arr_setitem(A, ind, val):
    if A != datetime_timedelta_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    mvtq__gff = (
        f"setitem for DatetimeTimedeltaArray with indexing type {ind} received an incorrect 'value' type {val}."
        )
    if isinstance(ind, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl(A, ind, val):
                A._days_data[ind] = val._days
                A._seconds_data[ind] = val._seconds
                A._microseconds_data[ind] = val._microseconds
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, ind, 1)
            return impl
        else:
            raise BodoError(mvtq__gff)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(mvtq__gff)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for snj__xxvaj in range(n):
                    A._days_data[ind[snj__xxvaj]] = val._days
                    A._seconds_data[ind[snj__xxvaj]] = val._seconds
                    A._microseconds_data[ind[snj__xxvaj]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[snj__xxvaj], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for snj__xxvaj in range(n):
                    A._days_data[ind[snj__xxvaj]] = val._days_data[snj__xxvaj]
                    A._seconds_data[ind[snj__xxvaj]] = val._seconds_data[
                        snj__xxvaj]
                    A._microseconds_data[ind[snj__xxvaj]
                        ] = val._microseconds_data[snj__xxvaj]
                    thlo__ljomf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, snj__xxvaj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[snj__xxvaj], thlo__ljomf)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for snj__xxvaj in range(n):
                    if not bodo.libs.array_kernels.isna(ind, snj__xxvaj
                        ) and ind[snj__xxvaj]:
                        A._days_data[snj__xxvaj] = val._days
                        A._seconds_data[snj__xxvaj] = val._seconds
                        A._microseconds_data[snj__xxvaj] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            snj__xxvaj, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                fzna__canwd = 0
                for snj__xxvaj in range(n):
                    if not bodo.libs.array_kernels.isna(ind, snj__xxvaj
                        ) and ind[snj__xxvaj]:
                        A._days_data[snj__xxvaj] = val._days_data[fzna__canwd]
                        A._seconds_data[snj__xxvaj] = val._seconds_data[
                            fzna__canwd]
                        A._microseconds_data[snj__xxvaj
                            ] = val._microseconds_data[fzna__canwd]
                        thlo__ljomf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, fzna__canwd)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            snj__xxvaj, thlo__ljomf)
                        fzna__canwd += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                enywn__mtij = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for snj__xxvaj in range(enywn__mtij.start, enywn__mtij.stop,
                    enywn__mtij.step):
                    A._days_data[snj__xxvaj] = val._days
                    A._seconds_data[snj__xxvaj] = val._seconds
                    A._microseconds_data[snj__xxvaj] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        snj__xxvaj, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                toila__pod = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, toila__pod,
                    ind, n)
            return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_timedelta_arr(A):
    if A == datetime_timedelta_array_type:
        return lambda A: len(A._days_data)


@overload_attribute(DatetimeTimeDeltaArrayType, 'shape')
def overload_datetime_timedelta_arr_shape(A):
    return lambda A: (len(A._days_data),)


@overload_attribute(DatetimeTimeDeltaArrayType, 'nbytes')
def timedelta_arr_nbytes_overload(A):
    return (lambda A: A._days_data.nbytes + A._seconds_data.nbytes + A.
        _microseconds_data.nbytes + A._null_bitmap.nbytes)


def overload_datetime_timedelta_arr_sub(arg1, arg2):
    if (arg1 == datetime_timedelta_array_type and arg2 ==
        datetime_timedelta_type):

        def impl(arg1, arg2):
            cdjb__jmwyk = arg1
            numba.parfors.parfor.init_prange()
            n = len(cdjb__jmwyk)
            A = alloc_datetime_timedelta_array(n)
            for snj__xxvaj in numba.parfors.parfor.internal_prange(n):
                A[snj__xxvaj] = cdjb__jmwyk[snj__xxvaj] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            kcce__ykp = True
        else:
            kcce__ykp = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                gdlzh__sdw = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for snj__xxvaj in numba.parfors.parfor.internal_prange(n):
                    afsil__idr = bodo.libs.array_kernels.isna(lhs, snj__xxvaj)
                    wfpf__tklau = bodo.libs.array_kernels.isna(rhs, snj__xxvaj)
                    if afsil__idr or wfpf__tklau:
                        hkt__mvpd = kcce__ykp
                    else:
                        hkt__mvpd = op(lhs[snj__xxvaj], rhs[snj__xxvaj])
                    gdlzh__sdw[snj__xxvaj] = hkt__mvpd
                return gdlzh__sdw
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                gdlzh__sdw = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for snj__xxvaj in numba.parfors.parfor.internal_prange(n):
                    thlo__ljomf = bodo.libs.array_kernels.isna(lhs, snj__xxvaj)
                    if thlo__ljomf:
                        hkt__mvpd = kcce__ykp
                    else:
                        hkt__mvpd = op(lhs[snj__xxvaj], rhs)
                    gdlzh__sdw[snj__xxvaj] = hkt__mvpd
                return gdlzh__sdw
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                gdlzh__sdw = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for snj__xxvaj in numba.parfors.parfor.internal_prange(n):
                    thlo__ljomf = bodo.libs.array_kernels.isna(rhs, snj__xxvaj)
                    if thlo__ljomf:
                        hkt__mvpd = kcce__ykp
                    else:
                        hkt__mvpd = op(lhs, rhs[snj__xxvaj])
                    gdlzh__sdw[snj__xxvaj] = hkt__mvpd
                return gdlzh__sdw
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for yxadl__hxqd in timedelta_unsupported_attrs:
        ntnps__gcvkd = 'pandas.Timedelta.' + yxadl__hxqd
        overload_attribute(PDTimeDeltaType, yxadl__hxqd)(
            create_unsupported_overload(ntnps__gcvkd))
    for ptq__uorlr in timedelta_unsupported_methods:
        ntnps__gcvkd = 'pandas.Timedelta.' + ptq__uorlr
        overload_method(PDTimeDeltaType, ptq__uorlr)(
            create_unsupported_overload(ntnps__gcvkd + '()'))


_intstall_pd_timedelta_unsupported()
