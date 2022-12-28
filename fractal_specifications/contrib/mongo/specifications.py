import re
from typing import Collection, Optional

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import (
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    RegexStringMatchSpecification,
)
from fractal_specifications.generic.specification import Specification


class SpecificationNotMappedToMongo(Exception):
    ...


class MongoSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, AndSpecification):
            return {
                "$and": [
                    MongoSpecificationBuilder.build(spec)
                    for spec in specification.to_collection()
                ]
            }
        elif isinstance(specification, OrSpecification):
            return {
                "$or": [
                    MongoSpecificationBuilder.build(spec)
                    for spec in specification.to_collection()
                ]
            }
        elif isinstance(specification, InSpecification):
            return {specification.field: {"$in": specification.value}}
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: {"$eq": specification.value}}
        elif isinstance(specification, LessThanSpecification):
            return {specification.field: {"$lt": specification.value}}
        elif isinstance(specification, LessThanEqualSpecification):
            return {specification.field: {"$lte": specification.value}}
        elif isinstance(specification, GreaterThanSpecification):
            return {specification.field: {"$gt": specification.value}}
        elif isinstance(specification, GreaterThanEqualSpecification):
            return {specification.field: {"$gte": specification.value}}
        elif isinstance(specification, RegexStringMatchSpecification):
            return {
                specification.field: {"$regex": f".*{re.escape(specification.value)}.*"}
            }
        elif isinstance(specification.to_collection(), dict):
            return {
                "$and": [
                    {key: {"$eq": value}}
                    for key, value in dict(specification.to_collection()).items()
                ]
            }
        raise SpecificationNotMappedToMongo(
            f"Specification '{specification}' not mapped to Mongo query."
        )
