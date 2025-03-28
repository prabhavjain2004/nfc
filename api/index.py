from django.http import JsonResponse
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_system.settings')
application = get_wsgi_application()

def handler(request):
    """Simple handler for Vercel"""
    return JsonResponse({
        'status': 'ok',
        'message': 'NFC Payment System API'
    })
