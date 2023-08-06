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
    twpby__kte = tuple(call_list)
    if twpby__kte in no_side_effect_call_tuples:
        return True
    if twpby__kte == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(twpby__kte) == 1 and tuple in getattr(twpby__kte[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        comos__kin = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        comos__kin = func.__globals__
    if extra_globals is not None:
        comos__kin.update(extra_globals)
    if add_default_globals:
        comos__kin.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, comos__kin, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[twnz__dwagr.name] for twnz__dwagr in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, comos__kin)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        uvxko__yqemo = tuple(typing_info.typemap[twnz__dwagr.name] for
            twnz__dwagr in args)
        ftyn__uqv = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, uvxko__yqemo, {}, {}, flags)
        ftyn__uqv.run()
    mzygc__ach = f_ir.blocks.popitem()[1]
    replace_arg_nodes(mzygc__ach, args)
    mutug__shu = mzygc__ach.body[:-2]
    update_locs(mutug__shu[len(args):], loc)
    for stmt in mutug__shu[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        uhq__yowty = mzygc__ach.body[-2]
        assert is_assign(uhq__yowty) and is_expr(uhq__yowty.value, 'cast')
        dxz__yzhwg = uhq__yowty.value.value
        mutug__shu.append(ir.Assign(dxz__yzhwg, ret_var, loc))
    return mutug__shu


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for yxmb__mkitu in stmt.list_vars():
            yxmb__mkitu.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        hrnnf__alw = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        rdp__vxqo, glwx__zjefj = hrnnf__alw(stmt)
        return glwx__zjefj
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        pgee__tvb = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(pgee__tvb, ir.UndefinedType):
            vgn__ubt = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{vgn__ubt}' is not defined", loc=loc)
    except GuardException as tzzd__vgyd:
        raise BodoError(err_msg, loc=loc)
    return pgee__tvb


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    pwt__oygy = get_definition(func_ir, var)
    evvy__kpwyu = None
    if typemap is not None:
        evvy__kpwyu = typemap.get(var.name, None)
    if isinstance(pwt__oygy, ir.Arg) and arg_types is not None:
        evvy__kpwyu = arg_types[pwt__oygy.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(evvy__kpwyu):
        return get_literal_value(evvy__kpwyu)
    if isinstance(pwt__oygy, (ir.Const, ir.Global, ir.FreeVar)):
        pgee__tvb = pwt__oygy.value
        return pgee__tvb
    if literalize_args and isinstance(pwt__oygy, ir.Arg
        ) and can_literalize_type(evvy__kpwyu, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({pwt__oygy.index}, loc=var.
            loc, file_infos={pwt__oygy.index: file_info} if file_info is not
            None else None)
    if is_expr(pwt__oygy, 'binop'):
        if file_info and pwt__oygy.fn == operator.add:
            try:
                efay__apt = get_const_value_inner(func_ir, pwt__oygy.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(efay__apt, True)
                wosdw__yjwqk = get_const_value_inner(func_ir, pwt__oygy.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return pwt__oygy.fn(efay__apt, wosdw__yjwqk)
            except (GuardException, BodoConstUpdatedError) as tzzd__vgyd:
                pass
            try:
                wosdw__yjwqk = get_const_value_inner(func_ir, pwt__oygy.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(wosdw__yjwqk, False)
                efay__apt = get_const_value_inner(func_ir, pwt__oygy.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return pwt__oygy.fn(efay__apt, wosdw__yjwqk)
            except (GuardException, BodoConstUpdatedError) as tzzd__vgyd:
                pass
        efay__apt = get_const_value_inner(func_ir, pwt__oygy.lhs, arg_types,
            typemap, updated_containers)
        wosdw__yjwqk = get_const_value_inner(func_ir, pwt__oygy.rhs,
            arg_types, typemap, updated_containers)
        return pwt__oygy.fn(efay__apt, wosdw__yjwqk)
    if is_expr(pwt__oygy, 'unary'):
        pgee__tvb = get_const_value_inner(func_ir, pwt__oygy.value,
            arg_types, typemap, updated_containers)
        return pwt__oygy.fn(pgee__tvb)
    if is_expr(pwt__oygy, 'getattr') and typemap:
        rfrim__pofn = typemap.get(pwt__oygy.value.name, None)
        if isinstance(rfrim__pofn, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and pwt__oygy.attr == 'columns':
            return pd.Index(rfrim__pofn.columns)
        if isinstance(rfrim__pofn, types.SliceType):
            tjct__paxy = get_definition(func_ir, pwt__oygy.value)
            require(is_call(tjct__paxy))
            khmj__eotf = find_callname(func_ir, tjct__paxy)
            prt__leq = False
            if khmj__eotf == ('_normalize_slice', 'numba.cpython.unicode'):
                require(pwt__oygy.attr in ('start', 'step'))
                tjct__paxy = get_definition(func_ir, tjct__paxy.args[0])
                prt__leq = True
            require(find_callname(func_ir, tjct__paxy) == ('slice', 'builtins')
                )
            if len(tjct__paxy.args) == 1:
                if pwt__oygy.attr == 'start':
                    return 0
                if pwt__oygy.attr == 'step':
                    return 1
                require(pwt__oygy.attr == 'stop')
                return get_const_value_inner(func_ir, tjct__paxy.args[0],
                    arg_types, typemap, updated_containers)
            if pwt__oygy.attr == 'start':
                pgee__tvb = get_const_value_inner(func_ir, tjct__paxy.args[
                    0], arg_types, typemap, updated_containers)
                if pgee__tvb is None:
                    pgee__tvb = 0
                if prt__leq:
                    require(pgee__tvb == 0)
                return pgee__tvb
            if pwt__oygy.attr == 'stop':
                assert not prt__leq
                return get_const_value_inner(func_ir, tjct__paxy.args[1],
                    arg_types, typemap, updated_containers)
            require(pwt__oygy.attr == 'step')
            if len(tjct__paxy.args) == 2:
                return 1
            else:
                pgee__tvb = get_const_value_inner(func_ir, tjct__paxy.args[
                    2], arg_types, typemap, updated_containers)
                if pgee__tvb is None:
                    pgee__tvb = 1
                if prt__leq:
                    require(pgee__tvb == 1)
                return pgee__tvb
    if is_expr(pwt__oygy, 'getattr'):
        return getattr(get_const_value_inner(func_ir, pwt__oygy.value,
            arg_types, typemap, updated_containers), pwt__oygy.attr)
    if is_expr(pwt__oygy, 'getitem'):
        value = get_const_value_inner(func_ir, pwt__oygy.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, pwt__oygy.index, arg_types,
            typemap, updated_containers)
        return value[index]
    xldo__gurd = guard(find_callname, func_ir, pwt__oygy, typemap)
    if xldo__gurd is not None and len(xldo__gurd) == 2 and xldo__gurd[0
        ] == 'keys' and isinstance(xldo__gurd[1], ir.Var):
        qekk__mlt = pwt__oygy.func
        pwt__oygy = get_definition(func_ir, xldo__gurd[1])
        qagdu__lgp = xldo__gurd[1].name
        if updated_containers and qagdu__lgp in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                qagdu__lgp, updated_containers[qagdu__lgp]))
        require(is_expr(pwt__oygy, 'build_map'))
        vals = [yxmb__mkitu[0] for yxmb__mkitu in pwt__oygy.items]
        ucrbd__kzgt = guard(get_definition, func_ir, qekk__mlt)
        assert isinstance(ucrbd__kzgt, ir.Expr) and ucrbd__kzgt.attr == 'keys'
        ucrbd__kzgt.attr = 'copy'
        return [get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in vals]
    if is_expr(pwt__oygy, 'build_map'):
        return {get_const_value_inner(func_ir, yxmb__mkitu[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            yxmb__mkitu[1], arg_types, typemap, updated_containers) for
            yxmb__mkitu in pwt__oygy.items}
    if is_expr(pwt__oygy, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in pwt__oygy.items)
    if is_expr(pwt__oygy, 'build_list'):
        return [get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in pwt__oygy.items]
    if is_expr(pwt__oygy, 'build_set'):
        return {get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in pwt__oygy.items}
    if xldo__gurd == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if xldo__gurd == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('range', 'builtins') and len(pwt__oygy.args) == 1:
        return range(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, yxmb__mkitu,
            arg_types, typemap, updated_containers) for yxmb__mkitu in
            pwt__oygy.args))
    if xldo__gurd == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('format', 'builtins'):
        twnz__dwagr = get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers)
        rinlj__dbj = get_const_value_inner(func_ir, pwt__oygy.args[1],
            arg_types, typemap, updated_containers) if len(pwt__oygy.args
            ) > 1 else ''
        return format(twnz__dwagr, rinlj__dbj)
    if xldo__gurd in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, pwt__oygy.args[
            0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, pwt__oygy.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            pwt__oygy.args[2], arg_types, typemap, updated_containers))
    if xldo__gurd == ('len', 'builtins') and typemap and isinstance(typemap
        .get(pwt__oygy.args[0].name, None), types.BaseTuple):
        return len(typemap[pwt__oygy.args[0].name])
    if xldo__gurd == ('len', 'builtins'):
        gxil__omboz = guard(get_definition, func_ir, pwt__oygy.args[0])
        if isinstance(gxil__omboz, ir.Expr) and gxil__omboz.op in (
            'build_tuple', 'build_list', 'build_set', 'build_map'):
            return len(gxil__omboz.items)
        return len(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd == ('CategoricalDtype', 'pandas'):
        kws = dict(pwt__oygy.kws)
        pmgr__yorc = get_call_expr_arg('CategoricalDtype', pwt__oygy.args,
            kws, 0, 'categories', '')
        ree__iun = get_call_expr_arg('CategoricalDtype', pwt__oygy.args,
            kws, 1, 'ordered', False)
        if ree__iun is not False:
            ree__iun = get_const_value_inner(func_ir, ree__iun, arg_types,
                typemap, updated_containers)
        if pmgr__yorc == '':
            pmgr__yorc = None
        else:
            pmgr__yorc = get_const_value_inner(func_ir, pmgr__yorc,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(pmgr__yorc, ree__iun)
    if xldo__gurd == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, pwt__oygy.args[0],
            arg_types, typemap, updated_containers))
    if xldo__gurd is not None and len(xldo__gurd) == 2 and xldo__gurd[1
        ] == 'pandas' and xldo__gurd[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, xldo__gurd[0])()
    if xldo__gurd is not None and len(xldo__gurd) == 2 and isinstance(
        xldo__gurd[1], ir.Var):
        pgee__tvb = get_const_value_inner(func_ir, xldo__gurd[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in pwt__oygy.args]
        kws = {pjva__njdgt[0]: get_const_value_inner(func_ir, pjva__njdgt[1
            ], arg_types, typemap, updated_containers) for pjva__njdgt in
            pwt__oygy.kws}
        return getattr(pgee__tvb, xldo__gurd[0])(*args, **kws)
    if xldo__gurd is not None and len(xldo__gurd) == 2 and xldo__gurd[1
        ] == 'bodo' and xldo__gurd[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in pwt__oygy.args)
        kwargs = {vgn__ubt: get_const_value_inner(func_ir, yxmb__mkitu,
            arg_types, typemap, updated_containers) for vgn__ubt,
            yxmb__mkitu in dict(pwt__oygy.kws).items()}
        return getattr(bodo, xldo__gurd[0])(*args, **kwargs)
    if is_call(pwt__oygy) and typemap and isinstance(typemap.get(pwt__oygy.
        func.name, None), types.Dispatcher):
        py_func = typemap[pwt__oygy.func.name].dispatcher.py_func
        require(pwt__oygy.vararg is None)
        args = tuple(get_const_value_inner(func_ir, yxmb__mkitu, arg_types,
            typemap, updated_containers) for yxmb__mkitu in pwt__oygy.args)
        kwargs = {vgn__ubt: get_const_value_inner(func_ir, yxmb__mkitu,
            arg_types, typemap, updated_containers) for vgn__ubt,
            yxmb__mkitu in dict(pwt__oygy.kws).items()}
        arg_types = tuple(bodo.typeof(yxmb__mkitu) for yxmb__mkitu in args)
        kw_types = {mcf__giqm: bodo.typeof(yxmb__mkitu) for mcf__giqm,
            yxmb__mkitu in kwargs.items()}
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
    f_ir, typemap, trqi__suexi, trqi__suexi = bodo.compiler.get_func_type_info(
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
                    yfacn__lkzza = guard(get_definition, f_ir, rhs.func)
                    if isinstance(yfacn__lkzza, ir.Const) and isinstance(
                        yfacn__lkzza.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    dsqu__nqqxq = guard(find_callname, f_ir, rhs)
                    if dsqu__nqqxq is None:
                        return False
                    func_name, dhac__jyfh = dsqu__nqqxq
                    if dhac__jyfh == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if dsqu__nqqxq in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if dsqu__nqqxq == ('File', 'h5py'):
                        return False
                    if isinstance(dhac__jyfh, ir.Var):
                        evvy__kpwyu = typemap[dhac__jyfh.name]
                        if isinstance(evvy__kpwyu, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(evvy__kpwyu, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(evvy__kpwyu, bodo.LoggingLoggerType):
                            return False
                        if str(evvy__kpwyu).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            dhac__jyfh), ir.Arg)):
                            return False
                    if dhac__jyfh in ('numpy.random', 'time', 'logging',
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
        mlzp__yyb = func.literal_value.code
        tpam__ikw = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            tpam__ikw = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(tpam__ikw, mlzp__yyb)
        fix_struct_return(f_ir)
        typemap, cgs__vtfjn, leb__glte, trqi__suexi = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, leb__glte, cgs__vtfjn = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, leb__glte, cgs__vtfjn = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, leb__glte, cgs__vtfjn = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(cgs__vtfjn, types.DictType):
        qvkr__vzkeo = guard(get_struct_keynames, f_ir, typemap)
        if qvkr__vzkeo is not None:
            cgs__vtfjn = StructType((cgs__vtfjn.value_type,) * len(
                qvkr__vzkeo), qvkr__vzkeo)
    if is_udf and isinstance(cgs__vtfjn, (SeriesType, HeterogeneousSeriesType)
        ):
        ndi__zsi = numba.core.registry.cpu_target.typing_context
        ewnm__xyijc = numba.core.registry.cpu_target.target_context
        yyjye__ncnx = bodo.transforms.series_pass.SeriesPass(f_ir, ndi__zsi,
            ewnm__xyijc, typemap, leb__glte, {})
        yyjye__ncnx.run()
        yyjye__ncnx.run()
        yyjye__ncnx.run()
        pwf__iti = compute_cfg_from_blocks(f_ir.blocks)
        jgzra__jsukj = [guard(_get_const_series_info, f_ir.blocks[hue__ehuh
            ], f_ir, typemap) for hue__ehuh in pwf__iti.exit_points() if
            isinstance(f_ir.blocks[hue__ehuh].body[-1], ir.Return)]
        if None in jgzra__jsukj or len(pd.Series(jgzra__jsukj).unique()) != 1:
            cgs__vtfjn.const_info = None
        else:
            cgs__vtfjn.const_info = jgzra__jsukj[0]
    return cgs__vtfjn


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    bvf__snk = block.body[-1].value
    fvfal__hvfxn = get_definition(f_ir, bvf__snk)
    require(is_expr(fvfal__hvfxn, 'cast'))
    fvfal__hvfxn = get_definition(f_ir, fvfal__hvfxn.value)
    require(is_call(fvfal__hvfxn) and find_callname(f_ir, fvfal__hvfxn) ==
        ('init_series', 'bodo.hiframes.pd_series_ext'))
    yfn__zgj = fvfal__hvfxn.args[1]
    oebqs__zuy = tuple(get_const_value_inner(f_ir, yfn__zgj, typemap=typemap))
    if isinstance(typemap[bvf__snk.name], HeterogeneousSeriesType):
        return len(typemap[bvf__snk.name].data), oebqs__zuy
    uic__fddv = fvfal__hvfxn.args[0]
    hqhz__kuvhs = get_definition(f_ir, uic__fddv)
    func_name, vrlt__xtwxj = find_callname(f_ir, hqhz__kuvhs)
    if is_call(hqhz__kuvhs) and bodo.utils.utils.is_alloc_callname(func_name,
        vrlt__xtwxj):
        imf__nxx = hqhz__kuvhs.args[0]
        jtd__hup = get_const_value_inner(f_ir, imf__nxx, typemap=typemap)
        return jtd__hup, oebqs__zuy
    if is_call(hqhz__kuvhs) and find_callname(f_ir, hqhz__kuvhs) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        uic__fddv = hqhz__kuvhs.args[0]
        hqhz__kuvhs = get_definition(f_ir, uic__fddv)
    require(is_expr(hqhz__kuvhs, 'build_tuple') or is_expr(hqhz__kuvhs,
        'build_list'))
    return len(hqhz__kuvhs.items), oebqs__zuy


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    trbuq__ymd = []
    tnml__vgglq = []
    values = []
    for mcf__giqm, yxmb__mkitu in build_map.items:
        ulr__sjz = find_const(f_ir, mcf__giqm)
        require(isinstance(ulr__sjz, str))
        tnml__vgglq.append(ulr__sjz)
        trbuq__ymd.append(mcf__giqm)
        values.append(yxmb__mkitu)
    ljmff__pkop = ir.Var(scope, mk_unique_var('val_tup'), loc)
    hrgol__dwf = ir.Assign(ir.Expr.build_tuple(values, loc), ljmff__pkop, loc)
    f_ir._definitions[ljmff__pkop.name] = [hrgol__dwf.value]
    kyhs__xjm = ir.Var(scope, mk_unique_var('key_tup'), loc)
    abpl__dkp = ir.Assign(ir.Expr.build_tuple(trbuq__ymd, loc), kyhs__xjm, loc)
    f_ir._definitions[kyhs__xjm.name] = [abpl__dkp.value]
    if typemap is not None:
        typemap[ljmff__pkop.name] = types.Tuple([typemap[yxmb__mkitu.name] for
            yxmb__mkitu in values])
        typemap[kyhs__xjm.name] = types.Tuple([typemap[yxmb__mkitu.name] for
            yxmb__mkitu in trbuq__ymd])
    return tnml__vgglq, ljmff__pkop, hrgol__dwf, kyhs__xjm, abpl__dkp


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    ksm__mpx = block.body[-1].value
    nggrw__kday = guard(get_definition, f_ir, ksm__mpx)
    require(is_expr(nggrw__kday, 'cast'))
    fvfal__hvfxn = guard(get_definition, f_ir, nggrw__kday.value)
    require(is_expr(fvfal__hvfxn, 'build_map'))
    require(len(fvfal__hvfxn.items) > 0)
    loc = block.loc
    scope = block.scope
    tnml__vgglq, ljmff__pkop, hrgol__dwf, kyhs__xjm, abpl__dkp = (
        extract_keyvals_from_struct_map(f_ir, fvfal__hvfxn, loc, scope))
    scknn__qytna = ir.Var(scope, mk_unique_var('conv_call'), loc)
    elnpr__mhvkh = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), scknn__qytna, loc)
    f_ir._definitions[scknn__qytna.name] = [elnpr__mhvkh.value]
    ouo__wdwgj = ir.Var(scope, mk_unique_var('struct_val'), loc)
    hdrnu__rgqzc = ir.Assign(ir.Expr.call(scknn__qytna, [ljmff__pkop,
        kyhs__xjm], {}, loc), ouo__wdwgj, loc)
    f_ir._definitions[ouo__wdwgj.name] = [hdrnu__rgqzc.value]
    nggrw__kday.value = ouo__wdwgj
    fvfal__hvfxn.items = [(mcf__giqm, mcf__giqm) for mcf__giqm, trqi__suexi in
        fvfal__hvfxn.items]
    block.body = block.body[:-2] + [hrgol__dwf, abpl__dkp, elnpr__mhvkh,
        hdrnu__rgqzc] + block.body[-2:]
    return tuple(tnml__vgglq)


def get_struct_keynames(f_ir, typemap):
    pwf__iti = compute_cfg_from_blocks(f_ir.blocks)
    kty__cxx = list(pwf__iti.exit_points())[0]
    block = f_ir.blocks[kty__cxx]
    require(isinstance(block.body[-1], ir.Return))
    ksm__mpx = block.body[-1].value
    nggrw__kday = guard(get_definition, f_ir, ksm__mpx)
    require(is_expr(nggrw__kday, 'cast'))
    fvfal__hvfxn = guard(get_definition, f_ir, nggrw__kday.value)
    require(is_call(fvfal__hvfxn) and find_callname(f_ir, fvfal__hvfxn) ==
        ('struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[fvfal__hvfxn.args[1].name])


def fix_struct_return(f_ir):
    vtvc__nffoo = None
    pwf__iti = compute_cfg_from_blocks(f_ir.blocks)
    for kty__cxx in pwf__iti.exit_points():
        vtvc__nffoo = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            kty__cxx], kty__cxx)
    return vtvc__nffoo


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    zwt__tni = ir.Block(ir.Scope(None, loc), loc)
    zwt__tni.body = node_list
    build_definitions({(0): zwt__tni}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(yxmb__mkitu) for yxmb__mkitu in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    rppi__tfak = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(rppi__tfak, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for gnhn__yrm in range(len(vals) - 1, -1, -1):
        yxmb__mkitu = vals[gnhn__yrm]
        if isinstance(yxmb__mkitu, str) and yxmb__mkitu.startswith(
            NESTED_TUP_SENTINEL):
            slf__bxsm = int(yxmb__mkitu[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:gnhn__yrm]) + (
                tuple(vals[gnhn__yrm + 1:gnhn__yrm + slf__bxsm + 1]),) +
                tuple(vals[gnhn__yrm + slf__bxsm + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    twnz__dwagr = None
    if len(args) > arg_no and arg_no >= 0:
        twnz__dwagr = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        twnz__dwagr = kws[arg_name]
    if twnz__dwagr is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return twnz__dwagr


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
    comos__kin = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        comos__kin.update(extra_globals)
    func.__globals__.update(comos__kin)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            jzgzl__ehkeh = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[jzgzl__ehkeh.name] = types.literal(default)
            except:
                pass_info.typemap[jzgzl__ehkeh.name] = numba.typeof(default)
            iwh__nxee = ir.Assign(ir.Const(default, loc), jzgzl__ehkeh, loc)
            pre_nodes.append(iwh__nxee)
            return jzgzl__ehkeh
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    uvxko__yqemo = tuple(pass_info.typemap[yxmb__mkitu.name] for
        yxmb__mkitu in args)
    if const:
        axko__oco = []
        for gnhn__yrm, twnz__dwagr in enumerate(args):
            pgee__tvb = guard(find_const, pass_info.func_ir, twnz__dwagr)
            if pgee__tvb:
                axko__oco.append(types.literal(pgee__tvb))
            else:
                axko__oco.append(uvxko__yqemo[gnhn__yrm])
        uvxko__yqemo = tuple(axko__oco)
    return ReplaceFunc(func, uvxko__yqemo, args, comos__kin,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(srj__zvezt) for srj__zvezt in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        vfmy__fbgsh = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {vfmy__fbgsh} = 0\n', (vfmy__fbgsh,)
    if isinstance(t, ArrayItemArrayType):
        mtqr__bxl, rqs__ikr = gen_init_varsize_alloc_sizes(t.dtype)
        vfmy__fbgsh = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {vfmy__fbgsh} = 0\n' + mtqr__bxl, (vfmy__fbgsh,) + rqs__ikr
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
        return 1 + sum(get_type_alloc_counts(srj__zvezt.dtype) for
            srj__zvezt in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(srj__zvezt) for srj__zvezt in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(srj__zvezt) for srj__zvezt in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    qet__cfsj = typing_context.resolve_getattr(obj_dtype, func_name)
    if qet__cfsj is None:
        webt__jlfz = types.misc.Module(np)
        try:
            qet__cfsj = typing_context.resolve_getattr(webt__jlfz, func_name)
        except AttributeError as tzzd__vgyd:
            qet__cfsj = None
        if qet__cfsj is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return qet__cfsj


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    qet__cfsj = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(qet__cfsj, types.BoundFunction):
        if axis is not None:
            mxjx__phm = qet__cfsj.get_call_type(typing_context, (), {'axis':
                axis})
        else:
            mxjx__phm = qet__cfsj.get_call_type(typing_context, (), {})
        return mxjx__phm.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(qet__cfsj):
            mxjx__phm = qet__cfsj.get_call_type(typing_context, (obj_dtype,
                ), {})
            return mxjx__phm.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    qet__cfsj = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(qet__cfsj, types.BoundFunction):
        vuz__hpf = qet__cfsj.template
        if axis is not None:
            return vuz__hpf._overload_func(obj_dtype, axis=axis)
        else:
            return vuz__hpf._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    qdwz__quoly = get_definition(func_ir, dict_var)
    require(isinstance(qdwz__quoly, ir.Expr))
    require(qdwz__quoly.op == 'build_map')
    hzpqv__mhy = qdwz__quoly.items
    trbuq__ymd = []
    values = []
    bpxb__zvnvj = False
    for gnhn__yrm in range(len(hzpqv__mhy)):
        eiks__bitwy, value = hzpqv__mhy[gnhn__yrm]
        try:
            eicu__grp = get_const_value_inner(func_ir, eiks__bitwy,
                arg_types, typemap, updated_containers)
            trbuq__ymd.append(eicu__grp)
            values.append(value)
        except GuardException as tzzd__vgyd:
            require_const_map[eiks__bitwy] = label
            bpxb__zvnvj = True
    if bpxb__zvnvj:
        raise GuardException
    return trbuq__ymd, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        trbuq__ymd = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as tzzd__vgyd:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in trbuq__ymd):
        raise BodoError(err_msg, loc)
    return trbuq__ymd


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    trbuq__ymd = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    kwau__ncvj = []
    nade__toe = [bodo.transforms.typing_pass._create_const_var(mcf__giqm,
        'dict_key', scope, loc, kwau__ncvj) for mcf__giqm in trbuq__ymd]
    bpfik__ggjil = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        yaq__fyckl = ir.Var(scope, mk_unique_var('sentinel'), loc)
        yltd__nfz = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        kwau__ncvj.append(ir.Assign(ir.Const('__bodo_tup', loc), yaq__fyckl,
            loc))
        awx__dcm = [yaq__fyckl] + nade__toe + bpfik__ggjil
        kwau__ncvj.append(ir.Assign(ir.Expr.build_tuple(awx__dcm, loc),
            yltd__nfz, loc))
        return (yltd__nfz,), kwau__ncvj
    else:
        fui__xch = ir.Var(scope, mk_unique_var('values_tup'), loc)
        dlt__hvw = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        kwau__ncvj.append(ir.Assign(ir.Expr.build_tuple(bpfik__ggjil, loc),
            fui__xch, loc))
        kwau__ncvj.append(ir.Assign(ir.Expr.build_tuple(nade__toe, loc),
            dlt__hvw, loc))
        return (fui__xch, dlt__hvw), kwau__ncvj
