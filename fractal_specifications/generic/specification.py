from __future__ import annotations

import json
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Collection, Iterator, Optional, Type, TypeVar


@lru_cache
def all_specifications():
    def get_subclasses(spec):
        for sub in spec.__subclasses__():
            yield sub
            for subsub in get_subclasses(sub):
                yield subsub

    from fractal_specifications.generic import collections, operators

    return {
        **{spec.name(): spec for spec in get_subclasses(Specification)},
        **{
            "==": operators.EqualsSpecification,
            "<": operators.LessThanSpecification,
            "<=": operators.LessThanEqualSpecification,
            ">": operators.GreaterThanSpecification,
            ">=": operators.GreaterThanEqualSpecification,
            "!": operators.NotSpecification,
            "&": collections.AndSpecification,
            "|": collections.OrSpecification,
        },
    }


def _parse_specification_item(field_op: str, value: Any) -> Optional[Specification]:
    if "__" not in field_op:
        return all_specifications()["equals"](field_op, value)

    field, operator = field_op.split("__")
    for op, spec in all_specifications().items():
        if op == operator:
            return spec(field, value)
    return None


def parse_specification(**kwargs) -> Iterator[Specification]:
    for field_op, value in kwargs.items():
        if spec := _parse_specification_item(field_op, value):
            yield spec


SpecificationSubType = TypeVar("SpecificationSubType", bound="Specification")


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

    def __and__(self, other):
        return self.And(other)

    def __or__(self, other):
        return self.Or(other)

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

    def to_dict(self):
        return {
            **{
                "op": self.name(),
            },
            **self.__dict__,
        }

    @classmethod
    def from_dict(cls, d: dict):
        name = d.pop("op")
        return all_specifications()[name]._from_dict(d)

    @classmethod
    def _from_dict(cls: Type[SpecificationSubType], d: dict):
        return cls(**d)

    def dumps(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def loads(s: str):
        return Specification.from_dict(json.loads(s))

    @classmethod
    def name(cls):
        return cls.__name__[:-13].lower()  # -Specification


class EmptySpecification(Specification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return True

    def to_collection(self) -> Collection:
        return []

    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return isinstance(other, EmptySpecification)
