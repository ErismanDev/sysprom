"""
Configurações de produção para AWS com Supabase
"""

import os
from dotenv import load_dotenv
from .settings import *

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de produção
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Configurações de segurança para produção
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configurações de hosts permitidos para AWS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.amplifyapp.com',
    '.amazonaws.com',
    '.elasticbeanstalk.com',
    '.us-east-1.elasticbeanstalk.com',
    '.us-west-2.elasticbeanstalk.com',
    '.sa-east-1.elasticbeanstalk.com',
    '.cloudfront.net',
    '.s3.amazonaws.com',
]

# Configurações do Supabase para produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SUPABASE_DATABASE', 'postgres'),
        'USER': os.environ.get('SUPABASE_USER', 'postgres.vubnekyyfjcrswaufnla'),
        'PASSWORD': os.environ.get('SUPABASE_PASSWORD', '2YXGdmXESoZAoPkO'),
        'HOST': os.environ.get('SUPABASE_HOST', 'aws-0-sa-east-1.pooler.supabase.com'),
        'PORT': os.environ.get('SUPABASE_PORT', '6543'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
    }
}

# Configurações de arquivos estáticos para AWS
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações de mídia para AWS S3 (opcional)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Configurações de logging para AWS
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configurações de sessão para produção
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Configurações de cache para AWS
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configurações de SSL/HTTPS
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Secret Key das variáveis de ambiente
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-change-in-production')

# Configurações de timezone
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True

# Configurações de email (opcional para AWS SES)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '') 