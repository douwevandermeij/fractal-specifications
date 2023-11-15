from typing import Any, Collection, List

from fractal_specifications.generic.specification import Specification


class NotSpecification(Specification):
    def __init__(self, specification: Specification):
        self.specification = specification

    def is_satisfied_by(self, obj: Any) -> bool:
        return not self.specification.is_satisfied_by(obj)

    def to_collection(self) -> Collection:
        return [self.specification]

    def __str__(self):
        return f"{self.__class__.__name__}({self.specification})"

    def __eq__(self, other):
        return (
            isinstance(other, NotSpecification)
            and self.specification == other.specification
        )

    def __hash__(self):
        return hash(self.specification)

    def to_dict(self):
        return {
            "op": self.name(),
            "spec": self.specification.to_dict(),
        }

    @classmethod
    def _from_dict(cls, d: dict):
        return cls(specification=Specification.from_dict(d["spec"]))


class FieldValueSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.field}={self.value})"

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.field == other.field
            and self.value == other.value
        )

    def __hash__(self):
        return hash((self.field, self.value))

    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    def to_collection(self) -> Collection:
        return {self.field, self.value}


def _get_value(obj: Any, field: str) -> Any:
    for f in field.split("."):
        obj = getattr(obj, f)
    return obj


class InSpecification(FieldValueSpecification):
    def __init__(self, field: str, values: List[Any]):
        super(InSpecification, self).__init__(field, values)

    def __hash__(self):
        return hash((self.field, tuple(self.value)))

    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) in self.value

    @classmethod
    def _from_dict(cls, d: dict):
        return cls(field=d["field"], values=d["value"])


class EqualsSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) == self.value

    @classmethod
    def name(cls):
        return "eq"


class NotEqualsSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) != self.value

    @classmethod
    def name(cls):
        return "neq"


class LessThanSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) < self.value

    @classmethod
    def name(cls):
        return "lt"


class LessThanEqualSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) <= self.value

    @classmethod
    def name(cls):
        return "lte"


class GreaterThanSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) > self.value

    @classmethod
    def name(cls):
        return "gt"


class GreaterThanEqualSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) >= self.value

    @classmethod
    def name(cls):
        return "gte"


class ContainsSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return self.value in _get_value(obj, self.field)


class RegexStringMatchSpecification(ContainsSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        import re

        return bool(re.match(self.value, _get_value(obj, self.field)))

    @classmethod
    def name(cls):
        return "matches"


class IsNoneSpecification(FieldValueSpecification):
    def __init__(self, field: str):
        super(IsNoneSpecification, self).__init__(field, None)

    def __str__(self):
        return f"{self.__class__.__name__}({self.field})"

    def is_satisfied_by(self, obj: Any) -> bool:
        return _get_value(obj, self.field) is None

    @classmethod
    def _from_dict(cls, d: dict):
        return cls(field=d["field"])
