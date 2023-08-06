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
            .utils.is_array_typ(qtfps__epirv, False) for qtfps__epirv in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(qtfps__epirv,
                str) for qtfps__epirv in names) and len(names) == len(data)
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
        return StructType(tuple(zzbov__lcfj.dtype for zzbov__lcfj in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(qtfps__epirv) for qtfps__epirv in d.keys())
        data = tuple(dtype_to_array_type(zzbov__lcfj) for zzbov__lcfj in d.
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
            is_array_typ(qtfps__epirv, False) for qtfps__epirv in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        otl__xmkvv = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, otl__xmkvv)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        otl__xmkvv = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, otl__xmkvv)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    tyeci__toatt = builder.module
    qyqbg__ywdeh = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    kgnzq__gzi = cgutils.get_or_insert_function(tyeci__toatt, qyqbg__ywdeh,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not kgnzq__gzi.is_declaration:
        return kgnzq__gzi
    kgnzq__gzi.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(kgnzq__gzi.append_basic_block())
    ssrus__eqkow = kgnzq__gzi.args[0]
    lxw__oea = context.get_value_type(payload_type).as_pointer()
    fmf__yini = builder.bitcast(ssrus__eqkow, lxw__oea)
    eyg__pwdr = context.make_helper(builder, payload_type, ref=fmf__yini)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), eyg__pwdr.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), eyg__pwdr
        .null_bitmap)
    builder.ret_void()
    return kgnzq__gzi


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    qte__vdsd = context.get_value_type(payload_type)
    ysft__xipcn = context.get_abi_sizeof(qte__vdsd)
    xwcag__slt = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    nzyrq__hnef = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ysft__xipcn), xwcag__slt)
    aqk__vnqie = context.nrt.meminfo_data(builder, nzyrq__hnef)
    fndr__xlrnf = builder.bitcast(aqk__vnqie, qte__vdsd.as_pointer())
    eyg__pwdr = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    ynit__zzdu = 0
    for arr_typ in struct_arr_type.data:
        klfz__rktqr = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        tzzkc__rbv = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(ynit__zzdu, ynit__zzdu +
            klfz__rktqr)])
        arr = gen_allocate_array(context, builder, arr_typ, tzzkc__rbv, c)
        arrs.append(arr)
        ynit__zzdu += klfz__rktqr
    eyg__pwdr.data = cgutils.pack_array(builder, arrs) if types.is_homogeneous(
        *struct_arr_type.data) else cgutils.pack_struct(builder, arrs)
    mmdsb__mpeg = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    asxbl__jdqg = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [mmdsb__mpeg])
    null_bitmap_ptr = asxbl__jdqg.data
    eyg__pwdr.null_bitmap = asxbl__jdqg._getvalue()
    builder.store(eyg__pwdr._getvalue(), fndr__xlrnf)
    return nzyrq__hnef, eyg__pwdr.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    teahs__fmxu = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        dyhe__pfvm = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            dyhe__pfvm)
        teahs__fmxu.append(arr.data)
    oiab__jvjaw = cgutils.pack_array(c.builder, teahs__fmxu
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, teahs__fmxu)
    gqlbi__zqwpi = cgutils.alloca_once_value(c.builder, oiab__jvjaw)
    uwpyy__zuv = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(qtfps__epirv.dtype)) for qtfps__epirv in data_typ]
    xhilc__sudt = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, uwpyy__zuv))
    tnog__htli = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, qtfps__epirv) for
        qtfps__epirv in names])
    juc__kbzyc = cgutils.alloca_once_value(c.builder, tnog__htli)
    return gqlbi__zqwpi, xhilc__sudt, juc__kbzyc


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    hxkr__nkke = all(isinstance(zzbov__lcfj, types.Array) and zzbov__lcfj.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for zzbov__lcfj in typ.data)
    if hxkr__nkke:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        rrp__giggh = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            rrp__giggh, i) for i in range(1, rrp__giggh.type.count)], lir.
            IntType(64))
    nzyrq__hnef, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if hxkr__nkke:
        gqlbi__zqwpi, xhilc__sudt, juc__kbzyc = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        qyqbg__ywdeh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        kgnzq__gzi = cgutils.get_or_insert_function(c.builder.module,
            qyqbg__ywdeh, name='struct_array_from_sequence')
        c.builder.call(kgnzq__gzi, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(gqlbi__zqwpi, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(xhilc__sudt,
            lir.IntType(8).as_pointer()), c.builder.bitcast(juc__kbzyc, lir
            .IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    shc__vze = c.context.make_helper(c.builder, typ)
    shc__vze.meminfo = nzyrq__hnef
    nxfik__yep = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(shc__vze._getvalue(), is_error=nxfik__yep)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    zpxea__wqvt = context.insert_const_string(builder.module, 'pandas')
    xuiqy__eulb = c.pyapi.import_module_noblock(zpxea__wqvt)
    dybcb__ivrc = c.pyapi.object_getattr_string(xuiqy__eulb, 'NA')
    with cgutils.for_range(builder, n_structs) as ahyh__rmi:
        twt__pog = ahyh__rmi.index
        xkq__bkm = seq_getitem(builder, context, val, twt__pog)
        set_bitmap_bit(builder, null_bitmap_ptr, twt__pog, 0)
        for zhjjx__ghs in range(len(typ.data)):
            arr_typ = typ.data[zhjjx__ghs]
            data_arr = builder.extract_value(data_tup, zhjjx__ghs)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            mvikd__yqmvq, npgrp__wqvf = c.pyapi.call_jit_code(set_na, sig,
                [data_arr, twt__pog])
        ecz__xzex = is_na_value(builder, context, xkq__bkm, dybcb__ivrc)
        appce__vuqi = builder.icmp_unsigned('!=', ecz__xzex, lir.Constant(
            ecz__xzex.type, 1))
        with builder.if_then(appce__vuqi):
            set_bitmap_bit(builder, null_bitmap_ptr, twt__pog, 1)
            for zhjjx__ghs in range(len(typ.data)):
                arr_typ = typ.data[zhjjx__ghs]
                if is_tuple_array:
                    eudtp__tzitp = c.pyapi.tuple_getitem(xkq__bkm, zhjjx__ghs)
                else:
                    eudtp__tzitp = c.pyapi.dict_getitem_string(xkq__bkm,
                        typ.names[zhjjx__ghs])
                ecz__xzex = is_na_value(builder, context, eudtp__tzitp,
                    dybcb__ivrc)
                appce__vuqi = builder.icmp_unsigned('!=', ecz__xzex, lir.
                    Constant(ecz__xzex.type, 1))
                with builder.if_then(appce__vuqi):
                    eudtp__tzitp = to_arr_obj_if_list_obj(c, context,
                        builder, eudtp__tzitp, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        eudtp__tzitp).value
                    data_arr = builder.extract_value(data_tup, zhjjx__ghs)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    mvikd__yqmvq, npgrp__wqvf = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, twt__pog, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(xkq__bkm)
    c.pyapi.decref(xuiqy__eulb)
    c.pyapi.decref(dybcb__ivrc)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    shc__vze = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    aqk__vnqie = context.nrt.meminfo_data(builder, shc__vze.meminfo)
    fndr__xlrnf = builder.bitcast(aqk__vnqie, context.get_value_type(
        payload_type).as_pointer())
    eyg__pwdr = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(fndr__xlrnf))
    return eyg__pwdr


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    eyg__pwdr = _get_struct_arr_payload(c.context, c.builder, typ, val)
    mvikd__yqmvq, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), eyg__pwdr.null_bitmap).data
    hxkr__nkke = all(isinstance(zzbov__lcfj, types.Array) and zzbov__lcfj.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for zzbov__lcfj in typ.data)
    if hxkr__nkke:
        gqlbi__zqwpi, xhilc__sudt, juc__kbzyc = _get_C_API_ptrs(c,
            eyg__pwdr.data, typ.data, typ.names)
        qyqbg__ywdeh = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        mbjfn__yvt = cgutils.get_or_insert_function(c.builder.module,
            qyqbg__ywdeh, name='np_array_from_struct_array')
        arr = c.builder.call(mbjfn__yvt, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(gqlbi__zqwpi,
            lir.IntType(8).as_pointer()), null_bitmap_ptr, c.builder.
            bitcast(xhilc__sudt, lir.IntType(8).as_pointer()), c.builder.
            bitcast(juc__kbzyc, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, eyg__pwdr.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    zpxea__wqvt = context.insert_const_string(builder.module, 'numpy')
    ncrt__uctra = c.pyapi.import_module_noblock(zpxea__wqvt)
    xgeug__wymms = c.pyapi.object_getattr_string(ncrt__uctra, 'object_')
    kguhz__cnzmx = c.pyapi.long_from_longlong(length)
    mzct__ozuqa = c.pyapi.call_method(ncrt__uctra, 'ndarray', (kguhz__cnzmx,
        xgeug__wymms))
    vig__toedp = c.pyapi.object_getattr_string(ncrt__uctra, 'nan')
    with cgutils.for_range(builder, length) as ahyh__rmi:
        twt__pog = ahyh__rmi.index
        pyarray_setitem(builder, context, mzct__ozuqa, twt__pog, vig__toedp)
        yljv__bnl = get_bitmap_bit(builder, null_bitmap_ptr, twt__pog)
        wqocr__cdi = builder.icmp_unsigned('!=', yljv__bnl, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(wqocr__cdi):
            if is_tuple_array:
                xkq__bkm = c.pyapi.tuple_new(len(typ.data))
            else:
                xkq__bkm = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(vig__toedp)
                    c.pyapi.tuple_setitem(xkq__bkm, i, vig__toedp)
                else:
                    c.pyapi.dict_setitem_string(xkq__bkm, typ.names[i],
                        vig__toedp)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                mvikd__yqmvq, qsrm__vyxoe = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, twt__pog])
                with builder.if_then(qsrm__vyxoe):
                    mvikd__yqmvq, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, twt__pog])
                    qeeva__hsjhi = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(xkq__bkm, i, qeeva__hsjhi)
                    else:
                        c.pyapi.dict_setitem_string(xkq__bkm, typ.names[i],
                            qeeva__hsjhi)
                        c.pyapi.decref(qeeva__hsjhi)
            pyarray_setitem(builder, context, mzct__ozuqa, twt__pog, xkq__bkm)
            c.pyapi.decref(xkq__bkm)
    c.pyapi.decref(ncrt__uctra)
    c.pyapi.decref(xgeug__wymms)
    c.pyapi.decref(kguhz__cnzmx)
    c.pyapi.decref(vig__toedp)
    return mzct__ozuqa


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    arhvb__janva = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if arhvb__janva == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for ehu__qov in range(arhvb__janva)])
    elif nested_counts_type.count < arhvb__janva:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for ehu__qov in range(
            arhvb__janva - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(zzbov__lcfj) for zzbov__lcfj in
            names_typ.types)
    nekg__psimi = tuple(zzbov__lcfj.instance_type for zzbov__lcfj in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(nekg__psimi, names)

    def codegen(context, builder, sig, args):
        elphm__zgpet, nested_counts, ehu__qov, ehu__qov = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        nzyrq__hnef, ehu__qov, ehu__qov = construct_struct_array(context,
            builder, struct_arr_type, elphm__zgpet, nested_counts)
        shc__vze = context.make_helper(builder, struct_arr_type)
        shc__vze.meminfo = nzyrq__hnef
        return shc__vze._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(qtfps__epirv,
            str) for qtfps__epirv in names) and len(names) == len(data)
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
        otl__xmkvv = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, otl__xmkvv)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        otl__xmkvv = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, otl__xmkvv)


