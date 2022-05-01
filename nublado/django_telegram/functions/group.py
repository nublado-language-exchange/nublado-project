import logging
import random
from functools import wraps

from telegram import Update, Bot
from telegram.utils.helpers import escape_markdown
from telegram.constants import (
    CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR, CHATMEMBER_MEMBER,
    CHAT_PRIVATE, CHAT_GROUP, CHAT_SUPERGROUP
)
from telegram.ext import CallbackContext

from django.conf import settings

from ..models import TelegramGroupMember

logger = logging.getLogger('django')

GROUP_MEMBERS = {
    CHATMEMBER_MEMBER: 1,
    CHATMEMBER_ADMINISTRATOR: 2,
    CHATMEMBER_CREATOR: 3
}
GROUP_TYPES = [
    CHAT_GROUP,
    CHAT_SUPERGROUP
]
BOTS = settings.DJANGO_TELEGRAM['bots']


def get_random_group_member(group_id: int):
    members = TelegramGroupMember.objects.filter(group_id=group_id)
    if len(members) > 0:
        index = random.randint(0, len(members) - 1)
        return members[index]
    else:
        return None


def get_chat_member(bot: Bot, user_id: int, chat_id: int):
    try:
        chat_member = bot.get_chat_member(
            chat_id, user_id
        )
        return chat_member
    except:
        return None


def is_group_chat(bot: Bot, chat_id: int) -> bool:
    """Return whether chat is a group chat."""
    try:
        chat = bot.get_chat(chat_id)
        return chat.type in GROUP_TYPES
    except:
        logger.warn(f"Chat {chat_id} isn't a group.")
        return False


def is_group(bot: Bot, chat_id: int, group_id: int) -> bool:
    """Returns whether chat is a specific group chat by id"""
    return is_group_chat(bot, chat_id) and chat_id == group_id


def is_member_status(
        bot: Bot,
        user_id: int,
        group_id: int,
        member_status: str = CHATMEMBER_MEMBER
):
    if member_status in GROUP_MEMBERS.keys():
        chat_member = get_chat_member(bot, user_id, group_id)
        if chat_member:
            if chat_member.status in GROUP_MEMBERS.keys():
                return GROUP_MEMBERS[chat_member.status] >= GROUP_MEMBERS[member_status]
            else:
                logger.warn("Chat member status not in GROUP_MEMBERS.")
                return False
        else:
            logger.warn("Non chat member.")
            return False
    else:
        logger.warn("Target member status not in GROUP_MEMBERS.")
        return False


def send_non_member_message(update: Update, bot: Bot, group_id: int) -> None:
    try:
        group = bot.get_chat(group_id)
        invite_link = escape_markdown(group.invite_link)
        message = f"This bot is exclusively for members of the group\n*{group.title}*." \
        f"\n\nCome join us!\n{invite_link}"
        bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
    except:
        return


# Decorators for command handlers
def restricted_group_chat(func):
    """Restrict access to messages coming from a group chat the bot belongs to."""
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user = update.effective_user
        if is_group_chat(context.bot, chat_id):
            return func(update, context)
        else:
            logger.warning(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            return
    return wrapped


def restricted_group_member(
        group_id: int,
        member_status: str = CHATMEMBER_MEMBER,
        group_chat: bool = True,
        private_chat: bool = True
):
    """Restrict access to a group's members determined by member status."""
    def callable(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext):
            chat_id = update.effective_chat.id
            user = update.effective_user
            bot = context.bot
            if is_member_status(bot, user.id, group_id, member_status):
                if group_chat and private_chat:
                    # The command can be executed in the group or in a private message with the bot.
                    if is_group(bot, chat_id, group_id) or chat_id == user.id:
                        return func(update, context)
                    else:
                        return
                elif group_chat:
                    # The command can only be executed in the group chat.
                    if is_group(bot, chat_id, group_id):
                        return func(update, context)
                    else:
                        return
                elif private_chat:
                    # The command can only be exectued in a private message with the bot.
                    if chat_id == user.id:
                        return func(update, context)
                    else:
                        return
                else:
                    return
            else:
                return
        return wrapped
    return callable