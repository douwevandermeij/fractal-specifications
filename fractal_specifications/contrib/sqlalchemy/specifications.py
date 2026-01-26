from typing import Any, Collection, Optional, cast

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


class SpecificationNotMappedToSqlAlchemyOrm(Exception):
    pass


class SqlAlchemyOrmSpecificationBuilder:
    @staticmethod
    def build(specification: Optional[Specification] = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, EmptySpecification):
            return None
        elif isinstance(specification, OrSpecification):
            return [
                s
                for spec in specification.to_collection()
                if (s := SqlAlchemyOrmSpecificationBuilder.build(spec))
            ]
        elif isinstance(specification, AndSpecification):
            results = [
                i
                for spec in specification.to_collection()
                if (i := SqlAlchemyOrmSpecificationBuilder.build(spec))
            ]
            # If all results are dicts, merge them (for filter_by usage)
            if all(isinstance(r, dict) for r in results):
                return {k: v for r in results for k, v in cast(dict[str, Any], r).items()}
            # Otherwise return as list (requires filter() usage)
            return results if results else None
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: specification.value}
        elif isinstance(specification, NotEqualsSpecification):
            # Return tuple format for != operation
            return (specification.field, "ne", specification.value)
        elif isinstance(specification, LessThanSpecification):
            # Return tuple format for < operation
            return (specification.field, "lt", specification.value)
        elif isinstance(specification, LessThanEqualSpecification):
            # Return tuple format for <= operation
            return (specification.field, "le", specification.value)
        elif isinstance(specification, GreaterThanSpecification):
            # Return tuple format for > operation
            return (specification.field, "gt", specification.value)
        elif isinstance(specification, GreaterThanEqualSpecification):
            # Return tuple format for >= operation
            return (specification.field, "ge", specification.value)
        elif isinstance(specification, IsNoneSpecification):
            # Return tuple format for IS NULL operation
            return (specification.field, "is_none", None)
        elif isinstance(specification, RegexStringMatchSpecification):
            # Return tuple format (field, operation, value) for operations that need filter()
            # Consumer should use: Model.field.op('~*')(value) for PostgreSQL
            return (specification.field, "regex", specification.value)
        elif isinstance(specification, ContainsSpecification):
            # Return tuple format (field, operation, value) for operations that need filter()
            # Consumer should use: Model.field.contains(value) or Model.field.like(f'%{value}%')
            return (specification.field, "contains", specification.value)
        elif isinstance(specification, InSpecification):
            # Return tuple format for IN operation
            return (specification.field, "in", specification.value)
        elif isinstance(specification.to_collection(), dict):
            return specification.to_collection()
        raise SpecificationNotMappedToSqlAlchemyOrm(
            f"Specification '{specification}' not mapped to SqlAlchemy Orm query."
        )
