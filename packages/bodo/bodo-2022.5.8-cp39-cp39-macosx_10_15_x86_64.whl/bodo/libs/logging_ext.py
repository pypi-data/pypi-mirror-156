"""
JIT support for Python's logging module
"""
import logging
import numba
from numba.core import types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import bound_function
from numba.core.typing.templates import AttributeTemplate, infer_getattr, signature
from numba.extending import NativeValue, box, models, overload_attribute, overload_method, register_model, typeof_impl, unbox
from bodo.utils.typing import create_unsupported_overload, gen_objmode_attr_overload


class LoggingLoggerType(types.Type):

    def __init__(self, is_root=False):
        self.is_root = is_root
        super(LoggingLoggerType, self).__init__(name=
            f'LoggingLoggerType(is_root={is_root})')


@typeof_impl.register(logging.RootLogger)
@typeof_impl.register(logging.Logger)
def typeof_logging(val, c):
    if isinstance(val, logging.RootLogger):
        return LoggingLoggerType(is_root=True)
    else:
        return LoggingLoggerType(is_root=False)


register_model(LoggingLoggerType)(models.OpaqueModel)


@box(LoggingLoggerType)
def box_logging_logger(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(LoggingLoggerType)
def unbox_logging_logger(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@lower_constant(LoggingLoggerType)
def lower_constant_logger(context, builder, ty, pyval):
    tqh__dzj = context.get_python_api(builder)
    return tqh__dzj.unserialize(tqh__dzj.serialize_object(pyval))


gen_objmode_attr_overload(LoggingLoggerType, 'level', None, types.int64)
gen_objmode_attr_overload(LoggingLoggerType, 'name', None, 'unicode_type')
gen_objmode_attr_overload(LoggingLoggerType, 'propagate', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'disabled', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'parent', None,
    LoggingLoggerType())
gen_objmode_attr_overload(LoggingLoggerType, 'root', None,
    LoggingLoggerType(is_root=True))


@infer_getattr
class LoggingLoggerAttribute(AttributeTemplate):
    key = LoggingLoggerType

    def _resolve_helper(self, logger_typ, args, kws):
        kws = dict(kws)
        dyn__gfnr = ', '.join('e{}'.format(ifljh__flcf) for ifljh__flcf in
            range(len(args)))
        if dyn__gfnr:
            dyn__gfnr += ', '
        fqimh__rwww = ', '.join("{} = ''".format(nch__mxazy) for nch__mxazy in
            kws.keys())
        nhr__zgww = f'def format_stub(string, {dyn__gfnr} {fqimh__rwww}):\n'
        nhr__zgww += '    pass\n'
        cxrbq__scs = {}
        exec(nhr__zgww, {}, cxrbq__scs)
        qlsf__kocft = cxrbq__scs['format_stub']
        xqnu__qxlgk = numba.core.utils.pysignature(qlsf__kocft)
        kbcex__dhgwi = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, kbcex__dhgwi).replace(pysig=xqnu__qxlgk)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for qnnu__lvl in ('logging.Logger', 'logging.RootLogger'):
        for vkaiv__sjy in func_names:
            oyny__qpsq = f'@bound_function("{qnnu__lvl}.{vkaiv__sjy}")\n'
            oyny__qpsq += (
                f'def resolve_{vkaiv__sjy}(self, logger_typ, args, kws):\n')
            oyny__qpsq += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(oyny__qpsq)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for xlxbz__gena in logging_logger_unsupported_attrs:
        jlw__jgm = 'logging.Logger.' + xlxbz__gena
        overload_attribute(LoggingLoggerType, xlxbz__gena)(
            create_unsupported_overload(jlw__jgm))
    for hhyth__yof in logging_logger_unsupported_methods:
        jlw__jgm = 'logging.Logger.' + hhyth__yof
        overload_method(LoggingLoggerType, hhyth__yof)(
            create_unsupported_overload(jlw__jgm))


_install_logging_logger_unsupported_objects()
