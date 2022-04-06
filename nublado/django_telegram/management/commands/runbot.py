from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ...apps import DjangoTelegramConfig


class Command(BaseCommand):
    help = "Initialize and run Telegram bots."

    def add_arguments(self, parser):
        parser.add_argument('bot_ids', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['bot_ids']:
            for bot_id in options['bot_ids']:
                try:
                    bot_token = settings.DJANGO_TELEGRAM['bots'][bot_id]['token']
                except:
                    error = "Bot id {} doesn't exist or is improperly configured.".format(bot_id)
                    raise CommandError(error)

                bot = DjangoTelegramConfig.bot_registry.get_bot(bot_token)
                if bot:
                    bot.start()
        return