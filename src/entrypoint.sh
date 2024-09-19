#!/bin/bash
set -e
python3 -m pip install --upgrade pip
python3 -m pip install -e .
python3 -m pip install -r requirements.txt
python3 -m gunicorn "quoteoftheday:app"
