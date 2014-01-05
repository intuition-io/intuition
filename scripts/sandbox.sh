#! /bin/bash

if [ -n "$1" ]; then
  image=$1
else
  image="hivetech/lab"
fi

echo "launching sandbox container..."
echo "Tips: in hivetech/lab box, prototype user has a full development \
  environment configured (password: proto)"

docker run -i -t \
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
  -name sandbox ${image} bash
