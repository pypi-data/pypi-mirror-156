import atexit
import datetime
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload, register_jitable
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, decode_if_dict_array, is_overload_false, is_overload_none, is_str_arr_type
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, is_array_typ, numba_to_c_type
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    rmcj__win = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, rmcj__win, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    rmcj__win = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, rmcj__win, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            rmcj__win = get_type_enum(arr)
            return _isend(arr.ctypes, size, rmcj__win, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        rmcj__win = np.int32(numba_to_c_type(arr.dtype))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            mdgn__larhr = size + 7 >> 3
            avaa__htpwv = _isend(arr._data.ctypes, size, rmcj__win, pe, tag,
                cond)
            oqi__jvmgw = _isend(arr._null_bitmap.ctypes, mdgn__larhr,
                els__quvpi, pe, tag, cond)
            return avaa__htpwv, oqi__jvmgw
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        okm__gwfm = np.int32(numba_to_c_type(offset_type))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            jgjwx__bvw = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(jgjwx__bvw, pe, tag - 1)
            mdgn__larhr = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                okm__gwfm, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), jgjwx__bvw,
                els__quvpi, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                mdgn__larhr, els__quvpi, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            rmcj__win = get_type_enum(arr)
            return _irecv(arr.ctypes, size, rmcj__win, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        rmcj__win = np.int32(numba_to_c_type(arr.dtype))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            mdgn__larhr = size + 7 >> 3
            avaa__htpwv = _irecv(arr._data.ctypes, size, rmcj__win, pe, tag,
                cond)
            oqi__jvmgw = _irecv(arr._null_bitmap.ctypes, mdgn__larhr,
                els__quvpi, pe, tag, cond)
            return avaa__htpwv, oqi__jvmgw
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        okm__gwfm = np.int32(numba_to_c_type(offset_type))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            blo__wzq = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            blo__wzq = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        nxvny__qklzg = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {blo__wzq}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        obckh__tepm = dict()
        exec(nxvny__qklzg, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            okm__gwfm, 'char_typ_enum': els__quvpi}, obckh__tepm)
        impl = obckh__tepm['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    rmcj__win = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), rmcj__win)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        pvyxa__wyz = n_pes if rank == root or allgather else 0
        ctukt__rby = np.empty(pvyxa__wyz, dtype)
        c_gather_scalar(send.ctypes, ctukt__rby.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return ctukt__rby
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        ofkjx__ifqmw = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], ofkjx__ifqmw)
        return builder.bitcast(ofkjx__ifqmw, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        ofkjx__ifqmw = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(ofkjx__ifqmw)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    pofkg__oxnfo = types.unliteral(value)
    if isinstance(pofkg__oxnfo, IndexValueType):
        pofkg__oxnfo = pofkg__oxnfo.val_typ
        ifykc__ghqx = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            ifykc__ghqx.append(types.int64)
            ifykc__ghqx.append(bodo.datetime64ns)
            ifykc__ghqx.append(bodo.timedelta64ns)
            ifykc__ghqx.append(bodo.datetime_date_type)
        if pofkg__oxnfo not in ifykc__ghqx:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(pofkg__oxnfo))
    typ_enum = np.int32(numba_to_c_type(pofkg__oxnfo))

    def impl(value, reduce_op):
        bvcyp__tkl = value_to_ptr(value)
        wsrjz__brk = value_to_ptr(value)
        _dist_reduce(bvcyp__tkl, wsrjz__brk, reduce_op, typ_enum)
        return load_val_ptr(wsrjz__brk, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    pofkg__oxnfo = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(pofkg__oxnfo))
    xyq__dvndf = pofkg__oxnfo(0)

    def impl(value, reduce_op):
        bvcyp__tkl = value_to_ptr(value)
        wsrjz__brk = value_to_ptr(xyq__dvndf)
        _dist_exscan(bvcyp__tkl, wsrjz__brk, reduce_op, typ_enum)
        return load_val_ptr(wsrjz__brk, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    gteo__rnb = 0
    rgb__xeprr = 0
    for i in range(len(recv_counts)):
        qqoi__quqb = recv_counts[i]
        mdgn__larhr = recv_counts_nulls[i]
        rarzf__dfojr = tmp_null_bytes[gteo__rnb:gteo__rnb + mdgn__larhr]
        for ohjhz__oem in range(qqoi__quqb):
            set_bit_to(null_bitmap_ptr, rgb__xeprr, get_bit(rarzf__dfojr,
                ohjhz__oem))
            rgb__xeprr += 1
        gteo__rnb += mdgn__larhr


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            wykh__dci = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                wykh__dci, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            udfav__jnmy = data.size
            recv_counts = gather_scalar(np.int32(udfav__jnmy), allgather,
                root=root)
            hmnc__hja = recv_counts.sum()
            iyv__soxyf = empty_like_type(hmnc__hja, data)
            zubcv__nzn = np.empty(1, np.int32)
            if rank == root or allgather:
                zubcv__nzn = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(udfav__jnmy), iyv__soxyf.ctypes,
                recv_counts.ctypes, zubcv__nzn.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return iyv__soxyf.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            iyv__soxyf = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(iyv__soxyf)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            iyv__soxyf = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(iyv__soxyf)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            udfav__jnmy = len(data)
            mdgn__larhr = udfav__jnmy + 7 >> 3
            recv_counts = gather_scalar(np.int32(udfav__jnmy), allgather,
                root=root)
            hmnc__hja = recv_counts.sum()
            iyv__soxyf = empty_like_type(hmnc__hja, data)
            zubcv__nzn = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            jowc__urwuy = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                zubcv__nzn = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                jowc__urwuy = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(udfav__jnmy),
                iyv__soxyf._days_data.ctypes, recv_counts.ctypes,
                zubcv__nzn.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(udfav__jnmy),
                iyv__soxyf._seconds_data.ctypes, recv_counts.ctypes,
                zubcv__nzn.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(udfav__jnmy),
                iyv__soxyf._microseconds_data.ctypes, recv_counts.ctypes,
                zubcv__nzn.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(mdgn__larhr),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                jowc__urwuy.ctypes, els__quvpi, allgather, np.int32(root))
            copy_gathered_null_bytes(iyv__soxyf._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return iyv__soxyf
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            udfav__jnmy = len(data)
            mdgn__larhr = udfav__jnmy + 7 >> 3
            recv_counts = gather_scalar(np.int32(udfav__jnmy), allgather,
                root=root)
            hmnc__hja = recv_counts.sum()
            iyv__soxyf = empty_like_type(hmnc__hja, data)
            zubcv__nzn = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            jowc__urwuy = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                zubcv__nzn = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                jowc__urwuy = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(udfav__jnmy), iyv__soxyf.
                _data.ctypes, recv_counts.ctypes, zubcv__nzn.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(mdgn__larhr),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                jowc__urwuy.ctypes, els__quvpi, allgather, np.int32(root))
            copy_gathered_null_bytes(iyv__soxyf._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return iyv__soxyf
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        sqt__xys = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            pymr__whnq = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                pymr__whnq, sqt__xys)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            kge__pppt = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            rtg__ytnuf = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(kge__pppt,
                rtg__ytnuf)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ddf__bxazt = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            rqf__oph = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rqf__oph, ddf__bxazt)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        rqbn__cwpwr = np.iinfo(np.int64).max
        njbj__xln = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ovgc__vqszb = data._start
            yarz__iob = data._stop
            if len(data) == 0:
                ovgc__vqszb = rqbn__cwpwr
                yarz__iob = njbj__xln
            ovgc__vqszb = bodo.libs.distributed_api.dist_reduce(ovgc__vqszb,
                np.int32(Reduce_Type.Min.value))
            yarz__iob = bodo.libs.distributed_api.dist_reduce(yarz__iob, np
                .int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if ovgc__vqszb == rqbn__cwpwr and yarz__iob == njbj__xln:
                ovgc__vqszb = 0
                yarz__iob = 0
            haqmb__bta = max(0, -(-(yarz__iob - ovgc__vqszb) // data._step))
            if haqmb__bta < total_len:
                yarz__iob = ovgc__vqszb + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                ovgc__vqszb = 0
                yarz__iob = 0
            return bodo.hiframes.pd_index_ext.init_range_index(ovgc__vqszb,
                yarz__iob, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            whwpw__hlj = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, whwpw__hlj)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            iyv__soxyf = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(iyv__soxyf
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        idsx__smx = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        nxvny__qklzg = f"""def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        nxvny__qklzg += '  T = data\n'
        nxvny__qklzg += '  T2 = init_table(T, True)\n'
        for luz__nbrck in data.type_to_blk.values():
            idsx__smx[f'arr_inds_{luz__nbrck}'] = np.array(data.
                block_to_arr_ind[luz__nbrck], dtype=np.int64)
            nxvny__qklzg += (
                f'  arr_list_{luz__nbrck} = get_table_block(T, {luz__nbrck})\n'
                )
            nxvny__qklzg += f"""  out_arr_list_{luz__nbrck} = alloc_list_like(arr_list_{luz__nbrck}, len(arr_list_{luz__nbrck}), True)
"""
            nxvny__qklzg += f'  for i in range(len(arr_list_{luz__nbrck})):\n'
            nxvny__qklzg += (
                f'    arr_ind_{luz__nbrck} = arr_inds_{luz__nbrck}[i]\n')
            nxvny__qklzg += f"""    ensure_column_unboxed(T, arr_list_{luz__nbrck}, i, arr_ind_{luz__nbrck})
"""
            nxvny__qklzg += f"""    out_arr_{luz__nbrck} = bodo.gatherv(arr_list_{luz__nbrck}[i], allgather, warn_if_rep, root)
"""
            nxvny__qklzg += (
                f'    out_arr_list_{luz__nbrck}[i] = out_arr_{luz__nbrck}\n')
            nxvny__qklzg += (
                f'  T2 = set_table_block(T2, out_arr_list_{luz__nbrck}, {luz__nbrck})\n'
                )
        nxvny__qklzg += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        nxvny__qklzg += f'  T2 = set_table_len(T2, length)\n'
        nxvny__qklzg += f'  return T2\n'
        obckh__tepm = {}
        exec(nxvny__qklzg, idsx__smx, obckh__tepm)
        hsuu__qsops = obckh__tepm['impl_table']
        return hsuu__qsops
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        egm__tsueq = len(data.columns)
        if egm__tsueq == 0:
            yxlzy__bvlcn = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                boni__fahgy = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    boni__fahgy, yxlzy__bvlcn)
            return impl
        ynazx__yzx = ', '.join(f'g_data_{i}' for i in range(egm__tsueq))
        nxvny__qklzg = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            abc__bui = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            ynazx__yzx = 'T2'
            nxvny__qklzg += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            nxvny__qklzg += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(egm__tsueq):
                nxvny__qklzg += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                nxvny__qklzg += (
                    """  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)
"""
                    .format(i, i))
        nxvny__qklzg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        nxvny__qklzg += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        nxvny__qklzg += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(ynazx__yzx))
        obckh__tepm = {}
        idsx__smx = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(nxvny__qklzg, idsx__smx, obckh__tepm)
        wnhjs__djilx = obckh__tepm['impl_df']
        return wnhjs__djilx
    if isinstance(data, ArrayItemArrayType):
        vhyrp__xrlj = np.int32(numba_to_c_type(types.int32))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            rpo__tgyvc = bodo.libs.array_item_arr_ext.get_offsets(data)
            wes__imc = bodo.libs.array_item_arr_ext.get_data(data)
            wes__imc = wes__imc[:rpo__tgyvc[-1]]
            udmr__msq = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            udfav__jnmy = len(data)
            qcmn__rrm = np.empty(udfav__jnmy, np.uint32)
            mdgn__larhr = udfav__jnmy + 7 >> 3
            for i in range(udfav__jnmy):
                qcmn__rrm[i] = rpo__tgyvc[i + 1] - rpo__tgyvc[i]
            recv_counts = gather_scalar(np.int32(udfav__jnmy), allgather,
                root=root)
            hmnc__hja = recv_counts.sum()
            zubcv__nzn = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            jowc__urwuy = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                zubcv__nzn = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for uee__zvj in range(len(recv_counts)):
                    recv_counts_nulls[uee__zvj] = recv_counts[uee__zvj
                        ] + 7 >> 3
                jowc__urwuy = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            ysbqt__vekq = np.empty(hmnc__hja + 1, np.uint32)
            qjbkm__ypydb = bodo.gatherv(wes__imc, allgather, warn_if_rep, root)
            xsneb__exp = np.empty(hmnc__hja + 7 >> 3, np.uint8)
            c_gatherv(qcmn__rrm.ctypes, np.int32(udfav__jnmy), ysbqt__vekq.
                ctypes, recv_counts.ctypes, zubcv__nzn.ctypes, vhyrp__xrlj,
                allgather, np.int32(root))
            c_gatherv(udmr__msq.ctypes, np.int32(mdgn__larhr),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                jowc__urwuy.ctypes, els__quvpi, allgather, np.int32(root))
            dummy_use(data)
            yiklo__gmq = np.empty(hmnc__hja + 1, np.uint64)
            convert_len_arr_to_offset(ysbqt__vekq.ctypes, yiklo__gmq.ctypes,
                hmnc__hja)
            copy_gathered_null_bytes(xsneb__exp.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                hmnc__hja, qjbkm__ypydb, yiklo__gmq, xsneb__exp)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        lyu__riik = data.names
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            nwwf__stz = bodo.libs.struct_arr_ext.get_data(data)
            dlp__pdnb = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            ljg__yxvc = bodo.gatherv(nwwf__stz, allgather=allgather, root=root)
            rank = bodo.libs.distributed_api.get_rank()
            udfav__jnmy = len(data)
            mdgn__larhr = udfav__jnmy + 7 >> 3
            recv_counts = gather_scalar(np.int32(udfav__jnmy), allgather,
                root=root)
            hmnc__hja = recv_counts.sum()
            vhn__exfa = np.empty(hmnc__hja + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            jowc__urwuy = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                jowc__urwuy = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(dlp__pdnb.ctypes, np.int32(mdgn__larhr),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                jowc__urwuy.ctypes, els__quvpi, allgather, np.int32(root))
            copy_gathered_null_bytes(vhn__exfa.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(ljg__yxvc,
                vhn__exfa, lyu__riik)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            iyv__soxyf = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(iyv__soxyf)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            iyv__soxyf = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(iyv__soxyf)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            iyv__soxyf = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(iyv__soxyf)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            iyv__soxyf = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            ipej__ezs = bodo.gatherv(data.indices, allgather, warn_if_rep, root
                )
            okkm__ebvd = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            bbdzt__meyk = gather_scalar(data.shape[0], allgather, root=root)
            zrxo__cvbo = bbdzt__meyk.sum()
            egm__tsueq = bodo.libs.distributed_api.dist_reduce(data.shape[1
                ], np.int32(Reduce_Type.Max.value))
            ilmx__odr = np.empty(zrxo__cvbo + 1, np.int64)
            ipej__ezs = ipej__ezs.astype(np.int64)
            ilmx__odr[0] = 0
            vrwb__geba = 1
            zzwph__fbeqq = 0
            for wnuxo__cwd in bbdzt__meyk:
                for rdbg__nea in range(wnuxo__cwd):
                    zzafa__khd = okkm__ebvd[zzwph__fbeqq + 1] - okkm__ebvd[
                        zzwph__fbeqq]
                    ilmx__odr[vrwb__geba] = ilmx__odr[vrwb__geba - 1
                        ] + zzafa__khd
                    vrwb__geba += 1
                    zzwph__fbeqq += 1
                zzwph__fbeqq += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(iyv__soxyf,
                ipej__ezs, ilmx__odr, (zrxo__cvbo, egm__tsueq))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        nxvny__qklzg = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        nxvny__qklzg += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        obckh__tepm = {}
        exec(nxvny__qklzg, {'bodo': bodo}, obckh__tepm)
        mbvda__gbvlg = obckh__tepm['impl_tuple']
        return mbvda__gbvlg
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    nxvny__qklzg = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    nxvny__qklzg += '    if random:\n'
    nxvny__qklzg += '        if random_seed is None:\n'
    nxvny__qklzg += '            random = 1\n'
    nxvny__qklzg += '        else:\n'
    nxvny__qklzg += '            random = 2\n'
    nxvny__qklzg += '    if random_seed is None:\n'
    nxvny__qklzg += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        egnt__aje = data
        egm__tsueq = len(egnt__aje.columns)
        for i in range(egm__tsueq):
            nxvny__qklzg += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        nxvny__qklzg += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        ynazx__yzx = ', '.join(f'data_{i}' for i in range(egm__tsueq))
        nxvny__qklzg += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(ohzv__wjfd) for
            ohzv__wjfd in range(egm__tsueq))))
        nxvny__qklzg += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        nxvny__qklzg += '    if dests is None:\n'
        nxvny__qklzg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        nxvny__qklzg += '    else:\n'
        nxvny__qklzg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for owy__qntl in range(egm__tsueq):
            nxvny__qklzg += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(owy__qntl))
        nxvny__qklzg += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(egm__tsueq))
        nxvny__qklzg += '    delete_table(out_table)\n'
        nxvny__qklzg += '    if parallel:\n'
        nxvny__qklzg += '        delete_table(table_total)\n'
        ynazx__yzx = ', '.join('out_arr_{}'.format(i) for i in range(
            egm__tsueq))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        nxvny__qklzg += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(ynazx__yzx, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        nxvny__qklzg += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        nxvny__qklzg += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        nxvny__qklzg += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        nxvny__qklzg += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        nxvny__qklzg += '    if dests is None:\n'
        nxvny__qklzg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        nxvny__qklzg += '    else:\n'
        nxvny__qklzg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        nxvny__qklzg += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        nxvny__qklzg += """    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)
"""
        nxvny__qklzg += '    delete_table(out_table)\n'
        nxvny__qklzg += '    if parallel:\n'
        nxvny__qklzg += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        nxvny__qklzg += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        nxvny__qklzg += '    if not parallel:\n'
        nxvny__qklzg += '        return data\n'
        nxvny__qklzg += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        nxvny__qklzg += '    if dests is None:\n'
        nxvny__qklzg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        nxvny__qklzg += '    elif bodo.get_rank() not in dests:\n'
        nxvny__qklzg += '        dim0_local_size = 0\n'
        nxvny__qklzg += '    else:\n'
        nxvny__qklzg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        nxvny__qklzg += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        nxvny__qklzg += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        nxvny__qklzg += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        nxvny__qklzg += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        nxvny__qklzg += '    if dests is None:\n'
        nxvny__qklzg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        nxvny__qklzg += '    else:\n'
        nxvny__qklzg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        nxvny__qklzg += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        nxvny__qklzg += '    delete_table(out_table)\n'
        nxvny__qklzg += '    if parallel:\n'
        nxvny__qklzg += '        delete_table(table_total)\n'
        nxvny__qklzg += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    obckh__tepm = {}
    idsx__smx = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        idsx__smx.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(egnt__aje.columns)})
    exec(nxvny__qklzg, idsx__smx, obckh__tepm)
    impl = obckh__tepm['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    nxvny__qklzg = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        nxvny__qklzg += '    if seed is None:\n'
        nxvny__qklzg += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        nxvny__qklzg += '    np.random.seed(seed)\n'
        nxvny__qklzg += '    if not parallel:\n'
        nxvny__qklzg += '        data = data.copy()\n'
        nxvny__qklzg += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            nxvny__qklzg += '        data = data[:n_samples]\n'
        nxvny__qklzg += '        return data\n'
        nxvny__qklzg += '    else:\n'
        nxvny__qklzg += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        nxvny__qklzg += '        permutation = np.arange(dim0_global_size)\n'
        nxvny__qklzg += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            nxvny__qklzg += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            nxvny__qklzg += '        n_samples = dim0_global_size\n'
        nxvny__qklzg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        nxvny__qklzg += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        nxvny__qklzg += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        nxvny__qklzg += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        nxvny__qklzg += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        nxvny__qklzg += '        return output\n'
    else:
        nxvny__qklzg += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            nxvny__qklzg += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            nxvny__qklzg += '    output = output[:local_n_samples]\n'
        nxvny__qklzg += '    return output\n'
    obckh__tepm = {}
    exec(nxvny__qklzg, {'np': np, 'bodo': bodo}, obckh__tepm)
    impl = obckh__tepm['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    ooiq__jddb = np.empty(sendcounts_nulls.sum(), np.uint8)
    gteo__rnb = 0
    rgb__xeprr = 0
    for fupx__jxxf in range(len(sendcounts)):
        qqoi__quqb = sendcounts[fupx__jxxf]
        mdgn__larhr = sendcounts_nulls[fupx__jxxf]
        rarzf__dfojr = ooiq__jddb[gteo__rnb:gteo__rnb + mdgn__larhr]
        for ohjhz__oem in range(qqoi__quqb):
            set_bit_to_arr(rarzf__dfojr, ohjhz__oem, get_bit_bitmap(
                null_bitmap_ptr, rgb__xeprr))
            rgb__xeprr += 1
        gteo__rnb += mdgn__larhr
    return ooiq__jddb


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    xxex__mav = MPI.COMM_WORLD
    data = xxex__mav.bcast(data, root)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    ougp__suxmv = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    dqmi__loe = (0,) * ougp__suxmv

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        qvpgw__nwjh = np.ascontiguousarray(data)
        lamhv__eujaf = data.ctypes
        wauy__csdj = dqmi__loe
        if rank == MPI_ROOT:
            wauy__csdj = qvpgw__nwjh.shape
        wauy__csdj = bcast_tuple(wauy__csdj)
        tywfe__easa = get_tuple_prod(wauy__csdj[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            wauy__csdj[0])
        send_counts *= tywfe__easa
        udfav__jnmy = send_counts[rank]
        ezxg__imk = np.empty(udfav__jnmy, dtype)
        zubcv__nzn = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(lamhv__eujaf, send_counts.ctypes, zubcv__nzn.ctypes,
            ezxg__imk.ctypes, np.int32(udfav__jnmy), np.int32(typ_val))
        return ezxg__imk.reshape((-1,) + wauy__csdj[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == bodo.dict_str_arr_type:
        import pyarrow as pa
        return pa.array(['a'], type=pa.dictionary(pa.int32(), pa.string()))
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        harj__feqih = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], harj__feqih)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        ddf__bxazt = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=ddf__bxazt)
        vhuwd__dry = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(vhuwd__dry)
        return pd.Index(arr, name=ddf__bxazt)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        ddf__bxazt = _get_name_value_for_type(dtype.name_typ)
        lyu__riik = tuple(_get_name_value_for_type(t) for t in dtype.names_typ)
        ldqy__hdz = tuple(get_value_for_type(t) for t in dtype.array_types)
        ldqy__hdz = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in ldqy__hdz)
        val = pd.MultiIndex.from_arrays(ldqy__hdz, names=lyu__riik)
        val.name = ddf__bxazt
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        ddf__bxazt = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=ddf__bxazt)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ldqy__hdz = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({ddf__bxazt: arr for ddf__bxazt, arr in zip(
            dtype.columns, ldqy__hdz)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        vhuwd__dry = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(vhuwd__dry[0],
            vhuwd__dry[0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if is_str_arr_type(data) or data == binary_array_type:
        vhyrp__xrlj = np.int32(numba_to_c_type(types.int32))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            blo__wzq = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            blo__wzq = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        nxvny__qklzg = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            data = decode_if_dict_array(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {blo__wzq}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        obckh__tepm = dict()
        exec(nxvny__qklzg, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            vhyrp__xrlj, 'char_typ_enum': els__quvpi,
            'decode_if_dict_array': decode_if_dict_array}, obckh__tepm)
        impl = obckh__tepm['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        vhyrp__xrlj = np.int32(numba_to_c_type(types.int32))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            uyuk__ccw = bodo.libs.array_item_arr_ext.get_offsets(data)
            ttksg__lglh = bodo.libs.array_item_arr_ext.get_data(data)
            ttksg__lglh = ttksg__lglh[:uyuk__ccw[-1]]
            aue__dbc = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            avnu__eywa = bcast_scalar(len(data))
            lxp__jjfs = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                lxp__jjfs[i] = uyuk__ccw[i + 1] - uyuk__ccw[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                avnu__eywa)
            zubcv__nzn = bodo.ir.join.calc_disp(send_counts)
            pjp__yixyp = np.empty(n_pes, np.int32)
            if rank == 0:
                lasa__vaxna = 0
                for i in range(n_pes):
                    aak__kxhd = 0
                    for rdbg__nea in range(send_counts[i]):
                        aak__kxhd += lxp__jjfs[lasa__vaxna]
                        lasa__vaxna += 1
                    pjp__yixyp[i] = aak__kxhd
            bcast(pjp__yixyp)
            bfsw__fmrqh = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                bfsw__fmrqh[i] = send_counts[i] + 7 >> 3
            jowc__urwuy = bodo.ir.join.calc_disp(bfsw__fmrqh)
            udfav__jnmy = send_counts[rank]
            hqys__nzlaz = np.empty(udfav__jnmy + 1, np_offset_type)
            omuh__xuxhc = bodo.libs.distributed_api.scatterv_impl(ttksg__lglh,
                pjp__yixyp)
            gyo__atef = udfav__jnmy + 7 >> 3
            qvl__ubc = np.empty(gyo__atef, np.uint8)
            zhv__byq = np.empty(udfav__jnmy, np.uint32)
            c_scatterv(lxp__jjfs.ctypes, send_counts.ctypes, zubcv__nzn.
                ctypes, zhv__byq.ctypes, np.int32(udfav__jnmy), vhyrp__xrlj)
            convert_len_arr_to_offset(zhv__byq.ctypes, hqys__nzlaz.ctypes,
                udfav__jnmy)
            pfkkp__saclm = get_scatter_null_bytes_buff(aue__dbc.ctypes,
                send_counts, bfsw__fmrqh)
            c_scatterv(pfkkp__saclm.ctypes, bfsw__fmrqh.ctypes, jowc__urwuy
                .ctypes, qvl__ubc.ctypes, np.int32(gyo__atef), els__quvpi)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                udfav__jnmy, omuh__xuxhc, hqys__nzlaz, qvl__ubc)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        els__quvpi = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            xmia__len = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            xmia__len = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            xmia__len = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            xmia__len = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            qvpgw__nwjh = data._data
            dlp__pdnb = data._null_bitmap
            ejm__sguq = len(qvpgw__nwjh)
            yicpa__indb = _scatterv_np(qvpgw__nwjh, send_counts)
            avnu__eywa = bcast_scalar(ejm__sguq)
            kvx__vat = len(yicpa__indb) + 7 >> 3
            gqwe__kmzaj = np.empty(kvx__vat, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                avnu__eywa)
            bfsw__fmrqh = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                bfsw__fmrqh[i] = send_counts[i] + 7 >> 3
            jowc__urwuy = bodo.ir.join.calc_disp(bfsw__fmrqh)
            pfkkp__saclm = get_scatter_null_bytes_buff(dlp__pdnb.ctypes,
                send_counts, bfsw__fmrqh)
            c_scatterv(pfkkp__saclm.ctypes, bfsw__fmrqh.ctypes, jowc__urwuy
                .ctypes, gqwe__kmzaj.ctypes, np.int32(kvx__vat), els__quvpi)
            return xmia__len(yicpa__indb, gqwe__kmzaj)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            ktc__ktjrv = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            pwle__gthki = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(ktc__ktjrv,
                pwle__gthki)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ovgc__vqszb = data._start
            yarz__iob = data._stop
            ckva__ffxx = data._step
            ddf__bxazt = data._name
            ddf__bxazt = bcast_scalar(ddf__bxazt)
            ovgc__vqszb = bcast_scalar(ovgc__vqszb)
            yarz__iob = bcast_scalar(yarz__iob)
            ckva__ffxx = bcast_scalar(ckva__ffxx)
            lyqhk__bkblq = bodo.libs.array_kernels.calc_nitems(ovgc__vqszb,
                yarz__iob, ckva__ffxx)
            chunk_start = bodo.libs.distributed_api.get_start(lyqhk__bkblq,
                n_pes, rank)
            vhjs__qlkt = bodo.libs.distributed_api.get_node_portion(
                lyqhk__bkblq, n_pes, rank)
            hxe__jyn = ovgc__vqszb + ckva__ffxx * chunk_start
            alr__ptv = ovgc__vqszb + ckva__ffxx * (chunk_start + vhjs__qlkt)
            alr__ptv = min(alr__ptv, yarz__iob)
            return bodo.hiframes.pd_index_ext.init_range_index(hxe__jyn,
                alr__ptv, ckva__ffxx, ddf__bxazt)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        whwpw__hlj = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            qvpgw__nwjh = data._data
            ddf__bxazt = data._name
            ddf__bxazt = bcast_scalar(ddf__bxazt)
            arr = bodo.libs.distributed_api.scatterv_impl(qvpgw__nwjh,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                ddf__bxazt, whwpw__hlj)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            qvpgw__nwjh = data._data
            ddf__bxazt = data._name
            ddf__bxazt = bcast_scalar(ddf__bxazt)
            arr = bodo.libs.distributed_api.scatterv_impl(qvpgw__nwjh,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, ddf__bxazt)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            iyv__soxyf = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            ddf__bxazt = bcast_scalar(data._name)
            lyu__riik = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(iyv__soxyf
                , lyu__riik, ddf__bxazt)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ddf__bxazt = bodo.hiframes.pd_series_ext.get_series_name(data)
            qghmi__ulk = bcast_scalar(ddf__bxazt)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            rqf__oph = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rqf__oph, qghmi__ulk)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        egm__tsueq = len(data.columns)
        ynazx__yzx = ', '.join('g_data_{}'.format(i) for i in range(egm__tsueq)
            )
        qyx__ksjyq = ColNamesMetaType(data.columns)
        nxvny__qklzg = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(egm__tsueq):
            nxvny__qklzg += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            nxvny__qklzg += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        nxvny__qklzg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        nxvny__qklzg += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        nxvny__qklzg += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({ynazx__yzx},), g_index, __col_name_meta_scaterv_impl)
"""
        obckh__tepm = {}
        exec(nxvny__qklzg, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            qyx__ksjyq}, obckh__tepm)
        wnhjs__djilx = obckh__tepm['impl_df']
        return wnhjs__djilx
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            wykh__dci = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                wykh__dci, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        nxvny__qklzg = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        nxvny__qklzg += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        obckh__tepm = {}
        exec(nxvny__qklzg, {'bodo': bodo}, obckh__tepm)
        mbvda__gbvlg = obckh__tepm['impl_tuple']
        return mbvda__gbvlg
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data, root=MPI_ROOT):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data, root=MPI_ROOT):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.bcast()')
    if isinstance(data, types.Array):

        def bcast_impl(data, root=MPI_ROOT):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0, np.int32(root))
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data, root=MPI_ROOT):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0, np.int32(root))
            bcast(data._null_bitmap, root)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data, root=MPI_ROOT):
            bcast(data._data, root)
            bcast(data._null_bitmap, root)
            return
        return bcast_impl_int_arr
    if is_str_arr_type(data) or data == binary_array_type:
        okm__gwfm = np.int32(numba_to_c_type(offset_type))
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            udfav__jnmy = len(data)
            smer__ghxc = num_total_chars(data)
            assert udfav__jnmy < INT_MAX
            assert smer__ghxc < INT_MAX
            nib__utr = get_offset_ptr(data)
            lamhv__eujaf = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            mdgn__larhr = udfav__jnmy + 7 >> 3
            c_bcast(nib__utr, np.int32(udfav__jnmy + 1), okm__gwfm, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(lamhv__eujaf, np.int32(smer__ghxc), els__quvpi, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(mdgn__larhr), els__quvpi, np.
                array([-1]).ctypes, 0, np.int32(root))
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def bcast_scalar(val, root=MPI_ROOT):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise BodoError(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val, root=MPI_ROOT: None
    if val == bodo.string_type:
        els__quvpi = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                xgtte__fnkx = 0
                wkdb__cxplz = np.empty(0, np.uint8).ctypes
            else:
                wkdb__cxplz, xgtte__fnkx = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            xgtte__fnkx = bodo.libs.distributed_api.bcast_scalar(xgtte__fnkx,
                root)
            if rank != root:
                rywl__hjok = np.empty(xgtte__fnkx + 1, np.uint8)
                rywl__hjok[xgtte__fnkx] = 0
                wkdb__cxplz = rywl__hjok.ctypes
            c_bcast(wkdb__cxplz, np.int32(xgtte__fnkx), els__quvpi, np.
                array([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(wkdb__cxplz, xgtte__fnkx)
        return impl_str
    typ_val = numba_to_c_type(val)
    nxvny__qklzg = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    obckh__tepm = {}
    exec(nxvny__qklzg, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, obckh__tepm)
    nbut__lmew = obckh__tepm['bcast_scalar_impl']
    return nbut__lmew


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    vha__yrc = len(val)
    nxvny__qklzg = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    nxvny__qklzg += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(vha__yrc)), 
        ',' if vha__yrc else '')
    obckh__tepm = {}
    exec(nxvny__qklzg, {'bcast_scalar': bcast_scalar}, obckh__tepm)
    bqd__ulw = obckh__tepm['bcast_tuple_impl']
    return bqd__ulw


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            udfav__jnmy = bcast_scalar(len(arr), root)
            mhe__hmcn = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(udfav__jnmy, mhe__hmcn)
            return arr
        return prealloc_impl
    return lambda arr, root=MPI_ROOT: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):
    if not idx.has_step:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            hxe__jyn = max(arr_start, slice_index.start) - arr_start
            alr__ptv = max(slice_index.stop - arr_start, 0)
            return slice(hxe__jyn, alr__ptv)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            ovgc__vqszb = slice_index.start
            ckva__ffxx = slice_index.step
            rifqk__ngl = (0 if ckva__ffxx == 1 or ovgc__vqszb > arr_start else
                abs(ckva__ffxx - arr_start % ckva__ffxx) % ckva__ffxx)
            hxe__jyn = max(arr_start, slice_index.start
                ) - arr_start + rifqk__ngl
            alr__ptv = max(slice_index.stop - arr_start, 0)
            return slice(hxe__jyn, alr__ptv, ckva__ffxx)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        zrp__ylj = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[zrp__ylj])
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if is_str_arr_type(arr) or arr == bodo.binary_array_type:
        ixzr__vpqt = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        els__quvpi = np.int32(numba_to_c_type(types.uint8))
        ihtqs__asjj = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            itlit__ouife = np.int32(10)
            tag = np.int32(11)
            rccq__bci = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                wes__imc = arr._data
                iryy__rxh = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    wes__imc, ind)
                jkuq__lxlii = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    wes__imc, ind + 1)
                length = jkuq__lxlii - iryy__rxh
                ofkjx__ifqmw = wes__imc[ind]
                rccq__bci[0] = length
                isend(rccq__bci, np.int32(1), root, itlit__ouife, True)
                isend(ofkjx__ifqmw, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                ihtqs__asjj, ixzr__vpqt, 0, 1)
            haqmb__bta = 0
            if rank == root:
                haqmb__bta = recv(np.int64, ANY_SOURCE, itlit__ouife)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    ihtqs__asjj, ixzr__vpqt, haqmb__bta, 1)
                lamhv__eujaf = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(lamhv__eujaf, np.int32(haqmb__bta), els__quvpi,
                    ANY_SOURCE, tag)
            dummy_use(rccq__bci)
            haqmb__bta = bcast_scalar(haqmb__bta)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    ihtqs__asjj, ixzr__vpqt, haqmb__bta, 1)
            lamhv__eujaf = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(lamhv__eujaf, np.int32(haqmb__bta), els__quvpi, np.
                array([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, haqmb__bta)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        yydm__anba = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, yydm__anba)
            if arr_start <= ind < arr_start + len(arr):
                wykh__dci = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = wykh__dci[ind - arr_start]
                send_arr = np.full(1, data, yydm__anba)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = yydm__anba(-1)
            if rank == root:
                val = recv(yydm__anba, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            cvs__fea = arr.dtype.categories[max(val, 0)]
            return cvs__fea
        return cat_getitem_impl
    ahuz__jdw = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, ahuz__jdw)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, ahuz__jdw)[0]
        if rank == root:
            val = recv(ahuz__jdw, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    myzd__zjwh = get_type_enum(out_data)
    assert typ_enum == myzd__zjwh
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    nxvny__qklzg = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        nxvny__qklzg += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    nxvny__qklzg += '  return\n'
    obckh__tepm = {}
    exec(nxvny__qklzg, {'alltoallv': alltoallv}, obckh__tepm)
    rtxk__ttgw = obckh__tepm['f']
    return rtxk__ttgw


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    ovgc__vqszb = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return ovgc__vqszb, count


@numba.njit
def get_start(total_size, pes, rank):
    ctukt__rby = total_size % pes
    bao__okb = (total_size - ctukt__rby) // pes
    return rank * bao__okb + min(rank, ctukt__rby)


@numba.njit
def get_end(total_size, pes, rank):
    ctukt__rby = total_size % pes
    bao__okb = (total_size - ctukt__rby) // pes
    return (rank + 1) * bao__okb + min(rank + 1, ctukt__rby)


@numba.njit
def get_node_portion(total_size, pes, rank):
    ctukt__rby = total_size % pes
    bao__okb = (total_size - ctukt__rby) // pes
    if rank < ctukt__rby:
        return bao__okb + 1
    else:
        return bao__okb


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    xyq__dvndf = in_arr.dtype(0)
    qjyr__hohd = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        aak__kxhd = xyq__dvndf
        for dbxk__thxgf in np.nditer(in_arr):
            aak__kxhd += dbxk__thxgf.item()
        lfcik__bzj = dist_exscan(aak__kxhd, qjyr__hohd)
        for i in range(in_arr.size):
            lfcik__bzj += in_arr[i]
            out_arr[i] = lfcik__bzj
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    wmlp__vxxum = in_arr.dtype(1)
    qjyr__hohd = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        aak__kxhd = wmlp__vxxum
        for dbxk__thxgf in np.nditer(in_arr):
            aak__kxhd *= dbxk__thxgf.item()
        lfcik__bzj = dist_exscan(aak__kxhd, qjyr__hohd)
        if get_rank() == 0:
            lfcik__bzj = wmlp__vxxum
        for i in range(in_arr.size):
            lfcik__bzj *= in_arr[i]
            out_arr[i] = lfcik__bzj
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        wmlp__vxxum = np.finfo(in_arr.dtype(1).dtype).max
    else:
        wmlp__vxxum = np.iinfo(in_arr.dtype(1).dtype).max
    qjyr__hohd = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        aak__kxhd = wmlp__vxxum
        for dbxk__thxgf in np.nditer(in_arr):
            aak__kxhd = min(aak__kxhd, dbxk__thxgf.item())
        lfcik__bzj = dist_exscan(aak__kxhd, qjyr__hohd)
        if get_rank() == 0:
            lfcik__bzj = wmlp__vxxum
        for i in range(in_arr.size):
            lfcik__bzj = min(lfcik__bzj, in_arr[i])
            out_arr[i] = lfcik__bzj
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        wmlp__vxxum = np.finfo(in_arr.dtype(1).dtype).min
    else:
        wmlp__vxxum = np.iinfo(in_arr.dtype(1).dtype).min
    wmlp__vxxum = in_arr.dtype(1)
    qjyr__hohd = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        aak__kxhd = wmlp__vxxum
        for dbxk__thxgf in np.nditer(in_arr):
            aak__kxhd = max(aak__kxhd, dbxk__thxgf.item())
        lfcik__bzj = dist_exscan(aak__kxhd, qjyr__hohd)
        if get_rank() == 0:
            lfcik__bzj = wmlp__vxxum
        for i in range(in_arr.size):
            lfcik__bzj = max(lfcik__bzj, in_arr[i])
            out_arr[i] = lfcik__bzj
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    rmcj__win = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), rmcj__win)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    pub__klq = args[0]
    if equiv_set.has_shape(pub__klq):
        return ArrayAnalysis.AnalyzeResult(shape=pub__klq, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)
ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_rep_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
@infer_global(rep_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


def print_if_not_empty(args):
    pass


@overload(print_if_not_empty)
def overload_print_if_not_empty(*args):
    vurx__zcqvy = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for
        i, nura__bgfcu in enumerate(args) if is_array_typ(nura__bgfcu) or
        isinstance(nura__bgfcu, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    nxvny__qklzg = f"""def impl(*args):
    if {vurx__zcqvy} or bodo.get_rank() == 0:
        print(*args)"""
    obckh__tepm = {}
    exec(nxvny__qklzg, globals(), obckh__tepm)
    impl = obckh__tepm['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        ogn__kqrv = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        nxvny__qklzg = 'def f(req, cond=True):\n'
        nxvny__qklzg += f'  return {ogn__kqrv}\n'
        obckh__tepm = {}
        exec(nxvny__qklzg, {'_wait': _wait}, obckh__tepm)
        impl = obckh__tepm['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        ctukt__rby = 1
        for a in t:
            ctukt__rby *= a
        return ctukt__rby
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    kezxp__sljwg = np.ascontiguousarray(in_arr)
    fuyz__hfp = get_tuple_prod(kezxp__sljwg.shape[1:])
    blx__mgwuh = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        nos__kcj = np.array(dest_ranks, dtype=np.int32)
    else:
        nos__kcj = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, kezxp__sljwg.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * blx__mgwuh, 
        dtype_size * fuyz__hfp, len(nos__kcj), nos__kcj.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp, types.int64))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len,
    n_samples):
    rqe__cgi = np.ascontiguousarray(rhs)
    mfokh__pkv = get_tuple_prod(rqe__cgi.shape[1:])
    ldv__kpsc = dtype_size * mfokh__pkv
    permutation_array_index(lhs.ctypes, lhs_len, ldv__kpsc, rqe__cgi.ctypes,
        rqe__cgi.shape[0], p.ctypes, p_len, n_samples)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def finalize_mpi():
    finalize()
    _check_for_cpp_errors()


@numba.njit
def finalize_fs():
    disconnect_hdfs()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(finalize_mpi)
atexit.register(flush_stdout)
atexit.register(finalize_fs)


def bcast_comm(data, comm_ranks, nranks, root=MPI_ROOT):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype, root)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks, root)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks, root=MPI_ROOT):
    return lambda data, comm_ranks, nranks, root=MPI_ROOT: bcast_comm_impl(data
        , comm_ranks, nranks, root)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks, root=MPI_ROOT):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        nxvny__qklzg = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        obckh__tepm = {}
        exec(nxvny__qklzg, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, obckh__tepm)
        nbut__lmew = obckh__tepm['bcast_scalar_impl']
        return nbut__lmew
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        egm__tsueq = len(data.columns)
        ynazx__yzx = ', '.join('g_data_{}'.format(i) for i in range(egm__tsueq)
            )
        rycau__vje = bodo.utils.transform.gen_const_tup(data.columns)
        ColNamesMetaType(('$_bodo_col2_',))
        nxvny__qklzg = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(egm__tsueq):
            nxvny__qklzg += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            nxvny__qklzg += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        nxvny__qklzg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        nxvny__qklzg += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        nxvny__qklzg += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(ynazx__yzx, rycau__vje))
        obckh__tepm = {}
        exec(nxvny__qklzg, {'bodo': bodo}, obckh__tepm)
        wnhjs__djilx = obckh__tepm['impl_df']
        return wnhjs__djilx
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ovgc__vqszb = data._start
            yarz__iob = data._stop
            ckva__ffxx = data._step
            ddf__bxazt = data._name
            ddf__bxazt = bcast_scalar(ddf__bxazt, root)
            ovgc__vqszb = bcast_scalar(ovgc__vqszb, root)
            yarz__iob = bcast_scalar(yarz__iob, root)
            ckva__ffxx = bcast_scalar(ckva__ffxx, root)
            lyqhk__bkblq = bodo.libs.array_kernels.calc_nitems(ovgc__vqszb,
                yarz__iob, ckva__ffxx)
            chunk_start = bodo.libs.distributed_api.get_start(lyqhk__bkblq,
                n_pes, rank)
            vhjs__qlkt = bodo.libs.distributed_api.get_node_portion(
                lyqhk__bkblq, n_pes, rank)
            hxe__jyn = ovgc__vqszb + ckva__ffxx * chunk_start
            alr__ptv = ovgc__vqszb + ckva__ffxx * (chunk_start + vhjs__qlkt)
            alr__ptv = min(alr__ptv, yarz__iob)
            return bodo.hiframes.pd_index_ext.init_range_index(hxe__jyn,
                alr__ptv, ckva__ffxx, ddf__bxazt)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            qvpgw__nwjh = data._data
            ddf__bxazt = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(qvpgw__nwjh,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, ddf__bxazt)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ddf__bxazt = bodo.hiframes.pd_series_ext.get_series_name(data)
            qghmi__ulk = bodo.libs.distributed_api.bcast_comm_impl(ddf__bxazt,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            rqf__oph = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rqf__oph, qghmi__ulk)
        return impl_series
    if isinstance(data, types.BaseTuple):
        nxvny__qklzg = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        nxvny__qklzg += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        obckh__tepm = {}
        exec(nxvny__qklzg, {'bcast_comm_impl': bcast_comm_impl}, obckh__tepm)
        mbvda__gbvlg = obckh__tepm['impl_tuple']
        return mbvda__gbvlg
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    ougp__suxmv = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    dqmi__loe = (0,) * ougp__suxmv

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        qvpgw__nwjh = np.ascontiguousarray(data)
        lamhv__eujaf = data.ctypes
        wauy__csdj = dqmi__loe
        if rank == root:
            wauy__csdj = qvpgw__nwjh.shape
        wauy__csdj = bcast_tuple(wauy__csdj, root)
        tywfe__easa = get_tuple_prod(wauy__csdj[1:])
        send_counts = wauy__csdj[0] * tywfe__easa
        ezxg__imk = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(lamhv__eujaf, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(ezxg__imk.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return ezxg__imk.reshape((-1,) + wauy__csdj[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        xxex__mav = MPI.COMM_WORLD
        qsa__dpmze = MPI.Get_processor_name()
        xqgg__wxq = xxex__mav.allgather(qsa__dpmze)
        node_ranks = defaultdict(list)
        for i, ydsj__jary in enumerate(xqgg__wxq):
            node_ranks[ydsj__jary].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    xxex__mav = MPI.COMM_WORLD
    egu__xtcu = xxex__mav.Get_group()
    ppoh__xguxc = egu__xtcu.Incl(comm_ranks)
    pmnj__eopp = xxex__mav.Create_group(ppoh__xguxc)
    return pmnj__eopp


def get_nodes_first_ranks():
    two__izxyq = get_host_ranks()
    return np.array([dppxn__zittq[0] for dppxn__zittq in two__izxyq.values(
        )], dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
