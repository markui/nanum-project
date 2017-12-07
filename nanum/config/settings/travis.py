from .base import *

INSTALLED_APPS += [

]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "localhost",
        "PORT": "5432",
        "NAME": "travisci",
        "USER": "postgres",
        "PASSWORD": ""
    }
}
