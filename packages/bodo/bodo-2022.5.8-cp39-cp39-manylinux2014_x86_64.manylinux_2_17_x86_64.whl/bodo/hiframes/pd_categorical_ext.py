import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        jrhfh__ncfcc = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=jrhfh__ncfcc)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    axruz__nif = tuple(val.categories.values)
    elem_type = None if len(axruz__nif) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(axruz__nif, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        sed__kqy = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, sed__kqy)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    ybji__tkrd = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    hpumu__gprm = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, dqu__tssip, dqu__tssip = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    wnnk__wyys = PDCategoricalDtype(hpumu__gprm, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, ybji__tkrd)
    return wnnk__wyys(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kbh__ekxw = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, kbh__ekxw).value
    c.pyapi.decref(kbh__ekxw)
    yuj__eblr = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, yuj__eblr).value
    c.pyapi.decref(yuj__eblr)
    jwxc__lml = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=jwxc__lml)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    kbh__ekxw = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    ciywy__tuaby = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    eyas__wxry = c.context.insert_const_string(c.builder.module, 'pandas')
    ygh__fbxof = c.pyapi.import_module_noblock(eyas__wxry)
    hogqb__mzjc = c.pyapi.call_method(ygh__fbxof, 'CategoricalDtype', (
        ciywy__tuaby, kbh__ekxw))
    c.pyapi.decref(kbh__ekxw)
    c.pyapi.decref(ciywy__tuaby)
    c.pyapi.decref(ygh__fbxof)
    c.context.nrt.decref(c.builder, typ, val)
    return hogqb__mzjc


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            f'CategoricalArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rgd__arab = get_categories_int_type(fe_type.dtype)
        sed__kqy = [('dtype', fe_type.dtype), ('codes', types.Array(
            rgd__arab, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, sed__kqy)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    sqqav__vrko = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), sqqav__vrko
        ).value
    c.pyapi.decref(sqqav__vrko)
    hogqb__mzjc = c.pyapi.object_getattr_string(val, 'dtype')
    fpwi__yhvf = c.pyapi.to_native_value(typ.dtype, hogqb__mzjc).value
    c.pyapi.decref(hogqb__mzjc)
    cfgxs__cmhy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cfgxs__cmhy.codes = codes
    cfgxs__cmhy.dtype = fpwi__yhvf
    return NativeValue(cfgxs__cmhy._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    zmfys__pmf = get_categories_int_type(typ.dtype)
    xuxsk__phgj = context.get_constant_generic(builder, types.Array(
        zmfys__pmf, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, xuxsk__phgj])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    owqhr__vohd = len(cat_dtype.categories)
    if owqhr__vohd < np.iinfo(np.int8).max:
        dtype = types.int8
    elif owqhr__vohd < np.iinfo(np.int16).max:
        dtype = types.int16
    elif owqhr__vohd < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    eyas__wxry = c.context.insert_const_string(c.builder.module, 'pandas')
    ygh__fbxof = c.pyapi.import_module_noblock(eyas__wxry)
    rgd__arab = get_categories_int_type(dtype)
    thz__waqm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    fjg__kvn = types.Array(rgd__arab, 1, 'C')
    c.context.nrt.incref(c.builder, fjg__kvn, thz__waqm.codes)
    sqqav__vrko = c.pyapi.from_native_value(fjg__kvn, thz__waqm.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, thz__waqm.dtype)
    hogqb__mzjc = c.pyapi.from_native_value(dtype, thz__waqm.dtype, c.
        env_manager)
    wzc__nmioa = c.pyapi.borrow_none()
    gzh__ipatp = c.pyapi.object_getattr_string(ygh__fbxof, 'Categorical')
    efaqm__aij = c.pyapi.call_method(gzh__ipatp, 'from_codes', (sqqav__vrko,
        wzc__nmioa, wzc__nmioa, hogqb__mzjc))
    c.pyapi.decref(gzh__ipatp)
    c.pyapi.decref(sqqav__vrko)
    c.pyapi.decref(hogqb__mzjc)
    c.pyapi.decref(ygh__fbxof)
    c.context.nrt.decref(c.builder, typ, val)
    return efaqm__aij


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, CategoricalArrayType):
        return CategoricalArrayType(_to_readonly(t.dtype))
    if isinstance(t, PDCategoricalDtype):
        return PDCategoricalDtype(t.categories, t.elem_type, t.ordered,
            _to_readonly(t.data), t.int_type)
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    if _to_readonly(toty) == fromty:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            ter__coed = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                bctz__rxf = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), ter__coed)
                return bctz__rxf
            return impl_lit

        def impl(A, other):
            ter__coed = get_code_for_value(A.dtype, other)
            bctz__rxf = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), ter__coed)
            return bctz__rxf
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        bcg__mobxc = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(bcg__mobxc)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    thz__waqm = cat_dtype.categories
    n = len(thz__waqm)
    for bwaz__wbp in range(n):
        if thz__waqm[bwaz__wbp] == val:
            return bwaz__wbp
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    viwna__mbqtf = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if (viwna__mbqtf != A.dtype.elem_type and viwna__mbqtf != types.
        unicode_type):
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if viwna__mbqtf == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            bctz__rxf = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for bwaz__wbp in numba.parfors.parfor.internal_prange(n):
                xfh__rfq = codes[bwaz__wbp]
                if xfh__rfq == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(bctz__rxf,
                            bwaz__wbp)
                    else:
                        bodo.libs.array_kernels.setna(bctz__rxf, bwaz__wbp)
                    continue
                bctz__rxf[bwaz__wbp] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[xfh__rfq]))
            return bctz__rxf
        return impl
    fjg__kvn = dtype_to_array_type(viwna__mbqtf)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        bctz__rxf = bodo.utils.utils.alloc_type(n, fjg__kvn, (-1,))
        for bwaz__wbp in numba.parfors.parfor.internal_prange(n):
            xfh__rfq = codes[bwaz__wbp]
            if xfh__rfq == -1:
                bodo.libs.array_kernels.setna(bctz__rxf, bwaz__wbp)
                continue
            bctz__rxf[bwaz__wbp] = bodo.utils.conversion.unbox_if_timestamp(
                categories[xfh__rfq])
        return bctz__rxf
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        ejpsh__gpm, fpwi__yhvf = args
        thz__waqm = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        thz__waqm.codes = ejpsh__gpm
        thz__waqm.dtype = fpwi__yhvf
        context.nrt.incref(builder, signature.args[0], ejpsh__gpm)
        context.nrt.incref(builder, signature.args[1], fpwi__yhvf)
        return thz__waqm._getvalue()
    luhba__mnp = CategoricalArrayType(cat_dtype)
    sig = luhba__mnp(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    yhcoe__qrvx = args[0]
    if equiv_set.has_shape(yhcoe__qrvx):
        return ArrayAnalysis.AnalyzeResult(shape=yhcoe__qrvx, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    rgd__arab = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, rgd__arab)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            wim__saapg = {}
            xuxsk__phgj = np.empty(n + 1, np.int64)
            ryzl__puh = {}
            vvrq__cxy = []
            cwe__pmt = {}
            for bwaz__wbp in range(n):
                cwe__pmt[categories[bwaz__wbp]] = bwaz__wbp
            for izmjj__aend in to_replace:
                if izmjj__aend != value:
                    if izmjj__aend in cwe__pmt:
                        if value in cwe__pmt:
                            wim__saapg[izmjj__aend] = izmjj__aend
                            nxri__bgms = cwe__pmt[izmjj__aend]
                            ryzl__puh[nxri__bgms] = cwe__pmt[value]
                            vvrq__cxy.append(nxri__bgms)
                        else:
                            wim__saapg[izmjj__aend] = value
                            cwe__pmt[value] = cwe__pmt[izmjj__aend]
            pahpm__imhn = np.sort(np.array(vvrq__cxy))
            sjkhj__cxwyd = 0
            hnij__knl = []
            for mfus__yatm in range(-1, n):
                while sjkhj__cxwyd < len(pahpm__imhn
                    ) and mfus__yatm > pahpm__imhn[sjkhj__cxwyd]:
                    sjkhj__cxwyd += 1
                hnij__knl.append(sjkhj__cxwyd)
            for hdcaa__qeviq in range(-1, n):
                asxk__gfawo = hdcaa__qeviq
                if hdcaa__qeviq in ryzl__puh:
                    asxk__gfawo = ryzl__puh[hdcaa__qeviq]
                xuxsk__phgj[hdcaa__qeviq + 1] = asxk__gfawo - hnij__knl[
                    asxk__gfawo + 1]
            return wim__saapg, xuxsk__phgj, len(pahpm__imhn)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for bwaz__wbp in range(len(new_codes_arr)):
        new_codes_arr[bwaz__wbp] = codes_map_arr[old_codes_arr[bwaz__wbp] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_replace,
        'CategoricalArray.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'CategoricalArray.replace()')
    xqtf__qhvgv = arr.dtype.ordered
    mpgs__ujg = arr.dtype.elem_type
    rcwbs__xjnxc = get_overload_const(to_replace)
    pfeg__dygc = get_overload_const(value)
    if (arr.dtype.categories is not None and rcwbs__xjnxc is not
        NOT_CONSTANT and pfeg__dygc is not NOT_CONSTANT):
        vycjk__aosq, codes_map_arr, dqu__tssip = python_build_replace_dicts(
            rcwbs__xjnxc, pfeg__dygc, arr.dtype.categories)
        if len(vycjk__aosq) == 0:
            return lambda arr, to_replace, value: arr.copy()
        fke__djpcb = []
        for wdnuf__mtc in arr.dtype.categories:
            if wdnuf__mtc in vycjk__aosq:
                hcwe__gdbtt = vycjk__aosq[wdnuf__mtc]
                if hcwe__gdbtt != wdnuf__mtc:
                    fke__djpcb.append(hcwe__gdbtt)
            else:
                fke__djpcb.append(wdnuf__mtc)
        case__otiht = pd.CategoricalDtype(fke__djpcb, xqtf__qhvgv
            ).categories.values
        zmg__wvtzd = MetaType(tuple(case__otiht))

        def impl_dtype(arr, to_replace, value):
            milu__vrryv = init_cat_dtype(bodo.utils.conversion.
                index_from_array(case__otiht), xqtf__qhvgv, None, zmg__wvtzd)
            thz__waqm = alloc_categorical_array(len(arr.codes), milu__vrryv)
            reassign_codes(thz__waqm.codes, arr.codes, codes_map_arr)
            return thz__waqm
        return impl_dtype
    mpgs__ujg = arr.dtype.elem_type
    if mpgs__ujg == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            wim__saapg, codes_map_arr, jggt__uplo = build_replace_dicts(
                to_replace, value, categories.values)
            if len(wim__saapg) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), xqtf__qhvgv,
                    None, None))
            n = len(categories)
            case__otiht = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                jggt__uplo, -1)
            fkd__gbv = 0
            for mfus__yatm in range(n):
                zeoro__cexz = categories[mfus__yatm]
                if zeoro__cexz in wim__saapg:
                    bgk__kvupi = wim__saapg[zeoro__cexz]
                    if bgk__kvupi != zeoro__cexz:
                        case__otiht[fkd__gbv] = bgk__kvupi
                        fkd__gbv += 1
                else:
                    case__otiht[fkd__gbv] = zeoro__cexz
                    fkd__gbv += 1
            thz__waqm = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                case__otiht), xqtf__qhvgv, None, None))
            reassign_codes(thz__waqm.codes, arr.codes, codes_map_arr)
            return thz__waqm
        return impl_str
    lwqfg__rgo = dtype_to_array_type(mpgs__ujg)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        wim__saapg, codes_map_arr, jggt__uplo = build_replace_dicts(to_replace,
            value, categories.values)
        if len(wim__saapg) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), xqtf__qhvgv, None, None))
        n = len(categories)
        case__otiht = bodo.utils.utils.alloc_type(n - jggt__uplo,
            lwqfg__rgo, None)
        fkd__gbv = 0
        for bwaz__wbp in range(n):
            zeoro__cexz = categories[bwaz__wbp]
            if zeoro__cexz in wim__saapg:
                bgk__kvupi = wim__saapg[zeoro__cexz]
                if bgk__kvupi != zeoro__cexz:
                    case__otiht[fkd__gbv] = bgk__kvupi
                    fkd__gbv += 1
            else:
                case__otiht[fkd__gbv] = zeoro__cexz
                fkd__gbv += 1
        thz__waqm = alloc_categorical_array(len(arr.codes), init_cat_dtype(
            bodo.utils.conversion.index_from_array(case__otiht),
            xqtf__qhvgv, None, None))
        reassign_codes(thz__waqm.codes, arr.codes, codes_map_arr)
        return thz__waqm
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    htrp__lslvq = dict()
    qpjgs__ukgiz = 0
    for bwaz__wbp in range(len(vals)):
        val = vals[bwaz__wbp]
        if val in htrp__lslvq:
            continue
        htrp__lslvq[val] = qpjgs__ukgiz
        qpjgs__ukgiz += 1
    return htrp__lslvq


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    htrp__lslvq = dict()
    for bwaz__wbp in range(len(vals)):
        val = vals[bwaz__wbp]
        htrp__lslvq[val] = bwaz__wbp
    return htrp__lslvq


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    opad__hbmpm = dict(fastpath=fastpath)
    qya__vagmm = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', opad__hbmpm, qya__vagmm)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        trr__xhh = get_overload_const(categories)
        if trr__xhh is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                mwqn__kwx = False
            else:
                mwqn__kwx = get_overload_const_bool(ordered)
            hksw__zpefd = pd.CategoricalDtype(trr__xhh, mwqn__kwx
                ).categories.values
            csmmx__ynr = MetaType(tuple(hksw__zpefd))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                milu__vrryv = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(hksw__zpefd), mwqn__kwx, None, csmmx__ynr)
                return bodo.utils.conversion.fix_arr_dtype(data, milu__vrryv)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            axruz__nif = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                axruz__nif, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            okyhd__lofby = arr.codes[ind]
            return arr.dtype.categories[max(okyhd__lofby, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for bwaz__wbp in range(len(arr1)):
        if arr1[bwaz__wbp] != arr2[bwaz__wbp]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    zhuxd__pnxc = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    cuvd__zctro = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    cxt__faamt = categorical_arrs_match(arr, val)
    mrbg__roqw = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    fkmx__hdf = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not zhuxd__pnxc:
            raise BodoError(mrbg__roqw)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            okyhd__lofby = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = okyhd__lofby
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (zhuxd__pnxc or cuvd__zctro or cxt__faamt !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(mrbg__roqw)
        if cxt__faamt == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(fkmx__hdf)
        if zhuxd__pnxc:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                qvxa__seo = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for mfus__yatm in range(n):
                    arr.codes[ind[mfus__yatm]] = qvxa__seo
            return impl_scalar
        if cxt__faamt == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for bwaz__wbp in range(n):
                    arr.codes[ind[bwaz__wbp]] = val.codes[bwaz__wbp]
            return impl_arr_ind_mask
        if cxt__faamt == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(fkmx__hdf)
                n = len(val.codes)
                for bwaz__wbp in range(n):
                    arr.codes[ind[bwaz__wbp]] = val.codes[bwaz__wbp]
            return impl_arr_ind_mask
        if cuvd__zctro:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for mfus__yatm in range(n):
                    kkl__unvuo = bodo.utils.conversion.unbox_if_timestamp(val
                        [mfus__yatm])
                    if kkl__unvuo not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    okyhd__lofby = categories.get_loc(kkl__unvuo)
                    arr.codes[ind[mfus__yatm]] = okyhd__lofby
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (zhuxd__pnxc or cuvd__zctro or cxt__faamt !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(mrbg__roqw)
        if cxt__faamt == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(fkmx__hdf)
        if zhuxd__pnxc:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                qvxa__seo = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for mfus__yatm in range(n):
                    if ind[mfus__yatm]:
                        arr.codes[mfus__yatm] = qvxa__seo
            return impl_scalar
        if cxt__faamt == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                vmxb__vwjmz = 0
                for bwaz__wbp in range(n):
                    if ind[bwaz__wbp]:
                        arr.codes[bwaz__wbp] = val.codes[vmxb__vwjmz]
                        vmxb__vwjmz += 1
            return impl_bool_ind_mask
        if cxt__faamt == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(fkmx__hdf)
                n = len(ind)
                vmxb__vwjmz = 0
                for bwaz__wbp in range(n):
                    if ind[bwaz__wbp]:
                        arr.codes[bwaz__wbp] = val.codes[vmxb__vwjmz]
                        vmxb__vwjmz += 1
            return impl_bool_ind_mask
        if cuvd__zctro:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                vmxb__vwjmz = 0
                categories = arr.dtype.categories
                for mfus__yatm in range(n):
                    if ind[mfus__yatm]:
                        kkl__unvuo = bodo.utils.conversion.unbox_if_timestamp(
                            val[vmxb__vwjmz])
                        if kkl__unvuo not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        okyhd__lofby = categories.get_loc(kkl__unvuo)
                        arr.codes[mfus__yatm] = okyhd__lofby
                        vmxb__vwjmz += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (zhuxd__pnxc or cuvd__zctro or cxt__faamt !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(mrbg__roqw)
        if cxt__faamt == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(fkmx__hdf)
        if zhuxd__pnxc:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                qvxa__seo = arr.dtype.categories.get_loc(val)
                sbnml__jjwa = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for mfus__yatm in range(sbnml__jjwa.start, sbnml__jjwa.stop,
                    sbnml__jjwa.step):
                    arr.codes[mfus__yatm] = qvxa__seo
            return impl_scalar
        if cxt__faamt == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if cxt__faamt == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(fkmx__hdf)
                arr.codes[ind] = val.codes
            return impl_arr
        if cuvd__zctro:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                sbnml__jjwa = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                vmxb__vwjmz = 0
                for mfus__yatm in range(sbnml__jjwa.start, sbnml__jjwa.stop,
                    sbnml__jjwa.step):
                    kkl__unvuo = bodo.utils.conversion.unbox_if_timestamp(val
                        [vmxb__vwjmz])
                    if kkl__unvuo not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    okyhd__lofby = categories.get_loc(kkl__unvuo)
                    arr.codes[mfus__yatm] = okyhd__lofby
                    vmxb__vwjmz += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
