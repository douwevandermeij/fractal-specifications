from typing import Optional

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import (
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
)
from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


class SpecificationNotMappedToElastic(Exception):
    pass


class ElasticSpecificationBuilder:
    @staticmethod
    def build(specification: Optional[Specification] = None) -> Optional[dict]:
        if specification is None:
            return None
        elif isinstance(specification, EmptySpecification):
            return None
        elif isinstance(specification, AndSpecification):
            return {
                "bool": {
                    "must": [
                        s
                        for spec in specification.to_collection()
                        if (s := ElasticSpecificationBuilder.build(spec))
                    ]
                }
            }
        elif isinstance(specification, OrSpecification):
            return {
                "bool": {
                    "should": [
                        s
                        for spec in specification.to_collection()
                        if (s := ElasticSpecificationBuilder.build(spec))
                    ]
                }
            }
        elif isinstance(specification, InSpecification):
            return {
                "query_string": {
                    "default_field": specification.field,
                    "query": specification.value,
                }
            }
        elif isinstance(specification, EqualsSpecification):
            return {"match": {"%s.keyword" % specification.field: specification.value}}
        elif isinstance(specification, LessThanSpecification):
            return {
                "bool": {
                    "filter": [
                        {"range": {specification.field: {"lt": specification.value}}}
                    ]
                }
            }
        elif isinstance(specification, LessThanEqualSpecification):
            return {
                "bool": {
                    "filter": [
                        {"range": {specification.field: {"lte": specification.value}}}
                    ]
                }
            }
        elif isinstance(specification, GreaterThanSpecification):
            return {
                "bool": {
                    "filter": [
                        {"range": {specification.field: {"gt": specification.value}}}
                    ]
                }
            }
        elif isinstance(specification, GreaterThanEqualSpecification):
            return {
                "bool": {
                    "filter": [
                        {"range": {specification.field: {"gte": specification.value}}}
                    ]
                }
            }
        raise SpecificationNotMappedToElastic(
            f"Specification '{specification}' not mapped to Elastic query."
        )
