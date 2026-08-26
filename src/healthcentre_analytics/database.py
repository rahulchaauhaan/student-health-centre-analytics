from __future__ import annotations

import sqlite3

import pandas as pd

from . import config


TABLE_FILES = {
    "students": config.DATA_PROCESSED / "students.csv",
    "staff": config.DATA_PROCESSED / "staff.csv",
    "services": config.DATA_PROCESSED / "services.csv",
    "visits": config.DATA_PROCESSED / "visits_clean.csv",
    "access": config.DATA_PROCESSED / "access.csv",
    "capacity_utilization": config.DATA_PROCESSED / "capacity_utilization.csv",
}


def create_database() -> None:
    schema = (config.DATABASE_DIR / "schema.sql").read_text()
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.executescript(schema)
        for table, path in TABLE_FILES.items():
            df = pd.read_csv(path, keep_default_na=False)
            df.to_sql(table, conn, if_exists="append", index=False)


def run_sql_file(path: str | None = None) -> dict[str, pd.DataFrame]:
    sql_path = config.SQL_DIR / "analysis_queries.sql" if path is None else config.PROJECT_ROOT / path
    content = sql_path.read_text()
    queries = {}
    current_name = None
    current_lines: list[str] = []
    for line in content.splitlines():
        if line.startswith("-- name:"):
            if current_name and current_lines:
                queries[current_name] = "\n".join(current_lines).strip().rstrip(";")
            current_name = line.split(":", 1)[1].strip()
            current_lines = []
        elif current_name:
            current_lines.append(line)
    if current_name and current_lines:
        queries[current_name] = "\n".join(current_lines).strip().rstrip(";")

    results = {}
    with sqlite3.connect(config.DB_PATH) as conn:
        for name, query in queries.items():
            if query:
                results[name] = pd.read_sql_query(query, conn)
    return results


if __name__ == "__main__":
    create_database()
    results = run_sql_file()
    print(f"SQLite database created at {config.DB_PATH}")
    print(f"Executed {len(results)} named SQL analyses")
