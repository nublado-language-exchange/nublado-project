from django.apps import AppConfig


class DjangoTelegramConfig(AppConfig):
    name = 'django_telegram'

    def ready(self):
        from . import signals