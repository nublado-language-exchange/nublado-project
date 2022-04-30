import logging

from telegram import Bot

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