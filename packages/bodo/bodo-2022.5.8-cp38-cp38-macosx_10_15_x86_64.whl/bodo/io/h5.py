"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        ufyy__apsf = self._get_h5_type(lhs, rhs)
        if ufyy__apsf is not None:
            nren__yipmj = str(ufyy__apsf.dtype)
            vtlne__qnil = 'def _h5_read_impl(dset, index):\n'
            vtlne__qnil += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(ufyy__apsf.ndim, nren__yipmj))
            gzd__krmzu = {}
            exec(vtlne__qnil, {}, gzd__krmzu)
            kah__yvera = gzd__krmzu['_h5_read_impl']
            gqa__apan = compile_to_numba_ir(kah__yvera, {'bodo': bodo}
                ).blocks.popitem()[1]
            xjqbo__cpzb = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(gqa__apan, [rhs.value, xjqbo__cpzb])
            mkoc__msk = gqa__apan.body[:-3]
            mkoc__msk[-1].target = assign.target
            return mkoc__msk
        return None

    def _get_h5_type(self, lhs, rhs):
        ufyy__apsf = self._get_h5_type_locals(lhs)
        if ufyy__apsf is not None:
            return ufyy__apsf
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        xjqbo__cpzb = rhs.index if rhs.op == 'getitem' else rhs.index_var
        oad__vko = guard(find_const, self.func_ir, xjqbo__cpzb)
        require(not isinstance(oad__vko, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            btkvh__fvjie = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            uxko__uuvs = get_const_value_inner(self.func_ir, btkvh__fvjie,
                arg_types=self.arg_types)
            obj_name_list.append(uxko__uuvs)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        hmsn__fjhvo = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        vrnqe__jrsez = h5py.File(hmsn__fjhvo, 'r')
        ypmf__wcr = vrnqe__jrsez
        for uxko__uuvs in obj_name_list:
            ypmf__wcr = ypmf__wcr[uxko__uuvs]
        require(isinstance(ypmf__wcr, h5py.Dataset))
        qbjs__vmdyr = len(ypmf__wcr.shape)
        gsqmt__rhndn = numba.np.numpy_support.from_dtype(ypmf__wcr.dtype)
        vrnqe__jrsez.close()
        return types.Array(gsqmt__rhndn, qbjs__vmdyr, 'C')

    def _get_h5_type_locals(self, varname):
        pqlr__stwoi = self.locals.pop(varname, None)
        if pqlr__stwoi is None and varname is not None:
            pqlr__stwoi = self.flags.h5_types.get(varname, None)
        return pqlr__stwoi
