from telegram import Update
from telegram.ext import CallbackContext

from django.conf import settings

from django_telegram.bot_utils.chat_actions import send_typing_action
from django_telegram.bot_utils.user_status import (
    restricted_group_owner,
    restricted_group_member,
    restricted_group_chat
)

# To do:Verify that  bot is in group.
GROUP_ID = settings.NUBLADO_GROUP_ID


@send_typing_action
@restricted_group_member
def start(update: Update, context: CallbackContext) -> None:
    """Send a message and prompt a reply on start."""
    user = update.effective_user
    bot_name = context.bot.first_name
    message = "Hello, {}. {} has started.".format(
        user.mention_markdown(),
        bot_name
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


@send_typing_action
@restricted_group_owner
def echo(update: Update, context: CallbackContext) -> None:
    """Echo a message to the group."""
    message = " ".join(context.args)
    context.bot.send_message(
        chat_id=GROUP_ID,
        text=message
    )


@send_typing_action
@restricted_group_member
def reverse_text(update: Update, context: CallbackContext) -> None:
    """Reverse the text provided as an argument and display it."""
    if context.args:
        message = " ".join(context.args)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message[::-1]
        )
