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
    nuhc__onyap = numba.core.bytecode.FunctionIdentity.from_function(func)
    qxev__xlji = numba.core.interpreter.Interpreter(nuhc__onyap)
    ytmr__yrk = numba.core.bytecode.ByteCode(func_id=nuhc__onyap)
    func_ir = qxev__xlji.interpret(ytmr__yrk)
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
        mcyan__hlz = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        mcyan__hlz.run()
    fjpa__cvs = numba.core.postproc.PostProcessor(func_ir)
    fjpa__cvs.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, evjgb__wsen in visit_vars_extensions.items():
        if isinstance(stmt, t):
            evjgb__wsen(stmt, callback, cbdata)
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
    aljx__sle = ['ravel', 'transpose', 'reshape']
    for mzaco__twpxi in blocks.values():
        for gag__doonp in mzaco__twpxi.body:
            if type(gag__doonp) in alias_analysis_extensions:
                evjgb__wsen = alias_analysis_extensions[type(gag__doonp)]
                evjgb__wsen(gag__doonp, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(gag__doonp, ir.Assign):
                cykta__mzyof = gag__doonp.value
                bhttx__rfa = gag__doonp.target.name
                if is_immutable_type(bhttx__rfa, typemap):
                    continue
                if isinstance(cykta__mzyof, ir.Var
                    ) and bhttx__rfa != cykta__mzyof.name:
                    _add_alias(bhttx__rfa, cykta__mzyof.name, alias_map,
                        arg_aliases)
                if isinstance(cykta__mzyof, ir.Expr) and (cykta__mzyof.op ==
                    'cast' or cykta__mzyof.op in ['getitem', 'static_getitem']
                    ):
                    _add_alias(bhttx__rfa, cykta__mzyof.value.name,
                        alias_map, arg_aliases)
                if isinstance(cykta__mzyof, ir.Expr
                    ) and cykta__mzyof.op == 'inplace_binop':
                    _add_alias(bhttx__rfa, cykta__mzyof.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(cykta__mzyof, ir.Expr
                    ) and cykta__mzyof.op == 'getattr' and cykta__mzyof.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(bhttx__rfa, cykta__mzyof.value.name,
                        alias_map, arg_aliases)
                if (isinstance(cykta__mzyof, ir.Expr) and cykta__mzyof.op ==
                    'getattr' and cykta__mzyof.attr not in ['shape'] and 
                    cykta__mzyof.value.name in arg_aliases):
                    _add_alias(bhttx__rfa, cykta__mzyof.value.name,
                        alias_map, arg_aliases)
                if isinstance(cykta__mzyof, ir.Expr
                    ) and cykta__mzyof.op == 'getattr' and cykta__mzyof.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(bhttx__rfa, cykta__mzyof.value.name,
                        alias_map, arg_aliases)
                if isinstance(cykta__mzyof, ir.Expr) and cykta__mzyof.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(bhttx__rfa, typemap):
                    for nzpi__qrgv in cykta__mzyof.items:
                        _add_alias(bhttx__rfa, nzpi__qrgv.name, alias_map,
                            arg_aliases)
                if isinstance(cykta__mzyof, ir.Expr
                    ) and cykta__mzyof.op == 'call':
                    jns__moxd = guard(find_callname, func_ir, cykta__mzyof,
                        typemap)
                    if jns__moxd is None:
                        continue
                    wxmx__mvh, fsdv__hjl = jns__moxd
                    if jns__moxd in alias_func_extensions:
                        ejm__pcuy = alias_func_extensions[jns__moxd]
                        ejm__pcuy(bhttx__rfa, cykta__mzyof.args, alias_map,
                            arg_aliases)
                    if fsdv__hjl == 'numpy' and wxmx__mvh in aljx__sle:
                        _add_alias(bhttx__rfa, cykta__mzyof.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(fsdv__hjl, ir.Var
                        ) and wxmx__mvh in aljx__sle:
                        _add_alias(bhttx__rfa, fsdv__hjl.name, alias_map,
                            arg_aliases)
    dlklw__wnsso = copy.deepcopy(alias_map)
    for nzpi__qrgv in dlklw__wnsso:
        for xktva__dimy in dlklw__wnsso[nzpi__qrgv]:
            alias_map[nzpi__qrgv] |= alias_map[xktva__dimy]
        for xktva__dimy in dlklw__wnsso[nzpi__qrgv]:
            alias_map[xktva__dimy] = alias_map[nzpi__qrgv]
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
    kcia__rynbs = compute_cfg_from_blocks(func_ir.blocks)
    jctbt__wsos = compute_use_defs(func_ir.blocks)
    sdc__znw = compute_live_map(kcia__rynbs, func_ir.blocks, jctbt__wsos.
        usemap, jctbt__wsos.defmap)
    wnwhr__wyou = True
    while wnwhr__wyou:
        wnwhr__wyou = False
        for jmzw__zrsa, block in func_ir.blocks.items():
            lives = {nzpi__qrgv.name for nzpi__qrgv in block.terminator.
                list_vars()}
            for mvp__wzfh, xewyo__gni in kcia__rynbs.successors(jmzw__zrsa):
                lives |= sdc__znw[mvp__wzfh]
            mvs__vhhr = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    bhttx__rfa = stmt.target
                    knf__ykwa = stmt.value
                    if bhttx__rfa.name not in lives:
                        if isinstance(knf__ykwa, ir.Expr
                            ) and knf__ykwa.op == 'make_function':
                            continue
                        if isinstance(knf__ykwa, ir.Expr
                            ) and knf__ykwa.op == 'getattr':
                            continue
                        if isinstance(knf__ykwa, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(bhttx__rfa,
                            None), types.Function):
                            continue
                        if isinstance(knf__ykwa, ir.Expr
                            ) and knf__ykwa.op == 'build_map':
                            continue
                        if isinstance(knf__ykwa, ir.Expr
                            ) and knf__ykwa.op == 'build_tuple':
                            continue
                    if isinstance(knf__ykwa, ir.Var
                        ) and bhttx__rfa.name == knf__ykwa.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    sze__ghr = analysis.ir_extension_usedefs[type(stmt)]
                    ggfh__refqp, wue__ljhmp = sze__ghr(stmt)
                    lives -= wue__ljhmp
                    lives |= ggfh__refqp
                else:
                    lives |= {nzpi__qrgv.name for nzpi__qrgv in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(bhttx__rfa.name)
                mvs__vhhr.append(stmt)
            mvs__vhhr.reverse()
            if len(block.body) != len(mvs__vhhr):
                wnwhr__wyou = True
            block.body = mvs__vhhr


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    cer__eaeh = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (cer__eaeh,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    mnf__otg = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), mnf__otg)


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
            for hwb__ltno in fnty.templates:
                self._inline_overloads.update(hwb__ltno._inline_overloads)
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
    mnf__otg = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), mnf__otg)
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
    zpofc__lwe, zwc__txqw = self._get_impl(args, kws)
    if zpofc__lwe is None:
        return
    sxmg__csq = types.Dispatcher(zpofc__lwe)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        scaro__lfkk = zpofc__lwe._compiler
        flags = compiler.Flags()
        ofmvk__unqub = scaro__lfkk.targetdescr.typing_context
        kni__kbw = scaro__lfkk.targetdescr.target_context
        gzom__cjps = scaro__lfkk.pipeline_class(ofmvk__unqub, kni__kbw,
            None, None, None, flags, None)
        jbx__lgdsn = InlineWorker(ofmvk__unqub, kni__kbw, scaro__lfkk.
            locals, gzom__cjps, flags, None)
        qec__mmni = sxmg__csq.dispatcher.get_call_template
        hwb__ltno, itm__mie, fkc__ldut, kws = qec__mmni(zwc__txqw, kws)
        if fkc__ldut in self._inline_overloads:
            return self._inline_overloads[fkc__ldut]['iinfo'].signature
        ir = jbx__lgdsn.run_untyped_passes(sxmg__csq.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, kni__kbw, ir, fkc__ldut, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, fkc__ldut, None)
        self._inline_overloads[sig.args] = {'folded_args': fkc__ldut}
        gaf__ejkda = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = gaf__ejkda
        if not self._inline.is_always_inline:
            sig = sxmg__csq.get_call_type(self.context, zwc__txqw, kws)
            self._compiled_overloads[sig.args] = sxmg__csq.get_overload(sig)
        nbaxk__bfrl = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': fkc__ldut,
            'iinfo': nbaxk__bfrl}
    else:
        sig = sxmg__csq.get_call_type(self.context, zwc__txqw, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = sxmg__csq.get_overload(sig)
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
    fxq__rta = [True, False]
    hypi__nav = [False, True]
    ftoia__szh = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    rigv__epes = get_local_target(context)
    rhe__iks = utils.order_by_target_specificity(rigv__epes, self.templates,
        fnkey=self.key[0])
    self._depth += 1
    for ozmcl__lda in rhe__iks:
        jcbdc__wzeo = ozmcl__lda(context)
        rkn__rdg = fxq__rta if jcbdc__wzeo.prefer_literal else hypi__nav
        rkn__rdg = [True] if getattr(jcbdc__wzeo, '_no_unliteral', False
            ) else rkn__rdg
        for wjsd__uefkn in rkn__rdg:
            try:
                if wjsd__uefkn:
                    sig = jcbdc__wzeo.apply(args, kws)
                else:
                    khsus__levwg = tuple([_unlit_non_poison(a) for a in args])
                    jwlt__ncbv = {neq__fbn: _unlit_non_poison(nzpi__qrgv) for
                        neq__fbn, nzpi__qrgv in kws.items()}
                    sig = jcbdc__wzeo.apply(khsus__levwg, jwlt__ncbv)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    ftoia__szh.add_error(jcbdc__wzeo, False, e, wjsd__uefkn)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = jcbdc__wzeo.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    gwtk__gxu = getattr(jcbdc__wzeo, 'cases', None)
                    if gwtk__gxu is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            gwtk__gxu)
                    else:
                        msg = 'No match.'
                    ftoia__szh.add_error(jcbdc__wzeo, True, msg, wjsd__uefkn)
    ftoia__szh.raise_error()


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
    hwb__ltno = self.template(context)
    dknc__wntul = None
    hwdca__fdq = None
    ivhcd__klgnp = None
    rkn__rdg = [True, False] if hwb__ltno.prefer_literal else [False, True]
    rkn__rdg = [True] if getattr(hwb__ltno, '_no_unliteral', False
        ) else rkn__rdg
    for wjsd__uefkn in rkn__rdg:
        if wjsd__uefkn:
            try:
                ivhcd__klgnp = hwb__ltno.apply(args, kws)
            except Exception as llgfb__dwnj:
                if isinstance(llgfb__dwnj, errors.ForceLiteralArg):
                    raise llgfb__dwnj
                dknc__wntul = llgfb__dwnj
                ivhcd__klgnp = None
            else:
                break
        else:
            ncssn__fhg = tuple([_unlit_non_poison(a) for a in args])
            lmrn__gzab = {neq__fbn: _unlit_non_poison(nzpi__qrgv) for 
                neq__fbn, nzpi__qrgv in kws.items()}
            wqc__slgjy = ncssn__fhg == args and kws == lmrn__gzab
            if not wqc__slgjy and ivhcd__klgnp is None:
                try:
                    ivhcd__klgnp = hwb__ltno.apply(ncssn__fhg, lmrn__gzab)
                except Exception as llgfb__dwnj:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        llgfb__dwnj, errors.NumbaError):
                        raise llgfb__dwnj
                    if isinstance(llgfb__dwnj, errors.ForceLiteralArg):
                        if hwb__ltno.prefer_literal:
                            raise llgfb__dwnj
                    hwdca__fdq = llgfb__dwnj
                else:
                    break
    if ivhcd__klgnp is None and (hwdca__fdq is not None or dknc__wntul is not
        None):
        mtrh__hoqe = '- Resolution failure for {} arguments:\n{}\n'
        dgw__vykz = _termcolor.highlight(mtrh__hoqe)
        if numba.core.config.DEVELOPER_MODE:
            hudgv__zqte = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    mbchd__fdcs = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    mbchd__fdcs = ['']
                hxds__ftr = '\n{}'.format(2 * hudgv__zqte)
                egi__dfso = _termcolor.reset(hxds__ftr + hxds__ftr.join(
                    _bt_as_lines(mbchd__fdcs)))
                return _termcolor.reset(egi__dfso)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            duup__nokuu = str(e)
            duup__nokuu = duup__nokuu if duup__nokuu else str(repr(e)
                ) + add_bt(e)
            cmna__ynqm = errors.TypingError(textwrap.dedent(duup__nokuu))
            return dgw__vykz.format(literalness, str(cmna__ynqm))
        import bodo
        if isinstance(dknc__wntul, bodo.utils.typing.BodoError):
            raise dknc__wntul
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', dknc__wntul) +
                nested_msg('non-literal', hwdca__fdq))
        else:
            if 'missing a required argument' in dknc__wntul.msg:
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
            raise errors.TypingError(msg, loc=dknc__wntul.loc)
    return ivhcd__klgnp


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
    wxmx__mvh = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=wxmx__mvh)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            cfbny__srn = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), cfbny__srn)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    rcept__brcl = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            rcept__brcl.append(types.Omitted(a.value))
        else:
            rcept__brcl.append(self.typeof_pyval(a))
    wyb__fcdtd = None
    try:
        error = None
        wyb__fcdtd = self.compile(tuple(rcept__brcl))
    except errors.ForceLiteralArg as e:
        udhju__cac = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if udhju__cac:
            rwso__lqvc = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            pyc__fuqj = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(udhju__cac))
            raise errors.CompilerError(rwso__lqvc.format(pyc__fuqj))
        zwc__txqw = []
        try:
            for i, nzpi__qrgv in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        zwc__txqw.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        zwc__txqw.append(types.literal(args[i]))
                else:
                    zwc__txqw.append(args[i])
            args = zwc__txqw
        except (OSError, FileNotFoundError) as vzb__ksvov:
            error = FileNotFoundError(str(vzb__ksvov) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                wyb__fcdtd = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        rsyvp__eqd = []
        for i, oluwx__nxzzw in enumerate(args):
            val = oluwx__nxzzw.value if isinstance(oluwx__nxzzw, numba.core
                .dispatcher.OmittedArg) else oluwx__nxzzw
            try:
                kgjqf__yjyw = typeof(val, Purpose.argument)
            except ValueError as kpwt__xjgm:
                rsyvp__eqd.append((i, str(kpwt__xjgm)))
            else:
                if kgjqf__yjyw is None:
                    rsyvp__eqd.append((i,
                        f'cannot determine Numba type of value {val}'))
        if rsyvp__eqd:
            ucwrw__ulvoi = '\n'.join(f'- argument {i}: {puu__sjb}' for i,
                puu__sjb in rsyvp__eqd)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{ucwrw__ulvoi}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                eet__btsx = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                ucave__gsasz = False
                for faxk__gdn in eet__btsx:
                    if faxk__gdn in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        ucave__gsasz = True
                        break
                if not ucave__gsasz:
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
                cfbny__srn = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), cfbny__srn)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return wyb__fcdtd


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
    for pncce__npuf in cres.library._codegen._engine._defined_symbols:
        if pncce__npuf.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in pncce__npuf and (
            'bodo_gb_udf_update_local' in pncce__npuf or 
            'bodo_gb_udf_combine' in pncce__npuf or 'bodo_gb_udf_eval' in
            pncce__npuf or 'bodo_gb_apply_general_udfs' in pncce__npuf):
            gb_agg_cfunc_addr[pncce__npuf
                ] = cres.library.get_pointer_to_function(pncce__npuf)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for pncce__npuf in cres.library._codegen._engine._defined_symbols:
        if pncce__npuf.startswith('cfunc') and ('get_join_cond_addr' not in
            pncce__npuf or 'bodo_join_gen_cond' in pncce__npuf):
            join_gen_cond_cfunc_addr[pncce__npuf
                ] = cres.library.get_pointer_to_function(pncce__npuf)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    zpofc__lwe = self._get_dispatcher_for_current_target()
    if zpofc__lwe is not self:
        return zpofc__lwe.compile(sig)
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
            iqqvd__hxbyi = self.overloads.get(tuple(args))
            if iqqvd__hxbyi is not None:
                return iqqvd__hxbyi.entry_point
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
            cyzkb__uhlei = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=cyzkb__uhlei):
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
                oiz__oxft = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in oiz__oxft:
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
    wyzmg__tccwm = self._final_module
    yyurb__dgbd = []
    uwf__nkydh = 0
    for fn in wyzmg__tccwm.functions:
        uwf__nkydh += 1
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
            yyurb__dgbd.append(fn.name)
    if uwf__nkydh == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if yyurb__dgbd:
        wyzmg__tccwm = wyzmg__tccwm.clone()
        for name in yyurb__dgbd:
            wyzmg__tccwm.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = wyzmg__tccwm
    return wyzmg__tccwm


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
    for cach__tkl in self.constraints:
        loc = cach__tkl.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                cach__tkl(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                qtfx__dtrz = numba.core.errors.TypingError(str(e), loc=
                    cach__tkl.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(qtfx__dtrz, e))
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
                    qtfx__dtrz = numba.core.errors.TypingError(msg.format(
                        con=cach__tkl, err=str(e)), loc=cach__tkl.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(qtfx__dtrz, e))
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
    for kmfz__riret in self._failures.values():
        for mhcbv__vyre in kmfz__riret:
            if isinstance(mhcbv__vyre.error, ForceLiteralArg):
                raise mhcbv__vyre.error
            if isinstance(mhcbv__vyre.error, bodo.utils.typing.BodoError):
                raise mhcbv__vyre.error
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
    axf__aqsjy = False
    mvs__vhhr = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        hme__mqg = set()
        walm__uxyk = lives & alias_set
        for nzpi__qrgv in walm__uxyk:
            hme__mqg |= alias_map[nzpi__qrgv]
        lives_n_aliases = lives | hme__mqg | arg_aliases
        if type(stmt) in remove_dead_extensions:
            evjgb__wsen = remove_dead_extensions[type(stmt)]
            stmt = evjgb__wsen(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                axf__aqsjy = True
                continue
        if isinstance(stmt, ir.Assign):
            bhttx__rfa = stmt.target
            knf__ykwa = stmt.value
            if bhttx__rfa.name not in lives:
                if has_no_side_effect(knf__ykwa, lives_n_aliases, call_table):
                    axf__aqsjy = True
                    continue
                if isinstance(knf__ykwa, ir.Expr
                    ) and knf__ykwa.op == 'call' and call_table[knf__ykwa.
                    func.name] == ['astype']:
                    tcwy__rkpti = guard(get_definition, func_ir, knf__ykwa.func
                        )
                    if (tcwy__rkpti is not None and tcwy__rkpti.op ==
                        'getattr' and isinstance(typemap[tcwy__rkpti.value.
                        name], types.Array) and tcwy__rkpti.attr == 'astype'):
                        axf__aqsjy = True
                        continue
            if saved_array_analysis and bhttx__rfa.name in lives and is_expr(
                knf__ykwa, 'getattr'
                ) and knf__ykwa.attr == 'shape' and is_array_typ(typemap[
                knf__ykwa.value.name]) and knf__ykwa.value.name not in lives:
                yhhz__wzwvi = {nzpi__qrgv: neq__fbn for neq__fbn,
                    nzpi__qrgv in func_ir.blocks.items()}
                if block in yhhz__wzwvi:
                    jmzw__zrsa = yhhz__wzwvi[block]
                    gncu__smp = saved_array_analysis.get_equiv_set(jmzw__zrsa)
                    fiebj__fwqm = gncu__smp.get_equiv_set(knf__ykwa.value)
                    if fiebj__fwqm is not None:
                        for nzpi__qrgv in fiebj__fwqm:
                            if nzpi__qrgv.endswith('#0'):
                                nzpi__qrgv = nzpi__qrgv[:-2]
                            if nzpi__qrgv in typemap and is_array_typ(typemap
                                [nzpi__qrgv]) and nzpi__qrgv in lives:
                                knf__ykwa.value = ir.Var(knf__ykwa.value.
                                    scope, nzpi__qrgv, knf__ykwa.value.loc)
                                axf__aqsjy = True
                                break
            if isinstance(knf__ykwa, ir.Var
                ) and bhttx__rfa.name == knf__ykwa.name:
                axf__aqsjy = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                axf__aqsjy = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            sze__ghr = analysis.ir_extension_usedefs[type(stmt)]
            ggfh__refqp, wue__ljhmp = sze__ghr(stmt)
            lives -= wue__ljhmp
            lives |= ggfh__refqp
        else:
            lives |= {nzpi__qrgv.name for nzpi__qrgv in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                cyx__cwtqs = set()
                if isinstance(knf__ykwa, ir.Expr):
                    cyx__cwtqs = {nzpi__qrgv.name for nzpi__qrgv in
                        knf__ykwa.list_vars()}
                if bhttx__rfa.name not in cyx__cwtqs:
                    lives.remove(bhttx__rfa.name)
        mvs__vhhr.append(stmt)
    mvs__vhhr.reverse()
    block.body = mvs__vhhr
    return axf__aqsjy


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            nlf__ope, = args
            if isinstance(nlf__ope, types.IterableType):
                dtype = nlf__ope.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), nlf__ope)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    duump__vfc = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (duump__vfc, self.dtype)
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
        except LiteralTypingError as xmbus__vkgzf:
            return
    try:
        return literal(value)
    except LiteralTypingError as xmbus__vkgzf:
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
        pltv__rau = py_func.__qualname__
    except AttributeError as xmbus__vkgzf:
        pltv__rau = py_func.__name__
    qrbg__gtn = inspect.getfile(py_func)
    for cls in self._locator_classes:
        geqd__uqrlf = cls.from_function(py_func, qrbg__gtn)
        if geqd__uqrlf is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (pltv__rau, qrbg__gtn))
    self._locator = geqd__uqrlf
    ofzj__oddx = inspect.getfile(py_func)
    viwki__fda = os.path.splitext(os.path.basename(ofzj__oddx))[0]
    if qrbg__gtn.startswith('<ipython-'):
        xlun__yigom = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', viwki__fda, count=1)
        if xlun__yigom == viwki__fda:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        viwki__fda = xlun__yigom
    skeup__jawz = '%s.%s' % (viwki__fda, pltv__rau)
    qnta__zue = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(skeup__jawz, qnta__zue)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    wca__qvrs = list(filter(lambda a: self._istuple(a.name), args))
    if len(wca__qvrs) == 2 and fn.__name__ == 'add':
        sccg__hireo = self.typemap[wca__qvrs[0].name]
        ljrnj__vgi = self.typemap[wca__qvrs[1].name]
        if sccg__hireo.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wca__qvrs[1]))
        if ljrnj__vgi.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wca__qvrs[0]))
        try:
            jaoc__jqrjz = [equiv_set.get_shape(x) for x in wca__qvrs]
            if None in jaoc__jqrjz:
                return None
            lmju__zju = sum(jaoc__jqrjz, ())
            return ArrayAnalysis.AnalyzeResult(shape=lmju__zju)
        except GuardException as xmbus__vkgzf:
            return None
    idhp__dxfvp = list(filter(lambda a: self._isarray(a.name), args))
    require(len(idhp__dxfvp) > 0)
    phcuz__igkkx = [x.name for x in idhp__dxfvp]
    cqp__vpu = [self.typemap[x.name].ndim for x in idhp__dxfvp]
    wfmd__wvxd = max(cqp__vpu)
    require(wfmd__wvxd > 0)
    jaoc__jqrjz = [equiv_set.get_shape(x) for x in idhp__dxfvp]
    if any(a is None for a in jaoc__jqrjz):
        return ArrayAnalysis.AnalyzeResult(shape=idhp__dxfvp[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, idhp__dxfvp))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, jaoc__jqrjz,
        phcuz__igkkx)


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
    hxshr__aocr = code_obj.code
    wtnmz__ogs = len(hxshr__aocr.co_freevars)
    das__odqf = hxshr__aocr.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        gfcmi__qznzt, op = ir_utils.find_build_sequence(caller_ir, code_obj
            .closure)
        assert op == 'build_tuple'
        das__odqf = [nzpi__qrgv.name for nzpi__qrgv in gfcmi__qznzt]
    grp__mqe = caller_ir.func_id.func.__globals__
    try:
        grp__mqe = getattr(code_obj, 'globals', grp__mqe)
    except KeyError as xmbus__vkgzf:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    odx__gezq = []
    for x in das__odqf:
        try:
            lct__kgk = caller_ir.get_definition(x)
        except KeyError as xmbus__vkgzf:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(lct__kgk, (ir.Const, ir.Global, ir.FreeVar)):
            val = lct__kgk.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                cer__eaeh = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                grp__mqe[cer__eaeh] = bodo.jit(distributed=False)(val)
                grp__mqe[cer__eaeh].is_nested_func = True
                val = cer__eaeh
            if isinstance(val, CPUDispatcher):
                cer__eaeh = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                grp__mqe[cer__eaeh] = val
                val = cer__eaeh
            odx__gezq.append(val)
        elif isinstance(lct__kgk, ir.Expr) and lct__kgk.op == 'make_function':
            prgm__fli = convert_code_obj_to_function(lct__kgk, caller_ir)
            cer__eaeh = ir_utils.mk_unique_var('nested_func').replace('.', '_')
            grp__mqe[cer__eaeh] = bodo.jit(distributed=False)(prgm__fli)
            grp__mqe[cer__eaeh].is_nested_func = True
            odx__gezq.append(cer__eaeh)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    mzlwt__fjfx = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate
        (odx__gezq)])
    aigu__cfmy = ','.join([('c_%d' % i) for i in range(wtnmz__ogs)])
    fifv__rranu = list(hxshr__aocr.co_varnames)
    lypl__pzdc = 0
    yxsid__yplkf = hxshr__aocr.co_argcount
    bua__nncnx = caller_ir.get_definition(code_obj.defaults)
    if bua__nncnx is not None:
        if isinstance(bua__nncnx, tuple):
            d = [caller_ir.get_definition(x).value for x in bua__nncnx]
            zfu__vbt = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in bua__nncnx.items]
            zfu__vbt = tuple(d)
        lypl__pzdc = len(zfu__vbt)
    jva__tsxt = yxsid__yplkf - lypl__pzdc
    zpydu__fgdk = ','.join([('%s' % fifv__rranu[i]) for i in range(jva__tsxt)])
    if lypl__pzdc:
        pvi__wjsle = [('%s = %s' % (fifv__rranu[i + jva__tsxt], zfu__vbt[i]
            )) for i in range(lypl__pzdc)]
        zpydu__fgdk += ', '
        zpydu__fgdk += ', '.join(pvi__wjsle)
    return _create_function_from_code_obj(hxshr__aocr, mzlwt__fjfx,
        zpydu__fgdk, aigu__cfmy, grp__mqe)


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
    for qrac__qxwwy, (kikow__uopkm, jnksg__iygw) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % jnksg__iygw)
            efvr__xopqc = _pass_registry.get(kikow__uopkm).pass_inst
            if isinstance(efvr__xopqc, CompilerPass):
                self._runPass(qrac__qxwwy, efvr__xopqc, state)
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
                    pipeline_name, jnksg__iygw)
                hmeke__qczyi = self._patch_error(msg, e)
                raise hmeke__qczyi
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
    uvkjx__dit = None
    wue__ljhmp = {}

    def lookup(var, already_seen, varonly=True):
        val = wue__ljhmp.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    wweyc__rhfa = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        bhttx__rfa = stmt.target
        knf__ykwa = stmt.value
        wue__ljhmp[bhttx__rfa.name] = knf__ykwa
        if isinstance(knf__ykwa, ir.Var) and knf__ykwa.name in wue__ljhmp:
            knf__ykwa = lookup(knf__ykwa, set())
        if isinstance(knf__ykwa, ir.Expr):
            ikoe__afb = set(lookup(nzpi__qrgv, set(), True).name for
                nzpi__qrgv in knf__ykwa.list_vars())
            if name in ikoe__afb:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(knf__ykwa)]
                xjaz__cyey = [x for x, ewame__yee in args if ewame__yee.
                    name != name]
                args = [(x, ewame__yee) for x, ewame__yee in args if x !=
                    ewame__yee.name]
                uohg__xrlvt = dict(args)
                if len(xjaz__cyey) == 1:
                    uohg__xrlvt[xjaz__cyey[0]] = ir.Var(bhttx__rfa.scope, 
                        name + '#init', bhttx__rfa.loc)
                replace_vars_inner(knf__ykwa, uohg__xrlvt)
                uvkjx__dit = nodes[i:]
                break
    return uvkjx__dit


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
        dlc__ess = expand_aliases({nzpi__qrgv.name for nzpi__qrgv in stmt.
            list_vars()}, alias_map, arg_aliases)
        jmtup__wch = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        bhyj__upbp = expand_aliases({nzpi__qrgv.name for nzpi__qrgv in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        mvq__inj = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(jmtup__wch & bhyj__upbp | mvq__inj & dlc__ess) == 0:
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
    uqcf__rhyha = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            uqcf__rhyha.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                uqcf__rhyha.update(get_parfor_writes(stmt, func_ir))
    return uqcf__rhyha


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    uqcf__rhyha = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        uqcf__rhyha.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        uqcf__rhyha = {nzpi__qrgv.name for nzpi__qrgv in stmt.df_out_vars.
            values()}
        if stmt.out_key_vars is not None:
            uqcf__rhyha.update({nzpi__qrgv.name for nzpi__qrgv in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        uqcf__rhyha = {nzpi__qrgv.name for nzpi__qrgv in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        uqcf__rhyha = {nzpi__qrgv.name for nzpi__qrgv in stmt.out_data_vars
            .values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            uqcf__rhyha.update({nzpi__qrgv.name for i, nzpi__qrgv in
                enumerate(stmt.out_vars) if i not in stmt.dead_var_inds and
                i not in stmt.dead_key_var_inds})
    if is_call_assign(stmt):
        jns__moxd = guard(find_callname, func_ir, stmt.value)
        if jns__moxd in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            uqcf__rhyha.add(stmt.value.args[0].name)
        if jns__moxd == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            uqcf__rhyha.add(stmt.value.args[1].name)
    return uqcf__rhyha


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
        evjgb__wsen = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        dzp__sxdtt = evjgb__wsen.format(self, msg)
        self.args = dzp__sxdtt,
    else:
        evjgb__wsen = _termcolor.errmsg('{0}')
        dzp__sxdtt = evjgb__wsen.format(self)
        self.args = dzp__sxdtt,
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
        for aki__mal in options['distributed']:
            dist_spec[aki__mal] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for aki__mal in options['distributed_block']:
            dist_spec[aki__mal] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    mlxk__wlme = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, wiwj__ncq in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(wiwj__ncq)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    glyb__ichs = {}
    for bagwl__jqjw in reversed(inspect.getmro(cls)):
        glyb__ichs.update(bagwl__jqjw.__dict__)
    qet__sjqk, mjkt__ihoc, pnolg__znxn, gjxt__sic = {}, {}, {}, {}
    for neq__fbn, nzpi__qrgv in glyb__ichs.items():
        if isinstance(nzpi__qrgv, pytypes.FunctionType):
            qet__sjqk[neq__fbn] = nzpi__qrgv
        elif isinstance(nzpi__qrgv, property):
            mjkt__ihoc[neq__fbn] = nzpi__qrgv
        elif isinstance(nzpi__qrgv, staticmethod):
            pnolg__znxn[neq__fbn] = nzpi__qrgv
        else:
            gjxt__sic[neq__fbn] = nzpi__qrgv
    djllk__vvv = (set(qet__sjqk) | set(mjkt__ihoc) | set(pnolg__znxn)) & set(
        spec)
    if djllk__vvv:
        raise NameError('name shadowing: {0}'.format(', '.join(djllk__vvv)))
    jbaly__godpa = gjxt__sic.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(gjxt__sic)
    if gjxt__sic:
        msg = 'class members are not yet supported: {0}'
        qgmat__hkwrm = ', '.join(gjxt__sic.keys())
        raise TypeError(msg.format(qgmat__hkwrm))
    for neq__fbn, nzpi__qrgv in mjkt__ihoc.items():
        if nzpi__qrgv.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(neq__fbn))
    jit_methods = {neq__fbn: bodo.jit(returns_maybe_distributed=mlxk__wlme)
        (nzpi__qrgv) for neq__fbn, nzpi__qrgv in qet__sjqk.items()}
    jit_props = {}
    for neq__fbn, nzpi__qrgv in mjkt__ihoc.items():
        mnf__otg = {}
        if nzpi__qrgv.fget:
            mnf__otg['get'] = bodo.jit(nzpi__qrgv.fget)
        if nzpi__qrgv.fset:
            mnf__otg['set'] = bodo.jit(nzpi__qrgv.fset)
        jit_props[neq__fbn] = mnf__otg
    jit_static_methods = {neq__fbn: bodo.jit(nzpi__qrgv.__func__) for 
        neq__fbn, nzpi__qrgv in pnolg__znxn.items()}
    gtrb__xmvsa = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    fajiz__fele = dict(class_type=gtrb__xmvsa, __doc__=jbaly__godpa)
    fajiz__fele.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), fajiz__fele)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, gtrb__xmvsa)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(gtrb__xmvsa, typingctx, targetctx).register()
    as_numba_type.register(cls, gtrb__xmvsa.instance_type)
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
    grkl__falg = ','.join('{0}:{1}'.format(neq__fbn, nzpi__qrgv) for 
        neq__fbn, nzpi__qrgv in struct.items())
    ecj__bjxo = ','.join('{0}:{1}'.format(neq__fbn, nzpi__qrgv) for 
        neq__fbn, nzpi__qrgv in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), grkl__falg, ecj__bjxo)
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
    ndk__bpu = numba.core.typeinfer.fold_arg_vars(typevars, self.args, self
        .vararg, self.kws)
    if ndk__bpu is None:
        return
    hig__sdv, akak__hfr = ndk__bpu
    for a in itertools.chain(hig__sdv, akak__hfr.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, hig__sdv, akak__hfr)
    except ForceLiteralArg as e:
        butki__utl = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(butki__utl, self.kws)
        xpo__gcno = set()
        ykpo__ghuje = set()
        eezwa__pxin = {}
        for qrac__qxwwy in e.requested_args:
            blj__qctnq = typeinfer.func_ir.get_definition(folded[qrac__qxwwy])
            if isinstance(blj__qctnq, ir.Arg):
                xpo__gcno.add(blj__qctnq.index)
                if blj__qctnq.index in e.file_infos:
                    eezwa__pxin[blj__qctnq.index] = e.file_infos[blj__qctnq
                        .index]
            else:
                ykpo__ghuje.add(qrac__qxwwy)
        if ykpo__ghuje:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif xpo__gcno:
            raise ForceLiteralArg(xpo__gcno, loc=self.loc, file_infos=
                eezwa__pxin)
    if sig is None:
        arye__elpml = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in hig__sdv]
        args += [('%s=%s' % (neq__fbn, nzpi__qrgv)) for neq__fbn,
            nzpi__qrgv in sorted(akak__hfr.items())]
        nik__fot = arye__elpml.format(fnty, ', '.join(map(str, args)))
        wdvsc__cce = context.explain_function_type(fnty)
        msg = '\n'.join([nik__fot, wdvsc__cce])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        gewnz__etalc = context.unify_pairs(sig.recvr, fnty.this)
        if gewnz__etalc is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if gewnz__etalc is not None and gewnz__etalc.is_precise():
            geqvh__tfr = fnty.copy(this=gewnz__etalc)
            typeinfer.propagate_refined_type(self.func, geqvh__tfr)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            rnzgh__qheq = target.getone()
            if context.unify_pairs(rnzgh__qheq, sig.return_type
                ) == rnzgh__qheq:
                sig = sig.replace(return_type=rnzgh__qheq)
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
        rwso__lqvc = '*other* must be a {} but got a {} instead'
        raise TypeError(rwso__lqvc.format(ForceLiteralArg, type(other)))
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
    tdq__ztuh = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for neq__fbn, nzpi__qrgv in kwargs.items():
        xjws__akig = None
        try:
            ntl__polbl = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var
                ('dummy'), loc)
            func_ir._definitions[ntl__polbl.name] = [nzpi__qrgv]
            xjws__akig = get_const_value_inner(func_ir, ntl__polbl)
            func_ir._definitions.pop(ntl__polbl.name)
            if isinstance(xjws__akig, str):
                xjws__akig = sigutils._parse_signature_string(xjws__akig)
            if isinstance(xjws__akig, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {neq__fbn} is annotated as type class {xjws__akig}."""
                    )
            assert isinstance(xjws__akig, types.Type)
            if isinstance(xjws__akig, (types.List, types.Set)):
                xjws__akig = xjws__akig.copy(reflected=False)
            tdq__ztuh[neq__fbn] = xjws__akig
        except BodoError as xmbus__vkgzf:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(xjws__akig, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(nzpi__qrgv, ir.Global):
                    msg = f'Global {nzpi__qrgv.name!r} is not defined.'
                if isinstance(nzpi__qrgv, ir.FreeVar):
                    msg = f'Freevar {nzpi__qrgv.name!r} is not defined.'
            if isinstance(nzpi__qrgv, ir.Expr) and nzpi__qrgv.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=neq__fbn, msg=msg, loc=loc)
    for name, typ in tdq__ztuh.items():
        self._legalize_arg_type(name, typ, loc)
    return tdq__ztuh


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
    hmog__iki = inst.arg
    assert hmog__iki > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(hmog__iki)]))
    tmps = [state.make_temp() for _ in range(hmog__iki - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    dzu__rbxpr = ir.Global('format', format, loc=self.loc)
    self.store(value=dzu__rbxpr, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    fzzfy__zomqn = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=fzzfy__zomqn, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    hmog__iki = inst.arg
    assert hmog__iki > 0, 'invalid BUILD_STRING count'
    raux__fooi = self.get(strings[0])
    for other, krdi__rzk in zip(strings[1:], tmps):
        other = self.get(other)
        cykta__mzyof = ir.Expr.binop(operator.add, lhs=raux__fooi, rhs=
            other, loc=self.loc)
        self.store(cykta__mzyof, krdi__rzk)
        raux__fooi = self.get(krdi__rzk)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    gispw__esrl = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, gispw__esrl])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    gzrgf__xkrwp = mk_unique_var(f'{var_name}')
    bixh__gsr = gzrgf__xkrwp.replace('<', '_').replace('>', '_')
    bixh__gsr = bixh__gsr.replace('.', '_').replace('$', '_v')
    return bixh__gsr


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
                afcg__weiz = get_overload_const_str(val2)
                if afcg__weiz != 'ns':
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
        ajdw__oqggy = states['defmap']
        if len(ajdw__oqggy) == 0:
            pdb__ixb = assign.target
            numba.core.ssa._logger.debug('first assign: %s', pdb__ixb)
            if pdb__ixb.name not in scope.localvars:
                pdb__ixb = scope.define(assign.target.name, loc=assign.loc)
        else:
            pdb__ixb = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=pdb__ixb, value=assign.value, loc=assign.loc)
        ajdw__oqggy[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    tgbb__vusoe = []
    for neq__fbn, nzpi__qrgv in typing.npydecl.registry.globals:
        if neq__fbn == func:
            tgbb__vusoe.append(nzpi__qrgv)
    for neq__fbn, nzpi__qrgv in typing.templates.builtin_registry.globals:
        if neq__fbn == func:
            tgbb__vusoe.append(nzpi__qrgv)
    if len(tgbb__vusoe) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return tgbb__vusoe


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    dggxm__dpk = {}
    hrkn__efkjc = find_topo_order(blocks)
    ibka__cerhq = {}
    for jmzw__zrsa in hrkn__efkjc:
        block = blocks[jmzw__zrsa]
        mvs__vhhr = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                bhttx__rfa = stmt.target.name
                knf__ykwa = stmt.value
                if (knf__ykwa.op == 'getattr' and knf__ykwa.attr in
                    arr_math and isinstance(typemap[knf__ykwa.value.name],
                    types.npytypes.Array)):
                    knf__ykwa = stmt.value
                    mxdk__aokc = knf__ykwa.value
                    dggxm__dpk[bhttx__rfa] = mxdk__aokc
                    scope = mxdk__aokc.scope
                    loc = mxdk__aokc.loc
                    crich__jcd = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[crich__jcd.name] = types.misc.Module(numpy)
                    amd__svfsl = ir.Global('np', numpy, loc)
                    lgnsc__bsd = ir.Assign(amd__svfsl, crich__jcd, loc)
                    knf__ykwa.value = crich__jcd
                    mvs__vhhr.append(lgnsc__bsd)
                    func_ir._definitions[crich__jcd.name] = [amd__svfsl]
                    func = getattr(numpy, knf__ykwa.attr)
                    lekv__uakki = get_np_ufunc_typ_lst(func)
                    ibka__cerhq[bhttx__rfa] = lekv__uakki
                if (knf__ykwa.op == 'call' and knf__ykwa.func.name in
                    dggxm__dpk):
                    mxdk__aokc = dggxm__dpk[knf__ykwa.func.name]
                    fipf__dvyun = calltypes.pop(knf__ykwa)
                    nkh__bgoa = fipf__dvyun.args[:len(knf__ykwa.args)]
                    fckn__irz = {name: typemap[nzpi__qrgv.name] for name,
                        nzpi__qrgv in knf__ykwa.kws}
                    bwdy__cfhvs = ibka__cerhq[knf__ykwa.func.name]
                    jzpa__deyth = None
                    for qjau__jph in bwdy__cfhvs:
                        try:
                            jzpa__deyth = qjau__jph.get_call_type(typingctx,
                                [typemap[mxdk__aokc.name]] + list(nkh__bgoa
                                ), fckn__irz)
                            typemap.pop(knf__ykwa.func.name)
                            typemap[knf__ykwa.func.name] = qjau__jph
                            calltypes[knf__ykwa] = jzpa__deyth
                            break
                        except Exception as xmbus__vkgzf:
                            pass
                    if jzpa__deyth is None:
                        raise TypeError(
                            f'No valid template found for {knf__ykwa.func.name}'
                            )
                    knf__ykwa.args = [mxdk__aokc] + knf__ykwa.args
            mvs__vhhr.append(stmt)
        block.body = mvs__vhhr


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    etznc__izhk = ufunc.nin
    scc__duhp = ufunc.nout
    jva__tsxt = ufunc.nargs
    assert jva__tsxt == etznc__izhk + scc__duhp
    if len(args) < etznc__izhk:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            etznc__izhk))
    if len(args) > jva__tsxt:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), jva__tsxt))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    wqcxb__rtco = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    bbcmp__fdwhp = max(wqcxb__rtco)
    api__uadn = args[etznc__izhk:]
    if not all(d == bbcmp__fdwhp for d in wqcxb__rtco[etznc__izhk:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(msmxj__gkxk, types.ArrayCompatible) and not
        isinstance(msmxj__gkxk, types.Bytes) for msmxj__gkxk in api__uadn):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(msmxj__gkxk.mutable for msmxj__gkxk in api__uadn):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    lnjkm__uvk = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    hmb__nxgam = None
    if bbcmp__fdwhp > 0 and len(api__uadn) < ufunc.nout:
        hmb__nxgam = 'C'
        rpty__ewlqh = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in rpty__ewlqh and 'F' in rpty__ewlqh:
            hmb__nxgam = 'F'
    return lnjkm__uvk, api__uadn, bbcmp__fdwhp, hmb__nxgam


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
        wbg__kbw = 'Dict.key_type cannot be of type {}'
        raise TypingError(wbg__kbw.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        wbg__kbw = 'Dict.value_type cannot be of type {}'
        raise TypingError(wbg__kbw.format(valty))
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
    wjra__xgp = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[wjra__xgp]
        return impl, args
    except KeyError as xmbus__vkgzf:
        pass
    impl, args = self._build_impl(wjra__xgp, args, kws)
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
        bse__tqy = find_topo_order(parfor.loop_body)
    xyfxd__urs = bse__tqy[0]
    mrgrk__rqx = {}
    _update_parfor_get_setitems(parfor.loop_body[xyfxd__urs].body, parfor.
        index_var, alias_map, mrgrk__rqx, lives_n_aliases)
    rqh__rxmg = set(mrgrk__rqx.keys())
    for cad__rypmr in bse__tqy:
        if cad__rypmr == xyfxd__urs:
            continue
        for stmt in parfor.loop_body[cad__rypmr].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            grogo__kktgq = set(nzpi__qrgv.name for nzpi__qrgv in stmt.
                list_vars())
            szj__txgqv = grogo__kktgq & rqh__rxmg
            for a in szj__txgqv:
                mrgrk__rqx.pop(a, None)
    for cad__rypmr in bse__tqy:
        if cad__rypmr == xyfxd__urs:
            continue
        block = parfor.loop_body[cad__rypmr]
        vhrm__tvt = mrgrk__rqx.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            vhrm__tvt, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    zwp__gex = max(blocks.keys())
    liysp__jcr, uvdc__nwc = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    pqw__jtnv = ir.Jump(liysp__jcr, ir.Loc('parfors_dummy', -1))
    blocks[zwp__gex].body.append(pqw__jtnv)
    kcia__rynbs = compute_cfg_from_blocks(blocks)
    jctbt__wsos = compute_use_defs(blocks)
    sdc__znw = compute_live_map(kcia__rynbs, blocks, jctbt__wsos.usemap,
        jctbt__wsos.defmap)
    alias_set = set(alias_map.keys())
    for jmzw__zrsa, block in blocks.items():
        mvs__vhhr = []
        eunji__doo = {nzpi__qrgv.name for nzpi__qrgv in block.terminator.
            list_vars()}
        for mvp__wzfh, xewyo__gni in kcia__rynbs.successors(jmzw__zrsa):
            eunji__doo |= sdc__znw[mvp__wzfh]
        for stmt in reversed(block.body):
            hme__mqg = eunji__doo & alias_set
            for nzpi__qrgv in hme__mqg:
                eunji__doo |= alias_map[nzpi__qrgv]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in eunji__doo and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                jns__moxd = guard(find_callname, func_ir, stmt.value)
                if jns__moxd == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in eunji__doo and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            eunji__doo |= {nzpi__qrgv.name for nzpi__qrgv in stmt.list_vars()}
            mvs__vhhr.append(stmt)
        mvs__vhhr.reverse()
        block.body = mvs__vhhr
    typemap.pop(uvdc__nwc.name)
    blocks[zwp__gex].body.pop()

    def trim_empty_parfor_branches(parfor):
        wnwhr__wyou = False
        blocks = parfor.loop_body.copy()
        for jmzw__zrsa, block in blocks.items():
            if len(block.body):
                fmv__sppu = block.body[-1]
                if isinstance(fmv__sppu, ir.Branch):
                    if len(blocks[fmv__sppu.truebr].body) == 1 and len(blocks
                        [fmv__sppu.falsebr].body) == 1:
                        zezjy__ycg = blocks[fmv__sppu.truebr].body[0]
                        emot__iswdk = blocks[fmv__sppu.falsebr].body[0]
                        if isinstance(zezjy__ycg, ir.Jump) and isinstance(
                            emot__iswdk, ir.Jump
                            ) and zezjy__ycg.target == emot__iswdk.target:
                            parfor.loop_body[jmzw__zrsa].body[-1] = ir.Jump(
                                zezjy__ycg.target, fmv__sppu.loc)
                            wnwhr__wyou = True
                    elif len(blocks[fmv__sppu.truebr].body) == 1:
                        zezjy__ycg = blocks[fmv__sppu.truebr].body[0]
                        if isinstance(zezjy__ycg, ir.Jump
                            ) and zezjy__ycg.target == fmv__sppu.falsebr:
                            parfor.loop_body[jmzw__zrsa].body[-1] = ir.Jump(
                                zezjy__ycg.target, fmv__sppu.loc)
                            wnwhr__wyou = True
                    elif len(blocks[fmv__sppu.falsebr].body) == 1:
                        emot__iswdk = blocks[fmv__sppu.falsebr].body[0]
                        if isinstance(emot__iswdk, ir.Jump
                            ) and emot__iswdk.target == fmv__sppu.truebr:
                            parfor.loop_body[jmzw__zrsa].body[-1] = ir.Jump(
                                emot__iswdk.target, fmv__sppu.loc)
                            wnwhr__wyou = True
        return wnwhr__wyou
    wnwhr__wyou = True
    while wnwhr__wyou:
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
        wnwhr__wyou = trim_empty_parfor_branches(parfor)
    jos__znc = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        jos__znc &= len(block.body) == 0
    if jos__znc:
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
    zkajb__vzks = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                zkajb__vzks += 1
                parfor = stmt
                pno__few = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = pno__few.scope
                loc = ir.Loc('parfors_dummy', -1)
                zwe__fsk = ir.Var(scope, mk_unique_var('$const'), loc)
                pno__few.body.append(ir.Assign(ir.Const(0, loc), zwe__fsk, loc)
                    )
                pno__few.body.append(ir.Return(zwe__fsk, loc))
                kcia__rynbs = compute_cfg_from_blocks(parfor.loop_body)
                for nov__nbw in kcia__rynbs.dead_nodes():
                    del parfor.loop_body[nov__nbw]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                pno__few = parfor.loop_body[max(parfor.loop_body.keys())]
                pno__few.body.pop()
                pno__few.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return zkajb__vzks


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
            iqqvd__hxbyi = self.overloads.get(tuple(args))
            if iqqvd__hxbyi is not None:
                return iqqvd__hxbyi.entry_point
            self._pre_compile(args, return_type, flags)
            pcc__iyqr = self.func_ir
            cyzkb__uhlei = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=cyzkb__uhlei):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=pcc__iyqr, args=args,
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
        fjlys__gapg = copy.deepcopy(flags)
        fjlys__gapg.no_rewrites = True

        def compile_local(the_ir, the_flags):
            sqf__junoh = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return sqf__junoh.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        gjxus__snat = compile_local(func_ir, fjlys__gapg)
        qmkj__ejn = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    qmkj__ejn = compile_local(func_ir, flags)
                except Exception as xmbus__vkgzf:
                    pass
        if qmkj__ejn is not None:
            cres = qmkj__ejn
        else:
            cres = gjxus__snat
        return cres
    else:
        sqf__junoh = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return sqf__junoh.compile_ir(func_ir=func_ir, lifted=lifted,
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
    lmnm__azxbd = self.get_data_type(typ.dtype)
    iigkb__mgdi = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        iigkb__mgdi):
        uzkpd__tepba = ary.ctypes.data
        qfaju__aclki = self.add_dynamic_addr(builder, uzkpd__tepba, info=
            str(type(uzkpd__tepba)))
        xfaz__aylj = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        xzc__qkjw = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            xzc__qkjw = xzc__qkjw.view('int64')
        val = bytearray(xzc__qkjw.data)
        kpcok__olnxw = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)),
            val)
        qfaju__aclki = cgutils.global_constant(builder, '.const.array.data',
            kpcok__olnxw)
        qfaju__aclki.align = self.get_abi_alignment(lmnm__azxbd)
        xfaz__aylj = None
    abf__pmlbs = self.get_value_type(types.intp)
    ujn__xsfl = [self.get_constant(types.intp, gky__fin) for gky__fin in
        ary.shape]
    piexj__dtthh = lir.Constant(lir.ArrayType(abf__pmlbs, len(ujn__xsfl)),
        ujn__xsfl)
    cawfm__jqrzg = [self.get_constant(types.intp, gky__fin) for gky__fin in
        ary.strides]
    zwn__ackk = lir.Constant(lir.ArrayType(abf__pmlbs, len(cawfm__jqrzg)),
        cawfm__jqrzg)
    ardv__wbyh = self.get_constant(types.intp, ary.dtype.itemsize)
    ztgfl__ttn = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        ztgfl__ttn, ardv__wbyh, qfaju__aclki.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), piexj__dtthh, zwn__ackk])


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
    kfui__wxtw = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    vpw__wxlkm = lir.Function(module, kfui__wxtw, name='nrt_atomic_{0}'.
        format(op))
    [diis__naqz] = vpw__wxlkm.args
    wqp__auxy = vpw__wxlkm.append_basic_block()
    builder = lir.IRBuilder(wqp__auxy)
    thj__hfec = lir.Constant(_word_type, 1)
    if False:
        cavan__mba = builder.atomic_rmw(op, diis__naqz, thj__hfec, ordering
            =ordering)
        res = getattr(builder, op)(cavan__mba, thj__hfec)
        builder.ret(res)
    else:
        cavan__mba = builder.load(diis__naqz)
        hfz__bkqc = getattr(builder, op)(cavan__mba, thj__hfec)
        bjkdl__nuu = builder.icmp_signed('!=', cavan__mba, lir.Constant(
            cavan__mba.type, -1))
        with cgutils.if_likely(builder, bjkdl__nuu):
            builder.store(hfz__bkqc, diis__naqz)
        builder.ret(hfz__bkqc)
    return vpw__wxlkm


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
        uadl__zql = state.targetctx.codegen()
        state.library = uadl__zql.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    qxev__xlji = state.func_ir
    typemap = state.typemap
    juwo__cpgfj = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    ehe__ckvgu = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            qxev__xlji, typemap, juwo__cpgfj, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            pboqk__kxce = lowering.Lower(targetctx, library, fndesc,
                qxev__xlji, metadata=metadata)
            pboqk__kxce.lower()
            if not flags.no_cpython_wrapper:
                pboqk__kxce.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(juwo__cpgfj, (types.Optional, types.
                        Generator)):
                        pass
                    else:
                        pboqk__kxce.create_cfunc_wrapper()
            env = pboqk__kxce.env
            dty__ublg = pboqk__kxce.call_helper
            del pboqk__kxce
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, dty__ublg, cfunc=None, env=env)
        else:
            vgok__qje = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(vgok__qje, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, dty__ublg, cfunc=vgok__qje,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        ysq__vcz = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = ysq__vcz - ehe__ckvgu
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
        izl__jhpcn = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, izl__jhpcn),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            prhsw__qjiu.do_break()
        fybpz__jojr = c.builder.icmp_signed('!=', izl__jhpcn, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(fybpz__jojr, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, izl__jhpcn)
                c.pyapi.decref(izl__jhpcn)
                prhsw__qjiu.do_break()
        c.pyapi.decref(izl__jhpcn)
    sbmkc__odx, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(sbmkc__odx, likely=True) as (qsvt__pewzx,
        vfuq__jttmn):
        with qsvt__pewzx:
            list.size = size
            grd__qzzx = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                grd__qzzx), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        grd__qzzx))
                    with cgutils.for_range(c.builder, size) as prhsw__qjiu:
                        itemobj = c.pyapi.list_getitem(obj, prhsw__qjiu.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        uvuyb__bufep = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(uvuyb__bufep.is_error,
                            likely=False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            prhsw__qjiu.do_break()
                        list.setitem(prhsw__qjiu.index, uvuyb__bufep.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with vfuq__jttmn:
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
    pmony__uta, ctjm__pjewd, sle__jzgq, idz__olhvt, jkmc__rrsuy = (
        compile_time_get_string_data(literal_string))
    wyzmg__tccwm = builder.module
    gv = context.insert_const_bytes(wyzmg__tccwm, pmony__uta)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        ctjm__pjewd), context.get_constant(types.int32, sle__jzgq), context
        .get_constant(types.uint32, idz__olhvt), context.get_constant(
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
    ywm__wpis = None
    if isinstance(shape, types.Integer):
        ywm__wpis = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(gky__fin, (types.Integer, types.IntEnumMember)) for
            gky__fin in shape):
            ywm__wpis = len(shape)
    return ywm__wpis


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
            ywm__wpis = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if ywm__wpis == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(ywm__wpis))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            phcuz__igkkx = self._get_names(x)
            if len(phcuz__igkkx) != 0:
                return phcuz__igkkx[0]
            return phcuz__igkkx
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    phcuz__igkkx = self._get_names(obj)
    if len(phcuz__igkkx) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(phcuz__igkkx[0])


def get_equiv_set(self, obj):
    phcuz__igkkx = self._get_names(obj)
    if len(phcuz__igkkx) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(phcuz__igkkx[0])


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
    psdqs__dwo = []
    for mtcqw__fpz in func_ir.arg_names:
        if mtcqw__fpz in typemap and isinstance(typemap[mtcqw__fpz], types.
            containers.UniTuple) and typemap[mtcqw__fpz].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(mtcqw__fpz))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for msvhp__twas in func_ir.blocks.values():
        for stmt in msvhp__twas.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    raeyb__potk = getattr(val, 'code', None)
                    if raeyb__potk is not None:
                        if getattr(val, 'closure', None) is not None:
                            ser__noek = '<creating a function from a closure>'
                            cykta__mzyof = ''
                        else:
                            ser__noek = raeyb__potk.co_name
                            cykta__mzyof = '(%s) ' % ser__noek
                    else:
                        ser__noek = '<could not ascertain use case>'
                        cykta__mzyof = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (ser__noek, cykta__mzyof))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                lpylo__ewss = False
                if isinstance(val, pytypes.FunctionType):
                    lpylo__ewss = val in {numba.gdb, numba.gdb_init}
                if not lpylo__ewss:
                    lpylo__ewss = getattr(val, '_name', '') == 'gdb_internal'
                if lpylo__ewss:
                    psdqs__dwo.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    xacsk__olfxs = func_ir.get_definition(var)
                    ymu__ghnz = guard(find_callname, func_ir, xacsk__olfxs)
                    if ymu__ghnz and ymu__ghnz[1] == 'numpy':
                        ty = getattr(numpy, ymu__ghnz[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    lft__jyvdd = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(lft__jyvdd), loc=stmt.loc)
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
    if len(psdqs__dwo) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        blgj__xbao = '\n'.join([x.strformat() for x in psdqs__dwo])
        raise errors.UnsupportedError(msg % blgj__xbao)


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
    neq__fbn, nzpi__qrgv = next(iter(val.items()))
    jjnul__bqb = typeof_impl(neq__fbn, c)
    tikyi__grpa = typeof_impl(nzpi__qrgv, c)
    if jjnul__bqb is None or tikyi__grpa is None:
        raise ValueError(
            f'Cannot type dict element type {type(neq__fbn)}, {type(nzpi__qrgv)}'
            )
    return types.DictType(jjnul__bqb, tikyi__grpa)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    fjxm__akdn = cgutils.alloca_once_value(c.builder, val)
    oecid__yfg = c.pyapi.object_hasattr_string(val, '_opaque')
    ajfoj__enkk = c.builder.icmp_unsigned('==', oecid__yfg, lir.Constant(
        oecid__yfg.type, 0))
    ycc__fswo = typ.key_type
    yfsr__azr = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(ycc__fswo, yfsr__azr)

    def copy_dict(out_dict, in_dict):
        for neq__fbn, nzpi__qrgv in in_dict.items():
            out_dict[neq__fbn] = nzpi__qrgv
    with c.builder.if_then(ajfoj__enkk):
        vnw__nhfe = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        avkhj__bkdbz = c.pyapi.call_function_objargs(vnw__nhfe, [])
        dhkuf__kxh = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(dhkuf__kxh, [avkhj__bkdbz, val])
        c.builder.store(avkhj__bkdbz, fjxm__akdn)
    val = c.builder.load(fjxm__akdn)
    otshl__mqz = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    xef__lki = c.pyapi.object_type(val)
    nhzuu__ildg = c.builder.icmp_unsigned('==', xef__lki, otshl__mqz)
    with c.builder.if_else(nhzuu__ildg) as (zak__korx, lga__ksrqs):
        with zak__korx:
            qzypc__xtj = c.pyapi.object_getattr_string(val, '_opaque')
            putqc__ygc = types.MemInfoPointer(types.voidptr)
            uvuyb__bufep = c.unbox(putqc__ygc, qzypc__xtj)
            mi = uvuyb__bufep.value
            rcept__brcl = putqc__ygc, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *rcept__brcl)
            hpti__wab = context.get_constant_null(rcept__brcl[1])
            args = mi, hpti__wab
            cgsq__chd, dmqwi__gfpz = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, dmqwi__gfpz)
            c.pyapi.decref(qzypc__xtj)
            xrx__ygn = c.builder.basic_block
        with lga__ksrqs:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", xef__lki, otshl__mqz)
            oslxe__wib = c.builder.basic_block
    pcjc__mza = c.builder.phi(dmqwi__gfpz.type)
    ulws__zpt = c.builder.phi(cgsq__chd.type)
    pcjc__mza.add_incoming(dmqwi__gfpz, xrx__ygn)
    pcjc__mza.add_incoming(dmqwi__gfpz.type(None), oslxe__wib)
    ulws__zpt.add_incoming(cgsq__chd, xrx__ygn)
    ulws__zpt.add_incoming(cgutils.true_bit, oslxe__wib)
    c.pyapi.decref(otshl__mqz)
    c.pyapi.decref(xef__lki)
    with c.builder.if_then(ajfoj__enkk):
        c.pyapi.decref(val)
    return NativeValue(pcjc__mza, is_error=ulws__zpt)


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
    kikdh__chjtk = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=kikdh__chjtk, name=updatevar)
    xjwhe__yftm = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=xjwhe__yftm, name=res)


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
        for neq__fbn, nzpi__qrgv in other.items():
            d[neq__fbn] = nzpi__qrgv
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
    cykta__mzyof = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(cykta__mzyof, res)


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
    rpipo__lhxhy = PassManager(name)
    if state.func_ir is None:
        rpipo__lhxhy.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            rpipo__lhxhy.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        rpipo__lhxhy.add_pass(FixupArgs, 'fix up args')
    rpipo__lhxhy.add_pass(IRProcessing, 'processing IR')
    rpipo__lhxhy.add_pass(WithLifting, 'Handle with contexts')
    rpipo__lhxhy.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        rpipo__lhxhy.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        rpipo__lhxhy.add_pass(DeadBranchPrune, 'dead branch pruning')
        rpipo__lhxhy.add_pass(GenericRewrites, 'nopython rewrites')
    rpipo__lhxhy.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    rpipo__lhxhy.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        rpipo__lhxhy.add_pass(DeadBranchPrune, 'dead branch pruning')
    rpipo__lhxhy.add_pass(FindLiterallyCalls, 'find literally calls')
    rpipo__lhxhy.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        rpipo__lhxhy.add_pass(ReconstructSSA, 'ssa')
    rpipo__lhxhy.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    rpipo__lhxhy.finalize()
    return rpipo__lhxhy


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
    a, fuh__tnolt = args
    if isinstance(a, types.List) and isinstance(fuh__tnolt, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(fuh__tnolt, types.List):
        return signature(fuh__tnolt, types.intp, fuh__tnolt)


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
        gqkv__gwtn, xdby__fnb = 0, 1
    else:
        gqkv__gwtn, xdby__fnb = 1, 0
    rjrg__dzk = ListInstance(context, builder, sig.args[gqkv__gwtn], args[
        gqkv__gwtn])
    tgm__ixpzd = rjrg__dzk.size
    ram__cnjrk = args[xdby__fnb]
    grd__qzzx = lir.Constant(ram__cnjrk.type, 0)
    ram__cnjrk = builder.select(cgutils.is_neg_int(builder, ram__cnjrk),
        grd__qzzx, ram__cnjrk)
    ztgfl__ttn = builder.mul(ram__cnjrk, tgm__ixpzd)
    argan__mxp = ListInstance.allocate(context, builder, sig.return_type,
        ztgfl__ttn)
    argan__mxp.size = ztgfl__ttn
    with cgutils.for_range_slice(builder, grd__qzzx, ztgfl__ttn, tgm__ixpzd,
        inc=True) as (exida__wro, _):
        with cgutils.for_range(builder, tgm__ixpzd) as prhsw__qjiu:
            value = rjrg__dzk.getitem(prhsw__qjiu.index)
            argan__mxp.setitem(builder.add(prhsw__qjiu.index, exida__wro),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, argan__mxp.value
        )


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
    mel__ehx = first.unify(self, second)
    if mel__ehx is not None:
        return mel__ehx
    mel__ehx = second.unify(self, first)
    if mel__ehx is not None:
        return mel__ehx
    ubk__owpk = self.can_convert(fromty=first, toty=second)
    if ubk__owpk is not None and ubk__owpk <= Conversion.safe:
        return second
    ubk__owpk = self.can_convert(fromty=second, toty=first)
    if ubk__owpk is not None and ubk__owpk <= Conversion.safe:
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
    ztgfl__ttn = payload.used
    listobj = c.pyapi.list_new(ztgfl__ttn)
    sbmkc__odx = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(sbmkc__odx, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(ztgfl__ttn
            .type, 0))
        with payload._iterate() as prhsw__qjiu:
            i = c.builder.load(index)
            item = prhsw__qjiu.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return sbmkc__odx, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    auqr__mogip = h.type
    tpf__ibuwj = self.mask
    dtype = self._ty.dtype
    ofmvk__unqub = context.typing_context
    fnty = ofmvk__unqub.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(ofmvk__unqub, (dtype, dtype), {})
    tppv__wehh = context.get_function(fnty, sig)
    xou__usg = ir.Constant(auqr__mogip, 1)
    hqz__bcrj = ir.Constant(auqr__mogip, 5)
    htfx__lov = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, tpf__ibuwj))
    if for_insert:
        tqfdt__qmju = tpf__ibuwj.type(-1)
        jvrpa__twnau = cgutils.alloca_once_value(builder, tqfdt__qmju)
    gul__jrx = builder.append_basic_block('lookup.body')
    mcby__jgt = builder.append_basic_block('lookup.found')
    qamzn__dcggy = builder.append_basic_block('lookup.not_found')
    owmda__vbxou = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        gnsk__zwpu = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, gnsk__zwpu)):
            htn__rbn = tppv__wehh(builder, (item, entry.key))
            with builder.if_then(htn__rbn):
                builder.branch(mcby__jgt)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, gnsk__zwpu)):
            builder.branch(qamzn__dcggy)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, gnsk__zwpu)):
                tmvc__ngj = builder.load(jvrpa__twnau)
                tmvc__ngj = builder.select(builder.icmp_unsigned('==',
                    tmvc__ngj, tqfdt__qmju), i, tmvc__ngj)
                builder.store(tmvc__ngj, jvrpa__twnau)
    with cgutils.for_range(builder, ir.Constant(auqr__mogip, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, xou__usg)
        i = builder.and_(i, tpf__ibuwj)
        builder.store(i, index)
    builder.branch(gul__jrx)
    with builder.goto_block(gul__jrx):
        i = builder.load(index)
        check_entry(i)
        iizx__aaatk = builder.load(htfx__lov)
        iizx__aaatk = builder.lshr(iizx__aaatk, hqz__bcrj)
        i = builder.add(xou__usg, builder.mul(i, hqz__bcrj))
        i = builder.and_(tpf__ibuwj, builder.add(i, iizx__aaatk))
        builder.store(i, index)
        builder.store(iizx__aaatk, htfx__lov)
        builder.branch(gul__jrx)
    with builder.goto_block(qamzn__dcggy):
        if for_insert:
            i = builder.load(index)
            tmvc__ngj = builder.load(jvrpa__twnau)
            i = builder.select(builder.icmp_unsigned('==', tmvc__ngj,
                tqfdt__qmju), i, tmvc__ngj)
            builder.store(i, index)
        builder.branch(owmda__vbxou)
    with builder.goto_block(mcby__jgt):
        builder.branch(owmda__vbxou)
    builder.position_at_end(owmda__vbxou)
    lpylo__ewss = builder.phi(ir.IntType(1), 'found')
    lpylo__ewss.add_incoming(cgutils.true_bit, mcby__jgt)
    lpylo__ewss.add_incoming(cgutils.false_bit, qamzn__dcggy)
    return lpylo__ewss, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    vfara__tnef = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    sfh__bqbry = payload.used
    xou__usg = ir.Constant(sfh__bqbry.type, 1)
    sfh__bqbry = payload.used = builder.add(sfh__bqbry, xou__usg)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, vfara__tnef), likely=True):
        payload.fill = builder.add(payload.fill, xou__usg)
    if do_resize:
        self.upsize(sfh__bqbry)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    lpylo__ewss, i = payload._lookup(item, h, for_insert=True)
    hetgx__vsypc = builder.not_(lpylo__ewss)
    with builder.if_then(hetgx__vsypc):
        entry = payload.get_entry(i)
        vfara__tnef = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        sfh__bqbry = payload.used
        xou__usg = ir.Constant(sfh__bqbry.type, 1)
        sfh__bqbry = payload.used = builder.add(sfh__bqbry, xou__usg)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, vfara__tnef), likely=True):
            payload.fill = builder.add(payload.fill, xou__usg)
        if do_resize:
            self.upsize(sfh__bqbry)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    sfh__bqbry = payload.used
    xou__usg = ir.Constant(sfh__bqbry.type, 1)
    sfh__bqbry = payload.used = self._builder.sub(sfh__bqbry, xou__usg)
    if do_resize:
        self.downsize(sfh__bqbry)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    wff__wrvpv = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, wff__wrvpv)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    bgsn__hkt = payload
    sbmkc__odx = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(sbmkc__odx), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with bgsn__hkt._iterate() as prhsw__qjiu:
        entry = prhsw__qjiu.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(bgsn__hkt.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as prhsw__qjiu:
        entry = prhsw__qjiu.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    sbmkc__odx = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(sbmkc__odx), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    sbmkc__odx = cgutils.alloca_once_value(builder, cgutils.true_bit)
    auqr__mogip = context.get_value_type(types.intp)
    grd__qzzx = ir.Constant(auqr__mogip, 0)
    xou__usg = ir.Constant(auqr__mogip, 1)
    mhkd__zprw = context.get_data_type(types.SetPayload(self._ty))
    tmevj__rmhk = context.get_abi_sizeof(mhkd__zprw)
    ybx__pdf = self._entrysize
    tmevj__rmhk -= ybx__pdf
    ykejb__qyj, tnw__bctlu = cgutils.muladd_with_overflow(builder, nentries,
        ir.Constant(auqr__mogip, ybx__pdf), ir.Constant(auqr__mogip,
        tmevj__rmhk))
    with builder.if_then(tnw__bctlu, likely=False):
        builder.store(cgutils.false_bit, sbmkc__odx)
    with builder.if_then(builder.load(sbmkc__odx), likely=True):
        if realloc:
            pce__qyvqf = self._set.meminfo
            diis__naqz = context.nrt.meminfo_varsize_alloc(builder,
                pce__qyvqf, size=ykejb__qyj)
            saxj__zmtf = cgutils.is_null(builder, diis__naqz)
        else:
            zmzlg__jvca = _imp_dtor(context, builder.module, self._ty)
            pce__qyvqf = context.nrt.meminfo_new_varsize_dtor(builder,
                ykejb__qyj, builder.bitcast(zmzlg__jvca, cgutils.voidptr_t))
            saxj__zmtf = cgutils.is_null(builder, pce__qyvqf)
        with builder.if_else(saxj__zmtf, likely=False) as (mrog__kwepq,
            qsvt__pewzx):
            with mrog__kwepq:
                builder.store(cgutils.false_bit, sbmkc__odx)
            with qsvt__pewzx:
                if not realloc:
                    self._set.meminfo = pce__qyvqf
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, ykejb__qyj, 255)
                payload.used = grd__qzzx
                payload.fill = grd__qzzx
                payload.finger = grd__qzzx
                kijm__bzmh = builder.sub(nentries, xou__usg)
                payload.mask = kijm__bzmh
    return builder.load(sbmkc__odx)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    sbmkc__odx = cgutils.alloca_once_value(builder, cgutils.true_bit)
    auqr__mogip = context.get_value_type(types.intp)
    grd__qzzx = ir.Constant(auqr__mogip, 0)
    xou__usg = ir.Constant(auqr__mogip, 1)
    mhkd__zprw = context.get_data_type(types.SetPayload(self._ty))
    tmevj__rmhk = context.get_abi_sizeof(mhkd__zprw)
    ybx__pdf = self._entrysize
    tmevj__rmhk -= ybx__pdf
    tpf__ibuwj = src_payload.mask
    nentries = builder.add(xou__usg, tpf__ibuwj)
    ykejb__qyj = builder.add(ir.Constant(auqr__mogip, tmevj__rmhk), builder
        .mul(ir.Constant(auqr__mogip, ybx__pdf), nentries))
    with builder.if_then(builder.load(sbmkc__odx), likely=True):
        zmzlg__jvca = _imp_dtor(context, builder.module, self._ty)
        pce__qyvqf = context.nrt.meminfo_new_varsize_dtor(builder,
            ykejb__qyj, builder.bitcast(zmzlg__jvca, cgutils.voidptr_t))
        saxj__zmtf = cgutils.is_null(builder, pce__qyvqf)
        with builder.if_else(saxj__zmtf, likely=False) as (mrog__kwepq,
            qsvt__pewzx):
            with mrog__kwepq:
                builder.store(cgutils.false_bit, sbmkc__odx)
            with qsvt__pewzx:
                self._set.meminfo = pce__qyvqf
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = grd__qzzx
                payload.mask = tpf__ibuwj
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, ybx__pdf)
                with src_payload._iterate() as prhsw__qjiu:
                    context.nrt.incref(builder, self._ty.dtype, prhsw__qjiu
                        .entry.key)
    return builder.load(sbmkc__odx)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    ckf__hlzs = context.get_value_type(types.voidptr)
    yfo__vvdus = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [ckf__hlzs, yfo__vvdus, ckf__hlzs])
    wxmx__mvh = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=wxmx__mvh)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        xals__mom = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, xals__mom)
        with payload._iterate() as prhsw__qjiu:
            entry = prhsw__qjiu.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    zfqkd__upxvw, = sig.args
    gfcmi__qznzt, = args
    hvkno__hdlo = numba.core.imputils.call_len(context, builder,
        zfqkd__upxvw, gfcmi__qznzt)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, hvkno__hdlo)
    with numba.core.imputils.for_iter(context, builder, zfqkd__upxvw,
        gfcmi__qznzt) as prhsw__qjiu:
        inst.add(prhsw__qjiu.value)
        context.nrt.decref(builder, set_type.dtype, prhsw__qjiu.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    zfqkd__upxvw = sig.args[1]
    gfcmi__qznzt = args[1]
    hvkno__hdlo = numba.core.imputils.call_len(context, builder,
        zfqkd__upxvw, gfcmi__qznzt)
    if hvkno__hdlo is not None:
        amusu__cfby = builder.add(inst.payload.used, hvkno__hdlo)
        inst.upsize(amusu__cfby)
    with numba.core.imputils.for_iter(context, builder, zfqkd__upxvw,
        gfcmi__qznzt) as prhsw__qjiu:
        kqp__mpz = context.cast(builder, prhsw__qjiu.value, zfqkd__upxvw.
            dtype, inst.dtype)
        inst.add(kqp__mpz)
        context.nrt.decref(builder, zfqkd__upxvw.dtype, prhsw__qjiu.value)
    if hvkno__hdlo is not None:
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
    dchy__rzjpw = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, dchy__rzjpw, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    vgok__qje = target_context.get_executable(library, fndesc, env)
    kwms__iwsqw = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=vgok__qje, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return kwms__iwsqw


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
