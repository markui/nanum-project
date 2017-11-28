import os

# DJANGO_SETTINGS_MODULE 환경변수가 지정되지 않았거나 config.settings 패키지인 경우
# settings.local의 값들을 전부 import
SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
if not SETTINGS_MODULE or SETTINGS_MODULE == 'config.settings':
    from .local import *