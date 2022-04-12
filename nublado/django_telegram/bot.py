import os
import datetime
import pytz
import logging

from core.utils import remove_lead_and_trail_slash
from telegram import ParseMode, Update
from telegram.ext import Defaults, ExtBot as TelegramBot, Updater, CommandHandler, Dispatcher

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django')


class Bot(object):
    def __init__(self, token: str):
        self.token = token
        defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
        self.telegram_bot = TelegramBot(
            self.token,
            defaults=defaults
        )
        self.updater = None
        self.dispatcher = None
        self.job_queue = None

        dt = settings.DJANGO_TELEGRAM
        if dt['mode'] == settings.BOT_MODE_POLLING:
            self.updater = Updater(
                self.token,
                use_context=True
            )
            self.job_queue = self.updater.job_queue
            self.dispatcher = self.updater.dispatcher
        elif dt['mode'] == settings.BOT_MODE_WEBHOOK:
            self.dispatcher = Dispatcher(self.telegram_bot, None)
        else:
            error_msg = "Bot mode must be in {} mode or {} mode.".format(
                settings.BOT_MODE_POLLING,
                settings.BOT_MODE_WEBHOOK
            )
            logger.error(error_msg)
            raise ImproperlyConfigured(error_msg)

    def start(self):
        dt = settings.DJANGO_TELEGRAM
        if dt['mode'] == settings.BOT_MODE_POLLING:
            logger.info("Bot mode: polling")
            self.updater.start_polling()
            self.updater.idle()
        elif dt['mode'] == settings.BOT_MODE_WEBHOOK:
            logger.info("Bot mode: webhooks")
            webhook_site = remove_lead_and_trail_slash(dt['webhook_site'])
            webhook_path = remove_lead_and_trail_slash(dt['webhook_path'])
            webhook_url = f"{webhook_site}/{webhook_path}/{self.token}/"
            self.telegram_bot.set_webhook(webhook_url)
        else:
            error_msg = "Bot mode must be in {} mode or {} mode.".format(
                settings.BOT_MODE_POLLING,
                settings.BOT_MODE_WEBHOOK
            )
            logger.error(error_msg)
            raise ImproperlyConfigured(error_msg)

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)

    def add_command_handler(self, command: str, func):
        handler = CommandHandler(command, func)
        self.add_handler(handler)

    # def schedule_daily_task(
    #     self,
    #     callback_func,
    #     hour=0,
    #     minute=0,
    #     tzinfo=pytz.timezone(settings.TIME_ZONE),
    #     days=(0, 1, 2, 3, 4, 5, 6),
    #     context=None,
    #     name=None,
    #     job_kwargs=None
    # ):
    #     self.job_queue.run_daily(
    #         callback_func,
    #         time=datetime.time(
    #             hour=hour,
    #             minute=minute,
    #             tzinfo=tzinfo
    #         ),
    #         days=days,
    #         context=context,
    #         name=name, 
    #         job_kwargs=job_kwargs
    #     )
