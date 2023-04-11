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
            "!=": operators.NotEqualsSpecification,
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
        return all_specifications()["eq"](field_op, value)

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

    def dumps(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def loads(s: str) -> Specification:
        return Specification.from_dict(json.loads(s))

    @classmethod
    def name(cls) -> str:
        return cls.__name__[:-13].lower()  # -Specification

    def dump_dsl(self) -> Optional[str]:
        from fractal_specifications.generic import collections, operators

        if isinstance(self, operators.NotSpecification):
            child = self.specification.dump_dsl()
            return f"!({child})"
        elif isinstance(self, operators.FieldValueSpecification):
            lhs = self.field
            operator = {
                operators.EqualsSpecification.__name__: "==",
                operators.NotEqualsSpecification.__name__: "!=",
                operators.GreaterThanSpecification.__name__: ">",
                operators.GreaterThanEqualSpecification.__name__: ">=",
                operators.LessThanSpecification.__name__: "<",
                operators.LessThanEqualSpecification.__name__: "<=",
                operators.InSpecification.__name__: "in",
                operators.ContainsSpecification.__name__: "contains",
                operators.IsNoneSpecification.__name__: "is None",
                operators.RegexStringMatchSpecification.__name__: "matches",
            }[self.__class__.__name__]
            if isinstance(self, operators.IsNoneSpecification):
                return f"{lhs} {operator}"
            rhs = f'"{self.value}"' if type(self.value) == str else repr(self.value)
            return f"{lhs} {operator} {rhs}"
        elif isinstance(
            self, (collections.AndSpecification, collections.OrSpecification)
        ):
            op = {
                collections.AndSpecification: " && ",
                collections.OrSpecification: " || ",
            }[type(self)]
            child_strings = [
                val for child in self.specifications if (val := child.dump_dsl())
            ]
            if child_strings:
                return f"({op.join(child_strings)})"
        elif isinstance(self, EmptySpecification):
            return "#"
        raise ValueError(f"Unsupported specification type: {type(self)}")

    @staticmethod
    def load_dsl(dsl_string) -> Specification:
        from lark import Lark

        from fractal_specifications.generic.dsl_parser import DSLTransformer, grammar

        dsl_parser = Lark(grammar, start="start", parser="lalr")
        transformer = DSLTransformer()
        tree = dsl_parser.parse(dsl_string)
        return transformer.transform(tree)


class EmptySpecification(Specification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return True

    def to_collection(self) -> Collection:
        return []

    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return isinstance(other, EmptySpecification)
