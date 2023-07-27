#!/bin/bash

#python main.py
gunicorn -b :80 main:main_app