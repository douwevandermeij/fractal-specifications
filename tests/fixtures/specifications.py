import pytest


@pytest.fixture
def equals_specification():
    from fractal_specifications.generic.operators import EqualsSpecification

    return EqualsSpecification("id", 1)


@pytest.fixture
def other_equals_specification():
    from fractal_specifications.generic.operators import EqualsSpecification

    return EqualsSpecification("name", "test")


@pytest.fixture
def or_specification(
    empty_specification, equals_specification, other_equals_specification
):
    from fractal_specifications.generic.collections import OrSpecification

    return OrSpecification(
        [empty_specification, equals_specification, other_equals_specification]
    )


@pytest.fixture
def and_specification(
    empty_specification, equals_specification, other_equals_specification
):
    from fractal_specifications.generic.collections import AndSpecification

    return AndSpecification(
        [empty_specification, equals_specification, other_equals_specification]
    )


@pytest.fixture
def contains_specification():
    from fractal_specifications.generic.operators import ContainsSpecification

    return ContainsSpecification("field", "test")


@pytest.fixture
def in_specification():
    from fractal_specifications.generic.operators import InSpecification

    return InSpecification("field", [1, 2, 3])


@pytest.fixture
def in_empty_specification():
    from fractal_specifications.generic.operators import InSpecification

    return InSpecification("field", [])


@pytest.fixture
def less_than_specification():
    from fractal_specifications.generic.operators import LessThanSpecification

    return LessThanSpecification("id", 1)


@pytest.fixture
def less_than_equal_specification():
    from fractal_specifications.generic.operators import LessThanEqualSpecification

    return LessThanEqualSpecification("id", 1)


@pytest.fixture
def greater_than_specification():
    from fractal_specifications.generic.operators import GreaterThanSpecification

    return GreaterThanSpecification("id", 1)


@pytest.fixture
def greater_than_equal_specification():
    from fractal_specifications.generic.operators import GreaterThanEqualSpecification

    return GreaterThanEqualSpecification("id", 1)


@pytest.fixture
def regex_string_match_specification():
    from fractal_specifications.generic.operators import RegexStringMatchSpecification

    return RegexStringMatchSpecification("id", "abc")


@pytest.fixture
def is_none_specification():
    from fractal_specifications.generic.operators import IsNoneSpecification

    return IsNoneSpecification("field")


@pytest.fixture
def dict_specification():
    from fractal_specifications.generic.specification import Specification

    class DictSpecification(Specification):
        def __init__(self, collection):
            self.collection = collection

        def is_satisfied_by(self, obj) -> bool:
            raise NotImplementedError

        def to_collection(self) -> dict:
            return self.collection

    return DictSpecification({"id": 1, "test": 2})


@pytest.fixture
def empty_specification():
    from fractal_specifications.generic.specification import EmptySpecification

    return EmptySpecification()


@pytest.fixture
def complex_specification():
    from fractal_specifications.generic import operators
    from fractal_specifications.generic.specification import EmptySpecification

    return (
        operators.EqualsSpecification("id", 1)
        & operators.EqualsSpecification("id", 1.5)
        & operators.EqualsSpecification("id", False)
        & operators.EqualsSpecification("id", True)
        & operators.EqualsSpecification("id", None)
        & operators.GreaterThanSpecification("price", 25)
        & operators.GreaterThanEqualSpecification("price", 25)
        & operators.LessThanSpecification("price", 25)
        & operators.LessThanEqualSpecification("price", 25)
        & operators.NotSpecification(operators.IsNoneSpecification("name"))
        & operators.ContainsSpecification("field", "y")
        | operators.NotEqualsSpecification("id", 1)
        & operators.InSpecification("field", [1, 2, 3])
        & operators.RegexStringMatchSpecification("field", ".*abc.*")
        | (EmptySpecification() & EmptySpecification())
    )
