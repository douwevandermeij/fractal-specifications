from typing import Any, Collection

import pytest

from fractal_specifications.contrib.mongo.specifications import (
    MongoSpecificationBuilder,
    SpecificationNotMappedToMongo,
)


def test_build_none():
    assert MongoSpecificationBuilder.build(None) is None


def test_build_equals_specification(equals_specification):
    assert MongoSpecificationBuilder.build(equals_specification) == {"id": {"$eq": 1}}


def test_build_or_specification(or_specification):
    assert MongoSpecificationBuilder.build(or_specification) == {
        "$or": [{"id": {"$eq": 1}}, {"name": {"$eq": "test"}}]
    }


def test_build_and_specification(and_specification):
    assert MongoSpecificationBuilder.build(and_specification) == {
        "$and": [{"id": {"$eq": 1}}, {"name": {"$eq": "test"}}]
    }


def test_build_contains_specification(contains_specification):
    assert MongoSpecificationBuilder.build(contains_specification) == {
        "field": {"$regex": ".*test.*"}
    }


def test_build_contains_specification_with_special_chars():
    from fractal_specifications.generic.operators import ContainsSpecification

    # Test that special regex characters are properly escaped
    spec = ContainsSpecification("field", "test.*value+")
    assert MongoSpecificationBuilder.build(spec) == {
        "field": {"$regex": r".*test\.\*value\+.*"}
    }


def test_build_not_equals_specification(not_equals_specification):
    assert MongoSpecificationBuilder.build(not_equals_specification) == {
        "id": {"$ne": 1}
    }


def test_build_in_specification(in_specification):
    assert MongoSpecificationBuilder.build(in_specification) == {
        "field": {"$in": [1, 2, 3]}
    }


def test_build_in_empty_specification(in_empty_specification):
    assert MongoSpecificationBuilder.build(in_empty_specification) == {
        "field": {"$in": []}
    }


def test_build_less_than_specification(less_than_specification):
    assert MongoSpecificationBuilder.build(less_than_specification) == {
        "id": {"$lt": 1}
    }


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert MongoSpecificationBuilder.build(less_than_equal_specification) == {
        "id": {"$lte": 1}
    }


def test_build_greater_than_specification(greater_than_specification):
    assert MongoSpecificationBuilder.build(greater_than_specification) == {
        "id": {"$gt": 1}
    }


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert MongoSpecificationBuilder.build(greater_than_equal_specification) == {
        "id": {"$gte": 1}
    }


def test_build_regex_string_match_specification(regex_string_match_specification):
    # RegexStringMatchSpecification now uses raw regex pattern without modification
    assert MongoSpecificationBuilder.build(regex_string_match_specification) == {
        "id": {"$regex": "abc"}
    }


def test_build_is_none_specification(is_none_specification):
    assert MongoSpecificationBuilder.build(is_none_specification) == {
        "field": {"$eq": None}
    }


def test_build_dict_specification(dict_specification):
    assert MongoSpecificationBuilder.build(dict_specification) == {
        "$and": [{"id": {"$eq": 1}}, {"test": {"$eq": 2}}]
    }


def test_build_empty_specification(empty_specification):
    assert MongoSpecificationBuilder.build(empty_specification) is None
    assert (
        MongoSpecificationBuilder.build(empty_specification & empty_specification)
        is None
    )
    assert (
        MongoSpecificationBuilder.build(empty_specification | empty_specification)
        is None
    )


def test_specification_not_mapped():
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToMongo):
        MongoSpecificationBuilder.build(ErrorSpecification())
