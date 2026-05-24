web: cd newsproject && gunicorn newsproject.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 60
release: cd newsproject && python manage.py migrate && python manage.py collectstatic --noinput
