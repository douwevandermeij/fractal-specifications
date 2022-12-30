import os
import re
import sys


def get_version_pyproject():
    with open(os.path.join(os.path.dirname(__file__), "pyproject.toml")) as fp:
        for line in fp:
            m = re.search(r'^version = ([\'"])([^\'"]+)\1$', line)
            if m:
                return m.group(2)
        else:
            raise RuntimeError("Unable to find version")


if __name__ == "__main__":
    new_version_string = f'__version__ = "{get_version_pyproject()}"'
    filename = os.path.join(os.path.dirname(__file__), sys.argv[1], "__init__.py")
    with open(filename, "r+") as f:
        text = f.read()
        text = re.sub(
            r'^__version__ = ([\'"])([^\'"]+)\1$', new_version_string, text, flags=re.M
        )
        f.seek(0)
        f.write(text)
        f.truncate()
