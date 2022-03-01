from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimestampModel
from .managers import (
    LanguageDayManager, LanguageDayMessageManager
)


class LanguageDay(TimestampModel):
    id = models.CharField(
        primary_key=True,
        max_length=5,
        editable=False
    )
    name = models.CharField(
        max_length=255,
        unique=True
    )

    objects = LanguageDayManager()

    class Meta:
        verbose_name = _("language day")
        verbose_name_plural = _("language days")

    def __str__(self):
        return "id: {0}, name: {1}".format(
            self.id,
            self.name
        )


class LanguageDayMessage(TimestampModel):
    """A message to be displayed at the beginning of a language day."""
    id = models.PositiveBigIntegerField(
        primary_key=True
    )
    language_day = models.ForeignKey(
        LanguageDay,
        on_delete=models.CASCADE
    )

    objects = LanguageDayMessageManager()

    class Meta:
        verbose_name = _("language day message")
        verbose_name_plural = _("language day messages")

    def __str__(self):
        return "message_id: {0}".format(
            self.id
        )


