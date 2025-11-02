from typing import Optional

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotEqualsSpecification,
    RegexStringMatchSpecification,
)
from fractal_specifications.generic.specification import (
    EmptySpecification,
    Specification,
)


class SpecificationNotMappedToDuckDB(Exception):
    pass


class DuckDBSpecificationBuilder:
    @staticmethod
    def build(specification: Optional[Specification] = None) -> tuple[str, list]:
        """Build DuckDB WHERE clause and parameters from specification."""
        if specification is None:
            return "TRUE", []

        try:
            return DuckDBSpecificationBuilder._build_spec(specification)
        except Exception as e:
            raise SpecificationNotMappedToDuckDB(
                f"Specification '{specification}' not mapped to DuckDB query: {e}"
            ) from e

    @staticmethod
    def _build_spec(specification: Specification) -> tuple[str, list]:
        if isinstance(specification, EmptySpecification):
            return "TRUE", []

        elif isinstance(specification, AndSpecification):
            clauses = []
            params = []
            for spec in specification.to_collection():
                if isinstance(spec, EmptySpecification):
                    continue  # Skip empty specifications in AND
                clause, spec_params = DuckDBSpecificationBuilder._build_spec(spec)
                clauses.append(f"({clause})")
                params.extend(spec_params)
            return " AND ".join(clauses) if clauses else "TRUE", params

        elif isinstance(specification, OrSpecification):
            clauses = []
            params = []
            for spec in specification.to_collection():
                if isinstance(spec, EmptySpecification):
                    continue  # Skip empty specifications in OR
                clause, spec_params = DuckDBSpecificationBuilder._build_spec(spec)
                clauses.append(f"({clause})")
                params.extend(spec_params)
            return " OR ".join(clauses) if clauses else "TRUE", params

        elif isinstance(specification, EqualsSpecification):
            return f"{specification.field} = ?", [specification.value]

        elif isinstance(specification, NotEqualsSpecification):
            return f"{specification.field} != ?", [specification.value]

        elif isinstance(specification, InSpecification):
            placeholders = ",".join(["?"] * len(specification.value))
            return f"{specification.field} IN ({placeholders})", specification.value

        elif isinstance(specification, LessThanSpecification):
            return f"{specification.field} < ?", [specification.value]

        elif isinstance(specification, LessThanEqualSpecification):
            return f"{specification.field} <= ?", [specification.value]

        elif isinstance(specification, GreaterThanSpecification):
            return f"{specification.field} > ?", [specification.value]

        elif isinstance(specification, GreaterThanEqualSpecification):
            return f"{specification.field} >= ?", [specification.value]

        elif isinstance(specification, RegexStringMatchSpecification):
            # DuckDB regex operator for pattern matching
            # NOTE: Check Regex BEFORE Contains since Regex inherits from Contains
            # Using regexp_matches for regex matching
            return f"regexp_matches({specification.field}, ?)", [specification.value]

        elif isinstance(specification, ContainsSpecification):
            # DuckDB ILIKE for case-insensitive pattern matching
            pattern = f"%{specification.value}%"
            return f"{specification.field} ILIKE ?", [pattern]

        elif isinstance(specification, IsNoneSpecification):
            return f"{specification.field} IS NULL", []

        elif hasattr(specification, "to_collection"):
            # Handle dict-based specifications (legacy support)
            collection = specification.to_collection()
            if isinstance(collection, dict):
                clauses = []
                params = []
                for field, value in collection.items():
                    clauses.append(f"{field} = ?")
                    params.append(value)
                return " AND ".join(clauses), params

        raise SpecificationNotMappedToDuckDB(
            f"Unknown specification type: {type(specification)}"
        )
