from dataclasses import make_dataclass

from fractal_specifications.generic.operators import EqualsSpecification


def test_equals_specification():
    spec = EqualsSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))
