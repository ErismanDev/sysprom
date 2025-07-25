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

def corrigir_sequencia_tabela_postgresql():
    """
    Corrige a sequência da tabela PermissaoFuncao no PostgreSQL
    """
    print("🔧 Corrigindo sequência da tabela PermissaoFuncao no PostgreSQL...")
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
    
    # 2. Corrigir a sequência no PostgreSQL
    with connection.cursor() as cursor:
        try:
            # Verificar a sequência atual da tabela
            cursor.execute("""
                SELECT pg_get_serial_sequence('militares_permissaofuncao', 'id')
            """)
            sequencia_atual = cursor.fetchone()[0]
            
            if sequencia_atual:
                print(f"🔍 Sequência atual da tabela: {sequencia_atual}")
                
                # Corrigir a sequência
                novo_valor = maior_id + 1
                cursor.execute(f"SELECT setval('{sequencia_atual}', {novo_valor}, true)")
                
                # Verificar se foi corrigido
                cursor.execute(f"SELECT last_value FROM {sequencia_atual}")
                novo_ultimo_valor = cursor.fetchone()[0]
                
                print(f"✅ Sequência corrigida!")
                print(f"   Novo valor da sequência: {novo_ultimo_valor}")
                
                return True
            else:
                print("❌ Nenhuma sequência encontrada para a tabela!")
                
                # Tentar criar uma sequência para a tabela
                print("🔧 Tentando criar sequência para a tabela...")
                
                # Verificar se existe uma sequência com nome padrão
                cursor.execute("""
                    SELECT sequence_name 
                    FROM information_schema.sequences 
                    WHERE sequence_name = 'militares_permissaofuncao_id_seq'
                """)
                seq_padrao = cursor.fetchone()
                
                if seq_padrao:
                    print(f"🔍 Sequência padrão encontrada: {seq_padrao[0]}")
                    
                    # Corrigir a sequência padrão
                    novo_valor = maior_id + 1
                    cursor.execute(f"SELECT setval('{seq_padrao[0]}', {novo_valor}, true)")
                    
                    # Associar a sequência à tabela
                    cursor.execute(f"""
                        ALTER TABLE militares_permissaofuncao 
                        ALTER COLUMN id SET DEFAULT nextval('{seq_padrao[0]}')
                    """)
                    
                    print(f"✅ Sequência associada à tabela!")
                    return True
                else:
                    print("❌ Nenhuma sequência padrão encontrada!")
                    return False
                
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
    print("🚀 Iniciando correção da sequência no PostgreSQL...")
    print("=" * 60)
    
    # Corrigir sequência
    if corrigir_sequencia_tabela_postgresql():
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