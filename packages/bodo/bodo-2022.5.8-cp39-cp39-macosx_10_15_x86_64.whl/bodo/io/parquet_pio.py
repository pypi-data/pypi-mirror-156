import os
import warnings
from collections import defaultdict
from glob import has_magic
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, box, intrinsic, models, overload, register_model, unbox
from pyarrow import null
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_bucket_region_njit, get_s3_fs_from_path, get_s3_subtree_fs, get_storage_options_pyobject, storage_options_dict_type
from bodo.io.helpers import is_nullable
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
use_nullable_int_arr = True
from urllib.parse import urlparse
import bodo.io.pa_parquet
REMOTE_FILESYSTEMS = {'s3', 'gcs', 'gs', 'http', 'hdfs', 'abfs', 'abfss'}
READ_STR_AS_DICT_THRESHOLD = 1.0
list_of_files_error_msg = (
    '. Make sure the list/glob passed to read_parquet() only contains paths to files (no directories)'
    )


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


@box(ParquetPredicateType)
def box_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return val


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None, input_file_name_col=
        None, read_as_dict_cols=None):
        self.columns = columns
        self.storage_options = storage_options
        self.input_file_name_col = input_file_name_col
        self.read_as_dict_cols = read_as_dict_cols
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options, input_file_name_col=
                self.input_file_name_col, read_as_dict_cols=self.
                read_as_dict_cols)
        except OSError as afp__njql:
            if 'non-file path' in str(afp__njql):
                raise FileNotFoundError(str(afp__njql))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        ycj__ftrn = lhs.scope
        dofsn__ttip = lhs.loc
        fzr__zqlo = None
        if lhs.name in self.locals:
            fzr__zqlo = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        dpiv__gggye = {}
        if lhs.name + ':convert' in self.locals:
            dpiv__gggye = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if fzr__zqlo is None:
            zysz__zcjgz = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            xkvi__frkt = get_const_value(file_name, self.func_ir,
                zysz__zcjgz, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            wfrx__pnso = False
            jvh__eeagm = guard(get_definition, self.func_ir, file_name)
            if isinstance(jvh__eeagm, ir.Arg):
                typ = self.args[jvh__eeagm.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, imnmq__mdptr, dkbr__krjj, col_indices,
                        partition_names, unlg__jge, upnj__mginb) = typ.schema
                    wfrx__pnso = True
            if not wfrx__pnso:
                (col_names, imnmq__mdptr, dkbr__krjj, col_indices,
                    partition_names, unlg__jge, upnj__mginb) = (
                    parquet_file_schema(xkvi__frkt, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            wgzt__uydq = list(fzr__zqlo.keys())
            baag__nvrm = {c: wcnjp__zlbd for wcnjp__zlbd, c in enumerate(
                wgzt__uydq)}
            awo__igdc = [fcsc__ble for fcsc__ble in fzr__zqlo.values()]
            dkbr__krjj = 'index' if 'index' in baag__nvrm else None
            if columns is None:
                selected_columns = wgzt__uydq
            else:
                selected_columns = columns
            col_indices = [baag__nvrm[c] for c in selected_columns]
            imnmq__mdptr = [awo__igdc[baag__nvrm[c]] for c in selected_columns]
            col_names = selected_columns
            dkbr__krjj = dkbr__krjj if dkbr__krjj in col_names else None
            partition_names = []
            unlg__jge = []
            upnj__mginb = []
        ustyn__ztmj = None if isinstance(dkbr__krjj, dict
            ) or dkbr__krjj is None else dkbr__krjj
        index_column_index = None
        index_column_type = types.none
        if ustyn__ztmj:
            pvjei__yec = col_names.index(ustyn__ztmj)
            index_column_index = col_indices.pop(pvjei__yec)
            index_column_type = imnmq__mdptr.pop(pvjei__yec)
            col_names.pop(pvjei__yec)
        for wcnjp__zlbd, c in enumerate(col_names):
            if c in dpiv__gggye:
                imnmq__mdptr[wcnjp__zlbd] = dpiv__gggye[c]
        fxf__zwop = [ir.Var(ycj__ftrn, mk_unique_var('pq_table'),
            dofsn__ttip), ir.Var(ycj__ftrn, mk_unique_var('pq_index'),
            dofsn__ttip)]
        ltj__dqqz = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, imnmq__mdptr, fxf__zwop, dofsn__ttip,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, unlg__jge, upnj__mginb)]
        return (col_names, fxf__zwop, dkbr__krjj, ltj__dqqz, imnmq__mdptr,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    nhn__txugw = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    korvu__lfk, tla__azpvp = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(korvu__lfk.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, korvu__lfk, tla__azpvp, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet')
    yascl__xhewh = ', '.join(f'out{wcnjp__zlbd}' for wcnjp__zlbd in range(
        nhn__txugw))
    itrya__qbs = f'def pq_impl(fname, {extra_args}):\n'
    itrya__qbs += (
        f'    (total_rows, {yascl__xhewh},) = _pq_reader_py(fname, {extra_args})\n'
        )
    ffgr__omqod = {}
    exec(itrya__qbs, {}, ffgr__omqod)
    jzsue__ouyac = ffgr__omqod['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        xbx__yama = pq_node.loc.strformat()
        dtwzh__ifqm = []
        ntme__srcl = []
        for wcnjp__zlbd in pq_node.out_used_cols:
            ucpqk__anjfk = pq_node.df_colnames[wcnjp__zlbd]
            dtwzh__ifqm.append(ucpqk__anjfk)
            if isinstance(pq_node.out_types[wcnjp__zlbd], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                ntme__srcl.append(ucpqk__anjfk)
        klc__ypa = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', klc__ypa, xbx__yama,
            dtwzh__ifqm)
        if ntme__srcl:
            nhgj__lqcoc = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                nhgj__lqcoc, xbx__yama, ntme__srcl)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        zivy__dwy = set(pq_node.out_used_cols)
        bzv__hyy = set(pq_node.unsupported_columns)
        qpxji__stg = zivy__dwy & bzv__hyy
        if qpxji__stg:
            kmq__iypr = sorted(qpxji__stg)
            atx__vcwj = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            xnbe__fkty = 0
            for ukefb__poqw in kmq__iypr:
                while pq_node.unsupported_columns[xnbe__fkty] != ukefb__poqw:
                    xnbe__fkty += 1
                atx__vcwj.append(
                    f"Column '{pq_node.df_colnames[ukefb__poqw]}' with unsupported arrow type {pq_node.unsupported_arrow_types[xnbe__fkty]}"
                    )
                xnbe__fkty += 1
            sas__lgdxa = '\n'.join(atx__vcwj)
            raise BodoError(sas__lgdxa, loc=pq_node.loc)
    kbrt__mtyc = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    hhfot__angi = typemap[pq_node.file_name.name]
    tym__arixo = (hhfot__angi,) + tuple(typemap[gwc__amv.name] for gwc__amv in
        tla__azpvp)
    vgff__loma = compile_to_numba_ir(jzsue__ouyac, {'_pq_reader_py':
        kbrt__mtyc}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        tym__arixo, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(vgff__loma, [pq_node.file_name] + tla__azpvp)
    ltj__dqqz = vgff__loma.body[:-3]
    if meta_head_only_info:
        ltj__dqqz[-1 - nhn__txugw].target = meta_head_only_info[1]
    ltj__dqqz[-2].target = pq_node.out_vars[0]
    ltj__dqqz[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        ltj__dqqz.pop(-1)
    elif not pq_node.out_used_cols:
        ltj__dqqz.pop(-2)
    return ltj__dqqz


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    xaax__lkwh = get_overload_const_str(dnf_filter_str)
    rtpf__euaqx = get_overload_const_str(expr_filter_str)
    fns__renra = ', '.join(f'f{wcnjp__zlbd}' for wcnjp__zlbd in range(len(
        var_tup)))
    itrya__qbs = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        itrya__qbs += f'  {fns__renra}, = var_tup\n'
    itrya__qbs += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    itrya__qbs += f'    dnf_filters_py = {xaax__lkwh}\n'
    itrya__qbs += f'    expr_filters_py = {rtpf__euaqx}\n'
    itrya__qbs += '  return (dnf_filters_py, expr_filters_py)\n'
    ffgr__omqod = {}
    exec(itrya__qbs, globals(), ffgr__omqod)
    return ffgr__omqod['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    ees__pyahm = next_label()
    rsj__mtlng = ',' if extra_args else ''
    itrya__qbs = f'def pq_reader_py(fname,{extra_args}):\n'
    itrya__qbs += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    itrya__qbs += f"    ev.add_attribute('g_fname', fname)\n"
    itrya__qbs += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    itrya__qbs += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{rsj__mtlng}))
"""
    itrya__qbs += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    itrya__qbs += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    ciz__sfggo = not out_used_cols
    llq__xti = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    lerc__bysx = {c: wcnjp__zlbd for wcnjp__zlbd, c in enumerate(col_indices)}
    kpiqi__eptuu = {c: wcnjp__zlbd for wcnjp__zlbd, c in enumerate(llq__xti)}
    nmch__waq = []
    hsqmp__nbl = set()
    jmb__podh = partition_names + [input_file_name_col]
    for wcnjp__zlbd in out_used_cols:
        if llq__xti[wcnjp__zlbd] not in jmb__podh:
            nmch__waq.append(col_indices[wcnjp__zlbd])
        elif not input_file_name_col or llq__xti[wcnjp__zlbd
            ] != input_file_name_col:
            hsqmp__nbl.add(col_indices[wcnjp__zlbd])
    if index_column_index is not None:
        nmch__waq.append(index_column_index)
    nmch__waq = sorted(nmch__waq)
    tjefz__qqjb = {c: wcnjp__zlbd for wcnjp__zlbd, c in enumerate(nmch__waq)}
    qzt__umsm = [(int(is_nullable(out_types[lerc__bysx[ouwc__meuaa]])) if 
        ouwc__meuaa != index_column_index else int(is_nullable(
        index_column_type))) for ouwc__meuaa in nmch__waq]
    str_as_dict_cols = []
    for ouwc__meuaa in nmch__waq:
        if ouwc__meuaa == index_column_index:
            fcsc__ble = index_column_type
        else:
            fcsc__ble = out_types[lerc__bysx[ouwc__meuaa]]
        if fcsc__ble == dict_str_arr_type:
            str_as_dict_cols.append(ouwc__meuaa)
    tjy__gdgim = []
    ewju__fjy = {}
    tmdk__sbnox = []
    pghl__rky = []
    for wcnjp__zlbd, rlmcq__scpo in enumerate(partition_names):
        try:
            zubty__arvjr = kpiqi__eptuu[rlmcq__scpo]
            if col_indices[zubty__arvjr] not in hsqmp__nbl:
                continue
        except (KeyError, ValueError) as vaibm__yrjy:
            continue
        ewju__fjy[rlmcq__scpo] = len(tjy__gdgim)
        tjy__gdgim.append(rlmcq__scpo)
        tmdk__sbnox.append(wcnjp__zlbd)
        ofp__gawtu = out_types[zubty__arvjr].dtype
        zfhp__urt = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            ofp__gawtu)
        pghl__rky.append(numba_to_c_type(zfhp__urt))
    itrya__qbs += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    itrya__qbs += f'    out_table = pq_read(\n'
    itrya__qbs += f'        fname_py, {is_parallel},\n'
    itrya__qbs += f'        unicode_to_utf8(bucket_region),\n'
    itrya__qbs += f'        dnf_filters, expr_filters,\n'
    itrya__qbs += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{ees__pyahm}.ctypes,
"""
    itrya__qbs += f'        {len(nmch__waq)},\n'
    itrya__qbs += f'        nullable_cols_arr_{ees__pyahm}.ctypes,\n'
    if len(tmdk__sbnox) > 0:
        itrya__qbs += (
            f'        np.array({tmdk__sbnox}, dtype=np.int32).ctypes,\n')
        itrya__qbs += (
            f'        np.array({pghl__rky}, dtype=np.int32).ctypes,\n')
        itrya__qbs += f'        {len(tmdk__sbnox)},\n'
    else:
        itrya__qbs += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        itrya__qbs += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        itrya__qbs += f'        0, 0,\n'
    itrya__qbs += f'        total_rows_np.ctypes,\n'
    itrya__qbs += f'        {input_file_name_col is not None},\n'
    itrya__qbs += f'    )\n'
    itrya__qbs += f'    check_and_propagate_cpp_exception()\n'
    prbfe__pclc = 'None'
    eykr__fwi = index_column_type
    ewe__wto = TableType(tuple(out_types))
    if ciz__sfggo:
        ewe__wto = types.none
    if index_column_index is not None:
        wefvv__ulzo = tjefz__qqjb[index_column_index]
        prbfe__pclc = (
            f'info_to_array(info_from_table(out_table, {wefvv__ulzo}), index_arr_type)'
            )
    itrya__qbs += f'    index_arr = {prbfe__pclc}\n'
    if ciz__sfggo:
        kytyd__fqho = None
    else:
        kytyd__fqho = []
        dcils__flnsu = 0
        evmm__dngpe = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for wcnjp__zlbd, ukefb__poqw in enumerate(col_indices):
            if dcils__flnsu < len(out_used_cols
                ) and wcnjp__zlbd == out_used_cols[dcils__flnsu]:
                ubqa__bwfr = col_indices[wcnjp__zlbd]
                if evmm__dngpe and ubqa__bwfr == evmm__dngpe:
                    kytyd__fqho.append(len(nmch__waq) + len(tjy__gdgim))
                elif ubqa__bwfr in hsqmp__nbl:
                    yhpkn__fbc = llq__xti[wcnjp__zlbd]
                    kytyd__fqho.append(len(nmch__waq) + ewju__fjy[yhpkn__fbc])
                else:
                    kytyd__fqho.append(tjefz__qqjb[ukefb__poqw])
                dcils__flnsu += 1
            else:
                kytyd__fqho.append(-1)
        kytyd__fqho = np.array(kytyd__fqho, dtype=np.int64)
    if ciz__sfggo:
        itrya__qbs += '    T = None\n'
    else:
        itrya__qbs += f"""    T = cpp_table_to_py_table(out_table, table_idx_{ees__pyahm}, py_table_type_{ees__pyahm})
"""
    itrya__qbs += f'    delete_table(out_table)\n'
    itrya__qbs += f'    total_rows = total_rows_np[0]\n'
    itrya__qbs += f'    ev.finalize()\n'
    itrya__qbs += f'    return (total_rows, T, index_arr)\n'
    ffgr__omqod = {}
    sim__ngmbr = {f'py_table_type_{ees__pyahm}': ewe__wto,
        f'table_idx_{ees__pyahm}': kytyd__fqho,
        f'selected_cols_arr_{ees__pyahm}': np.array(nmch__waq, np.int32),
        f'nullable_cols_arr_{ees__pyahm}': np.array(qzt__umsm, np.int32),
        'index_arr_type': eykr__fwi, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(itrya__qbs, sim__ngmbr, ffgr__omqod)
    kbrt__mtyc = ffgr__omqod['pq_reader_py']
    plyn__ofk = numba.njit(kbrt__mtyc, no_cpython_wrapper=True)
    return plyn__ofk


import pyarrow as pa
_pa_numba_typ_map = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.
    int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.int64,
    pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32(): types.
    uint32, pa.uint64(): types.uint64, pa.float32(): types.float32, pa.
    float64(): types.float64, pa.string(): string_type, pa.binary():
    bytes_type, pa.date32(): datetime_date_type, pa.date64(): types.
    NPDatetime('ns'), null(): string_type}


def get_arrow_timestamp_type(pa_ts_typ):
    uhf__hjzjj = 'ns', 'us', 'ms', 's'
    if pa_ts_typ.unit not in uhf__hjzjj:
        return types.Array(bodo.datetime64ns, 1, 'C'), False
    elif pa_ts_typ.tz is not None:
        lew__kruvc = pa_ts_typ.to_pandas_dtype().tz
        jfyg__rhj = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(lew__kruvc
            )
        return bodo.DatetimeArrayType(jfyg__rhj), True
    else:
        return types.Array(bodo.datetime64ns, 1, 'C'), True


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info, str_as_dict=False):
    if isinstance(pa_typ.type, pa.ListType):
        omljd__tcv, doym__ifv = _get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info)
        return ArrayItemArrayType(omljd__tcv), doym__ifv
    if isinstance(pa_typ.type, pa.StructType):
        fdzl__jrto = []
        tspii__wusf = []
        doym__ifv = True
        for yqof__qhj in pa_typ.flatten():
            tspii__wusf.append(yqof__qhj.name.split('.')[-1])
            hkxn__ffcd, abh__vzxp = _get_numba_typ_from_pa_typ(yqof__qhj,
                is_index, nullable_from_metadata, category_info)
            fdzl__jrto.append(hkxn__ffcd)
            doym__ifv = doym__ifv and abh__vzxp
        return StructArrayType(tuple(fdzl__jrto), tuple(tspii__wusf)
            ), doym__ifv
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale), True
    if str_as_dict:
        if pa_typ.type != pa.string():
            raise BodoError(
                f'Read as dictionary used for non-string column {pa_typ}')
        return dict_str_arr_type, True
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        xfxqb__mguo = _pa_numba_typ_map[pa_typ.type.index_type]
        jdh__dnar = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=xfxqb__mguo)
        return CategoricalArrayType(jdh__dnar), True
    if isinstance(pa_typ.type, pa.lib.TimestampType):
        return get_arrow_timestamp_type(pa_typ.type)
    elif pa_typ.type in _pa_numba_typ_map:
        aihe__boq = _pa_numba_typ_map[pa_typ.type]
        doym__ifv = True
    else:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    if aihe__boq == datetime_date_type:
        return datetime_date_array_type, doym__ifv
    if aihe__boq == bytes_type:
        return binary_array_type, doym__ifv
    omljd__tcv = (string_array_type if aihe__boq == string_type else types.
        Array(aihe__boq, 1, 'C'))
    if aihe__boq == types.bool_:
        omljd__tcv = boolean_array
    if nullable_from_metadata is not None:
        mmc__uiplf = nullable_from_metadata
    else:
        mmc__uiplf = use_nullable_int_arr
    if mmc__uiplf and not is_index and isinstance(aihe__boq, types.Integer
        ) and pa_typ.nullable:
        omljd__tcv = IntegerArrayType(aihe__boq)
    return omljd__tcv, doym__ifv


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None, typing_pa_schema=None):
    if get_row_counts:
        oknu__tkwrr = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    ese__ktqz = MPI.COMM_WORLD
    if isinstance(fpath, list):
        ncb__fcfg = urlparse(fpath[0])
        protocol = ncb__fcfg.scheme
        ccra__vfq = ncb__fcfg.netloc
        for wcnjp__zlbd in range(len(fpath)):
            qwpyo__syt = fpath[wcnjp__zlbd]
            sardc__sibnc = urlparse(qwpyo__syt)
            if sardc__sibnc.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if sardc__sibnc.netloc != ccra__vfq:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[wcnjp__zlbd] = qwpyo__syt.rstrip('/')
    else:
        ncb__fcfg = urlparse(fpath)
        protocol = ncb__fcfg.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as vaibm__yrjy:
            xhvc__qbnao = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(xhvc__qbnao)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as vaibm__yrjy:
            xhvc__qbnao = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    fs = []

    def getfs(parallel=False):
        if len(fs) == 1:
            return fs[0]
        if protocol == 's3':
            fs.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif protocol in {'gcs', 'gs'}:
            zaezb__cchzk = gcsfs.GCSFileSystem(token=None)
            fs.append(zaezb__cchzk)
        elif protocol == 'http':
            fs.append(fsspec.filesystem('http'))
        elif protocol in {'hdfs', 'abfs', 'abfss'}:
            fs.append(get_hdfs_fs(fpath) if not isinstance(fpath, list) else
                get_hdfs_fs(fpath[0]))
        else:
            fs.append(None)
        return fs[0]

    def get_legacy_fs():
        if protocol in {'s3', 'hdfs', 'abfs', 'abfss'}:
            from fsspec.implementations.arrow import ArrowFSWrapper
            return ArrowFSWrapper(getfs())
        else:
            return getfs()

    def glob(protocol, fs, path):
        if not protocol and fs is None:
            from fsspec.implementations.local import LocalFileSystem
            fs = LocalFileSystem()
        if isinstance(fs, pyarrow.fs.FileSystem):
            from fsspec.implementations.arrow import ArrowFSWrapper
            fs = ArrowFSWrapper(fs)
        try:
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{ncb__fcfg.netloc}'
                path = path[len(prefix):]
            wqaj__kcut = fs.glob(path)
            if protocol == 's3':
                wqaj__kcut = [('s3://' + qwpyo__syt) for qwpyo__syt in
                    wqaj__kcut if not qwpyo__syt.startswith('s3://')]
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                wqaj__kcut = [(prefix + qwpyo__syt) for qwpyo__syt in
                    wqaj__kcut]
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(wqaj__kcut) == 0:
            raise BodoError('No files found matching glob pattern')
        return wqaj__kcut
    jleoy__xpl = False
    if get_row_counts:
        yzql__ued = getfs(parallel=True)
        jleoy__xpl = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        noyg__pcbww = 1
        puak__msjq = os.cpu_count()
        if puak__msjq is not None and puak__msjq > 1:
            noyg__pcbww = puak__msjq // 2
        try:
            if get_row_counts:
                zlm__wuby = tracing.Event('pq.ParquetDataset', is_parallel=
                    False)
                if tracing.is_tracing():
                    zlm__wuby.add_attribute('g_dnf_filter', str(dnf_filters))
            zrk__ayj = pa.io_thread_count()
            pa.set_io_thread_count(noyg__pcbww)
            if isinstance(fpath, list):
                dzdrw__kacd = []
                for vvecs__waofw in fpath:
                    if has_magic(vvecs__waofw):
                        dzdrw__kacd += glob(protocol, getfs(), vvecs__waofw)
                    else:
                        dzdrw__kacd.append(vvecs__waofw)
                fpath = dzdrw__kacd
            elif has_magic(fpath):
                fpath = glob(protocol, getfs(), fpath)
            if protocol == 's3':
                if isinstance(fpath, list):
                    get_legacy_fs().info(fpath[0])
                else:
                    get_legacy_fs().info(fpath)
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{ncb__fcfg.netloc}'
                if isinstance(fpath, list):
                    pwijd__xkhu = [qwpyo__syt[len(prefix):] for qwpyo__syt in
                        fpath]
                else:
                    pwijd__xkhu = fpath[len(prefix):]
            else:
                pwijd__xkhu = fpath
            ajosh__dash = pq.ParquetDataset(pwijd__xkhu, filesystem=
                get_legacy_fs(), filters=None, use_legacy_dataset=True,
                validate_schema=False, metadata_nthreads=noyg__pcbww)
            pa.set_io_thread_count(zrk__ayj)
            if typing_pa_schema:
                ixlc__fmhu = typing_pa_schema
            else:
                ixlc__fmhu = bodo.io.pa_parquet.get_dataset_schema(ajosh__dash)
            if dnf_filters:
                if get_row_counts:
                    zlm__wuby.add_attribute('num_pieces_before_filter', len
                        (ajosh__dash.pieces))
                cvcs__ttl = time.time()
                ajosh__dash._filter(dnf_filters)
                if get_row_counts:
                    zlm__wuby.add_attribute('dnf_filter_time', time.time() -
                        cvcs__ttl)
                    zlm__wuby.add_attribute('num_pieces_after_filter', len(
                        ajosh__dash.pieces))
            if get_row_counts:
                zlm__wuby.finalize()
            ajosh__dash._metadata.fs = None
        except Exception as afp__njql:
            if isinstance(fpath, list) and isinstance(afp__njql, (OSError,
                FileNotFoundError)):
                afp__njql = BodoError(str(afp__njql) + list_of_files_error_msg)
            else:
                afp__njql = BodoError(
                    f"""error from pyarrow: {type(afp__njql).__name__}: {str(afp__njql)}
"""
                    )
            ese__ktqz.bcast(afp__njql)
            raise afp__njql
        if get_row_counts:
            mbrgz__xfa = tracing.Event('bcast dataset')
        ese__ktqz.bcast(ajosh__dash)
        ese__ktqz.bcast(ixlc__fmhu)
    else:
        if get_row_counts:
            mbrgz__xfa = tracing.Event('bcast dataset')
        ajosh__dash = ese__ktqz.bcast(None)
        if isinstance(ajosh__dash, Exception):
            jxfo__grqjq = ajosh__dash
            raise jxfo__grqjq
        ixlc__fmhu = ese__ktqz.bcast(None)
    pbx__cxse = set(ixlc__fmhu.names)
    if get_row_counts:
        aqid__emjrx = getfs()
    else:
        aqid__emjrx = get_legacy_fs()
    ajosh__dash._metadata.fs = aqid__emjrx
    if get_row_counts:
        mbrgz__xfa.finalize()
    ajosh__dash._bodo_total_rows = 0
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = jleoy__xpl = False
        for vvecs__waofw in ajosh__dash.pieces:
            vvecs__waofw._bodo_num_rows = 0
    if get_row_counts or jleoy__xpl:
        if get_row_counts and tracing.is_tracing():
            nwxx__reeqe = tracing.Event('get_row_counts')
            nwxx__reeqe.add_attribute('g_num_pieces', len(ajosh__dash.pieces))
            nwxx__reeqe.add_attribute('g_expr_filters', str(expr_filters))
        huit__saqyl = 0.0
        num_pieces = len(ajosh__dash.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        mio__pze = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        rbp__lla = 0
        edgd__foyr = 0
        epxb__hka = 0
        wxy__fstnc = True
        if expr_filters is not None:
            import random
            random.seed(37)
            drp__vxyci = random.sample(ajosh__dash.pieces, k=len(
                ajosh__dash.pieces))
        else:
            drp__vxyci = ajosh__dash.pieces
        for vvecs__waofw in drp__vxyci:
            vvecs__waofw._bodo_num_rows = 0
        fpaths = [vvecs__waofw.path for vvecs__waofw in drp__vxyci[start:
            mio__pze]]
        if protocol == 's3':
            ccra__vfq = ncb__fcfg.netloc
            prefix = 's3://' + ccra__vfq + '/'
            fpaths = [qwpyo__syt[len(prefix):] for qwpyo__syt in fpaths]
            aqid__emjrx = get_s3_subtree_fs(ccra__vfq, region=getfs().
                region, storage_options=storage_options)
        else:
            aqid__emjrx = getfs()
        noyg__pcbww = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(noyg__pcbww)
        pa.set_cpu_count(noyg__pcbww)
        jxfo__grqjq = None
        try:
            jbznd__czg = ds.dataset(fpaths, filesystem=aqid__emjrx,
                partitioning=ds.partitioning(flavor='hive') if ajosh__dash.
                partitions else None)
            for ywnlw__uouy, xwsja__bfn in zip(drp__vxyci[start:mio__pze],
                jbznd__czg.get_fragments()):
                if jleoy__xpl:
                    ksohw__pol = xwsja__bfn.metadata.schema.to_arrow_schema()
                    rtw__rwvl = set(ksohw__pol.names)
                    if pbx__cxse != rtw__rwvl:
                        rfudb__qmo = rtw__rwvl - pbx__cxse
                        wem__mele = pbx__cxse - rtw__rwvl
                        zysz__zcjgz = (
                            f'Schema in {ywnlw__uouy} was different.\n')
                        if rfudb__qmo:
                            zysz__zcjgz += f"""File contains column(s) {rfudb__qmo} not found in other files in the dataset.
"""
                        if wem__mele:
                            zysz__zcjgz += f"""File missing column(s) {wem__mele} found in other files in the dataset.
"""
                        raise BodoError(zysz__zcjgz)
                    try:
                        ixlc__fmhu = pa.unify_schemas([ixlc__fmhu, ksohw__pol])
                    except Exception as afp__njql:
                        zysz__zcjgz = (
                            f'Schema in {ywnlw__uouy} was different.\n' +
                            str(afp__njql))
                        raise BodoError(zysz__zcjgz)
                cvcs__ttl = time.time()
                zwi__exa = xwsja__bfn.scanner(schema=jbznd__czg.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                huit__saqyl += time.time() - cvcs__ttl
                ywnlw__uouy._bodo_num_rows = zwi__exa
                rbp__lla += zwi__exa
                edgd__foyr += xwsja__bfn.num_row_groups
                epxb__hka += sum(jfhy__vki.total_byte_size for jfhy__vki in
                    xwsja__bfn.row_groups)
        except Exception as afp__njql:
            jxfo__grqjq = afp__njql
        if ese__ktqz.allreduce(jxfo__grqjq is not None, op=MPI.LOR):
            for jxfo__grqjq in ese__ktqz.allgather(jxfo__grqjq):
                if jxfo__grqjq:
                    if isinstance(fpath, list) and isinstance(jxfo__grqjq,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(jxfo__grqjq) +
                            list_of_files_error_msg)
                    raise jxfo__grqjq
        if jleoy__xpl:
            wxy__fstnc = ese__ktqz.allreduce(wxy__fstnc, op=MPI.LAND)
            if not wxy__fstnc:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            ajosh__dash._bodo_total_rows = ese__ktqz.allreduce(rbp__lla, op
                =MPI.SUM)
            gjmh__eskq = ese__ktqz.allreduce(edgd__foyr, op=MPI.SUM)
            llnxw__ebt = ese__ktqz.allreduce(epxb__hka, op=MPI.SUM)
            ifwu__iuv = np.array([vvecs__waofw._bodo_num_rows for
                vvecs__waofw in ajosh__dash.pieces])
            ifwu__iuv = ese__ktqz.allreduce(ifwu__iuv, op=MPI.SUM)
            for vvecs__waofw, fyd__hidm in zip(ajosh__dash.pieces, ifwu__iuv):
                vvecs__waofw._bodo_num_rows = fyd__hidm
            if is_parallel and bodo.get_rank(
                ) == 0 and gjmh__eskq < bodo.get_size() and gjmh__eskq != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({gjmh__eskq}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if gjmh__eskq == 0:
                jppnt__kwrqp = 0
            else:
                jppnt__kwrqp = llnxw__ebt // gjmh__eskq
            if (bodo.get_rank() == 0 and llnxw__ebt >= 20 * 1048576 and 
                jppnt__kwrqp < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({jppnt__kwrqp} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                nwxx__reeqe.add_attribute('g_total_num_row_groups', gjmh__eskq)
                nwxx__reeqe.add_attribute('total_scan_time', huit__saqyl)
                tjtpr__inuvh = np.array([vvecs__waofw._bodo_num_rows for
                    vvecs__waofw in ajosh__dash.pieces])
                byix__yei = np.percentile(tjtpr__inuvh, [25, 50, 75])
                nwxx__reeqe.add_attribute('g_row_counts_min', tjtpr__inuvh.
                    min())
                nwxx__reeqe.add_attribute('g_row_counts_Q1', byix__yei[0])
                nwxx__reeqe.add_attribute('g_row_counts_median', byix__yei[1])
                nwxx__reeqe.add_attribute('g_row_counts_Q3', byix__yei[2])
                nwxx__reeqe.add_attribute('g_row_counts_max', tjtpr__inuvh.
                    max())
                nwxx__reeqe.add_attribute('g_row_counts_mean', tjtpr__inuvh
                    .mean())
                nwxx__reeqe.add_attribute('g_row_counts_std', tjtpr__inuvh.
                    std())
                nwxx__reeqe.add_attribute('g_row_counts_sum', tjtpr__inuvh.
                    sum())
                nwxx__reeqe.finalize()
    ajosh__dash._prefix = ''
    if protocol in {'hdfs', 'abfs', 'abfss'}:
        prefix = f'{protocol}://{ncb__fcfg.netloc}'
        if len(ajosh__dash.pieces) > 0:
            ywnlw__uouy = ajosh__dash.pieces[0]
            if not ywnlw__uouy.path.startswith(prefix):
                ajosh__dash._prefix = prefix
    if read_categories:
        _add_categories_to_pq_dataset(ajosh__dash)
    if get_row_counts:
        oknu__tkwrr.finalize()
    if jleoy__xpl and is_parallel:
        if tracing.is_tracing():
            bjq__yctt = tracing.Event('unify_schemas_across_ranks')
        jxfo__grqjq = None
        try:
            ixlc__fmhu = ese__ktqz.allreduce(ixlc__fmhu, bodo.io.helpers.
                pa_schema_unify_mpi_op)
        except Exception as afp__njql:
            jxfo__grqjq = afp__njql
        if tracing.is_tracing():
            bjq__yctt.finalize()
        if ese__ktqz.allreduce(jxfo__grqjq is not None, op=MPI.LOR):
            for jxfo__grqjq in ese__ktqz.allgather(jxfo__grqjq):
                if jxfo__grqjq:
                    zysz__zcjgz = (
                        f'Schema in some files were different.\n' + str(
                        jxfo__grqjq))
                    raise BodoError(zysz__zcjgz)
    ajosh__dash._bodo_arrow_schema = ixlc__fmhu
    return ajosh__dash


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region, prefix,
    str_as_dict_cols, start_offset, rows_to_read, has_partitions, schema):
    import pyarrow as pa
    puak__msjq = os.cpu_count()
    if puak__msjq is None or puak__msjq == 0:
        puak__msjq = 2
    vdw__okbj = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), puak__msjq)
    raira__old = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), puak__msjq
        )
    if is_parallel and len(fpaths) > raira__old and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(raira__old)
        pa.set_cpu_count(raira__old)
    else:
        pa.set_io_thread_count(vdw__okbj)
        pa.set_cpu_count(vdw__okbj)
    if fpaths[0].startswith('s3://'):
        ccra__vfq = urlparse(fpaths[0]).netloc
        prefix = 's3://' + ccra__vfq + '/'
        fpaths = [qwpyo__syt[len(prefix):] for qwpyo__syt in fpaths]
        if region == '':
            region = get_s3_bucket_region_njit(fpaths[0], parallel=False)
        aqid__emjrx = get_s3_subtree_fs(ccra__vfq, region=region,
            storage_options=storage_options)
    elif prefix and prefix.startswith(('hdfs', 'abfs', 'abfss')):
        aqid__emjrx = get_hdfs_fs(prefix + fpaths[0])
    elif fpaths[0].startswith(('gcs', 'gs')):
        import gcsfs
        aqid__emjrx = gcsfs.GCSFileSystem(token=None)
    else:
        aqid__emjrx = None
    fvb__xkwgd = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    ajosh__dash = ds.dataset(fpaths, filesystem=aqid__emjrx, partitioning=
        ds.partitioning(flavor='hive') if has_partitions else None, format=
        fvb__xkwgd)
    ttdr__hpccx = set(str_as_dict_cols)
    wampz__jqrn = schema.names
    for wcnjp__zlbd, name in enumerate(wampz__jqrn):
        if name in ttdr__hpccx:
            ydf__xwmq = schema.field(wcnjp__zlbd)
            fmwf__udsl = pa.field(name, pa.dictionary(pa.int32(), ydf__xwmq
                .type), ydf__xwmq.nullable)
            schema = schema.remove(wcnjp__zlbd).insert(wcnjp__zlbd, fmwf__udsl)
    ajosh__dash = ajosh__dash.replace_schema(pa.unify_schemas([ajosh__dash.
        schema, schema]))
    col_names = ajosh__dash.schema.names
    yya__odbtl = [col_names[mgm__zwa] for mgm__zwa in selected_fields]
    bam__ulql = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if bam__ulql and expr_filters is None:
        rfdk__ernnd = []
        eqgp__xlwae = 0
        urja__kguk = 0
        for xwsja__bfn in ajosh__dash.get_fragments():
            xlb__onl = []
            for jfhy__vki in xwsja__bfn.row_groups:
                povi__cyx = jfhy__vki.num_rows
                if start_offset < eqgp__xlwae + povi__cyx:
                    if urja__kguk == 0:
                        qwldt__una = start_offset - eqgp__xlwae
                        igu__kbf = min(povi__cyx - qwldt__una, rows_to_read)
                    else:
                        igu__kbf = min(povi__cyx, rows_to_read - urja__kguk)
                    urja__kguk += igu__kbf
                    xlb__onl.append(jfhy__vki.id)
                eqgp__xlwae += povi__cyx
                if urja__kguk == rows_to_read:
                    break
            rfdk__ernnd.append(xwsja__bfn.subset(row_group_ids=xlb__onl))
            if urja__kguk == rows_to_read:
                break
        ajosh__dash = ds.FileSystemDataset(rfdk__ernnd, ajosh__dash.schema,
            fvb__xkwgd, filesystem=ajosh__dash.filesystem)
        start_offset = qwldt__una
    uezbv__diwo = ajosh__dash.scanner(columns=yya__odbtl, filter=
        expr_filters, use_threads=True).to_reader()
    return ajosh__dash, uezbv__diwo, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema.to_arrow_schema()
    uivem__ayaw = [c for c in pa_schema.names if isinstance(pa_schema.field
        (c).type, pa.DictionaryType)]
    if len(uivem__ayaw) == 0:
        pq_dataset._category_info = {}
        return
    ese__ktqz = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            bxbni__fddw = pq_dataset.pieces[0].open()
            jfhy__vki = bxbni__fddw.read_row_group(0, uivem__ayaw)
            category_info = {c: tuple(jfhy__vki.column(c).chunk(0).
                dictionary.to_pylist()) for c in uivem__ayaw}
            del bxbni__fddw, jfhy__vki
        except Exception as afp__njql:
            ese__ktqz.bcast(afp__njql)
            raise afp__njql
        ese__ktqz.bcast(category_info)
    else:
        category_info = ese__ktqz.bcast(None)
        if isinstance(category_info, Exception):
            jxfo__grqjq = category_info
            raise jxfo__grqjq
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    dkbr__krjj = None
    nullable_from_metadata = defaultdict(lambda : None)
    fqw__pcrs = b'pandas'
    if schema.metadata is not None and fqw__pcrs in schema.metadata:
        import json
        ohf__wctf = json.loads(schema.metadata[fqw__pcrs].decode('utf8'))
        myw__ffahm = len(ohf__wctf['index_columns'])
        if myw__ffahm > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        dkbr__krjj = ohf__wctf['index_columns'][0] if myw__ffahm else None
        if not isinstance(dkbr__krjj, str) and not isinstance(dkbr__krjj, dict
            ):
            dkbr__krjj = None
        for ncif__jcl in ohf__wctf['columns']:
            grwu__ehfaw = ncif__jcl['name']
            if ncif__jcl['pandas_type'].startswith('int'
                ) and grwu__ehfaw is not None:
                if ncif__jcl['numpy_type'].startswith('Int'):
                    nullable_from_metadata[grwu__ehfaw] = True
                else:
                    nullable_from_metadata[grwu__ehfaw] = False
    return dkbr__krjj, nullable_from_metadata


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for grwu__ehfaw in pa_schema.names:
        yqof__qhj = pa_schema.field(grwu__ehfaw)
        if yqof__qhj.type == pa.string():
            str_columns.append(grwu__ehfaw)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    ese__ktqz = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        drp__vxyci = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        drp__vxyci = pq_dataset.pieces
    sua__azhs = np.zeros(len(str_columns), dtype=np.int64)
    ltc__hgklc = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(drp__vxyci):
        ywnlw__uouy = drp__vxyci[bodo.get_rank()]
        try:
            mntmk__kdoww = ywnlw__uouy.get_metadata()
            for wcnjp__zlbd in range(mntmk__kdoww.num_row_groups):
                for dcils__flnsu, grwu__ehfaw in enumerate(str_columns):
                    xnbe__fkty = pa_schema.get_field_index(grwu__ehfaw)
                    sua__azhs[dcils__flnsu] += mntmk__kdoww.row_group(
                        wcnjp__zlbd).column(xnbe__fkty).total_uncompressed_size
            mkdbg__edbk = mntmk__kdoww.num_rows
        except Exception as afp__njql:
            if isinstance(afp__njql, (OSError, FileNotFoundError)):
                mkdbg__edbk = 0
            else:
                raise
    else:
        mkdbg__edbk = 0
    ntxe__hgom = ese__ktqz.allreduce(mkdbg__edbk, op=MPI.SUM)
    if ntxe__hgom == 0:
        return set()
    ese__ktqz.Allreduce(sua__azhs, ltc__hgklc, op=MPI.SUM)
    jvb__sjrxu = ltc__hgklc / ntxe__hgom
    str_as_dict = set()
    for wcnjp__zlbd, romuh__goli in enumerate(jvb__sjrxu):
        if romuh__goli < READ_STR_AS_DICT_THRESHOLD:
            grwu__ehfaw = str_columns[wcnjp__zlbd][0]
            str_as_dict.add(grwu__ehfaw)
    return str_as_dict


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    imnmq__mdptr = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    if hasattr(pq_dataset, '_bodo_arrow_schema'):
        pa_schema = pq_dataset._bodo_arrow_schema
    else:
        pa_schema = pq_dataset.schema.to_arrow_schema()
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[wcnjp__zlbd].name for wcnjp__zlbd in range(len(
        pq_dataset.partitions.partition_names))]
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    eqrc__vzkek = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    vlh__djsu = read_as_dict_cols - eqrc__vzkek
    if len(vlh__djsu) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {vlh__djsu}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(eqrc__vzkek)
    eqrc__vzkek = eqrc__vzkek - read_as_dict_cols
    str_columns = [nfyq__yhnkq for nfyq__yhnkq in str_columns if 
        nfyq__yhnkq in eqrc__vzkek]
    str_as_dict: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    str_as_dict.update(read_as_dict_cols)
    col_names = pa_schema.names
    dkbr__krjj, nullable_from_metadata = get_pandas_metadata(pa_schema,
        num_pieces)
    awo__igdc = []
    jmy__viubt = []
    mmnl__zlnwq = []
    for wcnjp__zlbd, c in enumerate(col_names):
        yqof__qhj = pa_schema.field(c)
        aihe__boq, doym__ifv = _get_numba_typ_from_pa_typ(yqof__qhj, c ==
            dkbr__krjj, nullable_from_metadata[c], pq_dataset.
            _category_info, str_as_dict=c in str_as_dict)
        awo__igdc.append(aihe__boq)
        jmy__viubt.append(doym__ifv)
        mmnl__zlnwq.append(yqof__qhj.type)
    if partition_names:
        col_names += partition_names
        awo__igdc += [_get_partition_cat_dtype(pq_dataset.partitions.levels
            [wcnjp__zlbd]) for wcnjp__zlbd in range(len(partition_names))]
        jmy__viubt.extend([True] * len(partition_names))
        mmnl__zlnwq.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        awo__igdc += [dict_str_arr_type]
        jmy__viubt.append(True)
        mmnl__zlnwq.append(None)
    hip__ycna = {c: wcnjp__zlbd for wcnjp__zlbd, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in hip__ycna:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if dkbr__krjj and not isinstance(dkbr__krjj, dict
        ) and dkbr__krjj not in selected_columns:
        selected_columns.append(dkbr__krjj)
    col_names = selected_columns
    col_indices = []
    imnmq__mdptr = []
    unlg__jge = []
    upnj__mginb = []
    for wcnjp__zlbd, c in enumerate(col_names):
        ubqa__bwfr = hip__ycna[c]
        col_indices.append(ubqa__bwfr)
        imnmq__mdptr.append(awo__igdc[ubqa__bwfr])
        if not jmy__viubt[ubqa__bwfr]:
            unlg__jge.append(wcnjp__zlbd)
            upnj__mginb.append(mmnl__zlnwq[ubqa__bwfr])
    return (col_names, imnmq__mdptr, dkbr__krjj, col_indices,
        partition_names, unlg__jge, upnj__mginb)


def _get_partition_cat_dtype(part_set):
    pjccl__nkgh = part_set.dictionary.to_pandas()
    ldivu__xcal = bodo.typeof(pjccl__nkgh).dtype
    jdh__dnar = PDCategoricalDtype(tuple(pjccl__nkgh), ldivu__xcal, False)
    return CategoricalArrayType(jdh__dnar)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, types.voidptr,
    parquet_predicate_type, parquet_predicate_type,
    storage_options_dict_type, types.int64, types.voidptr, types.int32,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.voidptr,
    types.int32, types.voidptr, types.boolean))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region, row_group_size):

    def codegen(context, builder, sig, args):
        dpqft__awsfl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        dvon__ytycv = cgutils.get_or_insert_function(builder.module,
            dpqft__awsfl, name='pq_write')
        builder.call(dvon__ytycv, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr,
        types.int64), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region, row_group_size
    ):

    def codegen(context, builder, sig, args):
        dpqft__awsfl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        dvon__ytycv = cgutils.get_or_insert_function(builder.module,
            dpqft__awsfl, name='pq_write_partitioned')
        builder.call(dvon__ytycv, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64), codegen
