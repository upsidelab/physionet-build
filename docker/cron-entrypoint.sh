#!/bin/bash

set -e

mkdir -p $STATIC_ROOT/published-projects
mkdir -p $MEDIA_ROOT/{active-projects,archived-projects,credential-applications,published-projects,users}

./docker/wait-for-it.sh $DB_HOST:5432

python physionet-django/manage.py migrate

chgrp root /etc/cron.d/$FILE_NAME
chown root /etc/cron.d/$FILE_NAME
chmod 644 /etc/cron.d/$FILE_NAME
service cron start
echo "Infinite sleep"
exec /bin/sh -c "trap : TERM INT; (while true; do sleep 86400; done) & wait"
