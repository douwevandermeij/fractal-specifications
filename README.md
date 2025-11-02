# Fractal Specifications

> Fractal Specifications is an implementation of the specification pattern for building SOLID logic for your Python applications.

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]

<!-- Badges -->

[pypi-image]: https://img.shields.io/pypi/v/fractal-specifications
[pypi-url]: https://pypi.org/project/fractal-specifications/
[build-image]: https://github.com/douwevandermeij/fractal-specifications/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/douwevandermeij/fractal-specifications/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/douwevandermeij/fractal-specifications/branch/main/graph/badge.svg?token=BOC1ZUJISV
[coverage-url]: https://codecov.io/gh/douwevandermeij/fractal-specifications
[quality-image]: https://api.codeclimate.com/v1/badges/455ddff201b43f9b1025/maintainability
[quality-url]: https://codeclimate.com/github/douwevandermeij/fractal-specifications

## Installation

```bash
pip install fractal-specifications
```


## Background

This project comes with an [article on Medium](https://douwevandermeij.medium.com/specification-pattern-in-python-ff2bd0b603f6),
which sets out what the specification pattern is, what the benefits are and how it can be used.


## Development

Setup the development environment by running:

```bash
make dev-install
make dev-deps
```

Happy coding.

Occasionally you can run:

```bash
make lint
```

This is not explicitly necessary because the git hook does the same thing.

**Do not disable the git hooks upon commit!**

## Usage

Specifications can be used to encapsulate business rules.
An example specification is `EqualsSpecification("maximum_speed", 25)`.

A specification implements the `is_satisfied_by(obj)` function that returns `True` or `False`,
depending on the state of the `obj` that is passed into the function as parameter.
In our example, the `obj` needs to provide the attribute `maximum_speed`.

### Full code example

This example includes a repository to show an application of specifications.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from fractal_specifications.generic.operators import EqualsSpecification
from fractal_specifications.generic.specification import Specification


@dataclass
class Road:
    maximum_speed: int

    @staticmethod
    def slow_roads_specification() -> Specification:
        return EqualsSpecification("maximum_speed", 25)


class RoadRepository(ABC):
    @abstractmethod
    def get_all(self, specification: Specification) -> List[Road]:
        ...

    def slow_roads(self) -> List[Road]:
        return self.get_all(Road.slow_roads_specification())


class PythonListRoadRepository(RoadRepository):
    def __init__(self, roads: List[Road]):
        self.roads = roads

    def get_all(self, specification: Specification) -> List[Road]:
        return [
            road for road in self.roads
            if specification.is_satisfied_by(road)
        ]


if __name__ == "__main__":
    road_repository = PythonListRoadRepository([
        Road(maximum_speed=25),
        Road(maximum_speed=50),
        Road(maximum_speed=80),
        Road(maximum_speed=100),
    ])

    print(road_repository.slow_roads())
```

### Pre-processing

Since version 3.3.0 pre-processing object values is supported.
A pre-processor is a regular Python function that returns the same type as its (only) parameter.
Pre-processors can be used in all specifications derived from `FieldValueSpecification`.

For example, your repository contains objects with string values (e.g., users with a name and roles).
These strings may contain lowercase and uppercase characters and/or be part of a list.

```python
user_repository = UserRepository([
    User(name="John", roles=["admin", "billing"]),
    User(name="Jane", roles=["admin", "owner"]),
])
```

To find user "John", you can use the following specification:

```python
EqualsSpecification("name", "John")
```

However, you might also want to find "John" using the lowercase value "john" or partial value "jo".

You can do so by using a pre-processor as the third parameter:

```python
EqualsSpecification("name", "john", lambda i: i.lower())
ContainsSpecification("name", "jo", lambda i: i.lower())
```

This also works for list values:

```python
ContainsSpecification("roles", "BILLING", lambda i: [r.upper() for r in i])
```

Pre-processing currently **only** works for plain Python usage, so when manually using the `is_satisfied_by` function.
Pre-processors are not (yet) used in the "SpecificationBuilders" in `contrib`.

## Serialization / deserialization

Specifications can be exported as dictionary and loaded as such via `spec.to_dict()` and `Specification.from_dict(d)` respectively.

Specifications can also be exported to JSON via `spec.dumps()`. This essentially is a `json.dumps()` call around `spec.to_dict()`.

JSON specification strings can be loaded directly as Specification object via `Specification.loads(s)`.

Via this mechanism, specifications can be used outside the application runtime environment. For example, in a database or sent via API.

### Pre-processing

Since version 3.3.0 pre-processing object values is supported, but these pre-processors will **not** be part of the serialization.

### Domain Specific Language (DSL)

Apart from basic JSON serialization, Fractal Specifications also comes with a DSL.

Example specifications DSL strings:

- `field_name == 10`
  - This is a simple comparison expression with a numerical value.
- `obj.id == 10`
  - This is a comparison expression on an object attribute with a numerical value.
- `name != 'John'`
  - This is another comparison expression with a string value.
- `age >= 18 && is_student == True`
  - This is a logical AND operation between two comparison expressions and a boolean value.
- `roles contains "admin" || roles contains "editor"`
  - This is a logical OR operation between two values of a list field.
- `!(active == True)`
  - This is a negation of an expression.
- `name in ['John', 'Jane']`
  - This is an in_expression that checks if a field value is present in a list of values.
- `email matches \"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\"`
  - This is a regex match_expression that checks if a field value matches a given pattern.
- `items contains "element"`
  - This is a contains_expression that checks if a list field contains a given value
    - Contains can sometimes also be used with substrings, e.g, when using `is_satisfied_by`.
- `salary is None`
  - This is an is_none_expression that checks if a field value is None.
- `#`
  - This is an empty_expression that represents an empty expression.

Specifications can be loaded from a DSL string with `spec = Specification.load_dsl(dsl_string)`.\
Specifications can be serialized to a DSL string using `spec.dump_dsl()`.

Example:
```python
from dataclasses import dataclass

from fractal_specifications.generic.specification import Specification


@dataclass
class Demo:
    field: str


spec = Specification.load_dsl("field matches 'f.{20}s'")
spec.is_satisfied_by(Demo("fractal_specifications"))  # True
```

## Contrib

This library also comes with some additional helpers to integrate the specifications easier with existing backends,
such as the Django ORM, PostgreSQL, MongoDB, and more.

### Specification Support Matrix

| Specification Type | Django | SQLAlchemy | PostgreSQL | DuckDB | MongoDB | Elasticsearch | Firestore | Pandas |
|-------------------|--------|------------|------------|--------|---------|---------------|-----------|--------|
| `EqualsSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `NotEqualsSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `InSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ContainsSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅* | ❌ |
| `RegexStringMatchSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `LessThanSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `LessThanEqualSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GreaterThanSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GreaterThanEqualSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `IsNoneSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| `AndSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `OrSpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `EmptySpecification` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

\* Firestore's `ContainsSpecification` uses `array-contains` operator (for array membership, not string substring matching)

### Django

Specifications can easily be converted to (basic) Django ORM filters with `DjangoOrmSpecificationBuilder`.\
Using this contrib package requires `django` to be installed.

Query support:
* [x] Direct model fields `field=value`
* [x] Indirect model fields `field__sub_field=value`
  * Example: `EqualsSpecification("field__sub_field", "abc")`
    * Implies recursive subfields `field__sub_field__sub_sub_field=value`
  * This holds for all operators below as well as for Django specific operators
    * Example: `EqualsSpecification("field__sub_field__startswith", "ab")`
  * When using parse, make sure to use the `_lookup_separator="__"`:
    * Default, the resulting parsed specification will contain `"."` as separator
    * `Specification.parse(field__sub_field="abc", _lookup_separator="__")`
      * Will result in: `EqualsSpecification("field__sub_field", "abc")` instead of `EqualsSpecification("field.sub_field", "abc")`
* [x] Equals `field=value` or `__exact`
* [x] Not equals `~Q(field=value)` (negated Q object)
* [x] Less than `__lt`
* [x] Less than equal `__lte`
* [x] Greater than `__gt`
* [x] Greater than equal `__gte`
* [x] In `__in`
* [x] Contains `__icontains` (case-insensitive substring match)
* [x] Regex `__regex` (user-provided regex pattern)
* [x] And `Q((field_a=value_a) & (field_b=value_b))`
* [x] Or `Q((field_a=value_a) | (field_b=value_b))`
* [x] Is null `__isnull`

```python
from abc import ABC, abstractmethod
from django.db import models
from typing import List

from fractal_specifications.contrib.django.specifications import DjangoOrmSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification
from fractal_specifications.generic.specification import Specification


class Road(models.Model):
    maximum_speed = models.IntegerField()

    @staticmethod
    def slow_roads_specification() -> Specification:
        return EqualsSpecification("maximum_speed", 25)


class RoadRepository(ABC):
    @abstractmethod
    def get_all(self, specification: Specification) -> List[Road]:
        ...

    def slow_roads(self) -> List[Road]:
        return self.get_all(Road.slow_roads_specification())


class DjangoRoadRepository(RoadRepository):
    def get_all(self, specification: Specification) -> List[Road]:
        if q := DjangoOrmSpecificationBuilder.build(specification):
            return Road.objects.filter(q)
        return Road.objects.all()


if __name__ == "__main__":
    road_repository = DjangoRoadRepository()

    print(road_repository.slow_roads())
```

You could of course also skip the repository in between and do the filtering directly:

```python
from fractal_specifications.contrib.django.specifications import DjangoOrmSpecificationBuilder

q = DjangoOrmSpecificationBuilder.build(Road.slow_roads_specification())
Road.objects.filter(q)
```

### SQLAlchemy

Specifications can be converted to SQLAlchemy compatible formats with `SqlAlchemyOrmSpecificationBuilder`.

Query support:
* [x] Equals `{field: value}` (for `filter_by()` usage)
* [x] Not equals `(field, "ne", value)` (tuple format for `filter()` usage)
* [x] In `(field, "in", [values])` (tuple format for `filter()` usage)
* [x] Contains `(field, "contains", value)` (tuple format for `filter()` usage)
* [x] Regex `(field, "regex", pattern)` (tuple format for `filter()` usage)
* [x] Less than `(field, "lt", value)` (tuple format for `filter()` usage)
* [x] Less than equal `(field, "le", value)` (tuple format for `filter()` usage)
* [x] Greater than `(field, "gt", value)` (tuple format for `filter()` usage)
* [x] Greater than equal `(field, "ge", value)` (tuple format for `filter()` usage)
* [x] Is null `(field, "is_none", None)` (tuple format for `filter()` usage)
* [x] And - returns dict if all specs return dicts, otherwise list
* [x] Or `[{field: value}, {field2: value2}]`

**Note**: Operations that return tuples require using SQLAlchemy's `filter()` method with appropriate column methods:
- `NotEqualsSpecification`: Use `Model.field != value`
- `LessThanSpecification`: Use `Model.field < value`
- `LessThanEqualSpecification`: Use `Model.field <= value`
- `GreaterThanSpecification`: Use `Model.field > value`
- `GreaterThanEqualSpecification`: Use `Model.field >= value`
- `IsNoneSpecification`: Use `Model.field.is_(None)`
- `ContainsSpecification`: Use `Model.field.contains(value)` or `Model.field.like(f'%{value}%')`
- `RegexStringMatchSpecification`: Use `Model.field.op('~*')(pattern)` for PostgreSQL
- `InSpecification`: Use `Model.field.in_(values)`

```python
from fractal_specifications.contrib.sqlalchemy.specifications import SqlAlchemyOrmSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification, ContainsSpecification

# Simple equals - returns dict, use with filter_by()
spec = EqualsSpecification("name", "John")
q = SqlAlchemyOrmSpecificationBuilder.build(spec)  # {"name": "John"}
Model.query.filter_by(**q)

# Contains - returns tuple, use with filter()
spec = ContainsSpecification("description", "test")
field, op, value = SqlAlchemyOrmSpecificationBuilder.build(spec)  # ("description", "contains", "test")
Model.query.filter(getattr(Model, field).contains(value))
```

### Elasticsearch

Using this contrib package requires `elasticsearch` to be installed.

Query support:
* [x] Exact term match (Equals) `{"match": {"%s.keyword" % field: value}}`
* [x] String searches (In) `{"query_string": {"default_field": field, "query": value}}`
* [x] And `{"bool": {"must": [...]}}`
* [x] Or `{"bool": {"should": [...]}}`
* [x] Less than `{"bool": {"filter": [{"range": {field: {"lt": value}}}]}}`
* [x] Less than equal `{"bool": {"filter": [{"range": {field: {"lte": value}}}]}}`
* [x] Greater than `{"bool": {"filter": [{"range": {field: {"gt": value}}}]}}`
* [x] Greater than equal `{"bool": {"filter": [{"range": {field: {"gte": value}}}]}}`

```python
from elasticsearch import Elasticsearch
from fractal_specifications.contrib.elasticsearch.specifications import ElasticSpecificationBuilder

q = ElasticSpecificationBuilder.build(specification)
Elasticsearch(...).search(body={"query": q})
```

### Google Firestore

Query support:
* [x] Equals `(field, "==", value)`
* [x] And `[(field, "==", value), (field2, "==", value2)]`
* [x] Contains `(field, "array-contains", value)`
* [x] In `(field, "in", value)`
* [x] Less than `(field, "<", value)`
* [x] Less than equal `(field, "<=", value)`
* [x] Greater than `(field, ">", value)`
* [x] Greater than equal `(field, ">=", value)`

```python
from fractal_specifications.contrib.google_firestore.specifications import FirestoreSpecificationBuilder

q = FirestoreSpecificationBuilder.build(specification)
```

### PostgreSQL

Specifications can be converted to PostgreSQL WHERE clauses with parameters using `PostgresSpecificationBuilder`.

Query support:
* [x] Equals `field = %s` with `[value]`
* [x] Not equals `field != %s` with `[value]`
* [x] In `field IN (%s,%s,...)` with `[value1, value2, ...]`
* [x] Contains `field ILIKE %s` with `["%value%"]` (case-insensitive substring match)
* [x] Regex `field ~* %s` with `[pattern]` (case-insensitive regex)
* [x] Less than `field < %s` with `[value]`
* [x] Less than equal `field <= %s` with `[value]`
* [x] Greater than `field > %s` with `[value]`
* [x] Greater than equal `field >= %s` with `[value]`
* [x] Is null `field IS NULL` with `[]`
* [x] And `(clause1) AND (clause2)`
* [x] Or `(clause1) OR (clause2)`

```python
from fractal_specifications.contrib.postgresql.specifications import PostgresSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification, ContainsSpecification

spec = EqualsSpecification("name", "John") & ContainsSpecification("description", "test")
sql, params = PostgresSpecificationBuilder.build(spec)
# sql: "(name = %s) AND (description ILIKE %s)"
# params: ["John", "%test%"]

cursor.execute(f"SELECT * FROM table WHERE {sql}", params)
```

### DuckDB

Specifications can be converted to DuckDB WHERE clauses with parameters using `DuckDBSpecificationBuilder`.

Query support:
* [x] Equals `field = ?` with `[value]`
* [x] Not equals `field != ?` with `[value]`
* [x] In `field IN (?,?,...)` with `[value1, value2, ...]`
* [x] Contains `field ILIKE ?` with `["%value%"]` (case-insensitive substring match)
* [x] Regex `regexp_matches(field, ?)` with `[pattern]`
* [x] Less than `field < ?` with `[value]`
* [x] Less than equal `field <= ?` with `[value]`
* [x] Greater than `field > ?` with `[value]`
* [x] Greater than equal `field >= ?` with `[value]`
* [x] Is null `field IS NULL` with `[]`
* [x] And `(clause1) AND (clause2)`
* [x] Or `(clause1) OR (clause2)`

```python
from fractal_specifications.contrib.duckdb.specifications import DuckDBSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification, RegexStringMatchSpecification

spec = EqualsSpecification("status", "active") & RegexStringMatchSpecification("email", r".*@example\.com")
sql, params = DuckDBSpecificationBuilder.build(spec)
# sql: "(status = ?) AND (regexp_matches(email, ?))"
# params: ["active", ".*@example\\.com"]

conn.execute(f"SELECT * FROM table WHERE {sql}", params)
```

### MongoDB

Query support:
* [x] Equals `{field: {"$eq": value}}`
* [x] Not equals `{field: {"$ne": value}}`
* [x] In `{field: {"$in": [values]}}`
* [x] Contains `{field: {"$regex": ".*escaped_value.*"}}` (literal substring, special chars escaped)
* [x] Regex `{field: {"$regex": pattern}}` (user-provided regex pattern)
* [x] Less than `{field: {"$lt": value}}`
* [x] Less than equal `{field: {"$lte": value}}`
* [x] Greater than `{field: {"$gt": value}}`
* [x] Greater than equal `{field: {"$gte": value}}`
* [x] Is null `{field: {"$eq": None}}`
* [x] And `{"$and": [{...}, {...}]}`
* [x] Or `{"$or": [{...}, {...}]}`

```python
from fractal_specifications.contrib.mongo.specifications import MongoSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification, ContainsSpecification

spec = EqualsSpecification("status", "active") & ContainsSpecification("name", "test")
q = MongoSpecificationBuilder.build(spec)
# q: {"$and": [{"status": {"$eq": "active"}}, {"name": {"$regex": ".*test.*"}}]}

collection.find(q)
```

### Pandas

Pandas support comes in two different flavours.
You can use _columns_ or _indexes_ to filter on.

#### Filtering on columns

Query support:
* [x] Equals `df[field] == value`
* [x] And `(df[field] == value) & (df[field2] == value2)`
* [x] Or `(df[field] == value) | (df[field2] == value2)`
* [x] In `df[field].isin[value]`
* [x] Less than `df[field] < value`
* [x] Less than equal `df[field] <= value`
* [x] Greater than `df[field] > value`
* [x] Greater than equal `df[field] >= value`
* [x] Is null `df[field].isna()`

```python
import pandas as pd

from fractal_specifications.contrib.pandas.specifications import PandasSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification, IsNoneSpecification


df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "name": ["aa", "bb", "cc", "dd"],
        "field": ["x", "y", "z", None],
    }
)

