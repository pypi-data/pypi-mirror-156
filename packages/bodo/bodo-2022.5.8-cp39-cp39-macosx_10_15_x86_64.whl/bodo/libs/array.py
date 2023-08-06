"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import intrinsic, models, register_model
from numba.np.arrayobj import _getitem_array_single_int
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, get_categories_int_type
from bodo.libs import array_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, define_array_item_dtor, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType, int128_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType, _get_map_arr_data_type, init_map_arr_codegen
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, char_arr_type, null_bitmap_arr_type, offset_arr_type, string_array_type
from bodo.libs.struct_arr_ext import StructArrayPayloadType, StructArrayType, StructType, _get_struct_arr_payload, define_struct_arr_dtor
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, is_str_arr_type, raise_bodo_error
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('dict_str_array_to_info', array_ext.dict_str_array_to_info)
ll.add_symbol('get_nested_info', array_ext.get_nested_info)
ll.add_symbol('get_has_global_dictionary', array_ext.get_has_global_dictionary)
ll.add_symbol('numpy_array_to_info', array_ext.numpy_array_to_info)
ll.add_symbol('categorical_array_to_info', array_ext.categorical_array_to_info)
ll.add_symbol('nullable_array_to_info', array_ext.nullable_array_to_info)
ll.add_symbol('interval_array_to_info', array_ext.interval_array_to_info)
ll.add_symbol('decimal_array_to_info', array_ext.decimal_array_to_info)
ll.add_symbol('info_to_nested_array', array_ext.info_to_nested_array)
ll.add_symbol('info_to_list_string_array', array_ext.info_to_list_string_array)
ll.add_symbol('info_to_string_array', array_ext.info_to_string_array)
ll.add_symbol('info_to_numpy_array', array_ext.info_to_numpy_array)
ll.add_symbol('info_to_nullable_array', array_ext.info_to_nullable_array)
ll.add_symbol('info_to_interval_array', array_ext.info_to_interval_array)
ll.add_symbol('alloc_numpy', array_ext.alloc_numpy)
ll.add_symbol('alloc_string_array', array_ext.alloc_string_array)
ll.add_symbol('arr_info_list_to_table', array_ext.arr_info_list_to_table)
ll.add_symbol('info_from_table', array_ext.info_from_table)
ll.add_symbol('delete_info_decref_array', array_ext.delete_info_decref_array)
ll.add_symbol('delete_table_decref_arrays', array_ext.
    delete_table_decref_arrays)
ll.add_symbol('delete_table', array_ext.delete_table)
ll.add_symbol('shuffle_table', array_ext.shuffle_table)
ll.add_symbol('get_shuffle_info', array_ext.get_shuffle_info)
ll.add_symbol('delete_shuffle_info', array_ext.delete_shuffle_info)
ll.add_symbol('reverse_shuffle_table', array_ext.reverse_shuffle_table)
ll.add_symbol('hash_join_table', array_ext.hash_join_table)
ll.add_symbol('drop_duplicates_table', array_ext.drop_duplicates_table)
ll.add_symbol('sort_values_table', array_ext.sort_values_table)
ll.add_symbol('sample_table', array_ext.sample_table)
ll.add_symbol('shuffle_renormalization', array_ext.shuffle_renormalization)
ll.add_symbol('shuffle_renormalization_group', array_ext.
    shuffle_renormalization_group)
ll.add_symbol('groupby_and_aggregate', array_ext.groupby_and_aggregate)
ll.add_symbol('pivot_groupby_and_aggregate', array_ext.
    pivot_groupby_and_aggregate)
ll.add_symbol('get_groupby_labels', array_ext.get_groupby_labels)
ll.add_symbol('array_isin', array_ext.array_isin)
ll.add_symbol('get_search_regex', array_ext.get_search_regex)
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)
ll.add_symbol('array_info_getdata1', array_ext.array_info_getdata1)


class ArrayInfoType(types.Type):

    def __init__(self):
        super(ArrayInfoType, self).__init__(name='ArrayInfoType()')


array_info_type = ArrayInfoType()
register_model(ArrayInfoType)(models.OpaqueModel)


class TableTypeCPP(types.Type):

    def __init__(self):
        super(TableTypeCPP, self).__init__(name='TableTypeCPP()')


table_type = TableTypeCPP()
register_model(TableTypeCPP)(models.OpaqueModel)


@intrinsic
def array_to_info(typingctx, arr_type_t=None):
    return array_info_type(arr_type_t), array_to_info_codegen


