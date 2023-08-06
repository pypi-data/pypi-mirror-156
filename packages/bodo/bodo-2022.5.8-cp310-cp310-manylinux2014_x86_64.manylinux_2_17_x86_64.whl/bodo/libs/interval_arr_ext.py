"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qvwh__gozaf = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, qvwh__gozaf)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        pwjxy__fbwmc, plk__ddq = args
        kxlnv__cwuz = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        kxlnv__cwuz.left = pwjxy__fbwmc
        kxlnv__cwuz.right = plk__ddq
        context.nrt.incref(builder, signature.args[0], pwjxy__fbwmc)
        context.nrt.incref(builder, signature.args[1], plk__ddq)
        return kxlnv__cwuz._getvalue()
    uppv__gdth = IntervalArrayType(left)
    gmvc__tuf = uppv__gdth(left, right)
    return gmvc__tuf, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    mfq__qzap = []
    for pjdi__swqzt in args:
        djpk__axh = equiv_set.get_shape(pjdi__swqzt)
        if djpk__axh is not None:
            mfq__qzap.append(djpk__axh[0])
    if len(mfq__qzap) > 1:
        equiv_set.insert_equiv(*mfq__qzap)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    kxlnv__cwuz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, kxlnv__cwuz.left)
    zwyp__fog = c.pyapi.from_native_value(typ.arr_type, kxlnv__cwuz.left, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, kxlnv__cwuz.right)
    acw__knpt = c.pyapi.from_native_value(typ.arr_type, kxlnv__cwuz.right,
        c.env_manager)
    tswf__bdi = c.context.insert_const_string(c.builder.module, 'pandas')
    ehwh__jesg = c.pyapi.import_module_noblock(tswf__bdi)
    wvhg__ahhcd = c.pyapi.object_getattr_string(ehwh__jesg, 'arrays')
    heka__bqi = c.pyapi.object_getattr_string(wvhg__ahhcd, 'IntervalArray')
    jpmlg__fdqe = c.pyapi.call_method(heka__bqi, 'from_arrays', (zwyp__fog,
        acw__knpt))
    c.pyapi.decref(zwyp__fog)
    c.pyapi.decref(acw__knpt)
    c.pyapi.decref(ehwh__jesg)
    c.pyapi.decref(wvhg__ahhcd)
    c.pyapi.decref(heka__bqi)
    c.context.nrt.decref(c.builder, typ, val)
    return jpmlg__fdqe


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    zwyp__fog = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, zwyp__fog).value
    c.pyapi.decref(zwyp__fog)
    acw__knpt = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, acw__knpt).value
    c.pyapi.decref(acw__knpt)
    kxlnv__cwuz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kxlnv__cwuz.left = left
    kxlnv__cwuz.right = right
    xjfy__qult = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kxlnv__cwuz._getvalue(), is_error=xjfy__qult)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
