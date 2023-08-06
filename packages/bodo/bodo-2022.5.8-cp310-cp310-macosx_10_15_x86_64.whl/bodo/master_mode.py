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
        wyu__mvpgw = state
        eme__pjyou = inspect.getsourcelines(wyu__mvpgw)[0][0]
        assert eme__pjyou.startswith('@bodo.jit') or eme__pjyou.startswith(
            '@jit')
        stgv__rqm = eval(eme__pjyou[1:])
        self.dispatcher = stgv__rqm(wyu__mvpgw)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    hut__wjgv = MPI.COMM_WORLD
    while True:
        xlrxw__arkcq = hut__wjgv.bcast(None, root=MASTER_RANK)
        if xlrxw__arkcq[0] == 'exec':
            wyu__mvpgw = pickle.loads(xlrxw__arkcq[1])
            for muzi__mac, ccnnj__xsyzv in list(wyu__mvpgw.__globals__.items()
                ):
                if isinstance(ccnnj__xsyzv, MasterModeDispatcher):
                    wyu__mvpgw.__globals__[muzi__mac] = ccnnj__xsyzv.dispatcher
            if wyu__mvpgw.__module__ not in sys.modules:
                sys.modules[wyu__mvpgw.__module__] = pytypes.ModuleType(
                    wyu__mvpgw.__module__)
            eme__pjyou = inspect.getsourcelines(wyu__mvpgw)[0][0]
            assert eme__pjyou.startswith('@bodo.jit') or eme__pjyou.startswith(
                '@jit')
            stgv__rqm = eval(eme__pjyou[1:])
            func = stgv__rqm(wyu__mvpgw)
            etrnb__xbzvk = xlrxw__arkcq[2]
            edjxe__wgje = xlrxw__arkcq[3]
            tvoda__klo = []
            for cvni__osim in etrnb__xbzvk:
                if cvni__osim == 'scatter':
                    tvoda__klo.append(bodo.scatterv(None))
                elif cvni__osim == 'bcast':
                    tvoda__klo.append(hut__wjgv.bcast(None, root=MASTER_RANK))
            cqac__emivs = {}
            for argname, cvni__osim in edjxe__wgje.items():
                if cvni__osim == 'scatter':
                    cqac__emivs[argname] = bodo.scatterv(None)
                elif cvni__osim == 'bcast':
                    cqac__emivs[argname] = hut__wjgv.bcast(None, root=
                        MASTER_RANK)
            fynvl__iqav = func(*tvoda__klo, **cqac__emivs)
            if fynvl__iqav is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(fynvl__iqav)
            del (xlrxw__arkcq, wyu__mvpgw, func, stgv__rqm, etrnb__xbzvk,
                edjxe__wgje, tvoda__klo, cqac__emivs, fynvl__iqav)
            gc.collect()
        elif xlrxw__arkcq[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    hut__wjgv = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        etrnb__xbzvk = ['scatter' for tiu__ghh in range(len(args))]
        edjxe__wgje = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        dupnf__nwdk = func.py_func.__code__.co_varnames
        fyf__gzrd = func.targetoptions

        def get_distribution(argname):
            if argname in fyf__gzrd.get('distributed', []
                ) or argname in fyf__gzrd.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        etrnb__xbzvk = [get_distribution(argname) for argname in
            dupnf__nwdk[:len(args)]]
        edjxe__wgje = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    itdx__qrc = pickle.dumps(func.py_func)
    hut__wjgv.bcast(['exec', itdx__qrc, etrnb__xbzvk, edjxe__wgje])
    tvoda__klo = []
    for scbge__jyo, cvni__osim in zip(args, etrnb__xbzvk):
        if cvni__osim == 'scatter':
            tvoda__klo.append(bodo.scatterv(scbge__jyo))
        elif cvni__osim == 'bcast':
            hut__wjgv.bcast(scbge__jyo)
            tvoda__klo.append(scbge__jyo)
    cqac__emivs = {}
    for argname, scbge__jyo in kwargs.items():
        cvni__osim = edjxe__wgje[argname]
        if cvni__osim == 'scatter':
            cqac__emivs[argname] = bodo.scatterv(scbge__jyo)
        elif cvni__osim == 'bcast':
            hut__wjgv.bcast(scbge__jyo)
            cqac__emivs[argname] = scbge__jyo
    zwm__kjp = []
    for muzi__mac, ccnnj__xsyzv in list(func.py_func.__globals__.items()):
        if isinstance(ccnnj__xsyzv, MasterModeDispatcher):
            zwm__kjp.append((func.py_func.__globals__, muzi__mac, func.
                py_func.__globals__[muzi__mac]))
            func.py_func.__globals__[muzi__mac] = ccnnj__xsyzv.dispatcher
    fynvl__iqav = func(*tvoda__klo, **cqac__emivs)
    for ctpqr__hht, muzi__mac, ccnnj__xsyzv in zwm__kjp:
        ctpqr__hht[muzi__mac] = ccnnj__xsyzv
    if fynvl__iqav is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        fynvl__iqav = bodo.gatherv(fynvl__iqav)
    return fynvl__iqav


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
