import datetime
import operator
import warnings
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_nan, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        if isinstance(val.dtype, pd.core.arrays.integer._IntegerDtype):
            hnec__kppdw = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(hnec__kppdw)
        else:
            dtype = types.int64
        return NumericIndexType(dtype, get_val_type_maybe_str_literal(val.
            name), IntegerArrayType(dtype))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def tzval(self):
        return self.data.tz if isinstance(self.data, bodo.DatetimeArrayType
            ) else None

    def copy(self):
        return DatetimeIndexType(self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.hiframes.
            pd_timestamp_ext.PandasTimestampType(self.tzval))

    @property
    def pandas_type_name(self):
        return self.data.dtype.type_name

    @property
    def numpy_type_name(self):
        return str(self.data.dtype)


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    if isinstance(val.dtype, pd.DatetimeTZDtype):
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name),
            DatetimeArrayType(val.tz))
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    nbmwl__bdcb = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', ddiz__esant, idx_cpy_arg_defaults,
        fn_str=nbmwl__bdcb, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    rtes__loh = c.pyapi.import_module_noblock(cin__phe)
    ejmw__ydxh = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, ejmw__ydxh.data)
    kxjfx__puh = c.pyapi.from_native_value(typ.data, ejmw__ydxh.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ejmw__ydxh.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, ejmw__ydxh.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([kxjfx__puh])
    liqbg__klcx = c.pyapi.object_getattr_string(rtes__loh, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', niufy__ueqcm)])
    sbscl__kjch = c.pyapi.call(liqbg__klcx, args, kws)
    c.pyapi.decref(kxjfx__puh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(rtes__loh)
    c.pyapi.decref(liqbg__klcx)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return sbscl__kjch


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        vuxoy__egx = c.pyapi.object_getattr_string(val, 'array')
    else:
        vuxoy__egx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, vuxoy__egx).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    dtype = _dt_index_data_typ.dtype
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    c.pyapi.decref(vuxoy__egx)
    c.pyapi.decref(niufy__ueqcm)
    return NativeValue(jgnnk__okbv._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jmht__kcsk, wtp__wjv = args
        ejmw__ydxh = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ejmw__ydxh.data = jmht__kcsk
        ejmw__ydxh.name = wtp__wjv
        context.nrt.incref(builder, signature.args[0], jmht__kcsk)
        context.nrt.incref(builder, signature.args[1], wtp__wjv)
        dtype = _dt_index_data_typ.dtype
        ejmw__ydxh.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return ejmw__ydxh._getvalue()
    vskyj__gvkd = DatetimeIndexType(name, data)
    sig = signature(vskyj__gvkd, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    edr__yhl = args[0]
    if equiv_set.has_shape(edr__yhl):
        return ArrayAnalysis.AnalyzeResult(shape=edr__yhl, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    mmqgk__fgz = 'def impl(dti):\n'
    mmqgk__fgz += '    numba.parfors.parfor.init_prange()\n'
    mmqgk__fgz += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    mmqgk__fgz += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    mmqgk__fgz += '    n = len(A)\n'
    mmqgk__fgz += '    S = np.empty(n, np.int64)\n'
    mmqgk__fgz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    mmqgk__fgz += '        val = A[i]\n'
    mmqgk__fgz += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        mmqgk__fgz += '        S[i] = ts.' + field + '()\n'
    else:
        mmqgk__fgz += '        S[i] = ts.' + field + '\n'
    mmqgk__fgz += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    chffe__ept = {}
    exec(mmqgk__fgz, {'numba': numba, 'np': np, 'bodo': bodo}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        kaxma__fhtg = len(A)
        S = np.empty(kaxma__fhtg, np.bool_)
        for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
            val = A[i]
            bhg__eruq = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(bhg__eruq.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        kaxma__fhtg = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            kaxma__fhtg)
        for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
            val = A[i]
            bhg__eruq = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(bhg__eruq.year, bhg__eruq.month, bhg__eruq.day
                )
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        bqi__rtzb = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(bqi__rtzb)):
            if not bodo.libs.array_kernels.isna(bqi__rtzb, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(bqi__rtzb
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        bqi__rtzb = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(bqi__rtzb)):
            if not bodo.libs.array_kernels.isna(bqi__rtzb, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(bqi__rtzb
                    [i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'tz_convert', no_unliteral=True)
def overload_pd_datetime_tz_convert(A, tz):

    def impl(A, tz):
        return init_datetime_index(A._data.tz_convert(tz), A._name)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.DatetimeIndex()')
    xra__fua = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    nalo__udup = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        akdcs__yorkn = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(akdcs__yorkn)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        ikk__aosc = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            bqi__rtzb = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            kaxma__fhtg = len(bqi__rtzb)
            S = np.empty(kaxma__fhtg, ikk__aosc)
            lfkag__ywra = rhs.value
            for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bqi__rtzb[i]) - lfkag__ywra)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        ikk__aosc = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            bqi__rtzb = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            kaxma__fhtg = len(bqi__rtzb)
            S = np.empty(kaxma__fhtg, ikk__aosc)
            lfkag__ywra = lhs.value
            for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    lfkag__ywra - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(bqi__rtzb[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    eua__cuo = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    mmqgk__fgz = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        mmqgk__fgz += '  dt_index, _str = lhs, rhs\n'
        turjl__qsl = 'arr[i] {} other'.format(eua__cuo)
    else:
        mmqgk__fgz += '  dt_index, _str = rhs, lhs\n'
        turjl__qsl = 'other {} arr[i]'.format(eua__cuo)
    mmqgk__fgz += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    mmqgk__fgz += '  l = len(arr)\n'
    mmqgk__fgz += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    mmqgk__fgz += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    mmqgk__fgz += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    mmqgk__fgz += '    S[i] = {}\n'.format(turjl__qsl)
    mmqgk__fgz += '  return S\n'
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo, 'numba': numba, 'np': np}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.Index()')
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    if not is_overload_none(dtype):
        joo__ilh = parse_dtype(dtype, 'pandas.Index')
        nfct__yyhfa = False
    else:
        joo__ilh = getattr(data, 'dtype', None)
        nfct__yyhfa = True
    if isinstance(joo__ilh, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or joo__ilh == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType) or joo__ilh == types.NPTimedelta(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(joo__ilh, (types.Integer, types.Float, types.Boolean)):
            if nfct__yyhfa:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    akdcs__yorkn = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        akdcs__yorkn, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    akdcs__yorkn = bodo.utils.conversion.coerce_to_array(data)
                    dunk__kch = bodo.utils.conversion.fix_arr_dtype(
                        akdcs__yorkn, joo__ilh)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        dunk__kch, name)
        elif joo__ilh in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                ihf__rnl = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = ihf__rnl[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                ihf__rnl = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                rvs__vcf = ihf__rnl[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(rvs__vcf,
                    name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            lbn__eiszj = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(lbn__eiszj[ind])
        return impl

    def impl(I, ind):
        lbn__eiszj = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        rvs__vcf = lbn__eiszj[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(rvs__vcf, name)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            aztvk__rvka = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = aztvk__rvka[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            aztvk__rvka = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            rvs__vcf = aztvk__rvka[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(rvs__vcf,
                name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    jwnf__wzwo = False
    lge__zrg = False
    if closed is None:
        jwnf__wzwo = True
        lge__zrg = True
    elif closed == 'left':
        jwnf__wzwo = True
    elif closed == 'right':
        lge__zrg = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return jwnf__wzwo, lge__zrg


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, inline='always')
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    xra__fua = dict(tz=tz, normalize=normalize, closed=closed)
    nalo__udup = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', xra__fua, nalo__udup,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    uvz__yhjpp = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        uvz__yhjpp = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    mmqgk__fgz = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    mmqgk__fgz += uvz__yhjpp
    if is_overload_none(start):
        mmqgk__fgz += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        mmqgk__fgz += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        mmqgk__fgz += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        mmqgk__fgz += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        mmqgk__fgz += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            mmqgk__fgz += '  b = start_t.value\n'
            mmqgk__fgz += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            mmqgk__fgz += '  b = start_t.value\n'
            mmqgk__fgz += '  addend = np.int64(periods) * np.int64(stride)\n'
            mmqgk__fgz += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            mmqgk__fgz += '  e = end_t.value + stride\n'
            mmqgk__fgz += '  addend = np.int64(periods) * np.int64(-stride)\n'
            mmqgk__fgz += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        mmqgk__fgz += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        mmqgk__fgz += '  delta = end_t.value - start_t.value\n'
        mmqgk__fgz += '  step = delta / (periods - 1)\n'
        mmqgk__fgz += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        mmqgk__fgz += '  arr1 *= step\n'
        mmqgk__fgz += '  arr1 += start_t.value\n'
        mmqgk__fgz += '  arr = arr1.astype(np.int64)\n'
        mmqgk__fgz += '  arr[-1] = end_t.value\n'
    mmqgk__fgz += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    mmqgk__fgz += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np, 'pd': pd}, chffe__ept)
    f = chffe__ept['f']
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        waa__urssm = pd.Timedelta('1 day')
        if start is not None:
            waa__urssm = pd.Timedelta(start)
        yfu__emt = pd.Timedelta('1 day')
        if end is not None:
            yfu__emt = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        jwnf__wzwo, lge__zrg = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            pran__grpf = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = waa__urssm.value
                dzf__gvnbj = b + (yfu__emt.value - b
                    ) // pran__grpf * pran__grpf + pran__grpf // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = waa__urssm.value
                ttmp__fsuty = np.int64(periods) * np.int64(pran__grpf)
                dzf__gvnbj = np.int64(b) + ttmp__fsuty
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                dzf__gvnbj = yfu__emt.value + pran__grpf
                ttmp__fsuty = np.int64(periods) * np.int64(-pran__grpf)
                b = np.int64(dzf__gvnbj) + ttmp__fsuty
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            ugnt__jep = np.arange(b, dzf__gvnbj, pran__grpf, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            tqfi__xshy = yfu__emt.value - waa__urssm.value
            step = tqfi__xshy / (periods - 1)
            uwpp__jqrol = np.arange(0, periods, 1, np.float64)
            uwpp__jqrol *= step
            uwpp__jqrol += waa__urssm.value
            ugnt__jep = uwpp__jqrol.astype(np.int64)
            ugnt__jep[-1] = yfu__emt.value
        if not jwnf__wzwo and len(ugnt__jep) and ugnt__jep[0
            ] == waa__urssm.value:
            ugnt__jep = ugnt__jep[1:]
        if not lge__zrg and len(ugnt__jep) and ugnt__jep[-1] == yfu__emt.value:
            ugnt__jep = ugnt__jep[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(ugnt__jep)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    uqqro__lqaj = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        kaxma__fhtg = len(A)
        bep__udo = bodo.libs.int_arr_ext.alloc_int_array(kaxma__fhtg, np.uint32
            )
        wrpo__ahes = bodo.libs.int_arr_ext.alloc_int_array(kaxma__fhtg, np.
            uint32)
        fqs__yhng = bodo.libs.int_arr_ext.alloc_int_array(kaxma__fhtg, np.
            uint32)
        for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(bep__udo, i)
                bodo.libs.array_kernels.setna(wrpo__ahes, i)
                bodo.libs.array_kernels.setna(fqs__yhng, i)
                continue
            bep__udo[i], wrpo__ahes[i], fqs__yhng[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((bep__udo,
            wrpo__ahes, fqs__yhng), idx, uqqro__lqaj)
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.pd_timedelta_type
            )

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', _timedelta_index_data_typ), ('name', fe_type
            .name_typ), ('dict', types.DictType(_timedelta_index_data_typ.
            dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, cmks__uopd)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    rtes__loh = c.pyapi.import_module_noblock(cin__phe)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    kxjfx__puh = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([kxjfx__puh])
    kws = c.pyapi.dict_pack([('name', niufy__ueqcm)])
    liqbg__klcx = c.pyapi.object_getattr_string(rtes__loh, 'TimedeltaIndex')
    sbscl__kjch = c.pyapi.call(liqbg__klcx, args, kws)
    c.pyapi.decref(kxjfx__puh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(rtes__loh)
    c.pyapi.decref(liqbg__klcx)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return sbscl__kjch


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    lqgi__tamwh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, lqgi__tamwh
        ).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    c.pyapi.decref(lqgi__tamwh)
    c.pyapi.decref(niufy__ueqcm)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    dtype = _timedelta_index_data_typ.dtype
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    return NativeValue(jgnnk__okbv._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jmht__kcsk, wtp__wjv = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = jmht__kcsk
        timedelta_index.name = wtp__wjv
        context.nrt.incref(builder, signature.args[0], jmht__kcsk)
        context.nrt.incref(builder, signature.args[1], wtp__wjv)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    vskyj__gvkd = TimedeltaIndexType(name)
    sig = signature(vskyj__gvkd, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    nbmwl__bdcb = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()'
        )
    check_unsupported_args('TimedeltaIndex.copy', ddiz__esant,
        idx_cpy_arg_defaults, fn_str=nbmwl__bdcb, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        kaxma__fhtg = len(data)
        vuuf__gmr = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            vuuf__gmr = min(vuuf__gmr, val)
        ponl__mcfcg = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            vuuf__gmr)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(ponl__mcfcg, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        kaxma__fhtg = len(data)
        tqc__quud = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            tqc__quud = max(tqc__quud, val)
        ponl__mcfcg = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            tqc__quud)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(ponl__mcfcg, count)
    return impl


def gen_tdi_field_impl(field):
    mmqgk__fgz = 'def impl(tdi):\n'
    mmqgk__fgz += '    numba.parfors.parfor.init_prange()\n'
    mmqgk__fgz += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    mmqgk__fgz += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    mmqgk__fgz += '    n = len(A)\n'
    mmqgk__fgz += '    S = np.empty(n, np.int64)\n'
    mmqgk__fgz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    mmqgk__fgz += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        mmqgk__fgz += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        mmqgk__fgz += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        mmqgk__fgz += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        mmqgk__fgz += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    mmqgk__fgz += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    chffe__ept = {}
    exec(mmqgk__fgz, {'numba': numba, 'np': np, 'bodo': bodo}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    xra__fua = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    nalo__udup = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        akdcs__yorkn = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(akdcs__yorkn)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name='RangeIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    nbmwl__bdcb = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', ddiz__esant,
        idx_cpy_arg_defaults, fn_str=nbmwl__bdcb, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    bqnv__hcjg = c.pyapi.import_module_noblock(cin__phe)
    bkyej__dwtq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    fdzq__jpnw = c.pyapi.from_native_value(types.int64, bkyej__dwtq.start,
        c.env_manager)
    vpbte__mblqo = c.pyapi.from_native_value(types.int64, bkyej__dwtq.stop,
        c.env_manager)
    uqgvd__ediqr = c.pyapi.from_native_value(types.int64, bkyej__dwtq.step,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, bkyej__dwtq.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, bkyej__dwtq.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([fdzq__jpnw, vpbte__mblqo, uqgvd__ediqr])
    kws = c.pyapi.dict_pack([('name', niufy__ueqcm)])
    liqbg__klcx = c.pyapi.object_getattr_string(bqnv__hcjg, 'RangeIndex')
    cuc__jkjwa = c.pyapi.call(liqbg__klcx, args, kws)
    c.pyapi.decref(fdzq__jpnw)
    c.pyapi.decref(vpbte__mblqo)
    c.pyapi.decref(uqgvd__ediqr)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(bqnv__hcjg)
    c.pyapi.decref(liqbg__klcx)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return cuc__jkjwa


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    dtt__lamc = is_overload_constant_int(step) and get_overload_const_int(step
        ) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if dtt__lamc:
            raise_bodo_error('Step must not be zero')
        fyyc__ktdn = cgutils.is_scalar_zero(builder, args[2])
        wtk__rqgub = context.get_python_api(builder)
        with builder.if_then(fyyc__ktdn):
            wtk__rqgub.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        bkyej__dwtq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        bkyej__dwtq.start = args[0]
        bkyej__dwtq.stop = args[1]
        bkyej__dwtq.step = args[2]
        bkyej__dwtq.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return bkyej__dwtq._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, rgsh__tjk = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    fdzq__jpnw = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, fdzq__jpnw).value
    vpbte__mblqo = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, vpbte__mblqo).value
    uqgvd__ediqr = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, uqgvd__ediqr).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    c.pyapi.decref(fdzq__jpnw)
    c.pyapi.decref(vpbte__mblqo)
    c.pyapi.decref(uqgvd__ediqr)
    c.pyapi.decref(niufy__ueqcm)
    bkyej__dwtq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bkyej__dwtq.start = start
    bkyej__dwtq.stop = stop
    bkyej__dwtq.step = step
    bkyej__dwtq.name = name
    return NativeValue(bkyej__dwtq._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        uiir__zqg = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(uiir__zqg.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        uiir__zqg = 'RangeIndex(...) must be called with integers'
        raise BodoError(uiir__zqg)
    zqun__ond = 'start'
    kxjo__kid = 'stop'
    olv__nhp = 'step'
    if is_overload_none(start):
        zqun__ond = '0'
    if is_overload_none(stop):
        kxjo__kid = 'start'
        zqun__ond = '0'
    if is_overload_none(step):
        olv__nhp = '1'
    mmqgk__fgz = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    mmqgk__fgz += '  return init_range_index({}, {}, {}, name)\n'.format(
        zqun__ond, kxjo__kid, olv__nhp)
    chffe__ept = {}
    exec(mmqgk__fgz, {'init_range_index': init_range_index}, chffe__ept)
    tbk__nxh = chffe__ept['_pd_range_index_imp']
    return tbk__nxh


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                tru__ldy = numba.cpython.unicode._normalize_slice(idx, len(I))
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * tru__ldy.start
                stop = I._start + I._step * tru__ldy.stop
                step = I._step * tru__ldy.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', bodo.IntegerArrayType(types.int64)), ('name',
            fe_type.name_typ), ('dict', types.DictType(types.int64, types.
            int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    nbmwl__bdcb = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', ddiz__esant,
        idx_cpy_arg_defaults, fn_str=nbmwl__bdcb, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jmht__kcsk, wtp__wjv, rgsh__tjk = args
        xckb__ffzxe = signature.return_type
        yid__xrhhg = cgutils.create_struct_proxy(xckb__ffzxe)(context, builder)
        yid__xrhhg.data = jmht__kcsk
        yid__xrhhg.name = wtp__wjv
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        yid__xrhhg.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return yid__xrhhg._getvalue()
    jsvp__vhl = get_overload_const_str(freq)
    vskyj__gvkd = PeriodIndexType(jsvp__vhl, name)
    sig = signature(vskyj__gvkd, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    bqnv__hcjg = c.pyapi.import_module_noblock(cin__phe)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        jgnnk__okbv.data)
    vuxoy__egx = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), jgnnk__okbv.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, jgnnk__okbv.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, jgnnk__okbv.name,
        c.env_manager)
    rza__edagm = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', vuxoy__egx), ('name', niufy__ueqcm
        ), ('freq', rza__edagm)])
    liqbg__klcx = c.pyapi.object_getattr_string(bqnv__hcjg, 'PeriodIndex')
    cuc__jkjwa = c.pyapi.call(liqbg__klcx, args, kws)
    c.pyapi.decref(vuxoy__egx)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(rza__edagm)
    c.pyapi.decref(bqnv__hcjg)
    c.pyapi.decref(liqbg__klcx)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return cuc__jkjwa


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    drs__xsx = c.pyapi.object_getattr_string(val, 'asi8')
    vrh__rcoo = c.pyapi.call_method(val, 'isna', ())
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    rtes__loh = c.pyapi.import_module_noblock(cin__phe)
    mha__ejcq = c.pyapi.object_getattr_string(rtes__loh, 'arrays')
    vuxoy__egx = c.pyapi.call_method(mha__ejcq, 'IntegerArray', (drs__xsx,
        vrh__rcoo))
    data = c.pyapi.to_native_value(arr_typ, vuxoy__egx).value
    c.pyapi.decref(drs__xsx)
    c.pyapi.decref(vrh__rcoo)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(rtes__loh)
    c.pyapi.decref(mha__ejcq)
    c.pyapi.decref(vuxoy__egx)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(types.int64, types.int64), types.DictType(types.int64, types
        .int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    return NativeValue(jgnnk__okbv._getvalue())


class CategoricalIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, self.dtype.elem_type)


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        bjn__azpv = get_categories_int_type(fe_type.data.dtype)
        cmks__uopd = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(bjn__azpv, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            cmks__uopd)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    rtes__loh = c.pyapi.import_module_noblock(cin__phe)
    npkip__gshef = numba.core.cgutils.create_struct_proxy(typ)(c.context, c
        .builder, val)
    c.context.nrt.incref(c.builder, typ.data, npkip__gshef.data)
    kxjfx__puh = c.pyapi.from_native_value(typ.data, npkip__gshef.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, npkip__gshef.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, npkip__gshef.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([kxjfx__puh])
    kws = c.pyapi.dict_pack([('name', niufy__ueqcm)])
    liqbg__klcx = c.pyapi.object_getattr_string(rtes__loh, 'CategoricalIndex')
    sbscl__kjch = c.pyapi.call(liqbg__klcx, args, kws)
    c.pyapi.decref(kxjfx__puh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(rtes__loh)
    c.pyapi.decref(liqbg__klcx)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return sbscl__kjch


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    lqgi__tamwh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, lqgi__tamwh).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    c.pyapi.decref(lqgi__tamwh)
    c.pyapi.decref(niufy__ueqcm)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    return NativeValue(jgnnk__okbv._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        jmht__kcsk, wtp__wjv = args
        npkip__gshef = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        npkip__gshef.data = jmht__kcsk
        npkip__gshef.name = wtp__wjv
        context.nrt.incref(builder, signature.args[0], jmht__kcsk)
        context.nrt.incref(builder, signature.args[1], wtp__wjv)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        npkip__gshef.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return npkip__gshef._getvalue()
    vskyj__gvkd = CategoricalIndexType(data, name)
    sig = signature(vskyj__gvkd, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    nbmwl__bdcb = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', ddiz__esant,
        idx_cpy_arg_defaults, fn_str=nbmwl__bdcb, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, cmks__uopd)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    rtes__loh = c.pyapi.import_module_noblock(cin__phe)
    mczbl__whkmm = numba.core.cgutils.create_struct_proxy(typ)(c.context, c
        .builder, val)
    c.context.nrt.incref(c.builder, typ.data, mczbl__whkmm.data)
    kxjfx__puh = c.pyapi.from_native_value(typ.data, mczbl__whkmm.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, mczbl__whkmm.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, mczbl__whkmm.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([kxjfx__puh])
    kws = c.pyapi.dict_pack([('name', niufy__ueqcm)])
    liqbg__klcx = c.pyapi.object_getattr_string(rtes__loh, 'IntervalIndex')
    sbscl__kjch = c.pyapi.call(liqbg__klcx, args, kws)
    c.pyapi.decref(kxjfx__puh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(rtes__loh)
    c.pyapi.decref(liqbg__klcx)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return sbscl__kjch


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    lqgi__tamwh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, lqgi__tamwh).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    c.pyapi.decref(lqgi__tamwh)
    c.pyapi.decref(niufy__ueqcm)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    return NativeValue(jgnnk__okbv._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        jmht__kcsk, wtp__wjv = args
        mczbl__whkmm = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        mczbl__whkmm.data = jmht__kcsk
        mczbl__whkmm.name = wtp__wjv
        context.nrt.incref(builder, signature.args[0], jmht__kcsk)
        context.nrt.incref(builder, signature.args[1], wtp__wjv)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        mczbl__whkmm.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return mczbl__whkmm._getvalue()
    vskyj__gvkd = IntervalIndexType(data, name)
    sig = signature(vskyj__gvkd, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    Int64Index = pd.Int64Index
    UInt64Index = pd.UInt64Index
    Float64Index = pd.Float64Index


@typeof_impl.register(Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    nbmwl__bdcb = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', ddiz__esant, idx_cpy_arg_defaults,
        fn_str=nbmwl__bdcb, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    bqnv__hcjg = c.pyapi.import_module_noblock(cin__phe)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, jgnnk__okbv.data)
    vuxoy__egx = c.pyapi.from_native_value(typ.data, jgnnk__okbv.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, jgnnk__okbv.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, jgnnk__okbv.name,
        c.env_manager)
    ajq__ftdce = c.pyapi.make_none()
    pitn__sbgh = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    cuc__jkjwa = c.pyapi.call_method(bqnv__hcjg, 'Index', (vuxoy__egx,
        ajq__ftdce, pitn__sbgh, niufy__ueqcm))
    c.pyapi.decref(vuxoy__egx)
    c.pyapi.decref(ajq__ftdce)
    c.pyapi.decref(pitn__sbgh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(bqnv__hcjg)
    c.context.nrt.decref(c.builder, typ, val)
    return cuc__jkjwa


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        xckb__ffzxe = signature.return_type
        jgnnk__okbv = cgutils.create_struct_proxy(xckb__ffzxe)(context, builder
            )
        jgnnk__okbv.data = args[0]
        jgnnk__okbv.name = args[1]
        context.nrt.incref(builder, xckb__ffzxe.data, args[0])
        context.nrt.incref(builder, xckb__ffzxe.name_typ, args[1])
        dtype = xckb__ffzxe.dtype
        jgnnk__okbv.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return jgnnk__okbv._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    lqgi__tamwh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, lqgi__tamwh).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    c.pyapi.decref(lqgi__tamwh)
    c.pyapi.decref(niufy__ueqcm)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    dtype = typ.dtype
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    return NativeValue(jgnnk__okbv._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        rabq__unn = dict(dtype=dtype)
        wugr__kni = dict(dtype=None)
        check_unsupported_args(func_str, rabq__unn, wugr__kni, package_name
            ='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                akdcs__yorkn = bodo.utils.conversion.coerce_to_ndarray(data)
                udvqh__dpuk = bodo.utils.conversion.fix_arr_dtype(akdcs__yorkn,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    udvqh__dpuk, name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                akdcs__yorkn = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    akdcs__yorkn = akdcs__yorkn.copy()
                udvqh__dpuk = bodo.utils.conversion.fix_arr_dtype(akdcs__yorkn,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    udvqh__dpuk, name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((Int64Index, 'pandas.Int64Index',
        np.int64), (UInt64Index, 'pandas.UInt64Index', np.uint64), (
        Float64Index, 'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type if data_typ is None else data_typ
        super(StringIndexType, self).__init__(name=
            f'StringIndexType({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ, self.data)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        assert data_typ is None or data_typ == binary_array_type, 'data_typ must be binary_array_type'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    rxutv__jmzom = typ.data
    scalar_type = typ.data.dtype
    lqgi__tamwh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(rxutv__jmzom, lqgi__tamwh).value
    niufy__ueqcm = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, niufy__ueqcm).value
    c.pyapi.decref(lqgi__tamwh)
    c.pyapi.decref(niufy__ueqcm)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jgnnk__okbv.data = data
    jgnnk__okbv.name = name
    gdv__bpta, ufzn__vycn = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(scalar_type, types.int64), types.DictType(scalar_type, types
        .int64)(), [])
    jgnnk__okbv.dict = ufzn__vycn
    return NativeValue(jgnnk__okbv._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    rxutv__jmzom = typ.data
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    bqnv__hcjg = c.pyapi.import_module_noblock(cin__phe)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, rxutv__jmzom, jgnnk__okbv.data)
    vuxoy__egx = c.pyapi.from_native_value(rxutv__jmzom, jgnnk__okbv.data,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, jgnnk__okbv.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, jgnnk__okbv.name,
        c.env_manager)
    ajq__ftdce = c.pyapi.make_none()
    pitn__sbgh = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    cuc__jkjwa = c.pyapi.call_method(bqnv__hcjg, 'Index', (vuxoy__egx,
        ajq__ftdce, pitn__sbgh, niufy__ueqcm))
    c.pyapi.decref(vuxoy__egx)
    c.pyapi.decref(ajq__ftdce)
    c.pyapi.decref(pitn__sbgh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(bqnv__hcjg)
    c.context.nrt.decref(c.builder, typ, val)
    return cuc__jkjwa


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    zwaxh__qufv = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, zwaxh__qufv


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        lfxja__hur = 'bytes_type'
    else:
        lfxja__hur = 'string_type'
    mmqgk__fgz = 'def impl(context, builder, signature, args):\n'
    mmqgk__fgz += '    assert len(args) == 2\n'
    mmqgk__fgz += '    index_typ = signature.return_type\n'
    mmqgk__fgz += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    mmqgk__fgz += '    index_val.data = args[0]\n'
    mmqgk__fgz += '    index_val.name = args[1]\n'
    mmqgk__fgz += '    # increase refcount of stored values\n'
    mmqgk__fgz += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    mmqgk__fgz += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    mmqgk__fgz += '    # create empty dict for get_loc hashmap\n'
    mmqgk__fgz += '    index_val.dict = context.compile_internal(\n'
    mmqgk__fgz += '       builder,\n'
    mmqgk__fgz += (
        f'       lambda: numba.typed.Dict.empty({lfxja__hur}, types.int64),\n')
    mmqgk__fgz += (
        f'        types.DictType({lfxja__hur}, types.int64)(), [],)\n')
    mmqgk__fgz += '    return index_val._getvalue()\n'
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    nbmwl__bdcb = idx_typ_to_format_str_map[typ].format('copy()')
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', ddiz__esant, idx_cpy_arg_defaults,
        fn_str=nbmwl__bdcb, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if is_str_arr_type(arr_typ):
        return StringIndexType(name_typ, arr_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.DatetimeArrayType):
        return DatetimeIndexType(name_typ, arr_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


def _verify_setop_compatible(func_name, I, other):
    if not is_pd_index_type(other) and not isinstance(other, (SeriesType,
        types.Array)):
        raise BodoError(
            f'pd.Index.{func_name}(): unsupported type for argument other: {other}'
            )
    msd__qyjw = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    rubm__ouaoh = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if msd__qyjw != rubm__ouaoh:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {msd__qyjw} and {rubm__ouaoh}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    xra__fua = dict(sort=sort)
    iqtx__efx = dict(sort=None)
    check_unsupported_args('Index.union', xra__fua, iqtx__efx, package_name
        ='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    zooz__qgl = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        ykafl__khs = bodo.utils.conversion.coerce_to_array(I)
        bau__oaml = bodo.utils.conversion.coerce_to_array(other)
        zwpik__rmu = bodo.libs.array_kernels.concat([ykafl__khs, bau__oaml])
        xprgp__feg = bodo.libs.array_kernels.unique(zwpik__rmu)
        return zooz__qgl(xprgp__feg, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    xra__fua = dict(sort=sort)
    iqtx__efx = dict(sort=None)
    check_unsupported_args('Index.intersection', xra__fua, iqtx__efx,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    zooz__qgl = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        ykafl__khs = bodo.utils.conversion.coerce_to_array(I)
        bau__oaml = bodo.utils.conversion.coerce_to_array(other)
        drz__idxp = bodo.libs.array_kernels.unique(ykafl__khs)
        azcj__vgvs = bodo.libs.array_kernels.unique(bau__oaml)
        zwpik__rmu = bodo.libs.array_kernels.concat([drz__idxp, azcj__vgvs])
        vmua__qxaz = pd.Series(zwpik__rmu).sort_values().values
        tpsgv__sbd = bodo.libs.array_kernels.intersection_mask(vmua__qxaz)
        return zooz__qgl(vmua__qxaz[tpsgv__sbd], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    xra__fua = dict(sort=sort)
    iqtx__efx = dict(sort=None)
    check_unsupported_args('Index.difference', xra__fua, iqtx__efx,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    zooz__qgl = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        ykafl__khs = bodo.utils.conversion.coerce_to_array(I)
        bau__oaml = bodo.utils.conversion.coerce_to_array(other)
        drz__idxp = bodo.libs.array_kernels.unique(ykafl__khs)
        azcj__vgvs = bodo.libs.array_kernels.unique(bau__oaml)
        tpsgv__sbd = np.empty(len(drz__idxp), np.bool_)
        bodo.libs.array.array_isin(tpsgv__sbd, drz__idxp, azcj__vgvs, False)
        return zooz__qgl(drz__idxp[~tpsgv__sbd], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    xra__fua = dict(result_name=result_name, sort=sort)
    iqtx__efx = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', xra__fua,
        iqtx__efx, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    zooz__qgl = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        ykafl__khs = bodo.utils.conversion.coerce_to_array(I)
        bau__oaml = bodo.utils.conversion.coerce_to_array(other)
        drz__idxp = bodo.libs.array_kernels.unique(ykafl__khs)
        azcj__vgvs = bodo.libs.array_kernels.unique(bau__oaml)
        fmaxy__iuiaz = np.empty(len(drz__idxp), np.bool_)
        cbvx__gzcol = np.empty(len(azcj__vgvs), np.bool_)
        bodo.libs.array.array_isin(fmaxy__iuiaz, drz__idxp, azcj__vgvs, False)
        bodo.libs.array.array_isin(cbvx__gzcol, azcj__vgvs, drz__idxp, False)
        dlli__hmd = bodo.libs.array_kernels.concat([drz__idxp[~fmaxy__iuiaz
            ], azcj__vgvs[~cbvx__gzcol]])
        return zooz__qgl(dlli__hmd, None)
    return impl


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    xra__fua = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    iqtx__efx = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', xra__fua, iqtx__efx, package_name=
        'pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                ugnt__jep = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(ugnt__jep)):
                    if not bodo.libs.array_kernels.isna(ugnt__jep, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(ugnt__jep.dtype, ugnt__jep[i]))
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                ugnt__jep = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(ugnt__jep)):
                    if not bodo.libs.array_kernels.isna(ugnt__jep, i):
                        val = ugnt__jep[i]
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)
    if isinstance(I, CategoricalIndexType):

        def impl(I, val):
            key = bodo.utils.conversion.unbox_if_timestamp(val)
            if not is_null_value(I._dict):
                _init_engine(I, False)
                ugnt__jep = bodo.utils.conversion.coerce_to_array(I)
                hlegy__usk = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(ugnt__jep.dtype, key))
                return hlegy__usk in I._dict
            else:
                uiir__zqg = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(uiir__zqg)
                ugnt__jep = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(ugnt__jep)):
                    if not bodo.libs.array_kernels.isna(ugnt__jep, i):
                        if ugnt__jep[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            uiir__zqg = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(uiir__zqg)
            ugnt__jep = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(ugnt__jep)):
                if not bodo.libs.array_kernels.isna(ugnt__jep, i):
                    if ugnt__jep[i] == key:
                        ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    xra__fua = dict(method=method, tolerance=tolerance)
    nalo__udup = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.get_loc')
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            uiir__zqg = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(uiir__zqg)
            ugnt__jep = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(ugnt__jep)):
                if ugnt__jep[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        gsbb__iwsdd = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                kaxma__fhtg = len(I)
                jxl__vmu = np.empty(kaxma__fhtg, np.bool_)
                for i in numba.parfors.parfor.internal_prange(kaxma__fhtg):
                    jxl__vmu[i] = not gsbb__iwsdd
                return jxl__vmu
            return impl
        mmqgk__fgz = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if gsbb__iwsdd else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        chffe__ept = {}
        exec(mmqgk__fgz, {'bodo': bodo, 'np': np, 'numba': numba}, chffe__ept)
        impl = chffe__ept['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for jzbsc__ayyk in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(jzbsc__ayyk, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I, 'Index.values'
        )
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload(len, no_unliteral=True)
def overload_multi_index_len(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I)[0])


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(MultiIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)[0]),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_increasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(ugnt__jep, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_decreasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(ugnt__jep, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(NumericIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(StringIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(PeriodIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(CategoricalIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(BinaryIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
def overload_index_duplicated(I, keep='first'):
    if isinstance(I, RangeIndexType):

        def impl(I, keep='first'):
            return np.zeros(len(I), np.bool_)
        return impl

    def impl(I, keep='first'):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        jxl__vmu = bodo.libs.array_kernels.duplicated((ugnt__jep,))
        return jxl__vmu
    return impl


@overload_method(NumericIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'any', no_unliteral=True, inline='always')
def overload_index_any(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) > 0 and (I._start != 0 or len(I) > 1)
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(NumericIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'all', no_unliteral=True, inline='always')
def overload_index_all(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) == 0 or I._step > 0 and (I._start > 0 or I._stop <= 0
                ) or I._step < 0 and (I._start < 0 or I._stop >= 0
                ) or I._start % I._step != 0
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    xra__fua = dict(keep=keep)
    nalo__udup = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    mmqgk__fgz = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        mmqgk__fgz += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        mmqgk__fgz += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    edr__yhl = args[0]
    if isinstance(self.typemap[edr__yhl.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(edr__yhl):
        return ArrayAnalysis.AnalyzeResult(shape=edr__yhl, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    xra__fua = dict(na_action=na_action)
    bmeay__ilex = dict(na_action=None)
    check_unsupported_args('Index.map', xra__fua, bmeay__ilex, package_name
        ='pandas', module_name='Index')
    dtype = I.dtype
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.map')
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    gioxu__zqcjn = numba.core.registry.cpu_target.typing_context
    epaw__ljsox = numba.core.registry.cpu_target.target_context
    try:
        hto__zzz = get_const_func_output_type(mapper, (dtype,), {},
            gioxu__zqcjn, epaw__ljsox)
    except Exception as dzf__gvnbj:
        raise_bodo_error(get_udf_error_msg('Index.map()', dzf__gvnbj))
    ekjcn__mcmj = get_udf_out_arr_type(hto__zzz)
    func = get_overload_const_func(mapper, None)
    mmqgk__fgz = 'def f(I, mapper, na_action=None):\n'
    mmqgk__fgz += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    mmqgk__fgz += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    mmqgk__fgz += '  numba.parfors.parfor.init_prange()\n'
    mmqgk__fgz += '  n = len(A)\n'
    mmqgk__fgz += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    mmqgk__fgz += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    mmqgk__fgz += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    mmqgk__fgz += '    v = map_func(t2)\n'
    mmqgk__fgz += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    mmqgk__fgz += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    wbig__cuivo = bodo.compiler.udf_jit(func)
    chffe__ept = {}
    exec(mmqgk__fgz, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': wbig__cuivo, '_arr_typ': ekjcn__mcmj,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': ekjcn__mcmj.dtype}, chffe__ept)
    f = chffe__ept['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    ivfcp__fmatw, qbhni__wgx = sig.args
    if ivfcp__fmatw != qbhni__wgx:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    ivfcp__fmatw, qbhni__wgx = sig.args
    if ivfcp__fmatw != qbhni__wgx:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            mmqgk__fgz = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(lhs)
"""
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                mmqgk__fgz += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                mmqgk__fgz += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            chffe__ept = {}
            exec(mmqgk__fgz, {'bodo': bodo, 'op': op}, chffe__ept)
            impl = chffe__ept['impl']
            return impl
        if is_index_type(rhs):
            mmqgk__fgz = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(rhs)
"""
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                mmqgk__fgz += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                mmqgk__fgz += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            chffe__ept = {}
            exec(mmqgk__fgz, {'bodo': bodo, 'op': op}, chffe__ept)
            impl = chffe__ept['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    ugnt__jep = bodo.utils.conversion.coerce_to_array(data)
                    nig__yvw = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    jxl__vmu = op(ugnt__jep, nig__yvw)
                    return jxl__vmu
                return impl3
            count = len(lhs.data.types)
            mmqgk__fgz = 'def f(lhs, rhs):\n'
            mmqgk__fgz += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            chffe__ept = {}
            exec(mmqgk__fgz, {'op': op, 'np': np}, chffe__ept)
            impl = chffe__ept['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    ugnt__jep = bodo.utils.conversion.coerce_to_array(data)
                    nig__yvw = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    jxl__vmu = op(nig__yvw, ugnt__jep)
                    return jxl__vmu
                return impl4
            count = len(rhs.data.types)
            mmqgk__fgz = 'def f(lhs, rhs):\n'
            mmqgk__fgz += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            chffe__ept = {}
            exec(mmqgk__fgz, {'op': op, 'np': np}, chffe__ept)
            impl = chffe__ept['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_typ=None):
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_typ})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_typ)

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cmks__uopd = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, cmks__uopd)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    nbmwl__bdcb = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    ddiz__esant = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', ddiz__esant, idx_cpy_arg_defaults,
        fn_str=nbmwl__bdcb, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    cin__phe = c.context.insert_const_string(c.builder.module, 'pandas')
    bqnv__hcjg = c.pyapi.import_module_noblock(cin__phe)
    jgnnk__okbv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, jgnnk__okbv.data)
    vuxoy__egx = c.pyapi.from_native_value(typ.data, jgnnk__okbv.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, jgnnk__okbv.name)
    niufy__ueqcm = c.pyapi.from_native_value(typ.name_typ, jgnnk__okbv.name,
        c.env_manager)
    ajq__ftdce = c.pyapi.make_none()
    pitn__sbgh = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    cuc__jkjwa = c.pyapi.call_method(bqnv__hcjg, 'Index', (vuxoy__egx,
        ajq__ftdce, pitn__sbgh, niufy__ueqcm))
    c.pyapi.decref(vuxoy__egx)
    c.pyapi.decref(ajq__ftdce)
    c.pyapi.decref(pitn__sbgh)
    c.pyapi.decref(niufy__ueqcm)
    c.pyapi.decref(bqnv__hcjg)
    c.context.nrt.decref(c.builder, typ, val)
    return cuc__jkjwa


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        xckb__ffzxe = signature.return_type
        jgnnk__okbv = cgutils.create_struct_proxy(xckb__ffzxe)(context, builder
            )
        jgnnk__okbv.data = args[0]
        jgnnk__okbv.name = args[1]
        context.nrt.incref(builder, xckb__ffzxe.data, args[0])
        context.nrt.incref(builder, xckb__ffzxe.name_typ, args[1])
        return jgnnk__okbv._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'to_series', inline='always')
@overload_method(DatetimeIndexType, 'to_series', inline='always')
@overload_method(TimedeltaIndexType, 'to_series', inline='always')
@overload_method(RangeIndexType, 'to_series', inline='always')
@overload_method(StringIndexType, 'to_series', inline='always')
@overload_method(BinaryIndexType, 'to_series', inline='always')
@overload_method(CategoricalIndexType, 'to_series', inline='always')
def overload_index_to_series(I, index=None, name=None):
    if not (is_overload_constant_str(name) or is_overload_constant_int(name
        ) or is_overload_none(name)):
        raise_bodo_error(
            f'Index.to_series(): only constant string/int are supported for argument name'
            )
    if is_overload_none(name):
        tpt__uhc = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        tpt__uhc = 'name'
    mmqgk__fgz = 'def impl(I, index=None, name=None):\n'
    mmqgk__fgz += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        mmqgk__fgz += '    new_index = I\n'
    elif is_pd_index_type(index):
        mmqgk__fgz += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        mmqgk__fgz += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        mmqgk__fgz += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        mmqgk__fgz += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        mmqgk__fgz += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        mmqgk__fgz += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        mmqgk__fgz += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    mmqgk__fgz += f'    new_name = {tpt__uhc}\n'
    mmqgk__fgz += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(NumericIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'to_frame', inline='always', no_unliteral=True
    )
@overload_method(StringIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(BinaryIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(CategoricalIndexType, 'to_frame', inline='always',
    no_unliteral=True)
def overload_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        fxt__dum = 'I'
    elif is_overload_false(index):
        fxt__dum = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    mmqgk__fgz = 'def impl(I, index=True, name=None):\n'
    mmqgk__fgz += '    data = bodo.utils.conversion.index_to_array(I)\n'
    mmqgk__fgz += f'    new_index = {fxt__dum}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        trjsl__lfq = ColNamesMetaType((0,))
    elif is_overload_none(name):
        trjsl__lfq = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        trjsl__lfq = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        trjsl__lfq = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    mmqgk__fgz += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        trjsl__lfq}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        fxt__dum = 'I'
    elif is_overload_false(index):
        fxt__dum = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    mmqgk__fgz = 'def impl(I, index=True, name=None):\n'
    mmqgk__fgz += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    mmqgk__fgz += f'    new_index = {fxt__dum}\n'
    kpa__sipza = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * kpa__sipza:
        trjsl__lfq = ColNamesMetaType(tuple(range(kpa__sipza)))
    elif is_overload_none(name):
        trjsl__lfq = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if kpa__sipza != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {kpa__sipza} names, not {len(names)}'
                )
        if all(is_overload_constant_str(iagt__iunkk) or
            is_overload_constant_int(iagt__iunkk) for iagt__iunkk in names):
            trjsl__lfq = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    mmqgk__fgz += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    chffe__ept = {}
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        trjsl__lfq}, chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(NumericIndexType, 'to_numpy', inline='always')
@overload_method(DatetimeIndexType, 'to_numpy', inline='always')
@overload_method(TimedeltaIndexType, 'to_numpy', inline='always')
@overload_method(RangeIndexType, 'to_numpy', inline='always')
@overload_method(StringIndexType, 'to_numpy', inline='always')
@overload_method(BinaryIndexType, 'to_numpy', inline='always')
@overload_method(CategoricalIndexType, 'to_numpy', inline='always')
@overload_method(IntervalIndexType, 'to_numpy', inline='always')
def overload_index_to_numpy(I, dtype=None, copy=False, na_value=None):
    xra__fua = dict(dtype=dtype, na_value=na_value)
    nalo__udup = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(copy):
        raise_bodo_error('Index.to_numpy(): copy argument must be a boolean')
    if isinstance(I, RangeIndexType):

        def impl(I, dtype=None, copy=False, na_value=None):
            return np.arange(I._start, I._stop, I._step)
        return impl
    if is_overload_true(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I).copy()
        return impl
    if is_overload_false(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I)
        return impl

    def impl(I, dtype=None, copy=False, na_value=None):
        data = bodo.hiframes.pd_index_ext.get_index_data(I)
        return data.copy() if copy else data
    return impl


@overload_method(NumericIndexType, 'to_list', inline='always')
@overload_method(RangeIndexType, 'to_list', inline='always')
@overload_method(StringIndexType, 'to_list', inline='always')
@overload_method(BinaryIndexType, 'to_list', inline='always')
@overload_method(CategoricalIndexType, 'to_list', inline='always')
@overload_method(DatetimeIndexType, 'to_list', inline='always')
@overload_method(TimedeltaIndexType, 'to_list', inline='always')
@overload_method(NumericIndexType, 'tolist', inline='always')
@overload_method(RangeIndexType, 'tolist', inline='always')
@overload_method(StringIndexType, 'tolist', inline='always')
@overload_method(BinaryIndexType, 'tolist', inline='always')
@overload_method(CategoricalIndexType, 'tolist', inline='always')
@overload_method(DatetimeIndexType, 'tolist', inline='always')
@overload_method(TimedeltaIndexType, 'tolist', inline='always')
def overload_index_to_list(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            gimr__yaf = list()
            for i in range(I._start, I._stop, I.step):
                gimr__yaf.append(i)
            return gimr__yaf
        return impl

    def impl(I):
        gimr__yaf = list()
        for i in range(len(I)):
            gimr__yaf.append(I[i])
        return gimr__yaf
    return impl


@overload_attribute(NumericIndexType, 'T')
@overload_attribute(DatetimeIndexType, 'T')
@overload_attribute(TimedeltaIndexType, 'T')
@overload_attribute(RangeIndexType, 'T')
@overload_attribute(StringIndexType, 'T')
@overload_attribute(BinaryIndexType, 'T')
@overload_attribute(CategoricalIndexType, 'T')
@overload_attribute(PeriodIndexType, 'T')
@overload_attribute(MultiIndexType, 'T')
@overload_attribute(IntervalIndexType, 'T')
def overload_T(I):
    return lambda I: I


@overload_attribute(NumericIndexType, 'size')
@overload_attribute(DatetimeIndexType, 'size')
@overload_attribute(TimedeltaIndexType, 'size')
@overload_attribute(RangeIndexType, 'size')
@overload_attribute(StringIndexType, 'size')
@overload_attribute(BinaryIndexType, 'size')
@overload_attribute(CategoricalIndexType, 'size')
@overload_attribute(PeriodIndexType, 'size')
@overload_attribute(MultiIndexType, 'size')
@overload_attribute(IntervalIndexType, 'size')
def overload_size(I):
    return lambda I: len(I)


@overload_attribute(NumericIndexType, 'ndim')
@overload_attribute(DatetimeIndexType, 'ndim')
@overload_attribute(TimedeltaIndexType, 'ndim')
@overload_attribute(RangeIndexType, 'ndim')
@overload_attribute(StringIndexType, 'ndim')
@overload_attribute(BinaryIndexType, 'ndim')
@overload_attribute(CategoricalIndexType, 'ndim')
@overload_attribute(PeriodIndexType, 'ndim')
@overload_attribute(MultiIndexType, 'ndim')
@overload_attribute(IntervalIndexType, 'ndim')
def overload_ndim(I):
    return lambda I: 1


@overload_attribute(NumericIndexType, 'nlevels')
@overload_attribute(DatetimeIndexType, 'nlevels')
@overload_attribute(TimedeltaIndexType, 'nlevels')
@overload_attribute(RangeIndexType, 'nlevels')
@overload_attribute(StringIndexType, 'nlevels')
@overload_attribute(BinaryIndexType, 'nlevels')
@overload_attribute(CategoricalIndexType, 'nlevels')
@overload_attribute(PeriodIndexType, 'nlevels')
@overload_attribute(MultiIndexType, 'nlevels')
@overload_attribute(IntervalIndexType, 'nlevels')
def overload_nlevels(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(I._data)
    return lambda I: 1


@overload_attribute(NumericIndexType, 'empty')
@overload_attribute(DatetimeIndexType, 'empty')
@overload_attribute(TimedeltaIndexType, 'empty')
@overload_attribute(RangeIndexType, 'empty')
@overload_attribute(StringIndexType, 'empty')
@overload_attribute(BinaryIndexType, 'empty')
@overload_attribute(CategoricalIndexType, 'empty')
@overload_attribute(PeriodIndexType, 'empty')
@overload_attribute(MultiIndexType, 'empty')
@overload_attribute(IntervalIndexType, 'empty')
def overload_empty(I):
    return lambda I: len(I) == 0


@overload_attribute(NumericIndexType, 'is_all_dates')
@overload_attribute(DatetimeIndexType, 'is_all_dates')
@overload_attribute(TimedeltaIndexType, 'is_all_dates')
@overload_attribute(RangeIndexType, 'is_all_dates')
@overload_attribute(StringIndexType, 'is_all_dates')
@overload_attribute(BinaryIndexType, 'is_all_dates')
@overload_attribute(CategoricalIndexType, 'is_all_dates')
@overload_attribute(PeriodIndexType, 'is_all_dates')
@overload_attribute(MultiIndexType, 'is_all_dates')
@overload_attribute(IntervalIndexType, 'is_all_dates')
def overload_is_all_dates(I):
    if isinstance(I, (DatetimeIndexType, TimedeltaIndexType, PeriodIndexType)):
        return lambda I: True
    else:
        return lambda I: False


@overload_attribute(NumericIndexType, 'inferred_type')
@overload_attribute(DatetimeIndexType, 'inferred_type')
@overload_attribute(TimedeltaIndexType, 'inferred_type')
@overload_attribute(RangeIndexType, 'inferred_type')
@overload_attribute(StringIndexType, 'inferred_type')
@overload_attribute(BinaryIndexType, 'inferred_type')
@overload_attribute(CategoricalIndexType, 'inferred_type')
@overload_attribute(PeriodIndexType, 'inferred_type')
@overload_attribute(MultiIndexType, 'inferred_type')
@overload_attribute(IntervalIndexType, 'inferred_type')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Integer):
            return lambda I: 'integer'
        elif isinstance(I.dtype, types.Float):
            return lambda I: 'floating'
        elif isinstance(I.dtype, types.Boolean):
            return lambda I: 'boolean'
        return
    if isinstance(I, StringIndexType):

        def impl(I):
            if len(I._data) == 0:
                return 'empty'
            return 'string'
        return impl
    pqu__inlow = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = pqu__inlow[type(I)]
    return lambda I: inferred_type


@overload_attribute(NumericIndexType, 'dtype')
@overload_attribute(DatetimeIndexType, 'dtype')
@overload_attribute(TimedeltaIndexType, 'dtype')
@overload_attribute(RangeIndexType, 'dtype')
@overload_attribute(StringIndexType, 'dtype')
@overload_attribute(BinaryIndexType, 'dtype')
@overload_attribute(CategoricalIndexType, 'dtype')
@overload_attribute(MultiIndexType, 'dtype')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Boolean):
            return lambda I: np.dtype('O')
        dtype = I.dtype
        return lambda I: dtype
    if isinstance(I, CategoricalIndexType):
        dtype = pd.CategoricalDtype(I.dtype.categories, I.dtype.ordered)
        return lambda I: dtype
    cxg__vbe = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = cxg__vbe[type(I)]
    return lambda I: dtype


@overload_attribute(NumericIndexType, 'names')
@overload_attribute(DatetimeIndexType, 'names')
@overload_attribute(TimedeltaIndexType, 'names')
@overload_attribute(RangeIndexType, 'names')
@overload_attribute(StringIndexType, 'names')
@overload_attribute(BinaryIndexType, 'names')
@overload_attribute(CategoricalIndexType, 'names')
@overload_attribute(IntervalIndexType, 'names')
@overload_attribute(PeriodIndexType, 'names')
@overload_attribute(MultiIndexType, 'names')
def overload_names(I):
    if isinstance(I, MultiIndexType):
        return lambda I: I._names
    return lambda I: (I._name,)


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index_from_index(I, name)


def init_index_from_index(I, name):
    aaqt__gwy = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in aaqt__gwy:
        init_func = aaqt__gwy[type(I)]
        return lambda I, name, inplace=False: init_func(bodo.hiframes.
            pd_index_ext.get_index_data(I).copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(bodo.hiframes.pd_index_ext.get_index_data(I).
            copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise_bodo_error(f'init_index(): Unknown type {type(I)}')


def get_index_constructor(I):
    nxju__zcq = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in nxju__zcq:
        return nxju__zcq[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', xra__fua, nalo__udup, package_name=
        'pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            fcezq__yvd = len(I)
            if fcezq__yvd == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (fcezq__yvd - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(ugnt__jep)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', xra__fua, nalo__udup, package_name=
        'pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            fcezq__yvd = len(I)
            if fcezq__yvd == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (fcezq__yvd - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(ugnt__jep)
    return impl


@overload_method(NumericIndexType, 'argmin', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(PeriodIndexType, 'argmin', no_unliteral=True, inline='always')
def overload_index_argmin(I, axis=0, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmin()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step < 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmin(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(ugnt__jep)))
        return bodo.libs.array_ops.array_op_idxmin(ugnt__jep, index)
    return impl


@overload_method(NumericIndexType, 'argmax', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argmax', no_unliteral=True, inline='always')
def overload_index_argmax(I, axis=0, skipna=True):
    xra__fua = dict(axis=axis, skipna=skipna)
    nalo__udup = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmax()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step > 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmax(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(ugnt__jep))
        return bodo.libs.array_ops.array_op_idxmax(ugnt__jep, index)
    return impl


@overload_method(NumericIndexType, 'unique', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(IntervalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'unique', no_unliteral=True, inline=
    'always')
def overload_index_unique(I):
    zooz__qgl = get_index_constructor(I)

    def impl(I):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        nsie__rgrq = bodo.libs.array_kernels.unique(ugnt__jep)
        return zooz__qgl(nsie__rgrq, name)
    return impl


@overload_method(RangeIndexType, 'unique', no_unliteral=True, inline='always')
def overload_range_index_unique(I):

    def impl(I):
        return I.copy()
    return impl


@overload_method(NumericIndexType, 'nunique', inline='always')
@overload_method(BinaryIndexType, 'nunique', inline='always')
@overload_method(StringIndexType, 'nunique', inline='always')
@overload_method(CategoricalIndexType, 'nunique', inline='always')
@overload_method(DatetimeIndexType, 'nunique', inline='always')
@overload_method(TimedeltaIndexType, 'nunique', inline='always')
@overload_method(PeriodIndexType, 'nunique', inline='always')
def overload_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        kaxma__fhtg = bodo.libs.array_kernels.nunique(ugnt__jep, dropna)
        return kaxma__fhtg
    return impl


@overload_method(RangeIndexType, 'nunique', inline='always')
def overload_range_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        start = I._start
        stop = I._stop
        step = I._step
        return max(0, -(-(stop - start) // step))
    return impl


@overload_method(NumericIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(TimedeltaIndexType, 'isin', no_unliteral=True, inline='always'
    )
def overload_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            pstwo__iycs = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            kaxma__fhtg = len(A)
            jxl__vmu = np.empty(kaxma__fhtg, np.bool_)
            bodo.libs.array.array_isin(jxl__vmu, A, pstwo__iycs, False)
            return jxl__vmu
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        jxl__vmu = bodo.libs.array_ops.array_op_isin(A, values)
        return jxl__vmu
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            pstwo__iycs = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            kaxma__fhtg = len(A)
            jxl__vmu = np.empty(kaxma__fhtg, np.bool_)
            bodo.libs.array.array_isin(jxl__vmu, A, pstwo__iycs, False)
            return jxl__vmu
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        jxl__vmu = bodo.libs.array_ops.array_op_isin(A, values)
        return jxl__vmu
    return impl


@register_jitable
def order_range(I, ascending):
    step = I._step
    if ascending == (step > 0):
        return I.copy()
    else:
        start = I._start
        stop = I._stop
        name = get_index_name(I)
        fcezq__yvd = len(I)
        cxqd__bge = start + step * (fcezq__yvd - 1)
        eexo__anjrd = cxqd__bge - step * fcezq__yvd
        return init_range_index(cxqd__bge, eexo__anjrd, -step, name)


@overload_method(NumericIndexType, 'sort_values', no_unliteral=True, inline
    ='always')
@overload_method(BinaryIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(RangeIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
def overload_index_sort_values(I, return_indexer=False, ascending=True,
    na_position='last', key=None):
    xra__fua = dict(return_indexer=return_indexer, key=key)
    nalo__udup = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Index.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Index.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    if isinstance(I, RangeIndexType):

        def impl(I, return_indexer=False, ascending=True, na_position=
            'last', key=None):
            return order_range(I, ascending)
        return impl
    zooz__qgl = get_index_constructor(I)

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(ugnt__jep), 1, None)
        ldrgp__lrev = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            ugnt__jep,), index, ('$_bodo_col_',))
        ehes__hhj = ldrgp__lrev.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        jxl__vmu = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(ehes__hhj,
            0)
        return zooz__qgl(jxl__vmu, name)
    return impl


@overload_method(NumericIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(BinaryIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(CategoricalIndexType, 'argsort', no_unliteral=True, inline
    ='always')
@overload_method(DatetimeIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(RangeIndexType, 'argsort', no_unliteral=True, inline='always')
def overload_index_argsort(I, axis=0, kind='quicksort', order=None):
    xra__fua = dict(axis=axis, kind=kind, order=order)
    nalo__udup = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        ugnt__jep = bodo.hiframes.pd_index_ext.get_index_data(I)
        jxl__vmu = bodo.hiframes.series_impl.argsort(ugnt__jep)
        return jxl__vmu
    return impl


@overload_method(NumericIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'where', no_unliteral=True, inline='always'
    )
@overload_method(TimedeltaIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'where', no_unliteral=True, inline='always')
def overload_index_where(I, cond, other=np.nan):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.where()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('where',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        gwx__bcore = 'None'
    else:
        gwx__bcore = 'other'
    mmqgk__fgz = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        mmqgk__fgz += '  arr = np.arange(I._start, I._stop, I._step)\n'
        zooz__qgl = 'init_numeric_index'
    else:
        mmqgk__fgz += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    mmqgk__fgz += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    mmqgk__fgz += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {gwx__bcore})\n'
        )
    mmqgk__fgz += f'  return constructor(out_arr, name)\n'
    chffe__ept = {}
    zooz__qgl = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np, 'constructor': zooz__qgl},
        chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(NumericIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(DatetimeIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'putmask', no_unliteral=True, inline
    ='always')
@overload_method(RangeIndexType, 'putmask', no_unliteral=True, inline='always')
def overload_index_putmask(I, cond, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.putmask()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.putmask()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('putmask',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        gwx__bcore = 'None'
    else:
        gwx__bcore = 'other'
    mmqgk__fgz = 'def impl(I, cond, other):\n'
    mmqgk__fgz += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        mmqgk__fgz += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        mmqgk__fgz += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    mmqgk__fgz += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    mmqgk__fgz += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {gwx__bcore})\n'
        )
    mmqgk__fgz += f'  return constructor(out_arr, name)\n'
    chffe__ept = {}
    zooz__qgl = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np, 'constructor': zooz__qgl},
        chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(NumericIndexType, 'repeat', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'repeat', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'repeat', no_unliteral=True, inline='always')
def overload_index_repeat(I, repeats, axis=None):
    xra__fua = dict(axis=axis)
    nalo__udup = dict(axis=None)
    check_unsupported_args('Index.repeat', xra__fua, nalo__udup,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    mmqgk__fgz = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        mmqgk__fgz += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        mmqgk__fgz += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        mmqgk__fgz += (
            '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    mmqgk__fgz += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    mmqgk__fgz += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    mmqgk__fgz += '    return constructor(out_arr, name)'
    chffe__ept = {}
    zooz__qgl = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(mmqgk__fgz, {'bodo': bodo, 'np': np, 'constructor': zooz__qgl},
        chffe__ept)
    impl = chffe__ept['impl']
    return impl


@overload_method(NumericIndexType, 'is_integer', inline='always')
def overload_is_integer_numeric(I):
    truth = isinstance(I.dtype, types.Integer)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_floating', inline='always')
def overload_is_floating_numeric(I):
    truth = isinstance(I.dtype, types.Float)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_boolean', inline='always')
def overload_is_boolean_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_numeric', inline='always')
def overload_is_numeric_numeric(I):
    truth = not isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_object', inline='always')
def overload_is_object_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(StringIndexType, 'is_object', inline='always')
@overload_method(BinaryIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_numeric', inline='always')
@overload_method(RangeIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_object', inline='always')
def overload_is_methods_true(I):
    return lambda I: True


@overload_method(NumericIndexType, 'is_categorical', inline='always')
@overload_method(NumericIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_boolean', inline='always')
@overload_method(StringIndexType, 'is_floating', inline='always')
@overload_method(StringIndexType, 'is_categorical', inline='always')
@overload_method(StringIndexType, 'is_integer', inline='always')
@overload_method(StringIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_numeric', inline='always')
@overload_method(BinaryIndexType, 'is_boolean', inline='always')
@overload_method(BinaryIndexType, 'is_floating', inline='always')
@overload_method(BinaryIndexType, 'is_categorical', inline='always')
@overload_method(BinaryIndexType, 'is_integer', inline='always')
@overload_method(BinaryIndexType, 'is_interval', inline='always')
@overload_method(BinaryIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_boolean', inline='always')
@overload_method(DatetimeIndexType, 'is_floating', inline='always')
@overload_method(DatetimeIndexType, 'is_categorical', inline='always')
@overload_method(DatetimeIndexType, 'is_integer', inline='always')
@overload_method(DatetimeIndexType, 'is_interval', inline='always')
@overload_method(DatetimeIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_object', inline='always')
@overload_method(TimedeltaIndexType, 'is_boolean', inline='always')
@overload_method(TimedeltaIndexType, 'is_floating', inline='always')
@overload_method(TimedeltaIndexType, 'is_categorical', inline='always')
@overload_method(TimedeltaIndexType, 'is_integer', inline='always')
@overload_method(TimedeltaIndexType, 'is_interval', inline='always')
@overload_method(TimedeltaIndexType, 'is_numeric', inline='always')
@overload_method(TimedeltaIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_boolean', inline='always')
@overload_method(RangeIndexType, 'is_floating', inline='always')
@overload_method(RangeIndexType, 'is_categorical', inline='always')
@overload_method(RangeIndexType, 'is_interval', inline='always')
@overload_method(RangeIndexType, 'is_object', inline='always')
@overload_method(IntervalIndexType, 'is_boolean', inline='always')
@overload_method(IntervalIndexType, 'is_floating', inline='always')
@overload_method(IntervalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_integer', inline='always')
@overload_method(IntervalIndexType, 'is_numeric', inline='always')
@overload_method(IntervalIndexType, 'is_object', inline='always')
@overload_method(CategoricalIndexType, 'is_boolean', inline='always')
@overload_method(CategoricalIndexType, 'is_floating', inline='always')
@overload_method(CategoricalIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_interval', inline='always')
@overload_method(CategoricalIndexType, 'is_numeric', inline='always')
@overload_method(CategoricalIndexType, 'is_object', inline='always')
@overload_method(PeriodIndexType, 'is_boolean', inline='always')
@overload_method(PeriodIndexType, 'is_floating', inline='always')
@overload_method(PeriodIndexType, 'is_categorical', inline='always')
@overload_method(PeriodIndexType, 'is_integer', inline='always')
@overload_method(PeriodIndexType, 'is_interval', inline='always')
@overload_method(PeriodIndexType, 'is_numeric', inline='always')
@overload_method(PeriodIndexType, 'is_object', inline='always')
@overload_method(MultiIndexType, 'is_boolean', inline='always')
@overload_method(MultiIndexType, 'is_floating', inline='always')
@overload_method(MultiIndexType, 'is_categorical', inline='always')
@overload_method(MultiIndexType, 'is_integer', inline='always')
@overload_method(MultiIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_numeric', inline='always')
def overload_is_methods_false(I):
    return lambda I: False


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    if isinstance(ty.data, bodo.DatetimeArrayType):
        data = context.get_constant_generic(builder, ty.data, pyval.array)
    else:
        data = context.get_constant_generic(builder, types.Array(types.
            int64, 1, 'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    xkp__wwsrn = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, xkp__wwsrn])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    xkp__wwsrn = context.get_constant_null(types.DictType(types.int64,
        types.int64))
    return lir.Constant.literal_struct([data, name, xkp__wwsrn])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    xkp__wwsrn = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, xkp__wwsrn])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    rxutv__jmzom = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, rxutv__jmzom, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    xkp__wwsrn = context.get_constant_null(types.DictType(scalar_type,
        types.int64))
    return lir.Constant.literal_struct([data, name, xkp__wwsrn])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [nkd__ngzlj] = sig.args
    [index] = args
    kpu__xqeg = context.make_helper(builder, nkd__ngzlj, value=index)
    morg__sboka = context.make_helper(builder, sig.return_type)
    yga__enqwd = cgutils.alloca_once_value(builder, kpu__xqeg.start)
    cydrk__fmsq = context.get_constant(types.intp, 0)
    ujndq__xuf = cgutils.alloca_once_value(builder, cydrk__fmsq)
    morg__sboka.iter = yga__enqwd
    morg__sboka.stop = kpu__xqeg.stop
    morg__sboka.step = kpu__xqeg.step
    morg__sboka.count = ujndq__xuf
    gime__reij = builder.sub(kpu__xqeg.stop, kpu__xqeg.start)
    uysdx__hrtuk = context.get_constant(types.intp, 1)
    btp__gob = builder.icmp_signed('>', gime__reij, cydrk__fmsq)
    dwa__uqn = builder.icmp_signed('>', kpu__xqeg.step, cydrk__fmsq)
    oiii__ctnn = builder.not_(builder.xor(btp__gob, dwa__uqn))
    with builder.if_then(oiii__ctnn):
        mqy__nczuj = builder.srem(gime__reij, kpu__xqeg.step)
        mqy__nczuj = builder.select(btp__gob, mqy__nczuj, builder.neg(
            mqy__nczuj))
        twdit__lshha = builder.icmp_signed('>', mqy__nczuj, cydrk__fmsq)
        obgct__bauio = builder.add(builder.sdiv(gime__reij, kpu__xqeg.step),
            builder.select(twdit__lshha, uysdx__hrtuk, cydrk__fmsq))
        builder.store(obgct__bauio, ujndq__xuf)
    sbscl__kjch = morg__sboka._getvalue()
    cges__lqbwo = impl_ret_new_ref(context, builder, sig.return_type,
        sbscl__kjch)
    return cges__lqbwo


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(numba.np.arrayobj.getiter_array)


_install_index_getiter()
index_unsupported_methods = ['append', 'asof', 'asof_locs', 'astype',
    'delete', 'drop', 'droplevel', 'dropna', 'equals', 'factorize',
    'fillna', 'format', 'get_indexer', 'get_indexer_for',
    'get_indexer_non_unique', 'get_level_values', 'get_slice_bound',
    'get_value', 'groupby', 'holds_integer', 'identical', 'insert', 'is_',
    'is_mixed', 'is_type_compatible', 'item', 'join', 'memory_usage',
    'ravel', 'reindex', 'searchsorted', 'set_names', 'set_value', 'shift',
    'slice_indexer', 'slice_locs', 'sort', 'sortlevel', 'str',
    'to_flat_index', 'to_native_types', 'transpose', 'value_counts', 'view']
index_unsupported_atrs = ['array', 'asi8', 'has_duplicates', 'hasnans',
    'is_unique']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc', 'isin',
    'all', 'any', 'union', 'intersection', 'difference', 'symmetric_difference'
    ]
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing', 'dtype']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map',
    'isin', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_frame', 'to_list', 'tolist',
    'repeat', 'min', 'max']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'nbytes', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map', 'isin',
    'unique', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_list', 'tolist', 'to_numpy',
    'repeat', 'min', 'max']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_localize', 'round', 'floor', 'ceil', 'to_period', 'to_perioddelta',
    'to_pydatetime', 'month_name', 'day_name', 'mean', 'indexer_at_time',
    'indexer_between', 'indexer_between_time', 'all', 'any']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean', 'all', 'any']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing', 'dtype']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp',
    'isin', 'unique', 'all', 'any', 'where', 'putmask', 'sort_values',
    'union', 'intersection', 'difference', 'symmetric_difference',
    'to_series', 'to_frame', 'to_numpy', 'to_list', 'tolist', 'repeat',
    'min', 'max']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_methods = ['min', 'max']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_methods = ['repeat', 'min', 'max']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for mjzx__lus in index_unsupported_methods:
        for ohf__drr, typ in index_types:
            overload_method(typ, mjzx__lus, no_unliteral=True)(
                create_unsupported_overload(ohf__drr.format(mjzx__lus + '()')))
    for igqlm__jtku in index_unsupported_atrs:
        for ohf__drr, typ in index_types:
            overload_attribute(typ, igqlm__jtku, no_unliteral=True)(
                create_unsupported_overload(ohf__drr.format(igqlm__jtku)))
    pnfn__abp = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    cyqgk__jpkuf = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, upf__sjme in cyqgk__jpkuf:
        ohf__drr = idx_typ_to_format_str_map[typ]
        for vdt__advc in upf__sjme:
            overload_method(typ, vdt__advc, no_unliteral=True)(
                create_unsupported_overload(ohf__drr.format(vdt__advc + '()')))
    for typ, gvw__acy in pnfn__abp:
        ohf__drr = idx_typ_to_format_str_map[typ]
        for igqlm__jtku in gvw__acy:
            overload_attribute(typ, igqlm__jtku, no_unliteral=True)(
                create_unsupported_overload(ohf__drr.format(igqlm__jtku)))


_install_index_unsupported()