print(df)
#    id name field
# 0   1   aa     x
# 1   2   bb     y
# 2   3   cc     z
# 3   4   dd  None


specification = EqualsSpecification("id", 4)
f1 = PandasSpecificationBuilder.build(specification)

print(f1(df))
#    id name field
# 3   4   dd  None


specification = IsNoneSpecification("field")
f2 = PandasSpecificationBuilder.build(specification)

print(f2(df))
#    id name field
# 3   4   dd  None


print(df.pipe(f1).pipe(f2))
#    id name field
# 3   4   dd  None


specification = EqualsSpecification("id", 4) & IsNoneSpecification("field")
f3 = PandasSpecificationBuilder.build(specification)

print(f3(df))
#    id name field
# 3   4   dd  None
```

#### Filtering on indexes

Query support:
* [x] Equals `df.index.get_level_values(field) == value`
* [x] And `(df.index.get_level_values(field) == value) & (df.index.get_level_values(field2) == value2)`
* [x] Or `(df.index.get_level_values(field) == value) | (df.index.get_level_values(field2) == value2)`
* [x] In `df.index.get_level_values(field).isin[value]`
* [x] Less than `df.index.get_level_values(field) < value`
* [x] Less than equal `df.index.get_level_values(field) <= value`
* [x] Greater than `df.index.get_level_values(field) > value`
* [x] Greater than equal `df.index.get_level_values(field) >= value`
* [x] Is null `df.index.get_level_values(field).isna()`

```python
import pandas as pd

