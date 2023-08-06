"""
Support for PySpark APIs in Bodo JIT functions
"""
from collections import namedtuple
import numba
import numba.cpython.tupleobj
import numpy as np
import pyspark
import pyspark.sql.functions as F
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, infer_global, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_overload_constant_list, is_overload_constant_str, is_overload_true
ANON_SENTINEL = 'bodo_field_'


class SparkSessionType(types.Opaque):

    def __init__(self):
        super(SparkSessionType, self).__init__(name='SparkSessionType')


spark_session_type = SparkSessionType()
register_model(SparkSessionType)(models.OpaqueModel)


class SparkSessionBuilderType(types.Opaque):

    def __init__(self):
        super(SparkSessionBuilderType, self).__init__(name=
            'SparkSessionBuilderType')


spark_session_builder_type = SparkSessionBuilderType()
register_model(SparkSessionBuilderType)(models.OpaqueModel)


@intrinsic
def init_session(typingctx=None):

    def codegen(context, builder, signature, args):
        return context.get_constant_null(spark_session_type)
    return spark_session_type(), codegen


@intrinsic
def init_session_builder(typingctx=None):

    def codegen(context, builder, signature, args):
        return context.get_constant_null(spark_session_builder_type)
    return spark_session_builder_type(), codegen


@overload_method(SparkSessionBuilderType, 'appName', no_unliteral=True)
def overload_appName(A, s):
    return lambda A, s: A


@overload_method(SparkSessionBuilderType, 'getOrCreate', inline='always',
    no_unliteral=True)
def overload_getOrCreate(A):
    return lambda A: bodo.libs.pyspark_ext.init_session()


@typeof_impl.register(pyspark.sql.session.SparkSession)
def typeof_session(val, c):
    return spark_session_type


@box(SparkSessionType)
def box_spark_session(typ, val, c):
    zcfox__lgo = c.context.insert_const_string(c.builder.module, 'pyspark')
    nromj__ucb = c.pyapi.import_module_noblock(zcfox__lgo)
    tjguv__xslic = c.pyapi.object_getattr_string(nromj__ucb, 'sql')
    svaz__uxgo = c.pyapi.object_getattr_string(tjguv__xslic, 'SparkSession')
    seczs__opifh = c.pyapi.object_getattr_string(svaz__uxgo, 'builder')
    janav__viver = c.pyapi.call_method(seczs__opifh, 'getOrCreate', ())
    c.pyapi.decref(nromj__ucb)
    c.pyapi.decref(tjguv__xslic)
    c.pyapi.decref(svaz__uxgo)
    c.pyapi.decref(seczs__opifh)
    return janav__viver


@unbox(SparkSessionType)
def unbox_spark_session(typ, obj, c):
    return NativeValue(c.context.get_constant_null(spark_session_type))


@lower_constant(SparkSessionType)
def lower_constant_spark_session(context, builder, ty, pyval):
    return context.get_constant_null(spark_session_type)


class RowType(types.BaseNamedTuple):

    def __init__(self, types, fields):
        self.types = tuple(types)
        self.count = len(self.types)
        self.fields = tuple(fields)
        self.instance_class = namedtuple('Row', fields)
        bkk__bdcvj = 'Row({})'.format(', '.join(
            f'{hwaq__lsdks}:{eaa__cybxa}' for hwaq__lsdks, eaa__cybxa in
            zip(self.fields, self.types)))
        super(RowType, self).__init__(bkk__bdcvj)

    @property
    def key(self):
        return self.fields, self.types

    def __getitem__(self, i):
        return self.types[i]

    def __len__(self):
        return len(self.types)

    def __iter__(self):
        return iter(self.types)


@register_model(RowType)
class RowModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vyg__qis = [(hwaq__lsdks, eaa__cybxa) for hwaq__lsdks, eaa__cybxa in
            zip(fe_type.fields, fe_type.types)]
        super(RowModel, self).__init__(dmm, fe_type, vyg__qis)


@typeof_impl.register(pyspark.sql.types.Row)
def typeof_row(val, c):
    fields = val.__fields__ if hasattr(val, '__fields__') else tuple(
        f'{ANON_SENTINEL}{i}' for i in range(len(val)))
    return RowType(tuple(numba.typeof(eqg__ogb) for eqg__ogb in val), fields)


