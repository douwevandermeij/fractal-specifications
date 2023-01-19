from typing import Any, Collection

import pytest
from django.db.models import Q  # type: ignore

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), Q(id=1)),  # type: ignore
    (pytest.lazy_fixture("or_specification"), Q(id=1) | Q(name="test")),  # type: ignore
    (pytest.lazy_fixture("and_specification"), Q(id=1, name="test")),  # type: ignore
    (pytest.lazy_fixture("in_specification"), Q(field__in=[1, 2, 3])),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), Q(id__lt=1)),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), Q(id__lte=1)),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), Q(id__gt=1)),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), Q(id__gte=1)),  # type: ignore
    (pytest.lazy_fixture("regex_string_match_specification"), Q(id__regex=".*abc.*")),  # type: ignore
    (pytest.lazy_fixture("is_none_specification"), Q(field__isnull=True)),  # type: ignore
    (pytest.lazy_fixture("dict_specification"), Q(id=1, test=2)),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.django.specifications import (
        DjangoOrmSpecificationBuilder,
    )

    assert DjangoOrmSpecificationBuilder.build(specification) == expected


def test_create_q_dict():
    from fractal_specifications.contrib.django.specifications import (
        DjangoOrmSpecificationBuilder,
    )

    assert isinstance(DjangoOrmSpecificationBuilder._create_q({"id": 1}), Q)
    assert DjangoOrmSpecificationBuilder._create_q({"id": 1}).children == [("id", 1)]


def test_create_q_list():
    from fractal_specifications.contrib.django.specifications import (
        DjangoOrmSpecificationBuilder,
    )

    assert isinstance(DjangoOrmSpecificationBuilder._create_q([("id", 1)]), Q)
    assert DjangoOrmSpecificationBuilder._create_q([("id", 1)]).children == [("id", 1)]


def test_specification_not_mapped():
    from fractal_specifications.contrib.django.specifications import (
        DjangoOrmSpecificationBuilder,
        SpecificationNotMappedToDjangoOrm,
    )
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
