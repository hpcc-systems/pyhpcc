"""PEP 249 driver for HPCC Systems WsSQL2."""

import datetime

from pyhpcc.sql.connection import connect
from pyhpcc.sql.errors import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    TimeoutError,
    Warning,
)


class DBAPITypeObject:
    def __init__(self, *values):
        self.values = frozenset(values)

    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        if other in self.values:
            return True
        return any(other.startswith(value + "(") for value in self.values)

    def __contains__(self, other):
        return self == other

    def __repr__(self):
        return f"DBAPITypeObject({', '.join(sorted(self.values))})"


apilevel = "2.0"
threadsafety = 1
paramstyle = "qmark"

Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime
DateFromTicks = datetime.date.fromtimestamp
TimestampFromTicks = datetime.datetime.fromtimestamp
Binary = bytes


def TimeFromTicks(ticks):
    return datetime.datetime.fromtimestamp(ticks).time()


STRING = DBAPITypeObject("CHAR", "VARCHAR", "TEXT", "STRING")
BINARY = DBAPITypeObject("BLOB", "BYTEA")
NUMBER = DBAPITypeObject(
    "TINYINT",
    "UTINYINT",
    "SMALLINT",
    "USMALLINT",
    "INTEGER",
    "INT",
    "UINTEGER",
    "BIGINT",
    "UBIGINT",
    "HUGEINT",
    "UHUGEINT",
    "BIGNUM",
    "DECIMAL",
    "NUMERIC",
    "FLOAT",
    "REAL",
    "DOUBLE",
)
DATETIME = DBAPITypeObject(
    "DATE",
    "TIME",
    "TIME WITH TIME ZONE",
    "TIME_TZ",
    "TIMESTAMP",
    "TIMESTAMP WITH TIME ZONE",
    "TIMESTAMP_TZ",
    "TIMESTAMPTZ",
)
ROWID = DBAPITypeObject("ROWID")

__all__ = [
    "BINARY",
    "DATETIME",
    "NUMBER",
    "ROWID",
    "STRING",
    "Binary",
    "DBAPITypeObject",
    "DataError",
    "DatabaseError",
    "Date",
    "DateFromTicks",
    "Error",
    "IntegrityError",
    "InterfaceError",
    "InternalError",
    "NotSupportedError",
    "OperationalError",
    "ProgrammingError",
    "Time",
    "TimeFromTicks",
    "TimeoutError",
    "Timestamp",
    "TimestampFromTicks",
    "Warning",
    "apilevel",
    "connect",
    "paramstyle",
    "threadsafety",
]
