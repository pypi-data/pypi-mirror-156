"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils, types
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
import bodo.io
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
import bodo.utils
import bodo.utils.table_utils
import bodo.utils.typing
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
numba.core.config.DISABLE_PERFORMANCE_WARNINGS = 1
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        ibijn__nba = 'bodo' if distributed else 'bodo_seq'
        ibijn__nba = (ibijn__nba + '_inline' if inline_calls_pass else
            ibijn__nba)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, ibijn__nba
            )
        if inline_calls_pass:
            pm.add_pass_after(InlinePass, WithLifting)
        if udf_pipeline:
            pm.add_pass_after(ConvertCallsUDFPass, WithLifting)
        add_pass_before(pm, BodoUntypedPass, ReconstructSSA)
        replace_pass(pm, BodoTypeInference, NopythonTypeInference)
        remove_pass(pm, MakeFunctionToJitFunction)
        add_pass_before(pm, BodoSeriesPass, PreParforPass)
        if distributed:
            pm.add_pass_after(BodoDistributedPass, ParforPass)
        else:
            pm.add_pass_after(LowerParforSeq, ParforPass)
            pm.add_pass_after(LowerBodoIRExtSeq, LowerParforSeq)
        add_pass_before(pm, BodoTableColumnDelPass, IRLegalization)
        pm.add_pass_after(BodoDumpDistDiagnosticsPass, DumpParforDiagnostics)
        pm.finalize()
        return [pm]


