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
        cdoag__prvw = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, cdoag__prvw)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        rso__viv, wrrq__ltcft, yrvbe__mmf = args
        opfn__tvn = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        opfn__tvn.data = rso__viv
        opfn__tvn.indices = wrrq__ltcft
        opfn__tvn.has_global_dictionary = yrvbe__mmf
        context.nrt.incref(builder, signature.args[0], rso__viv)
        context.nrt.incref(builder, signature.args[1], wrrq__ltcft)
        return opfn__tvn._getvalue()
    xotrv__dghf = DictionaryArrayType(data_t)
    myx__umivu = xotrv__dghf(data_t, indices_t, types.bool_)
    return myx__umivu, codegen


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
        znki__vyw = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(znki__vyw, [val])
        c.pyapi.decref(znki__vyw)
    opfn__tvn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jrkgm__udjvt = c.pyapi.object_getattr_string(val, 'dictionary')
    kyobo__xgwy = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    xvs__rbel = c.pyapi.call_method(jrkgm__udjvt, 'to_numpy', (kyobo__xgwy,))
    opfn__tvn.data = c.unbox(typ.data, xvs__rbel).value
    wdk__ueng = c.pyapi.object_getattr_string(val, 'indices')
    xzwyb__vjuyt = c.context.insert_const_string(c.builder.module, 'pandas')
    uepe__qjips = c.pyapi.import_module_noblock(xzwyb__vjuyt)
    afc__pew = c.pyapi.string_from_constant_string('Int32')
    hmot__yyhcy = c.pyapi.call_method(uepe__qjips, 'array', (wdk__ueng,
        afc__pew))
    opfn__tvn.indices = c.unbox(dict_indices_arr_type, hmot__yyhcy).value
    opfn__tvn.has_global_dictionary = c.context.get_constant(types.bool_, False
        )
    c.pyapi.decref(jrkgm__udjvt)
    c.pyapi.decref(kyobo__xgwy)
    c.pyapi.decref(xvs__rbel)
    c.pyapi.decref(wdk__ueng)
    c.pyapi.decref(uepe__qjips)
    c.pyapi.decref(afc__pew)
    c.pyapi.decref(hmot__yyhcy)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    ixljf__mwom = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(opfn__tvn._getvalue(), is_error=ixljf__mwom)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    opfn__tvn = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, opfn__tvn.data)
        qhpx__unfw = c.box(typ.data, opfn__tvn.data)
        fyqi__ucx = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, opfn__tvn.indices)
        ojtg__nvgs = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        nwh__ftxfo = cgutils.get_or_insert_function(c.builder.module,
            ojtg__nvgs, name='box_dict_str_array')
        yuu__uwzn = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, fyqi__ucx.data)
        clhm__qyi = c.builder.extract_value(yuu__uwzn.shape, 0)
        whfmn__qwb = yuu__uwzn.data
        ehvs__ldj = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, fyqi__ucx.null_bitmap).data
        xvs__rbel = c.builder.call(nwh__ftxfo, [clhm__qyi, qhpx__unfw,
            whfmn__qwb, ehvs__ldj])
        c.pyapi.decref(qhpx__unfw)
    else:
        xzwyb__vjuyt = c.context.insert_const_string(c.builder.module,
            'pyarrow')
        rvqix__ymobg = c.pyapi.import_module_noblock(xzwyb__vjuyt)
        dzilx__jxibi = c.pyapi.object_getattr_string(rvqix__ymobg,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, opfn__tvn.data)
        qhpx__unfw = c.box(typ.data, opfn__tvn.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, opfn__tvn.
            indices)
        wdk__ueng = c.box(dict_indices_arr_type, opfn__tvn.indices)
        kmpd__xxnq = c.pyapi.call_method(dzilx__jxibi, 'from_arrays', (
            wdk__ueng, qhpx__unfw))
        kyobo__xgwy = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        xvs__rbel = c.pyapi.call_method(kmpd__xxnq, 'to_numpy', (kyobo__xgwy,))
        c.pyapi.decref(rvqix__ymobg)
        c.pyapi.decref(qhpx__unfw)
        c.pyapi.decref(wdk__ueng)
        c.pyapi.decref(dzilx__jxibi)
        c.pyapi.decref(kmpd__xxnq)
        c.pyapi.decref(kyobo__xgwy)
    c.context.nrt.decref(c.builder, typ, val)
    return xvs__rbel


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
    gwwpu__tpg = pyval.dictionary.to_numpy(False)
    rscwr__ikdx = pd.array(pyval.indices, 'Int32')
    gwwpu__tpg = context.get_constant_generic(builder, typ.data, gwwpu__tpg)
    rscwr__ikdx = context.get_constant_generic(builder,
        dict_indices_arr_type, rscwr__ikdx)
    mzvle__nnpga = context.get_constant(types.bool_, False)
    tpth__xtyeu = lir.Constant.literal_struct([gwwpu__tpg, rscwr__ikdx,
        mzvle__nnpga])
    return tpth__xtyeu


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            ddcau__hpq = A._indices[ind]
            return A._data[ddcau__hpq]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        rso__viv = A._data
        wrrq__ltcft = A._indices
        clhm__qyi = len(wrrq__ltcft)
        ylll__qeuaz = [get_str_arr_item_length(rso__viv, i) for i in range(
            len(rso__viv))]
        tiyp__zsor = 0
        for i in range(clhm__qyi):
            if not bodo.libs.array_kernels.isna(wrrq__ltcft, i):
                tiyp__zsor += ylll__qeuaz[wrrq__ltcft[i]]
        usayo__qoilo = pre_alloc_string_array(clhm__qyi, tiyp__zsor)
        for i in range(clhm__qyi):
            if bodo.libs.array_kernels.isna(wrrq__ltcft, i):
                bodo.libs.array_kernels.setna(usayo__qoilo, i)
                continue
            ind = wrrq__ltcft[i]
            if bodo.libs.array_kernels.isna(rso__viv, ind):
                bodo.libs.array_kernels.setna(usayo__qoilo, i)
                continue
            usayo__qoilo[i] = rso__viv[ind]
        return usayo__qoilo
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    ddcau__hpq = -1
    rso__viv = arr._data
    for i in range(len(rso__viv)):
        if bodo.libs.array_kernels.isna(rso__viv, i):
            continue
        if rso__viv[i] == val:
            ddcau__hpq = i
            break
    return ddcau__hpq


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    clhm__qyi = len(arr)
    ddcau__hpq = find_dict_ind(arr, val)
    if ddcau__hpq == -1:
        return init_bool_array(np.full(clhm__qyi, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == ddcau__hpq


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    clhm__qyi = len(arr)
    ddcau__hpq = find_dict_ind(arr, val)
    if ddcau__hpq == -1:
        return init_bool_array(np.full(clhm__qyi, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != ddcau__hpq


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
        utcqr__hlg = arr._data
        ripds__vct = bodo.libs.int_arr_ext.alloc_int_array(len(utcqr__hlg),
            dtype)
        for kuvd__odmqd in range(len(utcqr__hlg)):
            if bodo.libs.array_kernels.isna(utcqr__hlg, kuvd__odmqd):
                bodo.libs.array_kernels.setna(ripds__vct, kuvd__odmqd)
                continue
            ripds__vct[kuvd__odmqd] = np.int64(utcqr__hlg[kuvd__odmqd])
        clhm__qyi = len(arr)
        wrrq__ltcft = arr._indices
        usayo__qoilo = bodo.libs.int_arr_ext.alloc_int_array(clhm__qyi, dtype)
        for i in range(clhm__qyi):
            if bodo.libs.array_kernels.isna(wrrq__ltcft, i):
                bodo.libs.array_kernels.setna(usayo__qoilo, i)
                continue
            usayo__qoilo[i] = ripds__vct[wrrq__ltcft[i]]
        return usayo__qoilo
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    kkhwb__vsvib = len(arrs)
    lfluk__viqf = 'def impl(arrs, sep):\n'
    lfluk__viqf += '  ind_map = {}\n'
    lfluk__viqf += '  out_strs = []\n'
    lfluk__viqf += '  n = len(arrs[0])\n'
    for i in range(kkhwb__vsvib):
        lfluk__viqf += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(kkhwb__vsvib):
        lfluk__viqf += f'  data{i} = arrs[{i}]._data\n'
    lfluk__viqf += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    lfluk__viqf += '  for i in range(n):\n'
    dcs__zmp = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(kkhwb__vsvib)])
    lfluk__viqf += f'    if {dcs__zmp}:\n'
    lfluk__viqf += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    lfluk__viqf += '      continue\n'
    for i in range(kkhwb__vsvib):
        lfluk__viqf += f'    ind{i} = indices{i}[i]\n'
    egws__cxxy = '(' + ', '.join(f'ind{i}' for i in range(kkhwb__vsvib)) + ')'
    lfluk__viqf += f'    if {egws__cxxy} not in ind_map:\n'
    lfluk__viqf += '      out_ind = len(out_strs)\n'
    lfluk__viqf += f'      ind_map[{egws__cxxy}] = out_ind\n'
    zsr__jrfj = "''" if is_overload_none(sep) else 'sep'
    pzbz__sms = ', '.join([f'data{i}[ind{i}]' for i in range(kkhwb__vsvib)])
    lfluk__viqf += f'      v = {zsr__jrfj}.join([{pzbz__sms}])\n'
    lfluk__viqf += '      out_strs.append(v)\n'
    lfluk__viqf += '    else:\n'
    lfluk__viqf += f'      out_ind = ind_map[{egws__cxxy}]\n'
    lfluk__viqf += '    out_indices[i] = out_ind\n'
    lfluk__viqf += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    lfluk__viqf += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    hhvq__bglqx = {}
    exec(lfluk__viqf, {'bodo': bodo, 'numba': numba, 'np': np}, hhvq__bglqx)
    impl = hhvq__bglqx['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    zxb__cwgra = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    myx__umivu = toty(fromty)
    jvw__hbrkj = context.compile_internal(builder, zxb__cwgra, myx__umivu,
        (val,))
    return impl_ret_new_ref(context, builder, toty, jvw__hbrkj)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    gwwpu__tpg = arr._data
    uzsz__qqsv = len(gwwpu__tpg)
    phy__ujdl = pre_alloc_string_array(uzsz__qqsv, -1)
    if regex:
        xpvzb__tozjm = re.compile(pat, flags)
        for i in range(uzsz__qqsv):
            if bodo.libs.array_kernels.isna(gwwpu__tpg, i):
                bodo.libs.array_kernels.setna(phy__ujdl, i)
                continue
            phy__ujdl[i] = xpvzb__tozjm.sub(repl=repl, string=gwwpu__tpg[i])
    else:
        for i in range(uzsz__qqsv):
            if bodo.libs.array_kernels.isna(gwwpu__tpg, i):
                bodo.libs.array_kernels.setna(phy__ujdl, i)
                continue
            phy__ujdl[i] = gwwpu__tpg[i].replace(pat, repl)
    return init_dict_arr(phy__ujdl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    opfn__tvn = arr._data
    tizaw__wrzw = len(opfn__tvn)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(tizaw__wrzw)
    for i in range(tizaw__wrzw):
        dict_arr_out[i] = opfn__tvn[i].startswith(pat)
    rscwr__ikdx = arr._indices
    orgv__pbcjp = len(rscwr__ikdx)
    usayo__qoilo = bodo.libs.bool_arr_ext.alloc_bool_array(orgv__pbcjp)
    for i in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(usayo__qoilo, i)
        else:
            usayo__qoilo[i] = dict_arr_out[rscwr__ikdx[i]]
    return usayo__qoilo


@register_jitable
def str_endswith(arr, pat, na):
    opfn__tvn = arr._data
    tizaw__wrzw = len(opfn__tvn)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(tizaw__wrzw)
    for i in range(tizaw__wrzw):
        dict_arr_out[i] = opfn__tvn[i].endswith(pat)
    rscwr__ikdx = arr._indices
    orgv__pbcjp = len(rscwr__ikdx)
    usayo__qoilo = bodo.libs.bool_arr_ext.alloc_bool_array(orgv__pbcjp)
    for i in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(usayo__qoilo, i)
        else:
            usayo__qoilo[i] = dict_arr_out[rscwr__ikdx[i]]
    return usayo__qoilo


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    opfn__tvn = arr._data
    ivpzp__puin = pd.Series(opfn__tvn)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = ivpzp__puin.array._str_contains(pat, case, flags, na,
            regex)
    rscwr__ikdx = arr._indices
    orgv__pbcjp = len(rscwr__ikdx)
    usayo__qoilo = bodo.libs.bool_arr_ext.alloc_bool_array(orgv__pbcjp)
    for i in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(usayo__qoilo, i)
        else:
            usayo__qoilo[i] = dict_arr_out[rscwr__ikdx[i]]
    return usayo__qoilo


@register_jitable
def str_contains_non_regex(arr, pat, case):
    opfn__tvn = arr._data
    tizaw__wrzw = len(opfn__tvn)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(tizaw__wrzw)
    if not case:
        uhb__iywu = pat.upper()
    for i in range(tizaw__wrzw):
        if case:
            dict_arr_out[i] = pat in opfn__tvn[i]
        else:
            dict_arr_out[i] = uhb__iywu in opfn__tvn[i].upper()
    rscwr__ikdx = arr._indices
    orgv__pbcjp = len(rscwr__ikdx)
    usayo__qoilo = bodo.libs.bool_arr_ext.alloc_bool_array(orgv__pbcjp)
    for i in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(usayo__qoilo, i)
        else:
            usayo__qoilo[i] = dict_arr_out[rscwr__ikdx[i]]
    return usayo__qoilo


def create_simple_str2str_methods(func_name, func_args):
    lfluk__viqf = f"""def str_{func_name}({', '.join(func_args)}):
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
    hhvq__bglqx = {}
    exec(lfluk__viqf, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, hhvq__bglqx)
    return hhvq__bglqx[f'str_{func_name}']


def _register_simple_str2str_methods():
    rej__ybglb = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in rej__ybglb.keys():
        ajfvx__reih = create_simple_str2str_methods(func_name, rej__ybglb[
            func_name])
        ajfvx__reih = register_jitable(ajfvx__reih)
        globals()[f'str_{func_name}'] = ajfvx__reih


_register_simple_str2str_methods()


def create_find_methods(func_name):
    lfluk__viqf = f"""def str_{func_name}(arr, sub, start, end):
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
    hhvq__bglqx = {}
    exec(lfluk__viqf, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, hhvq__bglqx)
    return hhvq__bglqx[f'str_{func_name}']


def _register_find_methods():
    qep__lbg = ['find', 'rfind']
    for func_name in qep__lbg:
        ajfvx__reih = create_find_methods(func_name)
        ajfvx__reih = register_jitable(ajfvx__reih)
        globals()[f'str_{func_name}'] = ajfvx__reih


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    gwwpu__tpg = arr._data
    rscwr__ikdx = arr._indices
    uzsz__qqsv = len(gwwpu__tpg)
    orgv__pbcjp = len(rscwr__ikdx)
    dsouc__aswqj = bodo.libs.int_arr_ext.alloc_int_array(uzsz__qqsv, np.int64)
    rjc__gfjxl = bodo.libs.int_arr_ext.alloc_int_array(orgv__pbcjp, np.int64)
    regex = re.compile(pat, flags)
    for i in range(uzsz__qqsv):
        if bodo.libs.array_kernels.isna(gwwpu__tpg, i):
            bodo.libs.array_kernels.setna(dsouc__aswqj, i)
            continue
        dsouc__aswqj[i] = bodo.libs.str_ext.str_findall_count(regex,
            gwwpu__tpg[i])
    for i in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(rscwr__ikdx, i
            ) or bodo.libs.array_kernels.isna(dsouc__aswqj, rscwr__ikdx[i]):
            bodo.libs.array_kernels.setna(rjc__gfjxl, i)
        else:
            rjc__gfjxl[i] = dsouc__aswqj[rscwr__ikdx[i]]
    return rjc__gfjxl


@register_jitable
def str_len(arr):
    gwwpu__tpg = arr._data
    rscwr__ikdx = arr._indices
    orgv__pbcjp = len(rscwr__ikdx)
    dsouc__aswqj = bodo.libs.array_kernels.get_arr_lens(gwwpu__tpg, False)
    rjc__gfjxl = bodo.libs.int_arr_ext.alloc_int_array(orgv__pbcjp, np.int64)
    for i in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(rscwr__ikdx, i
            ) or bodo.libs.array_kernels.isna(dsouc__aswqj, rscwr__ikdx[i]):
            bodo.libs.array_kernels.setna(rjc__gfjxl, i)
        else:
            rjc__gfjxl[i] = dsouc__aswqj[rscwr__ikdx[i]]
    return rjc__gfjxl


@register_jitable
def str_slice(arr, start, stop, step):
    gwwpu__tpg = arr._data
    uzsz__qqsv = len(gwwpu__tpg)
    phy__ujdl = bodo.libs.str_arr_ext.pre_alloc_string_array(uzsz__qqsv, -1)
    for i in range(uzsz__qqsv):
        if bodo.libs.array_kernels.isna(gwwpu__tpg, i):
            bodo.libs.array_kernels.setna(phy__ujdl, i)
            continue
        phy__ujdl[i] = gwwpu__tpg[i][start:stop:step]
    return init_dict_arr(phy__ujdl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    gwwpu__tpg = arr._data
    rscwr__ikdx = arr._indices
    uzsz__qqsv = len(gwwpu__tpg)
    orgv__pbcjp = len(rscwr__ikdx)
    phy__ujdl = pre_alloc_string_array(uzsz__qqsv, -1)
    usayo__qoilo = pre_alloc_string_array(orgv__pbcjp, -1)
    for kuvd__odmqd in range(uzsz__qqsv):
        if bodo.libs.array_kernels.isna(gwwpu__tpg, kuvd__odmqd) or not -len(
            gwwpu__tpg[kuvd__odmqd]) <= i < len(gwwpu__tpg[kuvd__odmqd]):
            bodo.libs.array_kernels.setna(phy__ujdl, kuvd__odmqd)
            continue
        phy__ujdl[kuvd__odmqd] = gwwpu__tpg[kuvd__odmqd][i]
    for kuvd__odmqd in range(orgv__pbcjp):
        if bodo.libs.array_kernels.isna(rscwr__ikdx, kuvd__odmqd
            ) or bodo.libs.array_kernels.isna(phy__ujdl, rscwr__ikdx[
            kuvd__odmqd]):
            bodo.libs.array_kernels.setna(usayo__qoilo, kuvd__odmqd)
            continue
        usayo__qoilo[kuvd__odmqd] = phy__ujdl[rscwr__ikdx[kuvd__odmqd]]
    return usayo__qoilo


@register_jitable
def str_repeat_int(arr, repeats):
    gwwpu__tpg = arr._data
    uzsz__qqsv = len(gwwpu__tpg)
    phy__ujdl = pre_alloc_string_array(uzsz__qqsv, -1)
    for i in range(uzsz__qqsv):
        if bodo.libs.array_kernels.isna(gwwpu__tpg, i):
            bodo.libs.array_kernels.setna(phy__ujdl, i)
            continue
        phy__ujdl[i] = gwwpu__tpg[i] * repeats
    return init_dict_arr(phy__ujdl, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    lfluk__viqf = f"""def str_{func_name}(arr):
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
    hhvq__bglqx = {}
    exec(lfluk__viqf, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, hhvq__bglqx)
    return hhvq__bglqx[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        ajfvx__reih = create_str2bool_methods(func_name)
        ajfvx__reih = register_jitable(ajfvx__reih)
        globals()[f'str_{func_name}'] = ajfvx__reih


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    gwwpu__tpg = arr._data
    rscwr__ikdx = arr._indices
    uzsz__qqsv = len(gwwpu__tpg)
    orgv__pbcjp = len(rscwr__ikdx)
    regex = re.compile(pat, flags=flags)
    hkd__fvjrj = []
    for weyyv__jltn in range(n_cols):
        hkd__fvjrj.append(pre_alloc_string_array(uzsz__qqsv, -1))
    yfmys__tfh = bodo.libs.bool_arr_ext.alloc_bool_array(uzsz__qqsv)
    hrqa__heywi = rscwr__ikdx.copy()
    for i in range(uzsz__qqsv):
        if bodo.libs.array_kernels.isna(gwwpu__tpg, i):
            yfmys__tfh[i] = True
            for kuvd__odmqd in range(n_cols):
                bodo.libs.array_kernels.setna(hkd__fvjrj[kuvd__odmqd], i)
            continue
        zgt__idup = regex.search(gwwpu__tpg[i])
        if zgt__idup:
            yfmys__tfh[i] = False
            iiys__ank = zgt__idup.groups()
            for kuvd__odmqd in range(n_cols):
                hkd__fvjrj[kuvd__odmqd][i] = iiys__ank[kuvd__odmqd]
        else:
            yfmys__tfh[i] = True
            for kuvd__odmqd in range(n_cols):
                bodo.libs.array_kernels.setna(hkd__fvjrj[kuvd__odmqd], i)
    for i in range(orgv__pbcjp):
        if yfmys__tfh[hrqa__heywi[i]]:
            bodo.libs.array_kernels.setna(hrqa__heywi, i)
    akd__oxebf = [init_dict_arr(hkd__fvjrj[i], hrqa__heywi.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return akd__oxebf


def create_extractall_methods(is_multi_group):
    qbl__kdtyv = '_multi' if is_multi_group else ''
    lfluk__viqf = f"""def str_extractall{qbl__kdtyv}(arr, regex, n_cols, index_arr):
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
    hhvq__bglqx = {}
    exec(lfluk__viqf, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, hhvq__bglqx)
    return hhvq__bglqx[f'str_extractall{qbl__kdtyv}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        qbl__kdtyv = '_multi' if is_multi_group else ''
        ajfvx__reih = create_extractall_methods(is_multi_group)
        ajfvx__reih = register_jitable(ajfvx__reih)
        globals()[f'str_extractall{qbl__kdtyv}'] = ajfvx__reih


_register_extractall_methods()
