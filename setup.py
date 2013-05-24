#!/usr/bin/env python
#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import re
from setuptools import setup, find_packages


# _______________________________________________________________________  smart requirement detector _______________
#NOTE not that smart, does not work for now
def which(program):
    """
    Detect whether or not a program is installed.
    Thanks to http://stackoverflow.com/a/377028/70191
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

EDITABLE_REQUIREMENT = re.compile(r'^-e (?P<link>(?P<vcs>git|svn|hg|bzr).+#egg=(?P<package>.+)-(?P<version>\d(?:\.\d)*))$')

install_requires = []
dependency_links = []

for requirement in (l.strip() for l in open('scripts/requirements.txt')):
    match = EDITABLE_REQUIREMENT.match(requirement)
    if match:
        assert which(match.group('vcs')) is not None, \
            "VCS '%(vcs)s' must be installed in order to install %(link)s" % match.groupdict()
        install_requires.append("%(package)s==%(version)s" % match.groupdict())
        dependency_links.append(match.group('link'))
    else:
        install_requires.append(requirement)
# ___________________________________________________________________________________________________________________

LONG_DESCRIPTION = None
README_MARKDOWN = None

with open('README.md') as markdown_source:
    README_MARKDOWN = markdown_source.read()

try:
    import pandoc
    pandoc.core.PANDOC_PATH = 'pandoc'
    # Converts the README.md file to ReST, since PyPI uses ReST for formatting,
    # This allows to have one canonical README file, being the README.md
    doc = pandoc.Document()
    doc.markdown = README_MARKDOWN
    LONG_DESCRIPTION = doc.rst
except ImportError:
    # If pandoc isn't installed, e.g. when downloading from pip,
    # just use the regular README.
    LONG_DESCRIPTION = README_MARKDOWN

setup(
    name='quantrade',
    version='0.1.3',
    description='Engine and tools for quantitative trading.',
    author='Xavier Bruhiere',
    author_email='xavier.bruhiere@gmail.com',
    packages=find_packages(),
    long_description=LONG_DESCRIPTION,
    license='Apache 2.0',
    #TODO Update with .quantrade !
    data_files=[
        ('scripts', ['scripts/ordered_pip.sh',
                     'scripts/run_labo.py',
                     'scripts/run_shiny.sh']),
        ('config', ['config/local.sh',
                    'config/shiny-server.config',
                    'config/mysql.cfg'])
    ],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Linux',
        'Intended Audience :: Finance/Science/Research',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing'
    ],
    install_requires=[
        'plac',
        'sqlalchemy',
        'beautifulsoup4',
        'scipy',
        #FIXME 'matplotlib',
        'rpy2',
        'statsmodels',
        'patsy',
        'msgpack-python',
        'mysql-python'
        'logbook',
        'pytz',
        'numpy',
        'pandas',
        'pyzmq',

    ],
    dependency_links = [
        'http://github.com/Gusabi/zipline',
        'http://github.com/quandl/Python'
    ],
    url="https://github.com/Gusabi/ppQuanTrade"
)
