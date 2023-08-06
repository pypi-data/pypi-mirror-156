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
            mqddy__djt = 0
            omec__qpgub = []
            for i in range(usecols[-1] + 1):
                if i == usecols[mqddy__djt]:
                    omec__qpgub.append(arrs[mqddy__djt])
                    mqddy__djt += 1
                else:
                    omec__qpgub.append(None)
            for dkrdc__uzkjm in range(usecols[-1] + 1, num_arrs):
                omec__qpgub.append(None)
            self.arrays = omec__qpgub
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((aqzjj__tfu == wzxgs__qohd).all() for 
            aqzjj__tfu, wzxgs__qohd in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        zjj__yesu = len(self.arrays)
        uic__yehz = dict(zip(range(zjj__yesu), self.arrays))
        df = pd.DataFrame(uic__yehz, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        kafk__qjd = []
        ewco__aovm = []
        jqekb__jqr = {}
        wtltg__nfw = {}
        uucb__ojvby = defaultdict(int)
        iya__zsk = defaultdict(list)
        if not has_runtime_cols:
            for i, ojwj__oytr in enumerate(arr_types):
                if ojwj__oytr not in jqekb__jqr:
                    ptksr__gua = len(jqekb__jqr)
                    jqekb__jqr[ojwj__oytr] = ptksr__gua
                    wtltg__nfw[ptksr__gua] = ojwj__oytr
                hpa__aykbt = jqekb__jqr[ojwj__oytr]
                kafk__qjd.append(hpa__aykbt)
                ewco__aovm.append(uucb__ojvby[hpa__aykbt])
                uucb__ojvby[hpa__aykbt] += 1
                iya__zsk[hpa__aykbt].append(i)
        self.block_nums = kafk__qjd
        self.block_offsets = ewco__aovm
        self.type_to_blk = jqekb__jqr
        self.blk_to_type = wtltg__nfw
        self.block_to_arr_ind = iya__zsk
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
            hlzjw__vwgic = [(f'block_{i}', types.List(ojwj__oytr)) for i,
                ojwj__oytr in enumerate(fe_type.arr_types)]
        else:
            hlzjw__vwgic = [(f'block_{hpa__aykbt}', types.List(ojwj__oytr)) for
                ojwj__oytr, hpa__aykbt in fe_type.type_to_blk.items()]
        hlzjw__vwgic.append(('parent', types.pyobject))
        hlzjw__vwgic.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, hlzjw__vwgic)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    kms__oelk = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    obro__lxa = c.pyapi.make_none()
    uhlas__khh = c.context.get_constant(types.int64, 0)
    wjz__ogg = cgutils.alloca_once_value(c.builder, uhlas__khh)
    for ojwj__oytr, hpa__aykbt in typ.type_to_blk.items():
        kppf__fbiw = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[hpa__aykbt]))
        dkrdc__uzkjm, fjtxy__kxb = ListInstance.allocate_ex(c.context, c.
            builder, types.List(ojwj__oytr), kppf__fbiw)
        fjtxy__kxb.size = kppf__fbiw
        vyqx__mcdv = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[hpa__aykbt],
            dtype=np.int64))
        sikb__agz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, vyqx__mcdv)
        with cgutils.for_range(c.builder, kppf__fbiw) as ptcvu__uef:
            i = ptcvu__uef.index
            jdpp__piq = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), sikb__agz, i)
            xjz__bny = c.pyapi.long_from_longlong(jdpp__piq)
            yejvv__smk = c.pyapi.object_getitem(kms__oelk, xjz__bny)
            qljo__hoyx = c.builder.icmp_unsigned('==', yejvv__smk, obro__lxa)
            with c.builder.if_else(qljo__hoyx) as (oze__kjqam, xcm__mszzx):
                with oze__kjqam:
                    aoaj__mzae = c.context.get_constant_null(ojwj__oytr)
                    fjtxy__kxb.inititem(i, aoaj__mzae, incref=False)
                with xcm__mszzx:
                    cqkgj__secy = c.pyapi.call_method(yejvv__smk, '__len__', ()
                        )
                    omh__qgyld = c.pyapi.long_as_longlong(cqkgj__secy)
                    c.builder.store(omh__qgyld, wjz__ogg)
                    c.pyapi.decref(cqkgj__secy)
                    arr = c.pyapi.to_native_value(ojwj__oytr, yejvv__smk).value
                    fjtxy__kxb.inititem(i, arr, incref=False)
            c.pyapi.decref(yejvv__smk)
            c.pyapi.decref(xjz__bny)
        setattr(table, f'block_{hpa__aykbt}', fjtxy__kxb.value)
    table.len = c.builder.load(wjz__ogg)
    c.pyapi.decref(kms__oelk)
    c.pyapi.decref(obro__lxa)
    qodx__tud = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=qodx__tud)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        cnj__fde = c.context.get_constant(types.int64, 0)
        for i, ojwj__oytr in enumerate(typ.arr_types):
            omec__qpgub = getattr(table, f'block_{i}')
            unwrr__hyecv = ListInstance(c.context, c.builder, types.List(
                ojwj__oytr), omec__qpgub)
            cnj__fde = c.builder.add(cnj__fde, unwrr__hyecv.size)
        hxsh__jchc = c.pyapi.list_new(cnj__fde)
        zvx__axscw = c.context.get_constant(types.int64, 0)
        for i, ojwj__oytr in enumerate(typ.arr_types):
            omec__qpgub = getattr(table, f'block_{i}')
            unwrr__hyecv = ListInstance(c.context, c.builder, types.List(
                ojwj__oytr), omec__qpgub)
            with cgutils.for_range(c.builder, unwrr__hyecv.size) as ptcvu__uef:
                i = ptcvu__uef.index
                arr = unwrr__hyecv.getitem(i)
                c.context.nrt.incref(c.builder, ojwj__oytr, arr)
                idx = c.builder.add(zvx__axscw, i)
                c.pyapi.list_setitem(hxsh__jchc, idx, c.pyapi.
                    from_native_value(ojwj__oytr, arr, c.env_manager))
            zvx__axscw = c.builder.add(zvx__axscw, unwrr__hyecv.size)
        ewc__tbx = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        bdm__yag = c.pyapi.call_function_objargs(ewc__tbx, (hxsh__jchc,))
        c.pyapi.decref(ewc__tbx)
        c.pyapi.decref(hxsh__jchc)
        c.context.nrt.decref(c.builder, typ, val)
        return bdm__yag
    hxsh__jchc = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    jfk__zjx = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for ojwj__oytr, hpa__aykbt in typ.type_to_blk.items():
        omec__qpgub = getattr(table, f'block_{hpa__aykbt}')
        unwrr__hyecv = ListInstance(c.context, c.builder, types.List(
            ojwj__oytr), omec__qpgub)
        vyqx__mcdv = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[hpa__aykbt],
            dtype=np.int64))
        sikb__agz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, vyqx__mcdv)
        with cgutils.for_range(c.builder, unwrr__hyecv.size) as ptcvu__uef:
            i = ptcvu__uef.index
            jdpp__piq = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), sikb__agz, i)
            arr = unwrr__hyecv.getitem(i)
            pgig__wrz = cgutils.alloca_once_value(c.builder, arr)
            qzu__sudx = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(ojwj__oytr))
            is_null = is_ll_eq(c.builder, pgig__wrz, qzu__sudx)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (oze__kjqam, xcm__mszzx):
                with oze__kjqam:
                    obro__lxa = c.pyapi.make_none()
                    c.pyapi.list_setitem(hxsh__jchc, jdpp__piq, obro__lxa)
                with xcm__mszzx:
                    yejvv__smk = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, jfk__zjx)
                        ) as (lvzf__anbp, cxbjn__jcbyl):
                        with lvzf__anbp:
                            qtgh__snrox = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                jdpp__piq, ojwj__oytr)
                            c.builder.store(qtgh__snrox, yejvv__smk)
                        with cxbjn__jcbyl:
                            c.context.nrt.incref(c.builder, ojwj__oytr, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                ojwj__oytr, arr, c.env_manager), yejvv__smk)
                    c.pyapi.list_setitem(hxsh__jchc, jdpp__piq, c.builder.
                        load(yejvv__smk))
    ewc__tbx = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    bdm__yag = c.pyapi.call_function_objargs(ewc__tbx, (hxsh__jchc,))
    c.pyapi.decref(ewc__tbx)
    c.pyapi.decref(hxsh__jchc)
    c.context.nrt.decref(c.builder, typ, val)
    return bdm__yag


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
        zqicu__dqeb = context.get_constant(types.int64, 0)
        for i, ojwj__oytr in enumerate(table_type.arr_types):
            omec__qpgub = getattr(table, f'block_{i}')
            unwrr__hyecv = ListInstance(context, builder, types.List(
                ojwj__oytr), omec__qpgub)
            zqicu__dqeb = builder.add(zqicu__dqeb, unwrr__hyecv.size)
        return zqicu__dqeb
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    hpa__aykbt = table_type.block_nums[col_ind]
    lduhg__svh = table_type.block_offsets[col_ind]
    omec__qpgub = getattr(table, f'block_{hpa__aykbt}')
    unwrr__hyecv = ListInstance(context, builder, types.List(arr_type),
        omec__qpgub)
    arr = unwrr__hyecv.getitem(lduhg__svh)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, dkrdc__uzkjm = args
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
    dmgs__dgio = list(ind_typ.instance_type.meta)
    dezxy__ysvkr = defaultdict(list)
    for ind in dmgs__dgio:
        dezxy__ysvkr[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, dkrdc__uzkjm = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for hpa__aykbt, drk__ogl in dezxy__ysvkr.items():
            arr_type = table_type.blk_to_type[hpa__aykbt]
            omec__qpgub = getattr(table, f'block_{hpa__aykbt}')
            unwrr__hyecv = ListInstance(context, builder, types.List(
                arr_type), omec__qpgub)
            aoaj__mzae = context.get_constant_null(arr_type)
            if len(drk__ogl) == 1:
                lduhg__svh = drk__ogl[0]
                arr = unwrr__hyecv.getitem(lduhg__svh)
                context.nrt.decref(builder, arr_type, arr)
                unwrr__hyecv.inititem(lduhg__svh, aoaj__mzae, incref=False)
            else:
                kppf__fbiw = context.get_constant(types.int64, len(drk__ogl))
                mveid__bkw = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(drk__ogl, dtype=np
                    .int64))
                ytrfn__ipxd = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, mveid__bkw)
                with cgutils.for_range(builder, kppf__fbiw) as ptcvu__uef:
                    i = ptcvu__uef.index
                    lduhg__svh = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        ytrfn__ipxd, i)
                    arr = unwrr__hyecv.getitem(lduhg__svh)
                    context.nrt.decref(builder, arr_type, arr)
                    unwrr__hyecv.inititem(lduhg__svh, aoaj__mzae, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    uhlas__khh = context.get_constant(types.int64, 0)
    frk__gfu = context.get_constant(types.int64, 1)
    qwdhp__kghv = arr_type not in in_table_type.type_to_blk
    for ojwj__oytr, hpa__aykbt in out_table_type.type_to_blk.items():
        if ojwj__oytr in in_table_type.type_to_blk:
            uwi__mdbxc = in_table_type.type_to_blk[ojwj__oytr]
            fjtxy__kxb = ListInstance(context, builder, types.List(
                ojwj__oytr), getattr(in_table, f'block_{uwi__mdbxc}'))
            context.nrt.incref(builder, types.List(ojwj__oytr), fjtxy__kxb.
                value)
            setattr(out_table, f'block_{hpa__aykbt}', fjtxy__kxb.value)
    if qwdhp__kghv:
        dkrdc__uzkjm, fjtxy__kxb = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), frk__gfu)
        fjtxy__kxb.size = frk__gfu
        fjtxy__kxb.inititem(uhlas__khh, arr_arg, incref=True)
        hpa__aykbt = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{hpa__aykbt}', fjtxy__kxb.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        hpa__aykbt = out_table_type.type_to_blk[arr_type]
        fjtxy__kxb = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{hpa__aykbt}'))
        if is_new_col:
            n = fjtxy__kxb.size
            zajv__xyl = builder.add(n, frk__gfu)
            fjtxy__kxb.resize(zajv__xyl)
            fjtxy__kxb.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            zfby__pixug = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            fjtxy__kxb.setitem(zfby__pixug, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            zfby__pixug = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = fjtxy__kxb.size
            zajv__xyl = builder.add(n, frk__gfu)
            fjtxy__kxb.resize(zajv__xyl)
            context.nrt.incref(builder, arr_type, fjtxy__kxb.getitem(
                zfby__pixug))
            fjtxy__kxb.move(builder.add(zfby__pixug, frk__gfu), zfby__pixug,
                builder.sub(n, zfby__pixug))
            fjtxy__kxb.setitem(zfby__pixug, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    svgi__twjf = in_table_type.arr_types[col_ind]
    if svgi__twjf in out_table_type.type_to_blk:
        hpa__aykbt = out_table_type.type_to_blk[svgi__twjf]
        sss__cyf = getattr(out_table, f'block_{hpa__aykbt}')
        ngolg__wpu = types.List(svgi__twjf)
        zfby__pixug = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        gjrvy__okiu = ngolg__wpu.dtype(ngolg__wpu, types.intp)
        kvag__goo = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), gjrvy__okiu, (sss__cyf, zfby__pixug))
        context.nrt.decref(builder, svgi__twjf, kvag__goo)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    egr__sjk = list(table.arr_types)
    if ind == len(egr__sjk):
        ucn__nvcf = None
        egr__sjk.append(arr_type)
    else:
        ucn__nvcf = table.arr_types[ind]
        egr__sjk[ind] = arr_type
    lzt__wpbj = TableType(tuple(egr__sjk))
    lmecb__cna = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': lzt__wpbj}
    dkz__llzw = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    dkz__llzw += f'  T2 = init_table(out_table_typ, False)\n'
    dkz__llzw += f'  T2 = set_table_len(T2, len(table))\n'
    dkz__llzw += f'  T2 = set_table_parent(T2, table)\n'
    for typ, hpa__aykbt in lzt__wpbj.type_to_blk.items():
        if typ in table.type_to_blk:
            lmm__kkosd = table.type_to_blk[typ]
            dkz__llzw += (
                f'  arr_list_{hpa__aykbt} = get_table_block(table, {lmm__kkosd})\n'
                )
            dkz__llzw += f"""  out_arr_list_{hpa__aykbt} = alloc_list_like(arr_list_{hpa__aykbt}, {len(lzt__wpbj.block_to_arr_ind[hpa__aykbt])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[lmm__kkosd]
                ) & used_cols:
                dkz__llzw += f'  for i in range(len(arr_list_{hpa__aykbt})):\n'
                if typ not in (ucn__nvcf, arr_type):
                    dkz__llzw += (
                        f'    out_arr_list_{hpa__aykbt}[i] = arr_list_{hpa__aykbt}[i]\n'
                        )
                else:
                    bgu__eyeau = table.block_to_arr_ind[lmm__kkosd]
                    rvs__alm = np.empty(len(bgu__eyeau), np.int64)
                    foic__rzne = False
                    for pjzss__wqa, jdpp__piq in enumerate(bgu__eyeau):
                        if jdpp__piq != ind:
                            lfyqy__dbnyp = lzt__wpbj.block_offsets[jdpp__piq]
                        else:
                            lfyqy__dbnyp = -1
                            foic__rzne = True
                        rvs__alm[pjzss__wqa] = lfyqy__dbnyp
                    lmecb__cna[f'out_idxs_{hpa__aykbt}'] = np.array(rvs__alm,
                        np.int64)
                    dkz__llzw += f'    out_idx = out_idxs_{hpa__aykbt}[i]\n'
                    if foic__rzne:
                        dkz__llzw += f'    if out_idx == -1:\n'
                        dkz__llzw += f'      continue\n'
                    dkz__llzw += f"""    out_arr_list_{hpa__aykbt}[out_idx] = arr_list_{hpa__aykbt}[i]
