"""
Indexing support for Series objects, including loc/iloc/at/iat types.
"""
import operator
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.pd_timestamp_ext import convert_datetime64_to_timestamp, convert_numpy_timedelta64_to_pd_timedelta, integer_to_dt64, pd_timestamp_type
from bodo.utils.typing import BodoError, get_literal_value, get_overload_const_tuple, is_immutable_array, is_list_like_index_type, is_literal_type, is_overload_constant_str, is_overload_constant_tuple, is_scalar_type, raise_bodo_error


class SeriesIatType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        kxa__uem = 'SeriesIatType({})'.format(stype)
        super(SeriesIatType, self).__init__(kxa__uem)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 1


@register_model(SeriesIatType)
class SeriesIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xfy__lksf = [('obj', fe_type.stype)]
        super(SeriesIatModel, self).__init__(dmm, fe_type, xfy__lksf)


make_attribute_wrapper(SeriesIatType, 'obj', '_obj')


@intrinsic
def init_series_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gsog__zhp, = args
        obyl__yqjpw = signature.return_type
        dxr__rzgr = cgutils.create_struct_proxy(obyl__yqjpw)(context, builder)
        dxr__rzgr.obj = gsog__zhp
        context.nrt.incref(builder, signature.args[0], gsog__zhp)
        return dxr__rzgr._getvalue()
    return SeriesIatType(obj)(obj), codegen


@overload_attribute(SeriesType, 'iat')
def overload_series_iat(s):
    return lambda s: bodo.hiframes.series_indexing.init_series_iat(s)


@overload(operator.getitem, no_unliteral=True)
def overload_series_iat_getitem(I, idx):
    if isinstance(I, SeriesIatType):
        if not isinstance(types.unliteral(idx), types.Integer):
            raise BodoError('iAt based indexing can only have integer indexers'
                )
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
            'Series.iat')
        if I.stype.dtype == types.NPDatetime('ns'):
            return lambda I, idx: convert_datetime64_to_timestamp(np.int64(
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx]))
        if I.stype.dtype == types.NPTimedelta('ns'):
            return lambda I, idx: convert_numpy_timedelta64_to_pd_timedelta(
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx])
        return lambda I, idx: bodo.hiframes.pd_series_ext.get_series_data(I
            ._obj)[idx]


@overload(operator.setitem, no_unliteral=True)
def overload_series_iat_setitem(I, idx, val):
    if isinstance(I, SeriesIatType):
        if not isinstance(idx, types.Integer):
            raise BodoError('iAt based indexing can only have integer indexers'
                )
        if I.stype.dtype == bodo.string_type and val is not types.none:
            raise BodoError('Series string setitem not supported yet')
        if is_immutable_array(I.stype.data):
            raise BodoError(
                f'Series setitem not supported for Series with immutable array type {I.stype.data}'
                )
        if I.stype.dtype == types.NPDatetime('ns'
            ) and val == pd_timestamp_type:

            def impl_dt(I, idx, val):
                s = integer_to_dt64(val.value)
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx] = s
            return impl_dt
        if I.stype.dtype == types.NPDatetime('ns'
            ) and val == bodo.datetime_datetime_type:

            def impl_dt(I, idx, val):
                s = bodo.hiframes.pd_timestamp_ext.datetime_datetime_to_dt64(
                    val)
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx] = s
            return impl_dt
        if I.stype.dtype == types.NPTimedelta('ns'
            ) and val == datetime_timedelta_type:

            def impl_dt(I, idx, val):
                umkat__iiqr = (bodo.hiframes.datetime_timedelta_ext.
                    _to_nanoseconds(val))
                s = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    umkat__iiqr)
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx] = s
            return impl_dt
        if I.stype.dtype == types.NPTimedelta('ns'
            ) and val == pd_timedelta_type:

            def impl_dt(I, idx, val):
                umkat__iiqr = val.value
                s = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    umkat__iiqr)
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx] = s
            return impl_dt

        def impl(I, idx, val):
            bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx] = val
        return impl


class SeriesIlocType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        kxa__uem = 'SeriesIlocType({})'.format(stype)
        super(SeriesIlocType, self).__init__(kxa__uem)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 1


@register_model(SeriesIlocType)
class SeriesIlocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xfy__lksf = [('obj', fe_type.stype)]
        super(SeriesIlocModel, self).__init__(dmm, fe_type, xfy__lksf)


