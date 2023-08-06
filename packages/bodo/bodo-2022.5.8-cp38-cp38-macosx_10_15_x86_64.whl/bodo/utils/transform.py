"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'datetime_date_arr_to_dt64_arr', 'pd_timestamp_ext', 'hiframes', bodo),
    (bodo.libs.bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_compute_var_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    '_sem_handle_nan', 'series_kernels', 'hiframes', bodo), ('dist_return',
    'distributed_api', 'libs', bodo), ('rep_return', 'distributed_api',
    'libs', bodo), ('init_dataframe', 'pd_dataframe_ext', 'hiframes', bodo),
    ('get_dataframe_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_table', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_column_names', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_table_data', 'table', 'hiframes', bodo), ('get_dataframe_index',
    'pd_dataframe_ext', 'hiframes', bodo), ('init_rolling',
    'pd_rolling_ext', 'hiframes', bodo), ('init_groupby', 'pd_groupby_ext',
    'hiframes', bodo), ('calc_nitems', 'array_kernels', 'libs', bodo), (
    'concat', 'array_kernels', 'libs', bodo), ('unique', 'array_kernels',
    'libs', bodo), ('nunique', 'array_kernels', 'libs', bodo), ('quantile',
    'array_kernels', 'libs', bodo), ('explode', 'array_kernels', 'libs',
    bodo), ('explode_no_index', 'array_kernels', 'libs', bodo), (
    'get_arr_lens', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'get_str_arr_str_length', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('arange', np), (
    'internal_prange', 'parfor', numba), ('internal_prange', 'parfor',
    'parfors', numba), ('empty_inferred', 'ndarray', 'unsafe', numba), (
    '_slice_span', 'unicode', numba), ('_normalize_slice', 'unicode', numba
    ), ('init_session_builder', 'pyspark_ext', 'libs', bodo), (
    'init_session', 'pyspark_ext', 'libs', bodo), ('init_spark_df',
    'pyspark_ext', 'libs', bodo), ('h5size', 'h5_api', 'io', bodo), (
    'pre_alloc_struct_array', 'struct_arr_ext', 'libs', bodo), (bodo.libs.
    struct_arr_ext.pre_alloc_struct_array,), ('pre_alloc_tuple_array',
    'tuple_arr_ext', 'libs', bodo), (bodo.libs.tuple_arr_ext.
    pre_alloc_tuple_array,), ('pre_alloc_array_item_array',
    'array_item_arr_ext', 'libs', bodo), (bodo.libs.array_item_arr_ext.
    pre_alloc_array_item_array,), ('dist_reduce', 'distributed_api', 'libs',
    bodo), (bodo.libs.distributed_api.dist_reduce,), (
    'pre_alloc_string_array', 'str_arr_ext', 'libs', bodo), (bodo.libs.
    str_arr_ext.pre_alloc_string_array,), ('pre_alloc_binary_array',
    'binary_arr_ext', 'libs', bodo), (bodo.libs.binary_arr_ext.
    pre_alloc_binary_array,), ('pre_alloc_map_array', 'map_arr_ext', 'libs',
    bodo), (bodo.libs.map_arr_ext.pre_alloc_map_array,), (
    'convert_dict_arr_to_int', 'dict_arr_ext', 'libs', bodo), (
    'cat_dict_str', 'dict_arr_ext', 'libs', bodo), ('str_replace',
    'dict_arr_ext', 'libs', bodo), ('dict_arr_eq', 'dict_arr_ext', 'libs',
    bodo), ('dict_arr_ne', 'dict_arr_ext', 'libs', bodo), ('str_startswith',
    'dict_arr_ext', 'libs', bodo), ('str_endswith', 'dict_arr_ext', 'libs',
    bodo), ('str_contains_non_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_series_contains_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_capitalize', 'dict_arr_ext', 'libs', bodo), ('str_lower',
    'dict_arr_ext', 'libs', bodo), ('str_swapcase', 'dict_arr_ext', 'libs',
    bodo), ('str_title', 'dict_arr_ext', 'libs', bodo), ('str_upper',
    'dict_arr_ext', 'libs', bodo), ('str_center', 'dict_arr_ext', 'libs',
    bodo), ('str_get', 'dict_arr_ext', 'libs', bodo), ('str_repeat_int',
    'dict_arr_ext', 'libs', bodo), ('str_lstrip', 'dict_arr_ext', 'libs',
    bodo), ('str_rstrip', 'dict_arr_ext', 'libs', bodo), ('str_strip',
    'dict_arr_ext', 'libs', bodo), ('str_zfill', 'dict_arr_ext', 'libs',
    bodo), ('str_ljust', 'dict_arr_ext', 'libs', bodo), ('str_rjust',
    'dict_arr_ext', 'libs', bodo), ('str_find', 'dict_arr_ext', 'libs',
    bodo), ('str_rfind', 'dict_arr_ext', 'libs', bodo), ('str_slice',
    'dict_arr_ext', 'libs', bodo), ('str_extract', 'dict_arr_ext', 'libs',
    bodo), ('str_extractall', 'dict_arr_ext', 'libs', bodo), (
    'str_extractall_multi', 'dict_arr_ext', 'libs', bodo), ('str_len',
    'dict_arr_ext', 'libs', bodo), ('str_count', 'dict_arr_ext', 'libs',
    bodo), ('str_isalnum', 'dict_arr_ext', 'libs', bodo), ('str_isalpha',
    'dict_arr_ext', 'libs', bodo), ('str_isdigit', 'dict_arr_ext', 'libs',
    bodo), ('str_isspace', 'dict_arr_ext', 'libs', bodo), ('str_islower',
    'dict_arr_ext', 'libs', bodo), ('str_isupper', 'dict_arr_ext', 'libs',
    bodo), ('str_istitle', 'dict_arr_ext', 'libs', bodo), ('str_isnumeric',
    'dict_arr_ext', 'libs', bodo), ('str_isdecimal', 'dict_arr_ext', 'libs',
    bodo), ('prange', bodo), (bodo.prange,), ('objmode', bodo), (bodo.
    objmode,), ('get_label_dict_from_categories', 'pd_categorial_ext',
    'hiframes', bodo), ('get_label_dict_from_categories_no_duplicates',
    'pd_categorial_ext', 'hiframes', bodo), ('build_nullable_tuple',
    'nullable_tuple_ext', 'libs', bodo), ('generate_mappable_table_func',
    'table_utils', 'utils', bodo), ('table_astype', 'table_utils', 'utils',
    bodo), ('table_concat', 'table_utils', 'utils', bodo), ('table_filter',
    'table', 'hiframes', bodo), ('table_subset', 'table', 'hiframes', bodo)}


