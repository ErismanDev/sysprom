"""
Configurações específicas para o ambiente do Render
"""

import os
import dj_database_url
from .settings import *

# Configurações específicas do Render
DEBUG = False

# Configurações de hosts permitidos para o Render
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'sysprom.onrender.com',
    '*',  # Temporário para debug
]

# Configurações de banco de dados para o Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.strip():
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback para configuração local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'sepromcbmepi'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# OTIMIZAÇÕES DE BANCO DE DADOS PARA PERFORMANCE
DATABASES['default'].update({
    'CONN_MAX_AGE': 60,  # Manter conexões por 60 segundos
    'OPTIONS': {
        'connect_timeout': 10,
        'application_name': 'sepromcbmepi_render',
        'options': '-c statement_timeout=30000',  # 30 segundos timeout
    },
    'ATOMIC_REQUESTS': False,  # Desabilitar para melhor performance
    'AUTOCOMMIT': True,
})

# Configurações de arquivos estáticos para o Render
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Configurações de mídia
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Configurações de segurança para produção
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configurações de sessão
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configurações do WhiteNoise para arquivos estáticos - Configuração simples
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# Configurações de logging para o Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Reduzir logs de SQL para performance
            'propagate': False,
        },
        'gunicorn': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configurações de cache otimizadas
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Configurações de timezone
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True

# Configurações de idioma
LANGUAGE_CODE = 'pt-br'
USE_I18N = True
USE_L10N = True

# Configurações de segurança adicional
SECURE_SSL_REDIRECT = False  # Desabilitar para desenvolvimento
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configurações de CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://sysprom.onrender.com',
    'https://*.onrender.com',
]

# OTIMIZAÇÕES DE PERFORMANCE
# Desabilitar debug toolbar e outras ferramentas de desenvolvimento
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Configurações de sessão otimizadas
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_SAVE_EVERY_REQUEST = False

# Configurações de middleware otimizadas
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise deve vir primeiro
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'militares.middleware.SessaoMiddleware',  # Manter middleware customizado
]

# Configurações de template otimizadas
TEMPLATES[0]['OPTIONS']['debug'] = False
TEMPLATES[0]['OPTIONS']['auto_reload'] = False

# Configurações de email (desabilitar para evitar timeouts)
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Configurações de arquivos estáticos otimizadas
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configurações de WhiteNoise otimizadas - Configuração simples para evitar problemas
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_INDEX_FILE = True 