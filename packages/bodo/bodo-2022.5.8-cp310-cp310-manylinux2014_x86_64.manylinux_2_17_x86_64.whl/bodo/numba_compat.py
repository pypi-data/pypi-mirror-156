"""
Numba monkey patches to fix issues related to Bodo. Should be imported before any
other module in bodo package.
"""
import copy
import functools
import hashlib
import inspect
import itertools
import operator
import os
import re
import sys
import textwrap
import traceback
import types as pytypes
import warnings
from collections import OrderedDict
from collections.abc import Sequence
from contextlib import ExitStack
import numba
import numba.core.boxing
import numba.core.inline_closurecall
import numba.core.typing.listdecl
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, get_definition, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from bodo.utils.python_310_bytecode_pass import Bodo310ByteCodePass, peep_hole_call_function_ex_to_call_function_kw, peep_hole_fuse_dict_add_updates
from bodo.utils.typing import BodoError, get_overload_const_str, is_overload_constant_str, raise_bodo_error
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    from numba.core.utils import PYVERSION
    pof__bmf = numba.core.bytecode.FunctionIdentity.from_function(func)
    seybj__ydd = numba.core.interpreter.Interpreter(pof__bmf)
    qemcn__uewo = numba.core.bytecode.ByteCode(func_id=pof__bmf)
    func_ir = seybj__ydd.interpret(qemcn__uewo)
    if PYVERSION == (3, 10):
        func_ir = peep_hole_call_function_ex_to_call_function_kw(func_ir)
        func_ir = peep_hole_fuse_dict_add_updates(func_ir)
    if inline_closures:
        from numba.core.inline_closurecall import InlineClosureCallPass


        class DummyPipeline:

            def __init__(self, f_ir):
                self.state = numba.core.compiler.StateDict()
                self.state.typingctx = None
                self.state.targetctx = None
                self.state.args = None
                self.state.func_ir = f_ir
                self.state.typemap = None
                self.state.return_type = None
                self.state.calltypes = None
        numba.core.rewrites.rewrite_registry.apply('before-inference',
            DummyPipeline(func_ir).state)
        ehi__rfyl = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        ehi__rfyl.run()
    kngal__iubs = numba.core.postproc.PostProcessor(func_ir)
    kngal__iubs.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, zrl__ilbb in visit_vars_extensions.items():
        if isinstance(stmt, t):
            zrl__ilbb(stmt, callback, cbdata)
            return
    if isinstance(stmt, ir.Assign):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Arg):
        stmt.name = visit_vars_inner(stmt.name, callback, cbdata)
    elif isinstance(stmt, ir.Return):
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Raise):
        stmt.exception = visit_vars_inner(stmt.exception, callback, cbdata)
    elif isinstance(stmt, ir.Branch):
        stmt.cond = visit_vars_inner(stmt.cond, callback, cbdata)
    elif isinstance(stmt, ir.Jump):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
    elif isinstance(stmt, ir.Del):
        var = ir.Var(None, stmt.value, stmt.loc)
        var = visit_vars_inner(var, callback, cbdata)
        stmt.value = var.name
    elif isinstance(stmt, ir.DelAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
    elif isinstance(stmt, ir.SetAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.DelItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
    elif isinstance(stmt, ir.StaticSetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index_var = visit_vars_inner(stmt.index_var, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.SetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Print):
        stmt.args = [visit_vars_inner(x, callback, cbdata) for x in stmt.args]
        stmt.vararg = visit_vars_inner(stmt.vararg, callback, cbdata)
    else:
        pass
    return


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.visit_vars_stmt)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '52b7b645ba65c35f3cf564f936e113261db16a2dff1e80fbee2459af58844117':
        warnings.warn('numba.core.ir_utils.visit_vars_stmt has changed')
numba.core.ir_utils.visit_vars_stmt = visit_vars_stmt
old_run_pass = numba.core.typed_passes.InlineOverloads.run_pass


def InlineOverloads_run_pass(self, state):
    import bodo
    bodo.compiler.bodo_overload_inline_pass(state.func_ir, state.typingctx,
        state.targetctx, state.typemap, state.calltypes)
    return old_run_pass(self, state)


numba.core.typed_passes.InlineOverloads.run_pass = InlineOverloads_run_pass
from numba.core.ir_utils import _add_alias, alias_analysis_extensions, alias_func_extensions
_immutable_type_class = (types.Number, types.scalars._NPDatetimeBase, types
    .iterators.RangeType, types.UnicodeType)


def is_immutable_type(var, typemap):
    if typemap is None or var not in typemap:
        return False
    typ = typemap[var]
    if isinstance(typ, _immutable_type_class):
        return True
    if isinstance(typ, types.BaseTuple) and all(isinstance(t,
        _immutable_type_class) for t in typ.types):
        return True
    return False


def find_potential_aliases(blocks, args, typemap, func_ir, alias_map=None,
    arg_aliases=None):
    if alias_map is None:
        alias_map = {}
    if arg_aliases is None:
        arg_aliases = set(a for a in args if not is_immutable_type(a, typemap))
    func_ir._definitions = build_definitions(func_ir.blocks)
    uqfy__vuvvr = ['ravel', 'transpose', 'reshape']
    for nfxki__schu in blocks.values():
        for gfj__xnuj in nfxki__schu.body:
            if type(gfj__xnuj) in alias_analysis_extensions:
                zrl__ilbb = alias_analysis_extensions[type(gfj__xnuj)]
                zrl__ilbb(gfj__xnuj, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(gfj__xnuj, ir.Assign):
                zdm__lbm = gfj__xnuj.value
                mshzl__cwl = gfj__xnuj.target.name
                if is_immutable_type(mshzl__cwl, typemap):
                    continue
                if isinstance(zdm__lbm, ir.Var
                    ) and mshzl__cwl != zdm__lbm.name:
                    _add_alias(mshzl__cwl, zdm__lbm.name, alias_map,
                        arg_aliases)
                if isinstance(zdm__lbm, ir.Expr) and (zdm__lbm.op == 'cast' or
                    zdm__lbm.op in ['getitem', 'static_getitem']):
                    _add_alias(mshzl__cwl, zdm__lbm.value.name, alias_map,
                        arg_aliases)
                if isinstance(zdm__lbm, ir.Expr
                    ) and zdm__lbm.op == 'inplace_binop':
                    _add_alias(mshzl__cwl, zdm__lbm.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(zdm__lbm, ir.Expr
                    ) and zdm__lbm.op == 'getattr' and zdm__lbm.attr in ['T',
                    'ctypes', 'flat']:
                    _add_alias(mshzl__cwl, zdm__lbm.value.name, alias_map,
                        arg_aliases)
                if isinstance(zdm__lbm, ir.Expr
                    ) and zdm__lbm.op == 'getattr' and zdm__lbm.attr not in [
                    'shape'] and zdm__lbm.value.name in arg_aliases:
                    _add_alias(mshzl__cwl, zdm__lbm.value.name, alias_map,
                        arg_aliases)
                if isinstance(zdm__lbm, ir.Expr
                    ) and zdm__lbm.op == 'getattr' and zdm__lbm.attr in ('loc',
                    'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(mshzl__cwl, zdm__lbm.value.name, alias_map,
                        arg_aliases)
                if isinstance(zdm__lbm, ir.Expr) and zdm__lbm.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(mshzl__cwl, typemap):
                    for wtq__gwgac in zdm__lbm.items:
                        _add_alias(mshzl__cwl, wtq__gwgac.name, alias_map,
                            arg_aliases)
                if isinstance(zdm__lbm, ir.Expr) and zdm__lbm.op == 'call':
                    nmq__cgfm = guard(find_callname, func_ir, zdm__lbm, typemap
                        )
                    if nmq__cgfm is None:
                        continue
                    unq__nvw, bywgf__dik = nmq__cgfm
                    if nmq__cgfm in alias_func_extensions:
                        guyvf__lbzxx = alias_func_extensions[nmq__cgfm]
                        guyvf__lbzxx(mshzl__cwl, zdm__lbm.args, alias_map,
                            arg_aliases)
                    if bywgf__dik == 'numpy' and unq__nvw in uqfy__vuvvr:
                        _add_alias(mshzl__cwl, zdm__lbm.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(bywgf__dik, ir.Var
                        ) and unq__nvw in uqfy__vuvvr:
                        _add_alias(mshzl__cwl, bywgf__dik.name, alias_map,
                            arg_aliases)
    kidoh__bcp = copy.deepcopy(alias_map)
    for wtq__gwgac in kidoh__bcp:
        for dkil__xmya in kidoh__bcp[wtq__gwgac]:
            alias_map[wtq__gwgac] |= alias_map[dkil__xmya]
        for dkil__xmya in kidoh__bcp[wtq__gwgac]:
            alias_map[dkil__xmya] = alias_map[wtq__gwgac]
    return alias_map, arg_aliases


if _check_numba_change:
    lines = inspect.getsource(ir_utils.find_potential_aliases)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e6cf3e0f502f903453eb98346fc6854f87dc4ea1ac62f65c2d6aef3bf690b6c5':
        warnings.warn('ir_utils.find_potential_aliases has changed')
ir_utils.find_potential_aliases = find_potential_aliases
numba.parfors.array_analysis.find_potential_aliases = find_potential_aliases
if _check_numba_change:
    lines = inspect.getsource(ir_utils.dead_code_elimination)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '40a8626300a1a17523944ec7842b093c91258bbc60844bbd72191a35a4c366bf':
        warnings.warn('ir_utils.dead_code_elimination has changed')


def mini_dce(func_ir, typemap=None, alias_map=None, arg_aliases=None):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    htl__gme = compute_cfg_from_blocks(func_ir.blocks)
    jqc__cbhj = compute_use_defs(func_ir.blocks)
    kgexs__vnwwn = compute_live_map(htl__gme, func_ir.blocks, jqc__cbhj.
        usemap, jqc__cbhj.defmap)
    bjz__evggd = True
    while bjz__evggd:
        bjz__evggd = False
        for ljdmt__jtjpq, block in func_ir.blocks.items():
            lives = {wtq__gwgac.name for wtq__gwgac in block.terminator.
                list_vars()}
            for qct__zmuc, bnz__ouxzn in htl__gme.successors(ljdmt__jtjpq):
                lives |= kgexs__vnwwn[qct__zmuc]
            jnnd__bdfza = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    mshzl__cwl = stmt.target
                    jquei__upl = stmt.value
                    if mshzl__cwl.name not in lives:
                        if isinstance(jquei__upl, ir.Expr
                            ) and jquei__upl.op == 'make_function':
                            continue
                        if isinstance(jquei__upl, ir.Expr
                            ) and jquei__upl.op == 'getattr':
                            continue
                        if isinstance(jquei__upl, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(mshzl__cwl,
                            None), types.Function):
                            continue
                        if isinstance(jquei__upl, ir.Expr
                            ) and jquei__upl.op == 'build_map':
                            continue
                        if isinstance(jquei__upl, ir.Expr
                            ) and jquei__upl.op == 'build_tuple':
                            continue
                    if isinstance(jquei__upl, ir.Var
                        ) and mshzl__cwl.name == jquei__upl.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    zot__yeea = analysis.ir_extension_usedefs[type(stmt)]
                    pme__zjut, ath__dmd = zot__yeea(stmt)
                    lives -= ath__dmd
                    lives |= pme__zjut
                else:
                    lives |= {wtq__gwgac.name for wtq__gwgac in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(mshzl__cwl.name)
                jnnd__bdfza.append(stmt)
            jnnd__bdfza.reverse()
            if len(block.body) != len(jnnd__bdfza):
                bjz__evggd = True
            block.body = jnnd__bdfza


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    mmb__mzpzk = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (mmb__mzpzk,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    kjajc__byuwx = dict(key=func, _overload_func=staticmethod(overload_func
        ), _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), kjajc__byuwx)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '7f6974584cb10e49995b652827540cc6732e497c0b9f8231b44fd83fcc1c0a83':
        warnings.warn(
            'numba.core.typing.templates.make_overload_template has changed')
numba.core.typing.templates.make_overload_template = make_overload_template


def _resolve(self, typ, attr):
    if self._attr != attr:
        return None
    if isinstance(typ, types.TypeRef):
        assert typ == self.key
    else:
        assert isinstance(typ, self.key)


    class MethodTemplate(AbstractTemplate):
        key = self.key, attr
        _inline = self._inline
        _no_unliteral = getattr(self, '_no_unliteral', False)
        _overload_func = staticmethod(self._overload_func)
        _inline_overloads = self._inline_overloads
        prefer_literal = self.prefer_literal

        def generic(_, args, kws):
            args = (typ,) + tuple(args)
            fnty = self._get_function_type(self.context, typ)
            sig = self._get_signature(self.context, fnty, args, kws)
            sig = sig.replace(pysig=numba.core.utils.pysignature(self.
                _overload_func))
            for gebnx__xxkr in fnty.templates:
                self._inline_overloads.update(gebnx__xxkr._inline_overloads)
            if sig is not None:
                return sig.as_method()
    return types.BoundFunction(MethodTemplate, typ)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadMethodTemplate._resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ce8e0935dc939d0867ef969e1ed2975adb3533a58a4133fcc90ae13c4418e4d6':
        warnings.warn(
            'numba.core.typing.templates._OverloadMethodTemplate._resolve has changed'
            )
numba.core.typing.templates._OverloadMethodTemplate._resolve = _resolve


def make_overload_attribute_template(typ, attr, overload_func, inline,
    prefer_literal=False, base=_OverloadAttributeTemplate, **kwargs):
    assert isinstance(typ, types.Type) or issubclass(typ, types.Type)
    name = 'OverloadAttributeTemplate_%s_%s' % (typ, attr)
    no_unliteral = kwargs.pop('no_unliteral', False)
    kjajc__byuwx = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), kjajc__byuwx)
    return obj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_attribute_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f066c38c482d6cf8bf5735a529c3264118ba9b52264b24e58aad12a6b1960f5d':
        warnings.warn(
            'numba.core.typing.templates.make_overload_attribute_template has changed'
            )
numba.core.typing.templates.make_overload_attribute_template = (
    make_overload_attribute_template)


def generic(self, args, kws):
    from numba.core.typed_passes import PreLowerStripPhis
    tvune__qozx, kmgdk__antne = self._get_impl(args, kws)
    if tvune__qozx is None:
        return
    ncrm__bmwsv = types.Dispatcher(tvune__qozx)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        sts__cdjv = tvune__qozx._compiler
        flags = compiler.Flags()
        whnl__xza = sts__cdjv.targetdescr.typing_context
        cez__bzmgd = sts__cdjv.targetdescr.target_context
        vah__gpa = sts__cdjv.pipeline_class(whnl__xza, cez__bzmgd, None,
            None, None, flags, None)
        qjdvh__qhi = InlineWorker(whnl__xza, cez__bzmgd, sts__cdjv.locals,
            vah__gpa, flags, None)
        wyf__jkc = ncrm__bmwsv.dispatcher.get_call_template
        gebnx__xxkr, dox__uqx, scqf__vlv, kws = wyf__jkc(kmgdk__antne, kws)
        if scqf__vlv in self._inline_overloads:
            return self._inline_overloads[scqf__vlv]['iinfo'].signature
        ir = qjdvh__qhi.run_untyped_passes(ncrm__bmwsv.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, cez__bzmgd, ir, scqf__vlv, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, scqf__vlv, None)
        self._inline_overloads[sig.args] = {'folded_args': scqf__vlv}
        gwvb__cwxbn = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = gwvb__cwxbn
        if not self._inline.is_always_inline:
            sig = ncrm__bmwsv.get_call_type(self.context, kmgdk__antne, kws)
            self._compiled_overloads[sig.args] = ncrm__bmwsv.get_overload(sig)
        upptq__buxl = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': scqf__vlv,
            'iinfo': upptq__buxl}
    else:
        sig = ncrm__bmwsv.get_call_type(self.context, kmgdk__antne, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = ncrm__bmwsv.get_overload(sig)
    return sig


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5d453a6d0215ebf0bab1279ff59eb0040b34938623be99142ce20acc09cdeb64':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate.generic has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate.generic = generic


def bound_function(template_key, no_unliteral=False):

    def wrapper(method_resolver):

        @functools.wraps(method_resolver)
        def attribute_resolver(self, ty):


            class MethodTemplate(AbstractTemplate):
                key = template_key

                def generic(_, args, kws):
                    sig = method_resolver(self, ty, args, kws)
                    if sig is not None and sig.recvr is None:
                        sig = sig.replace(recvr=ty)
                    return sig
            MethodTemplate._no_unliteral = no_unliteral
            return types.BoundFunction(MethodTemplate, ty)
        return attribute_resolver
    return wrapper


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.bound_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a2feefe64eae6a15c56affc47bf0c1d04461f9566913442d539452b397103322':
        warnings.warn('numba.core.typing.templates.bound_function has changed')
numba.core.typing.templates.bound_function = bound_function


def get_call_type(self, context, args, kws):
    from numba.core import utils
    frgk__hlpu = [True, False]
    nvvq__oeym = [False, True]
    cal__lxcp = _ResolutionFailures(context, self, args, kws, depth=self._depth
        )
    from numba.core.target_extension import get_local_target
    pul__nho = get_local_target(context)
    pymdc__vgpkm = utils.order_by_target_specificity(pul__nho, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for lgek__spjej in pymdc__vgpkm:
        mlojo__mtecn = lgek__spjej(context)
        hei__xna = frgk__hlpu if mlojo__mtecn.prefer_literal else nvvq__oeym
        hei__xna = [True] if getattr(mlojo__mtecn, '_no_unliteral', False
            ) else hei__xna
        for jdfrr__uusy in hei__xna:
            try:
                if jdfrr__uusy:
                    sig = mlojo__mtecn.apply(args, kws)
                else:
                    zejqi__gborv = tuple([_unlit_non_poison(a) for a in args])
                    wkxpr__hwbr = {vubue__zdza: _unlit_non_poison(
                        wtq__gwgac) for vubue__zdza, wtq__gwgac in kws.items()}
                    sig = mlojo__mtecn.apply(zejqi__gborv, wkxpr__hwbr)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    cal__lxcp.add_error(mlojo__mtecn, False, e, jdfrr__uusy)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = mlojo__mtecn.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    zqgx__udo = getattr(mlojo__mtecn, 'cases', None)
                    if zqgx__udo is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            zqgx__udo)
                    else:
                        msg = 'No match.'
                    cal__lxcp.add_error(mlojo__mtecn, True, msg, jdfrr__uusy)
    cal__lxcp.raise_error()


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BaseFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '25f038a7216f8e6f40068ea81e11fd9af8ad25d19888f7304a549941b01b7015':
        warnings.warn(
            'numba.core.types.functions.BaseFunction.get_call_type has changed'
            )
numba.core.types.functions.BaseFunction.get_call_type = get_call_type
bodo_typing_error_info = """
This is often caused by the use of unsupported features or typing issues.
See https://docs.bodo.ai/
"""


def get_call_type2(self, context, args, kws):
    gebnx__xxkr = self.template(context)
    rhzfy__ivnz = None
    okxt__gfr = None
    qmn__qfzs = None
    hei__xna = [True, False] if gebnx__xxkr.prefer_literal else [False, True]
    hei__xna = [True] if getattr(gebnx__xxkr, '_no_unliteral', False
        ) else hei__xna
    for jdfrr__uusy in hei__xna:
        if jdfrr__uusy:
            try:
                qmn__qfzs = gebnx__xxkr.apply(args, kws)
            except Exception as njm__sho:
                if isinstance(njm__sho, errors.ForceLiteralArg):
                    raise njm__sho
                rhzfy__ivnz = njm__sho
                qmn__qfzs = None
            else:
                break
        else:
            hhj__nzn = tuple([_unlit_non_poison(a) for a in args])
            kac__jxqs = {vubue__zdza: _unlit_non_poison(wtq__gwgac) for 
                vubue__zdza, wtq__gwgac in kws.items()}
            imyl__sxb = hhj__nzn == args and kws == kac__jxqs
            if not imyl__sxb and qmn__qfzs is None:
                try:
                    qmn__qfzs = gebnx__xxkr.apply(hhj__nzn, kac__jxqs)
                except Exception as njm__sho:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(njm__sho
                        , errors.NumbaError):
                        raise njm__sho
                    if isinstance(njm__sho, errors.ForceLiteralArg):
                        if gebnx__xxkr.prefer_literal:
                            raise njm__sho
                    okxt__gfr = njm__sho
                else:
                    break
    if qmn__qfzs is None and (okxt__gfr is not None or rhzfy__ivnz is not None
        ):
        wpb__ahzkb = '- Resolution failure for {} arguments:\n{}\n'
        yew__bjhbn = _termcolor.highlight(wpb__ahzkb)
        if numba.core.config.DEVELOPER_MODE:
            ybuas__xdkae = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    dgksy__ihpbg = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    dgksy__ihpbg = ['']
                buba__jqhk = '\n{}'.format(2 * ybuas__xdkae)
                aefgp__xqvyl = _termcolor.reset(buba__jqhk + buba__jqhk.
                    join(_bt_as_lines(dgksy__ihpbg)))
                return _termcolor.reset(aefgp__xqvyl)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            daw__uwqy = str(e)
            daw__uwqy = daw__uwqy if daw__uwqy else str(repr(e)) + add_bt(e)
            osuky__guh = errors.TypingError(textwrap.dedent(daw__uwqy))
            return yew__bjhbn.format(literalness, str(osuky__guh))
        import bodo
        if isinstance(rhzfy__ivnz, bodo.utils.typing.BodoError):
            raise rhzfy__ivnz
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', rhzfy__ivnz) +
                nested_msg('non-literal', okxt__gfr))
        else:
            if 'missing a required argument' in rhzfy__ivnz.msg:
                msg = 'missing a required argument'
            else:
                msg = 'Compilation error for '
                if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                    DataFrameType):
                    msg += 'DataFrame.'
                elif isinstance(self.this, bodo.hiframes.pd_series_ext.
                    SeriesType):
                    msg += 'Series.'
                msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg, loc=rhzfy__ivnz.loc)
    return qmn__qfzs


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BoundFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '502cd77c0084452e903a45a0f1f8107550bfbde7179363b57dabd617ce135f4a':
        warnings.warn(
            'numba.core.types.functions.BoundFunction.get_call_type has changed'
            )
numba.core.types.functions.BoundFunction.get_call_type = get_call_type2


def string_from_string_and_size(self, string, size):
    from llvmlite import ir as lir
    fnty = lir.FunctionType(self.pyobj, [self.cstring, self.py_ssize_t])
    unq__nvw = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=unq__nvw)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            ilooj__hcz = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), ilooj__hcz)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    ebzc__bahnh = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            ebzc__bahnh.append(types.Omitted(a.value))
        else:
            ebzc__bahnh.append(self.typeof_pyval(a))
    rma__ghb = None
    try:
        error = None
        rma__ghb = self.compile(tuple(ebzc__bahnh))
    except errors.ForceLiteralArg as e:
        qryi__iqth = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if qryi__iqth:
            ftrnk__duduq = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            jvru__nyg = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(qryi__iqth))
            raise errors.CompilerError(ftrnk__duduq.format(jvru__nyg))
        kmgdk__antne = []
        try:
            for i, wtq__gwgac in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        kmgdk__antne.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        kmgdk__antne.append(types.literal(args[i]))
                else:
                    kmgdk__antne.append(args[i])
            args = kmgdk__antne
        except (OSError, FileNotFoundError) as uvf__idkd:
            error = FileNotFoundError(str(uvf__idkd) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                rma__ghb = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        jyvu__xisee = []
        for i, zliri__xjqz in enumerate(args):
            val = zliri__xjqz.value if isinstance(zliri__xjqz, numba.core.
                dispatcher.OmittedArg) else zliri__xjqz
            try:
                gipz__etrx = typeof(val, Purpose.argument)
            except ValueError as ycc__hvqep:
                jyvu__xisee.append((i, str(ycc__hvqep)))
            else:
                if gipz__etrx is None:
                    jyvu__xisee.append((i,
                        f'cannot determine Numba type of value {val}'))
        if jyvu__xisee:
            fnpi__juzr = '\n'.join(f'- argument {i}: {oytcq__qot}' for i,
                oytcq__qot in jyvu__xisee)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{fnpi__juzr}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                crk__slu = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                mgmb__azfm = False
                for zut__zev in crk__slu:
                    if zut__zev in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        mgmb__azfm = True
                        break
                if not mgmb__azfm:
                    msg = f'{str(e)}'
                msg += '\n' + e.loc.strformat() + '\n'
                e.patch_message(msg)
        error_rewrite(e, 'typing')
    except errors.UnsupportedError as e:
        error_rewrite(e, 'unsupported_error')
    except (errors.NotDefinedError, errors.RedefinedError, errors.
        VerificationError) as e:
        error_rewrite(e, 'interpreter')
    except errors.ConstantInferenceError as e:
        error_rewrite(e, 'constant_inference')
    except bodo.utils.typing.BodoError as e:
        error = bodo.utils.typing.BodoError(str(e))
    except Exception as e:
        if numba.core.config.SHOW_HELP:
            if hasattr(e, 'patch_message'):
                ilooj__hcz = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), ilooj__hcz)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return rma__ghb


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher._DispatcherBase.
        _compile_for_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5cdfbf0b13a528abf9f0408e70f67207a03e81d610c26b1acab5b2dc1f79bf06':
        warnings.warn(
            'numba.core.dispatcher._DispatcherBase._compile_for_args has changed'
            )
