from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_system.settings')
application = get_wsgi_application()

# This is the entry point for Vercel
def handler(request):
    return application(request)
