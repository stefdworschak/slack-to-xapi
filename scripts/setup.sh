#!/bin/bash
cd "$(dirname "$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)" )"  # cd into parent dir
SEED='./seed/xapi.json'

docker-compose exec webapp python3 manage.py makemigrations
docker-compose exec webapp python3 manage.py migrate

echo $SEED
docker-compose exec webapp python3 manage.py loaddata $SEED