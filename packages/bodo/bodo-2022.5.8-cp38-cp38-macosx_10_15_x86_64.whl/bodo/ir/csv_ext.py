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
    enh__agp = typemap[node.file_name.name]
    if types.unliteral(enh__agp) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {enh__agp}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        goii__psedl = typemap[node.skiprows.name]
        if isinstance(goii__psedl, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(goii__psedl, types.Integer) and not (isinstance
            (goii__psedl, (types.List, types.Tuple)) and isinstance(
            goii__psedl.dtype, types.Integer)) and not isinstance(goii__psedl,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {goii__psedl}."
                , loc=node.skiprows.loc)
        elif isinstance(goii__psedl, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        bht__gfncf = typemap[node.nrows.name]
        if not isinstance(bht__gfncf, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {bht__gfncf}."
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
        blc__jwh = csv_node.out_vars[0]
        if blc__jwh.name not in lives:
            return None
    else:
        txgs__fpc = csv_node.out_vars[0]
        dst__ymf = csv_node.out_vars[1]
        if txgs__fpc.name not in lives and dst__ymf.name not in lives:
            return None
        elif dst__ymf.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif txgs__fpc.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    goii__psedl = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            hbuk__aio = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            lytsz__zhl = csv_node.loc.strformat()
            lfczq__iszf = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', hbuk__aio,
                lytsz__zhl, lfczq__iszf)
            nhuv__xoh = csv_node.out_types[0].yield_type.data
            tisi__qtes = [hkkz__lcrio for uaxst__thol, hkkz__lcrio in
                enumerate(csv_node.df_colnames) if isinstance(nhuv__xoh[
                uaxst__thol], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if tisi__qtes:
                huyj__vespm = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    huyj__vespm, lytsz__zhl, tisi__qtes)
        if array_dists is not None:
            klok__ebh = csv_node.out_vars[0].name
            parallel = array_dists[klok__ebh] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        iybu__ovdnb = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        iybu__ovdnb += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        iybu__ovdnb += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        ijcqu__jrddl = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(iybu__ovdnb, {}, ijcqu__jrddl)
        aarh__sktzj = ijcqu__jrddl['csv_iterator_impl']
        grx__gns = 'def csv_reader_init(fname, nrows, skiprows):\n'
        grx__gns += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        grx__gns += '  return f_reader\n'
        exec(grx__gns, globals(), ijcqu__jrddl)
        nwmkx__kskq = ijcqu__jrddl['csv_reader_init']
        fpx__frt = numba.njit(nwmkx__kskq)
        compiled_funcs.append(fpx__frt)
        hdd__saxoo = compile_to_numba_ir(aarh__sktzj, {'_csv_reader_init':
            fpx__frt, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, goii__psedl), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(hdd__saxoo, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        yzyy__ythcl = hdd__saxoo.body[:-3]
        yzyy__ythcl[-1].target = csv_node.out_vars[0]
        return yzyy__ythcl
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    iybu__ovdnb = 'def csv_impl(fname, nrows, skiprows):\n'
    iybu__ovdnb += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    ijcqu__jrddl = {}
    exec(iybu__ovdnb, {}, ijcqu__jrddl)
    hjkz__dxje = ijcqu__jrddl['csv_impl']
    yomj__rgni = csv_node.usecols
    if yomj__rgni:
        yomj__rgni = [csv_node.usecols[uaxst__thol] for uaxst__thol in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        hbuk__aio = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        lytsz__zhl = csv_node.loc.strformat()
        lfczq__iszf = []
        tisi__qtes = []
        if yomj__rgni:
            for uaxst__thol in csv_node.out_used_cols:
                cvow__shlx = csv_node.df_colnames[uaxst__thol]
                lfczq__iszf.append(cvow__shlx)
                if isinstance(csv_node.out_types[uaxst__thol], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    tisi__qtes.append(cvow__shlx)
        bodo.user_logging.log_message('Column Pruning', hbuk__aio,
            lytsz__zhl, lfczq__iszf)
        if tisi__qtes:
            huyj__vespm = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                huyj__vespm, lytsz__zhl, tisi__qtes)
    qyyo__wvnw = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, yomj__rgni, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    hdd__saxoo = compile_to_numba_ir(hjkz__dxje, {'_csv_reader_py':
        qyyo__wvnw}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, goii__psedl), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(hdd__saxoo, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    yzyy__ythcl = hdd__saxoo.body[:-3]
    yzyy__ythcl[-1].target = csv_node.out_vars[1]
    yzyy__ythcl[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not yomj__rgni
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        yzyy__ythcl.pop(-1)
    elif not yomj__rgni:
        yzyy__ythcl.pop(-2)
    return yzyy__ythcl


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
    mztx__qhvqz = t.dtype
    if isinstance(mztx__qhvqz, PDCategoricalDtype):
        udqjg__bqdky = CategoricalArrayType(mztx__qhvqz)
        cfzy__isu = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, cfzy__isu, udqjg__bqdky)
        return cfzy__isu
    if mztx__qhvqz == types.NPDatetime('ns'):
        mztx__qhvqz = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        dhvq__bcp = 'int_arr_{}'.format(mztx__qhvqz)
        setattr(types, dhvq__bcp, t)
        return dhvq__bcp
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if mztx__qhvqz == types.bool_:
        mztx__qhvqz = 'bool_'
    if mztx__qhvqz == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(mztx__qhvqz, (
        StringArrayType, ArrayItemArrayType)):
        egwi__kud = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, egwi__kud, t)
        return egwi__kud
    return '{}[::1]'.format(mztx__qhvqz)


def _get_pd_dtype_str(t):
    mztx__qhvqz = t.dtype
    if isinstance(mztx__qhvqz, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(mztx__qhvqz.categories)
    if mztx__qhvqz == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if mztx__qhvqz.signed else 'U',
            mztx__qhvqz.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(mztx__qhvqz, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(mztx__qhvqz)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    cpj__wsjd = ''
    from collections import defaultdict
    lvte__rcqt = defaultdict(list)
    for psrl__zbxm, mjcna__yuwz in typemap.items():
        lvte__rcqt[mjcna__yuwz].append(psrl__zbxm)
    doe__bts = df.columns.to_list()
    tww__jdqsg = []
    for mjcna__yuwz, fzu__tce in lvte__rcqt.items():
        try:
            tww__jdqsg.append(df.loc[:, fzu__tce].astype(mjcna__yuwz, copy=
                False))
            df = df.drop(fzu__tce, axis=1)
        except (ValueError, TypeError) as trk__tuph:
            cpj__wsjd = (
                f"Caught the runtime error '{trk__tuph}' on columns {fzu__tce}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    rmim__ull = bool(cpj__wsjd)
    if parallel:
        yrrrp__rkzz = MPI.COMM_WORLD
        rmim__ull = yrrrp__rkzz.allreduce(rmim__ull, op=MPI.LOR)
    if rmim__ull:
        wyklo__kpco = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if cpj__wsjd:
            raise TypeError(f'{wyklo__kpco}\n{cpj__wsjd}')
        else:
            raise TypeError(
                f'{wyklo__kpco}\nPlease refer to errors on other ranks.')
    df = pd.concat(tww__jdqsg + [df], axis=1)
    dlmz__rrx = df.loc[:, doe__bts]
    return dlmz__rrx


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    fhkfo__qzu = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        iybu__ovdnb = '  skiprows = sorted(set(skiprows))\n'
    else:
        iybu__ovdnb = '  skiprows = [skiprows]\n'
    iybu__ovdnb += '  skiprows_list_len = len(skiprows)\n'
    iybu__ovdnb += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    iybu__ovdnb += '  check_java_installation(fname)\n'
    iybu__ovdnb += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    iybu__ovdnb += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    iybu__ovdnb += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    iybu__ovdnb += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, fhkfo__qzu, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    iybu__ovdnb += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    iybu__ovdnb += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    iybu__ovdnb += "      raise FileNotFoundError('File does not exist')\n"
    return iybu__ovdnb


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    ghp__lvro = [str(uaxst__thol) for uaxst__thol, apuk__uydz in enumerate(
        usecols) if col_typs[out_used_cols[uaxst__thol]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        ghp__lvro.append(str(idx_col_index))
    ctuoa__poorf = ', '.join(ghp__lvro)
    pqs__spq = _gen_parallel_flag_name(sanitized_cnames)
    hmg__sth = f"{pqs__spq}='bool_'" if check_parallel_runtime else ''
    rxsu__npn = [_get_pd_dtype_str(col_typs[out_used_cols[uaxst__thol]]) for
        uaxst__thol in range(len(usecols))]
    kaqov__rezh = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    ykdmy__qyxwn = [apuk__uydz for uaxst__thol, apuk__uydz in enumerate(
        usecols) if rxsu__npn[uaxst__thol] == 'str']
    if idx_col_index is not None and kaqov__rezh == 'str':
        ykdmy__qyxwn.append(idx_col_index)
    ljhk__rbucw = np.array(ykdmy__qyxwn, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = ljhk__rbucw
    iybu__ovdnb = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    gqxg__tes = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = gqxg__tes
    iybu__ovdnb += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    nwny__goixj = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = nwny__goixj
        iybu__ovdnb += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    hthez__jklz = defaultdict(list)
    for uaxst__thol, apuk__uydz in enumerate(usecols):
        if rxsu__npn[uaxst__thol] == 'str':
            continue
        hthez__jklz[rxsu__npn[uaxst__thol]].append(apuk__uydz)
    if idx_col_index is not None and kaqov__rezh != 'str':
        hthez__jklz[kaqov__rezh].append(idx_col_index)
    for uaxst__thol, kctsg__uuulm in enumerate(hthez__jklz.values()):
        glbs[f't_arr_{uaxst__thol}_{call_id}'] = np.asarray(kctsg__uuulm)
        iybu__ovdnb += (
            f'  t_arr_{uaxst__thol}_{call_id}_2 = t_arr_{uaxst__thol}_{call_id}\n'
            )
    if idx_col_index != None:
        iybu__ovdnb += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {hmg__sth}):
"""
    else:
        iybu__ovdnb += f'  with objmode(T=table_type_{call_id}, {hmg__sth}):\n'
    iybu__ovdnb += f'    typemap = {{}}\n'
    for uaxst__thol, nuht__ikatn in enumerate(hthez__jklz.keys()):
        iybu__ovdnb += f"""    typemap.update({{i:{nuht__ikatn} for i in t_arr_{uaxst__thol}_{call_id}_2}})
"""
    iybu__ovdnb += '    if f_reader.get_chunk_size() == 0:\n'
    iybu__ovdnb += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    iybu__ovdnb += '    else:\n'
    iybu__ovdnb += '      df = pd.read_csv(f_reader,\n'
    iybu__ovdnb += '        header=None,\n'
    iybu__ovdnb += '        parse_dates=[{}],\n'.format(ctuoa__poorf)
    iybu__ovdnb += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    iybu__ovdnb += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        iybu__ovdnb += f'    {pqs__spq} = f_reader.is_parallel()\n'
    else:
        iybu__ovdnb += f'    {pqs__spq} = {parallel}\n'
    iybu__ovdnb += f'    df = astype(df, typemap, {pqs__spq})\n'
    if idx_col_index != None:
        lipjz__smcny = sorted(gqxg__tes).index(idx_col_index)
        iybu__ovdnb += f'    idx_arr = df.iloc[:, {lipjz__smcny}].values\n'
        iybu__ovdnb += (
            f'    df.drop(columns=df.columns[{lipjz__smcny}], inplace=True)\n')
    if len(usecols) == 0:
        iybu__ovdnb += f'    T = None\n'
    else:
        iybu__ovdnb += f'    arrs = []\n'
        iybu__ovdnb += f'    for i in range(df.shape[1]):\n'
        iybu__ovdnb += f'      arrs.append(df.iloc[:, i].values)\n'
        iybu__ovdnb += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return iybu__ovdnb


def _gen_parallel_flag_name(sanitized_cnames):
    pqs__spq = '_parallel_value'
    while pqs__spq in sanitized_cnames:
        pqs__spq = '_' + pqs__spq
    return pqs__spq


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(hkkz__lcrio) for hkkz__lcrio in
        col_names]
    iybu__ovdnb = 'def csv_reader_py(fname, nrows, skiprows):\n'
    iybu__ovdnb += _gen_csv_file_reader_init(parallel, header, compression,
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    aanvu__tpiek = globals()
    if idx_col_typ != types.none:
        aanvu__tpiek[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        aanvu__tpiek[f'table_type_{call_id}'] = types.none
    else:
        aanvu__tpiek[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    iybu__ovdnb += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, aanvu__tpiek, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        iybu__ovdnb += '  return (T, idx_arr)\n'
    else:
        iybu__ovdnb += '  return (T, None)\n'
    ijcqu__jrddl = {}
    aanvu__tpiek['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(iybu__ovdnb, aanvu__tpiek, ijcqu__jrddl)
    qyyo__wvnw = ijcqu__jrddl['csv_reader_py']
    fpx__frt = numba.njit(qyyo__wvnw)
    compiled_funcs.append(fpx__frt)
    return fpx__frt
