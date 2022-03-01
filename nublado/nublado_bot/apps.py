import logging

from django.conf import settings
from django.apps import AppConfig

from telegram_bot.apps import TelegramBotConfig
from telegram_bot.bot import Bot

logger = logging.getLogger('django')


class NubladoBotConfig(AppConfig):
    name = 'nublado_bot'
    bot_key = settings.NUBLADO_BOT_TOKEN

    def ready(self):
        from .bot_commands.group_admin import(
            update_group_members,
            member_join_handler,
            member_exit_handler
        )
        from .bot_commands.misc import (
            start, echo, reverse_text
        )
        from .bot_commands.language_days import (
            schedule, language_day, initiate_language_day_c,
            initiate_language_day
        )
        from .bot_commands.group_points import (
            group_top_points, add_points_handler, remove_points_handler
        )

        bot_registry = TelegramBotConfig.registry
        bot = Bot(settings.NUBLADO_BOT_TOKEN)

        # Register handlers
        # group_admin
        bot.add_command_handler('update_group_members', update_group_members)
        # bot.add_handler(member_join_handler)
        # bot.add_handler(member_exit_handler)
        # misc
        bot.add_command_handler('start', start)
        bot.add_command_handler('reverse', reverse_text)
        bot.add_command_handler('echo', echo)
        # language_days
        bot.add_command_handler('schedule', schedule)
        bot.add_command_handler('language_day', language_day)
        bot.add_command_handler('initiate_language_day', initiate_language_day)
        bot.schedule_daily_task(
            initiate_language_day_c,
            hour=settings.LANGUAGE_DAY_HOUR_CHANGE,
            minute=settings.LANGUAGE_DAY_MINUTE_CHANGE,
            name="Initiate language day"         
        )
        # group_points
        bot.add_handler(add_points_handler)
        bot.add_handler(remove_points_handler)
        bot.add_command_handler('top_points', group_top_points)
        # Add the bot to the registry.
        bot_registry.add_bot(NubladoBotConfig.bot_key, bot)

