#!/usr/bin/env python
"""
Script para modificar as views para incluir 'BM' após o posto nas assinaturas eletrônicas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, AssinaturaAta
from django.contrib.auth.models import User

def modificar_views_para_bm():
    """Modifica as views para incluir 'BM' após o posto"""
    
    print("🔧 Modificando views para incluir 'BM' após o posto...")
    
    # Ler o arquivo views.py
    views_file = "militares/views.py"
    
    try:
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar ocorrências antes da modificação
        ocorrencias_antes = content.count("nome_assinante = assinatura.assinado_por.get_full_name()")
        print(f"  📊 Ocorrências encontradas: {ocorrencias_antes}")
        
        # Modificar as ocorrências para incluir BM
        # Substituir o bloco de código que define nome_assinante
        old_pattern = """            # Informações de assinatura eletrônica
            nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
"""
        
        new_pattern = """            # Informações de assinatura eletrônica
            nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            # Se o usuário tem militar associado, incluir posto com BM
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_assinante = f"{posto} {militar.nome_completo}"
"""
        
        # Fazer a substituição
        content_modified = content.replace(old_pattern, new_pattern)
        
        # Verificar se houve mudança
        if content_modified != content:
            # Fazer backup
            backup_file = "militares/views.py.backup_bm"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  💾 Backup criado: {backup_file}")
            
            # Salvar o arquivo modificado
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(content_modified)
            
            print("  ✅ Views modificadas com sucesso!")
            print("  📝 Agora as assinaturas eletrônicas incluirão 'BM' após o posto")
        else:
            print("  ⚠️  Nenhuma modificação foi necessária (padrão não encontrado)")
    
    except Exception as e:
        print(f"  ❌ Erro ao modificar views: {e}")

def verificar_militar_erisman():
    """Verifica o militar José ERISMAN"""
    
    print("\n🔍 Verificando militar José ERISMAN...")
    
    try:
        militar = Militar.objects.get(nome_completo__icontains="ERISMAN")
        print(f"  ✅ Militar encontrado: {militar.nome_completo}")
        print(f"  📋 Posto: {militar.get_posto_graduacao_display()}")
        print(f"  📋 Posto com BM: {militar.get_posto_graduacao_display()} BM")
        
        # Verificar se tem usuário associado
        if hasattr(militar, 'user') and militar.user:
            print(f"  👤 Usuário associado: {militar.user.username}")
        else:
            print("  ⚠️  Sem usuário associado")
            
    except Militar.DoesNotExist:
        print("  ❌ Militar José ERISMAN não encontrado")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando modificação das views para incluir 'BM'...")
    
    # Verificar militar ERISMAN
    verificar_militar_erisman()
    
    # Modificar views
    modificar_views_para_bm()
    
    print("\n✅ Processo concluído!") 