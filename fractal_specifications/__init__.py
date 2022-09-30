"""Fractal Specifications is an implementation of the specifications pattern for building SOLID logic for your Python applications."""


def find_version(fp):
    line = fp.readline()
    found_poetry = False
    while line:
        if found_poetry and "version" in line:
            return line.split()[-1][1:-1]
        if "tool.poetry" in line:
            found_poetry = True
        line = fp.readline()


def get_version():
    with open("pyproject.toml") as fp:
        return find_version(fp)


__version__ = get_version()
