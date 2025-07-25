#!/usr/bin/env python
"""
Script para corrigir a sequência da tabela PermissaoFuncao no PostgreSQL
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

def corrigir_sequencia_tabela():
    """
    Corrige a sequência da tabela PermissaoFuncao
    """
    print("🔧 Corrigindo sequência da tabela PermissaoFuncao...")
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
    
    # 2. Verificar estrutura da tabela
    with connection.cursor() as cursor:
        # Verificar se a coluna id tem sequência
        cursor.execute("""
            SELECT column_default 
            FROM information_schema.columns 
            WHERE table_name = 'militares_permissaofuncao' 
            AND column_name = 'id'
        """)
        coluna_info = cursor.fetchone()
        
        if coluna_info:
            print(f"🔍 Configuração atual da coluna ID: {coluna_info[0]}")
        
        # Verificar sequências existentes
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
            AND sequence_name LIKE '%permissaofuncao%'
        """)
        sequencias = cursor.fetchall()
        
        print(f"\n🔍 Sequências relacionadas:")
        for seq in sequencias:
            print(f"   - {seq[0]}")
        
        # 3. Corrigir a sequência
        if total_registros > 0 and maior_id:
            # Encontrar a sequência correta
            nome_sequencia = None
            for seq in sequencias:
                if 'militares_permissaofuncao' in seq[0].lower():
                    nome_sequencia = seq[0]
                    break
            
            if nome_sequencia:
                print(f"\n🔧 Corrigindo sequência: {nome_sequencia}")
                
                # Definir o próximo valor da sequência como maior_id + 1
                novo_valor = maior_id + 1
                cursor.execute(f"SELECT setval('{nome_sequencia}', {novo_valor}, true)")
                
                # Verificar se foi corrigido
                cursor.execute(f"SELECT last_value FROM {nome_sequencia}")
                novo_ultimo_valor = cursor.fetchone()[0]
                
                print(f"✅ Sequência corrigida!")
                print(f"   Novo valor da sequência: {novo_ultimo_valor}")
                
                return True
            else:
                print(f"\n❌ Sequência não encontrada!")
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
    print("🚀 Iniciando correção da sequência da tabela PermissaoFuncao...")
    print("=" * 60)
    
    # Corrigir sequência
    if corrigir_sequencia_tabela():
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