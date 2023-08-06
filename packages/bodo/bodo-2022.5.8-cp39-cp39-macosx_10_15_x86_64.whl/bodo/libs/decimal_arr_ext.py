"""Decimal array corresponding to Arrow Decimal128Array type.
It is similar to Spark's DecimalType. From Spark's docs:
'The DecimalType must have fixed precision (the maximum total number of digits) and
scale (the number of digits on the right of dot). For example, (5, 2) can support the
value from [-999.99 to 999.99].
The precision can be up to 38, the scale must be less or equal to precision.'
'When infer schema from decimal.Decimal objects, it will be DecimalType(38, 18).'
"""
import operator
from decimal import Decimal
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import decimal_ext
ll.add_symbol('box_decimal_array', decimal_ext.box_decimal_array)
ll.add_symbol('unbox_decimal', decimal_ext.unbox_decimal)
ll.add_symbol('unbox_decimal_array', decimal_ext.unbox_decimal_array)
ll.add_symbol('decimal_to_str', decimal_ext.decimal_to_str)
ll.add_symbol('str_to_decimal', decimal_ext.str_to_decimal)
ll.add_symbol('decimal_cmp_eq', decimal_ext.decimal_cmp_eq)
ll.add_symbol('decimal_cmp_ne', decimal_ext.decimal_cmp_ne)
ll.add_symbol('decimal_cmp_gt', decimal_ext.decimal_cmp_gt)
ll.add_symbol('decimal_cmp_ge', decimal_ext.decimal_cmp_ge)
ll.add_symbol('decimal_cmp_lt', decimal_ext.decimal_cmp_lt)
ll.add_symbol('decimal_cmp_le', decimal_ext.decimal_cmp_le)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
int128_type = types.Integer('int128', 128)


class Decimal128Type(types.Type):

    def __init__(self, precision, scale):
        assert isinstance(precision, int)
        assert isinstance(scale, int)
        super(Decimal128Type, self).__init__(name='Decimal128Type({}, {})'.
            format(precision, scale))
        self.precision = precision
        self.scale = scale
        self.bitwidth = 128


@typeof_impl.register(Decimal)
def typeof_decimal_value(val, c):
    return Decimal128Type(38, 18)


register_model(Decimal128Type)(models.IntegerModel)


@intrinsic
def int128_to_decimal128type(typingctx, val, precision_tp, scale_tp=None):
    assert val == int128_type
    assert is_overload_constant_int(precision_tp)
    assert is_overload_constant_int(scale_tp)

    def codegen(context, builder, signature, args):
        return args[0]
    precision = get_overload_const_int(precision_tp)
    scale = get_overload_const_int(scale_tp)
    return Decimal128Type(precision, scale)(int128_type, precision_tp, scale_tp
        ), codegen


@intrinsic
def decimal128type_to_int128(typingctx, val):
    assert isinstance(val, Decimal128Type)

    def codegen(context, builder, signature, args):
        return args[0]
    return int128_type(val), codegen


def decimal_to_str_codegen(context, builder, signature, args, scale):
    val, = args
    scale = context.get_constant(types.int32, scale)
    omot__dnzc = cgutils.create_struct_proxy(types.unicode_type)(context,
        builder)
    syxm__yml = lir.FunctionType(lir.VoidType(), [lir.IntType(128), lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64).as_pointer(),
        lir.IntType(32)])
    lzs__gmcyu = cgutils.get_or_insert_function(builder.module, syxm__yml,
        name='decimal_to_str')
    builder.call(lzs__gmcyu, [val, omot__dnzc._get_ptr_by_name('meminfo'),
        omot__dnzc._get_ptr_by_name('length'), scale])
    omot__dnzc.kind = context.get_constant(types.int32, numba.cpython.
        unicode.PY_UNICODE_1BYTE_KIND)
    omot__dnzc.is_ascii = context.get_constant(types.int32, 1)
    omot__dnzc.hash = context.get_constant(numba.cpython.unicode._Py_hash_t, -1
        )
    omot__dnzc.data = context.nrt.meminfo_data(builder, omot__dnzc.meminfo)
    omot__dnzc.parent = cgutils.get_null_value(omot__dnzc.parent.type)
    return omot__dnzc._getvalue()


@intrinsic
def decimal_to_str(typingctx, val_t=None):
    assert isinstance(val_t, Decimal128Type)

    def codegen(context, builder, signature, args):
        return decimal_to_str_codegen(context, builder, signature, args,
            val_t.scale)
    return bodo.string_type(val_t), codegen


