import re
from typing import Collection, Optional

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotEqualsSpecification,
    RegexStringMatchSpecification,
)
from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


class SpecificationNotMappedToMongo(Exception):
    pass


class MongoSpecificationBuilder:
    @staticmethod
    def build(specification: Optional[Specification] = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, EmptySpecification):
            return None
        elif isinstance(specification, AndSpecification):
            specs = [
                s
                for spec in specification.to_collection()
                if (s := MongoSpecificationBuilder.build(spec))
            ]
            return {"$and": specs} if specs else None
        elif isinstance(specification, OrSpecification):
            specs = [
                s
                for spec in specification.to_collection()
                if (s := MongoSpecificationBuilder.build(spec))
            ]
            return {"$or": specs} if specs else None
        elif isinstance(specification, InSpecification):
            return {specification.field: {"$in": specification.value}}
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: {"$eq": specification.value}}
        elif isinstance(specification, NotEqualsSpecification):
            return {specification.field: {"$ne": specification.value}}
        elif isinstance(specification, IsNoneSpecification):
            return {specification.field: {"$eq": None}}
        elif isinstance(specification, LessThanSpecification):
            return {specification.field: {"$lt": specification.value}}
        elif isinstance(specification, LessThanEqualSpecification):
            return {specification.field: {"$lte": specification.value}}
        elif isinstance(specification, GreaterThanSpecification):
            return {specification.field: {"$gt": specification.value}}
        elif isinstance(specification, GreaterThanEqualSpecification):
            return {specification.field: {"$gte": specification.value}}
        elif isinstance(specification, RegexStringMatchSpecification):
            # RegexStringMatchSpecification expects actual regex patterns from user
            return {specification.field: {"$regex": specification.value}}
        elif isinstance(specification, ContainsSpecification):
            # ContainsSpecification checks if substring exists, so escape and add wildcards
            return {
                specification.field: {"$regex": f".*{re.escape(specification.value)}.*"}
            }
        elif isinstance(specification.to_collection(), dict):
            specs = [
                {key: {"$eq": value}}
                for key, value in dict(specification.to_collection()).items()
            ]
            return {"$and": specs} if specs else None
        raise SpecificationNotMappedToMongo(
            f"Specification '{specification}' not mapped to Mongo query."
        )
