#! /bin/bash


# Oten used parameters
container_name="docker_intuition"
image="hivetech/intuition"
context="mongodb::192.168.0.12:27017/backtestNasdaq"


docker run -rm \
  -e PUSHBULLET_API_KEY=$PUSHBULLET_API_KEY \
  -e QUANDL_API_KEY=$QUANDL_API_KEY \
  -e MAILGUN_API_KEY=$MAILGUN_API_KEY \
  -e TRUEFX_API=$TRUEFX_API \
  -e DB_HOST=$DB_HOST \
  -e DB_PORT=$DB_PORT \
  -e DB_NAME=$DB_NAME \
  -e MSG_HOST=$MSG_HOST \
  -e MSG_PORT=$MSG_PORT \
  -e LOG=debug \
  -e LANGUAGE="fr_FR.UTF-8" \
  -e LANG="fr_FR.UTF-8" \
  -e LC_ALL="fr_FR.UTF-8" \
  $@
