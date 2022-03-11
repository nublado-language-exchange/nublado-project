import logging

from telegram import Update, Bot
from telegram.ext import CallbackContext

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

from django_telegram.bot_utils.chat_actions import (
    send_typing_action
)
from django_telegram.bot_utils.user_status import (
    restricted_group_member, restricted_group_owner
)
from language_days.functions import (
    get_language_day, set_language_day_locale,
    get_language_day_schedule
)
from django_telegram.models import TmpMessage


logger = logging.getLogger('django')

GROUP_ID = settings.NUBLADO_GROUP_ID


def clear_tmp_messages(bot: Bot) -> None:
    """Get previously saved tmp messages and delete them."""
    group_tmp_messages = TmpMessage.objects.filter(chat_id=GROUP_ID)

    if group_tmp_messages:
        for tmp_message in group_tmp_messages:
            try:
                bot.delete_message(
                    chat_id=tmp_message.chat_id,
                    message_id=tmp_message.message_id
                )
                logger.info("Message deleted")
            except:
                logger.error("Message to delete not found.")

            tmp_message.delete()


@restricted_group_member(group_id=GROUP_ID)
@send_typing_action
def schedule(update: Update, context: CallbackContext) -> None:
    """Display the group schedule."""
    message = get_language_day_schedule()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


@restricted_group_member(group_id=GROUP_ID)
@send_typing_action
def language_day(update: Update, context: CallbackContext) -> None:
    """Display the current language day."""
    set_language_day_locale()
    language_day = get_language_day()
    weekday = timezone.now().weekday()
    message = _("It's {weekday}, {time} {timezone}.\nIt's {language_day} day.").format(
        weekday=_(settings.WEEKDAYS[weekday]),
        time=timezone.now().strftime('%H:%M'),
        timezone=settings.TIME_ZONE,
        language_day=_(settings.LANGUAGE_DAYS[language_day])
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


def initiate_language_day_c(context: CallbackContext) -> None:
    """Display language-day-related messages and do some cleanup."""
    set_language_day_locale()
    language_day = get_language_day()
    schedule = get_language_day_schedule()
    # Daily message to be pinned.
    message = _("Welcome, friends. It's {language_day} day.\n\n{schedule}").format(
        language_day=_(settings.LANGUAGE_DAYS[language_day]),
        schedule=schedule
    )
    pinned_message = context.bot.send_message(
        chat_id=GROUP_ID,
        text=message
    )
    context.bot.pin_chat_message(
        chat_id=GROUP_ID,
        message_id=pinned_message.message_id
    )
    # Get previously saved tmp messages and delete them.
    clear_tmp_messages(context.bot)
    # Add the pinned message to the group of tmp messages to be deleted later.
    tmp_message = TmpMessage.objects.create_tmp_message(
        message_id=pinned_message.message_id,
        chat_id=GROUP_ID
    )
    logger.info(tmp_message)


@restricted_group_owner(group_id=GROUP_ID)
@send_typing_action
def initiate_language_day(update: Update, context: CallbackContext) -> None:
    """Manually execute language-day-initiation tasks."""
    initiate_language_day_c(context)
