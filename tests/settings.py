import os

SECRET_KEY = 'irrelevant'

INSTALLED_APPS = ['django_tekvat']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sqlite'}}

TEKVAT_APILAYER_ACCESS_KEY = os.environ.get('TEKVAT_APILAYER_ACCESS_KEY', '')