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
        pwna__chfu = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=pwna__chfu)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    zllpl__rwybf = tuple(val.categories.values)
    elem_type = None if len(zllpl__rwybf) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(zllpl__rwybf, elem_type, val.ordered, bodo.
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
        iyghl__mbz = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, iyghl__mbz)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    fjuwe__temfq = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    mhvjz__qvkn = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, rdfn__rdra, rdfn__rdra = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    miz__ycog = PDCategoricalDtype(mhvjz__qvkn, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, fjuwe__temfq)
    return miz__ycog(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jhjau__ylel = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, jhjau__ylel).value
    c.pyapi.decref(jhjau__ylel)
    etnnd__xny = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, etnnd__xny).value
    c.pyapi.decref(etnnd__xny)
    lmrxi__mct = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=lmrxi__mct)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    jhjau__ylel = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    glfzy__vikfn = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    svs__vbtah = c.context.insert_const_string(c.builder.module, 'pandas')
    ktkp__vli = c.pyapi.import_module_noblock(svs__vbtah)
    kcxx__eedj = c.pyapi.call_method(ktkp__vli, 'CategoricalDtype', (
        glfzy__vikfn, jhjau__ylel))
    c.pyapi.decref(jhjau__ylel)
    c.pyapi.decref(glfzy__vikfn)
    c.pyapi.decref(ktkp__vli)
    c.context.nrt.decref(c.builder, typ, val)
    return kcxx__eedj


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
        kpld__crthg = get_categories_int_type(fe_type.dtype)
        iyghl__mbz = [('dtype', fe_type.dtype), ('codes', types.Array(
            kpld__crthg, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, iyghl__mbz)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    ehbhm__navce = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), ehbhm__navce
        ).value
    c.pyapi.decref(ehbhm__navce)
    kcxx__eedj = c.pyapi.object_getattr_string(val, 'dtype')
    hbm__pvqf = c.pyapi.to_native_value(typ.dtype, kcxx__eedj).value
    c.pyapi.decref(kcxx__eedj)
    hxc__gkso = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hxc__gkso.codes = codes
    hxc__gkso.dtype = hbm__pvqf
    return NativeValue(hxc__gkso._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    iwkzo__mmq = get_categories_int_type(typ.dtype)
    lny__iicy = context.get_constant_generic(builder, types.Array(
        iwkzo__mmq, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, lny__iicy])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    fuwuw__dmng = len(cat_dtype.categories)
    if fuwuw__dmng < np.iinfo(np.int8).max:
        dtype = types.int8
    elif fuwuw__dmng < np.iinfo(np.int16).max:
        dtype = types.int16
    elif fuwuw__dmng < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    svs__vbtah = c.context.insert_const_string(c.builder.module, 'pandas')
    ktkp__vli = c.pyapi.import_module_noblock(svs__vbtah)
    kpld__crthg = get_categories_int_type(dtype)
    etcnd__oig = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    uwnkt__dhrf = types.Array(kpld__crthg, 1, 'C')
    c.context.nrt.incref(c.builder, uwnkt__dhrf, etcnd__oig.codes)
    ehbhm__navce = c.pyapi.from_native_value(uwnkt__dhrf, etcnd__oig.codes,
        c.env_manager)
    c.context.nrt.incref(c.builder, dtype, etcnd__oig.dtype)
    kcxx__eedj = c.pyapi.from_native_value(dtype, etcnd__oig.dtype, c.
        env_manager)
    hwv__geuvh = c.pyapi.borrow_none()
    uvtl__eoyk = c.pyapi.object_getattr_string(ktkp__vli, 'Categorical')
    mdu__mbyg = c.pyapi.call_method(uvtl__eoyk, 'from_codes', (ehbhm__navce,
        hwv__geuvh, hwv__geuvh, kcxx__eedj))
    c.pyapi.decref(uvtl__eoyk)
    c.pyapi.decref(ehbhm__navce)
    c.pyapi.decref(kcxx__eedj)
    c.pyapi.decref(ktkp__vli)
    c.context.nrt.decref(c.builder, typ, val)
    return mdu__mbyg


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
            bkx__bqm = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                fany__eeib = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), bkx__bqm)
                return fany__eeib
            return impl_lit

        def impl(A, other):
            bkx__bqm = get_code_for_value(A.dtype, other)
            fany__eeib = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), bkx__bqm)
            return fany__eeib
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        zyfbd__kriw = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(zyfbd__kriw)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    etcnd__oig = cat_dtype.categories
    n = len(etcnd__oig)
    for twjmi__zmao in range(n):
        if etcnd__oig[twjmi__zmao] == val:
            return twjmi__zmao
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    eavmd__phrkl = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if (eavmd__phrkl != A.dtype.elem_type and eavmd__phrkl != types.
        unicode_type):
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if eavmd__phrkl == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            fany__eeib = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for twjmi__zmao in numba.parfors.parfor.internal_prange(n):
                jllcb__snnxv = codes[twjmi__zmao]
                if jllcb__snnxv == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(fany__eeib
                            , twjmi__zmao)
                    else:
                        bodo.libs.array_kernels.setna(fany__eeib, twjmi__zmao)
                    continue
                fany__eeib[twjmi__zmao] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[jllcb__snnxv]))
            return fany__eeib
        return impl
    uwnkt__dhrf = dtype_to_array_type(eavmd__phrkl)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        fany__eeib = bodo.utils.utils.alloc_type(n, uwnkt__dhrf, (-1,))
        for twjmi__zmao in numba.parfors.parfor.internal_prange(n):
            jllcb__snnxv = codes[twjmi__zmao]
            if jllcb__snnxv == -1:
                bodo.libs.array_kernels.setna(fany__eeib, twjmi__zmao)
                continue
            fany__eeib[twjmi__zmao] = bodo.utils.conversion.unbox_if_timestamp(
                categories[jllcb__snnxv])
        return fany__eeib
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        nionl__oug, hbm__pvqf = args
        etcnd__oig = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        etcnd__oig.codes = nionl__oug
        etcnd__oig.dtype = hbm__pvqf
        context.nrt.incref(builder, signature.args[0], nionl__oug)
        context.nrt.incref(builder, signature.args[1], hbm__pvqf)
        return etcnd__oig._getvalue()
    loiqo__ubj = CategoricalArrayType(cat_dtype)
    sig = loiqo__ubj(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    jnmh__jzdyk = args[0]
    if equiv_set.has_shape(jnmh__jzdyk):
        return ArrayAnalysis.AnalyzeResult(shape=jnmh__jzdyk, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    kpld__crthg = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, kpld__crthg)
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
            pdo__fpmgh = {}
            lny__iicy = np.empty(n + 1, np.int64)
            wnegq__wkr = {}
            aqbdu__injiv = []
            exkia__kmzfe = {}
            for twjmi__zmao in range(n):
                exkia__kmzfe[categories[twjmi__zmao]] = twjmi__zmao
            for fbwp__fbhr in to_replace:
                if fbwp__fbhr != value:
                    if fbwp__fbhr in exkia__kmzfe:
                        if value in exkia__kmzfe:
                            pdo__fpmgh[fbwp__fbhr] = fbwp__fbhr
                            tav__xvuq = exkia__kmzfe[fbwp__fbhr]
                            wnegq__wkr[tav__xvuq] = exkia__kmzfe[value]
                            aqbdu__injiv.append(tav__xvuq)
                        else:
                            pdo__fpmgh[fbwp__fbhr] = value
                            exkia__kmzfe[value] = exkia__kmzfe[fbwp__fbhr]
            hwwo__ylr = np.sort(np.array(aqbdu__injiv))
            vpj__suemy = 0
            vxskv__lff = []
            for uve__tbr in range(-1, n):
                while vpj__suemy < len(hwwo__ylr) and uve__tbr > hwwo__ylr[
                    vpj__suemy]:
                    vpj__suemy += 1
                vxskv__lff.append(vpj__suemy)
            for kstqr__ysum in range(-1, n):
                xoot__zcrg = kstqr__ysum
                if kstqr__ysum in wnegq__wkr:
                    xoot__zcrg = wnegq__wkr[kstqr__ysum]
                lny__iicy[kstqr__ysum + 1] = xoot__zcrg - vxskv__lff[
                    xoot__zcrg + 1]
            return pdo__fpmgh, lny__iicy, len(hwwo__ylr)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for twjmi__zmao in range(len(new_codes_arr)):
        new_codes_arr[twjmi__zmao] = codes_map_arr[old_codes_arr[
            twjmi__zmao] + 1]


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
    llw__aoacx = arr.dtype.ordered
    caa__vofrv = arr.dtype.elem_type
    vcout__xaw = get_overload_const(to_replace)
    ggmbt__chr = get_overload_const(value)
    if (arr.dtype.categories is not None and vcout__xaw is not NOT_CONSTANT and
        ggmbt__chr is not NOT_CONSTANT):
        bdefp__fek, codes_map_arr, rdfn__rdra = python_build_replace_dicts(
            vcout__xaw, ggmbt__chr, arr.dtype.categories)
        if len(bdefp__fek) == 0:
            return lambda arr, to_replace, value: arr.copy()
        layx__unjrw = []
        for hrnss__zvs in arr.dtype.categories:
            if hrnss__zvs in bdefp__fek:
                hjlk__kyqw = bdefp__fek[hrnss__zvs]
                if hjlk__kyqw != hrnss__zvs:
                    layx__unjrw.append(hjlk__kyqw)
            else:
                layx__unjrw.append(hrnss__zvs)
        fdj__ats = pd.CategoricalDtype(layx__unjrw, llw__aoacx
            ).categories.values
        dwdvs__lwy = MetaType(tuple(fdj__ats))

        def impl_dtype(arr, to_replace, value):
            ncrl__zxn = init_cat_dtype(bodo.utils.conversion.
                index_from_array(fdj__ats), llw__aoacx, None, dwdvs__lwy)
            etcnd__oig = alloc_categorical_array(len(arr.codes), ncrl__zxn)
            reassign_codes(etcnd__oig.codes, arr.codes, codes_map_arr)
            return etcnd__oig
        return impl_dtype
    caa__vofrv = arr.dtype.elem_type
    if caa__vofrv == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            pdo__fpmgh, codes_map_arr, uhs__pbbm = build_replace_dicts(
                to_replace, value, categories.values)
            if len(pdo__fpmgh) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), llw__aoacx,
                    None, None))
            n = len(categories)
            fdj__ats = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                uhs__pbbm, -1)
            enzs__hkly = 0
            for uve__tbr in range(n):
                vcgg__rlv = categories[uve__tbr]
                if vcgg__rlv in pdo__fpmgh:
                    yztsq__rgpu = pdo__fpmgh[vcgg__rlv]
                    if yztsq__rgpu != vcgg__rlv:
                        fdj__ats[enzs__hkly] = yztsq__rgpu
                        enzs__hkly += 1
                else:
                    fdj__ats[enzs__hkly] = vcgg__rlv
                    enzs__hkly += 1
            etcnd__oig = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                fdj__ats), llw__aoacx, None, None))
            reassign_codes(etcnd__oig.codes, arr.codes, codes_map_arr)
            return etcnd__oig
        return impl_str
    zjop__srzd = dtype_to_array_type(caa__vofrv)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        pdo__fpmgh, codes_map_arr, uhs__pbbm = build_replace_dicts(to_replace,
            value, categories.values)
        if len(pdo__fpmgh) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), llw__aoacx, None, None))
        n = len(categories)
        fdj__ats = bodo.utils.utils.alloc_type(n - uhs__pbbm, zjop__srzd, None)
        enzs__hkly = 0
        for twjmi__zmao in range(n):
            vcgg__rlv = categories[twjmi__zmao]
            if vcgg__rlv in pdo__fpmgh:
                yztsq__rgpu = pdo__fpmgh[vcgg__rlv]
                if yztsq__rgpu != vcgg__rlv:
                    fdj__ats[enzs__hkly] = yztsq__rgpu
                    enzs__hkly += 1
            else:
                fdj__ats[enzs__hkly] = vcgg__rlv
                enzs__hkly += 1
        etcnd__oig = alloc_categorical_array(len(arr.codes), init_cat_dtype
            (bodo.utils.conversion.index_from_array(fdj__ats), llw__aoacx,
            None, None))
        reassign_codes(etcnd__oig.codes, arr.codes, codes_map_arr)
        return etcnd__oig
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
    zkb__itpf = dict()
    ikdd__eho = 0
    for twjmi__zmao in range(len(vals)):
        val = vals[twjmi__zmao]
        if val in zkb__itpf:
            continue
        zkb__itpf[val] = ikdd__eho
        ikdd__eho += 1
    return zkb__itpf


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    zkb__itpf = dict()
    for twjmi__zmao in range(len(vals)):
        val = vals[twjmi__zmao]
        zkb__itpf[val] = twjmi__zmao
    return zkb__itpf


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    txu__xvqc = dict(fastpath=fastpath)
    lwq__gbx = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', txu__xvqc, lwq__gbx)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        qbyl__oii = get_overload_const(categories)
        if qbyl__oii is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                twxu__wli = False
            else:
                twxu__wli = get_overload_const_bool(ordered)
            mvr__fdqa = pd.CategoricalDtype(qbyl__oii, twxu__wli
                ).categories.values
            eucmu__xao = MetaType(tuple(mvr__fdqa))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                ncrl__zxn = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(mvr__fdqa), twxu__wli, None, eucmu__xao)
                return bodo.utils.conversion.fix_arr_dtype(data, ncrl__zxn)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            zllpl__rwybf = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                zllpl__rwybf, ordered, None, None)
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
            yhu__awvwf = arr.codes[ind]
            return arr.dtype.categories[max(yhu__awvwf, 0)]
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
    for twjmi__zmao in range(len(arr1)):
        if arr1[twjmi__zmao] != arr2[twjmi__zmao]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    rblk__yvev = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    wky__cmnk = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    blf__ggv = categorical_arrs_match(arr, val)
    kzf__essh = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    wjfdz__rzm = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not rblk__yvev:
            raise BodoError(kzf__essh)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            yhu__awvwf = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = yhu__awvwf
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (rblk__yvev or wky__cmnk or blf__ggv !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(kzf__essh)
        if blf__ggv == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(wjfdz__rzm)
        if rblk__yvev:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                fyyr__cuuur = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for uve__tbr in range(n):
                    arr.codes[ind[uve__tbr]] = fyyr__cuuur
            return impl_scalar
        if blf__ggv == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for twjmi__zmao in range(n):
                    arr.codes[ind[twjmi__zmao]] = val.codes[twjmi__zmao]
            return impl_arr_ind_mask
        if blf__ggv == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(wjfdz__rzm)
                n = len(val.codes)
                for twjmi__zmao in range(n):
                    arr.codes[ind[twjmi__zmao]] = val.codes[twjmi__zmao]
            return impl_arr_ind_mask
        if wky__cmnk:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for uve__tbr in range(n):
                    mrtph__bnnj = bodo.utils.conversion.unbox_if_timestamp(val
                        [uve__tbr])
                    if mrtph__bnnj not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    yhu__awvwf = categories.get_loc(mrtph__bnnj)
                    arr.codes[ind[uve__tbr]] = yhu__awvwf
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (rblk__yvev or wky__cmnk or blf__ggv !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(kzf__essh)
        if blf__ggv == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(wjfdz__rzm)
        if rblk__yvev:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                fyyr__cuuur = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for uve__tbr in range(n):
                    if ind[uve__tbr]:
                        arr.codes[uve__tbr] = fyyr__cuuur
            return impl_scalar
        if blf__ggv == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                xpznx__axvl = 0
                for twjmi__zmao in range(n):
                    if ind[twjmi__zmao]:
                        arr.codes[twjmi__zmao] = val.codes[xpznx__axvl]
                        xpznx__axvl += 1
            return impl_bool_ind_mask
        if blf__ggv == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(wjfdz__rzm)
                n = len(ind)
                xpznx__axvl = 0
                for twjmi__zmao in range(n):
                    if ind[twjmi__zmao]:
                        arr.codes[twjmi__zmao] = val.codes[xpznx__axvl]
                        xpznx__axvl += 1
            return impl_bool_ind_mask
        if wky__cmnk:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                xpznx__axvl = 0
                categories = arr.dtype.categories
                for uve__tbr in range(n):
                    if ind[uve__tbr]:
                        mrtph__bnnj = bodo.utils.conversion.unbox_if_timestamp(
                            val[xpznx__axvl])
                        if mrtph__bnnj not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        yhu__awvwf = categories.get_loc(mrtph__bnnj)
                        arr.codes[uve__tbr] = yhu__awvwf
                        xpznx__axvl += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (rblk__yvev or wky__cmnk or blf__ggv !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(kzf__essh)
        if blf__ggv == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(wjfdz__rzm)
        if rblk__yvev:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                fyyr__cuuur = arr.dtype.categories.get_loc(val)
                hmho__mvqw = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for uve__tbr in range(hmho__mvqw.start, hmho__mvqw.stop,
                    hmho__mvqw.step):
                    arr.codes[uve__tbr] = fyyr__cuuur
            return impl_scalar
        if blf__ggv == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if blf__ggv == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(wjfdz__rzm)
                arr.codes[ind] = val.codes
            return impl_arr
        if wky__cmnk:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                hmho__mvqw = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                xpznx__axvl = 0
                for uve__tbr in range(hmho__mvqw.start, hmho__mvqw.stop,
                    hmho__mvqw.step):
                    mrtph__bnnj = bodo.utils.conversion.unbox_if_timestamp(val
                        [xpznx__axvl])
                    if mrtph__bnnj not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    yhu__awvwf = categories.get_loc(mrtph__bnnj)
                    arr.codes[uve__tbr] = yhu__awvwf
                    xpznx__axvl += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
