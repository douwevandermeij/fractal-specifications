import re
from functools import reduce
from typing import Callable, Dict, Iterator, Optional, Type

from django.db.models import Q  # type: ignore

from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


class SpecificationNotMappedToDjangoOrm(Exception):
    pass


class DjangoOrmSpecificationBuilder:
    @classmethod
    def build(
        cls,
        specification: Optional[Specification] = None,
    ) -> Optional[Q]:
        if specification is None:
            return None
        elif isinstance(specification, EmptySpecification):
            return None
        if builder := cls._spec_builders().get(type(specification)):
            return cls._create_q(builder(specification))
        elif isinstance(specification.to_collection(), dict):
            return cls._create_q(specification.to_collection())
        raise SpecificationNotMappedToDjangoOrm(
            f"Specification '{specification}' not mapped to Django Orm query."
        )

    @classmethod
    def _spec_builders(cls) -> Dict[Type[Specification], Callable]:
        from fractal_specifications.generic import collections, operators

        return {
            collections.AndSpecification: lambda s: reduce(
                lambda x, y: x & y, cls._build_collection(s)
            ),
            collections.OrSpecification: lambda s: reduce(
                lambda x, y: x | y, cls._build_collection(s)
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
            operators.IsNoneSpecification: lambda s: {f"{s.field}__isnull": True},
        }

    @classmethod
    def _build_collection(cls, specification) -> Iterator[Q]:
        for spec in specification.to_collection():
            if s := cls._create_q(cls.build(spec)):
                yield s

    @staticmethod
    def _create_q(filters) -> Q:
        if type(filters) is dict:
            return Q(**filters)
        elif type(filters) in {list, set, tuple}:
            return Q(*filters)
        return filters
