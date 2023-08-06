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
        rhc__vsq = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, rhc__vsq)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[zivn__bgxbj].values) for
        zivn__bgxbj in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (ccrsz__oed) for ccrsz__oed in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    vjrb__rvijf = c.context.insert_const_string(c.builder.module, 'pandas')
    wyz__ool = c.pyapi.import_module_noblock(vjrb__rvijf)
    lmrh__mqk = c.pyapi.object_getattr_string(wyz__ool, 'MultiIndex')
    qbli__rgg = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), qbli__rgg
        .data)
    tdn__dvgsc = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        qbli__rgg.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), qbli__rgg.names
        )
    mbt__ubcs = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        qbli__rgg.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, qbli__rgg.name)
    dffd__cxpxo = c.pyapi.from_native_value(typ.name_typ, qbli__rgg.name, c
        .env_manager)
    wpt__kqcfh = c.pyapi.borrow_none()
    hhma__vggfj = c.pyapi.call_method(lmrh__mqk, 'from_arrays', (tdn__dvgsc,
        wpt__kqcfh, mbt__ubcs))
    c.pyapi.object_setattr_string(hhma__vggfj, 'name', dffd__cxpxo)
    c.pyapi.decref(tdn__dvgsc)
    c.pyapi.decref(mbt__ubcs)
    c.pyapi.decref(dffd__cxpxo)
    c.pyapi.decref(wyz__ool)
    c.pyapi.decref(lmrh__mqk)
    c.context.nrt.decref(c.builder, typ, val)
    return hhma__vggfj


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    khwr__oabhr = []
    qnpy__ume = []
    for zivn__bgxbj in range(typ.nlevels):
        fzzsk__sfcp = c.pyapi.unserialize(c.pyapi.serialize_object(zivn__bgxbj)
            )
        hipp__xdf = c.pyapi.call_method(val, 'get_level_values', (fzzsk__sfcp,)
            )
        vxs__iht = c.pyapi.object_getattr_string(hipp__xdf, 'values')
        c.pyapi.decref(hipp__xdf)
        c.pyapi.decref(fzzsk__sfcp)
        qreu__vtzg = c.pyapi.to_native_value(typ.array_types[zivn__bgxbj],
            vxs__iht).value
        khwr__oabhr.append(qreu__vtzg)
        qnpy__ume.append(vxs__iht)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, khwr__oabhr)
    else:
        data = cgutils.pack_struct(c.builder, khwr__oabhr)
    mbt__ubcs = c.pyapi.object_getattr_string(val, 'names')
    fhpw__mwnu = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    kooub__kfqpd = c.pyapi.call_function_objargs(fhpw__mwnu, (mbt__ubcs,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), kooub__kfqpd
        ).value
    dffd__cxpxo = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, dffd__cxpxo).value
    qbli__rgg = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qbli__rgg.data = data
    qbli__rgg.names = names
    qbli__rgg.name = name
    for vxs__iht in qnpy__ume:
        c.pyapi.decref(vxs__iht)
    c.pyapi.decref(mbt__ubcs)
    c.pyapi.decref(fhpw__mwnu)
    c.pyapi.decref(kooub__kfqpd)
    c.pyapi.decref(dffd__cxpxo)
    return NativeValue(qbli__rgg._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    dvxvq__dnsy = 'pandas.MultiIndex.from_product'
    nrknd__kkfo = dict(sortorder=sortorder)
    cgyul__xtn = dict(sortorder=None)
    check_unsupported_args(dvxvq__dnsy, nrknd__kkfo, cgyul__xtn,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{dvxvq__dnsy}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{dvxvq__dnsy}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{dvxvq__dnsy}: iterables and names must be of the same length.')


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
    kepza__htn = MultiIndexType(array_types, names_typ)
    qzwnb__lohf = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, qzwnb__lohf, kepza__htn)
    yqiex__mzurf = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{qzwnb__lohf}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    ojtkx__xacgx = {}
    exec(yqiex__mzurf, globals(), ojtkx__xacgx)
    mgip__thshy = ojtkx__xacgx['impl']
    return mgip__thshy


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        fvgb__xxqh, phz__jumhk, klxn__rjry = args
        iiq__zalcu = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        iiq__zalcu.data = fvgb__xxqh
        iiq__zalcu.names = phz__jumhk
        iiq__zalcu.name = klxn__rjry
        context.nrt.incref(builder, signature.args[0], fvgb__xxqh)
        context.nrt.incref(builder, signature.args[1], phz__jumhk)
        context.nrt.incref(builder, signature.args[2], klxn__rjry)
        return iiq__zalcu._getvalue()
    ziv__qqqvg = MultiIndexType(data.types, names.types, name)
    return ziv__qqqvg(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        mbubs__cuna = len(I.array_types)
        yqiex__mzurf = 'def impl(I, ind):\n'
        yqiex__mzurf += '  data = I._data\n'
        yqiex__mzurf += (
            '  return init_multi_index(({},), I._names, I._name)\n'.format(
            ', '.join(f'ensure_contig_if_np(data[{zivn__bgxbj}][ind])' for
            zivn__bgxbj in range(mbubs__cuna))))
        ojtkx__xacgx = {}
        exec(yqiex__mzurf, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, ojtkx__xacgx)
        mgip__thshy = ojtkx__xacgx['impl']
        return mgip__thshy


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    dmqf__mfoi, nzfo__ayz = sig.args
    if dmqf__mfoi != nzfo__ayz:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
