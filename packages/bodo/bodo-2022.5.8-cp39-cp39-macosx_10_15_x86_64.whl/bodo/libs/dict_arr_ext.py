"""Dictionary encoded array data type, similar to DictionaryArray of Arrow.
The purpose is to improve memory consumption and performance over string_array_type for
string arrays that have a lot of repetitive values (typical in practice).
Can be extended to be used with types other than strings as well.
See:
https://bodo.atlassian.net/browse/BE-2295
https://bodo.atlassian.net/wiki/spaces/B/pages/993722369/Dictionary-encoded+String+Array+Support+in+Parquet+read+compute+...
https://arrow.apache.org/docs/cpp/api/array.html#dictionary-encoded
"""
import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_builtin, lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo
from bodo.libs import hstr_ext
from bodo.libs.bool_arr_ext import init_bool_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, get_str_arr_item_length, overload_str_arr_astype, pre_alloc_string_array
from bodo.utils.typing import BodoArrayIterator, is_overload_none, raise_bodo_error
ll.add_symbol('box_dict_str_array', hstr_ext.box_dict_str_array)
dict_indices_arr_type = IntegerArrayType(types.int32)


class DictionaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self, arr_data_type):
        self.data = arr_data_type
        super(DictionaryArrayType, self).__init__(name=
            f'DictionaryArrayType({arr_data_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    @property
    def dtype(self):
        return self.data.dtype

    def copy(self):
        return DictionaryArrayType(self.data)

    @property
    def indices_type(self):
        return dict_indices_arr_type

    @property
    def indices_dtype(self):
        return dict_indices_arr_type.dtype

    def unify(self, typingctx, other):
        if other == bodo.string_array_type:
            return bodo.string_array_type


dict_str_arr_type = DictionaryArrayType(bodo.string_array_type)


@register_model(DictionaryArrayType)
class DictionaryArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rnvt__yzs = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, rnvt__yzs)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        mdqb__trr, epmq__dgd, pndkm__eqp = args
        obq__inn = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        obq__inn.data = mdqb__trr
        obq__inn.indices = epmq__dgd
        obq__inn.has_global_dictionary = pndkm__eqp
        context.nrt.incref(builder, signature.args[0], mdqb__trr)
        context.nrt.incref(builder, signature.args[1], epmq__dgd)
        return obq__inn._getvalue()
    hho__qfxut = DictionaryArrayType(data_t)
    swew__qske = hho__qfxut(data_t, indices_t, types.bool_)
    return swew__qske, codegen


@typeof_impl.register(pa.DictionaryArray)
def typeof_dict_value(val, c):
    if val.type.value_type == pa.string():
        return dict_str_arr_type


def to_pa_dict_arr(A):
    if isinstance(A, pa.DictionaryArray):
        return A
    for i in range(len(A)):
        if pd.isna(A[i]):
            A[i] = None
    return pa.array(A).dictionary_encode()


