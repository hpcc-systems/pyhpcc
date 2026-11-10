"""DB-API connection implementation for HPCC WsSQL2."""

import re
import threading

from pyhpcc.sql._utils import _as_list
from pyhpcc.sql.config import SQLConfig
from pyhpcc.sql.cursor import Cursor
from pyhpcc.sql.errors import (
    DatabaseError,
    InterfaceError,
    NotSupportedError,
    OperationalError,
)
from pyhpcc.sql.transport import WsSql2Transport

_TABLE_COLUMNS = (
    "TABLE_CAT",
    "TABLE_SCHEM",
    "TABLE_NAME",
    "TABLE_TYPE",
    "REMARKS",
    "TYPE_CAT",
    "TYPE_SCHEM",
    "TYPE_NAME",
    "SELF_REFERENCING_COL_NAME",
    "REF_GENERATION",
)
_COLUMN_COLUMNS = (
    "TABLE_CAT",
    "TABLE_SCHEM",
    "TABLE_NAME",
    "COLUMN_NAME",
    "DATA_TYPE",
    "TYPE_NAME",
    "COLUMN_SIZE",
    "BUFFER_LENGTH",
    "DECIMAL_DIGITS",
    "NUM_PREC_RADIX",
    "NULLABLE",
    "REMARKS",
    "COLUMN_DEF",
    "SQL_DATA_TYPE",
    "SQL_DATETIME_SUB",
    "CHAR_OCTET_LENGTH",
    "ORDINAL_POSITION",
    "IS_NULLABLE",
    "SCOPE_CATALOG",
    "SCOPE_SCHEMA",
    "SCOPE_TABLE",
    "SOURCE_DATA_TYPE",
    "IS_AUTOINCREMENT",
    "IS_GENERATEDCOLUMN",
)
_DATA_TYPE_CODES = {
    "BOOLEAN": 16,
    "BOOL": 16,
    "BIT": -7,
    "TINYINT": -6,
    "UTINYINT": 5,
    "SMALLINT": 5,
    "USMALLINT": 4,
    "INTEGER": 4,
    "INT": 4,
    "BIGINT": -5,
    "UINTEGER": -5,
    "UBIGINT": 1111,
    "FLOAT": 6,
    "REAL": 7,
    "DOUBLE": 8,
    "DECIMAL": 3,
    "NUMERIC": 2,
    "VARCHAR": 12,
    "UUID": 1111,
    "DATE": 91,
    "TIME": 92,
    "TIME WITH TIME ZONE": 2013,
    "TIMESTAMP": 93,
    "TIMESTAMP WITH TIME ZONE": 2014,
    "BLOB": 2004,
    "BYTEA": 2004,
    "ARRAY": 2003,
    "STRUCT": 2002,
    "OTHER": 1111,
}
_INTEGER_METADATA_COLUMNS = {
    "DATA_TYPE",
    "COLUMN_SIZE",
    "BUFFER_LENGTH",
    "DECIMAL_DIGITS",
    "NUM_PREC_RADIX",
    "NULLABLE",
    "SQL_DATA_TYPE",
    "SQL_DATETIME_SUB",
    "CHAR_OCTET_LENGTH",
    "ORDINAL_POSITION",
}


