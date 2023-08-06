"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        if isinstance(obj_type, bodo.SeriesType):
            msbir__pzdkj = 'Series'
        else:
            msbir__pzdkj = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{msbir__pzdkj}.rolling()')
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hcll__zvs = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, hcll__zvs)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    oxhu__qfb = dict(win_type=win_type, axis=axis, closed=closed)
    wverm__ewnzz = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', oxhu__qfb, wverm__ewnzz,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    oxhu__qfb = dict(win_type=win_type, axis=axis, closed=closed)
    wverm__ewnzz = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', oxhu__qfb, wverm__ewnzz,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        neqn__nqqa, snviq__rya, yqvuj__mmr, rnkf__xwdpo, qtsaf__vdpzn = args
        rqrp__kcxvm = signature.return_type
        atz__zjk = cgutils.create_struct_proxy(rqrp__kcxvm)(context, builder)
        atz__zjk.obj = neqn__nqqa
        atz__zjk.window = snviq__rya
        atz__zjk.min_periods = yqvuj__mmr
        atz__zjk.center = rnkf__xwdpo
        context.nrt.incref(builder, signature.args[0], neqn__nqqa)
        context.nrt.incref(builder, signature.args[1], snviq__rya)
        context.nrt.incref(builder, signature.args[2], yqvuj__mmr)
        context.nrt.incref(builder, signature.args[3], rnkf__xwdpo)
        return atz__zjk._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    rqrp__kcxvm = RollingType(obj_type, window_type, on, selection, False)
    return rqrp__kcxvm(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    dzgg__hbtjq = not isinstance(rolling.window_type, types.Integer)
    kxdss__biqam = 'variable' if dzgg__hbtjq else 'fixed'
    gpasi__pdmrw = 'None'
    if dzgg__hbtjq:
        gpasi__pdmrw = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    ltclk__jvrk = []
    wzajv__okuc = 'on_arr, ' if dzgg__hbtjq else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{kxdss__biqam}(bodo.hiframes.pd_series_ext.get_series_data(df), {wzajv__okuc}index_arr, window, minp, center, func, raw)'
            , gpasi__pdmrw, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    lmte__cthj = rolling.obj_type.data
    out_cols = []
    for zokqa__trgbt in rolling.selection:
        aaw__scq = rolling.obj_type.columns.index(zokqa__trgbt)
        if zokqa__trgbt == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            oodcx__byxb = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {aaw__scq})'
                )
            out_cols.append(zokqa__trgbt)
        else:
            if not isinstance(lmte__cthj[aaw__scq].dtype, (types.Boolean,
                types.Number)):
                continue
            oodcx__byxb = (
                f'bodo.hiframes.rolling.rolling_{kxdss__biqam}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {aaw__scq}), {wzajv__okuc}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(zokqa__trgbt)
        ltclk__jvrk.append(oodcx__byxb)
    return ', '.join(ltclk__jvrk), gpasi__pdmrw, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    oxhu__qfb = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    wverm__ewnzz = dict(engine=None, engine_kwargs=None, args=None, kwargs=None
        )
    check_unsupported_args('Rolling.apply', oxhu__qfb, wverm__ewnzz,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    oxhu__qfb = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    wverm__ewnzz = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', oxhu__qfb, wverm__ewnzz,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        lmj__xnum = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        jtar__varc = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{bnf__txru}'" if
                isinstance(bnf__txru, str) else f'{bnf__txru}' for
                bnf__txru in rolling.selection if bnf__txru != rolling.on))
        urj__yzf = zzj__aesk = ''
        if fname == 'apply':
            urj__yzf = 'func, raw, args, kwargs'
            zzj__aesk = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            urj__yzf = zzj__aesk = 'other, pairwise'
        if fname == 'cov':
            urj__yzf = zzj__aesk = 'other, pairwise, ddof'
        arwh__mvhtz = (
            f'lambda df, window, minp, center, {urj__yzf}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {jtar__varc}){selection}.{fname}({zzj__aesk})'
            )
        lmj__xnum += f"""  return rolling.obj.apply({arwh__mvhtz}, rolling.window, rolling.min_periods, rolling.center, {urj__yzf})
"""
        yqp__zkg = {}
        exec(lmj__xnum, {'bodo': bodo}, yqp__zkg)
        impl = yqp__zkg['impl']
        return impl
    fktl__cslcf = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if fktl__cslcf else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if fktl__cslcf else rolling.obj_type.columns
        other_cols = None if fktl__cslcf else other.columns
        ltclk__jvrk, gpasi__pdmrw = _gen_corr_cov_out_data(out_cols,
            df_cols, other_cols, rolling.window_type, fname)
    else:
        ltclk__jvrk, gpasi__pdmrw, out_cols = _gen_df_rolling_out_data(rolling)
    nnx__bgxrr = fktl__cslcf or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    mzc__cvx = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    mzc__cvx += '  df = rolling.obj\n'
    mzc__cvx += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if fktl__cslcf else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    msbir__pzdkj = 'None'
    if fktl__cslcf:
        msbir__pzdkj = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif nnx__bgxrr:
        zokqa__trgbt = (set(out_cols) - set([rolling.on])).pop()
        msbir__pzdkj = f"'{zokqa__trgbt}'" if isinstance(zokqa__trgbt, str
            ) else str(zokqa__trgbt)
    mzc__cvx += f'  name = {msbir__pzdkj}\n'
    mzc__cvx += '  window = rolling.window\n'
    mzc__cvx += '  center = rolling.center\n'
    mzc__cvx += '  minp = rolling.min_periods\n'
    mzc__cvx += f'  on_arr = {gpasi__pdmrw}\n'
    if fname == 'apply':
        mzc__cvx += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        mzc__cvx += f"  func = '{fname}'\n"
        mzc__cvx += f'  index_arr = None\n'
        mzc__cvx += f'  raw = False\n'
    if nnx__bgxrr:
        mzc__cvx += (
            f'  return bodo.hiframes.pd_series_ext.init_series({ltclk__jvrk}, index, name)'
            )
        yqp__zkg = {}
        kskp__vfj = {'bodo': bodo}
        exec(mzc__cvx, kskp__vfj, yqp__zkg)
        impl = yqp__zkg['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(mzc__cvx, out_cols,
        ltclk__jvrk)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        sraw__phrd = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(sraw__phrd)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    dmz__aljdm = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(dmz__aljdm) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    dzgg__hbtjq = not isinstance(window_type, types.Integer)
    gpasi__pdmrw = 'None'
    if dzgg__hbtjq:
        gpasi__pdmrw = 'bodo.utils.conversion.index_to_array(index)'
    wzajv__okuc = 'on_arr, ' if dzgg__hbtjq else ''
    ltclk__jvrk = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {wzajv__okuc}window, minp, center)'
            , gpasi__pdmrw)
    for zokqa__trgbt in out_cols:
        if zokqa__trgbt in df_cols and zokqa__trgbt in other_cols:
            rki__asea = df_cols.index(zokqa__trgbt)
            mayj__jtc = other_cols.index(zokqa__trgbt)
            oodcx__byxb = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rki__asea}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {mayj__jtc}), {wzajv__okuc}window, minp, center)'
                )
        else:
            oodcx__byxb = 'np.full(len(df), np.nan)'
        ltclk__jvrk.append(oodcx__byxb)
    return ', '.join(ltclk__jvrk), gpasi__pdmrw


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    yuw__oazzc = {'pairwise': pairwise, 'ddof': ddof}
    kwh__vzd = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        yuw__oazzc, kwh__vzd, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    yuw__oazzc = {'ddof': ddof, 'pairwise': pairwise}
    kwh__vzd = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        yuw__oazzc, kwh__vzd, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, omdfe__xtf = args
        if isinstance(rolling, RollingType):
            dmz__aljdm = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(omdfe__xtf, (tuple, list)):
                if len(set(omdfe__xtf).difference(set(dmz__aljdm))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(omdfe__xtf).difference(set(dmz__aljdm))))
                selection = list(omdfe__xtf)
            else:
                if omdfe__xtf not in dmz__aljdm:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(omdfe__xtf))
                selection = [omdfe__xtf]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            bis__uyw = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(bis__uyw, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        dmz__aljdm = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            dmz__aljdm = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            dmz__aljdm = rolling.obj_type.columns
        if attr in dmz__aljdm:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    ial__omb = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    lmte__cthj = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in ial__omb):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        yhb__ctah = lmte__cthj[ial__omb.index(get_literal_value(on))]
        if not isinstance(yhb__ctah, types.Array
            ) or yhb__ctah.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(rwtb__gcug.dtype, (types.Boolean, types.Number)) for
        rwtb__gcug in lmte__cthj):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
