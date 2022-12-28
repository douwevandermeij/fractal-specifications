from typing import Collection, Optional

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import EqualsSpecification
from fractal_specifications.generic.specification import Specification


class SpecificationNotMappedToSqlAlchemyOrm(Exception):
    ...


class SqlAlchemyOrmSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Collection]:
        if specification is None:
            return None
        elif isinstance(specification, OrSpecification):
            return [
                SqlAlchemyOrmSpecificationBuilder.build(spec)
                for spec in specification.to_collection()
            ]
        elif isinstance(specification, AndSpecification):
            return {
                k: v
                for spec in specification.to_collection()
                if (i := SqlAlchemyOrmSpecificationBuilder.build(spec))
                for k, v in dict(i).items()
                if isinstance(i, dict)
            }
        elif isinstance(specification, EqualsSpecification):
            return {specification.field: specification.value}
        elif isinstance(specification.to_collection(), dict):
            return specification.to_collection()
        raise SpecificationNotMappedToSqlAlchemyOrm(
            f"Specification '{specification}' not mapped to SqlAlchemy Orm query."
        )