class Connection:
    def __init__(self, auth, config):
        self.auth = auth
        self._config = config
        self._transport = WsSql2Transport(auth, config)
        self._cursors = set()
        self._lock = threading.Lock()
        self._closed = False

    @property
    def autocommit(self):
        return True

    @autocommit.setter
    def autocommit(self, value):
        if not value:
            raise NotSupportedError("WsSQL2 does not support transactions")

    def cursor(self):
        self._check_open()
        cursor = Cursor(self)
        with self._lock:
            self._cursors.add(cursor)
        return cursor

    def close(self):
        with self._lock:
            if self._closed:
                return
            self._closed = True
            cursors = tuple(self._cursors)
        first_error = None
        for cursor in cursors:
            try:
                cursor.close()
            except DatabaseError as exc:
                if first_error is None:
                    first_error = exc
                else:
                    first_error.add_note(f"Additional cursor-close failure: {exc}")
        if first_error is not None:
            raise first_error

    def commit(self):
        self._check_open()

    def rollback(self):
        self._check_open()

    def cancel(self):
        self._check_open()
        first_error = None
        with self._lock:
            cursors = tuple(self._cursors)
        for cursor in cursors:
            try:
                cursor.cancel()
            except DatabaseError as exc:
                if first_error is None:
                    first_error = exc
                else:
                    first_error.add_note(f"Additional cancellation failure: {exc}")
        if first_error is not None:
            raise first_error

    def is_valid(self, timeout=0):
        self._check_open()
        if timeout < 0:
            raise InterfaceError("timeout cannot be negative")
        try:
            cursor = self.cursor()
            try:
                cursor.set_query_timeout(timeout)
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
            finally:
                cursor.close()
        except DatabaseError:
            return False

    def get_tables(self, table_pattern=None, types=None):
        cursor = self.cursor()
        try:
            if types and "TABLE" not in types:
                cursor._set_local_result(
                    [(name, "VARCHAR", 0, 0) for name in _TABLE_COLUMNS], []
                )
                return cursor
            pattern = (table_pattern or "*").replace("%", "*")
            rows = []
            offset = 0
            while True:
                response = self._transport.dfu_query(
                    {
                        "LogicalName": pattern,
                        "PageStartFrom": str(offset),
                        "PageSize": "100",
                        "IncludeSuperOwner": "true",
                    }
                )
                result = response.get("DFUQueryResponse")
                files_wrapper = (
                    result.get("DFULogicalFiles") if isinstance(result, dict) else None
                )
                if not isinstance(files_wrapper, dict):
                    raise OperationalError(
                        f"WsDfu response is missing DFULogicalFiles from {self._config.dfu_endpoint}"
                    )
                files = _as_list(files_wrapper.get("DFULogicalFile"))
                for file in files:
                    if not isinstance(file, dict) or file.get("isDirectory", False):
                        continue
                    rows.append(
                        [
                            None,
                            None,
                            file.get("Name"),
                            "TABLE",
                            file.get("Description"),
                            None,
                            None,
                            None,
                            None,
                            None,
                        ]
                    )
                if not files:
                    break
                offset += len(files)
                try:
                    total = int(result.get("NumFiles", -1))
                except (TypeError, ValueError):
                    total = -1
                if total >= 0 and offset >= total:
                    break
            cursor._set_local_result(
                [(name, "VARCHAR", 0, 0) for name in _TABLE_COLUMNS], rows
            )
            return cursor
        except Exception:
            cursor.close()
            raise

    def get_columns(self, table_pattern=None, column_pattern=None):
        tables = self.get_tables(table_pattern, ["TABLE"])
        try:
            table_names = [row[2] for row in tables.fetchall() if row[2] is not None]
        finally:
            tables.close()
        rows = []
        for logical_name in table_names:
            escaped_name = logical_name.replace("'", "''")
            description = self._transport.query_all(
                f"DESCRIBE SELECT * FROM hpcc_scan('{escaped_name}')",
                self._config.read_timeout,
            )
            ordinal = 0
            for field in description:
                if not isinstance(field, list) or len(field) < 2:
                    continue
                column_name = str(field[0])
                if not _matches(column_name, column_pattern):
                    continue
                raw_type = str(field[1])
                type_name, precision, scale = _parse_type(raw_type)
                nullable = str(field[2]).upper() if len(field) > 2 and field[2] else ""
                nullable_code = {"YES": 1, "NO": 0}.get(nullable, 2)
                radix = (
                    2
                    if type_name in {"REAL", "FLOAT", "DOUBLE"}
                    else (
                        10
                        if type_name
                        in {"TINYINT", "SMALLINT", "INTEGER", "BIGINT", "DECIMAL"}
                        else None
                    )
                )
                ordinal += 1
                rows.append(
                    [
                        None,
                        None,
                        logical_name,
                        column_name,
                        _data_type_code(type_name),
                        raw_type,
                        precision or None,
                        None,
                        scale or None,
                        radix,
                        nullable_code,
                        None,
                        None,
                        None,
                        None,
                        None,
                        ordinal,
                        nullable,
                        None,
                        None,
                        None,
                        None,
                        "NO",
                        "NO",
                    ]
                )
        cursor = self.cursor()
        cursor._set_local_result(
            [
                (
                    name,
                    "INTEGER" if name in _INTEGER_METADATA_COLUMNS else "VARCHAR",
                    0,
                    0,
                )
                for name in _COLUMN_COLUMNS
            ],
            rows,
        )
        return cursor

    def __enter__(self):
        self._check_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _remove_cursor(self, cursor):
        with self._lock:
            self._cursors.discard(cursor)

    def _check_open(self):
        if self._closed:
            raise InterfaceError("Connection is closed")


def connect(
    auth,
    *,
    sql_url=None,
    dfu_url=None,
    connect_timeout=30,
    read_timeout=None,
):
    """Create a DB-API connection using an existing PyHPCC ``Auth`` object."""
    config = SQLConfig.from_auth(
        auth,
        sql_url=sql_url,
        dfu_url=dfu_url,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
    )
    return Connection(auth, config)


def _matches(value, pattern):
    if pattern is None or pattern == "":
        return True
    regex = "".join(
        ".*" if char == "%" else "." if char == "_" else re.escape(char)
        for char in pattern
    )
    return re.fullmatch(regex, value, re.IGNORECASE) is not None


def _parse_type(value):
    from pyhpcc.sql.types import describe_type

    name, precision, scale = describe_type(value)
    return name, precision, scale


def _data_type_code(name):
    if name.startswith("VARCHAR("):
        return _DATA_TYPE_CODES["VARCHAR"]
    if name.startswith("TIME("):
        return _DATA_TYPE_CODES["TIME"]
    if name.startswith("TIMESTAMP("):
        return _DATA_TYPE_CODES["TIMESTAMP"]
    if name.startswith("LIST(") or name.endswith("[]"):
        return _DATA_TYPE_CODES["ARRAY"]
    if name.startswith("STRUCT("):
        return _DATA_TYPE_CODES["STRUCT"]
    return _DATA_TYPE_CODES.get(name, _DATA_TYPE_CODES["OTHER"])
