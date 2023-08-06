"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(qou__smxv, False) for qou__smxv in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(qou__smxv,
                str) for qou__smxv in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(xwbi__iccl.dtype for xwbi__iccl in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(qou__smxv) for qou__smxv in d.keys())
        data = tuple(dtype_to_array_type(xwbi__iccl) for xwbi__iccl in d.
            values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(qou__smxv, False) for qou__smxv in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xhpm__tat = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, xhpm__tat)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        xhpm__tat = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, xhpm__tat)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    ydmc__erg = builder.module
    dlrx__nqum = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    jzvz__xnsd = cgutils.get_or_insert_function(ydmc__erg, dlrx__nqum, name
        ='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not jzvz__xnsd.is_declaration:
        return jzvz__xnsd
    jzvz__xnsd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(jzvz__xnsd.append_basic_block())
    tzosg__kbwcz = jzvz__xnsd.args[0]
    dbl__yidmy = context.get_value_type(payload_type).as_pointer()
    tximt__gqj = builder.bitcast(tzosg__kbwcz, dbl__yidmy)
    zvhp__jmq = context.make_helper(builder, payload_type, ref=tximt__gqj)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), zvhp__jmq.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), zvhp__jmq
        .null_bitmap)
    builder.ret_void()
    return jzvz__xnsd


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    icho__okbb = context.get_value_type(payload_type)
    ecwv__vti = context.get_abi_sizeof(icho__okbb)
    hweb__zlk = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    ymc__wzyfm = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ecwv__vti), hweb__zlk)
    wnfem__wsi = context.nrt.meminfo_data(builder, ymc__wzyfm)
    stdp__vxdrh = builder.bitcast(wnfem__wsi, icho__okbb.as_pointer())
    zvhp__jmq = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    cee__gtae = 0
    for arr_typ in struct_arr_type.data:
        hyeej__hymzm = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype
            )
        shu__uee = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(cee__gtae, cee__gtae +
            hyeej__hymzm)])
        arr = gen_allocate_array(context, builder, arr_typ, shu__uee, c)
        arrs.append(arr)
        cee__gtae += hyeej__hymzm
    zvhp__jmq.data = cgutils.pack_array(builder, arrs) if types.is_homogeneous(
        *struct_arr_type.data) else cgutils.pack_struct(builder, arrs)
    pkg__imct = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    bhuz__xgyel = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [pkg__imct])
    null_bitmap_ptr = bhuz__xgyel.data
    zvhp__jmq.null_bitmap = bhuz__xgyel._getvalue()
    builder.store(zvhp__jmq._getvalue(), stdp__vxdrh)
    return ymc__wzyfm, zvhp__jmq.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    uju__msib = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        wwsme__efii = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            wwsme__efii)
        uju__msib.append(arr.data)
    mnrbj__ixv = cgutils.pack_array(c.builder, uju__msib
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, uju__msib)
    mro__iqwj = cgutils.alloca_once_value(c.builder, mnrbj__ixv)
    bwf__dkdxr = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(qou__smxv.dtype)) for qou__smxv in data_typ]
    utz__lyjaj = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, bwf__dkdxr))
    jpc__gqfge = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, qou__smxv) for qou__smxv in
        names])
    kdet__yic = cgutils.alloca_once_value(c.builder, jpc__gqfge)
    return mro__iqwj, utz__lyjaj, kdet__yic


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    gwrix__fwo = all(isinstance(xwbi__iccl, types.Array) and xwbi__iccl.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for xwbi__iccl in typ.data)
    if gwrix__fwo:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        ztcjf__odb = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            ztcjf__odb, i) for i in range(1, ztcjf__odb.type.count)], lir.
            IntType(64))
    ymc__wzyfm, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if gwrix__fwo:
        mro__iqwj, utz__lyjaj, kdet__yic = _get_C_API_ptrs(c, data_tup, typ
            .data, typ.names)
        dlrx__nqum = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        jzvz__xnsd = cgutils.get_or_insert_function(c.builder.module,
            dlrx__nqum, name='struct_array_from_sequence')
        c.builder.call(jzvz__xnsd, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(mro__iqwj, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(utz__lyjaj,
            lir.IntType(8).as_pointer()), c.builder.bitcast(kdet__yic, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    zgdo__wntwq = c.context.make_helper(c.builder, typ)
    zgdo__wntwq.meminfo = ymc__wzyfm
    rva__gyvd = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zgdo__wntwq._getvalue(), is_error=rva__gyvd)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    cmj__mab = context.insert_const_string(builder.module, 'pandas')
    qncnl__hhmu = c.pyapi.import_module_noblock(cmj__mab)
    ecx__czwy = c.pyapi.object_getattr_string(qncnl__hhmu, 'NA')
    with cgutils.for_range(builder, n_structs) as slkox__blthp:
        lqo__jfqs = slkox__blthp.index
        xpd__srxs = seq_getitem(builder, context, val, lqo__jfqs)
        set_bitmap_bit(builder, null_bitmap_ptr, lqo__jfqs, 0)
        for dgcdn__lyyc in range(len(typ.data)):
            arr_typ = typ.data[dgcdn__lyyc]
            data_arr = builder.extract_value(data_tup, dgcdn__lyyc)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            wdyk__lmyt, roba__wmnt = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, lqo__jfqs])
        kjf__biqf = is_na_value(builder, context, xpd__srxs, ecx__czwy)
        irpl__slho = builder.icmp_unsigned('!=', kjf__biqf, lir.Constant(
            kjf__biqf.type, 1))
        with builder.if_then(irpl__slho):
            set_bitmap_bit(builder, null_bitmap_ptr, lqo__jfqs, 1)
            for dgcdn__lyyc in range(len(typ.data)):
                arr_typ = typ.data[dgcdn__lyyc]
                if is_tuple_array:
                    scf__rdq = c.pyapi.tuple_getitem(xpd__srxs, dgcdn__lyyc)
                else:
                    scf__rdq = c.pyapi.dict_getitem_string(xpd__srxs, typ.
                        names[dgcdn__lyyc])
                kjf__biqf = is_na_value(builder, context, scf__rdq, ecx__czwy)
                irpl__slho = builder.icmp_unsigned('!=', kjf__biqf, lir.
                    Constant(kjf__biqf.type, 1))
                with builder.if_then(irpl__slho):
                    scf__rdq = to_arr_obj_if_list_obj(c, context, builder,
                        scf__rdq, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype, scf__rdq
                        ).value
                    data_arr = builder.extract_value(data_tup, dgcdn__lyyc)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    wdyk__lmyt, roba__wmnt = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, lqo__jfqs, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(xpd__srxs)
    c.pyapi.decref(qncnl__hhmu)
    c.pyapi.decref(ecx__czwy)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    zgdo__wntwq = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    wnfem__wsi = context.nrt.meminfo_data(builder, zgdo__wntwq.meminfo)
    stdp__vxdrh = builder.bitcast(wnfem__wsi, context.get_value_type(
        payload_type).as_pointer())
    zvhp__jmq = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(stdp__vxdrh))
    return zvhp__jmq


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    zvhp__jmq = _get_struct_arr_payload(c.context, c.builder, typ, val)
    wdyk__lmyt, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), zvhp__jmq.null_bitmap).data
    gwrix__fwo = all(isinstance(xwbi__iccl, types.Array) and xwbi__iccl.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for xwbi__iccl in typ.data)
    if gwrix__fwo:
        mro__iqwj, utz__lyjaj, kdet__yic = _get_C_API_ptrs(c, zvhp__jmq.
            data, typ.data, typ.names)
        dlrx__nqum = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        wfk__uctf = cgutils.get_or_insert_function(c.builder.module,
            dlrx__nqum, name='np_array_from_struct_array')
        arr = c.builder.call(wfk__uctf, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(mro__iqwj, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            utz__lyjaj, lir.IntType(8).as_pointer()), c.builder.bitcast(
            kdet__yic, lir.IntType(8).as_pointer()), c.context.get_constant
            (types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, zvhp__jmq.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    cmj__mab = context.insert_const_string(builder.module, 'numpy')
    lsnx__ynn = c.pyapi.import_module_noblock(cmj__mab)
    goatw__ismk = c.pyapi.object_getattr_string(lsnx__ynn, 'object_')
    ljavb__jqsck = c.pyapi.long_from_longlong(length)
    uljba__vydqd = c.pyapi.call_method(lsnx__ynn, 'ndarray', (ljavb__jqsck,
        goatw__ismk))
    phtc__hmi = c.pyapi.object_getattr_string(lsnx__ynn, 'nan')
    with cgutils.for_range(builder, length) as slkox__blthp:
        lqo__jfqs = slkox__blthp.index
        pyarray_setitem(builder, context, uljba__vydqd, lqo__jfqs, phtc__hmi)
        zdsb__cjju = get_bitmap_bit(builder, null_bitmap_ptr, lqo__jfqs)
        zcqf__coouz = builder.icmp_unsigned('!=', zdsb__cjju, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(zcqf__coouz):
            if is_tuple_array:
                xpd__srxs = c.pyapi.tuple_new(len(typ.data))
            else:
                xpd__srxs = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(phtc__hmi)
                    c.pyapi.tuple_setitem(xpd__srxs, i, phtc__hmi)
                else:
                    c.pyapi.dict_setitem_string(xpd__srxs, typ.names[i],
                        phtc__hmi)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                wdyk__lmyt, vuv__zkye = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, lqo__jfqs])
                with builder.if_then(vuv__zkye):
                    wdyk__lmyt, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, lqo__jfqs])
                    dwh__uvzi = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(xpd__srxs, i, dwh__uvzi)
                    else:
                        c.pyapi.dict_setitem_string(xpd__srxs, typ.names[i],
                            dwh__uvzi)
                        c.pyapi.decref(dwh__uvzi)
            pyarray_setitem(builder, context, uljba__vydqd, lqo__jfqs,
                xpd__srxs)
            c.pyapi.decref(xpd__srxs)
    c.pyapi.decref(lsnx__ynn)
    c.pyapi.decref(goatw__ismk)
    c.pyapi.decref(ljavb__jqsck)
    c.pyapi.decref(phtc__hmi)
    return uljba__vydqd


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    wkhag__cci = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if wkhag__cci == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for neiap__lvj in range(wkhag__cci)])
    elif nested_counts_type.count < wkhag__cci:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for neiap__lvj in range(
            wkhag__cci - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(xwbi__iccl) for xwbi__iccl in
            names_typ.types)
    ase__hftp = tuple(xwbi__iccl.instance_type for xwbi__iccl in dtypes_typ
        .types)
    struct_arr_type = StructArrayType(ase__hftp, names)

    def codegen(context, builder, sig, args):
        mge__ezgur, nested_counts, neiap__lvj, neiap__lvj = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        ymc__wzyfm, neiap__lvj, neiap__lvj = construct_struct_array(context,
            builder, struct_arr_type, mge__ezgur, nested_counts)
        zgdo__wntwq = context.make_helper(builder, struct_arr_type)
        zgdo__wntwq.meminfo = ymc__wzyfm
        return zgdo__wntwq._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(qou__smxv, str) for
            qou__smxv in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xhpm__tat = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, xhpm__tat)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        xhpm__tat = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, xhpm__tat)


