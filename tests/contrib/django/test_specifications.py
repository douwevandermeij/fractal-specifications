import pytest
from django.db.models import Q  # type: ignore

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"id": 1}),  # type: ignore
    (pytest.lazy_fixture("or_specification"), Q(id=1) | Q(name="test")),  # type: ignore
    (pytest.lazy_fixture("and_specification"), Q(id=1, name="test")),  # type: ignore
    (pytest.lazy_fixture("in_specification"), {"field__in": [1, 2, 3]}),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), {"id__lt": 1}),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), {"id__lte": 1}),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), {"id__gt": 1}),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), {"id__gte": 1}),  # type: ignore
    (pytest.lazy_fixture("regex_string_match_specification"), {"id__regex": ".*abc.*"}),  # type: ignore
    (pytest.lazy_fixture("dict_specification"), {"id": 1, "test": 2}),  # type: ignore
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

    assert isinstance(DjangoOrmSpecificationBuilder.create_q({"id": 1}), Q)
    assert DjangoOrmSpecificationBuilder.create_q({"id": 1}).children == [("id", 1)]


def test_create_q_list():
    from fractal_specifications.contrib.django.specifications import (
        DjangoOrmSpecificationBuilder,
    )

    assert isinstance(DjangoOrmSpecificationBuilder.create_q([("id", 1)]), Q)
    assert DjangoOrmSpecificationBuilder.create_q([("id", 1)]).children == [("id", 1)]
