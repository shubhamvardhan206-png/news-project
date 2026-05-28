import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-p4we%u-^u(z(bphy7qdr!or7fc0%p(vw+e*b*trod9r$mnt8nk')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to local development mode unless DEBUG is explicitly set to False.
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*.onrender.com', '*.pythonanywhere.com', 'testserver']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django-allauth required core apps
    'django.contrib.sites', 
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Social Providers
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    
    # Your local app
    'news',
]

# Required setting for django.contrib.sites used by allauth
SITE_ID = 2

# Authentication backends tell Django to check both regular users and social logins
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Account middleware required by newer versions of allauth
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'newsproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'news.context_processors.common_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'newsproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

# Check if DATABASE_URL is set (Render/Production)
if os.getenv('DATABASE_URL'):
    # Production: Use PostgreSQL via DATABASE_URL
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Development: Use SQLite (no PostgreSQL needed!)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# 📧 EMAIL CONFIGURATION
# ============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # ← अपना Gmail address लगाओ
EMAIL_HOST_PASSWORD = 'your-app-password'  # ← Google App Password लगाओ
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
SERVER_EMAIL = 'your-email@gmail.com'

# Custom Email Addresses
CONTACT_EMAIL = 'contact@newsportal.com'
ADVERTISE_EMAIL = 'ads@newsportal.com'
GENERAL_EMAIL = 'info@newsportal.com'
SUPPORT_EMAIL = 'support@newsportal.com'

# ============================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- Login & Allauth configurations ---

LOGIN_URL = '/login/'

# FIXED: Ab login/register karte hi user seedhe dashboard par redirect hoga
LOGIN_REDIRECT_URL = 'admin_dashboard'  

ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Shortcuts for smooth allauth behavior on local machine
ACCOUNT_EMAIL_VERIFICATION = "none"  # Skips mandatory email validation steps
SOCIALACCOUNT_LOGIN_ON_GET = True   # Skips intermediate confirmation page for social accounts
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# Social Account Providers Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'picture',
            'verified'
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': True,
        'VERSION': 'v13.0',
    }
}


# News API Key
NEWS_API_KEY = '83fad5e997474c6aa8705aad5edb636d'

# NewsData.io API Key (get from https://newsdata.io/)
NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY', 'pub_53f2f0a4ce5e0b2e5e5f5f5f5f5f5f5f5f5f')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Security settings for production
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# SSL/HTTPS settings - ONLY in production (not DEBUG mode)
SECURE_SSL_REDIRECT = False  # Disabled for local development
SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP locally
CSRF_COOKIE_SECURE = False  # Allow CSRF over HTTP locally
SECURE_HSTS_SECONDS = 0  # No HSTS on local dev
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Enable SSL only in production (Render)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True