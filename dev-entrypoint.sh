#!/bin/bash

set -e

echo "Environment: $ENVIRONMENT"

./wait-for-it.sh db:5432

poetry run /code/physionet-django/manage.py migrate

poetry run $@
