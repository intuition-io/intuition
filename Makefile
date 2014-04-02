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
	# TODO Recursively analyze all files and fail on conditions
	@echo -e '\tChecking complexity (experimental) ...'
	radon cc -ana intuition/core/engine.py
	@echo -e '\tChecking requirements ...'
	#TODO Fail if outdated
	piprot --outdated requirements.txt dev-requirements.txt
	@echo -e '\tChecking syntax ...'
	flake8 tests intuition
	@echo -e '\tRunning tests ...'
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
