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


if __name__ == '__main__':
    road_repository = PythonListRoadRepository([
        Road(maximum_speed=25),
        Road(maximum_speed=50),
        Road(maximum_speed=80),
        Road(maximum_speed=100),
    ])

    print(road_repository.slow_roads())
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


if __name__ == '__main__':
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
