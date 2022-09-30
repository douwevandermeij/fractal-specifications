from dataclasses import make_dataclass

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import EqualsSpecification


def test_and_specification_to_collection():
    spec = AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert spec.to_collection() == [
        EqualsSpecification("id", 1),
        EqualsSpecification("name", "a"),
    ]


def test_or_specification_to_collection():
    spec = OrSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert spec.to_collection() == [
        EqualsSpecification("id", 1),
        EqualsSpecification("name", "a"),
    ]


def test_and_specification_str():
    spec = AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert (
        spec.__str__()
        == "AndSpecification(EqualsSpecification(id=1),EqualsSpecification(name=a))"
    )


def test_or_specification_str():
    spec = OrSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    assert (
        spec.__str__()
        == "OrSpecification(EqualsSpecification(id=1),EqualsSpecification(name=a))"
    )


def test_and_specification():
    spec = AndSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_specification_and_and():
    spec = EqualsSpecification("id", 1).And(
        AndSpecification(
            [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
        )
    )
    assert isinstance(spec, AndSpecification)
    assert len(spec.specifications) == 3
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_and_specification_and():
    spec = AndSpecification([EqualsSpecification("id", 1)]).And(
        EqualsSpecification("name", "a")
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_and_specification_and_and():
    spec = AndSpecification([EqualsSpecification("id", 1)]).And(
        AndSpecification([EqualsSpecification("name", "a")])
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="a")))


def test_or_specification():
    spec = OrSpecification(
        [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=1, name="b")))


def test_specification_or_or():
    spec = EqualsSpecification("id", 1).Or(
        OrSpecification(
            [EqualsSpecification("id", 1), EqualsSpecification("name", "a")]
        )
    )
    assert isinstance(spec, OrSpecification)
    assert len(spec.specifications) == 3
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=2, name="a")))


def test_or_specification_or():
    spec = OrSpecification([EqualsSpecification("id", 1)]).Or(
        EqualsSpecification("name", "a")
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=2, name="a")))


def test_or_specification_or_or():
    spec = OrSpecification([EqualsSpecification("id", 1)]).Or(
        OrSpecification([EqualsSpecification("name", "a")])
    )
    DC = make_dataclass("DC", [("id", int), ("name", str)])
    assert spec.is_satisfied_by(DC(**dict(id=2, name="a")))
