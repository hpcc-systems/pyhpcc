import datetime
import decimal
import json
import os
import threading
from urllib.parse import urlsplit

import pytest
import requests

from pyhpcc.models.auth import Auth
from pyhpcc.sql import (
    NUMBER,
    DataError as SQLDataError,
    DatabaseError,
    NotSupportedError,
    OperationalError as SQLOperationalError,
    ProgrammingError,
    connect,
)
from pyhpcc.sql.config import SQLConfig
from pyhpcc.sql.errors import (
    DataError,
    InterfaceError,
    OperationalError,
    TimeoutError,
)
from pyhpcc.sql.transport import map_fault, map_server_error
from pyhpcc.sql.transport import _rows
from pyhpcc.sql.types import decode_value, describe_type


DEFAULT_SQL_URL = "http://localhost:8510/WsSQL2"
DEFAULT_DFU_URL = "http://localhost:8010/WsDfu/DFUQuery.json"
LONG_RUNNING_SQL = "SELECT count(*) AS total FROM range(10000000000000) t(i)"


class Response:
    def __init__(self, value, status=200):
        self._value = value
        self.status_code = status
        self.ok = status < 400
        self.text = json.dumps(value)

    def json(self):
        return self._value


def auth(protocol="http"):
    return Auth("localhost", "8010", "alice", "secret", protocol=protocol)


def column(name, type_name, precision=0, scale=0):
    return {
        "ColumnLabel": name,
        "ColumnTypeName": type_name,
        "Precision": precision,
        "Scale": scale,
    }


