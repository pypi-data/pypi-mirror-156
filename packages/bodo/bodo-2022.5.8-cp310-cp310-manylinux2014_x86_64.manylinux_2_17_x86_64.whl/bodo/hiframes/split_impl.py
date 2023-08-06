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
        vfma__sybr = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, vfma__sybr)


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
    igyx__kuuct = context.get_value_type(str_arr_split_view_payload_type)
    qmjj__orrtn = context.get_abi_sizeof(igyx__kuuct)
    enpui__dxsc = context.get_value_type(types.voidptr)
    lic__gyv = context.get_value_type(types.uintp)
    jft__ljsma = lir.FunctionType(lir.VoidType(), [enpui__dxsc, lic__gyv,
        enpui__dxsc])
    ixrzb__rltds = cgutils.get_or_insert_function(builder.module,
        jft__ljsma, name='dtor_str_arr_split_view')
    kqy__mxgn = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qmjj__orrtn), ixrzb__rltds)
    svs__tle = context.nrt.meminfo_data(builder, kqy__mxgn)
    beqho__ytn = builder.bitcast(svs__tle, igyx__kuuct.as_pointer())
    return kqy__mxgn, beqho__ytn


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        vcgyj__mtwi, soego__uhzct = args
        kqy__mxgn, beqho__ytn = construct_str_arr_split_view(context, builder)
        vadkj__sqd = _get_str_binary_arr_payload(context, builder,
            vcgyj__mtwi, string_array_type)
        jbii__pxof = lir.FunctionType(lir.VoidType(), [beqho__ytn.type, lir
            .IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        hdoas__gcwut = cgutils.get_or_insert_function(builder.module,
            jbii__pxof, name='str_arr_split_view_impl')
        coh__vcwra = context.make_helper(builder, offset_arr_type,
            vadkj__sqd.offsets).data
        ejc__gaeet = context.make_helper(builder, char_arr_type, vadkj__sqd
            .data).data
        ggy__qjgmm = context.make_helper(builder, null_bitmap_arr_type,
            vadkj__sqd.null_bitmap).data
        coa__inyfw = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(hdoas__gcwut, [beqho__ytn, vadkj__sqd.n_arrays,
            coh__vcwra, ejc__gaeet, ggy__qjgmm, coa__inyfw])
        jnyh__uvw = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(beqho__ytn))
        vpkow__cvdmk = context.make_helper(builder,
            string_array_split_view_type)
        vpkow__cvdmk.num_items = vadkj__sqd.n_arrays
        vpkow__cvdmk.index_offsets = jnyh__uvw.index_offsets
        vpkow__cvdmk.data_offsets = jnyh__uvw.data_offsets
        vpkow__cvdmk.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [vcgyj__mtwi]
            )
        vpkow__cvdmk.null_bitmap = jnyh__uvw.null_bitmap
        vpkow__cvdmk.meminfo = kqy__mxgn
        tnfhp__qoi = vpkow__cvdmk._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, tnfhp__qoi)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    mxf__ubpk = context.make_helper(builder, string_array_split_view_type, val)
    vnxe__wjgk = context.insert_const_string(builder.module, 'numpy')
    zbez__fup = c.pyapi.import_module_noblock(vnxe__wjgk)
    dtype = c.pyapi.object_getattr_string(zbez__fup, 'object_')
    hfron__qmz = builder.sext(mxf__ubpk.num_items, c.pyapi.longlong)
    iipl__atccb = c.pyapi.long_from_longlong(hfron__qmz)
    mzrm__eghd = c.pyapi.call_method(zbez__fup, 'ndarray', (iipl__atccb, dtype)
        )
    oyll__ooan = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    wip__xvl = c.pyapi._get_function(oyll__ooan, name='array_getptr1')
    tozjk__xul = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    sazzj__xbzp = c.pyapi._get_function(tozjk__xul, name='array_setitem')
    exir__oxk = c.pyapi.object_getattr_string(zbez__fup, 'nan')
    with cgutils.for_range(builder, mxf__ubpk.num_items) as uhrb__lob:
        str_ind = uhrb__lob.index
        soxd__yevz = builder.sext(builder.load(builder.gep(mxf__ubpk.
            index_offsets, [str_ind])), lir.IntType(64))
        wjzno__nzw = builder.sext(builder.load(builder.gep(mxf__ubpk.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        thm__jgke = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        pthj__ygqp = builder.gep(mxf__ubpk.null_bitmap, [thm__jgke])
        qzzc__qknoi = builder.load(pthj__ygqp)
        fxn__vvhkk = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(qzzc__qknoi, fxn__vvhkk), lir.
            Constant(lir.IntType(8), 1))
        loolh__ekjp = builder.sub(wjzno__nzw, soxd__yevz)
        loolh__ekjp = builder.sub(loolh__ekjp, loolh__ekjp.type(1))
        ljnb__qsd = builder.call(wip__xvl, [mzrm__eghd, str_ind])
        kebxk__tnj = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(kebxk__tnj) as (zzns__fhvoa, crkh__doi):
            with zzns__fhvoa:
                byc__ixo = c.pyapi.list_new(loolh__ekjp)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    byc__ixo), likely=True):
                    with cgutils.for_range(c.builder, loolh__ekjp
                        ) as uhrb__lob:
                        nfnbu__jilpi = builder.add(soxd__yevz, uhrb__lob.index)
                        data_start = builder.load(builder.gep(mxf__ubpk.
                            data_offsets, [nfnbu__jilpi]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        zhwm__zvddw = builder.load(builder.gep(mxf__ubpk.
                            data_offsets, [builder.add(nfnbu__jilpi,
                            nfnbu__jilpi.type(1))]))
                        kdxjd__gkg = builder.gep(builder.extract_value(
                            mxf__ubpk.data, 0), [data_start])
                        lekp__cbgez = builder.sext(builder.sub(zhwm__zvddw,
                            data_start), lir.IntType(64))
                        augt__uwke = c.pyapi.string_from_string_and_size(
                            kdxjd__gkg, lekp__cbgez)
                        c.pyapi.list_setitem(byc__ixo, uhrb__lob.index,
                            augt__uwke)
                builder.call(sazzj__xbzp, [mzrm__eghd, ljnb__qsd, byc__ixo])
            with crkh__doi:
                builder.call(sazzj__xbzp, [mzrm__eghd, ljnb__qsd, exir__oxk])
    c.pyapi.decref(zbez__fup)
    c.pyapi.decref(dtype)
    c.pyapi.decref(exir__oxk)
    return mzrm__eghd


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        roix__okac, hfygn__dba, kdxjd__gkg = args
        kqy__mxgn, beqho__ytn = construct_str_arr_split_view(context, builder)
        jbii__pxof = lir.FunctionType(lir.VoidType(), [beqho__ytn.type, lir
            .IntType(64), lir.IntType(64)])
        hdoas__gcwut = cgutils.get_or_insert_function(builder.module,
            jbii__pxof, name='str_arr_split_view_alloc')
        builder.call(hdoas__gcwut, [beqho__ytn, roix__okac, hfygn__dba])
        jnyh__uvw = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(beqho__ytn))
        vpkow__cvdmk = context.make_helper(builder,
            string_array_split_view_type)
        vpkow__cvdmk.num_items = roix__okac
        vpkow__cvdmk.index_offsets = jnyh__uvw.index_offsets
        vpkow__cvdmk.data_offsets = jnyh__uvw.data_offsets
        vpkow__cvdmk.data = kdxjd__gkg
        vpkow__cvdmk.null_bitmap = jnyh__uvw.null_bitmap
        context.nrt.incref(builder, data_t, kdxjd__gkg)
        vpkow__cvdmk.meminfo = kqy__mxgn
        tnfhp__qoi = vpkow__cvdmk._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, tnfhp__qoi)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        lwd__lvzx, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            lwd__lvzx = builder.extract_value(lwd__lvzx, 0)
        return builder.bitcast(builder.gep(lwd__lvzx, [ind]), lir.IntType(8
            ).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        lwd__lvzx, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            lwd__lvzx = builder.extract_value(lwd__lvzx, 0)
        return builder.load(builder.gep(lwd__lvzx, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        lwd__lvzx, ind, crhd__jkxo = args
        blvqj__wck = builder.gep(lwd__lvzx, [ind])
        builder.store(crhd__jkxo, blvqj__wck)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        sfyc__dzxfi, ind = args
        xdwn__xloi = context.make_helper(builder, arr_ctypes_t, sfyc__dzxfi)
        futym__uueqn = context.make_helper(builder, arr_ctypes_t)
        futym__uueqn.data = builder.gep(xdwn__xloi.data, [ind])
        futym__uueqn.meminfo = xdwn__xloi.meminfo
        fjxpz__afvnc = futym__uueqn._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, fjxpz__afvnc)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    idqj__tkv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not idqj__tkv:
        return 0, 0, 0
    nfnbu__jilpi = getitem_c_arr(arr._index_offsets, item_ind)
    jem__mawh = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    agmjf__gle = jem__mawh - nfnbu__jilpi
    if str_ind >= agmjf__gle:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, nfnbu__jilpi + str_ind)
    data_start += 1
    if nfnbu__jilpi + str_ind == 0:
        data_start = 0
    zhwm__zvddw = getitem_c_arr(arr._data_offsets, nfnbu__jilpi + str_ind + 1)
    gwiiz__sqgti = zhwm__zvddw - data_start
    return 1, data_start, gwiiz__sqgti


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
        tmvd__ljaq = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            nfnbu__jilpi = getitem_c_arr(A._index_offsets, ind)
            jem__mawh = getitem_c_arr(A._index_offsets, ind + 1)
            asjt__qsdy = jem__mawh - nfnbu__jilpi - 1
            vcgyj__mtwi = bodo.libs.str_arr_ext.pre_alloc_string_array(
                asjt__qsdy, -1)
            for vla__deji in range(asjt__qsdy):
                data_start = getitem_c_arr(A._data_offsets, nfnbu__jilpi +
                    vla__deji)
                data_start += 1
                if nfnbu__jilpi + vla__deji == 0:
                    data_start = 0
                zhwm__zvddw = getitem_c_arr(A._data_offsets, nfnbu__jilpi +
                    vla__deji + 1)
                gwiiz__sqgti = zhwm__zvddw - data_start
                blvqj__wck = get_array_ctypes_ptr(A._data, data_start)
                wdh__iiu = bodo.libs.str_arr_ext.decode_utf8(blvqj__wck,
                    gwiiz__sqgti)
                vcgyj__mtwi[vla__deji] = wdh__iiu
            return vcgyj__mtwi
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        vew__ucxc = offset_type.bitwidth // 8

        def _impl(A, ind):
            asjt__qsdy = len(A)
            if asjt__qsdy != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            roix__okac = 0
            hfygn__dba = 0
            for vla__deji in range(asjt__qsdy):
                if ind[vla__deji]:
                    roix__okac += 1
                    nfnbu__jilpi = getitem_c_arr(A._index_offsets, vla__deji)
                    jem__mawh = getitem_c_arr(A._index_offsets, vla__deji + 1)
                    hfygn__dba += jem__mawh - nfnbu__jilpi
            mzrm__eghd = pre_alloc_str_arr_view(roix__okac, hfygn__dba, A._data
                )
            item_ind = 0
            pnn__avbue = 0
            for vla__deji in range(asjt__qsdy):
                if ind[vla__deji]:
                    nfnbu__jilpi = getitem_c_arr(A._index_offsets, vla__deji)
                    jem__mawh = getitem_c_arr(A._index_offsets, vla__deji + 1)
                    ehki__icejr = jem__mawh - nfnbu__jilpi
                    setitem_c_arr(mzrm__eghd._index_offsets, item_ind,
                        pnn__avbue)
                    blvqj__wck = get_c_arr_ptr(A._data_offsets, nfnbu__jilpi)
                    mvw__qrma = get_c_arr_ptr(mzrm__eghd._data_offsets,
                        pnn__avbue)
                    _memcpy(mvw__qrma, blvqj__wck, ehki__icejr, vew__ucxc)
                    idqj__tkv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, vla__deji)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mzrm__eghd.
                        _null_bitmap, item_ind, idqj__tkv)
                    item_ind += 1
                    pnn__avbue += ehki__icejr
            setitem_c_arr(mzrm__eghd._index_offsets, item_ind, pnn__avbue)
            return mzrm__eghd
        return _impl
