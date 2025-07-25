#!/usr/bin/env python
"""
Script para migrar dados existentes de nome_funcao para o novo modelo CargoFuncao
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import UsuarioFuncao, CargoFuncao
from django.db import connection

def migrar_cargo_funcao():
    """Migra os dados existentes de nome_funcao para CargoFuncao"""
    print("🔄 INICIANDO MIGRAÇÃO DE CARGO_FUNCAO")
    print("=" * 60)
    
    # 1. Criar um cargo padrão para funções existentes
    cargo_padrao, created = CargoFuncao.objects.get_or_create(
        nome="Função Padrão",
        defaults={
            'descricao': 'Cargo criado automaticamente durante migração',
            'ativo': True,
            'ordem': 0
        }
    )
    
    if created:
        print(f"✅ Cargo padrão criado: {cargo_padrao.nome}")
    else:
        print(f"✅ Cargo padrão já existe: {cargo_padrao.nome}")
    
    # 2. Atualizar todas as funções existentes para usar o cargo padrão
    funcoes_sem_cargo = UsuarioFuncao.objects.filter(cargo_funcao__isnull=True)
    count = funcoes_sem_cargo.count()
    
    if count > 0:
        print(f"📋 Encontradas {count} funções sem cargo_funcao")
        
        # Atualizar em lote
        funcoes_sem_cargo.update(cargo_funcao=cargo_padrao)
        print(f"✅ {count} funções atualizadas com cargo padrão")
        
        # Mostrar algumas funções atualizadas
        print("\n📋 Exemplos de funções atualizadas:")
        for funcao in UsuarioFuncao.objects.filter(cargo_funcao=cargo_padrao)[:5]:
            print(f"   - {funcao.usuario.username}: {funcao.cargo_funcao.nome}")
    else:
        print("✅ Todas as funções já possuem cargo_funcao")
    
    # 3. Verificar se a migração foi bem-sucedida
    total_funcoes = UsuarioFuncao.objects.count()
    funcoes_com_cargo = UsuarioFuncao.objects.filter(cargo_funcao__isnull=False).count()
    
    print(f"\n📊 RESUMO DA MIGRAÇÃO:")
    print(f"   - Total de funções: {total_funcoes}")
    print(f"   - Funções com cargo: {funcoes_com_cargo}")
    print(f"   - Funções sem cargo: {total_funcoes - funcoes_com_cargo}")
    
    if funcoes_com_cargo == total_funcoes:
        print("✅ Migração concluída com sucesso!")
        return True
    else:
        print("❌ Erro na migração - algumas funções ainda não têm cargo")
        return False

if __name__ == "__main__":
    try:
        success = migrar_cargo_funcao()
        if success:
            print("\n🎉 Migração concluída! Agora você pode executar:")
            print("   python manage.py makemigrations militares")
            print("   python manage.py migrate militares")
        else:
            print("\n❌ Erro na migração. Verifique os dados e tente novamente.")
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc() 