#!/bin/bash

set -e

clear
source "./scripts/utils.sh"
echo $(date) " -- QuanTrade installation script"

# There is a lot to install, so run it as root
if [ $(whoami) != 'root' ]; then
    echo '** Error: This installation script needs root permissions'
    exit 1
fi


function install_packages() {
    echo "Installation of debian packages..."
    apt-get install git libzmq-dev r-base python2.7 mysql-server libmysqlclient-dev python-pip python-dev curl ruby1.9.3
    pip install pip-tools
}


function install_zipline() {
    if [ $1 == "dev" ]; then
        #TODO 
        #pip install zipline
        #Patch zipline !
    else
        if [ ! -d "../zipline" ]; then
            echo "Cloning and installing custom zipline project"
            git clone https://github.com/Gusabi/zipline ../zipline
            #FIXME Error: numpy not found..., so quick fix is to install it from Pypi before
            pip install numpy
            python ../zipline/setup.py install
        else
            log "Zipline already installed"
        fi
    fi
}


function setup_env() {
    echo "Environment setup"
    if [ ! -d "$HOME/.quantrade" ]; then
        echo "Creating project configuraiton directory: ~/.quantrade"
        mkdir -p $HOME/.quantrade/log
    fi
    echo "Copying configuration file templates..."
    echo "Note: do not forget to custom them at the end of the script"
    cp config/templates/local.tpl $HOME/.quantrade/local.sh
    cp config/templates/default.tpl $HOME/.quantrade/default.json
    cp config/templates/shiny-server.tpl $HOME/.quantrade/shiny-server.config

    echo "Writting in ~/.bashrc for permanent automatic environment load"
    echo "source $HOME/.quantrade/local.sh" >> $HOME/.bashrc

    echo "Sourcing environment setup file."
    source $HOME/.quantrade/local.sh

    echo "Restoring user permission"
    chown -R $USER $HOME/.quantrade
    chgrp -R $USER $HOME/.quantrade
}


function install_R() {
    echo "Updating R to 3.0"
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9
    echo "" >> /etc/apt/sources.list
    echo "## Last R Release" >> /etc/apt/sources.list
    echo "deb http://cran.irsn.fr/bin/linux/ubuntu raring/" >> /etc/apt/sources.list
    apt-get update
    apt-get install r-base
    #NOTE Never tested
    if [ -d "$HOME/R" -o -d "/usr/local/lib/R" -o -d "/usr/lib/R"]; then
        echo "R installation, assuming you already use it at least once"
        scripts/installation/install_r_packages.R
    else
        echo "No R libs directory found..."
        echo "Try to install manually one package:"
        echo "$ R"
        echo "R > install.packages('quantmod')"
        echo "Quit and then re-run: ./scripts/installation/install_r_packages.R"
    fi
}


function install_node() {
    #TODO Bad..., use n or nvm to install right version ? or github repos ?
    echo "Node.js installation"
    #echo "Downloading last release..."
    #wget http://nodejs.org/dist/v0.10.0/node-v0.10.0.tar.gz
    #tar xvzf node-v0.10.0.tar.gz && cd node-v0.10.0
    #./configure
    #make
    #make install
    echo "Installing node version manager (nvm)"
    if [ ! -d "$HOME/.nvm" ]; then
        curl https://raw.github.com/creationix/nvm/master/install.sh | sh
        source $HOME/.nvm/nvm.sh
    fi
    nvm install 0.10.7
    nvm use 0.10.7

    #FIXME Those commands are ran as root, eaccess problem then ?
    log "Handling permisisons"
    chown -R $USER $HOME/.npm
    chown -R $USER $HOME/.nvm

    # Cool version
    #git clone git://github.com/creationix/nvm.git $HOME/.nvm
    #NOTE Assume bash shell, use $SHELL
    #echo "source $HOME/.nvm/nvm.sh" >> $HOME/.bashrc
    #$HOME/nvm/nvm.sh install  0.10
    echo "" >> $HOME/.bashrc
    echo "# Node management" >> $HOME/.bashrc
    echo "export NODE_PATH=$HOME/.nvm/v0.10.7/lib/node_modules" >> $HOME/.bashrc
    echo "nvm use 0.10.7" >> $HOME/.bashrc
    echo "[[ -r $NVM_DIR/bash_completion ]] && . $NVM_DIR/bash_completion" >> $HOME/.bashrc

    #FIXME Deprecated
    echo "Node modules for QuanTrade installation, locally"
    cd server
    npm install -g
}


function setup_mysql() {
    echo "Setting up mysql quantrade database"
    mysql < ./scripts/installation/createdb.sql
    #NOTE Generate the script from a template ? (user and password field)
    ./scripts/database_manager.py -c
    log "Feeding database with US stocks"
    ./scripts/database_manager.py -a ./data/dump_sql.csv
    log "Feeding database with cac40 stocks"
    ./scripts/database_manager.py -a ./data/cac40.csv
}


function install_dependencies() {
    install_packages
    install_zipline

    echo "Installing dependances with pip..."
    ./scripts/installation/ordered_pip.sh ./scripts/installation/requirements.txt

    install_R
    install_node
}


function install_team_dashboard() {
    apt-get install libxslt1-dev libxml2-dev
    gem install bundler
    if [ ! -d "../team_dashboard" ]; then
        log "Cloning and installing team dashboard project"
        git clone git://github.com/fdietz/team_dashboard.git ../team_dashboard
        cd ../team_dashboard
        #FIXME libxml-ruby, ~> 2.6.0 and not 2.3.3
        log "Installing gem dependencies"
        bundle install
        cp config/database.example.yml config/database.yml
        log "Building database"
        rake db:create && rake db:migrate
        rake populate
    else
        log "Team dashboard already installed"
    fi
}


if [ $# -eq 0 ]; then
    setup_env
    install_dependencies
    #TODO Optional installation ?
    install_team_dashboard
    echo "Now edit ~/.quantrade/local.sh and ~/.quantrade/default.json to suit your environment"
else
    if [ $1 == "database" ]; then
        setup_mysql
    fi
fi

