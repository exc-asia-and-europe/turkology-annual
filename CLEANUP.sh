#!/usr/bin/env bash
# Deletes deprecated session data from the database. Needs to be run regularly (e.g. via daily cron job).

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/virtualenv/bin/activate
export PYTHON=$DIR/virtualenv/bin/python
export PYTHONPATH=$DIR

# --insecure is set so that static files (images, css, ...) are served. Ideally, static files would be served by a static file server such as Apache
$PYTHON $DIR/ta_online/manage.py cleanup
