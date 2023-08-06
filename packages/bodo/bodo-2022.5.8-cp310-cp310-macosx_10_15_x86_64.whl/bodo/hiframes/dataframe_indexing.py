"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            mokgj__ufu = idx
            cem__snkiy = df.data
            loh__exd = df.columns
            rihzd__pjlg = self.replace_range_with_numeric_idx_if_needed(df,
                mokgj__ufu)
            mwt__sdlt = DataFrameType(cem__snkiy, rihzd__pjlg, loh__exd)
            return mwt__sdlt(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            uwcav__wnvn = idx.types[0]
            eopg__sfi = idx.types[1]
            if isinstance(uwcav__wnvn, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(eopg__sfi):
                    aniqh__chm = get_overload_const_str(eopg__sfi)
                    if aniqh__chm not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, aniqh__chm))
                    bxfy__lgyz = df.columns.index(aniqh__chm)
                    return df.data[bxfy__lgyz].dtype(*args)
                if isinstance(eopg__sfi, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(uwcav__wnvn
                ) and uwcav__wnvn.dtype == types.bool_ or isinstance(
                uwcav__wnvn, types.SliceType):
                rihzd__pjlg = self.replace_range_with_numeric_idx_if_needed(df,
                    uwcav__wnvn)
                if is_overload_constant_str(eopg__sfi):
                    ohtca__pcomj = get_overload_const_str(eopg__sfi)
                    if ohtca__pcomj not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {ohtca__pcomj}'
                            )
                    bxfy__lgyz = df.columns.index(ohtca__pcomj)
                    eovx__qeptf = df.data[bxfy__lgyz]
                    les__vgbr = eovx__qeptf.dtype
                    qpiu__brfib = types.literal(df.columns[bxfy__lgyz])
                    mwt__sdlt = bodo.SeriesType(les__vgbr, eovx__qeptf,
                        rihzd__pjlg, qpiu__brfib)
                    return mwt__sdlt(*args)
                if isinstance(eopg__sfi, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(eopg__sfi):
                    jwoz__bpmxq = get_overload_const_list(eopg__sfi)
                    pcea__qus = types.unliteral(eopg__sfi)
                    if pcea__qus.dtype == types.bool_:
                        if len(df.columns) != len(jwoz__bpmxq):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {jwoz__bpmxq} has {len(jwoz__bpmxq)} values'
                                )
                        ucfh__ufia = []
                        sbcf__wfy = []
                        for grx__xsft in range(len(jwoz__bpmxq)):
                            if jwoz__bpmxq[grx__xsft]:
                                ucfh__ufia.append(df.columns[grx__xsft])
                                sbcf__wfy.append(df.data[grx__xsft])
                        edzh__dhqz = tuple()
                        mwt__sdlt = DataFrameType(tuple(sbcf__wfy),
                            rihzd__pjlg, tuple(ucfh__ufia))
                        return mwt__sdlt(*args)
                    elif pcea__qus.dtype == bodo.string_type:
                        edzh__dhqz, sbcf__wfy = (
                            get_df_getitem_kept_cols_and_data(df, jwoz__bpmxq))
                        mwt__sdlt = DataFrameType(sbcf__wfy, rihzd__pjlg,
                            edzh__dhqz)
                        return mwt__sdlt(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                ucfh__ufia = []
                sbcf__wfy = []
                for grx__xsft, wlkuk__nzv in enumerate(df.columns):
                    if wlkuk__nzv[0] != ind_val:
                        continue
                    ucfh__ufia.append(wlkuk__nzv[1] if len(wlkuk__nzv) == 2
                         else wlkuk__nzv[1:])
                    sbcf__wfy.append(df.data[grx__xsft])
                eovx__qeptf = tuple(sbcf__wfy)
                ezp__dfi = df.index
                oae__gkpv = tuple(ucfh__ufia)
                mwt__sdlt = DataFrameType(eovx__qeptf, ezp__dfi, oae__gkpv)
                return mwt__sdlt(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                bxfy__lgyz = df.columns.index(ind_val)
                eovx__qeptf = df.data[bxfy__lgyz]
                les__vgbr = eovx__qeptf.dtype
                ezp__dfi = df.index
                qpiu__brfib = types.literal(df.columns[bxfy__lgyz])
                mwt__sdlt = bodo.SeriesType(les__vgbr, eovx__qeptf,
                    ezp__dfi, qpiu__brfib)
                return mwt__sdlt(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            eovx__qeptf = df.data
            ezp__dfi = self.replace_range_with_numeric_idx_if_needed(df, ind)
            oae__gkpv = df.columns
            mwt__sdlt = DataFrameType(eovx__qeptf, ezp__dfi, oae__gkpv,
                is_table_format=df.is_table_format)
            return mwt__sdlt(*args)
        elif is_overload_constant_list(ind):
            euths__tocqc = get_overload_const_list(ind)
            oae__gkpv, eovx__qeptf = get_df_getitem_kept_cols_and_data(df,
                euths__tocqc)
            ezp__dfi = df.index
            vkzb__vse = df.is_table_format and len(euths__tocqc
                ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            mwt__sdlt = DataFrameType(eovx__qeptf, ezp__dfi, oae__gkpv,
                is_table_format=vkzb__vse)
            return mwt__sdlt(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        rihzd__pjlg = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return rihzd__pjlg


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for hggv__duuht in cols_to_keep_list:
        if hggv__duuht not in df.columns:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(hggv__duuht, df.columns))
    oae__gkpv = tuple(cols_to_keep_list)
    eovx__qeptf = tuple(df.data[df.column_index[ikdqs__fjyza]] for
        ikdqs__fjyza in oae__gkpv)
    return oae__gkpv, eovx__qeptf


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            ucfh__ufia = []
            sbcf__wfy = []
            for grx__xsft, wlkuk__nzv in enumerate(df.columns):
                if wlkuk__nzv[0] != ind_val:
                    continue
                ucfh__ufia.append(wlkuk__nzv[1] if len(wlkuk__nzv) == 2 else
                    wlkuk__nzv[1:])
                sbcf__wfy.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(grx__xsft))
            bwz__snkxd = 'def impl(df, ind):\n'
            cmpcg__ako = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(bwz__snkxd,
                ucfh__ufia, ', '.join(sbcf__wfy), cmpcg__ako)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        euths__tocqc = get_overload_const_list(ind)
        for hggv__duuht in euths__tocqc:
            if hggv__duuht not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(hggv__duuht, df.columns))
        jmjx__bwih = None
        if df.is_table_format and len(euths__tocqc
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            ugvrj__pzs = [df.column_index[hggv__duuht] for hggv__duuht in
                euths__tocqc]
            jmjx__bwih = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (ugvrj__pzs))}
            sbcf__wfy = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta)'
                )
        else:
            sbcf__wfy = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hggv__duuht]}).copy()'
                 for hggv__duuht in euths__tocqc)
        bwz__snkxd = 'def impl(df, ind):\n'
        cmpcg__ako = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(bwz__snkxd,
            euths__tocqc, sbcf__wfy, cmpcg__ako, extra_globals=jmjx__bwih)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        bwz__snkxd = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            bwz__snkxd += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        cmpcg__ako = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            sbcf__wfy = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            sbcf__wfy = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hggv__duuht]})[ind]'
                 for hggv__duuht in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(bwz__snkxd, df.
            columns, sbcf__wfy, cmpcg__ako)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        ikdqs__fjyza = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(ikdqs__fjyza)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bzog__ejx = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, bzog__ejx)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        hvqdf__thzlm, = args
        etj__kycrw = signature.return_type
        isd__fhmr = cgutils.create_struct_proxy(etj__kycrw)(context, builder)
        isd__fhmr.obj = hvqdf__thzlm
        context.nrt.incref(builder, signature.args[0], hvqdf__thzlm)
        return isd__fhmr._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        cmbem__cnkdb = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            ifzq__jnlfq = get_overload_const_int(idx.types[1])
            if ifzq__jnlfq < 0 or ifzq__jnlfq >= cmbem__cnkdb:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            asnui__vvd = [ifzq__jnlfq]
        else:
            is_out_series = False
            asnui__vvd = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >=
                cmbem__cnkdb for ind in asnui__vvd):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[asnui__vvd])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                ifzq__jnlfq = asnui__vvd[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, ifzq__jnlfq
                        )[idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    bwz__snkxd = 'def impl(I, idx):\n'
    bwz__snkxd += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        bwz__snkxd += f'  idx_t = {idx}\n'
    else:
        bwz__snkxd += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    cmpcg__ako = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    sbcf__wfy = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hggv__duuht]})[idx_t]'
         for hggv__duuht in col_names)
    if is_out_series:
        ewk__hrhtk = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        bwz__snkxd += f"""  return bodo.hiframes.pd_series_ext.init_series({sbcf__wfy}, {cmpcg__ako}, {ewk__hrhtk})
"""
        rsx__yotls = {}
        exec(bwz__snkxd, {'bodo': bodo}, rsx__yotls)
        return rsx__yotls['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(bwz__snkxd, col_names,
        sbcf__wfy, cmpcg__ako)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    bwz__snkxd = 'def impl(I, idx):\n'
    bwz__snkxd += '  df = I._obj\n'
    awp__tjpad = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hggv__duuht]})[{idx}]'
         for hggv__duuht in col_names)
    bwz__snkxd += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    bwz__snkxd += f"""  return bodo.hiframes.pd_series_ext.init_series(({awp__tjpad},), row_idx, None)
"""
    rsx__yotls = {}
    exec(bwz__snkxd, {'bodo': bodo}, rsx__yotls)
    impl = rsx__yotls['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        ikdqs__fjyza = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(ikdqs__fjyza)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bzog__ejx = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, bzog__ejx)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        hvqdf__thzlm, = args
        oitzp__wtpwb = signature.return_type
        exfrk__fhb = cgutils.create_struct_proxy(oitzp__wtpwb)(context, builder
            )
        exfrk__fhb.obj = hvqdf__thzlm
        context.nrt.incref(builder, signature.args[0], hvqdf__thzlm)
        return exfrk__fhb._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        bwz__snkxd = 'def impl(I, idx):\n'
        bwz__snkxd += '  df = I._obj\n'
        bwz__snkxd += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        cmpcg__ako = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        sbcf__wfy = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hggv__duuht]})[idx_t]'
             for hggv__duuht in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(bwz__snkxd, df.
            columns, sbcf__wfy, cmpcg__ako)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        rpask__ffb = idx.types[1]
        if is_overload_constant_str(rpask__ffb):
            wwus__ydn = get_overload_const_str(rpask__ffb)
            ifzq__jnlfq = df.columns.index(wwus__ydn)

            def impl_col_name(I, idx):
                df = I._obj
                cmpcg__ako = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                ktpb__wyvrn = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, ifzq__jnlfq))
                return bodo.hiframes.pd_series_ext.init_series(ktpb__wyvrn,
                    cmpcg__ako, wwus__ydn).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(rpask__ffb):
            col_idx_list = get_overload_const_list(rpask__ffb)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(hggv__duuht in df.columns for
                hggv__duuht in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        col_idx_list = list(pd.Series(df.columns, dtype=object)[col_idx_list])
    sbcf__wfy = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hggv__duuht]})[idx[0]]'
         for hggv__duuht in col_idx_list)
    cmpcg__ako = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    bwz__snkxd = 'def impl(I, idx):\n'
    bwz__snkxd += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(bwz__snkxd,
        col_idx_list, sbcf__wfy, cmpcg__ako)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        ikdqs__fjyza = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(ikdqs__fjyza)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bzog__ejx = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, bzog__ejx)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        hvqdf__thzlm, = args
        yai__xftq = signature.return_type
        glsw__elk = cgutils.create_struct_proxy(yai__xftq)(context, builder)
        glsw__elk.obj = hvqdf__thzlm
        context.nrt.incref(builder, signature.args[0], hvqdf__thzlm)
        return glsw__elk._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        ifzq__jnlfq = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            ktpb__wyvrn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                ifzq__jnlfq)
            return bodo.utils.conversion.box_if_dt64(ktpb__wyvrn[idx[0]])
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        ifzq__jnlfq = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[ifzq__jnlfq]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            ktpb__wyvrn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                ifzq__jnlfq)
            ktpb__wyvrn[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    glsw__elk = cgutils.create_struct_proxy(fromty)(context, builder, val)
    yturu__mvtd = context.cast(builder, glsw__elk.obj, fromty.df_type, toty
        .df_type)
    tcsu__sfnjr = cgutils.create_struct_proxy(toty)(context, builder)
    tcsu__sfnjr.obj = yturu__mvtd
    return tcsu__sfnjr._getvalue()
