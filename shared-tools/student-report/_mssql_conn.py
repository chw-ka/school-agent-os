"""Read legacy MSSQL connection from T:\\...\\connection.txt (same as PowerShell scripts)."""

from __future__ import annotations

import re
from pathlib import Path

DEFAULT_CONN_FILE = Path(
    r"T:\25-26\ITAdmin_13_StudentReport\_Program\Summaries\connection.txt"
)


def connection_string(conn_file: Path | None = None) -> str:
    path = conn_file or DEFAULT_CONN_FILE
    raw = path.read_text(encoding="utf-8").strip()
    server = re.search(r"Data Source=([^;]+)", raw)
    database = re.search(r"Initial Catalog=([^;]+)", raw)
    user = re.search(r"User ID=([^;]+)", raw)
    password = re.search(r"Password=([^;]+)", raw)
    if not all([server, database, user, password]):
        raise ValueError(f"Cannot parse connection file: {path}")
    return (
        f"DRIVER={{SQL Server}};"
        f"SERVER={server.group(1)};"
        f"DATABASE={database.group(1)};"
        f"UID={user.group(1)};"
        f"PWD={password.group(1)};"
    )
