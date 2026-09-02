"""
Settings package — defaults to development settings.

For production, set DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os

environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *  # noqa: F401, F403
else:
    from .development import *  # noqa: F401, F403
