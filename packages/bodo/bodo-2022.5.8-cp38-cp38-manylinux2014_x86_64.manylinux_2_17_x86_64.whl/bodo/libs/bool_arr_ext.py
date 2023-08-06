"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nigsc__lvn = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, nigsc__lvn)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    ifuav__qngv = c.context.insert_const_string(c.builder.module, 'pandas')
    irry__hxlwn = c.pyapi.import_module_noblock(ifuav__qngv)
    uuda__amors = c.pyapi.call_method(irry__hxlwn, 'BooleanDtype', ())
    c.pyapi.decref(irry__hxlwn)
    return uuda__amors


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    qrcz__enkw = n + 7 >> 3
    return np.full(qrcz__enkw, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    nzs__yaozt = c.context.typing_context.resolve_value_type(func)
    jbyne__kmuk = nzs__yaozt.get_call_type(c.context.typing_context,
        arg_typs, {})
    bcbs__teemv = c.context.get_function(nzs__yaozt, jbyne__kmuk)
    luwj__khq = c.context.call_conv.get_function_type(jbyne__kmuk.
        return_type, jbyne__kmuk.args)
    gscpu__uhhwa = c.builder.module
    wwggu__kepv = lir.Function(gscpu__uhhwa, luwj__khq, name=gscpu__uhhwa.
        get_unique_name('.func_conv'))
    wwggu__kepv.linkage = 'internal'
    jwxo__uxxa = lir.IRBuilder(wwggu__kepv.append_basic_block())
    mikna__izqe = c.context.call_conv.decode_arguments(jwxo__uxxa,
        jbyne__kmuk.args, wwggu__kepv)
    juead__uvwbf = bcbs__teemv(jwxo__uxxa, mikna__izqe)
    c.context.call_conv.return_value(jwxo__uxxa, juead__uvwbf)
    pvij__aihvc, msu__ddx = c.context.call_conv.call_function(c.builder,
        wwggu__kepv, jbyne__kmuk.return_type, jbyne__kmuk.args, args)
    return msu__ddx


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    qgwd__xgvcn = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(qgwd__xgvcn)
    c.pyapi.decref(qgwd__xgvcn)
    luwj__khq = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    spxe__okwvd = cgutils.get_or_insert_function(c.builder.module,
        luwj__khq, name='is_bool_array')
    luwj__khq = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    wwggu__kepv = cgutils.get_or_insert_function(c.builder.module,
        luwj__khq, name='is_pd_boolean_array')
    lnbrd__qvwt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rpwve__yog = c.builder.call(wwggu__kepv, [obj])
    yjdw__kidps = c.builder.icmp_unsigned('!=', rpwve__yog, rpwve__yog.type(0))
    with c.builder.if_else(yjdw__kidps) as (vfaf__xrk, djqcj__uyf):
        with vfaf__xrk:
            jvklg__znixv = c.pyapi.object_getattr_string(obj, '_data')
            lnbrd__qvwt.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), jvklg__znixv).value
            esc__lkv = c.pyapi.object_getattr_string(obj, '_mask')
            fim__ldl = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), esc__lkv).value
            qrcz__enkw = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            yfb__qrdv = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, fim__ldl)
            tgln__cupi = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [qrcz__enkw])
            luwj__khq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            wwggu__kepv = cgutils.get_or_insert_function(c.builder.module,
                luwj__khq, name='mask_arr_to_bitmap')
            c.builder.call(wwggu__kepv, [tgln__cupi.data, yfb__qrdv.data, n])
            lnbrd__qvwt.null_bitmap = tgln__cupi._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), fim__ldl)
            c.pyapi.decref(jvklg__znixv)
            c.pyapi.decref(esc__lkv)
        with djqcj__uyf:
            hwiu__sdlni = c.builder.call(spxe__okwvd, [obj])
            ruuae__dygfw = c.builder.icmp_unsigned('!=', hwiu__sdlni,
                hwiu__sdlni.type(0))
            with c.builder.if_else(ruuae__dygfw) as (qjj__omj, mlzt__icuzf):
                with qjj__omj:
                    lnbrd__qvwt.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    lnbrd__qvwt.null_bitmap = call_func_in_unbox(
                        gen_full_bitmap, (n,), (types.int64,), c)
                with mlzt__icuzf:
                    lnbrd__qvwt.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    qrcz__enkw = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    lnbrd__qvwt.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [qrcz__enkw])._getvalue()
                    iunrx__uhon = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, lnbrd__qvwt.data
                        ).data
                    fgh__hbhxj = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, lnbrd__qvwt.
                        null_bitmap).data
                    luwj__khq = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    wwggu__kepv = cgutils.get_or_insert_function(c.builder.
                        module, luwj__khq, name='unbox_bool_array_obj')
                    c.builder.call(wwggu__kepv, [obj, iunrx__uhon,
                        fgh__hbhxj, n])
    return NativeValue(lnbrd__qvwt._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    lnbrd__qvwt = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        lnbrd__qvwt.data, c.env_manager)
    xoj__gkd = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, lnbrd__qvwt.null_bitmap).data
    qgwd__xgvcn = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(qgwd__xgvcn)
    ifuav__qngv = c.context.insert_const_string(c.builder.module, 'numpy')
    jaktd__cedre = c.pyapi.import_module_noblock(ifuav__qngv)
    hhze__mwvkj = c.pyapi.object_getattr_string(jaktd__cedre, 'bool_')
    fim__ldl = c.pyapi.call_method(jaktd__cedre, 'empty', (qgwd__xgvcn,
        hhze__mwvkj))
    pwijs__dmxjs = c.pyapi.object_getattr_string(fim__ldl, 'ctypes')
    etsui__sdebn = c.pyapi.object_getattr_string(pwijs__dmxjs, 'data')
    gxjm__nnfn = c.builder.inttoptr(c.pyapi.long_as_longlong(etsui__sdebn),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as ios__xfdev:
        vkf__mdw = ios__xfdev.index
        tvt__ouj = c.builder.lshr(vkf__mdw, lir.Constant(lir.IntType(64), 3))
        ljvf__yokgj = c.builder.load(cgutils.gep(c.builder, xoj__gkd, tvt__ouj)
            )
        pavuv__stya = c.builder.trunc(c.builder.and_(vkf__mdw, lir.Constant
            (lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ljvf__yokgj, pavuv__stya), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        rsth__touwi = cgutils.gep(c.builder, gxjm__nnfn, vkf__mdw)
        c.builder.store(val, rsth__touwi)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        lnbrd__qvwt.null_bitmap)
    ifuav__qngv = c.context.insert_const_string(c.builder.module, 'pandas')
    irry__hxlwn = c.pyapi.import_module_noblock(ifuav__qngv)
    vlyvi__rbnf = c.pyapi.object_getattr_string(irry__hxlwn, 'arrays')
    uuda__amors = c.pyapi.call_method(vlyvi__rbnf, 'BooleanArray', (data,
        fim__ldl))
    c.pyapi.decref(irry__hxlwn)
    c.pyapi.decref(qgwd__xgvcn)
    c.pyapi.decref(jaktd__cedre)
    c.pyapi.decref(hhze__mwvkj)
    c.pyapi.decref(pwijs__dmxjs)
    c.pyapi.decref(etsui__sdebn)
    c.pyapi.decref(vlyvi__rbnf)
    c.pyapi.decref(data)
    c.pyapi.decref(fim__ldl)
    return uuda__amors


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    gbd__aca = np.empty(n, np.bool_)
    dzgib__qqw = np.empty(n + 7 >> 3, np.uint8)
    for vkf__mdw, s in enumerate(pyval):
        yzxf__zur = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(dzgib__qqw, vkf__mdw, int(not
            yzxf__zur))
        if not yzxf__zur:
            gbd__aca[vkf__mdw] = s
    euwf__fmyx = context.get_constant_generic(builder, data_type, gbd__aca)
    ghw__ngcn = context.get_constant_generic(builder, nulls_type, dzgib__qqw)
    return lir.Constant.literal_struct([euwf__fmyx, ghw__ngcn])


def lower_init_bool_array(context, builder, signature, args):
    tbb__uds, svlgh__qwxnw = args
    lnbrd__qvwt = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    lnbrd__qvwt.data = tbb__uds
    lnbrd__qvwt.null_bitmap = svlgh__qwxnw
    context.nrt.incref(builder, signature.args[0], tbb__uds)
    context.nrt.incref(builder, signature.args[1], svlgh__qwxnw)
    return lnbrd__qvwt._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    kciog__oge = args[0]
    if equiv_set.has_shape(kciog__oge):
        return ArrayAnalysis.AnalyzeResult(shape=kciog__oge, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    kciog__oge = args[0]
    if equiv_set.has_shape(kciog__oge):
        return ArrayAnalysis.AnalyzeResult(shape=kciog__oge, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    gbd__aca = np.empty(n, dtype=np.bool_)
    kjpy__vtmo = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(gbd__aca, kjpy__vtmo)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            vxvbe__ktz, dtngl__xdc = array_getitem_bool_index(A, ind)
            return init_bool_array(vxvbe__ktz, dtngl__xdc)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            vxvbe__ktz, dtngl__xdc = array_getitem_int_index(A, ind)
            return init_bool_array(vxvbe__ktz, dtngl__xdc)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            vxvbe__ktz, dtngl__xdc = array_getitem_slice_index(A, ind)
            return init_bool_array(vxvbe__ktz, dtngl__xdc)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    oazt__fdm = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(oazt__fdm)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(oazt__fdm)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'size')
def overload_bool_arr_size(A):
    return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for vkf__mdw in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, vkf__mdw):
                val = A[vkf__mdw]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            bzdl__sttpy = np.empty(n, nb_dtype)
            for vkf__mdw in numba.parfors.parfor.internal_prange(n):
                bzdl__sttpy[vkf__mdw] = data[vkf__mdw]
                if bodo.libs.array_kernels.isna(A, vkf__mdw):
                    bzdl__sttpy[vkf__mdw] = np.nan
            return bzdl__sttpy
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        bzdl__sttpy = np.empty(n, dtype=np.bool_)
        for vkf__mdw in numba.parfors.parfor.internal_prange(n):
            bzdl__sttpy[vkf__mdw] = data[vkf__mdw]
            if bodo.libs.array_kernels.isna(A, vkf__mdw):
                bzdl__sttpy[vkf__mdw] = value
        return bzdl__sttpy
    return impl


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    ukz__sefst = op.__name__
    ukz__sefst = ufunc_aliases.get(ukz__sefst, ukz__sefst)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for lyhx__bnzmw in numba.np.ufunc_db.get_ufuncs():
        xiqp__akkfp = create_op_overload(lyhx__bnzmw, lyhx__bnzmw.nin)
        overload(lyhx__bnzmw, no_unliteral=True)(xiqp__akkfp)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        xiqp__akkfp = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(xiqp__akkfp)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        xiqp__akkfp = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(xiqp__akkfp)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        xiqp__akkfp = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(xiqp__akkfp)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        pavuv__stya = []
        qpaag__wbhwx = False
        axype__ynes = False
        miz__mnob = False
        for vkf__mdw in range(len(A)):
            if bodo.libs.array_kernels.isna(A, vkf__mdw):
                if not qpaag__wbhwx:
                    data.append(False)
                    pavuv__stya.append(False)
                    qpaag__wbhwx = True
                continue
            val = A[vkf__mdw]
            if val and not axype__ynes:
                data.append(True)
                pavuv__stya.append(True)
                axype__ynes = True
            if not val and not miz__mnob:
                data.append(False)
                pavuv__stya.append(True)
                miz__mnob = True
            if qpaag__wbhwx and axype__ynes and miz__mnob:
                break
        vxvbe__ktz = np.array(data)
        n = len(vxvbe__ktz)
        qrcz__enkw = 1
        dtngl__xdc = np.empty(qrcz__enkw, np.uint8)
        for qjl__wkaai in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(dtngl__xdc, qjl__wkaai,
                pavuv__stya[qjl__wkaai])
        return init_bool_array(vxvbe__ktz, dtngl__xdc)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    uuda__amors = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, uuda__amors)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    uxqp__skc = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        rkanc__oczbp = bodo.utils.utils.is_array_typ(val1, False)
        rvsj__eqcmg = bodo.utils.utils.is_array_typ(val2, False)
        cgxm__wnrry = 'val1' if rkanc__oczbp else 'val2'
        dzqyl__jqq = 'def impl(val1, val2):\n'
        dzqyl__jqq += f'  n = len({cgxm__wnrry})\n'
        dzqyl__jqq += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        dzqyl__jqq += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if rkanc__oczbp:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            wtqfv__ivx = 'val1[i]'
        else:
            null1 = 'False\n'
            wtqfv__ivx = 'val1'
        if rvsj__eqcmg:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            lqslu__bdo = 'val2[i]'
        else:
            null2 = 'False\n'
            lqslu__bdo = 'val2'
        if uxqp__skc:
            dzqyl__jqq += f"""    result, isna_val = compute_or_body({null1}, {null2}, {wtqfv__ivx}, {lqslu__bdo})
"""
        else:
            dzqyl__jqq += f"""    result, isna_val = compute_and_body({null1}, {null2}, {wtqfv__ivx}, {lqslu__bdo})
"""
        dzqyl__jqq += '    out_arr[i] = result\n'
        dzqyl__jqq += '    if isna_val:\n'
        dzqyl__jqq += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        dzqyl__jqq += '      continue\n'
        dzqyl__jqq += '  return out_arr\n'
        gtt__akhn = {}
        exec(dzqyl__jqq, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, gtt__akhn)
        impl = gtt__akhn['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        awsci__ubzft = boolean_array
        return awsci__ubzft(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    glg__nnhv = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return glg__nnhv


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        hyt__trkdv = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(hyt__trkdv)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(hyt__trkdv)


_install_nullable_logical_lowering()
