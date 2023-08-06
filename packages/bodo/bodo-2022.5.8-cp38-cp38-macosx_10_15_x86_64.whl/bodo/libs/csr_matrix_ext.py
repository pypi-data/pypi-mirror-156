"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ehd__klwt = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, ehd__klwt)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        uzgbu__azn, bfx__uuz, uvxi__jlg, bwr__cwpsz = args
        ykp__uys = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        ykp__uys.data = uzgbu__azn
        ykp__uys.indices = bfx__uuz
        ykp__uys.indptr = uvxi__jlg
        ykp__uys.shape = bwr__cwpsz
        context.nrt.incref(builder, signature.args[0], uzgbu__azn)
        context.nrt.incref(builder, signature.args[1], bfx__uuz)
        context.nrt.incref(builder, signature.args[2], uvxi__jlg)
        return ykp__uys._getvalue()
    drvtb__kffb = CSRMatrixType(data_t.dtype, indices_t.dtype)
    hmwg__axb = drvtb__kffb(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return hmwg__axb, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    ykp__uys = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nqoh__dyky = c.pyapi.object_getattr_string(val, 'data')
    qkqu__jku = c.pyapi.object_getattr_string(val, 'indices')
    eyji__ruz = c.pyapi.object_getattr_string(val, 'indptr')
    kayk__novdk = c.pyapi.object_getattr_string(val, 'shape')
    ykp__uys.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        nqoh__dyky).value
    ykp__uys.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), qkqu__jku).value
    ykp__uys.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), eyji__ruz).value
    ykp__uys.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2),
        kayk__novdk).value
    c.pyapi.decref(nqoh__dyky)
    c.pyapi.decref(qkqu__jku)
    c.pyapi.decref(eyji__ruz)
    c.pyapi.decref(kayk__novdk)
    arynr__iqyrw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ykp__uys._getvalue(), is_error=arynr__iqyrw)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    ppgh__slzs = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    kwfvu__ede = c.pyapi.import_module_noblock(ppgh__slzs)
    ykp__uys = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        ykp__uys.data)
    nqoh__dyky = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ykp__uys.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        ykp__uys.indices)
    qkqu__jku = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), ykp__uys.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        ykp__uys.indptr)
    eyji__ruz = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), ykp__uys.indptr, c.env_manager)
    kayk__novdk = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        ykp__uys.shape, c.env_manager)
    cukwn__vxk = c.pyapi.tuple_pack([nqoh__dyky, qkqu__jku, eyji__ruz])
    khaft__jokgj = c.pyapi.call_method(kwfvu__ede, 'csr_matrix', (
        cukwn__vxk, kayk__novdk))
    c.pyapi.decref(cukwn__vxk)
    c.pyapi.decref(nqoh__dyky)
    c.pyapi.decref(qkqu__jku)
    c.pyapi.decref(eyji__ruz)
    c.pyapi.decref(kayk__novdk)
    c.pyapi.decref(kwfvu__ede)
    c.context.nrt.decref(c.builder, typ, val)
    return khaft__jokgj


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    slgu__bpnxb = A.dtype
    jmd__inssa = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            lhf__uizfy, kff__fhze = A.shape
            lad__kni = numba.cpython.unicode._normalize_slice(idx[0],
                lhf__uizfy)
            jgmvy__pqy = numba.cpython.unicode._normalize_slice(idx[1],
                kff__fhze)
            if lad__kni.step != 1 or jgmvy__pqy.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            ftgqn__fib = lad__kni.start
            ebt__ttqw = lad__kni.stop
            ltxj__azvdx = jgmvy__pqy.start
            byu__fcq = jgmvy__pqy.stop
            wlus__tjum = A.indptr
            osqqk__ifb = A.indices
            gfouk__imc = A.data
            ytyik__uky = ebt__ttqw - ftgqn__fib
            jyzo__nuu = byu__fcq - ltxj__azvdx
            dox__ihz = 0
            msv__pieau = 0
            for mqhvd__ipj in range(ytyik__uky):
                gflqf__eeqap = wlus__tjum[ftgqn__fib + mqhvd__ipj]
                cpxf__pxwx = wlus__tjum[ftgqn__fib + mqhvd__ipj + 1]
                for puwn__lhoxt in range(gflqf__eeqap, cpxf__pxwx):
                    if osqqk__ifb[puwn__lhoxt] >= ltxj__azvdx and osqqk__ifb[
                        puwn__lhoxt] < byu__fcq:
                        dox__ihz += 1
            nfbb__fgk = np.empty(ytyik__uky + 1, jmd__inssa)
            skjmy__lfdkp = np.empty(dox__ihz, jmd__inssa)
            ysd__qskz = np.empty(dox__ihz, slgu__bpnxb)
            nfbb__fgk[0] = 0
            for mqhvd__ipj in range(ytyik__uky):
                gflqf__eeqap = wlus__tjum[ftgqn__fib + mqhvd__ipj]
                cpxf__pxwx = wlus__tjum[ftgqn__fib + mqhvd__ipj + 1]
                for puwn__lhoxt in range(gflqf__eeqap, cpxf__pxwx):
                    if osqqk__ifb[puwn__lhoxt] >= ltxj__azvdx and osqqk__ifb[
                        puwn__lhoxt] < byu__fcq:
                        skjmy__lfdkp[msv__pieau] = osqqk__ifb[puwn__lhoxt
                            ] - ltxj__azvdx
                        ysd__qskz[msv__pieau] = gfouk__imc[puwn__lhoxt]
                        msv__pieau += 1
                nfbb__fgk[mqhvd__ipj + 1] = msv__pieau
            return init_csr_matrix(ysd__qskz, skjmy__lfdkp, nfbb__fgk, (
                ytyik__uky, jyzo__nuu))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
