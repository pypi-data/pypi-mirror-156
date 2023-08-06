import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qdpoy__poonc = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, qdpoy__poonc)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    gce__avj = context.get_value_type(str_arr_split_view_payload_type)
    ajkor__nemzs = context.get_abi_sizeof(gce__avj)
    deymx__bkbml = context.get_value_type(types.voidptr)
    iuvw__ukt = context.get_value_type(types.uintp)
    bud__nooo = lir.FunctionType(lir.VoidType(), [deymx__bkbml, iuvw__ukt,
        deymx__bkbml])
    vkk__ognt = cgutils.get_or_insert_function(builder.module, bud__nooo,
        name='dtor_str_arr_split_view')
    uyylh__nswgk = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ajkor__nemzs), vkk__ognt)
    bjo__syr = context.nrt.meminfo_data(builder, uyylh__nswgk)
    olgh__pxo = builder.bitcast(bjo__syr, gce__avj.as_pointer())
    return uyylh__nswgk, olgh__pxo


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        dyrwo__oypd, jrck__gza = args
        uyylh__nswgk, olgh__pxo = construct_str_arr_split_view(context, builder
            )
        sak__lvcn = _get_str_binary_arr_payload(context, builder,
            dyrwo__oypd, string_array_type)
        tdsms__utx = lir.FunctionType(lir.VoidType(), [olgh__pxo.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        xass__bww = cgutils.get_or_insert_function(builder.module,
            tdsms__utx, name='str_arr_split_view_impl')
        sdl__oqwkj = context.make_helper(builder, offset_arr_type,
            sak__lvcn.offsets).data
        xlit__mtdne = context.make_helper(builder, char_arr_type, sak__lvcn
            .data).data
        xwdid__lstug = context.make_helper(builder, null_bitmap_arr_type,
            sak__lvcn.null_bitmap).data
        hto__svrx = context.get_constant(types.int8, ord(sep_typ.literal_value)
            )
        builder.call(xass__bww, [olgh__pxo, sak__lvcn.n_arrays, sdl__oqwkj,
            xlit__mtdne, xwdid__lstug, hto__svrx])
        adpel__jiwld = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(olgh__pxo))
        nbpgw__qodw = context.make_helper(builder, string_array_split_view_type
            )
        nbpgw__qodw.num_items = sak__lvcn.n_arrays
        nbpgw__qodw.index_offsets = adpel__jiwld.index_offsets
        nbpgw__qodw.data_offsets = adpel__jiwld.data_offsets
        nbpgw__qodw.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [dyrwo__oypd]
            )
        nbpgw__qodw.null_bitmap = adpel__jiwld.null_bitmap
        nbpgw__qodw.meminfo = uyylh__nswgk
        nedub__mibkz = nbpgw__qodw._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, nedub__mibkz)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    ohi__atf = context.make_helper(builder, string_array_split_view_type, val)
    afs__rrt = context.insert_const_string(builder.module, 'numpy')
    otyc__obg = c.pyapi.import_module_noblock(afs__rrt)
    dtype = c.pyapi.object_getattr_string(otyc__obg, 'object_')
    jsog__bto = builder.sext(ohi__atf.num_items, c.pyapi.longlong)
    wkokq__zwei = c.pyapi.long_from_longlong(jsog__bto)
    llqc__axg = c.pyapi.call_method(otyc__obg, 'ndarray', (wkokq__zwei, dtype))
    serbb__layi = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    fdgiq__uxuv = c.pyapi._get_function(serbb__layi, name='array_getptr1')
    kojz__fdpi = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    oix__fje = c.pyapi._get_function(kojz__fdpi, name='array_setitem')
    mpir__adrw = c.pyapi.object_getattr_string(otyc__obg, 'nan')
    with cgutils.for_range(builder, ohi__atf.num_items) as pqko__klsy:
        str_ind = pqko__klsy.index
        dlcsl__ypijf = builder.sext(builder.load(builder.gep(ohi__atf.
            index_offsets, [str_ind])), lir.IntType(64))
        zyv__iinhv = builder.sext(builder.load(builder.gep(ohi__atf.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        gltu__efeaw = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        spqga__jvff = builder.gep(ohi__atf.null_bitmap, [gltu__efeaw])
        lydkh__lpysv = builder.load(spqga__jvff)
        qpob__oqpey = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(lydkh__lpysv, qpob__oqpey), lir.
            Constant(lir.IntType(8), 1))
        yzqf__ygwbf = builder.sub(zyv__iinhv, dlcsl__ypijf)
        yzqf__ygwbf = builder.sub(yzqf__ygwbf, yzqf__ygwbf.type(1))
        qdici__eff = builder.call(fdgiq__uxuv, [llqc__axg, str_ind])
        kajdh__mziv = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(kajdh__mziv) as (wpv__dbocq, uedhf__wyxn):
            with wpv__dbocq:
                bym__mcpzg = c.pyapi.list_new(yzqf__ygwbf)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    bym__mcpzg), likely=True):
                    with cgutils.for_range(c.builder, yzqf__ygwbf
                        ) as pqko__klsy:
                        lgyx__nra = builder.add(dlcsl__ypijf, pqko__klsy.index)
                        data_start = builder.load(builder.gep(ohi__atf.
                            data_offsets, [lgyx__nra]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        vqb__hjek = builder.load(builder.gep(ohi__atf.
                            data_offsets, [builder.add(lgyx__nra, lgyx__nra
                            .type(1))]))
                        pbtq__moel = builder.gep(builder.extract_value(
                            ohi__atf.data, 0), [data_start])
                        kmiha__yrcf = builder.sext(builder.sub(vqb__hjek,
                            data_start), lir.IntType(64))
                        kzcrl__jwezg = c.pyapi.string_from_string_and_size(
                            pbtq__moel, kmiha__yrcf)
                        c.pyapi.list_setitem(bym__mcpzg, pqko__klsy.index,
                            kzcrl__jwezg)
                builder.call(oix__fje, [llqc__axg, qdici__eff, bym__mcpzg])
            with uedhf__wyxn:
                builder.call(oix__fje, [llqc__axg, qdici__eff, mpir__adrw])
    c.pyapi.decref(otyc__obg)
    c.pyapi.decref(dtype)
    c.pyapi.decref(mpir__adrw)
    return llqc__axg


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        hnow__mel, jfh__zpog, pbtq__moel = args
        uyylh__nswgk, olgh__pxo = construct_str_arr_split_view(context, builder
            )
        tdsms__utx = lir.FunctionType(lir.VoidType(), [olgh__pxo.type, lir.
            IntType(64), lir.IntType(64)])
        xass__bww = cgutils.get_or_insert_function(builder.module,
            tdsms__utx, name='str_arr_split_view_alloc')
        builder.call(xass__bww, [olgh__pxo, hnow__mel, jfh__zpog])
        adpel__jiwld = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(olgh__pxo))
        nbpgw__qodw = context.make_helper(builder, string_array_split_view_type
            )
        nbpgw__qodw.num_items = hnow__mel
        nbpgw__qodw.index_offsets = adpel__jiwld.index_offsets
        nbpgw__qodw.data_offsets = adpel__jiwld.data_offsets
        nbpgw__qodw.data = pbtq__moel
        nbpgw__qodw.null_bitmap = adpel__jiwld.null_bitmap
        context.nrt.incref(builder, data_t, pbtq__moel)
        nbpgw__qodw.meminfo = uyylh__nswgk
        nedub__mibkz = nbpgw__qodw._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, nedub__mibkz)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        pcka__qwm, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            pcka__qwm = builder.extract_value(pcka__qwm, 0)
        return builder.bitcast(builder.gep(pcka__qwm, [ind]), lir.IntType(8
            ).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        pcka__qwm, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            pcka__qwm = builder.extract_value(pcka__qwm, 0)
        return builder.load(builder.gep(pcka__qwm, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        pcka__qwm, ind, odnq__tbz = args
        qdtnt__ugt = builder.gep(pcka__qwm, [ind])
        builder.store(odnq__tbz, qdtnt__ugt)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        ziop__pdhea, ind = args
        pwrw__zrv = context.make_helper(builder, arr_ctypes_t, ziop__pdhea)
        oew__cmvaq = context.make_helper(builder, arr_ctypes_t)
        oew__cmvaq.data = builder.gep(pwrw__zrv.data, [ind])
        oew__cmvaq.meminfo = pwrw__zrv.meminfo
        yekh__wqb = oew__cmvaq._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, yekh__wqb)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    rfepo__fiiki = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
        _null_bitmap, item_ind)
    if not rfepo__fiiki:
        return 0, 0, 0
    lgyx__nra = getitem_c_arr(arr._index_offsets, item_ind)
    ldv__worqm = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    dmu__njh = ldv__worqm - lgyx__nra
    if str_ind >= dmu__njh:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, lgyx__nra + str_ind)
    data_start += 1
    if lgyx__nra + str_ind == 0:
        data_start = 0
    vqb__hjek = getitem_c_arr(arr._data_offsets, lgyx__nra + str_ind + 1)
    mnhp__njtd = vqb__hjek - data_start
    return 1, data_start, mnhp__njtd


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        own__wpxa = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            lgyx__nra = getitem_c_arr(A._index_offsets, ind)
            ldv__worqm = getitem_c_arr(A._index_offsets, ind + 1)
            mbyru__wgwp = ldv__worqm - lgyx__nra - 1
            dyrwo__oypd = bodo.libs.str_arr_ext.pre_alloc_string_array(
                mbyru__wgwp, -1)
            for caemv__qerj in range(mbyru__wgwp):
                data_start = getitem_c_arr(A._data_offsets, lgyx__nra +
                    caemv__qerj)
                data_start += 1
                if lgyx__nra + caemv__qerj == 0:
                    data_start = 0
                vqb__hjek = getitem_c_arr(A._data_offsets, lgyx__nra +
                    caemv__qerj + 1)
                mnhp__njtd = vqb__hjek - data_start
                qdtnt__ugt = get_array_ctypes_ptr(A._data, data_start)
                rysbj__qnalv = bodo.libs.str_arr_ext.decode_utf8(qdtnt__ugt,
                    mnhp__njtd)
                dyrwo__oypd[caemv__qerj] = rysbj__qnalv
            return dyrwo__oypd
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        jquxc__ijsw = offset_type.bitwidth // 8

        def _impl(A, ind):
            mbyru__wgwp = len(A)
            if mbyru__wgwp != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            hnow__mel = 0
            jfh__zpog = 0
            for caemv__qerj in range(mbyru__wgwp):
                if ind[caemv__qerj]:
                    hnow__mel += 1
                    lgyx__nra = getitem_c_arr(A._index_offsets, caemv__qerj)
                    ldv__worqm = getitem_c_arr(A._index_offsets, 
                        caemv__qerj + 1)
                    jfh__zpog += ldv__worqm - lgyx__nra
            llqc__axg = pre_alloc_str_arr_view(hnow__mel, jfh__zpog, A._data)
            item_ind = 0
            dohbw__thar = 0
            for caemv__qerj in range(mbyru__wgwp):
                if ind[caemv__qerj]:
                    lgyx__nra = getitem_c_arr(A._index_offsets, caemv__qerj)
                    ldv__worqm = getitem_c_arr(A._index_offsets, 
                        caemv__qerj + 1)
                    gmcvw__mpotb = ldv__worqm - lgyx__nra
                    setitem_c_arr(llqc__axg._index_offsets, item_ind,
                        dohbw__thar)
                    qdtnt__ugt = get_c_arr_ptr(A._data_offsets, lgyx__nra)
                    lexd__ztsl = get_c_arr_ptr(llqc__axg._data_offsets,
                        dohbw__thar)
                    _memcpy(lexd__ztsl, qdtnt__ugt, gmcvw__mpotb, jquxc__ijsw)
                    rfepo__fiiki = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, caemv__qerj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(llqc__axg.
                        _null_bitmap, item_ind, rfepo__fiiki)
                    item_ind += 1
                    dohbw__thar += gmcvw__mpotb
            setitem_c_arr(llqc__axg._index_offsets, item_ind, dohbw__thar)
            return llqc__axg
        return _impl
