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
    xqho__nahbt = context.get_python_api(builder)
    return xqho__nahbt.unserialize(xqho__nahbt.serialize_object(pyval))


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
        pev__axan = ', '.join('e{}'.format(hvfwf__xpivz) for hvfwf__xpivz in
            range(len(args)))
        if pev__axan:
            pev__axan += ', '
        ssevv__osmpe = ', '.join("{} = ''".format(xyl__llm) for xyl__llm in
            kws.keys())
        srj__ysva = f'def format_stub(string, {pev__axan} {ssevv__osmpe}):\n'
        srj__ysva += '    pass\n'
        czmzj__kad = {}
        exec(srj__ysva, {}, czmzj__kad)
        myor__zmxzm = czmzj__kad['format_stub']
        vbrc__iquj = numba.core.utils.pysignature(myor__zmxzm)
        dqtbi__xhfy = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, dqtbi__xhfy).replace(pysig=vbrc__iquj)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for jddqv__uwku in ('logging.Logger', 'logging.RootLogger'):
        for uji__nwplp in func_names:
            akwv__myv = f'@bound_function("{jddqv__uwku}.{uji__nwplp}")\n'
            akwv__myv += (
                f'def resolve_{uji__nwplp}(self, logger_typ, args, kws):\n')
            akwv__myv += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(akwv__myv)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for rlm__ylt in logging_logger_unsupported_attrs:
        edco__gzpz = 'logging.Logger.' + rlm__ylt
        overload_attribute(LoggingLoggerType, rlm__ylt)(
            create_unsupported_overload(edco__gzpz))
    for rspvy__czae in logging_logger_unsupported_methods:
        edco__gzpz = 'logging.Logger.' + rspvy__czae
        overload_method(LoggingLoggerType, rspvy__czae)(
            create_unsupported_overload(edco__gzpz))


_install_logging_logger_unsupported_objects()
