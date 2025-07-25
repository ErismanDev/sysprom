#!/usr/bin/env python
"""
Ponto de entrada da aplicação para AWS Amplify
"""

import os
import sys
import django

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_production')
django.setup()

# Importar a aplicação WSGI
from sepromcbmepi.wsgi import application

# Para compatibilidade com diferentes servidores
app = application

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv) 