def add_pass_before(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for ibk__bmgcg, (vtg__itck, zvv__zbug) in enumerate(pm.passes):
        if vtg__itck == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(ibk__bmgcg, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for ibk__bmgcg, (vtg__itck, zvv__zbug) in enumerate(pm.passes):
        if vtg__itck == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[ibk__bmgcg] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for ibk__bmgcg, (vtg__itck, zvv__zbug) in enumerate(pm.passes):
        if vtg__itck == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(ibk__bmgcg)
    pm._finalized = False


@register_pass(mutates_CFG=True, analysis_only=False)
class InlinePass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        inline_calls(state.func_ir, state.locals)
        state.func_ir.blocks = ir_utils.simplify_CFG(state.func_ir.blocks)
        return True


def _convert_bodo_dispatcher_to_udf(rhs, func_ir):
    ikvw__mun = guard(get_definition, func_ir, rhs.func)
    if isinstance(ikvw__mun, (ir.Global, ir.FreeVar, ir.Const)):
        syz__nzn = ikvw__mun.value
    else:
        psm__ghfg = guard(find_callname, func_ir, rhs)
        if not (psm__ghfg and isinstance(psm__ghfg[0], str) and isinstance(
            psm__ghfg[1], str)):
            return
        func_name, func_mod = psm__ghfg
        try:
            import importlib
            www__stnog = importlib.import_module(func_mod)
            syz__nzn = getattr(www__stnog, func_name)
        except:
            return
    if isinstance(syz__nzn, CPUDispatcher) and issubclass(syz__nzn.
        _compiler.pipeline_class, BodoCompiler
        ) and syz__nzn._compiler.pipeline_class != BodoCompilerUDF:
        syz__nzn._compiler.pipeline_class = BodoCompilerUDF
        syz__nzn.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for qcjjh__okqxb in block.body:
                if is_call_assign(qcjjh__okqxb):
                    _convert_bodo_dispatcher_to_udf(qcjjh__okqxb.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        cqqme__pim = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        cqqme__pim.run()
        return True


def _update_definitions(func_ir, node_list):
    zzp__hxost = ir.Loc('', 0)
    oxqdq__yhb = ir.Block(ir.Scope(None, zzp__hxost), zzp__hxost)
    oxqdq__yhb.body = node_list
    build_definitions({(0): oxqdq__yhb}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill', 'mask', 'where'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query',
    'rolling', 'mask', 'where'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        dqtqp__nsfyr = 'overload_series_' + rhs.attr
        deyfo__ocjw = getattr(bodo.hiframes.series_impl, dqtqp__nsfyr)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        dqtqp__nsfyr = 'overload_dataframe_' + rhs.attr
        deyfo__ocjw = getattr(bodo.hiframes.dataframe_impl, dqtqp__nsfyr)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    hizd__mzgl = deyfo__ocjw(rhs_type)
    ralnc__xpv = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    lgwbs__okcvd = compile_func_single_block(hizd__mzgl, (rhs.value,), stmt
        .target, ralnc__xpv)
    _update_definitions(func_ir, lgwbs__okcvd)
    new_body += lgwbs__okcvd
    return True


def _inline_bodo_call(rhs, i, func_mod, func_name, pass_info, new_body,
    block, typingctx, targetctx, calltypes, work_list):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import replace_func, update_locs
    func_ir = pass_info.func_ir
    typemap = pass_info.typemap
    if isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        SeriesType) and func_name not in _series_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        if (func_name in bodo.hiframes.series_impl.explicit_binop_funcs or 
            func_name.startswith('r') and func_name[1:] in bodo.hiframes.
            series_impl.explicit_binop_funcs):
            return False
        rhs.args.insert(0, func_mod)
        njf__iht = tuple(typemap[gjtm__agt.name] for gjtm__agt in rhs.args)
        nat__blfdk = {ibijn__nba: typemap[gjtm__agt.name] for ibijn__nba,
            gjtm__agt in dict(rhs.kws).items()}
        hizd__mzgl = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*njf__iht, **nat__blfdk)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        njf__iht = tuple(typemap[gjtm__agt.name] for gjtm__agt in rhs.args)
        nat__blfdk = {ibijn__nba: typemap[gjtm__agt.name] for ibijn__nba,
            gjtm__agt in dict(rhs.kws).items()}
        hizd__mzgl = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*njf__iht, **nat__blfdk)
    else:
        return False
    cbu__yebg = replace_func(pass_info, hizd__mzgl, rhs.args, pysig=numba.
        core.utils.pysignature(hizd__mzgl), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    lmq__xuxi, zvv__zbug = inline_closure_call(func_ir, cbu__yebg.glbls,
        block, len(new_body), cbu__yebg.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=cbu__yebg.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for ddu__rnf in lmq__xuxi.values():
        ddu__rnf.loc = rhs.loc
        update_locs(ddu__rnf.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    hkiz__smezk = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = hkiz__smezk(func_ir, typemap)
    rbv__rzzia = func_ir.blocks
    work_list = list((gsam__acbl, rbv__rzzia[gsam__acbl]) for gsam__acbl in
        reversed(rbv__rzzia.keys()))
    while work_list:
        ser__sya, block = work_list.pop()
        new_body = []
        qcthz__ofr = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                psm__ghfg = guard(find_callname, func_ir, rhs, typemap)
                if psm__ghfg is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = psm__ghfg
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    qcthz__ofr = True
                    break
            new_body.append(stmt)
        if not qcthz__ofr:
            rbv__rzzia[ser__sya].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        tjxhh__saryn = DistributedPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes, state.
            return_type, state.metadata, state.flags)
        state.return_type = tjxhh__saryn.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dkjcw__qwkzv = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        jhku__noq = dkjcw__qwkzv.run()
        cpnt__gjwb = jhku__noq
        if cpnt__gjwb:
            cpnt__gjwb = dkjcw__qwkzv.run()
        if cpnt__gjwb:
            dkjcw__qwkzv.run()
        return jhku__noq


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        bsvy__zojw = 0
        hdyae__yfg = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            bsvy__zojw = int(os.environ[hdyae__yfg])
        except:
            pass
        if bsvy__zojw > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(bsvy__zojw,
                state.metadata)
        return True


class BodoCompilerSeq(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False,
            inline_calls_pass=inline_all_calls)


class BodoCompilerUDF(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False, udf_pipeline=True)


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerParforSeq(FunctionPass):
    _name = 'bodo_lower_parfor_seq_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bodo.transforms.distributed_pass.lower_parfor_sequential(state.
            typingctx, state.func_ir, state.typemap, state.calltypes, state
            .metadata)
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerBodoIRExtSeq(FunctionPass):
    _name = 'bodo_lower_ir_ext_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        from bodo.transforms.distributed_pass import distributed_run_extensions
        from bodo.transforms.table_column_del_pass import remove_dead_table_columns
        from bodo.utils.transform import compile_func_single_block
        from bodo.utils.typing import decode_if_dict_array, to_str_arr_if_dict_array
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        ralnc__xpv = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, ralnc__xpv)
        for block in state.func_ir.blocks.values():
            new_body = []
            for qcjjh__okqxb in block.body:
                if type(qcjjh__okqxb) in distributed_run_extensions:
                    pfbbl__dhra = distributed_run_extensions[type(qcjjh__okqxb)
                        ]
                    ieddk__huxhy = pfbbl__dhra(qcjjh__okqxb, None, state.
                        typemap, state.calltypes, state.typingctx, state.
                        targetctx)
                    new_body += ieddk__huxhy
                elif is_call_assign(qcjjh__okqxb):
                    rhs = qcjjh__okqxb.value
                    psm__ghfg = guard(find_callname, state.func_ir, rhs)
                    if psm__ghfg == ('gatherv', 'bodo') or psm__ghfg == (
                        'allgatherv', 'bodo'):
                        sutzo__ijpxp = state.typemap[qcjjh__okqxb.target.name]
                        fce__umay = state.typemap[rhs.args[0].name]
                        if isinstance(fce__umay, types.Array) and isinstance(
                            sutzo__ijpxp, types.Array):
                            uqp__iho = fce__umay.copy(readonly=False)
                            pxhw__jgx = sutzo__ijpxp.copy(readonly=False)
                            if uqp__iho == pxhw__jgx:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), qcjjh__okqxb.target, ralnc__xpv)
                                continue
                        if (sutzo__ijpxp != fce__umay and 
                            to_str_arr_if_dict_array(sutzo__ijpxp) ==
                            to_str_arr_if_dict_array(fce__umay)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), qcjjh__okqxb.target,
                                ralnc__xpv, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            qcjjh__okqxb.value = rhs.args[0]
                    new_body.append(qcjjh__okqxb)
                else:
                    new_body.append(qcjjh__okqxb)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        ifnpm__daj = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return ifnpm__daj.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    zipo__qrex = set()
    while work_list:
        ser__sya, block = work_list.pop()
        zipo__qrex.add(ser__sya)
        for i, decfj__dgnva in enumerate(block.body):
            if isinstance(decfj__dgnva, ir.Assign):
                kvmu__vrmz = decfj__dgnva.value
                if isinstance(kvmu__vrmz, ir.Expr) and kvmu__vrmz.op == 'call':
                    ikvw__mun = guard(get_definition, func_ir, kvmu__vrmz.func)
                    if isinstance(ikvw__mun, (ir.Global, ir.FreeVar)
                        ) and isinstance(ikvw__mun.value, CPUDispatcher
                        ) and issubclass(ikvw__mun.value._compiler.
                        pipeline_class, BodoCompiler):
                        qwmt__ehllj = ikvw__mun.value.py_func
                        arg_types = None
                        if typingctx:
                            gqz__hva = dict(kvmu__vrmz.kws)
                            hwpuz__svwe = tuple(typemap[gjtm__agt.name] for
                                gjtm__agt in kvmu__vrmz.args)
                            xkxib__pimm = {roe__cgo: typemap[gjtm__agt.name
                                ] for roe__cgo, gjtm__agt in gqz__hva.items()}
                            zvv__zbug, arg_types = (ikvw__mun.value.
                                fold_argument_types(hwpuz__svwe, xkxib__pimm))
                        zvv__zbug, dtzis__ounpw = inline_closure_call(func_ir,
                            qwmt__ehllj.__globals__, block, i, qwmt__ehllj,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((dtzis__ounpw[roe__cgo].name,
                            gjtm__agt) for roe__cgo, gjtm__agt in ikvw__mun
                            .value.locals.items() if roe__cgo in dtzis__ounpw)
                        break
    return zipo__qrex


def udf_jit(signature_or_function=None, **options):
    tdc__zpca = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=tdc__zpca,
        pipeline_class=bodo.compiler.BodoCompilerUDF, **options)