numba.core.dispatcher._DispatcherBase._compile_for_args = _compile_for_args


def resolve_gb_agg_funcs(cres):
    from bodo.ir.aggregate import gb_agg_cfunc_addr
    for wbh__lcc in cres.library._codegen._engine._defined_symbols:
        if wbh__lcc.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in wbh__lcc and (
            'bodo_gb_udf_update_local' in wbh__lcc or 'bodo_gb_udf_combine' in
            wbh__lcc or 'bodo_gb_udf_eval' in wbh__lcc or 
            'bodo_gb_apply_general_udfs' in wbh__lcc):
            gb_agg_cfunc_addr[wbh__lcc] = cres.library.get_pointer_to_function(
                wbh__lcc)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for wbh__lcc in cres.library._codegen._engine._defined_symbols:
        if wbh__lcc.startswith('cfunc') and ('get_join_cond_addr' not in
            wbh__lcc or 'bodo_join_gen_cond' in wbh__lcc):
            join_gen_cond_cfunc_addr[wbh__lcc
                ] = cres.library.get_pointer_to_function(wbh__lcc)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    tvune__qozx = self._get_dispatcher_for_current_target()
    if tvune__qozx is not self:
        return tvune__qozx.compile(sig)
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        if not self._can_compile:
            raise RuntimeError('compilation disabled')
        with self._compiling_counter:
            args, return_type = sigutils.normalize_signature(sig)
            tbics__rytf = self.overloads.get(tuple(args))
            if tbics__rytf is not None:
                return tbics__rytf.entry_point
            cres = self._cache.load_overload(sig, self.targetctx)
            if cres is not None:
                resolve_gb_agg_funcs(cres)
                resolve_join_general_cond_funcs(cres)
                self._cache_hits[sig] += 1
                if not cres.objectmode:
                    self.targetctx.insert_user_function(cres.entry_point,
                        cres.fndesc, [cres.library])
                self.add_overload(cres)
                return cres.entry_point
            self._cache_misses[sig] += 1
            cdlqv__yrd = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=cdlqv__yrd):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
                if bodo.get_rank() == 0:
                    self._cache.save_overload(sig, cres)
            else:
                dqaz__yvk = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in dqaz__yvk:
                    self._cache.save_overload(sig, cres)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.Dispatcher.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '934ec993577ea3b1c7dd2181ac02728abf8559fd42c17062cc821541b092ff8f':
        warnings.warn('numba.core.dispatcher.Dispatcher.compile has changed')
numba.core.dispatcher.Dispatcher.compile = compile


def _get_module_for_linking(self):
    import llvmlite.binding as ll
    self._ensure_finalized()
    if self._shared_module is not None:
        return self._shared_module
    tlzqs__ggbz = self._final_module
    ghfu__ngywq = []
    aqts__kbr = 0
    for fn in tlzqs__ggbz.functions:
        aqts__kbr += 1
        if not fn.is_declaration and fn.linkage == ll.Linkage.external:
            if 'get_agg_udf_addr' not in fn.name:
                if 'bodo_gb_udf_update_local' in fn.name:
                    continue
                if 'bodo_gb_udf_combine' in fn.name:
                    continue
                if 'bodo_gb_udf_eval' in fn.name:
                    continue
                if 'bodo_gb_apply_general_udfs' in fn.name:
                    continue
            if 'get_join_cond_addr' not in fn.name:
                if 'bodo_join_gen_cond' in fn.name:
                    continue
            ghfu__ngywq.append(fn.name)
    if aqts__kbr == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if ghfu__ngywq:
        tlzqs__ggbz = tlzqs__ggbz.clone()
        for name in ghfu__ngywq:
            tlzqs__ggbz.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = tlzqs__ggbz
    return tlzqs__ggbz


if _check_numba_change:
    lines = inspect.getsource(numba.core.codegen.CPUCodeLibrary.
        _get_module_for_linking)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '56dde0e0555b5ec85b93b97c81821bce60784515a1fbf99e4542e92d02ff0a73':
        warnings.warn(
            'numba.core.codegen.CPUCodeLibrary._get_module_for_linking has changed'
            )
numba.core.codegen.CPUCodeLibrary._get_module_for_linking = (
    _get_module_for_linking)


