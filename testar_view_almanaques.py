#!/usr/bin/env python
"""
Script para testar se a view almanaque_list funciona para superusuários
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from militares.views import almanaque_list
from militares.models import AlmanaqueMilitar

def testar_view_almanaques():
    """Testa se a view almanaque_list funciona para superusuários"""
    
    print("🧪 TESTANDO VIEW ALMANAQUES")
    print("=" * 60)
    
    # Buscar usuário admin
    try:
        user_admin = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user_admin.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    # Verificar dados do usuário
    print(f"📊 Dados do usuário:")
    print(f"   • is_superuser: {user_admin.is_superuser}")
    print(f"   • is_staff: {user_admin.is_staff}")
    
    # Verificar funções
    from militares.models import UsuarioFuncao
    funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    funcoes_especiais = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    
    print(f"   • Tem funções especiais: {funcoes_especiais.exists()}")
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"     - {funcao.cargo_funcao.nome}")
    
    # Verificar almanaques no banco
    print(f"\n📋 ALMANAQUES NO BANCO:")
    total_almanaques = AlmanaqueMilitar.objects.count()
    almanaques_ativos = AlmanaqueMilitar.objects.filter(ativo=True).count()
    
    print(f"   • Total de almanaques: {total_almanaques}")
    print(f"   • Almanaques ativos: {almanaques_ativos}")
    
    if almanaques_ativos > 0:
        almanaques = AlmanaqueMilitar.objects.filter(ativo=True)
        for almanaque in almanaques:
            print(f"     - {almanaque.titulo} ({almanaque.tipo})")
    
    # Testar a view
    print(f"\n🧪 TESTANDO VIEW:")
    factory = RequestFactory()
    request = factory.get('/militares/almanaques/')
    request.user = user_admin
    
    try:
        response = almanaque_list(request)
        print(f"   • Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ View funcionou corretamente!")
            
            # Verificar se o contexto tem almanaques
            if hasattr(response, 'context_data'):
                context = response.context_data
                almanaques_context = context.get('almanaques', [])
                total_context = context.get('total_almanaques', 0)
                
                print(f"   • Almanaques no contexto: {len(almanaques_context)}")
                print(f"   • Total no contexto: {total_context}")
                
                if len(almanaques_context) > 0:
                    print("   ✅ Almanaques estão sendo passados para o template!")
                    for almanaque in almanaques_context:
                        print(f"     - {almanaque.titulo} ({almanaque.tipo})")
                else:
                    print("   ❌ Nenhum almanaque no contexto")
            else:
                print("   ⚠️ Não foi possível verificar o contexto")
        else:
            print(f"   ❌ View retornou erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar view: {e}")
        import traceback
        traceback.print_exc()
    
    # Verificar lógica da view
    print(f"\n🔍 LÓGICA DA VIEW:")
    
    # Simular a lógica da view
    if user_admin.is_superuser or user_admin.is_staff or funcoes_especiais.exists():
        print("   ✅ Usuário tem acesso total (superusuário/staff/funções especiais)")
        almanaques_esperados = AlmanaqueMilitar.objects.filter(ativo=True).count()
        print(f"   📋 Deveria ver: {almanaques_esperados} almanaques")
    else:
        print("   ❌ Usuário não tem acesso total")
        
        # Verificar membros de comissão
        from militares.models import MembroComissao
        membros = MembroComissao.objects.filter(usuario=user_admin, ativo=True, comissao__status='ATIVA')
        
        if membros.exists():
            tem_cpo = membros.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros.filter(comissao__tipo='CPP').exists()
            
            print(f"   • É membro CPO: {tem_cpo}")
            print(f"   • É membro CPP: {tem_cpp}")
            
            if tem_cpo and tem_cpp:
                print("   ✅ Membro das duas comissões - deveria ver TODOS")
            elif tem_cpo:
                print("   ✅ Membro CPO - deveria ver OFICIAIS")
            elif tem_cpp:
                print("   ✅ Membro CPP - deveria ver PRACAS")
        else:
            print("   ❌ Não é membro de comissão")

if __name__ == "__main__":
    testar_view_almanaques() 