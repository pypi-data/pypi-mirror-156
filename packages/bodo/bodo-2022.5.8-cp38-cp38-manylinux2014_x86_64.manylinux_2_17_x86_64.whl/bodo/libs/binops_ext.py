""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_str_arr_type, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        usbwg__jrblw = lhs.data if isinstance(lhs, SeriesType) else lhs
        jjcsx__kgkix = rhs.data if isinstance(rhs, SeriesType) else rhs
        if usbwg__jrblw in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and jjcsx__kgkix.dtype in (bodo.datetime64ns, bodo.timedelta64ns
            ):
            usbwg__jrblw = jjcsx__kgkix.dtype
        elif jjcsx__kgkix in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and usbwg__jrblw.dtype in (bodo.datetime64ns, bodo.timedelta64ns
            ):
            jjcsx__kgkix = usbwg__jrblw.dtype
        uks__mljx = usbwg__jrblw, jjcsx__kgkix
        xeh__umu = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            vhf__mgl = self.context.resolve_function_type(self.key,
                uks__mljx, {}).return_type
        except Exception as xngnq__tgjig:
            raise BodoError(xeh__umu)
        if is_overload_bool(vhf__mgl):
            raise BodoError(xeh__umu)
        dznai__lev = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        chi__jjprv = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        vluw__zel = types.bool_
        pvcsq__myz = SeriesType(vluw__zel, vhf__mgl, dznai__lev, chi__jjprv)
        return pvcsq__myz(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        krxo__bjfj = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if krxo__bjfj is None:
            krxo__bjfj = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, krxo__bjfj, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        usbwg__jrblw = lhs.data if isinstance(lhs, SeriesType) else lhs
        jjcsx__kgkix = rhs.data if isinstance(rhs, SeriesType) else rhs
        uks__mljx = usbwg__jrblw, jjcsx__kgkix
        xeh__umu = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            vhf__mgl = self.context.resolve_function_type(self.key,
                uks__mljx, {}).return_type
        except Exception as mkm__zfk:
            raise BodoError(xeh__umu)
        dznai__lev = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        chi__jjprv = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        vluw__zel = vhf__mgl.dtype
        pvcsq__myz = SeriesType(vluw__zel, vhf__mgl, dznai__lev, chi__jjprv)
        return pvcsq__myz(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        krxo__bjfj = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if krxo__bjfj is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                krxo__bjfj = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, krxo__bjfj, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (is_str_arr_type(lhs) or types.unliteral(
            lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
                f'{op} operator')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
                f'{op} operator')
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            krxo__bjfj = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return krxo__bjfj(lhs, rhs)
        if is_str_arr_type(lhs) or is_str_arr_type(rhs):
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            krxo__bjfj = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return krxo__bjfj(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    fxdwf__ynj = lhs == datetime_timedelta_type and rhs == datetime_date_type
    hmmtw__yuw = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return fxdwf__ynj or hmmtw__yuw


def add_timestamp(lhs, rhs):
    otg__cokb = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    royzr__khvcb = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return otg__cokb or royzr__khvcb


def add_datetime_and_timedeltas(lhs, rhs):
    gsyft__udacc = [datetime_timedelta_type, pd_timedelta_type]
    xtung__pnwe = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    ukxyc__wqu = lhs in gsyft__udacc and rhs in gsyft__udacc
    jwx__yal = (lhs == datetime_datetime_type and rhs in gsyft__udacc or 
        rhs == datetime_datetime_type and lhs in gsyft__udacc)
    return ukxyc__wqu or jwx__yal


def mul_string_arr_and_int(lhs, rhs):
    jjcsx__kgkix = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    usbwg__jrblw = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return jjcsx__kgkix or usbwg__jrblw


def mul_timedelta_and_int(lhs, rhs):
    fxdwf__ynj = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    hmmtw__yuw = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return fxdwf__ynj or hmmtw__yuw


def mul_date_offset_and_int(lhs, rhs):
    uqz__bif = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    qkt__kked = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return uqz__bif or qkt__kked


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    mpx__luui = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    tjh__nmww = [date_offset_type, month_begin_type, month_end_type, week_type]
    return rhs in tjh__nmww and lhs in mpx__luui


def sub_dt_index_and_timestamp(lhs, rhs):
    xtb__pzcn = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    aenk__zbqjn = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return xtb__pzcn or aenk__zbqjn


def sub_dt_or_td(lhs, rhs):
    infnt__jail = lhs == datetime_date_type and rhs == datetime_timedelta_type
    hpguz__ozv = lhs == datetime_date_type and rhs == datetime_date_type
    xaz__blk = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return infnt__jail or hpguz__ozv or xaz__blk


def sub_datetime_and_timedeltas(lhs, rhs):
    juc__kuvtg = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    ghchr__kom = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return juc__kuvtg or ghchr__kom


def div_timedelta_and_int(lhs, rhs):
    ukxyc__wqu = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    rbqqv__uiau = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return ukxyc__wqu or rbqqv__uiau


def div_datetime_timedelta(lhs, rhs):
    ukxyc__wqu = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    rbqqv__uiau = lhs == datetime_timedelta_type and rhs == types.int64
    return ukxyc__wqu or rbqqv__uiau


def mod_timedeltas(lhs, rhs):
    pdgyy__ocvv = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    njg__dijr = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return pdgyy__ocvv or njg__dijr


def cmp_dt_index_to_string(lhs, rhs):
    xtb__pzcn = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    aenk__zbqjn = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return xtb__pzcn or aenk__zbqjn


def cmp_timestamp_or_date(lhs, rhs):
    sigei__hru = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    hwofl__vgko = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    sbpu__rjyu = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    azagw__djmv = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    iqgh__occ = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return sigei__hru or hwofl__vgko or sbpu__rjyu or azagw__djmv or iqgh__occ


def cmp_timeseries(lhs, rhs):
    zwryw__llw = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    tlmbn__mzhh = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    yyjqz__ucbv = zwryw__llw or tlmbn__mzhh
    jyel__xhh = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ono__fvd = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ydf__tlgnj = jyel__xhh or ono__fvd
    return yyjqz__ucbv or ydf__tlgnj


def cmp_timedeltas(lhs, rhs):
    ukxyc__wqu = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in ukxyc__wqu and rhs in ukxyc__wqu


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    gxbhe__fxz = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return gxbhe__fxz


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    amo__mxzs = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    tlyqh__cvrw = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    tdid__tfmzq = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    vdnh__egbz = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return amo__mxzs or tlyqh__cvrw or tdid__tfmzq or vdnh__egbz


def args_td_and_int_array(lhs, rhs):
    wcvlm__mkyzq = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    fefn__tttps = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return wcvlm__mkyzq and fefn__tttps


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        hmmtw__yuw = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        fxdwf__ynj = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        rirhc__dfl = hmmtw__yuw or fxdwf__ynj
        efxxs__vvgn = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        uzrqk__qlapo = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        wciia__uwwj = efxxs__vvgn or uzrqk__qlapo
        dsqpk__ilec = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        cukyx__hukt = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        wiar__obi = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        pjb__hsq = dsqpk__ilec or cukyx__hukt or wiar__obi
        qgn__gydlk = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        yxzzi__zsha = isinstance(lhs, tys) or isinstance(rhs, tys)
        xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (rirhc__dfl or wciia__uwwj or pjb__hsq or qgn__gydlk or
            yxzzi__zsha or xawp__ayb)
    if op == operator.pow:
        egysm__tlpn = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        pebd__wsd = isinstance(lhs, types.Float) and isinstance(rhs, (types
            .IntegerLiteral, types.Float, types.Integer) or rhs in types.
            unsigned_domain or rhs in types.signed_domain)
        wiar__obi = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return egysm__tlpn or pebd__wsd or wiar__obi or xawp__ayb
    if op == operator.floordiv:
        cukyx__hukt = lhs in types.real_domain and rhs in types.real_domain
        dsqpk__ilec = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        qag__dhg = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        ukxyc__wqu = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (cukyx__hukt or dsqpk__ilec or qag__dhg or ukxyc__wqu or
            xawp__ayb)
    if op == operator.truediv:
        fai__amg = lhs in machine_ints and rhs in machine_ints
        cukyx__hukt = lhs in types.real_domain and rhs in types.real_domain
        wiar__obi = lhs in types.complex_domain and rhs in types.complex_domain
        dsqpk__ilec = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        qag__dhg = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        vxwzt__xrw = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ukxyc__wqu = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (fai__amg or cukyx__hukt or wiar__obi or dsqpk__ilec or
            qag__dhg or vxwzt__xrw or ukxyc__wqu or xawp__ayb)
    if op == operator.mod:
        fai__amg = lhs in machine_ints and rhs in machine_ints
        cukyx__hukt = lhs in types.real_domain and rhs in types.real_domain
        dsqpk__ilec = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        qag__dhg = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return fai__amg or cukyx__hukt or dsqpk__ilec or qag__dhg or xawp__ayb
    if op == operator.add or op == operator.sub:
        rirhc__dfl = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        dnau__uygv = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        bucx__pybye = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        buf__vpzib = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        dsqpk__ilec = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        cukyx__hukt = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        wiar__obi = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        pjb__hsq = dsqpk__ilec or cukyx__hukt or wiar__obi
        xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        ujeoi__pnda = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        qgn__gydlk = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        rzt__nwrhs = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        ldz__oiqv = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        exsm__arh = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        smt__prx = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        wttl__acve = rzt__nwrhs or ldz__oiqv or exsm__arh or smt__prx
        wciia__uwwj = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        yqszp__aiyh = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        trpgg__ogdmf = wciia__uwwj or yqszp__aiyh
        gsh__iqccg = lhs == types.NPTimedelta and rhs == types.NPDatetime
        axt__qjl = (ujeoi__pnda or qgn__gydlk or wttl__acve or trpgg__ogdmf or
            gsh__iqccg)
        gfkib__eune = op == operator.add and axt__qjl
        return (rirhc__dfl or dnau__uygv or bucx__pybye or buf__vpzib or
            pjb__hsq or xawp__ayb or gfkib__eune)


def cmp_op_supported_by_numba(lhs, rhs):
    xawp__ayb = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    qgn__gydlk = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    rirhc__dfl = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    oli__qru = isinstance(lhs, types.NPDatetime) and isinstance(rhs, types.
        NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    wciia__uwwj = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    ujeoi__pnda = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
        types.BaseTuple)
    buf__vpzib = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    pjb__hsq = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    fhov__ibvdz = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    cok__vzjt = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    vvf__uxaj = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    ayj__lelu = isinstance(lhs, types.EnumMember) and isinstance(rhs, types
        .EnumMember)
    vto__avvur = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (qgn__gydlk or rirhc__dfl or oli__qru or wciia__uwwj or
        ujeoi__pnda or buf__vpzib or pjb__hsq or fhov__ibvdz or cok__vzjt or
        vvf__uxaj or xawp__ayb or ayj__lelu or vto__avvur)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        jqds__cgr = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(jqds__cgr)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        jqds__cgr = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(jqds__cgr)


install_arith_ops()
