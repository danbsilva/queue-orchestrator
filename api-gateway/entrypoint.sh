#!/bin/sh

if [ ! -d "migrations/versions" ]; then
    flask db init
fi

gunicorn -b :2000 -w 4 main:app
