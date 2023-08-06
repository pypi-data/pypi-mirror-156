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
    ttpv__oore = []
    bundn__kvfmo = []
    wltkl__gwwpu = []
    for urrwk__vzca, hdcla__wnibx in enumerate(json_node.out_vars):
        if hdcla__wnibx.name in lives:
            ttpv__oore.append(json_node.df_colnames[urrwk__vzca])
            bundn__kvfmo.append(json_node.out_vars[urrwk__vzca])
            wltkl__gwwpu.append(json_node.out_types[urrwk__vzca])
    json_node.df_colnames = ttpv__oore
    json_node.out_vars = bundn__kvfmo
    json_node.out_types = wltkl__gwwpu
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        flozw__ktdgg = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        jgqsh__ebi = json_node.loc.strformat()
        vxnko__ljbu = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', flozw__ktdgg,
            jgqsh__ebi, vxnko__ljbu)
        nku__jsy = [tfmt__bjvc for urrwk__vzca, tfmt__bjvc in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            urrwk__vzca], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if nku__jsy:
            dha__zxnaj = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', dha__zxnaj,
                jgqsh__ebi, nku__jsy)
    parallel = False
    if array_dists is not None:
        parallel = True
        for vuicu__ijru in json_node.out_vars:
            if array_dists[vuicu__ijru.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                vuicu__ijru.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    yax__rne = len(json_node.out_vars)
    ytbpn__aos = ', '.join('arr' + str(urrwk__vzca) for urrwk__vzca in
        range(yax__rne))
    gbs__fdqh = 'def json_impl(fname):\n'
    gbs__fdqh += '    ({},) = _json_reader_py(fname)\n'.format(ytbpn__aos)
    zmmda__bifo = {}
    exec(gbs__fdqh, {}, zmmda__bifo)
    nlnk__jfik = zmmda__bifo['json_impl']
    krfxb__gshh = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    ckho__iaufz = compile_to_numba_ir(nlnk__jfik, {'_json_reader_py':
        krfxb__gshh}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(ckho__iaufz, [json_node.file_name])
    bgr__bpawy = ckho__iaufz.body[:-3]
    for urrwk__vzca in range(len(json_node.out_vars)):
        bgr__bpawy[-len(json_node.out_vars) + urrwk__vzca
            ].target = json_node.out_vars[urrwk__vzca]
    return bgr__bpawy


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
    isxd__siwk = [sanitize_varname(tfmt__bjvc) for tfmt__bjvc in col_names]
    imw__ucx = ', '.join(str(urrwk__vzca) for urrwk__vzca, doaz__wpgfz in
        enumerate(col_typs) if doaz__wpgfz.dtype == types.NPDatetime('ns'))
    fknw__vkwn = ', '.join(["{}='{}'".format(ouds__waegd, bodo.ir.csv_ext.
        _get_dtype_str(doaz__wpgfz)) for ouds__waegd, doaz__wpgfz in zip(
        isxd__siwk, col_typs)])
    gamp__ntzv = ', '.join(["'{}':{}".format(qsy__ewnof, bodo.ir.csv_ext.
        _get_pd_dtype_str(doaz__wpgfz)) for qsy__ewnof, doaz__wpgfz in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    gbs__fdqh = 'def json_reader_py(fname):\n'
    gbs__fdqh += '  df_typeref_2 = df_typeref\n'
    gbs__fdqh += '  check_java_installation(fname)\n'
    gbs__fdqh += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    gbs__fdqh += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    gbs__fdqh += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    gbs__fdqh += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    gbs__fdqh += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    gbs__fdqh += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    gbs__fdqh += "      raise FileNotFoundError('File does not exist')\n"
    gbs__fdqh += f'  with objmode({fknw__vkwn}):\n'
    gbs__fdqh += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    gbs__fdqh += f'       convert_dates = {convert_dates}, \n'
    gbs__fdqh += f'       precise_float={precise_float}, \n'
    gbs__fdqh += f'       lines={lines}, \n'
    gbs__fdqh += '       dtype={{{}}},\n'.format(gamp__ntzv)
    gbs__fdqh += '       )\n'
    gbs__fdqh += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for ouds__waegd, qsy__ewnof in zip(isxd__siwk, col_names):
        gbs__fdqh += '    if len(df) > 0:\n'
        gbs__fdqh += "        {} = df['{}'].values\n".format(ouds__waegd,
            qsy__ewnof)
        gbs__fdqh += '    else:\n'
        gbs__fdqh += '        {} = np.array([])\n'.format(ouds__waegd)
    gbs__fdqh += '  return ({},)\n'.format(', '.join(jhbo__agi for
        jhbo__agi in isxd__siwk))
    xtpqx__qekil = globals()
    xtpqx__qekil.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode':
        objmode, 'check_java_installation': check_java_installation,
        'df_typeref': bodo.DataFrameType(tuple(col_typs), bodo.
        RangeIndexType(None), tuple(col_names)),
        'get_storage_options_pyobject': get_storage_options_pyobject})
    zmmda__bifo = {}
    exec(gbs__fdqh, xtpqx__qekil, zmmda__bifo)
    krfxb__gshh = zmmda__bifo['json_reader_py']
    vpmh__dozs = numba.njit(krfxb__gshh)
    compiled_funcs.append(vpmh__dozs)
    return vpmh__dozs
