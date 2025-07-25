#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, CargoFuncao
from django.db.models import Q

def testar_clemilton_lista():
    print("🔍 TESTANDO SE CLEMILTON APARECE NA LISTA CPO")
    print("=" * 50)
    
    # 1. Verificar se o vínculo foi criado
    try:
        usuario_clemilton = User.objects.get(username='361.367.943-49')
        militar_clemilton = usuario_clemilton.militar
        print(f"✅ Vínculo verificado:")
        print(f"   Usuário: {usuario_clemilton.get_full_name()}")
        print(f"   Militar: {militar_clemilton.nome_completo}")
        print(f"   Posto: {militar_clemilton.get_posto_graduacao_display()}")
        print(f"   Situação: {militar_clemilton.get_situacao_display()}")
    except Exception as e:
        print(f"❌ Erro ao verificar vínculo: {e}")
        return
    
    # 2. Testar filtros do formulário
    print(f"\n🔍 TESTANDO FILTROS DO FORMULÁRIO:")
    
    # Filtro 1: Usuários com militar vinculado e ativo
    usuarios_base = User.objects.filter(
        militar__isnull=False,
        militar__situacao='AT',
        is_active=True
    )
    print(f"   - Usuários base (com militar ativo): {usuarios_base.count()}")
    
    # Filtro 2: Apenas oficiais
    usuarios_oficiais = usuarios_base.filter(
        militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS']
    )
    print(f"   - Usuários oficiais: {usuarios_oficiais.count()}")
    
    # Filtro 3: Com função CPO ativa
    usuarios_cpo = usuarios_oficiais.filter(
        funcoes__cargo_funcao__nome__icontains='CPO',
        funcoes__status='ATIVO'
    ).distinct()
    print(f"   - Usuários com função CPO ativa: {usuarios_cpo.count()}")
    
    # Verificar se CLEMILTON está nos filtros
    clemilton_base = usuarios_base.filter(username='361.367.943-49').exists()
    clemilton_oficial = usuarios_oficiais.filter(username='361.367.943-49').exists()
    clemilton_cpo = usuarios_cpo.filter(username='361.367.943-49').exists()
    
    print(f"\n🔍 STATUS DO CLEMILTON NOS FILTROS:")
    print(f"   - Passa filtro base: {'✅' if clemilton_base else '❌'}")
    print(f"   - Passa filtro oficial: {'✅' if clemilton_oficial else '❌'}")
    print(f"   - Passa filtro CPO: {'✅' if clemilton_cpo else '❌'}")
    
    # 3. Listar todos os usuários que apareceriam na busca
    print(f"\n👥 USUÁRIOS QUE APARECERIAM NA BUSCA CPO:")
    for user in usuarios_cpo:
        militar = user.militar
        funcao_cpo = user.funcoes.filter(
            status='ATIVO',
            cargo_funcao__nome__icontains='CPO'
        ).first()
        status = "✅ CLEMILTON" if user.username == '361.367.943-49' else ""
        print(f"   - {militar.get_posto_graduacao_display()} {militar.nome_completo} ({funcao_cpo.cargo_funcao.nome if funcao_cpo else 'Sem função CPO'}) {status}")
    
    # 4. Testar a busca AJAX simulada
    print(f"\n🔍 TESTANDO BUSCA AJAX SIMULADA:")
    query = "CLEMILTON"
    
    # Simular a busca AJAX
    usuarios_busca = User.objects.filter(
        militar__isnull=False,
        militar__situacao='AT',
        is_active=True
    ).filter(
        Q(militar__nome_completo__icontains=query) |
        Q(militar__nome_guerra__icontains=query) |
        Q(militar__matricula__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(username__icontains=query)
    ).filter(
        militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS'],
        funcoes__cargo_funcao__nome__icontains='CPO',
        funcoes__status='ATIVO'
    ).distinct()
    
    print(f"   Busca por '{query}': {usuarios_busca.count()} resultados")
    for user in usuarios_busca:
        militar = user.militar
        funcao_cpo = user.funcoes.filter(
            status='ATIVO',
            cargo_funcao__nome__icontains='CPO'
        ).first()
        print(f"     ✅ {militar.get_posto_graduacao_display()} {militar.nome_completo} ({funcao_cpo.cargo_funcao.nome if funcao_cpo else 'Sem função CPO'})")

if __name__ == '__main__':
    testar_clemilton_lista() 