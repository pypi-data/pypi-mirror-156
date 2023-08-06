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
    edtb__yookp = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, edtb__yookp, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    edtb__yookp = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, edtb__yookp, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            edtb__yookp = get_type_enum(arr)
            return _isend(arr.ctypes, size, edtb__yookp, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        edtb__yookp = np.int32(numba_to_c_type(arr.dtype))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            zqt__eml = size + 7 >> 3
            garza__andy = _isend(arr._data.ctypes, size, edtb__yookp, pe,
                tag, cond)
            etyu__lehb = _isend(arr._null_bitmap.ctypes, zqt__eml,
                aabkr__thmut, pe, tag, cond)
            return garza__andy, etyu__lehb
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        lqnyj__usg = np.int32(numba_to_c_type(offset_type))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            jlui__xhbfd = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(jlui__xhbfd, pe, tag - 1)
            zqt__eml = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                lqnyj__usg, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), jlui__xhbfd,
                aabkr__thmut, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), zqt__eml,
                aabkr__thmut, pe, tag)
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
            edtb__yookp = get_type_enum(arr)
            return _irecv(arr.ctypes, size, edtb__yookp, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        edtb__yookp = np.int32(numba_to_c_type(arr.dtype))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            zqt__eml = size + 7 >> 3
            garza__andy = _irecv(arr._data.ctypes, size, edtb__yookp, pe,
                tag, cond)
            etyu__lehb = _irecv(arr._null_bitmap.ctypes, zqt__eml,
                aabkr__thmut, pe, tag, cond)
            return garza__andy, etyu__lehb
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        lqnyj__usg = np.int32(numba_to_c_type(offset_type))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            nwzw__wcp = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            nwzw__wcp = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zvrdy__fqou = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {nwzw__wcp}(size, n_chars)
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
        hmm__njtii = dict()
        exec(zvrdy__fqou, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            lqnyj__usg, 'char_typ_enum': aabkr__thmut}, hmm__njtii)
        impl = hmm__njtii['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    edtb__yookp = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), edtb__yookp)


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
        zfd__xrbvj = n_pes if rank == root or allgather else 0
        rva__spji = np.empty(zfd__xrbvj, dtype)
        c_gather_scalar(send.ctypes, rva__spji.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return rva__spji
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
        encl__epve = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], encl__epve)
        return builder.bitcast(encl__epve, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        encl__epve = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(encl__epve)
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
    spi__wlggo = types.unliteral(value)
    if isinstance(spi__wlggo, IndexValueType):
        spi__wlggo = spi__wlggo.val_typ
        ubqte__wuppp = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            ubqte__wuppp.append(types.int64)
            ubqte__wuppp.append(bodo.datetime64ns)
            ubqte__wuppp.append(bodo.timedelta64ns)
            ubqte__wuppp.append(bodo.datetime_date_type)
        if spi__wlggo not in ubqte__wuppp:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(spi__wlggo))
    typ_enum = np.int32(numba_to_c_type(spi__wlggo))

    def impl(value, reduce_op):
        skgre__wdhe = value_to_ptr(value)
        etzpz__cmrap = value_to_ptr(value)
        _dist_reduce(skgre__wdhe, etzpz__cmrap, reduce_op, typ_enum)
        return load_val_ptr(etzpz__cmrap, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    spi__wlggo = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(spi__wlggo))
    ylq__uqbxu = spi__wlggo(0)

    def impl(value, reduce_op):
        skgre__wdhe = value_to_ptr(value)
        etzpz__cmrap = value_to_ptr(ylq__uqbxu)
        _dist_exscan(skgre__wdhe, etzpz__cmrap, reduce_op, typ_enum)
        return load_val_ptr(etzpz__cmrap, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    jjrc__wejp = 0
    qjxp__qekmc = 0
    for i in range(len(recv_counts)):
        prk__vcg = recv_counts[i]
        zqt__eml = recv_counts_nulls[i]
        dzing__ocblt = tmp_null_bytes[jjrc__wejp:jjrc__wejp + zqt__eml]
        for agxyr__phzqf in range(prk__vcg):
            set_bit_to(null_bitmap_ptr, qjxp__qekmc, get_bit(dzing__ocblt,
                agxyr__phzqf))
            qjxp__qekmc += 1
        jjrc__wejp += zqt__eml


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            evpsj__rdry = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                evpsj__rdry, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            wap__xkqs = data.size
            recv_counts = gather_scalar(np.int32(wap__xkqs), allgather,
                root=root)
            aef__uem = recv_counts.sum()
            ohnu__tdr = empty_like_type(aef__uem, data)
            mdy__bpr = np.empty(1, np.int32)
            if rank == root or allgather:
                mdy__bpr = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(wap__xkqs), ohnu__tdr.ctypes,
                recv_counts.ctypes, mdy__bpr.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return ohnu__tdr.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            ohnu__tdr = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(ohnu__tdr)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ohnu__tdr = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(ohnu__tdr)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            wap__xkqs = len(data)
            zqt__eml = wap__xkqs + 7 >> 3
            recv_counts = gather_scalar(np.int32(wap__xkqs), allgather,
                root=root)
            aef__uem = recv_counts.sum()
            ohnu__tdr = empty_like_type(aef__uem, data)
            mdy__bpr = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            cvbo__ltjrf = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mdy__bpr = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                cvbo__ltjrf = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(wap__xkqs),
                ohnu__tdr._days_data.ctypes, recv_counts.ctypes, mdy__bpr.
                ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(wap__xkqs),
                ohnu__tdr._seconds_data.ctypes, recv_counts.ctypes,
                mdy__bpr.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(wap__xkqs),
                ohnu__tdr._microseconds_data.ctypes, recv_counts.ctypes,
                mdy__bpr.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(zqt__eml),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                cvbo__ltjrf.ctypes, aabkr__thmut, allgather, np.int32(root))
            copy_gathered_null_bytes(ohnu__tdr._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return ohnu__tdr
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            wap__xkqs = len(data)
            zqt__eml = wap__xkqs + 7 >> 3
            recv_counts = gather_scalar(np.int32(wap__xkqs), allgather,
                root=root)
            aef__uem = recv_counts.sum()
            ohnu__tdr = empty_like_type(aef__uem, data)
            mdy__bpr = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            cvbo__ltjrf = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mdy__bpr = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                cvbo__ltjrf = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(wap__xkqs), ohnu__tdr.
                _data.ctypes, recv_counts.ctypes, mdy__bpr.ctypes, np.int32
                (typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(zqt__eml),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                cvbo__ltjrf.ctypes, aabkr__thmut, allgather, np.int32(root))
            copy_gathered_null_bytes(ohnu__tdr._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return ohnu__tdr
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        beom__swggd = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ghs__hzee = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                ghs__hzee, beom__swggd)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            toxq__ttq = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            bvx__keutq = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(toxq__ttq,
                bvx__keutq)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            jurn__ojs = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            brme__uhg = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                brme__uhg, jurn__ojs)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        igtb__nidr = np.iinfo(np.int64).max
        qdg__vdnb = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            sxcs__atj = data._start
            wqeho__cahv = data._stop
            if len(data) == 0:
                sxcs__atj = igtb__nidr
                wqeho__cahv = qdg__vdnb
            sxcs__atj = bodo.libs.distributed_api.dist_reduce(sxcs__atj, np
                .int32(Reduce_Type.Min.value))
            wqeho__cahv = bodo.libs.distributed_api.dist_reduce(wqeho__cahv,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if sxcs__atj == igtb__nidr and wqeho__cahv == qdg__vdnb:
                sxcs__atj = 0
                wqeho__cahv = 0
            xtwu__xxp = max(0, -(-(wqeho__cahv - sxcs__atj) // data._step))
            if xtwu__xxp < total_len:
                wqeho__cahv = sxcs__atj + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                sxcs__atj = 0
                wqeho__cahv = 0
            return bodo.hiframes.pd_index_ext.init_range_index(sxcs__atj,
                wqeho__cahv, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            bji__ymj = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, bji__ymj)
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
            ohnu__tdr = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(ohnu__tdr,
                data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        hmez__ldiru = {'bodo': bodo, 'get_table_block': bodo.hiframes.table
            .get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        zvrdy__fqou = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        zvrdy__fqou += '  T = data\n'
        zvrdy__fqou += '  T2 = init_table(T, True)\n'
        for qgspy__jvgkc in data.type_to_blk.values():
            hmez__ldiru[f'arr_inds_{qgspy__jvgkc}'] = np.array(data.
                block_to_arr_ind[qgspy__jvgkc], dtype=np.int64)
            zvrdy__fqou += (
                f'  arr_list_{qgspy__jvgkc} = get_table_block(T, {qgspy__jvgkc})\n'
                )
            zvrdy__fqou += f"""  out_arr_list_{qgspy__jvgkc} = alloc_list_like(arr_list_{qgspy__jvgkc}, len(arr_list_{qgspy__jvgkc}), True)
"""
            zvrdy__fqou += f'  for i in range(len(arr_list_{qgspy__jvgkc})):\n'
            zvrdy__fqou += (
                f'    arr_ind_{qgspy__jvgkc} = arr_inds_{qgspy__jvgkc}[i]\n')
            zvrdy__fqou += f"""    ensure_column_unboxed(T, arr_list_{qgspy__jvgkc}, i, arr_ind_{qgspy__jvgkc})
"""
            zvrdy__fqou += f"""    out_arr_{qgspy__jvgkc} = bodo.gatherv(arr_list_{qgspy__jvgkc}[i], allgather, warn_if_rep, root)
"""
            zvrdy__fqou += (
                f'    out_arr_list_{qgspy__jvgkc}[i] = out_arr_{qgspy__jvgkc}\n'
                )
            zvrdy__fqou += f"""  T2 = set_table_block(T2, out_arr_list_{qgspy__jvgkc}, {qgspy__jvgkc})
"""
        zvrdy__fqou += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        zvrdy__fqou += f'  T2 = set_table_len(T2, length)\n'
        zvrdy__fqou += f'  return T2\n'
        hmm__njtii = {}
        exec(zvrdy__fqou, hmez__ldiru, hmm__njtii)
        epcbz__ffjq = hmm__njtii['impl_table']
        return epcbz__ffjq
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wkn__har = len(data.columns)
        if wkn__har == 0:
            amwkz__awfh = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                vjcjv__zvkbc = bodo.gatherv(index, allgather, warn_if_rep, root
                    )
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    vjcjv__zvkbc, amwkz__awfh)
            return impl
        afm__qyrrc = ', '.join(f'g_data_{i}' for i in range(wkn__har))
        zvrdy__fqou = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            zyyof__znhgd = bodo.hiframes.pd_dataframe_ext.DataFrameType(data
                .data, data.index, data.columns, Distribution.REP, True)
            afm__qyrrc = 'T2'
            zvrdy__fqou += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            zvrdy__fqou += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(wkn__har):
                zvrdy__fqou += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                zvrdy__fqou += (
                    """  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)
"""
                    .format(i, i))
        zvrdy__fqou += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zvrdy__fqou += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        zvrdy__fqou += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(afm__qyrrc))
        hmm__njtii = {}
        hmez__ldiru = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(zvrdy__fqou, hmez__ldiru, hmm__njtii)
        zxqmy__sbpbu = hmm__njtii['impl_df']
        return zxqmy__sbpbu
    if isinstance(data, ArrayItemArrayType):
        iacm__mnunw = np.int32(numba_to_c_type(types.int32))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            jzcsd__ryv = bodo.libs.array_item_arr_ext.get_offsets(data)
            soa__jcor = bodo.libs.array_item_arr_ext.get_data(data)
            soa__jcor = soa__jcor[:jzcsd__ryv[-1]]
            znvfn__nugq = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            wap__xkqs = len(data)
            pezvu__jzri = np.empty(wap__xkqs, np.uint32)
            zqt__eml = wap__xkqs + 7 >> 3
            for i in range(wap__xkqs):
                pezvu__jzri[i] = jzcsd__ryv[i + 1] - jzcsd__ryv[i]
            recv_counts = gather_scalar(np.int32(wap__xkqs), allgather,
                root=root)
            aef__uem = recv_counts.sum()
            mdy__bpr = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            cvbo__ltjrf = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mdy__bpr = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for sppj__xhbbn in range(len(recv_counts)):
                    recv_counts_nulls[sppj__xhbbn] = recv_counts[sppj__xhbbn
                        ] + 7 >> 3
                cvbo__ltjrf = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            gqswy__xjofv = np.empty(aef__uem + 1, np.uint32)
            bkg__yhrb = bodo.gatherv(soa__jcor, allgather, warn_if_rep, root)
            nbib__jdah = np.empty(aef__uem + 7 >> 3, np.uint8)
            c_gatherv(pezvu__jzri.ctypes, np.int32(wap__xkqs), gqswy__xjofv
                .ctypes, recv_counts.ctypes, mdy__bpr.ctypes, iacm__mnunw,
                allgather, np.int32(root))
            c_gatherv(znvfn__nugq.ctypes, np.int32(zqt__eml),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                cvbo__ltjrf.ctypes, aabkr__thmut, allgather, np.int32(root))
            dummy_use(data)
            ffq__cpz = np.empty(aef__uem + 1, np.uint64)
            convert_len_arr_to_offset(gqswy__xjofv.ctypes, ffq__cpz.ctypes,
                aef__uem)
            copy_gathered_null_bytes(nbib__jdah.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                aef__uem, bkg__yhrb, ffq__cpz, nbib__jdah)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        ynq__otvo = data.names
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            apo__nbeiy = bodo.libs.struct_arr_ext.get_data(data)
            rehzw__vqa = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            lmmov__cvzwl = bodo.gatherv(apo__nbeiy, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            wap__xkqs = len(data)
            zqt__eml = wap__xkqs + 7 >> 3
            recv_counts = gather_scalar(np.int32(wap__xkqs), allgather,
                root=root)
            aef__uem = recv_counts.sum()
            ltsww__oyy = np.empty(aef__uem + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            cvbo__ltjrf = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                cvbo__ltjrf = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(rehzw__vqa.ctypes, np.int32(zqt__eml), tmp_null_bytes
                .ctypes, recv_counts_nulls.ctypes, cvbo__ltjrf.ctypes,
                aabkr__thmut, allgather, np.int32(root))
            copy_gathered_null_bytes(ltsww__oyy.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(lmmov__cvzwl,
                ltsww__oyy, ynq__otvo)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            ohnu__tdr = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(ohnu__tdr)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ohnu__tdr = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(ohnu__tdr)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            ohnu__tdr = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(ohnu__tdr)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ohnu__tdr = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            bjh__zcjux = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            uxuui__lbc = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            xtb__ppkpd = gather_scalar(data.shape[0], allgather, root=root)
            lxkc__lwdz = xtb__ppkpd.sum()
            wkn__har = bodo.libs.distributed_api.dist_reduce(data.shape[1],
                np.int32(Reduce_Type.Max.value))
            vuiin__etyt = np.empty(lxkc__lwdz + 1, np.int64)
            bjh__zcjux = bjh__zcjux.astype(np.int64)
            vuiin__etyt[0] = 0
            uxjmb__smob = 1
            pubm__uxhzg = 0
            for bdk__dzy in xtb__ppkpd:
                for dooce__lwkv in range(bdk__dzy):
                    qpk__kit = uxuui__lbc[pubm__uxhzg + 1] - uxuui__lbc[
                        pubm__uxhzg]
                    vuiin__etyt[uxjmb__smob] = vuiin__etyt[uxjmb__smob - 1
                        ] + qpk__kit
                    uxjmb__smob += 1
                    pubm__uxhzg += 1
                pubm__uxhzg += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(ohnu__tdr,
                bjh__zcjux, vuiin__etyt, (lxkc__lwdz, wkn__har))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        zvrdy__fqou = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        zvrdy__fqou += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        hmm__njtii = {}
        exec(zvrdy__fqou, {'bodo': bodo}, hmm__njtii)
        xzx__xcj = hmm__njtii['impl_tuple']
        return xzx__xcj
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    zvrdy__fqou = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    zvrdy__fqou += '    if random:\n'
    zvrdy__fqou += '        if random_seed is None:\n'
    zvrdy__fqou += '            random = 1\n'
    zvrdy__fqou += '        else:\n'
    zvrdy__fqou += '            random = 2\n'
    zvrdy__fqou += '    if random_seed is None:\n'
    zvrdy__fqou += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        une__dejju = data
        wkn__har = len(une__dejju.columns)
        for i in range(wkn__har):
            zvrdy__fqou += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        zvrdy__fqou += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        afm__qyrrc = ', '.join(f'data_{i}' for i in range(wkn__har))
        zvrdy__fqou += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(mvamg__zlkcr) for
            mvamg__zlkcr in range(wkn__har))))
        zvrdy__fqou += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        zvrdy__fqou += '    if dests is None:\n'
        zvrdy__fqou += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zvrdy__fqou += '    else:\n'
        zvrdy__fqou += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for ugkup__lmwu in range(wkn__har):
            zvrdy__fqou += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(ugkup__lmwu))
        zvrdy__fqou += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(wkn__har))
        zvrdy__fqou += '    delete_table(out_table)\n'
        zvrdy__fqou += '    if parallel:\n'
        zvrdy__fqou += '        delete_table(table_total)\n'
        afm__qyrrc = ', '.join('out_arr_{}'.format(i) for i in range(wkn__har))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        zvrdy__fqou += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(afm__qyrrc, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        zvrdy__fqou += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        zvrdy__fqou += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        zvrdy__fqou += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        zvrdy__fqou += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        zvrdy__fqou += '    if dests is None:\n'
        zvrdy__fqou += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zvrdy__fqou += '    else:\n'
        zvrdy__fqou += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        zvrdy__fqou += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        zvrdy__fqou += """    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)
"""
        zvrdy__fqou += '    delete_table(out_table)\n'
        zvrdy__fqou += '    if parallel:\n'
        zvrdy__fqou += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        zvrdy__fqou += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        zvrdy__fqou += '    if not parallel:\n'
        zvrdy__fqou += '        return data\n'
        zvrdy__fqou += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        zvrdy__fqou += '    if dests is None:\n'
        zvrdy__fqou += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        zvrdy__fqou += '    elif bodo.get_rank() not in dests:\n'
        zvrdy__fqou += '        dim0_local_size = 0\n'
        zvrdy__fqou += '    else:\n'
        zvrdy__fqou += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        zvrdy__fqou += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        zvrdy__fqou += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        zvrdy__fqou += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        zvrdy__fqou += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        zvrdy__fqou += '    if dests is None:\n'
        zvrdy__fqou += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zvrdy__fqou += '    else:\n'
        zvrdy__fqou += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        zvrdy__fqou += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        zvrdy__fqou += '    delete_table(out_table)\n'
        zvrdy__fqou += '    if parallel:\n'
        zvrdy__fqou += '        delete_table(table_total)\n'
        zvrdy__fqou += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    hmm__njtii = {}
    hmez__ldiru = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array
        .array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hmez__ldiru.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(une__dejju.columns)})
    exec(zvrdy__fqou, hmez__ldiru, hmm__njtii)
    impl = hmm__njtii['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    zvrdy__fqou = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        zvrdy__fqou += '    if seed is None:\n'
        zvrdy__fqou += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        zvrdy__fqou += '    np.random.seed(seed)\n'
        zvrdy__fqou += '    if not parallel:\n'
        zvrdy__fqou += '        data = data.copy()\n'
        zvrdy__fqou += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            zvrdy__fqou += '        data = data[:n_samples]\n'
        zvrdy__fqou += '        return data\n'
        zvrdy__fqou += '    else:\n'
        zvrdy__fqou += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        zvrdy__fqou += '        permutation = np.arange(dim0_global_size)\n'
        zvrdy__fqou += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            zvrdy__fqou += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            zvrdy__fqou += '        n_samples = dim0_global_size\n'
        zvrdy__fqou += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        zvrdy__fqou += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        zvrdy__fqou += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        zvrdy__fqou += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        zvrdy__fqou += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        zvrdy__fqou += '        return output\n'
    else:
        zvrdy__fqou += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            zvrdy__fqou += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            zvrdy__fqou += '    output = output[:local_n_samples]\n'
        zvrdy__fqou += '    return output\n'
    hmm__njtii = {}
    exec(zvrdy__fqou, {'np': np, 'bodo': bodo}, hmm__njtii)
    impl = hmm__njtii['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    jswmk__wwcw = np.empty(sendcounts_nulls.sum(), np.uint8)
    jjrc__wejp = 0
    qjxp__qekmc = 0
    for xkp__rie in range(len(sendcounts)):
        prk__vcg = sendcounts[xkp__rie]
        zqt__eml = sendcounts_nulls[xkp__rie]
        dzing__ocblt = jswmk__wwcw[jjrc__wejp:jjrc__wejp + zqt__eml]
        for agxyr__phzqf in range(prk__vcg):
            set_bit_to_arr(dzing__ocblt, agxyr__phzqf, get_bit_bitmap(
                null_bitmap_ptr, qjxp__qekmc))
            qjxp__qekmc += 1
        jjrc__wejp += zqt__eml
    return jswmk__wwcw


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    hemon__ynns = MPI.COMM_WORLD
    data = hemon__ynns.bcast(data, root)
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
    ztf__qwogz = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    xupl__ncni = (0,) * ztf__qwogz

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        fao__zva = np.ascontiguousarray(data)
        kybtu__ucrp = data.ctypes
        avnw__sugs = xupl__ncni
        if rank == MPI_ROOT:
            avnw__sugs = fao__zva.shape
        avnw__sugs = bcast_tuple(avnw__sugs)
        ztwp__tlqlm = get_tuple_prod(avnw__sugs[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            avnw__sugs[0])
        send_counts *= ztwp__tlqlm
        wap__xkqs = send_counts[rank]
        plt__qamx = np.empty(wap__xkqs, dtype)
        mdy__bpr = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(kybtu__ucrp, send_counts.ctypes, mdy__bpr.ctypes,
            plt__qamx.ctypes, np.int32(wap__xkqs), np.int32(typ_val))
        return plt__qamx.reshape((-1,) + avnw__sugs[1:])
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
        dqb__vqao = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], dqb__vqao)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        jurn__ojs = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=jurn__ojs)
        bduyd__zge = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(bduyd__zge)
        return pd.Index(arr, name=jurn__ojs)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        jurn__ojs = _get_name_value_for_type(dtype.name_typ)
        ynq__otvo = tuple(_get_name_value_for_type(t) for t in dtype.names_typ)
        dbr__wyja = tuple(get_value_for_type(t) for t in dtype.array_types)
        dbr__wyja = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in dbr__wyja)
        val = pd.MultiIndex.from_arrays(dbr__wyja, names=ynq__otvo)
        val.name = jurn__ojs
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        jurn__ojs = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=jurn__ojs)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dbr__wyja = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({jurn__ojs: arr for jurn__ojs, arr in zip(dtype
            .columns, dbr__wyja)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        bduyd__zge = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(bduyd__zge[0],
            bduyd__zge[0])])
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
        iacm__mnunw = np.int32(numba_to_c_type(types.int32))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            nwzw__wcp = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            nwzw__wcp = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zvrdy__fqou = f"""def impl(
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
            recv_arr = {nwzw__wcp}(n_loc, n_loc_char)

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
        hmm__njtii = dict()
        exec(zvrdy__fqou, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            iacm__mnunw, 'char_typ_enum': aabkr__thmut,
            'decode_if_dict_array': decode_if_dict_array}, hmm__njtii)
        impl = hmm__njtii['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        iacm__mnunw = np.int32(numba_to_c_type(types.int32))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            ikc__lde = bodo.libs.array_item_arr_ext.get_offsets(data)
            ylwz__olty = bodo.libs.array_item_arr_ext.get_data(data)
            ylwz__olty = ylwz__olty[:ikc__lde[-1]]
            gkorw__dabo = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            lpcd__rcm = bcast_scalar(len(data))
            sawr__jch = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                sawr__jch[i] = ikc__lde[i + 1] - ikc__lde[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                lpcd__rcm)
            mdy__bpr = bodo.ir.join.calc_disp(send_counts)
            ree__wmgr = np.empty(n_pes, np.int32)
            if rank == 0:
                vtwhc__vwr = 0
                for i in range(n_pes):
                    xusc__ifc = 0
                    for dooce__lwkv in range(send_counts[i]):
                        xusc__ifc += sawr__jch[vtwhc__vwr]
                        vtwhc__vwr += 1
                    ree__wmgr[i] = xusc__ifc
            bcast(ree__wmgr)
            wyjrs__lcb = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                wyjrs__lcb[i] = send_counts[i] + 7 >> 3
            cvbo__ltjrf = bodo.ir.join.calc_disp(wyjrs__lcb)
            wap__xkqs = send_counts[rank]
            tcxsf__uvopw = np.empty(wap__xkqs + 1, np_offset_type)
            hsmfk__cyd = bodo.libs.distributed_api.scatterv_impl(ylwz__olty,
                ree__wmgr)
            wvh__khcv = wap__xkqs + 7 >> 3
            ibtut__bmwc = np.empty(wvh__khcv, np.uint8)
            cvf__tio = np.empty(wap__xkqs, np.uint32)
            c_scatterv(sawr__jch.ctypes, send_counts.ctypes, mdy__bpr.
                ctypes, cvf__tio.ctypes, np.int32(wap__xkqs), iacm__mnunw)
            convert_len_arr_to_offset(cvf__tio.ctypes, tcxsf__uvopw.ctypes,
                wap__xkqs)
            coc__efg = get_scatter_null_bytes_buff(gkorw__dabo.ctypes,
                send_counts, wyjrs__lcb)
            c_scatterv(coc__efg.ctypes, wyjrs__lcb.ctypes, cvbo__ltjrf.
                ctypes, ibtut__bmwc.ctypes, np.int32(wvh__khcv), aabkr__thmut)
            return bodo.libs.array_item_arr_ext.init_array_item_array(wap__xkqs
                , hsmfk__cyd, tcxsf__uvopw, ibtut__bmwc)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            auvgf__vjo = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            auvgf__vjo = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            auvgf__vjo = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            auvgf__vjo = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            fao__zva = data._data
            rehzw__vqa = data._null_bitmap
            gaksg__ecv = len(fao__zva)
            wihm__kqbrg = _scatterv_np(fao__zva, send_counts)
            lpcd__rcm = bcast_scalar(gaksg__ecv)
            fti__dyfqv = len(wihm__kqbrg) + 7 >> 3
            lri__eohg = np.empty(fti__dyfqv, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                lpcd__rcm)
            wyjrs__lcb = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                wyjrs__lcb[i] = send_counts[i] + 7 >> 3
            cvbo__ltjrf = bodo.ir.join.calc_disp(wyjrs__lcb)
            coc__efg = get_scatter_null_bytes_buff(rehzw__vqa.ctypes,
                send_counts, wyjrs__lcb)
            c_scatterv(coc__efg.ctypes, wyjrs__lcb.ctypes, cvbo__ltjrf.
                ctypes, lri__eohg.ctypes, np.int32(fti__dyfqv), aabkr__thmut)
            return auvgf__vjo(wihm__kqbrg, lri__eohg)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            zxcho__ionno = bodo.libs.distributed_api.scatterv_impl(data.
                _left, send_counts)
            qgib__fyaaw = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(zxcho__ionno,
                qgib__fyaaw)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            sxcs__atj = data._start
            wqeho__cahv = data._stop
            lvfu__tjv = data._step
            jurn__ojs = data._name
            jurn__ojs = bcast_scalar(jurn__ojs)
            sxcs__atj = bcast_scalar(sxcs__atj)
            wqeho__cahv = bcast_scalar(wqeho__cahv)
            lvfu__tjv = bcast_scalar(lvfu__tjv)
            pwug__rro = bodo.libs.array_kernels.calc_nitems(sxcs__atj,
                wqeho__cahv, lvfu__tjv)
            chunk_start = bodo.libs.distributed_api.get_start(pwug__rro,
                n_pes, rank)
            yei__izk = bodo.libs.distributed_api.get_node_portion(pwug__rro,
                n_pes, rank)
            bwg__aukq = sxcs__atj + lvfu__tjv * chunk_start
            wjs__fprc = sxcs__atj + lvfu__tjv * (chunk_start + yei__izk)
            wjs__fprc = min(wjs__fprc, wqeho__cahv)
            return bodo.hiframes.pd_index_ext.init_range_index(bwg__aukq,
                wjs__fprc, lvfu__tjv, jurn__ojs)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        bji__ymj = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            fao__zva = data._data
            jurn__ojs = data._name
            jurn__ojs = bcast_scalar(jurn__ojs)
            arr = bodo.libs.distributed_api.scatterv_impl(fao__zva, send_counts
                )
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                jurn__ojs, bji__ymj)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            fao__zva = data._data
            jurn__ojs = data._name
            jurn__ojs = bcast_scalar(jurn__ojs)
            arr = bodo.libs.distributed_api.scatterv_impl(fao__zva, send_counts
                )
            return bodo.utils.conversion.index_from_array(arr, jurn__ojs)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            ohnu__tdr = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            jurn__ojs = bcast_scalar(data._name)
            ynq__otvo = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(ohnu__tdr,
                ynq__otvo, jurn__ojs)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            jurn__ojs = bodo.hiframes.pd_series_ext.get_series_name(data)
            sdga__cpv = bcast_scalar(jurn__ojs)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            brme__uhg = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                brme__uhg, sdga__cpv)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wkn__har = len(data.columns)
        afm__qyrrc = ', '.join('g_data_{}'.format(i) for i in range(wkn__har))
        dgvm__mste = ColNamesMetaType(data.columns)
        zvrdy__fqou = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(wkn__har):
            zvrdy__fqou += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            zvrdy__fqou += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        zvrdy__fqou += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zvrdy__fqou += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        zvrdy__fqou += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({afm__qyrrc},), g_index, __col_name_meta_scaterv_impl)
"""
        hmm__njtii = {}
        exec(zvrdy__fqou, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            dgvm__mste}, hmm__njtii)
        zxqmy__sbpbu = hmm__njtii['impl_df']
        return zxqmy__sbpbu
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            evpsj__rdry = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                evpsj__rdry, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        zvrdy__fqou = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        zvrdy__fqou += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        hmm__njtii = {}
        exec(zvrdy__fqou, {'bodo': bodo}, hmm__njtii)
        xzx__xcj = hmm__njtii['impl_tuple']
        return xzx__xcj
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
        lqnyj__usg = np.int32(numba_to_c_type(offset_type))
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            wap__xkqs = len(data)
            txai__jag = num_total_chars(data)
            assert wap__xkqs < INT_MAX
            assert txai__jag < INT_MAX
            lgl__wmys = get_offset_ptr(data)
            kybtu__ucrp = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            zqt__eml = wap__xkqs + 7 >> 3
            c_bcast(lgl__wmys, np.int32(wap__xkqs + 1), lqnyj__usg, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(kybtu__ucrp, np.int32(txai__jag), aabkr__thmut, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(zqt__eml), aabkr__thmut, np.
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
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                xwdaq__dgo = 0
                rhtl__qxdq = np.empty(0, np.uint8).ctypes
            else:
                rhtl__qxdq, xwdaq__dgo = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            xwdaq__dgo = bodo.libs.distributed_api.bcast_scalar(xwdaq__dgo,
                root)
            if rank != root:
                qdl__bvwfp = np.empty(xwdaq__dgo + 1, np.uint8)
                qdl__bvwfp[xwdaq__dgo] = 0
                rhtl__qxdq = qdl__bvwfp.ctypes
            c_bcast(rhtl__qxdq, np.int32(xwdaq__dgo), aabkr__thmut, np.
                array([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(rhtl__qxdq, xwdaq__dgo)
        return impl_str
    typ_val = numba_to_c_type(val)
    zvrdy__fqou = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    hmm__njtii = {}
    exec(zvrdy__fqou, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, hmm__njtii)
    cta__lnfln = hmm__njtii['bcast_scalar_impl']
    return cta__lnfln


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    hyniv__ejhu = len(val)
    zvrdy__fqou = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    zvrdy__fqou += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(hyniv__ejhu)
        ), ',' if hyniv__ejhu else '')
    hmm__njtii = {}
    exec(zvrdy__fqou, {'bcast_scalar': bcast_scalar}, hmm__njtii)
    ipz__tnzl = hmm__njtii['bcast_tuple_impl']
    return ipz__tnzl


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            wap__xkqs = bcast_scalar(len(arr), root)
            yzmo__zpa = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(wap__xkqs, yzmo__zpa)
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
            bwg__aukq = max(arr_start, slice_index.start) - arr_start
            wjs__fprc = max(slice_index.stop - arr_start, 0)
            return slice(bwg__aukq, wjs__fprc)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            sxcs__atj = slice_index.start
            lvfu__tjv = slice_index.step
            xzveo__ofge = (0 if lvfu__tjv == 1 or sxcs__atj > arr_start else
                abs(lvfu__tjv - arr_start % lvfu__tjv) % lvfu__tjv)
            bwg__aukq = max(arr_start, slice_index.start
                ) - arr_start + xzveo__ofge
            wjs__fprc = max(slice_index.stop - arr_start, 0)
            return slice(bwg__aukq, wjs__fprc, lvfu__tjv)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        maq__nvf = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[maq__nvf])
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
        ocpx__hriup = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        aabkr__thmut = np.int32(numba_to_c_type(types.uint8))
        xjmq__tlbn = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            fki__tuwuj = np.int32(10)
            tag = np.int32(11)
            egfvh__hcd = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                soa__jcor = arr._data
                hykyt__tnl = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    soa__jcor, ind)
                dyzhz__pzrm = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    soa__jcor, ind + 1)
                length = dyzhz__pzrm - hykyt__tnl
                encl__epve = soa__jcor[ind]
                egfvh__hcd[0] = length
                isend(egfvh__hcd, np.int32(1), root, fki__tuwuj, True)
                isend(encl__epve, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(xjmq__tlbn
                , ocpx__hriup, 0, 1)
            xtwu__xxp = 0
            if rank == root:
                xtwu__xxp = recv(np.int64, ANY_SOURCE, fki__tuwuj)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    xjmq__tlbn, ocpx__hriup, xtwu__xxp, 1)
                kybtu__ucrp = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(kybtu__ucrp, np.int32(xtwu__xxp), aabkr__thmut,
                    ANY_SOURCE, tag)
            dummy_use(egfvh__hcd)
            xtwu__xxp = bcast_scalar(xtwu__xxp)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    xjmq__tlbn, ocpx__hriup, xtwu__xxp, 1)
            kybtu__ucrp = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(kybtu__ucrp, np.int32(xtwu__xxp), aabkr__thmut, np.
                array([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, xtwu__xxp)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        jor__pqjqg = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, jor__pqjqg)
            if arr_start <= ind < arr_start + len(arr):
                evpsj__rdry = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = evpsj__rdry[ind - arr_start]
                send_arr = np.full(1, data, jor__pqjqg)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = jor__pqjqg(-1)
            if rank == root:
                val = recv(jor__pqjqg, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            uvzvc__jjxvx = arr.dtype.categories[max(val, 0)]
            return uvzvc__jjxvx
        return cat_getitem_impl
    xap__zsy = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, xap__zsy)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, xap__zsy)[0]
        if rank == root:
            val = recv(xap__zsy, ANY_SOURCE, tag)
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
    sfsaz__xhmak = get_type_enum(out_data)
    assert typ_enum == sfsaz__xhmak
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
    zvrdy__fqou = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        zvrdy__fqou += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    zvrdy__fqou += '  return\n'
    hmm__njtii = {}
    exec(zvrdy__fqou, {'alltoallv': alltoallv}, hmm__njtii)
    ssho__eyjmo = hmm__njtii['f']
    return ssho__eyjmo


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    sxcs__atj = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return sxcs__atj, count


