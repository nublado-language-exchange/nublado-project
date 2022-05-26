import logging

from telegram import Update
from telegram.ext import (
    CallbackContext, MessageHandler, Filters
)

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.functions.chat_actions import (
    send_typing_action
)
from django_telegram.functions.group import (
    restricted_group_member
)
from group_points.bot_commands import (
    add_points as cmd_add_points,
    remove_points as cmd_remove_points
)

logger = logging.getLogger('django')

ADD_POINTS_CHAR = '+'
ADD_POINTS_REGEX = '^[' + ADD_POINTS_CHAR + '][\s\S]*$'
REMOVE_POINTS_CHAR = '-'
REMOVE_POINTS_REGEX = '^[' + REMOVE_POINTS_CHAR + '][\s\S]*$'
GROUP_ID = settings.NUBLADO_GROUP_ID

# Command handlers 
@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def add_points(update: Update, context: CallbackContext) -> None:
    cmd_add_points(update, context, GROUP_ID)


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def remove_points(update: Update, context: CallbackContext) -> None:
    cmd_remove_points(update, context, GROUP_ID)


# Message handlers to listen for triggers to add or remove points.
add_points_handler = MessageHandler(
    (Filters.regex(ADD_POINTS_REGEX) & Filters.reply),
    add_points
)


remove_points_handler = MessageHandler(
    (Filters.regex(REMOVE_POINTS_REGEX) & Filters.reply),
    remove_points
)
