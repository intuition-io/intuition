# Makefile
# xavier, 2013-07-30 07:56
#
# vim:ft=make

LOGS?=/tmp/intuition.logs
MODULES?=https://github.com/hackliff/intuition-modules
PLUGINS?=https://github.com/hackliff/intuition-plugins

all: dependencies modules install

install:
	@echo "[make] Copying library"
	sudo cp -r intuition /usr/local/lib/python2.7/dist-packages
	@echo "[make] Creating logs directory"
	test -d ${HOME}/.intuition || mkdir -p ${HOME}/.intuition/logs
	@echo "[make] Copying default configuration"
	cp config/default.tpl ${HOME}/.intuition/default.json
	cp config/plugins.tpl ${HOME}/.intuition/plugins.json
	@echo "Now edit your preferences in ~/.intuition"

modules:
	@echo "Downloading submodules"
	git submodule init
	git submodule update

dependencies:
	@echo "[make] Updating cache..."
	sudo apt-get update 2>&1 >> ${LOGS}
	@echo "[make] Installing packages"
	#sudo apt-get -y --force-yes install git-core r-base python-pip python-dev g++ make gfortran libzmq-dev mysql-client libmysqlclient-dev curl 2>&1 >> ${LOGS}
	sudo apt-get -y --force-yes install git-core r-base python-pip python-dev g++ make gfortran 2>&1 >> ${LOGS}
	@echo "[make] Installing python modules"
	pip install --upgrade distribute 2>&1 >> ${LOGS}
	pip install --upgrade numpy 2>&1 >> ${LOGS}
	pip install --upgrade -r ./scripts/installation/requirements.txt 2>&1 >> ${LOGS}
	#FIXME First installation needs to specify lib parameter
	@echo "[make] Installing R dependencies"
	./scripts/installation/install_r_packages.R 2>&1 >> ${LOGS}

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
