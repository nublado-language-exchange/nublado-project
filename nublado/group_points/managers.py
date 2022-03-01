from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class GroupMemberPointsManager(BaseUserManager):
    def get_group_top_points(self, group_id, limit=10):
        qs = super().get_queryset()
        qs = qs.select_related('group_member')
        qs = qs.filter(
            group_member__group_id=group_id,
            points__gt=0
        )
        qs = qs.order_by('-points')
        return qs[:limit]

    def get_queryset(self):
        return super(GroupMemberPointsManager, self).get_queryset()