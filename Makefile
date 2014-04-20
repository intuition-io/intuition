# Makefile
# vim:ft=make

LOGS?=/tmp/make-intuition.logs

all: dependencies install

install:
	python setup.py install

dependencies:
	@echo "[make] Installing packages"
	apt-get -y --force-yes install git-core python-pip python-dev g++ make gfortran 2>&1 >> ${LOGS}
	@echo "[make] Installing python modules"
	pip install --quiet --use-mirrors distribute 2>&1 >> ${LOGS}
	pip install --quiet --use-mirrors numpy 2>&1 >> ${LOGS}

package:
	# NOTE Replace the version in intuition.__init__.py ?
	@echo "[make] Committing changes"
	git add -A
	git commit
	git tag ${VERSION}
	git push --tags
	@echo "[make] Packaging intuition"
	python setup.py sdist
	python setup.py sdist upload

tests: warn_missing_linters
	# TODO Recursively analyze all files and fail on conditions
	@echo -e '\tChecking complexity (experimental) ...'
	radon cc -ana intuition/core/engine.py
	@echo -e '\tChecking requirements ...'
	# TODO Fail if outdated
	piprot --outdated requirements.txt dev-requirements.txt
	@echo -e '\tChecking syntax ...'
	pep8 --ignore E265 tests intuition
	@echo -e '\tRunning tests ...'
	nosetests -s -w tests --with-yanc --with-coverage --cover-package=intuition

watch: warn_missing_linters
	watchmedo shell-command \
    --patterns="*.py;*.txt" \
    --recursive \
    --command="make tests" .

present_pep8=$(shell which pep8)
present_radon=$(shell which radon)
present_nose=$(shell which nosetests)
present_piprot=$(shell which piprot)
present_watchdog=$(shell which watchmedo)
warn_missing_linters:
	@test -n "$(present_radon)" || echo "WARNING: radon not installed."
	@test -n "$(present_pep8)" || echo "WARNING: pep8 not installed."
	@test -n "$(present_nose)" || echo "WARNING: nose not installed."
	@test -n "$(present_piprot)" || echo "WARNING: piprot not installed."
	@test -n "$(present_watchdog)" || echo "WARNING: watchdog not installed."

.PHONY: dependencies install warn_missing_linters tests package
