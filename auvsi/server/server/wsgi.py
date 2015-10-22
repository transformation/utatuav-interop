"""
WSGI config for the interop server.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import logging
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

# Add parent directory to Python path
server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path = [server_dir] + sys.path

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
