#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Skip migrations during build as they should be handled during development
# python manage.py makemigrations
# python manage.py migrate
