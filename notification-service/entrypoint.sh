#!/bin/bash

#python main.py
gunicorn -b :80 -w 4 main:app