"""
            if typ == arr_type and not is_null:
                dkz__llzw += (
                    f'  out_arr_list_{hpa__aykbt}[{lzt__wpbj.block_offsets[ind]}] = arr\n'
                    )
        else:
            lmecb__cna[f'arr_list_typ_{hpa__aykbt}'] = types.List(arr_type)
            dkz__llzw += f"""  out_arr_list_{hpa__aykbt} = alloc_list_like(arr_list_typ_{hpa__aykbt}, 1, False)
"""
            if not is_null:
                dkz__llzw += f'  out_arr_list_{hpa__aykbt}[0] = arr\n'
        dkz__llzw += (
            f'  T2 = set_table_block(T2, out_arr_list_{hpa__aykbt}, {hpa__aykbt})\n'
            )
    dkz__llzw += f'  return T2\n'
    eqq__qsfi = {}
    exec(dkz__llzw, lmecb__cna, eqq__qsfi)
    return eqq__qsfi['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        dzjgf__idg = None
    else:
        dzjgf__idg = set(used_cols.instance_type.meta)
    idyf__jmpgs = get_overload_const_int(ind)
    return generate_set_table_data_code(table, idyf__jmpgs, arr, dzjgf__idg)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    idyf__jmpgs = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        dzjgf__idg = None
    else:
        dzjgf__idg = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, idyf__jmpgs, arr_type,
        dzjgf__idg, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    jsc__kfxi = args[0]
    if equiv_set.has_shape(jsc__kfxi):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            jsc__kfxi)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    ptv__gqbut = []
    for ojwj__oytr, hpa__aykbt in table_type.type_to_blk.items():
        gxaa__wzthc = len(table_type.block_to_arr_ind[hpa__aykbt])
        mgf__wsqqe = []
        for i in range(gxaa__wzthc):
            jdpp__piq = table_type.block_to_arr_ind[hpa__aykbt][i]
            mgf__wsqqe.append(pyval.arrays[jdpp__piq])
        ptv__gqbut.append(context.get_constant_generic(builder, types.List(
            ojwj__oytr), mgf__wsqqe))
    mps__boszc = context.get_constant_null(types.pyobject)
    jylek__yvsf = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(ptv__gqbut + [mps__boszc, jylek__yvsf])


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
        for ojwj__oytr, hpa__aykbt in out_table_type.type_to_blk.items():
            ytl__tql = context.get_constant_null(types.List(ojwj__oytr))
            setattr(table, f'block_{hpa__aykbt}', ytl__tql)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    cyj__twd = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        cyj__twd[typ.dtype] = i
    lqzrh__nwf = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(lqzrh__nwf, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        tyzii__lsj, dkrdc__uzkjm = args
        table = cgutils.create_struct_proxy(lqzrh__nwf)(context, builder)
        for ojwj__oytr, hpa__aykbt in lqzrh__nwf.type_to_blk.items():
            idx = cyj__twd[ojwj__oytr]
            inrvg__iiaj = signature(types.List(ojwj__oytr),
                tuple_of_lists_type, types.literal(idx))
            zyygu__pel = tyzii__lsj, idx
            kjokb__rgp = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, inrvg__iiaj, zyygu__pel)
            setattr(table, f'block_{hpa__aykbt}', kjokb__rgp)
        return table._getvalue()
    sig = lqzrh__nwf(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    hpa__aykbt = get_overload_const_int(blk_type)
    arr_type = None
    for ojwj__oytr, wzxgs__qohd in table_type.type_to_blk.items():
        if wzxgs__qohd == hpa__aykbt:
            arr_type = ojwj__oytr
            break
    assert arr_type is not None, 'invalid table type block'
    poc__sgk = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        omec__qpgub = getattr(table, f'block_{hpa__aykbt}')
        return impl_ret_borrowed(context, builder, poc__sgk, omec__qpgub)
    sig = poc__sgk(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, vli__yzma = args
        jdyex__bika = context.get_python_api(builder)
        jkgdo__chk = used_cols_typ == types.none
        if not jkgdo__chk:
            pcjwe__dprh = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), vli__yzma)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for ojwj__oytr, hpa__aykbt in table_type.type_to_blk.items():
            kppf__fbiw = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[hpa__aykbt]))
            vyqx__mcdv = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                hpa__aykbt], dtype=np.int64))
            sikb__agz = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, vyqx__mcdv)
            omec__qpgub = getattr(table, f'block_{hpa__aykbt}')
            with cgutils.for_range(builder, kppf__fbiw) as ptcvu__uef:
                i = ptcvu__uef.index
                jdpp__piq = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), sikb__agz, i
                    )
                sxrq__mcfm = types.none(table_type, types.List(ojwj__oytr),
                    types.int64, types.int64)
                ktw__vfyu = table_arg, omec__qpgub, i, jdpp__piq
                if jkgdo__chk:
                    ensure_column_unboxed_codegen(context, builder,
                        sxrq__mcfm, ktw__vfyu)
                else:
                    jmffb__ohkw = pcjwe__dprh.contains(jdpp__piq)
                    with builder.if_then(jmffb__ohkw):
                        ensure_column_unboxed_codegen(context, builder,
                            sxrq__mcfm, ktw__vfyu)
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
    table_arg, xvq__nnvdp, saypp__gkj, ndlft__zzsd = args
    jdyex__bika = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    jfk__zjx = cgutils.is_not_null(builder, table.parent)
    unwrr__hyecv = ListInstance(context, builder, sig.args[1], xvq__nnvdp)
    qnhx__ozjgr = unwrr__hyecv.getitem(saypp__gkj)
    pgig__wrz = cgutils.alloca_once_value(builder, qnhx__ozjgr)
    qzu__sudx = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, pgig__wrz, qzu__sudx)
    with builder.if_then(is_null):
        with builder.if_else(jfk__zjx) as (oze__kjqam, xcm__mszzx):
            with oze__kjqam:
                yejvv__smk = get_df_obj_column_codegen(context, builder,
                    jdyex__bika, table.parent, ndlft__zzsd, sig.args[1].dtype)
                arr = jdyex__bika.to_native_value(sig.args[1].dtype, yejvv__smk
                    ).value
                unwrr__hyecv.inititem(saypp__gkj, arr, incref=False)
                jdyex__bika.decref(yejvv__smk)
            with xcm__mszzx:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    hpa__aykbt = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, knfrj__jcyh, dkrdc__uzkjm = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{hpa__aykbt}', knfrj__jcyh)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, eokup__hxq = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = eokup__hxq
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ahz__lynms, fxkfs__okrpz = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, fxkfs__okrpz)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, ahz__lynms)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    poc__sgk = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(poc__sgk, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        poc__sgk = types.List(to_str_arr_if_dict_array(poc__sgk.dtype))

    def codegen(context, builder, sig, args):
        cuc__ilpa = args[1]
        dkrdc__uzkjm, fjtxy__kxb = ListInstance.allocate_ex(context,
            builder, poc__sgk, cuc__ilpa)
        fjtxy__kxb.size = cuc__ilpa
        return fjtxy__kxb.value
    sig = poc__sgk(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ=None):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    rydou__vds = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(rydou__vds)

    def codegen(context, builder, sig, args):
        cuc__ilpa, dkrdc__uzkjm = args
        dkrdc__uzkjm, fjtxy__kxb = ListInstance.allocate_ex(context,
            builder, list_type, cuc__ilpa)
        fjtxy__kxb.size = cuc__ilpa
        return fjtxy__kxb.value
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
        jjan__ypkli = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(jjan__ypkli)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    lmecb__cna = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        eprzd__kqwgd = used_cols.instance_type
        mqtye__bgkn = np.array(eprzd__kqwgd.meta, dtype=np.int64)
        lmecb__cna['used_cols_vals'] = mqtye__bgkn
        iadr__gtk = set([T.block_nums[i] for i in mqtye__bgkn])
    else:
        mqtye__bgkn = None
    dkz__llzw = 'def table_filter_func(T, idx, used_cols=None):\n'
    dkz__llzw += f'  T2 = init_table(T, False)\n'
    dkz__llzw += f'  l = 0\n'
    if mqtye__bgkn is not None and len(mqtye__bgkn) == 0:
        dkz__llzw += f'  l = _get_idx_length(idx, len(T))\n'
        dkz__llzw += f'  T2 = set_table_len(T2, l)\n'
        dkz__llzw += f'  return T2\n'
        eqq__qsfi = {}
        exec(dkz__llzw, lmecb__cna, eqq__qsfi)
        return eqq__qsfi['table_filter_func']
    if mqtye__bgkn is not None:
        dkz__llzw += f'  used_set = set(used_cols_vals)\n'
    for hpa__aykbt in T.type_to_blk.values():
        dkz__llzw += (
            f'  arr_list_{hpa__aykbt} = get_table_block(T, {hpa__aykbt})\n')
        dkz__llzw += f"""  out_arr_list_{hpa__aykbt} = alloc_list_like(arr_list_{hpa__aykbt}, len(arr_list_{hpa__aykbt}), False)
