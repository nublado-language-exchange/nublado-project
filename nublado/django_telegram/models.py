from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimestampModel, UUIDModel
from .managers import (
    TelegramGroupMemberManager,
    TmpMessageManager
)


class TelegramGroupMember(TimestampModel, UUIDModel):
    user_id = models.PositiveBigIntegerField()
    group_id = models.BigIntegerField()

    objects = TelegramGroupMemberManager()

    class Meta:
        verbose_name = _("Telegram group member")
        verbose_name_plural = _("Telegram group members")
        unique_together = ('user_id', 'group_id')

    def __str__(self):
        return "group: {0}, user: {1}".format(
            self.group_id,
            self.user_id
        )


class TmpMessage(TimestampModel):
    message_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()

    objects = TmpMessageManager()

    class Meta:
        verbose_name = _("tmp message")
        verbose_name_plural = _("tmp messages")
        unique_together = ('message_id', 'chat_id')

    def __str__(self):
        return "message_id: {}".format(self.message_id)