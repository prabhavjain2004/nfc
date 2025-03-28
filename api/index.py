import os
import sys
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_system.settings')

# Error handling wrapper
def handler(request):
    try:
        # Initialize Django WSGI application
        application = get_wsgi_application()
        
        # Handle the request
        return application(request)
    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}", file=sys.stderr)
        
        # Return error response
        return JsonResponse({
            'error': 'Internal Server Error',
            'detail': str(e)
        }, status=500)
