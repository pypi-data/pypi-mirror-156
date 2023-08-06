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
    xruug__uekh = {}
    yymn__uvrth, xqy__ktffg = self._current_database_schema(connection, **kw)
    dwswq__mbic = self._denormalize_quote_join(yymn__uvrth, schema)
    try:
        bysa__ber = self._get_schema_primary_keys(connection, dwswq__mbic, **kw
            )
        qjk__baf = connection.execute(text(
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
    except sa_exc.ProgrammingError as dge__tnm:
        if dge__tnm.orig.errno == 90030:
            return None
        raise
    for table_name, euq__qzma, hjz__cpy, fkzqz__cyj, wlhmc__woygb, otn__gtra, lst__mqmv, vnljs__jfuw, jfo__gqa, rob__cyei in qjk__baf:
        table_name = self.normalize_name(table_name)
        euq__qzma = self.normalize_name(euq__qzma)
        if table_name not in xruug__uekh:
            xruug__uekh[table_name] = list()
        if euq__qzma.startswith('sys_clustering_column'):
            continue
        ytq__wos = self.ischema_names.get(hjz__cpy, None)
        jyl__cdtu = {}
        if ytq__wos is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(hjz__cpy, euq__qzma))
            ytq__wos = sqltypes.NULLTYPE
        elif issubclass(ytq__wos, sqltypes.FLOAT):
            jyl__cdtu['precision'] = wlhmc__woygb
            jyl__cdtu['decimal_return_scale'] = otn__gtra
        elif issubclass(ytq__wos, sqltypes.Numeric):
            jyl__cdtu['precision'] = wlhmc__woygb
            jyl__cdtu['scale'] = otn__gtra
        elif issubclass(ytq__wos, (sqltypes.String, sqltypes.BINARY)):
            jyl__cdtu['length'] = fkzqz__cyj
        kvmfk__zkuyj = ytq__wos if isinstance(ytq__wos, sqltypes.NullType
            ) else ytq__wos(**jyl__cdtu)
        ztfy__rdx = bysa__ber.get(table_name)
        xruug__uekh[table_name].append({'name': euq__qzma, 'type':
            kvmfk__zkuyj, 'nullable': lst__mqmv == 'YES', 'default':
            vnljs__jfuw, 'autoincrement': jfo__gqa == 'YES', 'comment':
            rob__cyei, 'primary_key': euq__qzma in bysa__ber[table_name][
            'constrained_columns'] if ztfy__rdx else False})
    return xruug__uekh


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
    xruug__uekh = []
    yymn__uvrth, xqy__ktffg = self._current_database_schema(connection, **kw)
    dwswq__mbic = self._denormalize_quote_join(yymn__uvrth, schema)
    bysa__ber = self._get_schema_primary_keys(connection, dwswq__mbic, **kw)
    qjk__baf = connection.execute(text(
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
    for table_name, euq__qzma, hjz__cpy, fkzqz__cyj, wlhmc__woygb, otn__gtra, lst__mqmv, vnljs__jfuw, jfo__gqa, rob__cyei in qjk__baf:
        table_name = self.normalize_name(table_name)
        euq__qzma = self.normalize_name(euq__qzma)
        if euq__qzma.startswith('sys_clustering_column'):
            continue
        ytq__wos = self.ischema_names.get(hjz__cpy, None)
        jyl__cdtu = {}
        if ytq__wos is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(hjz__cpy, euq__qzma))
            ytq__wos = sqltypes.NULLTYPE
        elif issubclass(ytq__wos, sqltypes.FLOAT):
            jyl__cdtu['precision'] = wlhmc__woygb
            jyl__cdtu['decimal_return_scale'] = otn__gtra
        elif issubclass(ytq__wos, sqltypes.Numeric):
            jyl__cdtu['precision'] = wlhmc__woygb
            jyl__cdtu['scale'] = otn__gtra
        elif issubclass(ytq__wos, (sqltypes.String, sqltypes.BINARY)):
            jyl__cdtu['length'] = fkzqz__cyj
        kvmfk__zkuyj = ytq__wos if isinstance(ytq__wos, sqltypes.NullType
            ) else ytq__wos(**jyl__cdtu)
        ztfy__rdx = bysa__ber.get(table_name)
        xruug__uekh.append({'name': euq__qzma, 'type': kvmfk__zkuyj,
            'nullable': lst__mqmv == 'YES', 'default': vnljs__jfuw,
            'autoincrement': jfo__gqa == 'YES', 'comment': rob__cyei if 
            rob__cyei != '' else None, 'primary_key': euq__qzma in
            bysa__ber[table_name]['constrained_columns'] if ztfy__rdx else 
            False})
    return xruug__uekh


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
