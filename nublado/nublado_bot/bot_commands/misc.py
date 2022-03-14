from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import CHATMEMBER_CREATOR

from django.conf import settings

from django_telegram.bot_utils.chat_actions import send_typing_action
from django_telegram.bot_utils.user_status import (
    restricted_group_member
)

# To do:Verify that  bot is in group.
GROUP_ID = settings.NUBLADO_GROUP_ID


@restricted_group_member(group_id=GROUP_ID, group_chat=False)
@send_typing_action
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


@restricted_group_member(group_id=GROUP_ID, member_status=CHATMEMBER_CREATOR)
@send_typing_action
def echo(update: Update, context: CallbackContext) -> None:
    """Echo a message to the group."""
    message = " ".join(context.args)
    context.bot.send_message(
        chat_id=GROUP_ID,
        text=message
    )


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def reverse_text(update: Update, context: CallbackContext) -> None:
    """Reverse the text provided as an argument and display it."""
    if context.args:
        message = " ".join(context.args)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message[::-1]
        )
