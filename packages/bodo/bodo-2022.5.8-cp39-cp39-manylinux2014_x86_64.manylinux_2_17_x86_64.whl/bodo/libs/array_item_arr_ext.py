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
        utgl__ldpzm = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, utgl__ldpzm)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        utgl__ldpzm = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, utgl__ldpzm)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    lwpaa__ojx = builder.module
    zyg__fvvpo = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    txp__yxozo = cgutils.get_or_insert_function(lwpaa__ojx, zyg__fvvpo,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not txp__yxozo.is_declaration:
        return txp__yxozo
    txp__yxozo.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(txp__yxozo.append_basic_block())
    lylhh__rlsx = txp__yxozo.args[0]
    evbw__ghzxo = context.get_value_type(payload_type).as_pointer()
    rgtuj__fdhn = builder.bitcast(lylhh__rlsx, evbw__ghzxo)
    yzcj__rffke = context.make_helper(builder, payload_type, ref=rgtuj__fdhn)
    context.nrt.decref(builder, array_item_type.dtype, yzcj__rffke.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        yzcj__rffke.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        yzcj__rffke.null_bitmap)
    builder.ret_void()
    return txp__yxozo


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    pdsym__rhb = context.get_value_type(payload_type)
    mnw__max = context.get_abi_sizeof(pdsym__rhb)
    swlua__teh = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    ucve__btjda = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, mnw__max), swlua__teh)
    skq__ayy = context.nrt.meminfo_data(builder, ucve__btjda)
    vvvm__spkbu = builder.bitcast(skq__ayy, pdsym__rhb.as_pointer())
    yzcj__rffke = cgutils.create_struct_proxy(payload_type)(context, builder)
    yzcj__rffke.n_arrays = n_arrays
    hlez__oclm = n_elems.type.count
    hfumq__rtr = builder.extract_value(n_elems, 0)
    veix__uaz = cgutils.alloca_once_value(builder, hfumq__rtr)
    tkj__hdtzg = builder.icmp_signed('==', hfumq__rtr, lir.Constant(
        hfumq__rtr.type, -1))
    with builder.if_then(tkj__hdtzg):
        builder.store(n_arrays, veix__uaz)
    n_elems = cgutils.pack_array(builder, [builder.load(veix__uaz)] + [
        builder.extract_value(n_elems, uzlj__hhx) for uzlj__hhx in range(1,
        hlez__oclm)])
    yzcj__rffke.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    idmmf__vth = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    hwm__fegyi = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [idmmf__vth])
    offsets_ptr = hwm__fegyi.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    yzcj__rffke.offsets = hwm__fegyi._getvalue()
    sqyx__yuii = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    ouaef__rkn = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [sqyx__yuii])
    null_bitmap_ptr = ouaef__rkn.data
    yzcj__rffke.null_bitmap = ouaef__rkn._getvalue()
    builder.store(yzcj__rffke._getvalue(), vvvm__spkbu)
    return ucve__btjda, yzcj__rffke.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    yxle__psno, svch__nddtu = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    tnsa__mvg = context.insert_const_string(builder.module, 'pandas')
    bjv__onlqe = c.pyapi.import_module_noblock(tnsa__mvg)
    yuhqq__npj = c.pyapi.object_getattr_string(bjv__onlqe, 'NA')
    qfkd__few = c.context.get_constant(offset_type, 0)
    builder.store(qfkd__few, offsets_ptr)
    jejat__khso = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as ignm__bve:
        rvie__scwnj = ignm__bve.index
        item_ind = builder.load(jejat__khso)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [rvie__scwnj]))
        arr_obj = seq_getitem(builder, context, val, rvie__scwnj)
        set_bitmap_bit(builder, null_bitmap_ptr, rvie__scwnj, 0)
        maz__akqcz = is_na_value(builder, context, arr_obj, yuhqq__npj)
        yatk__zpjs = builder.icmp_unsigned('!=', maz__akqcz, lir.Constant(
            maz__akqcz.type, 1))
        with builder.if_then(yatk__zpjs):
            set_bitmap_bit(builder, null_bitmap_ptr, rvie__scwnj, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), jejat__khso)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(jejat__khso), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(bjv__onlqe)
    c.pyapi.decref(yuhqq__npj)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    eyyne__rxaaf = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if eyyne__rxaaf:
        zyg__fvvpo = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        rimin__pgoh = cgutils.get_or_insert_function(c.builder.module,
            zyg__fvvpo, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(rimin__pgoh,
            [val])])
    else:
        ghkl__qdp = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            ghkl__qdp, uzlj__hhx) for uzlj__hhx in range(1, ghkl__qdp.type.
            count)])
    ucve__btjda, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if eyyne__rxaaf:
        eubx__siv = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        rmcxe__jco = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        zyg__fvvpo = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        txp__yxozo = cgutils.get_or_insert_function(c.builder.module,
            zyg__fvvpo, name='array_item_array_from_sequence')
        c.builder.call(txp__yxozo, [val, c.builder.bitcast(rmcxe__jco, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), eubx__siv)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    wrdru__xqc = c.context.make_helper(c.builder, typ)
    wrdru__xqc.meminfo = ucve__btjda
    xxodd__cnj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wrdru__xqc._getvalue(), is_error=xxodd__cnj)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    wrdru__xqc = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    skq__ayy = context.nrt.meminfo_data(builder, wrdru__xqc.meminfo)
    vvvm__spkbu = builder.bitcast(skq__ayy, context.get_value_type(
        payload_type).as_pointer())
    yzcj__rffke = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(vvvm__spkbu))
    return yzcj__rffke


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    tnsa__mvg = context.insert_const_string(builder.module, 'numpy')
    wpffh__npfib = c.pyapi.import_module_noblock(tnsa__mvg)
    dvxcv__brk = c.pyapi.object_getattr_string(wpffh__npfib, 'object_')
    unsyx__jfl = c.pyapi.long_from_longlong(n_arrays)
    kqn__appfr = c.pyapi.call_method(wpffh__npfib, 'ndarray', (unsyx__jfl,
        dvxcv__brk))
    uoffj__vhq = c.pyapi.object_getattr_string(wpffh__npfib, 'nan')
    jejat__khso = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as ignm__bve:
        rvie__scwnj = ignm__bve.index
        pyarray_setitem(builder, context, kqn__appfr, rvie__scwnj, uoffj__vhq)
        pnf__cea = get_bitmap_bit(builder, null_bitmap_ptr, rvie__scwnj)
        owj__cfbou = builder.icmp_unsigned('!=', pnf__cea, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(owj__cfbou):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(rvie__scwnj, lir.Constant(
                rvie__scwnj.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [rvie__scwnj]))), lir.IntType(64))
            item_ind = builder.load(jejat__khso)
            yxle__psno, cpkoy__jjic = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), jejat__khso)
            arr_obj = c.pyapi.from_native_value(typ.dtype, cpkoy__jjic, c.
                env_manager)
            pyarray_setitem(builder, context, kqn__appfr, rvie__scwnj, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(wpffh__npfib)
    c.pyapi.decref(dvxcv__brk)
    c.pyapi.decref(unsyx__jfl)
    c.pyapi.decref(uoffj__vhq)
    return kqn__appfr


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    yzcj__rffke = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = yzcj__rffke.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), yzcj__rffke.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), yzcj__rffke.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        eubx__siv = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        rmcxe__jco = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        zyg__fvvpo = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        ciaup__jjawy = cgutils.get_or_insert_function(c.builder.module,
            zyg__fvvpo, name='np_array_from_array_item_array')
        arr = c.builder.call(ciaup__jjawy, [yzcj__rffke.n_arrays, c.builder
            .bitcast(rmcxe__jco, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), eubx__siv)])
    else:
        arr = _box_array_item_array_generic(typ, c, yzcj__rffke.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    qgc__gdhh, lkl__ntgtb, wzkqw__lyzqp = args
    etij__xgqtk = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    oecue__rmbm = sig.args[1]
    if not isinstance(oecue__rmbm, types.UniTuple):
        lkl__ntgtb = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for wzkqw__lyzqp in range(etij__xgqtk)])
    elif oecue__rmbm.count < etij__xgqtk:
        lkl__ntgtb = cgutils.pack_array(builder, [builder.extract_value(
            lkl__ntgtb, uzlj__hhx) for uzlj__hhx in range(oecue__rmbm.count
            )] + [lir.Constant(lir.IntType(64), -1) for wzkqw__lyzqp in
            range(etij__xgqtk - oecue__rmbm.count)])
    ucve__btjda, wzkqw__lyzqp, wzkqw__lyzqp, wzkqw__lyzqp = (
        construct_array_item_array(context, builder, array_item_type,
        qgc__gdhh, lkl__ntgtb))
    wrdru__xqc = context.make_helper(builder, array_item_type)
    wrdru__xqc.meminfo = ucve__btjda
    return wrdru__xqc._getvalue()


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
    n_arrays, fbuew__vrdyc, hwm__fegyi, ouaef__rkn = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    pdsym__rhb = context.get_value_type(payload_type)
    mnw__max = context.get_abi_sizeof(pdsym__rhb)
    swlua__teh = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    ucve__btjda = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, mnw__max), swlua__teh)
    skq__ayy = context.nrt.meminfo_data(builder, ucve__btjda)
    vvvm__spkbu = builder.bitcast(skq__ayy, pdsym__rhb.as_pointer())
    yzcj__rffke = cgutils.create_struct_proxy(payload_type)(context, builder)
    yzcj__rffke.n_arrays = n_arrays
    yzcj__rffke.data = fbuew__vrdyc
    yzcj__rffke.offsets = hwm__fegyi
    yzcj__rffke.null_bitmap = ouaef__rkn
    builder.store(yzcj__rffke._getvalue(), vvvm__spkbu)
    context.nrt.incref(builder, signature.args[1], fbuew__vrdyc)
    context.nrt.incref(builder, signature.args[2], hwm__fegyi)
    context.nrt.incref(builder, signature.args[3], ouaef__rkn)
    wrdru__xqc = context.make_helper(builder, array_item_type)
    wrdru__xqc.meminfo = ucve__btjda
    return wrdru__xqc._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    rjpid__htrp = ArrayItemArrayType(data_type)
    sig = rjpid__htrp(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        yzcj__rffke = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yzcj__rffke.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        yzcj__rffke = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        rmcxe__jco = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, yzcj__rffke.offsets).data
        hwm__fegyi = builder.bitcast(rmcxe__jco, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(hwm__fegyi, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        yzcj__rffke = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yzcj__rffke.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        yzcj__rffke = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yzcj__rffke.null_bitmap)
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
        yzcj__rffke = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return yzcj__rffke.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, kxwr__jam = args
        wrdru__xqc = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        skq__ayy = context.nrt.meminfo_data(builder, wrdru__xqc.meminfo)
        vvvm__spkbu = builder.bitcast(skq__ayy, context.get_value_type(
            payload_type).as_pointer())
        yzcj__rffke = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(vvvm__spkbu))
        context.nrt.decref(builder, data_typ, yzcj__rffke.data)
        yzcj__rffke.data = kxwr__jam
        context.nrt.incref(builder, data_typ, kxwr__jam)
        builder.store(yzcj__rffke._getvalue(), vvvm__spkbu)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    fbuew__vrdyc = get_data(arr)
    bgfo__ovjlk = len(fbuew__vrdyc)
    if bgfo__ovjlk < new_size:
        tutsb__azri = max(2 * bgfo__ovjlk, new_size)
        kxwr__jam = bodo.libs.array_kernels.resize_and_copy(fbuew__vrdyc,
            old_size, tutsb__azri)
        replace_data_arr(arr, kxwr__jam)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    fbuew__vrdyc = get_data(arr)
    hwm__fegyi = get_offsets(arr)
    ddm__fpnh = len(fbuew__vrdyc)
    mok__dcy = hwm__fegyi[-1]
    if ddm__fpnh != mok__dcy:
        kxwr__jam = bodo.libs.array_kernels.resize_and_copy(fbuew__vrdyc,
            mok__dcy, mok__dcy)
        replace_data_arr(arr, kxwr__jam)


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
            hwm__fegyi = get_offsets(arr)
            fbuew__vrdyc = get_data(arr)
            hldl__mig = hwm__fegyi[ind]
            zwyjb__eaw = hwm__fegyi[ind + 1]
            return fbuew__vrdyc[hldl__mig:zwyjb__eaw]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        wtmaa__zgc = arr.dtype

        def impl_bool(arr, ind):
            qzhk__pmh = len(arr)
            if qzhk__pmh != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ouaef__rkn = get_null_bitmap(arr)
            n_arrays = 0
            uak__eahtn = init_nested_counts(wtmaa__zgc)
            for uzlj__hhx in range(qzhk__pmh):
                if ind[uzlj__hhx]:
                    n_arrays += 1
                    wbcyg__cdfa = arr[uzlj__hhx]
                    uak__eahtn = add_nested_counts(uak__eahtn, wbcyg__cdfa)
            kqn__appfr = pre_alloc_array_item_array(n_arrays, uak__eahtn,
                wtmaa__zgc)
            jcjkk__ixnvi = get_null_bitmap(kqn__appfr)
            uknlm__qjx = 0
            for vlb__ywyy in range(qzhk__pmh):
                if ind[vlb__ywyy]:
                    kqn__appfr[uknlm__qjx] = arr[vlb__ywyy]
                    oja__hxox = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ouaef__rkn, vlb__ywyy)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jcjkk__ixnvi,
                        uknlm__qjx, oja__hxox)
                    uknlm__qjx += 1
            return kqn__appfr
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        wtmaa__zgc = arr.dtype

        def impl_int(arr, ind):
            ouaef__rkn = get_null_bitmap(arr)
            qzhk__pmh = len(ind)
            n_arrays = qzhk__pmh
            uak__eahtn = init_nested_counts(wtmaa__zgc)
            for fidnd__ahngl in range(qzhk__pmh):
                uzlj__hhx = ind[fidnd__ahngl]
                wbcyg__cdfa = arr[uzlj__hhx]
                uak__eahtn = add_nested_counts(uak__eahtn, wbcyg__cdfa)
            kqn__appfr = pre_alloc_array_item_array(n_arrays, uak__eahtn,
                wtmaa__zgc)
            jcjkk__ixnvi = get_null_bitmap(kqn__appfr)
            for vdpm__drfb in range(qzhk__pmh):
                vlb__ywyy = ind[vdpm__drfb]
                kqn__appfr[vdpm__drfb] = arr[vlb__ywyy]
                oja__hxox = bodo.libs.int_arr_ext.get_bit_bitmap_arr(ouaef__rkn
                    , vlb__ywyy)
                bodo.libs.int_arr_ext.set_bit_to_arr(jcjkk__ixnvi,
                    vdpm__drfb, oja__hxox)
            return kqn__appfr
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            qzhk__pmh = len(arr)
            mzhhg__vfo = numba.cpython.unicode._normalize_slice(ind, qzhk__pmh)
            imge__zpqhg = np.arange(mzhhg__vfo.start, mzhhg__vfo.stop,
                mzhhg__vfo.step)
            return arr[imge__zpqhg]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            hwm__fegyi = get_offsets(A)
            ouaef__rkn = get_null_bitmap(A)
            if idx == 0:
                hwm__fegyi[0] = 0
            n_items = len(val)
            uhdw__dsx = hwm__fegyi[idx] + n_items
            ensure_data_capacity(A, hwm__fegyi[idx], uhdw__dsx)
            fbuew__vrdyc = get_data(A)
            hwm__fegyi[idx + 1] = hwm__fegyi[idx] + n_items
            fbuew__vrdyc[hwm__fegyi[idx]:hwm__fegyi[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(ouaef__rkn, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            mzhhg__vfo = numba.cpython.unicode._normalize_slice(idx, len(A))
            for uzlj__hhx in range(mzhhg__vfo.start, mzhhg__vfo.stop,
                mzhhg__vfo.step):
                A[uzlj__hhx] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            hwm__fegyi = get_offsets(A)
            ouaef__rkn = get_null_bitmap(A)
            bzan__phqe = get_offsets(val)
            umzhz__bhqr = get_data(val)
            dhfot__lvhk = get_null_bitmap(val)
            qzhk__pmh = len(A)
            mzhhg__vfo = numba.cpython.unicode._normalize_slice(idx, qzhk__pmh)
            rkc__ydm, qakd__dfgv = mzhhg__vfo.start, mzhhg__vfo.stop
            assert mzhhg__vfo.step == 1
            if rkc__ydm == 0:
                hwm__fegyi[rkc__ydm] = 0
            bspuf__leiub = hwm__fegyi[rkc__ydm]
            uhdw__dsx = bspuf__leiub + len(umzhz__bhqr)
            ensure_data_capacity(A, bspuf__leiub, uhdw__dsx)
            fbuew__vrdyc = get_data(A)
            fbuew__vrdyc[bspuf__leiub:bspuf__leiub + len(umzhz__bhqr)
                ] = umzhz__bhqr
            hwm__fegyi[rkc__ydm:qakd__dfgv + 1] = bzan__phqe + bspuf__leiub
            ypyn__ths = 0
            for uzlj__hhx in range(rkc__ydm, qakd__dfgv):
                oja__hxox = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    dhfot__lvhk, ypyn__ths)
                bodo.libs.int_arr_ext.set_bit_to_arr(ouaef__rkn, uzlj__hhx,
                    oja__hxox)
                ypyn__ths += 1
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
