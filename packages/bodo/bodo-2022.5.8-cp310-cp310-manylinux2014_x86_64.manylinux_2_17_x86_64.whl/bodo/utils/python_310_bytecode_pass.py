"""
transforms the IR to handle bytecode issues in Python 3.10. This
should be removed once https://github.com/numba/numba/pull/7866
is included in Numba 0.56
"""
import operator
import numba
from numba.core import ir
from numba.core.compiler_machinery import FunctionPass, register_pass
from numba.core.errors import UnsupportedError
from numba.core.ir_utils import dprint_func_ir, get_definition, guard


@register_pass(mutates_CFG=False, analysis_only=False)
class Bodo310ByteCodePass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dprint_func_ir(state.func_ir,
            'starting Bodo 3.10 Bytecode optimizations pass')
        peep_hole_call_function_ex_to_call_function_kw(state.func_ir)
        peep_hole_fuse_dict_add_updates(state.func_ir)
        return True


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    psj__kqw = keyword_expr.items.copy()
    pta__eurp = keyword_expr.value_indexes
    for rtz__jwrpl, euzj__qfkog in pta__eurp.items():
        psj__kqw[euzj__qfkog] = rtz__jwrpl, psj__kqw[euzj__qfkog][1]
    new_body[buildmap_idx] = None
    return psj__kqw


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    tgq__mney = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    psj__kqw = []
    zskfp__pby = buildmap_idx + 1
    while zskfp__pby <= search_end:
        pud__uatmf = body[zskfp__pby]
        if not (isinstance(pud__uatmf, ir.Assign) and isinstance(pud__uatmf
            .value, ir.Const)):
            raise UnsupportedError(tgq__mney)
        pjl__mckth = pud__uatmf.target.name
        xjwt__hrkme = pud__uatmf.value.value
        zskfp__pby += 1
        rfrh__klt = True
        while zskfp__pby <= search_end and rfrh__klt:
            jppmy__wrlcm = body[zskfp__pby]
            if (isinstance(jppmy__wrlcm, ir.Assign) and isinstance(
                jppmy__wrlcm.value, ir.Expr) and jppmy__wrlcm.value.op ==
                'getattr' and jppmy__wrlcm.value.value.name ==
                buildmap_name and jppmy__wrlcm.value.attr == '__setitem__'):
                rfrh__klt = False
            else:
                zskfp__pby += 1
        if rfrh__klt or zskfp__pby == search_end:
            raise UnsupportedError(tgq__mney)
        lsrvy__mtry = body[zskfp__pby + 1]
        if not (isinstance(lsrvy__mtry, ir.Assign) and isinstance(
            lsrvy__mtry.value, ir.Expr) and lsrvy__mtry.value.op == 'call' and
            lsrvy__mtry.value.func.name == jppmy__wrlcm.target.name and len
            (lsrvy__mtry.value.args) == 2 and lsrvy__mtry.value.args[0].
            name == pjl__mckth):
            raise UnsupportedError(tgq__mney)
        hyrg__mlh = lsrvy__mtry.value.args[1]
        psj__kqw.append((xjwt__hrkme, hyrg__mlh))
        new_body[zskfp__pby] = None
        new_body[zskfp__pby + 1] = None
        zskfp__pby += 2
    return psj__kqw


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    tgq__mney = 'CALL_FUNCTION_EX with **kwargs not supported'
    zskfp__pby = 0
    kfy__qnqb = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        uwepw__jyqul = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        uwepw__jyqul = vararg_stmt.target.name
    fttp__zyb = True
    while search_end >= zskfp__pby and fttp__zyb:
        zgg__ojhq = body[search_end]
        if (isinstance(zgg__ojhq, ir.Assign) and zgg__ojhq.target.name ==
            uwepw__jyqul and isinstance(zgg__ojhq.value, ir.Expr) and 
            zgg__ojhq.value.op == 'build_tuple' and not zgg__ojhq.value.items):
            fttp__zyb = False
            new_body[search_end] = None
        else:
            if search_end == zskfp__pby or not (isinstance(zgg__ojhq, ir.
                Assign) and zgg__ojhq.target.name == uwepw__jyqul and
                isinstance(zgg__ojhq.value, ir.Expr) and zgg__ojhq.value.op ==
                'binop' and zgg__ojhq.value.fn == operator.add):
                raise UnsupportedError(tgq__mney)
            tan__cptb = zgg__ojhq.value.lhs.name
            uacat__goy = zgg__ojhq.value.rhs.name
            tyohm__uhtp = body[search_end - 1]
            if not (isinstance(tyohm__uhtp, ir.Assign) and isinstance(
                tyohm__uhtp.value, ir.Expr) and tyohm__uhtp.value.op ==
                'build_tuple' and len(tyohm__uhtp.value.items) == 1):
                raise UnsupportedError(tgq__mney)
            if tyohm__uhtp.target.name == tan__cptb:
                uwepw__jyqul = uacat__goy
            elif tyohm__uhtp.target.name == uacat__goy:
                uwepw__jyqul = tan__cptb
            else:
                raise UnsupportedError(tgq__mney)
            kfy__qnqb.append(tyohm__uhtp.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            kmjwf__vmhw = True
            while search_end >= zskfp__pby and kmjwf__vmhw:
                xgcd__hzhga = body[search_end]
                if isinstance(xgcd__hzhga, ir.Assign
                    ) and xgcd__hzhga.target.name == uwepw__jyqul:
                    kmjwf__vmhw = False
                else:
                    search_end -= 1
    if fttp__zyb:
        raise UnsupportedError(tgq__mney)
    return kfy__qnqb[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    tgq__mney = 'CALL_FUNCTION_EX with **kwargs not supported'
    for hbp__blkl in func_ir.blocks.values():
        jzmkk__pqhha = False
        new_body = []
        for ahyt__zstkh, iygbk__qyenx in enumerate(hbp__blkl.body):
            if (isinstance(iygbk__qyenx, ir.Assign) and isinstance(
                iygbk__qyenx.value, ir.Expr) and iygbk__qyenx.value.op ==
                'call' and iygbk__qyenx.value.varkwarg is not None):
                jzmkk__pqhha = True
                wrhin__nmz = iygbk__qyenx.value
                args = wrhin__nmz.args
                psj__kqw = wrhin__nmz.kws
                xxcv__rrfu = wrhin__nmz.vararg
                eygc__mkb = wrhin__nmz.varkwarg
                attlr__cwlti = ahyt__zstkh - 1
                jsx__brdln = attlr__cwlti
                jwtt__rlw = None
                xre__jvl = True
                while jsx__brdln >= 0 and xre__jvl:
                    jwtt__rlw = hbp__blkl.body[jsx__brdln]
                    if isinstance(jwtt__rlw, ir.Assign
                        ) and jwtt__rlw.target.name == eygc__mkb.name:
                        xre__jvl = False
                    else:
                        jsx__brdln -= 1
                if psj__kqw or xre__jvl or not (isinstance(jwtt__rlw.value,
                    ir.Expr) and jwtt__rlw.value.op == 'build_map'):
                    raise UnsupportedError(tgq__mney)
                if jwtt__rlw.value.items:
                    psj__kqw = _call_function_ex_replace_kws_small(jwtt__rlw
                        .value, new_body, jsx__brdln)
                else:
                    psj__kqw = _call_function_ex_replace_kws_large(hbp__blkl
                        .body, eygc__mkb.name, jsx__brdln, ahyt__zstkh - 1,
                        new_body)
                attlr__cwlti = jsx__brdln
                if xxcv__rrfu is not None:
                    if args:
                        raise UnsupportedError(tgq__mney)
                    mbiug__ihpa = attlr__cwlti
                    nrxai__onavy = None
                    xre__jvl = True
                    while mbiug__ihpa >= 0 and xre__jvl:
                        nrxai__onavy = hbp__blkl.body[mbiug__ihpa]
                        if isinstance(nrxai__onavy, ir.Assign
                            ) and nrxai__onavy.target.name == xxcv__rrfu.name:
                            xre__jvl = False
                        else:
                            mbiug__ihpa -= 1
                    if xre__jvl:
                        raise UnsupportedError(tgq__mney)
                    if isinstance(nrxai__onavy.value, ir.Expr
                        ) and nrxai__onavy.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(
                            nrxai__onavy.value, new_body, mbiug__ihpa)
                    else:
                        args = _call_function_ex_replace_args_large(
                            nrxai__onavy, hbp__blkl.body, new_body, mbiug__ihpa
                            )
                ektyr__ztc = ir.Expr.call(wrhin__nmz.func, args, psj__kqw,
                    wrhin__nmz.loc, target=wrhin__nmz.target)
                if iygbk__qyenx.target.name in func_ir._definitions and len(
                    func_ir._definitions[iygbk__qyenx.target.name]) == 1:
                    func_ir._definitions[iygbk__qyenx.target.name].clear()
                func_ir._definitions[iygbk__qyenx.target.name].append(
                    ektyr__ztc)
                iygbk__qyenx = ir.Assign(ektyr__ztc, iygbk__qyenx.target,
                    iygbk__qyenx.loc)
            new_body.append(iygbk__qyenx)
        if jzmkk__pqhha:
            hbp__blkl.body = [dzfg__nja for dzfg__nja in new_body if 
                dzfg__nja is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for hbp__blkl in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        jzmkk__pqhha = False
        for ahyt__zstkh, iygbk__qyenx in enumerate(hbp__blkl.body):
            quza__tdcus = True
            tmowp__swkx = None
            if isinstance(iygbk__qyenx, ir.Assign) and isinstance(iygbk__qyenx
                .value, ir.Expr):
                if iygbk__qyenx.value.op == 'build_map':
                    tmowp__swkx = iygbk__qyenx.target.name
                    lit_old_idx[iygbk__qyenx.target.name] = ahyt__zstkh
                    lit_new_idx[iygbk__qyenx.target.name] = ahyt__zstkh
                    map_updates[iygbk__qyenx.target.name
                        ] = iygbk__qyenx.value.items.copy()
                    quza__tdcus = False
                elif iygbk__qyenx.value.op == 'call' and ahyt__zstkh > 0:
                    gsuop__augai = iygbk__qyenx.value.func.name
                    jppmy__wrlcm = hbp__blkl.body[ahyt__zstkh - 1]
                    args = iygbk__qyenx.value.args
                    if (isinstance(jppmy__wrlcm, ir.Assign) and 
                        jppmy__wrlcm.target.name == gsuop__augai and
                        isinstance(jppmy__wrlcm.value, ir.Expr) and 
                        jppmy__wrlcm.value.op == 'getattr' and jppmy__wrlcm
                        .value.value.name in lit_old_idx):
                        wmwd__pmhgh = jppmy__wrlcm.value.value.name
                        lfb__euyz = jppmy__wrlcm.value.attr
                        if lfb__euyz == '__setitem__':
                            quza__tdcus = False
                            map_updates[wmwd__pmhgh].append(args)
                            new_body[-1] = None
                        elif lfb__euyz == 'update' and args[0
                            ].name in lit_old_idx:
                            quza__tdcus = False
                            map_updates[wmwd__pmhgh].extend(map_updates[
                                args[0].name])
                            new_body[-1] = None
                        if not quza__tdcus:
                            lit_new_idx[wmwd__pmhgh] = ahyt__zstkh
                            func_ir._definitions[jppmy__wrlcm.target.name
                                ].remove(jppmy__wrlcm.value)
            if not (isinstance(iygbk__qyenx, ir.Assign) and isinstance(
                iygbk__qyenx.value, ir.Expr) and iygbk__qyenx.value.op ==
                'getattr' and iygbk__qyenx.value.value.name in lit_old_idx and
                iygbk__qyenx.value.attr in ('__setitem__', 'update')):
                for grym__bmp in iygbk__qyenx.list_vars():
                    if (grym__bmp.name in lit_old_idx and grym__bmp.name !=
                        tmowp__swkx):
                        _insert_build_map(func_ir, grym__bmp.name,
                            hbp__blkl.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if quza__tdcus:
                new_body.append(iygbk__qyenx)
            else:
                func_ir._definitions[iygbk__qyenx.target.name].remove(
                    iygbk__qyenx.value)
                jzmkk__pqhha = True
                new_body.append(None)
        cjfi__uax = list(lit_old_idx.keys())
        for xwu__uzmc in cjfi__uax:
            _insert_build_map(func_ir, xwu__uzmc, hbp__blkl.body, new_body,
                lit_old_idx, lit_new_idx, map_updates)
        if jzmkk__pqhha:
            hbp__blkl.body = [dzfg__nja for dzfg__nja in new_body if 
                dzfg__nja is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    qlw__lkjm = lit_old_idx[name]
    uuzf__qewe = lit_new_idx[name]
    pebw__dst = map_updates[name]
    new_body[uuzf__qewe] = _build_new_build_map(func_ir, name, old_body,
        qlw__lkjm, pebw__dst)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    mtveu__typ = old_body[old_lineno]
    lvk__ukre = mtveu__typ.target
    ggj__filia = mtveu__typ.value
    gah__xpgb = []
    ohgs__vcuim = []
    for fgjc__xrb in new_items:
        wvn__iju, ntv__rwsk = fgjc__xrb
        omkxi__bcuxa = guard(get_definition, func_ir, wvn__iju)
        if isinstance(omkxi__bcuxa, (ir.Const, ir.Global, ir.FreeVar)):
            gah__xpgb.append(omkxi__bcuxa.value)
        ono__gssnc = guard(get_definition, func_ir, ntv__rwsk)
        if isinstance(ono__gssnc, (ir.Const, ir.Global, ir.FreeVar)):
            ohgs__vcuim.append(ono__gssnc.value)
        else:
            ohgs__vcuim.append(numba.core.interpreter._UNKNOWN_VALUE(
                ntv__rwsk.name))
    pta__eurp = {}
    if len(gah__xpgb) == len(new_items):
        ioti__qqcs = {dzfg__nja: wbg__iuq for dzfg__nja, wbg__iuq in zip(
            gah__xpgb, ohgs__vcuim)}
        for ahyt__zstkh, wvn__iju in enumerate(gah__xpgb):
            pta__eurp[wvn__iju] = ahyt__zstkh
    else:
        ioti__qqcs = None
    tlo__wtx = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=ioti__qqcs, value_indexes=pta__eurp, loc=ggj__filia.loc)
    func_ir._definitions[name].append(tlo__wtx)
    return ir.Assign(tlo__wtx, ir.Var(lvk__ukre.scope, name, lvk__ukre.loc),
        tlo__wtx.loc)
