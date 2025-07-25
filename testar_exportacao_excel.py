#!/usr/bin/env python
"""
Script para testar a funcionalidade de exportação Excel
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from militares.views import exportar_militares_excel
from militares.models import Militar

def testar_exportacao_excel():
    """
    Testa a funcionalidade de exportação Excel
    """
    print("🧪 Testando funcionalidade de exportação Excel...")
    
    # Criar um request factory
    factory = RequestFactory()
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_exportacao',
        defaults={
            'email': 'teste@teste.com',
            'first_name': 'Usuário',
            'last_name': 'Teste'
        }
    )
    
    # Criar um request
    request = factory.get('/militares/exportar-excel/')
    request.user = user
    
    try:
        # Chamar a view
        response = exportar_militares_excel(request)
        
        print(f"✅ Status da resposta: {response.status_code}")
        print(f"📊 Tipo de conteúdo: {response.get('Content-Type', 'Não definido')}")
        print(f"📁 Nome do arquivo: {response.get('Content-Disposition', 'Não definido')}")
        
        # Verificar se a resposta contém dados
        content = response.content.decode('utf-8')
        lines = content.split('\n')
        
        print(f"📋 Total de linhas: {len(lines)}")
        
        if len(lines) > 1:
            print("📋 Primeiras linhas do arquivo:")
            for i, line in enumerate(lines[:5]):
                print(f"  {i+1}: {line[:100]}...")
        
        # Verificar se há militares no arquivo
        militares_count = Militar.objects.filter(situacao='AT').count()
        print(f"👥 Total de militares ativos no banco: {militares_count}")
        
        # Contar linhas de dados (excluindo cabeçalho e linha vazia final)
        data_lines = len([line for line in lines if line.strip() and not line.startswith('Matrícula')])
        print(f"📊 Linhas de dados no arquivo: {data_lines}")
        
        if data_lines == militares_count:
            print("✅ Número de militares no arquivo corresponde ao banco!")
        else:
            print(f"⚠️  Diferença: {militares_count} no banco vs {data_lines} no arquivo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar exportação: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_exportacao_com_filtros():
    """
    Testa a exportação com diferentes filtros
    """
    print("\n🔍 Testando exportação com filtros...")
    
    factory = RequestFactory()
    user, created = User.objects.get_or_create(
        username='teste_exportacao',
        defaults={
            'email': 'teste@teste.com',
            'first_name': 'Usuário',
            'last_name': 'Teste'
        }
    )
    
    # Testar com filtro de posto
    request = factory.get('/militares/exportar-excel/?posto=cb')
    request.user = user
    
    try:
        response = exportar_militares_excel(request)
        content = response.content.decode('utf-8')
        lines = content.split('\n')
        data_lines = len([line for line in lines if line.strip() and not line.startswith('Matrícula')])
        
        coronais_count = Militar.objects.filter(situacao='AT', posto_graduacao='CB').count()
        print(f"👑 Coronéis no banco: {coronais_count}, no arquivo: {data_lines}")
        
        if data_lines == coronais_count:
            print("✅ Filtro por posto funcionando corretamente!")
        else:
            print("⚠️  Problema com filtro por posto")
            
    except Exception as e:
        print(f"❌ Erro ao testar filtro: {e}")

def verificar_estrutura_arquivo():
    """
    Verifica a estrutura do arquivo gerado
    """
    print("\n📋 Verificando estrutura do arquivo...")
    
    factory = RequestFactory()
    user, created = User.objects.get_or_create(
        username='teste_exportacao',
        defaults={
            'email': 'teste@teste.com',
            'first_name': 'Usuário',
            'last_name': 'Teste'
        }
    )
    
    request = factory.get('/militares/exportar-excel/')
    request.user = user
    
    try:
        response = exportar_militares_excel(request)
        content = response.content.decode('utf-8')
        lines = content.split('\n')
        
        if lines:
            # Verificar cabeçalho
            header = lines[0]
            campos = header.split(';')
            print(f"📊 Total de campos: {len(campos)}")
            print("📋 Campos disponíveis:")
            for i, campo in enumerate(campos, 1):
                print(f"  {i:2d}. {campo}")
            
            # Verificar se há dados
            if len(lines) > 1:
                primeira_linha_dados = lines[1]
                dados = primeira_linha_dados.split(';')
                print(f"\n📊 Primeira linha de dados tem {len(dados)} campos")
                
                # Mostrar alguns dados de exemplo
                if len(dados) >= 5:
                    print("📋 Exemplo de dados:")
                    print(f"  Matrícula: {dados[0]}")
                    print(f"  Nome: {dados[1]}")
                    print(f"  Nome de Guerra: {dados[2]}")
                    print(f"  CPF: {dados[3]}")
                    print(f"  Posto: {dados[4]}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

def main():
    """
    Função principal
    """
    print("🚀 Iniciando testes de exportação Excel...")
    print("=" * 60)
    
    # Testar exportação básica
    sucesso = testar_exportacao_excel()
    
    if sucesso:
        # Testar com filtros
        testar_exportacao_com_filtros()
        
        # Verificar estrutura
        verificar_estrutura_arquivo()
    
    print("\n" + "=" * 60)
    print("🏁 Testes concluídos!")

if __name__ == '__main__':
    main() 