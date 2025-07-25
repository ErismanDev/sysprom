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

def investigar_usuario_clemilton():
    print("🔍 INVESTIGANDO USUÁRIO CLEMILTON AQUINO ALMEIDA")
    print("=" * 60)
    
    # 1. Buscar o usuário
    try:
        usuario = User.objects.get(username='361.367.943-49')
        print(f"✅ Usuário encontrado: {usuario.get_full_name()}")
        print(f"   - Username: {usuario.username}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Ativo: {usuario.is_active}")
    except User.DoesNotExist:
        print("❌ Usuário não encontrado!")
        return
    
    # 2. Verificar militar vinculado
    try:
        militar = usuario.militar
        print(f"\n🎖️  Militar vinculado:")
        print(f"   - Nome: {militar.nome_completo}")
        print(f"   - Posto: {militar.get_posto_graduacao_display()}")
        print(f"   - Matrícula: {militar.matricula}")
        print(f"   - Situação: {militar.get_situacao_display()}")
        print(f"   - Ativo: {militar.situacao == 'AT'}")
    except Militar.DoesNotExist:
        print("❌ Militar não encontrado!")
        return
    
    # 3. Verificar funções do usuário
    funcoes = UsuarioFuncao.objects.filter(usuario=usuario)
    print(f"\n🏷️  Funções do usuário ({funcoes.count()} total):")
    
    for funcao in funcoes:
        print(f"   - {funcao.cargo_funcao.nome}")
        print(f"     Status: {funcao.get_status_display()}")
        print(f"     Tipo: {funcao.get_tipo_funcao_display()}")
        print(f"     Data início: {funcao.data_inicio}")
        print(f"     Data fim: {funcao.data_fim}")
        print()
    
    # 4. Verificar funções CPO especificamente
    funcoes_cpo = UsuarioFuncao.objects.filter(
        usuario=usuario,
        cargo_funcao__nome__icontains='CPO',
        status='ATIVO'
    )
    print(f"🎖️  Funções CPO ativas ({funcoes_cpo.count()}):")
    for funcao in funcoes_cpo:
        print(f"   ✅ {funcao.cargo_funcao.nome}")
    
    # 5. Testar filtros do formulário
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
    
    # 6. Verificar se há problemas com as datas
    from datetime import date
    hoje = date.today()
    
    funcoes_ativas_hoje = UsuarioFuncao.objects.filter(
        usuario=usuario,
        status='ATIVO',
        data_inicio__lte=hoje,
        cargo_funcao__nome__icontains='CPO'
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    )
    
    print(f"\n📅 FUNÇÕES CPO ATIVAS HOJE ({funcoes_ativas_hoje.count()}):")
    for funcao in funcoes_ativas_hoje:
        print(f"   ✅ {funcao.cargo_funcao.nome}")
        print(f"      Início: {funcao.data_inicio}")
        print(f"      Fim: {funcao.data_fim or 'Indefinido'}")
    
    # 7. Listar todos os usuários que apareceriam na busca
    print(f"\n👥 USUÁRIOS QUE APARECERIAM NA BUSCA CPO:")
    for user in usuarios_cpo:
        militar = user.militar
        funcao_cpo = user.funcoes.filter(
            status='ATIVO',
            cargo_funcao__nome__icontains='CPO'
        ).first()
        print(f"   - {militar.get_posto_graduacao_display()} {militar.nome_completo} ({funcao_cpo.cargo_funcao.nome if funcao_cpo else 'Sem função CPO'})")

if __name__ == '__main__':
    investigar_usuario_clemilton() 