from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimestampModel
from .managers import GroupNoteManager


class GroupNote(TimestampModel):
    group_id = models.BigIntegerField()
    note_tag = models.CharField(
        max_length=255
    )
    # Reference to a Telegram message
    message_id = models.BigIntegerField(
        null=True
    )
    content = models.TextField(
        null=True,
        blank=True
    )

    objects = GroupNoteManager()

    class Meta:
        verbose_name = _("Bot note")
        verbose_name_plural = _("Bot notes")
        unique_together = ('group_id', 'note_tag')