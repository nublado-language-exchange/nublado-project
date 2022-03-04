import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger('django')


class BotNotesConfig(AppConfig):
    name = "bot_notes"