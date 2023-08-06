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
        eeddo__kfv = self._get_h5_type(lhs, rhs)
        if eeddo__kfv is not None:
            mvw__jie = str(eeddo__kfv.dtype)
            zbsh__hxs = 'def _h5_read_impl(dset, index):\n'
            zbsh__hxs += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(eeddo__kfv.ndim, mvw__jie))
            btpn__ouh = {}
            exec(zbsh__hxs, {}, btpn__ouh)
            qifol__iqxg = btpn__ouh['_h5_read_impl']
            mgd__efx = compile_to_numba_ir(qifol__iqxg, {'bodo': bodo}
                ).blocks.popitem()[1]
            lbski__ywpt = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(mgd__efx, [rhs.value, lbski__ywpt])
            vws__hsakk = mgd__efx.body[:-3]
            vws__hsakk[-1].target = assign.target
            return vws__hsakk
        return None

    def _get_h5_type(self, lhs, rhs):
        eeddo__kfv = self._get_h5_type_locals(lhs)
        if eeddo__kfv is not None:
            return eeddo__kfv
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        lbski__ywpt = rhs.index if rhs.op == 'getitem' else rhs.index_var
        jzic__tsokt = guard(find_const, self.func_ir, lbski__ywpt)
        require(not isinstance(jzic__tsokt, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            mhemm__pgk = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            war__jfz = get_const_value_inner(self.func_ir, mhemm__pgk,
                arg_types=self.arg_types)
            obj_name_list.append(war__jfz)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        erond__afcld = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        lnzq__zjra = h5py.File(erond__afcld, 'r')
        mybkq__omfb = lnzq__zjra
        for war__jfz in obj_name_list:
            mybkq__omfb = mybkq__omfb[war__jfz]
        require(isinstance(mybkq__omfb, h5py.Dataset))
        qjjqc__ynijd = len(mybkq__omfb.shape)
        pmj__tvc = numba.np.numpy_support.from_dtype(mybkq__omfb.dtype)
        lnzq__zjra.close()
        return types.Array(pmj__tvc, qjjqc__ynijd, 'C')

    def _get_h5_type_locals(self, varname):
        xld__ave = self.locals.pop(varname, None)
        if xld__ave is None and varname is not None:
            xld__ave = self.flags.h5_types.get(varname, None)
        return xld__ave
