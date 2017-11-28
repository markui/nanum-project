from .base import *

config_secret = json.loads(open(CONFIG_SECRET_LOCAL_FILE).read())

# Database
DATABASES = config_secret['django']['databases']

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# Installed apps
INSTALLED_APPS += [
    'django_extensions',
]

