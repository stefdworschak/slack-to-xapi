#!/bin/bash
cd "$(dirname "$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)" )"  # cd into parent dir

docker-compose exec webapp ./manage.py test