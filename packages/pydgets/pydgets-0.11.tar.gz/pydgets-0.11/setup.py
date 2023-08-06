#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) 2015-2016 Jan Mach <email@jan-mach.cz>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

# Resources:
#   https://packaging.python.org/en/latest/
#   https://python-packaging.readthedocs.io/en/latest/index.html

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import sys
#
# Import local version of pynspect library, so that we can insert correct version
# number into documentation.
#
sys.path.insert(0, path.abspath('.'))
import pydgets

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pydgets',
    version = pydgets.__version__,
    description = 'Console widget library for Python 3',
    long_description = long_description,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
    ],
    keywords = 'library console widgets',
    url = 'https://pypi.org/project/pydgets/',
    project_urls={
        'Documentation': 'https://709.gitlab-pages.cesnet.cz/mentat/pydgets/master/html/manual.html',
        'Source': 'https://gitlab.cesnet.cz/709/mentat/pydgets',
        'Tracker': 'https://gitlab.cesnet.cz/709/mentat/pydgets/-/issues'
    },
    author = 'Jan Mach',
    author_email = 'email@jan-mach.cz',
    license = 'MIT',
    packages = ['pydgets'],
    include_package_data = True,
    zip_safe = False
)
