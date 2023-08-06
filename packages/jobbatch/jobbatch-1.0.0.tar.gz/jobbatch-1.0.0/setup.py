from importlib_metadata import entry_points
from setuptools import setup
import sys

if sys.version_info[0] == 2:
    sys.exit("Sorry, Python 2 is no longer supported.")

major_version = 1
minor_version = 0
build_version = 0

version = str(major_version) + "." + str(minor_version) + "." + str(build_version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="jobbatch",
    python_requires='>3.4',
    version=version,
    description="jobbatch: a utility for splitting tasks up into batches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Quentin Stafford-Fraser",
    url="https://github.com/quentinsf/jobbatch",
    license="GNU GPL 2",
    packages=["jobbatch"],
    entry_points={
        'console_scripts': ['jobbatch=jobbatch:main'],
    }
)

