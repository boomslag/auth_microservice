#!/bin/bash

set -e

# Specify the desired Python version
PYTHON_VERSION="3.9"

# Create the build/static folder if it doesn't exist
mkdir -p build/static

# Continue with the rest of the build script
python${PYTHON_VERSION} -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate