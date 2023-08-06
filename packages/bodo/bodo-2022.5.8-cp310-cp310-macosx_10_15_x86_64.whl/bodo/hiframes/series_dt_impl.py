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
        psls__huta = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(psls__huta)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ximb__bwwti = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, ximb__bwwti)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        nuafu__vojsg, = args
        jjkvo__ovqqv = signature.return_type
        yxith__ratc = cgutils.create_struct_proxy(jjkvo__ovqqv)(context,
            builder)
        yxith__ratc.obj = nuafu__vojsg
        context.nrt.incref(builder, signature.args[0], nuafu__vojsg)
        return yxith__ratc._getvalue()
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
        jjr__tqtrk = 'def impl(S_dt):\n'
        jjr__tqtrk += '    S = S_dt._obj\n'
        jjr__tqtrk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        jjr__tqtrk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        jjr__tqtrk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        jjr__tqtrk += '    numba.parfors.parfor.init_prange()\n'
        jjr__tqtrk += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            jjr__tqtrk += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            jjr__tqtrk += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        jjr__tqtrk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        jjr__tqtrk += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        jjr__tqtrk += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        jjr__tqtrk += '            continue\n'
        jjr__tqtrk += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            jjr__tqtrk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                jjr__tqtrk += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            jjr__tqtrk += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            gqk__sdob = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            jjr__tqtrk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            jjr__tqtrk += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            jjr__tqtrk += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(gqk__sdob[field]))
        elif field == 'is_leap_year':
            jjr__tqtrk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            jjr__tqtrk += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            gqk__sdob = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            jjr__tqtrk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            jjr__tqtrk += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            jjr__tqtrk += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(gqk__sdob[field]))
        else:
            jjr__tqtrk += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            jjr__tqtrk += '        out_arr[i] = ts.' + field + '\n'
        jjr__tqtrk += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        okv__uty = {}
        exec(jjr__tqtrk, {'bodo': bodo, 'numba': numba, 'np': np}, okv__uty)
        impl = okv__uty['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        qltt__owapv = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(qltt__owapv)


_install_date_fields()


def create_date_method_overload(method):
    sfu__lsf = method in ['day_name', 'month_name']
    if sfu__lsf:
        jjr__tqtrk = 'def overload_method(S_dt, locale=None):\n'
        jjr__tqtrk += '    unsupported_args = dict(locale=locale)\n'
        jjr__tqtrk += '    arg_defaults = dict(locale=None)\n'
        jjr__tqtrk += '    bodo.utils.typing.check_unsupported_args(\n'
        jjr__tqtrk += f"        'Series.dt.{method}',\n"
        jjr__tqtrk += '        unsupported_args,\n'
        jjr__tqtrk += '        arg_defaults,\n'
        jjr__tqtrk += "        package_name='pandas',\n"
        jjr__tqtrk += "        module_name='Series',\n"
        jjr__tqtrk += '    )\n'
    else:
        jjr__tqtrk = 'def overload_method(S_dt):\n'
        jjr__tqtrk += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    jjr__tqtrk += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    jjr__tqtrk += '        return\n'
    if sfu__lsf:
        jjr__tqtrk += '    def impl(S_dt, locale=None):\n'
    else:
        jjr__tqtrk += '    def impl(S_dt):\n'
    jjr__tqtrk += '        S = S_dt._obj\n'
    jjr__tqtrk += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    jjr__tqtrk += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    jjr__tqtrk += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    jjr__tqtrk += '        numba.parfors.parfor.init_prange()\n'
    jjr__tqtrk += '        n = len(arr)\n'
    if sfu__lsf:
        jjr__tqtrk += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        jjr__tqtrk += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    jjr__tqtrk += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    jjr__tqtrk += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    jjr__tqtrk += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    jjr__tqtrk += '                continue\n'
    jjr__tqtrk += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    jjr__tqtrk += f'            method_val = ts.{method}()\n'
    if sfu__lsf:
        jjr__tqtrk += '            out_arr[i] = method_val\n'
    else:
        jjr__tqtrk += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    jjr__tqtrk += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    jjr__tqtrk += '    return impl\n'
    okv__uty = {}
    exec(jjr__tqtrk, {'bodo': bodo, 'numba': numba, 'np': np}, okv__uty)
    overload_method = okv__uty['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        qltt__owapv = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            qltt__owapv)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        azvb__xoqm = S_dt._obj
        gtert__yjf = bodo.hiframes.pd_series_ext.get_series_data(azvb__xoqm)
        quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(azvb__xoqm)
        psls__huta = bodo.hiframes.pd_series_ext.get_series_name(azvb__xoqm)
        numba.parfors.parfor.init_prange()
        wzt__pbc = len(gtert__yjf)
        dqsd__gxhgk = (bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(wzt__pbc))
        for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
            tte__gxo = gtert__yjf[ipt__kif]
            cfs__oey = bodo.utils.conversion.box_if_dt64(tte__gxo)
            dqsd__gxhgk[ipt__kif] = datetime.date(cfs__oey.year, cfs__oey.
                month, cfs__oey.day)
        return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
            quyyk__hkphr, psls__huta)
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
            vzpct__avb = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            kxl__ubbem = 'convert_numpy_timedelta64_to_pd_timedelta'
            lgxh__qpmd = 'np.empty(n, np.int64)'
            zezoa__dspdf = attr
        elif attr == 'isocalendar':
            vzpct__avb = ['year', 'week', 'day']
            kxl__ubbem = 'convert_datetime64_to_timestamp'
            lgxh__qpmd = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            zezoa__dspdf = attr + '()'
        jjr__tqtrk = 'def impl(S_dt):\n'
        jjr__tqtrk += '    S = S_dt._obj\n'
        jjr__tqtrk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        jjr__tqtrk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        jjr__tqtrk += '    numba.parfors.parfor.init_prange()\n'
        jjr__tqtrk += '    n = len(arr)\n'
        for field in vzpct__avb:
            jjr__tqtrk += '    {} = {}\n'.format(field, lgxh__qpmd)
        jjr__tqtrk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        jjr__tqtrk += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in vzpct__avb:
            jjr__tqtrk += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        jjr__tqtrk += '            continue\n'
        zbxk__jbpi = '(' + '[i], '.join(vzpct__avb) + '[i])'
        jjr__tqtrk += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(zbxk__jbpi, kxl__ubbem, zezoa__dspdf))
        wzdi__vym = '(' + ', '.join(vzpct__avb) + ')'
        jjr__tqtrk += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(wzdi__vym))
        okv__uty = {}
        exec(jjr__tqtrk, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(vzpct__avb))}, okv__uty)
        impl = okv__uty['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    uzu__hokk = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, bsxbw__hno in uzu__hokk:
        qltt__owapv = create_series_dt_df_output_overload(attr)
        bsxbw__hno(SeriesDatetimePropertiesType, attr, inline='always')(
            qltt__owapv)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        jjr__tqtrk = 'def impl(S_dt):\n'
        jjr__tqtrk += '    S = S_dt._obj\n'
        jjr__tqtrk += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        jjr__tqtrk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        jjr__tqtrk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        jjr__tqtrk += '    numba.parfors.parfor.init_prange()\n'
        jjr__tqtrk += '    n = len(A)\n'
        jjr__tqtrk += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        jjr__tqtrk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        jjr__tqtrk += '        if bodo.libs.array_kernels.isna(A, i):\n'
        jjr__tqtrk += '            bodo.libs.array_kernels.setna(B, i)\n'
        jjr__tqtrk += '            continue\n'
        jjr__tqtrk += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            jjr__tqtrk += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            jjr__tqtrk += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            jjr__tqtrk += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            jjr__tqtrk += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        jjr__tqtrk += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        okv__uty = {}
        exec(jjr__tqtrk, {'numba': numba, 'np': np, 'bodo': bodo}, okv__uty)
        impl = okv__uty['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        jjr__tqtrk = 'def impl(S_dt):\n'
        jjr__tqtrk += '    S = S_dt._obj\n'
        jjr__tqtrk += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        jjr__tqtrk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        jjr__tqtrk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        jjr__tqtrk += '    numba.parfors.parfor.init_prange()\n'
        jjr__tqtrk += '    n = len(A)\n'
        if method == 'total_seconds':
            jjr__tqtrk += '    B = np.empty(n, np.float64)\n'
        else:
            jjr__tqtrk += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        jjr__tqtrk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        jjr__tqtrk += '        if bodo.libs.array_kernels.isna(A, i):\n'
        jjr__tqtrk += '            bodo.libs.array_kernels.setna(B, i)\n'
        jjr__tqtrk += '            continue\n'
        jjr__tqtrk += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            jjr__tqtrk += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            jjr__tqtrk += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            jjr__tqtrk += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            jjr__tqtrk += '    return B\n'
        okv__uty = {}
        exec(jjr__tqtrk, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, okv__uty)
        impl = okv__uty['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        qltt__owapv = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(qltt__owapv)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        qltt__owapv = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            qltt__owapv)


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
        azvb__xoqm = S_dt._obj
        ydbp__cjz = bodo.hiframes.pd_series_ext.get_series_data(azvb__xoqm)
        quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(azvb__xoqm)
        psls__huta = bodo.hiframes.pd_series_ext.get_series_name(azvb__xoqm)
        numba.parfors.parfor.init_prange()
        wzt__pbc = len(ydbp__cjz)
        ohgyu__wje = bodo.libs.str_arr_ext.pre_alloc_string_array(wzt__pbc, -1)
        for muap__hqhfc in numba.parfors.parfor.internal_prange(wzt__pbc):
            if bodo.libs.array_kernels.isna(ydbp__cjz, muap__hqhfc):
                bodo.libs.array_kernels.setna(ohgyu__wje, muap__hqhfc)
                continue
            ohgyu__wje[muap__hqhfc] = bodo.utils.conversion.box_if_dt64(
                ydbp__cjz[muap__hqhfc]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(ohgyu__wje,
            quyyk__hkphr, psls__huta)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        azvb__xoqm = S_dt._obj
        rwewt__dpchk = get_series_data(azvb__xoqm).tz_convert(tz)
        quyyk__hkphr = get_series_index(azvb__xoqm)
        psls__huta = get_series_name(azvb__xoqm)
        return init_series(rwewt__dpchk, quyyk__hkphr, psls__huta)
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
        wkrpk__gbaaj = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        qilm__iwur = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', wkrpk__gbaaj,
            qilm__iwur, package_name='pandas', module_name='Series')
        jjr__tqtrk = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        jjr__tqtrk += '    S = S_dt._obj\n'
        jjr__tqtrk += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        jjr__tqtrk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        jjr__tqtrk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        jjr__tqtrk += '    numba.parfors.parfor.init_prange()\n'
        jjr__tqtrk += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            jjr__tqtrk += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            jjr__tqtrk += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        jjr__tqtrk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        jjr__tqtrk += '        if bodo.libs.array_kernels.isna(A, i):\n'
        jjr__tqtrk += '            bodo.libs.array_kernels.setna(B, i)\n'
        jjr__tqtrk += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            nmhqj__dwkry = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            csz__vlkp = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            nmhqj__dwkry = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            csz__vlkp = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        jjr__tqtrk += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            csz__vlkp, nmhqj__dwkry, method)
        jjr__tqtrk += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        okv__uty = {}
        exec(jjr__tqtrk, {'numba': numba, 'np': np, 'bodo': bodo}, okv__uty)
        impl = okv__uty['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    awfy__oal = ['ceil', 'floor', 'round']
    for method in awfy__oal:
        qltt__owapv = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            qltt__owapv)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fxakr__xsq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lkuko__mjck = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fxakr__xsq)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                zysk__cukhu = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yvum__bld = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    zysk__cukhu)
                wzt__pbc = len(lkuko__mjck)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    aoh__gle = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        lkuko__mjck[ipt__kif])
                    trru__gyzg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yvum__bld[ipt__kif]))
                    if aoh__gle == cbp__qdp or trru__gyzg == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(aoh__gle, trru__gyzg)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yvum__bld = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, dt64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    xug__ivvn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yvum__bld[ipt__kif]))
                    if wbh__ojf == cbp__qdp or xug__ivvn == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(wbh__ojf, xug__ivvn)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yvum__bld = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, dt64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    xug__ivvn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yvum__bld[ipt__kif]))
                    if wbh__ojf == cbp__qdp or xug__ivvn == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(wbh__ojf, xug__ivvn)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                fsyr__lab = rhs.value
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if wbh__ojf == cbp__qdp or fsyr__lab == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(wbh__ojf, fsyr__lab)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                fsyr__lab = lhs.value
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if fsyr__lab == cbp__qdp or wbh__ojf == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(fsyr__lab, wbh__ojf)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, dt64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                pvwv__ejaza = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                xug__ivvn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pvwv__ejaza))
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if wbh__ojf == cbp__qdp or xug__ivvn == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(wbh__ojf, xug__ivvn)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, dt64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                pvwv__ejaza = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                xug__ivvn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pvwv__ejaza))
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if wbh__ojf == cbp__qdp or xug__ivvn == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(wbh__ojf, xug__ivvn)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                kvk__lyewl = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kvk__lyewl)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    eev__mpl = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if eev__mpl == cbp__qdp or wbh__ojf == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(eev__mpl, wbh__ojf)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                kvk__lyewl = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                wbh__ojf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kvk__lyewl)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    eev__mpl = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if wbh__ojf == cbp__qdp or eev__mpl == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(wbh__ojf, eev__mpl)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uewo__yls = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                gtert__yjf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uewo__yls))
                pvwv__ejaza = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                xug__ivvn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pvwv__ejaza))
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    xdi__yjsv = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(gtert__yjf[ipt__kif]))
                    if xug__ivvn == cbp__qdp or xdi__yjsv == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(xdi__yjsv, xug__ivvn)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uewo__yls = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                gtert__yjf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wzt__pbc = len(gtert__yjf)
                azvb__xoqm = np.empty(wzt__pbc, timedelta64_dtype)
                cbp__qdp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uewo__yls))
                pvwv__ejaza = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                xug__ivvn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pvwv__ejaza))
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    xdi__yjsv = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(gtert__yjf[ipt__kif]))
                    if xug__ivvn == cbp__qdp or xdi__yjsv == cbp__qdp:
                        jvsc__njfog = cbp__qdp
                    else:
                        jvsc__njfog = op(xug__ivvn, xdi__yjsv)
                    azvb__xoqm[ipt__kif
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        jvsc__njfog)
                return bodo.hiframes.pd_series_ext.init_series(azvb__xoqm,
                    quyyk__hkphr, psls__huta)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            jbe__ozjh = True
        else:
            jbe__ozjh = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uewo__yls = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                gtert__yjf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wzt__pbc = len(gtert__yjf)
                dqsd__gxhgk = bodo.libs.bool_arr_ext.alloc_bool_array(wzt__pbc)
                cbp__qdp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uewo__yls))
                xah__cvwc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                yog__sai = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(xah__cvwc))
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    mcf__stsqx = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(gtert__yjf[ipt__kif]))
                    if mcf__stsqx == cbp__qdp or yog__sai == cbp__qdp:
                        jvsc__njfog = jbe__ozjh
                    else:
                        jvsc__njfog = op(mcf__stsqx, yog__sai)
                    dqsd__gxhgk[ipt__kif] = jvsc__njfog
                return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
                    quyyk__hkphr, psls__huta)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uewo__yls = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                gtert__yjf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wzt__pbc = len(gtert__yjf)
                dqsd__gxhgk = bodo.libs.bool_arr_ext.alloc_bool_array(wzt__pbc)
                cbp__qdp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uewo__yls))
                kubw__sepoi = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                mcf__stsqx = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kubw__sepoi))
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    yog__sai = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(gtert__yjf[ipt__kif]))
                    if mcf__stsqx == cbp__qdp or yog__sai == cbp__qdp:
                        jvsc__njfog = jbe__ozjh
                    else:
                        jvsc__njfog = op(mcf__stsqx, yog__sai)
                    dqsd__gxhgk[ipt__kif] = jvsc__njfog
                return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wzt__pbc = len(gtert__yjf)
                dqsd__gxhgk = bodo.libs.bool_arr_ext.alloc_bool_array(wzt__pbc)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    mcf__stsqx = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(gtert__yjf[ipt__kif]))
                    if mcf__stsqx == cbp__qdp or rhs.value == cbp__qdp:
                        jvsc__njfog = jbe__ozjh
                    else:
                        jvsc__njfog = op(mcf__stsqx, rhs.value)
                    dqsd__gxhgk[ipt__kif] = jvsc__njfog
                return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
                    quyyk__hkphr, psls__huta)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                wzt__pbc = len(gtert__yjf)
                dqsd__gxhgk = bodo.libs.bool_arr_ext.alloc_bool_array(wzt__pbc)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    yog__sai = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        gtert__yjf[ipt__kif])
                    if yog__sai == cbp__qdp or lhs.value == cbp__qdp:
                        jvsc__njfog = jbe__ozjh
                    else:
                        jvsc__njfog = op(lhs.value, yog__sai)
                    dqsd__gxhgk[ipt__kif] = jvsc__njfog
                return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(lhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                wzt__pbc = len(gtert__yjf)
                dqsd__gxhgk = bodo.libs.bool_arr_ext.alloc_bool_array(wzt__pbc)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                wgzn__tyz = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                oicvv__yyjki = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wgzn__tyz)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    mcf__stsqx = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(gtert__yjf[ipt__kif]))
                    if mcf__stsqx == cbp__qdp or oicvv__yyjki == cbp__qdp:
                        jvsc__njfog = jbe__ozjh
                    else:
                        jvsc__njfog = op(mcf__stsqx, oicvv__yyjki)
                    dqsd__gxhgk[ipt__kif] = jvsc__njfog
                return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
                    quyyk__hkphr, psls__huta)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            uewo__yls = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                dmxr__jrn = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gtert__yjf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dmxr__jrn)
                quyyk__hkphr = bodo.hiframes.pd_series_ext.get_series_index(rhs
                    )
                psls__huta = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                wzt__pbc = len(gtert__yjf)
                dqsd__gxhgk = bodo.libs.bool_arr_ext.alloc_bool_array(wzt__pbc)
                cbp__qdp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uewo__yls)
                wgzn__tyz = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                oicvv__yyjki = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wgzn__tyz)
                for ipt__kif in numba.parfors.parfor.internal_prange(wzt__pbc):
                    kvk__lyewl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(gtert__yjf[ipt__kif]))
                    if kvk__lyewl == cbp__qdp or oicvv__yyjki == cbp__qdp:
                        jvsc__njfog = jbe__ozjh
                    else:
                        jvsc__njfog = op(oicvv__yyjki, kvk__lyewl)
                    dqsd__gxhgk[ipt__kif] = jvsc__njfog
                return bodo.hiframes.pd_series_ext.init_series(dqsd__gxhgk,
                    quyyk__hkphr, psls__huta)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for wirs__dts in series_dt_unsupported_attrs:
        rijq__znhjl = 'Series.dt.' + wirs__dts
        overload_attribute(SeriesDatetimePropertiesType, wirs__dts)(
            create_unsupported_overload(rijq__znhjl))
    for udbbt__xxdwx in series_dt_unsupported_methods:
        rijq__znhjl = 'Series.dt.' + udbbt__xxdwx
        overload_method(SeriesDatetimePropertiesType, udbbt__xxdwx,
            no_unliteral=True)(create_unsupported_overload(rijq__znhjl))


_install_series_dt_unsupported()
