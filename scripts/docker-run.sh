#! /bin/bash


image="hivetech/intuition"
container_name="trading_box"

if [ -n "$1" ]; then
  context=$1
else
  context="mongodb::192.168.0.12:27017/backtestNasdaq"
fi

docker run \
  -e PUSHBULLET_API_KEY=$PUSHBULLET_API_KEY \
  -e QUANDL_API_KEY=$QUANDL_API_KEY \
  -e MAILGUN_API_KEY=$MAILGUN_API_KEY \
  -e TRUEFX_API=$TRUEFX_API \
  -e DB_HOST=$DB_HOST \
  -e DB_PORT=$DB_PORT \
  -e DB_NAME=$DB_NAME \
  -e LOG=debug \
  -e LANGUAGE="fr_FR.UTF-8" \
  -e LANG="fr_FR.UTF-8" \
  -e LC_ALL="fr_FR.UTF-8" \
  -name ${container_name} ${image} \
  intuition --context ${context} --showlog --id ${container_name}
