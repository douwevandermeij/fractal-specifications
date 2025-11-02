from typing import Any, Collection

import pytest

from fractal_specifications.contrib.sqlalchemy.specifications import (
    SpecificationNotMappedToSqlAlchemyOrm,
    SqlAlchemyOrmSpecificationBuilder,
)


def test_build_none():
    assert SqlAlchemyOrmSpecificationBuilder.build(None) is None


def test_build_equals_specification(equals_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(equals_specification) == {"id": 1}


def test_build_or_specification(or_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(or_specification) == [
        {"id": 1},
        {"name": "test"},
    ]


def test_build_and_specification(and_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(and_specification) == {
        "id": 1,
        "name": "test",
    }


def test_build_contains_specification(contains_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(contains_specification) == (
        "field",
        "contains",
        "test",
    )


def test_build_in_specification(in_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(in_specification) == (
        "field",
        "in",
        [1, 2, 3],
    )


def test_build_in_empty_specification(in_empty_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(in_empty_specification) == (
        "field",
        "in",
        [],
    )


def test_build_not_equals_specification(not_equals_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(not_equals_specification) == (
        "id",
        "ne",
        1,
    )


def test_build_less_than_specification(less_than_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(less_than_specification) == (
        "id",
        "lt",
        1,
    )


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(less_than_equal_specification) == (
        "id",
        "le",
        1,
    )


def test_build_greater_than_specification(greater_than_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(greater_than_specification) == (
        "id",
        "gt",
        1,
    )


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(greater_than_equal_specification) == (
        "id",
        "ge",
        1,
    )


def test_build_regex_string_match_specification(regex_string_match_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(regex_string_match_specification) == (
        "id",
        "regex",
        "abc",
    )


def test_build_is_none_specification(is_none_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(is_none_specification) == (
        "field",
        "is_none",
        None,
    )


def test_build_dict_specification(dict_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(dict_specification) == {
        "id": 1,
        "test": 2,
    }


def test_build_empty_specification(empty_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(empty_specification) is None


def test_build_and_specification_with_only_empty_specs(empty_specification):
    # Test the case where AndSpecification contains only EmptySpecifications
    # Empty results list causes all() to return True (vacuous truth), returning empty dict
    spec = empty_specification & empty_specification
    assert SqlAlchemyOrmSpecificationBuilder.build(spec) == {}


def test_build_and_specification_with_mixed_types():
    # Test AndSpecification with mix of dict and tuple results
    from fractal_specifications.generic.operators import (
        ContainsSpecification,
        EqualsSpecification,
    )

    spec = EqualsSpecification("name", "test") & ContainsSpecification("desc", "value")
    result = SqlAlchemyOrmSpecificationBuilder.build(spec)
    # Should return a list because results contain both dict and tuple
    assert result == [{"name": "test"}, ("desc", "contains", "value")]


def test_specification_not_mapped():
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(ErrorSpecification())
