#!/usr/bin/env python
"""
Script para verificar assinaturas existentes e como estão sendo exibidas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, QuadroAcesso
from django.contrib.auth.models import User

def verificar_assinaturas_existentes():
    """Verifica assinaturas existentes"""
    
    print("🔍 Verificando assinaturas existentes...")
    
    # Verificar todas as assinaturas de quadro de acesso
    assinaturas = AssinaturaQuadroAcesso.objects.all()
    print(f"  📊 Total de assinaturas: {assinaturas.count()}")
    
    for assinatura in assinaturas:
        print(f"\n  📄 Assinatura ID: {assinatura.pk}")
        print(f"    - Data: {assinatura.data_assinatura}")
        print(f"    - Tipo: {assinatura.get_tipo_assinatura_display()}")
        print(f"    - Função: {assinatura.funcao_assinatura}")
        
        if assinatura.assinado_por:
            print(f"    - Assinado por: {assinatura.assinado_por.username}")
            
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                print(f"    - Militar: {militar.nome_completo}")
                print(f"    - Posto: {militar.get_posto_graduacao_display()}")
                
                # Simular como deveria aparecer
                posto = militar.get_posto_graduacao_display()
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo_bm = f"{posto} {militar.nome_completo}"
                print(f"    - Deveria aparecer: {nome_completo_bm}")
            else:
                print(f"    - Nome do usuário: {assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username}")

def verificar_quadros_com_assinaturas():
    """Verifica quadros que têm assinaturas"""
    
    print("\n📋 Verificando quadros com assinaturas...")
    
    quadros = QuadroAcesso.objects.all()
    for quadro in quadros:
        assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False)
        if assinaturas.exists():
            print(f"  📄 Quadro {quadro.pk}: {assinaturas.count()} assinatura(s)")
            for assinatura in assinaturas:
                print(f"    - Assinatura {assinatura.pk}: {assinatura.assinado_por.username}")

def testar_template_tag_diretamente():
    """Testa o template tag diretamente"""
    
    print("\n🔧 Testando template tag diretamente...")
    
    try:
        from militares.templatetags.militares_extras import nome_completo_militar
        
        # Buscar militar José ERISMAN
        militar = Militar.objects.get(nome_completo__icontains="ERISMAN")
        nome_formatado = nome_completo_militar(militar)
        print(f"  ✅ Nome formatado: {nome_formatado}")
        
        # Testar com outros militares
        outros_militares = Militar.objects.all()[:3]
        for militar in outros_militares:
            nome_formatado = nome_completo_militar(militar)
            print(f"  📝 {militar.nome_completo}: {nome_formatado}")
            
    except Exception as e:
        print(f"  ❌ Erro ao testar template tag: {e}")

def verificar_views_modificadas():
    """Verifica se as views foram modificadas corretamente"""
    
    print("\n🔧 Verificando se as views foram modificadas...")
    
    try:
        with open("militares/views.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se o código de BM foi adicionado
        if "Adicionar BM após o posto se não já estiver presente" in content:
            print("  ✅ Views modificadas - código BM encontrado")
        else:
            print("  ❌ Views não modificadas - código BM não encontrado")
            
        # Verificar se há backup
        if os.path.exists("militares/views.py.backup_bm"):
            print("  ✅ Backup encontrado")
        else:
            print("  ⚠️  Backup não encontrado")
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar views: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando verificação das assinaturas...")
    
    # Verificar assinaturas existentes
    verificar_assinaturas_existentes()
    
    # Verificar quadros com assinaturas
    verificar_quadros_com_assinaturas()
    
    # Testar template tag
    testar_template_tag_diretamente()
    
    # Verificar views
    verificar_views_modificadas()
    
    print("\n✅ Verificação concluída!") 