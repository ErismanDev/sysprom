#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, CargoFuncao

def testar_servidor():
    print("🔍 TESTANDO SERVIDOR")
    print("=" * 30)
    
    # 1. Testar se o Django está funcionando
    try:
        total_usuarios = User.objects.count()
        total_militares = Militar.objects.count()
        print(f"✅ Django funcionando:")
        print(f"   - Total de usuários: {total_usuarios}")
        print(f"   - Total de militares: {total_militares}")
    except Exception as e:
        print(f"❌ Erro no Django: {e}")
        return
    
    # 2. Testar se o CLEMILTON está disponível
    try:
        usuario_clemilton = User.objects.get(username='361.367.943-49')
        militar_clemilton = usuario_clemilton.militar
        print(f"✅ CLEMILTON disponível:")
        print(f"   - Usuário: {usuario_clemilton.get_full_name()}")
        print(f"   - Militar: {militar_clemilton.nome_completo}")
        print(f"   - Vínculo: {'✅' if militar_clemilton.user == usuario_clemilton else '❌'}")
    except Exception as e:
        print(f"❌ Erro com CLEMILTON: {e}")
    
    # 3. Testar busca de usuários CPO
    try:
        usuarios_cpo = User.objects.filter(
            militar__isnull=False,
            militar__situacao='AT',
            is_active=True,
            militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS'],
            funcoes__cargo_funcao__nome__icontains='CPO',
            funcoes__status='ATIVO'
        ).distinct()
        
        print(f"✅ Busca CPO funcionando:")
        print(f"   - Usuários CPO encontrados: {usuarios_cpo.count()}")
        
        clemilton_cpo = usuarios_cpo.filter(username='361.367.943-49').exists()
        print(f"   - CLEMILTON na lista CPO: {'✅' if clemilton_cpo else '❌'}")
        
    except Exception as e:
        print(f"❌ Erro na busca CPO: {e}")
    
    print(f"\n🎉 Teste concluído!")

if __name__ == '__main__':
    testar_servidor() 