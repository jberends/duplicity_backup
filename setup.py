#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

from duplicity_backup_s3 import __version__

requirements = ["Click>=7.0", "PyYAML", "envparse", "cerberus"]

setup_requirements = []

test_requirements = [
    "flake8",
    "tox",
    "coverage",
    "appdirs",
    "pydocstyle",
]

setup(
    python_requires='>=3.5',
    author="Jochem Berends",
    author_email="jochem.berends@ke-works.com",
    classifiers=[
        "Development Status :: 5 - Production",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    project_urls={
        'Changelog': 'https://github.com/jberends/duplicity_backup/blob/master/CHANGELOG.md',
        'Source': 'https://github.com/jberends/duplicity_backup',
        'Tracker': 'https://github.com/jberends/duplicity_backup/issues',
        'Readme': 'https://github.com/jberends/duplicity_backup/blob/master/README.md'
    },
    description="Duplicity backup to S3 for production servers using simple yaml config file.",
    entry_points={
        "console_scripts": (
            "duplicity_backup_s3 = duplicity_backup_s3.cli:duplicity_backup_s3")
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + r"\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="duplicity_backup_s3",
    name="duplicity_backup_s3",
    packages=find_packages(exclude=["tests"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/jberends/duplicity_backup",
    version=__version__,
    zip_safe=False,
)
