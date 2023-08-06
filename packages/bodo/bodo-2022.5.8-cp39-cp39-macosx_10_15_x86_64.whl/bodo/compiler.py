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
        sjs__hpj = 'bodo' if distributed else 'bodo_seq'
        sjs__hpj = sjs__hpj + '_inline' if inline_calls_pass else sjs__hpj
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, sjs__hpj)
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
    for czu__hjcj, (csww__muv, tsia__aipu) in enumerate(pm.passes):
        if csww__muv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(czu__hjcj, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for czu__hjcj, (csww__muv, tsia__aipu) in enumerate(pm.passes):
        if csww__muv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[czu__hjcj] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for czu__hjcj, (csww__muv, tsia__aipu) in enumerate(pm.passes):
        if csww__muv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(czu__hjcj)
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
    duw__hrfeq = guard(get_definition, func_ir, rhs.func)
    if isinstance(duw__hrfeq, (ir.Global, ir.FreeVar, ir.Const)):
        nyifu__doj = duw__hrfeq.value
    else:
        fjox__poyld = guard(find_callname, func_ir, rhs)
        if not (fjox__poyld and isinstance(fjox__poyld[0], str) and
            isinstance(fjox__poyld[1], str)):
            return
        func_name, func_mod = fjox__poyld
        try:
            import importlib
            hadv__zqlw = importlib.import_module(func_mod)
            nyifu__doj = getattr(hadv__zqlw, func_name)
        except:
            return
    if isinstance(nyifu__doj, CPUDispatcher) and issubclass(nyifu__doj.
        _compiler.pipeline_class, BodoCompiler
        ) and nyifu__doj._compiler.pipeline_class != BodoCompilerUDF:
        nyifu__doj._compiler.pipeline_class = BodoCompilerUDF
        nyifu__doj.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for dgli__kygnz in block.body:
                if is_call_assign(dgli__kygnz):
                    _convert_bodo_dispatcher_to_udf(dgli__kygnz.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        ngh__jgg = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        ngh__jgg.run()
        return True


def _update_definitions(func_ir, node_list):
    tzu__axiz = ir.Loc('', 0)
    okpv__uidjl = ir.Block(ir.Scope(None, tzu__axiz), tzu__axiz)
    okpv__uidjl.body = node_list
    build_definitions({(0): okpv__uidjl}, func_ir._definitions)


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
        cbih__kpiv = 'overload_series_' + rhs.attr
        eym__kkz = getattr(bodo.hiframes.series_impl, cbih__kpiv)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        cbih__kpiv = 'overload_dataframe_' + rhs.attr
        eym__kkz = getattr(bodo.hiframes.dataframe_impl, cbih__kpiv)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    jzjap__ppg = eym__kkz(rhs_type)
    tydwn__ohp = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    pmh__phte = compile_func_single_block(jzjap__ppg, (rhs.value,), stmt.
        target, tydwn__ohp)
    _update_definitions(func_ir, pmh__phte)
    new_body += pmh__phte
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
        dyo__jmrx = tuple(typemap[oano__ttoln.name] for oano__ttoln in rhs.args
            )
        sryto__sbtbu = {sjs__hpj: typemap[oano__ttoln.name] for sjs__hpj,
            oano__ttoln in dict(rhs.kws).items()}
        jzjap__ppg = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*dyo__jmrx, **sryto__sbtbu)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        dyo__jmrx = tuple(typemap[oano__ttoln.name] for oano__ttoln in rhs.args
            )
        sryto__sbtbu = {sjs__hpj: typemap[oano__ttoln.name] for sjs__hpj,
            oano__ttoln in dict(rhs.kws).items()}
        jzjap__ppg = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*dyo__jmrx, **sryto__sbtbu)
    else:
        return False
    luyrh__yiwag = replace_func(pass_info, jzjap__ppg, rhs.args, pysig=
        numba.core.utils.pysignature(jzjap__ppg), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    spc__bqju, tsia__aipu = inline_closure_call(func_ir, luyrh__yiwag.glbls,
        block, len(new_body), luyrh__yiwag.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=luyrh__yiwag.arg_types, typemap=
        typemap, calltypes=calltypes, work_list=work_list)
    for qotbp__gazh in spc__bqju.values():
        qotbp__gazh.loc = rhs.loc
        update_locs(qotbp__gazh.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    vlcs__zgvwq = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = vlcs__zgvwq(func_ir, typemap)
    kjuxe__bviob = func_ir.blocks
    work_list = list((kqr__qgqme, kjuxe__bviob[kqr__qgqme]) for kqr__qgqme in
        reversed(kjuxe__bviob.keys()))
    while work_list:
        xdnoa__ltin, block = work_list.pop()
        new_body = []
        wlyhl__eod = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                fjox__poyld = guard(find_callname, func_ir, rhs, typemap)
                if fjox__poyld is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = fjox__poyld
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    wlyhl__eod = True
                    break
            new_body.append(stmt)
        if not wlyhl__eod:
            kjuxe__bviob[xdnoa__ltin].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        bimvd__lyvl = DistributedPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = bimvd__lyvl.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dbrbw__epvka = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        fstws__ekxvp = dbrbw__epvka.run()
        awcrt__vmcre = fstws__ekxvp
        if awcrt__vmcre:
            awcrt__vmcre = dbrbw__epvka.run()
        if awcrt__vmcre:
            dbrbw__epvka.run()
        return fstws__ekxvp


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        vgz__hyp = 0
        lpf__qaiyb = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            vgz__hyp = int(os.environ[lpf__qaiyb])
        except:
            pass
        if vgz__hyp > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(vgz__hyp, state.
                metadata)
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
        tydwn__ohp = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, tydwn__ohp)
        for block in state.func_ir.blocks.values():
            new_body = []
            for dgli__kygnz in block.body:
                if type(dgli__kygnz) in distributed_run_extensions:
                    fkw__vyc = distributed_run_extensions[type(dgli__kygnz)]
                    xkwax__uud = fkw__vyc(dgli__kygnz, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += xkwax__uud
                elif is_call_assign(dgli__kygnz):
                    rhs = dgli__kygnz.value
                    fjox__poyld = guard(find_callname, state.func_ir, rhs)
                    if fjox__poyld == ('gatherv', 'bodo') or fjox__poyld == (
                        'allgatherv', 'bodo'):
                        jaoex__ppxjr = state.typemap[dgli__kygnz.target.name]
                        aimr__nsu = state.typemap[rhs.args[0].name]
                        if isinstance(aimr__nsu, types.Array) and isinstance(
                            jaoex__ppxjr, types.Array):
                            inmui__fptu = aimr__nsu.copy(readonly=False)
                            wrqgu__hjj = jaoex__ppxjr.copy(readonly=False)
                            if inmui__fptu == wrqgu__hjj:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), dgli__kygnz.target, tydwn__ohp)
                                continue
                        if (jaoex__ppxjr != aimr__nsu and 
                            to_str_arr_if_dict_array(jaoex__ppxjr) ==
                            to_str_arr_if_dict_array(aimr__nsu)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), dgli__kygnz.target,
                                tydwn__ohp, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            dgli__kygnz.value = rhs.args[0]
                    new_body.append(dgli__kygnz)
                else:
                    new_body.append(dgli__kygnz)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        xxtf__apwgd = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return xxtf__apwgd.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    whlx__thlh = set()
    while work_list:
        xdnoa__ltin, block = work_list.pop()
        whlx__thlh.add(xdnoa__ltin)
        for i, usu__fyohm in enumerate(block.body):
            if isinstance(usu__fyohm, ir.Assign):
                unse__xwu = usu__fyohm.value
                if isinstance(unse__xwu, ir.Expr) and unse__xwu.op == 'call':
                    duw__hrfeq = guard(get_definition, func_ir, unse__xwu.func)
                    if isinstance(duw__hrfeq, (ir.Global, ir.FreeVar)
                        ) and isinstance(duw__hrfeq.value, CPUDispatcher
                        ) and issubclass(duw__hrfeq.value._compiler.
                        pipeline_class, BodoCompiler):
                        mhtqt__dgxdb = duw__hrfeq.value.py_func
                        arg_types = None
                        if typingctx:
                            yep__uycx = dict(unse__xwu.kws)
                            loz__pmohj = tuple(typemap[oano__ttoln.name] for
                                oano__ttoln in unse__xwu.args)
                            qxhy__ddh = {mvw__qfp: typemap[oano__ttoln.name
                                ] for mvw__qfp, oano__ttoln in yep__uycx.
                                items()}
                            tsia__aipu, arg_types = (duw__hrfeq.value.
                                fold_argument_types(loz__pmohj, qxhy__ddh))
                        tsia__aipu, hpp__shtn = inline_closure_call(func_ir,
                            mhtqt__dgxdb.__globals__, block, i,
                            mhtqt__dgxdb, typingctx=typingctx, targetctx=
                            targetctx, arg_typs=arg_types, typemap=typemap,
                            calltypes=calltypes, work_list=work_list)
                        _locals.update((hpp__shtn[mvw__qfp].name,
                            oano__ttoln) for mvw__qfp, oano__ttoln in
                            duw__hrfeq.value.locals.items() if mvw__qfp in
                            hpp__shtn)
                        break
    return whlx__thlh


def udf_jit(signature_or_function=None, **options):
    vwnd__gufvi = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=vwnd__gufvi,
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
    for czu__hjcj, (csww__muv, tsia__aipu) in enumerate(pm.passes):
        if csww__muv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:czu__hjcj + 1]
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
    zussa__zwcdf = None
    kwpv__adt = None
    _locals = {}
    filv__mecg = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(filv__mecg, arg_types,
        kw_types)
    bos__gygxa = numba.core.compiler.Flags()
    xxt__jylh = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    ihuh__smgej = {'nopython': True, 'boundscheck': False, 'parallel':
        xxt__jylh}
    numba.core.registry.cpu_target.options.parse_as_flags(bos__gygxa,
        ihuh__smgej)
    mxqc__pnzv = TyperCompiler(typingctx, targetctx, zussa__zwcdf, args,
        kwpv__adt, bos__gygxa, _locals)
    return mxqc__pnzv.compile_extra(func)
