#!/usr/bin/env python
"""
Script para associar uma função ao usuário erisman
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

def associar_funcao_usuario():
    """Associa uma função administrativa ao usuário erisman"""
    
    try:
        # Buscar o usuário erisman
        usuario = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {usuario.get_full_name()} ({usuario.username})")
        
        # Verificar se já tem funções
        funcoes_existentes = UsuarioFuncao.objects.filter(usuario=usuario)
        if funcoes_existentes.exists():
            print(f"⚠️  Usuário já possui {funcoes_existentes.count()} função(ões):")
            for funcao in funcoes_existentes:
                print(f"   - {funcao.nome_funcao} ({funcao.get_tipo_funcao_display()}) - {funcao.get_status_display()}")
        
        # Criar função administrativa
        funcao_admin = UsuarioFuncao.objects.create(
            usuario=usuario,
            nome_funcao='Administrador do Sistema',
            tipo_funcao='ADMINISTRATIVO',
            descricao='Função administrativa com acesso total ao sistema',
            status='ATIVO',
            data_inicio=date.today(),
            observacoes='Função criada automaticamente via script'
        )
        
        print(f"✅ Função criada com sucesso:")
        print(f"   - Nome: {funcao_admin.nome_funcao}")
        print(f"   - Tipo: {funcao_admin.get_tipo_funcao_display()}")
        print(f"   - Status: {funcao_admin.get_status_display()}")
        print(f"   - Data Início: {funcao_admin.data_inicio}")
        
        # Verificar se agora tem funções ativas
        funcoes_ativas = UsuarioFuncao.objects.filter(
            usuario=usuario,
            status='ATIVO'
        )
        
        print(f"\n📊 Resumo:")
        print(f"   - Total de funções: {funcoes_existentes.count() + 1}")
        print(f"   - Funções ativas: {funcoes_ativas.count()}")
        
        if funcoes_ativas.count() == 1:
            print("✅ Usuário agora pode acessar o sistema normalmente!")
        else:
            print("⚠️  Usuário terá que selecionar uma função ao fazer login.")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Erro: Usuário 'erisman' não encontrado!")
        print("   Verifique se o usuário existe no sistema.")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao associar função: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Associando função ao usuário erisman...")
    print("=" * 50)
    
    sucesso = associar_funcao_usuario()
    
    print("=" * 50)
    if sucesso:
        print("✅ Processo concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Faça login com o usuário 'erisman'")
        print("   2. Se tiver múltiplas funções, selecione uma")
        print("   3. Acesse o sistema normalmente")
    else:
        print("❌ Processo falhou!")
        print("   Verifique os erros acima e tente novamente.") 