def define_struct_dtor(context, builder, struct_type, payload_type):
    tyeci__toatt = builder.module
    qyqbg__ywdeh = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    kgnzq__gzi = cgutils.get_or_insert_function(tyeci__toatt, qyqbg__ywdeh,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not kgnzq__gzi.is_declaration:
        return kgnzq__gzi
    kgnzq__gzi.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(kgnzq__gzi.append_basic_block())
    ssrus__eqkow = kgnzq__gzi.args[0]
    lxw__oea = context.get_value_type(payload_type).as_pointer()
    fmf__yini = builder.bitcast(ssrus__eqkow, lxw__oea)
    eyg__pwdr = context.make_helper(builder, payload_type, ref=fmf__yini)
    for i in range(len(struct_type.data)):
        wfzuo__bmirb = builder.extract_value(eyg__pwdr.null_bitmap, i)
        wqocr__cdi = builder.icmp_unsigned('==', wfzuo__bmirb, lir.Constant
            (wfzuo__bmirb.type, 1))
        with builder.if_then(wqocr__cdi):
            val = builder.extract_value(eyg__pwdr.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return kgnzq__gzi


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    aqk__vnqie = context.nrt.meminfo_data(builder, struct.meminfo)
    fndr__xlrnf = builder.bitcast(aqk__vnqie, context.get_value_type(
        payload_type).as_pointer())
    eyg__pwdr = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(fndr__xlrnf))
    return eyg__pwdr, fndr__xlrnf


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    zpxea__wqvt = context.insert_const_string(builder.module, 'pandas')
    xuiqy__eulb = c.pyapi.import_module_noblock(zpxea__wqvt)
    dybcb__ivrc = c.pyapi.object_getattr_string(xuiqy__eulb, 'NA')
    ifhrx__llz = []
    nulls = []
    for i, zzbov__lcfj in enumerate(typ.data):
        qeeva__hsjhi = c.pyapi.dict_getitem_string(val, typ.names[i])
        tsmcf__txmhu = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        ewmr__bbtgc = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(zzbov__lcfj)))
        ecz__xzex = is_na_value(builder, context, qeeva__hsjhi, dybcb__ivrc)
        wqocr__cdi = builder.icmp_unsigned('!=', ecz__xzex, lir.Constant(
            ecz__xzex.type, 1))
        with builder.if_then(wqocr__cdi):
            builder.store(context.get_constant(types.uint8, 1), tsmcf__txmhu)
            field_val = c.pyapi.to_native_value(zzbov__lcfj, qeeva__hsjhi
                ).value
            builder.store(field_val, ewmr__bbtgc)
        ifhrx__llz.append(builder.load(ewmr__bbtgc))
        nulls.append(builder.load(tsmcf__txmhu))
    c.pyapi.decref(xuiqy__eulb)
    c.pyapi.decref(dybcb__ivrc)
    nzyrq__hnef = construct_struct(context, builder, typ, ifhrx__llz, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = nzyrq__hnef
    nxfik__yep = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=nxfik__yep)


