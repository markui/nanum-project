from .base import *

config_secret = json.loads(open(CONFIG_SECRET_DEV_FILE).read())

# Installed Apps
INSTALLED_APPS += [
    'storages',
    'corsheaders',
]

# Secret Files / AWS
AWS_ACCESS_KEY_ID = config_secret['aws']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config_secret['aws']['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = config_secret['aws']['AWS_STORAGE_BUCKET_NAME']
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'ap-northeast-2'

# AWS Storage
STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

# S3 FileStorage
DEFAULT_FILE_STORAGE = 'config.storages.MediaStorage'
STATICFILES_STORAGE = 'config.storages.StaticStorage'

# Databases
DATABASES = config_secret['django']['databases']

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '.elasticbeanstalk.com',
    '.siwon.me',
    '172.31.16.135',
]

# CORS
CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
    'esdyee.github.io',
)