"""
        if mqtye__bgkn is None or hpa__aykbt in iadr__gtk:
            lmecb__cna[f'arr_inds_{hpa__aykbt}'] = np.array(T.
                block_to_arr_ind[hpa__aykbt], dtype=np.int64)
            dkz__llzw += f'  for i in range(len(arr_list_{hpa__aykbt})):\n'
            dkz__llzw += (
                f'    arr_ind_{hpa__aykbt} = arr_inds_{hpa__aykbt}[i]\n')
            if mqtye__bgkn is not None:
                dkz__llzw += (
                    f'    if arr_ind_{hpa__aykbt} not in used_set: continue\n')
            dkz__llzw += f"""    ensure_column_unboxed(T, arr_list_{hpa__aykbt}, i, arr_ind_{hpa__aykbt})
"""
            dkz__llzw += f"""    out_arr_{hpa__aykbt} = ensure_contig_if_np(arr_list_{hpa__aykbt}[i][idx])
"""
            dkz__llzw += f'    l = len(out_arr_{hpa__aykbt})\n'
            dkz__llzw += (
                f'    out_arr_list_{hpa__aykbt}[i] = out_arr_{hpa__aykbt}\n')
        dkz__llzw += (
            f'  T2 = set_table_block(T2, out_arr_list_{hpa__aykbt}, {hpa__aykbt})\n'
            )
    dkz__llzw += f'  T2 = set_table_len(T2, l)\n'
    dkz__llzw += f'  return T2\n'
    eqq__qsfi = {}
    exec(dkz__llzw, lmecb__cna, eqq__qsfi)
    return eqq__qsfi['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, used_cols=None):
    oewfg__chvu = list(idx.instance_type.meta)
    egr__sjk = tuple(np.array(T.arr_types, dtype=object)[oewfg__chvu])
    lzt__wpbj = TableType(egr__sjk)
    lmecb__cna = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': lzt__wpbj}
    if not is_overload_none(used_cols):
        rgxih__yidrl = used_cols.instance_type.meta
        bbszb__vzuk = set(rgxih__yidrl)
        lmecb__cna['kept_cols'] = np.array(rgxih__yidrl, np.int64)
        wac__aut = True
    else:
        wac__aut = False
    ljoqs__nrmv = {i: c for i, c in enumerate(oewfg__chvu)}
    dkz__llzw = 'def table_subset(T, idx, used_cols=None):\n'
    dkz__llzw += f'  T2 = init_table(out_table_typ, False)\n'
    dkz__llzw += f'  T2 = set_table_len(T2, len(T))\n'
    if wac__aut and len(bbszb__vzuk) == 0:
        dkz__llzw += f'  return T2\n'
        eqq__qsfi = {}
        exec(dkz__llzw, lmecb__cna, eqq__qsfi)
        return eqq__qsfi['table_subset']
    if wac__aut:
        dkz__llzw += f'  kept_cols_set = set(kept_cols)\n'
    for typ, hpa__aykbt in lzt__wpbj.type_to_blk.items():
        lmm__kkosd = T.type_to_blk[typ]
        dkz__llzw += (
            f'  arr_list_{hpa__aykbt} = get_table_block(T, {lmm__kkosd})\n')
        dkz__llzw += f"""  out_arr_list_{hpa__aykbt} = alloc_list_like(arr_list_{hpa__aykbt}, {len(lzt__wpbj.block_to_arr_ind[hpa__aykbt])}, False)