def array_to_info_codegen(context, builder, sig, args, incref=True):
    in_arr, = args
    arr_type = sig.args[0]
    if incref:
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, TupleArrayType):
        xqn__qbqma = context.make_helper(builder, arr_type, in_arr)
        in_arr = xqn__qbqma.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        otgkx__klqu = context.make_helper(builder, arr_type, in_arr)
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='list_string_array_to_info')
        return builder.call(znum__ezf, [otgkx__klqu.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                vigr__bsq = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for xdu__phn in arr_typ.data:
                    vigr__bsq += get_types(xdu__phn)
                return vigr__bsq
            elif isinstance(arr_typ, (types.Array, IntegerArrayType)
                ) or arr_typ == boolean_array:
                return get_types(arr_typ.dtype)
            elif arr_typ == string_array_type:
                return [CTypeEnum.STRING.value]
            elif arr_typ == binary_array_type:
                return [CTypeEnum.BINARY.value]
            elif isinstance(arr_typ, DecimalArrayType):
                return [CTypeEnum.Decimal.value, arr_typ.precision, arr_typ
                    .scale]
            else:
                return [numba_to_c_type(arr_typ)]

        def get_lengths(arr_typ, arr):
            hhdgu__ukjl = context.compile_internal(builder, lambda a: len(a
                ), types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                fsr__kyoy = context.make_helper(builder, arr_typ, value=arr)
                cnmy__tsw = get_lengths(_get_map_arr_data_type(arr_typ),
                    fsr__kyoy.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ult__owly = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                cnmy__tsw = get_lengths(arr_typ.dtype, ult__owly.data)
                cnmy__tsw = cgutils.pack_array(builder, [ult__owly.n_arrays
                    ] + [builder.extract_value(cnmy__tsw, kxp__ghj) for
                    kxp__ghj in range(cnmy__tsw.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ult__owly = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                cnmy__tsw = []
                for kxp__ghj, xdu__phn in enumerate(arr_typ.data):
                    ntsx__mxtos = get_lengths(xdu__phn, builder.
                        extract_value(ult__owly.data, kxp__ghj))
                    cnmy__tsw += [builder.extract_value(ntsx__mxtos,
                        vym__ost) for vym__ost in range(ntsx__mxtos.type.count)
                        ]
                cnmy__tsw = cgutils.pack_array(builder, [hhdgu__ukjl,
                    context.get_constant(types.int64, -1)] + cnmy__tsw)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                cnmy__tsw = cgutils.pack_array(builder, [hhdgu__ukjl])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return cnmy__tsw

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                fsr__kyoy = context.make_helper(builder, arr_typ, value=arr)
                cwmw__kfm = get_buffers(_get_map_arr_data_type(arr_typ),
                    fsr__kyoy.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ult__owly = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                hwb__ytlq = get_buffers(arr_typ.dtype, ult__owly.data)
                libd__zjmbc = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, ult__owly.offsets)
                vplq__hqpc = builder.bitcast(libd__zjmbc.data, lir.IntType(
                    8).as_pointer())
                dipg__nnl = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, ult__owly.null_bitmap)
                uxmr__gtctx = builder.bitcast(dipg__nnl.data, lir.IntType(8
                    ).as_pointer())
                cwmw__kfm = cgutils.pack_array(builder, [vplq__hqpc,
                    uxmr__gtctx] + [builder.extract_value(hwb__ytlq,
                    kxp__ghj) for kxp__ghj in range(hwb__ytlq.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ult__owly = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                hwb__ytlq = []
                for kxp__ghj, xdu__phn in enumerate(arr_typ.data):
                    hzj__pxflb = get_buffers(xdu__phn, builder.
                        extract_value(ult__owly.data, kxp__ghj))
                    hwb__ytlq += [builder.extract_value(hzj__pxflb,
                        vym__ost) for vym__ost in range(hzj__pxflb.type.count)]
                dipg__nnl = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, ult__owly.null_bitmap)
                uxmr__gtctx = builder.bitcast(dipg__nnl.data, lir.IntType(8
                    ).as_pointer())
                cwmw__kfm = cgutils.pack_array(builder, [uxmr__gtctx] +
                    hwb__ytlq)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                ivq__wqqzb = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    ivq__wqqzb = int128_type
                elif arr_typ == datetime_date_array_type:
                    ivq__wqqzb = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                adnzw__hxy = context.make_array(types.Array(ivq__wqqzb, 1, 'C')
                    )(context, builder, arr.data)
                dipg__nnl = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                hpx__dwps = builder.bitcast(adnzw__hxy.data, lir.IntType(8)
                    .as_pointer())
                uxmr__gtctx = builder.bitcast(dipg__nnl.data, lir.IntType(8
                    ).as_pointer())
                cwmw__kfm = cgutils.pack_array(builder, [uxmr__gtctx,
                    hpx__dwps])
            elif arr_typ in (string_array_type, binary_array_type):
                ult__owly = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                qagkb__nlfa = context.make_helper(builder, offset_arr_type,
                    ult__owly.offsets).data
                dyn__orepd = context.make_helper(builder, char_arr_type,
                    ult__owly.data).data
                jtiyd__eteq = context.make_helper(builder,
                    null_bitmap_arr_type, ult__owly.null_bitmap).data
                cwmw__kfm = cgutils.pack_array(builder, [builder.bitcast(
                    qagkb__nlfa, lir.IntType(8).as_pointer()), builder.
                    bitcast(jtiyd__eteq, lir.IntType(8).as_pointer()),
                    builder.bitcast(dyn__orepd, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                hpx__dwps = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                gqp__epnz = lir.Constant(lir.IntType(8).as_pointer(), None)
                cwmw__kfm = cgutils.pack_array(builder, [gqp__epnz, hpx__dwps])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return cwmw__kfm

        def get_field_names(arr_typ):
            voxu__evhgh = []
            if isinstance(arr_typ, StructArrayType):
                for paz__nhz, ivkhi__knon in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    voxu__evhgh.append(paz__nhz)
                    voxu__evhgh += get_field_names(ivkhi__knon)
            elif isinstance(arr_typ, ArrayItemArrayType):
                voxu__evhgh += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                voxu__evhgh += get_field_names(_get_map_arr_data_type(arr_typ))
            return voxu__evhgh
        vigr__bsq = get_types(arr_type)
        daz__clm = cgutils.pack_array(builder, [context.get_constant(types.
            int32, t) for t in vigr__bsq])
        wxsbv__obie = cgutils.alloca_once_value(builder, daz__clm)
        cnmy__tsw = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, cnmy__tsw)
        cwmw__kfm = get_buffers(arr_type, in_arr)
        cybwb__mirq = cgutils.alloca_once_value(builder, cwmw__kfm)
        voxu__evhgh = get_field_names(arr_type)
        if len(voxu__evhgh) == 0:
            voxu__evhgh = ['irrelevant']
        xid__exlt = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in voxu__evhgh])
        huyb__daxe = cgutils.alloca_once_value(builder, xid__exlt)
        if isinstance(arr_type, MapArrayType):
            yowga__xaj = _get_map_arr_data_type(arr_type)
            vqq__jnv = context.make_helper(builder, arr_type, value=in_arr)
            vzud__mnumb = vqq__jnv.data
        else:
            yowga__xaj = arr_type
            vzud__mnumb = in_arr
        ccyqb__pdx = context.make_helper(builder, yowga__xaj, vzud__mnumb)
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='nested_array_to_info')
        wygl__znaao = builder.call(znum__ezf, [builder.bitcast(wxsbv__obie,
            lir.IntType(32).as_pointer()), builder.bitcast(cybwb__mirq, lir
            .IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            huyb__daxe, lir.IntType(8).as_pointer()), ccyqb__pdx.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    if arr_type in (string_array_type, binary_array_type):
        pss__figtp = context.make_helper(builder, arr_type, in_arr)
        gfq__tyj = ArrayItemArrayType(char_arr_type)
        otgkx__klqu = context.make_helper(builder, gfq__tyj, pss__figtp.data)
        ult__owly = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        qagkb__nlfa = context.make_helper(builder, offset_arr_type,
            ult__owly.offsets).data
        dyn__orepd = context.make_helper(builder, char_arr_type, ult__owly.data
            ).data
        jtiyd__eteq = context.make_helper(builder, null_bitmap_arr_type,
            ult__owly.null_bitmap).data
        lizpm__mzqfv = builder.zext(builder.load(builder.gep(qagkb__nlfa, [
            ult__owly.n_arrays])), lir.IntType(64))
        ociw__iutgf = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='string_array_to_info')
        return builder.call(znum__ezf, [ult__owly.n_arrays, lizpm__mzqfv,
            dyn__orepd, qagkb__nlfa, jtiyd__eteq, otgkx__klqu.meminfo,
            ociw__iutgf])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        rnh__ioid = arr.data
        dsj__cve = arr.indices
        sig = array_info_type(arr_type.data)
        vwif__dcsoz = array_to_info_codegen(context, builder, sig, (
            rnh__ioid,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        xjnn__klt = array_to_info_codegen(context, builder, sig, (dsj__cve,
            ), False)
        kjaf__vosba = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, dsj__cve)
        uxmr__gtctx = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, kjaf__vosba.null_bitmap).data
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='dict_str_array_to_info')
        jxl__goydv = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(znum__ezf, [vwif__dcsoz, xjnn__klt, builder.
            bitcast(uxmr__gtctx, lir.IntType(8).as_pointer()), jxl__goydv])
    rmcx__vjw = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        vlkry__xwrrd = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        aeh__amhio = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(aeh__amhio, 1, 'C')
        rmcx__vjw = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if rmcx__vjw:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        hhdgu__ukjl = builder.extract_value(arr.shape, 0)
        pnp__nfrip = arr_type.dtype
        zrq__pecw = numba_to_c_type(pnp__nfrip)
        xkpb__pzyte = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zrq__pecw))
        if rmcx__vjw:
            oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            znum__ezf = cgutils.get_or_insert_function(builder.module,
                oddaf__koeu, name='categorical_array_to_info')
            return builder.call(znum__ezf, [hhdgu__ukjl, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                xkpb__pzyte), vlkry__xwrrd, arr.meminfo])
        else:
            oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            znum__ezf = cgutils.get_or_insert_function(builder.module,
                oddaf__koeu, name='numpy_array_to_info')
            return builder.call(znum__ezf, [hhdgu__ukjl, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                xkpb__pzyte), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        pnp__nfrip = arr_type.dtype
        ivq__wqqzb = pnp__nfrip
        if isinstance(arr_type, DecimalArrayType):
            ivq__wqqzb = int128_type
        if arr_type == datetime_date_array_type:
            ivq__wqqzb = types.int64
        adnzw__hxy = context.make_array(types.Array(ivq__wqqzb, 1, 'C'))(
            context, builder, arr.data)
        hhdgu__ukjl = builder.extract_value(adnzw__hxy.shape, 0)
        wnja__edie = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        zrq__pecw = numba_to_c_type(pnp__nfrip)
        xkpb__pzyte = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zrq__pecw))
        if isinstance(arr_type, DecimalArrayType):
            oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            znum__ezf = cgutils.get_or_insert_function(builder.module,
                oddaf__koeu, name='decimal_array_to_info')
            return builder.call(znum__ezf, [hhdgu__ukjl, builder.bitcast(
                adnzw__hxy.data, lir.IntType(8).as_pointer()), builder.load
                (xkpb__pzyte), builder.bitcast(wnja__edie.data, lir.IntType
                (8).as_pointer()), adnzw__hxy.meminfo, wnja__edie.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            znum__ezf = cgutils.get_or_insert_function(builder.module,
                oddaf__koeu, name='nullable_array_to_info')
            return builder.call(znum__ezf, [hhdgu__ukjl, builder.bitcast(
                adnzw__hxy.data, lir.IntType(8).as_pointer()), builder.load
                (xkpb__pzyte), builder.bitcast(wnja__edie.data, lir.IntType
                (8).as_pointer()), adnzw__hxy.meminfo, wnja__edie.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        zrb__ibj = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        oknpd__ljtfo = context.make_array(arr_type.arr_type)(context,
            builder, arr.right)
        hhdgu__ukjl = builder.extract_value(zrb__ibj.shape, 0)
        zrq__pecw = numba_to_c_type(arr_type.arr_type.dtype)
        xkpb__pzyte = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zrq__pecw))
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='interval_array_to_info')
        return builder.call(znum__ezf, [hhdgu__ukjl, builder.bitcast(
            zrb__ibj.data, lir.IntType(8).as_pointer()), builder.bitcast(
            oknpd__ljtfo.data, lir.IntType(8).as_pointer()), builder.load(
            xkpb__pzyte), zrb__ibj.meminfo, oknpd__ljtfo.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    hrec__rhss = cgutils.alloca_once(builder, lir.IntType(64))
    hpx__dwps = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    hovi__gsr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    znum__ezf = cgutils.get_or_insert_function(builder.module, oddaf__koeu,
        name='info_to_numpy_array')
    builder.call(znum__ezf, [in_info, hrec__rhss, hpx__dwps, hovi__gsr])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    rgf__mtqz = context.get_value_type(types.intp)
    ynel__upn = cgutils.pack_array(builder, [builder.load(hrec__rhss)], ty=
        rgf__mtqz)
    wox__lbkr = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    tja__ajoni = cgutils.pack_array(builder, [wox__lbkr], ty=rgf__mtqz)
    dyn__orepd = builder.bitcast(builder.load(hpx__dwps), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=dyn__orepd, shape=ynel__upn,
        strides=tja__ajoni, itemsize=wox__lbkr, meminfo=builder.load(hovi__gsr)
        )
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    bes__zxr = context.make_helper(builder, arr_type)
    oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    znum__ezf = cgutils.get_or_insert_function(builder.module, oddaf__koeu,
        name='info_to_list_string_array')
    builder.call(znum__ezf, [in_info, bes__zxr._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return bes__zxr._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    juwo__toym = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        agt__mpb = lengths_pos
        dabgb__jof = infos_pos
        pnu__sulwy, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        bnan__uqoo = ArrayItemArrayPayloadType(arr_typ)
        kvgk__byjr = context.get_data_type(bnan__uqoo)
        wyps__rwk = context.get_abi_sizeof(kvgk__byjr)
        hnh__izq = define_array_item_dtor(context, builder, arr_typ, bnan__uqoo
            )
        dccaf__dfwt = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, wyps__rwk), hnh__izq)
        tik__mle = context.nrt.meminfo_data(builder, dccaf__dfwt)
        kbsty__ommvd = builder.bitcast(tik__mle, kvgk__byjr.as_pointer())
        ult__owly = cgutils.create_struct_proxy(bnan__uqoo)(context, builder)
        ult__owly.n_arrays = builder.extract_value(builder.load(lengths_ptr
            ), agt__mpb)
        ult__owly.data = pnu__sulwy
        sgokf__gpv = builder.load(array_infos_ptr)
        kylbg__eqal = builder.bitcast(builder.extract_value(sgokf__gpv,
            dabgb__jof), juwo__toym)
        ult__owly.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, kylbg__eqal)
        gnt__ahjy = builder.bitcast(builder.extract_value(sgokf__gpv, 
            dabgb__jof + 1), juwo__toym)
        ult__owly.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, gnt__ahjy)
        builder.store(ult__owly._getvalue(), kbsty__ommvd)
        otgkx__klqu = context.make_helper(builder, arr_typ)
        otgkx__klqu.meminfo = dccaf__dfwt
        return otgkx__klqu._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        mxb__pavli = []
        dabgb__jof = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for rybda__mifr in arr_typ.data:
            pnu__sulwy, lengths_pos, infos_pos = nested_to_array(context,
                builder, rybda__mifr, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            mxb__pavli.append(pnu__sulwy)
        bnan__uqoo = StructArrayPayloadType(arr_typ.data)
        kvgk__byjr = context.get_value_type(bnan__uqoo)
        wyps__rwk = context.get_abi_sizeof(kvgk__byjr)
        hnh__izq = define_struct_arr_dtor(context, builder, arr_typ, bnan__uqoo
            )
        dccaf__dfwt = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, wyps__rwk), hnh__izq)
        tik__mle = context.nrt.meminfo_data(builder, dccaf__dfwt)
        kbsty__ommvd = builder.bitcast(tik__mle, kvgk__byjr.as_pointer())
        ult__owly = cgutils.create_struct_proxy(bnan__uqoo)(context, builder)
        ult__owly.data = cgutils.pack_array(builder, mxb__pavli
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, mxb__pavli)
        sgokf__gpv = builder.load(array_infos_ptr)
        gnt__ahjy = builder.bitcast(builder.extract_value(sgokf__gpv,
            dabgb__jof), juwo__toym)
        ult__owly.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, gnt__ahjy)
        builder.store(ult__owly._getvalue(), kbsty__ommvd)
        qspxl__uev = context.make_helper(builder, arr_typ)
        qspxl__uev.meminfo = dccaf__dfwt
        return qspxl__uev._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        sgokf__gpv = builder.load(array_infos_ptr)
        yxxa__ndj = builder.bitcast(builder.extract_value(sgokf__gpv,
            infos_pos), juwo__toym)
        pss__figtp = context.make_helper(builder, arr_typ)
        gfq__tyj = ArrayItemArrayType(char_arr_type)
        otgkx__klqu = context.make_helper(builder, gfq__tyj)
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_to_string_array')
        builder.call(znum__ezf, [yxxa__ndj, otgkx__klqu._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        pss__figtp.data = otgkx__klqu._getvalue()
        return pss__figtp._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        sgokf__gpv = builder.load(array_infos_ptr)
        hkg__ahx = builder.bitcast(builder.extract_value(sgokf__gpv, 
            infos_pos + 1), juwo__toym)
        return _lower_info_to_array_numpy(arr_typ, context, builder, hkg__ahx
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        ivq__wqqzb = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            ivq__wqqzb = int128_type
        elif arr_typ == datetime_date_array_type:
            ivq__wqqzb = types.int64
        sgokf__gpv = builder.load(array_infos_ptr)
        gnt__ahjy = builder.bitcast(builder.extract_value(sgokf__gpv,
            infos_pos), juwo__toym)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, gnt__ahjy)
        hkg__ahx = builder.bitcast(builder.extract_value(sgokf__gpv, 
            infos_pos + 1), juwo__toym)
        arr.data = _lower_info_to_array_numpy(types.Array(ivq__wqqzb, 1,
            'C'), context, builder, hkg__ahx)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, ymcjv__wob = args
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        return _lower_info_to_array_list_string_array(arr_type, context,
            builder, in_info)
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType,
        StructArrayType, TupleArrayType)):

        def get_num_arrays(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 1 + get_num_arrays(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_arrays(rybda__mifr) for rybda__mifr in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(rybda__mifr) for rybda__mifr in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            vxtjv__naakc = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            vxtjv__naakc = _get_map_arr_data_type(arr_type)
        else:
            vxtjv__naakc = arr_type
        hxt__vkjrr = get_num_arrays(vxtjv__naakc)
        cnmy__tsw = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for ymcjv__wob in range(hxt__vkjrr)])
        lengths_ptr = cgutils.alloca_once_value(builder, cnmy__tsw)
        gqp__epnz = lir.Constant(lir.IntType(8).as_pointer(), None)
        axnkf__bjxr = cgutils.pack_array(builder, [gqp__epnz for ymcjv__wob in
            range(get_num_infos(vxtjv__naakc))])
        array_infos_ptr = cgutils.alloca_once_value(builder, axnkf__bjxr)
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_to_nested_array')
        builder.call(znum__ezf, [in_info, builder.bitcast(lengths_ptr, lir.
            IntType(64).as_pointer()), builder.bitcast(array_infos_ptr, lir
            .IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, ymcjv__wob, ymcjv__wob = nested_to_array(context, builder,
            vxtjv__naakc, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            xqn__qbqma = context.make_helper(builder, arr_type)
            xqn__qbqma.data = arr
            context.nrt.incref(builder, vxtjv__naakc, arr)
            arr = xqn__qbqma._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, vxtjv__naakc)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        pss__figtp = context.make_helper(builder, arr_type)
        gfq__tyj = ArrayItemArrayType(char_arr_type)
        otgkx__klqu = context.make_helper(builder, gfq__tyj)
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_to_string_array')
        builder.call(znum__ezf, [in_info, otgkx__klqu._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        pss__figtp.data = otgkx__klqu._getvalue()
        return pss__figtp._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='get_nested_info')
        vwif__dcsoz = builder.call(znum__ezf, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        xjnn__klt = builder.call(znum__ezf, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        lpwfu__laejy = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        lpwfu__laejy.data = info_to_array_codegen(context, builder, sig, (
            vwif__dcsoz, context.get_constant_null(arr_type.data)))
        eyf__bnmgl = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = eyf__bnmgl(array_info_type, eyf__bnmgl)
        lpwfu__laejy.indices = info_to_array_codegen(context, builder, sig,
            (xjnn__klt, context.get_constant_null(eyf__bnmgl)))
        oddaf__koeu = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='get_has_global_dictionary')
        jxl__goydv = builder.call(znum__ezf, [in_info])
        lpwfu__laejy.has_global_dictionary = builder.trunc(jxl__goydv,
            cgutils.bool_t)
        return lpwfu__laejy._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        aeh__amhio = get_categories_int_type(arr_type.dtype)
        bhi__voyl = types.Array(aeh__amhio, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(bhi__voyl, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            sufh__jezgp = pd.CategoricalDtype(arr_type.dtype.categories,
                is_ordered).categories.values
            new_cats_tup = MetaType(tuple(sufh__jezgp))
            int_type = arr_type.dtype.int_type
            fzo__gpfk = bodo.typeof(sufh__jezgp)
            qcy__nglb = context.get_constant_generic(builder, fzo__gpfk,
                sufh__jezgp)
            pnp__nfrip = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(fzo__gpfk), [qcy__nglb])
        else:
            pnp__nfrip = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, pnp__nfrip)
        out_arr.dtype = pnp__nfrip
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        dyn__orepd = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = dyn__orepd
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ivq__wqqzb = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            ivq__wqqzb = int128_type
        elif arr_type == datetime_date_array_type:
            ivq__wqqzb = types.int64
        tzowj__yjlgl = types.Array(ivq__wqqzb, 1, 'C')
        adnzw__hxy = context.make_array(tzowj__yjlgl)(context, builder)
        rmpkk__ihb = types.Array(types.uint8, 1, 'C')
        yjfh__lakky = context.make_array(rmpkk__ihb)(context, builder)
        hrec__rhss = cgutils.alloca_once(builder, lir.IntType(64))
        wsdw__rummz = cgutils.alloca_once(builder, lir.IntType(64))
        hpx__dwps = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        hnw__erprh = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        hovi__gsr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        upm__byqz = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_to_nullable_array')
        builder.call(znum__ezf, [in_info, hrec__rhss, wsdw__rummz,
            hpx__dwps, hnw__erprh, hovi__gsr, upm__byqz])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        rgf__mtqz = context.get_value_type(types.intp)
        ynel__upn = cgutils.pack_array(builder, [builder.load(hrec__rhss)],
            ty=rgf__mtqz)
        wox__lbkr = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(ivq__wqqzb)))
        tja__ajoni = cgutils.pack_array(builder, [wox__lbkr], ty=rgf__mtqz)
        dyn__orepd = builder.bitcast(builder.load(hpx__dwps), context.
            get_data_type(ivq__wqqzb).as_pointer())
        numba.np.arrayobj.populate_array(adnzw__hxy, data=dyn__orepd, shape
            =ynel__upn, strides=tja__ajoni, itemsize=wox__lbkr, meminfo=
            builder.load(hovi__gsr))
        arr.data = adnzw__hxy._getvalue()
        ynel__upn = cgutils.pack_array(builder, [builder.load(wsdw__rummz)],
            ty=rgf__mtqz)
        wox__lbkr = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(types.uint8)))
        tja__ajoni = cgutils.pack_array(builder, [wox__lbkr], ty=rgf__mtqz)
        dyn__orepd = builder.bitcast(builder.load(hnw__erprh), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(yjfh__lakky, data=dyn__orepd,
            shape=ynel__upn, strides=tja__ajoni, itemsize=wox__lbkr,
            meminfo=builder.load(upm__byqz))
        arr.null_bitmap = yjfh__lakky._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zrb__ibj = context.make_array(arr_type.arr_type)(context, builder)
        oknpd__ljtfo = context.make_array(arr_type.arr_type)(context, builder)
        hrec__rhss = cgutils.alloca_once(builder, lir.IntType(64))
        kgavx__naf = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        gjc__cctwk = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        wibof__alwwn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        fhp__ekvyc = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_to_interval_array')
        builder.call(znum__ezf, [in_info, hrec__rhss, kgavx__naf,
            gjc__cctwk, wibof__alwwn, fhp__ekvyc])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        rgf__mtqz = context.get_value_type(types.intp)
        ynel__upn = cgutils.pack_array(builder, [builder.load(hrec__rhss)],
            ty=rgf__mtqz)
        wox__lbkr = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(arr_type.arr_type.dtype)))
        tja__ajoni = cgutils.pack_array(builder, [wox__lbkr], ty=rgf__mtqz)
        tkkza__rhim = builder.bitcast(builder.load(kgavx__naf), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(zrb__ibj, data=tkkza__rhim, shape=
            ynel__upn, strides=tja__ajoni, itemsize=wox__lbkr, meminfo=
            builder.load(wibof__alwwn))
        arr.left = zrb__ibj._getvalue()
        ihd__tos = builder.bitcast(builder.load(gjc__cctwk), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(oknpd__ljtfo, data=ihd__tos, shape
            =ynel__upn, strides=tja__ajoni, itemsize=wox__lbkr, meminfo=
            builder.load(fhp__ekvyc))
        arr.right = oknpd__ljtfo._getvalue()
        return arr._getvalue()
    raise_bodo_error(f'info_to_array(): array type {arr_type} is not supported'
        )


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type, 'info_to_array: expected info type'
    return arr_type(info_type, array_type), info_to_array_codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        hhdgu__ukjl, ymcjv__wob = args
        zrq__pecw = numba_to_c_type(array_type.dtype)
        xkpb__pzyte = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zrq__pecw))
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='alloc_numpy')
        return builder.call(znum__ezf, [hhdgu__ukjl, builder.load(xkpb__pzyte)]
            )
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        hhdgu__ukjl, fmg__rre = args
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='alloc_string_array')
        return builder.call(znum__ezf, [hhdgu__ukjl, fmg__rre])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    qui__tpzlt, = args
    kooj__thxwt = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], qui__tpzlt)
    oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    znum__ezf = cgutils.get_or_insert_function(builder.module, oddaf__koeu,
        name='arr_info_list_to_table')
    return builder.call(znum__ezf, [kooj__thxwt.data, kooj__thxwt.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_from_table')
        return builder.call(znum__ezf, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    qhchv__qbn = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        adxww__xjtfy, soib__nngv, ymcjv__wob = args
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='info_from_table')
        qles__cxv = cgutils.create_struct_proxy(qhchv__qbn)(context, builder)
        qles__cxv.parent = cgutils.get_null_value(qles__cxv.parent.type)
        xqeo__kms = context.make_array(table_idx_arr_t)(context, builder,
            soib__nngv)
        dvoqd__sgmh = context.get_constant(types.int64, -1)
        nuw__hdiv = context.get_constant(types.int64, 0)
        wloh__pqysz = cgutils.alloca_once_value(builder, nuw__hdiv)
        for t, vho__xxlvu in qhchv__qbn.type_to_blk.items():
            zad__stsoi = context.get_constant(types.int64, len(qhchv__qbn.
                block_to_arr_ind[vho__xxlvu]))
            ymcjv__wob, brp__jwv = ListInstance.allocate_ex(context,
                builder, types.List(t), zad__stsoi)
            brp__jwv.size = zad__stsoi
            gqlk__qrr = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(qhchv__qbn.block_to_arr_ind[
                vho__xxlvu], dtype=np.int64))
            ksyt__rqgni = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, gqlk__qrr)
            with cgutils.for_range(builder, zad__stsoi) as cwhi__naxu:
                kxp__ghj = cwhi__naxu.index
                kdx__jmcz = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ksyt__rqgni, kxp__ghj)
                ahnx__pld = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, xqeo__kms, kdx__jmcz)
                feuq__qwm = builder.icmp_unsigned('!=', ahnx__pld, dvoqd__sgmh)
                with builder.if_else(feuq__qwm) as (cvyfb__uvs, nzfmr__wnzcf):
                    with cvyfb__uvs:
                        pwkfv__favl = builder.call(znum__ezf, [adxww__xjtfy,
                            ahnx__pld])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            pwkfv__favl])
                        brp__jwv.inititem(kxp__ghj, arr, incref=False)
                        hhdgu__ukjl = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(hhdgu__ukjl, wloh__pqysz)
                    with nzfmr__wnzcf:
                        uiyir__bmmvz = context.get_constant_null(t)
                        brp__jwv.inititem(kxp__ghj, uiyir__bmmvz, incref=False)
            setattr(qles__cxv, f'block_{vho__xxlvu}', brp__jwv.value)
        qles__cxv.len = builder.load(wloh__pqysz)
        return qles__cxv._getvalue()
    return qhchv__qbn(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    qhchv__qbn = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        dqer__cfq, ymcjv__wob = args
        wsx__wess = cgutils.create_struct_proxy(qhchv__qbn)(context,
            builder, dqer__cfq)
        if qhchv__qbn.has_runtime_cols:
            sgftf__xwcts = lir.Constant(lir.IntType(64), 0)
            for vho__xxlvu, t in enumerate(qhchv__qbn.arr_types):
                tqhd__jncrs = getattr(wsx__wess, f'block_{vho__xxlvu}')
                sgiw__ayeyi = ListInstance(context, builder, types.List(t),
                    tqhd__jncrs)
                sgftf__xwcts = builder.add(sgftf__xwcts, sgiw__ayeyi.size)
        else:
            sgftf__xwcts = lir.Constant(lir.IntType(64), len(qhchv__qbn.
                arr_types))
        ymcjv__wob, vpxcs__zmrub = ListInstance.allocate_ex(context,
            builder, types.List(array_info_type), sgftf__xwcts)
        vpxcs__zmrub.size = sgftf__xwcts
        if qhchv__qbn.has_runtime_cols:
            lkjd__mixx = lir.Constant(lir.IntType(64), 0)
            for vho__xxlvu, t in enumerate(qhchv__qbn.arr_types):
                tqhd__jncrs = getattr(wsx__wess, f'block_{vho__xxlvu}')
                sgiw__ayeyi = ListInstance(context, builder, types.List(t),
                    tqhd__jncrs)
                zad__stsoi = sgiw__ayeyi.size
                with cgutils.for_range(builder, zad__stsoi) as cwhi__naxu:
                    kxp__ghj = cwhi__naxu.index
                    arr = sgiw__ayeyi.getitem(kxp__ghj)
                    ybkrd__flp = signature(array_info_type, t)
                    vfp__ezg = arr,
                    tva__kipf = array_to_info_codegen(context, builder,
                        ybkrd__flp, vfp__ezg)
                    vpxcs__zmrub.inititem(builder.add(lkjd__mixx, kxp__ghj),
                        tva__kipf, incref=False)
                lkjd__mixx = builder.add(lkjd__mixx, zad__stsoi)
        else:
            for t, vho__xxlvu in qhchv__qbn.type_to_blk.items():
                zad__stsoi = context.get_constant(types.int64, len(
                    qhchv__qbn.block_to_arr_ind[vho__xxlvu]))
                tqhd__jncrs = getattr(wsx__wess, f'block_{vho__xxlvu}')
                sgiw__ayeyi = ListInstance(context, builder, types.List(t),
                    tqhd__jncrs)
                gqlk__qrr = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(qhchv__qbn.
                    block_to_arr_ind[vho__xxlvu], dtype=np.int64))
                ksyt__rqgni = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, gqlk__qrr)
                with cgutils.for_range(builder, zad__stsoi) as cwhi__naxu:
                    kxp__ghj = cwhi__naxu.index
                    kdx__jmcz = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        ksyt__rqgni, kxp__ghj)
                    cfux__fsw = signature(types.none, qhchv__qbn, types.
                        List(t), types.int64, types.int64)
                    pnop__ahenj = dqer__cfq, tqhd__jncrs, kxp__ghj, kdx__jmcz
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, cfux__fsw, pnop__ahenj)
                    arr = sgiw__ayeyi.getitem(kxp__ghj)
                    ybkrd__flp = signature(array_info_type, t)
                    vfp__ezg = arr,
                    tva__kipf = array_to_info_codegen(context, builder,
                        ybkrd__flp, vfp__ezg)
                    vpxcs__zmrub.inititem(kdx__jmcz, tva__kipf, incref=False)
        ddn__dokp = vpxcs__zmrub.value
        rkd__xatzx = signature(table_type, types.List(array_info_type))
        xhlm__ukmzu = ddn__dokp,
        adxww__xjtfy = arr_info_list_to_table_codegen(context, builder,
            rkd__xatzx, xhlm__ukmzu)
        context.nrt.decref(builder, types.List(array_info_type), ddn__dokp)
        return adxww__xjtfy
    return table_type(qhchv__qbn, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='delete_table')
        builder.call(znum__ezf, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='shuffle_table')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))


