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


class FieldValueSpecification(Specification):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.field}={self.value})"

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.field == other.field
            and self.value == other.value
        )

    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    def to_collection(self) -> Collection:
        return {self.field, self.value}


class InSpecification(FieldValueSpecification):
    def __init__(self, field: str, values: List[Any]):
        super(InSpecification, self).__init__(field, values)

    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) in self.value


class EqualsSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) == self.value


class LessThanSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) < self.value


class LessThanEqualSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) <= self.value


class GreaterThanSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) > self.value


class GreaterThanEqualSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return getattr(obj, self.field) >= self.value


class ContainsSpecification(FieldValueSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return self.value in getattr(obj, self.field)


class RegexStringMatchSpecification(ContainsSpecification):
    pass
