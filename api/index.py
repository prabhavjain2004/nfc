import os
import sys
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse

# Configure Django settings based on environment
if os.getenv('VERCEL_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_system.settings')
    os.environ['DEBUG'] = 'False'
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_system.local_settings')
    os.environ['DEBUG'] = 'True'

try:
    # Initialize Django WSGI application
    application = get_wsgi_application()
except Exception as e:
    print(f"Django initialization error: {str(e)}", file=sys.stderr)
    application = None

def handler(request):
    """Handle incoming requests"""
    try:
        if application is None:
            return JsonResponse({
                'error': 'Application initialization failed',
                'detail': 'The server is not properly configured'
            }, status=500)

        # Basic health check endpoint
        if request.path == '/health/':
            return JsonResponse({'status': 'ok'}, status=200)

        # Handle the request through Django WSGI
        return application(request)

    except Exception as e:
        error_msg = str(e)
        print(f"Request handling error: {error_msg}", file=sys.stderr)
        
        return JsonResponse({
            'error': 'Internal Server Error',
            'detail': error_msg,
            'path': request.path
        }, status=500)
