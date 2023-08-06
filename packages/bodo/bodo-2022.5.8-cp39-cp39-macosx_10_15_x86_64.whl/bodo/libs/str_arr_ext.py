"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoArrayIterator, BodoError, decode_if_dict_array, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        jwpth__uvq = ArrayItemArrayType(char_arr_type)
        swq__dtf = [('data', jwpth__uvq)]
        models.StructModel.__init__(self, dmm, fe_type, swq__dtf)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        hyyy__dspv, = args
        bah__vqva = context.make_helper(builder, string_array_type)
        bah__vqva.data = hyyy__dspv
        context.nrt.incref(builder, data_typ, hyyy__dspv)
        return bah__vqva._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    skz__wqxy = c.context.insert_const_string(c.builder.module, 'pandas')
    wygjm__tcdhq = c.pyapi.import_module_noblock(skz__wqxy)
    thxgl__sqjbk = c.pyapi.call_method(wygjm__tcdhq, 'StringDtype', ())
    c.pyapi.decref(wygjm__tcdhq)
    return thxgl__sqjbk


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        obfv__cizu = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs
            )
        if obfv__cizu is not None:
            return obfv__cizu
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                zfeu__qsaq = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(zfeu__qsaq)
                for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                zfeu__qsaq = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(zfeu__qsaq)
                for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                zfeu__qsaq = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(zfeu__qsaq)
                for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise_bodo_error(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    yzh__hdpwb = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    fqu__gei = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and fqu__gei or yzh__hdpwb and is_str_arr_type(rhs
        ):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j
                    ) or bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs[j]
            return out_arr
        return impl_both
    if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs + rhs[j]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if is_str_arr_type(lhs) and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and is_str_arr_type(rhs):

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    yzt__iydud = context.make_helper(builder, arr_typ, arr_value)
    jwpth__uvq = ArrayItemArrayType(char_arr_type)
    ibrf__lrkb = _get_array_item_arr_payload(context, builder, jwpth__uvq,
        yzt__iydud.data)
    return ibrf__lrkb


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return ibrf__lrkb.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        wuhu__hrw = context.make_helper(builder, offset_arr_type,
            ibrf__lrkb.offsets).data
        return _get_num_total_chars(builder, wuhu__hrw, ibrf__lrkb.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xfkv__yxref = context.make_helper(builder, offset_arr_type,
            ibrf__lrkb.offsets)
        dhqrr__towbe = context.make_helper(builder, offset_ctypes_type)
        dhqrr__towbe.data = builder.bitcast(xfkv__yxref.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        dhqrr__towbe.meminfo = xfkv__yxref.meminfo
        thxgl__sqjbk = dhqrr__towbe._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            thxgl__sqjbk)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        hyyy__dspv = context.make_helper(builder, char_arr_type, ibrf__lrkb
            .data)
        dhqrr__towbe = context.make_helper(builder, data_ctypes_type)
        dhqrr__towbe.data = hyyy__dspv.data
        dhqrr__towbe.meminfo = hyyy__dspv.meminfo
        thxgl__sqjbk = dhqrr__towbe._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            thxgl__sqjbk)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        ymf__rengr, ind = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            ymf__rengr, sig.args[0])
        hyyy__dspv = context.make_helper(builder, char_arr_type, ibrf__lrkb
            .data)
        dhqrr__towbe = context.make_helper(builder, data_ctypes_type)
        dhqrr__towbe.data = builder.gep(hyyy__dspv.data, [ind])
        dhqrr__towbe.meminfo = hyyy__dspv.meminfo
        thxgl__sqjbk = dhqrr__towbe._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            thxgl__sqjbk)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        iyb__jbru, hva__mavrt, tus__ijpry, rbgk__nfbfh = args
        lirr__htq = builder.bitcast(builder.gep(iyb__jbru, [hva__mavrt]),
            lir.IntType(8).as_pointer())
        abbut__yzcef = builder.bitcast(builder.gep(tus__ijpry, [rbgk__nfbfh
            ]), lir.IntType(8).as_pointer())
        pflww__nykhu = builder.load(abbut__yzcef)
        builder.store(pflww__nykhu, lirr__htq)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        yxw__zmxz = context.make_helper(builder, null_bitmap_arr_type,
            ibrf__lrkb.null_bitmap)
        dhqrr__towbe = context.make_helper(builder, data_ctypes_type)
        dhqrr__towbe.data = yxw__zmxz.data
        dhqrr__towbe.meminfo = yxw__zmxz.meminfo
        thxgl__sqjbk = dhqrr__towbe._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            thxgl__sqjbk)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        wuhu__hrw = context.make_helper(builder, offset_arr_type,
            ibrf__lrkb.offsets).data
        return builder.load(builder.gep(wuhu__hrw, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ibrf__lrkb.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        pspe__cfl, ind = args
        if in_bitmap_typ == data_ctypes_type:
            dhqrr__towbe = context.make_helper(builder, data_ctypes_type,
                pspe__cfl)
            pspe__cfl = dhqrr__towbe.data
        return builder.load(builder.gep(pspe__cfl, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        pspe__cfl, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            dhqrr__towbe = context.make_helper(builder, data_ctypes_type,
                pspe__cfl)
            pspe__cfl = dhqrr__towbe.data
        builder.store(val, builder.gep(pspe__cfl, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        nysd__rvzzo = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        iuqi__nbew = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        bwih__vmjko = context.make_helper(builder, offset_arr_type,
            nysd__rvzzo.offsets).data
        unx__yhfqm = context.make_helper(builder, offset_arr_type,
            iuqi__nbew.offsets).data
        lwatd__svde = context.make_helper(builder, char_arr_type,
            nysd__rvzzo.data).data
        azbe__vius = context.make_helper(builder, char_arr_type, iuqi__nbew
            .data).data
        sgir__pbv = context.make_helper(builder, null_bitmap_arr_type,
            nysd__rvzzo.null_bitmap).data
        fmn__zdvh = context.make_helper(builder, null_bitmap_arr_type,
            iuqi__nbew.null_bitmap).data
        slo__dmryg = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, unx__yhfqm, bwih__vmjko, slo__dmryg)
        cgutils.memcpy(builder, azbe__vius, lwatd__svde, builder.load(
            builder.gep(bwih__vmjko, [ind])))
        fgg__aasc = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        gkg__ngv = builder.lshr(fgg__aasc, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, fmn__zdvh, sgir__pbv, gkg__ngv)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        nysd__rvzzo = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        iuqi__nbew = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        bwih__vmjko = context.make_helper(builder, offset_arr_type,
            nysd__rvzzo.offsets).data
        lwatd__svde = context.make_helper(builder, char_arr_type,
            nysd__rvzzo.data).data
        azbe__vius = context.make_helper(builder, char_arr_type, iuqi__nbew
            .data).data
        num_total_chars = _get_num_total_chars(builder, bwih__vmjko,
            nysd__rvzzo.n_arrays)
        cgutils.memcpy(builder, azbe__vius, lwatd__svde, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        nysd__rvzzo = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        iuqi__nbew = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        bwih__vmjko = context.make_helper(builder, offset_arr_type,
            nysd__rvzzo.offsets).data
        unx__yhfqm = context.make_helper(builder, offset_arr_type,
            iuqi__nbew.offsets).data
        sgir__pbv = context.make_helper(builder, null_bitmap_arr_type,
            nysd__rvzzo.null_bitmap).data
        zfeu__qsaq = nysd__rvzzo.n_arrays
        jjhro__brdjr = context.get_constant(offset_type, 0)
        lagp__jzqra = cgutils.alloca_once_value(builder, jjhro__brdjr)
        with cgutils.for_range(builder, zfeu__qsaq) as qxirc__oliel:
            kkwj__jfqpx = lower_is_na(context, builder, sgir__pbv,
                qxirc__oliel.index)
            with cgutils.if_likely(builder, builder.not_(kkwj__jfqpx)):
                nlos__ucdc = builder.load(builder.gep(bwih__vmjko, [
                    qxirc__oliel.index]))
                qwa__ocu = builder.load(lagp__jzqra)
                builder.store(nlos__ucdc, builder.gep(unx__yhfqm, [qwa__ocu]))
                builder.store(builder.add(qwa__ocu, lir.Constant(context.
                    get_value_type(offset_type), 1)), lagp__jzqra)
        qwa__ocu = builder.load(lagp__jzqra)
        nlos__ucdc = builder.load(builder.gep(bwih__vmjko, [zfeu__qsaq]))
        builder.store(nlos__ucdc, builder.gep(unx__yhfqm, [qwa__ocu]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        iwk__cgyk, ind, str, net__jhiww = args
        iwk__cgyk = context.make_array(sig.args[0])(context, builder, iwk__cgyk
            )
        dyd__flzyw = builder.gep(iwk__cgyk.data, [ind])
        cgutils.raw_memcpy(builder, dyd__flzyw, str, net__jhiww, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        dyd__flzyw, ind, xhyoa__yxgd, net__jhiww = args
        dyd__flzyw = builder.gep(dyd__flzyw, [ind])
        cgutils.raw_memcpy(builder, dyd__flzyw, xhyoa__yxgd, net__jhiww, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            wpd__zrl = A._data
            return np.int64(getitem_str_offset(wpd__zrl, idx + 1) -
                getitem_str_offset(wpd__zrl, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    pas__pdllf = np.int64(getitem_str_offset(A, i))
    hzpuv__pidu = np.int64(getitem_str_offset(A, i + 1))
    l = hzpuv__pidu - pas__pdllf
    qrv__qxk = get_data_ptr_ind(A, pas__pdllf)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(qrv__qxk, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    apm__dat = getitem_str_offset(A, i)
    jdck__tis = getitem_str_offset(A, i + 1)
    vya__opt = jdck__tis - apm__dat
    nwb__bxpf = getitem_str_offset(B, j)
    gtz__dfw = nwb__bxpf + vya__opt
    setitem_str_offset(B, j + 1, gtz__dfw)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if vya__opt != 0:
        hyyy__dspv = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(hyyy__dspv, np.
            int64(nwb__bxpf), np.int64(gtz__dfw))
        aijn__medaq = get_data_ptr(B).data
        ujczl__jyw = get_data_ptr(A).data
        memcpy_region(aijn__medaq, nwb__bxpf, ujczl__jyw, apm__dat, vya__opt, 1
            )


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    zfeu__qsaq = len(str_arr)
    rid__borml = np.empty(zfeu__qsaq, np.bool_)
    for i in range(zfeu__qsaq):
        rid__borml[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return rid__borml


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            zfeu__qsaq = len(data)
            l = []
            for i in range(zfeu__qsaq):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        wnpbj__bkmbp = data.count
        zdkdb__pykhh = ['to_list_if_immutable_arr(data[{}])'.format(i) for
            i in range(wnpbj__bkmbp)]
        if is_overload_true(str_null_bools):
            zdkdb__pykhh += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(wnpbj__bkmbp) if is_str_arr_type(data.types[i]) or 
                data.types[i] == binary_array_type]
        prry__ftct = 'def f(data, str_null_bools=None):\n'
        prry__ftct += '  return ({}{})\n'.format(', '.join(zdkdb__pykhh), 
            ',' if wnpbj__bkmbp == 1 else '')
        grex__iofls = {}
        exec(prry__ftct, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, grex__iofls)
        isike__omgjl = grex__iofls['f']
        return isike__omgjl
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                zfeu__qsaq = len(list_data)
                for i in range(zfeu__qsaq):
                    xhyoa__yxgd = list_data[i]
                    str_arr[i] = xhyoa__yxgd
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                zfeu__qsaq = len(list_data)
                for i in range(zfeu__qsaq):
                    xhyoa__yxgd = list_data[i]
                    str_arr[i] = xhyoa__yxgd
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        wnpbj__bkmbp = str_arr.count
        npjpj__pfw = 0
        prry__ftct = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(wnpbj__bkmbp):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                prry__ftct += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, wnpbj__bkmbp + npjpj__pfw))
                npjpj__pfw += 1
            else:
                prry__ftct += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        prry__ftct += '  return\n'
        grex__iofls = {}
        exec(prry__ftct, {'cp_str_list_to_array': cp_str_list_to_array},
            grex__iofls)
        jcim__mcus = grex__iofls['f']
        return jcim__mcus
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            zfeu__qsaq = len(str_list)
            str_arr = pre_alloc_string_array(zfeu__qsaq, -1)
            for i in range(zfeu__qsaq):
                xhyoa__yxgd = str_list[i]
                str_arr[i] = xhyoa__yxgd
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            zfeu__qsaq = len(A)
            yrwzh__lkvqm = 0
            for i in range(zfeu__qsaq):
                xhyoa__yxgd = A[i]
                yrwzh__lkvqm += get_utf8_size(xhyoa__yxgd)
            return yrwzh__lkvqm
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        zfeu__qsaq = len(arr)
        n_chars = num_total_chars(arr)
        qhmj__arrf = pre_alloc_string_array(zfeu__qsaq, np.int64(n_chars))
        copy_str_arr_slice(qhmj__arrf, arr, zfeu__qsaq)
        return qhmj__arrf
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    prry__ftct = 'def f(in_seq):\n'
    prry__ftct += '    n_strs = len(in_seq)\n'
    prry__ftct += '    A = pre_alloc_string_array(n_strs, -1)\n'
    prry__ftct += '    return A\n'
    grex__iofls = {}
    exec(prry__ftct, {'pre_alloc_string_array': pre_alloc_string_array},
        grex__iofls)
    mzc__glcxj = grex__iofls['f']
    return mzc__glcxj


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        atjmn__suh = 'pre_alloc_binary_array'
    else:
        atjmn__suh = 'pre_alloc_string_array'
    prry__ftct = 'def f(in_seq):\n'
    prry__ftct += '    n_strs = len(in_seq)\n'
    prry__ftct += f'    A = {atjmn__suh}(n_strs, -1)\n'
    prry__ftct += '    for i in range(n_strs):\n'
    prry__ftct += '        A[i] = in_seq[i]\n'
    prry__ftct += '    return A\n'
    grex__iofls = {}
    exec(prry__ftct, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, grex__iofls)
    mzc__glcxj = grex__iofls['f']
    return mzc__glcxj


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ytl__ohvqd = builder.add(ibrf__lrkb.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        zbasd__qjqwh = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        gkg__ngv = builder.mul(ytl__ohvqd, zbasd__qjqwh)
        mwfsb__xaml = context.make_array(offset_arr_type)(context, builder,
            ibrf__lrkb.offsets).data
        cgutils.memset(builder, mwfsb__xaml, gkg__ngv, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        emohe__cynf = ibrf__lrkb.n_arrays
        gkg__ngv = builder.lshr(builder.add(emohe__cynf, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        hmyxl__hmm = context.make_array(null_bitmap_arr_type)(context,
            builder, ibrf__lrkb.null_bitmap).data
        cgutils.memset(builder, hmyxl__hmm, gkg__ngv, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    iosol__ofgv = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        mtxc__ppdt = len(len_arr)
        for i in range(mtxc__ppdt):
            offsets[i] = iosol__ofgv
            iosol__ofgv += len_arr[i]
        offsets[mtxc__ppdt] = iosol__ofgv
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    beuvs__zdk = i // 8
    loud__njb = getitem_str_bitmap(bits, beuvs__zdk)
    loud__njb ^= np.uint8(-np.uint8(bit_is_set) ^ loud__njb) & kBitmask[i % 8]
    setitem_str_bitmap(bits, beuvs__zdk, loud__njb)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    umzha__ukrpq = get_null_bitmap_ptr(out_str_arr)
    cbm__vbx = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        lun__iilsw = get_bit_bitmap(cbm__vbx, j)
        set_bit_to(umzha__ukrpq, out_start + j, lun__iilsw)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, ymf__rengr, xdpp__flzb, nuaoi__stqee = args
        nysd__rvzzo = _get_str_binary_arr_payload(context, builder,
            ymf__rengr, string_array_type)
        iuqi__nbew = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        bwih__vmjko = context.make_helper(builder, offset_arr_type,
            nysd__rvzzo.offsets).data
        unx__yhfqm = context.make_helper(builder, offset_arr_type,
            iuqi__nbew.offsets).data
        lwatd__svde = context.make_helper(builder, char_arr_type,
            nysd__rvzzo.data).data
        azbe__vius = context.make_helper(builder, char_arr_type, iuqi__nbew
            .data).data
        num_total_chars = _get_num_total_chars(builder, bwih__vmjko,
            nysd__rvzzo.n_arrays)
        keirq__zdzho = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        czg__ypin = cgutils.get_or_insert_function(builder.module,
            keirq__zdzho, name='set_string_array_range')
        builder.call(czg__ypin, [unx__yhfqm, azbe__vius, bwih__vmjko,
            lwatd__svde, xdpp__flzb, nuaoi__stqee, nysd__rvzzo.n_arrays,
            num_total_chars])
        eumcs__bwoq = context.typing_context.resolve_value_type(
            copy_nulls_range)
        wqcr__pghk = eumcs__bwoq.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        kwrw__gknkf = context.get_function(eumcs__bwoq, wqcr__pghk)
        kwrw__gknkf(builder, (out_arr, ymf__rengr, xdpp__flzb))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    ehor__zzyy = c.context.make_helper(c.builder, typ, val)
    jwpth__uvq = ArrayItemArrayType(char_arr_type)
    ibrf__lrkb = _get_array_item_arr_payload(c.context, c.builder,
        jwpth__uvq, ehor__zzyy.data)
    moo__sku = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    lkyh__odozt = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        lkyh__odozt = 'pd_array_from_string_array'
    keirq__zdzho = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    bgjvy__tbgnx = cgutils.get_or_insert_function(c.builder.module,
        keirq__zdzho, name=lkyh__odozt)
    wuhu__hrw = c.context.make_array(offset_arr_type)(c.context, c.builder,
        ibrf__lrkb.offsets).data
    qrv__qxk = c.context.make_array(char_arr_type)(c.context, c.builder,
        ibrf__lrkb.data).data
    hmyxl__hmm = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, ibrf__lrkb.null_bitmap).data
    arr = c.builder.call(bgjvy__tbgnx, [ibrf__lrkb.n_arrays, wuhu__hrw,
        qrv__qxk, hmyxl__hmm, moo__sku])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        hmyxl__hmm = context.make_array(null_bitmap_arr_type)(context,
            builder, ibrf__lrkb.null_bitmap).data
        pjfxy__vqib = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        knjxb__rqsb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        loud__njb = builder.load(builder.gep(hmyxl__hmm, [pjfxy__vqib],
            inbounds=True))
        twqtz__hfc = lir.ArrayType(lir.IntType(8), 8)
        vne__mzbnq = cgutils.alloca_once_value(builder, lir.Constant(
            twqtz__hfc, (1, 2, 4, 8, 16, 32, 64, 128)))
        ceep__mddo = builder.load(builder.gep(vne__mzbnq, [lir.Constant(lir
            .IntType(64), 0), knjxb__rqsb], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(loud__njb,
            ceep__mddo), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pjfxy__vqib = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        knjxb__rqsb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        hmyxl__hmm = context.make_array(null_bitmap_arr_type)(context,
            builder, ibrf__lrkb.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, ibrf__lrkb.
            offsets).data
        sof__zgq = builder.gep(hmyxl__hmm, [pjfxy__vqib], inbounds=True)
        loud__njb = builder.load(sof__zgq)
        twqtz__hfc = lir.ArrayType(lir.IntType(8), 8)
        vne__mzbnq = cgutils.alloca_once_value(builder, lir.Constant(
            twqtz__hfc, (1, 2, 4, 8, 16, 32, 64, 128)))
        ceep__mddo = builder.load(builder.gep(vne__mzbnq, [lir.Constant(lir
            .IntType(64), 0), knjxb__rqsb], inbounds=True))
        ceep__mddo = builder.xor(ceep__mddo, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(loud__njb, ceep__mddo), sof__zgq)
        if str_arr_typ == string_array_type:
            lqayj__aeov = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            zgkpq__xyuu = builder.icmp_unsigned('!=', lqayj__aeov,
                ibrf__lrkb.n_arrays)
            with builder.if_then(zgkpq__xyuu):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [lqayj__aeov]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pjfxy__vqib = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        knjxb__rqsb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        hmyxl__hmm = context.make_array(null_bitmap_arr_type)(context,
            builder, ibrf__lrkb.null_bitmap).data
        sof__zgq = builder.gep(hmyxl__hmm, [pjfxy__vqib], inbounds=True)
        loud__njb = builder.load(sof__zgq)
        twqtz__hfc = lir.ArrayType(lir.IntType(8), 8)
        vne__mzbnq = cgutils.alloca_once_value(builder, lir.Constant(
            twqtz__hfc, (1, 2, 4, 8, 16, 32, 64, 128)))
        ceep__mddo = builder.load(builder.gep(vne__mzbnq, [lir.Constant(lir
            .IntType(64), 0), knjxb__rqsb], inbounds=True))
        builder.store(builder.or_(loud__njb, ceep__mddo), sof__zgq)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gkg__ngv = builder.udiv(builder.add(ibrf__lrkb.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        hmyxl__hmm = context.make_array(null_bitmap_arr_type)(context,
            builder, ibrf__lrkb.null_bitmap).data
        cgutils.memset(builder, hmyxl__hmm, gkg__ngv, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    bfh__vrt = context.make_helper(builder, string_array_type, str_arr)
    jwpth__uvq = ArrayItemArrayType(char_arr_type)
    bnwov__srwv = context.make_helper(builder, jwpth__uvq, bfh__vrt.data)
    cpi__ovi = ArrayItemArrayPayloadType(jwpth__uvq)
    dalp__dau = context.nrt.meminfo_data(builder, bnwov__srwv.meminfo)
    sceab__enibn = builder.bitcast(dalp__dau, context.get_value_type(
        cpi__ovi).as_pointer())
    return sceab__enibn


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        osin__mix, bkz__rack = args
        fsg__kzcm = _get_str_binary_arr_data_payload_ptr(context, builder,
            bkz__rack)
        tlncx__rdr = _get_str_binary_arr_data_payload_ptr(context, builder,
            osin__mix)
        dmv__uqvo = _get_str_binary_arr_payload(context, builder, bkz__rack,
            sig.args[1])
        rgfzu__fzaf = _get_str_binary_arr_payload(context, builder,
            osin__mix, sig.args[0])
        context.nrt.incref(builder, char_arr_type, dmv__uqvo.data)
        context.nrt.incref(builder, offset_arr_type, dmv__uqvo.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, dmv__uqvo.null_bitmap
            )
        context.nrt.decref(builder, char_arr_type, rgfzu__fzaf.data)
        context.nrt.decref(builder, offset_arr_type, rgfzu__fzaf.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, rgfzu__fzaf.
            null_bitmap)
        builder.store(builder.load(fsg__kzcm), tlncx__rdr)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        zfeu__qsaq = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return zfeu__qsaq
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, dyd__flzyw, rbcp__froe = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder, arr, sig
            .args[0])
        offsets = context.make_helper(builder, offset_arr_type, ibrf__lrkb.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ibrf__lrkb.data
            ).data
        keirq__zdzho = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        situ__tbhg = cgutils.get_or_insert_function(builder.module,
            keirq__zdzho, name='setitem_string_array')
        uzde__xtzyn = context.get_constant(types.int32, -1)
        fdsra__ezdd = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, ibrf__lrkb
            .n_arrays)
        builder.call(situ__tbhg, [offsets, data, num_total_chars, builder.
            extract_value(dyd__flzyw, 0), rbcp__froe, uzde__xtzyn,
            fdsra__ezdd, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    keirq__zdzho = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    lyat__kuhb = cgutils.get_or_insert_function(builder.module,
        keirq__zdzho, name='is_na')
    return builder.call(lyat__kuhb, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        lirr__htq, abbut__yzcef, wnpbj__bkmbp, pnad__uonxs = args
        cgutils.raw_memcpy(builder, lirr__htq, abbut__yzcef, wnpbj__bkmbp,
            pnad__uonxs)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        xad__kdiee, hoh__htn = unicode_to_utf8_and_len(val)
        nbdz__fqw = getitem_str_offset(A, ind)
        iiswt__xis = getitem_str_offset(A, ind + 1)
        bwhqm__bjvy = iiswt__xis - nbdz__fqw
        if bwhqm__bjvy != hoh__htn:
            return False
        dyd__flzyw = get_data_ptr_ind(A, nbdz__fqw)
        return memcmp(dyd__flzyw, xad__kdiee, hoh__htn) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        nbdz__fqw = getitem_str_offset(A, ind)
        bwhqm__bjvy = bodo.libs.str_ext.int_to_str_len(val)
        kpx__nlmb = nbdz__fqw + bwhqm__bjvy
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            nbdz__fqw, kpx__nlmb)
        dyd__flzyw = get_data_ptr_ind(A, nbdz__fqw)
        inplace_int64_to_str(dyd__flzyw, bwhqm__bjvy, val)
        setitem_str_offset(A, ind + 1, nbdz__fqw + bwhqm__bjvy)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        dyd__flzyw, = args
        iem__wxju = context.insert_const_string(builder.module, '<NA>')
        ohr__yro = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, dyd__flzyw, iem__wxju, ohr__yro, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    ztkc__etvtt = len('<NA>')

    def impl(A, ind):
        nbdz__fqw = getitem_str_offset(A, ind)
        kpx__nlmb = nbdz__fqw + ztkc__etvtt
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            nbdz__fqw, kpx__nlmb)
        dyd__flzyw = get_data_ptr_ind(A, nbdz__fqw)
        inplace_set_NA_str(dyd__flzyw)
        setitem_str_offset(A, ind + 1, nbdz__fqw + ztkc__etvtt)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            nbdz__fqw = getitem_str_offset(A, ind)
            iiswt__xis = getitem_str_offset(A, ind + 1)
            rbcp__froe = iiswt__xis - nbdz__fqw
            dyd__flzyw = get_data_ptr_ind(A, nbdz__fqw)
            vfa__smlis = decode_utf8(dyd__flzyw, rbcp__froe)
            return vfa__smlis
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            zfeu__qsaq = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(zfeu__qsaq):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            aijn__medaq = get_data_ptr(out_arr).data
            ujczl__jyw = get_data_ptr(A).data
            npjpj__pfw = 0
            qwa__ocu = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(zfeu__qsaq):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    czosx__cfjb = get_str_arr_item_length(A, i)
                    if czosx__cfjb == 1:
                        copy_single_char(aijn__medaq, qwa__ocu, ujczl__jyw,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(aijn__medaq, qwa__ocu, ujczl__jyw,
                            getitem_str_offset(A, i), czosx__cfjb, 1)
                    qwa__ocu += czosx__cfjb
                    setitem_str_offset(out_arr, npjpj__pfw + 1, qwa__ocu)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, npjpj__pfw)
                    else:
                        str_arr_set_not_na(out_arr, npjpj__pfw)
                    npjpj__pfw += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            zfeu__qsaq = len(ind)
            out_arr = pre_alloc_string_array(zfeu__qsaq, -1)
            npjpj__pfw = 0
            for i in range(zfeu__qsaq):
                xhyoa__yxgd = A[ind[i]]
                out_arr[npjpj__pfw] = xhyoa__yxgd
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, npjpj__pfw)
                npjpj__pfw += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            zfeu__qsaq = len(A)
            nkgi__dziek = numba.cpython.unicode._normalize_slice(ind,
                zfeu__qsaq)
            vhmdk__jvyan = numba.cpython.unicode._slice_span(nkgi__dziek)
            if nkgi__dziek.step == 1:
                nbdz__fqw = getitem_str_offset(A, nkgi__dziek.start)
                iiswt__xis = getitem_str_offset(A, nkgi__dziek.stop)
                n_chars = iiswt__xis - nbdz__fqw
                qhmj__arrf = pre_alloc_string_array(vhmdk__jvyan, np.int64(
                    n_chars))
                for i in range(vhmdk__jvyan):
                    qhmj__arrf[i] = A[nkgi__dziek.start + i]
                    if str_arr_is_na(A, nkgi__dziek.start + i):
                        str_arr_set_na(qhmj__arrf, i)
                return qhmj__arrf
            else:
                qhmj__arrf = pre_alloc_string_array(vhmdk__jvyan, -1)
                for i in range(vhmdk__jvyan):
                    qhmj__arrf[i] = A[nkgi__dziek.start + i * nkgi__dziek.step]
                    if str_arr_is_na(A, nkgi__dziek.start + i * nkgi__dziek
                        .step):
                        str_arr_set_na(qhmj__arrf, i)
                return qhmj__arrf
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    bkp__bugz = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(bkp__bugz)
        iavt__qrtl = 4

        def impl_scalar(A, idx, val):
            xfvly__uwh = (val._length if val._is_ascii else iavt__qrtl *
                val._length)
            hyyy__dspv = A._data
            nbdz__fqw = np.int64(getitem_str_offset(A, idx))
            kpx__nlmb = nbdz__fqw + xfvly__uwh
            bodo.libs.array_item_arr_ext.ensure_data_capacity(hyyy__dspv,
                nbdz__fqw, kpx__nlmb)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                kpx__nlmb, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                nkgi__dziek = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                pas__pdllf = nkgi__dziek.start
                hyyy__dspv = A._data
                nbdz__fqw = np.int64(getitem_str_offset(A, pas__pdllf))
                kpx__nlmb = nbdz__fqw + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(hyyy__dspv,
                    nbdz__fqw, kpx__nlmb)
                set_string_array_range(A, val, pas__pdllf, nbdz__fqw)
                thr__nvqb = 0
                for i in range(nkgi__dziek.start, nkgi__dziek.stop,
                    nkgi__dziek.step):
                    if str_arr_is_na(val, thr__nvqb):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    thr__nvqb += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                wqvn__pfkg = str_list_to_array(val)
                A[idx] = wqvn__pfkg
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                nkgi__dziek = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(nkgi__dziek.start, nkgi__dziek.stop,
                    nkgi__dziek.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(bkp__bugz)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                zfeu__qsaq = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(zfeu__qsaq, -1)
                for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                zfeu__qsaq = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(zfeu__qsaq, -1)
                zuyaa__fjxss = 0
                for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, zuyaa__fjxss):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, zuyaa__fjxss)
                        else:
                            out_arr[i] = str(val[zuyaa__fjxss])
                        zuyaa__fjxss += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(bkp__bugz)
    raise BodoError(bkp__bugz)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    shhr__gay = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(shhr__gay, (types.Float, types.Integer)
        ) and shhr__gay not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(shhr__gay, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            zfeu__qsaq = len(A)
            B = np.empty(zfeu__qsaq, shhr__gay)
            for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif shhr__gay == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            zfeu__qsaq = len(A)
            B = np.empty(zfeu__qsaq, shhr__gay)
            for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif shhr__gay == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            zfeu__qsaq = len(A)
            B = np.empty(zfeu__qsaq, shhr__gay)
            for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            zfeu__qsaq = len(A)
            B = np.empty(zfeu__qsaq, shhr__gay)
            for i in numba.parfors.parfor.internal_prange(zfeu__qsaq):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        dyd__flzyw, rbcp__froe = args
        rtofj__armtp = context.get_python_api(builder)
        ghc__vvs = rtofj__armtp.string_from_string_and_size(dyd__flzyw,
            rbcp__froe)
        kwb__klz = rtofj__armtp.to_native_value(string_type, ghc__vvs).value
        zdnyj__npl = cgutils.create_struct_proxy(string_type)(context,
            builder, kwb__klz)
        zdnyj__npl.hash = zdnyj__npl.hash.type(-1)
        rtofj__armtp.decref(ghc__vvs)
        return zdnyj__npl._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    str_arr = decode_if_dict_array(str_arr)
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type, '_str_arr_item_to_numeric: str arr expected'
    assert ind_t == types.int64, '_str_arr_item_to_numeric: integer index expected'

    def codegen(context, builder, sig, args):
        tauy__flqk, arr, ind, kfo__cng = args
        ibrf__lrkb = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ibrf__lrkb.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ibrf__lrkb.data
            ).data
        keirq__zdzho = lir.FunctionType(lir.IntType(32), [tauy__flqk.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        vlaq__jhxwp = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            vlaq__jhxwp = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        ysuan__lvsmn = cgutils.get_or_insert_function(builder.module,
            keirq__zdzho, vlaq__jhxwp)
        return builder.call(ysuan__lvsmn, [tauy__flqk, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    moo__sku = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    keirq__zdzho = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(32)])
    cxg__oab = cgutils.get_or_insert_function(c.builder.module,
        keirq__zdzho, name='string_array_from_sequence')
    uno__jmyja = c.builder.call(cxg__oab, [val, moo__sku])
    jwpth__uvq = ArrayItemArrayType(char_arr_type)
    bnwov__srwv = c.context.make_helper(c.builder, jwpth__uvq)
    bnwov__srwv.meminfo = uno__jmyja
    bfh__vrt = c.context.make_helper(c.builder, typ)
    hyyy__dspv = bnwov__srwv._getvalue()
    bfh__vrt.data = hyyy__dspv
    ibhln__zile = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bfh__vrt._getvalue(), is_error=ibhln__zile)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    zfeu__qsaq = len(pyval)
    qwa__ocu = 0
    vnq__kaxw = np.empty(zfeu__qsaq + 1, np_offset_type)
    pbmj__wqgz = []
    sco__nfgd = np.empty(zfeu__qsaq + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        vnq__kaxw[i] = qwa__ocu
        nnlf__fbx = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(sco__nfgd, i, int(not nnlf__fbx))
        if nnlf__fbx:
            continue
        cwx__idxjr = list(s.encode()) if isinstance(s, str) else list(s)
        pbmj__wqgz.extend(cwx__idxjr)
        qwa__ocu += len(cwx__idxjr)
    vnq__kaxw[zfeu__qsaq] = qwa__ocu
    xjnx__ynuc = np.array(pbmj__wqgz, np.uint8)
    bfuk__irnyz = context.get_constant(types.int64, zfeu__qsaq)
    aqkp__dcawn = context.get_constant_generic(builder, char_arr_type,
        xjnx__ynuc)
    muogd__hpg = context.get_constant_generic(builder, offset_arr_type,
        vnq__kaxw)
    vbsf__dxbat = context.get_constant_generic(builder,
        null_bitmap_arr_type, sco__nfgd)
    ibrf__lrkb = lir.Constant.literal_struct([bfuk__irnyz, aqkp__dcawn,
        muogd__hpg, vbsf__dxbat])
    ibrf__lrkb = cgutils.global_constant(builder, '.const.payload', ibrf__lrkb
        ).bitcast(cgutils.voidptr_t)
    mjqfs__ecbf = context.get_constant(types.int64, -1)
    uaa__jnif = context.get_constant_null(types.voidptr)
    wpx__kix = lir.Constant.literal_struct([mjqfs__ecbf, uaa__jnif,
        uaa__jnif, ibrf__lrkb, mjqfs__ecbf])
    wpx__kix = cgutils.global_constant(builder, '.const.meminfo', wpx__kix
        ).bitcast(cgutils.voidptr_t)
    hyyy__dspv = lir.Constant.literal_struct([wpx__kix])
    bfh__vrt = lir.Constant.literal_struct([hyyy__dspv])
    return bfh__vrt


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
