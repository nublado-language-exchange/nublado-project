import logging

from telegram import Update, Chat
from telegram.ext import (
    CallbackContext, MessageHandler, Filters
)

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.bot_utils.chat_actions import send_typing_action
from django_telegram.bot_utils.user_status import (
    restricted_group_owner,
    restricted_group_member
)
from bot_notes.models import GroupNote

logger = logging.getLogger('django')

TAG_CHAR = '#'
GET_GROUP_NOTE_REGEX = '^[' + TAG_CHAR + '][a-zA-Z0-9_-]+$'
GROUP_ID = settings.NUBLADO_GROUP_ID


@send_typing_action
@restricted_group_member
def group_notes(update: Update, context: CallbackContext) -> None:
    group_notes = GroupNote.objects.all()
    group_notes_list = [f"*- {note.note_tag}*" for note in group_notes]
    message = _("*Group notes*\n{}").format(
        "\n".join(group_notes_list)
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


@send_typing_action
@restricted_group_owner
def save_group_note(update: Update, context: CallbackContext) -> None:
    if context.args:
        note_tag = context.args[0]
        saved_message = _("Group note *{note_tag}* has been saved.").format(
            note_tag=note_tag
        )
        if update.message.reply_to_message:
            message_id = update.message.repy_to_message.message_id
            obj, created = GroupNote.objects.update_or_create(
                note_tag=note_tag, group_id=GROUP_ID,
                defaults={
                    'message_id': message_id,
                    'content': None
                }
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                reply_to_message_id=update.message.message_id,
                text=saved_message
            )
        else:
            if len(context.args) > 1:
                content = " ".join(context.args[1:])
                obj, created = GroupNote.objects.update_or_create(
                    note_tag=note_tag, group_id=GROUP_ID,
                    defaults={
                        'message_id': None,
                        'content': content
                    }
                )
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    reply_to_message_id=update.message.message_id,
                    text=saved_message
                )
            else:
                message = _("A group note needs content.")
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    reply_to_message_id=update.message.message_id,
                    text=message
                )
    else:
        message = _("A group note must have a tag.")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.message.message_id,
            text=message
        )


def get_group_note(update: Update, context: CallbackContext) -> None:
    message = update.message
    if message.startswith(TAG_CHAR):
        message = message.lstrip(TAG_CHAR)
        try:
            group_note = GroupNote.objects.get(
                note_tag=message,
                group_id=GROUP_ID
            )
            if group_note.content:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    reply_to_message_id=update.message.message_id,
                    text=group_note.content
                )
            elif group_note.message_id:
                try:
                    context.bot.forward_message(
                        message_id=group_note.message_id,
                        chat_id=asdf,
                        from_chat_id=adsf,
                    )
                except:
                    pass
            else:
                pass
        except GroupNote.DoesNotExist:
            pass