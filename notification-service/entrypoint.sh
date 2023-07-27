#!/bin/bash

#python main.py
gunicorn -b :80 main:main_app --workers 1 --threads 8 --timeout 0 --log-level debug --reload