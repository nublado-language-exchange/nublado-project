release: python manage.py migrate
web: gunicorn config.wsgi --workers $WEB_CONCURRENCY --pythonpath $PYTHONPATH --log-file -
worker: python manage.py runbot nubladobot
