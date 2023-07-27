#!/bin/sh

#if [ ! -d "migrations/versions" ]; then
#    flask db init
#fi

#while [ ! -d "migrations/versions" ]; do
#  sleep 10
#done

gunicorn -b :2000 main:main_app --reload
