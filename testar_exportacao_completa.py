#!/usr/bin/env python
"""
Script para testar a funcionalidade completa de exportação Excel
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

def testar_exportacao_completa():
    """
    Testa a exportação completa com diferentes cenários
    """
    print("🚀 Testando funcionalidade completa de exportação Excel...")
    print("=" * 60)
    
    factory = RequestFactory()
    user, created = User.objects.get_or_create(
        username='teste_exportacao',
        defaults={
            'email': 'teste@teste.com',
            'first_name': 'Usuário',
            'last_name': 'Teste'
        }
    )
    
    # Cenários de teste
    cenarios = [
        {
            'nome': 'Todos os militares',
            'url': '/militares/exportar-excel/',
            'descricao': 'Exportação sem filtros'
        },
        {
            'nome': 'Apenas Coronéis',
            'url': '/militares/exportar-excel/?posto=cb',
            'descricao': 'Filtro por posto CB (Coronel)'
        },
        {
            'nome': 'Apenas Majores',
            'url': '/militares/exportar-excel/?posto=mj',
            'descricao': 'Filtro por posto MJ (Major)'
        },
        {
            'nome': 'Quadro Combatente',
            'url': '/militares/exportar-excel/?quadro=COMB',
            'descricao': 'Filtro por quadro Combatente'
        },
        {
            'nome': 'Busca por nome',
            'url': '/militares/exportar-excel/?q=JOSÉ',
            'descricao': 'Busca por nome contendo JOSÉ'
        },
        {
            'nome': 'Múltiplos filtros',
            'url': '/militares/exportar-excel/?posto=cb&quadro=COMB',
            'descricao': 'Coronéis do quadro Combatente'
        }
    ]
    
    resultados = []
    
    for cenario in cenarios:
        print(f"\n📋 Testando: {cenario['nome']}")
        print(f"   Descrição: {cenario['descricao']}")
        
        request = factory.get(cenario['url'])
        request.user = user
        
        try:
            response = exportar_militares_excel(request)
            content = response.content.decode('utf-8')
            lines = content.split('\n')
            
            # Contar linhas de dados (excluindo cabeçalho)
            data_lines = len([line for line in lines if line.strip() and not line.startswith('Matrícula')])
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Linhas de dados: {data_lines}")
            print(f"   📁 Arquivo: {response.get('Content-Disposition', 'N/A')}")
            
            resultados.append({
                'cenario': cenario['nome'],
                'status': 'SUCESSO',
                'linhas': data_lines,
                'filename': response.get('Content-Disposition', 'N/A')
            })
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            resultados.append({
                'cenario': cenario['nome'],
                'status': 'ERRO',
                'erro': str(e)
            })
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    sucessos = 0
    erros = 0
    
    for resultado in resultados:
        if resultado['status'] == 'SUCESSO':
            print(f"✅ {resultado['cenario']}: {resultado['linhas']} militares")
            sucessos += 1
        else:
            print(f"❌ {resultado['cenario']}: {resultado['erro']}")
            erros += 1
    
    print(f"\n📈 Total de testes: {len(resultados)}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    
    if erros == 0:
        print("\n🎉 Todos os testes passaram com sucesso!")
    else:
        print(f"\n⚠️  {erros} teste(s) falharam")

def verificar_estrutura_dados():
    """
    Verifica a estrutura dos dados exportados
    """
    print("\n🔍 Verificando estrutura dos dados...")
    
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
        
        if len(lines) > 1:
            # Verificar cabeçalho
            header = lines[0]
            campos = header.split(';')
            
            print(f"📊 Total de campos: {len(campos)}")
            print("📋 Campos disponíveis:")
            for i, campo in enumerate(campos, 1):
                print(f"  {i:2d}. {campo}")
            
            # Verificar primeira linha de dados
            primeira_linha = lines[1]
            dados = primeira_linha.split(';')
            
            print(f"\n📊 Primeira linha de dados:")
            for i, (campo, valor) in enumerate(zip(campos, dados), 1):
                print(f"  {i:2d}. {campo}: {valor}")
            
            # Verificar se há caracteres especiais
            caracteres_especiais = []
            for i, char in enumerate(primeira_linha):
                if ord(char) > 127:
                    caracteres_especiais.append(f"Posição {i}: '{char}' (U+{ord(char):04X})")
            
            if caracteres_especiais:
                print(f"\n⚠️  Caracteres especiais encontrados:")
                for char_info in caracteres_especiais[:5]:
                    print(f"  - {char_info}")
            else:
                print("\n✅ Nenhum caractere especial problemático encontrado")
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

def main():
    """
    Função principal
    """
    # Testar exportação completa
    testar_exportacao_completa()
    
    # Verificar estrutura dos dados
    verificar_estrutura_dados()
    
    print("\n" + "=" * 60)
    print("🏁 Testes completos finalizados!")

if __name__ == '__main__':
    main() 