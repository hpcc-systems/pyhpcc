"""DB-API cursor implementation for WsSQL2."""

import threading

from pyhpcc.sql.errors import (
    DatabaseError,
    DataError,
    InterfaceError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
)
from pyhpcc.sql.types import decode_value, describe_type


class Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.arraysize = 1
        self.description = None
        self.rowcount = -1
        self.lastrowid = None
        self.timeout = 0
        self.fetch_size = 0
        self.max_rows = 0
        self._closed = False
        self._cursor_id = None
        self._columns = []
        self._rows = []
        self._row_index = 0
        self._current_row_number = 0
        self._pending_statements = []
        self._cancelled = False
        self._cancel_event = threading.Event()
        self._local_result = False

    def execute(self, operation, parameters=None):
        self._check_open()
        if not isinstance(operation, str):
            raise ProgrammingError("SQL text must be a string")
        if parameters not in (None, (), [], {}):
            raise NotSupportedError("SQL parameters are not supported by WsSQL2")
        self._close_server_cursor()
        self._pending_statements.clear()
        self._cancelled = False
        self._cancel_event.clear()
        self._clear_result()
        try:
            statements = self.connection._transport.split(
                operation, self._timeout_seconds(), self._cancel_event
            )
            if self._cancelled:
                raise OperationalError("Query was cancelled")
            if not statements:
                return self
            self._pending_statements = statements[1:]
            self._run(statements[0])
        except Exception:
            self._pending_statements.clear()
            self._clear_result()
            raise
        return self

    def executemany(self, operation, seq_of_parameters):
        if seq_of_parameters is None:
            raise ProgrammingError("seq_of_parameters cannot be None")
        raise NotSupportedError(
            "executemany is not supported by the read-only WsSQL2 driver"
        )

    def nextset(self):
        self._check_open()
        self._close_server_cursor()
        self._clear_result()
        self._cancelled = False
        self._cancel_event.clear()
        if not self._pending_statements:
            return None
        statement = self._pending_statements.pop(0)
        try:
            self._run(statement)
        except Exception:
            self._pending_statements.clear()
            self._clear_result()
            raise
        return True

    def fetchone(self):
        self._check_open()
        if self._cancelled:
            raise OperationalError("Query was cancelled")
        if self.description is None:
            raise InterfaceError("Cursor has no result set")
        if self.max_rows and self._current_row_number >= self.max_rows:
            return None
        while self._row_index >= len(self._rows):
            if self._cursor_id is None:
                return None
            self._fetch_page()
        raw = self._rows[self._row_index]
        self._row_index += 1
        if len(raw) != len(self._columns):
            error = OperationalError("WsSQL2 row width does not match result metadata")
            self._close_after_error(error)
            raise error
        if self._local_result:
            row = tuple(raw)
        else:
            try:
                row = tuple(
                    decode_value(value, column[1])
                    for value, column in zip(raw, self._columns)
                )
            except DataError as error:
                self._close_after_error(error)
                raise
        self._current_row_number += 1
        if self.max_rows and self._current_row_number >= self.max_rows:
            self._close_server_cursor()
        return row

    def fetchmany(self, size=None):
        self._check_open()
        count = self.arraysize if size is None else size
        if not isinstance(count, int) or count < 0:
            raise InterfaceError("fetchmany size must be a non-negative integer")
        return [row for _, row in zip(range(count), self)]

    def fetchall(self):
        self._check_open()
        return list(self)

    def setinputsizes(self, sizes):
        return None

    def setoutputsize(self, size, column=None):
        return None

    def set_fetch_size(self, size):
        if not isinstance(size, int) or size < 0:
            raise InterfaceError("fetch size must be a non-negative integer")
        self.fetch_size = size

    def set_max_rows(self, size):
        if not isinstance(size, int) or size < 0:
            raise InterfaceError("max rows must be a non-negative integer")
        self.max_rows = size
        if size and self._current_row_number >= size:
            self._close_server_cursor()

    def set_query_timeout(self, seconds):
        if not isinstance(seconds, (int, float)) or seconds < 0:
            raise InterfaceError(
                "query timeout must be a non-negative number of seconds"
            )
        self.timeout = seconds

    def cancel(self):
        self._cancelled = True
        self._cancel_event.set()
        self._pending_statements.clear()
        if self._cursor_id is not None:
            self._close_server_cursor()

    def close(self):
        if self._closed:
            return
        self._pending_statements.clear()
        try:
            self._close_server_cursor()
        finally:
            self._clear_result()
            self._closed = True
            self.connection._remove_cursor(self)

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row

    def __enter__(self):
        self._check_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _run(self, sql):
        body = self.connection._transport.execute(
            sql, self._timeout_seconds(), self._cancel_event
        )
        self._cursor_id = body["CursorId"]
        self.connection._transport.register_cursor(self._cursor_id)
        if self._cancelled:
            self._close_server_cursor()
            raise OperationalError("Query was cancelled")
        self._columns = _parse_columns(body.get("ResultSetMetadata"))
        self.description = [
            (name, type_name, None, None, precision or None, scale or None, None)
            for name, type_name, precision, scale in self._columns
        ]
        if not self._columns:
            self._close_server_cursor()
            raise ProgrammingError("Query did not produce a result set")
        self._fetch_page()

    def _fetch_page(self):
        cursor_id = self._cursor_id
        if cursor_id is None:
            return
        try:
            body, rows = self.connection._transport.fetch(
                cursor_id,
                self.fetch_size,
                self._timeout_seconds(),
                self._cancel_event,
            )
            if any(not isinstance(row, list) for row in rows):
                raise OperationalError("WsSQL2 returned a malformed row")
            self._rows = rows
            self._row_index = 0
            if body.get("Complete", False):
                self._release_cursor(cursor_id)
        except DatabaseError as error:
            try:
                self._close_server_cursor()
            except DatabaseError as close_error:
                error.add_note(f"Cursor cleanup failed: {close_error}")
            if self._cancelled:
                raise OperationalError("Query was cancelled") from error
            raise
        if self._cancelled:
            self._close_server_cursor()
            raise OperationalError("Query was cancelled")

    def _timeout_seconds(self):
        if self.timeout:
            return self.timeout
        return self.connection._config.read_timeout

    def _close_server_cursor(self):
        cursor_id = self._cursor_id
        if cursor_id is None:
            return
        self._cursor_id = None
        self.connection._transport.release_cursor(cursor_id)
        self.connection._transport.close_cursor(cursor_id)

    def _release_cursor(self, cursor_id):
        if self._cursor_id == cursor_id:
            self._cursor_id = None
        self.connection._transport.release_cursor(cursor_id)

    def _close_after_error(self, error):
        try:
            self._close_server_cursor()
        except OperationalError as close_error:
            error.add_note(f"Cursor cleanup failed: {close_error}")

    def _clear_result(self):
        self.description = None
        self.rowcount = -1
        self.lastrowid = None
        self._columns = []
        self._rows = []
        self._row_index = 0
        self._current_row_number = 0
        self._local_result = False

    def _check_open(self):
        if self._closed:
            raise InterfaceError("Cursor is closed")
        self.connection._check_open()

    def _set_local_result(self, columns, rows):
        self._check_open()
        self._close_server_cursor()
        self._pending_statements.clear()
        self._columns = [
            (name, type_name, precision, scale)
            for name, type_name, precision, scale in columns
        ]
        self.description = [
            (name, type_name, None, None, precision or None, scale or None, None)
            for name, type_name, precision, scale in self._columns
        ]
        self._rows = [list(row) for row in rows]
        self._row_index = 0
        self._local_result = True


def _parse_columns(metadata):
    if not isinstance(metadata, dict):
        return []
    raw_columns = metadata.get("Column")
    if raw_columns is None:
        return []
    if not isinstance(raw_columns, list):
        raw_columns = [raw_columns]
    columns = []
    for index, column in enumerate(raw_columns):
        if not isinstance(column, dict):
            continue
        name = (
            column.get("ColumnLabel")
            or column.get("ColumnName")
            or f"column{index + 1}"
        )
        type_name, precision, scale = describe_type(
            column.get("ColumnTypeName"),
            _as_int(column.get("Precision")),
            _as_int(column.get("Scale")),
        )
        columns.append((name, type_name, precision, scale))
    return columns


def _as_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
