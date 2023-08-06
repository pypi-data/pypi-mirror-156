"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
import numba
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type

    def __len__(self):
        return len(self.tuple_typ)


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bsji__fvetm = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, bsji__fvetm)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"
    data_tuple = types.unliteral(data_tuple)
    null_values = types.unliteral(null_values)

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        fmcb__enwau = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        fmcb__enwau.data = data_tuple
        fmcb__enwau.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return fmcb__enwau._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    ajln__bess = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, ajln__bess.data)
    c.context.nrt.incref(c.builder, typ.null_typ, ajln__bess.null_values)
    gdm__beei = c.pyapi.from_native_value(typ.tuple_typ, ajln__bess.data, c
        .env_manager)
    pyq__okeaj = c.pyapi.from_native_value(typ.null_typ, ajln__bess.
        null_values, c.env_manager)
    tzfp__juc = c.context.get_constant(types.int64, len(typ.tuple_typ))
    zkulv__oud = c.pyapi.list_new(tzfp__juc)
    with cgutils.for_range(c.builder, tzfp__juc) as bjh__mdrfh:
        i = bjh__mdrfh.index
        jodgg__stog = c.pyapi.long_from_longlong(i)
        aoxg__txta = c.pyapi.object_getitem(pyq__okeaj, jodgg__stog)
        cenqq__ybq = c.pyapi.to_native_value(types.bool_, aoxg__txta).value
        with c.builder.if_else(cenqq__ybq) as (mhic__orv, kcfmb__ufxl):
            with mhic__orv:
                c.pyapi.list_setitem(zkulv__oud, i, c.pyapi.make_none())
            with kcfmb__ufxl:
                zeidh__frkgv = c.pyapi.object_getitem(gdm__beei, jodgg__stog)
                c.pyapi.list_setitem(zkulv__oud, i, zeidh__frkgv)
        c.pyapi.decref(jodgg__stog)
        c.pyapi.decref(aoxg__txta)
    pucks__lqes = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    aypwj__cnaye = c.pyapi.call_function_objargs(pucks__lqes, (zkulv__oud,))
    c.pyapi.decref(gdm__beei)
    c.pyapi.decref(pyq__okeaj)
    c.pyapi.decref(pucks__lqes)
    c.pyapi.decref(zkulv__oud)
    c.context.nrt.decref(c.builder, typ, val)
    return aypwj__cnaye


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    fmcb__enwau = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (fmcb__enwau.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    zxs__tlcmv = 'def impl(val1, val2):\n'
    zxs__tlcmv += '    data_tup1 = val1._data\n'
    zxs__tlcmv += '    null_tup1 = val1._null_values\n'
    zxs__tlcmv += '    data_tup2 = val2._data\n'
    zxs__tlcmv += '    null_tup2 = val2._null_values\n'
    orxwi__ercnx = val1._tuple_typ
    for i in range(len(orxwi__ercnx)):
        zxs__tlcmv += f'    null1_{i} = null_tup1[{i}]\n'
        zxs__tlcmv += f'    null2_{i} = null_tup2[{i}]\n'
        zxs__tlcmv += f'    data1_{i} = data_tup1[{i}]\n'
        zxs__tlcmv += f'    data2_{i} = data_tup2[{i}]\n'
        zxs__tlcmv += f'    if null1_{i} != null2_{i}:\n'
        zxs__tlcmv += '        return False\n'
        zxs__tlcmv += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        zxs__tlcmv += f'        return False\n'
    zxs__tlcmv += f'    return True\n'
    qxmxr__ojrp = {}
    exec(zxs__tlcmv, {}, qxmxr__ojrp)
    impl = qxmxr__ojrp['impl']
    return impl


@overload_method(NullableTupleType, '__hash__')
def nullable_tuple_hash(val):

    def impl(val):
        return _nullable_tuple_hash(val)
    return impl


_PyHASH_XXPRIME_1 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_2 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_5 = numba.cpython.hashing._PyHASH_XXPRIME_1


@numba.generated_jit(nopython=True)
def _nullable_tuple_hash(nullable_tup):
    zxs__tlcmv = 'def impl(nullable_tup):\n'
    zxs__tlcmv += '    data_tup = nullable_tup._data\n'
    zxs__tlcmv += '    null_tup = nullable_tup._null_values\n'
    zxs__tlcmv += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    zxs__tlcmv += '    acc = _PyHASH_XXPRIME_5\n'
    orxwi__ercnx = nullable_tup._tuple_typ
    for i in range(len(orxwi__ercnx)):
        zxs__tlcmv += f'    null_val_{i} = null_tup[{i}]\n'
        zxs__tlcmv += f'    null_lane_{i} = hash(null_val_{i})\n'
        zxs__tlcmv += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        zxs__tlcmv += '        return -1\n'
        zxs__tlcmv += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        zxs__tlcmv += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        zxs__tlcmv += '    acc *= _PyHASH_XXPRIME_1\n'
        zxs__tlcmv += f'    if not null_val_{i}:\n'
        zxs__tlcmv += f'        lane_{i} = hash(data_tup[{i}])\n'
        zxs__tlcmv += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        zxs__tlcmv += f'            return -1\n'
        zxs__tlcmv += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        zxs__tlcmv += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        zxs__tlcmv += '        acc *= _PyHASH_XXPRIME_1\n'
    zxs__tlcmv += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    zxs__tlcmv += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    zxs__tlcmv += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    zxs__tlcmv += '    return numba.cpython.hashing.process_return(acc)\n'
    qxmxr__ojrp = {}
    exec(zxs__tlcmv, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, qxmxr__ojrp)
    impl = qxmxr__ojrp['impl']
    return impl