@intrinsic
def delete_shuffle_info(typingctx, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[0] == types.none:
            return
        oddaf__koeu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='delete_shuffle_info')
        return builder.call(znum__ezf, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='reverse_shuffle_table')
        return builder.call(znum__ezf, args)
    return table_type(table_type, shuffle_info_t), codegen


@intrinsic
def get_null_shuffle_info(typingctx):

    def codegen(context, builder, sig, args):
        return context.get_constant_null(sig.return_type)
    return shuffle_info_type(), codegen


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    key_in_out_t, same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    optional_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='hash_join_table')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.int64, types.voidptr, types.int64), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, dead_keys_t, parallel_t):
    assert table_t == table_type, 'C++ table type expected'

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='sort_values_table')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='sample_table')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='shuffle_renormalization')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='shuffle_renormalization_group')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='drop_duplicates_table')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean, types.boolean), codegen


@intrinsic
def pivot_groupby_and_aggregate(typingctx, table_t, n_keys_t,
    dispatch_table_t, dispatch_info_t, input_has_index, ftypes,
    func_offsets, udf_n_redvars, is_parallel, is_crosstab, skipdropna_t,
    return_keys, return_index, update_cb, combine_cb, eval_cb,
    udf_table_dummy_t):
    assert table_t == table_type
    assert dispatch_table_t == table_type
    assert dispatch_info_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='pivot_groupby_and_aggregate')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int64, table_t, table_t, types.boolean,
        types.voidptr, types.voidptr, types.voidptr, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, table_t), codegen


