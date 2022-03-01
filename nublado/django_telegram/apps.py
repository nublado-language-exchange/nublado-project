from django.apps import AppConfig

from .bot import Bot


class BotRegistry:
    def __init__(self):
        self.bots = {}

    def add_bot(self, key: str, bot: Bot) -> None:
        self.bots[key] = bot

    def get_bot(self, key: str):
        return self.bots.get(key, None)


class DjangoTelegramConfig(AppConfig):
    name = 'django_telegram'
    bot_registry = None

    def ready(self):
        from . import signals
        DjangoTelegramConfig.bot_registry = BotRegistry()