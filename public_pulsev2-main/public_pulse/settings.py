"""
Django settings for public_pulse project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings
SECRET_KEY = 'django-insecure-mogv-a2h_di=q9k5*!t9sngm8x)y2ajy*-(b0g5r1x0$9eh&9h'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your apps
    'landing_page',
    'complaints',
    'public_admin',
    'chatbot',
    # 'pulse_admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Changed to default Django locale middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'public_admin.middleware.SessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'public_admin.middleware.AdminAccessMiddleware',
]

ROOT_URLCONF = 'public_pulse.urls'

# ========== TEMPLATES SETTING ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'landing_page' / 'templates',
            BASE_DIR / 'pulse_admin' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'public_pulse.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ========== INTERNATIONALIZATION (i18n) ==========
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported languages
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिन्दी (Hindi)'),
    ('te', 'తెలుగు (Telugu)'),
    ('ta', 'தமிழ் (Tamil)'),
    ('kn', 'ಕನ್ನಡ (Kannada)'),
    ('ml', 'മലയാളം (Malayalam)'),
    ('mr', 'मराठी (Marathi)'),
    ('bn', 'বাংলা (Bengali)'),
]

# Locale paths - where translation files are stored
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== EMAIL CONFIGURATION ==========
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'civicpulse.govt@gmail.com'
EMAIL_HOST_PASSWORD = 'uqskqgvrgnhoqdrn'
DEFAULT_FROM_EMAIL = 'Civic Pulse <civicpulse.govt@gmail.com>'
EMAIL_TIMEOUT = 30
print("✅ USING REAL EMAIL SENDING - Emails will go to citizens' inboxes")

BASE_URL = 'http://127.0.0.1:8000'

# ========== AUTHENTICATION SETTINGS ==========
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# ========== SESSION SECURITY CONFIGURATION ==========
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 4 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# ========== CUSTOM SETTINGS ==========
AI_ANALYSIS_ENABLED = True
SENTIMENT_ANALYSIS_ENABLED = True
AUTO_CATEGORIZATION_ENABLED = True

# ========== EMAIL DEBUGGING ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
