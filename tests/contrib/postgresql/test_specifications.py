from typing import Any, Collection

import pytest

from fractal_specifications.contrib.postgresql.specifications import (
    PostgresSpecificationBuilder,
    SpecificationNotMappedToPostgres,
)


def test_build_none():
    sql, params = PostgresSpecificationBuilder.build(None)
    assert sql == "TRUE"
    assert params == []


def test_build_equals_specification(equals_specification):
    sql, params = PostgresSpecificationBuilder.build(equals_specification)
    assert sql == "id = %s"
    assert params == [1]


def test_build_or_specification(or_specification):
    sql, params = PostgresSpecificationBuilder.build(or_specification)
    assert sql == "(id = %s) OR (name = %s)"
    assert params == [1, "test"]


def test_build_and_specification(and_specification):
    sql, params = PostgresSpecificationBuilder.build(and_specification)
    assert sql == "(id = %s) AND (name = %s)"
    assert params == [1, "test"]


def test_build_contains_specification(contains_specification):
    sql, params = PostgresSpecificationBuilder.build(contains_specification)
    assert sql == "field ILIKE %s"
    assert params == ["%test%"]


def test_build_in_specification(in_specification):
    sql, params = PostgresSpecificationBuilder.build(in_specification)
    assert sql == "field IN (%s,%s,%s)"
    assert params == [1, 2, 3]


def test_build_in_empty_specification(in_empty_specification):
    sql, params = PostgresSpecificationBuilder.build(in_empty_specification)
    assert sql == "field IN ()"
    assert params == []


def test_build_less_than_specification(less_than_specification):
    sql, params = PostgresSpecificationBuilder.build(less_than_specification)
    assert sql == "id < %s"
    assert params == [1]


def test_build_less_than_equal_specification(less_than_equal_specification):
    sql, params = PostgresSpecificationBuilder.build(less_than_equal_specification)
    assert sql == "id <= %s"
    assert params == [1]


def test_build_greater_than_specification(greater_than_specification):
    sql, params = PostgresSpecificationBuilder.build(greater_than_specification)
    assert sql == "id > %s"
    assert params == [1]


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    sql, params = PostgresSpecificationBuilder.build(greater_than_equal_specification)
    assert sql == "id >= %s"
    assert params == [1]


def test_build_regex_string_match_specification(regex_string_match_specification):
    sql, params = PostgresSpecificationBuilder.build(regex_string_match_specification)
    # PostgreSQL uses ~* operator for case-insensitive regex matching
    assert sql == "id ~* %s"
    assert params == ["abc"]


def test_build_is_none_specification(is_none_specification):
    sql, params = PostgresSpecificationBuilder.build(is_none_specification)
    assert sql == "field IS NULL"
    assert params == []


def test_build_not_equals_specification():
    from fractal_specifications.generic.operators import NotEqualsSpecification

    spec = NotEqualsSpecification("id", 1)
    sql, params = PostgresSpecificationBuilder.build(spec)
    assert sql == "id != %s"
    assert params == [1]


def test_build_dict_specification(dict_specification):
    sql, params = PostgresSpecificationBuilder.build(dict_specification)
    assert sql == "id = %s AND test = %s"
    assert params == [1, 2]


def test_build_empty_specification(empty_specification):
    sql, params = PostgresSpecificationBuilder.build(empty_specification)
    assert sql == "TRUE"
    assert params == []

    sql, params = PostgresSpecificationBuilder.build(
        empty_specification & empty_specification
    )
    assert sql == "TRUE"
    assert params == []

    sql, params = PostgresSpecificationBuilder.build(
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
    sql, params = PostgresSpecificationBuilder.build(spec)
    assert sql == "(name = %s) AND (age > %s)"
    assert params == ["John", 18]


def test_build_complex_or_specification():
    from fractal_specifications.generic.operators import (
        EqualsSpecification,
        LessThanSpecification,
    )

    spec = EqualsSpecification("status", "active") | LessThanSpecification("age", 65)
    sql, params = PostgresSpecificationBuilder.build(spec)
    assert sql == "(status = %s) OR (age < %s)"
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
    sql, params = PostgresSpecificationBuilder.build(spec)
    assert sql == "((status = %s) AND (age > %s)) OR ((type = %s) AND (age < %s))"
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

    with pytest.raises(SpecificationNotMappedToPostgres):
        PostgresSpecificationBuilder.build(ErrorSpecification())