@intrinsic
def groupby_and_aggregate(typingctx, table_t, n_keys_t, input_has_index,
    ftypes, func_offsets, udf_n_redvars, is_parallel, skipdropna_t,
    shift_periods_t, transform_func, head_n, return_keys, return_index,
    dropna, update_cb, combine_cb, eval_cb, general_udfs_cb, udf_table_dummy_t
    ):
    assert table_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        znum__ezf = cgutils.get_or_insert_function(builder.module,
            oddaf__koeu, name='groupby_and_aggregate')
        wygl__znaao = builder.call(znum__ezf, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return wygl__znaao
    return table_type(table_t, types.int64, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        int64, types.int64, types.int64, types.boolean, types.boolean,
        types.boolean, types.voidptr, types.voidptr, types.voidptr, types.
        voidptr, table_t), codegen


get_groupby_labels = types.ExternalFunction('get_groupby_labels', types.
    int64(table_type, types.voidptr, types.voidptr, types.boolean, types.bool_)
    )
_array_isin = types.ExternalFunction('array_isin', types.void(
    array_info_type, array_info_type, array_info_type, types.bool_))


@numba.njit(no_cpython_wrapper=True)
def array_isin(out_arr, in_arr, in_values, is_parallel):
    in_arr = decode_if_dict_array(in_arr)
    in_values = decode_if_dict_array(in_values)
    lrvak__ipnm = array_to_info(in_arr)
    rcsu__ymgu = array_to_info(in_values)
    qdfc__glsa = array_to_info(out_arr)
    vff__uqhnu = arr_info_list_to_table([lrvak__ipnm, rcsu__ymgu, qdfc__glsa])
    _array_isin(qdfc__glsa, lrvak__ipnm, rcsu__ymgu, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(vff__uqhnu)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, pat, out_arr):
    lrvak__ipnm = array_to_info(in_arr)
    qdfc__glsa = array_to_info(out_arr)
    _get_search_regex(lrvak__ipnm, case, pat, qdfc__glsa)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    mrmpu__ddy = col_array_typ.dtype
    if isinstance(mrmpu__ddy, types.Number) or mrmpu__ddy in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                qles__cxv, qmyew__nprx = args
                qles__cxv = builder.bitcast(qles__cxv, lir.IntType(8).
                    as_pointer().as_pointer())
                mdcan__oqlz = lir.Constant(lir.IntType(64), c_ind)
                dzzh__vgfzw = builder.load(builder.gep(qles__cxv, [
                    mdcan__oqlz]))
                dzzh__vgfzw = builder.bitcast(dzzh__vgfzw, context.
                    get_data_type(mrmpu__ddy).as_pointer())
                return builder.load(builder.gep(dzzh__vgfzw, [qmyew__nprx]))
            return mrmpu__ddy(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.string_array_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                qles__cxv, qmyew__nprx = args
                qles__cxv = builder.bitcast(qles__cxv, lir.IntType(8).
                    as_pointer().as_pointer())
                mdcan__oqlz = lir.Constant(lir.IntType(64), c_ind)
                dzzh__vgfzw = builder.load(builder.gep(qles__cxv, [
                    mdcan__oqlz]))
                oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                skg__wey = cgutils.get_or_insert_function(builder.module,
                    oddaf__koeu, name='array_info_getitem')
                qkcvj__psj = cgutils.alloca_once(builder, lir.IntType(64))
                args = dzzh__vgfzw, qmyew__nprx, qkcvj__psj
                hpx__dwps = builder.call(skg__wey, args)
                return context.make_tuple(builder, sig.return_type, [
                    hpx__dwps, builder.load(qkcvj__psj)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                owzh__jviw = lir.Constant(lir.IntType(64), 1)
                dsknh__jccuc = lir.Constant(lir.IntType(64), 2)
                qles__cxv, qmyew__nprx = args
                qles__cxv = builder.bitcast(qles__cxv, lir.IntType(8).
                    as_pointer().as_pointer())
                mdcan__oqlz = lir.Constant(lir.IntType(64), c_ind)
                dzzh__vgfzw = builder.load(builder.gep(qles__cxv, [
                    mdcan__oqlz]))
                oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                kbb__pch = cgutils.get_or_insert_function(builder.module,
                    oddaf__koeu, name='get_nested_info')
                args = dzzh__vgfzw, dsknh__jccuc
                ycol__wgahi = builder.call(kbb__pch, args)
                oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                szfoq__bme = cgutils.get_or_insert_function(builder.module,
                    oddaf__koeu, name='array_info_getdata1')
                args = ycol__wgahi,
                hxl__daup = builder.call(szfoq__bme, args)
                hxl__daup = builder.bitcast(hxl__daup, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                tnvro__acdo = builder.sext(builder.load(builder.gep(
                    hxl__daup, [qmyew__nprx])), lir.IntType(64))
                args = dzzh__vgfzw, owzh__jviw
                rxrch__gki = builder.call(kbb__pch, args)
                oddaf__koeu = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                skg__wey = cgutils.get_or_insert_function(builder.module,
                    oddaf__koeu, name='array_info_getitem')
                qkcvj__psj = cgutils.alloca_once(builder, lir.IntType(64))
                args = rxrch__gki, tnvro__acdo, qkcvj__psj
                hpx__dwps = builder.call(skg__wey, args)
                return context.make_tuple(builder, sig.return_type, [
                    hpx__dwps, builder.load(qkcvj__psj)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{mrmpu__ddy}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if (isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType) or
        col_array_dtype == bodo.libs.bool_arr_ext.boolean_array or
        is_str_arr_type(col_array_dtype) or isinstance(col_array_dtype,
        types.Array) and col_array_dtype.dtype == bodo.datetime_date_type):

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                votla__asyy, qmyew__nprx = args
                votla__asyy = builder.bitcast(votla__asyy, lir.IntType(8).
                    as_pointer().as_pointer())
                mdcan__oqlz = lir.Constant(lir.IntType(64), c_ind)
                dzzh__vgfzw = builder.load(builder.gep(votla__asyy, [
                    mdcan__oqlz]))
                jtiyd__eteq = builder.bitcast(dzzh__vgfzw, context.
                    get_data_type(types.bool_).as_pointer())
                zgi__ffep = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    jtiyd__eteq, qmyew__nprx)
                upj__mfdk = builder.icmp_unsigned('!=', zgi__ffep, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(upj__mfdk, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        mrmpu__ddy = col_array_dtype.dtype
        if mrmpu__ddy in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    qles__cxv, qmyew__nprx = args
                    qles__cxv = builder.bitcast(qles__cxv, lir.IntType(8).
                        as_pointer().as_pointer())
                    mdcan__oqlz = lir.Constant(lir.IntType(64), c_ind)
                    dzzh__vgfzw = builder.load(builder.gep(qles__cxv, [
                        mdcan__oqlz]))
                    dzzh__vgfzw = builder.bitcast(dzzh__vgfzw, context.
                        get_data_type(mrmpu__ddy).as_pointer())
                    smyke__irdx = builder.load(builder.gep(dzzh__vgfzw, [
                        qmyew__nprx]))
                    upj__mfdk = builder.icmp_unsigned('!=', smyke__irdx,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(upj__mfdk, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(mrmpu__ddy, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    qles__cxv, qmyew__nprx = args
                    qles__cxv = builder.bitcast(qles__cxv, lir.IntType(8).
                        as_pointer().as_pointer())
                    mdcan__oqlz = lir.Constant(lir.IntType(64), c_ind)
                    dzzh__vgfzw = builder.load(builder.gep(qles__cxv, [
                        mdcan__oqlz]))
                    dzzh__vgfzw = builder.bitcast(dzzh__vgfzw, context.
                        get_data_type(mrmpu__ddy).as_pointer())
                    smyke__irdx = builder.load(builder.gep(dzzh__vgfzw, [
                        qmyew__nprx]))
                    cjfmr__woee = signature(types.bool_, mrmpu__ddy)
                    zgi__ffep = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, cjfmr__woee, (smyke__irdx,))
                    return builder.not_(builder.sext(zgi__ffep, lir.IntType(8))
                        )
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
