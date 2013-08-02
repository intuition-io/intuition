#
# Makefile
# xavier, 2013-07-30 07:56
#
# vim:ft=make

LOGS?=/tmp/quantrade.logs

all: dependencies install

install:
	@echo "[make] Copying library"
	cp -r neuronquant /usr/local/lib/python2.7/dist-packages
	@echo "[make] Creating logs directory"
	test -d ${HOME}/.quantrade || mkdir -p ${HOME}/.quantrade/logs
	mkdir -p ${HOME}/.quantrade/config
	@echo "[make] Copying default configuration"
	cp -r config/templates ${HOME}/.quantrade
	cp config/templates/default.tpl ${HOME}/.quantrade/config/default.json
	cp config/templates/plugins.tpl ${HOME}/.quantrade/config/plugins.json
	chown -R ${USER} ${HOME}/.quantrade

dependencies:
	@echo "[make] Updating cache..."
	apt-get update 2>&1 >> ${LOGS}
	@echo "[make] Installing packages"
	apt-get -y --force-yes install git r-base python-pip python-dev g++ make gfortran libzmq-dev mysql-client libmysqlclient-dev curl 2>&1 >> ${LOGS}
	@echo "[make] Installing python modules"
	pip install --upgrade distribute 2>&1 >> ${LOGS}
	pip install --upgrade -r ./scripts/installation/requirements.txt 2>&1 >> ${LOGS}

database:
	@echo "Setting up mysql quantrade database"
	mysql -u root -p < ./scripts/installation/createdb.sql
	@echo "Creating database schema"
	./scripts/database_manager.py -c
	@echo "Feeding database with US stocks"
	./scripts/database_manager.py -a ./data/symbols.csv
	@echo "Synchronizing..."
	./scripts/database_manager.py -s

team_dashboard:
	@echo "Coming!"

node:
	@echo "Coming!"

R-3.0:
	@echo "Coming!"

tests:
	nose tests
