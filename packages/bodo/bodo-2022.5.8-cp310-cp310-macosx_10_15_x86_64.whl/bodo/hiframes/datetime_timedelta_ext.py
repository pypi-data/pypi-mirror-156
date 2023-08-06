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
        kujeg__dbyh = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, kujeg__dbyh)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    zpmr__qtfep = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    pcvo__mzb = c.pyapi.long_from_longlong(zpmr__qtfep.value)
    nft__zpda = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(nft__zpda, (pcvo__mzb,))
    c.pyapi.decref(pcvo__mzb)
    c.pyapi.decref(nft__zpda)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    pcvo__mzb = c.pyapi.object_getattr_string(val, 'value')
    yucmw__grgs = c.pyapi.long_as_longlong(pcvo__mzb)
    zpmr__qtfep = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zpmr__qtfep.value = yucmw__grgs
    c.pyapi.decref(pcvo__mzb)
    fmpe__ypxrr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zpmr__qtfep._getvalue(), is_error=fmpe__ypxrr)


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
            neye__uea = 1000 * microseconds
            return init_pd_timedelta(neye__uea)
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
            neye__uea = 1000 * microseconds
            return init_pd_timedelta(neye__uea)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    zlq__itn, lcqac__box = pd._libs.tslibs.conversion.precision_from_unit(unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * zlq__itn)
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
            niig__kkz = (rhs.microseconds + (rhs.seconds + rhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + niig__kkz
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            hjkg__wyyb = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = hjkg__wyyb + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            fxhg__hwgfi = rhs.toordinal()
            qpv__jwdmv = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            ahz__pjota = rhs.microsecond
            uel__yjrk = lhs.value // 1000
            repy__djx = lhs.nanoseconds
            brohi__uuir = ahz__pjota + uel__yjrk
            kwci__smcg = 1000000 * (fxhg__hwgfi * 86400 + qpv__jwdmv
                ) + brohi__uuir
            fdd__kzqt = repy__djx
            return compute_pd_timestamp(kwci__smcg, fdd__kzqt)
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
            rcssq__vpv = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            rcssq__vpv = rcssq__vpv + lhs
            gvox__xkbb, vgou__lpvyg = divmod(rcssq__vpv.seconds, 3600)
            onav__erwa, bez__xygg = divmod(vgou__lpvyg, 60)
            if 0 < rcssq__vpv.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(rcssq__vpv
                    .days)
                return datetime.datetime(d.year, d.month, d.day, gvox__xkbb,
                    onav__erwa, bez__xygg, rcssq__vpv.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            rcssq__vpv = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            rcssq__vpv = rcssq__vpv + rhs
            gvox__xkbb, vgou__lpvyg = divmod(rcssq__vpv.seconds, 3600)
            onav__erwa, bez__xygg = divmod(vgou__lpvyg, 60)
            if 0 < rcssq__vpv.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(rcssq__vpv
                    .days)
                return datetime.datetime(d.year, d.month, d.day, gvox__xkbb,
                    onav__erwa, bez__xygg, rcssq__vpv.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ainf__rqpnf = lhs.value - rhs.value
            return pd.Timedelta(ainf__rqpnf)
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
            ebgwy__cth = lhs
            numba.parfors.parfor.init_prange()
            n = len(ebgwy__cth)
            A = alloc_datetime_timedelta_array(n)
            for sig__iuar in numba.parfors.parfor.internal_prange(n):
                A[sig__iuar] = ebgwy__cth[sig__iuar] - rhs
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
            qhg__amj = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, qhg__amj)
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
            fhp__suoan, qhg__amj = divmod(lhs.value, rhs.value)
            return fhp__suoan, pd.Timedelta(qhg__amj)
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
        kujeg__dbyh = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, kujeg__dbyh)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    zpmr__qtfep = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ilp__wwvuo = c.pyapi.long_from_longlong(zpmr__qtfep.days)
    bykk__mjwqg = c.pyapi.long_from_longlong(zpmr__qtfep.seconds)
    zgx__gqs = c.pyapi.long_from_longlong(zpmr__qtfep.microseconds)
    nft__zpda = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(nft__zpda, (ilp__wwvuo, bykk__mjwqg,
        zgx__gqs))
    c.pyapi.decref(ilp__wwvuo)
    c.pyapi.decref(bykk__mjwqg)
    c.pyapi.decref(zgx__gqs)
    c.pyapi.decref(nft__zpda)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    ilp__wwvuo = c.pyapi.object_getattr_string(val, 'days')
    bykk__mjwqg = c.pyapi.object_getattr_string(val, 'seconds')
    zgx__gqs = c.pyapi.object_getattr_string(val, 'microseconds')
    invq__ypp = c.pyapi.long_as_longlong(ilp__wwvuo)
    jfia__wfgj = c.pyapi.long_as_longlong(bykk__mjwqg)
    tyhmp__skir = c.pyapi.long_as_longlong(zgx__gqs)
    zpmr__qtfep = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zpmr__qtfep.days = invq__ypp
    zpmr__qtfep.seconds = jfia__wfgj
    zpmr__qtfep.microseconds = tyhmp__skir
    c.pyapi.decref(ilp__wwvuo)
    c.pyapi.decref(bykk__mjwqg)
    c.pyapi.decref(zgx__gqs)
    fmpe__ypxrr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zpmr__qtfep._getvalue(), is_error=fmpe__ypxrr)


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
    fhp__suoan, qhg__amj = divmod(a, b)
    qhg__amj *= 2
    peb__gtdbg = qhg__amj > b if b > 0 else qhg__amj < b
    if peb__gtdbg or qhg__amj == b and fhp__suoan % 2 == 1:
        fhp__suoan += 1
    return fhp__suoan


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
                yuub__wgq = _cmp(_getstate(lhs), _getstate(rhs))
                return op(yuub__wgq, 0)
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
            fhp__suoan, qhg__amj = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return fhp__suoan, datetime.timedelta(0, 0, qhg__amj)
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
    zid__sven = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != zid__sven
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
        kujeg__dbyh = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, kujeg__dbyh)


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
    aryn__qiued = types.Array(types.intp, 1, 'C')
    chnw__bccc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        aryn__qiued, [n])
    pyz__xwcjc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        aryn__qiued, [n])
    qrx__xtiyy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        aryn__qiued, [n])
    quwlz__wis = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    mma__escno = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [quwlz__wis])
    cso__jgqws = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    ioig__doi = cgutils.get_or_insert_function(c.builder.module, cso__jgqws,
        name='unbox_datetime_timedelta_array')
    c.builder.call(ioig__doi, [val, n, chnw__bccc.data, pyz__xwcjc.data,
        qrx__xtiyy.data, mma__escno.data])
    tpfm__nov = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tpfm__nov.days_data = chnw__bccc._getvalue()
    tpfm__nov.seconds_data = pyz__xwcjc._getvalue()
    tpfm__nov.microseconds_data = qrx__xtiyy._getvalue()
    tpfm__nov.null_bitmap = mma__escno._getvalue()
    fmpe__ypxrr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tpfm__nov._getvalue(), is_error=fmpe__ypxrr)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    ebgwy__cth = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    chnw__bccc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ebgwy__cth.days_data)
    pyz__xwcjc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ebgwy__cth.seconds_data).data
    qrx__xtiyy = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ebgwy__cth.microseconds_data).data
    mhndt__joxcp = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, ebgwy__cth.null_bitmap).data
    n = c.builder.extract_value(chnw__bccc.shape, 0)
    cso__jgqws = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    empwc__fqe = cgutils.get_or_insert_function(c.builder.module,
        cso__jgqws, name='box_datetime_timedelta_array')
    bgsd__gdnp = c.builder.call(empwc__fqe, [n, chnw__bccc.data, pyz__xwcjc,
        qrx__xtiyy, mhndt__joxcp])
    c.context.nrt.decref(c.builder, typ, val)
    return bgsd__gdnp


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        nospn__myf, gjb__wgtwj, ivd__bqhx, fcot__ufmfm = args
        job__uomvc = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        job__uomvc.days_data = nospn__myf
        job__uomvc.seconds_data = gjb__wgtwj
        job__uomvc.microseconds_data = ivd__bqhx
        job__uomvc.null_bitmap = fcot__ufmfm
        context.nrt.incref(builder, signature.args[0], nospn__myf)
        context.nrt.incref(builder, signature.args[1], gjb__wgtwj)
        context.nrt.incref(builder, signature.args[2], ivd__bqhx)
        context.nrt.incref(builder, signature.args[3], fcot__ufmfm)
        return job__uomvc._getvalue()
    drbws__wan = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return drbws__wan, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    chnw__bccc = np.empty(n, np.int64)
    pyz__xwcjc = np.empty(n, np.int64)
    qrx__xtiyy = np.empty(n, np.int64)
    yfceg__sttur = np.empty(n + 7 >> 3, np.uint8)
    for sig__iuar, s in enumerate(pyval):
        yff__xfla = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(yfceg__sttur, sig__iuar, int(
            not yff__xfla))
        if not yff__xfla:
            chnw__bccc[sig__iuar] = s.days
            pyz__xwcjc[sig__iuar] = s.seconds
            qrx__xtiyy[sig__iuar] = s.microseconds
    ifg__hxfad = context.get_constant_generic(builder, days_data_type,
        chnw__bccc)
    tkhaw__lftrc = context.get_constant_generic(builder, seconds_data_type,
        pyz__xwcjc)
    hckn__wohd = context.get_constant_generic(builder,
        microseconds_data_type, qrx__xtiyy)
    vaqn__gek = context.get_constant_generic(builder, nulls_type, yfceg__sttur)
    return lir.Constant.literal_struct([ifg__hxfad, tkhaw__lftrc,
        hckn__wohd, vaqn__gek])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    chnw__bccc = np.empty(n, dtype=np.int64)
    pyz__xwcjc = np.empty(n, dtype=np.int64)
    qrx__xtiyy = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(chnw__bccc, pyz__xwcjc, qrx__xtiyy,
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
            ati__ioei = bodo.utils.conversion.coerce_to_ndarray(ind)
            zajye__vwins = A._null_bitmap
            sce__figmp = A._days_data[ati__ioei]
            kvce__zguuh = A._seconds_data[ati__ioei]
            qdnn__nklf = A._microseconds_data[ati__ioei]
            n = len(sce__figmp)
            yjb__umsxc = get_new_null_mask_bool_index(zajye__vwins, ind, n)
            return init_datetime_timedelta_array(sce__figmp, kvce__zguuh,
                qdnn__nklf, yjb__umsxc)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            ati__ioei = bodo.utils.conversion.coerce_to_ndarray(ind)
            zajye__vwins = A._null_bitmap
            sce__figmp = A._days_data[ati__ioei]
            kvce__zguuh = A._seconds_data[ati__ioei]
            qdnn__nklf = A._microseconds_data[ati__ioei]
            n = len(sce__figmp)
            yjb__umsxc = get_new_null_mask_int_index(zajye__vwins, ati__ioei, n
                )
            return init_datetime_timedelta_array(sce__figmp, kvce__zguuh,
                qdnn__nklf, yjb__umsxc)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            zajye__vwins = A._null_bitmap
            sce__figmp = np.ascontiguousarray(A._days_data[ind])
            kvce__zguuh = np.ascontiguousarray(A._seconds_data[ind])
            qdnn__nklf = np.ascontiguousarray(A._microseconds_data[ind])
            yjb__umsxc = get_new_null_mask_slice_index(zajye__vwins, ind, n)
            return init_datetime_timedelta_array(sce__figmp, kvce__zguuh,
                qdnn__nklf, yjb__umsxc)
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
    secsc__hdd = (
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
            raise BodoError(secsc__hdd)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(secsc__hdd)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for sig__iuar in range(n):
                    A._days_data[ind[sig__iuar]] = val._days
                    A._seconds_data[ind[sig__iuar]] = val._seconds
                    A._microseconds_data[ind[sig__iuar]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[sig__iuar], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for sig__iuar in range(n):
                    A._days_data[ind[sig__iuar]] = val._days_data[sig__iuar]
                    A._seconds_data[ind[sig__iuar]] = val._seconds_data[
                        sig__iuar]
                    A._microseconds_data[ind[sig__iuar]
                        ] = val._microseconds_data[sig__iuar]
                    calvp__qmh = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, sig__iuar)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[sig__iuar], calvp__qmh)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for sig__iuar in range(n):
                    if not bodo.libs.array_kernels.isna(ind, sig__iuar
                        ) and ind[sig__iuar]:
                        A._days_data[sig__iuar] = val._days
                        A._seconds_data[sig__iuar] = val._seconds
                        A._microseconds_data[sig__iuar] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            sig__iuar, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                xjyd__vnl = 0
                for sig__iuar in range(n):
                    if not bodo.libs.array_kernels.isna(ind, sig__iuar
                        ) and ind[sig__iuar]:
                        A._days_data[sig__iuar] = val._days_data[xjyd__vnl]
                        A._seconds_data[sig__iuar] = val._seconds_data[
                            xjyd__vnl]
                        A._microseconds_data[sig__iuar
                            ] = val._microseconds_data[xjyd__vnl]
                        calvp__qmh = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, xjyd__vnl)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            sig__iuar, calvp__qmh)
                        xjyd__vnl += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                ssw__dmpuw = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for sig__iuar in range(ssw__dmpuw.start, ssw__dmpuw.stop,
                    ssw__dmpuw.step):
                    A._days_data[sig__iuar] = val._days
                    A._seconds_data[sig__iuar] = val._seconds
                    A._microseconds_data[sig__iuar] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        sig__iuar, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                ujoz__fbz = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, ujoz__fbz, ind, n
                    )
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
            ebgwy__cth = arg1
            numba.parfors.parfor.init_prange()
            n = len(ebgwy__cth)
            A = alloc_datetime_timedelta_array(n)
            for sig__iuar in numba.parfors.parfor.internal_prange(n):
                A[sig__iuar] = ebgwy__cth[sig__iuar] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            vmclb__gui = True
        else:
            vmclb__gui = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                axuq__xdv = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for sig__iuar in numba.parfors.parfor.internal_prange(n):
                    wgdah__yaniq = bodo.libs.array_kernels.isna(lhs, sig__iuar)
                    kdpy__tjg = bodo.libs.array_kernels.isna(rhs, sig__iuar)
                    if wgdah__yaniq or kdpy__tjg:
                        ncnb__aua = vmclb__gui
                    else:
                        ncnb__aua = op(lhs[sig__iuar], rhs[sig__iuar])
                    axuq__xdv[sig__iuar] = ncnb__aua
                return axuq__xdv
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                axuq__xdv = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for sig__iuar in numba.parfors.parfor.internal_prange(n):
                    calvp__qmh = bodo.libs.array_kernels.isna(lhs, sig__iuar)
                    if calvp__qmh:
                        ncnb__aua = vmclb__gui
                    else:
                        ncnb__aua = op(lhs[sig__iuar], rhs)
                    axuq__xdv[sig__iuar] = ncnb__aua
                return axuq__xdv
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                axuq__xdv = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for sig__iuar in numba.parfors.parfor.internal_prange(n):
                    calvp__qmh = bodo.libs.array_kernels.isna(rhs, sig__iuar)
                    if calvp__qmh:
                        ncnb__aua = vmclb__gui
                    else:
                        ncnb__aua = op(lhs, rhs[sig__iuar])
                    axuq__xdv[sig__iuar] = ncnb__aua
                return axuq__xdv
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for dyrgk__nkd in timedelta_unsupported_attrs:
        olpfa__rcsq = 'pandas.Timedelta.' + dyrgk__nkd
        overload_attribute(PDTimeDeltaType, dyrgk__nkd)(
            create_unsupported_overload(olpfa__rcsq))
    for vhwy__ljgfv in timedelta_unsupported_methods:
        olpfa__rcsq = 'pandas.Timedelta.' + vhwy__ljgfv
        overload_method(PDTimeDeltaType, vhwy__ljgfv)(
            create_unsupported_overload(olpfa__rcsq + '()'))


_intstall_pd_timedelta_unsupported()
