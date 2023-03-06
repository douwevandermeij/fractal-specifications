from typing import Any, Collection

import pandas as pd  # type: ignore
import pytest  # type: ignore

df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "name": ["test", "test", "test", "test"],
        "field": [3, 4, 5, 6],
    }
)

dfi = df.set_index(["id", "name", "field"])

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), df[df.id == 1].to_dict()),  # type: ignore
    (
        pytest.lazy_fixture("or_specification"),  # type: ignore
        (df[(df.id == 1) | (df.name == "test")]).to_dict(),
    ),
    (
        pytest.lazy_fixture("and_specification"),  # type: ignore
        (df[(df.id == 1) & (df.name == "test")]).to_dict(),
    ),
    (pytest.lazy_fixture("in_specification"), df[df.field.isin([1, 2, 3])].to_dict()),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), df[df.id < 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), df[df.id <= 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), df[df.id > 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), df[df.id >= 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]

specifications_index = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), dfi[dfi.index.get_level_values("id") == 1].to_dict()),  # type: ignore
    (
        pytest.lazy_fixture("or_specification"),  # type: ignore
        (
            dfi[
                (dfi.index.get_level_values("id") == 1)
                | (dfi.index.get_level_values("name") == "test")
            ]
        ).to_dict(),
    ),
    (
        pytest.lazy_fixture("and_specification"),  # type: ignore
        (
            dfi[
                (dfi.index.get_level_values("id") == 1)
                & (dfi.index.get_level_values("name") == "test")
            ]
        ).to_dict(),
    ),
    (pytest.lazy_fixture("in_specification"), dfi[dfi.index.get_level_values("field").isin([1, 2, 3])].to_dict()),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), dfi[dfi.index.get_level_values("id") < 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), dfi[dfi.index.get_level_values("id") <= 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), dfi[dfi.index.get_level_values("id") > 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), dfi[dfi.index.get_level_values("id") >= 1].to_dict()),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.pandas.specifications import (
        PandasSpecificationBuilder,
    )

    f = PandasSpecificationBuilder.build(specification)

    assert f == expected or f(df).to_dict() == expected


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


@pytest.mark.parametrize("specification, expected", specifications_index)
def test_build_with_index(specification, expected):
    from fractal_specifications.contrib.pandas.specifications import (
        PandasIndexSpecificationBuilder,
    )

    f = PandasIndexSpecificationBuilder.build(specification)

    assert f == expected or f(dfi).to_dict() == expected


def test_specification_not_mapped_with_index():
    from fractal_specifications.contrib.pandas.specifications import (
        PandasIndexSpecificationBuilder,
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
        PandasIndexSpecificationBuilder.build(ErrorSpecification())
