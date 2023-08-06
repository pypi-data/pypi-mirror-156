"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    eqx__cruq = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    rxf__gkxc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    uatj__xsz = builder.gep(null_bitmap_ptr, [eqx__cruq], inbounds=True)
    fcum__pzrai = builder.load(uatj__xsz)
    fzlf__ijgov = lir.ArrayType(lir.IntType(8), 8)
    lgn__wcyar = cgutils.alloca_once_value(builder, lir.Constant(
        fzlf__ijgov, (1, 2, 4, 8, 16, 32, 64, 128)))
    pjwp__vxi = builder.load(builder.gep(lgn__wcyar, [lir.Constant(lir.
        IntType(64), 0), rxf__gkxc], inbounds=True))
    if val:
        builder.store(builder.or_(fcum__pzrai, pjwp__vxi), uatj__xsz)
    else:
        pjwp__vxi = builder.xor(pjwp__vxi, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(fcum__pzrai, pjwp__vxi), uatj__xsz)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    eqx__cruq = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    rxf__gkxc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    fcum__pzrai = builder.load(builder.gep(null_bitmap_ptr, [eqx__cruq],
        inbounds=True))
    fzlf__ijgov = lir.ArrayType(lir.IntType(8), 8)
    lgn__wcyar = cgutils.alloca_once_value(builder, lir.Constant(
        fzlf__ijgov, (1, 2, 4, 8, 16, 32, 64, 128)))
    pjwp__vxi = builder.load(builder.gep(lgn__wcyar, [lir.Constant(lir.
        IntType(64), 0), rxf__gkxc], inbounds=True))
    return builder.and_(fcum__pzrai, pjwp__vxi)