@unbox(DictionaryArrayType)
def unbox_dict_arr(typ, val, c):
    if bodo.hiframes.boxing._use_dict_str_type:
        moajs__tmbve = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(moajs__tmbve, [val])
        c.pyapi.decref(moajs__tmbve)
    obq__inn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    irac__tqot = c.pyapi.object_getattr_string(val, 'dictionary')
    uttb__vazlb = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    hkt__ciqw = c.pyapi.call_method(irac__tqot, 'to_numpy', (uttb__vazlb,))
    obq__inn.data = c.unbox(typ.data, hkt__ciqw).value
    yjb__ulhoj = c.pyapi.object_getattr_string(val, 'indices')
    evctk__dissn = c.context.insert_const_string(c.builder.module, 'pandas')
    gbwdi__wgb = c.pyapi.import_module_noblock(evctk__dissn)
    iyps__xpsro = c.pyapi.string_from_constant_string('Int32')
    tmexn__uyel = c.pyapi.call_method(gbwdi__wgb, 'array', (yjb__ulhoj,
        iyps__xpsro))
    obq__inn.indices = c.unbox(dict_indices_arr_type, tmexn__uyel).value
    obq__inn.has_global_dictionary = c.context.get_constant(types.bool_, False)
    c.pyapi.decref(irac__tqot)
    c.pyapi.decref(uttb__vazlb)
    c.pyapi.decref(hkt__ciqw)
    c.pyapi.decref(yjb__ulhoj)
    c.pyapi.decref(gbwdi__wgb)
    c.pyapi.decref(iyps__xpsro)
    c.pyapi.decref(tmexn__uyel)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    oglau__jkvc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(obq__inn._getvalue(), is_error=oglau__jkvc)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    obq__inn = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, obq__inn.data)
        zvs__gjvvw = c.box(typ.data, obq__inn.data)
        kypi__krrg = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, obq__inn.indices)
        vhwyq__ccy = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        hquz__kjoz = cgutils.get_or_insert_function(c.builder.module,
            vhwyq__ccy, name='box_dict_str_array')
        rgo__hdoqt = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, kypi__krrg.data)
        tvzz__awja = c.builder.extract_value(rgo__hdoqt.shape, 0)
        iev__vxaw = rgo__hdoqt.data
        blgym__bas = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, kypi__krrg.null_bitmap).data
        hkt__ciqw = c.builder.call(hquz__kjoz, [tvzz__awja, zvs__gjvvw,
            iev__vxaw, blgym__bas])
        c.pyapi.decref(zvs__gjvvw)
    else:
        evctk__dissn = c.context.insert_const_string(c.builder.module,
            'pyarrow')
        kfhzr__uvvvj = c.pyapi.import_module_noblock(evctk__dissn)
        vtl__qheuv = c.pyapi.object_getattr_string(kfhzr__uvvvj,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, obq__inn.data)
        zvs__gjvvw = c.box(typ.data, obq__inn.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, obq__inn.indices
            )
        yjb__ulhoj = c.box(dict_indices_arr_type, obq__inn.indices)
        fez__lhq = c.pyapi.call_method(vtl__qheuv, 'from_arrays', (
            yjb__ulhoj, zvs__gjvvw))
        uttb__vazlb = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        hkt__ciqw = c.pyapi.call_method(fez__lhq, 'to_numpy', (uttb__vazlb,))
        c.pyapi.decref(kfhzr__uvvvj)
        c.pyapi.decref(zvs__gjvvw)
        c.pyapi.decref(yjb__ulhoj)
        c.pyapi.decref(vtl__qheuv)
        c.pyapi.decref(fez__lhq)
        c.pyapi.decref(uttb__vazlb)
    c.context.nrt.decref(c.builder, typ, val)
    return hkt__ciqw


@overload(len, no_unliteral=True)
def overload_dict_arr_len(A):
    if isinstance(A, DictionaryArrayType):
        return lambda A: len(A._indices)


@overload_attribute(DictionaryArrayType, 'shape')
def overload_dict_arr_shape(A):
    return lambda A: (len(A._indices),)


@overload_attribute(DictionaryArrayType, 'ndim')
def overload_dict_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DictionaryArrayType, 'size')
def overload_dict_arr_size(A):
    return lambda A: len(A._indices)


@overload_method(DictionaryArrayType, 'tolist', no_unliteral=True)
def overload_dict_arr_tolist(A):
    return lambda A: list(A)


overload_method(DictionaryArrayType, 'astype', no_unliteral=True)(
    overload_str_arr_astype)


@overload_method(DictionaryArrayType, 'copy', no_unliteral=True)
def overload_dict_arr_copy(A):

    def copy_impl(A):
        return init_dict_arr(A._data.copy(), A._indices.copy(), A.
            _has_global_dictionary)
    return copy_impl


@overload_attribute(DictionaryArrayType, 'dtype')
def overload_dict_arr_dtype(A):
    return lambda A: A._data.dtype


@overload_attribute(DictionaryArrayType, 'nbytes')
def dict_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._indices.nbytes