@box(RowType)
def box_row(typ, val, c):
    tpi__dlxnz = c.pyapi.unserialize(c.pyapi.serialize_object(pyspark.sql.
        types.Row))
    if all(hwaq__lsdks.startswith(ANON_SENTINEL) for hwaq__lsdks in typ.fields
        ):
        ituaq__qgyq = [c.box(eaa__cybxa, c.builder.extract_value(val, i)) for
            i, eaa__cybxa in enumerate(typ.types)]
        encj__ewgu = c.pyapi.call_function_objargs(tpi__dlxnz, ituaq__qgyq)
        for obj in ituaq__qgyq:
            c.pyapi.decref(obj)
        c.pyapi.decref(tpi__dlxnz)
        return encj__ewgu
    args = c.pyapi.tuple_pack([])
    ituaq__qgyq = []
    kvejp__xnleg = []
    for i, eaa__cybxa in enumerate(typ.types):
        wqcs__bhv = c.builder.extract_value(val, i)
        obj = c.box(eaa__cybxa, wqcs__bhv)
        kvejp__xnleg.append((typ.fields[i], obj))
        ituaq__qgyq.append(obj)
    kws = c.pyapi.dict_pack(kvejp__xnleg)
    encj__ewgu = c.pyapi.call(tpi__dlxnz, args, kws)
    for obj in ituaq__qgyq:
        c.pyapi.decref(obj)
    c.pyapi.decref(tpi__dlxnz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    return encj__ewgu


@infer_global(pyspark.sql.types.Row)
class RowConstructor(AbstractTemplate):

    def generic(self, args, kws):
        if args and kws:
            raise BodoError(
                'pyspark.sql.types.Row: Cannot use both args and kwargs to create Row'
                )
        qizq__jytd = ', '.join(f'arg{i}' for i in range(len(args)))
        xihhi__knzsw = ', '.join(f"{kuq__usz} = ''" for kuq__usz in kws)
        func_text = f'def row_stub({qizq__jytd}{xihhi__knzsw}):\n'
        func_text += '    pass\n'
        auuk__lkv = {}
        exec(func_text, {}, auuk__lkv)
        khdc__yaag = auuk__lkv['row_stub']
        ueik__gurm = numba.core.utils.pysignature(khdc__yaag)
        if args:
            ppafk__kcbo = RowType(args, tuple(f'{ANON_SENTINEL}{i}' for i in
                range(len(args))))
            return signature(ppafk__kcbo, *args).replace(pysig=ueik__gurm)
        kws = dict(kws)
        ppafk__kcbo = RowType(tuple(kws.values()), tuple(kws.keys()))
        return signature(ppafk__kcbo, *kws.values()).replace(pysig=ueik__gurm)


lower_builtin(pyspark.sql.types.Row, types.VarArg(types.Any))(numba.cpython
    .tupleobj.namedtuple_constructor)


class SparkDataFrameType(types.Type):

    def __init__(self, df):
        self.df = df
        super(SparkDataFrameType, self).__init__(f'SparkDataFrame({df})')

    @property
    def key(self):
        return self.df

    def copy(self):
        return SparkDataFrameType(self.df)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SparkDataFrameType)
class SparkDataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vyg__qis = [('df', fe_type.df)]
        super(SparkDataFrameModel, self).__init__(dmm, fe_type, vyg__qis)


make_attribute_wrapper(SparkDataFrameType, 'df', '_df')


@intrinsic
def init_spark_df(typingctx, df_typ=None):

    def codegen(context, builder, sig, args):
        df, = args
        spark_df = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        spark_df.df = df
        context.nrt.incref(builder, sig.args[0], df)
        return spark_df._getvalue()
    return SparkDataFrameType(df_typ)(df_typ), codegen


@overload_method(SparkSessionType, 'createDataFrame', inline='always',
    no_unliteral=True)
