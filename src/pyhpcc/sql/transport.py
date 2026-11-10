"""HTTP transport for the HPCC WsSQL2 and WsDfu services."""

import json
import logging
import re
import threading
from decimal import Decimal

import requests

from pyhpcc.sql._utils import _as_list
from pyhpcc.sql.errors import (
    DatabaseError,
    DataError,
    IntegrityError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    TimeoutError,
)

log = logging.getLogger(__name__)

QUERY_CANCELLED = 20001
QUERY_LIFETIME_EXCEEDED = 20002
_ERROR_PREFIX = re.compile(r"^([A-Z][A-Za-z ]*?) Error: ")


class WsSql2Transport:
    def __init__(self, auth, config):
        self.auth = auth
        self.config = config
        self._active = set()
        self._lock = threading.Lock()

    def register_cursor(self, cursor_id):
        with self._lock:
            self._active.add(cursor_id)

    def release_cursor(self, cursor_id):
        with self._lock:
            self._active.discard(cursor_id)

    def split(self, sql, timeout=None, cancel_event=None):
        response = self._request(
            self.config.endpoint + "/SplitQuery.json",
            {"SQLText": sql},
            timeout,
            cancel_event,
        )
        body = response.get("SplitQueryResponse")
        if not isinstance(body, dict):
            raise OperationalError("WsSQL2 response has no SplitQueryResponse")
        wrapper = body.get("Statements") or {}
        statements = wrapper.get("Statement") if isinstance(wrapper, dict) else None
        if statements is None:
            return []
        if isinstance(statements, str):
            return [statements]
        if isinstance(statements, list) and all(
            isinstance(item, str) for item in statements
        ):
            return statements
        raise OperationalError("WsSQL2 returned invalid SplitQueryResponse statements")

    def execute(self, sql, timeout=None, cancel_event=None):
        if log.isEnabledFor(logging.DEBUG):
            log.debug("WsSQL2 ExecuteQuery sql_hash=%s", hash(sql))
        response = self._request(
            self.config.endpoint + "/ExecuteQuery.json",
            {"SQLText": sql, "IncludeResultSetMetadata": "true"},
            timeout,
            cancel_event,
        )
        body = response.get("ExecuteQueryResponse")
        if not isinstance(body, dict) or not body.get("CursorId"):
            raise OperationalError("WsSQL2 ExecuteQueryResponse has no CursorId")
        return body

    def fetch(self, cursor_id, fetch_size, timeout=None, cancel_event=None):
        response = self._request(
            self.config.endpoint + "/FetchResultSet.json",
            {"CursorId": cursor_id, "FetchSize": str(fetch_size)},
            timeout,
            cancel_event,
        )
        body = response.get("FetchResultSetResponse")
        if not isinstance(body, dict):
            raise OperationalError("WsSQL2 response has no FetchResultSetResponse")
        return body, _rows(body)

    def close_cursor(self, cursor_id):
        if cursor_id is None:
            return
        response = self._request(
            self.config.endpoint + "/CloseResultSet.json",
            {"CursorId": cursor_id},
            None,
        )
        body = response.get("CloseResultSetResponse")
        if not isinstance(body, dict):
            raise OperationalError("WsSQL2 response has no CloseResultSetResponse")

    def dfu_query(self, fields):
        return self._request(self.config.dfu_endpoint, fields)

    def query_all(self, sql, timeout=None):
        body = self.execute(sql, timeout)
        cursor_id = body["CursorId"]
        rows = []
        try:
            while True:
                page, values = self.fetch(cursor_id, 0, timeout)
                rows.extend(values)
                if page.get("Complete", False):
                    return rows
        except DatabaseError as exc:
            try:
                self.close_cursor(cursor_id)
            except DatabaseError as close_error:
                exc.add_note(f"Cursor cleanup failed: {close_error}")
            raise

    def cancel_all(self):
        with self._lock:
            cursors = tuple(self._active)
        for cursor_id in cursors:
            self.close_cursor(cursor_id)

    def _request(self, endpoint, fields, timeout=None, cancel_event=None):
        read_timeout = self.config.read_timeout if timeout is None else timeout
        request_timeout = (self.config.connect_timeout, read_timeout)
        if read_timeout == 0:
            request_timeout = (self.config.connect_timeout, None)
        try:
            response = self.auth.session.post(
                endpoint,
                data=fields,
                params={key: None for key in getattr(self.auth.session, "params", {})},
                auth=self.auth.oauth if self.auth.require_auth else None,
                timeout=request_timeout,
                headers={"Accept": "application/json"},
                allow_redirects=False,
            )
        except requests.exceptions.Timeout as exc:
            if cancel_event is not None and cancel_event.is_set():
                raise OperationalError("Query was cancelled") from exc
            raise TimeoutError(f"Timed out calling {endpoint}") from exc
        except requests.exceptions.RequestException as exc:
            if cancel_event is not None and cancel_event.is_set():
                raise OperationalError("Query was cancelled") from exc
            raise OperationalError(
                f"HTTP request failed for {endpoint}: {exc}"
            ) from exc

        if response.status_code in {401, 403}:
            raise OperationalError(
                f"Authentication failed calling {endpoint}: {response.text}"
            )
        if not 200 <= response.status_code < 300:
            raise OperationalError(
                f"HTTP {response.status_code} from {endpoint}: {response.text}"
            )
        try:
            result = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as exc:
            raise OperationalError(f"Malformed JSON response from {endpoint}") from exc
        if not isinstance(result, dict):
            raise OperationalError(
                f"Malformed JSON response from {endpoint}: expected an object"
            )
        _raise_esp_fault(result)
        return result