def str_to_decimal_codegen(context, builder, signature, args):
    val, dpx__onzd, dpx__onzd = args
    val = bodo.libs.str_ext.gen_unicode_to_std_str(context, builder, val)
    syxm__yml = lir.FunctionType(lir.IntType(128), [lir.IntType(8).
        as_pointer()])
    lzs__gmcyu = cgutils.get_or_insert_function(builder.module, syxm__yml,
        name='str_to_decimal')
    qjoa__ytr = builder.call(lzs__gmcyu, [val])
    return qjoa__ytr


@intrinsic
def str_to_decimal(typingctx, val, precision_tp, scale_tp=None):
    assert val == bodo.string_type or is_overload_constant_str(val)
    assert is_overload_constant_int(precision_tp)
    assert is_overload_constant_int(scale_tp)

    def codegen(context, builder, signature, args):
        return str_to_decimal_codegen(context, builder, signature, args)
    precision = get_overload_const_int(precision_tp)
    scale = get_overload_const_int(scale_tp)
    return Decimal128Type(precision, scale)(val, precision_tp, scale_tp
        ), codegen


@overload(str, no_unliteral=True)
def overload_str_decimal(val):
    if isinstance(val, Decimal128Type):

        def impl(val):
            return decimal_to_str(val)
        return impl


@intrinsic
def decimal128type_to_int64_tuple(typingctx, val):
    assert isinstance(val, Decimal128Type)

    def codegen(context, builder, signature, args):
        moex__ori = cgutils.alloca_once(builder, lir.ArrayType(lir.IntType(
            64), 2))
        builder.store(args[0], builder.bitcast(moex__ori, lir.IntType(128).
            as_pointer()))
        return builder.load(moex__ori)
    return types.UniTuple(types.int64, 2)(val), codegen


@intrinsic
def decimal128type_cmp(typingctx, val1, scale1, val2, scale2, func_name):
    assert is_overload_constant_str(func_name)
    skean__vscx = get_overload_const_str(func_name)

    def codegen(context, builder, signature, args):
        val1, scale1, val2, scale2, dpx__onzd = args
        syxm__yml = lir.FunctionType(lir.IntType(1), [lir.IntType(128), lir
            .IntType(64), lir.IntType(128), lir.IntType(64)])
        lzs__gmcyu = cgutils.get_or_insert_function(builder.module,
            syxm__yml, name=skean__vscx)
        return builder.call(lzs__gmcyu, (val1, scale1, val2, scale2))
    return types.boolean(val1, scale1, val2, scale2, func_name), codegen


def decimal_create_cmp_op_overload(op):

    def overload_cmp(lhs, rhs):
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            skean__vscx = 'decimal_cmp_' + op.__name__
            scale1 = lhs.scale
            scale2 = rhs.scale

            def impl(lhs, rhs):
                return decimal128type_cmp(lhs, scale1, rhs, scale2, skean__vscx
                    )
            return impl
    return overload_cmp


@lower_constant(Decimal128Type)
def lower_constant_decimal(context, builder, ty, pyval):
    vas__euxbp = numba.njit(lambda v: decimal128type_to_int64_tuple(v))(pyval)
    vifqg__aytwx = [context.get_constant_generic(builder, types.int64, v) for
        v in vas__euxbp]
    uxk__yyn = cgutils.pack_array(builder, vifqg__aytwx)
    moex__ori = cgutils.alloca_once(builder, lir.IntType(128))
    builder.store(uxk__yyn, builder.bitcast(moex__ori, lir.ArrayType(lir.
        IntType(64), 2).as_pointer()))
    return builder.load(moex__ori)


@overload(Decimal, no_unliteral=True)
def decimal_constructor_overload(value='0', context=None):
    if not is_overload_none(context):
        raise BodoError('decimal.Decimal() context argument not supported yet')
    if isinstance(value, (types.Integer,)) or is_overload_constant_str(value
        ) or value == bodo.string_type:

        def impl(value='0', context=None):
            return str_to_decimal(str(value), 38, 18)
        return impl
    else:
        raise BodoError(
            'decimal.Decimal() value type must be an integer or string')


@overload(bool, no_unliteral=True)
def decimal_to_bool(dec):
    if not isinstance(dec, Decimal128Type):
        return

    def impl(dec):
        return bool(decimal128type_to_int128(dec))
    return impl


@unbox(Decimal128Type)
def unbox_decimal(typ, val, c):
    syxm__yml = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(128).as_pointer()])
    lzs__gmcyu = cgutils.get_or_insert_function(c.builder.module, syxm__yml,
        name='unbox_decimal')
    moex__ori = cgutils.alloca_once(c.builder, c.context.get_value_type(
        int128_type))
    c.builder.call(lzs__gmcyu, [val, moex__ori])
    qnoyb__wrrur = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    mhn__bhvsh = c.builder.load(moex__ori)
    return NativeValue(mhn__bhvsh, is_error=qnoyb__wrrur)


