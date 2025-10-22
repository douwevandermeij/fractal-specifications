from typing import Any, Collection

import pytest

from fractal_specifications.contrib.elasticsearch.specifications import (
    ElasticSpecificationBuilder,
    SpecificationNotMappedToElastic,
)


def test_build_none():
    assert ElasticSpecificationBuilder.build(None) is None


def test_build_equals_specification(equals_specification):
    assert ElasticSpecificationBuilder.build(equals_specification) == {
        "match": {"id.keyword": 1}
    }


def test_build_or_specification(or_specification):
    assert ElasticSpecificationBuilder.build(or_specification) == {
        "bool": {
            "should": [
                {"match": {"id.keyword": 1}},
                {"match": {"name.keyword": "test"}},
            ]
        }
    }


def test_build_and_specification(and_specification):
    assert ElasticSpecificationBuilder.build(and_specification) == {
        "bool": {
            "must": [
                {"match": {"id.keyword": 1}},
                {"match": {"name.keyword": "test"}},
            ]
        }
    }


def test_build_contains_specification(contains_specification):
    with pytest.raises(SpecificationNotMappedToElastic):
        ElasticSpecificationBuilder.build(contains_specification)


def test_build_in_specification(in_specification):
    assert ElasticSpecificationBuilder.build(in_specification) == {
        "query_string": {"default_field": "field", "query": [1, 2, 3]}
    }


def test_build_in_empty_specification(in_empty_specification):
    assert ElasticSpecificationBuilder.build(in_empty_specification) == {
        "query_string": {"default_field": "field", "query": []}
    }


def test_build_less_than_specification(less_than_specification):
    assert ElasticSpecificationBuilder.build(less_than_specification) == {
        "bool": {"filter": [{"range": {"id": {"lt": 1}}}]}
    }


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert ElasticSpecificationBuilder.build(less_than_equal_specification) == {
        "bool": {"filter": [{"range": {"id": {"lte": 1}}}]}
    }


def test_build_greater_than_specification(greater_than_specification):
    assert ElasticSpecificationBuilder.build(greater_than_specification) == {
        "bool": {"filter": [{"range": {"id": {"gt": 1}}}]}
    }


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert ElasticSpecificationBuilder.build(greater_than_equal_specification) == {
        "bool": {"filter": [{"range": {"id": {"gte": 1}}}]}
    }


def test_build_regex_string_match_specification(regex_string_match_specification):
    with pytest.raises(SpecificationNotMappedToElastic):
        assert ElasticSpecificationBuilder.build(regex_string_match_specification) == {}


def test_build_is_none_specification(is_none_specification):
    with pytest.raises(SpecificationNotMappedToElastic):
        ElasticSpecificationBuilder.build(is_none_specification)


def test_build_dict_specification(dict_specification):
    with pytest.raises(SpecificationNotMappedToElastic):
        ElasticSpecificationBuilder.build(dict_specification)


def test_build_empty_specification(empty_specification):
    assert ElasticSpecificationBuilder.build(empty_specification) is None


def test_specification_not_mapped():
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToElastic):
        ElasticSpecificationBuilder.build(ErrorSpecification())
