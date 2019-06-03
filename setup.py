#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

requirements = ["Click>=6.0", "PyYAML"]

setup_requirements = []

test_requirements = [
    "black",
    "bumpversion",
    "watchdog",
    "flake8",
    "tox",
    "coverage",
    "twine",
]

setup(
    author="Jochem Berends",
    author_email="jochem.berends@ke-works.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Duplicity backup to S3 for production servers using simple toml file.",
    entry_points={
        "console_scripts": ["duplicity_backup_s3=duplicity_backup_s3.__main__:main"]
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + r"\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="duplicity_backup_s3",
    name="duplicity_backup_s3",
    packages=find_packages(include=["duplicity_backup_s3"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/jberends/duplicity_s3",
    version="0.1.0",
    zip_safe=False,
)
