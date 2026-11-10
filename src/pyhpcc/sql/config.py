"""Connection options for the HPCC SQL driver."""

import math
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from pyhpcc.models.auth import Auth
from pyhpcc.sql.errors import InterfaceError


@dataclass(frozen=True)
class SQLConfig:
    endpoint: str
    dfu_endpoint: str
    connect_timeout: float
    read_timeout: float | None

    @classmethod
    def from_auth(
        cls,
        auth: Auth,
        *,
        sql_url: str | None = None,
        dfu_url: str | None = None,
        connect_timeout: float = 30,
        read_timeout: float | None = None,
    ) -> "SQLConfig":
        if not isinstance(auth, Auth):
            raise InterfaceError("auth must be a pyhpcc.models.auth.Auth instance")
        for name, value in (
            ("connect_timeout", connect_timeout),
            ("read_timeout", read_timeout),
        ):
            if value is not None and (
                not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise InterfaceError(f"{name} must be a non-negative finite number")

        scheme = auth.protocol.lower() if isinstance(auth.protocol, str) else ""
        if scheme not in {"http", "https"}:
            raise InterfaceError("Auth.protocol must be http or https")
        default_sql_port = 18510 if scheme == "https" else 8510
        default_dfu_port = 18010 if scheme == "https" else 8010
        host = _host_from_auth(auth)
        endpoint = _service_url(
            sql_url or f"{scheme}://{host}:{default_sql_port}/WsSQL2",
            "/WsSQL2",
            "sql_url",
        )
        dfu_endpoint = _service_url(
            dfu_url or f"{scheme}://{host}:{default_dfu_port}/WsDfu/DFUQuery.json",
            "/WsDfu/DFUQuery.json",
            "dfu_url",
        )
        return cls(
            endpoint=endpoint,
            dfu_endpoint=dfu_endpoint,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
        )


def _host_from_auth(auth: Auth) -> str:
    if not isinstance(auth.ip, str):
        raise InterfaceError("Auth.ip must contain only an HPCC host")
    raw = auth.ip.strip()
    try:
        parsed = urlsplit(raw if "://" in raw else f"{auth.protocol}://{raw}")
    except ValueError as exc:
        raise InterfaceError("Auth.ip must contain only an HPCC host") from exc
    if (
        not parsed.hostname
        or parsed.path not in ("", "/")
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise InterfaceError("Auth.ip must contain only an HPCC host")
    hostname = parsed.hostname
    if ":" in hostname:
        hostname = f"[{hostname}]"
    return hostname


def _service_url(value: str, default_path: str, name: str) -> str:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise InterfaceError(f"{name} is not a valid HTTP(S) URL") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise InterfaceError(
            f"{name} must be an absolute HTTP(S) URL without credentials or query"
        )
    path = parsed.path.rstrip("/") or default_path
    netloc = parsed.hostname
    if ":" in netloc:
        netloc = f"[{netloc}]"
    if port is not None:
        netloc = f"{netloc}:{port}"
    return urlunsplit((parsed.scheme, netloc, path, "", ""))
