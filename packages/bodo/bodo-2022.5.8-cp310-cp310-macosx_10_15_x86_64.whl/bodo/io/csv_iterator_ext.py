"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.typing import ColNamesMetaType
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name, escapechar, storage_options):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        wtbw__ymtr = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(wtbw__ymtr)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name
        self._escapechar = escapechar
        self._storage_options = storage_options

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vni__abid = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, vni__abid)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    tjc__qol = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    pguek__jmsbc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    szp__fwv = cgutils.get_or_insert_function(builder.module, pguek__jmsbc,
        name='initialize_csv_reader')
    builder.call(szp__fwv, [tjc__qol.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), tjc__qol.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [fkwxb__llwt] = sig.args
    [jbd__tqy] = args
    tjc__qol = cgutils.create_struct_proxy(fkwxb__llwt)(context, builder,
        value=jbd__tqy)
    pguek__jmsbc = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    szp__fwv = cgutils.get_or_insert_function(builder.module, pguek__jmsbc,
        name='update_csv_reader')
    rqae__upt = builder.call(szp__fwv, [tjc__qol.csv_reader])
    result.set_valid(rqae__upt)
    with builder.if_then(rqae__upt):
        gro__eaxd = builder.load(tjc__qol.index)
        igwir__bqag = types.Tuple([sig.return_type.first_type, types.int64])
        bfko__uobgm = gen_read_csv_objmode(sig.args[0])
        kzas__htbtn = signature(igwir__bqag, bodo.ir.connector.
            stream_reader_type, types.int64)
        grkjo__qdx = context.compile_internal(builder, bfko__uobgm,
            kzas__htbtn, [tjc__qol.csv_reader, gro__eaxd])
        pzktg__dmww, krvts__xjapm = cgutils.unpack_tuple(builder, grkjo__qdx)
        tdko__jaud = builder.add(gro__eaxd, krvts__xjapm, flags=['nsw'])
        builder.store(tdko__jaud, tjc__qol.index)
        result.yield_(pzktg__dmww)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        cllid__hamq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        cllid__hamq.csv_reader = args[0]
        dqce__ojpq = context.get_constant(types.uintp, 0)
        cllid__hamq.index = cgutils.alloca_once_value(builder, dqce__ojpq)
        return cllid__hamq._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    tjq__ifmzn = csv_iterator_typeref.instance_type
    sig = signature(tjq__ifmzn, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    rbfpk__bfdqr = 'def read_csv_objmode(f_reader):\n'
    hkdxh__fuf = [sanitize_varname(wwil__imjrm) for wwil__imjrm in
        csv_iterator_type._out_colnames]
    pbhn__jhmx = ir_utils.next_label()
    lkvl__lfoq = globals()
    out_types = csv_iterator_type._out_types
    lkvl__lfoq[f'table_type_{pbhn__jhmx}'] = TableType(tuple(out_types))
    lkvl__lfoq[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    bxvek__bnx = list(range(len(csv_iterator_type._usecols)))
    rbfpk__bfdqr += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        hkdxh__fuf, out_types, csv_iterator_type._usecols, bxvek__bnx,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, pbhn__jhmx, lkvl__lfoq,
        parallel=False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    zcw__mqs = bodo.ir.csv_ext._gen_parallel_flag_name(hkdxh__fuf)
    susb__wfxou = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [zcw__mqs]
    rbfpk__bfdqr += f"  return {', '.join(susb__wfxou)}"
    lkvl__lfoq = globals()
    bzvyg__dddsu = {}
    exec(rbfpk__bfdqr, lkvl__lfoq, bzvyg__dddsu)
    ibtf__onvki = bzvyg__dddsu['read_csv_objmode']
    hrmr__zil = numba.njit(ibtf__onvki)
    bodo.ir.csv_ext.compiled_funcs.append(hrmr__zil)
    hboy__ckqfk = 'def read_func(reader, local_start):\n'
    hboy__ckqfk += f"  {', '.join(susb__wfxou)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        hboy__ckqfk += f'  local_len = len(T)\n'
        hboy__ckqfk += '  total_size = local_len\n'
        hboy__ckqfk += f'  if ({zcw__mqs}):\n'
        hboy__ckqfk += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        hboy__ckqfk += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        yzvzz__piz = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        hboy__ckqfk += '  total_size = 0\n'
        yzvzz__piz = (
            f'bodo.utils.conversion.convert_to_index({susb__wfxou[1]}, {csv_iterator_type._index_name!r})'
            )
    hboy__ckqfk += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({susb__wfxou[0]},), {yzvzz__piz}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(hboy__ckqfk, {'bodo': bodo, 'objmode_func': hrmr__zil, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, bzvyg__dddsu)
    return bzvyg__dddsu['read_func']