def pyarray_check(builder, context, obj):
    dric__vsej = context.get_argument_type(types.pyobject)
    dtef__fkbh = lir.FunctionType(lir.IntType(32), [dric__vsej])
    hjei__jdpxx = cgutils.get_or_insert_function(builder.module, dtef__fkbh,
        name='is_np_array')
    return builder.call(hjei__jdpxx, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    dric__vsej = context.get_argument_type(types.pyobject)
    fxhio__ntwjn = context.get_value_type(types.intp)
    hka__cqhd = lir.FunctionType(lir.IntType(8).as_pointer(), [dric__vsej,
        fxhio__ntwjn])
    zfs__srpmh = cgutils.get_or_insert_function(builder.module, hka__cqhd,
        name='array_getptr1')
    xqjg__fgm = lir.FunctionType(dric__vsej, [dric__vsej, lir.IntType(8).
        as_pointer()])
    zib__isyi = cgutils.get_or_insert_function(builder.module, xqjg__fgm,
        name='array_getitem')
    bieu__dfty = builder.call(zfs__srpmh, [arr_obj, ind])
    return builder.call(zib__isyi, [arr_obj, bieu__dfty])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    dric__vsej = context.get_argument_type(types.pyobject)
    fxhio__ntwjn = context.get_value_type(types.intp)
    hka__cqhd = lir.FunctionType(lir.IntType(8).as_pointer(), [dric__vsej,
        fxhio__ntwjn])
    zfs__srpmh = cgutils.get_or_insert_function(builder.module, hka__cqhd,
        name='array_getptr1')
    gcc__icabo = lir.FunctionType(lir.VoidType(), [dric__vsej, lir.IntType(
        8).as_pointer(), dric__vsej])
    eap__iknrl = cgutils.get_or_insert_function(builder.module, gcc__icabo,
        name='array_setitem')
    bieu__dfty = builder.call(zfs__srpmh, [arr_obj, ind])
    builder.call(eap__iknrl, [arr_obj, bieu__dfty, val_obj])


def seq_getitem(builder, context, obj, ind):
    dric__vsej = context.get_argument_type(types.pyobject)
    fxhio__ntwjn = context.get_value_type(types.intp)
    ltdbf__uvr = lir.FunctionType(dric__vsej, [dric__vsej, fxhio__ntwjn])
    iwn__snhx = cgutils.get_or_insert_function(builder.module, ltdbf__uvr,
        name='seq_getitem')
    return builder.call(iwn__snhx, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    dric__vsej = context.get_argument_type(types.pyobject)
    ahig__zhvw = lir.FunctionType(lir.IntType(32), [dric__vsej, dric__vsej])
    vqh__gssmb = cgutils.get_or_insert_function(builder.module, ahig__zhvw,
        name='is_na_value')
    return builder.call(vqh__gssmb, [val, C_NA])


def list_check(builder, context, obj):
    dric__vsej = context.get_argument_type(types.pyobject)
    piqyp__jvird = context.get_value_type(types.int32)
    qtbui__cmw = lir.FunctionType(piqyp__jvird, [dric__vsej])
    uknjw__kaff = cgutils.get_or_insert_function(builder.module, qtbui__cmw,
        name='list_check')
    return builder.call(uknjw__kaff, [obj])


def dict_keys(builder, context, obj):
    dric__vsej = context.get_argument_type(types.pyobject)
    qtbui__cmw = lir.FunctionType(dric__vsej, [dric__vsej])
    uknjw__kaff = cgutils.get_or_insert_function(builder.module, qtbui__cmw,
        name='dict_keys')
    return builder.call(uknjw__kaff, [obj])


def dict_values(builder, context, obj):
    dric__vsej = context.get_argument_type(types.pyobject)
    qtbui__cmw = lir.FunctionType(dric__vsej, [dric__vsej])
    uknjw__kaff = cgutils.get_or_insert_function(builder.module, qtbui__cmw,
        name='dict_values')
    return builder.call(uknjw__kaff, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    dric__vsej = context.get_argument_type(types.pyobject)
    qtbui__cmw = lir.FunctionType(lir.VoidType(), [dric__vsej, dric__vsej])
    uknjw__kaff = cgutils.get_or_insert_function(builder.module, qtbui__cmw,
        name='dict_merge_from_seq2')
    builder.call(uknjw__kaff, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    idbnp__bmsvt = cgutils.alloca_once_value(builder, val)
    zhfd__egl = list_check(builder, context, val)
    aysit__nkh = builder.icmp_unsigned('!=', zhfd__egl, lir.Constant(
        zhfd__egl.type, 0))
    with builder.if_then(aysit__nkh):
        zivxn__kcche = context.insert_const_string(builder.module, 'numpy')
        xqk__rrve = c.pyapi.import_module_noblock(zivxn__kcche)
        uqs__hkpso = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            uqs__hkpso = str(typ.dtype)
        nfrg__xhfu = c.pyapi.object_getattr_string(xqk__rrve, uqs__hkpso)
        vgsht__eoabw = builder.load(idbnp__bmsvt)
        yybg__vnwm = c.pyapi.call_method(xqk__rrve, 'asarray', (
            vgsht__eoabw, nfrg__xhfu))
        builder.store(yybg__vnwm, idbnp__bmsvt)
        c.pyapi.decref(xqk__rrve)
        c.pyapi.decref(nfrg__xhfu)
    val = builder.load(idbnp__bmsvt)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        ewk__ads = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        bvk__kueln, umn__yznac = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [ewk__ads])
        context.nrt.decref(builder, typ, ewk__ads)
        return cgutils.pack_array(builder, [umn__yznac])
    if isinstance(typ, (StructType, types.BaseTuple)):
        zivxn__kcche = context.insert_const_string(builder.module, 'pandas')
        bob__dcfa = c.pyapi.import_module_noblock(zivxn__kcche)
        C_NA = c.pyapi.object_getattr_string(bob__dcfa, 'NA')
        zohsi__fbtwk = bodo.utils.transform.get_type_alloc_counts(typ)
        zthjv__rmxgh = context.make_tuple(builder, types.Tuple(zohsi__fbtwk *
            [types.int64]), zohsi__fbtwk * [context.get_constant(types.
            int64, 0)])
        mse__qhtu = cgutils.alloca_once_value(builder, zthjv__rmxgh)
        osp__fnhma = 0
        wkc__easwj = typ.data if isinstance(typ, StructType) else typ.types
        for abej__bgi, t in enumerate(wkc__easwj):
            lslhh__vqar = bodo.utils.transform.get_type_alloc_counts(t)
            if lslhh__vqar == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    abej__bgi])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, abej__bgi)
            ojfs__rwfhz = is_na_value(builder, context, val_obj, C_NA)
            tkrq__kvqx = builder.icmp_unsigned('!=', ojfs__rwfhz, lir.
                Constant(ojfs__rwfhz.type, 1))
            with builder.if_then(tkrq__kvqx):
                zthjv__rmxgh = builder.load(mse__qhtu)
                ogfha__sctlp = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for abej__bgi in range(lslhh__vqar):
                    djrc__jvxab = builder.extract_value(zthjv__rmxgh, 
                        osp__fnhma + abej__bgi)
                    ewn__mgg = builder.extract_value(ogfha__sctlp, abej__bgi)
                    zthjv__rmxgh = builder.insert_value(zthjv__rmxgh,
                        builder.add(djrc__jvxab, ewn__mgg), osp__fnhma +
                        abej__bgi)
                builder.store(zthjv__rmxgh, mse__qhtu)
            osp__fnhma += lslhh__vqar
        c.pyapi.decref(bob__dcfa)
        c.pyapi.decref(C_NA)
        return builder.load(mse__qhtu)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    zivxn__kcche = context.insert_const_string(builder.module, 'pandas')
    bob__dcfa = c.pyapi.import_module_noblock(zivxn__kcche)
    C_NA = c.pyapi.object_getattr_string(bob__dcfa, 'NA')
    zohsi__fbtwk = bodo.utils.transform.get_type_alloc_counts(typ)
    zthjv__rmxgh = context.make_tuple(builder, types.Tuple(zohsi__fbtwk * [
        types.int64]), [n] + (zohsi__fbtwk - 1) * [context.get_constant(
        types.int64, 0)])
    mse__qhtu = cgutils.alloca_once_value(builder, zthjv__rmxgh)
    with cgutils.for_range(builder, n) as hgptd__vrvty:
        ukh__lsc = hgptd__vrvty.index
        awm__mzar = seq_getitem(builder, context, arr_obj, ukh__lsc)
        ojfs__rwfhz = is_na_value(builder, context, awm__mzar, C_NA)
        tkrq__kvqx = builder.icmp_unsigned('!=', ojfs__rwfhz, lir.Constant(
            ojfs__rwfhz.type, 1))
        with builder.if_then(tkrq__kvqx):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                zthjv__rmxgh = builder.load(mse__qhtu)
                ogfha__sctlp = get_array_elem_counts(c, builder, context,
                    awm__mzar, typ.dtype)
                for abej__bgi in range(zohsi__fbtwk - 1):
                    djrc__jvxab = builder.extract_value(zthjv__rmxgh, 
                        abej__bgi + 1)
                    ewn__mgg = builder.extract_value(ogfha__sctlp, abej__bgi)
                    zthjv__rmxgh = builder.insert_value(zthjv__rmxgh,
                        builder.add(djrc__jvxab, ewn__mgg), abej__bgi + 1)
                builder.store(zthjv__rmxgh, mse__qhtu)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                osp__fnhma = 1
                for abej__bgi, t in enumerate(typ.data):
                    lslhh__vqar = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if lslhh__vqar == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(awm__mzar, abej__bgi)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(awm__mzar,
                            typ.names[abej__bgi])
                    ojfs__rwfhz = is_na_value(builder, context, val_obj, C_NA)
                    tkrq__kvqx = builder.icmp_unsigned('!=', ojfs__rwfhz,
                        lir.Constant(ojfs__rwfhz.type, 1))
                    with builder.if_then(tkrq__kvqx):
                        zthjv__rmxgh = builder.load(mse__qhtu)
                        ogfha__sctlp = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for abej__bgi in range(lslhh__vqar):
                            djrc__jvxab = builder.extract_value(zthjv__rmxgh,
                                osp__fnhma + abej__bgi)
                            ewn__mgg = builder.extract_value(ogfha__sctlp,
                                abej__bgi)
                            zthjv__rmxgh = builder.insert_value(zthjv__rmxgh,
                                builder.add(djrc__jvxab, ewn__mgg), 
                                osp__fnhma + abej__bgi)
                        builder.store(zthjv__rmxgh, mse__qhtu)
                    osp__fnhma += lslhh__vqar
            else:
                assert isinstance(typ, MapArrayType), typ
                zthjv__rmxgh = builder.load(mse__qhtu)
                lcugn__fuqei = dict_keys(builder, context, awm__mzar)
                wqhi__fli = dict_values(builder, context, awm__mzar)
                bbpox__jmmq = get_array_elem_counts(c, builder, context,
                    lcugn__fuqei, typ.key_arr_type)
                fwiaw__hogvc = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for abej__bgi in range(1, fwiaw__hogvc + 1):
                    djrc__jvxab = builder.extract_value(zthjv__rmxgh, abej__bgi
                        )
                    ewn__mgg = builder.extract_value(bbpox__jmmq, abej__bgi - 1
                        )
                    zthjv__rmxgh = builder.insert_value(zthjv__rmxgh,
                        builder.add(djrc__jvxab, ewn__mgg), abej__bgi)
                cvx__tohm = get_array_elem_counts(c, builder, context,
                    wqhi__fli, typ.value_arr_type)
                for abej__bgi in range(fwiaw__hogvc + 1, zohsi__fbtwk):
                    djrc__jvxab = builder.extract_value(zthjv__rmxgh, abej__bgi
                        )
                    ewn__mgg = builder.extract_value(cvx__tohm, abej__bgi -
                        fwiaw__hogvc)
                    zthjv__rmxgh = builder.insert_value(zthjv__rmxgh,
                        builder.add(djrc__jvxab, ewn__mgg), abej__bgi)
                builder.store(zthjv__rmxgh, mse__qhtu)
                c.pyapi.decref(lcugn__fuqei)
                c.pyapi.decref(wqhi__fli)
        c.pyapi.decref(awm__mzar)
    c.pyapi.decref(bob__dcfa)
    c.pyapi.decref(C_NA)
    return builder.load(mse__qhtu)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    zwhe__rnpc = n_elems.type.count
    assert zwhe__rnpc >= 1
    akj__dgwbm = builder.extract_value(n_elems, 0)
    if zwhe__rnpc != 1:
        ojkv__ecyif = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, abej__bgi) for abej__bgi in range(1, zwhe__rnpc)])
        ckfmw__jbngz = types.Tuple([types.int64] * (zwhe__rnpc - 1))
    else:
        ojkv__ecyif = context.get_dummy_value()
        ckfmw__jbngz = types.none
    mojr__hglr = types.TypeRef(arr_type)
    cyzk__gapr = arr_type(types.int64, mojr__hglr, ckfmw__jbngz)
    args = [akj__dgwbm, context.get_dummy_value(), ojkv__ecyif]
    jxg__wbwt = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        bvk__kueln, cktt__cfzu = c.pyapi.call_jit_code(jxg__wbwt,
            cyzk__gapr, args)
    else:
        cktt__cfzu = context.compile_internal(builder, jxg__wbwt,
            cyzk__gapr, args)
    return cktt__cfzu


