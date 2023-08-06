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
        except OSError as pek__nhdje:
            if 'non-file path' in str(pek__nhdje):
                raise FileNotFoundError(str(pek__nhdje))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        pwnqq__mkuu = lhs.scope
        wvf__wgnl = lhs.loc
        qmi__heas = None
        if lhs.name in self.locals:
            qmi__heas = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        aml__rfhel = {}
        if lhs.name + ':convert' in self.locals:
            aml__rfhel = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if qmi__heas is None:
            modm__sfm = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            kbs__psws = get_const_value(file_name, self.func_ir, modm__sfm,
                arg_types=self.args, file_info=ParquetFileInfo(columns,
                storage_options=storage_options, input_file_name_col=
                input_file_name_col, read_as_dict_cols=read_as_dict_cols))
            kvnw__wke = False
            dwnq__pixi = guard(get_definition, self.func_ir, file_name)
            if isinstance(dwnq__pixi, ir.Arg):
                typ = self.args[dwnq__pixi.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, dfdk__dan, mmqu__dral, col_indices,
                        partition_names, dlsll__abkf, ikn__lbes) = typ.schema
                    kvnw__wke = True
            if not kvnw__wke:
                (col_names, dfdk__dan, mmqu__dral, col_indices,
                    partition_names, dlsll__abkf, ikn__lbes) = (
                    parquet_file_schema(kbs__psws, columns, storage_options
                    =storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            ntki__dlr = list(qmi__heas.keys())
            dujk__ilnzc = {c: pep__kux for pep__kux, c in enumerate(ntki__dlr)}
            ylfz__nnsp = [cws__atsgn for cws__atsgn in qmi__heas.values()]
            mmqu__dral = 'index' if 'index' in dujk__ilnzc else None
            if columns is None:
                selected_columns = ntki__dlr
            else:
                selected_columns = columns
            col_indices = [dujk__ilnzc[c] for c in selected_columns]
            dfdk__dan = [ylfz__nnsp[dujk__ilnzc[c]] for c in selected_columns]
            col_names = selected_columns
            mmqu__dral = mmqu__dral if mmqu__dral in col_names else None
            partition_names = []
            dlsll__abkf = []
            ikn__lbes = []
        vvo__xviol = None if isinstance(mmqu__dral, dict
            ) or mmqu__dral is None else mmqu__dral
        index_column_index = None
        index_column_type = types.none
        if vvo__xviol:
            klccr__vecwy = col_names.index(vvo__xviol)
            index_column_index = col_indices.pop(klccr__vecwy)
            index_column_type = dfdk__dan.pop(klccr__vecwy)
            col_names.pop(klccr__vecwy)
        for pep__kux, c in enumerate(col_names):
            if c in aml__rfhel:
                dfdk__dan[pep__kux] = aml__rfhel[c]
        vld__xatd = [ir.Var(pwnqq__mkuu, mk_unique_var('pq_table'),
            wvf__wgnl), ir.Var(pwnqq__mkuu, mk_unique_var('pq_index'),
            wvf__wgnl)]
        dvy__pnzq = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, dfdk__dan, vld__xatd, wvf__wgnl,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, dlsll__abkf, ikn__lbes)]
        return (col_names, vld__xatd, mmqu__dral, dvy__pnzq, dfdk__dan,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    armcl__jgzmy = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    hww__mjn, ynre__ykoi = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(hww__mjn.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, hww__mjn, ynre__ykoi, pq_node.original_df_colnames,
        pq_node.partition_names, pq_node.original_out_types, typemap, 'parquet'
        )
    wupb__tvcs = ', '.join(f'out{pep__kux}' for pep__kux in range(armcl__jgzmy)
        )
    mxnjx__ljee = f'def pq_impl(fname, {extra_args}):\n'
    mxnjx__ljee += (
        f'    (total_rows, {wupb__tvcs},) = _pq_reader_py(fname, {extra_args})\n'
        )
    kvu__liuxc = {}
    exec(mxnjx__ljee, {}, kvu__liuxc)
    yuqkq__til = kvu__liuxc['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        uhef__qziqu = pq_node.loc.strformat()
        qne__fyeon = []
        ksib__artr = []
        for pep__kux in pq_node.out_used_cols:
            eyu__csj = pq_node.df_colnames[pep__kux]
            qne__fyeon.append(eyu__csj)
            if isinstance(pq_node.out_types[pep__kux], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                ksib__artr.append(eyu__csj)
        dxm__kgcbi = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', dxm__kgcbi,
            uhef__qziqu, qne__fyeon)
        if ksib__artr:
            pyrgf__ruz = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', pyrgf__ruz,
                uhef__qziqu, ksib__artr)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        qmwz__xearw = set(pq_node.out_used_cols)
        ciq__bgid = set(pq_node.unsupported_columns)
        vtj__ofzz = qmwz__xearw & ciq__bgid
        if vtj__ofzz:
            adf__fhfot = sorted(vtj__ofzz)
            cjqnx__nlzsw = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            jqbi__cuiev = 0
            for dxk__bxwig in adf__fhfot:
                while pq_node.unsupported_columns[jqbi__cuiev] != dxk__bxwig:
                    jqbi__cuiev += 1
                cjqnx__nlzsw.append(
                    f"Column '{pq_node.df_colnames[dxk__bxwig]}' with unsupported arrow type {pq_node.unsupported_arrow_types[jqbi__cuiev]}"
                    )
                jqbi__cuiev += 1
            gnme__ycfz = '\n'.join(cjqnx__nlzsw)
            raise BodoError(gnme__ycfz, loc=pq_node.loc)
    shz__iuff = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    veeqj__ffa = typemap[pq_node.file_name.name]
    lbteg__lkth = (veeqj__ffa,) + tuple(typemap[jiot__crc.name] for
        jiot__crc in ynre__ykoi)
    kojcr__waoaq = compile_to_numba_ir(yuqkq__til, {'_pq_reader_py':
        shz__iuff}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        lbteg__lkth, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(kojcr__waoaq, [pq_node.file_name] + ynre__ykoi)
    dvy__pnzq = kojcr__waoaq.body[:-3]
    if meta_head_only_info:
        dvy__pnzq[-1 - armcl__jgzmy].target = meta_head_only_info[1]
    dvy__pnzq[-2].target = pq_node.out_vars[0]
    dvy__pnzq[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        dvy__pnzq.pop(-1)
    elif not pq_node.out_used_cols:
        dvy__pnzq.pop(-2)
    return dvy__pnzq


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    cdr__tdkrd = get_overload_const_str(dnf_filter_str)
    grux__qcuam = get_overload_const_str(expr_filter_str)
    pxvtx__tmw = ', '.join(f'f{pep__kux}' for pep__kux in range(len(var_tup)))
    mxnjx__ljee = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        mxnjx__ljee += f'  {pxvtx__tmw}, = var_tup\n'
    mxnjx__ljee += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    mxnjx__ljee += f'    dnf_filters_py = {cdr__tdkrd}\n'
    mxnjx__ljee += f'    expr_filters_py = {grux__qcuam}\n'
    mxnjx__ljee += '  return (dnf_filters_py, expr_filters_py)\n'
    kvu__liuxc = {}
    exec(mxnjx__ljee, globals(), kvu__liuxc)
    return kvu__liuxc['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    vfwr__yydt = next_label()
    ycyd__nut = ',' if extra_args else ''
    mxnjx__ljee = f'def pq_reader_py(fname,{extra_args}):\n'
    mxnjx__ljee += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    mxnjx__ljee += f"    ev.add_attribute('g_fname', fname)\n"
    mxnjx__ljee += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    mxnjx__ljee += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{ycyd__nut}))
"""
    mxnjx__ljee += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    mxnjx__ljee += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    uiyfq__diorf = not out_used_cols
    ebpue__hjqk = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    gefw__piut = {c: pep__kux for pep__kux, c in enumerate(col_indices)}
    ewxg__fgp = {c: pep__kux for pep__kux, c in enumerate(ebpue__hjqk)}
    gzrrq__dlu = []
    anq__jpqlc = set()
    cgj__goi = partition_names + [input_file_name_col]
    for pep__kux in out_used_cols:
        if ebpue__hjqk[pep__kux] not in cgj__goi:
            gzrrq__dlu.append(col_indices[pep__kux])
        elif not input_file_name_col or ebpue__hjqk[pep__kux
            ] != input_file_name_col:
            anq__jpqlc.add(col_indices[pep__kux])
    if index_column_index is not None:
        gzrrq__dlu.append(index_column_index)
    gzrrq__dlu = sorted(gzrrq__dlu)
    jie__gqt = {c: pep__kux for pep__kux, c in enumerate(gzrrq__dlu)}
    dbcn__nzm = [(int(is_nullable(out_types[gefw__piut[rpku__lnhos]])) if 
        rpku__lnhos != index_column_index else int(is_nullable(
        index_column_type))) for rpku__lnhos in gzrrq__dlu]
    str_as_dict_cols = []
    for rpku__lnhos in gzrrq__dlu:
        if rpku__lnhos == index_column_index:
            cws__atsgn = index_column_type
        else:
            cws__atsgn = out_types[gefw__piut[rpku__lnhos]]
        if cws__atsgn == dict_str_arr_type:
            str_as_dict_cols.append(rpku__lnhos)
    qysj__ylcg = []
    gtd__dsb = {}
    ezcpr__uif = []
    khykh__nau = []
    for pep__kux, zqmo__ieu in enumerate(partition_names):
        try:
            gvfht__szo = ewxg__fgp[zqmo__ieu]
            if col_indices[gvfht__szo] not in anq__jpqlc:
                continue
        except (KeyError, ValueError) as igho__tpvmw:
            continue
        gtd__dsb[zqmo__ieu] = len(qysj__ylcg)
        qysj__ylcg.append(zqmo__ieu)
        ezcpr__uif.append(pep__kux)
        jft__gvl = out_types[gvfht__szo].dtype
        pwp__fqr = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            jft__gvl)
        khykh__nau.append(numba_to_c_type(pwp__fqr))
    mxnjx__ljee += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    mxnjx__ljee += f'    out_table = pq_read(\n'
    mxnjx__ljee += f'        fname_py, {is_parallel},\n'
    mxnjx__ljee += f'        unicode_to_utf8(bucket_region),\n'
    mxnjx__ljee += f'        dnf_filters, expr_filters,\n'
    mxnjx__ljee += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{vfwr__yydt}.ctypes,
"""
    mxnjx__ljee += f'        {len(gzrrq__dlu)},\n'
    mxnjx__ljee += f'        nullable_cols_arr_{vfwr__yydt}.ctypes,\n'
    if len(ezcpr__uif) > 0:
        mxnjx__ljee += (
            f'        np.array({ezcpr__uif}, dtype=np.int32).ctypes,\n')
        mxnjx__ljee += (
            f'        np.array({khykh__nau}, dtype=np.int32).ctypes,\n')
        mxnjx__ljee += f'        {len(ezcpr__uif)},\n'
    else:
        mxnjx__ljee += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        mxnjx__ljee += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        mxnjx__ljee += f'        0, 0,\n'
    mxnjx__ljee += f'        total_rows_np.ctypes,\n'
    mxnjx__ljee += f'        {input_file_name_col is not None},\n'
    mxnjx__ljee += f'    )\n'
    mxnjx__ljee += f'    check_and_propagate_cpp_exception()\n'
    pemil__kgl = 'None'
    zxont__egw = index_column_type
    lhqe__bkei = TableType(tuple(out_types))
    if uiyfq__diorf:
        lhqe__bkei = types.none
    if index_column_index is not None:
        uzs__gxyn = jie__gqt[index_column_index]
        pemil__kgl = (
            f'info_to_array(info_from_table(out_table, {uzs__gxyn}), index_arr_type)'
            )
    mxnjx__ljee += f'    index_arr = {pemil__kgl}\n'
    if uiyfq__diorf:
        yuhkc__eot = None
    else:
        yuhkc__eot = []
        rzrt__nrm = 0
        xgdqj__xiym = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for pep__kux, dxk__bxwig in enumerate(col_indices):
            if rzrt__nrm < len(out_used_cols) and pep__kux == out_used_cols[
                rzrt__nrm]:
                inzb__itxda = col_indices[pep__kux]
                if xgdqj__xiym and inzb__itxda == xgdqj__xiym:
                    yuhkc__eot.append(len(gzrrq__dlu) + len(qysj__ylcg))
                elif inzb__itxda in anq__jpqlc:
                    ngihd__suqmg = ebpue__hjqk[pep__kux]
                    yuhkc__eot.append(len(gzrrq__dlu) + gtd__dsb[ngihd__suqmg])
                else:
                    yuhkc__eot.append(jie__gqt[dxk__bxwig])
                rzrt__nrm += 1
            else:
                yuhkc__eot.append(-1)
        yuhkc__eot = np.array(yuhkc__eot, dtype=np.int64)
    if uiyfq__diorf:
        mxnjx__ljee += '    T = None\n'
    else:
        mxnjx__ljee += f"""    T = cpp_table_to_py_table(out_table, table_idx_{vfwr__yydt}, py_table_type_{vfwr__yydt})
"""
    mxnjx__ljee += f'    delete_table(out_table)\n'
    mxnjx__ljee += f'    total_rows = total_rows_np[0]\n'
    mxnjx__ljee += f'    ev.finalize()\n'
    mxnjx__ljee += f'    return (total_rows, T, index_arr)\n'
    kvu__liuxc = {}
    riutx__yjcto = {f'py_table_type_{vfwr__yydt}': lhqe__bkei,
        f'table_idx_{vfwr__yydt}': yuhkc__eot,
        f'selected_cols_arr_{vfwr__yydt}': np.array(gzrrq__dlu, np.int32),
        f'nullable_cols_arr_{vfwr__yydt}': np.array(dbcn__nzm, np.int32),
        'index_arr_type': zxont__egw, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(mxnjx__ljee, riutx__yjcto, kvu__liuxc)
    shz__iuff = kvu__liuxc['pq_reader_py']
    zuj__fxnye = numba.njit(shz__iuff, no_cpython_wrapper=True)
    return zuj__fxnye


import pyarrow as pa
_pa_numba_typ_map = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.
    int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.int64,
    pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32(): types.
    uint32, pa.uint64(): types.uint64, pa.float32(): types.float32, pa.
    float64(): types.float64, pa.string(): string_type, pa.binary():
    bytes_type, pa.date32(): datetime_date_type, pa.date64(): types.
    NPDatetime('ns'), null(): string_type}


def get_arrow_timestamp_type(pa_ts_typ):
    dgw__lny = 'ns', 'us', 'ms', 's'
    if pa_ts_typ.unit not in dgw__lny:
        return types.Array(bodo.datetime64ns, 1, 'C'), False
    elif pa_ts_typ.tz is not None:
        gwbyj__geu = pa_ts_typ.to_pandas_dtype().tz
        ffnjl__pfdiu = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(
            gwbyj__geu)
        return bodo.DatetimeArrayType(ffnjl__pfdiu), True
    else:
        return types.Array(bodo.datetime64ns, 1, 'C'), True


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info, str_as_dict=False):
    if isinstance(pa_typ.type, pa.ListType):
        mosim__uzch, jgtr__jgdoi = _get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info)
        return ArrayItemArrayType(mosim__uzch), jgtr__jgdoi
    if isinstance(pa_typ.type, pa.StructType):
        gve__xbkz = []
        oty__exr = []
        jgtr__jgdoi = True
        for lqqks__nku in pa_typ.flatten():
            oty__exr.append(lqqks__nku.name.split('.')[-1])
            grsxs__pvefp, qavk__cge = _get_numba_typ_from_pa_typ(lqqks__nku,
                is_index, nullable_from_metadata, category_info)
            gve__xbkz.append(grsxs__pvefp)
            jgtr__jgdoi = jgtr__jgdoi and qavk__cge
        return StructArrayType(tuple(gve__xbkz), tuple(oty__exr)), jgtr__jgdoi
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
        voh__ckqgj = _pa_numba_typ_map[pa_typ.type.index_type]
        mxomz__lpfp = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=voh__ckqgj)
        return CategoricalArrayType(mxomz__lpfp), True
    if isinstance(pa_typ.type, pa.lib.TimestampType):
        return get_arrow_timestamp_type(pa_typ.type)
    elif pa_typ.type in _pa_numba_typ_map:
        tdvsn__guhi = _pa_numba_typ_map[pa_typ.type]
        jgtr__jgdoi = True
    else:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    if tdvsn__guhi == datetime_date_type:
        return datetime_date_array_type, jgtr__jgdoi
    if tdvsn__guhi == bytes_type:
        return binary_array_type, jgtr__jgdoi
    mosim__uzch = (string_array_type if tdvsn__guhi == string_type else
        types.Array(tdvsn__guhi, 1, 'C'))
    if tdvsn__guhi == types.bool_:
        mosim__uzch = boolean_array
    if nullable_from_metadata is not None:
        wzb__iph = nullable_from_metadata
    else:
        wzb__iph = use_nullable_int_arr
    if wzb__iph and not is_index and isinstance(tdvsn__guhi, types.Integer
        ) and pa_typ.nullable:
        mosim__uzch = IntegerArrayType(tdvsn__guhi)
    return mosim__uzch, jgtr__jgdoi


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None, typing_pa_schema=None):
    if get_row_counts:
        hkvu__xwe = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    xwxqh__ups = MPI.COMM_WORLD
    if isinstance(fpath, list):
        ujh__mbs = urlparse(fpath[0])
        protocol = ujh__mbs.scheme
        ymk__fbkq = ujh__mbs.netloc
        for pep__kux in range(len(fpath)):
            mzy__yalr = fpath[pep__kux]
            nbfxs__plwdv = urlparse(mzy__yalr)
            if nbfxs__plwdv.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if nbfxs__plwdv.netloc != ymk__fbkq:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[pep__kux] = mzy__yalr.rstrip('/')
    else:
        ujh__mbs = urlparse(fpath)
        protocol = ujh__mbs.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as igho__tpvmw:
            uih__hzpw = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(uih__hzpw)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as igho__tpvmw:
            uih__hzpw = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            noj__afmk = gcsfs.GCSFileSystem(token=None)
            fs.append(noj__afmk)
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
                prefix = f'{protocol}://{ujh__mbs.netloc}'
                path = path[len(prefix):]
            bto__ysimj = fs.glob(path)
            if protocol == 's3':
                bto__ysimj = [('s3://' + mzy__yalr) for mzy__yalr in
                    bto__ysimj if not mzy__yalr.startswith('s3://')]
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                bto__ysimj = [(prefix + mzy__yalr) for mzy__yalr in bto__ysimj]
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(bto__ysimj) == 0:
            raise BodoError('No files found matching glob pattern')
        return bto__ysimj
    ahch__ibfef = False
    if get_row_counts:
        iah__hbh = getfs(parallel=True)
        ahch__ibfef = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        kfbhc__rvny = 1
        wpo__knrkf = os.cpu_count()
        if wpo__knrkf is not None and wpo__knrkf > 1:
            kfbhc__rvny = wpo__knrkf // 2
        try:
            if get_row_counts:
                xaht__nwo = tracing.Event('pq.ParquetDataset', is_parallel=
                    False)
                if tracing.is_tracing():
                    xaht__nwo.add_attribute('g_dnf_filter', str(dnf_filters))
            ddq__gnj = pa.io_thread_count()
            pa.set_io_thread_count(kfbhc__rvny)
            if isinstance(fpath, list):
                omj__vclfv = []
                for uioew__ummzq in fpath:
                    if has_magic(uioew__ummzq):
                        omj__vclfv += glob(protocol, getfs(), uioew__ummzq)
                    else:
                        omj__vclfv.append(uioew__ummzq)
                fpath = omj__vclfv
            elif has_magic(fpath):
                fpath = glob(protocol, getfs(), fpath)
            if protocol == 's3':
                if isinstance(fpath, list):
                    get_legacy_fs().info(fpath[0])
                else:
                    get_legacy_fs().info(fpath)
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{ujh__mbs.netloc}'
                if isinstance(fpath, list):
                    ehahp__yqd = [mzy__yalr[len(prefix):] for mzy__yalr in
                        fpath]
                else:
                    ehahp__yqd = fpath[len(prefix):]
            else:
                ehahp__yqd = fpath
            bgcmc__qkm = pq.ParquetDataset(ehahp__yqd, filesystem=
                get_legacy_fs(), filters=None, use_legacy_dataset=True,
                validate_schema=False, metadata_nthreads=kfbhc__rvny)
            pa.set_io_thread_count(ddq__gnj)
            if typing_pa_schema:
                ndy__dmp = typing_pa_schema
            else:
                ndy__dmp = bodo.io.pa_parquet.get_dataset_schema(bgcmc__qkm)
            if dnf_filters:
                if get_row_counts:
                    xaht__nwo.add_attribute('num_pieces_before_filter', len
                        (bgcmc__qkm.pieces))
                eeob__zyue = time.time()
                bgcmc__qkm._filter(dnf_filters)
                if get_row_counts:
                    xaht__nwo.add_attribute('dnf_filter_time', time.time() -
                        eeob__zyue)
                    xaht__nwo.add_attribute('num_pieces_after_filter', len(
                        bgcmc__qkm.pieces))
            if get_row_counts:
                xaht__nwo.finalize()
            bgcmc__qkm._metadata.fs = None
        except Exception as pek__nhdje:
            if isinstance(fpath, list) and isinstance(pek__nhdje, (OSError,
                FileNotFoundError)):
                pek__nhdje = BodoError(str(pek__nhdje) +
                    list_of_files_error_msg)
            else:
                pek__nhdje = BodoError(
                    f"""error from pyarrow: {type(pek__nhdje).__name__}: {str(pek__nhdje)}
"""
                    )
            xwxqh__ups.bcast(pek__nhdje)
            raise pek__nhdje
        if get_row_counts:
            vruw__khq = tracing.Event('bcast dataset')
        xwxqh__ups.bcast(bgcmc__qkm)
        xwxqh__ups.bcast(ndy__dmp)
    else:
        if get_row_counts:
            vruw__khq = tracing.Event('bcast dataset')
        bgcmc__qkm = xwxqh__ups.bcast(None)
        if isinstance(bgcmc__qkm, Exception):
            idcxk__pdywk = bgcmc__qkm
            raise idcxk__pdywk
        ndy__dmp = xwxqh__ups.bcast(None)
    yjdm__bsa = set(ndy__dmp.names)
    if get_row_counts:
        jilg__bny = getfs()
    else:
        jilg__bny = get_legacy_fs()
    bgcmc__qkm._metadata.fs = jilg__bny
    if get_row_counts:
        vruw__khq.finalize()
    bgcmc__qkm._bodo_total_rows = 0
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = ahch__ibfef = False
        for uioew__ummzq in bgcmc__qkm.pieces:
            uioew__ummzq._bodo_num_rows = 0
    if get_row_counts or ahch__ibfef:
        if get_row_counts and tracing.is_tracing():
            ltj__zfc = tracing.Event('get_row_counts')
            ltj__zfc.add_attribute('g_num_pieces', len(bgcmc__qkm.pieces))
            ltj__zfc.add_attribute('g_expr_filters', str(expr_filters))
        unqme__gmzpc = 0.0
        num_pieces = len(bgcmc__qkm.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        zkld__xiuar = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        rpdwc__oynl = 0
        nju__ezybc = 0
        rnbu__ibz = 0
        fbz__ctskx = True
        if expr_filters is not None:
            import random
            random.seed(37)
            bxwm__gpq = random.sample(bgcmc__qkm.pieces, k=len(bgcmc__qkm.
                pieces))
        else:
            bxwm__gpq = bgcmc__qkm.pieces
        for uioew__ummzq in bxwm__gpq:
            uioew__ummzq._bodo_num_rows = 0
        fpaths = [uioew__ummzq.path for uioew__ummzq in bxwm__gpq[start:
            zkld__xiuar]]
        if protocol == 's3':
            ymk__fbkq = ujh__mbs.netloc
            prefix = 's3://' + ymk__fbkq + '/'
            fpaths = [mzy__yalr[len(prefix):] for mzy__yalr in fpaths]
            jilg__bny = get_s3_subtree_fs(ymk__fbkq, region=getfs().region,
                storage_options=storage_options)
        else:
            jilg__bny = getfs()
        kfbhc__rvny = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(kfbhc__rvny)
        pa.set_cpu_count(kfbhc__rvny)
        idcxk__pdywk = None
        try:
            mmr__vns = ds.dataset(fpaths, filesystem=jilg__bny,
                partitioning=ds.partitioning(flavor='hive') if bgcmc__qkm.
                partitions else None)
            for zeas__ogyfd, basx__owuag in zip(bxwm__gpq[start:zkld__xiuar
                ], mmr__vns.get_fragments()):
                if ahch__ibfef:
                    umt__mue = basx__owuag.metadata.schema.to_arrow_schema()
                    xyf__hhw = set(umt__mue.names)
                    if yjdm__bsa != xyf__hhw:
                        elje__dwlj = xyf__hhw - yjdm__bsa
                        sqf__ynk = yjdm__bsa - xyf__hhw
                        modm__sfm = f'Schema in {zeas__ogyfd} was different.\n'
                        if elje__dwlj:
                            modm__sfm += f"""File contains column(s) {elje__dwlj} not found in other files in the dataset.
"""
                        if sqf__ynk:
                            modm__sfm += f"""File missing column(s) {sqf__ynk} found in other files in the dataset.
"""
                        raise BodoError(modm__sfm)
                    try:
                        ndy__dmp = pa.unify_schemas([ndy__dmp, umt__mue])
                    except Exception as pek__nhdje:
                        modm__sfm = (
                            f'Schema in {zeas__ogyfd} was different.\n' +
                            str(pek__nhdje))
                        raise BodoError(modm__sfm)
                eeob__zyue = time.time()
                vpwzv__pvbml = basx__owuag.scanner(schema=mmr__vns.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                unqme__gmzpc += time.time() - eeob__zyue
                zeas__ogyfd._bodo_num_rows = vpwzv__pvbml
                rpdwc__oynl += vpwzv__pvbml
                nju__ezybc += basx__owuag.num_row_groups
                rnbu__ibz += sum(qvl__mdc.total_byte_size for qvl__mdc in
                    basx__owuag.row_groups)
        except Exception as pek__nhdje:
            idcxk__pdywk = pek__nhdje
        if xwxqh__ups.allreduce(idcxk__pdywk is not None, op=MPI.LOR):
            for idcxk__pdywk in xwxqh__ups.allgather(idcxk__pdywk):
                if idcxk__pdywk:
                    if isinstance(fpath, list) and isinstance(idcxk__pdywk,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(idcxk__pdywk) +
                            list_of_files_error_msg)
                    raise idcxk__pdywk
        if ahch__ibfef:
            fbz__ctskx = xwxqh__ups.allreduce(fbz__ctskx, op=MPI.LAND)
            if not fbz__ctskx:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            bgcmc__qkm._bodo_total_rows = xwxqh__ups.allreduce(rpdwc__oynl,
                op=MPI.SUM)
            tcl__axfp = xwxqh__ups.allreduce(nju__ezybc, op=MPI.SUM)
            yujg__xgtyn = xwxqh__ups.allreduce(rnbu__ibz, op=MPI.SUM)
            uiq__leint = np.array([uioew__ummzq._bodo_num_rows for
                uioew__ummzq in bgcmc__qkm.pieces])
            uiq__leint = xwxqh__ups.allreduce(uiq__leint, op=MPI.SUM)
            for uioew__ummzq, vrn__wvmz in zip(bgcmc__qkm.pieces, uiq__leint):
                uioew__ummzq._bodo_num_rows = vrn__wvmz
            if is_parallel and bodo.get_rank(
                ) == 0 and tcl__axfp < bodo.get_size() and tcl__axfp != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({tcl__axfp}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if tcl__axfp == 0:
                ylm__hhtq = 0
            else:
                ylm__hhtq = yujg__xgtyn // tcl__axfp
            if (bodo.get_rank() == 0 and yujg__xgtyn >= 20 * 1048576 and 
                ylm__hhtq < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({ylm__hhtq} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                ltj__zfc.add_attribute('g_total_num_row_groups', tcl__axfp)
                ltj__zfc.add_attribute('total_scan_time', unqme__gmzpc)
                wpsnj__zxxo = np.array([uioew__ummzq._bodo_num_rows for
                    uioew__ummzq in bgcmc__qkm.pieces])
                jhu__nluhg = np.percentile(wpsnj__zxxo, [25, 50, 75])
                ltj__zfc.add_attribute('g_row_counts_min', wpsnj__zxxo.min())
                ltj__zfc.add_attribute('g_row_counts_Q1', jhu__nluhg[0])
                ltj__zfc.add_attribute('g_row_counts_median', jhu__nluhg[1])
                ltj__zfc.add_attribute('g_row_counts_Q3', jhu__nluhg[2])
                ltj__zfc.add_attribute('g_row_counts_max', wpsnj__zxxo.max())
                ltj__zfc.add_attribute('g_row_counts_mean', wpsnj__zxxo.mean())
                ltj__zfc.add_attribute('g_row_counts_std', wpsnj__zxxo.std())
                ltj__zfc.add_attribute('g_row_counts_sum', wpsnj__zxxo.sum())
                ltj__zfc.finalize()
    bgcmc__qkm._prefix = ''
    if protocol in {'hdfs', 'abfs', 'abfss'}:
        prefix = f'{protocol}://{ujh__mbs.netloc}'
        if len(bgcmc__qkm.pieces) > 0:
            zeas__ogyfd = bgcmc__qkm.pieces[0]
            if not zeas__ogyfd.path.startswith(prefix):
                bgcmc__qkm._prefix = prefix
    if read_categories:
        _add_categories_to_pq_dataset(bgcmc__qkm)
    if get_row_counts:
        hkvu__xwe.finalize()
    if ahch__ibfef and is_parallel:
        if tracing.is_tracing():
            xyony__gad = tracing.Event('unify_schemas_across_ranks')
        idcxk__pdywk = None
        try:
            ndy__dmp = xwxqh__ups.allreduce(ndy__dmp, bodo.io.helpers.
                pa_schema_unify_mpi_op)
        except Exception as pek__nhdje:
            idcxk__pdywk = pek__nhdje
        if tracing.is_tracing():
            xyony__gad.finalize()
        if xwxqh__ups.allreduce(idcxk__pdywk is not None, op=MPI.LOR):
            for idcxk__pdywk in xwxqh__ups.allgather(idcxk__pdywk):
                if idcxk__pdywk:
                    modm__sfm = (f'Schema in some files were different.\n' +
                        str(idcxk__pdywk))
                    raise BodoError(modm__sfm)
    bgcmc__qkm._bodo_arrow_schema = ndy__dmp
    return bgcmc__qkm


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region, prefix,
    str_as_dict_cols, start_offset, rows_to_read, has_partitions, schema):
    import pyarrow as pa
    wpo__knrkf = os.cpu_count()
    if wpo__knrkf is None or wpo__knrkf == 0:
        wpo__knrkf = 2
    jbsig__mzw = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), wpo__knrkf)
    nnpe__zfil = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), wpo__knrkf
        )
    if is_parallel and len(fpaths) > nnpe__zfil and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(nnpe__zfil)
        pa.set_cpu_count(nnpe__zfil)
    else:
        pa.set_io_thread_count(jbsig__mzw)
        pa.set_cpu_count(jbsig__mzw)
    if fpaths[0].startswith('s3://'):
        ymk__fbkq = urlparse(fpaths[0]).netloc
        prefix = 's3://' + ymk__fbkq + '/'
        fpaths = [mzy__yalr[len(prefix):] for mzy__yalr in fpaths]
        if region == '':
            region = get_s3_bucket_region_njit(fpaths[0], parallel=False)
        jilg__bny = get_s3_subtree_fs(ymk__fbkq, region=region,
            storage_options=storage_options)
    elif prefix and prefix.startswith(('hdfs', 'abfs', 'abfss')):
        jilg__bny = get_hdfs_fs(prefix + fpaths[0])
    elif fpaths[0].startswith(('gcs', 'gs')):
        import gcsfs
        jilg__bny = gcsfs.GCSFileSystem(token=None)
    else:
        jilg__bny = None
    lyv__cgmf = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    bgcmc__qkm = ds.dataset(fpaths, filesystem=jilg__bny, partitioning=ds.
        partitioning(flavor='hive') if has_partitions else None, format=
        lyv__cgmf)
    yyhao__epjq = set(str_as_dict_cols)
    cmhlf__bggsw = schema.names
    for pep__kux, name in enumerate(cmhlf__bggsw):
        if name in yyhao__epjq:
            druu__phko = schema.field(pep__kux)
            ryoh__sme = pa.field(name, pa.dictionary(pa.int32(), druu__phko
                .type), druu__phko.nullable)
            schema = schema.remove(pep__kux).insert(pep__kux, ryoh__sme)
    bgcmc__qkm = bgcmc__qkm.replace_schema(pa.unify_schemas([bgcmc__qkm.
        schema, schema]))
    col_names = bgcmc__qkm.schema.names
    acvt__pnne = [col_names[bezwv__rsp] for bezwv__rsp in selected_fields]
    nntrt__hyuwp = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if nntrt__hyuwp and expr_filters is None:
        dlmw__zzqqt = []
        yglm__scwm = 0
        gkc__hzvbz = 0
        for basx__owuag in bgcmc__qkm.get_fragments():
            fzfm__rhiwv = []
            for qvl__mdc in basx__owuag.row_groups:
                tzc__ztmxp = qvl__mdc.num_rows
                if start_offset < yglm__scwm + tzc__ztmxp:
                    if gkc__hzvbz == 0:
                        qfze__ilda = start_offset - yglm__scwm
                        xuca__lnt = min(tzc__ztmxp - qfze__ilda, rows_to_read)
                    else:
                        xuca__lnt = min(tzc__ztmxp, rows_to_read - gkc__hzvbz)
                    gkc__hzvbz += xuca__lnt
                    fzfm__rhiwv.append(qvl__mdc.id)
                yglm__scwm += tzc__ztmxp
                if gkc__hzvbz == rows_to_read:
                    break
            dlmw__zzqqt.append(basx__owuag.subset(row_group_ids=fzfm__rhiwv))
            if gkc__hzvbz == rows_to_read:
                break
        bgcmc__qkm = ds.FileSystemDataset(dlmw__zzqqt, bgcmc__qkm.schema,
            lyv__cgmf, filesystem=bgcmc__qkm.filesystem)
        start_offset = qfze__ilda
    afu__jwu = bgcmc__qkm.scanner(columns=acvt__pnne, filter=expr_filters,
        use_threads=True).to_reader()
    return bgcmc__qkm, afu__jwu, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema.to_arrow_schema()
    kxkoo__oidgs = [c for c in pa_schema.names if isinstance(pa_schema.
        field(c).type, pa.DictionaryType)]
    if len(kxkoo__oidgs) == 0:
        pq_dataset._category_info = {}
        return
    xwxqh__ups = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            flvpa__sgykp = pq_dataset.pieces[0].open()
            qvl__mdc = flvpa__sgykp.read_row_group(0, kxkoo__oidgs)
            category_info = {c: tuple(qvl__mdc.column(c).chunk(0).
                dictionary.to_pylist()) for c in kxkoo__oidgs}
            del flvpa__sgykp, qvl__mdc
        except Exception as pek__nhdje:
            xwxqh__ups.bcast(pek__nhdje)
            raise pek__nhdje
        xwxqh__ups.bcast(category_info)
    else:
        category_info = xwxqh__ups.bcast(None)
        if isinstance(category_info, Exception):
            idcxk__pdywk = category_info
            raise idcxk__pdywk
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    mmqu__dral = None
    nullable_from_metadata = defaultdict(lambda : None)
    zavw__uasgh = b'pandas'
    if schema.metadata is not None and zavw__uasgh in schema.metadata:
        import json
        evsn__kqstg = json.loads(schema.metadata[zavw__uasgh].decode('utf8'))
        arw__odb = len(evsn__kqstg['index_columns'])
        if arw__odb > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        mmqu__dral = evsn__kqstg['index_columns'][0] if arw__odb else None
        if not isinstance(mmqu__dral, str) and not isinstance(mmqu__dral, dict
            ):
            mmqu__dral = None
        for ahnok__hqruw in evsn__kqstg['columns']:
            rharg__rgv = ahnok__hqruw['name']
            if ahnok__hqruw['pandas_type'].startswith('int'
                ) and rharg__rgv is not None:
                if ahnok__hqruw['numpy_type'].startswith('Int'):
                    nullable_from_metadata[rharg__rgv] = True
                else:
                    nullable_from_metadata[rharg__rgv] = False
    return mmqu__dral, nullable_from_metadata


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for rharg__rgv in pa_schema.names:
        lqqks__nku = pa_schema.field(rharg__rgv)
        if lqqks__nku.type == pa.string():
            str_columns.append(rharg__rgv)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    xwxqh__ups = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        bxwm__gpq = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        bxwm__gpq = pq_dataset.pieces
    uayb__ysz = np.zeros(len(str_columns), dtype=np.int64)
    ixbj__ehlh = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(bxwm__gpq):
        zeas__ogyfd = bxwm__gpq[bodo.get_rank()]
        try:
            xdgnb__cwsrv = zeas__ogyfd.get_metadata()
            for pep__kux in range(xdgnb__cwsrv.num_row_groups):
                for rzrt__nrm, rharg__rgv in enumerate(str_columns):
                    jqbi__cuiev = pa_schema.get_field_index(rharg__rgv)
                    uayb__ysz[rzrt__nrm] += xdgnb__cwsrv.row_group(pep__kux
                        ).column(jqbi__cuiev).total_uncompressed_size
            kyku__nbtyn = xdgnb__cwsrv.num_rows
        except Exception as pek__nhdje:
            if isinstance(pek__nhdje, (OSError, FileNotFoundError)):
                kyku__nbtyn = 0
            else:
                raise
    else:
        kyku__nbtyn = 0
    hffgm__vbij = xwxqh__ups.allreduce(kyku__nbtyn, op=MPI.SUM)
    if hffgm__vbij == 0:
        return set()
    xwxqh__ups.Allreduce(uayb__ysz, ixbj__ehlh, op=MPI.SUM)
    vji__ghd = ixbj__ehlh / hffgm__vbij
    str_as_dict = set()
    for pep__kux, mzy__unmza in enumerate(vji__ghd):
        if mzy__unmza < READ_STR_AS_DICT_THRESHOLD:
            rharg__rgv = str_columns[pep__kux][0]
            str_as_dict.add(rharg__rgv)
    return str_as_dict


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    dfdk__dan = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    if hasattr(pq_dataset, '_bodo_arrow_schema'):
        pa_schema = pq_dataset._bodo_arrow_schema
    else:
        pa_schema = pq_dataset.schema.to_arrow_schema()
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[pep__kux].name for pep__kux in range(len(
        pq_dataset.partitions.partition_names))]
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    demsb__bra = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    zbs__eowg = read_as_dict_cols - demsb__bra
    if len(zbs__eowg) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {zbs__eowg}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(demsb__bra)
    demsb__bra = demsb__bra - read_as_dict_cols
    str_columns = [ylkhy__esav for ylkhy__esav in str_columns if 
        ylkhy__esav in demsb__bra]
    str_as_dict: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    str_as_dict.update(read_as_dict_cols)
    col_names = pa_schema.names
    mmqu__dral, nullable_from_metadata = get_pandas_metadata(pa_schema,
        num_pieces)
    ylfz__nnsp = []
    xpcp__bqd = []
    czzl__hrnhq = []
    for pep__kux, c in enumerate(col_names):
        lqqks__nku = pa_schema.field(c)
        tdvsn__guhi, jgtr__jgdoi = _get_numba_typ_from_pa_typ(lqqks__nku, c ==
            mmqu__dral, nullable_from_metadata[c], pq_dataset.
            _category_info, str_as_dict=c in str_as_dict)
        ylfz__nnsp.append(tdvsn__guhi)
        xpcp__bqd.append(jgtr__jgdoi)
        czzl__hrnhq.append(lqqks__nku.type)
    if partition_names:
        col_names += partition_names
        ylfz__nnsp += [_get_partition_cat_dtype(pq_dataset.partitions.
            levels[pep__kux]) for pep__kux in range(len(partition_names))]
        xpcp__bqd.extend([True] * len(partition_names))
        czzl__hrnhq.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        ylfz__nnsp += [dict_str_arr_type]
        xpcp__bqd.append(True)
        czzl__hrnhq.append(None)
    uii__grg = {c: pep__kux for pep__kux, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in uii__grg:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if mmqu__dral and not isinstance(mmqu__dral, dict
        ) and mmqu__dral not in selected_columns:
        selected_columns.append(mmqu__dral)
    col_names = selected_columns
    col_indices = []
    dfdk__dan = []
    dlsll__abkf = []
    ikn__lbes = []
    for pep__kux, c in enumerate(col_names):
        inzb__itxda = uii__grg[c]
        col_indices.append(inzb__itxda)
        dfdk__dan.append(ylfz__nnsp[inzb__itxda])
        if not xpcp__bqd[inzb__itxda]:
            dlsll__abkf.append(pep__kux)
            ikn__lbes.append(czzl__hrnhq[inzb__itxda])
    return (col_names, dfdk__dan, mmqu__dral, col_indices, partition_names,
        dlsll__abkf, ikn__lbes)


def _get_partition_cat_dtype(part_set):
    cyvcx__gir = part_set.dictionary.to_pandas()
    jhdf__mmsxm = bodo.typeof(cyvcx__gir).dtype
    mxomz__lpfp = PDCategoricalDtype(tuple(cyvcx__gir), jhdf__mmsxm, False)
    return CategoricalArrayType(mxomz__lpfp)


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
        rwuz__hsfp = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        xob__smi = cgutils.get_or_insert_function(builder.module,
            rwuz__hsfp, name='pq_write')
        builder.call(xob__smi, args)
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
        rwuz__hsfp = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        xob__smi = cgutils.get_or_insert_function(builder.module,
            rwuz__hsfp, name='pq_write_partitioned')
        builder.call(xob__smi, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64), codegen
