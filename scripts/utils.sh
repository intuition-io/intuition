#! /bin/bash
#
# utils.sh
# Copyright (C) 2013 xavier <xavier@laptop-300E5A>
#
# Distributed under terms of the MIT license.
#
#FIXME Those methods don't detect ls command, check in /usr/lib ?

#dpkg --get-selections | grep "^python$"


function log () {
  printf "\r\033[00;36m  [ \033[00;34m..\033[00;36m ] $1\033[0m\n"
}


success () {
  printf "\r\033[00;36m  [ \033[00;32mOK\033[00;36m ] $1\033[0m\n"
}


fail () {
  printf "\r\033[00;36m  [\033[00;31mFAIL\033[00;36m] $1\033[0m\n"
  echo ''
  exit
}


function die()
{
    echo "${@}"
    exit 1
}


link_files () {
  ln -s $1 $2
  success "linked $1 to $2"
}


function is_installed () {
    dpkg -s "$1" >/dev/null 2>&1 && {
        return 1
    } || {
        return 0
    }
}


# http://git-scm.com/book/fr/Git-sur-le-serveur-Installation-de-Git-sur-un-serveur
# Initially: Create a repo on the server and clone it on the server as well for new app
# Pushing: (github hook) update git server and the clone
function create_git_app () {
    git clone --bare --shared $1 $1.git
    scp -r $1.git xavier@192.168.0.17:/home/xavier/git-server
}


function usage () {
    log "Checking if $1 is installed"
    if is_installed $1; then
        fail "$1 Not installed"
    else
        success "$1 installed"
    fi
}


# pip dev state upgrade: pip install --upgrade https://github.com/jkbr/httpie/tarball/master
