#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

from duplicity_backup_s3 import __version__

requirements = ["Click>=7.0", "PyYAML", "envparse", "appdirs", "cerberus"]

setup_requirements = []

test_requirements = [
    "flake8",
    "tox",
    "coverage",
    "pydocstyle",
]

setup(
    python_requires=">=3.6",
    author="Jochem Berends",
    author_email="jberends@jbits.nl",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Compression",
        "Topic :: System :: Archiving :: Mirroring",
    ],
    project_urls={
        "Changelog": "https://github.com/jberends/duplicity_backup/blob/master/"
                     "CHANGELOG.md",
        "Contributors": "https://github.com/jberends/duplicity_backup/blob/master/"
                        "CONTRIBUTORS.md",
        "Source": "https://github.com/jberends/duplicity_backup",
        "Tracker": "https://github.com/jberends/duplicity_backup/issues",
        "Readme": "https://github.com/jberends/duplicity_backup/blob/master/README.md",
    },
    description="Duplicity backup to S3 for production servers using simple yaml "
                "config file.",
    entry_points={
        "console_scripts": (
            "duplicity_backup_s3 = duplicity_backup_s3.cli:duplicity_backup_s3"
        )
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
