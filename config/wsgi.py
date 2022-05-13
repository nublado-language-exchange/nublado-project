import os
import logging

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

logger = logging.getLogger('django')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = get_wsgi_application()