"""
        eghcw__ebs = True
        if wac__aut:
            mjckv__bzdg = set(lzt__wpbj.block_to_arr_ind[hpa__aykbt])
            aujx__temp = mjckv__bzdg & bbszb__vzuk
            eghcw__ebs = len(aujx__temp) > 0
        if eghcw__ebs:
            lmecb__cna[f'out_arr_inds_{hpa__aykbt}'] = np.array(lzt__wpbj.
                block_to_arr_ind[hpa__aykbt], dtype=np.int64)
            dkz__llzw += f'  for i in range(len(out_arr_list_{hpa__aykbt})):\n'
            dkz__llzw += (
                f'    out_arr_ind_{hpa__aykbt} = out_arr_inds_{hpa__aykbt}[i]\n'
                )
            if wac__aut:
                dkz__llzw += (
                    f'    if out_arr_ind_{hpa__aykbt} not in kept_cols_set: continue\n'
                    )
            uykgx__ajqyk = []
            gmrph__qaubz = []
            for jmzvk__uvl in lzt__wpbj.block_to_arr_ind[hpa__aykbt]:
                ntonl__hxpwu = ljoqs__nrmv[jmzvk__uvl]
                uykgx__ajqyk.append(ntonl__hxpwu)
                dbxqi__hezc = T.block_offsets[ntonl__hxpwu]
                gmrph__qaubz.append(dbxqi__hezc)
            lmecb__cna[f'in_logical_idx_{hpa__aykbt}'] = np.array(uykgx__ajqyk,
                dtype=np.int64)
            lmecb__cna[f'in_physical_idx_{hpa__aykbt}'] = np.array(gmrph__qaubz
                , dtype=np.int64)
            dkz__llzw += (
                f'    logical_idx_{hpa__aykbt} = in_logical_idx_{hpa__aykbt}[i]\n'
                )
            dkz__llzw += (
                f'    physical_idx_{hpa__aykbt} = in_physical_idx_{hpa__aykbt}[i]\n'
                )
            dkz__llzw += f"""    ensure_column_unboxed(T, arr_list_{hpa__aykbt}, physical_idx_{hpa__aykbt}, logical_idx_{hpa__aykbt})
