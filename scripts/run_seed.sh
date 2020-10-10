#!/bin/bash
cd "$(dirname "$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)" )"  # cd into parent dir
python3 manage.py loaddata $1