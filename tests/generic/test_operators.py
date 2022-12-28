from dataclasses import make_dataclass

from fractal_specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    FieldValueSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotSpecification,
)


def test_not_specification():
    spec = NotSpecification(EqualsSpecification("id", 2))
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_not_specification_to_collection():
    spec = NotSpecification(EqualsSpecification("id", 2))
    assert spec.to_collection() == [EqualsSpecification("id", 2)]


def test_not_specification_str():
    spec = NotSpecification(EqualsSpecification("id", 2))
    assert spec.__str__() == "NotSpecification(EqualsSpecification(id=2))"


def test_not_specification_eq():
    assert NotSpecification(EqualsSpecification("id", 2)) == NotSpecification(
        EqualsSpecification("id", 2)
    )


def test_field_value_specification():
    spec = FieldValueSpecification("field", "value")
    assert spec.to_collection() == {"field", "value"}


def test_in_specification():
    spec = InSpecification("id", [1, 2, 3])
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_equals_specification():
    spec = EqualsSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_less_than_specification():
    spec = LessThanSpecification("id", 2)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_less_than_equal_specification():
    spec = LessThanEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_greater_than_specification():
    spec = GreaterThanSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=2)))


def test_greater_than_equal_specification():
    spec = GreaterThanEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))


def test_contains_specification():
    spec = ContainsSpecification("name", "a")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(**dict(name="fractal")))


def test_is_none_specification():
    spec = IsNoneSpecification("name")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(**dict(name=None)))
