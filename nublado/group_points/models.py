from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import (
    TimestampModel
)
from django_telegram.models import TelegramGroupMember
from .managers import GroupMemberPointsManager


class GroupMemberPoints(
    TimestampModel
):
    group_member = models.OneToOneField(
        TelegramGroupMember,
        primary_key=True,
        on_delete=models.CASCADE
    )
    points = models.PositiveBigIntegerField(
        default=0
    )
    point_increment = models.PositiveBigIntegerField(
        default=1
    )

    objects = GroupMemberPointsManager()

    class Meta:
        verbose_name = _("group member points")

    def __str__(self):
        return "id: {0}, points: {1}".format(
            self.group_member_id,
            self.points
        )