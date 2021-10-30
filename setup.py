from setuptools import setup, find_packages
from avereno.version import get_version


def get_long_description():
    with open("README.md", "r") as readme:
        return readme.read()


setup(
    name="avereno",
    version=get_version(),
    description="Yet another retry utility in Python",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="HEI",
    author_email="contact@hei.school",
    url="https://github.com/hei-school/avereno",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
)
