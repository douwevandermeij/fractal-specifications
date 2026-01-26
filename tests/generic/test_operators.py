from dataclasses import make_dataclass
from typing import List

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
    NotEqualsSpecification,
    NotSpecification,
    RegexStringMatchSpecification,
)


def test_not_specification():
    spec = NotSpecification(EqualsSpecification("id", 2))
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=1))


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
    assert spec.is_satisfied_by(DC(id=1))


def test_equals_specification():
    spec = EqualsSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=1))


def test_equals_specification_dot():
    spec = EqualsSpecification("obj.id", 1)
    DC1 = make_dataclass("DC1", [("id", int)])
    DC2 = make_dataclass("DC2", [("obj", DC1)])
    assert spec.is_satisfied_by(DC2(DC1(id=1)))


def test_not_equals_specification():
    spec = NotEqualsSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=2))


def test_less_than_specification():
    spec = LessThanSpecification("id", 2)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=1))


def test_less_than_equal_specification():
    spec = LessThanEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=1))


def test_greater_than_specification():
    spec = GreaterThanSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=2))


def test_greater_than_equal_specification():
    spec = GreaterThanEqualSpecification("id", 1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(id=1))


def test_contains_specification():
    spec = ContainsSpecification("name", "a")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(name="fractal"))


def test_contains_dot_specification():
    spec = ContainsSpecification("obj.name", "a")
    DC = make_dataclass("DC", [("name", str)])
    OBJ = make_dataclass("OBJ", [("obj", DC)])
    assert spec.is_satisfied_by(OBJ(obj=DC(name="fractal")))


def test_contains_double_underscore_specification():
    spec = ContainsSpecification("obj__name", "a")
    DC = make_dataclass("DC", [("name", str)])
    OBJ = make_dataclass("OBJ", [("obj", DC)])
    assert spec.is_satisfied_by(OBJ(obj=DC(name="fractal")))


def test_contains_none_specification():
    spec = ContainsSpecification("name", "a")
    DC = make_dataclass("DC", [("name", None)])
    assert not spec.is_satisfied_by(DC(name=None))


def test_list_contains_specification():
    spec = ContainsSpecification("names", "fractal")
    DC = make_dataclass("DC", [("names", list)])
    assert spec.is_satisfied_by(DC(names=["fractal"]))


def test_regex_string_match_specification():
    spec = RegexStringMatchSpecification("name", "^f.*l$")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(name="fractal"))


def test_is_none_specification():
    spec = IsNoneSpecification("name")
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(name=None))


def test_is_none_specification_str():
    spec = IsNoneSpecification("name")
    assert spec.__str__() == "IsNoneSpecification(name)"


def test_is_none_specification_repr():
    spec = IsNoneSpecification("name")
    assert spec.__repr__() == "IsNoneSpecification(name)"


def test_pre_process_equals_specification():
    spec = EqualsSpecification("name", "abc", lambda i: i.lower())
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(name="ABC"))


def test_pre_process_contains_specification():
    spec = ContainsSpecification("name", "A", lambda i: i.upper())
    DC = make_dataclass("DC", [("name", str)])
    assert spec.is_satisfied_by(DC(name="fractal"))


def test_pre_process_list_contains_specification():
    spec = ContainsSpecification("roles", "ADMIN", lambda i: [r.upper() for r in i])
    DC = make_dataclass("DC", [("roles", List[str])])
    assert spec.is_satisfied_by(DC(roles=["admin", "owner"]))


def test_pre_process_regex_string_match_specification():
    spec = RegexStringMatchSpecification(
        "roles", "a.*n", lambda i: ",".join([r.lower() for r in i])
    )
    DC = make_dataclass("DC", [("roles", List[str])])
    assert spec.is_satisfied_by(DC(roles=["admin", "owner"]))


def test_none_regex_string_match_specification():
    spec = RegexStringMatchSpecification("name", r"^[a-z]+$")
    DC = make_dataclass("DC", [("name", str)])
    assert not spec.is_satisfied_by(DC(name=None))
