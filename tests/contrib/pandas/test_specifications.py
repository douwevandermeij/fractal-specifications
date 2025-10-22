from typing import Any, Collection

import pandas as pd  # type: ignore
import pytest  # type: ignore

from fractal_specifications.contrib.pandas.specifications import (
    PandasIndexSpecificationBuilder,
    PandasSpecificationBuilder,
    SpecificationNotMappedToPandas,
)

df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "name": ["test", "test", "test", "test"],
        "field": [3, 4, 5, 6],
    }
)

dfi = df.set_index(["id", "name", "field"])


def test_build_none():
    assert PandasSpecificationBuilder.build(None) is None


def test_build_equals_specification(equals_specification):
    assert (
        PandasSpecificationBuilder.build(equals_specification)(df).to_dict()
        == df[df.id == 1].to_dict()
    )


def test_build_or_specification(or_specification):
    assert (
        PandasSpecificationBuilder.build(or_specification)(df).to_dict()
        == (df[(df.id == 1) | (df.name == "test")]).to_dict()
    )


def test_build_and_specification(and_specification):
    assert (
        PandasSpecificationBuilder.build(and_specification)(df).to_dict()
        == (df[(df.id == 1) & (df.name == "test")]).to_dict()
    )


def test_build_contains_specification(contains_specification):
    with pytest.raises(SpecificationNotMappedToPandas):
        PandasSpecificationBuilder.build(contains_specification)


def test_build_in_specification(in_specification):
    assert (
        PandasSpecificationBuilder.build(in_specification)(df).to_dict()
        == df[df.field.isin([1, 2, 3])].to_dict()
    )


def test_build_in_empty_specification(in_empty_specification):
    assert (
        PandasSpecificationBuilder.build(in_empty_specification)(df).to_dict()
        == df[df.field.isin([])].to_dict()
    )


def test_build_less_than_specification(less_than_specification):
    assert (
        PandasSpecificationBuilder.build(less_than_specification)(df).to_dict()
        == df[df.id < 1].to_dict()
    )


def test_build_less_than_equal_specification(less_than_equal_specification):
    assert (
        PandasSpecificationBuilder.build(less_than_equal_specification)(df).to_dict()
        == df[df.id <= 1].to_dict()
    )


def test_build_greater_than_specification(greater_than_specification):
    assert (
        PandasSpecificationBuilder.build(greater_than_specification)(df).to_dict()
        == df[df.id > 1].to_dict()
    )


def test_build_greater_than_equal_specification(greater_than_equal_specification):
    assert (
        PandasSpecificationBuilder.build(greater_than_equal_specification)(df).to_dict()
        == df[df.id >= 1].to_dict()
    )


def test_build_regex_string_match_specification(regex_string_match_specification):
    with pytest.raises(SpecificationNotMappedToPandas):
        PandasSpecificationBuilder.build(regex_string_match_specification)


def test_build_is_none_specification(is_none_specification):
    assert PandasSpecificationBuilder.build(is_none_specification)(df).to_dict() == {
        "field": {},
        "id": {},
        "name": {},
    }


def test_build_dict_specification(dict_specification):
    with pytest.raises(SpecificationNotMappedToPandas):
        PandasSpecificationBuilder.build(dict_specification)


def test_build_empty_specification(empty_specification):
    assert PandasSpecificationBuilder.build(empty_specification) is None


def test_specification_not_mapped():
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


def test_build_with_index_none():
    assert PandasIndexSpecificationBuilder.build(None) is None


def test_build_with_index_equals_specification(equals_specification):
    assert (
        PandasIndexSpecificationBuilder.build(equals_specification)(dfi).to_dict()
        == dfi[dfi.index.get_level_values("id") == 1].to_dict()
    )


def test_build_with_index_or_specification(or_specification):
    assert (
        PandasIndexSpecificationBuilder.build(or_specification)(dfi).to_dict()
        == (
            dfi[
                (dfi.index.get_level_values("id") == 1)
                | (dfi.index.get_level_values("name") == "test")
            ]
        ).to_dict()
    )


def test_build_with_index_and_specification(and_specification):
    assert (
        PandasIndexSpecificationBuilder.build(and_specification)(dfi).to_dict()
        == (
            dfi[
                (dfi.index.get_level_values("id") == 1)
                & (dfi.index.get_level_values("name") == "test")
            ]
        ).to_dict()
    )


def test_build_with_index_contains_specification(contains_specification):
    with pytest.raises(SpecificationNotMappedToPandas):
        PandasIndexSpecificationBuilder.build(contains_specification)


def test_build_with_index_in_specification(in_specification):
    assert (
        PandasIndexSpecificationBuilder.build(in_specification)(dfi).to_dict()
        == dfi[dfi.index.get_level_values("field").isin([1, 2, 3])].to_dict()
    )


def test_build_with_index_in_empty_specification(in_empty_specification):
    assert (
        PandasIndexSpecificationBuilder.build(in_empty_specification)(dfi).to_dict()
        == dfi[dfi.index.get_level_values("field").isin([])].to_dict()
    )


def test_build_with_index_less_than_specification(less_than_specification):
    assert (
        PandasIndexSpecificationBuilder.build(less_than_specification)(dfi).to_dict()
        == dfi[dfi.index.get_level_values("id") < 1].to_dict()
    )


def test_build_with_index_less_than_equal_specification(less_than_equal_specification):
    assert (
        PandasIndexSpecificationBuilder.build(less_than_equal_specification)(
            dfi
        ).to_dict()
        == dfi[dfi.index.get_level_values("id") <= 1].to_dict()
    )


def test_build_with_index_greater_than_specification(greater_than_specification):
    assert (
        PandasIndexSpecificationBuilder.build(greater_than_specification)(dfi).to_dict()
        == dfi[dfi.index.get_level_values("id") > 1].to_dict()
    )


def test_build_with_index_greater_than_equal_specification(
    greater_than_equal_specification,
):
    assert (
        PandasIndexSpecificationBuilder.build(greater_than_equal_specification)(
            dfi
        ).to_dict()
        == dfi[dfi.index.get_level_values("id") >= 1].to_dict()
    )


def test_build_with_index_regex_string_match_specification(
    regex_string_match_specification,
):
    with pytest.raises(SpecificationNotMappedToPandas):
        PandasIndexSpecificationBuilder.build(regex_string_match_specification)


def test_build_with_index_is_none_specification(is_none_specification):
    assert (
        PandasIndexSpecificationBuilder.build(is_none_specification)(dfi).to_dict()
        == {}
    )


def test_build_with_index_dict_specification(dict_specification):
    with pytest.raises(SpecificationNotMappedToPandas):
        PandasIndexSpecificationBuilder.build(dict_specification)


def test_build_with_index_empty_specification(empty_specification):
    assert PandasIndexSpecificationBuilder.build(empty_specification) is None


def test_specification_not_mapped_with_index():
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
