"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType, get_series_data, get_series_index, get_series_name, init_series
from bodo.libs.pd_datetime_arr_ext import PandasDatetimeTZDtype
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        adzn__skhq = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(adzn__skhq)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wrkru__bpv = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, wrkru__bpv)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        apag__ywl, = args
        izjx__jfrkv = signature.return_type
        vpncp__xst = cgutils.create_struct_proxy(izjx__jfrkv)(context, builder)
        vpncp__xst.obj = apag__ywl
        context.nrt.incref(builder, signature.args[0], apag__ywl)
        return vpncp__xst._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if S_dt.stype.dtype != types.NPDatetime('ns') and not isinstance(S_dt
            .stype.dtype, PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{field}')
        pves__wynh = 'def impl(S_dt):\n'
        pves__wynh += '    S = S_dt._obj\n'
        pves__wynh += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        pves__wynh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        pves__wynh += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        pves__wynh += '    numba.parfors.parfor.init_prange()\n'
        pves__wynh += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            pves__wynh += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            pves__wynh += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        pves__wynh += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        pves__wynh += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        pves__wynh += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        pves__wynh += '            continue\n'
        pves__wynh += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            pves__wynh += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                pves__wynh += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            pves__wynh += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            arykj__hhh = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            pves__wynh += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            pves__wynh += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            pves__wynh += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(arykj__hhh[field]))
        elif field == 'is_leap_year':
            pves__wynh += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            pves__wynh += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            arykj__hhh = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            pves__wynh += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            pves__wynh += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            pves__wynh += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(arykj__hhh[field]))
        else:
            pves__wynh += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            pves__wynh += '        out_arr[i] = ts.' + field + '\n'
        pves__wynh += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        gjmky__jfw = {}
        exec(pves__wynh, {'bodo': bodo, 'numba': numba, 'np': np}, gjmky__jfw)
        impl = gjmky__jfw['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        xidm__llzq = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(xidm__llzq)


_install_date_fields()


def create_date_method_overload(method):
    oftl__uam = method in ['day_name', 'month_name']
    if oftl__uam:
        pves__wynh = 'def overload_method(S_dt, locale=None):\n'
        pves__wynh += '    unsupported_args = dict(locale=locale)\n'
        pves__wynh += '    arg_defaults = dict(locale=None)\n'
        pves__wynh += '    bodo.utils.typing.check_unsupported_args(\n'
        pves__wynh += f"        'Series.dt.{method}',\n"
        pves__wynh += '        unsupported_args,\n'
        pves__wynh += '        arg_defaults,\n'
        pves__wynh += "        package_name='pandas',\n"
        pves__wynh += "        module_name='Series',\n"
        pves__wynh += '    )\n'
    else:
        pves__wynh = 'def overload_method(S_dt):\n'
        pves__wynh += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    pves__wynh += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    pves__wynh += '        return\n'
    if oftl__uam:
        pves__wynh += '    def impl(S_dt, locale=None):\n'
    else:
        pves__wynh += '    def impl(S_dt):\n'
    pves__wynh += '        S = S_dt._obj\n'
    pves__wynh += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    pves__wynh += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    pves__wynh += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    pves__wynh += '        numba.parfors.parfor.init_prange()\n'
    pves__wynh += '        n = len(arr)\n'
    if oftl__uam:
        pves__wynh += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        pves__wynh += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    pves__wynh += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    pves__wynh += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    pves__wynh += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    pves__wynh += '                continue\n'
    pves__wynh += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    pves__wynh += f'            method_val = ts.{method}()\n'
    if oftl__uam:
        pves__wynh += '            out_arr[i] = method_val\n'
    else:
        pves__wynh += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    pves__wynh += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    pves__wynh += '    return impl\n'
    gjmky__jfw = {}
    exec(pves__wynh, {'bodo': bodo, 'numba': numba, 'np': np}, gjmky__jfw)
    overload_method = gjmky__jfw['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        xidm__llzq = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            xidm__llzq)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        uot__jgm = S_dt._obj
        znc__xmjvu = bodo.hiframes.pd_series_ext.get_series_data(uot__jgm)
        jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(uot__jgm)
        adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(uot__jgm)
        numba.parfors.parfor.init_prange()
        srmhu__pirbv = len(znc__xmjvu)
        vlz__lydw = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            srmhu__pirbv)
        for uodk__qtsi in numba.parfors.parfor.internal_prange(srmhu__pirbv):
            ljolu__ydhzd = znc__xmjvu[uodk__qtsi]
            tiwdx__pfu = bodo.utils.conversion.box_if_dt64(ljolu__ydhzd)
            vlz__lydw[uodk__qtsi] = datetime.date(tiwdx__pfu.year,
                tiwdx__pfu.month, tiwdx__pfu.day)
        return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
            jpojf__tqg, adzn__skhq)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and (S_dt.stype.
            dtype == types.NPDatetime('ns') or isinstance(S_dt.stype.dtype,
            PandasDatetimeTZDtype))):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{attr}')
        if attr == 'components':
            urwac__nafz = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            nrs__gmf = 'convert_numpy_timedelta64_to_pd_timedelta'
            nkpa__ghhrt = 'np.empty(n, np.int64)'
            myjym__oln = attr
        elif attr == 'isocalendar':
            urwac__nafz = ['year', 'week', 'day']
            nrs__gmf = 'convert_datetime64_to_timestamp'
            nkpa__ghhrt = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            myjym__oln = attr + '()'
        pves__wynh = 'def impl(S_dt):\n'
        pves__wynh += '    S = S_dt._obj\n'
        pves__wynh += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        pves__wynh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        pves__wynh += '    numba.parfors.parfor.init_prange()\n'
        pves__wynh += '    n = len(arr)\n'
        for field in urwac__nafz:
            pves__wynh += '    {} = {}\n'.format(field, nkpa__ghhrt)
        pves__wynh += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        pves__wynh += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in urwac__nafz:
            pves__wynh += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        pves__wynh += '            continue\n'
        amqj__hnt = '(' + '[i], '.join(urwac__nafz) + '[i])'
        pves__wynh += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(amqj__hnt, nrs__gmf, myjym__oln))
        awc__ldq = '(' + ', '.join(urwac__nafz) + ')'
        pves__wynh += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(awc__ldq))
        gjmky__jfw = {}
        exec(pves__wynh, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(urwac__nafz))}, gjmky__jfw)
        impl = gjmky__jfw['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    tcij__pxcy = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, jovat__sqcl in tcij__pxcy:
        xidm__llzq = create_series_dt_df_output_overload(attr)
        jovat__sqcl(SeriesDatetimePropertiesType, attr, inline='always')(
            xidm__llzq)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        pves__wynh = 'def impl(S_dt):\n'
        pves__wynh += '    S = S_dt._obj\n'
        pves__wynh += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        pves__wynh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        pves__wynh += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        pves__wynh += '    numba.parfors.parfor.init_prange()\n'
        pves__wynh += '    n = len(A)\n'
        pves__wynh += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        pves__wynh += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        pves__wynh += '        if bodo.libs.array_kernels.isna(A, i):\n'
        pves__wynh += '            bodo.libs.array_kernels.setna(B, i)\n'
        pves__wynh += '            continue\n'
        pves__wynh += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            pves__wynh += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            pves__wynh += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            pves__wynh += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            pves__wynh += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        pves__wynh += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        gjmky__jfw = {}
        exec(pves__wynh, {'numba': numba, 'np': np, 'bodo': bodo}, gjmky__jfw)
        impl = gjmky__jfw['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        pves__wynh = 'def impl(S_dt):\n'
        pves__wynh += '    S = S_dt._obj\n'
        pves__wynh += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        pves__wynh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        pves__wynh += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        pves__wynh += '    numba.parfors.parfor.init_prange()\n'
        pves__wynh += '    n = len(A)\n'
        if method == 'total_seconds':
            pves__wynh += '    B = np.empty(n, np.float64)\n'
        else:
            pves__wynh += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        pves__wynh += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        pves__wynh += '        if bodo.libs.array_kernels.isna(A, i):\n'
        pves__wynh += '            bodo.libs.array_kernels.setna(B, i)\n'
        pves__wynh += '            continue\n'
        pves__wynh += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            pves__wynh += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            pves__wynh += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            pves__wynh += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            pves__wynh += '    return B\n'
        gjmky__jfw = {}
        exec(pves__wynh, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, gjmky__jfw)
        impl = gjmky__jfw['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        xidm__llzq = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(xidm__llzq)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        xidm__llzq = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            xidm__llzq)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        uot__jgm = S_dt._obj
        bkdym__mgaf = bodo.hiframes.pd_series_ext.get_series_data(uot__jgm)
        jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(uot__jgm)
        adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(uot__jgm)
        numba.parfors.parfor.init_prange()
        srmhu__pirbv = len(bkdym__mgaf)
        rdja__pfja = bodo.libs.str_arr_ext.pre_alloc_string_array(srmhu__pirbv,
            -1)
        for dzwyb__kgbl in numba.parfors.parfor.internal_prange(srmhu__pirbv):
            if bodo.libs.array_kernels.isna(bkdym__mgaf, dzwyb__kgbl):
                bodo.libs.array_kernels.setna(rdja__pfja, dzwyb__kgbl)
                continue
            rdja__pfja[dzwyb__kgbl] = bodo.utils.conversion.box_if_dt64(
                bkdym__mgaf[dzwyb__kgbl]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(rdja__pfja,
            jpojf__tqg, adzn__skhq)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        uot__jgm = S_dt._obj
        ukbab__pjs = get_series_data(uot__jgm).tz_convert(tz)
        jpojf__tqg = get_series_index(uot__jgm)
        adzn__skhq = get_series_name(uot__jgm)
        return init_series(ukbab__pjs, jpojf__tqg, adzn__skhq)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'
            ) and not isinstance(S_dt.stype.dtype, bodo.libs.
            pd_datetime_arr_ext.PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{method}()')
        ytzv__rpdd = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        wqb__rtb = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', ytzv__rpdd, wqb__rtb,
            package_name='pandas', module_name='Series')
        pves__wynh = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        pves__wynh += '    S = S_dt._obj\n'
        pves__wynh += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        pves__wynh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        pves__wynh += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        pves__wynh += '    numba.parfors.parfor.init_prange()\n'
        pves__wynh += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            pves__wynh += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            pves__wynh += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        pves__wynh += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        pves__wynh += '        if bodo.libs.array_kernels.isna(A, i):\n'
        pves__wynh += '            bodo.libs.array_kernels.setna(B, i)\n'
        pves__wynh += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            wvs__frycq = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            bum__wstjz = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            wvs__frycq = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            bum__wstjz = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        pves__wynh += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            bum__wstjz, wvs__frycq, method)
        pves__wynh += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        gjmky__jfw = {}
        exec(pves__wynh, {'numba': numba, 'np': np, 'bodo': bodo}, gjmky__jfw)
        impl = gjmky__jfw['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    makvx__xzr = ['ceil', 'floor', 'round']
    for method in makvx__xzr:
        xidm__llzq = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            xidm__llzq)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ebwgg__fupei = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dim__bmv = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ebwgg__fupei)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                zfwmr__gluxq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ylts__mxnlf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    zfwmr__gluxq)
                srmhu__pirbv = len(dim__bmv)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    rpbbq__wsp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dim__bmv[uodk__qtsi]))
                    iigv__mijb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ylts__mxnlf[uodk__qtsi]))
                    if rpbbq__wsp == zdc__dmi or iigv__mijb == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(rpbbq__wsp, iigv__mijb)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ylts__mxnlf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, dt64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    rli__yzg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ylts__mxnlf[uodk__qtsi]))
                    if mkm__oecj == zdc__dmi or rli__yzg == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(mkm__oecj, rli__yzg)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ylts__mxnlf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, dt64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    rli__yzg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ylts__mxnlf[uodk__qtsi]))
                    if mkm__oecj == zdc__dmi or rli__yzg == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(mkm__oecj, rli__yzg)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                drzfb__cnjl = rhs.value
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if mkm__oecj == zdc__dmi or drzfb__cnjl == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(mkm__oecj, drzfb__cnjl)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                drzfb__cnjl = lhs.value
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if drzfb__cnjl == zdc__dmi or mkm__oecj == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(drzfb__cnjl, mkm__oecj)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, dt64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                ixlw__tvc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                rli__yzg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ixlw__tvc))
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if mkm__oecj == zdc__dmi or rli__yzg == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(mkm__oecj, rli__yzg)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, dt64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                ixlw__tvc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                rli__yzg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ixlw__tvc))
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if mkm__oecj == zdc__dmi or rli__yzg == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(mkm__oecj, rli__yzg)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                ncfgk__vtra = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ncfgk__vtra)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    pkm__ool = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if pkm__ool == zdc__dmi or mkm__oecj == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(pkm__ool, mkm__oecj)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                ncfgk__vtra = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                mkm__oecj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ncfgk__vtra)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    pkm__ool = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if mkm__oecj == zdc__dmi or pkm__ool == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(mkm__oecj, pkm__ool)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            sza__eyt = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                znc__xmjvu = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(sza__eyt))
                ixlw__tvc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                rli__yzg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ixlw__tvc))
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    vkyy__zkf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if rli__yzg == zdc__dmi or vkyy__zkf == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(vkyy__zkf, rli__yzg)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            sza__eyt = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                znc__xmjvu = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                uot__jgm = np.empty(srmhu__pirbv, timedelta64_dtype)
                zdc__dmi = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(sza__eyt))
                ixlw__tvc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                rli__yzg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ixlw__tvc))
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    vkyy__zkf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if rli__yzg == zdc__dmi or vkyy__zkf == zdc__dmi:
                        sxg__nlwn = zdc__dmi
                    else:
                        sxg__nlwn = op(rli__yzg, vkyy__zkf)
                    uot__jgm[uodk__qtsi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        sxg__nlwn)
                return bodo.hiframes.pd_series_ext.init_series(uot__jgm,
                    jpojf__tqg, adzn__skhq)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            ixz__ldq = True
        else:
            ixz__ldq = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            sza__eyt = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                znc__xmjvu = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                vlz__lydw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    srmhu__pirbv)
                zdc__dmi = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(sza__eyt))
                jmrhe__flgr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                til__anxt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jmrhe__flgr))
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    adw__dmzrg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if adw__dmzrg == zdc__dmi or til__anxt == zdc__dmi:
                        sxg__nlwn = ixz__ldq
                    else:
                        sxg__nlwn = op(adw__dmzrg, til__anxt)
                    vlz__lydw[uodk__qtsi] = sxg__nlwn
                return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            sza__eyt = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                znc__xmjvu = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                vlz__lydw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    srmhu__pirbv)
                zdc__dmi = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(sza__eyt))
                qfb__myzjd = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                adw__dmzrg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(qfb__myzjd))
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    til__anxt = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if adw__dmzrg == zdc__dmi or til__anxt == zdc__dmi:
                        sxg__nlwn = ixz__ldq
                    else:
                        sxg__nlwn = op(adw__dmzrg, til__anxt)
                    vlz__lydw[uodk__qtsi] = sxg__nlwn
                return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                srmhu__pirbv = len(znc__xmjvu)
                vlz__lydw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    srmhu__pirbv)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    adw__dmzrg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if adw__dmzrg == zdc__dmi or rhs.value == zdc__dmi:
                        sxg__nlwn = ixz__ldq
                    else:
                        sxg__nlwn = op(adw__dmzrg, rhs.value)
                    vlz__lydw[uodk__qtsi] = sxg__nlwn
                return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
                    jpojf__tqg, adzn__skhq)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                srmhu__pirbv = len(znc__xmjvu)
                vlz__lydw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    srmhu__pirbv)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    til__anxt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        znc__xmjvu[uodk__qtsi])
                    if til__anxt == zdc__dmi or lhs.value == zdc__dmi:
                        sxg__nlwn = ixz__ldq
                    else:
                        sxg__nlwn = op(lhs.value, til__anxt)
                    vlz__lydw[uodk__qtsi] = sxg__nlwn
                return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                srmhu__pirbv = len(znc__xmjvu)
                vlz__lydw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    srmhu__pirbv)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                hnsp__ckde = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                vrav__xgdls = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hnsp__ckde)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    adw__dmzrg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if adw__dmzrg == zdc__dmi or vrav__xgdls == zdc__dmi:
                        sxg__nlwn = ixz__ldq
                    else:
                        sxg__nlwn = op(adw__dmzrg, vrav__xgdls)
                    vlz__lydw[uodk__qtsi] = sxg__nlwn
                return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
                    jpojf__tqg, adzn__skhq)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            sza__eyt = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                kitv__vyz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                znc__xmjvu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kitv__vyz)
                jpojf__tqg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adzn__skhq = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                srmhu__pirbv = len(znc__xmjvu)
                vlz__lydw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    srmhu__pirbv)
                zdc__dmi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    sza__eyt)
                hnsp__ckde = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                vrav__xgdls = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hnsp__ckde)
                for uodk__qtsi in numba.parfors.parfor.internal_prange(
                    srmhu__pirbv):
                    ncfgk__vtra = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(znc__xmjvu[uodk__qtsi]))
                    if ncfgk__vtra == zdc__dmi or vrav__xgdls == zdc__dmi:
                        sxg__nlwn = ixz__ldq
                    else:
                        sxg__nlwn = op(vrav__xgdls, ncfgk__vtra)
                    vlz__lydw[uodk__qtsi] = sxg__nlwn
                return bodo.hiframes.pd_series_ext.init_series(vlz__lydw,
                    jpojf__tqg, adzn__skhq)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for ekcr__vcb in series_dt_unsupported_attrs:
        qrnm__bvbs = 'Series.dt.' + ekcr__vcb
        overload_attribute(SeriesDatetimePropertiesType, ekcr__vcb)(
            create_unsupported_overload(qrnm__bvbs))
    for jfl__rtx in series_dt_unsupported_methods:
        qrnm__bvbs = 'Series.dt.' + jfl__rtx
        overload_method(SeriesDatetimePropertiesType, jfl__rtx,
            no_unliteral=True)(create_unsupported_overload(qrnm__bvbs))


_install_series_dt_unsupported()
