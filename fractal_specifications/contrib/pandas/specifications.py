from functools import reduce
from typing import Callable, Dict, Iterator, Optional, Type

import pandas as pd  # type: ignore

from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


class SpecificationNotMappedToPandas(Exception):
    pass


class PandasSpecificationBuilder:
    @classmethod
    def build(
        cls,
        specification: Optional[Specification] = None,
        *,
        return_mask=False,
    ) -> Optional[Callable[[pd.DataFrame], pd.Series]]:
        if specification is None or isinstance(specification, EmptySpecification):
            return None
        if builder := cls._spec_builders().get(type(specification)):
            if f := builder(specification):
                return lambda df: f(df) if return_mask else df[f(df)]
        raise SpecificationNotMappedToPandas(
            f"Specification '{specification}' not mapped to Pandas query."
        )

    @classmethod
    def _spec_builders(
        cls,
    ) -> Dict[Type[Specification], Callable]:
        from fractal_specifications.generic import collections, operators

        return {
            collections.AndSpecification: lambda s: reduce(
                lambda x, y: lambda df: x(df) & y(df), cls._build_collection(s)
            ),
            collections.OrSpecification: lambda s: reduce(
                lambda x, y: lambda df: x(df) | y(df), cls._build_collection(s)
            ),
            operators.EqualsSpecification: lambda s: lambda df: df[s.field] == s.value,
            operators.InSpecification: lambda s: lambda df: df[s.field].isin(s.value),
            operators.LessThanSpecification: lambda s: lambda df: df[s.field] < s.value,
            operators.LessThanEqualSpecification: lambda s: lambda df: df[s.field]
            <= s.value,
            operators.GreaterThanSpecification: lambda s: lambda df: df[s.field]
            > s.value,
            operators.GreaterThanEqualSpecification: lambda s: lambda df: df[s.field]
            >= s.value,
            operators.IsNoneSpecification: lambda s: lambda df: df[s.field].isna(),
        }

    @classmethod
    def _build_collection(
        cls, specification
    ) -> Iterator[Callable[[pd.DataFrame], pd.Series]]:
        for spec in specification.to_collection():
            if s := cls.build(spec, return_mask=True):
                yield s


class PandasIndexSpecificationBuilder(PandasSpecificationBuilder):
    @classmethod
    def _spec_builders(
        cls,
    ) -> Dict[Type[Specification], Callable]:
        from fractal_specifications.generic import collections, operators

        return {
            collections.AndSpecification: lambda s: reduce(
                lambda x, y: lambda df: x(df) & y(df), cls._build_collection(s)
            ),
            collections.OrSpecification: lambda s: reduce(
                lambda x, y: lambda df: x(df) | y(df), cls._build_collection(s)
            ),
            operators.EqualsSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            )
            == s.value,
            operators.InSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            ).isin(s.value),
            operators.LessThanSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            )
            < s.value,
            operators.LessThanEqualSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            )
            <= s.value,
            operators.GreaterThanSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            )
            > s.value,
            operators.GreaterThanEqualSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            )
            >= s.value,
            operators.IsNoneSpecification: lambda s: lambda df: df.index.get_level_values(
                s.field
            ).isna(),
        }