make_attribute_wrapper(SeriesIlocType, 'obj', '_obj')


@intrinsic
def init_series_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gsog__zhp, = args
        vqzvi__evvhy = signature.return_type
        ulwbi__yns = cgutils.create_struct_proxy(vqzvi__evvhy)(context, builder
            )
        ulwbi__yns.obj = gsog__zhp
        context.nrt.incref(builder, signature.args[0], gsog__zhp)
        return ulwbi__yns._getvalue()
    return SeriesIlocType(obj)(obj), codegen


@overload_attribute(SeriesType, 'iloc')
def overload_series_iloc(s):
    return lambda s: bodo.hiframes.series_indexing.init_series_iloc(s)


@overload(operator.getitem, no_unliteral=True)
def overload_series_iloc_getitem(I, idx):
    if isinstance(I, SeriesIlocType):
        if I.stype.dtype == types.NPTimedelta('ns') and isinstance(idx,
            types.Integer):
            return lambda I, idx: convert_numpy_timedelta64_to_pd_timedelta(
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx])
        if isinstance(idx, types.Integer):
            return lambda I, idx: bodo.utils.conversion.box_if_dt64(bodo.
                hiframes.pd_series_ext.get_series_data(I._obj)[idx])
        if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
            Integer, types.Boolean)):

            def impl(I, idx):
                S = I._obj
                utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx)
                haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S)[
                    utv__rowx]
                emgw__mdhxm = bodo.hiframes.pd_series_ext.get_series_index(S)[
                    utv__rowx]
                kxa__uem = bodo.hiframes.pd_series_ext.get_series_name(S)
                return bodo.hiframes.pd_series_ext.init_series(haat__faell,
                    emgw__mdhxm, kxa__uem)
            return impl
        if isinstance(idx, types.SliceType):

            def impl_slice(I, idx):
                S = I._obj
                haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S)[
                    idx]
                emgw__mdhxm = bodo.hiframes.pd_series_ext.get_series_index(S)[
                    idx]
                kxa__uem = bodo.hiframes.pd_series_ext.get_series_name(S)
                return bodo.hiframes.pd_series_ext.init_series(haat__faell,
                    emgw__mdhxm, kxa__uem)
            return impl_slice
        raise BodoError('Series.iloc[] getitem using {} not supported'.
            format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_series_iloc_setitem(I, idx, val):
    if isinstance(I, SeriesIlocType):
        if I.stype.dtype == bodo.string_type and val is not types.none:
            raise BodoError('Series string setitem not supported yet')
        if is_immutable_array(I.stype.data):
            raise BodoError(
                f'Series setitem not supported for Series with immutable array type {I.stype.data}'
                )
        if isinstance(idx, types.Integer) or isinstance(idx, types.SliceType
            ) and is_scalar_type(val):
            if I.stype.dtype == types.NPDatetime('ns'
                ) and val == pd_timestamp_type:

                def impl_dt(I, idx, val):
                    s = integer_to_dt64(val.value)
                    bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx
                        ] = s
                return impl_dt
            if I.stype.dtype == types.NPDatetime('ns'
                ) and val == bodo.datetime_datetime_type:

                def impl_dt(I, idx, val):
                    s = (bodo.hiframes.pd_timestamp_ext.
                        datetime_datetime_to_dt64(val))
                    bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx
                        ] = s
                return impl_dt
            if I.stype.dtype == types.NPTimedelta('ns'
                ) and val == datetime_timedelta_type:

                def impl_dt(I, idx, val):
                    umkat__iiqr = (bodo.hiframes.datetime_timedelta_ext.
                        _to_nanoseconds(val))
                    s = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        umkat__iiqr)
                    bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx
                        ] = s
                return impl_dt
            if I.stype.dtype == types.NPTimedelta('ns'
                ) and val == pd_timedelta_type:

                def impl_dt(I, idx, val):
                    umkat__iiqr = val.value
                    s = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        umkat__iiqr)
                    bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx
                        ] = s
                return impl_dt

            def impl(I, idx, val):
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx] = val
            return impl
        if isinstance(idx, types.SliceType):

            def impl_slice(I, idx, val):
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[idx
                    ] = bodo.utils.conversion.coerce_to_array(val, False)
            return impl_slice
        if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
            Integer, types.Boolean)):
            if is_scalar_type(val):
                if I.stype.dtype == types.NPDatetime('ns'
                    ) and val == pd_timestamp_type:

                    def impl_dt(I, idx, val):
                        s = integer_to_dt64(val.value)
                        utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx
                            )
                        bodo.hiframes.pd_series_ext.get_series_data(I._obj)[
                            utv__rowx] = s
                    return impl_dt
                if I.stype.dtype == types.NPDatetime('ns'
                    ) and val == bodo.datetime_datetime_type:

                    def impl_dt(I, idx, val):
                        s = (bodo.hiframes.pd_timestamp_ext.
                            datetime_datetime_to_dt64(val))
                        utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx
                            )
                        bodo.hiframes.pd_series_ext.get_series_data(I._obj)[
                            utv__rowx] = s
                    return impl_dt
                if I.stype.dtype == types.NPTimedelta('ns'
                    ) and val == datetime_timedelta_type:

                    def impl_dt(I, idx, val):
                        umkat__iiqr = (bodo.hiframes.datetime_timedelta_ext
                            ._to_nanoseconds(val))
                        s = (bodo.hiframes.pd_timestamp_ext.
                            integer_to_timedelta64(umkat__iiqr))
                        utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx
                            )
                        bodo.hiframes.pd_series_ext.get_series_data(I._obj)[
                            utv__rowx] = s
                    return impl_dt
                if I.stype.dtype == types.NPTimedelta('ns'
                    ) and val == pd_timedelta_type:

                    def impl_dt(I, idx, val):
                        umkat__iiqr = val.value
                        s = (bodo.hiframes.pd_timestamp_ext.
                            integer_to_timedelta64(umkat__iiqr))
                        utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx
                            )
                        bodo.hiframes.pd_series_ext.get_series_data(I._obj)[
                            utv__rowx] = s
                    return impl_dt

                def impl(I, idx, val):
                    utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx)
                    bodo.hiframes.pd_series_ext.get_series_data(I._obj)[
                        utv__rowx] = val
                return impl

            def impl_arr(I, idx, val):
                utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx)
                bodo.hiframes.pd_series_ext.get_series_data(I._obj)[utv__rowx
                    ] = bodo.utils.conversion.coerce_to_array(val, False)
            return impl_arr
        raise BodoError('Series.iloc[] setitem using {} not supported'.
            format(idx))


