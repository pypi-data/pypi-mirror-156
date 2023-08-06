"""Support distributed deep learning with Horovod
"""
import time
import numba
import numpy as np
from mpi4py import MPI
import bodo
from bodo.libs.distributed_api import create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks
dl_status = None


def assert_dl_initialized():
    assert dl_status is not None, 'Horovod has not been initialized. Call bodo.dl.start() first'


class DLStatus(object):

    def __init__(self, framework, gpu_ranks):
        self.framework = framework
        self.gpu_ranks = gpu_ranks


def get_num_gpus(framework):
    if framework == 'torch':
        import torch
        return torch.cuda.device_count()
    elif framework == 'tensorflow':
        import tensorflow as tf
        return len(tf.config.experimental.list_physical_devices('GPU'))
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))


def get_gpu_ranks(framework):
    avdy__mnw = MPI.COMM_WORLD
    sqq__pkij = avdy__mnw.Get_rank()
    dsj__fnoa = get_host_ranks()
    ejyrb__htuda = get_nodes_first_ranks()
    if sqq__pkij in ejyrb__htuda:
        try:
            tgvfv__ilk = get_num_gpus(framework)
        except Exception as smetl__ydx:
            tgvfv__ilk = smetl__ydx
        dsz__hxg = create_subcomm_mpi4py(ejyrb__htuda)
        eiwu__zma = dsz__hxg.gather(tgvfv__ilk)
        if sqq__pkij == 0:
            gpu_ranks = []
            whuf__mgkzk = None
            for auiu__izs, uczc__jppvd in enumerate(dsj__fnoa.values()):
                ywy__gnxl = eiwu__zma[auiu__izs]
                if isinstance(ywy__gnxl, Exception):
                    whuf__mgkzk = ywy__gnxl
                    break
                if ywy__gnxl == 0:
                    continue
                ywtt__dlyi = len(uczc__jppvd) // ywy__gnxl
                for wrmw__zdxf, oiu__jnkl in enumerate(uczc__jppvd):
                    if wrmw__zdxf % ywtt__dlyi == 0:
                        zcz__rudif = wrmw__zdxf / ywtt__dlyi
                        if zcz__rudif < ywy__gnxl:
                            gpu_ranks.append(oiu__jnkl)
            if whuf__mgkzk:
                avdy__mnw.bcast(whuf__mgkzk)
                raise whuf__mgkzk
            else:
                avdy__mnw.bcast(gpu_ranks)
    if sqq__pkij != 0:
        gpu_ranks = avdy__mnw.bcast(None)
        if isinstance(gpu_ranks, Exception):
            smetl__ydx = gpu_ranks
            raise smetl__ydx
    return gpu_ranks


def is_cuda_available():
    assert_dl_initialized()
    return len(dl_status.gpu_ranks) > 0


def initialize_horovod(framework):
    global dl_status
    if dl_status is not None:
        assert dl_status.framework == framework, 'Attempted to initialize Horovod with different DL frameworks'
        return np.array(dl_status.gpu_ranks, dtype=np.int32)
    gpu_ranks = get_gpu_ranks(framework)
    if framework == 'torch':
        import horovod.torch as hvd
        import torch
        torch.set_num_threads(1)
    elif framework == 'tensorflow':
        import horovod.tensorflow as hvd
        import tensorflow as tf
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))
    qkx__jnm = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        dsz__hxg = MPI.COMM_WORLD.Split(color=0 if qkx__jnm in gpu_ranks else
            MPI.UNDEFINED, key=qkx__jnm)
        if dsz__hxg != MPI.COMM_NULL:
            hvd.init(comm=dsz__hxg)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                swq__gop = tf.config.experimental.list_physical_devices('GPU')
                for mfyq__fka in swq__gop:
                    tf.config.experimental.set_memory_growth(mfyq__fka, True)
                tf.config.experimental.set_visible_devices(swq__gop[hvd.
                    local_rank()], 'GPU')
    else:
        if qkx__jnm == 0:
            print('[BODO-DL]: No GPUs found in cluster. Using CPUs')
        hvd.init()
    dl_status = DLStatus(framework, np.array(gpu_ranks, dtype=np.int32))


@numba.njit
def start(framework):
    with numba.objmode:
        initialize_horovod(framework)


@numba.njit
def end():
    with numba.objmode:
        end_py()


def end_py():
    if is_cuda_available():
        vtq__ybfrg = 17
        avdy__mnw = MPI.COMM_WORLD
        gri__ldgai = MPI.Get_processor_name()
        pgcfv__isdpu = get_host_ranks()[gri__ldgai]
        assert_dl_initialized()
        if bodo.get_rank() == pgcfv__isdpu[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for sqq__pkij in pgcfv__isdpu[1:]:
                avdy__mnw.isend(1, dest=sqq__pkij, tag=vtq__ybfrg)
        else:
            while True:
                uobm__tlo = MPI.Status()
                oxf__kmj = avdy__mnw.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    uobm__tlo)
                if oxf__kmj:
                    assert uobm__tlo.source == pgcfv__isdpu[0]
                    assert uobm__tlo.tag == vtq__ybfrg
                    avdy__mnw.recv(source=0, tag=vtq__ybfrg)
                    break
                time.sleep(1.0)
    else:
        bodo.barrier()


def _prepare_data_get_gpu_ranks():
    assert_dl_initialized()
    return dl_status.gpu_ranks


@numba.njit
def prepare_data(data):
    with numba.objmode(gpu_ranks='int32[:]'):
        gpu_ranks = _prepare_data_get_gpu_ranks()
    if len(gpu_ranks) > 0:
        data = bodo.rebalance(data, dests=list(gpu_ranks), parallel=True)
    else:
        data = bodo.rebalance(data, parallel=True)
    return data
