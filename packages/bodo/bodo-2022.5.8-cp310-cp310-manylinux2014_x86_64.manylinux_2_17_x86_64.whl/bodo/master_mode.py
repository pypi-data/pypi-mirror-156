import gc
import inspect
import sys
import types as pytypes
import bodo
master_mode_on = False
MASTER_RANK = 0


class MasterModeDispatcher(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, *args, **kwargs):
        assert bodo.get_rank() == MASTER_RANK
        return master_wrapper(self.dispatcher, *args, **kwargs)

    def __getstate__(self):
        assert bodo.get_rank() == MASTER_RANK
        return self.dispatcher.py_func

    def __setstate__(self, state):
        assert bodo.get_rank() != MASTER_RANK
        bwl__zehbs = state
        gjitx__ccx = inspect.getsourcelines(bwl__zehbs)[0][0]
        assert gjitx__ccx.startswith('@bodo.jit') or gjitx__ccx.startswith(
            '@jit')
        qeqe__dsv = eval(gjitx__ccx[1:])
        self.dispatcher = qeqe__dsv(bwl__zehbs)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    uzul__mxjtj = MPI.COMM_WORLD
    while True:
        inj__mbvw = uzul__mxjtj.bcast(None, root=MASTER_RANK)
        if inj__mbvw[0] == 'exec':
            bwl__zehbs = pickle.loads(inj__mbvw[1])
            for oae__yql, qykg__cbw in list(bwl__zehbs.__globals__.items()):
                if isinstance(qykg__cbw, MasterModeDispatcher):
                    bwl__zehbs.__globals__[oae__yql] = qykg__cbw.dispatcher
            if bwl__zehbs.__module__ not in sys.modules:
                sys.modules[bwl__zehbs.__module__] = pytypes.ModuleType(
                    bwl__zehbs.__module__)
            gjitx__ccx = inspect.getsourcelines(bwl__zehbs)[0][0]
            assert gjitx__ccx.startswith('@bodo.jit') or gjitx__ccx.startswith(
                '@jit')
            qeqe__dsv = eval(gjitx__ccx[1:])
            func = qeqe__dsv(bwl__zehbs)
            cxqch__efxr = inj__mbvw[2]
            tikzq__wjoau = inj__mbvw[3]
            qjnxd__crg = []
            for ecbwp__xzlft in cxqch__efxr:
                if ecbwp__xzlft == 'scatter':
                    qjnxd__crg.append(bodo.scatterv(None))
                elif ecbwp__xzlft == 'bcast':
                    qjnxd__crg.append(uzul__mxjtj.bcast(None, root=MASTER_RANK)
                        )
            kdt__snsr = {}
            for argname, ecbwp__xzlft in tikzq__wjoau.items():
                if ecbwp__xzlft == 'scatter':
                    kdt__snsr[argname] = bodo.scatterv(None)
                elif ecbwp__xzlft == 'bcast':
                    kdt__snsr[argname] = uzul__mxjtj.bcast(None, root=
                        MASTER_RANK)
            naibv__wwdyo = func(*qjnxd__crg, **kdt__snsr)
            if naibv__wwdyo is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(naibv__wwdyo)
            del (inj__mbvw, bwl__zehbs, func, qeqe__dsv, cxqch__efxr,
                tikzq__wjoau, qjnxd__crg, kdt__snsr, naibv__wwdyo)
            gc.collect()
        elif inj__mbvw[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    uzul__mxjtj = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        cxqch__efxr = ['scatter' for mev__srtc in range(len(args))]
        tikzq__wjoau = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        jdzi__egm = func.py_func.__code__.co_varnames
        oor__zpnci = func.targetoptions

        def get_distribution(argname):
            if argname in oor__zpnci.get('distributed', []
                ) or argname in oor__zpnci.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        cxqch__efxr = [get_distribution(argname) for argname in jdzi__egm[:
            len(args)]]
        tikzq__wjoau = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    fywj__tya = pickle.dumps(func.py_func)
    uzul__mxjtj.bcast(['exec', fywj__tya, cxqch__efxr, tikzq__wjoau])
    qjnxd__crg = []
    for tavs__ffjci, ecbwp__xzlft in zip(args, cxqch__efxr):
        if ecbwp__xzlft == 'scatter':
            qjnxd__crg.append(bodo.scatterv(tavs__ffjci))
        elif ecbwp__xzlft == 'bcast':
            uzul__mxjtj.bcast(tavs__ffjci)
            qjnxd__crg.append(tavs__ffjci)
    kdt__snsr = {}
    for argname, tavs__ffjci in kwargs.items():
        ecbwp__xzlft = tikzq__wjoau[argname]
        if ecbwp__xzlft == 'scatter':
            kdt__snsr[argname] = bodo.scatterv(tavs__ffjci)
        elif ecbwp__xzlft == 'bcast':
            uzul__mxjtj.bcast(tavs__ffjci)
            kdt__snsr[argname] = tavs__ffjci
    diti__smz = []
    for oae__yql, qykg__cbw in list(func.py_func.__globals__.items()):
        if isinstance(qykg__cbw, MasterModeDispatcher):
            diti__smz.append((func.py_func.__globals__, oae__yql, func.
                py_func.__globals__[oae__yql]))
            func.py_func.__globals__[oae__yql] = qykg__cbw.dispatcher
    naibv__wwdyo = func(*qjnxd__crg, **kdt__snsr)
    for hae__puw, oae__yql, qykg__cbw in diti__smz:
        hae__puw[oae__yql] = qykg__cbw
    if naibv__wwdyo is not None and func.overloads[func.signatures[0]
        ].metadata['is_return_distributed']:
        naibv__wwdyo = bodo.gatherv(naibv__wwdyo)
    return naibv__wwdyo


def init_master_mode():
    if bodo.get_size() == 1:
        return
    global master_mode_on
    assert master_mode_on is False, 'init_master_mode can only be called once on each process'
    master_mode_on = True
    assert sys.version_info[:2] >= (3, 8
        ), 'Python 3.8+ required for master mode'
    from bodo import jit
    globals()['jit'] = jit
    import cloudpickle
    from mpi4py import MPI
    globals()['pickle'] = cloudpickle
    globals()['MPI'] = MPI

    def master_exit():
        MPI.COMM_WORLD.bcast(['exit'])
    if bodo.get_rank() == MASTER_RANK:
        import atexit
        atexit.register(master_exit)
    else:
        worker_loop()
