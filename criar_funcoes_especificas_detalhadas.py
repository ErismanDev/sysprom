#!/usr/bin/env python
"""
Script para criar funções específicas detalhadas para CPO e CPP
"""
import os
import sys
import django
from datetime import date

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def criar_funcoes_especificas_detalhadas():
    """Cria funções específicas detalhadas para CPO e CPP"""
    
    # Buscar usuário padrão
    try:
        usuario_padrao = User.objects.get(username='erisman')
        print(f"✅ Usuário padrão encontrado: {usuario_padrao.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado!")
        return False
    
    # Lista de funções específicas detalhadas
    funcoes_especificas = [
        # CPO - Comissão de Promoções de Oficiais
        {
            'nome_funcao': 'Presidente da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Presidente da Comissão de Promoções de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Membro Nato da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro nato da Comissão de Promoções de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Membro Efetivo da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro efetivo da Comissão de Promoções de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Secretário da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Secretário da Comissão de Promoções de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Suplente da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro suplente da Comissão de Promoções de Oficiais',
            'status': 'ATIVO'
        },
        
        # CPP - Comissão de Promoções de Praças
        {
            'nome_funcao': 'Presidente da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Presidente da Comissão de Promoções de Praças',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Membro Nato da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro nato da Comissão de Promoções de Praças',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Membro Efetivo da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro efetivo da Comissão de Promoções de Praças',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Secretário da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Secretário da Comissão de Promoções de Praças',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Suplente da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro suplente da Comissão de Promoções de Praças',
            'status': 'ATIVO'
        }
    ]
    
    print("🔧 Criando funções específicas detalhadas para CPO e CPP...")
    print("=" * 60)
    
    funcoes_criadas = 0
    funcoes_existentes = 0
    
    for funcao_info in funcoes_especificas:
        # Verificar se a função já existe para este usuário
        funcao_existente = UsuarioFuncao.objects.filter(
            usuario=usuario_padrao,
            nome_funcao=funcao_info['nome_funcao']
        ).first()
        
        if funcao_existente:
            print(f"⚠️  Função já existe: {funcao_info['nome_funcao']}")
            funcoes_existentes += 1
        else:
            # Criar a função associada ao usuário padrão
            nova_funcao = UsuarioFuncao.objects.create(
                usuario=usuario_padrao,
                nome_funcao=funcao_info['nome_funcao'],
                tipo_funcao=funcao_info['tipo_funcao'],
                descricao=funcao_info['descricao'],
                status=funcao_info['status'],
                data_inicio=date.today(),
                observacoes='Função criada automaticamente via script'
            )
            
            print(f"✅ Função criada: {nova_funcao.nome_funcao} ({nova_funcao.get_tipo_funcao_display()})")
            funcoes_criadas += 1
    
    print("=" * 60)
    print(f"📊 Resumo:")
    print(f"   - Funções criadas: {funcoes_criadas}")
    print(f"   - Funções já existentes: {funcoes_existentes}")
    print(f"   - Total processado: {len(funcoes_especificas)}")
    
    # Mostrar funções de comissão organizadas
    print(f"\n📋 Funções de comissão disponíveis:")
    
    # CPO
    print(f"\n   🎖️  Comissão de Promoções de Oficiais (CPO):")
    funcoes_cpo = UsuarioFuncao.objects.filter(
        nome_funcao__icontains='CPO'
    ).order_by('nome_funcao')
    
    for funcao in funcoes_cpo:
        print(f"     - {funcao.nome_funcao}")
    
    # CPP
    print(f"\n   🎖️  Comissão de Promoções de Praças (CPP):")
    funcoes_cpp = UsuarioFuncao.objects.filter(
        nome_funcao__icontains='CPP'
    ).order_by('nome_funcao')
    
    for funcao in funcoes_cpp:
        print(f"     - {funcao.nome_funcao}")
    
    return True

if __name__ == '__main__':
    sucesso = criar_funcoes_especificas_detalhadas()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ Funções específicas criadas com sucesso!")
        print("\n📝 Funções disponíveis:")
        print("   CPO:")
        print("     - Presidente da CPO")
        print("     - Membro Nato da CPO")
        print("     - Membro Efetivo da CPO")
        print("     - Secretário da CPO")
        print("     - Suplente da CPO")
        print("   CPP:")
        print("     - Presidente da CPP")
        print("     - Membro Nato da CPP")
        print("     - Membro Efetivo da CPP")
        print("     - Secretário da CPP")
        print("     - Suplente da CPP")
    else:
        print("❌ Processo falhou!")
        print("   Verifique os erros acima e tente novamente.") 