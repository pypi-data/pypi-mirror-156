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
            aofer__tuku = idx
            ttd__okkq = df.data
            mylht__etwr = df.columns
            gdx__kbg = self.replace_range_with_numeric_idx_if_needed(df,
                aofer__tuku)
            czu__hqa = DataFrameType(ttd__okkq, gdx__kbg, mylht__etwr)
            return czu__hqa(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            lqohw__nkfo = idx.types[0]
            jjaez__itxx = idx.types[1]
            if isinstance(lqohw__nkfo, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(jjaez__itxx):
                    ndl__ftf = get_overload_const_str(jjaez__itxx)
                    if ndl__ftf not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, ndl__ftf))
                    zpxjg__gxn = df.columns.index(ndl__ftf)
                    return df.data[zpxjg__gxn].dtype(*args)
                if isinstance(jjaez__itxx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(lqohw__nkfo
                ) and lqohw__nkfo.dtype == types.bool_ or isinstance(
                lqohw__nkfo, types.SliceType):
                gdx__kbg = self.replace_range_with_numeric_idx_if_needed(df,
                    lqohw__nkfo)
                if is_overload_constant_str(jjaez__itxx):
                    trp__ryfia = get_overload_const_str(jjaez__itxx)
                    if trp__ryfia not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {trp__ryfia}'
                            )
                    zpxjg__gxn = df.columns.index(trp__ryfia)
                    bzhm__eecl = df.data[zpxjg__gxn]
                    vxfzv__pztqs = bzhm__eecl.dtype
                    htki__uuc = types.literal(df.columns[zpxjg__gxn])
                    czu__hqa = bodo.SeriesType(vxfzv__pztqs, bzhm__eecl,
                        gdx__kbg, htki__uuc)
                    return czu__hqa(*args)
                if isinstance(jjaez__itxx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(jjaez__itxx):
                    xwjv__thy = get_overload_const_list(jjaez__itxx)
                    hqcy__dgfm = types.unliteral(jjaez__itxx)
                    if hqcy__dgfm.dtype == types.bool_:
                        if len(df.columns) != len(xwjv__thy):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {xwjv__thy} has {len(xwjv__thy)} values'
                                )
                        zyy__qvob = []
                        mnj__pgrhf = []
                        for brvre__ixpyi in range(len(xwjv__thy)):
                            if xwjv__thy[brvre__ixpyi]:
                                zyy__qvob.append(df.columns[brvre__ixpyi])
                                mnj__pgrhf.append(df.data[brvre__ixpyi])
                        tqnzz__dfhd = tuple()
                        czu__hqa = DataFrameType(tuple(mnj__pgrhf),
                            gdx__kbg, tuple(zyy__qvob))
                        return czu__hqa(*args)
                    elif hqcy__dgfm.dtype == bodo.string_type:
                        tqnzz__dfhd, mnj__pgrhf = (
                            get_df_getitem_kept_cols_and_data(df, xwjv__thy))
                        czu__hqa = DataFrameType(mnj__pgrhf, gdx__kbg,
                            tqnzz__dfhd)
                        return czu__hqa(*args)
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
                zyy__qvob = []
                mnj__pgrhf = []
                for brvre__ixpyi, sevw__vho in enumerate(df.columns):
                    if sevw__vho[0] != ind_val:
                        continue
                    zyy__qvob.append(sevw__vho[1] if len(sevw__vho) == 2 else
                        sevw__vho[1:])
                    mnj__pgrhf.append(df.data[brvre__ixpyi])
                bzhm__eecl = tuple(mnj__pgrhf)
                vvgkx__uggqb = df.index
                mlo__fwzg = tuple(zyy__qvob)
                czu__hqa = DataFrameType(bzhm__eecl, vvgkx__uggqb, mlo__fwzg)
                return czu__hqa(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                zpxjg__gxn = df.columns.index(ind_val)
                bzhm__eecl = df.data[zpxjg__gxn]
                vxfzv__pztqs = bzhm__eecl.dtype
                vvgkx__uggqb = df.index
                htki__uuc = types.literal(df.columns[zpxjg__gxn])
                czu__hqa = bodo.SeriesType(vxfzv__pztqs, bzhm__eecl,
                    vvgkx__uggqb, htki__uuc)
                return czu__hqa(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            bzhm__eecl = df.data
            vvgkx__uggqb = self.replace_range_with_numeric_idx_if_needed(df,
                ind)
            mlo__fwzg = df.columns
            czu__hqa = DataFrameType(bzhm__eecl, vvgkx__uggqb, mlo__fwzg,
                is_table_format=df.is_table_format)
            return czu__hqa(*args)
        elif is_overload_constant_list(ind):
            qqxpf__dmpo = get_overload_const_list(ind)
            mlo__fwzg, bzhm__eecl = get_df_getitem_kept_cols_and_data(df,
                qqxpf__dmpo)
            vvgkx__uggqb = df.index
            jwpkx__izu = df.is_table_format and len(qqxpf__dmpo
                ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            czu__hqa = DataFrameType(bzhm__eecl, vvgkx__uggqb, mlo__fwzg,
                is_table_format=jwpkx__izu)
            return czu__hqa(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        gdx__kbg = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64,
            df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return gdx__kbg


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for kfsg__kvq in cols_to_keep_list:
        if kfsg__kvq not in df.columns:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(kfsg__kvq, df.columns))
    mlo__fwzg = tuple(cols_to_keep_list)
    bzhm__eecl = tuple(df.data[df.column_index[twyc__ptq]] for twyc__ptq in
        mlo__fwzg)
    return mlo__fwzg, bzhm__eecl


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
            zyy__qvob = []
            mnj__pgrhf = []
            for brvre__ixpyi, sevw__vho in enumerate(df.columns):
                if sevw__vho[0] != ind_val:
                    continue
                zyy__qvob.append(sevw__vho[1] if len(sevw__vho) == 2 else
                    sevw__vho[1:])
                mnj__pgrhf.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(brvre__ixpyi))
            qhnfp__udza = 'def impl(df, ind):\n'
            hon__rrwj = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(qhnfp__udza,
                zyy__qvob, ', '.join(mnj__pgrhf), hon__rrwj)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        qqxpf__dmpo = get_overload_const_list(ind)
        for kfsg__kvq in qqxpf__dmpo:
            if kfsg__kvq not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(kfsg__kvq, df.columns))
        zuo__afwgs = None
        if df.is_table_format and len(qqxpf__dmpo
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            dzduw__qab = [df.column_index[kfsg__kvq] for kfsg__kvq in
                qqxpf__dmpo]
            zuo__afwgs = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (dzduw__qab))}
            mnj__pgrhf = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta)'
                )
        else:
            mnj__pgrhf = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[kfsg__kvq]}).copy()'
                 for kfsg__kvq in qqxpf__dmpo)
        qhnfp__udza = 'def impl(df, ind):\n'
        hon__rrwj = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(qhnfp__udza,
            qqxpf__dmpo, mnj__pgrhf, hon__rrwj, extra_globals=zuo__afwgs)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        qhnfp__udza = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            qhnfp__udza += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        hon__rrwj = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            mnj__pgrhf = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            mnj__pgrhf = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[kfsg__kvq]})[ind]'
                 for kfsg__kvq in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(qhnfp__udza, df.
            columns, mnj__pgrhf, hon__rrwj)
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
        twyc__ptq = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(twyc__ptq)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        msu__vzt = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, msu__vzt)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kelwa__nvp, = args
        zwnnb__rqk = signature.return_type
        qcqx__njehl = cgutils.create_struct_proxy(zwnnb__rqk)(context, builder)
        qcqx__njehl.obj = kelwa__nvp
        context.nrt.incref(builder, signature.args[0], kelwa__nvp)
        return qcqx__njehl._getvalue()
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
        umav__vnh = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            kxh__gtyt = get_overload_const_int(idx.types[1])
            if kxh__gtyt < 0 or kxh__gtyt >= umav__vnh:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            ibwp__ldyf = [kxh__gtyt]
        else:
            is_out_series = False
            ibwp__ldyf = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= umav__vnh for
                ind in ibwp__ldyf):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[ibwp__ldyf])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                kxh__gtyt = ibwp__ldyf[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, kxh__gtyt)[
                        idx[0]])
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
    qhnfp__udza = 'def impl(I, idx):\n'
    qhnfp__udza += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        qhnfp__udza += f'  idx_t = {idx}\n'
    else:
        qhnfp__udza += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    hon__rrwj = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]'
    mnj__pgrhf = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[kfsg__kvq]})[idx_t]'
         for kfsg__kvq in col_names)
    if is_out_series:
        ykdfi__kpdmg = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        qhnfp__udza += f"""  return bodo.hiframes.pd_series_ext.init_series({mnj__pgrhf}, {hon__rrwj}, {ykdfi__kpdmg})
"""
        zec__qsn = {}
        exec(qhnfp__udza, {'bodo': bodo}, zec__qsn)
        return zec__qsn['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(qhnfp__udza, col_names,
        mnj__pgrhf, hon__rrwj)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    qhnfp__udza = 'def impl(I, idx):\n'
    qhnfp__udza += '  df = I._obj\n'
    suk__urco = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[kfsg__kvq]})[{idx}]'
         for kfsg__kvq in col_names)
    qhnfp__udza += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    qhnfp__udza += f"""  return bodo.hiframes.pd_series_ext.init_series(({suk__urco},), row_idx, None)
"""
    zec__qsn = {}
    exec(qhnfp__udza, {'bodo': bodo}, zec__qsn)
    impl = zec__qsn['impl']
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
        twyc__ptq = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(twyc__ptq)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        msu__vzt = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, msu__vzt)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kelwa__nvp, = args
        tfwsp__redr = signature.return_type
        ynjj__vrwic = cgutils.create_struct_proxy(tfwsp__redr)(context, builder
            )
        ynjj__vrwic.obj = kelwa__nvp
        context.nrt.incref(builder, signature.args[0], kelwa__nvp)
        return ynjj__vrwic._getvalue()
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
        qhnfp__udza = 'def impl(I, idx):\n'
        qhnfp__udza += '  df = I._obj\n'
        qhnfp__udza += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        hon__rrwj = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        mnj__pgrhf = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[kfsg__kvq]})[idx_t]'
             for kfsg__kvq in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(qhnfp__udza, df.
            columns, mnj__pgrhf, hon__rrwj)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        ayj__hibz = idx.types[1]
        if is_overload_constant_str(ayj__hibz):
            dphx__olutl = get_overload_const_str(ayj__hibz)
            kxh__gtyt = df.columns.index(dphx__olutl)

            def impl_col_name(I, idx):
                df = I._obj
                hon__rrwj = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
                    df)
                zwbdt__hudj = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, kxh__gtyt))
                return bodo.hiframes.pd_series_ext.init_series(zwbdt__hudj,
                    hon__rrwj, dphx__olutl).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(ayj__hibz):
            col_idx_list = get_overload_const_list(ayj__hibz)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(kfsg__kvq in df.columns for
                kfsg__kvq in col_idx_list):
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
    mnj__pgrhf = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[kfsg__kvq]})[idx[0]]'
         for kfsg__kvq in col_idx_list)
    hon__rrwj = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    qhnfp__udza = 'def impl(I, idx):\n'
    qhnfp__udza += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(qhnfp__udza,
        col_idx_list, mnj__pgrhf, hon__rrwj)


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
        twyc__ptq = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(twyc__ptq)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        msu__vzt = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, msu__vzt)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kelwa__nvp, = args
        afqje__yhdo = signature.return_type
        cgrw__kaptu = cgutils.create_struct_proxy(afqje__yhdo)(context, builder
            )
        cgrw__kaptu.obj = kelwa__nvp
        context.nrt.incref(builder, signature.args[0], kelwa__nvp)
        return cgrw__kaptu._getvalue()
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
        kxh__gtyt = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            zwbdt__hudj = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                kxh__gtyt)
            return bodo.utils.conversion.box_if_dt64(zwbdt__hudj[idx[0]])
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
        kxh__gtyt = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[kxh__gtyt]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            zwbdt__hudj = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                kxh__gtyt)
            zwbdt__hudj[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    cgrw__kaptu = cgutils.create_struct_proxy(fromty)(context, builder, val)
    kujf__vgh = context.cast(builder, cgrw__kaptu.obj, fromty.df_type, toty
        .df_type)
    dfy__pro = cgutils.create_struct_proxy(toty)(context, builder)
    dfy__pro.obj = kujf__vgh
    return dfy__pro._getvalue()
