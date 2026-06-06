"""Integration tests for the SQLite specification builder against a real database.

Rows are stored as JSON documents in a ``data`` column — the pattern the builder
targets via ``json_extract`` — so these verify the generated SQL is valid and
returns the rows ``is_satisfied_by`` would select.
"""

import json
import sqlite3

import pytest

from fractal_specifications.contrib.sqlite.specifications import (
    SqliteSpecificationBuilder,
)
from fractal_specifications.generic.operators import (
    EqualsSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanSpecification,
    NotEqualsSpecification,
)

ROWS = [
    {"id": 1, "name": "Alice", "age": 30, "status": "active"},
    {"id": 2, "name": "Bob", "age": 25, "status": "active"},
    {"id": 3, "name": "Charlie", "age": 35, "status": "inactive"},
    {"id": 4, "name": None, "age": 22, "status": "active"},
]


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE users (id TEXT PRIMARY KEY, data TEXT)")
    connection.executemany(
        "INSERT INTO users VALUES (?, ?)",
        [(str(row["id"]), json.dumps(row)) for row in ROWS],
    )
    yield connection
    connection.close()


def query_ids(conn, specification):
    where, params = SqliteSpecificationBuilder.build(specification)
    rows = conn.execute(
        f"SELECT json_extract(data, '$.id') FROM users WHERE {where}", params
    ).fetchall()
    return sorted(r[0] for r in rows)


def test_equals(conn):
    assert query_ids(conn, EqualsSpecification("status", "active")) == [1, 2, 4]


def test_greater_than(conn):
    assert query_ids(conn, GreaterThanSpecification("age", 28)) == [1, 3]


def test_less_than(conn):
    assert query_ids(conn, LessThanSpecification("age", 28)) == [2, 4]


def test_in(conn):
    assert query_ids(conn, InSpecification("age", [22, 35])) == [3, 4]


def test_is_none(conn):
    assert query_ids(conn, IsNoneSpecification("name")) == [4]


def test_not_equals_includes_null_rows(conn):
    # Bob is excluded; the null-name row (4) is kept, matching Python semantics.
    assert query_ids(conn, NotEqualsSpecification("name", "Bob")) == [1, 3, 4]


def test_range_on_null_field_excludes_without_raising(conn):
    # No 'salary' field exists -> json_extract is NULL -> excluded, no error.
    assert query_ids(conn, GreaterThanSpecification("salary", 0)) == []


def test_and(conn):
    spec = EqualsSpecification("status", "active") & GreaterThanSpecification("age", 24)
    assert query_ids(conn, spec) == [1, 2]


def test_or(conn):
    spec = EqualsSpecification("name", "Alice") | EqualsSpecification("name", "Bob")
    assert query_ids(conn, spec) == [1, 2]


def test_nested(conn):
    spec = (
        EqualsSpecification("status", "active") & GreaterThanSpecification("age", 28)
    ) | EqualsSpecification("status", "inactive")
    assert query_ids(conn, spec) == [1, 3]
