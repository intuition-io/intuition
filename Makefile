# Makefile
# xavier, 2013-07-30 07:56
#
# vim:ft=make

LOGS?=/tmp/intuition.logs

all: dependencies modules install

install:
	python setup.py install

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
	flake8 intuition
	nosetests -w tests --with-coverage --cover-package=intuition

present_pep8=$(shell which pep8)
present_pyflakes=$(shell which pyflakes)
warn_missing_linters:
	@test -n "$(present_pep8)" || echo "WARNING: pep8 not installed."
	@test -n "$(present_pyflakes)" || echo "WARNING: pyflakes not installed."

.PHONY: dependencies install warn_missing_linters tests package
