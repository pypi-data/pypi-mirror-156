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
    eyjy__oro = keyword_expr.items.copy()
    ecii__bsd = keyword_expr.value_indexes
    for iull__ibh, vrb__rztpb in ecii__bsd.items():
        eyjy__oro[vrb__rztpb] = iull__ibh, eyjy__oro[vrb__rztpb][1]
    new_body[buildmap_idx] = None
    return eyjy__oro


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    lbx__agoay = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    eyjy__oro = []
    vyboa__iyq = buildmap_idx + 1
    while vyboa__iyq <= search_end:
        ztu__ijw = body[vyboa__iyq]
        if not (isinstance(ztu__ijw, ir.Assign) and isinstance(ztu__ijw.
            value, ir.Const)):
            raise UnsupportedError(lbx__agoay)
        veei__omwvc = ztu__ijw.target.name
        glter__ejg = ztu__ijw.value.value
        vyboa__iyq += 1
        ykhh__rade = True
        while vyboa__iyq <= search_end and ykhh__rade:
            ngra__wsh = body[vyboa__iyq]
            if (isinstance(ngra__wsh, ir.Assign) and isinstance(ngra__wsh.
                value, ir.Expr) and ngra__wsh.value.op == 'getattr' and 
                ngra__wsh.value.value.name == buildmap_name and ngra__wsh.
                value.attr == '__setitem__'):
                ykhh__rade = False
            else:
                vyboa__iyq += 1
        if ykhh__rade or vyboa__iyq == search_end:
            raise UnsupportedError(lbx__agoay)
        hwxu__tksp = body[vyboa__iyq + 1]
        if not (isinstance(hwxu__tksp, ir.Assign) and isinstance(hwxu__tksp
            .value, ir.Expr) and hwxu__tksp.value.op == 'call' and 
            hwxu__tksp.value.func.name == ngra__wsh.target.name and len(
            hwxu__tksp.value.args) == 2 and hwxu__tksp.value.args[0].name ==
            veei__omwvc):
            raise UnsupportedError(lbx__agoay)
        mls__lhb = hwxu__tksp.value.args[1]
        eyjy__oro.append((glter__ejg, mls__lhb))
        new_body[vyboa__iyq] = None
        new_body[vyboa__iyq + 1] = None
        vyboa__iyq += 2
    return eyjy__oro


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    lbx__agoay = 'CALL_FUNCTION_EX with **kwargs not supported'
    vyboa__iyq = 0
    hey__iyiwc = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        knez__zub = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        knez__zub = vararg_stmt.target.name
    tcmz__tndh = True
    while search_end >= vyboa__iyq and tcmz__tndh:
        lwh__bkdy = body[search_end]
        if (isinstance(lwh__bkdy, ir.Assign) and lwh__bkdy.target.name ==
            knez__zub and isinstance(lwh__bkdy.value, ir.Expr) and 
            lwh__bkdy.value.op == 'build_tuple' and not lwh__bkdy.value.items):
            tcmz__tndh = False
            new_body[search_end] = None
        else:
            if search_end == vyboa__iyq or not (isinstance(lwh__bkdy, ir.
                Assign) and lwh__bkdy.target.name == knez__zub and
                isinstance(lwh__bkdy.value, ir.Expr) and lwh__bkdy.value.op ==
                'binop' and lwh__bkdy.value.fn == operator.add):
                raise UnsupportedError(lbx__agoay)
            rrxcp__khazw = lwh__bkdy.value.lhs.name
            zfhl__ookew = lwh__bkdy.value.rhs.name
            snb__uwifx = body[search_end - 1]
            if not (isinstance(snb__uwifx, ir.Assign) and isinstance(
                snb__uwifx.value, ir.Expr) and snb__uwifx.value.op ==
                'build_tuple' and len(snb__uwifx.value.items) == 1):
                raise UnsupportedError(lbx__agoay)
            if snb__uwifx.target.name == rrxcp__khazw:
                knez__zub = zfhl__ookew
            elif snb__uwifx.target.name == zfhl__ookew:
                knez__zub = rrxcp__khazw
            else:
                raise UnsupportedError(lbx__agoay)
            hey__iyiwc.append(snb__uwifx.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            yopq__upqrs = True
            while search_end >= vyboa__iyq and yopq__upqrs:
                tnlkn__lzmvj = body[search_end]
                if isinstance(tnlkn__lzmvj, ir.Assign
                    ) and tnlkn__lzmvj.target.name == knez__zub:
                    yopq__upqrs = False
                else:
                    search_end -= 1
    if tcmz__tndh:
        raise UnsupportedError(lbx__agoay)
    return hey__iyiwc[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    lbx__agoay = 'CALL_FUNCTION_EX with **kwargs not supported'
    for qhtu__sek in func_ir.blocks.values():
        bkx__yzoae = False
        new_body = []
        for bsxb__poqgk, amye__gyel in enumerate(qhtu__sek.body):
            if (isinstance(amye__gyel, ir.Assign) and isinstance(amye__gyel
                .value, ir.Expr) and amye__gyel.value.op == 'call' and 
                amye__gyel.value.varkwarg is not None):
                bkx__yzoae = True
                sny__cbqv = amye__gyel.value
                args = sny__cbqv.args
                eyjy__oro = sny__cbqv.kws
                zhbmq__qvt = sny__cbqv.vararg
                wms__zifs = sny__cbqv.varkwarg
                ovkm__mbif = bsxb__poqgk - 1
                wxgno__gxcbq = ovkm__mbif
                wud__yqspx = None
                jhrvt__ctqe = True
                while wxgno__gxcbq >= 0 and jhrvt__ctqe:
                    wud__yqspx = qhtu__sek.body[wxgno__gxcbq]
                    if isinstance(wud__yqspx, ir.Assign
                        ) and wud__yqspx.target.name == wms__zifs.name:
                        jhrvt__ctqe = False
                    else:
                        wxgno__gxcbq -= 1
                if eyjy__oro or jhrvt__ctqe or not (isinstance(wud__yqspx.
                    value, ir.Expr) and wud__yqspx.value.op == 'build_map'):
                    raise UnsupportedError(lbx__agoay)
                if wud__yqspx.value.items:
                    eyjy__oro = _call_function_ex_replace_kws_small(wud__yqspx
                        .value, new_body, wxgno__gxcbq)
                else:
                    eyjy__oro = _call_function_ex_replace_kws_large(qhtu__sek
                        .body, wms__zifs.name, wxgno__gxcbq, bsxb__poqgk - 
                        1, new_body)
                ovkm__mbif = wxgno__gxcbq
                if zhbmq__qvt is not None:
                    if args:
                        raise UnsupportedError(lbx__agoay)
                    jni__xofln = ovkm__mbif
                    fiio__fmaa = None
                    jhrvt__ctqe = True
                    while jni__xofln >= 0 and jhrvt__ctqe:
                        fiio__fmaa = qhtu__sek.body[jni__xofln]
                        if isinstance(fiio__fmaa, ir.Assign
                            ) and fiio__fmaa.target.name == zhbmq__qvt.name:
                            jhrvt__ctqe = False
                        else:
                            jni__xofln -= 1
                    if jhrvt__ctqe:
                        raise UnsupportedError(lbx__agoay)
                    if isinstance(fiio__fmaa.value, ir.Expr
                        ) and fiio__fmaa.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(fiio__fmaa
                            .value, new_body, jni__xofln)
                    else:
                        args = _call_function_ex_replace_args_large(fiio__fmaa,
                            qhtu__sek.body, new_body, jni__xofln)
                xibiu__zova = ir.Expr.call(sny__cbqv.func, args, eyjy__oro,
                    sny__cbqv.loc, target=sny__cbqv.target)
                if amye__gyel.target.name in func_ir._definitions and len(
                    func_ir._definitions[amye__gyel.target.name]) == 1:
                    func_ir._definitions[amye__gyel.target.name].clear()
                func_ir._definitions[amye__gyel.target.name].append(xibiu__zova
                    )
                amye__gyel = ir.Assign(xibiu__zova, amye__gyel.target,
                    amye__gyel.loc)
            new_body.append(amye__gyel)
        if bkx__yzoae:
            qhtu__sek.body = [noshn__wqx for noshn__wqx in new_body if 
                noshn__wqx is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for qhtu__sek in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        bkx__yzoae = False
        for bsxb__poqgk, amye__gyel in enumerate(qhtu__sek.body):
            vxgx__qssa = True
            ywvv__zhia = None
            if isinstance(amye__gyel, ir.Assign) and isinstance(amye__gyel.
                value, ir.Expr):
                if amye__gyel.value.op == 'build_map':
                    ywvv__zhia = amye__gyel.target.name
                    lit_old_idx[amye__gyel.target.name] = bsxb__poqgk
                    lit_new_idx[amye__gyel.target.name] = bsxb__poqgk
                    map_updates[amye__gyel.target.name
                        ] = amye__gyel.value.items.copy()
                    vxgx__qssa = False
                elif amye__gyel.value.op == 'call' and bsxb__poqgk > 0:
                    ugy__rrm = amye__gyel.value.func.name
                    ngra__wsh = qhtu__sek.body[bsxb__poqgk - 1]
                    args = amye__gyel.value.args
                    if (isinstance(ngra__wsh, ir.Assign) and ngra__wsh.
                        target.name == ugy__rrm and isinstance(ngra__wsh.
                        value, ir.Expr) and ngra__wsh.value.op == 'getattr' and
                        ngra__wsh.value.value.name in lit_old_idx):
                        ljo__ulkd = ngra__wsh.value.value.name
                        axcm__cexhi = ngra__wsh.value.attr
                        if axcm__cexhi == '__setitem__':
                            vxgx__qssa = False
                            map_updates[ljo__ulkd].append(args)
                            new_body[-1] = None
                        elif axcm__cexhi == 'update' and args[0
                            ].name in lit_old_idx:
                            vxgx__qssa = False
                            map_updates[ljo__ulkd].extend(map_updates[args[
                                0].name])
                            new_body[-1] = None
                        if not vxgx__qssa:
                            lit_new_idx[ljo__ulkd] = bsxb__poqgk
                            func_ir._definitions[ngra__wsh.target.name].remove(
                                ngra__wsh.value)
            if not (isinstance(amye__gyel, ir.Assign) and isinstance(
                amye__gyel.value, ir.Expr) and amye__gyel.value.op ==
                'getattr' and amye__gyel.value.value.name in lit_old_idx and
                amye__gyel.value.attr in ('__setitem__', 'update')):
                for jcvim__mfea in amye__gyel.list_vars():
                    if (jcvim__mfea.name in lit_old_idx and jcvim__mfea.
                        name != ywvv__zhia):
                        _insert_build_map(func_ir, jcvim__mfea.name,
                            qhtu__sek.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if vxgx__qssa:
                new_body.append(amye__gyel)
            else:
                func_ir._definitions[amye__gyel.target.name].remove(amye__gyel
                    .value)
                bkx__yzoae = True
                new_body.append(None)
        sihym__jijuu = list(lit_old_idx.keys())
        for cnwdo__bovsx in sihym__jijuu:
            _insert_build_map(func_ir, cnwdo__bovsx, qhtu__sek.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if bkx__yzoae:
            qhtu__sek.body = [noshn__wqx for noshn__wqx in new_body if 
                noshn__wqx is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    sdqz__uej = lit_old_idx[name]
    dkv__tkle = lit_new_idx[name]
    ucju__zmp = map_updates[name]
    new_body[dkv__tkle] = _build_new_build_map(func_ir, name, old_body,
        sdqz__uej, ucju__zmp)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    apl__rhqa = old_body[old_lineno]
    stk__tjo = apl__rhqa.target
    lfmjj__owp = apl__rhqa.value
    gdiu__cwzo = []
    yngpq__mzaod = []
    for czst__vrlux in new_items:
        hzwfl__xmsvu, fkk__nqz = czst__vrlux
        akv__rwr = guard(get_definition, func_ir, hzwfl__xmsvu)
        if isinstance(akv__rwr, (ir.Const, ir.Global, ir.FreeVar)):
            gdiu__cwzo.append(akv__rwr.value)
        ikxbh__znj = guard(get_definition, func_ir, fkk__nqz)
        if isinstance(ikxbh__znj, (ir.Const, ir.Global, ir.FreeVar)):
            yngpq__mzaod.append(ikxbh__znj.value)
        else:
            yngpq__mzaod.append(numba.core.interpreter._UNKNOWN_VALUE(
                fkk__nqz.name))
    ecii__bsd = {}
    if len(gdiu__cwzo) == len(new_items):
        nhebs__bxpbd = {noshn__wqx: alfw__kajgm for noshn__wqx, alfw__kajgm in
            zip(gdiu__cwzo, yngpq__mzaod)}
        for bsxb__poqgk, hzwfl__xmsvu in enumerate(gdiu__cwzo):
            ecii__bsd[hzwfl__xmsvu] = bsxb__poqgk
    else:
        nhebs__bxpbd = None
    wcqe__lfuzf = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=nhebs__bxpbd, value_indexes=ecii__bsd, loc=lfmjj__owp.loc
        )
    func_ir._definitions[name].append(wcqe__lfuzf)
    return ir.Assign(wcqe__lfuzf, ir.Var(stk__tjo.scope, name, stk__tjo.loc
        ), wcqe__lfuzf.loc)
