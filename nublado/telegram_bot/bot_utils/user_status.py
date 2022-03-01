import logging
from functools import wraps

from telegram import Update, Bot
from telegram.utils.helpers import escape_markdown
from telegram.constants import (
    CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR, CHATMEMBER_MEMBER
)
from telegram.ext import CallbackContext

from django.conf import settings

logger = logging.getLogger('django')

GROUP_MEMBERS = [
    CHATMEMBER_CREATOR,
    CHATMEMBER_ADMINISTRATOR,
    CHATMEMBER_MEMBER
]

BOTS = settings.DJANGO_TELEGRAM['bots']


def get_group_member(bot: Bot, user_id: int, group_id: int = None):
    try:
        if not group_id:
            group_id = BOTS[bot.token]['group_id']
        chat_member = bot.get_chat_member(
            group_id, user_id
        )
        return chat_member
    except:
        return None


def is_group_owner(bot: Bot, user_id: int) -> bool:
    chat_member = get_group_member(bot, user_id)
    return bool(chat_member) and chat_member.status and chat_member.status == CHATMEMBER_CREATOR


def is_group_member(bot: Bot, user_id: int) -> bool:
    chat_member = get_group_member(bot, user_id)
    return bool(chat_member) and chat_member.status and chat_member.status in GROUP_MEMBERS


def is_in_sudo_list(bot: Bot, user_id: int) -> bool:
    try:
        sudo_list = BOTS[bot.token]['sudo_list']
    except:
        return False

    return user_id in sudo_list and is_group_member(bot, user_id)


def send_non_member_message(update: Update, bot: Bot) -> None:
    try:
        group_id = BOTS[bot.token]['group_id']
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
def restricted_group_member(func):
    """Restrict access to commands to group members."""
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext):
        user = update.effective_user

        if not is_group_member(context.bot, user.id):
            logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            send_non_member_message(update, context.bot)
            return
        else:
            return func(update, context)

    return wrapped


def restricted_group_owner(func):
    """Restrict access to commands to group owner."""
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext):
        user = update.effective_user

        if not is_group_member(context.bot, user.id):
            logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            send_non_member_message(update, context)
            return

        if not is_group_owner(context.bot, user.id):
            logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            return

        return func(update, context)

    return wrapped


def restricted_sudo_list(func):
    """Restrict access to commands to user ids in SUDO_LIST."""
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext):
        user = update.effective_user

        if not is_group_member(context.bot, user.id):
            logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            send_non_member_message(update, context)
            return

        if not is_in_sudo_list(context.bot, user.id):
            logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            return

        return func(update, context)

    return wrapped