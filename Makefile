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
	pip install --quiet --use-mirrors distribute nose flake8 2>&1 >> ${LOGS}
	pip install --quiet --use-mirrors numpy 2>&1 >> ${LOGS}

package:
	#python setup.py register
	python setup.py sdist
	git tag ${VERSION}
	git push --tags
	python setup.py sdist upload

tests: warn_missing_linters
	@hr '-'
	@echo -e '\tChecking requirements ...'
	@hr '-'
	#TODO Fail if outdated
	piprot --outdated requirements.txt dev-requirements.txt
	@hr '-'
	@echo -e '\tChecking syntax ...'
	@hr '-'
	flake8 tests intuition
	@hr '-'
	@echo -e '\tRunning tests ...'
	@hr '-'
	nosetests -w tests --with-yanc --with-coverage --cover-package=intuition

watch: warn_missing_linters
	watchmedo shell-command \
    --patterns="*.py;*.txt" \
    --recursive \
    --command="make tests" .

present_pep8=$(shell which pep8)
present_pyflakes=$(shell which pyflakes)
warn_missing_linters:
	@test -n "$(present_pep8)" || echo "WARNING: pep8 not installed."
	@test -n "$(present_pyflakes)" || echo "WARNING: pyflakes not installed."

.PHONY: dependencies install warn_missing_linters tests package
