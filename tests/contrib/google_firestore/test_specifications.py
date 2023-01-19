import pytest

specifications = [
    (None, None),
    (pytest.lazy_fixture("equals_specification"), ("id", "==", 1)),  # type: ignore
    (
        pytest.lazy_fixture("and_specification"),  # type: ignore
        [("id", "==", 1), ("name", "==", "test")],
    ),
    (pytest.lazy_fixture("contains_specification"), ("field", "array-contains", "test")),  # type: ignore
    (pytest.lazy_fixture("in_specification"), ("field", "in", [1, 2, 3])),  # type: ignore
    (pytest.lazy_fixture("in_empty_specification"), None),  # type: ignore
    (pytest.lazy_fixture("less_than_specification"), ("id", "<", 1)),  # type: ignore
    (pytest.lazy_fixture("less_than_equal_specification"), ("id", "<=", 1)),  # type: ignore
    (pytest.lazy_fixture("greater_than_specification"), ("id", ">", 1)),  # type: ignore
    (pytest.lazy_fixture("greater_than_equal_specification"), ("id", ">=", 1)),  # type: ignore
    (pytest.lazy_fixture("dict_specification"), [("id", "==", 1), ("test", "==", 2)]),  # type: ignore
    (pytest.lazy_fixture("empty_specification"), None),  # type: ignore
]


@pytest.mark.parametrize("specification, expected", specifications)
def test_build(specification, expected):
    from fractal_specifications.contrib.google_firestore.specifications import (
        FirestoreSpecificationBuilder,
    )

    assert FirestoreSpecificationBuilder.build(specification) == expected


def test_build_error(or_specification):
    from fractal_specifications.contrib.google_firestore.specifications import (
        FirestoreSpecificationBuilder,
        SpecificationNotMappedToFirestore,
    )

    with pytest.raises(SpecificationNotMappedToFirestore):
        FirestoreSpecificationBuilder.build(or_specification)
