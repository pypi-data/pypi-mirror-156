import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    qqj__uxrh = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        zpia__ivk, = args
        ksvhm__gasy = cgutils.create_struct_proxy(string_type)(context,
            builder, value=zpia__ivk)
        nmaha__kpt = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        wpv__cmhr = cgutils.create_struct_proxy(qqj__uxrh)(context, builder)
        is_ascii = builder.icmp_unsigned('==', ksvhm__gasy.is_ascii, lir.
            Constant(ksvhm__gasy.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (lnhqz__ufez, ort__ipc):
            with lnhqz__ufez:
                context.nrt.incref(builder, string_type, zpia__ivk)
                nmaha__kpt.data = ksvhm__gasy.data
                nmaha__kpt.meminfo = ksvhm__gasy.meminfo
                wpv__cmhr.f1 = ksvhm__gasy.length
            with ort__ipc:
                xszr__maz = lir.FunctionType(lir.IntType(64), [lir.IntType(
                    8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                zbff__vurj = cgutils.get_or_insert_function(builder.module,
                    xszr__maz, name='unicode_to_utf8')
                jciz__eowk = context.get_constant_null(types.voidptr)
                csvi__giq = builder.call(zbff__vurj, [jciz__eowk,
                    ksvhm__gasy.data, ksvhm__gasy.length, ksvhm__gasy.kind])
                wpv__cmhr.f1 = csvi__giq
                abwbd__xum = builder.add(csvi__giq, lir.Constant(lir.
                    IntType(64), 1))
                nmaha__kpt.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=abwbd__xum, align=32)
                nmaha__kpt.data = context.nrt.meminfo_data(builder,
                    nmaha__kpt.meminfo)
                builder.call(zbff__vurj, [nmaha__kpt.data, ksvhm__gasy.data,
                    ksvhm__gasy.length, ksvhm__gasy.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    nmaha__kpt.data, [csvi__giq]))
        wpv__cmhr.f0 = nmaha__kpt._getvalue()
        return wpv__cmhr._getvalue()
    return qqj__uxrh(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        xszr__maz = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        yyi__fhcz = cgutils.get_or_insert_function(builder.module,
            xszr__maz, name='memcmp')
        return builder.call(yyi__fhcz, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    gpno__hntxg = n(10)

    def impl(n):
        if n == 0:
            return 1
        tcl__nlbp = 0
        if n < 0:
            n = -n
            tcl__nlbp += 1
        while n > 0:
            n = n // gpno__hntxg
            tcl__nlbp += 1
        return tcl__nlbp
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [udn__tcg] = args
        if isinstance(udn__tcg, StdStringType):
            return signature(types.float64, udn__tcg)
        if udn__tcg == string_type:
            return signature(types.float64, udn__tcg)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    ksvhm__gasy = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    xszr__maz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    hknp__cpas = cgutils.get_or_insert_function(builder.module, xszr__maz,
        name='init_string_const')
    return builder.call(hknp__cpas, [ksvhm__gasy.data, ksvhm__gasy.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        htnj__fyjfs = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(htnj__fyjfs._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return htnj__fyjfs
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ksvhm__gasy = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return ksvhm__gasy.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kdo__myd = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, kdo__myd)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        kwha__qtoaa, = args
        zsi__rrbll = types.List(string_type)
        iluh__fheym = numba.cpython.listobj.ListInstance.allocate(context,
            builder, zsi__rrbll, kwha__qtoaa)
        iluh__fheym.size = kwha__qtoaa
        ckti__ojvko = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        ckti__ojvko.data = iluh__fheym.value
        return ckti__ojvko._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            wxvz__qfqs = 0
            qpsw__kofhn = v
            if qpsw__kofhn < 0:
                wxvz__qfqs = 1
                qpsw__kofhn = -qpsw__kofhn
            if qpsw__kofhn < 1:
                csyx__krtyp = 1
            else:
                csyx__krtyp = 1 + int(np.floor(np.log10(qpsw__kofhn)))
            length = wxvz__qfqs + csyx__krtyp + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    xszr__maz = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    hknp__cpas = cgutils.get_or_insert_function(builder.module, xszr__maz,
        name='str_to_float64')
    res = builder.call(hknp__cpas, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    xszr__maz = lir.FunctionType(lir.FloatType(), [lir.IntType(8).as_pointer()]
        )
    hknp__cpas = cgutils.get_or_insert_function(builder.module, xszr__maz,
        name='str_to_float32')
    res = builder.call(hknp__cpas, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    ksvhm__gasy = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    xszr__maz = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    hknp__cpas = cgutils.get_or_insert_function(builder.module, xszr__maz,
        name='str_to_int64')
    res = builder.call(hknp__cpas, (ksvhm__gasy.data, ksvhm__gasy.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ksvhm__gasy = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    xszr__maz = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    hknp__cpas = cgutils.get_or_insert_function(builder.module, xszr__maz,
        name='str_to_uint64')
    res = builder.call(hknp__cpas, (ksvhm__gasy.data, ksvhm__gasy.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        rcpxx__rpjf = ', '.join('e{}'.format(kuvy__hilx) for kuvy__hilx in
            range(len(args)))
        if rcpxx__rpjf:
            rcpxx__rpjf += ', '
        xps__osyke = ', '.join("{} = ''".format(a) for a in kws.keys())
        naht__wfb = f'def format_stub(string, {rcpxx__rpjf} {xps__osyke}):\n'
        naht__wfb += '    pass\n'
        dmmx__bleg = {}
        exec(naht__wfb, {}, dmmx__bleg)
        wux__ovjd = dmmx__bleg['format_stub']
        uhu__rrue = numba.core.utils.pysignature(wux__ovjd)
        xkmx__bope = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, xkmx__bope).replace(pysig=uhu__rrue)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    loz__luo = pat is not None and len(pat) > 1
    if loz__luo:
        rpivr__nco = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    iluh__fheym = len(arr)
    huwb__hyx = 0
    jbnra__voc = 0
    for kuvy__hilx in numba.parfors.parfor.internal_prange(iluh__fheym):
        if bodo.libs.array_kernels.isna(arr, kuvy__hilx):
            continue
        if loz__luo:
            zmf__xphn = rpivr__nco.split(arr[kuvy__hilx], maxsplit=n)
        elif pat == '':
            zmf__xphn = [''] + list(arr[kuvy__hilx]) + ['']
        else:
            zmf__xphn = arr[kuvy__hilx].split(pat, n)
        huwb__hyx += len(zmf__xphn)
        for s in zmf__xphn:
            jbnra__voc += bodo.libs.str_arr_ext.get_utf8_size(s)
    ujsfy__cffbt = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        iluh__fheym, (huwb__hyx, jbnra__voc), bodo.libs.str_arr_ext.
        string_array_type)
    vuasl__rurvq = bodo.libs.array_item_arr_ext.get_offsets(ujsfy__cffbt)
    iyk__dji = bodo.libs.array_item_arr_ext.get_null_bitmap(ujsfy__cffbt)
    acigu__hjdtq = bodo.libs.array_item_arr_ext.get_data(ujsfy__cffbt)
    jtfqo__wjc = 0
    for zodtx__ffv in numba.parfors.parfor.internal_prange(iluh__fheym):
        vuasl__rurvq[zodtx__ffv] = jtfqo__wjc
        if bodo.libs.array_kernels.isna(arr, zodtx__ffv):
            bodo.libs.int_arr_ext.set_bit_to_arr(iyk__dji, zodtx__ffv, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(iyk__dji, zodtx__ffv, 1)
        if loz__luo:
            zmf__xphn = rpivr__nco.split(arr[zodtx__ffv], maxsplit=n)
        elif pat == '':
            zmf__xphn = [''] + list(arr[zodtx__ffv]) + ['']
        else:
            zmf__xphn = arr[zodtx__ffv].split(pat, n)
        ryu__eznto = len(zmf__xphn)
        for leru__febql in range(ryu__eznto):
            s = zmf__xphn[leru__febql]
            acigu__hjdtq[jtfqo__wjc] = s
            jtfqo__wjc += 1
    vuasl__rurvq[iluh__fheym] = jtfqo__wjc
    return ujsfy__cffbt


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                lusxr__tmskr = '-0x'
                x = x * -1
            else:
                lusxr__tmskr = '0x'
            x = np.uint64(x)
            if x == 0:
                eahi__pmj = 1
            else:
                eahi__pmj = fast_ceil_log2(x + 1)
                eahi__pmj = (eahi__pmj + 3) // 4
            length = len(lusxr__tmskr) + eahi__pmj
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, lusxr__tmskr._data,
                len(lusxr__tmskr), 1)
            int_to_hex(output, eahi__pmj, len(lusxr__tmskr), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    dfsr__fsq = 0 if x & x - 1 == 0 else 1
    oez__ecz = [np.uint64(18446744069414584320), np.uint64(4294901760), np.
        uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    hwqqo__abtw = 32
    for kuvy__hilx in range(len(oez__ecz)):
        owgrv__dyvjj = 0 if x & oez__ecz[kuvy__hilx] == 0 else hwqqo__abtw
        dfsr__fsq = dfsr__fsq + owgrv__dyvjj
        x = x >> owgrv__dyvjj
        hwqqo__abtw = hwqqo__abtw >> 1
    return dfsr__fsq


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        unhs__tufs = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        xszr__maz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        sbns__vkccn = cgutils.get_or_insert_function(builder.module,
            xszr__maz, name='int_to_hex')
        zcqn__slqj = builder.inttoptr(builder.add(builder.ptrtoint(
            unhs__tufs.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(sbns__vkccn, (zcqn__slqj, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
