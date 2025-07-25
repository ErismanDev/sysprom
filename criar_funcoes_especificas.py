#!/usr/bin/env python
"""
Script para criar funções específicas para membros da CPP, CPO, diretores e chefes
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

def criar_funcoes_especificas():
    """Cria funções específicas para membros da CPP, CPO, diretores e chefes"""
    
    # Buscar ou criar usuário padrão para as funções
    try:
        usuario_padrao = User.objects.get(username='erisman')
        print(f"✅ Usuário padrão encontrado: {usuario_padrao.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado!")
        print("   Criando usuário padrão para as funções...")
        
        # Criar usuário padrão
        usuario_padrao = User.objects.create_user(
            username='admin_sistema',
            email='admin@sistema.com',
            password='admin123',
            first_name='Administrador',
            last_name='do Sistema',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Usuário padrão criado: {usuario_padrao.get_full_name()}")
    
    # Lista de funções específicas a serem criadas
    funcoes_especificas = [
        # CPP - Comissão Permanente de Promoções
        {
            'nome_funcao': 'Presidente da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Presidente da Comissão Permanente de Promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Vice-Presidente da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Vice-Presidente da Comissão Permanente de Promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Membro da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro da Comissão Permanente de Promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Secretário da CPP',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Secretário da Comissão Permanente de Promoções',
            'status': 'ATIVO'
        },
        
        # CPO - Comissão Permanente de Oficiais
        {
            'nome_funcao': 'Presidente da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Presidente da Comissão Permanente de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Vice-Presidente da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Vice-Presidente da Comissão Permanente de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Membro da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Membro da Comissão Permanente de Oficiais',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Secretário da CPO',
            'tipo_funcao': 'COMISSAO',
            'descricao': 'Secretário da Comissão Permanente de Oficiais',
            'status': 'ATIVO'
        },
        
        # Diretores
        {
            'nome_funcao': 'Diretor de Gestão de Pessoas',
            'tipo_funcao': 'GESTAO',
            'descricao': 'Diretor responsável pela gestão de pessoas',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Diretor de Promoções',
            'tipo_funcao': 'GESTAO',
            'descricao': 'Diretor responsável pelas promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Diretor de Administração',
            'tipo_funcao': 'ADMINISTRATIVO',
            'descricao': 'Diretor de administração',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Diretor de Operações',
            'tipo_funcao': 'OPERACIONAL',
            'descricao': 'Diretor de operações',
            'status': 'ATIVO'
        },
        
        # Chefes
        {
            'nome_funcao': 'Chefe da Seção de Promoções',
            'tipo_funcao': 'GESTAO',
            'descricao': 'Chefe da seção responsável pelas promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Chefe da Seção de Pessoal',
            'tipo_funcao': 'ADMINISTRATIVO',
            'descricao': 'Chefe da seção de pessoal',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Chefe da Seção de Administração',
            'tipo_funcao': 'ADMINISTRATIVO',
            'descricao': 'Chefe da seção de administração',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Chefe da Seção de Operações',
            'tipo_funcao': 'OPERACIONAL',
            'descricao': 'Chefe da seção de operações',
            'status': 'ATIVO'
        },
        
        # Outras funções importantes
        {
            'nome_funcao': 'Assessor de Promoções',
            'tipo_funcao': 'GESTAO',
            'descricao': 'Assessor especializado em promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Analista de Promoções',
            'tipo_funcao': 'ADMINISTRATIVO',
            'descricao': 'Analista responsável pelo processamento de promoções',
            'status': 'ATIVO'
        },
        {
            'nome_funcao': 'Coordenador de Comissões',
            'tipo_funcao': 'GESTAO',
            'descricao': 'Coordenador das comissões de promoções',
            'status': 'ATIVO'
        }
    ]
    
    print("🔧 Criando funções específicas para o sistema...")
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
    
    # Mostrar todas as funções disponíveis
    print(f"\n📋 Funções disponíveis no sistema:")
    todas_funcoes = UsuarioFuncao.objects.all().order_by('tipo_funcao', 'nome_funcao')
    
    tipos_agrupados = {}
    for funcao in todas_funcoes:
        tipo = funcao.get_tipo_funcao_display()
        if tipo not in tipos_agrupados:
            tipos_agrupados[tipo] = []
        tipos_agrupados[tipo].append(funcao.nome_funcao)
    
    for tipo, funcoes in tipos_agrupados.items():
        print(f"\n   {tipo}:")
        for funcao in funcoes:
            print(f"     - {funcao}")
    
    return True

if __name__ == '__main__':
    sucesso = criar_funcoes_especificas()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ Processo concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. As funções estão disponíveis para serem associadas aos usuários")
        print("   2. Use o sistema para associar funções aos usuários específicos")
        print("   3. Cada usuário pode ter múltiplas funções")
        print("   4. As funções foram criadas associadas ao usuário padrão")
    else:
        print("❌ Processo falhou!")
        print("   Verifique os erros acima e tente novamente.") 