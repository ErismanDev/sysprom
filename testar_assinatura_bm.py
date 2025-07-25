#!/usr/bin/env python
"""
Script para testar as assinaturas com 'BM' após o posto
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, QuadroAcesso
from django.contrib.auth.models import User

def testar_assinatura_bm():
    """Testa as assinaturas com BM"""
    
    print("🧪 Testando assinaturas com 'BM' após o posto...")
    
    # Buscar militar José ERISMAN
    try:
        militar = Militar.objects.get(nome_completo__icontains="ERISMAN")
        print(f"  ✅ Militar encontrado: {militar.nome_completo}")
        print(f"  📋 Posto: {militar.get_posto_graduacao_display()}")
        
        # Verificar se tem usuário associado
        if hasattr(militar, 'user') and militar.user:
            print(f"  👤 Usuário associado: {militar.user.username}")
            
            # Simular nome com BM
            posto = militar.get_posto_graduacao_display()
            if "BM" not in posto:
                posto = f"{posto} BM"
            nome_completo_bm = f"{posto} {militar.nome_completo}"
            print(f"  📝 Nome completo com BM: {nome_completo_bm}")
            
            # Verificar assinaturas existentes
            assinaturas = AssinaturaQuadroAcesso.objects.filter(assinado_por=militar.user)
            print(f"  📋 Assinaturas encontradas: {assinaturas.count()}")
            
            for assinatura in assinaturas:
                print(f"    - Data: {assinatura.data_assinatura}")
                print(f"    - Tipo: {assinatura.get_tipo_assinatura_display()}")
                print(f"    - Função: {assinatura.funcao_assinatura}")
                
        else:
            print("  ⚠️  Sem usuário associado")
            
    except Militar.DoesNotExist:
        print("  ❌ Militar José ERISMAN não encontrado")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

def testar_template_tag():
    """Testa o template tag nome_completo_militar"""
    
    print("\n🔧 Testando template tag nome_completo_militar...")
    
    try:
        from militares.templatetags.militares_extras import nome_completo_militar
        
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

def verificar_quadros_acesso():
    """Verifica quadros de acesso com assinaturas"""
    
    print("\n📋 Verificando quadros de acesso...")
    
    quadros = QuadroAcesso.objects.all()
    print(f"  📊 Total de quadros: {quadros.count()}")
    
    for quadro in quadros:
        assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False)
        if assinaturas.exists():
            print(f"  📄 Quadro {quadro.pk}: {assinaturas.count()} assinatura(s)")
            for assinatura in assinaturas:
                if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                    militar = assinatura.assinado_por.militar
                    posto = militar.get_posto_graduacao_display()
                    if "BM" not in posto:
                        posto = f"{posto} BM"
                    nome_completo = f"{posto} {militar.nome_completo}"
                    print(f"    - {nome_completo} ({assinatura.funcao_assinatura})")

if __name__ == "__main__":
    print("🚀 Iniciando testes das assinaturas com 'BM'...")
    
    # Testar assinatura BM
    testar_assinatura_bm()
    
    # Testar template tag
    testar_template_tag()
    
    # Verificar quadros de acesso
    verificar_quadros_acesso()
    
    print("\n✅ Testes concluídos!") 