def remove_hiframes(rhs, lives, call_list):
    jvtp__inoel = tuple(call_list)
    if jvtp__inoel in no_side_effect_call_tuples:
        return True
    if jvtp__inoel == (bodo.hiframes.pd_index_ext.init_range_index,):
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if call_list == ['set_table_data_null', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['ensure_column_unboxed', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives and rhs.args[1].name not in lives:
        return True
    if call_list == ['generate_table_nbytes', 'table_utils', 'utils', bodo
        ] and rhs.args[1].name not in lives:
        return True
    if len(jvtp__inoel) == 1 and tuple in getattr(jvtp__inoel[0], '__mro__', ()
        ):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        gzm__nul = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        gzm__nul = func.__globals__
    if extra_globals is not None:
        gzm__nul.update(extra_globals)
    if add_default_globals:
        gzm__nul.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, gzm__nul, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[ameg__grnvb.name] for ameg__grnvb in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, gzm__nul)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        mcxi__biv = tuple(typing_info.typemap[ameg__grnvb.name] for
            ameg__grnvb in args)
        glhc__nnl = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, mcxi__biv, {}, {}, flags)
        glhc__nnl.run()
    hoa__cwzh = f_ir.blocks.popitem()[1]
    replace_arg_nodes(hoa__cwzh, args)
    fynu__zdgl = hoa__cwzh.body[:-2]
    update_locs(fynu__zdgl[len(args):], loc)
    for stmt in fynu__zdgl[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        bfct__xpnr = hoa__cwzh.body[-2]
        assert is_assign(bfct__xpnr) and is_expr(bfct__xpnr.value, 'cast')
        uaysd__gjq = bfct__xpnr.value.value
        fynu__zdgl.append(ir.Assign(uaysd__gjq, ret_var, loc))
    return fynu__zdgl


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for sunn__acr in stmt.list_vars():
            sunn__acr.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        uziaj__hgrsp = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        haio__jzhxt, ieafy__ruqe = uziaj__hgrsp(stmt)
        return ieafy__ruqe
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        syxz__sjc = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(syxz__sjc, ir.UndefinedType):
            ffej__vevky = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{ffej__vevky}' is not defined", loc=loc)
    except GuardException as gdchm__vov:
        raise BodoError(err_msg, loc=loc)
    return syxz__sjc


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    ilf__owwfa = get_definition(func_ir, var)
    uvim__wzh = None
    if typemap is not None:
        uvim__wzh = typemap.get(var.name, None)
    if isinstance(ilf__owwfa, ir.Arg) and arg_types is not None:
        uvim__wzh = arg_types[ilf__owwfa.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(uvim__wzh):
        return get_literal_value(uvim__wzh)
    if isinstance(ilf__owwfa, (ir.Const, ir.Global, ir.FreeVar)):
        syxz__sjc = ilf__owwfa.value
        return syxz__sjc
    if literalize_args and isinstance(ilf__owwfa, ir.Arg
        ) and can_literalize_type(uvim__wzh, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({ilf__owwfa.index}, loc=var
            .loc, file_infos={ilf__owwfa.index: file_info} if file_info is not
            None else None)
    if is_expr(ilf__owwfa, 'binop'):
        if file_info and ilf__owwfa.fn == operator.add:
            try:
                her__muzjv = get_const_value_inner(func_ir, ilf__owwfa.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(her__muzjv, True)
                njfgk__xqj = get_const_value_inner(func_ir, ilf__owwfa.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return ilf__owwfa.fn(her__muzjv, njfgk__xqj)
            except (GuardException, BodoConstUpdatedError) as gdchm__vov:
                pass
            try:
                njfgk__xqj = get_const_value_inner(func_ir, ilf__owwfa.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(njfgk__xqj, False)
                her__muzjv = get_const_value_inner(func_ir, ilf__owwfa.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return ilf__owwfa.fn(her__muzjv, njfgk__xqj)
            except (GuardException, BodoConstUpdatedError) as gdchm__vov:
                pass
        her__muzjv = get_const_value_inner(func_ir, ilf__owwfa.lhs,
            arg_types, typemap, updated_containers)
        njfgk__xqj = get_const_value_inner(func_ir, ilf__owwfa.rhs,
            arg_types, typemap, updated_containers)
        return ilf__owwfa.fn(her__muzjv, njfgk__xqj)
    if is_expr(ilf__owwfa, 'unary'):
        syxz__sjc = get_const_value_inner(func_ir, ilf__owwfa.value,
            arg_types, typemap, updated_containers)
        return ilf__owwfa.fn(syxz__sjc)
    if is_expr(ilf__owwfa, 'getattr') and typemap:
        dlng__ipk = typemap.get(ilf__owwfa.value.name, None)
        if isinstance(dlng__ipk, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and ilf__owwfa.attr == 'columns':
            return pd.Index(dlng__ipk.columns)
        if isinstance(dlng__ipk, types.SliceType):
            vpwuf__qam = get_definition(func_ir, ilf__owwfa.value)
            require(is_call(vpwuf__qam))
            iarv__fvr = find_callname(func_ir, vpwuf__qam)
            odlbn__mvhju = False
            if iarv__fvr == ('_normalize_slice', 'numba.cpython.unicode'):
                require(ilf__owwfa.attr in ('start', 'step'))
                vpwuf__qam = get_definition(func_ir, vpwuf__qam.args[0])
                odlbn__mvhju = True
            require(find_callname(func_ir, vpwuf__qam) == ('slice', 'builtins')
                )
            if len(vpwuf__qam.args) == 1:
                if ilf__owwfa.attr == 'start':
                    return 0
                if ilf__owwfa.attr == 'step':
                    return 1
                require(ilf__owwfa.attr == 'stop')
                return get_const_value_inner(func_ir, vpwuf__qam.args[0],
                    arg_types, typemap, updated_containers)
            if ilf__owwfa.attr == 'start':
                syxz__sjc = get_const_value_inner(func_ir, vpwuf__qam.args[
                    0], arg_types, typemap, updated_containers)
                if syxz__sjc is None:
                    syxz__sjc = 0
                if odlbn__mvhju:
                    require(syxz__sjc == 0)
                return syxz__sjc
            if ilf__owwfa.attr == 'stop':
                assert not odlbn__mvhju
                return get_const_value_inner(func_ir, vpwuf__qam.args[1],
                    arg_types, typemap, updated_containers)
            require(ilf__owwfa.attr == 'step')
            if len(vpwuf__qam.args) == 2:
                return 1
            else:
                syxz__sjc = get_const_value_inner(func_ir, vpwuf__qam.args[
                    2], arg_types, typemap, updated_containers)
                if syxz__sjc is None:
                    syxz__sjc = 1
                if odlbn__mvhju:
                    require(syxz__sjc == 1)
                return syxz__sjc
    if is_expr(ilf__owwfa, 'getattr'):
        return getattr(get_const_value_inner(func_ir, ilf__owwfa.value,
            arg_types, typemap, updated_containers), ilf__owwfa.attr)
    if is_expr(ilf__owwfa, 'getitem'):
        value = get_const_value_inner(func_ir, ilf__owwfa.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, ilf__owwfa.index, arg_types,
            typemap, updated_containers)
        return value[index]
    ryu__xogf = guard(find_callname, func_ir, ilf__owwfa, typemap)
    if ryu__xogf is not None and len(ryu__xogf) == 2 and ryu__xogf[0
        ] == 'keys' and isinstance(ryu__xogf[1], ir.Var):
        qxmz__fcfty = ilf__owwfa.func
        ilf__owwfa = get_definition(func_ir, ryu__xogf[1])
        zks__hrfd = ryu__xogf[1].name
        if updated_containers and zks__hrfd in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                zks__hrfd, updated_containers[zks__hrfd]))
        require(is_expr(ilf__owwfa, 'build_map'))
        vals = [sunn__acr[0] for sunn__acr in ilf__owwfa.items]
        lsgna__xlvt = guard(get_definition, func_ir, qxmz__fcfty)
        assert isinstance(lsgna__xlvt, ir.Expr) and lsgna__xlvt.attr == 'keys'
        lsgna__xlvt.attr = 'copy'
        return [get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in vals]
    if is_expr(ilf__owwfa, 'build_map'):
        return {get_const_value_inner(func_ir, sunn__acr[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            sunn__acr[1], arg_types, typemap, updated_containers) for
            sunn__acr in ilf__owwfa.items}
    if is_expr(ilf__owwfa, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in ilf__owwfa.items)
    if is_expr(ilf__owwfa, 'build_list'):
        return [get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in ilf__owwfa.items]
    if is_expr(ilf__owwfa, 'build_set'):
        return {get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in ilf__owwfa.items}
    if ryu__xogf == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if ryu__xogf == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('range', 'builtins') and len(ilf__owwfa.args) == 1:
        return range(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, sunn__acr,
            arg_types, typemap, updated_containers) for sunn__acr in
            ilf__owwfa.args))
    if ryu__xogf == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('format', 'builtins'):
        ameg__grnvb = get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers)
        fhs__wtrq = get_const_value_inner(func_ir, ilf__owwfa.args[1],
            arg_types, typemap, updated_containers) if len(ilf__owwfa.args
            ) > 1 else ''
        return format(ameg__grnvb, fhs__wtrq)
    if ryu__xogf in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'
        ), ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, ilf__owwfa.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, ilf__owwfa.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            ilf__owwfa.args[2], arg_types, typemap, updated_containers))
    if ryu__xogf == ('len', 'builtins') and typemap and isinstance(typemap.
        get(ilf__owwfa.args[0].name, None), types.BaseTuple):
        return len(typemap[ilf__owwfa.args[0].name])
    if ryu__xogf == ('len', 'builtins'):
        hqs__hcdus = guard(get_definition, func_ir, ilf__owwfa.args[0])
        if isinstance(hqs__hcdus, ir.Expr) and hqs__hcdus.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(hqs__hcdus.items)
        return len(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf == ('CategoricalDtype', 'pandas'):
        kws = dict(ilf__owwfa.kws)
        fmqe__hrde = get_call_expr_arg('CategoricalDtype', ilf__owwfa.args,
            kws, 0, 'categories', '')
        lqbfk__ufyaj = get_call_expr_arg('CategoricalDtype', ilf__owwfa.
            args, kws, 1, 'ordered', False)
        if lqbfk__ufyaj is not False:
            lqbfk__ufyaj = get_const_value_inner(func_ir, lqbfk__ufyaj,
                arg_types, typemap, updated_containers)
        if fmqe__hrde == '':
            fmqe__hrde = None
        else:
            fmqe__hrde = get_const_value_inner(func_ir, fmqe__hrde,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(fmqe__hrde, lqbfk__ufyaj)
    if ryu__xogf == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, ilf__owwfa.args[0],
            arg_types, typemap, updated_containers))
    if ryu__xogf is not None and len(ryu__xogf) == 2 and ryu__xogf[1
        ] == 'pandas' and ryu__xogf[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, ryu__xogf[0])()
    if ryu__xogf is not None and len(ryu__xogf) == 2 and isinstance(ryu__xogf
        [1], ir.Var):
        syxz__sjc = get_const_value_inner(func_ir, ryu__xogf[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in ilf__owwfa.args]
        kws = {aehq__ogyv[0]: get_const_value_inner(func_ir, aehq__ogyv[1],
            arg_types, typemap, updated_containers) for aehq__ogyv in
            ilf__owwfa.kws}
        return getattr(syxz__sjc, ryu__xogf[0])(*args, **kws)
    if ryu__xogf is not None and len(ryu__xogf) == 2 and ryu__xogf[1
        ] == 'bodo' and ryu__xogf[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in ilf__owwfa.args)
        kwargs = {ffej__vevky: get_const_value_inner(func_ir, sunn__acr,
            arg_types, typemap, updated_containers) for ffej__vevky,
            sunn__acr in dict(ilf__owwfa.kws).items()}
        return getattr(bodo, ryu__xogf[0])(*args, **kwargs)
    if is_call(ilf__owwfa) and typemap and isinstance(typemap.get(
        ilf__owwfa.func.name, None), types.Dispatcher):
        py_func = typemap[ilf__owwfa.func.name].dispatcher.py_func
        require(ilf__owwfa.vararg is None)
        args = tuple(get_const_value_inner(func_ir, sunn__acr, arg_types,
            typemap, updated_containers) for sunn__acr in ilf__owwfa.args)
        kwargs = {ffej__vevky: get_const_value_inner(func_ir, sunn__acr,
            arg_types, typemap, updated_containers) for ffej__vevky,
            sunn__acr in dict(ilf__owwfa.kws).items()}
        arg_types = tuple(bodo.typeof(sunn__acr) for sunn__acr in args)
        kw_types = {fmd__lgf: bodo.typeof(sunn__acr) for fmd__lgf,
            sunn__acr in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, xfnjr__wgn, xfnjr__wgn = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    suv__axt = guard(get_definition, f_ir, rhs.func)
                    if isinstance(suv__axt, ir.Const) and isinstance(suv__axt
                        .value, numba.core.dispatcher.ObjModeLiftedWith):
                        return False
                    wyv__qjibl = guard(find_callname, f_ir, rhs)
                    if wyv__qjibl is None:
                        return False
                    func_name, yyn__hrfo = wyv__qjibl
                    if yyn__hrfo == 'pandas' and func_name.startswith('read_'):
                        return False
                    if wyv__qjibl in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if wyv__qjibl == ('File', 'h5py'):
                        return False
                    if isinstance(yyn__hrfo, ir.Var):
                        uvim__wzh = typemap[yyn__hrfo.name]
                        if isinstance(uvim__wzh, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(uvim__wzh, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(uvim__wzh, bodo.LoggingLoggerType):
                            return False
                        if str(uvim__wzh).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            yyn__hrfo), ir.Arg)):
                            return False
                    if yyn__hrfo in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        gmnh__wyi = func.literal_value.code
        najf__nzwd = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            najf__nzwd = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(najf__nzwd, gmnh__wyi)
        fix_struct_return(f_ir)
        typemap, wqhxr__grmpu, dow__xyw, xfnjr__wgn = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, dow__xyw, wqhxr__grmpu = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, dow__xyw, wqhxr__grmpu = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, dow__xyw, wqhxr__grmpu = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(wqhxr__grmpu, types.DictType):
        moimg__qcm = guard(get_struct_keynames, f_ir, typemap)
        if moimg__qcm is not None:
            wqhxr__grmpu = StructType((wqhxr__grmpu.value_type,) * len(
                moimg__qcm), moimg__qcm)
    if is_udf and isinstance(wqhxr__grmpu, (SeriesType,
        HeterogeneousSeriesType)):
        zoq__ikfzx = numba.core.registry.cpu_target.typing_context
        nzuo__qqy = numba.core.registry.cpu_target.target_context
        sxigh__enq = bodo.transforms.series_pass.SeriesPass(f_ir,
            zoq__ikfzx, nzuo__qqy, typemap, dow__xyw, {})
        sxigh__enq.run()
        sxigh__enq.run()
        sxigh__enq.run()
        bii__ayfma = compute_cfg_from_blocks(f_ir.blocks)
        ktu__novg = [guard(_get_const_series_info, f_ir.blocks[xkocg__bvbu],
            f_ir, typemap) for xkocg__bvbu in bii__ayfma.exit_points() if
            isinstance(f_ir.blocks[xkocg__bvbu].body[-1], ir.Return)]
        if None in ktu__novg or len(pd.Series(ktu__novg).unique()) != 1:
            wqhxr__grmpu.const_info = None
        else:
            wqhxr__grmpu.const_info = ktu__novg[0]
    return wqhxr__grmpu


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    jblgn__zajqf = block.body[-1].value
    itn__rruzk = get_definition(f_ir, jblgn__zajqf)
    require(is_expr(itn__rruzk, 'cast'))
    itn__rruzk = get_definition(f_ir, itn__rruzk.value)
    require(is_call(itn__rruzk) and find_callname(f_ir, itn__rruzk) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    dmm__kcgy = itn__rruzk.args[1]
    cdz__olxzv = tuple(get_const_value_inner(f_ir, dmm__kcgy, typemap=typemap))
    if isinstance(typemap[jblgn__zajqf.name], HeterogeneousSeriesType):
        return len(typemap[jblgn__zajqf.name].data), cdz__olxzv
    yhinr__oxokp = itn__rruzk.args[0]
    oegi__kbv = get_definition(f_ir, yhinr__oxokp)
    func_name, nym__otuu = find_callname(f_ir, oegi__kbv)
    if is_call(oegi__kbv) and bodo.utils.utils.is_alloc_callname(func_name,
        nym__otuu):
        nlsy__dkfdf = oegi__kbv.args[0]
        hrjz__yqzs = get_const_value_inner(f_ir, nlsy__dkfdf, typemap=typemap)
        return hrjz__yqzs, cdz__olxzv
    if is_call(oegi__kbv) and find_callname(f_ir, oegi__kbv) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'), (
        'build_nullable_tuple', 'bodo.libs.nullable_tuple_ext')]:
        yhinr__oxokp = oegi__kbv.args[0]
        oegi__kbv = get_definition(f_ir, yhinr__oxokp)
    require(is_expr(oegi__kbv, 'build_tuple') or is_expr(oegi__kbv,
        'build_list'))
    return len(oegi__kbv.items), cdz__olxzv


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    djtvw__iwwf = []
    yft__vpcs = []
    values = []
    for fmd__lgf, sunn__acr in build_map.items:
        yys__bkues = find_const(f_ir, fmd__lgf)
        require(isinstance(yys__bkues, str))
        yft__vpcs.append(yys__bkues)
        djtvw__iwwf.append(fmd__lgf)
        values.append(sunn__acr)
    fowb__ybz = ir.Var(scope, mk_unique_var('val_tup'), loc)
    kyhq__npkpb = ir.Assign(ir.Expr.build_tuple(values, loc), fowb__ybz, loc)
    f_ir._definitions[fowb__ybz.name] = [kyhq__npkpb.value]
    iive__wsxys = ir.Var(scope, mk_unique_var('key_tup'), loc)
    zjxhk__dyrz = ir.Assign(ir.Expr.build_tuple(djtvw__iwwf, loc),
        iive__wsxys, loc)
    f_ir._definitions[iive__wsxys.name] = [zjxhk__dyrz.value]
    if typemap is not None:
        typemap[fowb__ybz.name] = types.Tuple([typemap[sunn__acr.name] for
            sunn__acr in values])
        typemap[iive__wsxys.name] = types.Tuple([typemap[sunn__acr.name] for
            sunn__acr in djtvw__iwwf])
    return yft__vpcs, fowb__ybz, kyhq__npkpb, iive__wsxys, zjxhk__dyrz


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    isosr__nitnk = block.body[-1].value
    rku__ufaw = guard(get_definition, f_ir, isosr__nitnk)
    require(is_expr(rku__ufaw, 'cast'))
    itn__rruzk = guard(get_definition, f_ir, rku__ufaw.value)
    require(is_expr(itn__rruzk, 'build_map'))
    require(len(itn__rruzk.items) > 0)
    loc = block.loc
    scope = block.scope
    yft__vpcs, fowb__ybz, kyhq__npkpb, iive__wsxys, zjxhk__dyrz = (
        extract_keyvals_from_struct_map(f_ir, itn__rruzk, loc, scope))
    sga__dbgxg = ir.Var(scope, mk_unique_var('conv_call'), loc)
    xfgc__lea = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), sga__dbgxg, loc)
    f_ir._definitions[sga__dbgxg.name] = [xfgc__lea.value]
    lmh__sqvn = ir.Var(scope, mk_unique_var('struct_val'), loc)
    xlj__vczr = ir.Assign(ir.Expr.call(sga__dbgxg, [fowb__ybz, iive__wsxys],
        {}, loc), lmh__sqvn, loc)
    f_ir._definitions[lmh__sqvn.name] = [xlj__vczr.value]
    rku__ufaw.value = lmh__sqvn
    itn__rruzk.items = [(fmd__lgf, fmd__lgf) for fmd__lgf, xfnjr__wgn in
        itn__rruzk.items]
    block.body = block.body[:-2] + [kyhq__npkpb, zjxhk__dyrz, xfgc__lea,
        xlj__vczr] + block.body[-2:]
    return tuple(yft__vpcs)


