# Copyright (C) 2012 - 2022 Charlie Clark

"""Python utility module Google Visualization Python API."""

__author__ = "Charlie Clark"

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(
    name = "gviz_data_table",
    packages = find_packages(".",
                             exclude=["*.tests",],
                             ),
    version = "2.0.0",
    description = "Python API for Google Visualization",
    long_description = README,
    author = __author__,
    author_email = 'charlie.clark@clark-consulting.eu',
    license = "BSD",
    keywords = 'charting graph Google Visualisation',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        ],
        project_urls={
        'Documentation': 'https://gviz-data-table.readthedocs.io/en/stable/',
        'Source': 'https://foss.heptapod.net/openpyxl/gviz-data-table',
        'Tracker': 'https://foss.heptapod.net/openpyxl/gviz-data-table/-/issues',
    },
    python_requires = ">=3.8",
)
