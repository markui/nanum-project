from .base import *

DATABASES = config_secret_common['django']['databases']

INSTALLED_APPS += [
    'django_extensions',
]