from fractal_specifications.contrib.pandas.specifications import PandasIndexSpecificationBuilder
from fractal_specifications.generic.operators import EqualsSpecification, GreaterThanSpecification


df = pd.DataFrame({"month": [1, 4, 7, 10],
                   "year": [2012, 2014, 2013, 2014],
                   "sale": [55, 40, 84, 31]})
df = df.set_index("month")

print(df)
#        year  sale
# month
# 1      2012    55
# 4      2014    40
# 7      2013    84
# 10     2014    31

specification = EqualsSpecification("month", 4)
f1 = PandasIndexSpecificationBuilder.build(specification)

print(f1(df))
#        year  sale
# month
# 4      2014    40


df = df.reset_index()
df = df.set_index("year")

specification = GreaterThanSpecification("year", 2013)
f2 = PandasIndexSpecificationBuilder.build(specification)

print(f2(df))
#       month  sale
# year
# 2014      4    40
# 2014     10    31


df = df.reset_index()
df = df.set_index(["month", "year"])

print(df.pipe(f1).pipe(f2))
#             sale
# month year
# 4     2014    40


specification = EqualsSpecification("month", 4) & GreaterThanSpecification("year", 2013)
f3 = PandasIndexSpecificationBuilder.build(specification)

print(f3(df))
#             sale
# month year
# 4     2014    40
```
