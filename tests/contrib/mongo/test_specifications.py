from typing import Any, Collection

import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"id": {"$eq": 1}}),  # type: ignore
    (
        pytest.lazy_fixture("or_specification"),  # type: ignore
        {"$or": [{"id": {"$eq": 1}}, {"name": {"$eq": "test"}}]},
    ),
    (
        pytest.lazy_fixture("and_specification"),  # type: ignore
        {"$and": [{"id": {"$eq": 1}}, {"name": {"$eq": "test"}}]},
    ),
    (pytest.lazy_fixture("in_specification"), {"field": {"$in": [1, 2, 3]}}),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), {"id": {"$lt": 1}}),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), {"id": {"$lte": 1}}),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), {"id": {"$gt": 1}}),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), {"id": {"$gte": 1}}),  # type: ignore
    (pytest.lazy_fixture("regex_string_match_specification"), {"id": {"$regex": ".*abc.*"}}),  # type: ignore
    (
        pytest.lazy_fixture("dict_specification"),  # type: ignore
        {"$and": [{"id": {"$eq": 1}}, {"test": {"$eq": 2}}]},
    ),
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.mongo.specifications import (
        MongoSpecificationBuilder,
    )

    assert MongoSpecificationBuilder.build(specification) == expected


def test_specification_not_mapped():
    from fractal_specifications.contrib.mongo.specifications import (
        MongoSpecificationBuilder,
        SpecificationNotMappedToMongo,
    )
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