def is_udf_call(func_type):
    return isinstance(func_type, numba.core.types.Dispatcher
        ) and func_type.dispatcher._compiler.pipeline_class == BodoCompilerUDF


def is_user_dispatcher(func_type):
    return isinstance(func_type, numba.core.types.functions.ObjModeDispatcher
        ) or isinstance(func_type, numba.core.types.Dispatcher) and issubclass(
        func_type.dispatcher._compiler.pipeline_class, BodoCompiler)


@register_pass(mutates_CFG=False, analysis_only=True)
class DummyCR(FunctionPass):
    _name = 'bodo_dummy_cr'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        state.cr = (state.func_ir, state.typemap, state.calltypes, state.
            return_type)
        return True


def remove_passes_after(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for ibk__bmgcg, (vtg__itck, zvv__zbug) in enumerate(pm.passes):
        if vtg__itck == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:ibk__bmgcg + 1]
    pm._finalized = False


class TyperCompiler(BodoCompiler):

    def define_pipelines(self):
        [pm] = self._create_bodo_pipeline()
        remove_passes_after(pm, InlineOverloads)
        pm.add_pass_after(DummyCR, InlineOverloads)
        pm.finalize()
        return [pm]


def get_func_type_info(func, arg_types, kw_types):
    typingctx = numba.core.registry.cpu_target.typing_context
    targetctx = numba.core.registry.cpu_target.target_context
    vxivu__kip = None
    wjxcj__kxsw = None
    _locals = {}
    nsf__zaf = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(nsf__zaf, arg_types,
        kw_types)
    pyf__zfjsw = numba.core.compiler.Flags()
    fxzbr__gxsa = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    jzk__uolg = {'nopython': True, 'boundscheck': False, 'parallel':
        fxzbr__gxsa}
    numba.core.registry.cpu_target.options.parse_as_flags(pyf__zfjsw, jzk__uolg
        )
    wfy__yrfim = TyperCompiler(typingctx, targetctx, vxivu__kip, args,
        wjxcj__kxsw, pyf__zfjsw, _locals)
    return wfy__yrfim.compile_extra(func)
