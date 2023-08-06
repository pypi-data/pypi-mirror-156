"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    txj__ixdj = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(txj__ixdj)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        redhi__mra = _get_map_arr_data_type(fe_type)
        zaco__uqiv = [('data', redhi__mra)]
        models.StructModel.__init__(self, dmm, fe_type, zaco__uqiv)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    tyweo__rig = all(isinstance(aety__gbk, types.Array) and aety__gbk.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        aety__gbk in (typ.key_arr_type, typ.value_arr_type))
    if tyweo__rig:
        zzcj__hcyob = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        oemma__zdfkr = cgutils.get_or_insert_function(c.builder.module,
            zzcj__hcyob, name='count_total_elems_list_array')
        iibf__gpouw = cgutils.pack_array(c.builder, [n_maps, c.builder.call
            (oemma__zdfkr, [val])])
    else:
        iibf__gpouw = get_array_elem_counts(c, c.builder, c.context, val, typ)
    redhi__mra = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, redhi__mra,
        iibf__gpouw, c)
    zvlzj__mhz = _get_array_item_arr_payload(c.context, c.builder,
        redhi__mra, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, zvlzj__mhz.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, zvlzj__mhz.offsets).data
    yasx__dvz = _get_struct_arr_payload(c.context, c.builder, redhi__mra.
        dtype, zvlzj__mhz.data)
    key_arr = c.builder.extract_value(yasx__dvz.data, 0)
    value_arr = c.builder.extract_value(yasx__dvz.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    mydia__pgse, rtt__vnr = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [yasx__dvz.null_bitmap])
    if tyweo__rig:
        iquyl__aaayh = c.context.make_array(redhi__mra.dtype.data[0])(c.
            context, c.builder, key_arr).data
        dqmux__atdc = c.context.make_array(redhi__mra.dtype.data[1])(c.
            context, c.builder, value_arr).data
        zzcj__hcyob = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        ezjg__vzjjl = cgutils.get_or_insert_function(c.builder.module,
            zzcj__hcyob, name='map_array_from_sequence')
        iolm__mnadq = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        idzal__yrz = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(ezjg__vzjjl, [val, c.builder.bitcast(iquyl__aaayh,
            lir.IntType(8).as_pointer()), c.builder.bitcast(dqmux__atdc,
            lir.IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir
            .Constant(lir.IntType(32), iolm__mnadq), lir.Constant(lir.
            IntType(32), idzal__yrz)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    ewol__zeud = c.context.make_helper(c.builder, typ)
    ewol__zeud.data = data_arr
    knfc__wbikt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ewol__zeud._getvalue(), is_error=knfc__wbikt)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    zao__hdjm = context.insert_const_string(builder.module, 'pandas')
    xsbw__ifr = c.pyapi.import_module_noblock(zao__hdjm)
    oaqdp__bhfiy = c.pyapi.object_getattr_string(xsbw__ifr, 'NA')
    jah__lpq = c.context.get_constant(offset_type, 0)
    builder.store(jah__lpq, offsets_ptr)
    ruiwr__dih = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as ahit__uyqu:
        bgkg__vagop = ahit__uyqu.index
        item_ind = builder.load(ruiwr__dih)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [bgkg__vagop]))
        mdzz__bbk = seq_getitem(builder, context, val, bgkg__vagop)
        set_bitmap_bit(builder, null_bitmap_ptr, bgkg__vagop, 0)
        aoe__mosjw = is_na_value(builder, context, mdzz__bbk, oaqdp__bhfiy)
        qbba__qep = builder.icmp_unsigned('!=', aoe__mosjw, lir.Constant(
            aoe__mosjw.type, 1))
        with builder.if_then(qbba__qep):
            set_bitmap_bit(builder, null_bitmap_ptr, bgkg__vagop, 1)
            fonhf__mgiu = dict_keys(builder, context, mdzz__bbk)
            koi__vtsos = dict_values(builder, context, mdzz__bbk)
            n_items = bodo.utils.utils.object_length(c, fonhf__mgiu)
            _unbox_array_item_array_copy_data(typ.key_arr_type, fonhf__mgiu,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                koi__vtsos, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), ruiwr__dih)
            c.pyapi.decref(fonhf__mgiu)
            c.pyapi.decref(koi__vtsos)
        c.pyapi.decref(mdzz__bbk)
    builder.store(builder.trunc(builder.load(ruiwr__dih), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(xsbw__ifr)
    c.pyapi.decref(oaqdp__bhfiy)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    ewol__zeud = c.context.make_helper(c.builder, typ, val)
    data_arr = ewol__zeud.data
    redhi__mra = _get_map_arr_data_type(typ)
    zvlzj__mhz = _get_array_item_arr_payload(c.context, c.builder,
        redhi__mra, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, zvlzj__mhz.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, zvlzj__mhz.offsets).data
    yasx__dvz = _get_struct_arr_payload(c.context, c.builder, redhi__mra.
        dtype, zvlzj__mhz.data)
    key_arr = c.builder.extract_value(yasx__dvz.data, 0)
    value_arr = c.builder.extract_value(yasx__dvz.data, 1)
    if all(isinstance(aety__gbk, types.Array) and aety__gbk.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type) for
        aety__gbk in (typ.key_arr_type, typ.value_arr_type)):
        iquyl__aaayh = c.context.make_array(redhi__mra.dtype.data[0])(c.
            context, c.builder, key_arr).data
        dqmux__atdc = c.context.make_array(redhi__mra.dtype.data[1])(c.
            context, c.builder, value_arr).data
        zzcj__hcyob = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        cve__etaxf = cgutils.get_or_insert_function(c.builder.module,
            zzcj__hcyob, name='np_array_from_map_array')
        iolm__mnadq = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        idzal__yrz = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(cve__etaxf, [zvlzj__mhz.n_arrays, c.builder.
            bitcast(iquyl__aaayh, lir.IntType(8).as_pointer()), c.builder.
            bitcast(dqmux__atdc, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), iolm__mnadq),
            lir.Constant(lir.IntType(32), idzal__yrz)])
    else:
        arr = _box_map_array_generic(typ, c, zvlzj__mhz.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    zao__hdjm = context.insert_const_string(builder.module, 'numpy')
    mjuj__pbd = c.pyapi.import_module_noblock(zao__hdjm)
    vef__vnwha = c.pyapi.object_getattr_string(mjuj__pbd, 'object_')
    ygo__lidu = c.pyapi.long_from_longlong(n_maps)
    rph__nwm = c.pyapi.call_method(mjuj__pbd, 'ndarray', (ygo__lidu,
        vef__vnwha))
    mmq__ujqw = c.pyapi.object_getattr_string(mjuj__pbd, 'nan')
    qtob__yha = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    ruiwr__dih = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as ahit__uyqu:
        bws__gjo = ahit__uyqu.index
        pyarray_setitem(builder, context, rph__nwm, bws__gjo, mmq__ujqw)
        nsvvb__vgue = get_bitmap_bit(builder, null_bitmap_ptr, bws__gjo)
        efc__cruq = builder.icmp_unsigned('!=', nsvvb__vgue, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(efc__cruq):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(bws__gjo, lir.Constant(bws__gjo.
                type, 1))])), builder.load(builder.gep(offsets_ptr, [
                bws__gjo]))), lir.IntType(64))
            item_ind = builder.load(ruiwr__dih)
            mdzz__bbk = c.pyapi.dict_new()
            rmkk__ljjfg = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            mydia__pgse, thone__odsy = c.pyapi.call_jit_code(rmkk__ljjfg,
                typ.key_arr_type(typ.key_arr_type, types.int64, types.int64
                ), [key_arr, item_ind, n_items])
            mydia__pgse, kok__ovix = c.pyapi.call_jit_code(rmkk__ljjfg, typ
                .value_arr_type(typ.value_arr_type, types.int64, types.
                int64), [value_arr, item_ind, n_items])
            sue__fdlbv = c.pyapi.from_native_value(typ.key_arr_type,
                thone__odsy, c.env_manager)
            gku__dfvz = c.pyapi.from_native_value(typ.value_arr_type,
                kok__ovix, c.env_manager)
            jwh__oqzdt = c.pyapi.call_function_objargs(qtob__yha, (
                sue__fdlbv, gku__dfvz))
            dict_merge_from_seq2(builder, context, mdzz__bbk, jwh__oqzdt)
            builder.store(builder.add(item_ind, n_items), ruiwr__dih)
            pyarray_setitem(builder, context, rph__nwm, bws__gjo, mdzz__bbk)
            c.pyapi.decref(jwh__oqzdt)
            c.pyapi.decref(sue__fdlbv)
            c.pyapi.decref(gku__dfvz)
            c.pyapi.decref(mdzz__bbk)
    c.pyapi.decref(qtob__yha)
    c.pyapi.decref(mjuj__pbd)
    c.pyapi.decref(vef__vnwha)
    c.pyapi.decref(ygo__lidu)
    c.pyapi.decref(mmq__ujqw)
    return rph__nwm


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    ewol__zeud = context.make_helper(builder, sig.return_type)
    ewol__zeud.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return ewol__zeud._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    edyl__krby = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return edyl__krby(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    ohg__pfb = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(num_maps
        , nested_counts, struct_typ)
    return init_map_arr(ohg__pfb)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    vff__wduyf = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            vsee__rksb = val.keys()
            mnplw__bvp = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), vff__wduyf, ('key', 'value'))
            for yvwdq__jacfc, mcg__lacg in enumerate(vsee__rksb):
                mnplw__bvp[yvwdq__jacfc
                    ] = bodo.libs.struct_arr_ext.init_struct((mcg__lacg,
                    val[mcg__lacg]), ('key', 'value'))
            arr._data[ind] = mnplw__bvp
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            zui__rcd = dict()
            euied__ysgr = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            mnplw__bvp = bodo.libs.array_item_arr_ext.get_data(arr._data)
            qnvfq__wbd, auil__lpq = bodo.libs.struct_arr_ext.get_data(
                mnplw__bvp)
            jgh__nab = euied__ysgr[ind]
            jko__ila = euied__ysgr[ind + 1]
            for yvwdq__jacfc in range(jgh__nab, jko__ila):
                zui__rcd[qnvfq__wbd[yvwdq__jacfc]] = auil__lpq[yvwdq__jacfc]
            return zui__rcd
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
