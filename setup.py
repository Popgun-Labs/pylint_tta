#!/usr/bin/env python
import os
import shutil
import sys
from setuptools import setup, find_packages

__version__ = '0.0.4a'

readme = open('README.md').read()
requirements_txt = open('requirements.txt').read().split('\n')

requirements = list(filter(lambda x: '--extra' not in x and x is not '', requirements_txt))

dependency_links = list(filter(lambda x: '--extra' in x, requirements_txt))
dependency_links = list(map(lambda x: x.split(' ')[-1], dependency_links))

setup(
    # Metadata
    name='pylint_tta',
    version=__version__,
    author='Kendrick Tan',
    author_email='kendrick@wearepopgun.com',
    url='https://github.com/Popgun-Labs/pylint-tta',
    description='Linter for PyTorch Tensor operations',
    long_description=readme,
    long_description_content_type='text/markdown',

    # Package info
    packages=find_packages(exclude=('test',)),
    zip_safe=True,
    install_requires=requirements,
    dependency_links=dependency_links,
)