@box(StructType)
def box_struct(typ, val, c):
    csrb__hdbi = c.pyapi.dict_new(len(typ.data))
    eyg__pwdr, ehu__qov = _get_struct_payload(c.context, c.builder, typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(csrb__hdbi, typ.names[i], c.pyapi.
            borrow_none())
        wfzuo__bmirb = c.builder.extract_value(eyg__pwdr.null_bitmap, i)
        wqocr__cdi = c.builder.icmp_unsigned('==', wfzuo__bmirb, lir.
            Constant(wfzuo__bmirb.type, 1))
        with c.builder.if_then(wqocr__cdi):
            gfuoe__jdufv = c.builder.extract_value(eyg__pwdr.data, i)
            c.context.nrt.incref(c.builder, val_typ, gfuoe__jdufv)
            eudtp__tzitp = c.pyapi.from_native_value(val_typ, gfuoe__jdufv,
                c.env_manager)
            c.pyapi.dict_setitem_string(csrb__hdbi, typ.names[i], eudtp__tzitp)
            c.pyapi.decref(eudtp__tzitp)
    c.context.nrt.decref(c.builder, typ, val)
    return csrb__hdbi


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(zzbov__lcfj) for zzbov__lcfj in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, scjl__ygqxn = args
        payload_type = StructPayloadType(struct_type.data)
        qte__vdsd = context.get_value_type(payload_type)
        ysft__xipcn = context.get_abi_sizeof(qte__vdsd)
        xwcag__slt = define_struct_dtor(context, builder, struct_type,
            payload_type)
        nzyrq__hnef = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, ysft__xipcn), xwcag__slt)
        aqk__vnqie = context.nrt.meminfo_data(builder, nzyrq__hnef)
        fndr__xlrnf = builder.bitcast(aqk__vnqie, qte__vdsd.as_pointer())
        eyg__pwdr = cgutils.create_struct_proxy(payload_type)(context, builder)
        eyg__pwdr.data = data
        eyg__pwdr.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for ehu__qov in range(len(data_typ
            .types))])
        builder.store(eyg__pwdr._getvalue(), fndr__xlrnf)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = nzyrq__hnef
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        eyg__pwdr, ehu__qov = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            eyg__pwdr.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        eyg__pwdr, ehu__qov = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            eyg__pwdr.null_bitmap)
    bzo__gvft = types.UniTuple(types.int8, len(struct_typ.data))
    return bzo__gvft(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, ehu__qov, val = args
        eyg__pwdr, fndr__xlrnf = _get_struct_payload(context, builder,
            struct_typ, struct)
        gqbtb__nknx = eyg__pwdr.data
        vonny__tww = builder.insert_value(gqbtb__nknx, val, field_ind)
        zjcon__ghfpg = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, zjcon__ghfpg, gqbtb__nknx)
        context.nrt.incref(builder, zjcon__ghfpg, vonny__tww)
        eyg__pwdr.data = vonny__tww
        builder.store(eyg__pwdr._getvalue(), fndr__xlrnf)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    zsc__hdpl = get_overload_const_str(ind)
    if zsc__hdpl not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            zsc__hdpl, struct))
    return struct.names.index(zsc__hdpl)


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
    qte__vdsd = context.get_value_type(payload_type)
    ysft__xipcn = context.get_abi_sizeof(qte__vdsd)
    xwcag__slt = define_struct_dtor(context, builder, struct_type, payload_type
        )
    nzyrq__hnef = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ysft__xipcn), xwcag__slt)
    aqk__vnqie = context.nrt.meminfo_data(builder, nzyrq__hnef)
    fndr__xlrnf = builder.bitcast(aqk__vnqie, qte__vdsd.as_pointer())
    eyg__pwdr = cgutils.create_struct_proxy(payload_type)(context, builder)
    eyg__pwdr.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    eyg__pwdr.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(eyg__pwdr._getvalue(), fndr__xlrnf)
    return nzyrq__hnef


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    yxh__xync = tuple(d.dtype for d in struct_arr_typ.data)
    apz__bpj = StructType(yxh__xync, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        zrk__hsj, ind = args
        eyg__pwdr = _get_struct_arr_payload(context, builder,
            struct_arr_typ, zrk__hsj)
        ifhrx__llz = []
        vqk__pgd = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            dyhe__pfvm = builder.extract_value(eyg__pwdr.data, i)
            nxigj__mxw = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [dyhe__pfvm,
                ind])
            vqk__pgd.append(nxigj__mxw)
            rieud__fcbnz = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            wqocr__cdi = builder.icmp_unsigned('==', nxigj__mxw, lir.
                Constant(nxigj__mxw.type, 1))
            with builder.if_then(wqocr__cdi):
                edfo__dem = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    dyhe__pfvm, ind])
                builder.store(edfo__dem, rieud__fcbnz)
            ifhrx__llz.append(builder.load(rieud__fcbnz))
        if isinstance(apz__bpj, types.DictType):
            ogcyt__pumr = [context.insert_const_string(builder.module,
                eix__tgero) for eix__tgero in struct_arr_typ.names]
            qocaj__opx = cgutils.pack_array(builder, ifhrx__llz)
            xwcj__tmen = cgutils.pack_array(builder, ogcyt__pumr)

            def impl(names, vals):
                d = {}
                for i, eix__tgero in enumerate(names):
                    d[eix__tgero] = vals[i]
                return d
            rwh__plj = context.compile_internal(builder, impl, apz__bpj(
                types.Tuple(tuple(types.StringLiteral(eix__tgero) for
                eix__tgero in struct_arr_typ.names)), types.Tuple(yxh__xync
                )), [xwcj__tmen, qocaj__opx])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                yxh__xync), qocaj__opx)
            return rwh__plj
        nzyrq__hnef = construct_struct(context, builder, apz__bpj,
            ifhrx__llz, vqk__pgd)
        struct = context.make_helper(builder, apz__bpj)
        struct.meminfo = nzyrq__hnef
        return struct._getvalue()
    return apz__bpj(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        eyg__pwdr = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            eyg__pwdr.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        eyg__pwdr = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            eyg__pwdr.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(zzbov__lcfj) for zzbov__lcfj in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, asxbl__jdqg, scjl__ygqxn = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        qte__vdsd = context.get_value_type(payload_type)
        ysft__xipcn = context.get_abi_sizeof(qte__vdsd)
        xwcag__slt = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        nzyrq__hnef = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, ysft__xipcn), xwcag__slt)
        aqk__vnqie = context.nrt.meminfo_data(builder, nzyrq__hnef)
        fndr__xlrnf = builder.bitcast(aqk__vnqie, qte__vdsd.as_pointer())
        eyg__pwdr = cgutils.create_struct_proxy(payload_type)(context, builder)
        eyg__pwdr.data = data
        eyg__pwdr.null_bitmap = asxbl__jdqg
        builder.store(eyg__pwdr._getvalue(), fndr__xlrnf)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, asxbl__jdqg)
        shc__vze = context.make_helper(builder, struct_arr_type)
        shc__vze.meminfo = nzyrq__hnef
        return shc__vze._getvalue()
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
    lsvgo__vsesn = len(arr.data)
    tvg__vvyb = 'def impl(arr, ind):\n'
    tvg__vvyb += '  data = get_data(arr)\n'
    tvg__vvyb += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        tvg__vvyb += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        tvg__vvyb += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        tvg__vvyb += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    tvg__vvyb += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(lsvgo__vsesn)), ', '.join("'{}'".format(eix__tgero) for
        eix__tgero in arr.names)))
    mmc__fxjy = {}
    exec(tvg__vvyb, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, mmc__fxjy)
    impl = mmc__fxjy['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        lsvgo__vsesn = len(arr.data)
        tvg__vvyb = 'def impl(arr, ind, val):\n'
        tvg__vvyb += '  data = get_data(arr)\n'
        tvg__vvyb += '  null_bitmap = get_null_bitmap(arr)\n'
        tvg__vvyb += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(lsvgo__vsesn):
            if isinstance(val, StructType):
                tvg__vvyb += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                tvg__vvyb += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                tvg__vvyb += '  else:\n'
                tvg__vvyb += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                tvg__vvyb += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        mmc__fxjy = {}
        exec(tvg__vvyb, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, mmc__fxjy)
        impl = mmc__fxjy['impl']
        return impl
    if isinstance(ind, types.SliceType):
        lsvgo__vsesn = len(arr.data)
        tvg__vvyb = 'def impl(arr, ind, val):\n'
        tvg__vvyb += '  data = get_data(arr)\n'
        tvg__vvyb += '  null_bitmap = get_null_bitmap(arr)\n'
        tvg__vvyb += '  val_data = get_data(val)\n'
        tvg__vvyb += '  val_null_bitmap = get_null_bitmap(val)\n'
        tvg__vvyb += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(lsvgo__vsesn):
            tvg__vvyb += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        mmc__fxjy = {}
        exec(tvg__vvyb, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, mmc__fxjy)
        impl = mmc__fxjy['impl']
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
    tvg__vvyb = 'def impl(A):\n'
    tvg__vvyb += '  total_nbytes = 0\n'
    tvg__vvyb += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        tvg__vvyb += f'  total_nbytes += data[{i}].nbytes\n'
    tvg__vvyb += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    tvg__vvyb += '  return total_nbytes\n'
    mmc__fxjy = {}
    exec(tvg__vvyb, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, mmc__fxjy)
    impl = mmc__fxjy['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        asxbl__jdqg = get_null_bitmap(A)
        ppek__jkz = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        fak__qkz = asxbl__jdqg.copy()
        return init_struct_arr(ppek__jkz, fak__qkz, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(qtfps__epirv.copy() for qtfps__epirv in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    kzqj__tnrqk = arrs.count
    tvg__vvyb = 'def f(arrs):\n'
    tvg__vvyb += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(kzqj__tnrqk)))
    mmc__fxjy = {}
    exec(tvg__vvyb, {}, mmc__fxjy)
    impl = mmc__fxjy['f']
    return impl
