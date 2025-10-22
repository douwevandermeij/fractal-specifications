"""Integration tests for DuckDB specification builder using real in-memory database."""

import pytest

duckdb = pytest.importorskip("duckdb")

from fractal_specifications.contrib.duckdb.specifications import (  # noqa: E402
    DuckDBSpecificationBuilder,
)
from fractal_specifications.generic.operators import (  # noqa: E402
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotEqualsSpecification,
)


@pytest.fixture
def db_connection():
    """Create an in-memory DuckDB connection."""
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def users_table(db_connection):
    """Create and populate a users table."""
    db_connection.execute("""
        CREATE TABLE users (
            id INTEGER,
            name VARCHAR,
            age INTEGER,
            email VARCHAR,
            status VARCHAR,
            salary DECIMAL
        )
    """)

    db_connection.execute("""
        INSERT INTO users VALUES
            (1, 'Alice', 30, 'alice@example.com', 'active', 75000),
            (2, 'Bob', 25, 'bob@example.com', 'active', 60000),
            (3, 'Charlie', 35, 'charlie@example.com', 'inactive', 80000),
            (4, 'David', 28, 'david@example.com', 'active', 65000),
            (5, 'Eve', 40, 'eve@example.com', 'inactive', 90000),
            (6, NULL, 22, 'unknown@example.com', 'active', 50000)
    """)

    return db_connection


def execute_query(conn, specification, table="users"):
    """Helper to execute a query with specification."""
    sql, params = DuckDBSpecificationBuilder.build(specification)
    query = f"SELECT * FROM {table} WHERE {sql}"
    return conn.execute(query, params).fetchall()


def test_equals_specification_integration(users_table):
    spec = EqualsSpecification("name", "Alice")
    results = execute_query(users_table, spec)

    assert len(results) == 1
    assert results[0][1] == "Alice"  # name column


def test_not_equals_specification_integration(users_table):
    spec = NotEqualsSpecification("status", "active")
    results = execute_query(users_table, spec)

    assert len(results) == 2
    assert all(row[4] == "inactive" for row in results)  # status column


def test_in_specification_integration(users_table):
    spec = InSpecification("age", [25, 30, 35])
    results = execute_query(users_table, spec)

    assert len(results) == 3
    ages = [row[2] for row in results]
    assert sorted(ages) == [25, 30, 35]


def test_less_than_specification_integration(users_table):
    spec = LessThanSpecification("age", 30)
    results = execute_query(users_table, spec)

    assert len(results) == 3
    assert all(row[2] < 30 for row in results)


def test_less_than_equal_specification_integration(users_table):
    spec = LessThanEqualSpecification("age", 30)
    results = execute_query(users_table, spec)

    assert len(results) == 4
    assert all(row[2] <= 30 for row in results)


def test_greater_than_specification_integration(users_table):
    spec = GreaterThanSpecification("age", 30)
    results = execute_query(users_table, spec)

    assert len(results) == 2
    assert all(row[2] > 30 for row in results)


def test_greater_than_equal_specification_integration(users_table):
    spec = GreaterThanEqualSpecification("age", 30)
    results = execute_query(users_table, spec)

    assert len(results) == 3
    assert all(row[2] >= 30 for row in results)


def test_contains_specification_integration(users_table):
    spec = ContainsSpecification("email", "alice")
    results = execute_query(users_table, spec)

    assert len(results) == 1
    assert "alice" in results[0][3].lower()


def test_is_none_specification_integration(users_table):
    spec = IsNoneSpecification("name")
    results = execute_query(users_table, spec)

    assert len(results) == 1
    assert results[0][1] is None


def test_and_specification_integration(users_table):
    spec = EqualsSpecification("status", "active") & GreaterThanSpecification("age", 25)
    results = execute_query(users_table, spec)

    assert len(results) == 2
    assert all(row[4] == "active" and row[2] > 25 for row in results)


def test_or_specification_integration(users_table):
    spec = EqualsSpecification("name", "Alice") | EqualsSpecification("name", "Bob")
    results = execute_query(users_table, spec)

    assert len(results) == 2
    names = [row[1] for row in results]
    assert sorted(names) == ["Alice", "Bob"]


