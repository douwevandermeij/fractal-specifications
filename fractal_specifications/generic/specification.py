from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Collection, Iterator, Optional


class Operators(str, Enum):
    EQUALS = "equals"
    IN = "in"
    CONTAINS = "contains"
    LESS_THAN = "lt"
    LESS_THAN_EQUAL = "lte"
    GREATER_THAN = "gt"
    GREATER_THAN_EQUAL = "gte"


def get_op_specs():
    from fractal_specifications.generic import operators

    return {
        Operators.EQUALS: operators.EqualsSpecification,
        Operators.IN: operators.InSpecification,
        Operators.CONTAINS: operators.ContainsSpecification,
        Operators.LESS_THAN: operators.LessThanSpecification,
        Operators.LESS_THAN_EQUAL: operators.LessThanEqualSpecification,
        Operators.GREATER_THAN: operators.GreaterThanSpecification,
        Operators.GREATER_THAN_EQUAL: operators.GreaterThanEqualSpecification,
    }


def _parse_specification_item(field_op: str, value: Any) -> Optional[Specification]:
    if "__" not in field_op:
        return get_op_specs()[Operators.EQUALS](field_op, value)

    field, operator = field_op.split("__")
    for op, spec in get_op_specs().items():
        if op == operator:
            return spec(field, value)
    return None


def parse_specification(**kwargs) -> Iterator[Specification]:
    for field_op, value in kwargs.items():
        if spec := _parse_specification_item(field_op, value):
            yield spec


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_collection(self) -> Collection:
        raise NotImplementedError

    def And(self, specification: "Specification") -> "Specification":
        from fractal_specifications.generic.collections import AndSpecification

        if isinstance(specification, AndSpecification):
            return specification.And(self)
        return AndSpecification([self, specification])

    def Or(self, specification: "Specification") -> "Specification":
        from fractal_specifications.generic.collections import OrSpecification

        if isinstance(specification, OrSpecification):
            return specification.Or(self)
        return OrSpecification([self, specification])

    def __str__(self):
        raise NotImplementedError

    @staticmethod
    def Not(specification: "Specification") -> "Specification":
        from fractal_specifications.generic.operators import NotSpecification

        return NotSpecification(specification)

    @staticmethod
    def parse(**kwargs):
        specs = list(parse_specification(**kwargs))
        if len(specs) > 1:
            from fractal_specifications.generic.collections import AndSpecification

            return AndSpecification(specs)
        elif len(specs) == 1:
            return specs[0]
        return None
