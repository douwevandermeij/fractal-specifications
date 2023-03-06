from typing import Any, Collection

import pandas as pd  # type: ignore
import pytest  # type: ignore

df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "name": [2, 3, 4, 5],
        "field": [3, 4, 5, 6],
    }
)

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), (df.id == 1).all()),  # type: ignore
    (
        pytest.lazy_fixture("or_specification"),  # type: ignore
        (df.id == 1).all() | (df.name == "test").all(),
    ),
    (
        pytest.lazy_fixture("and_specification"),  # type: ignore
        (df.id == 1).all() & (df.name == "test").all(),
    ),
    (pytest.lazy_fixture("in_specification"), (df.id.isin([1, 2, 3])).all()),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), (df.id < 1).all()),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), (df.id <= 1).all()),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), (df.id > 1).all()),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), (df.id >= 1).all()),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.pandas.specifications import (
        PandasSpecificationBuilder,
    )

    f = PandasSpecificationBuilder.build(specification)

    assert f == expected or f(df).all() == expected


def test_specification_not_mapped():
    from fractal_specifications.contrib.pandas.specifications import (
        PandasSpecificationBuilder,
        SpecificationNotMappedToPandas,
    )
    from fractal_specifications.generic.specification import Specification

    class ErrorSpecification(Specification):
        def is_satisfied_by(self, obj: Any) -> bool:
            return False

        def to_collection(self) -> Collection:
            return []

        def __str__(self):
            return self.__class__.__name__

    with pytest.raises(SpecificationNotMappedToPandas):
        PandasSpecificationBuilder.build(ErrorSpecification())
