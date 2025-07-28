"""
Configurações para Supabase
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

# Configurações para desenvolvimento (não produção)
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,*').split(',')

# Configuração de arquivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações de segurança (desabilitadas para desenvolvimento)
SECURE_SSL_REDIRECT = False  # Desabilitado para desenvolvimento
SECURE_PROXY_SSL_HEADER = None  # Desabilitado para desenvolvimento

# Secret Key das variáveis de ambiente
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY) 