@lower_constant(DictionaryArrayType)
def lower_constant_dict_arr(context, builder, typ, pyval):
    if bodo.hiframes.boxing._use_dict_str_type and isinstance(pyval, np.ndarray
        ):
        pyval = pa.array(pyval).dictionary_encode()
    rdgm__vatms = pyval.dictionary.to_numpy(False)
    pfa__zzpd = pd.array(pyval.indices, 'Int32')
    rdgm__vatms = context.get_constant_generic(builder, typ.data, rdgm__vatms)
    pfa__zzpd = context.get_constant_generic(builder, dict_indices_arr_type,
        pfa__zzpd)
    iezgr__dssw = context.get_constant(types.bool_, False)
    zwgk__jgzy = lir.Constant.literal_struct([rdgm__vatms, pfa__zzpd,
        iezgr__dssw])
    return zwgk__jgzy


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            jvb__eok = A._indices[ind]
            return A._data[jvb__eok]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        mdqb__trr = A._data
        epmq__dgd = A._indices
        tvzz__awja = len(epmq__dgd)
        mrvo__tmo = [get_str_arr_item_length(mdqb__trr, i) for i in range(
            len(mdqb__trr))]
        xfyy__ypbj = 0
        for i in range(tvzz__awja):
            if not bodo.libs.array_kernels.isna(epmq__dgd, i):
                xfyy__ypbj += mrvo__tmo[epmq__dgd[i]]
        guwi__puoh = pre_alloc_string_array(tvzz__awja, xfyy__ypbj)
        for i in range(tvzz__awja):
            if bodo.libs.array_kernels.isna(epmq__dgd, i):
                bodo.libs.array_kernels.setna(guwi__puoh, i)
                continue
            ind = epmq__dgd[i]
            if bodo.libs.array_kernels.isna(mdqb__trr, ind):
                bodo.libs.array_kernels.setna(guwi__puoh, i)
                continue
            guwi__puoh[i] = mdqb__trr[ind]
        return guwi__puoh
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    jvb__eok = -1
    mdqb__trr = arr._data
    for i in range(len(mdqb__trr)):
        if bodo.libs.array_kernels.isna(mdqb__trr, i):
            continue
        if mdqb__trr[i] == val:
            jvb__eok = i
            break
    return jvb__eok


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    tvzz__awja = len(arr)
    jvb__eok = find_dict_ind(arr, val)
    if jvb__eok == -1:
        return init_bool_array(np.full(tvzz__awja, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == jvb__eok


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    tvzz__awja = len(arr)
    jvb__eok = find_dict_ind(arr, val)
    if jvb__eok == -1:
        return init_bool_array(np.full(tvzz__awja, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != jvb__eok


def get_binary_op_overload(op, lhs, rhs):
    if op == operator.eq:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(rhs, lhs)
    if op == operator.ne:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(rhs, lhs)


def convert_dict_arr_to_int(arr, dtype):
    return arr


@overload(convert_dict_arr_to_int)
def convert_dict_arr_to_int_overload(arr, dtype):

    def impl(arr, dtype):
        eso__oqju = arr._data
        jcn__dljgp = bodo.libs.int_arr_ext.alloc_int_array(len(eso__oqju),
            dtype)
        for zmm__gwgxt in range(len(eso__oqju)):
            if bodo.libs.array_kernels.isna(eso__oqju, zmm__gwgxt):
                bodo.libs.array_kernels.setna(jcn__dljgp, zmm__gwgxt)
                continue
            jcn__dljgp[zmm__gwgxt] = np.int64(eso__oqju[zmm__gwgxt])
        tvzz__awja = len(arr)
        epmq__dgd = arr._indices
        guwi__puoh = bodo.libs.int_arr_ext.alloc_int_array(tvzz__awja, dtype)
        for i in range(tvzz__awja):
            if bodo.libs.array_kernels.isna(epmq__dgd, i):
                bodo.libs.array_kernels.setna(guwi__puoh, i)
                continue
            guwi__puoh[i] = jcn__dljgp[epmq__dgd[i]]
        return guwi__puoh
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    lcsqj__puy = len(arrs)
    tge__sptl = 'def impl(arrs, sep):\n'
    tge__sptl += '  ind_map = {}\n'
    tge__sptl += '  out_strs = []\n'
    tge__sptl += '  n = len(arrs[0])\n'
    for i in range(lcsqj__puy):
        tge__sptl += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(lcsqj__puy):
        tge__sptl += f'  data{i} = arrs[{i}]._data\n'
    tge__sptl += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    tge__sptl += '  for i in range(n):\n'
    vfp__vfj = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(lcsqj__puy)])
    tge__sptl += f'    if {vfp__vfj}:\n'
    tge__sptl += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    tge__sptl += '      continue\n'
    for i in range(lcsqj__puy):
        tge__sptl += f'    ind{i} = indices{i}[i]\n'
    gmol__qmq = '(' + ', '.join(f'ind{i}' for i in range(lcsqj__puy)) + ')'
    tge__sptl += f'    if {gmol__qmq} not in ind_map:\n'
    tge__sptl += '      out_ind = len(out_strs)\n'
    tge__sptl += f'      ind_map[{gmol__qmq}] = out_ind\n'
    hgio__sadqf = "''" if is_overload_none(sep) else 'sep'
    yexd__dds = ', '.join([f'data{i}[ind{i}]' for i in range(lcsqj__puy)])
    tge__sptl += f'      v = {hgio__sadqf}.join([{yexd__dds}])\n'
    tge__sptl += '      out_strs.append(v)\n'
    tge__sptl += '    else:\n'
    tge__sptl += f'      out_ind = ind_map[{gmol__qmq}]\n'
    tge__sptl += '    out_indices[i] = out_ind\n'
    tge__sptl += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    tge__sptl += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    trcrn__ghk = {}
    exec(tge__sptl, {'bodo': bodo, 'numba': numba, 'np': np}, trcrn__ghk)
    impl = trcrn__ghk['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    xwsn__jjf = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    swew__qske = toty(fromty)
    trv__lecs = context.compile_internal(builder, xwsn__jjf, swew__qske, (val,)
        )
    return impl_ret_new_ref(context, builder, toty, trv__lecs)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    rdgm__vatms = arr._data
    ycylh__nhxwd = len(rdgm__vatms)
    zzock__fjt = pre_alloc_string_array(ycylh__nhxwd, -1)
    if regex:
        cngwm__tthqf = re.compile(pat, flags)
        for i in range(ycylh__nhxwd):
            if bodo.libs.array_kernels.isna(rdgm__vatms, i):
                bodo.libs.array_kernels.setna(zzock__fjt, i)
                continue
            zzock__fjt[i] = cngwm__tthqf.sub(repl=repl, string=rdgm__vatms[i])
    else:
        for i in range(ycylh__nhxwd):
            if bodo.libs.array_kernels.isna(rdgm__vatms, i):
                bodo.libs.array_kernels.setna(zzock__fjt, i)
                continue
            zzock__fjt[i] = rdgm__vatms[i].replace(pat, repl)
    return init_dict_arr(zzock__fjt, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    obq__inn = arr._data
    utwl__rni = len(obq__inn)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(utwl__rni)
    for i in range(utwl__rni):
        dict_arr_out[i] = obq__inn[i].startswith(pat)
    pfa__zzpd = arr._indices
    wast__wzztk = len(pfa__zzpd)
    guwi__puoh = bodo.libs.bool_arr_ext.alloc_bool_array(wast__wzztk)
    for i in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(guwi__puoh, i)
        else:
            guwi__puoh[i] = dict_arr_out[pfa__zzpd[i]]
    return guwi__puoh


@register_jitable
def str_endswith(arr, pat, na):
    obq__inn = arr._data
    utwl__rni = len(obq__inn)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(utwl__rni)
    for i in range(utwl__rni):
        dict_arr_out[i] = obq__inn[i].endswith(pat)
    pfa__zzpd = arr._indices
    wast__wzztk = len(pfa__zzpd)
    guwi__puoh = bodo.libs.bool_arr_ext.alloc_bool_array(wast__wzztk)
    for i in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(guwi__puoh, i)
        else:
            guwi__puoh[i] = dict_arr_out[pfa__zzpd[i]]
    return guwi__puoh


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    obq__inn = arr._data
    sjjwe__tgxw = pd.Series(obq__inn)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = sjjwe__tgxw.array._str_contains(pat, case, flags, na,
            regex)
    pfa__zzpd = arr._indices
    wast__wzztk = len(pfa__zzpd)
    guwi__puoh = bodo.libs.bool_arr_ext.alloc_bool_array(wast__wzztk)
    for i in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(guwi__puoh, i)
        else:
            guwi__puoh[i] = dict_arr_out[pfa__zzpd[i]]
    return guwi__puoh


@register_jitable
def str_contains_non_regex(arr, pat, case):
    obq__inn = arr._data
    utwl__rni = len(obq__inn)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(utwl__rni)
    if not case:
        gay__bfaxg = pat.upper()
    for i in range(utwl__rni):
        if case:
            dict_arr_out[i] = pat in obq__inn[i]
        else:
            dict_arr_out[i] = gay__bfaxg in obq__inn[i].upper()
    pfa__zzpd = arr._indices
    wast__wzztk = len(pfa__zzpd)
    guwi__puoh = bodo.libs.bool_arr_ext.alloc_bool_array(wast__wzztk)
    for i in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(guwi__puoh, i)
        else:
            guwi__puoh[i] = dict_arr_out[pfa__zzpd[i]]
    return guwi__puoh


def create_simple_str2str_methods(func_name, func_args):
    tge__sptl = f"""def str_{func_name}({', '.join(func_args)}):
    data_arr = arr._data
    n_data = len(data_arr)
    out_str_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_data, -1)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_str_arr, i)
            continue
        out_str_arr[i] = data_arr[i].{func_name}({', '.join(func_args[1:])})
    return init_dict_arr(out_str_arr, arr._indices.copy(), arr._has_global_dictionary)
"""
    trcrn__ghk = {}
    exec(tge__sptl, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, trcrn__ghk)
    return trcrn__ghk[f'str_{func_name}']


def _register_simple_str2str_methods():
    rlkg__zdf = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in rlkg__zdf.keys():
        voip__rmqj = create_simple_str2str_methods(func_name, rlkg__zdf[
            func_name])
        voip__rmqj = register_jitable(voip__rmqj)
        globals()[f'str_{func_name}'] = voip__rmqj


_register_simple_str2str_methods()


def create_find_methods(func_name):
    tge__sptl = f"""def str_{func_name}(arr, sub, start, end):
  data_arr = arr._data
  indices_arr = arr._indices
  n_data = len(data_arr)
  n_indices = len(indices_arr)
  tmp_dict_arr = bodo.libs.int_arr_ext.alloc_int_array(n_data, np.int64)
  out_int_arr = bodo.libs.int_arr_ext.alloc_int_array(n_indices, np.int64)
  for i in range(n_data):
    if bodo.libs.array_kernels.isna(data_arr, i):
      bodo.libs.array_kernels.setna(tmp_dict_arr, i)
      continue
    tmp_dict_arr[i] = data_arr[i].{func_name}(sub, start, end)
  for i in range(n_indices):
    if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
      tmp_dict_arr, indices_arr[i]
    ):
      bodo.libs.array_kernels.setna(out_int_arr, i)
    else:
      out_int_arr[i] = tmp_dict_arr[indices_arr[i]]
  return out_int_arr"""
    trcrn__ghk = {}
    exec(tge__sptl, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, trcrn__ghk)
    return trcrn__ghk[f'str_{func_name}']


def _register_find_methods():
    mho__pgci = ['find', 'rfind']
    for func_name in mho__pgci:
        voip__rmqj = create_find_methods(func_name)
        voip__rmqj = register_jitable(voip__rmqj)
        globals()[f'str_{func_name}'] = voip__rmqj


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    rdgm__vatms = arr._data
    pfa__zzpd = arr._indices
    ycylh__nhxwd = len(rdgm__vatms)
    wast__wzztk = len(pfa__zzpd)
    xtywa__kqrws = bodo.libs.int_arr_ext.alloc_int_array(ycylh__nhxwd, np.int64
        )
    dtvua__mcwzo = bodo.libs.int_arr_ext.alloc_int_array(wast__wzztk, np.int64)
    regex = re.compile(pat, flags)
    for i in range(ycylh__nhxwd):
        if bodo.libs.array_kernels.isna(rdgm__vatms, i):
            bodo.libs.array_kernels.setna(xtywa__kqrws, i)
            continue
        xtywa__kqrws[i] = bodo.libs.str_ext.str_findall_count(regex,
            rdgm__vatms[i])
    for i in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(pfa__zzpd, i
            ) or bodo.libs.array_kernels.isna(xtywa__kqrws, pfa__zzpd[i]):
            bodo.libs.array_kernels.setna(dtvua__mcwzo, i)
        else:
            dtvua__mcwzo[i] = xtywa__kqrws[pfa__zzpd[i]]
    return dtvua__mcwzo


@register_jitable
def str_len(arr):
    rdgm__vatms = arr._data
    pfa__zzpd = arr._indices
    wast__wzztk = len(pfa__zzpd)
    xtywa__kqrws = bodo.libs.array_kernels.get_arr_lens(rdgm__vatms, False)
    dtvua__mcwzo = bodo.libs.int_arr_ext.alloc_int_array(wast__wzztk, np.int64)
    for i in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(pfa__zzpd, i
            ) or bodo.libs.array_kernels.isna(xtywa__kqrws, pfa__zzpd[i]):
            bodo.libs.array_kernels.setna(dtvua__mcwzo, i)
        else:
            dtvua__mcwzo[i] = xtywa__kqrws[pfa__zzpd[i]]
    return dtvua__mcwzo


@register_jitable
def str_slice(arr, start, stop, step):
    rdgm__vatms = arr._data
    ycylh__nhxwd = len(rdgm__vatms)
    zzock__fjt = bodo.libs.str_arr_ext.pre_alloc_string_array(ycylh__nhxwd, -1)
    for i in range(ycylh__nhxwd):
        if bodo.libs.array_kernels.isna(rdgm__vatms, i):
            bodo.libs.array_kernels.setna(zzock__fjt, i)
            continue
        zzock__fjt[i] = rdgm__vatms[i][start:stop:step]
    return init_dict_arr(zzock__fjt, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    rdgm__vatms = arr._data
    pfa__zzpd = arr._indices
    ycylh__nhxwd = len(rdgm__vatms)
    wast__wzztk = len(pfa__zzpd)
    zzock__fjt = pre_alloc_string_array(ycylh__nhxwd, -1)
    guwi__puoh = pre_alloc_string_array(wast__wzztk, -1)
    for zmm__gwgxt in range(ycylh__nhxwd):
        if bodo.libs.array_kernels.isna(rdgm__vatms, zmm__gwgxt) or not -len(
            rdgm__vatms[zmm__gwgxt]) <= i < len(rdgm__vatms[zmm__gwgxt]):
            bodo.libs.array_kernels.setna(zzock__fjt, zmm__gwgxt)
            continue
        zzock__fjt[zmm__gwgxt] = rdgm__vatms[zmm__gwgxt][i]
    for zmm__gwgxt in range(wast__wzztk):
        if bodo.libs.array_kernels.isna(pfa__zzpd, zmm__gwgxt
            ) or bodo.libs.array_kernels.isna(zzock__fjt, pfa__zzpd[zmm__gwgxt]
            ):
            bodo.libs.array_kernels.setna(guwi__puoh, zmm__gwgxt)
            continue
        guwi__puoh[zmm__gwgxt] = zzock__fjt[pfa__zzpd[zmm__gwgxt]]
    return guwi__puoh


@register_jitable
def str_repeat_int(arr, repeats):
    rdgm__vatms = arr._data
    ycylh__nhxwd = len(rdgm__vatms)
    zzock__fjt = pre_alloc_string_array(ycylh__nhxwd, -1)
    for i in range(ycylh__nhxwd):
        if bodo.libs.array_kernels.isna(rdgm__vatms, i):
            bodo.libs.array_kernels.setna(zzock__fjt, i)
            continue
        zzock__fjt[i] = rdgm__vatms[i] * repeats
    return init_dict_arr(zzock__fjt, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    tge__sptl = f"""def str_{func_name}(arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    out_dict_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_data)
    out_bool_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_indices)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_dict_arr, i)
            continue
        out_dict_arr[i] = np.bool_(data_arr[i].{func_name}())
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
            data_arr, indices_arr[i]        ):
            bodo.libs.array_kernels.setna(out_bool_arr, i)
        else:
            out_bool_arr[i] = out_dict_arr[indices_arr[i]]
    return out_bool_arr"""
    trcrn__ghk = {}
    exec(tge__sptl, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, trcrn__ghk)
    return trcrn__ghk[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        voip__rmqj = create_str2bool_methods(func_name)
        voip__rmqj = register_jitable(voip__rmqj)
        globals()[f'str_{func_name}'] = voip__rmqj


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    rdgm__vatms = arr._data
    pfa__zzpd = arr._indices
    ycylh__nhxwd = len(rdgm__vatms)
    wast__wzztk = len(pfa__zzpd)
    regex = re.compile(pat, flags=flags)
    pceun__coyx = []
    for bem__szk in range(n_cols):
        pceun__coyx.append(pre_alloc_string_array(ycylh__nhxwd, -1))
    gur__ybkm = bodo.libs.bool_arr_ext.alloc_bool_array(ycylh__nhxwd)
    ycgg__cajs = pfa__zzpd.copy()
    for i in range(ycylh__nhxwd):
        if bodo.libs.array_kernels.isna(rdgm__vatms, i):
            gur__ybkm[i] = True
            for zmm__gwgxt in range(n_cols):
                bodo.libs.array_kernels.setna(pceun__coyx[zmm__gwgxt], i)
            continue
        znqco__ehn = regex.search(rdgm__vatms[i])
        if znqco__ehn:
            gur__ybkm[i] = False
            jompj__xyugi = znqco__ehn.groups()
            for zmm__gwgxt in range(n_cols):
                pceun__coyx[zmm__gwgxt][i] = jompj__xyugi[zmm__gwgxt]
        else:
            gur__ybkm[i] = True
            for zmm__gwgxt in range(n_cols):
                bodo.libs.array_kernels.setna(pceun__coyx[zmm__gwgxt], i)
    for i in range(wast__wzztk):
        if gur__ybkm[ycgg__cajs[i]]:
            bodo.libs.array_kernels.setna(ycgg__cajs, i)
    osxbf__dszny = [init_dict_arr(pceun__coyx[i], ycgg__cajs.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return osxbf__dszny


def create_extractall_methods(is_multi_group):
    qdut__kahei = '_multi' if is_multi_group else ''
    tge__sptl = f"""def str_extractall{qdut__kahei}(arr, regex, n_cols, index_arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    indices_count = [0 for _ in range(n_data)]
    for i in range(n_indices):
        if not bodo.libs.array_kernels.isna(indices_arr, i):
            indices_count[indices_arr[i]] += 1
    dict_group_count = []
    out_dict_len = out_ind_len = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        dict_group_count.append((out_dict_len, len(m)))
        out_dict_len += len(m)
        out_ind_len += indices_count[i] * len(m)
    out_dict_arr_list = []
    for _ in range(n_cols):
        out_dict_arr_list.append(pre_alloc_string_array(out_dict_len, -1))
    out_indices_arr = bodo.libs.int_arr_ext.alloc_int_array(out_ind_len, np.int32)
    out_ind_arr = bodo.utils.utils.alloc_type(out_ind_len, index_arr, (-1,))
    out_match_arr = np.empty(out_ind_len, np.int64)
    curr_ind = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        for s in m:
            for j in range(n_cols):
                out_dict_arr_list[j][curr_ind] = s{'[j]' if is_multi_group else ''}
            curr_ind += 1
    curr_ind = 0
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i):
            continue
        n_rows = dict_group_count[indices_arr[i]][1]
        for k in range(n_rows):
            out_indices_arr[curr_ind] = dict_group_count[indices_arr[i]][0] + k
            out_ind_arr[curr_ind] = index_arr[i]
            out_match_arr[curr_ind] = k
            curr_ind += 1
    out_arr_list = [
        init_dict_arr(
            out_dict_arr_list[i], out_indices_arr.copy(), arr._has_global_dictionary
        )
        for i in range(n_cols)
    ]
    return (out_ind_arr, out_match_arr, out_arr_list) 
"""
    trcrn__ghk = {}
    exec(tge__sptl, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, trcrn__ghk)
    return trcrn__ghk[f'str_extractall{qdut__kahei}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        qdut__kahei = '_multi' if is_multi_group else ''
        voip__rmqj = create_extractall_methods(is_multi_group)
        voip__rmqj = register_jitable(voip__rmqj)
        globals()[f'str_extractall{qdut__kahei}'] = voip__rmqj


_register_extractall_methods()
