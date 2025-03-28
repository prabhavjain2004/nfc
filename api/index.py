import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_system.settings')
django_application = get_wsgi_application()

# Wrap the application with StaticFilesHandler
application = StaticFilesHandler(django_application)

def handler(request):
    if request.path.startswith('/static/'):
        return application(request)
    return django_application(request)
