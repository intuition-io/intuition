# Makefile
# xavier, 2013-07-30 07:56
#
# vim:ft=make

LOGS?=/tmp/intuition.logs
MODULES?=https://github.com/hackliff/intuition-modules
PLUGINS?=https://github.com/hackliff/intuition-plugins

all: dependencies install

install:
	@echo "[make] Copying library"
	cp -r intuition /usr/local/lib/python2.7/dist-packages
	@echo "[make] Creating logs directory"
	test -d ${HOME}/.intuition || mkdir -p ${HOME}/.intuition/logs
	mkdir -p ${HOME}/.intuition/config
	@echo "[make] Copying default configuration"
	cp -r config/templates ${HOME}/.intuition
	cp config/templates/default.tpl ${HOME}/.intuition/config/default.json
	cp config/templates/plugins.tpl ${HOME}/.intuition/config/plugins.json
	chmod -R ugo+rwx ${HOME}/.intuition
	chmod -R ugo+rwx ${PWD}

modules:
	git clone ${MODULES} intuition/modules
	git clone ${PLUGINS} intuition/plugins

dependencies:
	@echo "[make] Updating cache..."
	apt-get update 2>&1 >> ${LOGS}
	@echo "[make] Installing packages"
	sudo apt-get -y --force-yes install git-core r-base python-pip python-dev g++ make gfortran libzmq-dev mysql-client libmysqlclient-dev curl 2>&1 >> ${LOGS}
	@echo "[make] Installing python modules"
	pip install --upgrade distribute 2>&1 >> ${LOGS}
	pip install --upgrade numpy 2>&1 >> ${LOGS}
	pip install --upgrade -r ./scripts/installation/requirements.txt 2>&1 >> ${LOGS}
	@echo "[make] Installing R dependencies"
	./scripts/installation/install_r_packages.R 2>&1 >> ${LOGS}

database:
	@echo "Setting up mysql Intuition database"
	mysql -u root -p < ./scripts/installation/createdb.sql
	@echo "Creating database schema"
	./scripts/database_manager.py -c
	@echo "Feeding database with US stocks"
	./scripts/database_manager.py -a ./data/symbols.csv
	@echo "Synchronizing..."
	./scripts/database_manager.py -s

tags:
	@ctags --python-kinds=-iv -R intuition

etags:
	@ctags -e --python-kinds=-iv -R intuition

tests: warn_missing_linters
	@flake8 tests
	@nose tests

present_pep8=$(shell which pep8)
present_pyflakes=$(shell which pyflakes)
warn_missing_linters:
	@test -n "$(present_pep8)" || echo "WARNING: pep8 not installed."
	@test -n "$(present_pyflakes)" || echo "WARNING: pyflakes not installed."


.PHONY: tags dependencies install warn_missing_linters database tests
