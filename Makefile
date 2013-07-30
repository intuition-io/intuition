#
# Makefile
# xavier, 2013-07-30 07:56
#
# vim:ft=make

LOGS = /tmp/quantrade.logs

all: dependencies install

install:
	@echo "[make] Copying library"
	cp -r neuronquant /usr/local/lib/python2.7/dist-packages
	@echo "[make] Creating logs directory"
	test -d ${HOME}/.quantrade || mkdir -p ${HOME}/.quantrade/logs
	@echo "[make] Copying default configuration"
	cp -r config ${HOME}/.quantrade
	chown -R ${USER} ${HOME}/.quantrade

dependencies:
	@echo "[make] Updating cache..."
	apt-get update 2>&1 >> ${LOGS}
	@echo "[make] Installing packages"
	apt-get -y --force-yes install git r-base python-pip python-dev g++ make gfortran libzmq-dev mysql-client libmysqlclient-dev curl 2>&1 >> ${LOGS}
	@echo "[make] Installing python modules"
	pip install --upgrade distribute 2>&1 >> ${LOGS}
	pip install --use-mirrors -U -r ./scripts/installation/requirements.txt 2>&1 >> ${LOGS}

mysql:
	@echo "Not yet"

team_dashboard:
	@echo "Not yet"

node:
	@echo "Not yet"

R-3.0:
	@echo "Not yet"

tests:
	nose tests