@pytest.fixture(scope="module")
def local_sql_connection():
    sql_url = os.environ.get("PYHPCC_SQL_URL", DEFAULT_SQL_URL)
    dfu_url = os.environ.get("PYHPCC_DFU_URL", DEFAULT_DFU_URL)
    parsed = urlsplit(sql_url)
    if not parsed.hostname or parsed.scheme not in {"http", "https"}:
        pytest.fail("PYHPCC_SQL_URL must be an absolute HTTP(S) WsSQL2 URL")
    username = os.environ.get("HPCC_USERNAME", "")
    password = os.environ.get("HPCC_PASSWORD", "")
    auth = Auth(
        parsed.hostname,
        str(parsed.port or (443 if parsed.scheme == "https" else 80)),
        username,
        password,
        require_auth=bool(username),
        protocol=parsed.scheme,
    )
    try:
        connection = connect(
            auth,
            sql_url=sql_url,
            dfu_url=dfu_url,
            connect_timeout=3,
            read_timeout=30,
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS value")
            assert cursor.fetchone() == (1,)
    except Exception as exc:
        pytest.fail(
            f"Cannot execute a query against local WsSQL2 at {sql_url}: {exc}. "
            "Set PYHPCC_SQL_URL/PYHPCC_DFU_URL and HPCC_USERNAME/HPCC_PASSWORD "
            "to match the local services."
        )
    try:
        yield connection
    finally:
        connection.close()


def test_config_defaults_to_jdbc_ports_and_overrides_urls():
    config = SQLConfig.from_auth(auth())
    assert config.endpoint == "http://localhost:8510/WsSQL2"
    assert config.dfu_endpoint == "http://localhost:8010/WsDfu/DFUQuery.json"
    secure = SQLConfig.from_auth(auth("https"))
    assert secure.endpoint == "https://localhost:18510/WsSQL2"
    assert secure.dfu_endpoint == "https://localhost:18010/WsDfu/DFUQuery.json"
    override = SQLConfig.from_auth(
        auth(),
        sql_url="https://sql.example:9443",
        dfu_url="https://dfu.example:9444",
        connect_timeout=3,
        read_timeout=4,
    )
    assert override.endpoint == "https://sql.example:9443/WsSQL2"
    assert override.dfu_endpoint == "https://dfu.example:9444/WsDfu/DFUQuery.json"
    assert override.connect_timeout == 3
    assert override.read_timeout == 4


def test_config_rejects_bad_auth_urls_and_timeouts():
    with pytest.raises(InterfaceError):
        SQLConfig.from_auth(object())
    with pytest.raises(InterfaceError):
        SQLConfig.from_auth(auth(), sql_url="file:///tmp/sql")
    with pytest.raises(InterfaceError):
        SQLConfig.from_auth(auth(), read_timeout=-1)


def test_dbapi_query_fetches_rows_and_sends_existing_auth(monkeypatch):
    instance = auth()
    instance.session.params = {"leftover": "from previous PyHPCC call"}
    calls = []

    def post(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/SplitQuery.json"):
            return Response(
                {"SplitQueryResponse": {"Statements": {"Statement": "SELECT 1"}}}
            )
        if url.endswith("/ExecuteQuery.json"):
            return Response(
                {
                    "ExecuteQueryResponse": {
                        "CursorId": "c1",
                        "ResultSetMetadata": {
                            "Column": [column("id", "INTEGER", 10)],
                        },
                    }
                }
            )
        if url.endswith("/FetchResultSet.json"):
            return Response(
                {
                    "FetchResultSetResponse": {
                        "RowsJSON": "[[1],[2]]",
                        "Complete": True,
                    }
                }
            )
        raise AssertionError(f"Unexpected endpoint {url}")

    monkeypatch.setattr(instance.session, "post", post)
    with connect(instance) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.description[0][:2] == ("id", "INTEGER")
        assert cursor.fetchmany() == [(1,)]
        assert cursor.fetchall() == [(2,)]
        assert cursor.fetchone() is None

    assert calls[0][0] == "http://localhost:8510/WsSQL2/SplitQuery.json"
    assert calls[0][1]["auth"] == ("alice", "secret")
    assert calls[0][1]["timeout"] == (30, None)
    assert calls[0][1]["params"] == {"leftover": None}
    assert calls[1][1]["data"]["IncludeResultSetMetadata"] == "true"


def test_scripts_advance_to_the_next_result_set(monkeypatch):
    instance = auth()
    requests_seen = []

    def post(url, **kwargs):
        data = kwargs["data"]
        requests_seen.append((url, data))
        if url.endswith("/SplitQuery.json"):
            return Response(
                {
                    "SplitQueryResponse": {
                        "Statements": {"Statement": ["SELECT 1", "SELECT 2"]}
                    }
                }
            )
        if url.endswith("/ExecuteQuery.json"):
            number = len(
                [url for url, _ in requests_seen if url.endswith("/ExecuteQuery.json")]
            )
            return Response(
                {
                    "ExecuteQueryResponse": {
                        "CursorId": f"c{number}",
                        "ResultSetMetadata": {"Column": column("value", "INTEGER")},
                    }
                }
            )
        if url.endswith("/FetchResultSet.json"):
            value = 1 if data["CursorId"] == "c1" else 2
            return Response(
                {
                    "FetchResultSetResponse": {
                        "RowsJSON": f"[[{value}]]",
                        "Complete": True,
                    }
                }
            )
        raise AssertionError(url)

    monkeypatch.setattr(instance.session, "post", post)
    connection = connect(instance)
    cursor = connection.cursor()
    cursor.execute("SELECT 1; SELECT 2")
    assert cursor.fetchall() == [(1,)]
    assert cursor.nextset() is True
    assert cursor.fetchall() == [(2,)]
    assert cursor.nextset() is None
    cursor.close()
    connection.close()


def test_max_rows_and_cancel_close_server_cursor(monkeypatch):
    instance = auth()
    closed = []

    def post(url, **kwargs):
        if url.endswith("/SplitQuery.json"):
            return Response(
                {"SplitQueryResponse": {"Statements": {"Statement": "SELECT 1"}}}
            )
        if url.endswith("/ExecuteQuery.json"):
            return Response(
                {
                    "ExecuteQueryResponse": {
                        "CursorId": "c1",
                        "ResultSetMetadata": {"Column": column("value", "INTEGER")},
                    }
                }
            )
        if url.endswith("/FetchResultSet.json"):
            return Response(
                {
                    "FetchResultSetResponse": {
                        "RowsJSON": "[[1],[2]]",
                        "Complete": False,
                    }
                }
            )
        if url.endswith("/CloseResultSet.json"):
            closed.append(kwargs["data"]["CursorId"])
            return Response({"CloseResultSetResponse": {"Closed": True}})
        raise AssertionError(url)

    monkeypatch.setattr(instance.session, "post", post)
    connection = connect(instance)
    cursor = connection.cursor()
    cursor.set_max_rows(1)
    cursor.execute("SELECT 1")
    assert cursor.fetchone() == (1,)
    assert cursor.fetchone() is None
    assert closed == ["c1"]

    cursor.execute("SELECT 1")
    cursor.cancel()
    assert closed == ["c1", "c1"]
    with pytest.raises(OperationalError, match="cancelled"):
        cursor.fetchone()
    cursor.close()
    connection.close()


def test_dbapi_rejects_parameters_and_non_result_queries(monkeypatch):
    instance = auth()
    monkeypatch.setattr(
        instance.session,
        "post",
        lambda url, **kwargs: (
            Response({"SplitQueryResponse": {"Statements": {"Statement": "SELECT 1"}}})
            if url.endswith("/SplitQuery.json")
            else Response(
                {"ExecuteQueryResponse": {"CursorId": "c1", "ResultSetMetadata": {}}}
            )
            if url.endswith("/ExecuteQuery.json")
            else Response(
                {"FetchResultSetResponse": {"RowsJSON": "[]", "Complete": True}}
            )
            if url.endswith("/FetchResultSet.json")
            else Response({"CloseResultSetResponse": {"Closed": True}})
        ),
    )
    connection = connect(instance)
    cursor = connection.cursor()
    with pytest.raises(NotSupportedError):
        cursor.execute("SELECT ?", (1,))
    with pytest.raises(ProgrammingError, match="result set"):
        cursor.execute("UPDATE t SET x = 1")
    cursor.close()
    connection.close()


def test_query_failure_closes_server_cursor(monkeypatch):
    instance = auth()
    closed = []

    def post(url, **kwargs):
        if url.endswith("/SplitQuery.json"):
            return Response(
                {"SplitQueryResponse": {"Statements": {"Statement": "SELECT bad"}}}
            )
        if url.endswith("/ExecuteQuery.json"):
            return Response(
                {
                    "ExecuteQueryResponse": {
                        "CursorId": "c1",
                        "ResultSetMetadata": {"Column": column("value", "INTEGER")},
                    }
                }
            )
        if url.endswith("/FetchResultSet.json"):
            return Response(
                {
                    "Exceptions": {
                        "Exception": {
                            "Code": -1,
                            "Message": "Parser Error: invalid SQL",
                        }
                    }
                }
            )
        if url.endswith("/CloseResultSet.json"):
            closed.append(kwargs["data"]["CursorId"])
            return Response({"CloseResultSetResponse": {"Closed": True}})
        raise AssertionError(url)

    monkeypatch.setattr(instance.session, "post", post)
    connection = connect(instance)
    cursor = connection.cursor()
    with pytest.raises(ProgrammingError, match="invalid SQL"):
        cursor.execute("SELECT bad")
    assert closed == ["c1"]
    cursor.close()
    connection.close()


def test_error_mapping_and_value_conversion():
    assert isinstance(map_server_error("Parser Error: invalid SQL"), ProgrammingError)
    assert isinstance(map_server_error("Conversion Error: invalid value"), DataError)
    assert isinstance(map_fault(20002, "query too long"), TimeoutError)
    assert describe_type("DECIMAL(18,2)") == ("DECIMAL", 18, 2)
    assert "INTEGER" == NUMBER
    assert decode_value("18446744073709551615", "UBIGINT") == 18446744073709551615
    assert decode_value("1.10", "DECIMAL(8,2)") == decimal.Decimal("1.10")
    assert decode_value("inf", "DOUBLE") == float("inf")
    assert decode_value("2025-01-02", "DATE") == datetime.date(2025, 1, 2)
    assert decode_value("2025-01-02T03:04:05", "TIMESTAMP") == datetime.datetime(
        2025, 1, 2, 3, 4, 5
    )
    with pytest.raises(DataError):
        decode_value("999", "TINYINT")


def test_read_timeout_maps_to_dbapi_timeout(monkeypatch):
    instance = auth()

    def post(url, **kwargs):
        raise requests.exceptions.ReadTimeout("too slow")

    monkeypatch.setattr(instance.session, "post", post)
    connection = connect(instance, read_timeout=0.01)
    with pytest.raises(TimeoutError):
        connection.cursor().execute("SELECT 1")


def test_metadata_lists_files_and_columns(monkeypatch):
    instance = auth()
    requests_seen = []

    def post(url, **kwargs):
        requests_seen.append(url)
        if url.endswith("DFUQuery.json"):
            return Response(
                {
                    "DFUQueryResponse": {
                        "NumFiles": 1,
                        "DFULogicalFiles": {
                            "DFULogicalFile": {
                                "Name": "scope::people",
                                "Description": "people file",
                                "isDirectory": False,
                            }
                        },
                    }
                }
            )
        if url.endswith("/ExecuteQuery.json"):
            return Response({"ExecuteQueryResponse": {"CursorId": "describe"}})
        if url.endswith("/FetchResultSet.json"):
            return Response(
                {
                    "FetchResultSetResponse": {
                        "RowsJSON": '[["id","BIGINT","NO"],["name","VARCHAR","YES"]]',
                        "Complete": True,
                    }
                }
            )
        raise AssertionError(url)

    monkeypatch.setattr(instance.session, "post", post)
    connection = connect(instance)
    tables = connection.get_tables("scope::%")
    assert tables.fetchone()[2:5] == ("scope::people", "TABLE", "people file")
    tables.close()
    columns = connection.get_columns("scope::people", "id")
    row = columns.fetchone()
    assert row[2:4] == ("scope::people", "id")
    assert row[5] == "BIGINT"
    assert row[16] == 1
    assert len(requests_seen) == 4
    columns.close()
    connection.close()


@pytest.mark.integration
def test_local_server_executes_and_pages_queries(local_sql_connection):
    with local_sql_connection.cursor() as cursor:
        cursor.set_fetch_size(2)
        cursor.execute("SELECT * FROM range(3) AS t(i)")
        assert cursor.fetchone() == (0,)
        assert cursor.fetchone() == (1,)
        assert cursor.fetchone() == (2,)
        assert cursor.fetchone() is None


@pytest.mark.integration
def test_local_server_handles_an_exactly_full_final_page(local_sql_connection):
    with local_sql_connection.cursor() as cursor:
        cursor.set_fetch_size(2)
        cursor.execute("SELECT * FROM range(2) AS t(i)")
        assert cursor.fetchall() == [(0,), (1,)]
        assert cursor.fetchone() is None


@pytest.mark.integration
def test_local_server_runs_multi_statement_scripts(local_sql_connection):
    script = "".join(f"SELECT {value} AS value;\n-- advance\n" for value in range(12))
    with local_sql_connection.cursor() as cursor:
        cursor.execute(script)
        values = []
        while True:
            if cursor.description is not None:
                values.append(cursor.fetchone()[0])
                assert cursor.fetchone() is None
            if cursor.nextset() is None:
                break
        assert values == list(range(12))


@pytest.mark.integration
def test_local_server_stops_script_errors(local_sql_connection):
    with local_sql_connection.cursor() as cursor:
        with pytest.raises(ProgrammingError):
            cursor.execute("SELECT 1; SELEC 2; SELECT 3")

        cursor.execute(
            "SELECT 1 AS value; " "SELECT missing_column FROM range(1); " "SELECT 3"
        )
        assert cursor.fetchone() == (1,)
        with pytest.raises(ProgrammingError):
            cursor.nextset()
        assert cursor.nextset() is None


@pytest.mark.integration
def test_local_server_cancels_running_queries(local_sql_connection):
    with local_sql_connection.cursor() as cursor:
        timer = threading.Timer(0.5, cursor.cancel)
        timer.start()
        try:
            with pytest.raises(SQLOperationalError, match="cancel"):
                cursor.execute(LONG_RUNNING_SQL)
        finally:
            timer.join(timeout=30)
        assert not timer.is_alive()
        cursor.execute("SELECT 1 AS value")
        assert cursor.fetchone() == (1,)


@pytest.mark.integration
def test_local_server_cancels_remaining_script_statements(local_sql_connection):
    with local_sql_connection.cursor() as cursor:
        timer = threading.Timer(0.5, cursor.cancel)
        timer.start()
        try:
            with pytest.raises(SQLOperationalError, match="cancel"):
                cursor.execute(LONG_RUNNING_SQL + "; SELECT 2")
        finally:
            timer.join(timeout=30)
        assert not timer.is_alive()
        assert cursor.nextset() is None


@pytest.mark.integration
def test_local_server_enforces_query_timeout_and_releases_cursor(
    local_sql_connection,
):
    with local_sql_connection.cursor() as cursor:
        cursor.set_query_timeout(1)
        with pytest.raises(TimeoutError):
            cursor.execute(LONG_RUNNING_SQL)
        cursor.set_query_timeout(0)
        cursor.execute("SELECT 1 AS value")
        assert cursor.fetchone() == (1,)


@pytest.mark.integration
def test_local_server_reports_live_errors_and_decodes_types(local_sql_connection):
    with local_sql_connection.cursor() as cursor:
        with pytest.raises(ProgrammingError):
            cursor.execute("SELEC invalid")
        with pytest.raises(ProgrammingError):
            cursor.execute("SELECT missing_column FROM range(1)")
        with pytest.raises(SQLDataError):
            cursor.execute("SELECT 'x'::INTEGER")
        with pytest.raises(DatabaseError):
            cursor.execute("CREATE TABLE pyhpcc_test_must_not_create(i INTEGER)")

        cursor.execute(
            "SELECT 12345678901234567890::HUGEINT AS huge, "
            "1.10::DECIMAL(18,2) AS amount, "
            "'x'::BLOB AS bytes, DATE '2024-01-02' AS day, "
            "TIMESTAMP '2024-01-02 03:04:05.123456' AS moment, "
            "NULL::VARCHAR AS absent, uuid() AS token, "
            "[1,2] AS items, {'a':1} AS record"
        )
        huge, amount, blob, day, moment, absent, token, items, record = (
            cursor.fetchone()
        )
        assert huge == 12345678901234567890
        assert amount == decimal.Decimal("1.10")
        assert blob == b"x"
        assert day == datetime.date(2024, 1, 2)
        assert moment == datetime.datetime(2024, 1, 2, 3, 4, 5, 123456)
        assert absent is None
        assert str(token)
        assert items == [1, 2]
        assert record == {"a": 1}


@pytest.mark.integration
def test_local_server_caps_rows_and_lists_logical_file_metadata(
    local_sql_connection,
):
    with local_sql_connection.cursor() as cursor:
        cursor.set_fetch_size(2)
        cursor.set_max_rows(1)
        cursor.execute("SELECT * FROM range(5) AS t(i)")
        assert cursor.fetchall() == [(0,)]

    tables = local_sql_connection.get_tables("regress::multi::book", ["TABLE"])
    try:
        table_rows = tables.fetchall()
        assert any(row[2] == "regress::multi::book" for row in table_rows)
    finally:
        tables.close()

    columns = local_sql_connection.get_columns("regress::multi::book", "id")
    try:
        column_rows = columns.fetchall()
        assert any(
            row[2] == "regress::multi::book" and row[3] == "id" and row[5] == "BIGINT"
            for row in column_rows
        )
    finally:
        columns.close()


@pytest.mark.integration
def test_local_server_releases_early_closed_cursors(local_sql_connection):
    for _ in range(12):
        with local_sql_connection.cursor() as cursor:
            cursor.set_fetch_size(1)
            cursor.execute("SELECT * FROM range(10) AS t(i)")
            assert cursor.fetchone() == (0,)


@pytest.mark.integration
def test_local_server_rejects_bad_credentials_when_auth_is_enabled(
    local_sql_connection,
):
    current_auth = local_sql_connection.auth
    if not current_auth.username:
        pytest.skip("Set HPCC_USERNAME to test authentication failures")

    bad_auth = Auth(
        current_auth.ip,
        current_auth.port,
        current_auth.username,
        "invalid-password-for-pyhpcc-test",
        require_auth=True,
        protocol=current_auth.protocol,
    )
    connection = connect(
        bad_auth,
        sql_url=os.environ.get("PYHPCC_SQL_URL", DEFAULT_SQL_URL),
        connect_timeout=3,
        read_timeout=30,
    )
    try:
        with connection.cursor() as cursor:
            with pytest.raises(SQLOperationalError, match="Authentication failed"):
                cursor.execute("SELECT 1")
    finally:
        connection.close()


@pytest.mark.integration
def test_local_server_reads_first_two_pages_of_every_regress_file(
    local_sql_connection,
):
    expected_failures = {
        "regress::multi::dg_var",
        "regress::single::dg_var",
    }
    tables = local_sql_connection.get_tables("regress::%", ["TABLE"])
    try:
        logical_names = [row[2] for row in tables.fetchall() if row[2]]
    finally:
        tables.close()
    assert logical_names, "No regress:: logical files found on local WsDfu"

    failures = {}
    for logical_name in logical_names:
        try:
            escaped_name = logical_name.replace("'", "''")
            with local_sql_connection.cursor() as cursor:
                cursor.set_fetch_size(50)
                cursor.set_max_rows(100)
                cursor.execute(f"SELECT * FROM hpcc_scan('{escaped_name}')")
                rows = cursor.fetchall()
                assert len(rows) <= 100
        except (DatabaseError, AssertionError) as exc:
            failures[logical_name] = f"{type(exc).__name__}: {exc}"

    unexpected_failures = {
        name: failure
        for name, failure in failures.items()
        if name not in expected_failures
    }
    unexpected_passes = expected_failures.intersection(logical_names) - failures.keys()
    details = []
    if unexpected_failures:
        details.append(
            f"{len(unexpected_failures)} of {len(logical_names)} files failed: "
            + "; ".join(
                f"{name} -> {failure}"
                for name, failure in sorted(unexpected_failures.items())
            )
        )
    if unexpected_passes:
        details.append(
            "Expected failures now pass; remove them from expected_failures: "
            + ", ".join(sorted(unexpected_passes))
        )
    assert not details, "\n".join(details)


def test_local_server_preserves_decimal_scale_from_json_rows():
    assert _rows({"RowsJSON": "[[1.10]]"}) == [[decimal.Decimal("1.10")]]