class SeriesLocType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        kxa__uem = 'SeriesLocType({})'.format(stype)
        super(SeriesLocType, self).__init__(kxa__uem)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 1


@register_model(SeriesLocType)
class SeriesLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xfy__lksf = [('obj', fe_type.stype)]
        super(SeriesLocModel, self).__init__(dmm, fe_type, xfy__lksf)


make_attribute_wrapper(SeriesLocType, 'obj', '_obj')


@intrinsic
def init_series_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gsog__zhp, = args
        vhlyg__lza = signature.return_type
        yloh__xpqkc = cgutils.create_struct_proxy(vhlyg__lza)(context, builder)
        yloh__xpqkc.obj = gsog__zhp
        context.nrt.incref(builder, signature.args[0], gsog__zhp)
        return yloh__xpqkc._getvalue()
    return SeriesLocType(obj)(obj), codegen


@overload_attribute(SeriesType, 'loc')
def overload_series_loc(s):
    return lambda s: bodo.hiframes.series_indexing.init_series_loc(s)


@overload(operator.getitem)
def overload_series_loc_getitem(I, idx):
    if not isinstance(I, SeriesLocType):
        return
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl(I, idx):
            S = I._obj
            utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx)
            haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S)[
                utv__rowx]
            emgw__mdhxm = bodo.hiframes.pd_series_ext.get_series_index(S)[
                utv__rowx]
            kxa__uem = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(haat__faell,
                emgw__mdhxm, kxa__uem)
        return impl
    if isinstance(idx, types.Integer) and isinstance(I.stype.index,
        RangeIndexType):

        def impl_range_index_int(I, idx):
            S = I._obj
            haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S)
            emgw__mdhxm = bodo.hiframes.pd_series_ext.get_series_index(S)
            ausye__idj = (idx - emgw__mdhxm._start) // emgw__mdhxm._step
            return haat__faell[ausye__idj]
        return impl_range_index_int
    raise BodoError(
        f'Series.loc[] getitem (location-based indexing) using {idx} not supported yet'
        )


