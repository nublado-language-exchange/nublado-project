from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class LanguageDayManager(BaseUserManager):
    def create_language_day(self, id=None, language=None, **kwargs):
        if id is None:
            raise ValueError(_("Id is required."))
        if not language:
            raise ValueError(_("Language is required."))

        language_day = self.model(
            id=id,
            language=language,
            **kwargs
        )
        language_day.full_clean()
        language_day.save(using=self._db)

        return language_day

    def create(self, id=None, language=None, **kwargs):
        return self.create_language_day(
            id=id,
            language=language,
            **kwargs
        )

    def get_queryset(self):
        return super(LanguageDayManager, self).get_queryset()


# class LanguageDayMessageManager(BaseUserManager):
#     def get_queryset(self):
#         return super(LanguageDayMessageManager, self).get_queryset()