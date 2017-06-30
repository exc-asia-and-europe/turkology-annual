#!/usr/bin/env bash
source virtualenv/bin/activate
export PYTHON=virtualenv/bin/python
export PYTHONPATH=.

# --insecure is set so that static files (images, css, ...) are served. Ideally, static files would be served by a static file server such as Apache
$PYTHON ta_online/manage.py runserver 0.0.0.0:8089 --insecure
