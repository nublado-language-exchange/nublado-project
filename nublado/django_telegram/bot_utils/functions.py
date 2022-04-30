import logging

from telegram import Bot, Message

from ..models import TelegramGroupMember

logger = logging.getLogger('django')


def update_group_members_from_admins(bot: Bot, group_id: int):
    try:
        group_admins = bot.get_chat_administrators(group_id)
        for group_admin in group_admins:
            user = group_admin.user
            group_member, group_member_created = TelegramGroupMember.objects.get_or_create(
                group_id=group_id,
                user_id=user.id
            )
        logger.info(TelegramGroupMember.objects.count())
        return TelegramGroupMember.objects.all()
    except:
        return None


def parse_command_last_arg_text(
    message: Message,
    maxsplit: int = 1
):
    """Returns the text for commands that receive text as its last arg"""
    # Message text is the command and given arguments (e.g., /command arg some text)
    message_text = message.text
    if maxsplit >= 1:
        command_and_args = message_text.split(None, maxsplit)
        if len(command_and_args) >= maxsplit + 1:
            arg_text = command_and_args[maxsplit]
            return arg_text
        else:
            return None
    else:
        return False
