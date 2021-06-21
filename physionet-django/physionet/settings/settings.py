import os

from decouple import config

from physionet.settings.base import *

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(',')
SITE_ID = config("SITE_ID")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config("DB_HOST"),
        'PORT': '',
        'TEST': {
            'MIRROR': 'default'
        }
    }
}

# When ready, use the following:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

EMAIL_FROM_DOMAINS = ['physionet.org']
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
CONTACT_EMAIL = config("CONTACT_EMAIL")
SERVER_EMAIL = config("SERVER_EMAIL")

ADMINS = [(config("ADMINS_NAME"), config("ADMINS_MAIL"))]

GCP_BUCKET_PREFIX = ""

DEMO_FILE_ROOT = os.path.join(os.path.abspath(os.path.join(BASE_DIR, os.pardir)), 'demo-files')

MEDIA_ROOT = '/data/pn-media'

DATACITE_API_URL = 'https://api.datacite.org/dois'
DATACITE_PREFIX = config('DATACITE_PREFIX', default=False)
DATACITE_USER = config('DATACITE_USER', default=False)
DATACITE_PASS = config('DATACITE_PASS', default=False)

# Tags for the ORCID API
ORCID_DOMAIN = 'https://orcid.org'
ORCID_REDIRECT_URI = config("OCRID_REDIRECT_URI")
ORCID_AUTH_URL = 'https://orcid.org/oauth/authorize'
ORCID_TOKEN_URL = 'https://orcid.org/oauth/token'
ORCID_CLIENT_ID = config('ORCID_CLIENT_ID', default=False)
ORCID_CLIENT_SECRET = config('ORCID_CLIENT_SECRET', default=False)
ORCID_SCOPE = config('ORCID_SCOPE', default=False)

# If defined, MEDIA_X_ACCEL_ALIAS is the virtual URL path
# corresponding to MEDIA_ROOT. If possible, when serving a file
# located in MEDIA_ROOT, the response will use an X-Accel-Redirect
# header so that nginx can serve the file directly.
MEDIA_X_ACCEL_ALIAS = '/protected'

STATIC_ROOT = '/data/pn-static'

if RUNNING_TEST_SUITE:
    MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'test')
    STATIC_ROOT = os.path.join(STATIC_ROOT, 'test')
