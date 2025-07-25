#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, ComissaoPromocao, MembroComissao, UsuarioFuncao, CargoFuncao

def verificar_postgresql():
    print("=== VERIFICANDO POSTGRESQL ===\n")
    
    print(f"Usuários: {User.objects.count()}")
    print(f"Militares: {Militar.objects.count()}")
    print(f"Comissões: {ComissaoPromocao.objects.count()}")
    print(f"Membros de comissões: {MembroComissao.objects.count()}")
    print(f"Funções de usuários: {UsuarioFuncao.objects.count()}")
    print(f"Cargos/Funções: {CargoFuncao.objects.count()}")
    
    print(f"\n=== PRIMEIROS 5 USUÁRIOS ===")
    for user in User.objects.all()[:5]:
        print(f"  • {user.username} (ID: {user.id})")
    
    print(f"\n=== PRIMEIROS 5 MILITARES ===")
    for militar in Militar.objects.all()[:5]:
        print(f"  • {militar.nome_guerra} - {militar.cpf} (ID: {militar.id})")
    
    print(f"\n=== COMISSÕES ===")
    for comissao in ComissaoPromocao.objects.all():
        print(f"  • {comissao.nome} ({comissao.tipo}) - {comissao.status} (ID: {comissao.id})")

if __name__ == '__main__':
    verificar_postgresql() 