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
        mul__qvql = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, mul__qvql)


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
    fbl__glhax = c.context.insert_const_string(c.builder.module, 'pandas')
    vcj__kmsx = c.pyapi.import_module_noblock(fbl__glhax)
    xaxe__fngds = c.pyapi.call_method(vcj__kmsx, 'BooleanDtype', ())
    c.pyapi.decref(vcj__kmsx)
    return xaxe__fngds


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    ptilz__gmw = n + 7 >> 3
    return np.full(ptilz__gmw, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    abvg__sev = c.context.typing_context.resolve_value_type(func)
    jxar__mff = abvg__sev.get_call_type(c.context.typing_context, arg_typs, {})
    xsad__qbn = c.context.get_function(abvg__sev, jxar__mff)
    jijn__bokow = c.context.call_conv.get_function_type(jxar__mff.
        return_type, jxar__mff.args)
    jfszp__gas = c.builder.module
    lncxh__gxk = lir.Function(jfszp__gas, jijn__bokow, name=jfszp__gas.
        get_unique_name('.func_conv'))
    lncxh__gxk.linkage = 'internal'
    yqpx__vvo = lir.IRBuilder(lncxh__gxk.append_basic_block())
    kya__lhu = c.context.call_conv.decode_arguments(yqpx__vvo, jxar__mff.
        args, lncxh__gxk)
    lti__zuuzk = xsad__qbn(yqpx__vvo, kya__lhu)
    c.context.call_conv.return_value(yqpx__vvo, lti__zuuzk)
    trwwx__hdimk, hueo__inmq = c.context.call_conv.call_function(c.builder,
        lncxh__gxk, jxar__mff.return_type, jxar__mff.args, args)
    return hueo__inmq


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    sgtms__hniwu = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(sgtms__hniwu)
    c.pyapi.decref(sgtms__hniwu)
    jijn__bokow = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    wdy__iaw = cgutils.get_or_insert_function(c.builder.module, jijn__bokow,
        name='is_bool_array')
    jijn__bokow = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    lncxh__gxk = cgutils.get_or_insert_function(c.builder.module,
        jijn__bokow, name='is_pd_boolean_array')
    cxvyc__eegqa = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    usfya__hsbhg = c.builder.call(lncxh__gxk, [obj])
    nzd__omvqu = c.builder.icmp_unsigned('!=', usfya__hsbhg, usfya__hsbhg.
        type(0))
    with c.builder.if_else(nzd__omvqu) as (ehro__rzq, wqw__jbjd):
        with ehro__rzq:
            xiss__jiqx = c.pyapi.object_getattr_string(obj, '_data')
            cxvyc__eegqa.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), xiss__jiqx).value
            bil__hjfjz = c.pyapi.object_getattr_string(obj, '_mask')
            qlby__xvvxs = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), bil__hjfjz).value
            ptilz__gmw = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            pfyg__ovwfz = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, qlby__xvvxs)
            mmmn__qhl = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [ptilz__gmw])
            jijn__bokow = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            lncxh__gxk = cgutils.get_or_insert_function(c.builder.module,
                jijn__bokow, name='mask_arr_to_bitmap')
            c.builder.call(lncxh__gxk, [mmmn__qhl.data, pfyg__ovwfz.data, n])
            cxvyc__eegqa.null_bitmap = mmmn__qhl._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), qlby__xvvxs)
            c.pyapi.decref(xiss__jiqx)
            c.pyapi.decref(bil__hjfjz)
        with wqw__jbjd:
            pyiq__edq = c.builder.call(wdy__iaw, [obj])
            ykrbp__wpgtp = c.builder.icmp_unsigned('!=', pyiq__edq,
                pyiq__edq.type(0))
            with c.builder.if_else(ykrbp__wpgtp) as (cixce__cajvc, eprzn__zsv):
                with cixce__cajvc:
                    cxvyc__eegqa.data = c.pyapi.to_native_value(types.Array
                        (types.bool_, 1, 'C'), obj).value
                    cxvyc__eegqa.null_bitmap = call_func_in_unbox(
                        gen_full_bitmap, (n,), (types.int64,), c)
                with eprzn__zsv:
                    cxvyc__eegqa.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    ptilz__gmw = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    cxvyc__eegqa.null_bitmap = bodo.utils.utils._empty_nd_impl(
                        c.context, c.builder, types.Array(types.uint8, 1,
                        'C'), [ptilz__gmw])._getvalue()
                    aypod__jfrjk = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, cxvyc__eegqa.data
                        ).data
                    xpxo__bgm = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, cxvyc__eegqa.
                        null_bitmap).data
                    jijn__bokow = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    lncxh__gxk = cgutils.get_or_insert_function(c.builder.
                        module, jijn__bokow, name='unbox_bool_array_obj')
                    c.builder.call(lncxh__gxk, [obj, aypod__jfrjk,
                        xpxo__bgm, n])
    return NativeValue(cxvyc__eegqa._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    cxvyc__eegqa = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        cxvyc__eegqa.data, c.env_manager)
    tec__tld = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, cxvyc__eegqa.null_bitmap).data
    sgtms__hniwu = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(sgtms__hniwu)
    fbl__glhax = c.context.insert_const_string(c.builder.module, 'numpy')
    qswmr__wwtn = c.pyapi.import_module_noblock(fbl__glhax)
    gejcu__ekhjj = c.pyapi.object_getattr_string(qswmr__wwtn, 'bool_')
    qlby__xvvxs = c.pyapi.call_method(qswmr__wwtn, 'empty', (sgtms__hniwu,
        gejcu__ekhjj))
    vnim__jqn = c.pyapi.object_getattr_string(qlby__xvvxs, 'ctypes')
    umv__ivj = c.pyapi.object_getattr_string(vnim__jqn, 'data')
    gpor__irnhz = c.builder.inttoptr(c.pyapi.long_as_longlong(umv__ivj),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as htc__wgom:
        imzuo__siyf = htc__wgom.index
        mpz__zunxt = c.builder.lshr(imzuo__siyf, lir.Constant(lir.IntType(
            64), 3))
        arhop__azb = c.builder.load(cgutils.gep(c.builder, tec__tld,
            mpz__zunxt))
        atnl__lix = c.builder.trunc(c.builder.and_(imzuo__siyf, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(arhop__azb, atnl__lix), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        regq__qgqj = cgutils.gep(c.builder, gpor__irnhz, imzuo__siyf)
        c.builder.store(val, regq__qgqj)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        cxvyc__eegqa.null_bitmap)
    fbl__glhax = c.context.insert_const_string(c.builder.module, 'pandas')
    vcj__kmsx = c.pyapi.import_module_noblock(fbl__glhax)
    ump__mjawm = c.pyapi.object_getattr_string(vcj__kmsx, 'arrays')
    xaxe__fngds = c.pyapi.call_method(ump__mjawm, 'BooleanArray', (data,
        qlby__xvvxs))
    c.pyapi.decref(vcj__kmsx)
    c.pyapi.decref(sgtms__hniwu)
    c.pyapi.decref(qswmr__wwtn)
    c.pyapi.decref(gejcu__ekhjj)
    c.pyapi.decref(vnim__jqn)
    c.pyapi.decref(umv__ivj)
    c.pyapi.decref(ump__mjawm)
    c.pyapi.decref(data)
    c.pyapi.decref(qlby__xvvxs)
    return xaxe__fngds


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    pqh__ual = np.empty(n, np.bool_)
    wob__cxx = np.empty(n + 7 >> 3, np.uint8)
    for imzuo__siyf, s in enumerate(pyval):
        tmo__gqgc = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(wob__cxx, imzuo__siyf, int(not
            tmo__gqgc))
        if not tmo__gqgc:
            pqh__ual[imzuo__siyf] = s
    egmm__rdxnn = context.get_constant_generic(builder, data_type, pqh__ual)
    whwz__kpcsh = context.get_constant_generic(builder, nulls_type, wob__cxx)
    return lir.Constant.literal_struct([egmm__rdxnn, whwz__kpcsh])


def lower_init_bool_array(context, builder, signature, args):
    mrmgz__mshyp, hoajq__bxgu = args
    cxvyc__eegqa = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    cxvyc__eegqa.data = mrmgz__mshyp
    cxvyc__eegqa.null_bitmap = hoajq__bxgu
    context.nrt.incref(builder, signature.args[0], mrmgz__mshyp)
    context.nrt.incref(builder, signature.args[1], hoajq__bxgu)
    return cxvyc__eegqa._getvalue()


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
    vodpj__xfnv = args[0]
    if equiv_set.has_shape(vodpj__xfnv):
        return ArrayAnalysis.AnalyzeResult(shape=vodpj__xfnv, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vodpj__xfnv = args[0]
    if equiv_set.has_shape(vodpj__xfnv):
        return ArrayAnalysis.AnalyzeResult(shape=vodpj__xfnv, pre=[])
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
    pqh__ual = np.empty(n, dtype=np.bool_)
    wdzqa__fasky = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(pqh__ual, wdzqa__fasky)


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
            emn__wlp, kjgh__cdb = array_getitem_bool_index(A, ind)
            return init_bool_array(emn__wlp, kjgh__cdb)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            emn__wlp, kjgh__cdb = array_getitem_int_index(A, ind)
            return init_bool_array(emn__wlp, kjgh__cdb)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            emn__wlp, kjgh__cdb = array_getitem_slice_index(A, ind)
            return init_bool_array(emn__wlp, kjgh__cdb)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    orn__koqs = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(orn__koqs)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(orn__koqs)
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
        for imzuo__siyf in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, imzuo__siyf):
                val = A[imzuo__siyf]
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
            abhp__zctw = np.empty(n, nb_dtype)
            for imzuo__siyf in numba.parfors.parfor.internal_prange(n):
                abhp__zctw[imzuo__siyf] = data[imzuo__siyf]
                if bodo.libs.array_kernels.isna(A, imzuo__siyf):
                    abhp__zctw[imzuo__siyf] = np.nan
            return abhp__zctw
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        abhp__zctw = np.empty(n, dtype=np.bool_)
        for imzuo__siyf in numba.parfors.parfor.internal_prange(n):
            abhp__zctw[imzuo__siyf] = data[imzuo__siyf]
            if bodo.libs.array_kernels.isna(A, imzuo__siyf):
                abhp__zctw[imzuo__siyf] = value
        return abhp__zctw
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
    uevi__honl = op.__name__
    uevi__honl = ufunc_aliases.get(uevi__honl, uevi__honl)
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
    for ijx__tobi in numba.np.ufunc_db.get_ufuncs():
        etj__slj = create_op_overload(ijx__tobi, ijx__tobi.nin)
        overload(ijx__tobi, no_unliteral=True)(etj__slj)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        etj__slj = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(etj__slj)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        etj__slj = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(etj__slj)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        etj__slj = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(etj__slj)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        atnl__lix = []
        qbn__ckkkk = False
        vssnd__znadi = False
        vlon__xycmk = False
        for imzuo__siyf in range(len(A)):
            if bodo.libs.array_kernels.isna(A, imzuo__siyf):
                if not qbn__ckkkk:
                    data.append(False)
                    atnl__lix.append(False)
                    qbn__ckkkk = True
                continue
            val = A[imzuo__siyf]
            if val and not vssnd__znadi:
                data.append(True)
                atnl__lix.append(True)
                vssnd__znadi = True
            if not val and not vlon__xycmk:
                data.append(False)
                atnl__lix.append(True)
                vlon__xycmk = True
            if qbn__ckkkk and vssnd__znadi and vlon__xycmk:
                break
        emn__wlp = np.array(data)
        n = len(emn__wlp)
        ptilz__gmw = 1
        kjgh__cdb = np.empty(ptilz__gmw, np.uint8)
        for wcvsl__troql in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(kjgh__cdb, wcvsl__troql,
                atnl__lix[wcvsl__troql])
        return init_bool_array(emn__wlp, kjgh__cdb)
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
    xaxe__fngds = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, xaxe__fngds)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    dpnrp__seeq = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        sho__shkn = bodo.utils.utils.is_array_typ(val1, False)
        cjdvf__kvluv = bodo.utils.utils.is_array_typ(val2, False)
        nhyl__gop = 'val1' if sho__shkn else 'val2'
        dkk__rqcrf = 'def impl(val1, val2):\n'
        dkk__rqcrf += f'  n = len({nhyl__gop})\n'
        dkk__rqcrf += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        dkk__rqcrf += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if sho__shkn:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            vuiin__anpa = 'val1[i]'
        else:
            null1 = 'False\n'
            vuiin__anpa = 'val1'
        if cjdvf__kvluv:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            wyfup__tigx = 'val2[i]'
        else:
            null2 = 'False\n'
            wyfup__tigx = 'val2'
        if dpnrp__seeq:
            dkk__rqcrf += f"""    result, isna_val = compute_or_body({null1}, {null2}, {vuiin__anpa}, {wyfup__tigx})
"""
        else:
            dkk__rqcrf += f"""    result, isna_val = compute_and_body({null1}, {null2}, {vuiin__anpa}, {wyfup__tigx})
"""
        dkk__rqcrf += '    out_arr[i] = result\n'
        dkk__rqcrf += '    if isna_val:\n'
        dkk__rqcrf += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        dkk__rqcrf += '      continue\n'
        dkk__rqcrf += '  return out_arr\n'
        ybrkq__abdgg = {}
        exec(dkk__rqcrf, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, ybrkq__abdgg
            )
        impl = ybrkq__abdgg['impl']
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
        omk__thr = boolean_array
        return omk__thr(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    gelu__wqxu = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return gelu__wqxu


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        jfajj__mwdpf = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(jfajj__mwdpf)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(jfajj__mwdpf)


_install_nullable_logical_lowering()
