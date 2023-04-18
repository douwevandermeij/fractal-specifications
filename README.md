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

```sh
pip install fractal-specifications
```


## Background

This project comes with an [article on Medium](https://douwevandermeij.medium.com/specification-pattern-in-python-ff2bd0b603f6),
which sets out what the specification pattern is, what the benefits are and how it can be used.


## Development

Setup the development environment by running:

```sh
make deps
pre-commit install
```

Happy coding.

Occasionally you can run:

```sh
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

## Serialization / deserialization

Specifications can be exported as dictionary and loaded as such via `spec.to_dict()` and `Specification.from_dict(d)` respectively.

Specifications can also be exported to JSON via `spec.dumps()`. This essentially is a `json.dumps()` call around `spec.to_dict()`.

JSON specification strings can be loaded directly as Specification object via `Specification.loads(s)`.

Via this mechanism, specifications can be used outside the application runtime environment. For example, in a database or sent via API.

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
such as the Django ORM.

### Django

Specifications can easily be converted to (basic) Django ORM filters with `DjangoOrmSpecificationBuilder`.\
Using this contrib package requires `django` to be installed.

Query support:
* [x] Direct model fields `field=value`
* [ ] Indirect model fields `field__sub_field=value`
  * Implies recursive subfields `field__sub_field__sub_sub_field=value`
  * This holds for all operators below as well
* [x] Equals `field=value` or `__exact`
* [x] Less than `__lt`
* [x] Less than equal `__lte`
* [x] Greater than `__gt`
* [x] Greater than equal `__gte`
* [x] In `__in`
* [x] And `Q((field_a=value_a) & (field_b=value_b))`
* [x] Or `Q((field_a=value_a) | (field_b=value_b))`
* [x] Partial regex `__regex=r".* value .*"`
* [ ] Full regex `__regex`
* [ ] Contains regex `__contains`
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

Query support:
* [x] Direct model fields `{field: value}`
* [x] And `{field: value, field2: value2}`
* [x] Or `[{field: value}, {field2: value2}]`

```python
from fractal_specifications.contrib.sqlalchemy.specifications import SqlAlchemyOrmSpecificationBuilder

q = SqlAlchemyOrmSpecificationBuilder.build(specification)
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

### Mongo

Query support:
* [x] Equals `{field: {"$eq": value}}`
* [x] And `{"$and": [{field: {"$eq": value}}, {field2: {"$eq": value2}}]}`
* [x] Or `{"or": [{field: {"$eq": value}}, {field2: {"$eq": value2}}]}`
* [x] In `{field: {"$in": value}}`
* [x] Less than `{field: {"$lt": value}}`
* [x] Less than equal `{field: {"$lte": value}}`
* [x] Greater than `{field: {"$gt": value}}`
* [x] Greater than equal `{field: {"$gte": value}}`
* [x] Regex string match `{field: {"$regex": ".*%s.*" % value}}`

```python
from fractal_specifications.contrib.mongo.specifications import MongoSpecificationBuilder

q = MongoSpecificationBuilder.build(specification)
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
