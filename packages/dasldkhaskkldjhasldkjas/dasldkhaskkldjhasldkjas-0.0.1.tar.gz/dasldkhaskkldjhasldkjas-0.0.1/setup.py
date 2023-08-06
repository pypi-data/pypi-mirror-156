#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dasldkhaskkldjhasldkjas",
    python_requires = '>=3.8',
    version = "0.0.1",
    author = "cd",
    author_email = "user@example.com",
    description = ("test package"),
    keywords = "test",
    #url = "http://packages.python.org/an_example_pypi_project",
    packages=find_packages(),
    package_dir={"": "src"},
    scripts=[],
    install_requires= [
        'lxml',
    ],
    long_description=read('README.md'),
)
