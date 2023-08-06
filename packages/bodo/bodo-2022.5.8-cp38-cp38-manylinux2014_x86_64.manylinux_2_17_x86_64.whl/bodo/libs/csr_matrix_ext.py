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
        hckdh__yuv = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, hckdh__yuv)


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
        wouww__hhoro, ajwoc__sxa, rxuxs__dyrx, hrxd__gjd = args
        qjkes__nukwm = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        qjkes__nukwm.data = wouww__hhoro
        qjkes__nukwm.indices = ajwoc__sxa
        qjkes__nukwm.indptr = rxuxs__dyrx
        qjkes__nukwm.shape = hrxd__gjd
        context.nrt.incref(builder, signature.args[0], wouww__hhoro)
        context.nrt.incref(builder, signature.args[1], ajwoc__sxa)
        context.nrt.incref(builder, signature.args[2], rxuxs__dyrx)
        return qjkes__nukwm._getvalue()
    ideb__nlf = CSRMatrixType(data_t.dtype, indices_t.dtype)
    lhepc__fdfbo = ideb__nlf(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return lhepc__fdfbo, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    qjkes__nukwm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wsn__kzjln = c.pyapi.object_getattr_string(val, 'data')
    hcwa__fvxjz = c.pyapi.object_getattr_string(val, 'indices')
    mqm__inji = c.pyapi.object_getattr_string(val, 'indptr')
    bwb__iqa = c.pyapi.object_getattr_string(val, 'shape')
    qjkes__nukwm.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), wsn__kzjln).value
    qjkes__nukwm.indices = c.pyapi.to_native_value(types.Array(typ.
        idx_dtype, 1, 'C'), hcwa__fvxjz).value
    qjkes__nukwm.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), mqm__inji).value
    qjkes__nukwm.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), bwb__iqa).value
    c.pyapi.decref(wsn__kzjln)
    c.pyapi.decref(hcwa__fvxjz)
    c.pyapi.decref(mqm__inji)
    c.pyapi.decref(bwb__iqa)
    xod__myf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qjkes__nukwm._getvalue(), is_error=xod__myf)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    bsf__csvh = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    ojni__zmy = c.pyapi.import_module_noblock(bsf__csvh)
    qjkes__nukwm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        qjkes__nukwm.data)
    wsn__kzjln = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        qjkes__nukwm.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        qjkes__nukwm.indices)
    hcwa__fvxjz = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), qjkes__nukwm.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        qjkes__nukwm.indptr)
    mqm__inji = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), qjkes__nukwm.indptr, c.env_manager)
    bwb__iqa = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        qjkes__nukwm.shape, c.env_manager)
    jshkn__cyeoz = c.pyapi.tuple_pack([wsn__kzjln, hcwa__fvxjz, mqm__inji])
    okc__dmwrf = c.pyapi.call_method(ojni__zmy, 'csr_matrix', (jshkn__cyeoz,
        bwb__iqa))
    c.pyapi.decref(jshkn__cyeoz)
    c.pyapi.decref(wsn__kzjln)
    c.pyapi.decref(hcwa__fvxjz)
    c.pyapi.decref(mqm__inji)
    c.pyapi.decref(bwb__iqa)
    c.pyapi.decref(ojni__zmy)
    c.context.nrt.decref(c.builder, typ, val)
    return okc__dmwrf


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
    qrvr__luzx = A.dtype
    zpnjv__ofs = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            uoqr__nvbz, ypxym__pyv = A.shape
            aacw__xikfy = numba.cpython.unicode._normalize_slice(idx[0],
                uoqr__nvbz)
            ziypo__uoq = numba.cpython.unicode._normalize_slice(idx[1],
                ypxym__pyv)
            if aacw__xikfy.step != 1 or ziypo__uoq.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            vcgz__mgvd = aacw__xikfy.start
            cwgdj__ppe = aacw__xikfy.stop
            yvq__fpbw = ziypo__uoq.start
            gra__lvex = ziypo__uoq.stop
            hdh__uqhf = A.indptr
            qvuwy__rtw = A.indices
            ldijd__okkq = A.data
            ohowb__fmo = cwgdj__ppe - vcgz__mgvd
            vcyq__floj = gra__lvex - yvq__fpbw
            qsta__ifivu = 0
            ckfyp__cgw = 0
            for mgo__imvto in range(ohowb__fmo):
                pvku__kxc = hdh__uqhf[vcgz__mgvd + mgo__imvto]
                sbu__rfqm = hdh__uqhf[vcgz__mgvd + mgo__imvto + 1]
                for hddk__gmg in range(pvku__kxc, sbu__rfqm):
                    if qvuwy__rtw[hddk__gmg] >= yvq__fpbw and qvuwy__rtw[
                        hddk__gmg] < gra__lvex:
                        qsta__ifivu += 1
            qgzpr__oox = np.empty(ohowb__fmo + 1, zpnjv__ofs)
            mmbhi__mugu = np.empty(qsta__ifivu, zpnjv__ofs)
            brwn__dbxg = np.empty(qsta__ifivu, qrvr__luzx)
            qgzpr__oox[0] = 0
            for mgo__imvto in range(ohowb__fmo):
                pvku__kxc = hdh__uqhf[vcgz__mgvd + mgo__imvto]
                sbu__rfqm = hdh__uqhf[vcgz__mgvd + mgo__imvto + 1]
                for hddk__gmg in range(pvku__kxc, sbu__rfqm):
                    if qvuwy__rtw[hddk__gmg] >= yvq__fpbw and qvuwy__rtw[
                        hddk__gmg] < gra__lvex:
                        mmbhi__mugu[ckfyp__cgw] = qvuwy__rtw[hddk__gmg
                            ] - yvq__fpbw
                        brwn__dbxg[ckfyp__cgw] = ldijd__okkq[hddk__gmg]
                        ckfyp__cgw += 1
                qgzpr__oox[mgo__imvto + 1] = ckfyp__cgw
            return init_csr_matrix(brwn__dbxg, mmbhi__mugu, qgzpr__oox, (
                ohowb__fmo, vcyq__floj))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