def _rows(body):
    value = body.get("RowsJSON", body.get("Rows"))
    if not isinstance(value, str):
        raise OperationalError("WsSQL2 response is missing its RowsJSON payload")
    try:
        rows = json.loads(value, parse_float=Decimal)
    except (TypeError, ValueError) as exc:
        raise OperationalError("Malformed Rows payload") from exc
    if not isinstance(rows, list) or any(not isinstance(row, list) for row in rows):
        raise OperationalError("Malformed Rows payload: expected an array of rows")
    return rows


def _raise_esp_fault(response):
    exceptions = response.get("Exceptions")
    if not isinstance(exceptions, dict):
        return
    faults = _as_list(exceptions.get("Exception"))
    if not faults:
        raise OperationalError("WsSQL2 request failed")
    messages = []
    for fault in faults:
        if not isinstance(fault, dict):
            continue
        code = fault.get("Code", -1)
        message = str(fault.get("Message", "WsSQL2 request failed"))
        mapped = map_fault(code, message)
        messages.append(mapped)
    if not messages:
        raise OperationalError("WsSQL2 request failed")
    first = messages[0]
    if len(messages) > 1:
        first.add_note(
            "Additional WsSQL2 errors: " + "; ".join(str(item) for item in messages[1:])
        )
    raise first


def map_fault(code, message):
    try:
        code = int(code)
    except (TypeError, ValueError):
        code = -1
    if code == QUERY_CANCELLED:
        return OperationalError(message)
    if code == QUERY_LIFETIME_EXCEEDED:
        return TimeoutError(message)
    return map_server_error(message)


def map_server_error(message):
    message_text = message
    error_type = None
    try:
        parsed = json.loads(message)
    except (TypeError, ValueError):
        parsed = None
    if isinstance(parsed, dict):
        error_type = parsed.get("exception_type")
        subtype = parsed.get("error_subtype")
        if subtype:
            error_type = f"{error_type or ''} {subtype}".strip()
        if error_type:
            message_text = parsed.get("exception_message", message)
    else:
        match = _ERROR_PREFIX.match(message)
        if match:
            error_type = match.group(1)

    if not error_type:
        return OperationalError(message)
    normalized = error_type.lower()
    if any(token in normalized for token in ("parser", "syntax", "binder", "catalog")):
        return ProgrammingError(message_text)
    if any(
        token in normalized for token in ("conversion", "out of range", "invalid input")
    ):
        return DataError(message_text)
    if "constraint" in normalized:
        return IntegrityError(message_text)
    if "not implemented" in normalized:
        return NotSupportedError(message_text)
    if "interrupt" in normalized:
        return TimeoutError(message_text)
    return OperationalError(message_text)
