import os
import sys
import datetime as dt
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_noop as _


# Get key env values from the virtual environment.
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable.".format(var_name)
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Subdirectory for app bundles.
APP_DIR = 'nublado'
sys.path.append(os.path.join(BASE_DIR, APP_DIR))

APPS_ROOT = BASE_DIR / APP_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = []

# Installed apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
LOCAL_APPS = [
    'core.apps.CoreConfig',
    'django_telegram.apps.DjangoTelegramConfig',
    'group_points.apps.GroupPointsConfig',
    'language_days.apps.LanguageDaysConfig',
    'bot_notes.apps.BotNotesConfig',
    'nublado_bot.apps.NubladoBotConfig',
    'project_app.apps.ProjectAppConfig'
]
THIRD_PARTY_APPS = []
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization and localization
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _("English")),
    ('es', _("Spanish")),
]
LANGUAGES_DICT = dict(LANGUAGES)

LOCALE_PATHS = (
    APPS_ROOT / "project_app" / "locale",
)

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING = {
    'version': 1,
    # Version of logging
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # Handlers
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'nublado-debug.log',
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    # Loggers
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

# Language day schedule
EN = 'en'
ES = 'es'
FREE = 'free'
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
# Note: Do some error-checking on this.
LANGUAGE_DAY_SCHEDULE = {
    ES: [],
    EN: [],
    FREE: [MON, TUE, WED, THU, FRI, SAT, SUN]
}
LANGUAGE_DAYS = {
    EN: _("English"),
    ES: _("Spanish"),
    FREE: _("Free")
}
LANGUAGE_DAY_HOUR_CHANGE = 0
LANGUAGE_DAY_MINUTE_CHANGE = 1
LANGUAGE_DAY_TIME_CHANGE = dt.time(
    hour=LANGUAGE_DAY_HOUR_CHANGE,
    minute=LANGUAGE_DAY_MINUTE_CHANGE
).strftime('%H:%M')
WEEKDAYS = [
    _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"),
    _("Friday"), _("Saturday"), _("Sunday")
]
WEEKDAYS_ABBR = [
    _("Mon."), _("Tue."), _("Wed."), _("Thu."),
    _("Fri."), _("Sat."), _("Sun.")
]


# Telegram bot stuff
BOT_MODE_WEBHOOK = "webhook"
BOT_MODE_POLLING = "polling"

#NubladoBot
# Command line arg to run this bot
NUBLADO_BOT = 'nubladobot'
NUBLADO_BOT_TOKEN = get_env_variable('NUBLADO_BOT_TOKEN')
NUBLADO_GROUP_ID = int(get_env_variable('NUBLADO_GROUP_ID'))
NUBLADO_REPO_ID = int(get_env_variable('NUBLADO_REPO_ID'))
NUBLADO_GROUP_OWNER_ID = int(get_env_variable('NUBLADO_GROUP_OWNER_ID'))
NUBLADO_SUDO_LIST = [NUBLADO_GROUP_OWNER_ID, ]

BOT_TOKENS = {
    NUBLADO_BOT: NUBLADO_BOT_TOKEN
}

DJANGO_TELEGRAM = {
    'mode': BOT_MODE_WEBHOOK,
    'webhook_port': int(os.environ.get('PORT', 5000)),
    'webhook_site' : "https://nubladoproject.herokuapp.com",
	'webhook_path' : "bot/webhook",
    'bots': {
        NUBLADO_BOT_TOKEN: {
            'token': NUBLADO_BOT_TOKEN,
            'group_id': NUBLADO_GROUP_ID,
            'repo_id': NUBLADO_REPO_ID,
            'sudo_list': NUBLADO_SUDO_LIST
        }
    }
}
