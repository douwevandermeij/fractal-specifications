from decimal import Decimal

import pytest

from fractal_specifications.contrib.sqlite.specifications import (
    SpecificationNotMappedToSqlite,
    SqliteSpecificationBuilder,
)

build = SqliteSpecificationBuilder.build


def test_build_none():
    assert build(None) == ("1 = 1", [])


def test_build_empty_specification(empty_specification):
    assert build(empty_specification) == ("1 = 1", [])
    assert build(empty_specification & empty_specification) == ("1 = 1", [])
    assert build(empty_specification | empty_specification) == ("1 = 1", [])


def test_build_equals_specification(equals_specification):
    assert build(equals_specification) == ("json_extract(data, ?) = ?", ["$.id", 1])


def test_nested_field_path():
    from fractal_specifications.generic.operators import EqualsSpecification

    assert build(EqualsSpecification("address__city", "NYC")) == (
        "json_extract(data, ?) = ?",
        ["$.address.city", "NYC"],
    )


def test_build_and_specification(and_specification):
    # The leading EmptySpecification is skipped.
    sql, params = build(and_specification)
    assert sql == "(json_extract(data, ?) = ?) AND (json_extract(data, ?) = ?)"
    assert params == ["$.id", 1, "$.name", "test"]


def test_build_or_specification(or_specification):
    sql, params = build(or_specification)
    assert sql == "(json_extract(data, ?) = ?) OR (json_extract(data, ?) = ?)"
    assert params == ["$.id", 1, "$.name", "test"]


def test_build_in_specification(in_specification):
    assert build(in_specification) == (
        "json_extract(data, ?) IN (?, ?, ?)",
        ["$.field", 1, 2, 3],
    )


def test_build_in_empty_specification(in_empty_specification):
    assert build(in_empty_specification) == ("0 = 1", [])


def test_build_less_than_specification(less_than_specification):
    assert build(less_than_specification) == ("json_extract(data, ?) < ?", ["$.id", 1])


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert build(less_than_equal_specification) == (
        "json_extract(data, ?) <= ?",
        ["$.id", 1],
    )


def test_build_greater_than_specification(greater_than_specification):
    assert build(greater_than_specification) == (
        "json_extract(data, ?) > ?",
        ["$.id", 1],
    )


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert build(greater_than_equal_specification) == (
        "json_extract(data, ?) >= ?",
        ["$.id", 1],
    )


def test_build_is_none_specification(is_none_specification):
    assert build(is_none_specification) == (
        "json_extract(data, ?) IS NULL",
        ["$.field"],
    )


def test_build_not_equals_is_null_safe(not_equals_specification):
    sql, params = build(not_equals_specification)
    assert sql == "(json_extract(data, ?) IS NULL OR json_extract(data, ?) <> ?)"
    assert params == ["$.id", "$.id", 1]


def test_build_not_equals_none_becomes_is_not_null():
    from fractal_specifications.generic.operators import NotEqualsSpecification

    assert build(NotEqualsSpecification("opt", None)) == (
        "json_extract(data, ?) IS NOT NULL",
        ["$.opt"],
    )


def _unmappable_specs():
    from fractal_specifications.generic.operators import (
        ContainsSpecification,
        EqualsSpecification,
        GreaterThanSpecification,
        InSpecification,
        NotSpecification,
        RegexStringMatchSpecification,
    )

    return [
        ContainsSpecification("name", "x"),
        RegexStringMatchSpecification("name", "abc"),
        NotSpecification(EqualsSpecification("name", "x")),
        EqualsSpecification("price", Decimal("1.00")),  # non-native value
        GreaterThanSpecification("price", Decimal("9.99")),
        InSpecification("price", [Decimal("1.00")]),
    ]


@pytest.mark.parametrize("spec", _unmappable_specs())
def test_unmappable_specs_raise(spec):
    with pytest.raises(SpecificationNotMappedToSqlite):
        build(spec)


def test_non_native_inside_and_propagates():
    from fractal_specifications.generic.collections import AndSpecification
    from fractal_specifications.generic.operators import EqualsSpecification

    spec = AndSpecification(
        [
            EqualsSpecification("name", "x"),
            EqualsSpecification("price", Decimal("1.00")),
        ]
    )
    with pytest.raises(SpecificationNotMappedToSqlite):
        build(spec)
