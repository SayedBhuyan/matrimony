"""
Development settings — extends base.py.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings.development
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all hosts in development
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
INTERNAL_IPS = ['127.0.0.1']

# Show emails in the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
