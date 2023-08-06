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
    engel__quh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    uszss__aeafc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    eoy__jtft = builder.gep(null_bitmap_ptr, [engel__quh], inbounds=True)
    pwsn__yytmg = builder.load(eoy__jtft)
    jtcx__gce = lir.ArrayType(lir.IntType(8), 8)
    iqqan__rgtv = cgutils.alloca_once_value(builder, lir.Constant(jtcx__gce,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    faeb__soaky = builder.load(builder.gep(iqqan__rgtv, [lir.Constant(lir.
        IntType(64), 0), uszss__aeafc], inbounds=True))
    if val:
        builder.store(builder.or_(pwsn__yytmg, faeb__soaky), eoy__jtft)
    else:
        faeb__soaky = builder.xor(faeb__soaky, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(pwsn__yytmg, faeb__soaky), eoy__jtft)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    engel__quh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    uszss__aeafc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    pwsn__yytmg = builder.load(builder.gep(null_bitmap_ptr, [engel__quh],
        inbounds=True))
    jtcx__gce = lir.ArrayType(lir.IntType(8), 8)
    iqqan__rgtv = cgutils.alloca_once_value(builder, lir.Constant(jtcx__gce,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    faeb__soaky = builder.load(builder.gep(iqqan__rgtv, [lir.Constant(lir.
        IntType(64), 0), uszss__aeafc], inbounds=True))
    return builder.and_(pwsn__yytmg, faeb__soaky)


def pyarray_check(builder, context, obj):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    urfcz__jrrq = lir.FunctionType(lir.IntType(32), [mpx__dzvmb])
    xvb__zys = cgutils.get_or_insert_function(builder.module, urfcz__jrrq,
        name='is_np_array')
    return builder.call(xvb__zys, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    dbcs__tdf = context.get_value_type(types.intp)
    cnx__xadhj = lir.FunctionType(lir.IntType(8).as_pointer(), [mpx__dzvmb,
        dbcs__tdf])
    pzq__ufazq = cgutils.get_or_insert_function(builder.module, cnx__xadhj,
        name='array_getptr1')
    pbr__xfi = lir.FunctionType(mpx__dzvmb, [mpx__dzvmb, lir.IntType(8).
        as_pointer()])
    iwh__kvdgf = cgutils.get_or_insert_function(builder.module, pbr__xfi,
        name='array_getitem')
    uswgz__qdd = builder.call(pzq__ufazq, [arr_obj, ind])
    return builder.call(iwh__kvdgf, [arr_obj, uswgz__qdd])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    dbcs__tdf = context.get_value_type(types.intp)
    cnx__xadhj = lir.FunctionType(lir.IntType(8).as_pointer(), [mpx__dzvmb,
        dbcs__tdf])
    pzq__ufazq = cgutils.get_or_insert_function(builder.module, cnx__xadhj,
        name='array_getptr1')
    bgbw__mgcx = lir.FunctionType(lir.VoidType(), [mpx__dzvmb, lir.IntType(
        8).as_pointer(), mpx__dzvmb])
    qsrnn__aqe = cgutils.get_or_insert_function(builder.module, bgbw__mgcx,
        name='array_setitem')
    uswgz__qdd = builder.call(pzq__ufazq, [arr_obj, ind])
    builder.call(qsrnn__aqe, [arr_obj, uswgz__qdd, val_obj])


def seq_getitem(builder, context, obj, ind):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    dbcs__tdf = context.get_value_type(types.intp)
    fliaa__ztlr = lir.FunctionType(mpx__dzvmb, [mpx__dzvmb, dbcs__tdf])
    qmd__shrp = cgutils.get_or_insert_function(builder.module, fliaa__ztlr,
        name='seq_getitem')
    return builder.call(qmd__shrp, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    ivssi__biiyc = lir.FunctionType(lir.IntType(32), [mpx__dzvmb, mpx__dzvmb])
    ydujo__yejum = cgutils.get_or_insert_function(builder.module,
        ivssi__biiyc, name='is_na_value')
    return builder.call(ydujo__yejum, [val, C_NA])


def list_check(builder, context, obj):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    agm__bxw = context.get_value_type(types.int32)
    ejc__dwa = lir.FunctionType(agm__bxw, [mpx__dzvmb])
    bmk__fmbwk = cgutils.get_or_insert_function(builder.module, ejc__dwa,
        name='list_check')
    return builder.call(bmk__fmbwk, [obj])


def dict_keys(builder, context, obj):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    ejc__dwa = lir.FunctionType(mpx__dzvmb, [mpx__dzvmb])
    bmk__fmbwk = cgutils.get_or_insert_function(builder.module, ejc__dwa,
        name='dict_keys')
    return builder.call(bmk__fmbwk, [obj])


def dict_values(builder, context, obj):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    ejc__dwa = lir.FunctionType(mpx__dzvmb, [mpx__dzvmb])
    bmk__fmbwk = cgutils.get_or_insert_function(builder.module, ejc__dwa,
        name='dict_values')
    return builder.call(bmk__fmbwk, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    mpx__dzvmb = context.get_argument_type(types.pyobject)
    ejc__dwa = lir.FunctionType(lir.VoidType(), [mpx__dzvmb, mpx__dzvmb])
    bmk__fmbwk = cgutils.get_or_insert_function(builder.module, ejc__dwa,
        name='dict_merge_from_seq2')
    builder.call(bmk__fmbwk, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    hkxl__tpqfs = cgutils.alloca_once_value(builder, val)
    upmld__sbi = list_check(builder, context, val)
    oys__qzyo = builder.icmp_unsigned('!=', upmld__sbi, lir.Constant(
        upmld__sbi.type, 0))
    with builder.if_then(oys__qzyo):
        oqcm__wvql = context.insert_const_string(builder.module, 'numpy')
        wdk__fkzb = c.pyapi.import_module_noblock(oqcm__wvql)
        dtkzm__vrf = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            dtkzm__vrf = str(typ.dtype)
        hop__bbkt = c.pyapi.object_getattr_string(wdk__fkzb, dtkzm__vrf)
        bmfht__yhgeq = builder.load(hkxl__tpqfs)
        ilm__nrt = c.pyapi.call_method(wdk__fkzb, 'asarray', (bmfht__yhgeq,
            hop__bbkt))
        builder.store(ilm__nrt, hkxl__tpqfs)
        c.pyapi.decref(wdk__fkzb)
        c.pyapi.decref(hop__bbkt)
    val = builder.load(hkxl__tpqfs)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        xzi__mpq = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        mxyby__myt, emu__ybwtf = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [xzi__mpq])
        context.nrt.decref(builder, typ, xzi__mpq)
        return cgutils.pack_array(builder, [emu__ybwtf])
    if isinstance(typ, (StructType, types.BaseTuple)):
        oqcm__wvql = context.insert_const_string(builder.module, 'pandas')
        isxxy__epq = c.pyapi.import_module_noblock(oqcm__wvql)
        C_NA = c.pyapi.object_getattr_string(isxxy__epq, 'NA')
        znbqy__moxxt = bodo.utils.transform.get_type_alloc_counts(typ)
        dvlyt__rwyoq = context.make_tuple(builder, types.Tuple(znbqy__moxxt *
            [types.int64]), znbqy__moxxt * [context.get_constant(types.
            int64, 0)])
        gdpe__kalg = cgutils.alloca_once_value(builder, dvlyt__rwyoq)
        zqoo__nciu = 0
        ntdcb__vktvc = typ.data if isinstance(typ, StructType) else typ.types
        for mik__tedj, t in enumerate(ntdcb__vktvc):
            fxfp__vbcbm = bodo.utils.transform.get_type_alloc_counts(t)
            if fxfp__vbcbm == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    mik__tedj])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, mik__tedj)
            eti__aib = is_na_value(builder, context, val_obj, C_NA)
            phl__mdm = builder.icmp_unsigned('!=', eti__aib, lir.Constant(
                eti__aib.type, 1))
            with builder.if_then(phl__mdm):
                dvlyt__rwyoq = builder.load(gdpe__kalg)
                bnwr__aay = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for mik__tedj in range(fxfp__vbcbm):
                    griv__vgi = builder.extract_value(dvlyt__rwyoq, 
                        zqoo__nciu + mik__tedj)
                    onmwn__nwlm = builder.extract_value(bnwr__aay, mik__tedj)
                    dvlyt__rwyoq = builder.insert_value(dvlyt__rwyoq,
                        builder.add(griv__vgi, onmwn__nwlm), zqoo__nciu +
                        mik__tedj)
                builder.store(dvlyt__rwyoq, gdpe__kalg)
            zqoo__nciu += fxfp__vbcbm
        c.pyapi.decref(isxxy__epq)
        c.pyapi.decref(C_NA)
        return builder.load(gdpe__kalg)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    oqcm__wvql = context.insert_const_string(builder.module, 'pandas')
    isxxy__epq = c.pyapi.import_module_noblock(oqcm__wvql)
    C_NA = c.pyapi.object_getattr_string(isxxy__epq, 'NA')
    znbqy__moxxt = bodo.utils.transform.get_type_alloc_counts(typ)
    dvlyt__rwyoq = context.make_tuple(builder, types.Tuple(znbqy__moxxt * [
        types.int64]), [n] + (znbqy__moxxt - 1) * [context.get_constant(
        types.int64, 0)])
    gdpe__kalg = cgutils.alloca_once_value(builder, dvlyt__rwyoq)
    with cgutils.for_range(builder, n) as jwtp__hbg:
        kzvqr__waojl = jwtp__hbg.index
        puxww__rji = seq_getitem(builder, context, arr_obj, kzvqr__waojl)
        eti__aib = is_na_value(builder, context, puxww__rji, C_NA)
        phl__mdm = builder.icmp_unsigned('!=', eti__aib, lir.Constant(
            eti__aib.type, 1))
        with builder.if_then(phl__mdm):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                dvlyt__rwyoq = builder.load(gdpe__kalg)
                bnwr__aay = get_array_elem_counts(c, builder, context,
                    puxww__rji, typ.dtype)
                for mik__tedj in range(znbqy__moxxt - 1):
                    griv__vgi = builder.extract_value(dvlyt__rwyoq, 
                        mik__tedj + 1)
                    onmwn__nwlm = builder.extract_value(bnwr__aay, mik__tedj)
                    dvlyt__rwyoq = builder.insert_value(dvlyt__rwyoq,
                        builder.add(griv__vgi, onmwn__nwlm), mik__tedj + 1)
                builder.store(dvlyt__rwyoq, gdpe__kalg)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                zqoo__nciu = 1
                for mik__tedj, t in enumerate(typ.data):
                    fxfp__vbcbm = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if fxfp__vbcbm == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(puxww__rji, mik__tedj)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(puxww__rji,
                            typ.names[mik__tedj])
                    eti__aib = is_na_value(builder, context, val_obj, C_NA)
                    phl__mdm = builder.icmp_unsigned('!=', eti__aib, lir.
                        Constant(eti__aib.type, 1))
                    with builder.if_then(phl__mdm):
                        dvlyt__rwyoq = builder.load(gdpe__kalg)
                        bnwr__aay = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for mik__tedj in range(fxfp__vbcbm):
                            griv__vgi = builder.extract_value(dvlyt__rwyoq,
                                zqoo__nciu + mik__tedj)
                            onmwn__nwlm = builder.extract_value(bnwr__aay,
                                mik__tedj)
                            dvlyt__rwyoq = builder.insert_value(dvlyt__rwyoq,
                                builder.add(griv__vgi, onmwn__nwlm), 
                                zqoo__nciu + mik__tedj)
                        builder.store(dvlyt__rwyoq, gdpe__kalg)
                    zqoo__nciu += fxfp__vbcbm
            else:
                assert isinstance(typ, MapArrayType), typ
                dvlyt__rwyoq = builder.load(gdpe__kalg)
                nvto__zsxl = dict_keys(builder, context, puxww__rji)
                mjnzv__mgk = dict_values(builder, context, puxww__rji)
                omb__knmth = get_array_elem_counts(c, builder, context,
                    nvto__zsxl, typ.key_arr_type)
                dmxx__kjzba = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for mik__tedj in range(1, dmxx__kjzba + 1):
                    griv__vgi = builder.extract_value(dvlyt__rwyoq, mik__tedj)
                    onmwn__nwlm = builder.extract_value(omb__knmth, 
                        mik__tedj - 1)
                    dvlyt__rwyoq = builder.insert_value(dvlyt__rwyoq,
                        builder.add(griv__vgi, onmwn__nwlm), mik__tedj)
                fwv__qdj = get_array_elem_counts(c, builder, context,
                    mjnzv__mgk, typ.value_arr_type)
                for mik__tedj in range(dmxx__kjzba + 1, znbqy__moxxt):
                    griv__vgi = builder.extract_value(dvlyt__rwyoq, mik__tedj)
                    onmwn__nwlm = builder.extract_value(fwv__qdj, mik__tedj -
                        dmxx__kjzba)
                    dvlyt__rwyoq = builder.insert_value(dvlyt__rwyoq,
                        builder.add(griv__vgi, onmwn__nwlm), mik__tedj)
                builder.store(dvlyt__rwyoq, gdpe__kalg)
                c.pyapi.decref(nvto__zsxl)
                c.pyapi.decref(mjnzv__mgk)
        c.pyapi.decref(puxww__rji)
    c.pyapi.decref(isxxy__epq)
    c.pyapi.decref(C_NA)
    return builder.load(gdpe__kalg)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    hqc__joipk = n_elems.type.count
    assert hqc__joipk >= 1
    atx__sllls = builder.extract_value(n_elems, 0)
    if hqc__joipk != 1:
        fdbbe__xpuo = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, mik__tedj) for mik__tedj in range(1, hqc__joipk)])
        tnq__dxshr = types.Tuple([types.int64] * (hqc__joipk - 1))
    else:
        fdbbe__xpuo = context.get_dummy_value()
        tnq__dxshr = types.none
    klw__njyd = types.TypeRef(arr_type)
    xxvo__osag = arr_type(types.int64, klw__njyd, tnq__dxshr)
    args = [atx__sllls, context.get_dummy_value(), fdbbe__xpuo]
    nvvv__uuzxd = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        mxyby__myt, sdub__wtjwq = c.pyapi.call_jit_code(nvvv__uuzxd,
            xxvo__osag, args)
    else:
        sdub__wtjwq = context.compile_internal(builder, nvvv__uuzxd,
            xxvo__osag, args)
    return sdub__wtjwq


def is_ll_eq(builder, val1, val2):
    ujpgz__kznz = val1.type.pointee
    kkttf__jzuqx = val2.type.pointee
    assert ujpgz__kznz == kkttf__jzuqx, 'invalid llvm value comparison'
    if isinstance(ujpgz__kznz, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(ujpgz__kznz.elements) if isinstance(ujpgz__kznz, lir.
            BaseStructType) else ujpgz__kznz.count
        pcl__maq = lir.Constant(lir.IntType(1), 1)
        for mik__tedj in range(n_elems):
            xrx__feg = lir.IntType(32)(0)
            aptqg__hharv = lir.IntType(32)(mik__tedj)
            fwap__nmx = builder.gep(val1, [xrx__feg, aptqg__hharv],
                inbounds=True)
            bug__fpsry = builder.gep(val2, [xrx__feg, aptqg__hharv],
                inbounds=True)
            pcl__maq = builder.and_(pcl__maq, is_ll_eq(builder, fwap__nmx,
                bug__fpsry))
        return pcl__maq
    rzca__emng = builder.load(val1)
    uugyt__ujtgs = builder.load(val2)
    if rzca__emng.type in (lir.FloatType(), lir.DoubleType()):
        utt__owcyd = 32 if rzca__emng.type == lir.FloatType() else 64
        rzca__emng = builder.bitcast(rzca__emng, lir.IntType(utt__owcyd))
        uugyt__ujtgs = builder.bitcast(uugyt__ujtgs, lir.IntType(utt__owcyd))
    return builder.icmp_unsigned('==', rzca__emng, uugyt__ujtgs)
