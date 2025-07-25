#!/usr/bin/env python
"""
Script para corrigir diretamente a sequência da tabela PermissaoFuncao
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import connection, models
from militares.models import PermissaoFuncao

def corrigir_sequencia_direta():
    """
    Corrige a sequência diretamente usando SQL
    """
    print("🔧 Corrigindo sequência diretamente...")
    print("=" * 60)
    
    # 1. Verificar registros existentes
    total_registros = PermissaoFuncao.objects.count()
    print(f"📊 Total de registros na tabela: {total_registros}")
    
    if total_registros > 0:
        # Buscar o maior ID
        maior_id = PermissaoFuncao.objects.aggregate(
            models.Max('id')
        )['id__max']
        print(f"📊 Maior ID encontrado: {maior_id}")
    
    # 2. Corrigir a sequência diretamente
    with connection.cursor() as cursor:
        try:
            # Verificar se a sequência existe
            cursor.execute("SELECT last_value FROM permissaofuncao")
            ultimo_valor = cursor.fetchone()[0]
            print(f"🔍 Último valor da sequência atual: {ultimo_valor}")
            
            # Corrigir a sequência
            novo_valor = maior_id + 1
            cursor.execute(f"SELECT setval('permissaofuncao', {novo_valor}, true)")
            
            # Verificar se foi corrigido
            cursor.execute("SELECT last_value FROM permissaofuncao")
            novo_ultimo_valor = cursor.fetchone()[0]
            
            print(f"✅ Sequência corrigida!")
            print(f"   Novo valor da sequência: {novo_ultimo_valor}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao corrigir sequência: {e}")
            return False
    
    return True

def testar_criacao_permissao():
    """
    Testa a criação de uma nova permissão
    """
    print(f"\n🧪 Testando criação de nova permissão...")
    
    try:
        # Tentar criar uma permissão de teste
        permissao_teste = PermissaoFuncao.objects.create(
            modulo='TESTE',
            acesso='VISUALIZAR',
            ativo=True,
            observacoes='Permissão de teste para verificar sequência'
        )
        
        print(f"✅ Permissão de teste criada com sucesso!")
        print(f"   ID: {permissao_teste.id}")
        print(f"   Módulo: {permissao_teste.modulo}")
        print(f"   Acesso: {permissao_teste.acesso}")
        
        # Remover a permissão de teste
        permissao_teste.delete()
        print(f"🗑️  Permissão de teste removida")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar permissão de teste: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 Iniciando correção direta da sequência...")
    print("=" * 60)
    
    # Corrigir sequência
    if corrigir_sequencia_direta():
        print("\n✅ Correção concluída!")
        
        # Testar criação
        if testar_criacao_permissao():
            print("\n🎉 Problema resolvido! A sequência está funcionando corretamente.")
        else:
            print("\n❌ Ainda há problemas com a sequência.")
    else:
        print("\n❌ Falha na correção da sequência.")
    
    print("\n" + "=" * 60)
    print("🏁 Processo concluído!")

if __name__ == '__main__':
    main() 