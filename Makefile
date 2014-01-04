# Makefile
# xavier, 2013-07-30 07:56
#
# vim:ft=make

LOGS?=/tmp/intuition.logs
MODULES?=https://github.com/hackliff/intuition-modules
PLUGINS?=https://github.com/hackliff/intuition-plugins

all: dependencies modules install

install:
	python setup.py install

modules:
	@echo "Downloading submodules"
	git submodule init
	git submodule update

dependencies:
	@echo "[make] Installing packages"
	apt-get -y --force-yes install git-core python-pip python-dev g++ make gfortran 2>&1 >> ${LOGS}
	@echo "[make] Installing python modules"
	pip install --use-mirrors distribute nose flake8 2>&1 >> ${LOGS}
	pip install --use-mirrors numpy 2>&1 >> ${LOGS}

package:
	python setup.py sdist
	git tag ${VERSION}
	git push --tags
	python setup.py sdist upload

tests: warn_missing_linters
	@flake8 intuition
	@nosetests tests

present_pep8=$(shell which pep8)
present_pyflakes=$(shell which pyflakes)
warn_missing_linters:
	@test -n "$(present_pep8)" || echo "WARNING: pep8 not installed."
	@test -n "$(present_pyflakes)" || echo "WARNING: pyflakes not installed."

.PHONY: dependencies install warn_missing_linters tests package