def define_struct_dtor(context, builder, struct_type, payload_type):
    ydmc__erg = builder.module
    dlrx__nqum = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    jzvz__xnsd = cgutils.get_or_insert_function(ydmc__erg, dlrx__nqum, name
        ='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not jzvz__xnsd.is_declaration:
        return jzvz__xnsd
    jzvz__xnsd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(jzvz__xnsd.append_basic_block())
    tzosg__kbwcz = jzvz__xnsd.args[0]
    dbl__yidmy = context.get_value_type(payload_type).as_pointer()
    tximt__gqj = builder.bitcast(tzosg__kbwcz, dbl__yidmy)
    zvhp__jmq = context.make_helper(builder, payload_type, ref=tximt__gqj)
    for i in range(len(struct_type.data)):
        snokj__wpb = builder.extract_value(zvhp__jmq.null_bitmap, i)
        zcqf__coouz = builder.icmp_unsigned('==', snokj__wpb, lir.Constant(
            snokj__wpb.type, 1))
        with builder.if_then(zcqf__coouz):
            val = builder.extract_value(zvhp__jmq.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return jzvz__xnsd


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    wnfem__wsi = context.nrt.meminfo_data(builder, struct.meminfo)
    stdp__vxdrh = builder.bitcast(wnfem__wsi, context.get_value_type(
        payload_type).as_pointer())
    zvhp__jmq = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(stdp__vxdrh))
    return zvhp__jmq, stdp__vxdrh


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    cmj__mab = context.insert_const_string(builder.module, 'pandas')
    qncnl__hhmu = c.pyapi.import_module_noblock(cmj__mab)
    ecx__czwy = c.pyapi.object_getattr_string(qncnl__hhmu, 'NA')
    szbvw__nltv = []
    nulls = []
    for i, xwbi__iccl in enumerate(typ.data):
        dwh__uvzi = c.pyapi.dict_getitem_string(val, typ.names[i])
        izdgq__sxfd = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        ces__fdwt = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(xwbi__iccl)))
        kjf__biqf = is_na_value(builder, context, dwh__uvzi, ecx__czwy)
        zcqf__coouz = builder.icmp_unsigned('!=', kjf__biqf, lir.Constant(
            kjf__biqf.type, 1))
        with builder.if_then(zcqf__coouz):
            builder.store(context.get_constant(types.uint8, 1), izdgq__sxfd)
            field_val = c.pyapi.to_native_value(xwbi__iccl, dwh__uvzi).value
            builder.store(field_val, ces__fdwt)
        szbvw__nltv.append(builder.load(ces__fdwt))
        nulls.append(builder.load(izdgq__sxfd))
    c.pyapi.decref(qncnl__hhmu)
    c.pyapi.decref(ecx__czwy)
    ymc__wzyfm = construct_struct(context, builder, typ, szbvw__nltv, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = ymc__wzyfm
    rva__gyvd = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=rva__gyvd)


