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
            xwge__agk = 'Series'
        else:
            xwge__agk = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{xwge__agk}.rolling()')
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
        uezt__mvoui = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, uezt__mvoui)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    krkwn__mktqi = dict(win_type=win_type, axis=axis, closed=closed)
    sep__bfqu = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', krkwn__mktqi, sep__bfqu,
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
    krkwn__mktqi = dict(win_type=win_type, axis=axis, closed=closed)
    sep__bfqu = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', krkwn__mktqi, sep__bfqu,
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
        kzr__qsv, nuvff__jvd, mcwrf__ouu, qicqm__bppl, gya__pdq = args
        obtsj__mghcj = signature.return_type
        psf__qxypd = cgutils.create_struct_proxy(obtsj__mghcj)(context, builder
            )
        psf__qxypd.obj = kzr__qsv
        psf__qxypd.window = nuvff__jvd
        psf__qxypd.min_periods = mcwrf__ouu
        psf__qxypd.center = qicqm__bppl
        context.nrt.incref(builder, signature.args[0], kzr__qsv)
        context.nrt.incref(builder, signature.args[1], nuvff__jvd)
        context.nrt.incref(builder, signature.args[2], mcwrf__ouu)
        context.nrt.incref(builder, signature.args[3], qicqm__bppl)
        return psf__qxypd._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    obtsj__mghcj = RollingType(obj_type, window_type, on, selection, False)
    return obtsj__mghcj(obj_type, window_type, min_periods_type,
        center_type, on_type), codegen


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
    hqq__fonfo = not isinstance(rolling.window_type, types.Integer)
    nscc__zdyf = 'variable' if hqq__fonfo else 'fixed'
    embyu__ktdh = 'None'
    if hqq__fonfo:
        embyu__ktdh = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    dyrx__acy = []
    uyfe__ybs = 'on_arr, ' if hqq__fonfo else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{nscc__zdyf}(bodo.hiframes.pd_series_ext.get_series_data(df), {uyfe__ybs}index_arr, window, minp, center, func, raw)'
            , embyu__ktdh, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    mdbl__gemhm = rolling.obj_type.data
    out_cols = []
    for mbkq__gru in rolling.selection:
        ciry__evp = rolling.obj_type.columns.index(mbkq__gru)
        if mbkq__gru == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            kjbix__vgvm = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ciry__evp})'
                )
            out_cols.append(mbkq__gru)
        else:
            if not isinstance(mdbl__gemhm[ciry__evp].dtype, (types.Boolean,
                types.Number)):
                continue
            kjbix__vgvm = (
                f'bodo.hiframes.rolling.rolling_{nscc__zdyf}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ciry__evp}), {uyfe__ybs}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(mbkq__gru)
        dyrx__acy.append(kjbix__vgvm)
    return ', '.join(dyrx__acy), embyu__ktdh, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    krkwn__mktqi = dict(engine=engine, engine_kwargs=engine_kwargs, args=
        args, kwargs=kwargs)
    sep__bfqu = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', krkwn__mktqi, sep__bfqu,
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
    krkwn__mktqi = dict(win_type=win_type, axis=axis, closed=closed, method
        =method)
    sep__bfqu = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', krkwn__mktqi, sep__bfqu,
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
        ljy__hki = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        eewg__joo = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{nogi__zxehv}'" if
                isinstance(nogi__zxehv, str) else f'{nogi__zxehv}' for
                nogi__zxehv in rolling.selection if nogi__zxehv != rolling.on))
        vaqus__bnl = xlr__bxkts = ''
        if fname == 'apply':
            vaqus__bnl = 'func, raw, args, kwargs'
            xlr__bxkts = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            vaqus__bnl = xlr__bxkts = 'other, pairwise'
        if fname == 'cov':
            vaqus__bnl = xlr__bxkts = 'other, pairwise, ddof'
        hgdq__vkbvq = (
            f'lambda df, window, minp, center, {vaqus__bnl}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {eewg__joo}){selection}.{fname}({xlr__bxkts})'
            )
        ljy__hki += f"""  return rolling.obj.apply({hgdq__vkbvq}, rolling.window, rolling.min_periods, rolling.center, {vaqus__bnl})
"""
        lumx__lzr = {}
        exec(ljy__hki, {'bodo': bodo}, lumx__lzr)
        impl = lumx__lzr['impl']
        return impl
    csdr__wyym = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if csdr__wyym else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if csdr__wyym else rolling.obj_type.columns
        other_cols = None if csdr__wyym else other.columns
        dyrx__acy, embyu__ktdh = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        dyrx__acy, embyu__ktdh, out_cols = _gen_df_rolling_out_data(rolling)
    prtf__xiey = csdr__wyym or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    dmmaw__rczf = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    dmmaw__rczf += '  df = rolling.obj\n'
    dmmaw__rczf += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if csdr__wyym else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    xwge__agk = 'None'
    if csdr__wyym:
        xwge__agk = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif prtf__xiey:
        mbkq__gru = (set(out_cols) - set([rolling.on])).pop()
        xwge__agk = f"'{mbkq__gru}'" if isinstance(mbkq__gru, str) else str(
            mbkq__gru)
    dmmaw__rczf += f'  name = {xwge__agk}\n'
    dmmaw__rczf += '  window = rolling.window\n'
    dmmaw__rczf += '  center = rolling.center\n'
    dmmaw__rczf += '  minp = rolling.min_periods\n'
    dmmaw__rczf += f'  on_arr = {embyu__ktdh}\n'
    if fname == 'apply':
        dmmaw__rczf += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        dmmaw__rczf += f"  func = '{fname}'\n"
        dmmaw__rczf += f'  index_arr = None\n'
        dmmaw__rczf += f'  raw = False\n'
    if prtf__xiey:
        dmmaw__rczf += (
            f'  return bodo.hiframes.pd_series_ext.init_series({dyrx__acy}, index, name)'
            )
        lumx__lzr = {}
        vueh__rxj = {'bodo': bodo}
        exec(dmmaw__rczf, vueh__rxj, lumx__lzr)
        impl = lumx__lzr['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(dmmaw__rczf, out_cols,
        dyrx__acy)


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
        adg__zade = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(adg__zade)


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
    irwnb__mip = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(irwnb__mip) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    hqq__fonfo = not isinstance(window_type, types.Integer)
    embyu__ktdh = 'None'
    if hqq__fonfo:
        embyu__ktdh = 'bodo.utils.conversion.index_to_array(index)'
    uyfe__ybs = 'on_arr, ' if hqq__fonfo else ''
    dyrx__acy = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {uyfe__ybs}window, minp, center)'
            , embyu__ktdh)
    for mbkq__gru in out_cols:
        if mbkq__gru in df_cols and mbkq__gru in other_cols:
            ais__uithu = df_cols.index(mbkq__gru)
            latx__vezm = other_cols.index(mbkq__gru)
            kjbix__vgvm = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ais__uithu}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {latx__vezm}), {uyfe__ybs}window, minp, center)'
                )
        else:
            kjbix__vgvm = 'np.full(len(df), np.nan)'
        dyrx__acy.append(kjbix__vgvm)
    return ', '.join(dyrx__acy), embyu__ktdh


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    vxl__gkxab = {'pairwise': pairwise, 'ddof': ddof}
    ywdz__vzu = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        vxl__gkxab, ywdz__vzu, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    vxl__gkxab = {'ddof': ddof, 'pairwise': pairwise}
    ywdz__vzu = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        vxl__gkxab, ywdz__vzu, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, bvj__xqu = args
        if isinstance(rolling, RollingType):
            irwnb__mip = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(bvj__xqu, (tuple, list)):
                if len(set(bvj__xqu).difference(set(irwnb__mip))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(bvj__xqu).difference(set(irwnb__mip))))
                selection = list(bvj__xqu)
            else:
                if bvj__xqu not in irwnb__mip:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(bvj__xqu))
                selection = [bvj__xqu]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            rxta__amvl = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(rxta__amvl, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        irwnb__mip = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            irwnb__mip = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            irwnb__mip = rolling.obj_type.columns
        if attr in irwnb__mip:
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
    vto__elpw = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    mdbl__gemhm = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in vto__elpw):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        vyfmr__zaj = mdbl__gemhm[vto__elpw.index(get_literal_value(on))]
        if not isinstance(vyfmr__zaj, types.Array
            ) or vyfmr__zaj.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(mxnyw__ntuv.dtype, (types.Boolean, types.Number)) for
        mxnyw__ntuv in mdbl__gemhm):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
