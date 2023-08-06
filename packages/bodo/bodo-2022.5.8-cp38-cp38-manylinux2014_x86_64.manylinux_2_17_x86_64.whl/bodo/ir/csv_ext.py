from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from mpi4py import MPI
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, escapechar,
        storage_options=None, index_column_index=None, index_column_typ=
        types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.escapechar = escapechar
        self.storage_options = storage_options
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.out_used_cols = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, escapechar={}, storage_options={}, index_column_index={}, index_colum_typ = {}, out_used_colss={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            escapechar, self.storage_options, self.index_column_index, self
            .index_column_typ, self.out_used_cols))


def check_node_typing(node, typemap):
    wis__nfir = typemap[node.file_name.name]
    if types.unliteral(wis__nfir) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {wis__nfir}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        phol__gfivn = typemap[node.skiprows.name]
        if isinstance(phol__gfivn, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(phol__gfivn, types.Integer) and not (isinstance
            (phol__gfivn, (types.List, types.Tuple)) and isinstance(
            phol__gfivn.dtype, types.Integer)) and not isinstance(phol__gfivn,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {phol__gfivn}."
                , loc=node.skiprows.loc)
        elif isinstance(phol__gfivn, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        wzmbg__pxnr = typemap[node.nrows.name]
        if not isinstance(wzmbg__pxnr, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {wzmbg__pxnr}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)
csv_file_chunk_reader = types.ExternalFunction('csv_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
    storage_options_dict_type, types.int64, types.bool_, types.int64, types
    .bool_))


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        yerar__solpm = csv_node.out_vars[0]
        if yerar__solpm.name not in lives:
            return None
    else:
        ebejg__rdytl = csv_node.out_vars[0]
        oswaj__gst = csv_node.out_vars[1]
        if ebejg__rdytl.name not in lives and oswaj__gst.name not in lives:
            return None
        elif oswaj__gst.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif ebejg__rdytl.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    phol__gfivn = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            qreb__wofjk = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            kitmb__uqeir = csv_node.loc.strformat()
            gxolq__ntm = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', qreb__wofjk,
                kitmb__uqeir, gxolq__ntm)
            iivi__jyupx = csv_node.out_types[0].yield_type.data
            kvnj__ktlfr = [ehxvz__nlir for frop__pjj, ehxvz__nlir in
                enumerate(csv_node.df_colnames) if isinstance(iivi__jyupx[
                frop__pjj], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if kvnj__ktlfr:
                ogs__errb = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    ogs__errb, kitmb__uqeir, kvnj__ktlfr)
        if array_dists is not None:
            vuodp__fxin = csv_node.out_vars[0].name
            parallel = array_dists[vuodp__fxin] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        fdnyx__vlw = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        fdnyx__vlw += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        fdnyx__vlw += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        gvdk__mud = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(fdnyx__vlw, {}, gvdk__mud)
        xdiws__nqze = gvdk__mud['csv_iterator_impl']
        nkr__lmi = 'def csv_reader_init(fname, nrows, skiprows):\n'
        nkr__lmi += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        nkr__lmi += '  return f_reader\n'
        exec(nkr__lmi, globals(), gvdk__mud)
        gdsip__mzmcs = gvdk__mud['csv_reader_init']
        tpji__wzilb = numba.njit(gdsip__mzmcs)
        compiled_funcs.append(tpji__wzilb)
        snn__lplr = compile_to_numba_ir(xdiws__nqze, {'_csv_reader_init':
            tpji__wzilb, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, phol__gfivn), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(snn__lplr, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        cbufg__yhif = snn__lplr.body[:-3]
        cbufg__yhif[-1].target = csv_node.out_vars[0]
        return cbufg__yhif
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    fdnyx__vlw = 'def csv_impl(fname, nrows, skiprows):\n'
    fdnyx__vlw += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    gvdk__mud = {}
    exec(fdnyx__vlw, {}, gvdk__mud)
    gkbid__djv = gvdk__mud['csv_impl']
    wpepg__jozz = csv_node.usecols
    if wpepg__jozz:
        wpepg__jozz = [csv_node.usecols[frop__pjj] for frop__pjj in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        qreb__wofjk = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        kitmb__uqeir = csv_node.loc.strformat()
        gxolq__ntm = []
        kvnj__ktlfr = []
        if wpepg__jozz:
            for frop__pjj in csv_node.out_used_cols:
                lujc__jkua = csv_node.df_colnames[frop__pjj]
                gxolq__ntm.append(lujc__jkua)
                if isinstance(csv_node.out_types[frop__pjj], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    kvnj__ktlfr.append(lujc__jkua)
        bodo.user_logging.log_message('Column Pruning', qreb__wofjk,
            kitmb__uqeir, gxolq__ntm)
        if kvnj__ktlfr:
            ogs__errb = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', ogs__errb,
                kitmb__uqeir, kvnj__ktlfr)
    dlt__hcsal = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, wpepg__jozz, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    snn__lplr = compile_to_numba_ir(gkbid__djv, {'_csv_reader_py':
        dlt__hcsal}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, phol__gfivn), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(snn__lplr, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    cbufg__yhif = snn__lplr.body[:-3]
    cbufg__yhif[-1].target = csv_node.out_vars[1]
    cbufg__yhif[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not wpepg__jozz
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        cbufg__yhif.pop(-1)
    elif not wpepg__jozz:
        cbufg__yhif.pop(-2)
    return cbufg__yhif


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    return bodo.ir.connector.base_connector_remove_dead_columns(csv_node,
        column_live_map, equiv_vars, typemap, 'CSVReader', csv_node.usecols)


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader
    ] = bodo.ir.connector.connector_table_column_use


def _get_dtype_str(t):
    mkyvl__xhm = t.dtype
    if isinstance(mkyvl__xhm, PDCategoricalDtype):
        sxcy__gzhp = CategoricalArrayType(mkyvl__xhm)
        cuq__clc = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, cuq__clc, sxcy__gzhp)
        return cuq__clc
    if mkyvl__xhm == types.NPDatetime('ns'):
        mkyvl__xhm = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        fay__wsl = 'int_arr_{}'.format(mkyvl__xhm)
        setattr(types, fay__wsl, t)
        return fay__wsl
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if mkyvl__xhm == types.bool_:
        mkyvl__xhm = 'bool_'
    if mkyvl__xhm == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(mkyvl__xhm, (
        StringArrayType, ArrayItemArrayType)):
        rkc__utl = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, rkc__utl, t)
        return rkc__utl
    return '{}[::1]'.format(mkyvl__xhm)


def _get_pd_dtype_str(t):
    mkyvl__xhm = t.dtype
    if isinstance(mkyvl__xhm, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(mkyvl__xhm.categories)
    if mkyvl__xhm == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if mkyvl__xhm.signed else 'U',
            mkyvl__xhm.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(mkyvl__xhm, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(mkyvl__xhm)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    cpyo__kqss = ''
    from collections import defaultdict
    ghe__ldm = defaultdict(list)
    for qwzn__zxf, zss__veoo in typemap.items():
        ghe__ldm[zss__veoo].append(qwzn__zxf)
    fegbs__nau = df.columns.to_list()
    dhlq__lbrrn = []
    for zss__veoo, gjpaq__ktpt in ghe__ldm.items():
        try:
            dhlq__lbrrn.append(df.loc[:, gjpaq__ktpt].astype(zss__veoo,
                copy=False))
            df = df.drop(gjpaq__ktpt, axis=1)
        except (ValueError, TypeError) as hekgu__npc:
            cpyo__kqss = (
                f"Caught the runtime error '{hekgu__npc}' on columns {gjpaq__ktpt}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    iispj__nqxw = bool(cpyo__kqss)
    if parallel:
        bmnc__dnv = MPI.COMM_WORLD
        iispj__nqxw = bmnc__dnv.allreduce(iispj__nqxw, op=MPI.LOR)
    if iispj__nqxw:
        gjgof__rjbzb = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if cpyo__kqss:
            raise TypeError(f'{gjgof__rjbzb}\n{cpyo__kqss}')
        else:
            raise TypeError(
                f'{gjgof__rjbzb}\nPlease refer to errors on other ranks.')
    df = pd.concat(dhlq__lbrrn + [df], axis=1)
    uwmmr__iyrx = df.loc[:, fegbs__nau]
    return uwmmr__iyrx


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    sgs__sxb = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        fdnyx__vlw = '  skiprows = sorted(set(skiprows))\n'
    else:
        fdnyx__vlw = '  skiprows = [skiprows]\n'
    fdnyx__vlw += '  skiprows_list_len = len(skiprows)\n'
    fdnyx__vlw += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    fdnyx__vlw += '  check_java_installation(fname)\n'
    fdnyx__vlw += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    fdnyx__vlw += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    fdnyx__vlw += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    fdnyx__vlw += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, sgs__sxb, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    fdnyx__vlw += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    fdnyx__vlw += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    fdnyx__vlw += "      raise FileNotFoundError('File does not exist')\n"
    return fdnyx__vlw


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    kas__hcc = [str(frop__pjj) for frop__pjj, cywzp__ipsyj in enumerate(
        usecols) if col_typs[out_used_cols[frop__pjj]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        kas__hcc.append(str(idx_col_index))
    youiu__vsr = ', '.join(kas__hcc)
    svy__okwq = _gen_parallel_flag_name(sanitized_cnames)
    mefu__zhf = f"{svy__okwq}='bool_'" if check_parallel_runtime else ''
    jca__lkku = [_get_pd_dtype_str(col_typs[out_used_cols[frop__pjj]]) for
        frop__pjj in range(len(usecols))]
    tpln__hoa = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    eyau__razg = [cywzp__ipsyj for frop__pjj, cywzp__ipsyj in enumerate(
        usecols) if jca__lkku[frop__pjj] == 'str']
    if idx_col_index is not None and tpln__hoa == 'str':
        eyau__razg.append(idx_col_index)
    ubnh__wvubb = np.array(eyau__razg, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = ubnh__wvubb
    fdnyx__vlw = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    qpxcp__prp = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = qpxcp__prp
    fdnyx__vlw += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    hijw__mwb = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = hijw__mwb
        fdnyx__vlw += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    xjnzd__tgcmk = defaultdict(list)
    for frop__pjj, cywzp__ipsyj in enumerate(usecols):
        if jca__lkku[frop__pjj] == 'str':
            continue
        xjnzd__tgcmk[jca__lkku[frop__pjj]].append(cywzp__ipsyj)
    if idx_col_index is not None and tpln__hoa != 'str':
        xjnzd__tgcmk[tpln__hoa].append(idx_col_index)
    for frop__pjj, hfsn__awqka in enumerate(xjnzd__tgcmk.values()):
        glbs[f't_arr_{frop__pjj}_{call_id}'] = np.asarray(hfsn__awqka)
        fdnyx__vlw += (
            f'  t_arr_{frop__pjj}_{call_id}_2 = t_arr_{frop__pjj}_{call_id}\n')
    if idx_col_index != None:
        fdnyx__vlw += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {mefu__zhf}):
"""
    else:
        fdnyx__vlw += f'  with objmode(T=table_type_{call_id}, {mefu__zhf}):\n'
    fdnyx__vlw += f'    typemap = {{}}\n'
    for frop__pjj, avkj__zeo in enumerate(xjnzd__tgcmk.keys()):
        fdnyx__vlw += f"""    typemap.update({{i:{avkj__zeo} for i in t_arr_{frop__pjj}_{call_id}_2}})
"""
    fdnyx__vlw += '    if f_reader.get_chunk_size() == 0:\n'
    fdnyx__vlw += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    fdnyx__vlw += '    else:\n'
    fdnyx__vlw += '      df = pd.read_csv(f_reader,\n'
    fdnyx__vlw += '        header=None,\n'
    fdnyx__vlw += '        parse_dates=[{}],\n'.format(youiu__vsr)
    fdnyx__vlw += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    fdnyx__vlw += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        fdnyx__vlw += f'    {svy__okwq} = f_reader.is_parallel()\n'
    else:
        fdnyx__vlw += f'    {svy__okwq} = {parallel}\n'
    fdnyx__vlw += f'    df = astype(df, typemap, {svy__okwq})\n'
    if idx_col_index != None:
        jutk__hftl = sorted(qpxcp__prp).index(idx_col_index)
        fdnyx__vlw += f'    idx_arr = df.iloc[:, {jutk__hftl}].values\n'
        fdnyx__vlw += (
            f'    df.drop(columns=df.columns[{jutk__hftl}], inplace=True)\n')
    if len(usecols) == 0:
        fdnyx__vlw += f'    T = None\n'
    else:
        fdnyx__vlw += f'    arrs = []\n'
        fdnyx__vlw += f'    for i in range(df.shape[1]):\n'
        fdnyx__vlw += f'      arrs.append(df.iloc[:, i].values)\n'
        fdnyx__vlw += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return fdnyx__vlw


def _gen_parallel_flag_name(sanitized_cnames):
    svy__okwq = '_parallel_value'
    while svy__okwq in sanitized_cnames:
        svy__okwq = '_' + svy__okwq
    return svy__okwq


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(ehxvz__nlir) for ehxvz__nlir in
        col_names]
    fdnyx__vlw = 'def csv_reader_py(fname, nrows, skiprows):\n'
    fdnyx__vlw += _gen_csv_file_reader_init(parallel, header, compression, 
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    rjm__wpax = globals()
    if idx_col_typ != types.none:
        rjm__wpax[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        rjm__wpax[f'table_type_{call_id}'] = types.none
    else:
        rjm__wpax[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    fdnyx__vlw += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, rjm__wpax, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        fdnyx__vlw += '  return (T, idx_arr)\n'
    else:
        fdnyx__vlw += '  return (T, None)\n'
    gvdk__mud = {}
    rjm__wpax['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(fdnyx__vlw, rjm__wpax, gvdk__mud)
    dlt__hcsal = gvdk__mud['csv_reader_py']
    tpji__wzilb = numba.njit(dlt__hcsal)
    compiled_funcs.append(tpji__wzilb)
    return tpji__wzilb