def test_complex_nested_specification_integration(users_table):
    # (status = 'active' AND age >= 25) OR (status = 'inactive' AND salary > 85000)
    spec = (
        EqualsSpecification("status", "active") & GreaterThanEqualSpecification("age", 25)
    ) | (
        EqualsSpecification("status", "inactive") & GreaterThanSpecification("salary", 85000)
    )
    results = execute_query(users_table, spec)

    assert len(results) == 4
    # Alice (active, 30), Bob (active, 25), David (active, 28), Eve (inactive, 90000)
    names = sorted([row[1] for row in results])
    assert names == ["Alice", "Bob", "David", "Eve"]


def test_multiple_conditions_integration(users_table):
    # active users between ages 25-35 with salary > 60000
    spec = (
        EqualsSpecification("status", "active")
        & GreaterThanEqualSpecification("age", 25)
        & LessThanEqualSpecification("age", 35)
        & GreaterThanSpecification("salary", 60000)
    )
    results = execute_query(users_table, spec)

    assert len(results) == 2
    # Alice (75000) and David (65000)
    names = sorted([row[1] for row in results])
    assert names == ["Alice", "David"]


def test_in_with_strings_integration(users_table):
    spec = InSpecification("name", ["Alice", "Charlie", "Eve"])
    results = execute_query(users_table, spec)

    assert len(results) == 3
    names = sorted([row[1] for row in results])
    assert names == ["Alice", "Charlie", "Eve"]


def test_empty_result_integration(users_table):
    spec = EqualsSpecification("name", "NonExistent")
    results = execute_query(users_table, spec)

    assert len(results) == 0


def test_all_records_integration(users_table):
    spec = GreaterThanSpecification("age", 0)
    results = execute_query(users_table, spec)

    # All records have valid ages > 0
    assert len(results) == 6


def test_decimal_comparison_integration(users_table):
    spec = GreaterThanEqualSpecification("salary", 75000)
    results = execute_query(users_table, spec)

    assert len(results) == 3
    # Alice (75000), Charlie (80000), Eve (90000)
    salaries = sorted([row[5] for row in results])
    assert salaries == [75000, 80000, 90000]


@pytest.fixture
def products_table(db_connection):
    """Create and populate a products table for additional tests."""
    db_connection.execute("""
        CREATE TABLE products (
            id INTEGER,
            name VARCHAR,
            category VARCHAR,
            price DECIMAL,
            in_stock BOOLEAN
        )
    """)

    db_connection.execute("""
        INSERT INTO products VALUES
            (1, 'Laptop', 'Electronics', 999.99, true),
            (2, 'Mouse', 'Electronics', 29.99, true),
            (3, 'Desk', 'Furniture', 299.99, false),
            (4, 'Chair', 'Furniture', 199.99, true),
            (5, 'Monitor', 'Electronics', 399.99, true)
    """)

    return db_connection


def test_category_filter_integration(products_table):
    spec = EqualsSpecification("category", "Electronics")
    results = execute_query(products_table, spec, table="products")

    assert len(results) == 3
    assert all(row[2] == "Electronics" for row in results)


def test_price_range_integration(products_table):
    spec = (
        GreaterThanSpecification("price", 100)
        & LessThanSpecification("price", 500)
    )
    results = execute_query(products_table, spec, table="products")

    assert len(results) == 3
    # Desk (299.99), Chair (199.99), Monitor (399.99)
    prices = sorted([float(row[3]) for row in results])
    assert prices == [199.99, 299.99, 399.99]


def test_complex_product_query_integration(products_table):
    # Electronics under $500 OR Furniture in stock
    spec = (
        EqualsSpecification("category", "Electronics")
        & LessThanSpecification("price", 500)
    ) | (
        EqualsSpecification("category", "Furniture")
        & EqualsSpecification("in_stock", True)
    )
    results = execute_query(products_table, spec, table="products")

    assert len(results) == 3
    # Mouse (29.99), Monitor (399.99), Chair (199.99)
    product_ids = sorted([row[0] for row in results])
    assert product_ids == [2, 4, 5]
