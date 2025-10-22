from typing import Any, Collection

import pytest

from fractal_specifications.contrib.google_firestore.specifications import (
    FirestoreSpecificationBuilder,
    SpecificationNotMappedToFirestore,
)


def test_build_none():
    assert FirestoreSpecificationBuilder.build(None) is None


def test_build_equals_specification(equals_specification):
    assert FirestoreSpecificationBuilder.build(equals_specification) == ("id", "==", 1)


def test_build_or_specification(or_specification):
    with pytest.raises(SpecificationNotMappedToFirestore):
        FirestoreSpecificationBuilder.build(or_specification)


def test_build_and_specification(and_specification):
    assert FirestoreSpecificationBuilder.build(and_specification) == [
        ("id", "==", 1),
        ("name", "==", "test"),
    ]


def test_build_contains_specification(contains_specification):
    assert FirestoreSpecificationBuilder.build(contains_specification) == (
        "field",
        "array-contains",
        "test",
    )


def test_build_in_specification(in_specification):
    assert FirestoreSpecificationBuilder.build(in_specification) == (
        "field",
        "in",
        [1, 2, 3],
    )


def test_build_in_empty_specification(in_empty_specification):
    assert FirestoreSpecificationBuilder.build(in_empty_specification) is None


def test_build_less_than_specification(less_than_specification):
    assert FirestoreSpecificationBuilder.build(less_than_specification) == (
        "id",
        "<",
        1,
    )


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert FirestoreSpecificationBuilder.build(less_than_equal_specification) == (
        "id",
        "<=",
        1,
    )


def test_build_greater_than_specification(greater_than_specification):
    assert FirestoreSpecificationBuilder.build(greater_than_specification) == (
        "id",
        ">",
        1,
    )


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert FirestoreSpecificationBuilder.build(greater_than_equal_specification) == (
        "id",
        ">=",
        1,
    )


def test_build_regex_string_match_specification(regex_string_match_specification):
    assert FirestoreSpecificationBuilder.build(regex_string_match_specification) == (
        "id",
        "array-contains",
        "abc",
    )


def test_build_is_none_specification(is_none_specification):
    with pytest.raises(SpecificationNotMappedToFirestore):
        FirestoreSpecificationBuilder.build(is_none_specification)


def test_build_dict_specification(dict_specification):
    assert FirestoreSpecificationBuilder.build(dict_specification) == [
        ("id", "==", 1),
        ("test", "==", 2),
    ]


def test_build_empty_specification(empty_specification):
    assert FirestoreSpecificationBuilder.build(empty_specification) is None


def test_specification_not_mapped():
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToFirestore):
        FirestoreSpecificationBuilder.build(ErrorSpecification())
