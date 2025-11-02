from typing import Any, Collection

import pytest
from django.db.models import Q  # type: ignore

from fractal_specifications.contrib.django.specifications import (
    DjangoOrmSpecificationBuilder,
    SpecificationNotMappedToDjangoOrm,
)


def test_build_none():
    assert DjangoOrmSpecificationBuilder.build(None) is None


def test_build_equals_specification(equals_specification):
    assert DjangoOrmSpecificationBuilder.build(equals_specification) == Q(id=1)


def test_build_or_specification(or_specification):
    assert DjangoOrmSpecificationBuilder.build(or_specification) == Q(id=1) | Q(
        name="test"
    )


def test_build_and_specification(and_specification):
    assert DjangoOrmSpecificationBuilder.build(and_specification) == Q(
        id=1, name="test"
    )


def test_build_not_equals_specification(not_equals_specification):
    assert DjangoOrmSpecificationBuilder.build(not_equals_specification) == ~Q(id=1)


def test_build_contains_specification(contains_specification):
    assert DjangoOrmSpecificationBuilder.build(contains_specification) == Q(
        field__icontains="test"
    )


def test_build_in_specification(in_specification):
    assert DjangoOrmSpecificationBuilder.build(in_specification) == Q(
        field__in=[1, 2, 3]
    )


def test_build_in_empty_specification(in_empty_specification):
    assert DjangoOrmSpecificationBuilder.build(in_empty_specification) == Q(
        field__in=[]
    )


def test_build_less_than_specification(less_than_specification):
    assert DjangoOrmSpecificationBuilder.build(less_than_specification) == Q(id__lt=1)


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert DjangoOrmSpecificationBuilder.build(less_than_equal_specification) == Q(
        id__lte=1
    )


def test_build_greater_than_specification(greater_than_specification):
    assert DjangoOrmSpecificationBuilder.build(greater_than_specification) == Q(
        id__gt=1
    )


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert DjangoOrmSpecificationBuilder.build(greater_than_equal_specification) == Q(
        id__gte=1
    )


def test_build_regex_string_match_specification(regex_string_match_specification):
    assert DjangoOrmSpecificationBuilder.build(regex_string_match_specification) == Q(
        id__regex="abc"
    )


def test_build_is_none_specification(is_none_specification):
    assert DjangoOrmSpecificationBuilder.build(is_none_specification) == Q(
        field__isnull=True
    )


def test_build_dict_specification(dict_specification):
    assert DjangoOrmSpecificationBuilder.build(dict_specification) == Q(id=1, test=2)


def test_build_empty_specification(empty_specification):
    assert DjangoOrmSpecificationBuilder.build(empty_specification) is None


def test_create_q_dict():
    assert isinstance(DjangoOrmSpecificationBuilder._create_q({"id": 1}), Q)
    assert DjangoOrmSpecificationBuilder._create_q({"id": 1}).children == [("id", 1)]


def test_create_q_list():
    assert isinstance(DjangoOrmSpecificationBuilder._create_q([("id", 1)]), Q)
    assert DjangoOrmSpecificationBuilder._create_q([("id", 1)]).children == [("id", 1)]


def test_specification_not_mapped():
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToDjangoOrm):
        DjangoOrmSpecificationBuilder.build(ErrorSpecification())
