from typing import Any, Collection

import pytest

from fractal_specifications.contrib.duckdb.specifications import (
    DuckDBSpecificationBuilder,
    SpecificationNotMappedToDuckDB,
)


def test_build_none():
    sql, params = DuckDBSpecificationBuilder.build(None)
    assert sql == "TRUE"
    assert params == []


def test_build_equals_specification(equals_specification):
    sql, params = DuckDBSpecificationBuilder.build(equals_specification)
    assert sql == "id = ?"
    assert params == [1]


def test_build_or_specification(or_specification):
    sql, params = DuckDBSpecificationBuilder.build(or_specification)
    assert sql == "(id = ?) OR (name = ?)"
    assert params == [1, "test"]


def test_build_and_specification(and_specification):
    sql, params = DuckDBSpecificationBuilder.build(and_specification)
    assert sql == "(id = ?) AND (name = ?)"
    assert params == [1, "test"]


def test_build_contains_specification(contains_specification):
    sql, params = DuckDBSpecificationBuilder.build(contains_specification)
    assert sql == "field ILIKE ?"
    assert params == ["%test%"]


def test_build_in_specification(in_specification):
    sql, params = DuckDBSpecificationBuilder.build(in_specification)
    assert sql == "field IN (?,?,?)"
    assert params == [1, 2, 3]


def test_build_in_empty_specification(in_empty_specification):
    sql, params = DuckDBSpecificationBuilder.build(in_empty_specification)
    assert sql == "field IN ()"
    assert params == []


def test_build_less_than_specification(less_than_specification):
    sql, params = DuckDBSpecificationBuilder.build(less_than_specification)
    assert sql == "id < ?"
    assert params == [1]


def test_build_less_than_equal_specification(less_than_equal_specification):
    sql, params = DuckDBSpecificationBuilder.build(less_than_equal_specification)
    assert sql == "id <= ?"
    assert params == [1]


def test_build_greater_than_specification(greater_than_specification):
    sql, params = DuckDBSpecificationBuilder.build(greater_than_specification)
    assert sql == "id > ?"
    assert params == [1]


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    sql, params = DuckDBSpecificationBuilder.build(greater_than_equal_specification)
    assert sql == "id >= ?"
    assert params == [1]


def test_build_regex_string_match_specification(regex_string_match_specification):
    sql, params = DuckDBSpecificationBuilder.build(regex_string_match_specification)
    # DuckDB uses regexp_matches for regex matching
    assert sql == "regexp_matches(id, ?)"
    assert params == ["abc"]


def test_build_is_none_specification(is_none_specification):
    sql, params = DuckDBSpecificationBuilder.build(is_none_specification)
    assert sql == "field IS NULL"
    assert params == []


def test_build_not_equals_specification():
    from fractal_specifications.generic.operators import NotEqualsSpecification

    spec = NotEqualsSpecification("id", 1)
    sql, params = DuckDBSpecificationBuilder.build(spec)
    assert sql == "id != ?"
    assert params == [1]


def test_build_dict_specification(dict_specification):
    sql, params = DuckDBSpecificationBuilder.build(dict_specification)
    assert sql == "id = ? AND test = ?"
    assert params == [1, 2]


def test_build_empty_specification(empty_specification):
    sql, params = DuckDBSpecificationBuilder.build(empty_specification)
    assert sql == "TRUE"
    assert params == []

    sql, params = DuckDBSpecificationBuilder.build(
        empty_specification & empty_specification
    )
    assert sql == "TRUE"
    assert params == []

    sql, params = DuckDBSpecificationBuilder.build(
        empty_specification | empty_specification
    )
    assert sql == "TRUE"
    assert params == []


def test_build_complex_and_specification():
    from fractal_specifications.generic.operators import (
        EqualsSpecification,
        GreaterThanSpecification,
    )

    spec = EqualsSpecification("name", "John") & GreaterThanSpecification("age", 18)
    sql, params = DuckDBSpecificationBuilder.build(spec)
    assert sql == "(name = ?) AND (age > ?)"
    assert params == ["John", 18]


def test_build_complex_or_specification():
    from fractal_specifications.generic.operators import (
        EqualsSpecification,
        LessThanSpecification,
    )

    spec = EqualsSpecification("status", "active") | LessThanSpecification("age", 65)
    sql, params = DuckDBSpecificationBuilder.build(spec)
    assert sql == "(status = ?) OR (age < ?)"
    assert params == ["active", 65]


def test_build_nested_specification():
    from fractal_specifications.generic.operators import (
        EqualsSpecification,
        GreaterThanSpecification,
        LessThanSpecification,
    )

    spec = (EqualsSpecification("status", "active") & GreaterThanSpecification("age", 18)) | (
        EqualsSpecification("type", "premium") & LessThanSpecification("age", 65)
    )
    sql, params = DuckDBSpecificationBuilder.build(spec)
    assert sql == "((status = ?) AND (age > ?)) OR ((type = ?) AND (age < ?))"
    assert params == ["active", 18, "premium", 65]


def test_specification_not_mapped():
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToDuckDB):
        DuckDBSpecificationBuilder.build(ErrorSpecification())
