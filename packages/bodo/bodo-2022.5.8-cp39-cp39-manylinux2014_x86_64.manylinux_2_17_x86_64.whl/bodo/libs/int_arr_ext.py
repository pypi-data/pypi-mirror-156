"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name=
            f'IntegerArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)

    @property
    def get_pandas_scalar_type_instance(self):
        pifnc__pkvw = int(np.log2(self.dtype.bitwidth // 8))
        dtnzy__kci = 0 if self.dtype.signed else 4
        idx = pifnc__pkvw + dtnzy__kci
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hodtt__etnal = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, hodtt__etnal)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    kfvc__yfte = 8 * val.dtype.itemsize
    uci__gtp = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(uci__gtp, kfvc__yfte))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        jaw__nbj = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(jaw__nbj)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    dco__kmfb = c.context.insert_const_string(c.builder.module, 'pandas')
    xxxzq__fqnre = c.pyapi.import_module_noblock(dco__kmfb)
    ola__luf = c.pyapi.call_method(xxxzq__fqnre, str(typ)[:-2], ())
    c.pyapi.decref(xxxzq__fqnre)
    return ola__luf


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    kfvc__yfte = 8 * val.itemsize
    uci__gtp = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(uci__gtp, kfvc__yfte))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    pijbw__yvc = n + 7 >> 3
    blfg__chmt = np.empty(pijbw__yvc, np.uint8)
    for i in range(n):
        jafp__eye = i // 8
        blfg__chmt[jafp__eye] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            blfg__chmt[jafp__eye]) & kBitmask[i % 8]
    return blfg__chmt


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    pbib__pkz = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(pbib__pkz)
    c.pyapi.decref(pbib__pkz)
    gdk__akm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pijbw__yvc = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    rxjpq__wsae = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [pijbw__yvc])
    chqv__zcdmf = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    ejl__fvcs = cgutils.get_or_insert_function(c.builder.module,
        chqv__zcdmf, name='is_pd_int_array')
    ies__jlh = c.builder.call(ejl__fvcs, [obj])
    ynoje__thut = c.builder.icmp_unsigned('!=', ies__jlh, ies__jlh.type(0))
    with c.builder.if_else(ynoje__thut) as (mxnr__jiuxa, ndp__lnpbg):
        with mxnr__jiuxa:
            uaug__qdlq = c.pyapi.object_getattr_string(obj, '_data')
            gdk__akm.data = c.pyapi.to_native_value(types.Array(typ.dtype, 
                1, 'C'), uaug__qdlq).value
            zyy__eyrk = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), zyy__eyrk).value
            c.pyapi.decref(uaug__qdlq)
            c.pyapi.decref(zyy__eyrk)
            suaow__msd = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            chqv__zcdmf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            ejl__fvcs = cgutils.get_or_insert_function(c.builder.module,
                chqv__zcdmf, name='mask_arr_to_bitmap')
            c.builder.call(ejl__fvcs, [rxjpq__wsae.data, suaow__msd.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with ndp__lnpbg:
            gsekw__lwtdc = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            chqv__zcdmf = lir.FunctionType(lir.IntType(32), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            xhsf__vvlqs = cgutils.get_or_insert_function(c.builder.module,
                chqv__zcdmf, name='int_array_from_sequence')
            c.builder.call(xhsf__vvlqs, [obj, c.builder.bitcast(
                gsekw__lwtdc.data, lir.IntType(8).as_pointer()),
                rxjpq__wsae.data])
            gdk__akm.data = gsekw__lwtdc._getvalue()
    gdk__akm.null_bitmap = rxjpq__wsae._getvalue()
    ixb__ibfth = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gdk__akm._getvalue(), is_error=ixb__ibfth)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    gdk__akm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        gdk__akm.data, c.env_manager)
    cehh__iazr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, gdk__akm.null_bitmap).data
    pbib__pkz = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(pbib__pkz)
    dco__kmfb = c.context.insert_const_string(c.builder.module, 'numpy')
    eeztl__swx = c.pyapi.import_module_noblock(dco__kmfb)
    moww__juhke = c.pyapi.object_getattr_string(eeztl__swx, 'bool_')
    mask_arr = c.pyapi.call_method(eeztl__swx, 'empty', (pbib__pkz,
        moww__juhke))
    jrz__zyl = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    zyo__bdo = c.pyapi.object_getattr_string(jrz__zyl, 'data')
    fsh__dto = c.builder.inttoptr(c.pyapi.long_as_longlong(zyo__bdo), lir.
        IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as dznck__zdwz:
        i = dznck__zdwz.index
        twrk__rrayx = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        ztxw__lspkh = c.builder.load(cgutils.gep(c.builder, cehh__iazr,
            twrk__rrayx))
        itetf__bkzhi = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ztxw__lspkh, itetf__bkzhi), lir
            .Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        ocqde__wiqf = cgutils.gep(c.builder, fsh__dto, i)
        c.builder.store(val, ocqde__wiqf)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        gdk__akm.null_bitmap)
    dco__kmfb = c.context.insert_const_string(c.builder.module, 'pandas')
    xxxzq__fqnre = c.pyapi.import_module_noblock(dco__kmfb)
    uni__psz = c.pyapi.object_getattr_string(xxxzq__fqnre, 'arrays')
    ola__luf = c.pyapi.call_method(uni__psz, 'IntegerArray', (data, mask_arr))
    c.pyapi.decref(xxxzq__fqnre)
    c.pyapi.decref(pbib__pkz)
    c.pyapi.decref(eeztl__swx)
    c.pyapi.decref(moww__juhke)
    c.pyapi.decref(jrz__zyl)
    c.pyapi.decref(zyo__bdo)
    c.pyapi.decref(uni__psz)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return ola__luf


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        hhygc__byc, tlifo__gabx = args
        gdk__akm = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        gdk__akm.data = hhygc__byc
        gdk__akm.null_bitmap = tlifo__gabx
        context.nrt.incref(builder, signature.args[0], hhygc__byc)
        context.nrt.incref(builder, signature.args[1], tlifo__gabx)
        return gdk__akm._getvalue()
    bso__wvgku = IntegerArrayType(data.dtype)
    emf__bhxes = bso__wvgku(data, null_bitmap)
    return emf__bhxes, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    mmfl__qiqv = np.empty(n, pyval.dtype.type)
    iaiyf__els = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        hih__ufi = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(iaiyf__els, i, int(not hih__ufi))
        if not hih__ufi:
            mmfl__qiqv[i] = s
    uawbl__fsgj = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), mmfl__qiqv)
    ahsq__ellu = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), iaiyf__els)
    return lir.Constant.literal_struct([uawbl__fsgj, ahsq__ellu])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    tfb__tomc = args[0]
    if equiv_set.has_shape(tfb__tomc):
        return ArrayAnalysis.AnalyzeResult(shape=tfb__tomc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    tfb__tomc = args[0]
    if equiv_set.has_shape(tfb__tomc):
        return ArrayAnalysis.AnalyzeResult(shape=tfb__tomc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    mmfl__qiqv = np.empty(n, dtype)
    zlq__kldsp = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(mmfl__qiqv, zlq__kldsp)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            ktgs__jhv, msz__gzid = array_getitem_bool_index(A, ind)
            return init_integer_array(ktgs__jhv, msz__gzid)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            ktgs__jhv, msz__gzid = array_getitem_int_index(A, ind)
            return init_integer_array(ktgs__jhv, msz__gzid)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            ktgs__jhv, msz__gzid = array_getitem_slice_index(A, ind)
            return init_integer_array(ktgs__jhv, msz__gzid)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    maj__wkdcc = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    jue__ishz = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if jue__ishz:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(maj__wkdcc)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or jue__ishz):
        raise BodoError(maj__wkdcc)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            sakmt__oei = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                sakmt__oei[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    sakmt__oei[i] = np.nan
            return sakmt__oei
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                gljf__nbg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                nblz__ahm = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                gkj__slbn = gljf__nbg & nblz__ahm
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, gkj__slbn)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        pijbw__yvc = n + 7 >> 3
        sakmt__oei = np.empty(pijbw__yvc, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            gljf__nbg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            nblz__ahm = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            gkj__slbn = gljf__nbg & nblz__ahm
            bodo.libs.int_arr_ext.set_bit_to_arr(sakmt__oei, i, gkj__slbn)
        return sakmt__oei
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for qxvzy__sqpl in numba.np.ufunc_db.get_ufuncs():
        gfwe__hdh = create_op_overload(qxvzy__sqpl, qxvzy__sqpl.nin)
        overload(qxvzy__sqpl, no_unliteral=True)(gfwe__hdh)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        gfwe__hdh = create_op_overload(op, 2)
        overload(op)(gfwe__hdh)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        gfwe__hdh = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(gfwe__hdh)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        gfwe__hdh = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(gfwe__hdh)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    ofih__qcx = len(arrs.types)
    psls__vazm = 'def f(arrs):\n'
    ola__luf = ', '.join('arrs[{}]._data'.format(i) for i in range(ofih__qcx))
    psls__vazm += '  return ({}{})\n'.format(ola__luf, ',' if ofih__qcx == 
        1 else '')
    qurgp__dyogt = {}
    exec(psls__vazm, {}, qurgp__dyogt)
    impl = qurgp__dyogt['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    ofih__qcx = len(arrs.types)
    etqp__wpvjz = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        ofih__qcx))
    psls__vazm = 'def f(arrs):\n'
    psls__vazm += '  n = {}\n'.format(etqp__wpvjz)
    psls__vazm += '  n_bytes = (n + 7) >> 3\n'
    psls__vazm += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    psls__vazm += '  curr_bit = 0\n'
    for i in range(ofih__qcx):
        psls__vazm += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        psls__vazm += '  for j in range(len(arrs[{}])):\n'.format(i)
        psls__vazm += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        psls__vazm += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        psls__vazm += '    curr_bit += 1\n'
    psls__vazm += '  return new_mask\n'
    qurgp__dyogt = {}
    exec(psls__vazm, {'np': np, 'bodo': bodo}, qurgp__dyogt)
    impl = qurgp__dyogt['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    xtuzj__yntt = dict(skipna=skipna, min_count=min_count)
    izctu__kdsc = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', xtuzj__yntt, izctu__kdsc)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        itetf__bkzhi = []
        cugyb__vig = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not cugyb__vig:
                    data.append(dtype(1))
                    itetf__bkzhi.append(False)
                    cugyb__vig = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                itetf__bkzhi.append(True)
        ktgs__jhv = np.array(data)
        n = len(ktgs__jhv)
        pijbw__yvc = n + 7 >> 3
        msz__gzid = np.empty(pijbw__yvc, np.uint8)
        for gbb__yvg in range(n):
            set_bit_to_arr(msz__gzid, gbb__yvg, itetf__bkzhi[gbb__yvg])
        return init_integer_array(ktgs__jhv, msz__gzid)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    wdlu__rpkm = numba.core.registry.cpu_target.typing_context
    ymf__vzahj = wdlu__rpkm.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    ymf__vzahj = to_nullable_type(ymf__vzahj)

    def impl(A):
        n = len(A)
        mrn__bzsuk = bodo.utils.utils.alloc_type(n, ymf__vzahj, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(mrn__bzsuk, i)
                continue
            mrn__bzsuk[i] = op(A[i])
        return mrn__bzsuk
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    ofw__ufme = isinstance(lhs, (types.Number, types.Boolean))
    mti__qmbl = isinstance(rhs, (types.Number, types.Boolean))
    qxbfk__dcblh = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    vmarh__mxgl = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    wdlu__rpkm = numba.core.registry.cpu_target.typing_context
    ymf__vzahj = wdlu__rpkm.resolve_function_type(op, (qxbfk__dcblh,
        vmarh__mxgl), {}).return_type
    ymf__vzahj = to_nullable_type(ymf__vzahj)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    paztc__wrbq = 'lhs' if ofw__ufme else 'lhs[i]'
    qvisu__pfw = 'rhs' if mti__qmbl else 'rhs[i]'
    uct__cgynv = ('False' if ofw__ufme else
        'bodo.libs.array_kernels.isna(lhs, i)')
    voyw__hmm = ('False' if mti__qmbl else
        'bodo.libs.array_kernels.isna(rhs, i)')
    psls__vazm = 'def impl(lhs, rhs):\n'
    psls__vazm += '  n = len({})\n'.format('lhs' if not ofw__ufme else 'rhs')
    if inplace:
        psls__vazm += '  out_arr = {}\n'.format('lhs' if not ofw__ufme else
            'rhs')
    else:
        psls__vazm += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    psls__vazm += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    psls__vazm += '    if ({}\n'.format(uct__cgynv)
    psls__vazm += '        or {}):\n'.format(voyw__hmm)
    psls__vazm += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    psls__vazm += '      continue\n'
    psls__vazm += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(paztc__wrbq, qvisu__pfw))
    psls__vazm += '  return out_arr\n'
    qurgp__dyogt = {}
    exec(psls__vazm, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        ymf__vzahj, 'op': op}, qurgp__dyogt)
    impl = qurgp__dyogt['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        ofw__ufme = lhs in [pd_timedelta_type]
        mti__qmbl = rhs in [pd_timedelta_type]
        if ofw__ufme:

            def impl(lhs, rhs):
                n = len(rhs)
                mrn__bzsuk = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(mrn__bzsuk, i)
                        continue
                    mrn__bzsuk[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return mrn__bzsuk
            return impl
        elif mti__qmbl:

            def impl(lhs, rhs):
                n = len(lhs)
                mrn__bzsuk = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(mrn__bzsuk, i)
                        continue
                    mrn__bzsuk[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return mrn__bzsuk
            return impl
    return impl