def is_ll_eq(builder, val1, val2):
    rffg__zhn = val1.type.pointee
    jxrio__zeuy = val2.type.pointee
    assert rffg__zhn == jxrio__zeuy, 'invalid llvm value comparison'
    if isinstance(rffg__zhn, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(rffg__zhn.elements) if isinstance(rffg__zhn, lir.
            BaseStructType) else rffg__zhn.count
        ukfz__xpsdc = lir.Constant(lir.IntType(1), 1)
        for abej__bgi in range(n_elems):
            jxv__gjb = lir.IntType(32)(0)
            ypnu__jwheo = lir.IntType(32)(abej__bgi)
            ubog__ynf = builder.gep(val1, [jxv__gjb, ypnu__jwheo], inbounds
                =True)
            jbm__lxmdp = builder.gep(val2, [jxv__gjb, ypnu__jwheo],
                inbounds=True)
            ukfz__xpsdc = builder.and_(ukfz__xpsdc, is_ll_eq(builder,
                ubog__ynf, jbm__lxmdp))
        return ukfz__xpsdc
    lfhxj__sikks = builder.load(val1)
    zmob__ehezf = builder.load(val2)
    if lfhxj__sikks.type in (lir.FloatType(), lir.DoubleType()):
        nrtu__mludg = 32 if lfhxj__sikks.type == lir.FloatType() else 64
        lfhxj__sikks = builder.bitcast(lfhxj__sikks, lir.IntType(nrtu__mludg))
        zmob__ehezf = builder.bitcast(zmob__ehezf, lir.IntType(nrtu__mludg))
    return builder.icmp_unsigned('==', lfhxj__sikks, zmob__ehezf)
