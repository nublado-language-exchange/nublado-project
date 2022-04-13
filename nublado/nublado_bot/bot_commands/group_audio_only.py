import logging

from telegram import Update
from telegram.constants import CHATMEMBER_CREATOR
from telegram.ext import (
    CallbackContext, MessageHandler, Filters
)

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.apps import DjangoTelegramConfig
from django_telegram.bot_utils.chat_actions import (
    send_typing_action
)
from django_telegram.bot_utils.user_status import (
    restricted_group_member
)

logger = logging.getLogger('django')

NUBLADO_BOT_ID = 5075400666
GROUP_ID = settings.NUBLADO_GROUP_ID
AUDIO_ONLY_ON = "on"
AUDIO_ONLY_OFF = "off"
HANDLER_GROUP = 1

msg_audio_only = _("Audio-only mode is on. Please send a voice message.")
msg_audio_only_activated = _("Audio-only mode has been activated.")
msg_audio_only_already_activated = _("Audio-only mode is already activated.")
msg_audio_only_deactivated = _("Audio-only mode has been deactivated.")
msg_audio_only_not_activated = _("Audio-only mode is not activated.")


@send_typing_action
@restricted_group_member(group_id=GROUP_ID, member_status=CHATMEMBER_CREATOR)
def audio_only(update: Update, context: CallbackContext):
    if len(context.args) >= 1:
        logger.info("SHIT")
        dispatcher = context.dispatcher
        logger.info(dispatcher)
        if context.args[0] == AUDIO_ONLY_ON:
            dispatcher.add_handler(audio_only_handler, HANDLER_GROUP)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg_audio_only_activated
            )
        elif context.args[0] == AUDIO_ONLY_OFF:
            try:
                dispatcher.remove_handler(audio_only_handler, HANDLER_GROUP)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=msg_audio_only_deactivated
                )
            except:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=msg_audio_only_not_activated
                )
        else:
            pass


def remove_message(update: Update, context: CallbackContext):
    message_id = update.message.message_id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg_audio_only
    )
    try:
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=message_id
        )
        logger.info("Message deleted")
    except:
        logger.error("Message to delete not found.")


audio_only_handler = MessageHandler(
    (~ Filters.voice & ~ Filters.photo & ~ Filters.command & ~ Filters.via_bot(NUBLADO_BOT_ID)),
    remove_message
)