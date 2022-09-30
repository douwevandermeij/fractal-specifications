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
    def slow_roads_specification():
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


road_repository = PythonListRoadRepository([
    Road(maximum_speed=25),
    Road(maximum_speed=50),
    Road(maximum_speed=80),
    Road(maximum_speed=100),
])


if __name__ == '__main__':
    print(road_repository.slow_roads())
```
