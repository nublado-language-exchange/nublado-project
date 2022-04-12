import json
import logging

from telegram import Update
from telegram.error import TelegramError

from django.http import Http404, JsonResponse
from django.views import View

from .apps import DjangoTelegramConfig

logger = logging.getLogger('django')


class BotWebhookView(View):
    def post(self, request, *args, **kwargs):
        token = kwargs['token']
        bot = DjangoTelegramConfig.bot_registry.get_bot(token)

        if bot is not None:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except:
                logger.warn("Telegram bot <{}> invalid request : {}".format(
                    bot.telegram_bot.username,
                    repr(request))
                )
                raise Http404

            try:
                update = Update.de_json(data, bot.telegram_bot)
                bot.dispatcher.process_update(update)
                logger.debug("Bot <{}> : Processed update {}".format(
                    bot.telegram_bot.username,
                    update
                ))
            except TelegramError as te:
                logger.warn("Bot <{}> : Error was raised while processing Update.".format(
                    bot.telegram_bot.username
                ))
                bot.dispatcher.dispatch_error(update, te)

            return JsonResponse({})
        else:
            raise Http404