@box(Decimal128Type)
def box_decimal(typ, val, c):
    xjs__cuq = decimal_to_str_codegen(c.context, c.builder, bodo.
        string_type(typ), (val,), typ.scale)
    rboa__eejy = c.pyapi.from_native_value(bodo.string_type, xjs__cuq, c.
        env_manager)
    okms__mdfw = c.context.insert_const_string(c.builder.module, 'decimal')
    mcwv__orm = c.pyapi.import_module_noblock(okms__mdfw)
    moex__ori = c.pyapi.call_method(mcwv__orm, 'Decimal', (rboa__eejy,))
    c.pyapi.decref(rboa__eejy)
    c.pyapi.decref(mcwv__orm)
    return moex__ori


@overload_method(Decimal128Type, '__hash__', no_unliteral=True)
def decimal_hash(val):

    def impl(val):
        return hash(decimal_to_str(val))
    return impl


class DecimalArrayType(types.ArrayCompatible):

    def __init__(self, precision, scale):
        self.precision = precision
        self.scale = scale
        super(DecimalArrayType, self).__init__(name=
            'DecimalArrayType({}, {})'.format(precision, scale))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return DecimalArrayType(self.precision, self.scale)

    @property
    def dtype(self):
        return Decimal128Type(self.precision, self.scale)


data_type = types.Array(int128_type, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DecimalArrayType)
class DecimalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        frdjh__mht = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, frdjh__mht)


make_attribute_wrapper(DecimalArrayType, 'data', '_data')
make_attribute_wrapper(DecimalArrayType, 'null_bitmap', '_null_bitmap')


@intrinsic
def init_decimal_array(typingctx, data, null_bitmap, precision_tp, scale_tp
    =None):
    assert data == types.Array(int128_type, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    assert is_overload_constant_int(precision_tp)
    assert is_overload_constant_int(scale_tp)

    def codegen(context, builder, signature, args):
        acyi__muj, sgvxu__iso, dpx__onzd, dpx__onzd = args
        hzgf__grpi = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        hzgf__grpi.data = acyi__muj
        hzgf__grpi.null_bitmap = sgvxu__iso
        context.nrt.incref(builder, signature.args[0], acyi__muj)
        context.nrt.incref(builder, signature.args[1], sgvxu__iso)
        return hzgf__grpi._getvalue()
    precision = get_overload_const_int(precision_tp)
    scale = get_overload_const_int(scale_tp)
    ifspp__njxwa = DecimalArrayType(precision, scale)
    puw__nltkc = ifspp__njxwa(data, null_bitmap, precision_tp, scale_tp)
    return puw__nltkc, codegen


@lower_constant(DecimalArrayType)
def lower_constant_decimal_arr(context, builder, typ, pyval):
    n = len(pyval)
    qwrm__tru = context.get_constant(types.int64, n)
    pcuc__vtwc = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(int128_type, 1, 'C'), [qwrm__tru])
    lcyn__kfhb = np.empty(n + 7 >> 3, np.uint8)

    def f(arr, idx, val):
        arr[idx] = decimal128type_to_int128(val)
    for hftfr__iuhm, eju__rhms in enumerate(pyval):
        slo__ksg = pd.isna(eju__rhms)
        bodo.libs.int_arr_ext.set_bit_to_arr(lcyn__kfhb, hftfr__iuhm, int(
            not slo__ksg))
        if not slo__ksg:
            context.compile_internal(builder, f, types.void(types.Array(
                int128_type, 1, 'C'), types.int64, Decimal128Type(typ.
                precision, typ.scale)), [pcuc__vtwc._getvalue(), context.
                get_constant(types.int64, hftfr__iuhm), context.
                get_constant_generic(builder, Decimal128Type(typ.precision,
                typ.scale), eju__rhms)])
    tbzp__wcr = context.get_constant_generic(builder, nulls_type, lcyn__kfhb)
    hzgf__grpi = context.make_helper(builder, typ)
    hzgf__grpi.data = pcuc__vtwc._getvalue()
    hzgf__grpi.null_bitmap = tbzp__wcr
    return hzgf__grpi._getvalue()


@numba.njit(no_cpython_wrapper=True)
def alloc_decimal_array(n, precision, scale):
    phte__vlpr = np.empty(n, dtype=int128_type)
    ghbzz__rny = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_decimal_array(phte__vlpr, ghbzz__rny, precision, scale)


def alloc_decimal_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_decimal_arr_ext_alloc_decimal_array
    ) = alloc_decimal_array_equiv


