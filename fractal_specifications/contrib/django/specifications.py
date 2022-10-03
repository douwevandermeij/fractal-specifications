import re
from functools import reduce
from typing import Callable, Collection, Dict, Iterator, Optional, Type, Union

from django.db.models import Q  # type: ignore

from fractal_specifications.generic.specification import Specification


class SpecificationNotMappedToDjangoOrm(Exception):
    ...


class DjangoOrmSpecificationBuilder:
    @staticmethod
    def build(specification: Specification = None) -> Optional[Union[Collection, Q]]:
        if specification is None:
            return None
        if builder := DjangoOrmSpecificationBuilder._spec_builders().get(
            type(specification)
        ):
            return builder(specification)
        elif isinstance(specification.to_collection(), dict):
            return specification.to_collection()
        raise SpecificationNotMappedToDjangoOrm(
            f"Specification '{specification}' not mapped to Django Orm query."
        )

    @staticmethod
    def _spec_builders() -> Dict[Type[Specification], Callable]:
        from fractal_specifications.generic import collections, operators

        return {
            collections.AndSpecification: lambda s: reduce(
                lambda x, y: x & y, DjangoOrmSpecificationBuilder._build_collection(s)
            ),
            collections.OrSpecification: lambda s: reduce(
                lambda x, y: x | y, DjangoOrmSpecificationBuilder._build_collection(s)
            ),
            operators.EqualsSpecification: lambda s: {s.field: s.value},
            operators.InSpecification: lambda s: {f"{s.field}__in": s.value},
            operators.LessThanSpecification: lambda s: {f"{s.field}__lt": s.value},
            operators.LessThanEqualSpecification: lambda s: {
                f"{s.field}__lte": s.value
            },
            operators.GreaterThanSpecification: lambda s: {f"{s.field}__gt": s.value},
            operators.GreaterThanEqualSpecification: lambda s: {
                f"{s.field}__gte": s.value
            },
            operators.RegexStringMatchSpecification: lambda s: {
                f"{s.field}__regex": rf".*{re.escape(s.value)}.*"
            },
        }

    @staticmethod
    def _build_collection(specification) -> Iterator[Q]:
        for spec in specification.to_collection():
            yield DjangoOrmSpecificationBuilder._create_q(
                DjangoOrmSpecificationBuilder.build(spec)
            )

    @staticmethod
    def _create_q(filters) -> Q:
        if type(filters) is list:
            return Q(*filters)
        elif type(filters) is dict:
            return Q(**filters)
