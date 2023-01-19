import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), {"id": 1}),  # type: ignore
    (pytest.lazy_fixture("or_specification"), [{"id": 1}, {"name": "test"}]),  # type: ignore
    (pytest.lazy_fixture("and_specification"), {"id": 1, "name": "test"}),  # type: ignore
    (pytest.lazy_fixture("dict_specification"), {"id": 1, "test": 2}),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.sqlalchemy.specifications import (
        SqlAlchemyOrmSpecificationBuilder,
    )

    assert SqlAlchemyOrmSpecificationBuilder.build(specification) == expected


def test_build_error(greater_than_specification):
    from fractal_specifications.contrib.sqlalchemy.specifications import (
        SpecificationNotMappedToSqlAlchemyOrm,
        SqlAlchemyOrmSpecificationBuilder,
    )

    with pytest.raises(SpecificationNotMappedToSqlAlchemyOrm):
        SqlAlchemyOrmSpecificationBuilder.build(greater_than_specification)