@box(DecimalArrayType)
def box_decimal_arr(typ, val, c):
    ifi__wim = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    phte__vlpr = c.context.make_array(types.Array(int128_type, 1, 'C'))(c.
        context, c.builder, ifi__wim.data)
    cif__ejdqu = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ifi__wim.null_bitmap).data
    n = c.builder.extract_value(phte__vlpr.shape, 0)
    scale = c.context.get_constant(types.int32, typ.scale)
    syxm__yml = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(128).as_pointer(), lir.IntType(8).as_pointer(), lir.IntType
        (32)])
    rsaez__syza = cgutils.get_or_insert_function(c.builder.module,
        syxm__yml, name='box_decimal_array')
    vuejd__jdm = c.builder.call(rsaez__syza, [n, phte__vlpr.data,
        cif__ejdqu, scale])
    c.context.nrt.decref(c.builder, typ, val)
    return vuejd__jdm


@unbox(DecimalArrayType)
def unbox_decimal_arr(typ, val, c):
    hzgf__grpi = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cgs__avh = c.pyapi.call_method(val, '__len__', ())
    n = c.pyapi.long_as_longlong(cgs__avh)
    c.pyapi.decref(cgs__avh)
    bfu__ospl = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    pcuc__vtwc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(int128_type, 1, 'C'), [n])
    wsgw__ertk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [bfu__ospl])
    syxm__yml = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64), lir.IntType(128).as_pointer(), lir.IntType(8).
        as_pointer()])
    lzs__gmcyu = cgutils.get_or_insert_function(c.builder.module, syxm__yml,
        name='unbox_decimal_array')
    c.builder.call(lzs__gmcyu, [val, n, pcuc__vtwc.data, wsgw__ertk.data])
    hzgf__grpi.null_bitmap = wsgw__ertk._getvalue()
    hzgf__grpi.data = pcuc__vtwc._getvalue()
    qnoyb__wrrur = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hzgf__grpi._getvalue(), is_error=qnoyb__wrrur)


@overload_method(DecimalArrayType, 'copy', no_unliteral=True)
def overload_decimal_arr_copy(A):
    precision = A.precision
    scale = A.scale
    return lambda A: bodo.libs.decimal_arr_ext.init_decimal_array(A._data.
        copy(), A._null_bitmap.copy(), precision, scale)


@overload(len, no_unliteral=True)
def overload_decimal_arr_len(A):
    if isinstance(A, DecimalArrayType):
        return lambda A: len(A._data)


@overload_attribute(DecimalArrayType, 'shape')
def overload_decimal_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(DecimalArrayType, 'dtype')
def overload_decimal_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(DecimalArrayType, 'ndim')
def overload_decimal_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DecimalArrayType, 'nbytes')
def decimal_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload(operator.setitem, no_unliteral=True)
def decimal_arr_setitem(A, idx, val):
    if not isinstance(A, DecimalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    wmahs__uxebg = (
        f"setitem for DecimalArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if isinstance(val, Decimal128Type):

            def impl_scalar(A, idx, val):
                A._data[idx] = decimal128type_to_int128(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(wmahs__uxebg)
    if not (is_iterable_type(val) and isinstance(val.dtype, bodo.
        Decimal128Type) or isinstance(val, Decimal128Type)):
        raise BodoError(wmahs__uxebg)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):
        if isinstance(val, Decimal128Type):
            return lambda A, idx, val: array_setitem_int_index(A, idx,
                decimal128type_to_int128(val))

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if isinstance(val, Decimal128Type):
            return lambda A, idx, val: array_setitem_bool_index(A, idx,
                decimal128type_to_int128(val))

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):
        if isinstance(val, Decimal128Type):
            return lambda A, idx, val: array_setitem_slice_index(A, idx,
                decimal128type_to_int128(val))

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for DecimalArray with indexing type {idx} not supported.')


@overload(operator.getitem, no_unliteral=True)
def decimal_arr_getitem(A, ind):
    if not isinstance(A, DecimalArrayType):
        return
    if isinstance(ind, types.Integer):
        precision = A.precision
        scale = A.scale
        return lambda A, ind: int128_to_decimal128type(A._data[ind],
            precision, scale)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        precision = A.precision
        scale = A.scale

        def impl(A, ind):
            bwwej__mrwp, gnysw__dsi = array_getitem_bool_index(A, ind)
            return init_decimal_array(bwwej__mrwp, gnysw__dsi, precision, scale
                )
        return impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        precision = A.precision
        scale = A.scale

        def impl(A, ind):
            bwwej__mrwp, gnysw__dsi = array_getitem_int_index(A, ind)
            return init_decimal_array(bwwej__mrwp, gnysw__dsi, precision, scale
                )
        return impl
    if isinstance(ind, types.SliceType):
        precision = A.precision
        scale = A.scale

        def impl_slice(A, ind):
            bwwej__mrwp, gnysw__dsi = array_getitem_slice_index(A, ind)
            return init_decimal_array(bwwej__mrwp, gnysw__dsi, precision, scale
                )
        return impl_slice
    raise BodoError(
        f'getitem for DecimalArray with indexing type {ind} not supported.')