def get_struct_keynames(f_ir, typemap):
    bii__ayfma = compute_cfg_from_blocks(f_ir.blocks)
    lof__kzj = list(bii__ayfma.exit_points())[0]
    block = f_ir.blocks[lof__kzj]
    require(isinstance(block.body[-1], ir.Return))
    isosr__nitnk = block.body[-1].value
    rku__ufaw = guard(get_definition, f_ir, isosr__nitnk)
    require(is_expr(rku__ufaw, 'cast'))
    itn__rruzk = guard(get_definition, f_ir, rku__ufaw.value)
    require(is_call(itn__rruzk) and find_callname(f_ir, itn__rruzk) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[itn__rruzk.args[1].name])


def fix_struct_return(f_ir):
    efps__jtqc = None
    bii__ayfma = compute_cfg_from_blocks(f_ir.blocks)
    for lof__kzj in bii__ayfma.exit_points():
        efps__jtqc = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            lof__kzj], lof__kzj)
    return efps__jtqc


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    bug__rux = ir.Block(ir.Scope(None, loc), loc)
    bug__rux.body = node_list
    build_definitions({(0): bug__rux}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(sunn__acr) for sunn__acr in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    mnzrs__yodk = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(mnzrs__yodk, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for bedvd__xccm in range(len(vals) - 1, -1, -1):
        sunn__acr = vals[bedvd__xccm]
        if isinstance(sunn__acr, str) and sunn__acr.startswith(
            NESTED_TUP_SENTINEL):
            smm__ymsv = int(sunn__acr[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:bedvd__xccm]) + (
                tuple(vals[bedvd__xccm + 1:bedvd__xccm + smm__ymsv + 1]),) +
                tuple(vals[bedvd__xccm + smm__ymsv + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    ameg__grnvb = None
    if len(args) > arg_no and arg_no >= 0:
        ameg__grnvb = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        ameg__grnvb = kws[arg_name]
    if ameg__grnvb is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return ameg__grnvb


def set_call_expr_arg(var, args, kws, arg_no, arg_name, add_if_missing=False):
    if len(args) > arg_no:
        args[arg_no] = var
    elif add_if_missing or arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    gzm__nul = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        gzm__nul.update(extra_globals)
    func.__globals__.update(gzm__nul)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            qvaor__jqq = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[qvaor__jqq.name] = types.literal(default)
            except:
                pass_info.typemap[qvaor__jqq.name] = numba.typeof(default)
            usg__wjveu = ir.Assign(ir.Const(default, loc), qvaor__jqq, loc)
            pre_nodes.append(usg__wjveu)
            return qvaor__jqq
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    mcxi__biv = tuple(pass_info.typemap[sunn__acr.name] for sunn__acr in args)
    if const:
        tkete__wxk = []
        for bedvd__xccm, ameg__grnvb in enumerate(args):
            syxz__sjc = guard(find_const, pass_info.func_ir, ameg__grnvb)
            if syxz__sjc:
                tkete__wxk.append(types.literal(syxz__sjc))
            else:
                tkete__wxk.append(mcxi__biv[bedvd__xccm])
        mcxi__biv = tuple(tkete__wxk)
    return ReplaceFunc(func, mcxi__biv, args, gzm__nul, inline_bodo_calls,
        run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(ifqxq__wvku) for ifqxq__wvku in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        oawoc__fqm = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {oawoc__fqm} = 0\n', (oawoc__fqm,)
    if isinstance(t, ArrayItemArrayType):
        yiz__qanx, ppwdj__dtwk = gen_init_varsize_alloc_sizes(t.dtype)
        oawoc__fqm = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {oawoc__fqm} = 0\n' + yiz__qanx, (oawoc__fqm,) + ppwdj__dtwk
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(ifqxq__wvku.dtype) for
            ifqxq__wvku in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(ifqxq__wvku) for ifqxq__wvku in t.data
            )
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(ifqxq__wvku) for ifqxq__wvku in t.
            types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    pspom__iftw = typing_context.resolve_getattr(obj_dtype, func_name)
    if pspom__iftw is None:
        wfu__nchl = types.misc.Module(np)
        try:
            pspom__iftw = typing_context.resolve_getattr(wfu__nchl, func_name)
        except AttributeError as gdchm__vov:
            pspom__iftw = None
        if pspom__iftw is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return pspom__iftw


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    pspom__iftw = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(pspom__iftw, types.BoundFunction):
        if axis is not None:
            ujuy__hmkh = pspom__iftw.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            ujuy__hmkh = pspom__iftw.get_call_type(typing_context, (), {})
        return ujuy__hmkh.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(pspom__iftw):
            ujuy__hmkh = pspom__iftw.get_call_type(typing_context, (
                obj_dtype,), {})
            return ujuy__hmkh.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    pspom__iftw = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(pspom__iftw, types.BoundFunction):
        jlp__rjjje = pspom__iftw.template
        if axis is not None:
            return jlp__rjjje._overload_func(obj_dtype, axis=axis)
        else:
            return jlp__rjjje._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    qqdgr__cdi = get_definition(func_ir, dict_var)
    require(isinstance(qqdgr__cdi, ir.Expr))
    require(qqdgr__cdi.op == 'build_map')
    mvr__xgry = qqdgr__cdi.items
    djtvw__iwwf = []
    values = []
    pqo__bjp = False
    for bedvd__xccm in range(len(mvr__xgry)):
        vdvm__das, value = mvr__xgry[bedvd__xccm]
        try:
            jmix__cut = get_const_value_inner(func_ir, vdvm__das, arg_types,
                typemap, updated_containers)
            djtvw__iwwf.append(jmix__cut)
            values.append(value)
        except GuardException as gdchm__vov:
            require_const_map[vdvm__das] = label
            pqo__bjp = True
    if pqo__bjp:
        raise GuardException
    return djtvw__iwwf, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        djtvw__iwwf = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as gdchm__vov:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in djtvw__iwwf):
        raise BodoError(err_msg, loc)
    return djtvw__iwwf


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    djtvw__iwwf = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    yrxq__iss = []
    ushi__bov = [bodo.transforms.typing_pass._create_const_var(fmd__lgf,
        'dict_key', scope, loc, yrxq__iss) for fmd__lgf in djtvw__iwwf]
    gkomy__mqmg = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        exej__foiym = ir.Var(scope, mk_unique_var('sentinel'), loc)
        hen__sgohu = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        yrxq__iss.append(ir.Assign(ir.Const('__bodo_tup', loc), exej__foiym,
            loc))
        vyddx__leif = [exej__foiym] + ushi__bov + gkomy__mqmg
        yrxq__iss.append(ir.Assign(ir.Expr.build_tuple(vyddx__leif, loc),
            hen__sgohu, loc))
        return (hen__sgohu,), yrxq__iss
    else:
        sysh__yxhkj = ir.Var(scope, mk_unique_var('values_tup'), loc)
        rvf__qfy = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        yrxq__iss.append(ir.Assign(ir.Expr.build_tuple(gkomy__mqmg, loc),
            sysh__yxhkj, loc))
        yrxq__iss.append(ir.Assign(ir.Expr.build_tuple(ushi__bov, loc),
            rvf__qfy, loc))
        return (sysh__yxhkj, rvf__qfy), yrxq__iss