def overload_create_df(sp_session, data, schema=None, samplingRatio=None,
    verifySchema=True):
    check_runtime_cols_unsupported(data, 'spark.createDataFrame()')
    if isinstance(data, DataFrameType):

        def impl_df(sp_session, data, schema=None, samplingRatio=None,
            verifySchema=True):
            data = bodo.scatterv(data, warn_if_dist=False)
            return bodo.libs.pyspark_ext.init_spark_df(data)
        return impl_df
    if not (isinstance(data, types.List) and isinstance(data.dtype, RowType)):
        raise BodoError(
            f"SparkSession.createDataFrame(): 'data' should be a Pandas dataframe or list of Rows, not {data}"
            )
    uzp__aeoiy = data.dtype.fields
    atufu__hym = len(data.dtype.types)
    func_text = (
        'def impl(sp_session, data, schema=None, samplingRatio=None, verifySchema=True):\n'
        )
    func_text += f'  n = len(data)\n'
    fqph__yfzcm = []
    for i, eaa__cybxa in enumerate(data.dtype.types):
        ftc__bgkf = dtype_to_array_type(eaa__cybxa)
        func_text += (
            f'  A{i} = bodo.utils.utils.alloc_type(n, arr_typ{i}, (-1,))\n')
        fqph__yfzcm.append(ftc__bgkf)
    func_text += f'  for i in range(n):\n'
    func_text += f'    r = data[i]\n'
    for i in range(atufu__hym):
        func_text += (
            f'    A{i}[i] = bodo.utils.conversion.unbox_if_timestamp(r[{i}])\n'
            )
    qwp__bqpz = '({}{})'.format(', '.join(f'A{i}' for i in range(atufu__hym
        )), ',' if len(uzp__aeoiy) == 1 else '')
    func_text += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)\n'
        )
    func_text += f"""  pdf = bodo.hiframes.pd_dataframe_ext.init_dataframe({qwp__bqpz}, index, __col_name_meta_value_create_df)
"""
    func_text += f'  pdf = bodo.scatterv(pdf)\n'
    func_text += f'  return bodo.libs.pyspark_ext.init_spark_df(pdf)\n'
    auuk__lkv = {}
    acbrk__fxw = {'bodo': bodo, '__col_name_meta_value_create_df':
        ColNamesMetaType(tuple(uzp__aeoiy))}
    for i in range(atufu__hym):
        acbrk__fxw[f'arr_typ{i}'] = fqph__yfzcm[i]
    exec(func_text, acbrk__fxw, auuk__lkv)
    impl = auuk__lkv['impl']
    return impl


@overload_method(SparkDataFrameType, 'toPandas', inline='always',
    no_unliteral=True)
def overload_to_pandas(spark_df, _is_bodo_dist=False):
    if is_overload_true(_is_bodo_dist):
        return lambda spark_df, _is_bodo_dist=False: spark_df._df

    def impl(spark_df, _is_bodo_dist=False):
        return bodo.gatherv(spark_df._df, warn_if_rep=False)
    return impl


@overload_method(SparkDataFrameType, 'limit', inline='always', no_unliteral
    =True)
def overload_limit(spark_df, num):

    def impl(spark_df, num):
        return bodo.libs.pyspark_ext.init_spark_df(spark_df._df.iloc[:num])
    return impl


def _df_to_rows(df):
    pass


