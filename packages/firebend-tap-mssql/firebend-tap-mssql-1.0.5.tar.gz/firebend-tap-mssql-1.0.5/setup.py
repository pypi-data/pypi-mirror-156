#!/usr/bin/env python
from pathlib import Path
from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="firebend-tap-mssql",
    version="1.0.5",
    description="Singer.io tap for extracting data from SQL Server - PipelineWise compatible",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Stitch, wintersrd, SteveDMurphy, degreed-data-engineering, Firebend",
    url="https://github.com/firebend/pipelinewise-tap-mssql",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    py_modules=["tap_mssql"],
    install_requires=[
        "pendulum~=1.5.1",
        "singer-python~=5.12.2",
        "sqlalchemy~=1.4.31",
        "pyodbc==4.0.32",
        "backoff==1.8.0",
        "MarkupSafe==2.0.1",
        "jinja2==2.11.3",
    ],
    extras_require={
        'test': [
            'pylint~=2.12.2',
            'pytest~=6.2.5',
            'pytest-cov~=3.0.0',
        ]
    },
    entry_points="""
          [console_scripts]
          tap-mssql=tap_mssql:main
      """,
    packages=["tap_mssql", "tap_mssql.sync_strategies"],
)
