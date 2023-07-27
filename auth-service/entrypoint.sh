#!/bin/sh

#if [ ! -d "migrations/versions" ]; then
#    flask db init
#fi

#while [ ! -d "migrations/versions" ]; do
#  sleep 10
#done

gunicorn -b :80 main:main_app
