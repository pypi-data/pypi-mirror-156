"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.ArrayCompatible):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zizq__kver = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, zizq__kver)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[hpbc__qeka].values) for
        hpbc__qeka in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (pzptd__xroap) for pzptd__xroap in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    lfydz__ltrpe = c.context.insert_const_string(c.builder.module, 'pandas')
    lsrce__gdax = c.pyapi.import_module_noblock(lfydz__ltrpe)
    rqqr__pljw = c.pyapi.object_getattr_string(lsrce__gdax, 'MultiIndex')
    otw__iho = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), otw__iho.data
        )
    jeey__uopg = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        otw__iho.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), otw__iho.names)
    dcw__ifv = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        otw__iho.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, otw__iho.name)
    qbaif__mzz = c.pyapi.from_native_value(typ.name_typ, otw__iho.name, c.
        env_manager)
    ufey__pzuf = c.pyapi.borrow_none()
    offks__lvvv = c.pyapi.call_method(rqqr__pljw, 'from_arrays', (
        jeey__uopg, ufey__pzuf, dcw__ifv))
    c.pyapi.object_setattr_string(offks__lvvv, 'name', qbaif__mzz)
    c.pyapi.decref(jeey__uopg)
    c.pyapi.decref(dcw__ifv)
    c.pyapi.decref(qbaif__mzz)
    c.pyapi.decref(lsrce__gdax)
    c.pyapi.decref(rqqr__pljw)
    c.context.nrt.decref(c.builder, typ, val)
    return offks__lvvv


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    narv__nxo = []
    xac__clga = []
    for hpbc__qeka in range(typ.nlevels):
        nhm__wrt = c.pyapi.unserialize(c.pyapi.serialize_object(hpbc__qeka))
        xnzmr__zatf = c.pyapi.call_method(val, 'get_level_values', (nhm__wrt,))
        fzxf__vjey = c.pyapi.object_getattr_string(xnzmr__zatf, 'values')
        c.pyapi.decref(xnzmr__zatf)
        c.pyapi.decref(nhm__wrt)
        lubi__wiks = c.pyapi.to_native_value(typ.array_types[hpbc__qeka],
            fzxf__vjey).value
        narv__nxo.append(lubi__wiks)
        xac__clga.append(fzxf__vjey)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, narv__nxo)
    else:
        data = cgutils.pack_struct(c.builder, narv__nxo)
    dcw__ifv = c.pyapi.object_getattr_string(val, 'names')
    rbf__eytz = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    cvn__ktaer = c.pyapi.call_function_objargs(rbf__eytz, (dcw__ifv,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), cvn__ktaer
        ).value
    qbaif__mzz = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qbaif__mzz).value
    otw__iho = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    otw__iho.data = data
    otw__iho.names = names
    otw__iho.name = name
    for fzxf__vjey in xac__clga:
        c.pyapi.decref(fzxf__vjey)
    c.pyapi.decref(dcw__ifv)
    c.pyapi.decref(rbf__eytz)
    c.pyapi.decref(cvn__ktaer)
    c.pyapi.decref(qbaif__mzz)
    return NativeValue(otw__iho._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    lbsof__judis = 'pandas.MultiIndex.from_product'
    nmpge__pnch = dict(sortorder=sortorder)
    jjzt__obl = dict(sortorder=None)
    check_unsupported_args(lbsof__judis, nmpge__pnch, jjzt__obl,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{lbsof__judis}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{lbsof__judis}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{lbsof__judis}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    askyv__dlq = MultiIndexType(array_types, names_typ)
    djmkf__lhzed = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, djmkf__lhzed, askyv__dlq)
    yvl__phu = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{djmkf__lhzed}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    hfwj__tezld = {}
    exec(yvl__phu, globals(), hfwj__tezld)
    ebqh__itpkz = hfwj__tezld['impl']
    return ebqh__itpkz


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        zgj__deypz, rsy__zanj, righc__qin = args
        pouef__luf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        pouef__luf.data = zgj__deypz
        pouef__luf.names = rsy__zanj
        pouef__luf.name = righc__qin
        context.nrt.incref(builder, signature.args[0], zgj__deypz)
        context.nrt.incref(builder, signature.args[1], rsy__zanj)
        context.nrt.incref(builder, signature.args[2], righc__qin)
        return pouef__luf._getvalue()
    jckd__mxuko = MultiIndexType(data.types, names.types, name)
    return jckd__mxuko(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        asnh__wnzmi = len(I.array_types)
        yvl__phu = 'def impl(I, ind):\n'
        yvl__phu += '  data = I._data\n'
        yvl__phu += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{hpbc__qeka}][ind])' for hpbc__qeka in
            range(asnh__wnzmi))))
        hfwj__tezld = {}
        exec(yvl__phu, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, hfwj__tezld)
        ebqh__itpkz = hfwj__tezld['impl']
        return ebqh__itpkz


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    lznm__oll, reuhn__ryqg = sig.args
    if lznm__oll != reuhn__ryqg:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
