#!/bin/bash

set -e

# Create the build/static folder if it doesn't exist
mkdir -p build/static

# Continue with the rest of the build script
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate