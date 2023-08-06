import hashlib
import inspect
import warnings
import snowflake.sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy import exc as sa_exc
from sqlalchemy import util as sa_util
from sqlalchemy.sql import text
_check_snowflake_sqlalchemy_change = True


def _get_schema_columns(self, connection, schema, **kw):
    mzobg__ggnz = {}
    ywm__fvm, ykt__iai = self._current_database_schema(connection, **kw)
    pazh__wvwpu = self._denormalize_quote_join(ywm__fvm, schema)
    try:
        brkd__kdmep = self._get_schema_primary_keys(connection, pazh__wvwpu,
            **kw)
        pvdv__mmw = connection.execute(text(
            """
        SELECT /* sqlalchemy:_get_schema_columns */
                ic.table_name,
                ic.column_name,
                ic.data_type,
                ic.character_maximum_length,
                ic.numeric_precision,
                ic.numeric_scale,
                ic.is_nullable,
                ic.column_default,
                ic.is_identity,
                ic.comment
            FROM information_schema.columns ic
            WHERE ic.table_schema=:table_schema
            ORDER BY ic.ordinal_position"""
            ), {'table_schema': self.denormalize_name(schema)})
    except sa_exc.ProgrammingError as elejp__fho:
        if elejp__fho.orig.errno == 90030:
            return None
        raise
    for table_name, yffd__bhbnq, dwpcz__dalb, gpypx__psv, tdqr__qdc, kmey__okxce, eoexi__qrwl, sba__zpf, bbnqf__bqpj, lfluu__vsdry in pvdv__mmw:
        table_name = self.normalize_name(table_name)
        yffd__bhbnq = self.normalize_name(yffd__bhbnq)
        if table_name not in mzobg__ggnz:
            mzobg__ggnz[table_name] = list()
        if yffd__bhbnq.startswith('sys_clustering_column'):
            continue
        pfr__wczz = self.ischema_names.get(dwpcz__dalb, None)
        mdqk__cynnk = {}
        if pfr__wczz is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(dwpcz__dalb, yffd__bhbnq))
            pfr__wczz = sqltypes.NULLTYPE
        elif issubclass(pfr__wczz, sqltypes.FLOAT):
            mdqk__cynnk['precision'] = tdqr__qdc
            mdqk__cynnk['decimal_return_scale'] = kmey__okxce
        elif issubclass(pfr__wczz, sqltypes.Numeric):
            mdqk__cynnk['precision'] = tdqr__qdc
            mdqk__cynnk['scale'] = kmey__okxce
        elif issubclass(pfr__wczz, (sqltypes.String, sqltypes.BINARY)):
            mdqk__cynnk['length'] = gpypx__psv
        eokca__rblw = pfr__wczz if isinstance(pfr__wczz, sqltypes.NullType
            ) else pfr__wczz(**mdqk__cynnk)
        qrgdm__tgts = brkd__kdmep.get(table_name)
        mzobg__ggnz[table_name].append({'name': yffd__bhbnq, 'type':
            eokca__rblw, 'nullable': eoexi__qrwl == 'YES', 'default':
            sba__zpf, 'autoincrement': bbnqf__bqpj == 'YES', 'comment':
            lfluu__vsdry, 'primary_key': yffd__bhbnq in brkd__kdmep[
            table_name]['constrained_columns'] if qrgdm__tgts else False})
    return mzobg__ggnz


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_schema_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdf39af1ac165319d3b6074e8cf9296a090a21f0e2c05b644ff8ec0e56e2d769':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns = (
    _get_schema_columns)


def _get_table_columns(self, connection, table_name, schema=None, **kw):
    mzobg__ggnz = []
    ywm__fvm, ykt__iai = self._current_database_schema(connection, **kw)
    pazh__wvwpu = self._denormalize_quote_join(ywm__fvm, schema)
    brkd__kdmep = self._get_schema_primary_keys(connection, pazh__wvwpu, **kw)
    pvdv__mmw = connection.execute(text(
        """
    SELECT /* sqlalchemy:get_table_columns */
            ic.table_name,
            ic.column_name,
            ic.data_type,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.is_nullable,
            ic.column_default,
            ic.is_identity,
            ic.comment
        FROM information_schema.columns ic
        WHERE ic.table_schema=:table_schema
        AND ic.table_name=:table_name
        ORDER BY ic.ordinal_position"""
        ), {'table_schema': self.denormalize_name(schema), 'table_name':
        self.denormalize_name(table_name)})
    for table_name, yffd__bhbnq, dwpcz__dalb, gpypx__psv, tdqr__qdc, kmey__okxce, eoexi__qrwl, sba__zpf, bbnqf__bqpj, lfluu__vsdry in pvdv__mmw:
        table_name = self.normalize_name(table_name)
        yffd__bhbnq = self.normalize_name(yffd__bhbnq)
        if yffd__bhbnq.startswith('sys_clustering_column'):
            continue
        pfr__wczz = self.ischema_names.get(dwpcz__dalb, None)
        mdqk__cynnk = {}
        if pfr__wczz is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(dwpcz__dalb, yffd__bhbnq))
            pfr__wczz = sqltypes.NULLTYPE
        elif issubclass(pfr__wczz, sqltypes.FLOAT):
            mdqk__cynnk['precision'] = tdqr__qdc
            mdqk__cynnk['decimal_return_scale'] = kmey__okxce
        elif issubclass(pfr__wczz, sqltypes.Numeric):
            mdqk__cynnk['precision'] = tdqr__qdc
            mdqk__cynnk['scale'] = kmey__okxce
        elif issubclass(pfr__wczz, (sqltypes.String, sqltypes.BINARY)):
            mdqk__cynnk['length'] = gpypx__psv
        eokca__rblw = pfr__wczz if isinstance(pfr__wczz, sqltypes.NullType
            ) else pfr__wczz(**mdqk__cynnk)
        qrgdm__tgts = brkd__kdmep.get(table_name)
        mzobg__ggnz.append({'name': yffd__bhbnq, 'type': eokca__rblw,
            'nullable': eoexi__qrwl == 'YES', 'default': sba__zpf,
            'autoincrement': bbnqf__bqpj == 'YES', 'comment': lfluu__vsdry if
            lfluu__vsdry != '' else None, 'primary_key': yffd__bhbnq in
            brkd__kdmep[table_name]['constrained_columns'] if qrgdm__tgts else
            False})
    return mzobg__ggnz


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_table_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9ecc8a2425c655836ade4008b1b98a8fd1819f3be43ba77b0fbbfc1f8740e2be':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns = (
    _get_table_columns)
