#!/bin/sh

#if [ ! -d "migrations/versions" ]; then
#    flask db init
#fi

#while [ ! -d "migrations/versions" ]; do
#  sleep 10
#done

gunicorn -b :2000 main:main_app --workers 1 --threads 8 --timeout 0 --log-level debug --reload
