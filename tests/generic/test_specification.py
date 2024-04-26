from dataclasses import make_dataclass

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    RegexStringMatchSpecification,
)
from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


def test_parse():
    assert Specification.parse(id=1) == EqualsSpecification("id", 1)
    assert Specification.parse(id_x=1) == EqualsSpecification("id_x", 1)
    assert Specification.parse(id__x=1) == EqualsSpecification("id.x", 1)
    assert Specification.parse(id__x=1, _lookup_separator="__") == EqualsSpecification(
        "id__x", 1
    )
    assert Specification.parse(id__eq=1) == EqualsSpecification("id", 1)
    assert Specification.parse(obj__id__eq=1) == EqualsSpecification("obj.id", 1)
    assert Specification.parse(id__in=[1]) == InSpecification("id", [1])
    assert Specification.parse(id__contains="a") == ContainsSpecification("id", "a")
    assert Specification.parse(name__matches=r"^.*$") == RegexStringMatchSpecification(
        "name", r"^.*$"
    )
    assert Specification.parse(id__lt=1) == LessThanSpecification("id", 1)
    assert Specification.parse(id__lte=1) == LessThanEqualSpecification("id", 1)
    assert Specification.parse(id__gt=1) == GreaterThanSpecification("id", 1)
    assert Specification.parse(id__gte=1) == GreaterThanEqualSpecification("id", 1)
    assert Specification.parse(id=1, name="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id__eq=1, name__eq="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id__eq=1, name="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id=1, name__eq="a") == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert Specification.parse(id__gt=1, name__contains="a") == AndSpecification(
        [GreaterThanSpecification("id", 1), ContainsSpecification("name", "a")]
    )


def test_specification_and():
    spec = EqualsSpecification("id", 1).And(EqualsSpecification("name", "a"))
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_specification_or():
    spec = EqualsSpecification("id", 1).Or(EqualsSpecification("name", "a"))
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_specification_not_and():
    spec = Specification.Not(
        EqualsSpecification("id", 1).And(EqualsSpecification("name", "a"))
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="b")))


def test_specification_not_or():
    spec = Specification.Not(
        EqualsSpecification("id", 1).Or(EqualsSpecification("name", "a"))
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=2, name="b")))


def test_parse_none():
    assert Specification.parse() is None


def test_and():
    assert Specification.parse(id=1) & Specification.parse(
        name="a"
    ) == AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )


def test_or():
    assert Specification.parse(id=1) | Specification.parse(name="a") == OrSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )


def test_empty():
    assert EmptySpecification().is_satisfied_by(None)
    assert EmptySpecification().to_collection() == []
    assert str(EmptySpecification()) == "EmptySpecification"
    assert EmptySpecification() == EmptySpecification()


def test_hash(equals_specification, complex_specification):
    test_dict = {
        equals_specification: True,
        complex_specification: True,
        equals_specification & complex_specification: True,
        equals_specification | complex_specification: True,
    }
    assert test_dict[equals_specification]
    assert test_dict[complex_specification]
    assert test_dict[equals_specification & complex_specification]
    assert test_dict[equals_specification | complex_specification]