def propagate(self, typeinfer):
    import bodo
    errors = []
    for lcevz__xdsb in self.constraints:
        loc = lcevz__xdsb.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                lcevz__xdsb(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                kucol__orbs = numba.core.errors.TypingError(str(e), loc=
                    lcevz__xdsb.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(kucol__orbs, e))
            except bodo.utils.typing.BodoError as e:
                if loc not in e.locs_in_msg:
                    errors.append(bodo.utils.typing.BodoError(str(e.msg) +
                        '\n' + loc.strformat() + '\n', locs_in_msg=e.
                        locs_in_msg + [loc]))
                else:
                    errors.append(bodo.utils.typing.BodoError(e.msg,
                        locs_in_msg=e.locs_in_msg))
            except Exception as e:
                from numba.core import utils
                if utils.use_old_style_errors():
                    numba.core.typeinfer._logger.debug('captured error',
                        exc_info=e)
                    msg = """Internal error at {con}.
{err}
Enable logging at debug level for details."""
                    kucol__orbs = numba.core.errors.TypingError(msg.format(
                        con=lcevz__xdsb, err=str(e)), loc=lcevz__xdsb.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(kucol__orbs, e))
                elif utils.use_new_style_errors():
                    raise e
                else:
                    msg = (
                        f"Unknown CAPTURED_ERRORS style: '{numba.core.config.CAPTURED_ERRORS}'."
                        )
                    assert 0, msg
    return errors


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.ConstraintNetwork.propagate)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e73635eeba9ba43cb3372f395b747ae214ce73b729fb0adba0a55237a1cb063':
        warnings.warn(
            'numba.core.typeinfer.ConstraintNetwork.propagate has changed')
numba.core.typeinfer.ConstraintNetwork.propagate = propagate


def raise_error(self):
    import bodo
    for wmqn__zqxwo in self._failures.values():
        for uul__agwj in wmqn__zqxwo:
            if isinstance(uul__agwj.error, ForceLiteralArg):
                raise uul__agwj.error
            if isinstance(uul__agwj.error, bodo.utils.typing.BodoError):
                raise uul__agwj.error
    raise TypingError(self.format())


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.
        _ResolutionFailures.raise_error)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84b89430f5c8b46cfc684804e6037f00a0f170005cd128ad245551787b2568ea':
        warnings.warn(
            'numba.core.types.functions._ResolutionFailures.raise_error has changed'
            )
numba.core.types.functions._ResolutionFailures.raise_error = raise_error


def bodo_remove_dead_block(block, lives, call_table, arg_aliases, alias_map,
    alias_set, func_ir, typemap):
    from bodo.transforms.distributed_pass import saved_array_analysis
    from bodo.utils.utils import is_array_typ, is_expr
    zdkhg__cwtn = False
    jnnd__bdfza = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        wicye__eytmp = set()
        wcnk__zhfds = lives & alias_set
        for wtq__gwgac in wcnk__zhfds:
            wicye__eytmp |= alias_map[wtq__gwgac]
        lives_n_aliases = lives | wicye__eytmp | arg_aliases
        if type(stmt) in remove_dead_extensions:
            zrl__ilbb = remove_dead_extensions[type(stmt)]
            stmt = zrl__ilbb(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                zdkhg__cwtn = True
                continue
        if isinstance(stmt, ir.Assign):
            mshzl__cwl = stmt.target
            jquei__upl = stmt.value
            if mshzl__cwl.name not in lives:
                if has_no_side_effect(jquei__upl, lives_n_aliases, call_table):
                    zdkhg__cwtn = True
                    continue
                if isinstance(jquei__upl, ir.Expr
                    ) and jquei__upl.op == 'call' and call_table[jquei__upl
                    .func.name] == ['astype']:
                    kuc__dzv = guard(get_definition, func_ir, jquei__upl.func)
                    if (kuc__dzv is not None and kuc__dzv.op == 'getattr' and
                        isinstance(typemap[kuc__dzv.value.name], types.
                        Array) and kuc__dzv.attr == 'astype'):
                        zdkhg__cwtn = True
                        continue
            if saved_array_analysis and mshzl__cwl.name in lives and is_expr(
                jquei__upl, 'getattr'
                ) and jquei__upl.attr == 'shape' and is_array_typ(typemap[
                jquei__upl.value.name]) and jquei__upl.value.name not in lives:
                exdd__dnxbz = {wtq__gwgac: vubue__zdza for vubue__zdza,
                    wtq__gwgac in func_ir.blocks.items()}
                if block in exdd__dnxbz:
                    ljdmt__jtjpq = exdd__dnxbz[block]
                    xql__oaok = saved_array_analysis.get_equiv_set(ljdmt__jtjpq
                        )
                    xof__nnv = xql__oaok.get_equiv_set(jquei__upl.value)
                    if xof__nnv is not None:
                        for wtq__gwgac in xof__nnv:
                            if wtq__gwgac.endswith('#0'):
                                wtq__gwgac = wtq__gwgac[:-2]
                            if wtq__gwgac in typemap and is_array_typ(typemap
                                [wtq__gwgac]) and wtq__gwgac in lives:
                                jquei__upl.value = ir.Var(jquei__upl.value.
                                    scope, wtq__gwgac, jquei__upl.value.loc)
                                zdkhg__cwtn = True
                                break
            if isinstance(jquei__upl, ir.Var
                ) and mshzl__cwl.name == jquei__upl.name:
                zdkhg__cwtn = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                zdkhg__cwtn = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            zot__yeea = analysis.ir_extension_usedefs[type(stmt)]
            pme__zjut, ath__dmd = zot__yeea(stmt)
            lives -= ath__dmd
            lives |= pme__zjut
        else:
            lives |= {wtq__gwgac.name for wtq__gwgac in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                cixqq__lezin = set()
                if isinstance(jquei__upl, ir.Expr):
                    cixqq__lezin = {wtq__gwgac.name for wtq__gwgac in
                        jquei__upl.list_vars()}
                if mshzl__cwl.name not in cixqq__lezin:
                    lives.remove(mshzl__cwl.name)
        jnnd__bdfza.append(stmt)
    jnnd__bdfza.reverse()
    block.body = jnnd__bdfza
    return zdkhg__cwtn


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            wbj__nzgrt, = args
            if isinstance(wbj__nzgrt, types.IterableType):
                dtype = wbj__nzgrt.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), wbj__nzgrt)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    wtu__wfx = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (wtu__wfx, self.dtype)
    super(types.Set, self).__init__(name=name)


types.Set.__init__ = Set__init__


@lower_builtin(operator.eq, types.UnicodeType, types.UnicodeType)
def eq_str(context, builder, sig, args):
    func = numba.cpython.unicode.unicode_eq(*sig.args)
    return context.compile_internal(builder, func, sig, args)


numba.parfors.parfor.push_call_vars = (lambda blocks, saved_globals,
    saved_getattrs, typemap, nested=False: None)


def maybe_literal(value):
    if isinstance(value, (list, dict, pytypes.FunctionType)):
        return
    if isinstance(value, tuple):
        try:
            return types.Tuple([literal(x) for x in value])
        except LiteralTypingError as rgdlb__naaed:
            return
    try:
        return literal(value)
    except LiteralTypingError as rgdlb__naaed:
        return


if _check_numba_change:
    lines = inspect.getsource(types.maybe_literal)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8fb2fd93acf214b28e33e37d19dc2f7290a42792ec59b650553ac278854b5081':
        warnings.warn('types.maybe_literal has changed')
types.maybe_literal = maybe_literal
types.misc.maybe_literal = maybe_literal


def CacheImpl__init__(self, py_func):
    self._lineno = py_func.__code__.co_firstlineno
    try:
        wdhk__lfkz = py_func.__qualname__
    except AttributeError as rgdlb__naaed:
        wdhk__lfkz = py_func.__name__
    zmqog__mpvc = inspect.getfile(py_func)
    for cls in self._locator_classes:
        zjew__kkdg = cls.from_function(py_func, zmqog__mpvc)
        if zjew__kkdg is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (wdhk__lfkz, zmqog__mpvc))
    self._locator = zjew__kkdg
    kgnej__xad = inspect.getfile(py_func)
    nlud__gdnm = os.path.splitext(os.path.basename(kgnej__xad))[0]
    if zmqog__mpvc.startswith('<ipython-'):
        wkvkv__uqtkc = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', nlud__gdnm, count=1)
        if wkvkv__uqtkc == nlud__gdnm:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        nlud__gdnm = wkvkv__uqtkc
    nqrct__yxf = '%s.%s' % (nlud__gdnm, wdhk__lfkz)
    svyo__jgrho = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(nqrct__yxf, svyo__jgrho)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    parj__odo = list(filter(lambda a: self._istuple(a.name), args))
    if len(parj__odo) == 2 and fn.__name__ == 'add':
        gyqwr__vyfa = self.typemap[parj__odo[0].name]
        qqg__cxu = self.typemap[parj__odo[1].name]
        if gyqwr__vyfa.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                parj__odo[1]))
        if qqg__cxu.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                parj__odo[0]))
        try:
            nvf__bel = [equiv_set.get_shape(x) for x in parj__odo]
            if None in nvf__bel:
                return None
            tkj__dro = sum(nvf__bel, ())
            return ArrayAnalysis.AnalyzeResult(shape=tkj__dro)
        except GuardException as rgdlb__naaed:
            return None
    wpad__qkw = list(filter(lambda a: self._isarray(a.name), args))
    require(len(wpad__qkw) > 0)
    xhpgc__koz = [x.name for x in wpad__qkw]
    iotb__qwd = [self.typemap[x.name].ndim for x in wpad__qkw]
    cdof__cql = max(iotb__qwd)
    require(cdof__cql > 0)
    nvf__bel = [equiv_set.get_shape(x) for x in wpad__qkw]
    if any(a is None for a in nvf__bel):
        return ArrayAnalysis.AnalyzeResult(shape=wpad__qkw[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, wpad__qkw))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, nvf__bel,
        xhpgc__koz)


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_broadcast)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6c91fec038f56111338ea2b08f5f0e7f61ebdab1c81fb811fe26658cc354e40f':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast has changed'
            )
numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast = (
    _analyze_broadcast)


def slice_size(self, index, dsize, equiv_set, scope, stmts):
    return None, None


numba.parfors.array_analysis.ArrayAnalysis.slice_size = slice_size


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    ereaa__mdh = code_obj.code
    yiirj__mdwhb = len(ereaa__mdh.co_freevars)
    fjk__nrd = ereaa__mdh.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        laak__vunbv, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        fjk__nrd = [wtq__gwgac.name for wtq__gwgac in laak__vunbv]
    tpmts__csjli = caller_ir.func_id.func.__globals__
    try:
        tpmts__csjli = getattr(code_obj, 'globals', tpmts__csjli)
    except KeyError as rgdlb__naaed:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    gqcp__bysxx = []
    for x in fjk__nrd:
        try:
            khvqx__awwe = caller_ir.get_definition(x)
        except KeyError as rgdlb__naaed:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(khvqx__awwe, (ir.Const, ir.Global, ir.FreeVar)):
            val = khvqx__awwe.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                mmb__mzpzk = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                tpmts__csjli[mmb__mzpzk] = bodo.jit(distributed=False)(val)
                tpmts__csjli[mmb__mzpzk].is_nested_func = True
                val = mmb__mzpzk
            if isinstance(val, CPUDispatcher):
                mmb__mzpzk = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                tpmts__csjli[mmb__mzpzk] = val
                val = mmb__mzpzk
            gqcp__bysxx.append(val)
        elif isinstance(khvqx__awwe, ir.Expr
            ) and khvqx__awwe.op == 'make_function':
            qad__utd = convert_code_obj_to_function(khvqx__awwe, caller_ir)
            mmb__mzpzk = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            tpmts__csjli[mmb__mzpzk] = bodo.jit(distributed=False)(qad__utd)
            tpmts__csjli[mmb__mzpzk].is_nested_func = True
            gqcp__bysxx.append(mmb__mzpzk)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    xvn__gqic = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        gqcp__bysxx)])
    curc__dvm = ','.join([('c_%d' % i) for i in range(yiirj__mdwhb)])
    qda__igh = list(ereaa__mdh.co_varnames)
    bgfft__cqtd = 0
    uzqe__cmy = ereaa__mdh.co_argcount
    mysmb__gkgt = caller_ir.get_definition(code_obj.defaults)
    if mysmb__gkgt is not None:
        if isinstance(mysmb__gkgt, tuple):
            d = [caller_ir.get_definition(x).value for x in mysmb__gkgt]
            qghvo__ncngy = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in mysmb__gkgt.items]
            qghvo__ncngy = tuple(d)
        bgfft__cqtd = len(qghvo__ncngy)
    qaka__vgwl = uzqe__cmy - bgfft__cqtd
    jqdw__zvhk = ','.join([('%s' % qda__igh[i]) for i in range(qaka__vgwl)])
    if bgfft__cqtd:
        chjz__whp = [('%s = %s' % (qda__igh[i + qaka__vgwl], qghvo__ncngy[i
            ])) for i in range(bgfft__cqtd)]
        jqdw__zvhk += ', '
        jqdw__zvhk += ', '.join(chjz__whp)
    return _create_function_from_code_obj(ereaa__mdh, xvn__gqic, jqdw__zvhk,
        curc__dvm, tpmts__csjli)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.convert_code_obj_to_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b840769812418d589460e924a15477e83e7919aac8a3dcb0188ff447344aa8ac':
        warnings.warn(
            'numba.core.ir_utils.convert_code_obj_to_function has changed')
numba.core.ir_utils.convert_code_obj_to_function = convert_code_obj_to_function
numba.core.untyped_passes.convert_code_obj_to_function = (
    convert_code_obj_to_function)


def passmanager_run(self, state):
    from numba.core.compiler import _EarlyPipelineCompletion
    if not self.finalized:
        raise RuntimeError('Cannot run non-finalised pipeline')
    from numba.core.compiler_machinery import CompilerPass, _pass_registry
    import bodo
    for ycno__cfxb, (gwrr__yqpm, cnr__nari) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % cnr__nari)
            racp__wwke = _pass_registry.get(gwrr__yqpm).pass_inst
            if isinstance(racp__wwke, CompilerPass):
                self._runPass(ycno__cfxb, racp__wwke, state)
            else:
                raise BaseException('Legacy pass in use')
        except _EarlyPipelineCompletion as e:
            raise e
        except bodo.utils.typing.BodoError as e:
            raise
        except Exception as e:
            if numba.core.config.DEVELOPER_MODE:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                msg = 'Failed in %s mode pipeline (step: %s)' % (self.
                    pipeline_name, cnr__nari)
                jryg__fpk = self._patch_error(msg, e)
                raise jryg__fpk
            else:
                raise e


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler_machinery.PassManager.run)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '43505782e15e690fd2d7e53ea716543bec37aa0633502956864edf649e790cdb':
        warnings.warn(
            'numba.core.compiler_machinery.PassManager.run has changed')
numba.core.compiler_machinery.PassManager.run = passmanager_run
if _check_numba_change:
    lines = inspect.getsource(numba.np.ufunc.parallel._launch_threads)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a57ef28c4168fdd436a5513bba4351ebc6d9fba76c5819f44046431a79b9030f':
        warnings.warn('numba.np.ufunc.parallel._launch_threads has changed')
numba.np.ufunc.parallel._launch_threads = lambda : None