@overload(_df_to_rows)
def overload_df_to_rows(df):
    func_text = 'def impl(df):\n'
    for i in range(len(df.columns)):
        func_text += (
            f'  A{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    func_text += '  n = len(df)\n'
    func_text += '  out = []\n'
    func_text += '  for i in range(n):\n'
    afzvo__xyk = ', '.join(f'{c}=A{i}[i]' for i, c in enumerate(df.columns))
    func_text += f'    out.append(Row({afzvo__xyk}))\n'
    func_text += '  return out\n'
    auuk__lkv = {}
    acbrk__fxw = {'bodo': bodo, 'Row': pyspark.sql.types.Row}
    exec(func_text, acbrk__fxw, auuk__lkv)
    impl = auuk__lkv['impl']
    return impl


@overload_method(SparkDataFrameType, 'collect', inline='always',
    no_unliteral=True)
def overload_collect(spark_df):

    def impl(spark_df):
        data = bodo.gatherv(spark_df._df, warn_if_rep=False)
        return _df_to_rows(data)
    return impl


@overload_method(SparkDataFrameType, 'take', inline='always', no_unliteral=True
    )
def overload_take(spark_df, num):

    def impl(spark_df, num):
        return spark_df.limit(num).collect()
    return impl


@infer_getattr
class SparkDataFrameAttribute(AttributeTemplate):
    key = SparkDataFrameType

    def generic_resolve(self, sdf, attr):
        if attr in sdf.df.columns:
            return ColumnType(ExprType('col', (attr,)))


SparkDataFrameAttribute._no_unliteral = True


@overload_method(SparkDataFrameType, 'select', no_unliteral=True)
def overload_df_select(spark_df, *cols):
    return _gen_df_select(spark_df, cols)


def _gen_df_select(spark_df, cols, avoid_stararg=False):
    df_type = spark_df.df
    if isinstance(cols, tuple) and len(cols) == 1 and isinstance(cols[0], (
        types.StarArgTuple, types.StarArgUniTuple)):
        cols = cols[0]
    if len(cols) == 1 and is_overload_constant_list(cols[0]):
        cols = get_overload_const_list(cols[0])
    func_text = f"def impl(spark_df, {'' if avoid_stararg else '*cols'}):\n"
    func_text += '  df = spark_df._df\n'
    out_col_names = []
    out_data = []
    for col in cols:
        col = get_overload_const_str(col) if is_overload_constant_str(col
            ) else col
        out_col_names.append(_get_col_name(col))
        data, tcr__vjbq = _gen_col_code(col, df_type)
        func_text += tcr__vjbq
        out_data.append(data)
    return _gen_init_spark_df(func_text, out_data, out_col_names)


def _gen_init_spark_df(func_text, out_data, out_col_names):
    qwp__bqpz = '({}{})'.format(', '.join(out_data), ',' if len(out_data) ==
        1 else '')
    tits__yenc = '0' if not out_data else f'len({out_data[0]})'
    func_text += f'  n = {tits__yenc}\n'
    func_text += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)\n'
        )
    func_text += f"""  pdf = bodo.hiframes.pd_dataframe_ext.init_dataframe({qwp__bqpz}, index, __col_name_meta_value_init_spark_df)
"""
    func_text += f'  return bodo.libs.pyspark_ext.init_spark_df(pdf)\n'
    auuk__lkv = {}
    acbrk__fxw = {'bodo': bodo, 'np': np,
        '__col_name_meta_value_init_spark_df': ColNamesMetaType(tuple(
        out_col_names))}
    exec(func_text, acbrk__fxw, auuk__lkv)
    impl = auuk__lkv['impl']
    return impl


@overload_method(SparkDataFrameType, 'show', inline='always', no_unliteral=True
    )
def overload_show(spark_df, n=20, truncate=True, vertical=False):
    bxs__iqil = dict(truncate=truncate, vertical=vertical)
    yzav__qkpew = dict(truncate=True, vertical=False)
    check_unsupported_args('SparkDataFrameType.show', bxs__iqil, yzav__qkpew)

    def impl(spark_df, n=20, truncate=True, vertical=False):
        print(spark_df._df.head(n))
    return impl


@overload_method(SparkDataFrameType, 'printSchema', inline='always',
    no_unliteral=True)
def overload_print_schema(spark_df):

    def impl(spark_df):
        print(spark_df._df.dtypes)
    return impl


@overload_method(SparkDataFrameType, 'withColumn', inline='always',
    no_unliteral=True)
def overload_with_column(spark_df, colName, col):
    _check_column(col)
    if not is_overload_constant_str(colName):
        raise BodoError(
            f"SparkDataFrame.withColumn(): 'colName' should be a constant string, not {colName}"
            )
    col_name = get_overload_const_str(colName)
    aoaeh__blwl = spark_df.df.columns
    pees__qrrxb = aoaeh__blwl if col_name in aoaeh__blwl else aoaeh__blwl + (
        col_name,)
    bra__beu, jbzhx__lnn = _gen_col_code(col, spark_df.df)
    out_data = [(bra__beu if c == col_name else
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {aoaeh__blwl.index(c)})'
        ) for c in pees__qrrxb]
    func_text = 'def impl(spark_df, colName, col):\n'
    func_text += '  df = spark_df._df\n'
    func_text += jbzhx__lnn
    return _gen_init_spark_df(func_text, out_data, pees__qrrxb)


@overload_method(SparkDataFrameType, 'withColumnRenamed', inline='always',
    no_unliteral=True)
