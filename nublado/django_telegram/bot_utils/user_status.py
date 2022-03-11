import logging
from functools import wraps

from telegram import Update, Bot
from telegram.utils.helpers import escape_markdown
from telegram.constants import (
    CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR, CHATMEMBER_MEMBER,
    CHAT_GROUP, CHAT_SUPERGROUP
)
from telegram.ext import CallbackContext

from django.conf import settings

logger = logging.getLogger('django')

GROUP_MEMBERS = [
    CHATMEMBER_CREATOR,
    CHATMEMBER_ADMINISTRATOR,
    CHATMEMBER_MEMBER
]

GROUP_TYPES = [
    CHAT_GROUP,
    CHAT_SUPERGROUP
]

BOTS = settings.DJANGO_TELEGRAM['bots']


def get_group_member(bot: Bot, user_id: int, group_id: int):
    try:
        chat_member = bot.get_chat_member(
            group_id, user_id
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
        return False


def is_group(bot: Bot, chat_id: int, group_id: int) -> bool:
    """Returns whether chat is a specific group chat by id"""
    try:
        chat = bot.get_chat(chat_id)
        return chat.type in GROUP_TYPES and chat_id == group_id
    except:
        return False


def is_group_owner(bot: Bot, user_id: int, group_id: int) -> bool:
    chat_member = get_group_member(bot, user_id, group_id)
    return bool(chat_member) and chat_member.status and chat_member.status == CHATMEMBER_CREATOR


def is_group_member(bot: Bot, user_id: int, group_id: int) -> bool:
    chat_member = get_group_member(bot, user_id, group_id)
    return bool(chat_member) and chat_member.status and chat_member.status in GROUP_MEMBERS


def is_in_sudo_list(bot: Bot, user_id: int) -> bool:
    try:
        sudo_list = BOTS[bot.token]['sudo_list']
    except:
        return False
    return user_id in sudo_list and is_group_member(bot, user_id)


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
        if not is_group_chat(context.bot, chat_id):
            logger.warning(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
            return
        else:
            return func(update, context)
    return wrapped


def restricted_group(group_id: int = None):
    """Restrict access to messages coming from specific group the bot belongs to."""
    def callable(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext):
            chat_id = update.effective_chat.id
            user = update.effective_user
            bot = context.bot
            if group_id:
                if not is_group(bot, chat_id, group_id):
                    logger.warning(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
                    return
                else:
                    return func(update, context)
            else:
                return 
        return wrapped
    return callable


def restricted_group_member(group_id:int = None):
    """Restrict access to commands to group members."""
    def callable(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext):
            user = update.effective_user
            bot = context.bot
            if group_id:
                if not is_group_member(context.bot, user.id, group_id):
                    logger.warning(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
                    send_non_member_message(update, bot, group_id)
                    return
                else:
                    return func(update, context)
            else:
                return
        return wrapped
    return callable


def restricted_group_owner(group_id:int = None):
    """Restrict access to commands to group owner."""
    def callable(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext):
            user = update.effective_user
            bot = context.bot
            if group_id:
                if not is_group_owner(bot, user.id, group_id):
                    logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
                    return
            else:
                return
            return func(update, context)
        return wrapped
    return callable


def restricted_sudo_list(group_id: int = None):
    """Restrict access to commands to user ids in SUDO_LIST."""
    def callable(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext):
            user = update.effective_user
            bot = context.bot
            if group_id:
                if not is_group_member(bot, user.id, group_id):
                    logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
                    send_non_member_message(update, context, group_id)
                    return
                if not is_in_sudo_list(bot, user.id):
                    logger.info(f"Unauthorized access: {func.__name__} - {user.id} - {user.username}.")
                    return
            else:
                return
            return func(update, context)
        return wrapped
    return callable