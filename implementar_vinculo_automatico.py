#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, CargoFuncao

def implementar_vinculo_automatico():
    print("🔧 IMPLEMENTANDO VÍNCULO AUTOMÁTICO")
    print("=" * 50)
    
    # 1. Verificar usuários sem militar vinculado
    usuarios_sem_militar = User.objects.filter(
        militar__isnull=True,
        is_active=True
    )
    
    print(f"📋 Usuários sem militar vinculado ({usuarios_sem_militar.count()}):")
    for usuario in usuarios_sem_militar:
        print(f"   - {usuario.get_full_name()} ({usuario.username})")
    
    # 2. Tentar vincular automaticamente
    print(f"\n🔗 VINCULANDO AUTOMATICAMENTE:")
    vinculados = 0
    
    for usuario in usuarios_sem_militar:
        # Buscar militar pelo nome
        nome_completo = usuario.get_full_name()
        if nome_completo:
            militares_encontrados = Militar.objects.filter(
                nome_completo__icontains=nome_completo.split()[0]  # Primeiro nome
            )
            
            if militares_encontrados.exists():
                militar = militares_encontrados.first()
                
                # Verificar se o militar já tem usuário
                if not hasattr(militar, 'user') or not militar.user:
                    # Vincular
                    militar.user = usuario
                    militar.save()
                    print(f"   ✅ {usuario.get_full_name()} → {militar.nome_completo}")
                    vinculados += 1
                else:
                    print(f"   ⚠️  {usuario.get_full_name()} - Militar já tem usuário: {militar.user.username}")
            else:
                print(f"   ❌ {usuario.get_full_name()} - Militar não encontrado")
    
    print(f"\n📊 RESULTADO:")
    print(f"   - Usuários vinculados: {vinculados}")
    
    # 3. Verificar usuários com funções mas sem militar
    usuarios_com_funcoes = User.objects.filter(
        militar__isnull=True,
        funcoes__isnull=False
    ).distinct()
    
    print(f"\n🏷️  Usuários com funções mas sem militar ({usuarios_com_funcoes.count()}):")
    for usuario in usuarios_com_funcoes:
        funcoes = usuario.funcoes.all()
        nomes_funcoes = [f.cargo_funcao.nome for f in funcoes]
        print(f"   - {usuario.get_full_name()}: {', '.join(nomes_funcoes)}")
    
    # 4. Verificar militares sem usuário
    militares_sem_usuario = Militar.objects.filter(
        user__isnull=True,
        situacao='AT'
    )
    
    print(f"\n🎖️  Militares ativos sem usuário ({militares_sem_usuario.count()}):")
    for militar in militares_sem_usuario[:10]:  # Mostrar apenas os primeiros 10
        print(f"   - {militar.get_posto_graduacao_display()} {militar.nome_completo}")
    
    if militares_sem_usuario.count() > 10:
        print(f"   ... e mais {militares_sem_usuario.count() - 10} militares")
    
    print(f"\n🎉 Implementação concluída!")

if __name__ == '__main__':
    implementar_vinculo_automatico() 