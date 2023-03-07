from fractal_specifications.generic.specification import Specification


def test_dumps(equals_specification):
    assert equals_specification.dumps() == '{"op": "equals", "field": "id", "value": 1}'


def test_loads(equals_specification):
    assert (
        Specification.loads('{"op": "equals", "field": "id", "value": 1}')
        == equals_specification
    )


def test_to_dict(equals_specification):
    assert equals_specification.to_dict() == {"op": "equals", "field": "id", "value": 1}


def test_from_dict(equals_specification):
    assert (
        Specification.from_dict({"op": "equals", "field": "id", "value": 1})
        == equals_specification
    )


def test_complex_specification_serialization(complex_specification):
    assert (
        Specification.from_dict(complex_specification.to_dict())
        == complex_specification
    )


def test_shorthand_ops(complex_specification):
    s = complex_specification.dumps()
    for old, new in [
        ("equals", "=="),
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