"""
            dkz__llzw += f"""    out_arr_list_{hpa__aykbt}[i] = arr_list_{hpa__aykbt}[physical_idx_{hpa__aykbt}].copy()
"""
        dkz__llzw += (
            f'  T2 = set_table_block(T2, out_arr_list_{hpa__aykbt}, {hpa__aykbt})\n'
            )
    dkz__llzw += f'  return T2\n'
    eqq__qsfi = {}
    exec(dkz__llzw, lmecb__cna, eqq__qsfi)
    return eqq__qsfi['table_subset']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    dkz__llzw = 'def impl(T):\n'
    dkz__llzw += f'  T2 = init_table(T, True)\n'
    dkz__llzw += f'  l = len(T)\n'
    lmecb__cna = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for hpa__aykbt in T.type_to_blk.values():
        lmecb__cna[f'arr_inds_{hpa__aykbt}'] = np.array(T.block_to_arr_ind[
            hpa__aykbt], dtype=np.int64)
        dkz__llzw += (
            f'  arr_list_{hpa__aykbt} = get_table_block(T, {hpa__aykbt})\n')
        dkz__llzw += f"""  out_arr_list_{hpa__aykbt} = alloc_list_like(arr_list_{hpa__aykbt}, len(arr_list_{hpa__aykbt}), True)
