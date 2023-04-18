import pytest

from fractal_specifications.generic.specification import Specification


def test_dumps(equals_specification):
    assert equals_specification.dumps() == '{"op": "eq", "field": "id", "value": 1}'


def test_loads(equals_specification):
    assert (
        Specification.loads('{"op": "eq", "field": "id", "value": 1}')
        == equals_specification
    )


def test_to_dict(equals_specification):
    assert equals_specification.to_dict() == {"op": "eq", "field": "id", "value": 1}


def test_from_dict(equals_specification):
    assert (
        Specification.from_dict({"op": "eq", "field": "id", "value": 1})
        == equals_specification
    )


def test_complex_specification_serialization(complex_specification):
    assert complex_specification.to_dict() == {
        "op": "or",
        "specs": [
            {
                "op": "and",
                "specs": [
                    {"field": "id", "op": "eq", "value": 1},
                    {"field": "id", "op": "eq", "value": 1.5},
                    {"field": "id", "op": "eq", "value": False},
                    {"field": "id", "op": "eq", "value": True},
                    {"field": "id", "op": "eq", "value": None},
                    {"field": "price", "op": "gt", "value": 25},
                    {"field": "price", "op": "gte", "value": 25},
                    {"field": "price", "op": "lt", "value": 25},
                    {"field": "price", "op": "lte", "value": 25},
                    {
                        "op": "not",
                        "spec": {"field": "name", "op": "isnone", "value": None},
                    },
                    {"field": "field", "op": "contains", "value": "y"},
                ],
            },
            {
                "op": "and",
                "specs": [
                    {"field": "id", "op": "neq", "value": 1},
                    {"field": "field", "op": "in", "value": [1, 2, 3]},
                    {"field": "field", "op": "matches", "value": ".*abc.*"},
                ],
            },
            {"op": "and", "specs": [{"op": "empty"}, {"op": "empty"}]},
        ],
    }
    assert (
        Specification.from_dict(complex_specification.to_dict())
        == complex_specification
    )


def test_shorthand_ops(complex_specification):
    s = complex_specification.dumps()
    for old, new in [
        ("neq", "!="),
        ("eq", "=="),
        ("lte", "<="),
        ("lt", "<"),
        ("gte", ">="),
        ("gt", ">"),
        ("not", "!"),
        ("and", "&"),
        ("or", "|"),
    ]:
        s = s.replace(old, new)
    assert Specification.loads(s) == complex_specification


def test_complex_specification_dsl(complex_specification):
    print(complex_specification)
    assert (
        Specification.load_dsl(complex_specification.dump_dsl())
        == complex_specification
    )


def test_error_specification_dsl(complex_specification):
    from typing import Any, Collection

    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(ValueError):
        ErrorSpecification().dump_dsl()


def test_random_dsl_strings():
    for s in [
        "#",
        "# && #",
        "x == 1",
        "x == 'x'",
        "x != 'x'",
        "id != 1 && field in [1, 2, 3]",
        "a == 1 || ((b == 2) && c == 3)",
        "id == 1",
        "(id == 1)",
        "!(id == 1)",
        "(id == 1 || id == 2)",
        "id == 1 || id == 2",
        "id == 1 || id == 2 || id == 3 || id == 4",
        "(id == 1 || id == 2 || id == 3) && id == 3",
        "((id == 1 || (id == 2 || id == 3)) && id == 3)",
        "id == 1 || (id == 2 && id == 3)",
        "id == 1 || (id == 2 && id == 3 && !(name is None))",
        "!(name is None)",
        "!(name is None) && id == 1 && id == 3",
        "!(name is None) && (id == 1 || !(id == 3))",
        "!((name is None) && id == 1)",
        'field == "y"',
        'field == "y" || field == "y"',
        "field == 'y'",
        'field == "y"',
        "field contains 'y'",
        "id == 2 || field in [1, 2, 4, '2']",
        "field in [1, 2, 4, '2'] && id == 2",
        "field matches 'a*' && field in [1, 2, 4, '2']",
        'field matches "\\"',
        'field matches "\\"',
        "field matches '\\'",
        "field matches '\..*'",
        "((id == 1 && price > 25 && price >= 25 && price < 25 && price <= 25 && !(name is None) && field contains 'y' && field in [1, 2, 3] && field matches 'aaa\..*bbb'))",
        "((id == 1 && price > 25 && price >= 25 && price < 25 && price <= 25 && !(name is None) && field contains 'y') || (id != 1 && field in [1, 2, 3] && field matches '.*abc.*') || (# && #))",
        "!(id == 2)",
        "id != 2",
        "id == True",
        "id == False",
        "id == None",
        "id == -1",
        "id == 1.5",
        "field_name == 10",
        "name != 'John'",
        "age >= 18 && is_student == True",
        'roles contains "admin" || roles contains "editor"',
        "!(active == True)",
        "name in['John', 'Jane']",
        'email matches "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"',
        'address contains "123 Main St"',
        "#",
        "salary is None",
        "obj.id == 1",
    ]:
        spec = Specification.load_dsl(s)
        assert spec == Specification.load_dsl(spec.dump_dsl())
