import json
import logging

from telegram import Update
from telegram.error import TelegramError

from django.http import Http404, JsonResponse
from django.views import View

from .apps import TelegramBotConfig

logger = logging.getLogger('django')


class BotWebhookView(View):
    def post(self, request, *args, **kwargs):
        token = request.kwargs['token']
        bot = TelegramBotConfig.registry.get_bot(token)

        if bot is not None:
            telegram_bot = bot.telegram_bot
            dispatcher = bot.dispatcher

            try:
                data = json.loads(request.body.decode('utf-8'))
            except:
                logger.warn("Telegram bot <{}> invalid request : {}".format(
                    telegram_bot.username,
                    repr(request))
                )
                raise Http404

            try:
                update = Update.de_json(data, telegram_bot)
                dispatcher.process_update(update)
                logger.debug("Bot <{}> : Processed update {}".format(
                    telegram_bot.username,
                    update
                ))
            except TelegramError as te:
                logger.warn("Bot <{}> : Error was raised while processing Update.".format(
                    telegram_bot.username
                ))
                dispatcher.dispatch_error(update, te)

            return JsonResponse()
        else:
            raise Http404
