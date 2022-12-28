from typing import Collection, Optional

from fractal_specifications.generic.collections import AndSpecification
from fractal_specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
)
from fractal_specifications.generic.specification import Specification


class SpecificationNotMappedToFirestore(Exception):
    ...


class FirestoreSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, AndSpecification):
            return [
                FirestoreSpecificationBuilder.build(spec)
                for spec in specification.to_collection()
            ]
        elif isinstance(specification, ContainsSpecification):
            return specification.field, "array-contains", specification.value
        elif isinstance(specification, InSpecification):
            if not specification.value:
                return None
            return specification.field, "in", specification.value
        elif isinstance(specification, EqualsSpecification):
            return specification.field, "==", specification.value
        elif isinstance(specification, LessThanSpecification):
            return specification.field, "<", specification.value
        elif isinstance(specification, LessThanEqualSpecification):
            return specification.field, "<=", specification.value
        elif isinstance(specification, GreaterThanSpecification):
            return specification.field, ">", specification.value
        elif isinstance(specification, GreaterThanEqualSpecification):
            return specification.field, ">=", specification.value
        elif isinstance(specification.to_collection(), dict):
            return [
                (key, "==", value)
                for key, value in dict(specification.to_collection()).items()
            ]
        raise SpecificationNotMappedToFirestore(
            f"Specification '{specification}' not mapped to Firestore query."
        )
