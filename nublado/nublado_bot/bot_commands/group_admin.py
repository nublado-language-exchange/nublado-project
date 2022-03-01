import logging

from telegram import Update, User as TelegramUser
from telegram.ext import (
    CallbackContext, MessageHandler, Filters
)
from telegram.error import TelegramError

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.bot_utils.chat_actions import (
    send_typing_action
)
from django_telegram.bot_utils.user_utils import get_username_or_name
from django_telegram.bot_utils.user_status import (
    restricted_group_owner
)
from django_telegram.models import TelegramGroupMember

logger = logging.getLogger('django')

GROUP_ID = settings.NUBLADO_GROUP_ID


@send_typing_action
@restricted_group_owner
def update_group_members(update: Update, context: CallbackContext) -> None:
    member_list = []
    group_members = TelegramGroupMember.objects.filter(group_id=GROUP_ID)

    for member in group_members:
        user_id = member.user_id
        try:
            chat_member = context.bot.get_chat_member(
                GROUP_ID, user_id
            )
            user = chat_member.user
            name = get_username_or_name(user)
            member_list.append("*{}*".format(name))
        except TelegramError:
            logger.info("User id {} not in group {}".format(user_id, GROUP_ID))

    message = _("*Members*\n{member_list}").format(
        member_list="\n".join(member_list)
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


def member_join(update: Update, context: CallbackContext) -> None:
    if update.message.new_chat_members:
        for user in update.message.new_chat_members:
            name = get_username_or_name(user)
            message = f"*{name}* has appeared."
            context.bot.send_message(
                chat_id=GROUP_ID,
                text=message
            )


def member_exit(update: Update, context: CallbackContext) -> None:
    if update.message.left_chat_member:
        user = update.message.left_chat_member
        name = get_username_or_name(user)
        message = f"*{name}* has disappeared."
        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message
        )


member_join_handler = MessageHandler(
    Filters.status_update.new_chat_members,
    member_join
)


member_exit_handler = MessageHandler(
    Filters.status_update.left_chat_member,
    member_exit
)
