# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Packaging
  ---------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
from glob import glob
from setuptools import setup, find_packages
from intuition import (
    __version__, __author__, __licence__, __project__
)


def get_requirements():
    with open('./requirements.txt') as requirements:
        # Avoid github based requirements and replace them
        deps = requirements.read().split('\n')[:-2]
        deps.append('zipline>=0.5.11.dev')
    return deps


requires = [
    'beautifulsoup4',
    'blist',
    'Cython',
    'ystockquote',
    'numpy',
    'schematics',
    'schema',
    'python-dateutil',
    'pytz',
    'PyYAML',
    'Quandl>=1.9.7',
    'dna>=0.0.6',
    'six',
    'zipline>=0.5.9',
    'pandas>=0.13.1'
]


def long_description():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return "failed to read README.md"


setup(
    name=__project__,
    version=__version__,
    description='A trading system building blocks',
    author=__author__,
    author_email='xavier.bruhiere@gmail.com',
    packages=find_packages(),
    long_description=long_description(),
    license=__licence__,
    install_requires=requires,
    url="https://github.com/hackliff/intuition",
    entry_points={
        'console_scripts': [
            'intuition = intuition.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing',
    ],
    data_files=[
        (os.path.expanduser('~/.intuition/data'), glob('data/*')),
        (os.path.expanduser('~/.intuition/logs'), glob('./MANIFEST.in'))
    ],
    dependency_links=[
        'http://github.com/quantopian/zipline/tarball/master#egg=zipline-0.5.11.dev'
    ]
)