def get_reduce_nodes(reduction_node, nodes, func_ir):
    uzywf__zzv = None
    ath__dmd = {}

    def lookup(var, already_seen, varonly=True):
        val = ath__dmd.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    bfz__okks = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        mshzl__cwl = stmt.target
        jquei__upl = stmt.value
        ath__dmd[mshzl__cwl.name] = jquei__upl
        if isinstance(jquei__upl, ir.Var) and jquei__upl.name in ath__dmd:
            jquei__upl = lookup(jquei__upl, set())
        if isinstance(jquei__upl, ir.Expr):
            qtvq__pta = set(lookup(wtq__gwgac, set(), True).name for
                wtq__gwgac in jquei__upl.list_vars())
            if name in qtvq__pta:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(jquei__upl)]
                slm__mqchf = [x for x, sbpfd__hcjfu in args if sbpfd__hcjfu
                    .name != name]
                args = [(x, sbpfd__hcjfu) for x, sbpfd__hcjfu in args if x !=
                    sbpfd__hcjfu.name]
                bkeg__gkrrb = dict(args)
                if len(slm__mqchf) == 1:
                    bkeg__gkrrb[slm__mqchf[0]] = ir.Var(mshzl__cwl.scope, 
                        name + '#init', mshzl__cwl.loc)
                replace_vars_inner(jquei__upl, bkeg__gkrrb)
                uzywf__zzv = nodes[i:]
                break
    return uzywf__zzv


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_reduce_nodes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a05b52aff9cb02e595a510cd34e973857303a71097fc5530567cb70ca183ef3b':
        warnings.warn('numba.parfors.parfor.get_reduce_nodes has changed')
numba.parfors.parfor.get_reduce_nodes = get_reduce_nodes


def _can_reorder_stmts(stmt, next_stmt, func_ir, call_table, alias_map,
    arg_aliases):
    from numba.parfors.parfor import Parfor, expand_aliases, is_assert_equiv
    if isinstance(stmt, Parfor) and not isinstance(next_stmt, Parfor
        ) and not isinstance(next_stmt, ir.Print) and (not isinstance(
        next_stmt, ir.Assign) or has_no_side_effect(next_stmt.value, set(),
        call_table) or guard(is_assert_equiv, func_ir, next_stmt.value)):
        esxw__yoiv = expand_aliases({wtq__gwgac.name for wtq__gwgac in stmt
            .list_vars()}, alias_map, arg_aliases)
        qpxu__qywnj = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        ocd__fvpd = expand_aliases({wtq__gwgac.name for wtq__gwgac in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        nyoq__uwype = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(qpxu__qywnj & ocd__fvpd | nyoq__uwype & esxw__yoiv) == 0:
            return True
    return False


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor._can_reorder_stmts)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '18caa9a01b21ab92b4f79f164cfdbc8574f15ea29deedf7bafdf9b0e755d777c':
        warnings.warn('numba.parfors.parfor._can_reorder_stmts has changed')
numba.parfors.parfor._can_reorder_stmts = _can_reorder_stmts


def get_parfor_writes(parfor, func_ir):
    from numba.parfors.parfor import Parfor
    assert isinstance(parfor, Parfor)
    ppkg__ixptx = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            ppkg__ixptx.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                ppkg__ixptx.update(get_parfor_writes(stmt, func_ir))
    return ppkg__ixptx


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    ppkg__ixptx = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        ppkg__ixptx.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        ppkg__ixptx = {wtq__gwgac.name for wtq__gwgac in stmt.df_out_vars.
            values()}
        if stmt.out_key_vars is not None:
            ppkg__ixptx.update({wtq__gwgac.name for wtq__gwgac in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        ppkg__ixptx = {wtq__gwgac.name for wtq__gwgac in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        ppkg__ixptx = {wtq__gwgac.name for wtq__gwgac in stmt.out_data_vars
            .values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            ppkg__ixptx.update({wtq__gwgac.name for i, wtq__gwgac in
                enumerate(stmt.out_vars) if i not in stmt.dead_var_inds and
                i not in stmt.dead_key_var_inds})
    if is_call_assign(stmt):
        nmq__cgfm = guard(find_callname, func_ir, stmt.value)
        if nmq__cgfm in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            ppkg__ixptx.add(stmt.value.args[0].name)
        if nmq__cgfm == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            ppkg__ixptx.add(stmt.value.args[1].name)
    return ppkg__ixptx


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.get_stmt_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1a7a80b64c9a0eb27e99dc8eaae187bde379d4da0b74c84fbf87296d87939974':
        warnings.warn('numba.core.ir_utils.get_stmt_writes has changed')


def patch_message(self, new_message):
    self.msg = new_message
    self.args = (new_message,) + self.args[1:]


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.patch_message)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ed189a428a7305837e76573596d767b6e840e99f75c05af6941192e0214fa899':
        warnings.warn('numba.core.errors.NumbaError.patch_message has changed')
numba.core.errors.NumbaError.patch_message = patch_message


def add_context(self, msg):
    if numba.core.config.DEVELOPER_MODE:
        self.contexts.append(msg)
        zrl__ilbb = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        kyan__vqr = zrl__ilbb.format(self, msg)
        self.args = kyan__vqr,
    else:
        zrl__ilbb = _termcolor.errmsg('{0}')
        kyan__vqr = zrl__ilbb.format(self)
        self.args = kyan__vqr,
    return self


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.add_context)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6a388d87788f8432c2152ac55ca9acaa94dbc3b55be973b2cf22dd4ee7179ab8':
        warnings.warn('numba.core.errors.NumbaError.add_context has changed')
numba.core.errors.NumbaError.add_context = add_context


def _get_dist_spec_from_options(spec, **options):
    from bodo.transforms.distributed_analysis import Distribution
    dist_spec = {}
    if 'distributed' in options:
        for edv__tytq in options['distributed']:
            dist_spec[edv__tytq] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for edv__tytq in options['distributed_block']:
            dist_spec[edv__tytq] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    ujheo__hjd = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, cbhr__mgol in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(cbhr__mgol)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    iyt__eqt = {}
    for cjj__fvqn in reversed(inspect.getmro(cls)):
        iyt__eqt.update(cjj__fvqn.__dict__)
    aaq__cwi, ttee__elvo, cwwa__omhlj, ikhx__zks = {}, {}, {}, {}
    for vubue__zdza, wtq__gwgac in iyt__eqt.items():
        if isinstance(wtq__gwgac, pytypes.FunctionType):
            aaq__cwi[vubue__zdza] = wtq__gwgac
        elif isinstance(wtq__gwgac, property):
            ttee__elvo[vubue__zdza] = wtq__gwgac
        elif isinstance(wtq__gwgac, staticmethod):
            cwwa__omhlj[vubue__zdza] = wtq__gwgac
        else:
            ikhx__zks[vubue__zdza] = wtq__gwgac
    yeeiy__eudyq = (set(aaq__cwi) | set(ttee__elvo) | set(cwwa__omhlj)) & set(
        spec)
    if yeeiy__eudyq:
        raise NameError('name shadowing: {0}'.format(', '.join(yeeiy__eudyq)))
    xuh__eqf = ikhx__zks.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(ikhx__zks)
    if ikhx__zks:
        msg = 'class members are not yet supported: {0}'
        dsc__btvhy = ', '.join(ikhx__zks.keys())
        raise TypeError(msg.format(dsc__btvhy))
    for vubue__zdza, wtq__gwgac in ttee__elvo.items():
        if wtq__gwgac.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(vubue__zdza)
                )
    jit_methods = {vubue__zdza: bodo.jit(returns_maybe_distributed=
        ujheo__hjd)(wtq__gwgac) for vubue__zdza, wtq__gwgac in aaq__cwi.items()
        }
    jit_props = {}
    for vubue__zdza, wtq__gwgac in ttee__elvo.items():
        kjajc__byuwx = {}
        if wtq__gwgac.fget:
            kjajc__byuwx['get'] = bodo.jit(wtq__gwgac.fget)
        if wtq__gwgac.fset:
            kjajc__byuwx['set'] = bodo.jit(wtq__gwgac.fset)
        jit_props[vubue__zdza] = kjajc__byuwx
    jit_static_methods = {vubue__zdza: bodo.jit(wtq__gwgac.__func__) for 
        vubue__zdza, wtq__gwgac in cwwa__omhlj.items()}
    upt__ahbf = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    dlply__yqb = dict(class_type=upt__ahbf, __doc__=xuh__eqf)
    dlply__yqb.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), dlply__yqb)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, upt__ahbf)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(upt__ahbf, typingctx, targetctx).register()
    as_numba_type.register(cls, upt__ahbf.instance_type)
    return cls


if _check_numba_change:
    lines = inspect.getsource(jitclass_base.register_class_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '005e6e2e89a47f77a19ba86305565050d4dbc2412fc4717395adf2da348671a9':
        warnings.warn('jitclass_base.register_class_type has changed')
jitclass_base.register_class_type = register_class_type


def ClassType__init__(self, class_def, ctor_template_cls, struct,
    jit_methods, jit_props, jit_static_methods, dist_spec=None):
    if dist_spec is None:
        dist_spec = {}
    self.class_name = class_def.__name__
    self.class_doc = class_def.__doc__
    self._ctor_template_class = ctor_template_cls
    self.jit_methods = jit_methods
    self.jit_props = jit_props
    self.jit_static_methods = jit_static_methods
    self.struct = struct
    self.dist_spec = dist_spec
    doyl__wixmq = ','.join('{0}:{1}'.format(vubue__zdza, wtq__gwgac) for 
        vubue__zdza, wtq__gwgac in struct.items())
    lhyg__cvecn = ','.join('{0}:{1}'.format(vubue__zdza, wtq__gwgac) for 
        vubue__zdza, wtq__gwgac in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), doyl__wixmq, lhyg__cvecn)
    super(types.misc.ClassType, self).__init__(name)


if _check_numba_change:
    lines = inspect.getsource(types.misc.ClassType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '2b848ea82946c88f540e81f93ba95dfa7cd66045d944152a337fe2fc43451c30':
        warnings.warn('types.misc.ClassType.__init__ has changed')
types.misc.ClassType.__init__ = ClassType__init__


def jitclass(cls_or_spec=None, spec=None, **options):
    if cls_or_spec is not None and spec is None and not isinstance(cls_or_spec,
        type):
        spec = cls_or_spec
        cls_or_spec = None

    def wrap(cls):
        if numba.core.config.DISABLE_JIT:
            return cls
        else:
            from numba.experimental.jitclass.base import ClassBuilder
            return register_class_type(cls, spec, types.ClassType,
                ClassBuilder, **options)
    if cls_or_spec is None:
        return wrap
    else:
        return wrap(cls_or_spec)


if _check_numba_change:
    lines = inspect.getsource(jitclass_decorators.jitclass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '265f1953ee5881d1a5d90238d3c932cd300732e41495657e65bf51e59f7f4af5':
        warnings.warn('jitclass_decorators.jitclass has changed')


def CallConstraint_resolve(self, typeinfer, typevars, fnty):
    assert fnty
    context = typeinfer.context
    wexhj__csu = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if wexhj__csu is None:
        return
    xzn__lmgcl, sggpn__izasj = wexhj__csu
    for a in itertools.chain(xzn__lmgcl, sggpn__izasj.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, xzn__lmgcl, sggpn__izasj)
    except ForceLiteralArg as e:
        mpc__fjeug = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(mpc__fjeug, self.kws)
        gswz__seffh = set()
        vnvv__xvypn = set()
        hknh__iovs = {}
        for ycno__cfxb in e.requested_args:
            abvu__leguo = typeinfer.func_ir.get_definition(folded[ycno__cfxb])
            if isinstance(abvu__leguo, ir.Arg):
                gswz__seffh.add(abvu__leguo.index)
                if abvu__leguo.index in e.file_infos:
                    hknh__iovs[abvu__leguo.index] = e.file_infos[abvu__leguo
                        .index]
            else:
                vnvv__xvypn.add(ycno__cfxb)
        if vnvv__xvypn:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif gswz__seffh:
            raise ForceLiteralArg(gswz__seffh, loc=self.loc, file_infos=
                hknh__iovs)
    if sig is None:
        uvk__uktbl = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in xzn__lmgcl]
        args += [('%s=%s' % (vubue__zdza, wtq__gwgac)) for vubue__zdza,
            wtq__gwgac in sorted(sggpn__izasj.items())]
        clk__irn = uvk__uktbl.format(fnty, ', '.join(map(str, args)))
        guern__uaft = context.explain_function_type(fnty)
        msg = '\n'.join([clk__irn, guern__uaft])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        qtj__enza = context.unify_pairs(sig.recvr, fnty.this)
        if qtj__enza is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if qtj__enza is not None and qtj__enza.is_precise():
            puvox__kfu = fnty.copy(this=qtj__enza)
            typeinfer.propagate_refined_type(self.func, puvox__kfu)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            erp__hhies = target.getone()
            if context.unify_pairs(erp__hhies, sig.return_type) == erp__hhies:
                sig = sig.replace(return_type=erp__hhies)
    self.signature = sig
    self._add_refine_map(typeinfer, typevars, sig)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.CallConstraint.resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c78cd8ffc64b836a6a2ddf0362d481b52b9d380c5249920a87ff4da052ce081f':
        warnings.warn('numba.core.typeinfer.CallConstraint.resolve has changed'
            )
numba.core.typeinfer.CallConstraint.resolve = CallConstraint_resolve


def ForceLiteralArg__init__(self, arg_indices, fold_arguments=None, loc=
    None, file_infos=None):
    super(ForceLiteralArg, self).__init__(
        'Pseudo-exception to force literal arguments in the dispatcher',
        loc=loc)
    self.requested_args = frozenset(arg_indices)
    self.fold_arguments = fold_arguments
    if file_infos is None:
        self.file_infos = {}
    else:
        self.file_infos = file_infos


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b241d5e36a4cf7f4c73a7ad3238693612926606c7a278cad1978070b82fb55ef':
        warnings.warn('numba.core.errors.ForceLiteralArg.__init__ has changed')
numba.core.errors.ForceLiteralArg.__init__ = ForceLiteralArg__init__


def ForceLiteralArg_bind_fold_arguments(self, fold_arguments):
    e = ForceLiteralArg(self.requested_args, fold_arguments, loc=self.loc,
        file_infos=self.file_infos)
    return numba.core.utils.chain_exception(e, self)


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.
        bind_fold_arguments)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e93cca558f7c604a47214a8f2ec33ee994104cb3e5051166f16d7cc9315141d':
        warnings.warn(
            'numba.core.errors.ForceLiteralArg.bind_fold_arguments has changed'
            )
numba.core.errors.ForceLiteralArg.bind_fold_arguments = (
    ForceLiteralArg_bind_fold_arguments)


def ForceLiteralArg_combine(self, other):
    if not isinstance(other, ForceLiteralArg):
        ftrnk__duduq = '*other* must be a {} but got a {} instead'
        raise TypeError(ftrnk__duduq.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args,
        file_infos={**self.file_infos, **other.file_infos})


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.combine)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '49bf06612776f5d755c1c7d1c5eb91831a57665a8fed88b5651935f3bf33e899':
        warnings.warn('numba.core.errors.ForceLiteralArg.combine has changed')
numba.core.errors.ForceLiteralArg.combine = ForceLiteralArg_combine


