from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('project_app.urls')),
    path('admin/', admin.site.urls),
    path('bot/', include('telegram_bot.urls', namespace='bot')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
