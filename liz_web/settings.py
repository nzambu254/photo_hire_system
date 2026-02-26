"""
Liz Web - Photography Equipment Hire System
Django settings
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-liz-web-change-this-in-production-key-2025!'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Liz Web Apps
    'accounts',
    'equipment',
    'bookings',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'liz_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'liz_web.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# M-Pesa Daraja API Configuration (SANDBOX - no real money charged)
# ─────────────────────────────────────────────────────────────────
# 1. Go to https://developer.safaricom.co.ke/
# 2. Create a free account and create an app
# 3. Copy your Consumer Key and Consumer Secret below
# ─────────────────────────────────────────────────────────────────
MPESA_ENV = 'sandbox'  # Change to 'production' for live
MPESA_CONSUMER_KEY = 'JzjaQx5RT361Z82wIbR8CN3XCylaQm8ogtHYmozl6bRlTBGV'        # ← Paste from Daraja portal
MPESA_CONSUMER_SECRET = '4pte3U88XChyUuBPW3WyG8dLxjLXLUh47dwc6YsWNdPcDSAnYVLANpzJ5saiNmCh'  # ← Paste from Daraja portal
MPESA_SHORTCODE = '174379'                           # Sandbox test shortcode
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Sandbox passkey
MPESA_CALLBACK_URL = 'https://mydomain.com/payments/mpesa/callback/'  # Not needed for sandbox polling

# Hire Settings
LATE_FEE_PER_DAY_PERCENT = 10  # 10% of daily rate per overdue day
DAMAGE_FEE_PERCENT = 50  # 50% of equipment value for damage
