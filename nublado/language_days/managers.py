from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class LanguageDayManager(BaseUserManager):
    def get_queryset(self):
        return super(LanguageDayManager, self).get_queryset()


class LanguageDayMessageManager(BaseUserManager):
    def get_queryset(self):
        return super(LanguageDayMessageManager, self).get_queryset()