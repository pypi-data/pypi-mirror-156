#!/usr/bin/env python
from os import path

from setuptools import setup


def get_version(rel_path):
    """get version information from __init__.py file."""
    with open(rel_path) as fp:
        cont = fp.read().splitlines()
    for line in cont:
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version infomation.")


curr_dir = path.dirname(path.abspath(__file__))
version = get_version(path.join(curr_dir, 'msbff', '__init__.py'))

setup(
    name='msbff',
    version=version,
    url='https://github.com/BioGavin/msbff',
    license='GPL',
    author='Zhen-Yi Zhou',
    author_email="gavinchou64@gmail.com",
    description="Bioactive Fractions Filtering.",
    classifiers=["Programming Language :: Python :: 3.8",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Operating System :: OS Independent"],
    scripts=['scripts/msbff'],
    packages=['msbff'],
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "matplotlib",
        "numpy"
    ]
)
