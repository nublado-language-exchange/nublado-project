from django.conf import settings
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from .views import BotWebhookView

app_name = 'django_telegram'

urlpatterns = [
    re_path(
        r'^webhook/(?P<token>.+)/$',
        csrf_exempt(BotWebhookView.as_view()),
        name='bot_webhook_view'
    ),
]