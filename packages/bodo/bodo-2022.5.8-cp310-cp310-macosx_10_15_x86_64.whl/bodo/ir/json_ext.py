import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_java_installation, sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines,
        compression, storage_options):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression
        self.storage_options = storage_options

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)
json_file_chunk_reader = types.ExternalFunction('json_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    bool_, types.int64, types.voidptr, types.voidptr,
    storage_options_dict_type))


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    xkga__yrxfl = []
    xjjs__xtpsq = []
    kjmiy__nsr = []
    for wcy__mxzw, tvkj__mwyvx in enumerate(json_node.out_vars):
        if tvkj__mwyvx.name in lives:
            xkga__yrxfl.append(json_node.df_colnames[wcy__mxzw])
            xjjs__xtpsq.append(json_node.out_vars[wcy__mxzw])
            kjmiy__nsr.append(json_node.out_types[wcy__mxzw])
    json_node.df_colnames = xkga__yrxfl
    json_node.out_vars = xjjs__xtpsq
    json_node.out_types = kjmiy__nsr
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        lzwz__fodkq = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        uocw__qqc = json_node.loc.strformat()
        emli__dtvsk = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', lzwz__fodkq,
            uocw__qqc, emli__dtvsk)
        lby__mahj = [qtpz__shjds for wcy__mxzw, qtpz__shjds in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            wcy__mxzw], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if lby__mahj:
            hov__nmxit = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', hov__nmxit,
                uocw__qqc, lby__mahj)
    parallel = False
    if array_dists is not None:
        parallel = True
        for vggw__horr in json_node.out_vars:
            if array_dists[vggw__horr.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                vggw__horr.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    jvb__mapo = len(json_node.out_vars)
    uwmii__iicwc = ', '.join('arr' + str(wcy__mxzw) for wcy__mxzw in range(
        jvb__mapo))
    alvvr__fvqt = 'def json_impl(fname):\n'
    alvvr__fvqt += '    ({},) = _json_reader_py(fname)\n'.format(uwmii__iicwc)
    mkqp__hgt = {}
    exec(alvvr__fvqt, {}, mkqp__hgt)
    skmt__zrqm = mkqp__hgt['json_impl']
    nqel__hzj = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    txz__gut = compile_to_numba_ir(skmt__zrqm, {'_json_reader_py':
        nqel__hzj}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(txz__gut, [json_node.file_name])
    pfk__rwda = txz__gut.body[:-3]
    for wcy__mxzw in range(len(json_node.out_vars)):
        pfk__rwda[-len(json_node.out_vars) + wcy__mxzw
            ].target = json_node.out_vars[wcy__mxzw]
    return pfk__rwda


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression, storage_options):
    wnkj__jtqby = [sanitize_varname(qtpz__shjds) for qtpz__shjds in col_names]
    bfwtg__qxlr = ', '.join(str(wcy__mxzw) for wcy__mxzw, ebfwj__opd in
        enumerate(col_typs) if ebfwj__opd.dtype == types.NPDatetime('ns'))
    zdbn__ksv = ', '.join(["{}='{}'".format(mvwbt__ogej, bodo.ir.csv_ext.
        _get_dtype_str(ebfwj__opd)) for mvwbt__ogej, ebfwj__opd in zip(
        wnkj__jtqby, col_typs)])
    mwt__bljd = ', '.join(["'{}':{}".format(fyn__oqyjj, bodo.ir.csv_ext.
        _get_pd_dtype_str(ebfwj__opd)) for fyn__oqyjj, ebfwj__opd in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    alvvr__fvqt = 'def json_reader_py(fname):\n'
    alvvr__fvqt += '  df_typeref_2 = df_typeref\n'
    alvvr__fvqt += '  check_java_installation(fname)\n'
    alvvr__fvqt += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    alvvr__fvqt += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    alvvr__fvqt += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    alvvr__fvqt += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    alvvr__fvqt += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    alvvr__fvqt += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    alvvr__fvqt += "      raise FileNotFoundError('File does not exist')\n"
    alvvr__fvqt += f'  with objmode({zdbn__ksv}):\n'
    alvvr__fvqt += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    alvvr__fvqt += f'       convert_dates = {convert_dates}, \n'
    alvvr__fvqt += f'       precise_float={precise_float}, \n'
    alvvr__fvqt += f'       lines={lines}, \n'
    alvvr__fvqt += '       dtype={{{}}},\n'.format(mwt__bljd)
    alvvr__fvqt += '       )\n'
    alvvr__fvqt += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for mvwbt__ogej, fyn__oqyjj in zip(wnkj__jtqby, col_names):
        alvvr__fvqt += '    if len(df) > 0:\n'
        alvvr__fvqt += "        {} = df['{}'].values\n".format(mvwbt__ogej,
            fyn__oqyjj)
        alvvr__fvqt += '    else:\n'
        alvvr__fvqt += '        {} = np.array([])\n'.format(mvwbt__ogej)
    alvvr__fvqt += '  return ({},)\n'.format(', '.join(gtyx__amfjp for
        gtyx__amfjp in wnkj__jtqby))
    orbyz__kufc = globals()
    orbyz__kufc.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode':
        objmode, 'check_java_installation': check_java_installation,
        'df_typeref': bodo.DataFrameType(tuple(col_typs), bodo.
        RangeIndexType(None), tuple(col_names)),
        'get_storage_options_pyobject': get_storage_options_pyobject})
    mkqp__hgt = {}
    exec(alvvr__fvqt, orbyz__kufc, mkqp__hgt)
    nqel__hzj = mkqp__hgt['json_reader_py']
    tzpf__wtsg = numba.njit(nqel__hzj)
    compiled_funcs.append(tzpf__wtsg)
    return tzpf__wtsg