@overload(operator.setitem)
def overload_series_loc_setitem(I, idx, val):
    if not isinstance(I, SeriesLocType):
        return
    if is_immutable_array(I.stype.data):
        raise BodoError(
            f'Series setitem not supported for Series with immutable array type {I.stype.data}'
            )
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl(I, idx, val):
            S = I._obj
            S[idx] = val
        return impl
    raise BodoError(
        f'Series.loc[] setitem (location-based indexing) using {idx} not supported yet'
        )


@overload(operator.getitem)
def overload_series_getitem(S, idx):
    if isinstance(S, SeriesType) and not (isinstance(S.index,
        HeterogeneousIndexType) and is_overload_constant_tuple(S.index.data)):
        if isinstance(idx, types.Integer):
            if isinstance(S.index, NumericIndexType) and isinstance(S.index
                .dtype, types.Integer):
                raise BodoError(
                    'Indexing Series with Integer index using [] (which is label-based) not supported yet'
                    )
            if isinstance(S.index, RangeIndexType):

                def impl(S, idx):
                    haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S
                        )
                    I = bodo.hiframes.pd_series_ext.get_series_index(S)
                    utv__rowx = idx * I._step + I._start
                    return bodo.utils.conversion.box_if_dt64(haat__faell[
                        utv__rowx])
                return impl
            return lambda S, idx: bodo.utils.conversion.box_if_dt64(bodo.
                hiframes.pd_series_ext.get_series_data(S)[idx])
        if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
            Integer, types.Boolean)):
            if isinstance(S.index, NumericIndexType) and isinstance(S.index
                .dtype, types.Integer) and isinstance(idx.dtype, types.Integer
                ):
                raise BodoError(
                    'Indexing Series with Integer index using [] (which is label-based) not supported yet'
                    )

            def impl_arr(S, idx):
                utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx)
                haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S)[
                    utv__rowx]
                emgw__mdhxm = bodo.hiframes.pd_series_ext.get_series_index(S)[
                    utv__rowx]
                kxa__uem = bodo.hiframes.pd_series_ext.get_series_name(S)
                return bodo.hiframes.pd_series_ext.init_series(haat__faell,
                    emgw__mdhxm, kxa__uem)
            return impl_arr
        if isinstance(idx, types.SliceType):

            def impl_slice(S, idx):
                haat__faell = bodo.hiframes.pd_series_ext.get_series_data(S)[
                    idx]
                emgw__mdhxm = bodo.hiframes.pd_series_ext.get_series_index(S)[
                    idx]
                kxa__uem = bodo.hiframes.pd_series_ext.get_series_name(S)
                return bodo.hiframes.pd_series_ext.init_series(haat__faell,
                    emgw__mdhxm, kxa__uem)
            return impl_slice
        if idx == bodo.string_type or is_overload_constant_str(idx):
            if isinstance(S.index, bodo.hiframes.pd_index_ext.StringIndexType):

                def impl_str_getitem(S, idx):
                    qvu__suaw = bodo.hiframes.pd_series_ext.get_series_index(S)
                    xoxt__brbi = qvu__suaw.get_loc(idx)
                    if xoxt__brbi is None:
                        raise IndexError
                    else:
                        val = bodo.hiframes.pd_series_ext.get_series_data(S)[
                            bodo.utils.indexing.unoptional(xoxt__brbi)]
                    return val
                return impl_str_getitem
            else:
                raise BodoError(
                    f'Cannot get Series value using a string, unless the index type is also string'
                    )
        raise BodoError(f'getting Series value using {idx} not supported yet')
    elif bodo.utils.utils.is_array_typ(S) and isinstance(idx, SeriesType):
        return lambda S, idx: S[bodo.hiframes.pd_series_ext.get_series_data
            (idx)]


