import datetime as dt
import logging

from telegram import (
    Bot, Update, ChatPermissions,
    InlineKeyboardButton, InlineKeyboardMarkup
)

from telegram.ext import (
    CallbackContext, CallbackQueryHandler, MessageHandler, Filters
)
from telegram.error import TelegramError
from telegram.constants import CHATMEMBER_CREATOR

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.models import TelegramGroupMember
from django_telegram.bot_utils.chat_actions import (
    send_typing_action
)
from django_telegram.bot_utils.user_utils import get_username_or_name
from django_telegram.bot_utils.user_status import (
    restricted_group_member
)
from django_telegram.models import TelegramGroupMember
from language_days.functions import set_language_day_locale

logger = logging.getLogger('django')

GROUP_ID = settings.NUBLADO_GROUP_ID

# Callback data
AGREE_BTN_CALLBACK_DATA = "chat_member_welcome_agree"

# Translated strings.
MSG_AGREE = _("I agree.")
MSG_WELCOME = _(
    "Welcome to the group, {name}.\n\n" \
    "Please read the following rules and click the \"I agree\" button to participate.\n\n" \
    "*Rules (tentative)*\n" \
    "- Communicate in only English and Spanish.\n" \
    "- Don't harass other group members.\n" \
    "- Don't send private messages to other group members without their permission.\n" \
    "- Be a good example. There are people here learning your language. Help them out with corrections."
)
MSG_WELCOME_AGREED = _(
    "Welcome to the group, {name}.\n\n" \
    "We require new members to introduce themselves with a voice message within one day " \
    "of their joining. Failure to do so will result in your removal from the group.\n\n" \
    "We look forward to hearing from you."
)


def add_member(user_id, group_id):
    member_exists = TelegramGroupMember.objects.filter(
        group_id=group_id,
        user_id=user_id
    ).exists()
    if not member_exists:
        TelegramGroupMember.objects.create_group_member(
            group_id=group_id,
            user_id=user_id
        )


def remove_member(user_id, group_id):
    TelegramGroupMember.objects.filter(
        group_id=group_id,
        user_id=user_id
    ).delete()


def restrict_chat_member(bot: Bot, user_id: int, chat_id: int):
    try:
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False  
        )
        bot.restrict_chat_member(
            user_id=user_id,
            chat_id=chat_id,
            permissions=permissions 
        )
        return True
    except:
        logger.error("Error disactivating member " + user_id)
        return False


def unrestrict_chat_member(bot: Bot, user_id: int, chat_id: int, interval_minutes: int = 2):
    """Restore restricted chat member to group's default member permissions."""
    try:
        chat = bot.get_chat(chat_id)
        permissions = chat.permissions
        date_now = dt.datetime.now()
        date_until = date_now + dt.timedelta(minutes=interval_minutes)
        bot.restrict_chat_member(
            user_id=user_id,
            chat_id=chat_id,
            permissions=permissions,
            until_date=date_until
        )
        return True
    except:
        logger.error("Error unrestricting member " + user_id)
        return False


@send_typing_action
@restricted_group_member(group_id=GROUP_ID, member_status=CHATMEMBER_CREATOR)
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
        set_language_day_locale()
        for user in update.message.new_chat_members:
            # Add user to db
            add_member(user.id, GROUP_ID)
            # Mute user until he or she presses the "I agree" button.
            restrict_chat_member(context.bot, user.id, GROUP_ID)
            message = _(MSG_WELCOME).format(
                name=user.mention_markdown()
            )
            callback_data = AGREE_BTN_CALLBACK_DATA + " " + str(user.id)
            keyboard = [
                [
                    InlineKeyboardButton(
                        _(MSG_AGREE),
                        callback_data=callback_data
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                text=message,
                chat_id=GROUP_ID,
                reply_markup=reply_markup
            )
        # Delete service message.
        try:
            context.bot.delete_message(
                message_id=update.message.message_id,
                chat_id=update.effective_chat.id
            )
        except:
            pass


def member_exit(update: Update, context: CallbackContext) -> None:
    if update.message.left_chat_member:
        user = update.message.left_chat_member
        # Delete member from db.
        remove_member(user.id, GROUP_ID)
        # Delete service message.
        try:
            context.bot.delete_message(
                message_id=update.message.message_id,
                chat_id=update.effective_chat.id
            )
        except:
            pass


# Listen for when new members join group.
member_join_handler = MessageHandler(
    Filters.status_update.new_chat_members,
    member_join
)


# Listen for when members leave group.
member_exit_handler = MessageHandler(
    Filters.status_update.left_chat_member,
    member_exit
)


def chat_member_welcome_agree(
    bot: Bot, user_id: int, chat_id: int, welcome_message_id: int = None
) -> None:
    unrestrict_chat_member(bot, user_id, chat_id)
    if welcome_message_id:
        try:
            bot.delete_message(
                message_id=welcome_message_id,
                chat_id=chat_id
            )
        except:
            logger.error("Error tring to delete  welcome message " + welcome_message_id)
    try:
        member = bot.get_chat_member(chat_id, user_id)
        message = _(MSG_WELCOME_AGREED).format(
            name=member.user.mention_markdown()
        )
        bot.send_message(
            chat_id=chat_id,
            text=message
        )
    except:
        pass


def welcome_button_handler_c(update: Update, context: CallbackContext) -> None:
    """Parse the CallbackQuery and perform corresponding actions."""
    query = update.callback_query
    query.answer()
    data = query.data.split(" ")
    if len(data) >= 2:
        if data[0] == AGREE_BTN_CALLBACK_DATA:
            user_id = int(data[1])
            # Check if effective user is the user that clicked the button.
            if update.effective_user.id == user_id:
                chat_member_welcome_agree(
                    context.bot,
                    user_id,
                    GROUP_ID,
                    query.message.message_id
                )
            else:
                logger.info("Another user clicked the welcome buttton.")
    else:
        query.edit_message_text(text=f"Selected option: {query.data}")


welcome_button_handler = CallbackQueryHandler(
    welcome_button_handler_c,
    pattern='^' + AGREE_BTN_CALLBACK_DATA
)
