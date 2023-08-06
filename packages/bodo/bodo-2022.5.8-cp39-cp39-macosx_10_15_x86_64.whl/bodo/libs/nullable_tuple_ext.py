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
        fvsix__ekns = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, fvsix__ekns)


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
        syw__opyhk = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        syw__opyhk.data = data_tuple
        syw__opyhk.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return syw__opyhk._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    ejc__kxe = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.tuple_typ, ejc__kxe.data)
    c.context.nrt.incref(c.builder, typ.null_typ, ejc__kxe.null_values)
    xcjfv__oytt = c.pyapi.from_native_value(typ.tuple_typ, ejc__kxe.data, c
        .env_manager)
    yye__dmj = c.pyapi.from_native_value(typ.null_typ, ejc__kxe.null_values,
        c.env_manager)
    xuq__edix = c.context.get_constant(types.int64, len(typ.tuple_typ))
    zitn__hfg = c.pyapi.list_new(xuq__edix)
    with cgutils.for_range(c.builder, xuq__edix) as uoth__zrh:
        i = uoth__zrh.index
        mjkgf__eom = c.pyapi.long_from_longlong(i)
        nnv__azbn = c.pyapi.object_getitem(yye__dmj, mjkgf__eom)
        tzfej__nfajm = c.pyapi.to_native_value(types.bool_, nnv__azbn).value
        with c.builder.if_else(tzfej__nfajm) as (hnojv__chys, fdl__ponon):
            with hnojv__chys:
                c.pyapi.list_setitem(zitn__hfg, i, c.pyapi.make_none())
            with fdl__ponon:
                yig__wdvn = c.pyapi.object_getitem(xcjfv__oytt, mjkgf__eom)
                c.pyapi.list_setitem(zitn__hfg, i, yig__wdvn)
        c.pyapi.decref(mjkgf__eom)
        c.pyapi.decref(nnv__azbn)
    uvw__tbvf = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    hgpkg__majvo = c.pyapi.call_function_objargs(uvw__tbvf, (zitn__hfg,))
    c.pyapi.decref(xcjfv__oytt)
    c.pyapi.decref(yye__dmj)
    c.pyapi.decref(uvw__tbvf)
    c.pyapi.decref(zitn__hfg)
    c.context.nrt.decref(c.builder, typ, val)
    return hgpkg__majvo


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
    syw__opyhk = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (syw__opyhk.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    tbh__jnckr = 'def impl(val1, val2):\n'
    tbh__jnckr += '    data_tup1 = val1._data\n'
    tbh__jnckr += '    null_tup1 = val1._null_values\n'
    tbh__jnckr += '    data_tup2 = val2._data\n'
    tbh__jnckr += '    null_tup2 = val2._null_values\n'
    nwkem__wbrzm = val1._tuple_typ
    for i in range(len(nwkem__wbrzm)):
        tbh__jnckr += f'    null1_{i} = null_tup1[{i}]\n'
        tbh__jnckr += f'    null2_{i} = null_tup2[{i}]\n'
        tbh__jnckr += f'    data1_{i} = data_tup1[{i}]\n'
        tbh__jnckr += f'    data2_{i} = data_tup2[{i}]\n'
        tbh__jnckr += f'    if null1_{i} != null2_{i}:\n'
        tbh__jnckr += '        return False\n'
        tbh__jnckr += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        tbh__jnckr += f'        return False\n'
    tbh__jnckr += f'    return True\n'
    onr__naxtn = {}
    exec(tbh__jnckr, {}, onr__naxtn)
    impl = onr__naxtn['impl']
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
    tbh__jnckr = 'def impl(nullable_tup):\n'
    tbh__jnckr += '    data_tup = nullable_tup._data\n'
    tbh__jnckr += '    null_tup = nullable_tup._null_values\n'
    tbh__jnckr += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    tbh__jnckr += '    acc = _PyHASH_XXPRIME_5\n'
    nwkem__wbrzm = nullable_tup._tuple_typ
    for i in range(len(nwkem__wbrzm)):
        tbh__jnckr += f'    null_val_{i} = null_tup[{i}]\n'
        tbh__jnckr += f'    null_lane_{i} = hash(null_val_{i})\n'
        tbh__jnckr += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        tbh__jnckr += '        return -1\n'
        tbh__jnckr += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        tbh__jnckr += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        tbh__jnckr += '    acc *= _PyHASH_XXPRIME_1\n'
        tbh__jnckr += f'    if not null_val_{i}:\n'
        tbh__jnckr += f'        lane_{i} = hash(data_tup[{i}])\n'
        tbh__jnckr += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        tbh__jnckr += f'            return -1\n'
        tbh__jnckr += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        tbh__jnckr += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        tbh__jnckr += '        acc *= _PyHASH_XXPRIME_1\n'
    tbh__jnckr += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    tbh__jnckr += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    tbh__jnckr += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    tbh__jnckr += '    return numba.cpython.hashing.process_return(acc)\n'
    onr__naxtn = {}
    exec(tbh__jnckr, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, onr__naxtn)
    impl = onr__naxtn['impl']
    return impl
