from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import TimestampModel
from .managers import (
    LanguageDayManager
)


class LanguageDay(TimestampModel):
    class Weekday(models.IntegerChoices):
        MON = settings.MON, _('Monday')
        TUE = settings.TUE, _('Tuesday')
        WED = settings.WED, _('Wednesday')
        THU = settings.THU, _('Thursday')
        FRI = settings.FRI, _('Friday')
        SAT = settings.SAT, _('Saturday')
        SUN = settings.SUN, _('Sunday')

    class Language(models.TextChoices):
        EN = settings.EN, _('English')
        ES = settings.ES, _('Spanish')
        FREE = settings.FREE, _('Free')

    id = models.IntegerField(
        primary_key=True,
        choices=Weekday.choices
    )
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        default=Language.FREE
    )

    objects = LanguageDayManager()

    class Meta:
        verbose_name = _("language day")
        verbose_name_plural = _("language days")

    def __str__(self):
        return "id: {0} - {1}, language: {2}".format(
            self.id,
            self.Weekday.labels[self.id],
            self.language
        )


# class LanguageDayMessage(TimestampModel):
#     """A message to be displayed at the beginning of a language day."""
#     id = models.PositiveBigIntegerField(
#         primary_key=True
#     )
#     language_day = models.ForeignKey(
#         LanguageDay,
#         on_delete=models.CASCADE
#     )

#     objects = LanguageDayMessageManager()

#     class Meta:
#         verbose_name = _("language day message")
#         verbose_name_plural = _("language day messages")

#     def __str__(self):
#         return "message_id: {0}".format(
#             self.id
#         )


