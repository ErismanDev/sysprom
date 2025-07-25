#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, CargoFuncao

def verificar_militar_clemilton():
    print("🔍 VERIFICANDO MILITAR CLEMILTON")
    print("=" * 50)
    
    # 1. Buscar militar CLEMILTON
    militares_clemilton = Militar.objects.filter(
        nome_completo__icontains='CLEMILTON'
    )
    
    print(f"📋 Militares encontrados com 'CLEMILTON' ({militares_clemilton.count()}):")
    for militar in militares_clemilton:
        print(f"   - {militar.nome_completo}")
        print(f"     Posto: {militar.get_posto_graduacao_display()}")
        print(f"     Matrícula: {militar.matricula}")
        print(f"     Situação: {militar.get_situacao_display()}")
        print(f"     Tem usuário: {'✅' if hasattr(militar, 'user') and militar.user else '❌'}")
        if hasattr(militar, 'user') and militar.user:
            print(f"     Usuário: {militar.user.username}")
        print()
    
    # 2. Buscar usuário CLEMILTON
    try:
        usuario_clemilton = User.objects.get(username='361.367.943-49')
        print(f"👤 Usuário CLEMILTON:")
        print(f"   - Nome: {usuario_clemilton.get_full_name()}")
        print(f"   - Username: {usuario_clemilton.username}")
        print(f"   - Email: {usuario_clemilton.email}")
        print(f"   - Ativo: {usuario_clemilton.is_active}")
        print(f"   - Tem militar: {'✅' if hasattr(usuario_clemilton, 'militar') and usuario_clemilton.militar else '❌'}")
    except User.DoesNotExist:
        print("❌ Usuário CLEMILTON não encontrado!")
        return
    
    # 3. Verificar funções do usuário
    funcoes = UsuarioFuncao.objects.filter(usuario=usuario_clemilton)
    print(f"\n🏷️  Funções do usuário ({funcoes.count()}):")
    for funcao in funcoes:
        print(f"   - {funcao.cargo_funcao.nome} (Status: {funcao.get_status_display()})")
    
    # 4. Tentar criar vínculo se militar existir
    if militares_clemilton.exists():
        militar_clemilton = militares_clemilton.first()
        print(f"\n🔗 CRIANDO VÍNCULO:")
        print(f"   Militar: {militar_clemilton.nome_completo}")
        print(f"   Usuário: {usuario_clemilton.get_full_name()}")
        
        # Verificar se já tem vínculo
        if hasattr(militar_clemilton, 'user') and militar_clemilton.user:
            print(f"   ⚠️  Militar já tem usuário: {militar_clemilton.user.username}")
        else:
            # Criar vínculo
            militar_clemilton.user = usuario_clemilton
            militar_clemilton.save()
            print(f"   ✅ Vínculo criado com sucesso!")
            
            # Verificar novamente
            militar_clemilton.refresh_from_db()
            print(f"   ✅ Militar agora tem usuário: {militar_clemilton.user.username}")
    else:
        print(f"\n❌ Nenhum militar CLEMILTON encontrado!")
        print(f"   Buscando militares com nome similar...")
        
        # Buscar militares com nome similar
        militares_similares = Militar.objects.filter(
            nome_completo__icontains='CLEM'
        )
        print(f"   Militares com 'CLEM' ({militares_similares.count()}):")
        for militar in militares_similares:
            print(f"     - {militar.nome_completo} ({militar.get_posto_graduacao_display()})")

if __name__ == '__main__':
    verificar_militar_clemilton() 