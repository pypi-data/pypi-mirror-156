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
        phzs__xyb = int(np.log2(self.dtype.bitwidth // 8))
        ofokc__rgktr = 0 if self.dtype.signed else 4
        idx = phzs__xyb + ofokc__rgktr
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rguk__enrcy = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, rguk__enrcy)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    gaahy__yfzzs = 8 * val.dtype.itemsize
    cyrd__nfkm = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(cyrd__nfkm, gaahy__yfzzs))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        tde__omj = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(tde__omj)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    duoz__onox = c.context.insert_const_string(c.builder.module, 'pandas')
    byyzv__hge = c.pyapi.import_module_noblock(duoz__onox)
    phf__lnk = c.pyapi.call_method(byyzv__hge, str(typ)[:-2], ())
    c.pyapi.decref(byyzv__hge)
    return phf__lnk


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    gaahy__yfzzs = 8 * val.itemsize
    cyrd__nfkm = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(cyrd__nfkm, gaahy__yfzzs))
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
    mniq__akb = n + 7 >> 3
    bjabp__pxj = np.empty(mniq__akb, np.uint8)
    for i in range(n):
        xkfp__bty = i // 8
        bjabp__pxj[xkfp__bty] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            bjabp__pxj[xkfp__bty]) & kBitmask[i % 8]
    return bjabp__pxj


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    fvmi__hnjxc = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(fvmi__hnjxc)
    c.pyapi.decref(fvmi__hnjxc)
    mbi__rni = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mniq__akb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    zcys__wtv = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [mniq__akb])
    myalq__vakko = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    kwpx__ienjp = cgutils.get_or_insert_function(c.builder.module,
        myalq__vakko, name='is_pd_int_array')
    qap__prxp = c.builder.call(kwpx__ienjp, [obj])
    elxy__dsh = c.builder.icmp_unsigned('!=', qap__prxp, qap__prxp.type(0))
    with c.builder.if_else(elxy__dsh) as (hhn__uhkjg, fdoss__pjhi):
        with hhn__uhkjg:
            cgs__vopu = c.pyapi.object_getattr_string(obj, '_data')
            mbi__rni.data = c.pyapi.to_native_value(types.Array(typ.dtype, 
                1, 'C'), cgs__vopu).value
            ovzu__dlurz = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), ovzu__dlurz).value
            c.pyapi.decref(cgs__vopu)
            c.pyapi.decref(ovzu__dlurz)
            rlb__jah = c.context.make_array(types.Array(types.bool_, 1, 'C'))(c
                .context, c.builder, mask_arr)
            myalq__vakko = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            kwpx__ienjp = cgutils.get_or_insert_function(c.builder.module,
                myalq__vakko, name='mask_arr_to_bitmap')
            c.builder.call(kwpx__ienjp, [zcys__wtv.data, rlb__jah.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with fdoss__pjhi:
            ycyv__nxzx = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            myalq__vakko = lir.FunctionType(lir.IntType(32), [lir.IntType(8
                ).as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8)
                .as_pointer()])
            jrxk__cuqr = cgutils.get_or_insert_function(c.builder.module,
                myalq__vakko, name='int_array_from_sequence')
            c.builder.call(jrxk__cuqr, [obj, c.builder.bitcast(ycyv__nxzx.
                data, lir.IntType(8).as_pointer()), zcys__wtv.data])
            mbi__rni.data = ycyv__nxzx._getvalue()
    mbi__rni.null_bitmap = zcys__wtv._getvalue()
    xcbms__oshm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mbi__rni._getvalue(), is_error=xcbms__oshm)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    mbi__rni = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        mbi__rni.data, c.env_manager)
    yupz__lmiul = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, mbi__rni.null_bitmap).data
    fvmi__hnjxc = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(fvmi__hnjxc)
    duoz__onox = c.context.insert_const_string(c.builder.module, 'numpy')
    dww__ekm = c.pyapi.import_module_noblock(duoz__onox)
    dtv__btwco = c.pyapi.object_getattr_string(dww__ekm, 'bool_')
    mask_arr = c.pyapi.call_method(dww__ekm, 'empty', (fvmi__hnjxc, dtv__btwco)
        )
    giny__uiam = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    kta__qspu = c.pyapi.object_getattr_string(giny__uiam, 'data')
    syouc__wxo = c.builder.inttoptr(c.pyapi.long_as_longlong(kta__qspu),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as ypbp__olyo:
        i = ypbp__olyo.index
        lomn__rzg = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        nqfo__njy = c.builder.load(cgutils.gep(c.builder, yupz__lmiul,
            lomn__rzg))
        red__qttsu = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(nqfo__njy, red__qttsu), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        qljys__ppkwl = cgutils.gep(c.builder, syouc__wxo, i)
        c.builder.store(val, qljys__ppkwl)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        mbi__rni.null_bitmap)
    duoz__onox = c.context.insert_const_string(c.builder.module, 'pandas')
    byyzv__hge = c.pyapi.import_module_noblock(duoz__onox)
    kly__mze = c.pyapi.object_getattr_string(byyzv__hge, 'arrays')
    phf__lnk = c.pyapi.call_method(kly__mze, 'IntegerArray', (data, mask_arr))
    c.pyapi.decref(byyzv__hge)
    c.pyapi.decref(fvmi__hnjxc)
    c.pyapi.decref(dww__ekm)
    c.pyapi.decref(dtv__btwco)
    c.pyapi.decref(giny__uiam)
    c.pyapi.decref(kta__qspu)
    c.pyapi.decref(kly__mze)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return phf__lnk


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        ddjdd__fto, uyzbq__djgat = args
        mbi__rni = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        mbi__rni.data = ddjdd__fto
        mbi__rni.null_bitmap = uyzbq__djgat
        context.nrt.incref(builder, signature.args[0], ddjdd__fto)
        context.nrt.incref(builder, signature.args[1], uyzbq__djgat)
        return mbi__rni._getvalue()
    kkgq__vslhs = IntegerArrayType(data.dtype)
    ipqr__pga = kkgq__vslhs(data, null_bitmap)
    return ipqr__pga, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    hyirl__cqtn = np.empty(n, pyval.dtype.type)
    urbr__kywo = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        ofias__kgb = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(urbr__kywo, i, int(not ofias__kgb)
            )
        if not ofias__kgb:
            hyirl__cqtn[i] = s
    kenjj__caz = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), hyirl__cqtn)
    zus__zvfa = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), urbr__kywo)
    return lir.Constant.literal_struct([kenjj__caz, zus__zvfa])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    iuy__nmku = args[0]
    if equiv_set.has_shape(iuy__nmku):
        return ArrayAnalysis.AnalyzeResult(shape=iuy__nmku, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    iuy__nmku = args[0]
    if equiv_set.has_shape(iuy__nmku):
        return ArrayAnalysis.AnalyzeResult(shape=iuy__nmku, pre=[])
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
    hyirl__cqtn = np.empty(n, dtype)
    nhfl__cns = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(hyirl__cqtn, nhfl__cns)


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
            ooj__rcbl, xaecn__vxbr = array_getitem_bool_index(A, ind)
            return init_integer_array(ooj__rcbl, xaecn__vxbr)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            ooj__rcbl, xaecn__vxbr = array_getitem_int_index(A, ind)
            return init_integer_array(ooj__rcbl, xaecn__vxbr)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            ooj__rcbl, xaecn__vxbr = array_getitem_slice_index(A, ind)
            return init_integer_array(ooj__rcbl, xaecn__vxbr)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    saw__sikr = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    efbj__osc = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if efbj__osc:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(saw__sikr)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or efbj__osc):
        raise BodoError(saw__sikr)
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
            pkctp__nry = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                pkctp__nry[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    pkctp__nry[i] = np.nan
            return pkctp__nry
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
                ikoz__peq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                afbr__fiqz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                vmzmd__tij = ikoz__peq & afbr__fiqz
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, vmzmd__tij)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        mniq__akb = n + 7 >> 3
        pkctp__nry = np.empty(mniq__akb, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            ikoz__peq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            afbr__fiqz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            vmzmd__tij = ikoz__peq & afbr__fiqz
            bodo.libs.int_arr_ext.set_bit_to_arr(pkctp__nry, i, vmzmd__tij)
        return pkctp__nry
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
    for thtf__pfi in numba.np.ufunc_db.get_ufuncs():
        wzegr__gevoy = create_op_overload(thtf__pfi, thtf__pfi.nin)
        overload(thtf__pfi, no_unliteral=True)(wzegr__gevoy)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        wzegr__gevoy = create_op_overload(op, 2)
        overload(op)(wzegr__gevoy)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        wzegr__gevoy = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(wzegr__gevoy)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        wzegr__gevoy = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(wzegr__gevoy)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    pmyw__cxde = len(arrs.types)
    moih__adl = 'def f(arrs):\n'
    phf__lnk = ', '.join('arrs[{}]._data'.format(i) for i in range(pmyw__cxde))
    moih__adl += '  return ({}{})\n'.format(phf__lnk, ',' if pmyw__cxde == 
        1 else '')
    tztex__gcxzc = {}
    exec(moih__adl, {}, tztex__gcxzc)
    impl = tztex__gcxzc['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    pmyw__cxde = len(arrs.types)
    nmdin__nren = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        pmyw__cxde))
    moih__adl = 'def f(arrs):\n'
    moih__adl += '  n = {}\n'.format(nmdin__nren)
    moih__adl += '  n_bytes = (n + 7) >> 3\n'
    moih__adl += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    moih__adl += '  curr_bit = 0\n'
    for i in range(pmyw__cxde):
        moih__adl += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        moih__adl += '  for j in range(len(arrs[{}])):\n'.format(i)
        moih__adl += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        moih__adl += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        moih__adl += '    curr_bit += 1\n'
    moih__adl += '  return new_mask\n'
    tztex__gcxzc = {}
    exec(moih__adl, {'np': np, 'bodo': bodo}, tztex__gcxzc)
    impl = tztex__gcxzc['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    wzb__qnyny = dict(skipna=skipna, min_count=min_count)
    twtxf__iqhyz = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', wzb__qnyny, twtxf__iqhyz)

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
        red__qttsu = []
        urq__iqd = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not urq__iqd:
                    data.append(dtype(1))
                    red__qttsu.append(False)
                    urq__iqd = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                red__qttsu.append(True)
        ooj__rcbl = np.array(data)
        n = len(ooj__rcbl)
        mniq__akb = n + 7 >> 3
        xaecn__vxbr = np.empty(mniq__akb, np.uint8)
        for uax__pomv in range(n):
            set_bit_to_arr(xaecn__vxbr, uax__pomv, red__qttsu[uax__pomv])
        return init_integer_array(ooj__rcbl, xaecn__vxbr)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    fjwt__biu = numba.core.registry.cpu_target.typing_context
    bvf__mju = fjwt__biu.resolve_function_type(op, (types.Array(A.dtype, 1,
        'C'),), {}).return_type
    bvf__mju = to_nullable_type(bvf__mju)

    def impl(A):
        n = len(A)
        wxf__wksa = bodo.utils.utils.alloc_type(n, bvf__mju, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(wxf__wksa, i)
                continue
            wxf__wksa[i] = op(A[i])
        return wxf__wksa
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    qbm__gtgl = isinstance(lhs, (types.Number, types.Boolean))
    zee__nnvc = isinstance(rhs, (types.Number, types.Boolean))
    cae__rettq = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    mjsy__enxpw = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    fjwt__biu = numba.core.registry.cpu_target.typing_context
    bvf__mju = fjwt__biu.resolve_function_type(op, (cae__rettq, mjsy__enxpw
        ), {}).return_type
    bvf__mju = to_nullable_type(bvf__mju)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    hum__kdo = 'lhs' if qbm__gtgl else 'lhs[i]'
    fmc__cpuj = 'rhs' if zee__nnvc else 'rhs[i]'
    udvvq__fyd = ('False' if qbm__gtgl else
        'bodo.libs.array_kernels.isna(lhs, i)')
    cnxcy__mlu = ('False' if zee__nnvc else
        'bodo.libs.array_kernels.isna(rhs, i)')
    moih__adl = 'def impl(lhs, rhs):\n'
    moih__adl += '  n = len({})\n'.format('lhs' if not qbm__gtgl else 'rhs')
    if inplace:
        moih__adl += '  out_arr = {}\n'.format('lhs' if not qbm__gtgl else
            'rhs')
    else:
        moih__adl += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    moih__adl += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    moih__adl += '    if ({}\n'.format(udvvq__fyd)
    moih__adl += '        or {}):\n'.format(cnxcy__mlu)
    moih__adl += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    moih__adl += '      continue\n'
    moih__adl += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(hum__kdo, fmc__cpuj))
    moih__adl += '  return out_arr\n'
    tztex__gcxzc = {}
    exec(moih__adl, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        bvf__mju, 'op': op}, tztex__gcxzc)
    impl = tztex__gcxzc['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        qbm__gtgl = lhs in [pd_timedelta_type]
        zee__nnvc = rhs in [pd_timedelta_type]
        if qbm__gtgl:

            def impl(lhs, rhs):
                n = len(rhs)
                wxf__wksa = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(wxf__wksa, i)
                        continue
                    wxf__wksa[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return wxf__wksa
            return impl
        elif zee__nnvc:

            def impl(lhs, rhs):
                n = len(lhs)
                wxf__wksa = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(wxf__wksa, i)
                        continue
                    wxf__wksa[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return wxf__wksa
            return impl
    return impl
