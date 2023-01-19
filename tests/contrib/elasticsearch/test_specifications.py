from typing import Any, Collection

import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"match": {"id.keyword": 1}}),  # type: ignore
    (
        pytest.lazy_fixture("or_specification"),  # type: ignore
        {
            "bool": {
                "should": [
                    {"match": {"id.keyword": 1}},
                    {"match": {"name.keyword": "test"}},
                ]
            }
        },
    ),
    (
        pytest.lazy_fixture("and_specification"),  # type: ignore
        {
            "bool": {
                "must": [
                    {"match": {"id.keyword": 1}},
                    {"match": {"name.keyword": "test"}},
                ]
            }
        },
    ),
    (pytest.lazy_fixture("in_specification"), {"query_string": {"default_field": "field", "query": [1, 2, 3]}}),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), {"bool": {"filter": [{"range": {"id": {"lt": 1}}}]}}),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), {"bool": {"filter": [{"range": {"id": {"lte": 1}}}]}}),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), {"bool": {"filter": [{"range": {"id": {"gt": 1}}}]}}),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), {"bool": {"filter": [{"range": {"id": {"gte": 1}}}]}}),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.elasticsearch.specifications import (
        ElasticSpecificationBuilder,
    )

    assert ElasticSpecificationBuilder.build(specification) == expected


def test_specification_not_mapped():
    from fractal_specifications.contrib.elasticsearch.specifications import (
        ElasticSpecificationBuilder,
        SpecificationNotMappedToElastic,
    )
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
