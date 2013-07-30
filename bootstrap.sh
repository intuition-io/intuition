#!/bin/bash
#NOTE With QUANTRADE_REPO set before installation this script could be generic

set -e
export DEBIAN_FRONTEND=noninteractive
export QUANTRADE_REPO=${QUANTRADE_REPO:-"https://github.com/Gusabi/ppQuanTrade.git"}

#TODO project=https://.../[].git

# A hack try for generic use, especially vagrant and docker compliant
if [[ "$HOME" == "/root" ]]; then
    ## We are in a vagrant box, at bootstrap
    export HOME="/home/vagrant"
    export USER="vagrant"
elif [[ "$HOME" == "/" ]]; then
    # We are in a docker (lxc ?) container
    export HOME="/root"
    export USER=$(whoami)
fi

LOGS="/tmp/quantrade.log"
echo "[bootstrap] logs stored in $LOGS"

# Run a full apt-get update first.
echo "[bootstrap] Updating apt-get caches..."
apt-get update 2>&1 >> "$LOGS"

# Install required packages
echo "[bootstrap] Installing git and make..."
apt-get -y --force-yes install git make 2>&1 >> "$LOGS"

# We assume if you are in a git repository this is probably this very project one
cd $HOME 
# The test makes it vagrant compliant (synced folders)
test -d ppQuanTrade || git clone $QUANTRADE_REPO
cd ppQuanTrade
#fi
make all

echo
echo "[bootstrap] Done ! Tune the configuration in $HOME/.quantrade"
