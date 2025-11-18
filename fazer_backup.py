#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para fazer backup do banco de dados"""
import os
import sys
import django
from django.core.management import call_command
from io import open

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

# Gerar nome do arquivo
from datetime import datetime
nome_arquivo = f"backup_sepromcbmepi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Fazer backup com encoding UTF-8
print(f"Criando backup: {nome_arquivo}")
with open(nome_arquivo, 'w', encoding='utf-8') as f:
    call_command('dumpdata', stdout=f, exclude=['auth.permission', 'contenttypes'])

print(f"✅ Backup criado com sucesso: {nome_arquivo}")
print(f"Tamanho do arquivo: {os.path.getsize(nome_arquivo) / 1024 / 1024:.2f} MB")

