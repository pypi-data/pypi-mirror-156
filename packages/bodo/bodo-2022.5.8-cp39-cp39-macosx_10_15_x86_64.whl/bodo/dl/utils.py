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
    ewzy__cph = MPI.COMM_WORLD
    cxja__err = ewzy__cph.Get_rank()
    duti__uqlu = get_host_ranks()
    eei__ujjh = get_nodes_first_ranks()
    if cxja__err in eei__ujjh:
        try:
            apd__uvtq = get_num_gpus(framework)
        except Exception as asq__gob:
            apd__uvtq = asq__gob
        zfdaq__nday = create_subcomm_mpi4py(eei__ujjh)
        izya__xnna = zfdaq__nday.gather(apd__uvtq)
        if cxja__err == 0:
            gpu_ranks = []
            qjx__adc = None
            for ybpyf__hmacf, ntqyd__xfj in enumerate(duti__uqlu.values()):
                tzn__ldjp = izya__xnna[ybpyf__hmacf]
                if isinstance(tzn__ldjp, Exception):
                    qjx__adc = tzn__ldjp
                    break
                if tzn__ldjp == 0:
                    continue
                mfxy__emau = len(ntqyd__xfj) // tzn__ldjp
                for zizn__szmyo, okorb__fbxo in enumerate(ntqyd__xfj):
                    if zizn__szmyo % mfxy__emau == 0:
                        fhjav__btuvl = zizn__szmyo / mfxy__emau
                        if fhjav__btuvl < tzn__ldjp:
                            gpu_ranks.append(okorb__fbxo)
            if qjx__adc:
                ewzy__cph.bcast(qjx__adc)
                raise qjx__adc
            else:
                ewzy__cph.bcast(gpu_ranks)
    if cxja__err != 0:
        gpu_ranks = ewzy__cph.bcast(None)
        if isinstance(gpu_ranks, Exception):
            asq__gob = gpu_ranks
            raise asq__gob
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
    qdxg__zdj = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        zfdaq__nday = MPI.COMM_WORLD.Split(color=0 if qdxg__zdj in
            gpu_ranks else MPI.UNDEFINED, key=qdxg__zdj)
        if zfdaq__nday != MPI.COMM_NULL:
            hvd.init(comm=zfdaq__nday)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                oesz__gdyec = tf.config.experimental.list_physical_devices(
                    'GPU')
                for vmcg__hmd in oesz__gdyec:
                    tf.config.experimental.set_memory_growth(vmcg__hmd, True)
                tf.config.experimental.set_visible_devices(oesz__gdyec[hvd.
                    local_rank()], 'GPU')
    else:
        if qdxg__zdj == 0:
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
        mrv__qaj = 17
        ewzy__cph = MPI.COMM_WORLD
        jnnc__iohb = MPI.Get_processor_name()
        kqilf__sniu = get_host_ranks()[jnnc__iohb]
        assert_dl_initialized()
        if bodo.get_rank() == kqilf__sniu[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for cxja__err in kqilf__sniu[1:]:
                ewzy__cph.isend(1, dest=cxja__err, tag=mrv__qaj)
        else:
            while True:
                hqa__gsybo = MPI.Status()
                uwhf__rgiw = ewzy__cph.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    hqa__gsybo)
                if uwhf__rgiw:
                    assert hqa__gsybo.source == kqilf__sniu[0]
                    assert hqa__gsybo.tag == mrv__qaj
                    ewzy__cph.recv(source=0, tag=mrv__qaj)
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
