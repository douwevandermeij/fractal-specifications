from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Collection, Iterator, Optional


def _parse_specification_item(field_op: str, value: Any) -> Optional[Specification]:
    if "__" not in field_op:
        from fractal_specifications.generic.operators import EqualsSpecification

        return EqualsSpecification(field_op, value)
    else:
        field, op = field_op.split("__")
        if op == "equals":
            from fractal_specifications.generic.operators import EqualsSpecification

            return EqualsSpecification(field, value)
        elif op == "in":
            from fractal_specifications.generic.operators import InSpecification

            return InSpecification(field, value)
        elif op == "contains":
            from fractal_specifications.generic.operators import ContainsSpecification

            return ContainsSpecification(field, value)
        elif op == "lt":
            from fractal_specifications.generic.operators import LessThanSpecification

            return LessThanSpecification(field, value)
        elif op == "lte":
            from fractal_specifications.generic.operators import (
                LessThanEqualSpecification,
            )

            return LessThanEqualSpecification(field, value)
        elif op == "gt":
            from fractal_specifications.generic.operators import (
                GreaterThanSpecification,
            )

            return GreaterThanSpecification(field, value)
        elif op == "gte":
            from fractal_specifications.generic.operators import (
                GreaterThanEqualSpecification,
            )

            return GreaterThanEqualSpecification(field, value)
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
