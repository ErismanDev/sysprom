#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def redefinir_senha():
    try:
        user = User.objects.get(username='erisman')
        user.set_password('cbmepi123')
        user.save()
        print('Senha do usuário "erisman" redefinida para: cbmepi123')
    except User.DoesNotExist:
        print('Usuário "erisman" não encontrado!')

if __name__ == '__main__':
    redefinir_senha() 