"""
Configurações para Supabase em PRODUÇÃO
"""

import os
from dotenv import load_dotenv
from .settings import *

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Supabase usando variáveis de ambiente
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
        },
    }
}

# Configurações para PRODUÇÃO
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Configuração de arquivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# Configurações de segurança para PRODUÇÃO
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Secret Key das variáveis de ambiente
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY) 