from django.conf import settings
from django.utils import timezone
from django.utils.translation import activate, gettext as _

from language_days.models import LanguageDay

# Make decorator for language day translations.

def set_language_day_locale():
    """Activate the locale that corresponds to the current language day."""
    language_day = get_language_day()
    if language_day in settings.LANGUAGES_DICT.keys():
        activate(language_day)
    else:
        activate(settings.LANGUAGE_CODE)


def get_language_day() -> str:
    """Get the language day key based on an integer weekday value (Monday = 0)."""
    weekday = timezone.now().weekday()

    if 0 <= weekday <= 6:
        try:
            ld = LanguageDay.objects.get(id=weekday)
            language_day = ld.language
        except LanguageDay.DoesNotExist:
            language_day = settings.FREE
    else:
        raise ValueError("Weekday must be between 0 and 6, inclusive.")

    return language_day


def get_language_day_schedule() -> str:
    """Return the language day schedule as a formatted string."""
    set_language_day_locale()

    schedule = (_("*Schedule:*\nThe day changes at {time_change} {timezone}.") + "\n\n").format(
        time_change=settings.LANGUAGE_DAY_TIME_CHANGE,
        timezone=settings.TIME_ZONE
    )

    for language in LanguageDay.Language.values:
        weekdays = LanguageDay.objects.filter(language=language).values_list('id', flat=True).order_by('id')
        if weekdays:
            weekday_abbr_list = [_(settings.WEEKDAYS_ABBR[weekday]) for weekday in weekdays]
            weekday_abbr = ", ".join(weekday_abbr_list) if weekday_abbr_list else ""
            schedule += "{language_day}: {weekday}\n".format(
                language_day=_(settings.LANGUAGE_DAYS[language]).capitalize(), 
                weekday=weekday_abbr
            )

    return schedule