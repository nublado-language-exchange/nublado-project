import os
import datetime
import pytz
import logging

from telegram import Bot as TelegramBot, ParseMode, Update
from telegram.ext import Defaults, Updater, CommandHandler

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django')


class Bot(object):
    def __init__(self, token: str):
        self.token = token
        self.telegram_bot = TelegramBot(self.token)
        defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
        self.updater = Updater(
            self.token,
            use_context=True,
            defaults=defaults
        )
        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

    def start(self):
        dt = settings.DJANGO_TELEGRAM

        if dt['mode'] == settings.BOT_MODE_POLLING:
            # Polling
            logger.info("Bot mode: polling")
            self.updater.start_polling()
            self.updater.idle()
        elif dt['mode'] == settings.BOT_MODE_WEBHOOK:
            # Webook
            logger.info("Bot mode: webhooks")

            webhook_site = dt['webhook_site']
            if webhook_site.endswith("/"):
                webhook_site = webhook_site[:-1]

            webhook_path = dt['webhook_path']
            if webhook_path.startswith("/"):
                webhook_path = webhook_path[1:]
            if webhook_path.endswith("/"):
                webhook_path = webhook_path[:-1]

            url_path = f"{webhook_path}/{self.token}"
            webhook_url = f"{webhook_site}/{url_path}"

            self.updater.start_webhook(
                listen="0.0.0.0",
                port=dt['webhook_port'],
                url_path=url_path,
                webhook_url = webhook_url
            )
            self.updater.idle()
        else:
            error_msg = "Bot mode must be {} or {}.".format(
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

    def schedule_daily_task(
        self,
        callback_func,
        hour=0,
        minute=0,
        tzinfo=pytz.timezone(settings.TIME_ZONE),
        days=(0, 1, 2, 3, 4, 5, 6),
        context=None,
        name=None,
        job_kwargs=None
    ):
        self.job_queue.run_daily(
            callback_func,
            time=datetime.time(
                hour=hour,
                minute=minute,
                tzinfo=tzinfo
            ),
            days=days,
            context=context,
            name=name, 
            job_kwargs=job_kwargs
        )
