import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimestampModel(models.Model):
    date_created = models.DateTimeField(
        verbose_name=_("date created"),
        default=timezone.now,
        editable=False
    )
    date_updated = models.DateTimeField(
        verbose_name=_("date updated"),
        auto_now=True,
        editable=False
    )

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    A model whose id is a generated uuid.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True