@numba.njit
def get_start(total_size, pes, rank):
    rva__spji = total_size % pes
    wle__tncb = (total_size - rva__spji) // pes
    return rank * wle__tncb + min(rank, rva__spji)


@numba.njit
def get_end(total_size, pes, rank):
    rva__spji = total_size % pes
    wle__tncb = (total_size - rva__spji) // pes
    return (rank + 1) * wle__tncb + min(rank + 1, rva__spji)


@numba.njit
def get_node_portion(total_size, pes, rank):
    rva__spji = total_size % pes
    wle__tncb = (total_size - rva__spji) // pes
    if rank < rva__spji:
        return wle__tncb + 1
    else:
        return wle__tncb


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    ylq__uqbxu = in_arr.dtype(0)
    ajxw__iku = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        xusc__ifc = ylq__uqbxu
        for imru__jic in np.nditer(in_arr):
            xusc__ifc += imru__jic.item()
        ykwmy__iseo = dist_exscan(xusc__ifc, ajxw__iku)
        for i in range(in_arr.size):
            ykwmy__iseo += in_arr[i]
            out_arr[i] = ykwmy__iseo
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    mom__xcfjg = in_arr.dtype(1)
    ajxw__iku = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        xusc__ifc = mom__xcfjg
        for imru__jic in np.nditer(in_arr):
            xusc__ifc *= imru__jic.item()
        ykwmy__iseo = dist_exscan(xusc__ifc, ajxw__iku)
        if get_rank() == 0:
            ykwmy__iseo = mom__xcfjg
        for i in range(in_arr.size):
            ykwmy__iseo *= in_arr[i]
            out_arr[i] = ykwmy__iseo
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        mom__xcfjg = np.finfo(in_arr.dtype(1).dtype).max
    else:
        mom__xcfjg = np.iinfo(in_arr.dtype(1).dtype).max
    ajxw__iku = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        xusc__ifc = mom__xcfjg
        for imru__jic in np.nditer(in_arr):
            xusc__ifc = min(xusc__ifc, imru__jic.item())
        ykwmy__iseo = dist_exscan(xusc__ifc, ajxw__iku)
        if get_rank() == 0:
            ykwmy__iseo = mom__xcfjg
        for i in range(in_arr.size):
            ykwmy__iseo = min(ykwmy__iseo, in_arr[i])
            out_arr[i] = ykwmy__iseo
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        mom__xcfjg = np.finfo(in_arr.dtype(1).dtype).min
    else:
        mom__xcfjg = np.iinfo(in_arr.dtype(1).dtype).min
    mom__xcfjg = in_arr.dtype(1)
    ajxw__iku = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        xusc__ifc = mom__xcfjg
        for imru__jic in np.nditer(in_arr):
            xusc__ifc = max(xusc__ifc, imru__jic.item())
        ykwmy__iseo = dist_exscan(xusc__ifc, ajxw__iku)
        if get_rank() == 0:
            ykwmy__iseo = mom__xcfjg
        for i in range(in_arr.size):
            ykwmy__iseo = max(ykwmy__iseo, in_arr[i])
            out_arr[i] = ykwmy__iseo
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    edtb__yookp = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), edtb__yookp)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lvrig__fhvef = args[0]
    if equiv_set.has_shape(lvrig__fhvef):
        return ArrayAnalysis.AnalyzeResult(shape=lvrig__fhvef, pre=[])
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
    srn__cbij = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for i,
        ueuq__mcc in enumerate(args) if is_array_typ(ueuq__mcc) or
        isinstance(ueuq__mcc, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    zvrdy__fqou = f"""def impl(*args):
    if {srn__cbij} or bodo.get_rank() == 0:
        print(*args)"""
    hmm__njtii = {}
    exec(zvrdy__fqou, globals(), hmm__njtii)
    impl = hmm__njtii['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        ruedd__zkybb = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        zvrdy__fqou = 'def f(req, cond=True):\n'
        zvrdy__fqou += f'  return {ruedd__zkybb}\n'
        hmm__njtii = {}
        exec(zvrdy__fqou, {'_wait': _wait}, hmm__njtii)
        impl = hmm__njtii['f']
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
        rva__spji = 1
        for a in t:
            rva__spji *= a
        return rva__spji
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    pffa__lrqef = np.ascontiguousarray(in_arr)
    buyom__pat = get_tuple_prod(pffa__lrqef.shape[1:])
    nxqg__efud = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        pow__lxuw = np.array(dest_ranks, dtype=np.int32)
    else:
        pow__lxuw = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, pffa__lrqef.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * nxqg__efud, 
        dtype_size * buyom__pat, len(pow__lxuw), pow__lxuw.ctypes)
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
    kepz__kov = np.ascontiguousarray(rhs)
    tuxat__vdduv = get_tuple_prod(kepz__kov.shape[1:])
    hgdmy__emum = dtype_size * tuxat__vdduv
    permutation_array_index(lhs.ctypes, lhs_len, hgdmy__emum, kepz__kov.
        ctypes, kepz__kov.shape[0], p.ctypes, p_len, n_samples)
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
        zvrdy__fqou = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        hmm__njtii = {}
        exec(zvrdy__fqou, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, hmm__njtii)
        cta__lnfln = hmm__njtii['bcast_scalar_impl']
        return cta__lnfln
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wkn__har = len(data.columns)
        afm__qyrrc = ', '.join('g_data_{}'.format(i) for i in range(wkn__har))
        ndmhd__qsast = bodo.utils.transform.gen_const_tup(data.columns)
        ColNamesMetaType(('$_bodo_col2_',))
        zvrdy__fqou = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(wkn__har):
            zvrdy__fqou += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            zvrdy__fqou += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        zvrdy__fqou += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zvrdy__fqou += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        zvrdy__fqou += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(afm__qyrrc, ndmhd__qsast))
        hmm__njtii = {}
        exec(zvrdy__fqou, {'bodo': bodo}, hmm__njtii)
        zxqmy__sbpbu = hmm__njtii['impl_df']
        return zxqmy__sbpbu
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            sxcs__atj = data._start
            wqeho__cahv = data._stop
            lvfu__tjv = data._step
            jurn__ojs = data._name
            jurn__ojs = bcast_scalar(jurn__ojs, root)
            sxcs__atj = bcast_scalar(sxcs__atj, root)
            wqeho__cahv = bcast_scalar(wqeho__cahv, root)
            lvfu__tjv = bcast_scalar(lvfu__tjv, root)
            pwug__rro = bodo.libs.array_kernels.calc_nitems(sxcs__atj,
                wqeho__cahv, lvfu__tjv)
            chunk_start = bodo.libs.distributed_api.get_start(pwug__rro,
                n_pes, rank)
            yei__izk = bodo.libs.distributed_api.get_node_portion(pwug__rro,
                n_pes, rank)
            bwg__aukq = sxcs__atj + lvfu__tjv * chunk_start
            wjs__fprc = sxcs__atj + lvfu__tjv * (chunk_start + yei__izk)
            wjs__fprc = min(wjs__fprc, wqeho__cahv)
            return bodo.hiframes.pd_index_ext.init_range_index(bwg__aukq,
                wjs__fprc, lvfu__tjv, jurn__ojs)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            fao__zva = data._data
            jurn__ojs = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(fao__zva,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, jurn__ojs)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            jurn__ojs = bodo.hiframes.pd_series_ext.get_series_name(data)
            sdga__cpv = bodo.libs.distributed_api.bcast_comm_impl(jurn__ojs,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            brme__uhg = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                brme__uhg, sdga__cpv)
        return impl_series
    if isinstance(data, types.BaseTuple):
        zvrdy__fqou = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        zvrdy__fqou += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        hmm__njtii = {}
        exec(zvrdy__fqou, {'bcast_comm_impl': bcast_comm_impl}, hmm__njtii)
        xzx__xcj = hmm__njtii['impl_tuple']
        return xzx__xcj
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    ztf__qwogz = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    xupl__ncni = (0,) * ztf__qwogz

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        fao__zva = np.ascontiguousarray(data)
        kybtu__ucrp = data.ctypes
        avnw__sugs = xupl__ncni
        if rank == root:
            avnw__sugs = fao__zva.shape
        avnw__sugs = bcast_tuple(avnw__sugs, root)
        ztwp__tlqlm = get_tuple_prod(avnw__sugs[1:])
        send_counts = avnw__sugs[0] * ztwp__tlqlm
        plt__qamx = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(kybtu__ucrp, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(plt__qamx.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return plt__qamx.reshape((-1,) + avnw__sugs[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        hemon__ynns = MPI.COMM_WORLD
        hhx__snjdp = MPI.Get_processor_name()
        nxntk__ypjp = hemon__ynns.allgather(hhx__snjdp)
        node_ranks = defaultdict(list)
        for i, lomv__jzmw in enumerate(nxntk__ypjp):
            node_ranks[lomv__jzmw].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    hemon__ynns = MPI.COMM_WORLD
    ghvev__kete = hemon__ynns.Get_group()
    mrqx__dvig = ghvev__kete.Incl(comm_ranks)
    pcb__jqd = hemon__ynns.Create_group(mrqx__dvig)
    return pcb__jqd


def get_nodes_first_ranks():
    yiimq__nrco = get_host_ranks()
    return np.array([fpwrn__ufxd[0] for fpwrn__ufxd in yiimq__nrco.values()
        ], dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
