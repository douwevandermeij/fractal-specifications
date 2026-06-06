from typing import Dict, List, Optional, Tuple, cast

from fractal_specifications.generic.collections import (
    AndSpecification,
    OrSpecification,
)
from fractal_specifications.generic.operators import (
    EqualsSpecification,
    FieldValueSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotEqualsSpecification,
)
from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


class SpecificationNotMappedToSqlite(Exception):
    """Raised when a specification cannot be translated to a SQLite WHERE clause.

    Callers that store entities as JSON documents typically catch this and fall
    back to evaluating the specification in Python, so an unmapped specification
    only loses the pushdown optimisation — it never produces a wrong result.
    """


# Values that round-trip losslessly to JSON and that ``json_extract`` returns
# unchanged. For these, a SQL comparison is *exactly* equivalent to evaluating
# ``Specification.is_satisfied_by`` over the deserialised entity. Other types
# (Decimal, date, datetime, UUID, Enum) are commonly stored as strings and would
# compare differently in SQL than in Python, so specifications referencing them
# are reported as unmapped for the caller to evaluate in Python.
_NATIVE_TYPES = (str, int, float, bool)


def _is_native(value) -> bool:
    return value is None or isinstance(value, _NATIVE_TYPES)


def _field_path(field: str) -> str:
    """Translate a field to a JSON path: ``a__b`` / ``a.b`` -> ``$.a.b``."""
    return "$." + field.replace("__", ".")


class SqliteSpecificationBuilder:
    """Translate a ``Specification`` into a SQLite WHERE clause over a JSON column.

    Fields are read with ``json_extract(data, ?)`` (the JSON path is bound as a
    parameter, so field names are never interpolated into SQL). This targets the
    common SQLite pattern of storing each record as a JSON document in a ``data``
    column, which needs no per-field schema.

    Only specifications that translate to something *exactly* equivalent to
    Python-side filtering are mapped; anything else raises
    ``SpecificationNotMappedToSqlite`` so the caller can fall back to Python.
    """

    @staticmethod
    def build(specification: Optional[Specification] = None) -> Tuple[str, List]:
        if specification is None:
            return "1 = 1", []
        return SqliteSpecificationBuilder._build_spec(specification)

    @staticmethod
    def _build_spec(specification: Specification) -> Tuple[str, List]:
        if isinstance(specification, EmptySpecification):
            return "1 = 1", []

        if isinstance(specification, (AndSpecification, OrSpecification)):
            joiner = " AND " if isinstance(specification, AndSpecification) else " OR "
            clauses: List[str] = []
            params: List = []
            for spec in specification.to_collection():
                if isinstance(spec, EmptySpecification):
                    continue
                clause, spec_params = SqliteSpecificationBuilder._build_spec(spec)
                clauses.append(f"({clause})")
                params.extend(spec_params)
            if not clauses:
                return "1 = 1", []
            return joiner.join(clauses), params

        if isinstance(specification, IsNoneSpecification):
            return "json_extract(data, ?) IS NULL", [_field_path(specification.field)]

        if isinstance(specification, InSpecification):
            values = list(specification.value)
            if not all(_is_native(v) for v in values):
                raise SpecificationNotMappedToSqlite(
                    f"Non-native value in IN specification: {specification}"
                )
            path = _field_path(specification.field)
            if not values:
                return "0 = 1", []  # `x IN ()` matches nothing, like Python
            placeholders = ", ".join("?" for _ in values)
            return f"json_extract(data, ?) IN ({placeholders})", [path, *values]

        if isinstance(specification, NotEqualsSpecification):
            if not _is_native(specification.value):
                raise SpecificationNotMappedToSqlite(
                    f"Non-native value in specification: {specification}"
                )
            path = _field_path(specification.field)
            if specification.value is None:
                # Python: ``field != None`` is True for any non-null value.
                return "json_extract(data, ?) IS NOT NULL", [path]
            # Python includes rows whose field is None (None != value); SQL's
            # ``NULL <> value`` is NULL (excluded), so make the null case explicit.
            return (
                "(json_extract(data, ?) IS NULL OR json_extract(data, ?) <> ?)",
                [path, path, specification.value],
            )

        comparison_ops: Dict[type, str] = {
            EqualsSpecification: "=",
            LessThanSpecification: "<",
            LessThanEqualSpecification: "<=",
            GreaterThanSpecification: ">",
            GreaterThanEqualSpecification: ">=",
        }
        # Exact-type match (not isinstance) so a subclass we don't recognise
        # cannot be silently mistranslated through its parent's operator.
        operator = comparison_ops.get(type(specification))
        if operator is not None:
            field_value = cast(FieldValueSpecification, specification)
            if not _is_native(field_value.value):
                raise SpecificationNotMappedToSqlite(
                    f"Non-native value in specification: {specification}"
                )
            path = _field_path(field_value.field)
            return f"json_extract(data, ?) {operator} ?", [path, field_value.value]

        raise SpecificationNotMappedToSqlite(
            f"Specification '{specification}' ({type(specification).__name__}) "
            "not mapped to SQLite"
        )