"""
        dkz__llzw += f'  for i in range(len(arr_list_{hpa__aykbt})):\n'
        dkz__llzw += f'    arr_ind_{hpa__aykbt} = arr_inds_{hpa__aykbt}[i]\n'
        dkz__llzw += f"""    ensure_column_unboxed(T, arr_list_{hpa__aykbt}, i, arr_ind_{hpa__aykbt})
"""
        dkz__llzw += (
            f'    out_arr_{hpa__aykbt} = decode_if_dict_array(arr_list_{hpa__aykbt}[i])\n'
            )
        dkz__llzw += (
            f'    out_arr_list_{hpa__aykbt}[i] = out_arr_{hpa__aykbt}\n')
        dkz__llzw += (
            f'  T2 = set_table_block(T2, out_arr_list_{hpa__aykbt}, {hpa__aykbt})\n'
            )
    dkz__llzw += f'  T2 = set_table_len(T2, l)\n'
    dkz__llzw += f'  return T2\n'
    eqq__qsfi = {}
    exec(dkz__llzw, lmecb__cna, eqq__qsfi)
    return eqq__qsfi['impl']


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
        wtxy__ufw = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        wtxy__ufw = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            wtxy__ufw.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        sxjp__nwso, ydceh__jam = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = ydceh__jam
        ptv__gqbut = cgutils.unpack_tuple(builder, sxjp__nwso)
        for i, omec__qpgub in enumerate(ptv__gqbut):
            setattr(table, f'block_{i}', omec__qpgub)
            context.nrt.incref(builder, types.List(wtxy__ufw[i]), omec__qpgub)
        return table._getvalue()
    table_type = TableType(tuple(wtxy__ufw), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
