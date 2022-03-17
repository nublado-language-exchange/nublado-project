import logging

from telegram import Update, Chat, ParseMode, Message
from telegram.ext import (
    CallbackContext, MessageHandler, Filters
)
from telegram.constants import CHATMEMBER_CREATOR
from telegram.error import TelegramError

from django.conf import settings
from django.utils.translation import gettext as _

from django_telegram.bot_utils.chat_actions import send_typing_action
from django_telegram.bot_utils.user_status import (
    restricted_group_member, is_group_chat, get_chat_member
)
from bot_notes.models import GroupNote

logger = logging.getLogger('django')

TAG_CHAR = '#'
GET_GROUP_NOTE_REGEX = '^[' + TAG_CHAR + '][a-zA-Z0-9_-]+$'
GROUP_ID = settings.NUBLADO_GROUP_ID
OWNER_ID = settings.NUBLADO_GROUP_OWNER_ID
REPO_ID = settings.NUBLADO_REPO_ID


def parse_note_text(message: Message):
    message_text = message.text
    args = message_text.split(None, 2)
    if len(args) >= 3:
        note_text = args[2]
        return note_text
    else:
        return None


@restricted_group_member(group_id=GROUP_ID)
@send_typing_action
def group_notes(update: Update, context: CallbackContext) -> None:
    group_notes = GroupNote.objects.all()
    if len(group_notes) > 0:
        group_notes_list = [f"*- {note.note_tag}*" for note in group_notes]
        message = _("*Group notes*\n{}").format(
            "\n".join(group_notes_list)
        )
    else:
        message = _("There are currently no group notes.")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


@restricted_group_member(group_id=GROUP_ID, member_status=CHATMEMBER_CREATOR)
@send_typing_action
def save_group_note(update: Update, context: CallbackContext) -> None:
    if context.args:
        note_tag = context.args[0]
        saved_message = _("Group note *{note_tag}* has been saved.").format(
            note_tag=note_tag
        )
        if update.message.reply_to_message:
            note_message_id = update.message.reply_to_message.message_id
            try:
                copied_message = context.bot.copy_message(
                    chat_id=REPO_ID,
                    from_chat_id=update.effective_chat.id,
                    message_id=note_message_id
                )
                obj, created = GroupNote.objects.update_or_create(
                    note_tag=note_tag,
                    group_id=GROUP_ID,
                    defaults={
                        'message_id': copied_message.message_id,
                        'content': None
                    }
                )
                if obj:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        reply_to_message_id=update.message.message_id,
                        text=saved_message
                    )
            except TelegramError as e:
                logger.info(e)
        else:
            if len(context.args) > 1:
                content = parse_note_text(update.effective_message)
                if content:
                    obj, created = GroupNote.objects.update_or_create(
                        note_tag=note_tag,
                        group_id=GROUP_ID,
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


@restricted_group_member(group_id=GROUP_ID, member_status=CHATMEMBER_CREATOR)
@send_typing_action
def remove_group_note(update: Update, context: CallbackContext) -> None:
    """Removes a group note specified by a tag argument."""
    if context.args:
        note_tag = context.args[0]
        num_removed, removed_dict = GroupNote.objects.filter(
            note_tag=note_tag,
            group_id=GROUP_ID
        ).delete()
        if num_removed > 0:
            removed_message = _("The group note *{note_tag}* has been removed.").format(
                note_tag=note_tag
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                reply_to_message_id=update.message.message_id,
                text=removed_message
            )
        else:
            not_found_message = _("The group note *{note_tag}* doesn't exist.").format(
                note_tag=note_tag
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                reply_to_message_id=update.message.message_id,
                text=not_found_message
            )
    else:
        message = _("A group note must have a tag.")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.message.message_id,
            text=message
        )


@restricted_group_member(group_id=GROUP_ID)
@send_typing_action
def get_group_note(update: Update, context: CallbackContext) -> None:
    """Retrieves a group note specified by a tag argument."""
    message = update.message.text
    if message.startswith(TAG_CHAR):
        note_tag = message.lstrip(TAG_CHAR)
        try:
            group_note = GroupNote.objects.get(
                note_tag=note_tag,
                group_id=GROUP_ID
            )
            if group_note.content:
                try:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        reply_to_message_id=update.message.message_id,
                        text=group_note.content
                    )
                except TelegramError as e:
                    logger.info(e)
            elif group_note.message_id:
                try:
                    # context.bot.forward_message(
                    #     chat_id=update.effective_chat.id,
                    #     from_chat_id=REPO_ID,
                    #     message_id=group_note.message_id
                    # )
                    copied_message = context.bot.copy_message(
                        chat_id=update.effective_chat.id,
                        from_chat_id=REPO_ID,
                        message_id=group_note.message_id,
                        reply_to_message_id=update.message.message_id
                    )
                except:
                    owner = get_chat_member(context.bot, OWNER_ID, GROUP_ID)
                    not_found_message = _(
                        "The content for the group note *{note_tag}* was not found in the group repo.\n\n" \
                        "Please contact {group_owner} to resolve this issue."
                    ).format(
                        note_tag=note_tag,
                        group_owner=owner.user.mention_markdown()
                    )
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        reply_to_message_id=update.message.message_id,
                        text=not_found_message
                    )            
            else:
                pass
        except GroupNote.DoesNotExist:
            pass


# Handlers to listen for triggers to retrieve notes.
get_group_note_handler = MessageHandler(
    Filters.regex(GET_GROUP_NOTE_REGEX),
    get_group_note
)