def _get_global_type(self, gv):
    from bodo.utils.typing import FunctionLiteral
    ty = self._lookup_global(gv)
    if ty is not None:
        return ty
    if isinstance(gv, pytypes.ModuleType):
        return types.Module(gv)
    if isinstance(gv, pytypes.FunctionType):
        return FunctionLiteral(gv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.
        _get_global_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8ffe6b81175d1eecd62a37639b5005514b4477d88f35f5b5395041ac8c945a4a':
        warnings.warn(
            'numba.core.typing.context.BaseContext._get_global_type has changed'
            )
numba.core.typing.context.BaseContext._get_global_type = _get_global_type


def _legalize_args(self, func_ir, args, kwargs, loc, func_globals,
    func_closures):
    from numba.core import sigutils
    from bodo.utils.transform import get_const_value_inner
    if args:
        raise errors.CompilerError(
            "objectmode context doesn't take any positional arguments")
    lxtlo__ekcsz = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for vubue__zdza, wtq__gwgac in kwargs.items():
        rxm__poci = None
        try:
            nkfm__atzy = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var
                ('dummy'), loc)
            func_ir._definitions[nkfm__atzy.name] = [wtq__gwgac]
            rxm__poci = get_const_value_inner(func_ir, nkfm__atzy)
            func_ir._definitions.pop(nkfm__atzy.name)
            if isinstance(rxm__poci, str):
                rxm__poci = sigutils._parse_signature_string(rxm__poci)
            if isinstance(rxm__poci, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {vubue__zdza} is annotated as type class {rxm__poci}."""
                    )
            assert isinstance(rxm__poci, types.Type)
            if isinstance(rxm__poci, (types.List, types.Set)):
                rxm__poci = rxm__poci.copy(reflected=False)
            lxtlo__ekcsz[vubue__zdza] = rxm__poci
        except BodoError as rgdlb__naaed:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(rxm__poci, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(wtq__gwgac, ir.Global):
                    msg = f'Global {wtq__gwgac.name!r} is not defined.'
                if isinstance(wtq__gwgac, ir.FreeVar):
                    msg = f'Freevar {wtq__gwgac.name!r} is not defined.'
            if isinstance(wtq__gwgac, ir.Expr) and wtq__gwgac.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=vubue__zdza, msg=msg, loc=loc)
    for name, typ in lxtlo__ekcsz.items():
        self._legalize_arg_type(name, typ, loc)
    return lxtlo__ekcsz


if _check_numba_change:
    lines = inspect.getsource(numba.core.withcontexts._ObjModeContextType.
        _legalize_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '867c9ba7f1bcf438be56c38e26906bb551f59a99f853a9f68b71208b107c880e':
        warnings.warn(
            'numba.core.withcontexts._ObjModeContextType._legalize_args has changed'
            )
numba.core.withcontexts._ObjModeContextType._legalize_args = _legalize_args


def op_FORMAT_VALUE_byteflow(self, state, inst):
    flags = inst.arg
    if flags & 3 != 0:
        msg = 'str/repr/ascii conversion in f-strings not supported yet'
        raise errors.UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))
    format_spec = None
    if flags & 4 == 4:
        format_spec = state.pop()
    value = state.pop()
    fmtvar = state.make_temp()
    res = state.make_temp()
    state.append(inst, value=value, res=res, fmtvar=fmtvar, format_spec=
        format_spec)
    state.push(res)


def op_BUILD_STRING_byteflow(self, state, inst):
    rowh__gcarx = inst.arg
    assert rowh__gcarx > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(rowh__gcarx)]))
    tmps = [state.make_temp() for _ in range(rowh__gcarx - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    zzh__vtaeb = ir.Global('format', format, loc=self.loc)
    self.store(value=zzh__vtaeb, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    dgobc__txhgn = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=dgobc__txhgn, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    rowh__gcarx = inst.arg
    assert rowh__gcarx > 0, 'invalid BUILD_STRING count'
    vsj__hhvf = self.get(strings[0])
    for other, gcox__nuna in zip(strings[1:], tmps):
        other = self.get(other)
        zdm__lbm = ir.Expr.binop(operator.add, lhs=vsj__hhvf, rhs=other,
            loc=self.loc)
        self.store(zdm__lbm, gcox__nuna)
        vsj__hhvf = self.get(gcox__nuna)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    ykf__som = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, ykf__som])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    pjg__pcli = mk_unique_var(f'{var_name}')
    vhytw__uqa = pjg__pcli.replace('<', '_').replace('>', '_')
    vhytw__uqa = vhytw__uqa.replace('.', '_').replace('$', '_v')
    return vhytw__uqa


if _check_numba_change:
    lines = inspect.getsource(numba.core.inline_closurecall.
        _created_inlined_var_name)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0d91aac55cd0243e58809afe9d252562f9ae2899cde1112cc01a46804e01821e':
        warnings.warn(
            'numba.core.inline_closurecall._created_inlined_var_name has changed'
            )
numba.core.inline_closurecall._created_inlined_var_name = (
    _created_inlined_var_name)


def resolve_number___call__(self, classty):
    import numpy as np
    from numba.core.typing.templates import make_callable_template
    import bodo
    ty = classty.instance_type
    if isinstance(ty, types.NPDatetime):

        def typer(val1, val2):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(val1,
                'numpy.datetime64')
            if val1 == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
                if not is_overload_constant_str(val2):
                    raise_bodo_error(
                        "datetime64(): 'units' must be a 'str' specifying 'ns'"
                        )
                holkm__hmj = get_overload_const_str(val2)
                if holkm__hmj != 'ns':
                    raise BodoError("datetime64(): 'units' must be 'ns'")
                return types.NPDatetime('ns')
    else:

        def typer(val):
            if isinstance(val, (types.BaseTuple, types.Sequence)):
                fnty = self.context.resolve_value_type(np.array)
                sig = fnty.get_call_type(self.context, (val, types.DType(ty
                    )), {})
                return sig.return_type
            elif isinstance(val, (types.Number, types.Boolean, types.
                IntEnumMember)):
                return ty
            elif val == types.unicode_type:
                return ty
            elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
                if ty.bitwidth == 64:
                    return ty
                else:
                    msg = (
                        f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                        )
                    raise errors.TypingError(msg)
            elif isinstance(val, types.Array
                ) and val.ndim == 0 and val.dtype == ty:
                return ty
            else:
                msg = f'Casting {val} to {ty} directly is unsupported.'
                if isinstance(val, types.Array):
                    msg += f" Try doing '<array>.astype(np.{ty})' instead"
                raise errors.TypingError(msg)
    return types.Function(make_callable_template(key=ty, typer=typer))


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.
        NumberClassAttribute.resolve___call__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdaf0c7d0820130481bb2bd922985257b9281b670f0bafffe10e51cabf0d5081':
        warnings.warn(
            'numba.core.typing.builtins.NumberClassAttribute.resolve___call__ has changed'
            )
numba.core.typing.builtins.NumberClassAttribute.resolve___call__ = (
    resolve_number___call__)


def on_assign(self, states, assign):
    if assign.target.name == states['varname']:
        scope = states['scope']
        tsq__fzk = states['defmap']
        if len(tsq__fzk) == 0:
            lhu__cfu = assign.target
            numba.core.ssa._logger.debug('first assign: %s', lhu__cfu)
            if lhu__cfu.name not in scope.localvars:
                lhu__cfu = scope.define(assign.target.name, loc=assign.loc)
        else:
            lhu__cfu = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=lhu__cfu, value=assign.value, loc=assign.loc)
        tsq__fzk[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    ysn__qot = []
    for vubue__zdza, wtq__gwgac in typing.npydecl.registry.globals:
        if vubue__zdza == func:
            ysn__qot.append(wtq__gwgac)
    for vubue__zdza, wtq__gwgac in typing.templates.builtin_registry.globals:
        if vubue__zdza == func:
            ysn__qot.append(wtq__gwgac)
    if len(ysn__qot) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return ysn__qot


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    sill__jzi = {}
    tbtl__niiy = find_topo_order(blocks)
    koc__euave = {}
    for ljdmt__jtjpq in tbtl__niiy:
        block = blocks[ljdmt__jtjpq]
        jnnd__bdfza = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                mshzl__cwl = stmt.target.name
                jquei__upl = stmt.value
                if (jquei__upl.op == 'getattr' and jquei__upl.attr in
                    arr_math and isinstance(typemap[jquei__upl.value.name],
                    types.npytypes.Array)):
                    jquei__upl = stmt.value
                    zat__wacn = jquei__upl.value
                    sill__jzi[mshzl__cwl] = zat__wacn
                    scope = zat__wacn.scope
                    loc = zat__wacn.loc
                    pkh__gndo = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[pkh__gndo.name] = types.misc.Module(numpy)
                    svabt__xuau = ir.Global('np', numpy, loc)
                    zhzp__idw = ir.Assign(svabt__xuau, pkh__gndo, loc)
                    jquei__upl.value = pkh__gndo
                    jnnd__bdfza.append(zhzp__idw)
                    func_ir._definitions[pkh__gndo.name] = [svabt__xuau]
                    func = getattr(numpy, jquei__upl.attr)
                    gyy__aavrg = get_np_ufunc_typ_lst(func)
                    koc__euave[mshzl__cwl] = gyy__aavrg
                if (jquei__upl.op == 'call' and jquei__upl.func.name in
                    sill__jzi):
                    zat__wacn = sill__jzi[jquei__upl.func.name]
                    ggvsf__jjwyr = calltypes.pop(jquei__upl)
                    fhiog__kqo = ggvsf__jjwyr.args[:len(jquei__upl.args)]
                    ycnj__fwyk = {name: typemap[wtq__gwgac.name] for name,
                        wtq__gwgac in jquei__upl.kws}
                    opza__xztmy = koc__euave[jquei__upl.func.name]
                    ubl__xjvdr = None
                    for zqx__dkq in opza__xztmy:
                        try:
                            ubl__xjvdr = zqx__dkq.get_call_type(typingctx, 
                                [typemap[zat__wacn.name]] + list(fhiog__kqo
                                ), ycnj__fwyk)
                            typemap.pop(jquei__upl.func.name)
                            typemap[jquei__upl.func.name] = zqx__dkq
                            calltypes[jquei__upl] = ubl__xjvdr
                            break
                        except Exception as rgdlb__naaed:
                            pass
                    if ubl__xjvdr is None:
                        raise TypeError(
                            f'No valid template found for {jquei__upl.func.name}'
                            )
                    jquei__upl.args = [zat__wacn] + jquei__upl.args
            jnnd__bdfza.append(stmt)
        block.body = jnnd__bdfza


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    pxje__gmvrg = ufunc.nin
    bqj__tfxu = ufunc.nout
    qaka__vgwl = ufunc.nargs
    assert qaka__vgwl == pxje__gmvrg + bqj__tfxu
    if len(args) < pxje__gmvrg:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            pxje__gmvrg))
    if len(args) > qaka__vgwl:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), qaka__vgwl)
            )
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    gccg__kex = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    cybh__zzv = max(gccg__kex)
    clzo__aqxci = args[pxje__gmvrg:]
    if not all(d == cybh__zzv for d in gccg__kex[pxje__gmvrg:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(lox__yzkg, types.ArrayCompatible) and not
        isinstance(lox__yzkg, types.Bytes) for lox__yzkg in clzo__aqxci):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(lox__yzkg.mutable for lox__yzkg in clzo__aqxci):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    aqde__anw = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    lnsr__cfhpu = None
    if cybh__zzv > 0 and len(clzo__aqxci) < ufunc.nout:
        lnsr__cfhpu = 'C'
        aood__fgdop = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in aood__fgdop and 'F' in aood__fgdop:
            lnsr__cfhpu = 'F'
    return aqde__anw, clzo__aqxci, cybh__zzv, lnsr__cfhpu


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.Numpy_rules_ufunc.
        _handle_inputs)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4b97c64ad9c3d50e082538795054f35cf6d2fe962c3ca40e8377a4601b344d5c':
        warnings.warn('Numpy_rules_ufunc._handle_inputs has changed')
numba.core.typing.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)
numba.np.ufunc.dufunc.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)


def DictType__init__(self, keyty, valty, initial_value=None):
    from numba.types import DictType, InitialValue, NoneType, Optional, Tuple, TypeRef, unliteral
    assert not isinstance(keyty, TypeRef)
    assert not isinstance(valty, TypeRef)
    keyty = unliteral(keyty)
    valty = unliteral(valty)
    if isinstance(keyty, (Optional, NoneType)):
        hat__ptztr = 'Dict.key_type cannot be of type {}'
        raise TypingError(hat__ptztr.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        hat__ptztr = 'Dict.value_type cannot be of type {}'
        raise TypingError(hat__ptztr.format(valty))
    self.key_type = keyty
    self.value_type = valty
    self.keyvalue_type = Tuple([keyty, valty])
    name = '{}[{},{}]<iv={}>'.format(self.__class__.__name__, keyty, valty,
        initial_value)
    super(DictType, self).__init__(name)
    InitialValue.__init__(self, initial_value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.DictType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '475acd71224bd51526750343246e064ff071320c0d10c17b8b8ac81d5070d094':
        warnings.warn('DictType.__init__ has changed')
numba.core.types.containers.DictType.__init__ = DictType__init__


def _legalize_arg_types(self, args):
    for i, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(i))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    whiz__mafw = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[whiz__mafw]
        return impl, args
    except KeyError as rgdlb__naaed:
        pass
    impl, args = self._build_impl(whiz__mafw, args, kws)
    return impl, args


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate._get_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4e27d07b214ca16d6e8ed88f70d886b6b095e160d8f77f8df369dd4ed2eb3fae':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate._get_impl has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate._get_impl = (
    _overload_template_get_impl)


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        ohinv__cgzpa = find_topo_order(parfor.loop_body)
    ecy__xlh = ohinv__cgzpa[0]
    yxbt__lduom = {}
    _update_parfor_get_setitems(parfor.loop_body[ecy__xlh].body, parfor.
        index_var, alias_map, yxbt__lduom, lives_n_aliases)
    qxs__iymi = set(yxbt__lduom.keys())
    for spfme__rwm in ohinv__cgzpa:
        if spfme__rwm == ecy__xlh:
            continue
        for stmt in parfor.loop_body[spfme__rwm].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            bufe__apb = set(wtq__gwgac.name for wtq__gwgac in stmt.list_vars())
            lwo__sugs = bufe__apb & qxs__iymi
            for a in lwo__sugs:
                yxbt__lduom.pop(a, None)
    for spfme__rwm in ohinv__cgzpa:
        if spfme__rwm == ecy__xlh:
            continue
        block = parfor.loop_body[spfme__rwm]
        xte__ytzh = yxbt__lduom.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            xte__ytzh, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    idv__rtssz = max(blocks.keys())
    vwgea__emcto, cxem__fkdjb = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    ajmkr__gpr = ir.Jump(vwgea__emcto, ir.Loc('parfors_dummy', -1))
    blocks[idv__rtssz].body.append(ajmkr__gpr)
    htl__gme = compute_cfg_from_blocks(blocks)
    jqc__cbhj = compute_use_defs(blocks)
    kgexs__vnwwn = compute_live_map(htl__gme, blocks, jqc__cbhj.usemap,
        jqc__cbhj.defmap)
    alias_set = set(alias_map.keys())
    for ljdmt__jtjpq, block in blocks.items():
        jnnd__bdfza = []
        cksw__bqi = {wtq__gwgac.name for wtq__gwgac in block.terminator.
            list_vars()}
        for qct__zmuc, bnz__ouxzn in htl__gme.successors(ljdmt__jtjpq):
            cksw__bqi |= kgexs__vnwwn[qct__zmuc]
        for stmt in reversed(block.body):
            wicye__eytmp = cksw__bqi & alias_set
            for wtq__gwgac in wicye__eytmp:
                cksw__bqi |= alias_map[wtq__gwgac]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in cksw__bqi and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                nmq__cgfm = guard(find_callname, func_ir, stmt.value)
                if nmq__cgfm == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in cksw__bqi and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            cksw__bqi |= {wtq__gwgac.name for wtq__gwgac in stmt.list_vars()}
            jnnd__bdfza.append(stmt)
        jnnd__bdfza.reverse()
        block.body = jnnd__bdfza
    typemap.pop(cxem__fkdjb.name)
    blocks[idv__rtssz].body.pop()

    def trim_empty_parfor_branches(parfor):
        bjz__evggd = False
        blocks = parfor.loop_body.copy()
        for ljdmt__jtjpq, block in blocks.items():
            if len(block.body):
                qsmzh__aiag = block.body[-1]
                if isinstance(qsmzh__aiag, ir.Branch):
                    if len(blocks[qsmzh__aiag.truebr].body) == 1 and len(blocks
                        [qsmzh__aiag.falsebr].body) == 1:
                        ekw__mhjv = blocks[qsmzh__aiag.truebr].body[0]
                        gbkbe__wug = blocks[qsmzh__aiag.falsebr].body[0]
                        if isinstance(ekw__mhjv, ir.Jump) and isinstance(
                            gbkbe__wug, ir.Jump
                            ) and ekw__mhjv.target == gbkbe__wug.target:
                            parfor.loop_body[ljdmt__jtjpq].body[-1] = ir.Jump(
                                ekw__mhjv.target, qsmzh__aiag.loc)
                            bjz__evggd = True
                    elif len(blocks[qsmzh__aiag.truebr].body) == 1:
                        ekw__mhjv = blocks[qsmzh__aiag.truebr].body[0]
                        if isinstance(ekw__mhjv, ir.Jump
                            ) and ekw__mhjv.target == qsmzh__aiag.falsebr:
                            parfor.loop_body[ljdmt__jtjpq].body[-1] = ir.Jump(
                                ekw__mhjv.target, qsmzh__aiag.loc)
                            bjz__evggd = True
                    elif len(blocks[qsmzh__aiag.falsebr].body) == 1:
                        gbkbe__wug = blocks[qsmzh__aiag.falsebr].body[0]
                        if isinstance(gbkbe__wug, ir.Jump
                            ) and gbkbe__wug.target == qsmzh__aiag.truebr:
                            parfor.loop_body[ljdmt__jtjpq].body[-1] = ir.Jump(
                                gbkbe__wug.target, qsmzh__aiag.loc)
                            bjz__evggd = True
        return bjz__evggd
    bjz__evggd = True
    while bjz__evggd:
        """
        Process parfor body recursively.
        Note that this is the only place in this function that uses the
        argument lives instead of lives_n_aliases.  The former does not
        include the aliases of live variables but only the live variable
        names themselves.  See a comment in this function for how that
        is used.
        """
        remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
            func_ir, typemap)
        simplify_parfor_body_CFG(func_ir.blocks)
        bjz__evggd = trim_empty_parfor_branches(parfor)
    hgbnv__vah = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        hgbnv__vah &= len(block.body) == 0
    if hgbnv__vah:
        return None
    return parfor


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.remove_dead_parfor)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1c9b008a7ead13e988e1efe67618d8f87f0b9f3d092cc2cd6bfcd806b1fdb859':
        warnings.warn('remove_dead_parfor has changed')
numba.parfors.parfor.remove_dead_parfor = remove_dead_parfor
numba.core.ir_utils.remove_dead_extensions[numba.parfors.parfor.Parfor
    ] = remove_dead_parfor


def simplify_parfor_body_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import simplify_CFG
    from numba.parfors.parfor import Parfor
    watbe__tuam = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                watbe__tuam += 1
                parfor = stmt
                solmd__hntz = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = solmd__hntz.scope
                loc = ir.Loc('parfors_dummy', -1)
                aboza__pvko = ir.Var(scope, mk_unique_var('$const'), loc)
                solmd__hntz.body.append(ir.Assign(ir.Const(0, loc),
                    aboza__pvko, loc))
                solmd__hntz.body.append(ir.Return(aboza__pvko, loc))
                htl__gme = compute_cfg_from_blocks(parfor.loop_body)
                for piu__zwrd in htl__gme.dead_nodes():
                    del parfor.loop_body[piu__zwrd]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                solmd__hntz = parfor.loop_body[max(parfor.loop_body.keys())]
                solmd__hntz.body.pop()
                solmd__hntz.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return watbe__tuam


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def _lifted_compile(self, sig):
    import numba.core.event as ev
    from numba.core import compiler, sigutils
    from numba.core.compiler_lock import global_compiler_lock
    from numba.core.ir_utils import remove_dels
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        with self._compiling_counter:
            flags = self.flags
            args, return_type = sigutils.normalize_signature(sig)
            tbics__rytf = self.overloads.get(tuple(args))
            if tbics__rytf is not None:
                return tbics__rytf.entry_point
            self._pre_compile(args, return_type, flags)
            puif__mop = self.func_ir
            cdlqv__yrd = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=cdlqv__yrd):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=puif__mop, args=args,
                    return_type=return_type, flags=flags, locals=self.
                    locals, lifted=(), lifted_from=self.lifted_from,
                    is_lifted_loop=True)
                if cres.typing_error is not None and not flags.enable_pyobject:
                    raise cres.typing_error
                self.add_overload(cres)
            remove_dels(self.func_ir.blocks)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.LiftedCode.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1351ebc5d8812dc8da167b30dad30eafb2ca9bf191b49aaed6241c21e03afff1':
        warnings.warn('numba.core.dispatcher.LiftedCode.compile has changed')
numba.core.dispatcher.LiftedCode.compile = _lifted_compile


def compile_ir(typingctx, targetctx, func_ir, args, return_type, flags,
    locals, lifted=(), lifted_from=None, is_lifted_loop=False, library=None,
    pipeline_class=Compiler):
    if is_lifted_loop:
        jll__rpkug = copy.deepcopy(flags)
        jll__rpkug.no_rewrites = True

        def compile_local(the_ir, the_flags):
            fmhv__qzimg = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return fmhv__qzimg.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        bcc__kukd = compile_local(func_ir, jll__rpkug)
        bvj__jemt = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    bvj__jemt = compile_local(func_ir, flags)
                except Exception as rgdlb__naaed:
                    pass
        if bvj__jemt is not None:
            cres = bvj__jemt
        else:
            cres = bcc__kukd
        return cres
    else:
        fmhv__qzimg = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return fmhv__qzimg.compile_ir(func_ir=func_ir, lifted=lifted,
            lifted_from=lifted_from)


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.compile_ir)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c48ce5493f4c43326e8cbdd46f3ea038b2b9045352d9d25894244798388e5e5b':
        warnings.warn('numba.core.compiler.compile_ir has changed')
numba.core.compiler.compile_ir = compile_ir


def make_constant_array(self, builder, typ, ary):
    import math
    from llvmlite import ir as lir
    njw__rrs = self.get_data_type(typ.dtype)
    qfu__nto = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        qfu__nto):
        rmouq__wbu = ary.ctypes.data
        hqc__mle = self.add_dynamic_addr(builder, rmouq__wbu, info=str(type
            (rmouq__wbu)))
        jpc__ozdmo = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        ndtnb__fpubh = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            ndtnb__fpubh = ndtnb__fpubh.view('int64')
        val = bytearray(ndtnb__fpubh.data)
        vhxqp__xqa = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        hqc__mle = cgutils.global_constant(builder, '.const.array.data',
            vhxqp__xqa)
        hqc__mle.align = self.get_abi_alignment(njw__rrs)
        jpc__ozdmo = None
    iaq__fpphc = self.get_value_type(types.intp)
    tue__tjqi = [self.get_constant(types.intp, aodd__cqa) for aodd__cqa in
        ary.shape]
    idh__xisl = lir.Constant(lir.ArrayType(iaq__fpphc, len(tue__tjqi)),
        tue__tjqi)
    bci__zonuz = [self.get_constant(types.intp, aodd__cqa) for aodd__cqa in
        ary.strides]
    ameap__jnba = lir.Constant(lir.ArrayType(iaq__fpphc, len(bci__zonuz)),
        bci__zonuz)
    peqc__odbwg = self.get_constant(types.intp, ary.dtype.itemsize)
    zcdb__tli = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        zcdb__tli, peqc__odbwg, hqc__mle.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), idh__xisl, ameap__jnba])


if _check_numba_change:
    lines = inspect.getsource(numba.core.base.BaseContext.make_constant_array)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5721b5360b51f782f79bd794f7bf4d48657911ecdc05c30db22fd55f15dad821':
        warnings.warn(
            'numba.core.base.BaseContext.make_constant_array has changed')
numba.core.base.BaseContext.make_constant_array = make_constant_array


def _define_atomic_inc_dec(module, op, ordering):
    from llvmlite import ir as lir
    from numba.core.runtime.nrtdynmod import _word_type
    nqjnu__dgek = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    pba__vbyaa = lir.Function(module, nqjnu__dgek, name='nrt_atomic_{0}'.
        format(op))
    [txl__zexrf] = pba__vbyaa.args
    pwf__xoql = pba__vbyaa.append_basic_block()
    builder = lir.IRBuilder(pwf__xoql)
    qkvw__zbbv = lir.Constant(_word_type, 1)
    if False:
        yvjpe__ammx = builder.atomic_rmw(op, txl__zexrf, qkvw__zbbv,
            ordering=ordering)
        res = getattr(builder, op)(yvjpe__ammx, qkvw__zbbv)
        builder.ret(res)
    else:
        yvjpe__ammx = builder.load(txl__zexrf)
        quv__hbez = getattr(builder, op)(yvjpe__ammx, qkvw__zbbv)
        dkq__cjw = builder.icmp_signed('!=', yvjpe__ammx, lir.Constant(
            yvjpe__ammx.type, -1))
        with cgutils.if_likely(builder, dkq__cjw):
            builder.store(quv__hbez, txl__zexrf)
        builder.ret(quv__hbez)
    return pba__vbyaa


if _check_numba_change:
    lines = inspect.getsource(numba.core.runtime.nrtdynmod.
        _define_atomic_inc_dec)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9cc02c532b2980b6537b702f5608ea603a1ff93c6d3c785ae2cf48bace273f48':
        warnings.warn(
            'numba.core.runtime.nrtdynmod._define_atomic_inc_dec has changed')
numba.core.runtime.nrtdynmod._define_atomic_inc_dec = _define_atomic_inc_dec


def NativeLowering_run_pass(self, state):
    from llvmlite import binding as llvm
    from numba.core import funcdesc, lowering
    from numba.core.typed_passes import fallback_context
    if state.library is None:
        eqcar__xrrs = state.targetctx.codegen()
        state.library = eqcar__xrrs.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    seybj__ydd = state.func_ir
    typemap = state.typemap
    jab__qtwch = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    pmde__qzwq = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            seybj__ydd, typemap, jab__qtwch, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            djjw__puw = lowering.Lower(targetctx, library, fndesc,
                seybj__ydd, metadata=metadata)
            djjw__puw.lower()
            if not flags.no_cpython_wrapper:
                djjw__puw.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(jab__qtwch, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        djjw__puw.create_cfunc_wrapper()
            env = djjw__puw.env
            ayeoe__jfm = djjw__puw.call_helper
            del djjw__puw
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, ayeoe__jfm, cfunc=None, env=env)
        else:
            hrb__gphs = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(hrb__gphs, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, ayeoe__jfm, cfunc=hrb__gphs,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        bevv__akhmn = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = bevv__akhmn - pmde__qzwq
        metadata['llvm_pass_timings'] = library.recorded_timings
    return True


if _check_numba_change:
    lines = inspect.getsource(numba.core.typed_passes.NativeLowering.run_pass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a777ce6ce1bb2b1cbaa3ac6c2c0e2adab69a9c23888dff5f1cbb67bfb176b5de':
        warnings.warn(
            'numba.core.typed_passes.NativeLowering.run_pass has changed')
numba.core.typed_passes.NativeLowering.run_pass = NativeLowering_run_pass


def _python_list_to_native(typ, obj, c, size, listptr, errorptr):
    from llvmlite import ir as lir
    from numba.core.boxing import _NumbaTypeHelper
    from numba.cpython import listobj

    def check_element_type(nth, itemobj, expected_typobj):
        nqe__oors = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, nqe__oors),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            pvfqe__pvzr.do_break()
        lkz__nzgj = c.builder.icmp_signed('!=', nqe__oors, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(lkz__nzgj, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, nqe__oors)
                c.pyapi.decref(nqe__oors)
                pvfqe__pvzr.do_break()
        c.pyapi.decref(nqe__oors)
    pgevj__nbfll, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(pgevj__nbfll, likely=True) as (duzdi__kqwmv,
        wrvgt__irxy):
        with duzdi__kqwmv:
            list.size = size
            mmbxw__tpg = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                mmbxw__tpg), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        mmbxw__tpg))
                    with cgutils.for_range(c.builder, size) as pvfqe__pvzr:
                        itemobj = c.pyapi.list_getitem(obj, pvfqe__pvzr.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        fzwtf__wry = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(fzwtf__wry.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            pvfqe__pvzr.do_break()
                        list.setitem(pvfqe__pvzr.index, fzwtf__wry.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with wrvgt__irxy:
            c.builder.store(cgutils.true_bit, errorptr)
    with c.builder.if_then(c.builder.load(errorptr)):
        c.context.nrt.decref(c.builder, typ, list.value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.boxing._python_list_to_native)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f8e546df8b07adfe74a16b6aafb1d4fddbae7d3516d7944b3247cc7c9b7ea88a':
        warnings.warn('numba.core.boxing._python_list_to_native has changed')
numba.core.boxing._python_list_to_native = _python_list_to_native


def make_string_from_constant(context, builder, typ, literal_string):
    from llvmlite import ir as lir
    from numba.cpython.hashing import _Py_hash_t
    from numba.cpython.unicode import compile_time_get_string_data
    yuc__vataq, mbvea__fwiq, vqv__nqn, zle__nyt, mmky__ipdc = (
        compile_time_get_string_data(literal_string))
    tlzqs__ggbz = builder.module
    gv = context.insert_const_bytes(tlzqs__ggbz, yuc__vataq)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        mbvea__fwiq), context.get_constant(types.int32, vqv__nqn), context.
        get_constant(types.uint32, zle__nyt), context.get_constant(
        _Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    vgnuz__gmaq = None
    if isinstance(shape, types.Integer):
        vgnuz__gmaq = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(aodd__cqa, (types.Integer, types.IntEnumMember)) for
            aodd__cqa in shape):
            vgnuz__gmaq = len(shape)
    return vgnuz__gmaq


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.parse_shape)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e62e3ff09d36df5ac9374055947d6a8be27160ce32960d3ef6cb67f89bd16429':
        warnings.warn('numba.core.typing.npydecl.parse_shape has changed')
numba.core.typing.npydecl.parse_shape = parse_shape


def _get_names(self, obj):
    if isinstance(obj, ir.Var) or isinstance(obj, str):
        name = obj if isinstance(obj, str) else obj.name
        if name not in self.typemap:
            return name,
        typ = self.typemap[name]
        if isinstance(typ, (types.BaseTuple, types.ArrayCompatible)):
            vgnuz__gmaq = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if vgnuz__gmaq == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(
                    vgnuz__gmaq))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            xhpgc__koz = self._get_names(x)
            if len(xhpgc__koz) != 0:
                return xhpgc__koz[0]
            return xhpgc__koz
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    xhpgc__koz = self._get_names(obj)
    if len(xhpgc__koz) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(xhpgc__koz[0])


def get_equiv_set(self, obj):
    xhpgc__koz = self._get_names(obj)
    if len(xhpgc__koz) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(xhpgc__koz[0])


if _check_numba_change:
    for name, orig, new, hash in ((
        'numba.parfors.array_analysis.ShapeEquivSet._get_names', numba.
        parfors.array_analysis.ShapeEquivSet._get_names, _get_names,
        '8c9bf136109028d5445fd0a82387b6abeb70c23b20b41e2b50c34ba5359516ee'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const',
        numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const,
        get_equiv_const,
        'bef410ca31a9e29df9ee74a4a27d339cc332564e4a237828b8a4decf625ce44e'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set', numba.
        parfors.array_analysis.ShapeEquivSet.get_equiv_set, get_equiv_set,
        'ec936d340c488461122eb74f28a28b88227cb1f1bca2b9ba3c19258cfe1eb40a')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
numba.parfors.array_analysis.ShapeEquivSet._get_names = _get_names
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const = get_equiv_const
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set = get_equiv_set


def raise_on_unsupported_feature(func_ir, typemap):
    import numpy
    iiw__edqf = []
    for mmyhn__cma in func_ir.arg_names:
        if mmyhn__cma in typemap and isinstance(typemap[mmyhn__cma], types.
            containers.UniTuple) and typemap[mmyhn__cma].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(mmyhn__cma))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for ojjji__ddddn in func_ir.blocks.values():
        for stmt in ojjji__ddddn.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    job__kfj = getattr(val, 'code', None)
                    if job__kfj is not None:
                        if getattr(val, 'closure', None) is not None:
                            pxjd__rgfm = '<creating a function from a closure>'
                            zdm__lbm = ''
                        else:
                            pxjd__rgfm = job__kfj.co_name
                            zdm__lbm = '(%s) ' % pxjd__rgfm
                    else:
                        pxjd__rgfm = '<could not ascertain use case>'
                        zdm__lbm = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (pxjd__rgfm, zdm__lbm))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                smhy__puy = False
                if isinstance(val, pytypes.FunctionType):
                    smhy__puy = val in {numba.gdb, numba.gdb_init}
                if not smhy__puy:
                    smhy__puy = getattr(val, '_name', '') == 'gdb_internal'
                if smhy__puy:
                    iiw__edqf.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    nbgf__xib = func_ir.get_definition(var)
                    uxe__mwsl = guard(find_callname, func_ir, nbgf__xib)
                    if uxe__mwsl and uxe__mwsl[1] == 'numpy':
                        ty = getattr(numpy, uxe__mwsl[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    kil__stcfl = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(kil__stcfl), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if isinstance(ty, types.ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)
    if len(iiw__edqf) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        uyyyq__lku = '\n'.join([x.strformat() for x in iiw__edqf])
        raise errors.UnsupportedError(msg % uyyyq__lku)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '237a4fe8395a40899279c718bc3754102cd2577463ef2f48daceea78d79b2d5e':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    vubue__zdza, wtq__gwgac = next(iter(val.items()))
    wdo__wfcuk = typeof_impl(vubue__zdza, c)
    jag__mwvfu = typeof_impl(wtq__gwgac, c)
    if wdo__wfcuk is None or jag__mwvfu is None:
        raise ValueError(
            f'Cannot type dict element type {type(vubue__zdza)}, {type(wtq__gwgac)}'
            )
    return types.DictType(wdo__wfcuk, jag__mwvfu)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    cfesu__lda = cgutils.alloca_once_value(c.builder, val)
    ngnda__srdm = c.pyapi.object_hasattr_string(val, '_opaque')
    kkoru__fosl = c.builder.icmp_unsigned('==', ngnda__srdm, lir.Constant(
        ngnda__srdm.type, 0))
    max__nnf = typ.key_type
    okl__mrj = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(max__nnf, okl__mrj)

    def copy_dict(out_dict, in_dict):
        for vubue__zdza, wtq__gwgac in in_dict.items():
            out_dict[vubue__zdza] = wtq__gwgac
    with c.builder.if_then(kkoru__fosl):
        ifckr__mol = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        vwj__lzj = c.pyapi.call_function_objargs(ifckr__mol, [])
        lii__wyfgc = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(lii__wyfgc, [vwj__lzj, val])
        c.builder.store(vwj__lzj, cfesu__lda)
    val = c.builder.load(cfesu__lda)
    lpc__koo = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    lndr__bqmq = c.pyapi.object_type(val)
    wxfmz__whkeo = c.builder.icmp_unsigned('==', lndr__bqmq, lpc__koo)
    with c.builder.if_else(wxfmz__whkeo) as (hka__pqdb, rbw__dqxq):
        with hka__pqdb:
            oxxt__hvbru = c.pyapi.object_getattr_string(val, '_opaque')
            chf__whlc = types.MemInfoPointer(types.voidptr)
            fzwtf__wry = c.unbox(chf__whlc, oxxt__hvbru)
            mi = fzwtf__wry.value
            ebzc__bahnh = chf__whlc, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *ebzc__bahnh)
            nve__vypt = context.get_constant_null(ebzc__bahnh[1])
            args = mi, nve__vypt
            pyu__ucr, fui__xrss = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, fui__xrss)
            c.pyapi.decref(oxxt__hvbru)
            onmgw__xvgf = c.builder.basic_block
        with rbw__dqxq:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", lndr__bqmq, lpc__koo)
            szr__bifrz = c.builder.basic_block
    ank__uyccb = c.builder.phi(fui__xrss.type)
    bgkyg__wwbs = c.builder.phi(pyu__ucr.type)
    ank__uyccb.add_incoming(fui__xrss, onmgw__xvgf)
    ank__uyccb.add_incoming(fui__xrss.type(None), szr__bifrz)
    bgkyg__wwbs.add_incoming(pyu__ucr, onmgw__xvgf)
    bgkyg__wwbs.add_incoming(cgutils.true_bit, szr__bifrz)
    c.pyapi.decref(lpc__koo)
    c.pyapi.decref(lndr__bqmq)
    with c.builder.if_then(kkoru__fosl):
        c.pyapi.decref(val)
    return NativeValue(ank__uyccb, is_error=bgkyg__wwbs)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def op_DICT_UPDATE_byteflow(self, state, inst):
    value = state.pop()
    index = inst.arg
    target = state.peek(index)
    updatevar = state.make_temp()
    res = state.make_temp()
    state.append(inst, target=target, value=value, updatevar=updatevar, res=res
        )


if _check_numba_change:
    if hasattr(numba.core.byteflow.TraceRunner, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_DICT_UPDATE has changed')
numba.core.byteflow.TraceRunner.op_DICT_UPDATE = op_DICT_UPDATE_byteflow


def op_DICT_UPDATE_interpreter(self, inst, target, value, updatevar, res):
    from numba.core import ir
    target = self.get(target)
    value = self.get(value)
    ppica__pbw = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=ppica__pbw, name=updatevar)
    ysu__npnva = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=ysu__npnva, name=res)


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_DICT_UPDATE has changed')
numba.core.interpreter.Interpreter.op_DICT_UPDATE = op_DICT_UPDATE_interpreter


@numba.extending.overload_method(numba.core.types.DictType, 'update')
def ol_dict_update(d, other):
    if not isinstance(d, numba.core.types.DictType):
        return
    if not isinstance(other, numba.core.types.DictType):
        return

    def impl(d, other):
        for vubue__zdza, wtq__gwgac in other.items():
            d[vubue__zdza] = wtq__gwgac
    return impl


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'ol_dict_update'):
        warnings.warn('numba.typed.dictobject.ol_dict_update has changed')


def op_CALL_FUNCTION_EX_byteflow(self, state, inst):
    from numba.core.utils import PYVERSION
    if inst.arg & 1 and PYVERSION != (3, 10):
        errmsg = 'CALL_FUNCTION_EX with **kwargs not supported'
        raise errors.UnsupportedError(errmsg)
    if inst.arg & 1:
        varkwarg = state.pop()
    else:
        varkwarg = None
    vararg = state.pop()
    func = state.pop()
    res = state.make_temp()
    state.append(inst, func=func, vararg=vararg, varkwarg=varkwarg, res=res)
    state.push(res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.byteflow.TraceRunner.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '349e7cfd27f5dab80fe15a7728c5f098f3f225ba8512d84331e39d01e863c6d4':
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX has changed')
numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_byteflow)


def op_CALL_FUNCTION_EX_interpreter(self, inst, func, vararg, varkwarg, res):
    func = self.get(func)
    vararg = self.get(vararg)
    if varkwarg is not None:
        varkwarg = self.get(varkwarg)
    zdm__lbm = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(zdm__lbm, res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.interpreter.Interpreter.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84846e5318ab7ccc8f9abaae6ab9e0ca879362648196f9d4b0ffb91cf2e01f5d':
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX has changed'
            )
numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_interpreter)


@classmethod
def ir_expr_call(cls, func, args, kws, loc, vararg=None, varkwarg=None,
    target=None):
    assert isinstance(func, ir.Var)
    assert isinstance(loc, ir.Loc)
    op = 'call'
    return cls(op=op, loc=loc, func=func, args=args, kws=kws, vararg=vararg,
        varkwarg=varkwarg, target=target)


if _check_numba_change:
    lines = inspect.getsource(ir.Expr.call)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '665601d0548d4f648d454492e542cb8aa241107a8df6bc68d0eec664c9ada738':
        warnings.warn('ir.Expr.call has changed')
ir.Expr.call = ir_expr_call


@staticmethod
def define_untyped_pipeline(state, name='untyped'):
    from numba.core.compiler_machinery import PassManager
    from numba.core.untyped_passes import DeadBranchPrune, FindLiterallyCalls, FixupArgs, GenericRewrites, InlineClosureLikes, InlineInlinables, IRProcessing, LiteralPropagationSubPipelinePass, LiteralUnroll, MakeFunctionToJitFunction, ReconstructSSA, RewriteSemanticConstants, TranslateByteCode, WithLifting
    from numba.core.utils import PYVERSION
    nzne__optb = PassManager(name)
    if state.func_ir is None:
        nzne__optb.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            nzne__optb.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        nzne__optb.add_pass(FixupArgs, 'fix up args')
    nzne__optb.add_pass(IRProcessing, 'processing IR')
    nzne__optb.add_pass(WithLifting, 'Handle with contexts')
    nzne__optb.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        nzne__optb.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        nzne__optb.add_pass(DeadBranchPrune, 'dead branch pruning')
        nzne__optb.add_pass(GenericRewrites, 'nopython rewrites')
    nzne__optb.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    nzne__optb.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        nzne__optb.add_pass(DeadBranchPrune, 'dead branch pruning')
    nzne__optb.add_pass(FindLiterallyCalls, 'find literally calls')
    nzne__optb.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        nzne__optb.add_pass(ReconstructSSA, 'ssa')
    nzne__optb.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    nzne__optb.finalize()
    return nzne__optb


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fc5a0665658cc30588a78aca984ac2d323d5d3a45dce538cc62688530c772896':
        warnings.warn(
            'numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline has changed'
            )
numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline = (
    define_untyped_pipeline)


def mul_list_generic(self, args, kws):
    a, ulfno__krk = args
    if isinstance(a, types.List) and isinstance(ulfno__krk, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(ulfno__krk, types.List):
        return signature(ulfno__krk, types.intp, ulfno__krk)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.listdecl.MulList.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '95882385a8ffa67aa576e8169b9ee6b3197e0ad3d5def4b47fa65ce8cd0f1575':
        warnings.warn('numba.core.typing.listdecl.MulList.generic has changed')
numba.core.typing.listdecl.MulList.generic = mul_list_generic


@lower_builtin(operator.mul, types.Integer, types.List)
def list_mul(context, builder, sig, args):
    from llvmlite import ir as lir
    from numba.core.imputils import impl_ret_new_ref
    from numba.cpython.listobj import ListInstance
    if isinstance(sig.args[0], types.List):
        ulc__fhk, qxn__rfuua = 0, 1
    else:
        ulc__fhk, qxn__rfuua = 1, 0
    oqq__pgrco = ListInstance(context, builder, sig.args[ulc__fhk], args[
        ulc__fhk])
    qhe__hri = oqq__pgrco.size
    ifzb__tib = args[qxn__rfuua]
    mmbxw__tpg = lir.Constant(ifzb__tib.type, 0)
    ifzb__tib = builder.select(cgutils.is_neg_int(builder, ifzb__tib),
        mmbxw__tpg, ifzb__tib)
    zcdb__tli = builder.mul(ifzb__tib, qhe__hri)
    xdci__yqzmq = ListInstance.allocate(context, builder, sig.return_type,
        zcdb__tli)
    xdci__yqzmq.size = zcdb__tli
    with cgutils.for_range_slice(builder, mmbxw__tpg, zcdb__tli, qhe__hri,
        inc=True) as (jxovv__ooasm, _):
        with cgutils.for_range(builder, qhe__hri) as pvfqe__pvzr:
            value = oqq__pgrco.getitem(pvfqe__pvzr.index)
            xdci__yqzmq.setitem(builder.add(pvfqe__pvzr.index, jxovv__ooasm
                ), value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, xdci__yqzmq.
        value)


def unify_pairs(self, first, second):
    from numba.core.typeconv import Conversion
    if first == second:
        return first
    if first is types.undefined:
        return second
    elif second is types.undefined:
        return first
    if first is types.unknown or second is types.unknown:
        return types.unknown
    hli__dvlke = first.unify(self, second)
    if hli__dvlke is not None:
        return hli__dvlke
    hli__dvlke = second.unify(self, first)
    if hli__dvlke is not None:
        return hli__dvlke
    iog__dxk = self.can_convert(fromty=first, toty=second)
    if iog__dxk is not None and iog__dxk <= Conversion.safe:
        return second
    iog__dxk = self.can_convert(fromty=second, toty=first)
    if iog__dxk is not None and iog__dxk <= Conversion.safe:
        return first
    if isinstance(first, types.Literal) or isinstance(second, types.Literal):
        first = types.unliteral(first)
        second = types.unliteral(second)
        return self.unify_pairs(first, second)
    return None


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.unify_pairs
        )
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f0eaf4cfdf1537691de26efd24d7e320f7c3f10d35e9aefe70cb946b3be0008c':
        warnings.warn(
            'numba.core.typing.context.BaseContext.unify_pairs has changed')
numba.core.typing.context.BaseContext.unify_pairs = unify_pairs


def _native_set_to_python_list(typ, payload, c):
    from llvmlite import ir
    zcdb__tli = payload.used
    listobj = c.pyapi.list_new(zcdb__tli)
    pgevj__nbfll = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(pgevj__nbfll, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(zcdb__tli.
            type, 0))
        with payload._iterate() as pvfqe__pvzr:
            i = c.builder.load(index)
            item = pvfqe__pvzr.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return pgevj__nbfll, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    bpp__bgt = h.type
    rgrvb__viml = self.mask
    dtype = self._ty.dtype
    whnl__xza = context.typing_context
    fnty = whnl__xza.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(whnl__xza, (dtype, dtype), {})
    lau__ahga = context.get_function(fnty, sig)
    mntm__rmeay = ir.Constant(bpp__bgt, 1)
    yav__xpifi = ir.Constant(bpp__bgt, 5)
    ajhp__bvkmv = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, rgrvb__viml))
    if for_insert:
        mmf__eghs = rgrvb__viml.type(-1)
        erzvo__uyqks = cgutils.alloca_once_value(builder, mmf__eghs)
    ffrsj__sab = builder.append_basic_block('lookup.body')
    klgtz__xxr = builder.append_basic_block('lookup.found')
    jzmfp__kyeq = builder.append_basic_block('lookup.not_found')
    ylt__noqsi = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        crxd__sgrjg = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, crxd__sgrjg)):
            kfom__ypzs = lau__ahga(builder, (item, entry.key))
            with builder.if_then(kfom__ypzs):
                builder.branch(klgtz__xxr)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, crxd__sgrjg)):
            builder.branch(jzmfp__kyeq)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, crxd__sgrjg)):
                llbrq__qrpg = builder.load(erzvo__uyqks)
                llbrq__qrpg = builder.select(builder.icmp_unsigned('==',
                    llbrq__qrpg, mmf__eghs), i, llbrq__qrpg)
                builder.store(llbrq__qrpg, erzvo__uyqks)
    with cgutils.for_range(builder, ir.Constant(bpp__bgt, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, mntm__rmeay)
        i = builder.and_(i, rgrvb__viml)
        builder.store(i, index)
    builder.branch(ffrsj__sab)
    with builder.goto_block(ffrsj__sab):
        i = builder.load(index)
        check_entry(i)
        pmpby__jzvc = builder.load(ajhp__bvkmv)
        pmpby__jzvc = builder.lshr(pmpby__jzvc, yav__xpifi)
        i = builder.add(mntm__rmeay, builder.mul(i, yav__xpifi))
        i = builder.and_(rgrvb__viml, builder.add(i, pmpby__jzvc))
        builder.store(i, index)
        builder.store(pmpby__jzvc, ajhp__bvkmv)
        builder.branch(ffrsj__sab)
    with builder.goto_block(jzmfp__kyeq):
        if for_insert:
            i = builder.load(index)
            llbrq__qrpg = builder.load(erzvo__uyqks)
            i = builder.select(builder.icmp_unsigned('==', llbrq__qrpg,
                mmf__eghs), i, llbrq__qrpg)
            builder.store(i, index)
        builder.branch(ylt__noqsi)
    with builder.goto_block(klgtz__xxr):
        builder.branch(ylt__noqsi)
    builder.position_at_end(ylt__noqsi)
    smhy__puy = builder.phi(ir.IntType(1), 'found')
    smhy__puy.add_incoming(cgutils.true_bit, klgtz__xxr)
    smhy__puy.add_incoming(cgutils.false_bit, jzmfp__kyeq)
    return smhy__puy, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    wpymv__hnm = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    xiubk__izmh = payload.used
    mntm__rmeay = ir.Constant(xiubk__izmh.type, 1)
    xiubk__izmh = payload.used = builder.add(xiubk__izmh, mntm__rmeay)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, wpymv__hnm), likely=True):
        payload.fill = builder.add(payload.fill, mntm__rmeay)
    if do_resize:
        self.upsize(xiubk__izmh)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    smhy__puy, i = payload._lookup(item, h, for_insert=True)
    tiw__nmtre = builder.not_(smhy__puy)
    with builder.if_then(tiw__nmtre):
        entry = payload.get_entry(i)
        wpymv__hnm = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        xiubk__izmh = payload.used
        mntm__rmeay = ir.Constant(xiubk__izmh.type, 1)
        xiubk__izmh = payload.used = builder.add(xiubk__izmh, mntm__rmeay)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, wpymv__hnm), likely=True):
            payload.fill = builder.add(payload.fill, mntm__rmeay)
        if do_resize:
            self.upsize(xiubk__izmh)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    xiubk__izmh = payload.used
    mntm__rmeay = ir.Constant(xiubk__izmh.type, 1)
    xiubk__izmh = payload.used = self._builder.sub(xiubk__izmh, mntm__rmeay)
    if do_resize:
        self.downsize(xiubk__izmh)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    nqc__odck = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, nqc__odck)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    dvjhd__eyisy = payload
    pgevj__nbfll = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(pgevj__nbfll), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with dvjhd__eyisy._iterate() as pvfqe__pvzr:
        entry = pvfqe__pvzr.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(dvjhd__eyisy.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as pvfqe__pvzr:
        entry = pvfqe__pvzr.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    pgevj__nbfll = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(pgevj__nbfll), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    pgevj__nbfll = cgutils.alloca_once_value(builder, cgutils.true_bit)
    bpp__bgt = context.get_value_type(types.intp)
    mmbxw__tpg = ir.Constant(bpp__bgt, 0)
    mntm__rmeay = ir.Constant(bpp__bgt, 1)
    udjp__ltsj = context.get_data_type(types.SetPayload(self._ty))
    jjlu__iirga = context.get_abi_sizeof(udjp__ltsj)
    jnbj__ged = self._entrysize
    jjlu__iirga -= jnbj__ged
    dscek__zitsd, hatt__bskb = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(bpp__bgt, jnbj__ged), ir.Constant(bpp__bgt,
        jjlu__iirga))
    with builder.if_then(hatt__bskb, likely=False):
        builder.store(cgutils.false_bit, pgevj__nbfll)
    with builder.if_then(builder.load(pgevj__nbfll), likely=True):
        if realloc:
            qyq__dncxq = self._set.meminfo
            txl__zexrf = context.nrt.meminfo_varsize_alloc(builder,
                qyq__dncxq, size=dscek__zitsd)
            bevw__phr = cgutils.is_null(builder, txl__zexrf)
        else:
            razt__opfv = _imp_dtor(context, builder.module, self._ty)
            qyq__dncxq = context.nrt.meminfo_new_varsize_dtor(builder,
                dscek__zitsd, builder.bitcast(razt__opfv, cgutils.voidptr_t))
            bevw__phr = cgutils.is_null(builder, qyq__dncxq)
        with builder.if_else(bevw__phr, likely=False) as (lwtui__xabq,
            duzdi__kqwmv):
            with lwtui__xabq:
                builder.store(cgutils.false_bit, pgevj__nbfll)
            with duzdi__kqwmv:
                if not realloc:
                    self._set.meminfo = qyq__dncxq
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, dscek__zitsd, 255)
                payload.used = mmbxw__tpg
                payload.fill = mmbxw__tpg
                payload.finger = mmbxw__tpg
                flw__vtl = builder.sub(nentries, mntm__rmeay)
                payload.mask = flw__vtl
    return builder.load(pgevj__nbfll)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    pgevj__nbfll = cgutils.alloca_once_value(builder, cgutils.true_bit)
    bpp__bgt = context.get_value_type(types.intp)
    mmbxw__tpg = ir.Constant(bpp__bgt, 0)
    mntm__rmeay = ir.Constant(bpp__bgt, 1)
    udjp__ltsj = context.get_data_type(types.SetPayload(self._ty))
    jjlu__iirga = context.get_abi_sizeof(udjp__ltsj)
    jnbj__ged = self._entrysize
    jjlu__iirga -= jnbj__ged
    rgrvb__viml = src_payload.mask
    nentries = builder.add(mntm__rmeay, rgrvb__viml)
    dscek__zitsd = builder.add(ir.Constant(bpp__bgt, jjlu__iirga), builder.
        mul(ir.Constant(bpp__bgt, jnbj__ged), nentries))
    with builder.if_then(builder.load(pgevj__nbfll), likely=True):
        razt__opfv = _imp_dtor(context, builder.module, self._ty)
        qyq__dncxq = context.nrt.meminfo_new_varsize_dtor(builder,
            dscek__zitsd, builder.bitcast(razt__opfv, cgutils.voidptr_t))
        bevw__phr = cgutils.is_null(builder, qyq__dncxq)
        with builder.if_else(bevw__phr, likely=False) as (lwtui__xabq,
            duzdi__kqwmv):
            with lwtui__xabq:
                builder.store(cgutils.false_bit, pgevj__nbfll)
            with duzdi__kqwmv:
                self._set.meminfo = qyq__dncxq
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = mmbxw__tpg
                payload.mask = rgrvb__viml
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, jnbj__ged)
                with src_payload._iterate() as pvfqe__pvzr:
                    context.nrt.incref(builder, self._ty.dtype, pvfqe__pvzr
                        .entry.key)
    return builder.load(pgevj__nbfll)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    tsz__tyy = context.get_value_type(types.voidptr)
    gxcs__aqlf = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [tsz__tyy, gxcs__aqlf, tsz__tyy])
    unq__nvw = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=unq__nvw)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        orqku__bfgff = builder.bitcast(fn.args[0], cgutils.voidptr_t.
            as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, orqku__bfgff)
        with payload._iterate() as pvfqe__pvzr:
            entry = pvfqe__pvzr.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    vrche__fvji, = sig.args
    laak__vunbv, = args
    lgjmm__jtlj = numba.core.imputils.call_len(context, builder,
        vrche__fvji, laak__vunbv)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, lgjmm__jtlj)
    with numba.core.imputils.for_iter(context, builder, vrche__fvji,
        laak__vunbv) as pvfqe__pvzr:
        inst.add(pvfqe__pvzr.value)
        context.nrt.decref(builder, set_type.dtype, pvfqe__pvzr.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    vrche__fvji = sig.args[1]
    laak__vunbv = args[1]
    lgjmm__jtlj = numba.core.imputils.call_len(context, builder,
        vrche__fvji, laak__vunbv)
    if lgjmm__jtlj is not None:
        xpj__fezo = builder.add(inst.payload.used, lgjmm__jtlj)
        inst.upsize(xpj__fezo)
    with numba.core.imputils.for_iter(context, builder, vrche__fvji,
        laak__vunbv) as pvfqe__pvzr:
        mmnl__tax = context.cast(builder, pvfqe__pvzr.value, vrche__fvji.
            dtype, inst.dtype)
        inst.add(mmnl__tax)
        context.nrt.decref(builder, vrche__fvji.dtype, pvfqe__pvzr.value)
    if lgjmm__jtlj is not None:
        inst.downsize(inst.payload.used)
    return context.get_dummy_value()


if _check_numba_change:
    for name, orig, hash in ((
        'numba.core.boxing._native_set_to_python_list', numba.core.boxing.
        _native_set_to_python_list,
        'b47f3d5e582c05d80899ee73e1c009a7e5121e7a660d42cb518bb86933f3c06f'),
        ('numba.cpython.setobj._SetPayload._lookup', numba.cpython.setobj.
        _SetPayload._lookup,
        'c797b5399d7b227fe4eea3a058b3d3103f59345699388afb125ae47124bee395'),
        ('numba.cpython.setobj.SetInstance._add_entry', numba.cpython.
        setobj.SetInstance._add_entry,
        'c5ed28a5fdb453f242e41907cb792b66da2df63282c17abe0b68fc46782a7f94'),
        ('numba.cpython.setobj.SetInstance._add_key', numba.cpython.setobj.
        SetInstance._add_key,
        '324d6172638d02a361cfa0ca7f86e241e5a56a008d4ab581a305f9ae5ea4a75f'),
        ('numba.cpython.setobj.SetInstance._remove_entry', numba.cpython.
        setobj.SetInstance._remove_entry,
        '2c441b00daac61976e673c0e738e8e76982669bd2851951890dd40526fa14da1'),
        ('numba.cpython.setobj.SetInstance.pop', numba.cpython.setobj.
        SetInstance.pop,
        '1a7b7464cbe0577f2a38f3af9acfef6d4d25d049b1e216157275fbadaab41d1b'),
        ('numba.cpython.setobj.SetInstance._resize', numba.cpython.setobj.
        SetInstance._resize,
        '5ca5c2ba4f8c4bf546fde106b9c2656d4b22a16d16e163fb64c5d85ea4d88746'),
        ('numba.cpython.setobj.SetInstance._replace_payload', numba.cpython
        .setobj.SetInstance._replace_payload,
        'ada75a6c85828bff69c8469538c1979801f560a43fb726221a9c21bf208ae78d'),
        ('numba.cpython.setobj.SetInstance._allocate_payload', numba.
        cpython.setobj.SetInstance._allocate_payload,
        '2e80c419df43ebc71075b4f97fc1701c10dbc576aed248845e176b8d5829e61b'),
        ('numba.cpython.setobj.SetInstance._copy_payload', numba.cpython.
        setobj.SetInstance._copy_payload,
        '0885ac36e1eb5a0a0fc4f5d91e54b2102b69e536091fed9f2610a71d225193ec'),
        ('numba.cpython.setobj.set_constructor', numba.cpython.setobj.
        set_constructor,
        '3d521a60c3b8eaf70aa0f7267427475dfddd8f5e5053b5bfe309bb5f1891b0ce'),
        ('numba.cpython.setobj.set_update', numba.cpython.setobj.set_update,
        '965c4f7f7abcea5cbe0491b602e6d4bcb1800fa1ec39b1ffccf07e1bc56051c3')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.boxing._native_set_to_python_list = _native_set_to_python_list
numba.cpython.setobj._SetPayload._lookup = _lookup
numba.cpython.setobj.SetInstance._add_entry = _add_entry
numba.cpython.setobj.SetInstance._add_key = _add_key
numba.cpython.setobj.SetInstance._remove_entry = _remove_entry
numba.cpython.setobj.SetInstance.pop = pop
numba.cpython.setobj.SetInstance._resize = _resize
numba.cpython.setobj.SetInstance._replace_payload = _replace_payload
numba.cpython.setobj.SetInstance._allocate_payload = _allocate_payload
numba.cpython.setobj.SetInstance._copy_payload = _copy_payload


def _reduce(self):
    libdata = self.library.serialize_using_object_code()
    typeann = str(self.type_annotation)
    fndesc = self.fndesc
    fndesc.typemap = fndesc.calltypes = None
    referenced_envs = self._find_referenced_environments()
    ecsrr__ibz = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, ecsrr__ibz, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    hrb__gphs = target_context.get_executable(library, fndesc, env)
    ral__tjx = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=hrb__gphs, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return ral__tjx


if _check_numba_change:
    for name, orig, hash in (('numba.core.compiler.CompileResult._reduce',
        numba.core.compiler.CompileResult._reduce,
        '5f86eacfa5202c202b3dc200f1a7a9b6d3f9d1ec16d43a52cb2d580c34fbfa82'),
        ('numba.core.compiler.CompileResult._rebuild', numba.core.compiler.
        CompileResult._rebuild,
        '44fa9dc2255883ab49195d18c3cca8c0ad715d0dd02033bd7e2376152edc4e84')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.compiler.CompileResult._reduce = _reduce
numba.core.compiler.CompileResult._rebuild = _rebuild


def _get_cache_path(self):
    return numba.config.CACHE_DIR


if _check_numba_change:
    if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
        numba.core.caching._IPythonCacheLocator.get_cache_path = (
            _get_cache_path)
