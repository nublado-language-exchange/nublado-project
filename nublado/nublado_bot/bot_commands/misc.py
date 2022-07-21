import random
import logging

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import CHATMEMBER_CREATOR

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.functions.chat_actions import send_typing_action
from django_telegram.functions.group import (
    restricted_group_member,
    get_random_group_member
)
from django_telegram.functions.functions import parse_command_last_arg_text

logger = logging.getLogger('django')

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


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def hello(update: Update, context: CallbackContext) -> None:
    member = get_random_group_member(GROUP_ID)
    if member:
        try:
            user = update.effective_user
            chat_member = context.bot.get_chat_member(GROUP_ID, member.user_id)
            message = _("Hey {}.\n{} says hello.").format(
                chat_member.user.mention_markdown(),
                user.mention_markdown()
            )
            context.bot.send_message(
                chat_id=GROUP_ID,
                text=message
            )
        except:
            pass      


@restricted_group_member(group_id=GROUP_ID, member_status=CHATMEMBER_CREATOR)
@send_typing_action
def echo(update: Update, context: CallbackContext) -> None:
    """Echo a message to the group."""
    if len(context.args) >= 1:
        message = parse_command_last_arg_text(
            update.effective_message,
            maxsplit=1
        )
        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message
        )


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def reverse_text(update: Update, context: CallbackContext) -> None:
    """Reverse the text provided as an argument and display it."""
    if len(context.args) >= 1:
        message = parse_command_last_arg_text(
            update.effective_message,
            maxsplit=1
        )
        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message[::-1]
        )
    else:
        message = _("The command requires some text to be reversed.")
        context.bot.send_message(
            chat_id=GROUP_ID,
            text=message
        )


@restricted_group_member(group_id=GROUP_ID, private_chat=False)
@send_typing_action
def roll_die(update: Update, context: CallbackContext) -> None:
    """Roll a die and show an animation."""
    user = update.effective_user
    result = context.bot.send_dice(
        chat_id=GROUP_ID
    )

    value = result['dice']['value']
    user = update.effective_user
    message = _("{} has rolled a {}.").format(
        user.mention_markdown(),
        value
    )
    context.bot.send_message(
        chat_id=GROUP_ID,
        text=message
    )


def roll_dice_c(
    update: Update,
    context: CallbackContext,
    min_dice=1,
    max_dice=10,
    dice_min_val=1,
    dice_max_val=6,
    dice_sum=False
):
    if len(context.args) >= 1:
        int_arg = int(context.args[0])
        if int_arg >= min_dice and int_arg <= max_dice:
            num_dice = int_arg
            results = []
            user = update.effective_user
            for x in range(num_dice):
                result = random.randint(dice_min_val, dice_max_val)
                results.append(result)
            if dice_sum:
                total = sum(results)
                message = _("{} has rolled {}.\n\n Sum: {}").format(
                    user.mention_markdown(),
                    results,
                    total
                )
            else:
                message = _("{} has rolled {}.").format(
                    user.mention_markdown(),
                    results
                )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message 
            )
    else:
        message = _("Please specify the number of dice to be rolled ({} - {}).").format(
            min_dice,
            max_dice
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )



@restricted_group_member(group_id=GROUP_ID, private_chat=True)
@send_typing_action
def roll(update: Update, context: CallbackContext) -> None:
    """Roll specified number of dice and show results as text."""
    roll_dice_c(update, context, dice_sum=False)


@restricted_group_member(group_id=GROUP_ID, private_chat=True)
@send_typing_action
def roll_sum(update: Update, context: CallbackContext) -> None:
    """Roll specified number of dice and show results as text."""
    roll_dice_c(update, context, dice_sum=True)