def overload_with_column_renamed(spark_df, existing, new):
    if not (is_overload_constant_str(existing) and is_overload_constant_str
        (new)):
        raise BodoError(
            f"SparkDataFrame.withColumnRenamed(): 'existing' and 'new' should be a constant strings, not ({existing}, {new})"
            )
    mco__sewzs = get_overload_const_str(existing)
    ebgih__cuc = get_overload_const_str(new)
    aoaeh__blwl = spark_df.df.columns
    pees__qrrxb = tuple(ebgih__cuc if c == mco__sewzs else c for c in
        aoaeh__blwl)
    out_data = [f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
         for i in range(len(aoaeh__blwl))]
    func_text = 'def impl(spark_df, existing, new):\n'
    func_text += '  df = spark_df._df\n'
    return _gen_init_spark_df(func_text, out_data, pees__qrrxb)


@overload_attribute(SparkDataFrameType, 'columns', inline='always')
def overload_dataframe_columns(spark_df):
    roz__akr = list(str(kuq__usz) for kuq__usz in spark_df.df.columns)
    func_text = 'def impl(spark_df):\n'
    func_text += f'  return {roz__akr}\n'
    auuk__lkv = {}
    exec(func_text, {}, auuk__lkv)
    impl = auuk__lkv['impl']
    return impl


class ColumnType(types.Type):

    def __init__(self, expr):
        self.expr = expr
        super(ColumnType, self).__init__(f'Column({expr})')

    @property
    def key(self):
        return self.expr

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(ColumnType)(models.OpaqueModel)


class ExprType(types.Type):

    def __init__(self, op, children):
        self.op = op
        self.children = children
        super(ExprType, self).__init__(f'{op}({children})')

    @property
    def key(self):
        return self.op, self.children

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(ExprType)(models.OpaqueModel)


@intrinsic
def init_col_from_name(typingctx, col=None):
    assert is_overload_constant_str(col)
    ocxil__zhzj = get_overload_const_str(col)
    yepwq__coyzj = ColumnType(ExprType('col', (ocxil__zhzj,)))

    def codegen(context, builder, signature, args):
        return context.get_constant_null(yepwq__coyzj)
    return yepwq__coyzj(col), codegen


@overload(F.col, no_unliteral=True)
@overload(F.column, no_unliteral=True)
def overload_f_col(col):
    if not is_overload_constant_str(col):
        raise BodoError(
            f'pyspark.sql.functions.col(): column name should be a constant string, not {col}'
            )
    return lambda col: init_col_from_name(col)


@intrinsic
def init_f_sum(typingctx, col=None):
    yepwq__coyzj = ColumnType(ExprType('sum', (col.expr,)))

    def codegen(context, builder, signature, args):
        return context.get_constant_null(yepwq__coyzj)
    return yepwq__coyzj(col), codegen


@overload(F.sum, no_unliteral=True)
def overload_f_sum(col):
    if is_overload_constant_str(col):
        return lambda col: init_f_sum(init_col_from_name(col))
    if not isinstance(col, ColumnType):
        raise BodoError(
            f'pyspark.sql.functions.sum(): input should be a Column object or a constant string, not {col}'
            )
    return lambda col: init_f_sum(col)


def _get_col_name(col):
    if isinstance(col, str):
        return col
    _check_column(col)
    return _get_col_name_exr(col.expr)


def _get_col_name_exr(expr):
    if expr.op == 'sum':
        return f'sum({_get_col_name_exr(expr.children[0])})'
    assert expr.op == 'col'
    return expr.children[0]


def _gen_col_code(col, df_type):
    if isinstance(col, str):
        return _gen_col_code_colname(col, df_type)
    _check_column(col)
    return _gen_col_code_expr(col.expr, df_type)


def _gen_col_code_expr(expr, df_type):
    if expr.op == 'col':
        return _gen_col_code_colname(expr.children[0], df_type)
    if expr.op == 'sum':
        pxreo__mrc, jrfwq__ulzw = _gen_col_code_expr(expr.children[0], df_type)
        i = ir_utils.next_label()
        func_text = f"""  A{i} = np.asarray([bodo.libs.array_ops.array_op_sum({pxreo__mrc}, True, 0)])
"""
        return f'A{i}', jrfwq__ulzw + func_text


def _gen_col_code_colname(col_name, df_type):
    dni__bbo = df_type.columns.index(col_name)
    i = ir_utils.next_label()
    func_text = (
        f'  A{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {dni__bbo})\n'
        )
    return f'A{i}', func_text


def _check_column(col):
    if not isinstance(col, ColumnType):
        raise BodoError('Column object expected')
