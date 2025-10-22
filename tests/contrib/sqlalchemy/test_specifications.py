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
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(contains_specification)


def test_build_in_specification(in_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(in_specification)


def test_build_in_empty_specification(in_empty_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(in_empty_specification)


def test_build_less_than_specification(less_than_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(less_than_specification)


def test_build_less_than_equal_specification(less_than_equal_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(less_than_equal_specification)


def test_build_greater_than_specification(greater_than_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(greater_than_specification)


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(greater_than_equal_specification)


def test_build_regex_string_match_specification(regex_string_match_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(regex_string_match_specification)


def test_build_is_none_specification(is_none_specification):
    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(is_none_specification)


def test_build_dict_specification(dict_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(dict_specification) == {
        "id": 1,
        "test": 2,
    }


def test_build_empty_specification(empty_specification):
    assert SqlAlchemyOrmSpecificationBuilder.build(empty_specification) is None


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
