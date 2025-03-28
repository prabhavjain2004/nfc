#!/bin/bash

# Set Python path
export PATH="/opt/conda/bin:$PATH"

echo "Python version:"
python --version

echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Skip migrations during build as they should be handled during development
# python manage.py makemigrations
# python manage.py migrate
