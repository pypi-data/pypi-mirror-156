"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_none, is_overload_true, to_str_arr_if_dict_array


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            uuapn__rju = 0
            ntvi__ogtyb = []
            for i in range(usecols[-1] + 1):
                if i == usecols[uuapn__rju]:
                    ntvi__ogtyb.append(arrs[uuapn__rju])
                    uuapn__rju += 1
                else:
                    ntvi__ogtyb.append(None)
            for odr__tudry in range(usecols[-1] + 1, num_arrs):
                ntvi__ogtyb.append(None)
            self.arrays = ntvi__ogtyb
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((ozh__fzm == xvhmi__ajek).all() for ozh__fzm,
            xvhmi__ajek in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        xwouh__zaz = len(self.arrays)
        totn__ipgo = dict(zip(range(xwouh__zaz), self.arrays))
        df = pd.DataFrame(totn__ipgo, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        cqgfp__lsea = []
        gehma__xwy = []
        ovbzs__oot = {}
        fuh__jai = {}
        ulv__bce = defaultdict(int)
        tqgo__siih = defaultdict(list)
        if not has_runtime_cols:
            for i, zghu__waneq in enumerate(arr_types):
                if zghu__waneq not in ovbzs__oot:
                    cqbl__yqbel = len(ovbzs__oot)
                    ovbzs__oot[zghu__waneq] = cqbl__yqbel
                    fuh__jai[cqbl__yqbel] = zghu__waneq
                cpved__beefd = ovbzs__oot[zghu__waneq]
                cqgfp__lsea.append(cpved__beefd)
                gehma__xwy.append(ulv__bce[cpved__beefd])
                ulv__bce[cpved__beefd] += 1
                tqgo__siih[cpved__beefd].append(i)
        self.block_nums = cqgfp__lsea
        self.block_offsets = gehma__xwy
        self.type_to_blk = ovbzs__oot
        self.blk_to_type = fuh__jai
        self.block_to_arr_ind = tqgo__siih
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(arr) for arr in val.arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            awjcn__zdqdi = [(f'block_{i}', types.List(zghu__waneq)) for i,
                zghu__waneq in enumerate(fe_type.arr_types)]
        else:
            awjcn__zdqdi = [(f'block_{cpved__beefd}', types.List(
                zghu__waneq)) for zghu__waneq, cpved__beefd in fe_type.
                type_to_blk.items()]
        awjcn__zdqdi.append(('parent', types.pyobject))
        awjcn__zdqdi.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, awjcn__zdqdi)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    omkox__xpe = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    qpn__iqe = c.pyapi.make_none()
    umnlu__cqhe = c.context.get_constant(types.int64, 0)
    qfrum__tdjd = cgutils.alloca_once_value(c.builder, umnlu__cqhe)
    for zghu__waneq, cpved__beefd in typ.type_to_blk.items():
        jssw__ibaf = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[cpved__beefd]))
        odr__tudry, nqzw__wvsth = ListInstance.allocate_ex(c.context, c.
            builder, types.List(zghu__waneq), jssw__ibaf)
        nqzw__wvsth.size = jssw__ibaf
        lmog__kqg = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            cpved__beefd], dtype=np.int64))
        vcbv__rvv = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, lmog__kqg)
        with cgutils.for_range(c.builder, jssw__ibaf) as bvp__ati:
            i = bvp__ati.index
            fyt__eln = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), vcbv__rvv, i)
            qejgf__tvqtl = c.pyapi.long_from_longlong(fyt__eln)
            ddhwr__xira = c.pyapi.object_getitem(omkox__xpe, qejgf__tvqtl)
            bckcn__uhdr = c.builder.icmp_unsigned('==', ddhwr__xira, qpn__iqe)
            with c.builder.if_else(bckcn__uhdr) as (dlhmo__pxxv, sjgir__xptq):
                with dlhmo__pxxv:
                    xmpd__xmtmd = c.context.get_constant_null(zghu__waneq)
                    nqzw__wvsth.inititem(i, xmpd__xmtmd, incref=False)
                with sjgir__xptq:
                    vecu__rekf = c.pyapi.call_method(ddhwr__xira, '__len__', ()
                        )
                    hvyd__rpit = c.pyapi.long_as_longlong(vecu__rekf)
                    c.builder.store(hvyd__rpit, qfrum__tdjd)
                    c.pyapi.decref(vecu__rekf)
                    arr = c.pyapi.to_native_value(zghu__waneq, ddhwr__xira
                        ).value
                    nqzw__wvsth.inititem(i, arr, incref=False)
            c.pyapi.decref(ddhwr__xira)
            c.pyapi.decref(qejgf__tvqtl)
        setattr(table, f'block_{cpved__beefd}', nqzw__wvsth.value)
    table.len = c.builder.load(qfrum__tdjd)
    c.pyapi.decref(omkox__xpe)
    c.pyapi.decref(qpn__iqe)
    jaei__upuk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=jaei__upuk)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        qanxg__dbbxc = c.context.get_constant(types.int64, 0)
        for i, zghu__waneq in enumerate(typ.arr_types):
            ntvi__ogtyb = getattr(table, f'block_{i}')
            soww__poun = ListInstance(c.context, c.builder, types.List(
                zghu__waneq), ntvi__ogtyb)
            qanxg__dbbxc = c.builder.add(qanxg__dbbxc, soww__poun.size)
        iqhho__vmpqs = c.pyapi.list_new(qanxg__dbbxc)
        axtg__ybp = c.context.get_constant(types.int64, 0)
        for i, zghu__waneq in enumerate(typ.arr_types):
            ntvi__ogtyb = getattr(table, f'block_{i}')
            soww__poun = ListInstance(c.context, c.builder, types.List(
                zghu__waneq), ntvi__ogtyb)
            with cgutils.for_range(c.builder, soww__poun.size) as bvp__ati:
                i = bvp__ati.index
                arr = soww__poun.getitem(i)
                c.context.nrt.incref(c.builder, zghu__waneq, arr)
                idx = c.builder.add(axtg__ybp, i)
                c.pyapi.list_setitem(iqhho__vmpqs, idx, c.pyapi.
                    from_native_value(zghu__waneq, arr, c.env_manager))
            axtg__ybp = c.builder.add(axtg__ybp, soww__poun.size)
        bvq__fiyr = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        wpkg__xwv = c.pyapi.call_function_objargs(bvq__fiyr, (iqhho__vmpqs,))
        c.pyapi.decref(bvq__fiyr)
        c.pyapi.decref(iqhho__vmpqs)
        c.context.nrt.decref(c.builder, typ, val)
        return wpkg__xwv
    iqhho__vmpqs = c.pyapi.list_new(c.context.get_constant(types.int64, len
        (typ.arr_types)))
    mdlp__vxl = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for zghu__waneq, cpved__beefd in typ.type_to_blk.items():
        ntvi__ogtyb = getattr(table, f'block_{cpved__beefd}')
        soww__poun = ListInstance(c.context, c.builder, types.List(
            zghu__waneq), ntvi__ogtyb)
        lmog__kqg = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            cpved__beefd], dtype=np.int64))
        vcbv__rvv = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, lmog__kqg)
        with cgutils.for_range(c.builder, soww__poun.size) as bvp__ati:
            i = bvp__ati.index
            fyt__eln = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), vcbv__rvv, i)
            arr = soww__poun.getitem(i)
            mmhiq__zqai = cgutils.alloca_once_value(c.builder, arr)
            ncahp__ywenz = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(zghu__waneq))
            is_null = is_ll_eq(c.builder, mmhiq__zqai, ncahp__ywenz)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (dlhmo__pxxv, sjgir__xptq):
                with dlhmo__pxxv:
                    qpn__iqe = c.pyapi.make_none()
                    c.pyapi.list_setitem(iqhho__vmpqs, fyt__eln, qpn__iqe)
                with sjgir__xptq:
                    ddhwr__xira = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, mdlp__vxl)
                        ) as (egnjf__exjj, tbzdz__jds):
                        with egnjf__exjj:
                            awmoq__qza = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                fyt__eln, zghu__waneq)
                            c.builder.store(awmoq__qza, ddhwr__xira)
                        with tbzdz__jds:
                            c.context.nrt.incref(c.builder, zghu__waneq, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                zghu__waneq, arr, c.env_manager), ddhwr__xira)
                    c.pyapi.list_setitem(iqhho__vmpqs, fyt__eln, c.builder.
                        load(ddhwr__xira))
    bvq__fiyr = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    wpkg__xwv = c.pyapi.call_function_objargs(bvq__fiyr, (iqhho__vmpqs,))
    c.pyapi.decref(bvq__fiyr)
    c.pyapi.decref(iqhho__vmpqs)
    c.context.nrt.decref(c.builder, typ, val)
    return wpkg__xwv


@lower_builtin(len, TableType)
def table_len_lower(context, builder, sig, args):
    impl = table_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@lower_getattr(TableType, 'shape')
def lower_table_shape(context, builder, typ, val):
    impl = table_shape_overload(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        uypq__wunzc = context.get_constant(types.int64, 0)
        for i, zghu__waneq in enumerate(table_type.arr_types):
            ntvi__ogtyb = getattr(table, f'block_{i}')
            soww__poun = ListInstance(context, builder, types.List(
                zghu__waneq), ntvi__ogtyb)
            uypq__wunzc = builder.add(uypq__wunzc, soww__poun.size)
        return uypq__wunzc
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    cpved__beefd = table_type.block_nums[col_ind]
    vnaw__qbf = table_type.block_offsets[col_ind]
    ntvi__ogtyb = getattr(table, f'block_{cpved__beefd}')
    soww__poun = ListInstance(context, builder, types.List(arr_type),
        ntvi__ogtyb)
    arr = soww__poun.getitem(vnaw__qbf)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, odr__tudry = args
        arr = get_table_data_codegen(context, builder, table_arg, col_ind,
            table_type)
        return impl_ret_borrowed(context, builder, arr_type, arr)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType
        ), 'Can only delete columns from a table'
    assert isinstance(ind_typ, types.TypeRef) and isinstance(ind_typ.
        instance_type, MetaType), 'ind_typ must be a typeref for a meta type'
    xsjk__pvfrx = list(ind_typ.instance_type.meta)
    gwcxz__nvp = defaultdict(list)
    for ind in xsjk__pvfrx:
        gwcxz__nvp[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, odr__tudry = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for cpved__beefd, eltr__dkk in gwcxz__nvp.items():
            arr_type = table_type.blk_to_type[cpved__beefd]
            ntvi__ogtyb = getattr(table, f'block_{cpved__beefd}')
            soww__poun = ListInstance(context, builder, types.List(arr_type
                ), ntvi__ogtyb)
            xmpd__xmtmd = context.get_constant_null(arr_type)
            if len(eltr__dkk) == 1:
                vnaw__qbf = eltr__dkk[0]
                arr = soww__poun.getitem(vnaw__qbf)
                context.nrt.decref(builder, arr_type, arr)
                soww__poun.inititem(vnaw__qbf, xmpd__xmtmd, incref=False)
            else:
                jssw__ibaf = context.get_constant(types.int64, len(eltr__dkk))
                mln__crst = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(eltr__dkk, dtype=
                    np.int64))
                zem__osils = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, mln__crst)
                with cgutils.for_range(builder, jssw__ibaf) as bvp__ati:
                    i = bvp__ati.index
                    vnaw__qbf = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        zem__osils, i)
                    arr = soww__poun.getitem(vnaw__qbf)
                    context.nrt.decref(builder, arr_type, arr)
                    soww__poun.inititem(vnaw__qbf, xmpd__xmtmd, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    umnlu__cqhe = context.get_constant(types.int64, 0)
    bxjm__oukp = context.get_constant(types.int64, 1)
    gpvec__zzdf = arr_type not in in_table_type.type_to_blk
    for zghu__waneq, cpved__beefd in out_table_type.type_to_blk.items():
        if zghu__waneq in in_table_type.type_to_blk:
            cjti__nclmu = in_table_type.type_to_blk[zghu__waneq]
            nqzw__wvsth = ListInstance(context, builder, types.List(
                zghu__waneq), getattr(in_table, f'block_{cjti__nclmu}'))
            context.nrt.incref(builder, types.List(zghu__waneq),
                nqzw__wvsth.value)
            setattr(out_table, f'block_{cpved__beefd}', nqzw__wvsth.value)
    if gpvec__zzdf:
        odr__tudry, nqzw__wvsth = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), bxjm__oukp)
        nqzw__wvsth.size = bxjm__oukp
        nqzw__wvsth.inititem(umnlu__cqhe, arr_arg, incref=True)
        cpved__beefd = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{cpved__beefd}', nqzw__wvsth.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        cpved__beefd = out_table_type.type_to_blk[arr_type]
        nqzw__wvsth = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{cpved__beefd}'))
        if is_new_col:
            n = nqzw__wvsth.size
            lepek__hfqp = builder.add(n, bxjm__oukp)
            nqzw__wvsth.resize(lepek__hfqp)
            nqzw__wvsth.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            ohvwu__exje = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            nqzw__wvsth.setitem(ohvwu__exje, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            ohvwu__exje = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = nqzw__wvsth.size
            lepek__hfqp = builder.add(n, bxjm__oukp)
            nqzw__wvsth.resize(lepek__hfqp)
            context.nrt.incref(builder, arr_type, nqzw__wvsth.getitem(
                ohvwu__exje))
            nqzw__wvsth.move(builder.add(ohvwu__exje, bxjm__oukp),
                ohvwu__exje, builder.sub(n, ohvwu__exje))
            nqzw__wvsth.setitem(ohvwu__exje, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ulf__nbll = in_table_type.arr_types[col_ind]
    if ulf__nbll in out_table_type.type_to_blk:
        cpved__beefd = out_table_type.type_to_blk[ulf__nbll]
        tkl__xtmj = getattr(out_table, f'block_{cpved__beefd}')
        lmxv__aone = types.List(ulf__nbll)
        ohvwu__exje = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        jsb__cmz = lmxv__aone.dtype(lmxv__aone, types.intp)
        iswzp__dahmt = context.compile_internal(builder, lambda lst, i: lst
            .pop(i), jsb__cmz, (tkl__xtmj, ohvwu__exje))
        context.nrt.decref(builder, ulf__nbll, iswzp__dahmt)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    amtcd__haur = list(table.arr_types)
    if ind == len(amtcd__haur):
        gpnty__gap = None
        amtcd__haur.append(arr_type)
    else:
        gpnty__gap = table.arr_types[ind]
        amtcd__haur[ind] = arr_type
    izrn__aapo = TableType(tuple(amtcd__haur))
    gpu__yja = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': izrn__aapo}
    kwy__nolym = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    kwy__nolym += f'  T2 = init_table(out_table_typ, False)\n'
    kwy__nolym += f'  T2 = set_table_len(T2, len(table))\n'
    kwy__nolym += f'  T2 = set_table_parent(T2, table)\n'
    for typ, cpved__beefd in izrn__aapo.type_to_blk.items():
        if typ in table.type_to_blk:
            czc__qitev = table.type_to_blk[typ]
            kwy__nolym += (
                f'  arr_list_{cpved__beefd} = get_table_block(table, {czc__qitev})\n'
                )
            kwy__nolym += f"""  out_arr_list_{cpved__beefd} = alloc_list_like(arr_list_{cpved__beefd}, {len(izrn__aapo.block_to_arr_ind[cpved__beefd])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[czc__qitev]
                ) & used_cols:
                kwy__nolym += (
                    f'  for i in range(len(arr_list_{cpved__beefd})):\n')
                if typ not in (gpnty__gap, arr_type):
                    kwy__nolym += f"""    out_arr_list_{cpved__beefd}[i] = arr_list_{cpved__beefd}[i]
"""
                else:
                    qcnyy__oyh = table.block_to_arr_ind[czc__qitev]
                    wkuec__enqdi = np.empty(len(qcnyy__oyh), np.int64)
                    kxlz__fmkiv = False
                    for nzi__sxso, fyt__eln in enumerate(qcnyy__oyh):
                        if fyt__eln != ind:
                            nrte__uje = izrn__aapo.block_offsets[fyt__eln]
                        else:
                            nrte__uje = -1
                            kxlz__fmkiv = True
                        wkuec__enqdi[nzi__sxso] = nrte__uje
                    gpu__yja[f'out_idxs_{cpved__beefd}'] = np.array(
                        wkuec__enqdi, np.int64)
                    kwy__nolym += f'    out_idx = out_idxs_{cpved__beefd}[i]\n'
                    if kxlz__fmkiv:
                        kwy__nolym += f'    if out_idx == -1:\n'
                        kwy__nolym += f'      continue\n'
                    kwy__nolym += f"""    out_arr_list_{cpved__beefd}[out_idx] = arr_list_{cpved__beefd}[i]
"""
            if typ == arr_type and not is_null:
                kwy__nolym += f"""  out_arr_list_{cpved__beefd}[{izrn__aapo.block_offsets[ind]}] = arr
"""
        else:
            gpu__yja[f'arr_list_typ_{cpved__beefd}'] = types.List(arr_type)
            kwy__nolym += f"""  out_arr_list_{cpved__beefd} = alloc_list_like(arr_list_typ_{cpved__beefd}, 1, False)
"""
            if not is_null:
                kwy__nolym += f'  out_arr_list_{cpved__beefd}[0] = arr\n'
        kwy__nolym += (
            f'  T2 = set_table_block(T2, out_arr_list_{cpved__beefd}, {cpved__beefd})\n'
            )
    kwy__nolym += f'  return T2\n'
    cmtfv__uxq = {}
    exec(kwy__nolym, gpu__yja, cmtfv__uxq)
    return cmtfv__uxq['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        fid__ugay = None
    else:
        fid__ugay = set(used_cols.instance_type.meta)
    fsw__eyy = get_overload_const_int(ind)
    return generate_set_table_data_code(table, fsw__eyy, arr, fid__ugay)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    fsw__eyy = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        fid__ugay = None
    else:
        fid__ugay = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, fsw__eyy, arr_type,
        fid__ugay, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    jmva__pqmz = args[0]
    if equiv_set.has_shape(jmva__pqmz):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            jmva__pqmz)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    tnrau__jweq = []
    for zghu__waneq, cpved__beefd in table_type.type_to_blk.items():
        ibeg__jhd = len(table_type.block_to_arr_ind[cpved__beefd])
        nxo__paqh = []
        for i in range(ibeg__jhd):
            fyt__eln = table_type.block_to_arr_ind[cpved__beefd][i]
            nxo__paqh.append(pyval.arrays[fyt__eln])
        tnrau__jweq.append(context.get_constant_generic(builder, types.List
            (zghu__waneq), nxo__paqh))
    sla__tea = context.get_constant_null(types.pyobject)
    zukpj__aoqjy = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(tnrau__jweq + [sla__tea, zukpj__aoqjy])


@intrinsic
def init_table(typingctx, table_type, to_str_if_dict_t):
    out_table_type = table_type.instance_type if isinstance(table_type,
        types.TypeRef) else table_type
    assert isinstance(out_table_type, TableType
        ), 'table type or typeref expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        out_table_type = to_str_arr_if_dict_array(out_table_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(out_table_type)(context, builder)
        for zghu__waneq, cpved__beefd in out_table_type.type_to_blk.items():
            ryyqf__ghv = context.get_constant_null(types.List(zghu__waneq))
            setattr(table, f'block_{cpved__beefd}', ryyqf__ghv)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    hhih__gjka = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        hhih__gjka[typ.dtype] = i
    luag__znu = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(luag__znu, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        uazx__tvnsu, odr__tudry = args
        table = cgutils.create_struct_proxy(luag__znu)(context, builder)
        for zghu__waneq, cpved__beefd in luag__znu.type_to_blk.items():
            idx = hhih__gjka[zghu__waneq]
            ynlb__rpc = signature(types.List(zghu__waneq),
                tuple_of_lists_type, types.literal(idx))
            jfg__gyb = uazx__tvnsu, idx
            alb__ojq = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, ynlb__rpc, jfg__gyb)
            setattr(table, f'block_{cpved__beefd}', alb__ojq)
        return table._getvalue()
    sig = luag__znu(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    cpved__beefd = get_overload_const_int(blk_type)
    arr_type = None
    for zghu__waneq, xvhmi__ajek in table_type.type_to_blk.items():
        if xvhmi__ajek == cpved__beefd:
            arr_type = zghu__waneq
            break
    assert arr_type is not None, 'invalid table type block'
    fzqrq__hem = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        ntvi__ogtyb = getattr(table, f'block_{cpved__beefd}')
        return impl_ret_borrowed(context, builder, fzqrq__hem, ntvi__ogtyb)
    sig = fzqrq__hem(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, hvrlh__jaxsi = args
        cza__iqsu = context.get_python_api(builder)
        wbjf__hpqk = used_cols_typ == types.none
        if not wbjf__hpqk:
            ety__zebj = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), hvrlh__jaxsi)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for zghu__waneq, cpved__beefd in table_type.type_to_blk.items():
            jssw__ibaf = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[cpved__beefd]))
            lmog__kqg = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                cpved__beefd], dtype=np.int64))
            vcbv__rvv = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, lmog__kqg)
            ntvi__ogtyb = getattr(table, f'block_{cpved__beefd}')
            with cgutils.for_range(builder, jssw__ibaf) as bvp__ati:
                i = bvp__ati.index
                fyt__eln = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), vcbv__rvv, i
                    )
                ufceq__hemc = types.none(table_type, types.List(zghu__waneq
                    ), types.int64, types.int64)
                mzqw__ccus = table_arg, ntvi__ogtyb, i, fyt__eln
                if wbjf__hpqk:
                    ensure_column_unboxed_codegen(context, builder,
                        ufceq__hemc, mzqw__ccus)
                else:
                    mdnku__skj = ety__zebj.contains(fyt__eln)
                    with builder.if_then(mdnku__skj):
                        ensure_column_unboxed_codegen(context, builder,
                            ufceq__hemc, mzqw__ccus)
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, used_cols_typ)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t, arr_ind_t):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, gcxbg__lrd, tcyh__owx, djo__fafhy = args
    cza__iqsu = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    mdlp__vxl = cgutils.is_not_null(builder, table.parent)
    soww__poun = ListInstance(context, builder, sig.args[1], gcxbg__lrd)
    uoi__pvons = soww__poun.getitem(tcyh__owx)
    mmhiq__zqai = cgutils.alloca_once_value(builder, uoi__pvons)
    ncahp__ywenz = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, mmhiq__zqai, ncahp__ywenz)
    with builder.if_then(is_null):
        with builder.if_else(mdlp__vxl) as (dlhmo__pxxv, sjgir__xptq):
            with dlhmo__pxxv:
                ddhwr__xira = get_df_obj_column_codegen(context, builder,
                    cza__iqsu, table.parent, djo__fafhy, sig.args[1].dtype)
                arr = cza__iqsu.to_native_value(sig.args[1].dtype, ddhwr__xira
                    ).value
                soww__poun.inititem(tcyh__owx, arr, incref=False)
                cza__iqsu.decref(ddhwr__xira)
            with sjgir__xptq:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    cpved__beefd = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, reaof__otghr, odr__tudry = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{cpved__beefd}', reaof__otghr)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, gea__hodok = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = gea__hodok
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        evhst__erfwy, zqlvn__vufi = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, zqlvn__vufi)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, evhst__erfwy)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    fzqrq__hem = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(fzqrq__hem, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        fzqrq__hem = types.List(to_str_arr_if_dict_array(fzqrq__hem.dtype))

    def codegen(context, builder, sig, args):
        vsqy__wlw = args[1]
        odr__tudry, nqzw__wvsth = ListInstance.allocate_ex(context, builder,
            fzqrq__hem, vsqy__wlw)
        nqzw__wvsth.size = vsqy__wlw
        return nqzw__wvsth.value
    sig = fzqrq__hem(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ=None):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    ntxxb__lsivy = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(ntxxb__lsivy)

    def codegen(context, builder, sig, args):
        vsqy__wlw, odr__tudry = args
        odr__tudry, nqzw__wvsth = ListInstance.allocate_ex(context, builder,
            list_type, vsqy__wlw)
        nqzw__wvsth.size = vsqy__wlw
        return nqzw__wvsth.value
    sig = list_type(size_typ, data_typ)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        fynrp__ceu = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(fynrp__ceu)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    gpu__yja = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        djuug__qzi = used_cols.instance_type
        wauv__vcd = np.array(djuug__qzi.meta, dtype=np.int64)
        gpu__yja['used_cols_vals'] = wauv__vcd
        zes__stnm = set([T.block_nums[i] for i in wauv__vcd])
    else:
        wauv__vcd = None
    kwy__nolym = 'def table_filter_func(T, idx, used_cols=None):\n'
    kwy__nolym += f'  T2 = init_table(T, False)\n'
    kwy__nolym += f'  l = 0\n'
    if wauv__vcd is not None and len(wauv__vcd) == 0:
        kwy__nolym += f'  l = _get_idx_length(idx, len(T))\n'
        kwy__nolym += f'  T2 = set_table_len(T2, l)\n'
        kwy__nolym += f'  return T2\n'
        cmtfv__uxq = {}
        exec(kwy__nolym, gpu__yja, cmtfv__uxq)
        return cmtfv__uxq['table_filter_func']
    if wauv__vcd is not None:
        kwy__nolym += f'  used_set = set(used_cols_vals)\n'
    for cpved__beefd in T.type_to_blk.values():
        kwy__nolym += (
            f'  arr_list_{cpved__beefd} = get_table_block(T, {cpved__beefd})\n'
            )
        kwy__nolym += f"""  out_arr_list_{cpved__beefd} = alloc_list_like(arr_list_{cpved__beefd}, len(arr_list_{cpved__beefd}), False)
"""
        if wauv__vcd is None or cpved__beefd in zes__stnm:
            gpu__yja[f'arr_inds_{cpved__beefd}'] = np.array(T.
                block_to_arr_ind[cpved__beefd], dtype=np.int64)
            kwy__nolym += f'  for i in range(len(arr_list_{cpved__beefd})):\n'
            kwy__nolym += (
                f'    arr_ind_{cpved__beefd} = arr_inds_{cpved__beefd}[i]\n')
            if wauv__vcd is not None:
                kwy__nolym += (
                    f'    if arr_ind_{cpved__beefd} not in used_set: continue\n'
                    )
            kwy__nolym += f"""    ensure_column_unboxed(T, arr_list_{cpved__beefd}, i, arr_ind_{cpved__beefd})
"""
            kwy__nolym += f"""    out_arr_{cpved__beefd} = ensure_contig_if_np(arr_list_{cpved__beefd}[i][idx])
"""
            kwy__nolym += f'    l = len(out_arr_{cpved__beefd})\n'
            kwy__nolym += (
                f'    out_arr_list_{cpved__beefd}[i] = out_arr_{cpved__beefd}\n'
                )
        kwy__nolym += (
            f'  T2 = set_table_block(T2, out_arr_list_{cpved__beefd}, {cpved__beefd})\n'
            )
    kwy__nolym += f'  T2 = set_table_len(T2, l)\n'
    kwy__nolym += f'  return T2\n'
    cmtfv__uxq = {}
    exec(kwy__nolym, gpu__yja, cmtfv__uxq)
    return cmtfv__uxq['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, used_cols=None):
    orl__rudv = list(idx.instance_type.meta)
    amtcd__haur = tuple(np.array(T.arr_types, dtype=object)[orl__rudv])
    izrn__aapo = TableType(amtcd__haur)
    gpu__yja = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': izrn__aapo}
    if not is_overload_none(used_cols):
        rcomx__tlxi = used_cols.instance_type.meta
        pfhw__xdqzm = set(rcomx__tlxi)
        gpu__yja['kept_cols'] = np.array(rcomx__tlxi, np.int64)
        zadf__qwlk = True
    else:
        zadf__qwlk = False
    ukicm__lxbu = {i: c for i, c in enumerate(orl__rudv)}
    kwy__nolym = 'def table_subset(T, idx, used_cols=None):\n'
    kwy__nolym += f'  T2 = init_table(out_table_typ, False)\n'
    kwy__nolym += f'  T2 = set_table_len(T2, len(T))\n'
    if zadf__qwlk and len(pfhw__xdqzm) == 0:
        kwy__nolym += f'  return T2\n'
        cmtfv__uxq = {}
        exec(kwy__nolym, gpu__yja, cmtfv__uxq)
        return cmtfv__uxq['table_subset']
    if zadf__qwlk:
        kwy__nolym += f'  kept_cols_set = set(kept_cols)\n'
    for typ, cpved__beefd in izrn__aapo.type_to_blk.items():
        czc__qitev = T.type_to_blk[typ]
        kwy__nolym += (
            f'  arr_list_{cpved__beefd} = get_table_block(T, {czc__qitev})\n')
        kwy__nolym += f"""  out_arr_list_{cpved__beefd} = alloc_list_like(arr_list_{cpved__beefd}, {len(izrn__aapo.block_to_arr_ind[cpved__beefd])}, False)
"""
        htg__iji = True
        if zadf__qwlk:
            svp__nmglp = set(izrn__aapo.block_to_arr_ind[cpved__beefd])
            euyb__acb = svp__nmglp & pfhw__xdqzm
            htg__iji = len(euyb__acb) > 0
        if htg__iji:
            gpu__yja[f'out_arr_inds_{cpved__beefd}'] = np.array(izrn__aapo.
                block_to_arr_ind[cpved__beefd], dtype=np.int64)
            kwy__nolym += (
                f'  for i in range(len(out_arr_list_{cpved__beefd})):\n')
            kwy__nolym += (
                f'    out_arr_ind_{cpved__beefd} = out_arr_inds_{cpved__beefd}[i]\n'
                )
            if zadf__qwlk:
                kwy__nolym += (
                    f'    if out_arr_ind_{cpved__beefd} not in kept_cols_set: continue\n'
                    )
            pffn__xbqe = []
            bitan__nsgsa = []
            for kajn__ckxpi in izrn__aapo.block_to_arr_ind[cpved__beefd]:
                couk__vvtu = ukicm__lxbu[kajn__ckxpi]
                pffn__xbqe.append(couk__vvtu)
                nqcbg__iscky = T.block_offsets[couk__vvtu]
                bitan__nsgsa.append(nqcbg__iscky)
            gpu__yja[f'in_logical_idx_{cpved__beefd}'] = np.array(pffn__xbqe,
                dtype=np.int64)
            gpu__yja[f'in_physical_idx_{cpved__beefd}'] = np.array(bitan__nsgsa
                , dtype=np.int64)
            kwy__nolym += (
                f'    logical_idx_{cpved__beefd} = in_logical_idx_{cpved__beefd}[i]\n'
                )
            kwy__nolym += (
                f'    physical_idx_{cpved__beefd} = in_physical_idx_{cpved__beefd}[i]\n'
                )
            kwy__nolym += f"""    ensure_column_unboxed(T, arr_list_{cpved__beefd}, physical_idx_{cpved__beefd}, logical_idx_{cpved__beefd})
"""
            kwy__nolym += f"""    out_arr_list_{cpved__beefd}[i] = arr_list_{cpved__beefd}[physical_idx_{cpved__beefd}].copy()
"""
        kwy__nolym += (
            f'  T2 = set_table_block(T2, out_arr_list_{cpved__beefd}, {cpved__beefd})\n'
            )
    kwy__nolym += f'  return T2\n'
    cmtfv__uxq = {}
    exec(kwy__nolym, gpu__yja, cmtfv__uxq)
    return cmtfv__uxq['table_subset']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    kwy__nolym = 'def impl(T):\n'
    kwy__nolym += f'  T2 = init_table(T, True)\n'
    kwy__nolym += f'  l = len(T)\n'
    gpu__yja = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for cpved__beefd in T.type_to_blk.values():
        gpu__yja[f'arr_inds_{cpved__beefd}'] = np.array(T.block_to_arr_ind[
            cpved__beefd], dtype=np.int64)
        kwy__nolym += (
            f'  arr_list_{cpved__beefd} = get_table_block(T, {cpved__beefd})\n'
            )
        kwy__nolym += f"""  out_arr_list_{cpved__beefd} = alloc_list_like(arr_list_{cpved__beefd}, len(arr_list_{cpved__beefd}), True)
"""
        kwy__nolym += f'  for i in range(len(arr_list_{cpved__beefd})):\n'
        kwy__nolym += (
            f'    arr_ind_{cpved__beefd} = arr_inds_{cpved__beefd}[i]\n')
        kwy__nolym += f"""    ensure_column_unboxed(T, arr_list_{cpved__beefd}, i, arr_ind_{cpved__beefd})
"""
        kwy__nolym += f"""    out_arr_{cpved__beefd} = decode_if_dict_array(arr_list_{cpved__beefd}[i])
"""
        kwy__nolym += (
            f'    out_arr_list_{cpved__beefd}[i] = out_arr_{cpved__beefd}\n')
        kwy__nolym += (
            f'  T2 = set_table_block(T2, out_arr_list_{cpved__beefd}, {cpved__beefd})\n'
            )
    kwy__nolym += f'  T2 = set_table_len(T2, l)\n'
    kwy__nolym += f'  return T2\n'
    cmtfv__uxq = {}
    exec(kwy__nolym, gpu__yja, cmtfv__uxq)
    return cmtfv__uxq['impl']


@overload(operator.getitem, no_unliteral=True, inline='always')
def overload_table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return lambda T, idx: table_filter(T, idx)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        cmz__simk = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        cmz__simk = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            cmz__simk.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        eeao__vhotu, upcn__wobe = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = upcn__wobe
        tnrau__jweq = cgutils.unpack_tuple(builder, eeao__vhotu)
        for i, ntvi__ogtyb in enumerate(tnrau__jweq):
            setattr(table, f'block_{i}', ntvi__ogtyb)
            context.nrt.incref(builder, types.List(cmz__simk[i]), ntvi__ogtyb)
        return table._getvalue()
    table_type = TableType(tuple(cmz__simk), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
