"""Mapping from WsSQL2 types and values to Python values."""

import datetime
import decimal
import re
import uuid

from pyhpcc.sql.errors import DataError

_DECIMAL = re.compile(
    r"(?:DECIMAL|NUMERIC)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", re.IGNORECASE
)


def describe_type(type_name: str | None, precision: int = 0, scale: int = 0):
    name = (type_name or "OTHER").strip().upper()
    match = _DECIMAL.fullmatch(name)
    if match:
        precision, scale = int(match.group(1)), int(match.group(2))
        name = "DECIMAL"
    if not precision:
        precision = {
            "TINYINT": 3,
            "SMALLINT": 5,
            "UTINYINT": 5,
            "INTEGER": 10,
            "INT": 10,
            "USMALLINT": 10,
            "BIGINT": 19,
            "UINTEGER": 20,
            "BOOLEAN": 1,
            "BOOL": 1,
            "REAL": 7,
            "FLOAT": 7,
            "DOUBLE": 15,
        }.get(name, 0)
    return name, precision, scale


def decode_value(value, type_name: str | None):
    if value is None:
        return None
    name = (type_name or "OTHER").strip().upper()
    normalized = _DECIMAL.sub("DECIMAL", name)
    try:
        if name in {"BOOLEAN", "BOOL"}:
            if isinstance(value, bool):
                return value
            lowered = str(value).lower()
            if lowered not in {"true", "false"}:
                raise ValueError("not a boolean")
            return lowered == "true"
        if name == "TINYINT":
            return _exact_integer(value, -128, 127)
        if name in {"UTINYINT", "SMALLINT"}:
            return _exact_integer(
                value,
                0 if name == "UTINYINT" else -32768,
                255 if name == "UTINYINT" else 32767,
            )
        if name in {"USMALLINT", "INTEGER", "INT"}:
            low, high = (0, 65535) if name == "USMALLINT" else (-2147483648, 2147483647)
            return _exact_integer(value, low, high)
        if name in {"BIGINT", "UINTEGER"}:
            low, high = (
                (0, 4294967295)
                if name == "UINTEGER"
                else (-9223372036854775808, 9223372036854775807)
            )
            return _exact_integer(value, low, high)
        if name in {"UBIGINT", "HUGEINT", "UHUGEINT", "BIGNUM"}:
            return _exact_big_integer(value)
        if name in {"FLOAT", "REAL", "DOUBLE"}:
            text = str(value).lower()
            return {
                "inf": float("inf"),
                "+inf": float("inf"),
                "-inf": float("-inf"),
                "nan": float("nan"),
            }.get(text, float(text))
        if normalized in {"DECIMAL", "NUMERIC"}:
            return decimal.Decimal(str(value))
        if name.startswith(("VARCHAR(", "ENUM(")) or name in {
            "VARCHAR",
            "BIT",
            "INTERVAL",
            "ENUM",
        }:
            return str(value)
        if name == "UUID":
            return uuid.UUID(str(value))
        if name in {"BLOB", "BYTEA"}:
            return bytes.fromhex(str(value))
        if name == "DATE":
            return datetime.date.fromisoformat(str(value))
        if name.startswith("TIME WITH TIME ZONE") or name == "TIME_TZ":
            return datetime.time.fromisoformat(str(value))
        if name == "TIME" or name.startswith("TIME("):
            return datetime.time.fromisoformat(str(value))
        if name.startswith("TIMESTAMP WITH TIME ZONE") or name in {
            "TIMESTAMPTZ",
            "TIMESTAMP_TZ",
        }:
            return datetime.datetime.fromisoformat(str(value).replace(" ", "T"))
        if name.startswith("TIMESTAMP") or name in {
            "DATETIME",
            "TIMESTAMP_S",
            "TIMESTAMP_MS",
            "TIMESTAMP_NS",
        }:
            return datetime.datetime.fromisoformat(
                str(value).replace(" ", "T")
            ).replace(tzinfo=None)
        if isinstance(value, (dict, list)):
            return value
        if name.startswith(("LIST(", "STRUCT(", "MAP(")) or name.endswith("[]"):
            return value
        return value
    except (ValueError, TypeError, decimal.InvalidOperation, OverflowError) as exc:
        raise DataError(f"Cannot convert value to {name}: {value}") from exc


def _exact_integer(value, minimum, maximum):
    number = decimal.Decimal(str(value))
    integer = number.to_integral_value()
    if number != integer or integer < minimum or integer > maximum:
        raise ValueError("integer value is out of range")
    return int(integer)


def _exact_big_integer(value):
    number = decimal.Decimal(str(value))
    integer = number.to_integral_value()
    if number != integer:
        raise ValueError("integer value has a fractional component")
    return int(integer)
