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
        vxdo__vefc = context.make_helper(builder, arr_type, in_arr)
        in_arr = vxdo__vefc.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        dnbdj__epofk = context.make_helper(builder, arr_type, in_arr)
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='list_string_array_to_info')
        return builder.call(pwdpz__tgdky, [dnbdj__epofk.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                oos__pyghc = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for gub__kpwz in arr_typ.data:
                    oos__pyghc += get_types(gub__kpwz)
                return oos__pyghc
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
            okz__kxr = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                tukp__uml = context.make_helper(builder, arr_typ, value=arr)
                mdk__dwsx = get_lengths(_get_map_arr_data_type(arr_typ),
                    tukp__uml.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ignxw__sak = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                mdk__dwsx = get_lengths(arr_typ.dtype, ignxw__sak.data)
                mdk__dwsx = cgutils.pack_array(builder, [ignxw__sak.
                    n_arrays] + [builder.extract_value(mdk__dwsx, fqb__zff) for
                    fqb__zff in range(mdk__dwsx.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ignxw__sak = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                mdk__dwsx = []
                for fqb__zff, gub__kpwz in enumerate(arr_typ.data):
                    fce__qld = get_lengths(gub__kpwz, builder.extract_value
                        (ignxw__sak.data, fqb__zff))
                    mdk__dwsx += [builder.extract_value(fce__qld,
                        xez__hnqlt) for xez__hnqlt in range(fce__qld.type.
                        count)]
                mdk__dwsx = cgutils.pack_array(builder, [okz__kxr, context.
                    get_constant(types.int64, -1)] + mdk__dwsx)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                mdk__dwsx = cgutils.pack_array(builder, [okz__kxr])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return mdk__dwsx

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                tukp__uml = context.make_helper(builder, arr_typ, value=arr)
                heb__ttzsd = get_buffers(_get_map_arr_data_type(arr_typ),
                    tukp__uml.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ignxw__sak = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                xmf__ycjrf = get_buffers(arr_typ.dtype, ignxw__sak.data)
                wsr__ffi = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, ignxw__sak.offsets)
                wcmm__zob = builder.bitcast(wsr__ffi.data, lir.IntType(8).
                    as_pointer())
                wzh__vadhp = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, ignxw__sak.null_bitmap)
                ubjra__vkl = builder.bitcast(wzh__vadhp.data, lir.IntType(8
                    ).as_pointer())
                heb__ttzsd = cgutils.pack_array(builder, [wcmm__zob,
                    ubjra__vkl] + [builder.extract_value(xmf__ycjrf,
                    fqb__zff) for fqb__zff in range(xmf__ycjrf.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ignxw__sak = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                xmf__ycjrf = []
                for fqb__zff, gub__kpwz in enumerate(arr_typ.data):
                    elw__uvcxy = get_buffers(gub__kpwz, builder.
                        extract_value(ignxw__sak.data, fqb__zff))
                    xmf__ycjrf += [builder.extract_value(elw__uvcxy,
                        xez__hnqlt) for xez__hnqlt in range(elw__uvcxy.type
                        .count)]
                wzh__vadhp = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, ignxw__sak.null_bitmap)
                ubjra__vkl = builder.bitcast(wzh__vadhp.data, lir.IntType(8
                    ).as_pointer())
                heb__ttzsd = cgutils.pack_array(builder, [ubjra__vkl] +
                    xmf__ycjrf)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                ignky__mqp = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    ignky__mqp = int128_type
                elif arr_typ == datetime_date_array_type:
                    ignky__mqp = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                axwl__ngru = context.make_array(types.Array(ignky__mqp, 1, 'C')
                    )(context, builder, arr.data)
                wzh__vadhp = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                kinv__bwfdu = builder.bitcast(axwl__ngru.data, lir.IntType(
                    8).as_pointer())
                ubjra__vkl = builder.bitcast(wzh__vadhp.data, lir.IntType(8
                    ).as_pointer())
                heb__ttzsd = cgutils.pack_array(builder, [ubjra__vkl,
                    kinv__bwfdu])
            elif arr_typ in (string_array_type, binary_array_type):
                ignxw__sak = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                rxtth__fycel = context.make_helper(builder, offset_arr_type,
                    ignxw__sak.offsets).data
                ruw__jwgvx = context.make_helper(builder, char_arr_type,
                    ignxw__sak.data).data
                cdyj__rnzup = context.make_helper(builder,
                    null_bitmap_arr_type, ignxw__sak.null_bitmap).data
                heb__ttzsd = cgutils.pack_array(builder, [builder.bitcast(
                    rxtth__fycel, lir.IntType(8).as_pointer()), builder.
                    bitcast(cdyj__rnzup, lir.IntType(8).as_pointer()),
                    builder.bitcast(ruw__jwgvx, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                kinv__bwfdu = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                aut__ampfw = lir.Constant(lir.IntType(8).as_pointer(), None)
                heb__ttzsd = cgutils.pack_array(builder, [aut__ampfw,
                    kinv__bwfdu])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return heb__ttzsd

        def get_field_names(arr_typ):
            beut__mtkxr = []
            if isinstance(arr_typ, StructArrayType):
                for xmrfa__xamd, ejrr__ucoyt in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    beut__mtkxr.append(xmrfa__xamd)
                    beut__mtkxr += get_field_names(ejrr__ucoyt)
            elif isinstance(arr_typ, ArrayItemArrayType):
                beut__mtkxr += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                beut__mtkxr += get_field_names(_get_map_arr_data_type(arr_typ))
            return beut__mtkxr
        oos__pyghc = get_types(arr_type)
        wrdjt__len = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in oos__pyghc])
        spus__chiag = cgutils.alloca_once_value(builder, wrdjt__len)
        mdk__dwsx = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, mdk__dwsx)
        heb__ttzsd = get_buffers(arr_type, in_arr)
        wyv__tuazh = cgutils.alloca_once_value(builder, heb__ttzsd)
        beut__mtkxr = get_field_names(arr_type)
        if len(beut__mtkxr) == 0:
            beut__mtkxr = ['irrelevant']
        gbt__gtxlf = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in beut__mtkxr])
        zdvf__xmpfw = cgutils.alloca_once_value(builder, gbt__gtxlf)
        if isinstance(arr_type, MapArrayType):
            wzne__cezai = _get_map_arr_data_type(arr_type)
            rum__jwwb = context.make_helper(builder, arr_type, value=in_arr)
            vpcnr__zic = rum__jwwb.data
        else:
            wzne__cezai = arr_type
            vpcnr__zic = in_arr
        zbg__ocq = context.make_helper(builder, wzne__cezai, vpcnr__zic)
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='nested_array_to_info')
        hytt__nwnd = builder.call(pwdpz__tgdky, [builder.bitcast(
            spus__chiag, lir.IntType(32).as_pointer()), builder.bitcast(
            wyv__tuazh, lir.IntType(8).as_pointer().as_pointer()), builder.
            bitcast(lengths_ptr, lir.IntType(64).as_pointer()), builder.
            bitcast(zdvf__xmpfw, lir.IntType(8).as_pointer()), zbg__ocq.
            meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
    if arr_type in (string_array_type, binary_array_type):
        ztly__gzuhi = context.make_helper(builder, arr_type, in_arr)
        hay__joko = ArrayItemArrayType(char_arr_type)
        dnbdj__epofk = context.make_helper(builder, hay__joko, ztly__gzuhi.data
            )
        ignxw__sak = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        rxtth__fycel = context.make_helper(builder, offset_arr_type,
            ignxw__sak.offsets).data
        ruw__jwgvx = context.make_helper(builder, char_arr_type, ignxw__sak
            .data).data
        cdyj__rnzup = context.make_helper(builder, null_bitmap_arr_type,
            ignxw__sak.null_bitmap).data
        czic__atm = builder.zext(builder.load(builder.gep(rxtth__fycel, [
            ignxw__sak.n_arrays])), lir.IntType(64))
        zoaqp__zwxvl = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='string_array_to_info')
        return builder.call(pwdpz__tgdky, [ignxw__sak.n_arrays, czic__atm,
            ruw__jwgvx, rxtth__fycel, cdyj__rnzup, dnbdj__epofk.meminfo,
            zoaqp__zwxvl])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        pwkpo__thygv = arr.data
        oyvk__ymf = arr.indices
        sig = array_info_type(arr_type.data)
        wps__fmp = array_to_info_codegen(context, builder, sig, (
            pwkpo__thygv,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        zhxh__tph = array_to_info_codegen(context, builder, sig, (oyvk__ymf
            ,), False)
        ubhn__vmrtj = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, oyvk__ymf)
        ubjra__vkl = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, ubhn__vmrtj.null_bitmap).data
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='dict_str_array_to_info')
        qnlt__vsqeu = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(pwdpz__tgdky, [wps__fmp, zhxh__tph, builder.
            bitcast(ubjra__vkl, lir.IntType(8).as_pointer()), qnlt__vsqeu])
    jyz__uscr = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        lshrn__qwov = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        jppom__wgqy = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(jppom__wgqy, 1, 'C')
        jyz__uscr = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if jyz__uscr:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        okz__kxr = builder.extract_value(arr.shape, 0)
        lxxk__vhmys = arr_type.dtype
        wqv__pfi = numba_to_c_type(lxxk__vhmys)
        ggyj__wwk = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), wqv__pfi))
        if jyz__uscr:
            zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
                zmmnx__kfjvg, name='categorical_array_to_info')
            return builder.call(pwdpz__tgdky, [okz__kxr, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                ggyj__wwk), lshrn__qwov, arr.meminfo])
        else:
            zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
                zmmnx__kfjvg, name='numpy_array_to_info')
            return builder.call(pwdpz__tgdky, [okz__kxr, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                ggyj__wwk), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        lxxk__vhmys = arr_type.dtype
        ignky__mqp = lxxk__vhmys
        if isinstance(arr_type, DecimalArrayType):
            ignky__mqp = int128_type
        if arr_type == datetime_date_array_type:
            ignky__mqp = types.int64
        axwl__ngru = context.make_array(types.Array(ignky__mqp, 1, 'C'))(
            context, builder, arr.data)
        okz__kxr = builder.extract_value(axwl__ngru.shape, 0)
        jnpn__uaxa = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        wqv__pfi = numba_to_c_type(lxxk__vhmys)
        ggyj__wwk = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), wqv__pfi))
        if isinstance(arr_type, DecimalArrayType):
            zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
                zmmnx__kfjvg, name='decimal_array_to_info')
            return builder.call(pwdpz__tgdky, [okz__kxr, builder.bitcast(
                axwl__ngru.data, lir.IntType(8).as_pointer()), builder.load
                (ggyj__wwk), builder.bitcast(jnpn__uaxa.data, lir.IntType(8
                ).as_pointer()), axwl__ngru.meminfo, jnpn__uaxa.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
                zmmnx__kfjvg, name='nullable_array_to_info')
            return builder.call(pwdpz__tgdky, [okz__kxr, builder.bitcast(
                axwl__ngru.data, lir.IntType(8).as_pointer()), builder.load
                (ggyj__wwk), builder.bitcast(jnpn__uaxa.data, lir.IntType(8
                ).as_pointer()), axwl__ngru.meminfo, jnpn__uaxa.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        cnm__hrf = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        iyke__qixi = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        okz__kxr = builder.extract_value(cnm__hrf.shape, 0)
        wqv__pfi = numba_to_c_type(arr_type.arr_type.dtype)
        ggyj__wwk = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), wqv__pfi))
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='interval_array_to_info')
        return builder.call(pwdpz__tgdky, [okz__kxr, builder.bitcast(
            cnm__hrf.data, lir.IntType(8).as_pointer()), builder.bitcast(
            iyke__qixi.data, lir.IntType(8).as_pointer()), builder.load(
            ggyj__wwk), cnm__hrf.meminfo, iyke__qixi.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    ukr__gdxdu = cgutils.alloca_once(builder, lir.IntType(64))
    kinv__bwfdu = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    gvi__capn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
        zmmnx__kfjvg, name='info_to_numpy_array')
    builder.call(pwdpz__tgdky, [in_info, ukr__gdxdu, kinv__bwfdu, gvi__capn])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    sew__ulcfr = context.get_value_type(types.intp)
    wpfs__tep = cgutils.pack_array(builder, [builder.load(ukr__gdxdu)], ty=
        sew__ulcfr)
    qtoic__omhlz = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    kpgz__vgvo = cgutils.pack_array(builder, [qtoic__omhlz], ty=sew__ulcfr)
    ruw__jwgvx = builder.bitcast(builder.load(kinv__bwfdu), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=ruw__jwgvx, shape=wpfs__tep,
        strides=kpgz__vgvo, itemsize=qtoic__omhlz, meminfo=builder.load(
        gvi__capn))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    eax__zouy = context.make_helper(builder, arr_type)
    zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
        zmmnx__kfjvg, name='info_to_list_string_array')
    builder.call(pwdpz__tgdky, [in_info, eax__zouy._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return eax__zouy._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    zgrlj__agrjs = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        wrbxi__qpqaz = lengths_pos
        ayh__mdl = infos_pos
        vxyna__mnv, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        wsm__twm = ArrayItemArrayPayloadType(arr_typ)
        erqgz__cxfd = context.get_data_type(wsm__twm)
        ijb__hbjha = context.get_abi_sizeof(erqgz__cxfd)
        netvc__nks = define_array_item_dtor(context, builder, arr_typ, wsm__twm
            )
        xwi__huwxg = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, ijb__hbjha), netvc__nks)
        qii__abjsl = context.nrt.meminfo_data(builder, xwi__huwxg)
        latt__okxte = builder.bitcast(qii__abjsl, erqgz__cxfd.as_pointer())
        ignxw__sak = cgutils.create_struct_proxy(wsm__twm)(context, builder)
        ignxw__sak.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), wrbxi__qpqaz)
        ignxw__sak.data = vxyna__mnv
        aehd__plkh = builder.load(array_infos_ptr)
        kpgb__mev = builder.bitcast(builder.extract_value(aehd__plkh,
            ayh__mdl), zgrlj__agrjs)
        ignxw__sak.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, kpgb__mev)
        hwgtd__cvqsr = builder.bitcast(builder.extract_value(aehd__plkh, 
            ayh__mdl + 1), zgrlj__agrjs)
        ignxw__sak.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, hwgtd__cvqsr)
        builder.store(ignxw__sak._getvalue(), latt__okxte)
        dnbdj__epofk = context.make_helper(builder, arr_typ)
        dnbdj__epofk.meminfo = xwi__huwxg
        return dnbdj__epofk._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        vrg__iao = []
        ayh__mdl = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for tuhix__glrka in arr_typ.data:
            vxyna__mnv, lengths_pos, infos_pos = nested_to_array(context,
                builder, tuhix__glrka, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            vrg__iao.append(vxyna__mnv)
        wsm__twm = StructArrayPayloadType(arr_typ.data)
        erqgz__cxfd = context.get_value_type(wsm__twm)
        ijb__hbjha = context.get_abi_sizeof(erqgz__cxfd)
        netvc__nks = define_struct_arr_dtor(context, builder, arr_typ, wsm__twm
            )
        xwi__huwxg = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, ijb__hbjha), netvc__nks)
        qii__abjsl = context.nrt.meminfo_data(builder, xwi__huwxg)
        latt__okxte = builder.bitcast(qii__abjsl, erqgz__cxfd.as_pointer())
        ignxw__sak = cgutils.create_struct_proxy(wsm__twm)(context, builder)
        ignxw__sak.data = cgutils.pack_array(builder, vrg__iao
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, vrg__iao)
        aehd__plkh = builder.load(array_infos_ptr)
        hwgtd__cvqsr = builder.bitcast(builder.extract_value(aehd__plkh,
            ayh__mdl), zgrlj__agrjs)
        ignxw__sak.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, hwgtd__cvqsr)
        builder.store(ignxw__sak._getvalue(), latt__okxte)
        ksgv__smkn = context.make_helper(builder, arr_typ)
        ksgv__smkn.meminfo = xwi__huwxg
        return ksgv__smkn._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        aehd__plkh = builder.load(array_infos_ptr)
        uwjc__tnriz = builder.bitcast(builder.extract_value(aehd__plkh,
            infos_pos), zgrlj__agrjs)
        ztly__gzuhi = context.make_helper(builder, arr_typ)
        hay__joko = ArrayItemArrayType(char_arr_type)
        dnbdj__epofk = context.make_helper(builder, hay__joko)
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_to_string_array')
        builder.call(pwdpz__tgdky, [uwjc__tnriz, dnbdj__epofk.
            _get_ptr_by_name('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ztly__gzuhi.data = dnbdj__epofk._getvalue()
        return ztly__gzuhi._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        aehd__plkh = builder.load(array_infos_ptr)
        bngv__dcjh = builder.bitcast(builder.extract_value(aehd__plkh, 
            infos_pos + 1), zgrlj__agrjs)
        return _lower_info_to_array_numpy(arr_typ, context, builder, bngv__dcjh
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        ignky__mqp = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            ignky__mqp = int128_type
        elif arr_typ == datetime_date_array_type:
            ignky__mqp = types.int64
        aehd__plkh = builder.load(array_infos_ptr)
        hwgtd__cvqsr = builder.bitcast(builder.extract_value(aehd__plkh,
            infos_pos), zgrlj__agrjs)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, hwgtd__cvqsr)
        bngv__dcjh = builder.bitcast(builder.extract_value(aehd__plkh, 
            infos_pos + 1), zgrlj__agrjs)
        arr.data = _lower_info_to_array_numpy(types.Array(ignky__mqp, 1,
            'C'), context, builder, bngv__dcjh)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, vbj__wyy = args
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
                return 1 + sum([get_num_arrays(tuhix__glrka) for
                    tuhix__glrka in arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(tuhix__glrka) for
                    tuhix__glrka in arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            yejv__kdwpa = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            yejv__kdwpa = _get_map_arr_data_type(arr_type)
        else:
            yejv__kdwpa = arr_type
        pallz__kfzn = get_num_arrays(yejv__kdwpa)
        mdk__dwsx = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for vbj__wyy in range(pallz__kfzn)])
        lengths_ptr = cgutils.alloca_once_value(builder, mdk__dwsx)
        aut__ampfw = lir.Constant(lir.IntType(8).as_pointer(), None)
        lljy__iqoc = cgutils.pack_array(builder, [aut__ampfw for vbj__wyy in
            range(get_num_infos(yejv__kdwpa))])
        array_infos_ptr = cgutils.alloca_once_value(builder, lljy__iqoc)
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_to_nested_array')
        builder.call(pwdpz__tgdky, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, vbj__wyy, vbj__wyy = nested_to_array(context, builder,
            yejv__kdwpa, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            vxdo__vefc = context.make_helper(builder, arr_type)
            vxdo__vefc.data = arr
            context.nrt.incref(builder, yejv__kdwpa, arr)
            arr = vxdo__vefc._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, yejv__kdwpa)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        ztly__gzuhi = context.make_helper(builder, arr_type)
        hay__joko = ArrayItemArrayType(char_arr_type)
        dnbdj__epofk = context.make_helper(builder, hay__joko)
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_to_string_array')
        builder.call(pwdpz__tgdky, [in_info, dnbdj__epofk._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ztly__gzuhi.data = dnbdj__epofk._getvalue()
        return ztly__gzuhi._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='get_nested_info')
        wps__fmp = builder.call(pwdpz__tgdky, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        zhxh__tph = builder.call(pwdpz__tgdky, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        qpdcp__ykkj = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        qpdcp__ykkj.data = info_to_array_codegen(context, builder, sig, (
            wps__fmp, context.get_constant_null(arr_type.data)))
        cxq__lombt = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = cxq__lombt(array_info_type, cxq__lombt)
        qpdcp__ykkj.indices = info_to_array_codegen(context, builder, sig,
            (zhxh__tph, context.get_constant_null(cxq__lombt)))
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='get_has_global_dictionary')
        qnlt__vsqeu = builder.call(pwdpz__tgdky, [in_info])
        qpdcp__ykkj.has_global_dictionary = builder.trunc(qnlt__vsqeu,
            cgutils.bool_t)
        return qpdcp__ykkj._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        jppom__wgqy = get_categories_int_type(arr_type.dtype)
        bgw__htyfk = types.Array(jppom__wgqy, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(bgw__htyfk, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            ztw__ashvf = pd.CategoricalDtype(arr_type.dtype.categories,
                is_ordered).categories.values
            new_cats_tup = MetaType(tuple(ztw__ashvf))
            int_type = arr_type.dtype.int_type
            cfp__nlwtm = bodo.typeof(ztw__ashvf)
            zup__ytw = context.get_constant_generic(builder, cfp__nlwtm,
                ztw__ashvf)
            lxxk__vhmys = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(cfp__nlwtm), [zup__ytw])
        else:
            lxxk__vhmys = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, lxxk__vhmys)
        out_arr.dtype = lxxk__vhmys
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ruw__jwgvx = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = ruw__jwgvx
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ignky__mqp = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            ignky__mqp = int128_type
        elif arr_type == datetime_date_array_type:
            ignky__mqp = types.int64
        uzib__wtdv = types.Array(ignky__mqp, 1, 'C')
        axwl__ngru = context.make_array(uzib__wtdv)(context, builder)
        vjw__cswum = types.Array(types.uint8, 1, 'C')
        yop__tjlo = context.make_array(vjw__cswum)(context, builder)
        ukr__gdxdu = cgutils.alloca_once(builder, lir.IntType(64))
        aclj__outx = cgutils.alloca_once(builder, lir.IntType(64))
        kinv__bwfdu = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        otf__zspr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        gvi__capn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ktu__jpaj = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_to_nullable_array')
        builder.call(pwdpz__tgdky, [in_info, ukr__gdxdu, aclj__outx,
            kinv__bwfdu, otf__zspr, gvi__capn, ktu__jpaj])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        sew__ulcfr = context.get_value_type(types.intp)
        wpfs__tep = cgutils.pack_array(builder, [builder.load(ukr__gdxdu)],
            ty=sew__ulcfr)
        qtoic__omhlz = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(ignky__mqp)))
        kpgz__vgvo = cgutils.pack_array(builder, [qtoic__omhlz], ty=sew__ulcfr)
        ruw__jwgvx = builder.bitcast(builder.load(kinv__bwfdu), context.
            get_data_type(ignky__mqp).as_pointer())
        numba.np.arrayobj.populate_array(axwl__ngru, data=ruw__jwgvx, shape
            =wpfs__tep, strides=kpgz__vgvo, itemsize=qtoic__omhlz, meminfo=
            builder.load(gvi__capn))
        arr.data = axwl__ngru._getvalue()
        wpfs__tep = cgutils.pack_array(builder, [builder.load(aclj__outx)],
            ty=sew__ulcfr)
        qtoic__omhlz = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        kpgz__vgvo = cgutils.pack_array(builder, [qtoic__omhlz], ty=sew__ulcfr)
        ruw__jwgvx = builder.bitcast(builder.load(otf__zspr), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(yop__tjlo, data=ruw__jwgvx, shape=
            wpfs__tep, strides=kpgz__vgvo, itemsize=qtoic__omhlz, meminfo=
            builder.load(ktu__jpaj))
        arr.null_bitmap = yop__tjlo._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        cnm__hrf = context.make_array(arr_type.arr_type)(context, builder)
        iyke__qixi = context.make_array(arr_type.arr_type)(context, builder)
        ukr__gdxdu = cgutils.alloca_once(builder, lir.IntType(64))
        tyulv__iau = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        bjnp__zfwpn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        pitt__gkjtk = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        pfosl__sqg = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_to_interval_array')
        builder.call(pwdpz__tgdky, [in_info, ukr__gdxdu, tyulv__iau,
            bjnp__zfwpn, pitt__gkjtk, pfosl__sqg])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        sew__ulcfr = context.get_value_type(types.intp)
        wpfs__tep = cgutils.pack_array(builder, [builder.load(ukr__gdxdu)],
            ty=sew__ulcfr)
        qtoic__omhlz = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        kpgz__vgvo = cgutils.pack_array(builder, [qtoic__omhlz], ty=sew__ulcfr)
        jylwu__oum = builder.bitcast(builder.load(tyulv__iau), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(cnm__hrf, data=jylwu__oum, shape=
            wpfs__tep, strides=kpgz__vgvo, itemsize=qtoic__omhlz, meminfo=
            builder.load(pitt__gkjtk))
        arr.left = cnm__hrf._getvalue()
        dvmeb__eyz = builder.bitcast(builder.load(bjnp__zfwpn), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(iyke__qixi, data=dvmeb__eyz, shape
            =wpfs__tep, strides=kpgz__vgvo, itemsize=qtoic__omhlz, meminfo=
            builder.load(pfosl__sqg))
        arr.right = iyke__qixi._getvalue()
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
        okz__kxr, vbj__wyy = args
        wqv__pfi = numba_to_c_type(array_type.dtype)
        ggyj__wwk = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), wqv__pfi))
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='alloc_numpy')
        return builder.call(pwdpz__tgdky, [okz__kxr, builder.load(ggyj__wwk)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        okz__kxr, ptc__jooh = args
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='alloc_string_array')
        return builder.call(pwdpz__tgdky, [okz__kxr, ptc__jooh])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    yzvj__mniij, = args
    vetxc__ncm = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], yzvj__mniij)
    zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
        zmmnx__kfjvg, name='arr_info_list_to_table')
    return builder.call(pwdpz__tgdky, [vetxc__ncm.data, vetxc__ncm.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_from_table')
        return builder.call(pwdpz__tgdky, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    mavs__ogma = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        uwz__ieau, byd__gnd, vbj__wyy = args
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='info_from_table')
        hgj__lfo = cgutils.create_struct_proxy(mavs__ogma)(context, builder)
        hgj__lfo.parent = cgutils.get_null_value(hgj__lfo.parent.type)
        vld__yqqjf = context.make_array(table_idx_arr_t)(context, builder,
            byd__gnd)
        pqyl__fpjl = context.get_constant(types.int64, -1)
        cpe__laj = context.get_constant(types.int64, 0)
        gsztd__sbw = cgutils.alloca_once_value(builder, cpe__laj)
        for t, bxy__ehjxx in mavs__ogma.type_to_blk.items():
            ubdrt__okw = context.get_constant(types.int64, len(mavs__ogma.
                block_to_arr_ind[bxy__ehjxx]))
            vbj__wyy, hjec__flut = ListInstance.allocate_ex(context,
                builder, types.List(t), ubdrt__okw)
            hjec__flut.size = ubdrt__okw
            kdrmp__owlux = context.make_constant_array(builder, types.Array
                (types.int64, 1, 'C'), np.array(mavs__ogma.block_to_arr_ind
                [bxy__ehjxx], dtype=np.int64))
            tgo__gnsh = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, kdrmp__owlux)
            with cgutils.for_range(builder, ubdrt__okw) as neb__gup:
                fqb__zff = neb__gup.index
                wqvl__hjt = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    tgo__gnsh, fqb__zff)
                dhj__lnd = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, vld__yqqjf, wqvl__hjt)
                zjv__ijnp = builder.icmp_unsigned('!=', dhj__lnd, pqyl__fpjl)
                with builder.if_else(zjv__ijnp) as (iuwh__ugnp, cwdjm__fnqy):
                    with iuwh__ugnp:
                        vklp__gbzdm = builder.call(pwdpz__tgdky, [uwz__ieau,
                            dhj__lnd])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            vklp__gbzdm])
                        hjec__flut.inititem(fqb__zff, arr, incref=False)
                        okz__kxr = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(okz__kxr, gsztd__sbw)
                    with cwdjm__fnqy:
                        qdoel__runq = context.get_constant_null(t)
                        hjec__flut.inititem(fqb__zff, qdoel__runq, incref=False
                            )
            setattr(hgj__lfo, f'block_{bxy__ehjxx}', hjec__flut.value)
        hgj__lfo.len = builder.load(gsztd__sbw)
        return hgj__lfo._getvalue()
    return mavs__ogma(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    mavs__ogma = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        wlif__lkd, vbj__wyy = args
        ntqe__vnvk = cgutils.create_struct_proxy(mavs__ogma)(context,
            builder, wlif__lkd)
        if mavs__ogma.has_runtime_cols:
            fmwt__vbl = lir.Constant(lir.IntType(64), 0)
            for bxy__ehjxx, t in enumerate(mavs__ogma.arr_types):
                alcez__rdb = getattr(ntqe__vnvk, f'block_{bxy__ehjxx}')
                ucke__hnqw = ListInstance(context, builder, types.List(t),
                    alcez__rdb)
                fmwt__vbl = builder.add(fmwt__vbl, ucke__hnqw.size)
        else:
            fmwt__vbl = lir.Constant(lir.IntType(64), len(mavs__ogma.arr_types)
                )
        vbj__wyy, nvqk__gab = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), fmwt__vbl)
        nvqk__gab.size = fmwt__vbl
        if mavs__ogma.has_runtime_cols:
            mnf__etss = lir.Constant(lir.IntType(64), 0)
            for bxy__ehjxx, t in enumerate(mavs__ogma.arr_types):
                alcez__rdb = getattr(ntqe__vnvk, f'block_{bxy__ehjxx}')
                ucke__hnqw = ListInstance(context, builder, types.List(t),
                    alcez__rdb)
                ubdrt__okw = ucke__hnqw.size
                with cgutils.for_range(builder, ubdrt__okw) as neb__gup:
                    fqb__zff = neb__gup.index
                    arr = ucke__hnqw.getitem(fqb__zff)
                    uoi__pqd = signature(array_info_type, t)
                    tfdk__wfb = arr,
                    ipnts__nrt = array_to_info_codegen(context, builder,
                        uoi__pqd, tfdk__wfb)
                    nvqk__gab.inititem(builder.add(mnf__etss, fqb__zff),
                        ipnts__nrt, incref=False)
                mnf__etss = builder.add(mnf__etss, ubdrt__okw)
        else:
            for t, bxy__ehjxx in mavs__ogma.type_to_blk.items():
                ubdrt__okw = context.get_constant(types.int64, len(
                    mavs__ogma.block_to_arr_ind[bxy__ehjxx]))
                alcez__rdb = getattr(ntqe__vnvk, f'block_{bxy__ehjxx}')
                ucke__hnqw = ListInstance(context, builder, types.List(t),
                    alcez__rdb)
                kdrmp__owlux = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(mavs__ogma.
                    block_to_arr_ind[bxy__ehjxx], dtype=np.int64))
                tgo__gnsh = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, kdrmp__owlux)
                with cgutils.for_range(builder, ubdrt__okw) as neb__gup:
                    fqb__zff = neb__gup.index
                    wqvl__hjt = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        tgo__gnsh, fqb__zff)
                    sfva__ykwyz = signature(types.none, mavs__ogma, types.
                        List(t), types.int64, types.int64)
                    jju__kwjca = wlif__lkd, alcez__rdb, fqb__zff, wqvl__hjt
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, sfva__ykwyz, jju__kwjca)
                    arr = ucke__hnqw.getitem(fqb__zff)
                    uoi__pqd = signature(array_info_type, t)
                    tfdk__wfb = arr,
                    ipnts__nrt = array_to_info_codegen(context, builder,
                        uoi__pqd, tfdk__wfb)
                    nvqk__gab.inititem(wqvl__hjt, ipnts__nrt, incref=False)
        tvogc__iyj = nvqk__gab.value
        agh__ckwqv = signature(table_type, types.List(array_info_type))
        knkia__nio = tvogc__iyj,
        uwz__ieau = arr_info_list_to_table_codegen(context, builder,
            agh__ckwqv, knkia__nio)
        context.nrt.decref(builder, types.List(array_info_type), tvogc__iyj)
        return uwz__ieau
    return table_type(mavs__ogma, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='delete_table')
        builder.call(pwdpz__tgdky, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='shuffle_table')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
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
        zmmnx__kfjvg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='delete_shuffle_info')
        return builder.call(pwdpz__tgdky, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='reverse_shuffle_table')
        return builder.call(pwdpz__tgdky, args)
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
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='hash_join_table')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
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
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='sort_values_table')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='sample_table')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='shuffle_renormalization')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='shuffle_renormalization_group')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='drop_duplicates_table')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
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
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='pivot_groupby_and_aggregate')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
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
        zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        pwdpz__tgdky = cgutils.get_or_insert_function(builder.module,
            zmmnx__kfjvg, name='groupby_and_aggregate')
        hytt__nwnd = builder.call(pwdpz__tgdky, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return hytt__nwnd
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
    yqhrj__idp = array_to_info(in_arr)
    lpi__itl = array_to_info(in_values)
    hzzwc__sxph = array_to_info(out_arr)
    rkvs__jrs = arr_info_list_to_table([yqhrj__idp, lpi__itl, hzzwc__sxph])
    _array_isin(hzzwc__sxph, yqhrj__idp, lpi__itl, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(rkvs__jrs)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, pat, out_arr):
    yqhrj__idp = array_to_info(in_arr)
    hzzwc__sxph = array_to_info(out_arr)
    _get_search_regex(yqhrj__idp, case, pat, hzzwc__sxph)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    naxu__sox = col_array_typ.dtype
    if isinstance(naxu__sox, types.Number) or naxu__sox in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hgj__lfo, zut__papx = args
                hgj__lfo = builder.bitcast(hgj__lfo, lir.IntType(8).
                    as_pointer().as_pointer())
                tzkl__whgt = lir.Constant(lir.IntType(64), c_ind)
                ywm__pwdz = builder.load(builder.gep(hgj__lfo, [tzkl__whgt]))
                ywm__pwdz = builder.bitcast(ywm__pwdz, context.
                    get_data_type(naxu__sox).as_pointer())
                return builder.load(builder.gep(ywm__pwdz, [zut__papx]))
            return naxu__sox(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.string_array_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hgj__lfo, zut__papx = args
                hgj__lfo = builder.bitcast(hgj__lfo, lir.IntType(8).
                    as_pointer().as_pointer())
                tzkl__whgt = lir.Constant(lir.IntType(64), c_ind)
                ywm__pwdz = builder.load(builder.gep(hgj__lfo, [tzkl__whgt]))
                zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                bbjhd__ues = cgutils.get_or_insert_function(builder.module,
                    zmmnx__kfjvg, name='array_info_getitem')
                pzpe__htadc = cgutils.alloca_once(builder, lir.IntType(64))
                args = ywm__pwdz, zut__papx, pzpe__htadc
                kinv__bwfdu = builder.call(bbjhd__ues, args)
                return context.make_tuple(builder, sig.return_type, [
                    kinv__bwfdu, builder.load(pzpe__htadc)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                bqmjb__mdst = lir.Constant(lir.IntType(64), 1)
                uan__rtv = lir.Constant(lir.IntType(64), 2)
                hgj__lfo, zut__papx = args
                hgj__lfo = builder.bitcast(hgj__lfo, lir.IntType(8).
                    as_pointer().as_pointer())
                tzkl__whgt = lir.Constant(lir.IntType(64), c_ind)
                ywm__pwdz = builder.load(builder.gep(hgj__lfo, [tzkl__whgt]))
                zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                eatd__jkj = cgutils.get_or_insert_function(builder.module,
                    zmmnx__kfjvg, name='get_nested_info')
                args = ywm__pwdz, uan__rtv
                kur__qaec = builder.call(eatd__jkj, args)
                zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                ufmyz__nhwkq = cgutils.get_or_insert_function(builder.
                    module, zmmnx__kfjvg, name='array_info_getdata1')
                args = kur__qaec,
                zhrgj__ogjx = builder.call(ufmyz__nhwkq, args)
                zhrgj__ogjx = builder.bitcast(zhrgj__ogjx, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                shaj__auc = builder.sext(builder.load(builder.gep(
                    zhrgj__ogjx, [zut__papx])), lir.IntType(64))
                args = ywm__pwdz, bqmjb__mdst
                uos__rptat = builder.call(eatd__jkj, args)
                zmmnx__kfjvg = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                bbjhd__ues = cgutils.get_or_insert_function(builder.module,
                    zmmnx__kfjvg, name='array_info_getitem')
                pzpe__htadc = cgutils.alloca_once(builder, lir.IntType(64))
                args = uos__rptat, shaj__auc, pzpe__htadc
                kinv__bwfdu = builder.call(bbjhd__ues, args)
                return context.make_tuple(builder, sig.return_type, [
                    kinv__bwfdu, builder.load(pzpe__htadc)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{naxu__sox}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if (isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType) or
        col_array_dtype == bodo.libs.bool_arr_ext.boolean_array or
        is_str_arr_type(col_array_dtype) or isinstance(col_array_dtype,
        types.Array) and col_array_dtype.dtype == bodo.datetime_date_type):

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xqpq__zqo, zut__papx = args
                xqpq__zqo = builder.bitcast(xqpq__zqo, lir.IntType(8).
                    as_pointer().as_pointer())
                tzkl__whgt = lir.Constant(lir.IntType(64), c_ind)
                ywm__pwdz = builder.load(builder.gep(xqpq__zqo, [tzkl__whgt]))
                cdyj__rnzup = builder.bitcast(ywm__pwdz, context.
                    get_data_type(types.bool_).as_pointer())
                vxy__plrgw = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    cdyj__rnzup, zut__papx)
                lwg__orffk = builder.icmp_unsigned('!=', vxy__plrgw, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(lwg__orffk, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        naxu__sox = col_array_dtype.dtype
        if naxu__sox in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    hgj__lfo, zut__papx = args
                    hgj__lfo = builder.bitcast(hgj__lfo, lir.IntType(8).
                        as_pointer().as_pointer())
                    tzkl__whgt = lir.Constant(lir.IntType(64), c_ind)
                    ywm__pwdz = builder.load(builder.gep(hgj__lfo, [
                        tzkl__whgt]))
                    ywm__pwdz = builder.bitcast(ywm__pwdz, context.
                        get_data_type(naxu__sox).as_pointer())
                    gxhwo__wszp = builder.load(builder.gep(ywm__pwdz, [
                        zut__papx]))
                    lwg__orffk = builder.icmp_unsigned('!=', gxhwo__wszp,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(lwg__orffk, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(naxu__sox, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    hgj__lfo, zut__papx = args
                    hgj__lfo = builder.bitcast(hgj__lfo, lir.IntType(8).
                        as_pointer().as_pointer())
                    tzkl__whgt = lir.Constant(lir.IntType(64), c_ind)
                    ywm__pwdz = builder.load(builder.gep(hgj__lfo, [
                        tzkl__whgt]))
                    ywm__pwdz = builder.bitcast(ywm__pwdz, context.
                        get_data_type(naxu__sox).as_pointer())
                    gxhwo__wszp = builder.load(builder.gep(ywm__pwdz, [
                        zut__papx]))
                    cxbxb__tegx = signature(types.bool_, naxu__sox)
                    vxy__plrgw = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, cxbxb__tegx, (gxhwo__wszp,))
                    return builder.not_(builder.sext(vxy__plrgw, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
