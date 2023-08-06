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
        ibsnd__pysy = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, ibsnd__pysy)


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
        vpnz__kulp, qkgzq__ztu = args
        bkg__jtt = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        bkg__jtt.left = vpnz__kulp
        bkg__jtt.right = qkgzq__ztu
        context.nrt.incref(builder, signature.args[0], vpnz__kulp)
        context.nrt.incref(builder, signature.args[1], qkgzq__ztu)
        return bkg__jtt._getvalue()
    vlx__ivgv = IntervalArrayType(left)
    gcgt__hqd = vlx__ivgv(left, right)
    return gcgt__hqd, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    fxtol__auvv = []
    for wacf__gahaa in args:
        bwr__vlht = equiv_set.get_shape(wacf__gahaa)
        if bwr__vlht is not None:
            fxtol__auvv.append(bwr__vlht[0])
    if len(fxtol__auvv) > 1:
        equiv_set.insert_equiv(*fxtol__auvv)
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
    bkg__jtt = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, bkg__jtt.left)
    ovxrv__tieil = c.pyapi.from_native_value(typ.arr_type, bkg__jtt.left, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, bkg__jtt.right)
    umdp__jblh = c.pyapi.from_native_value(typ.arr_type, bkg__jtt.right, c.
        env_manager)
    cyfw__askxb = c.context.insert_const_string(c.builder.module, 'pandas')
    zmkv__azsa = c.pyapi.import_module_noblock(cyfw__askxb)
    keef__bumn = c.pyapi.object_getattr_string(zmkv__azsa, 'arrays')
    jipno__tkhm = c.pyapi.object_getattr_string(keef__bumn, 'IntervalArray')
    xrp__utgu = c.pyapi.call_method(jipno__tkhm, 'from_arrays', (
        ovxrv__tieil, umdp__jblh))
    c.pyapi.decref(ovxrv__tieil)
    c.pyapi.decref(umdp__jblh)
    c.pyapi.decref(zmkv__azsa)
    c.pyapi.decref(keef__bumn)
    c.pyapi.decref(jipno__tkhm)
    c.context.nrt.decref(c.builder, typ, val)
    return xrp__utgu


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    ovxrv__tieil = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, ovxrv__tieil).value
    c.pyapi.decref(ovxrv__tieil)
    umdp__jblh = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, umdp__jblh).value
    c.pyapi.decref(umdp__jblh)
    bkg__jtt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bkg__jtt.left = left
    bkg__jtt.right = right
    kxdme__splzj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bkg__jtt._getvalue(), is_error=kxdme__splzj)


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
