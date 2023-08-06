"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xxqoo__kcy = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, xxqoo__kcy)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        xxqoo__kcy = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, xxqoo__kcy)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    dqlj__ufrh = builder.module
    ckxs__kwt = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    hkb__lvyh = cgutils.get_or_insert_function(dqlj__ufrh, ckxs__kwt, name=
        '.dtor.array_item.{}'.format(array_item_type.dtype))
    if not hkb__lvyh.is_declaration:
        return hkb__lvyh
    hkb__lvyh.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(hkb__lvyh.append_basic_block())
    fyq__mvn = hkb__lvyh.args[0]
    fgl__ankwr = context.get_value_type(payload_type).as_pointer()
    kul__vmj = builder.bitcast(fyq__mvn, fgl__ankwr)
    njl__jqek = context.make_helper(builder, payload_type, ref=kul__vmj)
    context.nrt.decref(builder, array_item_type.dtype, njl__jqek.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), njl__jqek
        .offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), njl__jqek
        .null_bitmap)
    builder.ret_void()
    return hkb__lvyh


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    zus__hbze = context.get_value_type(payload_type)
    zvu__pndle = context.get_abi_sizeof(zus__hbze)
    nbby__kuvgl = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    mvrd__pztw = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zvu__pndle), nbby__kuvgl)
    lfnak__uhgi = context.nrt.meminfo_data(builder, mvrd__pztw)
    zqsos__tmrq = builder.bitcast(lfnak__uhgi, zus__hbze.as_pointer())
    njl__jqek = cgutils.create_struct_proxy(payload_type)(context, builder)
    njl__jqek.n_arrays = n_arrays
    lhfzs__aqui = n_elems.type.count
    mhps__houro = builder.extract_value(n_elems, 0)
    ecty__pri = cgutils.alloca_once_value(builder, mhps__houro)
    gvvje__tvar = builder.icmp_signed('==', mhps__houro, lir.Constant(
        mhps__houro.type, -1))
    with builder.if_then(gvvje__tvar):
        builder.store(n_arrays, ecty__pri)
    n_elems = cgutils.pack_array(builder, [builder.load(ecty__pri)] + [
        builder.extract_value(n_elems, mhro__vncl) for mhro__vncl in range(
        1, lhfzs__aqui)])
    njl__jqek.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    ubog__ikneq = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    brf__ccgd = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [ubog__ikneq])
    offsets_ptr = brf__ccgd.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    njl__jqek.offsets = brf__ccgd._getvalue()
    opsr__ynjca = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    zqn__dazuy = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [opsr__ynjca])
    null_bitmap_ptr = zqn__dazuy.data
    njl__jqek.null_bitmap = zqn__dazuy._getvalue()
    builder.store(njl__jqek._getvalue(), zqsos__tmrq)
    return mvrd__pztw, njl__jqek.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    khayb__qoge, awqmx__tqk = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    pdzcj__ryokb = context.insert_const_string(builder.module, 'pandas')
    tovuh__rlina = c.pyapi.import_module_noblock(pdzcj__ryokb)
    ypi__qsgzt = c.pyapi.object_getattr_string(tovuh__rlina, 'NA')
    knalq__qsc = c.context.get_constant(offset_type, 0)
    builder.store(knalq__qsc, offsets_ptr)
    vlmp__kxupp = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as nowdb__wsf:
        mhh__qyc = nowdb__wsf.index
        item_ind = builder.load(vlmp__kxupp)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [mhh__qyc]))
        arr_obj = seq_getitem(builder, context, val, mhh__qyc)
        set_bitmap_bit(builder, null_bitmap_ptr, mhh__qyc, 0)
        vltyd__mbrqp = is_na_value(builder, context, arr_obj, ypi__qsgzt)
        uoqg__rnuyu = builder.icmp_unsigned('!=', vltyd__mbrqp, lir.
            Constant(vltyd__mbrqp.type, 1))
        with builder.if_then(uoqg__rnuyu):
            set_bitmap_bit(builder, null_bitmap_ptr, mhh__qyc, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), vlmp__kxupp)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(vlmp__kxupp), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(tovuh__rlina)
    c.pyapi.decref(ypi__qsgzt)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    tbh__gjlw = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if tbh__gjlw:
        ckxs__kwt = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        pvmf__iaiwm = cgutils.get_or_insert_function(c.builder.module,
            ckxs__kwt, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(pvmf__iaiwm,
            [val])])
    else:
        qukqo__adq = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            qukqo__adq, mhro__vncl) for mhro__vncl in range(1, qukqo__adq.
            type.count)])
    mvrd__pztw, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if tbh__gjlw:
        fctv__thxx = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        awpvm__kubho = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        ckxs__kwt = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        hkb__lvyh = cgutils.get_or_insert_function(c.builder.module,
            ckxs__kwt, name='array_item_array_from_sequence')
        c.builder.call(hkb__lvyh, [val, c.builder.bitcast(awpvm__kubho, lir
            .IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), fctv__thxx)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    xtbl__wsjck = c.context.make_helper(c.builder, typ)
    xtbl__wsjck.meminfo = mvrd__pztw
    gzr__rgwn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xtbl__wsjck._getvalue(), is_error=gzr__rgwn)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    xtbl__wsjck = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    lfnak__uhgi = context.nrt.meminfo_data(builder, xtbl__wsjck.meminfo)
    zqsos__tmrq = builder.bitcast(lfnak__uhgi, context.get_value_type(
        payload_type).as_pointer())
    njl__jqek = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(zqsos__tmrq))
    return njl__jqek


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    pdzcj__ryokb = context.insert_const_string(builder.module, 'numpy')
    vscg__ngr = c.pyapi.import_module_noblock(pdzcj__ryokb)
    iohs__ulhi = c.pyapi.object_getattr_string(vscg__ngr, 'object_')
    fgigh__xlfsh = c.pyapi.long_from_longlong(n_arrays)
    jbcnb__cjlrh = c.pyapi.call_method(vscg__ngr, 'ndarray', (fgigh__xlfsh,
        iohs__ulhi))
    aclz__zcs = c.pyapi.object_getattr_string(vscg__ngr, 'nan')
    vlmp__kxupp = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as nowdb__wsf:
        mhh__qyc = nowdb__wsf.index
        pyarray_setitem(builder, context, jbcnb__cjlrh, mhh__qyc, aclz__zcs)
        ncl__lfy = get_bitmap_bit(builder, null_bitmap_ptr, mhh__qyc)
        qulc__fnsj = builder.icmp_unsigned('!=', ncl__lfy, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(qulc__fnsj):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(mhh__qyc, lir.Constant(mhh__qyc.
                type, 1))])), builder.load(builder.gep(offsets_ptr, [
                mhh__qyc]))), lir.IntType(64))
            item_ind = builder.load(vlmp__kxupp)
            khayb__qoge, qpse__zeaf = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), vlmp__kxupp)
            arr_obj = c.pyapi.from_native_value(typ.dtype, qpse__zeaf, c.
                env_manager)
            pyarray_setitem(builder, context, jbcnb__cjlrh, mhh__qyc, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(vscg__ngr)
    c.pyapi.decref(iohs__ulhi)
    c.pyapi.decref(fgigh__xlfsh)
    c.pyapi.decref(aclz__zcs)
    return jbcnb__cjlrh


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    njl__jqek = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = njl__jqek.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), njl__jqek.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), njl__jqek.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        fctv__thxx = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        awpvm__kubho = c.context.make_helper(c.builder, typ.dtype, data_arr
            ).data
        ckxs__kwt = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        ecli__uqjb = cgutils.get_or_insert_function(c.builder.module,
            ckxs__kwt, name='np_array_from_array_item_array')
        arr = c.builder.call(ecli__uqjb, [njl__jqek.n_arrays, c.builder.
            bitcast(awpvm__kubho, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), fctv__thxx)])
    else:
        arr = _box_array_item_array_generic(typ, c, njl__jqek.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    htmz__khdn, yzi__drdpa, rneb__qzgj = args
    svf__zyhef = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    uoptc__ows = sig.args[1]
    if not isinstance(uoptc__ows, types.UniTuple):
        yzi__drdpa = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for rneb__qzgj in range(svf__zyhef)])
    elif uoptc__ows.count < svf__zyhef:
        yzi__drdpa = cgutils.pack_array(builder, [builder.extract_value(
            yzi__drdpa, mhro__vncl) for mhro__vncl in range(uoptc__ows.
            count)] + [lir.Constant(lir.IntType(64), -1) for rneb__qzgj in
            range(svf__zyhef - uoptc__ows.count)])
    mvrd__pztw, rneb__qzgj, rneb__qzgj, rneb__qzgj = (
        construct_array_item_array(context, builder, array_item_type,
        htmz__khdn, yzi__drdpa))
    xtbl__wsjck = context.make_helper(builder, array_item_type)
    xtbl__wsjck.meminfo = mvrd__pztw
    return xtbl__wsjck._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, cxox__elo, brf__ccgd, zqn__dazuy = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    zus__hbze = context.get_value_type(payload_type)
    zvu__pndle = context.get_abi_sizeof(zus__hbze)
    nbby__kuvgl = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    mvrd__pztw = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zvu__pndle), nbby__kuvgl)
    lfnak__uhgi = context.nrt.meminfo_data(builder, mvrd__pztw)
    zqsos__tmrq = builder.bitcast(lfnak__uhgi, zus__hbze.as_pointer())
    njl__jqek = cgutils.create_struct_proxy(payload_type)(context, builder)
    njl__jqek.n_arrays = n_arrays
    njl__jqek.data = cxox__elo
    njl__jqek.offsets = brf__ccgd
    njl__jqek.null_bitmap = zqn__dazuy
    builder.store(njl__jqek._getvalue(), zqsos__tmrq)
    context.nrt.incref(builder, signature.args[1], cxox__elo)
    context.nrt.incref(builder, signature.args[2], brf__ccgd)
    context.nrt.incref(builder, signature.args[3], zqn__dazuy)
    xtbl__wsjck = context.make_helper(builder, array_item_type)
    xtbl__wsjck.meminfo = mvrd__pztw
    return xtbl__wsjck._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    wtoqp__uprp = ArrayItemArrayType(data_type)
    sig = wtoqp__uprp(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        njl__jqek = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            njl__jqek.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        njl__jqek = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        awpvm__kubho = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, njl__jqek.offsets).data
        brf__ccgd = builder.bitcast(awpvm__kubho, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(brf__ccgd, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        njl__jqek = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            njl__jqek.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        njl__jqek = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            njl__jqek.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        njl__jqek = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return njl__jqek.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, pduua__ffgaq = args
        xtbl__wsjck = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        lfnak__uhgi = context.nrt.meminfo_data(builder, xtbl__wsjck.meminfo)
        zqsos__tmrq = builder.bitcast(lfnak__uhgi, context.get_value_type(
            payload_type).as_pointer())
        njl__jqek = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(zqsos__tmrq))
        context.nrt.decref(builder, data_typ, njl__jqek.data)
        njl__jqek.data = pduua__ffgaq
        context.nrt.incref(builder, data_typ, pduua__ffgaq)
        builder.store(njl__jqek._getvalue(), zqsos__tmrq)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    cxox__elo = get_data(arr)
    hkiyh__kaypo = len(cxox__elo)
    if hkiyh__kaypo < new_size:
        garjy__gswc = max(2 * hkiyh__kaypo, new_size)
        pduua__ffgaq = bodo.libs.array_kernels.resize_and_copy(cxox__elo,
            old_size, garjy__gswc)
        replace_data_arr(arr, pduua__ffgaq)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    cxox__elo = get_data(arr)
    brf__ccgd = get_offsets(arr)
    jpdtb__gttft = len(cxox__elo)
    xkm__qqy = brf__ccgd[-1]
    if jpdtb__gttft != xkm__qqy:
        pduua__ffgaq = bodo.libs.array_kernels.resize_and_copy(cxox__elo,
            xkm__qqy, xkm__qqy)
        replace_data_arr(arr, pduua__ffgaq)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            brf__ccgd = get_offsets(arr)
            cxox__elo = get_data(arr)
            fcqc__ehm = brf__ccgd[ind]
            wkav__gng = brf__ccgd[ind + 1]
            return cxox__elo[fcqc__ehm:wkav__gng]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        oxsmw__ilfu = arr.dtype

        def impl_bool(arr, ind):
            lyun__jgay = len(arr)
            if lyun__jgay != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            zqn__dazuy = get_null_bitmap(arr)
            n_arrays = 0
            fiyr__szjmg = init_nested_counts(oxsmw__ilfu)
            for mhro__vncl in range(lyun__jgay):
                if ind[mhro__vncl]:
                    n_arrays += 1
                    yukgh__ydltl = arr[mhro__vncl]
                    fiyr__szjmg = add_nested_counts(fiyr__szjmg, yukgh__ydltl)
            jbcnb__cjlrh = pre_alloc_array_item_array(n_arrays, fiyr__szjmg,
                oxsmw__ilfu)
            zzkhf__whpyl = get_null_bitmap(jbcnb__cjlrh)
            ure__zwohg = 0
            for zynkc__cvdf in range(lyun__jgay):
                if ind[zynkc__cvdf]:
                    jbcnb__cjlrh[ure__zwohg] = arr[zynkc__cvdf]
                    cfjy__yggki = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        zqn__dazuy, zynkc__cvdf)
                    bodo.libs.int_arr_ext.set_bit_to_arr(zzkhf__whpyl,
                        ure__zwohg, cfjy__yggki)
                    ure__zwohg += 1
            return jbcnb__cjlrh
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        oxsmw__ilfu = arr.dtype

        def impl_int(arr, ind):
            zqn__dazuy = get_null_bitmap(arr)
            lyun__jgay = len(ind)
            n_arrays = lyun__jgay
            fiyr__szjmg = init_nested_counts(oxsmw__ilfu)
            for cye__kkt in range(lyun__jgay):
                mhro__vncl = ind[cye__kkt]
                yukgh__ydltl = arr[mhro__vncl]
                fiyr__szjmg = add_nested_counts(fiyr__szjmg, yukgh__ydltl)
            jbcnb__cjlrh = pre_alloc_array_item_array(n_arrays, fiyr__szjmg,
                oxsmw__ilfu)
            zzkhf__whpyl = get_null_bitmap(jbcnb__cjlrh)
            for bxu__ajwks in range(lyun__jgay):
                zynkc__cvdf = ind[bxu__ajwks]
                jbcnb__cjlrh[bxu__ajwks] = arr[zynkc__cvdf]
                cfjy__yggki = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    zqn__dazuy, zynkc__cvdf)
                bodo.libs.int_arr_ext.set_bit_to_arr(zzkhf__whpyl,
                    bxu__ajwks, cfjy__yggki)
            return jbcnb__cjlrh
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            lyun__jgay = len(arr)
            mtjyo__ykkq = numba.cpython.unicode._normalize_slice(ind,
                lyun__jgay)
            nrm__hsm = np.arange(mtjyo__ykkq.start, mtjyo__ykkq.stop,
                mtjyo__ykkq.step)
            return arr[nrm__hsm]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            brf__ccgd = get_offsets(A)
            zqn__dazuy = get_null_bitmap(A)
            if idx == 0:
                brf__ccgd[0] = 0
            n_items = len(val)
            cqex__qtjo = brf__ccgd[idx] + n_items
            ensure_data_capacity(A, brf__ccgd[idx], cqex__qtjo)
            cxox__elo = get_data(A)
            brf__ccgd[idx + 1] = brf__ccgd[idx] + n_items
            cxox__elo[brf__ccgd[idx]:brf__ccgd[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(zqn__dazuy, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            mtjyo__ykkq = numba.cpython.unicode._normalize_slice(idx, len(A))
            for mhro__vncl in range(mtjyo__ykkq.start, mtjyo__ykkq.stop,
                mtjyo__ykkq.step):
                A[mhro__vncl] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            brf__ccgd = get_offsets(A)
            zqn__dazuy = get_null_bitmap(A)
            mezhh__yynr = get_offsets(val)
            vsk__hupb = get_data(val)
            hrxj__juoy = get_null_bitmap(val)
            lyun__jgay = len(A)
            mtjyo__ykkq = numba.cpython.unicode._normalize_slice(idx,
                lyun__jgay)
            pslr__qink, ahulp__kay = mtjyo__ykkq.start, mtjyo__ykkq.stop
            assert mtjyo__ykkq.step == 1
            if pslr__qink == 0:
                brf__ccgd[pslr__qink] = 0
            duhau__iuee = brf__ccgd[pslr__qink]
            cqex__qtjo = duhau__iuee + len(vsk__hupb)
            ensure_data_capacity(A, duhau__iuee, cqex__qtjo)
            cxox__elo = get_data(A)
            cxox__elo[duhau__iuee:duhau__iuee + len(vsk__hupb)] = vsk__hupb
            brf__ccgd[pslr__qink:ahulp__kay + 1] = mezhh__yynr + duhau__iuee
            aadjd__pxy = 0
            for mhro__vncl in range(pslr__qink, ahulp__kay):
                cfjy__yggki = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    hrxj__juoy, aadjd__pxy)
                bodo.libs.int_arr_ext.set_bit_to_arr(zqn__dazuy, mhro__vncl,
                    cfjy__yggki)
                aadjd__pxy += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