@box(StructType)
def box_struct(typ, val, c):
    gqya__mrak = c.pyapi.dict_new(len(typ.data))
    zvhp__jmq, neiap__lvj = _get_struct_payload(c.context, c.builder, typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(gqya__mrak, typ.names[i], c.pyapi.
            borrow_none())
        snokj__wpb = c.builder.extract_value(zvhp__jmq.null_bitmap, i)
        zcqf__coouz = c.builder.icmp_unsigned('==', snokj__wpb, lir.
            Constant(snokj__wpb.type, 1))
        with c.builder.if_then(zcqf__coouz):
            bodx__dovx = c.builder.extract_value(zvhp__jmq.data, i)
            c.context.nrt.incref(c.builder, val_typ, bodx__dovx)
            scf__rdq = c.pyapi.from_native_value(val_typ, bodx__dovx, c.
                env_manager)
            c.pyapi.dict_setitem_string(gqya__mrak, typ.names[i], scf__rdq)
            c.pyapi.decref(scf__rdq)
    c.context.nrt.decref(c.builder, typ, val)
    return gqya__mrak


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(xwbi__iccl) for xwbi__iccl in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, yaai__uoqir = args
        payload_type = StructPayloadType(struct_type.data)
        icho__okbb = context.get_value_type(payload_type)
        ecwv__vti = context.get_abi_sizeof(icho__okbb)
        hweb__zlk = define_struct_dtor(context, builder, struct_type,
            payload_type)
        ymc__wzyfm = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, ecwv__vti), hweb__zlk)
        wnfem__wsi = context.nrt.meminfo_data(builder, ymc__wzyfm)
        stdp__vxdrh = builder.bitcast(wnfem__wsi, icho__okbb.as_pointer())
        zvhp__jmq = cgutils.create_struct_proxy(payload_type)(context, builder)
        zvhp__jmq.data = data
        zvhp__jmq.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for neiap__lvj in range(len(
            data_typ.types))])
        builder.store(zvhp__jmq._getvalue(), stdp__vxdrh)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = ymc__wzyfm
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        zvhp__jmq, neiap__lvj = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            zvhp__jmq.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        zvhp__jmq, neiap__lvj = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            zvhp__jmq.null_bitmap)
    mud__vfox = types.UniTuple(types.int8, len(struct_typ.data))
    return mud__vfox(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, neiap__lvj, val = args
        zvhp__jmq, stdp__vxdrh = _get_struct_payload(context, builder,
            struct_typ, struct)
        fage__fzq = zvhp__jmq.data
        tjk__snaz = builder.insert_value(fage__fzq, val, field_ind)
        tfirl__cbo = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, tfirl__cbo, fage__fzq)
        context.nrt.incref(builder, tfirl__cbo, tjk__snaz)
        zvhp__jmq.data = tjk__snaz
        builder.store(zvhp__jmq._getvalue(), stdp__vxdrh)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    opbvv__kuzx = get_overload_const_str(ind)
    if opbvv__kuzx not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            opbvv__kuzx, struct))
    return struct.names.index(opbvv__kuzx)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    icho__okbb = context.get_value_type(payload_type)
    ecwv__vti = context.get_abi_sizeof(icho__okbb)
    hweb__zlk = define_struct_dtor(context, builder, struct_type, payload_type)
    ymc__wzyfm = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ecwv__vti), hweb__zlk)
    wnfem__wsi = context.nrt.meminfo_data(builder, ymc__wzyfm)
    stdp__vxdrh = builder.bitcast(wnfem__wsi, icho__okbb.as_pointer())
    zvhp__jmq = cgutils.create_struct_proxy(payload_type)(context, builder)
    zvhp__jmq.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    zvhp__jmq.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(zvhp__jmq._getvalue(), stdp__vxdrh)
    return ymc__wzyfm


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    hvlv__pur = tuple(d.dtype for d in struct_arr_typ.data)
    dpsym__maqp = StructType(hvlv__pur, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        lghj__bdh, ind = args
        zvhp__jmq = _get_struct_arr_payload(context, builder,
            struct_arr_typ, lghj__bdh)
        szbvw__nltv = []
        uixuu__urct = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            wwsme__efii = builder.extract_value(zvhp__jmq.data, i)
            ake__fli = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                wwsme__efii, ind])
            uixuu__urct.append(ake__fli)
            fyib__zubnh = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            zcqf__coouz = builder.icmp_unsigned('==', ake__fli, lir.
                Constant(ake__fli.type, 1))
            with builder.if_then(zcqf__coouz):
                pnnpk__daa = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    wwsme__efii, ind])
                builder.store(pnnpk__daa, fyib__zubnh)
            szbvw__nltv.append(builder.load(fyib__zubnh))
        if isinstance(dpsym__maqp, types.DictType):
            xerqe__gzu = [context.insert_const_string(builder.module,
                bkv__bgcnr) for bkv__bgcnr in struct_arr_typ.names]
            rqth__vgak = cgutils.pack_array(builder, szbvw__nltv)
            qury__eqm = cgutils.pack_array(builder, xerqe__gzu)

            def impl(names, vals):
                d = {}
                for i, bkv__bgcnr in enumerate(names):
                    d[bkv__bgcnr] = vals[i]
                return d
            hpx__dtc = context.compile_internal(builder, impl, dpsym__maqp(
                types.Tuple(tuple(types.StringLiteral(bkv__bgcnr) for
                bkv__bgcnr in struct_arr_typ.names)), types.Tuple(hvlv__pur
                )), [qury__eqm, rqth__vgak])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                hvlv__pur), rqth__vgak)
            return hpx__dtc
        ymc__wzyfm = construct_struct(context, builder, dpsym__maqp,
            szbvw__nltv, uixuu__urct)
        struct = context.make_helper(builder, dpsym__maqp)
        struct.meminfo = ymc__wzyfm
        return struct._getvalue()
    return dpsym__maqp(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        zvhp__jmq = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            zvhp__jmq.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        zvhp__jmq = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            zvhp__jmq.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(xwbi__iccl) for xwbi__iccl in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, bhuz__xgyel, yaai__uoqir = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        icho__okbb = context.get_value_type(payload_type)
        ecwv__vti = context.get_abi_sizeof(icho__okbb)
        hweb__zlk = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        ymc__wzyfm = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, ecwv__vti), hweb__zlk)
        wnfem__wsi = context.nrt.meminfo_data(builder, ymc__wzyfm)
        stdp__vxdrh = builder.bitcast(wnfem__wsi, icho__okbb.as_pointer())
        zvhp__jmq = cgutils.create_struct_proxy(payload_type)(context, builder)
        zvhp__jmq.data = data
        zvhp__jmq.null_bitmap = bhuz__xgyel
        builder.store(zvhp__jmq._getvalue(), stdp__vxdrh)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, bhuz__xgyel)
        zgdo__wntwq = context.make_helper(builder, struct_arr_type)
        zgdo__wntwq.meminfo = ymc__wzyfm
        return zgdo__wntwq._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    waa__iee = len(arr.data)
    eylid__jxga = 'def impl(arr, ind):\n'
    eylid__jxga += '  data = get_data(arr)\n'
    eylid__jxga += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        eylid__jxga += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        eylid__jxga += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        eylid__jxga += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    eylid__jxga += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(waa__iee)), ', '.join("'{}'".format(bkv__bgcnr) for
        bkv__bgcnr in arr.names)))
    ylvj__xvgqh = {}
    exec(eylid__jxga, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, ylvj__xvgqh)
    impl = ylvj__xvgqh['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        waa__iee = len(arr.data)
        eylid__jxga = 'def impl(arr, ind, val):\n'
        eylid__jxga += '  data = get_data(arr)\n'
        eylid__jxga += '  null_bitmap = get_null_bitmap(arr)\n'
        eylid__jxga += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(waa__iee):
            if isinstance(val, StructType):
                eylid__jxga += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                eylid__jxga += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                eylid__jxga += '  else:\n'
                eylid__jxga += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                eylid__jxga += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        ylvj__xvgqh = {}
        exec(eylid__jxga, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, ylvj__xvgqh)
        impl = ylvj__xvgqh['impl']
        return impl
    if isinstance(ind, types.SliceType):
        waa__iee = len(arr.data)
        eylid__jxga = 'def impl(arr, ind, val):\n'
        eylid__jxga += '  data = get_data(arr)\n'
        eylid__jxga += '  null_bitmap = get_null_bitmap(arr)\n'
        eylid__jxga += '  val_data = get_data(val)\n'
        eylid__jxga += '  val_null_bitmap = get_null_bitmap(val)\n'
        eylid__jxga += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(waa__iee):
            eylid__jxga += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        ylvj__xvgqh = {}
        exec(eylid__jxga, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, ylvj__xvgqh)
        impl = ylvj__xvgqh['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    eylid__jxga = 'def impl(A):\n'
    eylid__jxga += '  total_nbytes = 0\n'
    eylid__jxga += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        eylid__jxga += f'  total_nbytes += data[{i}].nbytes\n'
    eylid__jxga += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    eylid__jxga += '  return total_nbytes\n'
    ylvj__xvgqh = {}
    exec(eylid__jxga, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, ylvj__xvgqh)
    impl = ylvj__xvgqh['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        bhuz__xgyel = get_null_bitmap(A)
        krr__ltqs = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        mrhih__zjqo = bhuz__xgyel.copy()
        return init_struct_arr(krr__ltqs, mrhih__zjqo, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(qou__smxv.copy() for qou__smxv in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    tkkam__lszy = arrs.count
    eylid__jxga = 'def f(arrs):\n'
    eylid__jxga += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(tkkam__lszy)))
    ylvj__xvgqh = {}
    exec(eylid__jxga, {}, ylvj__xvgqh)
    impl = ylvj__xvgqh['f']
    return impl
