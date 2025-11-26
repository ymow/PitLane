"""Settings module initialization."""
import os

env = os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if 'production' in env:
    from .production import *
elif 'development' in env:
    from .development import *
else:
    from .base import *
