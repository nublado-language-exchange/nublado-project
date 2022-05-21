import logging

from telegram import Update
from telegram.ext import (
    CallbackContext, MessageHandler, Filters
)

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.functions.user import get_username_or_name
from django_telegram.functions.chat_actions import (
    send_typing_action
)
from django_telegram.functions.group import (
    get_chat_member, restricted_group_member
)
from django_telegram.models import TelegramGroupMember
from group_points.models import GroupMemberPoints
from language_days.functions import (
    set_language_day_locale,
)

logger = logging.getLogger('django')

ADD_POINTS_CHAR = '+'
ADD_POINTS_REGEX = '^[' + ADD_POINTS_CHAR + '][\s\S]*$'
REMOVE_POINTS_CHAR = '-'
REMOVE_POINTS_REGEX = '^[' + REMOVE_POINTS_CHAR + '][\s\S]*$'
POINT_NAME = _("magical trinket")
POINTS_NAME = _("magical trinkets")
TOP_POINTS_LIMIT = 10
GROUP_ID = settings.NUBLADO_GROUP_ID

# Translated messages
msg_no_give_points_bot = _("You can't give {points_name} to a bot.")
msg_no_take_points_bot = _("You can't take {points_name} from a bot.")
msg_no_give_points_self = _("You can't give {points_name} to yourself.")
msg_no_take_points_self = _("You can't take {points_name} from yourself.")
msg_give_points = _(
    "*{sender_name} ({sender_points})* has given some " + \
    "{points_name} to *{receiver_name} ({receiver_points})*."
)
msg_give_point = _(
    "*{sender_name} ({sender_points})* has given a " + \
    "{points_name} to *{receiver_name} ({receiver_points})*."
)
msg_take_points = _(
    "*{sender_name} ({sender_points})* has taken some " + \
    "{points_name} from *{receiver_name} ({receiver_points})*."
)
msg_take_point = _(
    "*{sender_name} ({sender_points})* has taken a " + \
    "{points_name} from *{receiver_name} ({receiver_points})*."
)


# Command handlers 
def get_group_member_points(user_id, group_id):
    """Get user's total points in group."""
    group_member, group_member_created = TelegramGroupMember.objects.get_or_create(
        group_id=group_id,
        user_id=user_id
    )
    member_points, member_points_created = GroupMemberPoints.objects.get_or_create(
        group_member_id=group_member.id
    )
    return member_points


def group_top_points(update: Update, context: CallbackContext) -> None:
    member_points = GroupMemberPoints.objects.get_group_top_points(
        GROUP_ID, TOP_POINTS_LIMIT
    )

    if member_points:
        top_points = []

        for member in member_points:
            points = member.points
            user_id = member.group_member.user_id
            chat_member = get_chat_member(context, user_id, GROUP_ID)

            if chat_member:
                user = chat_member.user
                logger.info(user)
                name = get_username_or_name(user)
                name_points = "*{points}: {name}*".format(
                    name=name,
                    points=points
                )
                top_points.append(name_points)

        message = _("*Top {point_name} rankings*\n{rankings_list}").format(
            point_name=_(POINT_NAME),
            rankings_list="\n".join(top_points)
        )
        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message
        )


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def add_points(update: Update, context: CallbackContext) -> None:
    # Check if the message is a reply to another message.
    if update.message.reply_to_message:
        set_language_day_locale()
        sender = update.effective_user
        sender_name = get_username_or_name(sender)
        receiver = update.message.reply_to_message.from_user
        receiver_name = get_username_or_name(receiver)

        # Check if the reply is to another member and not a bot or oneself.
        if not receiver.is_bot and sender != receiver:
            sender_points = get_group_member_points(sender.id, GROUP_ID)
            receiver_points = get_group_member_points(receiver.id, GROUP_ID)
            receiver_points.points += sender_points.point_increment
            receiver_points.save()

            if sender_points.point_increment > 1:
                message = _(msg_give_points).format(
                    sender_name=sender_name,
                    sender_points=sender_points.points,
                    points_name=_(POINTS_NAME),
                    receiver_name=receiver_name,
                    receiver_points=receiver_points.points
                )
            else:
                message = _(msg_give_point).format(
                    sender_name=sender_name,
                    sender_points=sender_points.points,
                    points_name=_(POINT_NAME),
                    receiver_name=receiver_name,
                    receiver_points=receiver_points.points
                )
        elif receiver.is_bot:
            message = _(msg_no_give_points_bot).format(
                points_name=_(POINTS_NAME)
            )
        elif receiver == sender:
            message = _(msg_no_give_points_self).format(
                points_name=_(POINTS_NAME)
            )

        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message
        )


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def remove_points(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        set_language_day_locale()
        sender = update.effective_user
        sender_name = get_username_or_name(sender)
        receiver = update.message.reply_to_message.from_user
        receiver_name = get_username_or_name(receiver)

        if not receiver.is_bot and sender != receiver:
            sender_points = get_group_member_points(sender.id, GROUP_ID)
            receiver_points = get_group_member_points(receiver.id, GROUP_ID)
            points = receiver_points.points - sender_points.point_increment
            receiver_points.points = points if points >= 0 else 0
            receiver_points.save()

            if sender_points.point_increment > 1:
                message = _(msg_take_points).format(
                    sender_name=sender_name,
                    sender_points=sender_points.points,
                    points_name=_(POINTS_NAME),
                    receiver_name=receiver_name,
                    receiver_points=receiver_points.points
                )
            else:
                message = _(msg_take_point).format(
                    sender_name=sender_name,
                    sender_points=sender_points.points,
                    points_name=_(POINT_NAME),
                    receiver_name=receiver_name,
                    receiver_points=receiver_points.points
                )
        elif receiver.is_bot:
            message = _(msg_no_take_points_bot).format(
                points_name=_(POINTS_NAME)
            )
        elif receiver == sender:
            message = _(msg_no_take_points_self).format(
                points_name=_(POINTS_NAME)
            )        
        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message
        )


# Message handlers to listen for triggers to add or remove points.
add_points_handler = MessageHandler(
    (Filters.regex(ADD_POINTS_REGEX) & Filters.reply),
    add_points
)


remove_points_handler = MessageHandler(
    (Filters.regex(REMOVE_POINTS_REGEX) & Filters.reply),
    remove_points
)