@overload(operator.setitem, no_unliteral=True)
def overload_series_setitem(S, idx, val):
    if isinstance(S, SeriesType):
        if S.dtype == bodo.string_type and val is not types.none and not (
            is_list_like_index_type(idx) and idx.dtype == types.bool_):
            raise BodoError('Series string setitem not supported yet')
        if isinstance(idx, types.Integer):
            if isinstance(S.index, NumericIndexType) and isinstance(S.index
                .dtype, types.Integer):
                raise BodoError(
                    'Indexing Series with Integer index using [] (which is label-based) not supported yet'
                    )
            if S.dtype == types.NPDatetime('ns') and val == pd_timestamp_type:

                def impl_dt(S, idx, val):
                    s = integer_to_dt64(val.value)
                    bodo.hiframes.pd_series_ext.get_series_data(S)[idx] = s
                return impl_dt
            if S.dtype == types.NPTimedelta('ns'
                ) and val == datetime_timedelta_type:

                def impl_dt(S, idx, val):
                    umkat__iiqr = (bodo.hiframes.datetime_timedelta_ext.
                        _to_nanoseconds(val))
                    s = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        umkat__iiqr)
                    bodo.hiframes.pd_series_ext.get_series_data(S)[idx] = s
                return impl_dt
            if S.dtype == types.NPTimedelta('ns') and val == pd_timedelta_type:

                def impl_dt(S, idx, val):
                    umkat__iiqr = val.value
                    s = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        umkat__iiqr)
                    bodo.hiframes.pd_series_ext.get_series_data(S)[idx] = s
                return impl_dt

            def impl(S, idx, val):
                bodo.hiframes.pd_series_ext.get_series_data(S)[idx] = val
            return impl
        if isinstance(idx, types.SliceType):

            def impl_slice(S, idx, val):
                bodo.hiframes.pd_series_ext.get_series_data(S)[idx
                    ] = bodo.utils.conversion.coerce_to_array(val, False)
            return impl_slice
        if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
            Integer, types.Boolean)):
            if isinstance(S.index, NumericIndexType) and isinstance(S.index
                .dtype, types.Integer) and isinstance(idx.dtype, types.Integer
                ):
                raise BodoError(
                    'Indexing Series with Integer index using [] (which is label-based) not supported yet'
                    )

            def impl_arr(S, idx, val):
                utv__rowx = bodo.utils.conversion.coerce_to_ndarray(idx)
                bodo.hiframes.pd_series_ext.get_series_data(S)[utv__rowx
                    ] = bodo.utils.conversion.coerce_to_array(val, False)
            return impl_arr
        raise BodoError(f'Series [] setitem using {idx} not supported yet')


@overload(operator.setitem, no_unliteral=True)
def overload_array_list_setitem(A, idx, val):
    if isinstance(A, types.Array) and isinstance(idx, (types.List, SeriesType)
        ):

        def impl(A, idx, val):
            A[bodo.utils.conversion.coerce_to_array(idx)] = val
        return impl


@overload(operator.getitem, no_unliteral=True)
def overload_const_index_series_getitem(S, idx):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)) and isinstance(S
        .index, HeterogeneousIndexType) and is_overload_constant_tuple(S.
        index.data):
        rnnc__oxlm = get_overload_const_tuple(S.index.data)
        if isinstance(idx, types.Integer) and not any(isinstance(cqf__eauj,
            int) for cqf__eauj in rnnc__oxlm):
            return lambda S, idx: bodo.hiframes.pd_series_ext.get_series_data(S
                )[idx]
        if is_literal_type(idx):
            vcoan__fpemq = get_literal_value(idx)
            if vcoan__fpemq not in rnnc__oxlm:
                raise_bodo_error(
                    f"Series label-based getitem: '{vcoan__fpemq}' not in {rnnc__oxlm}"
                    )
            arr_ind = rnnc__oxlm.index(vcoan__fpemq)
            return lambda S, idx: bodo.hiframes.pd_series_ext.get_series_data(S
                )[arr_ind]


@lower_cast(SeriesIatType, SeriesIatType)
@lower_cast(SeriesIlocType, SeriesIlocType)
@lower_cast(SeriesLocType, SeriesLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    dxr__rzgr = cgutils.create_struct_proxy(fromty)(context, builder, val)
    wtx__tbw = context.cast(builder, dxr__rzgr.obj, fromty.stype, toty.stype)
    zfnnl__ouj = cgutils.create_struct_proxy(toty)(context, builder)
    zfnnl__ouj.obj = wtx__tbw
    return zfnnl__ouj._getvalue()
