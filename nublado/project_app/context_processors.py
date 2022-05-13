from django.conf import settings


def global_settings(request):
    """
    Returns values to be gobally available in templates.
    """

    return {
        "project_name": settings.PROJECT_NAME,
    }
