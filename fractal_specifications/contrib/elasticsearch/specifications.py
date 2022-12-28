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
from fractal_specifications.generic.specification import Specification


class SpecificationNotMappedToElastic(Exception):
    ...


class ElasticSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[dict]:
        if specification is None:
            return None
        elif isinstance(specification, AndSpecification):
            return {
                "bool": {
                    "must": [
                        ElasticSpecificationBuilder.build(spec)
                        for spec in specification.to_collection()
                    ]
                }
            }
        elif isinstance(specification, OrSpecification):
            return {
                "bool": {
                    "should": [
                        ElasticSpecificationBuilder.build(spec)
                        for spec in specification.to_collection()
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
