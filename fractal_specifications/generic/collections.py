from abc import abstractmethod
from typing import Any, Collection, List

from fractal_specifications.generic.specification import Specification


class CollectionSpecification(Specification):
    def __init__(self, specifications: List[Specification]):
        self.specifications = specifications

    @abstractmethod
    def is_satisfied_by(self, obj: Any) -> bool:
        raise NotImplementedError

    def to_collection(self) -> Collection:
        return self.specifications

    def __str__(self):
        return f"{self.__class__.__name__}({','.join(map(lambda s: str(s), self.specifications))})"

    def __eq__(self, other):
        return type(self) is type(other) and self.specifications == other.specifications

    def __hash__(self):
        return hash(tuple(self.specifications))

    def to_dict(self):
        return {
            "op": self.name(),
            "specs": [spec.to_dict() for spec in self.specifications],
        }

    @classmethod
    def _from_dict(cls, d: dict):
        return cls(specifications=[Specification.from_dict(s) for s in d["specs"]])


class AndSpecification(CollectionSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return all([spec.is_satisfied_by(obj) for spec in self.specifications])

    def And(self, specification: Specification) -> Specification:
        if isinstance(specification, AndSpecification):
            return AndSpecification(self.specifications + specification.specifications)
        else:
            return AndSpecification(self.specifications + [specification])


class OrSpecification(CollectionSpecification):
    def is_satisfied_by(self, obj: Any) -> bool:
        return any([spec.is_satisfied_by(obj) for spec in self.specifications])

    def Or(self, specification: Specification) -> Specification:
        if isinstance(specification, OrSpecification):
            return OrSpecification(self.specifications + specification.specifications)
        else:
            return OrSpecification(self.specifications + [specification])
