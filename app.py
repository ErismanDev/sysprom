#!/usr/bin/env python
"""
Ponto de entrada da aplicação para Render - Otimizado para performance
"""

import os
import sys
import django
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Adicionar o diretório do projeto ao path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Configurar o Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_render')
    
    # Configurações de performance
    os.environ.setdefault('DJANGO_CACHE_TIMEOUT', '300')
    os.environ.setdefault('DJANGO_DB_CONN_MAX_AGE', '60')
    
    logger.info("🔄 Configurando Django...")
    django.setup()
    logger.info("✅ Django configurado com sucesso")
    
    # Importar a aplicação WSGI
    from sepromcbmepi.wsgi import application
    logger.info("✅ Aplicação WSGI importada")
    
    # Para compatibilidade com diferentes servidores
    app = application
    
    # Configurações de performance para a aplicação
    if hasattr(app, 'config'):
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    logger.info("🚀 Aplicação pronta para receber requisições")
    
except Exception as e:
    logger.error(f"❌ Erro ao configurar aplicação: {e}")
    raise

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv) 