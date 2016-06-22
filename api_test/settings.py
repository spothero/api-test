from django.conf import settings


INSTALLED_APPS = settings.INSTALLED_APPS + (
    'django_hosts',
)

FIXTURE_FILE = getattr(settings, 'API_TEST_FIXTURE_FILE', '')
