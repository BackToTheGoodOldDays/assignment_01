"""
WSGI config for Clean Architecture bookstore project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'framework.settings')

application = get_wsgi_application()
