# Import os module
import os
# creates the WSGI application
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the WSGI application object
application = get_wsgi_application()
