#!/usr/bin/env python
"""
Script para testar o template diretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, QuadroAcesso
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template import Context, Template

def testar_template_diretamente():
    """Testa o template diretamente"""
    
    print("🧪 Testando template diretamente...")
    
    try:
        # Buscar quadro com assinaturas
        quadro = QuadroAcesso.objects.first()
        if not quadro:
            print("  ❌ Nenhum quadro encontrado")
            return
            
        assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False)
        if not assinaturas.exists():
            print("  ❌ Nenhuma assinatura encontrada")
            return
            
        print(f"  📄 Quadro: {quadro.pk}")
        print(f"  📝 Assinaturas: {assinaturas.count()}")
        
        # Testar template tag diretamente
        from militares.templatetags.militares_extras import nome_completo_militar
        
        for assinatura in assinaturas:
            print(f"\n  📄 Assinatura {assinatura.pk}:")
            
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                nome_formatado = nome_completo_militar(militar)
                print(f"    - Militar: {militar.nome_completo}")
                print(f"    - Posto: {militar.get_posto_graduacao_display()}")
                print(f"    - Nome formatado: {nome_formatado}")
                
                # Testar template simples
                template_text = """
                {% load militares_extras %}
                Nome: {{ militar|nome_completo_militar }}
                """
                
                template = Template(template_text)
                context = Context({'militar': militar})
                resultado = template.render(context)
                
                print(f"    - Resultado do template: {resultado.strip()}")
            else:
                print(f"    - Usuário: {assinatura.assinado_por.username}")
                print(f"    - Nome: {assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username}")
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")

def testar_template_completo():
    """Testa o template completo"""
    
    print("\n🔧 Testando template completo...")
    
    try:
        # Buscar quadro com assinaturas
        quadro = QuadroAcesso.objects.first()
        if not quadro:
            print("  ❌ Nenhum quadro encontrado")
            return
            
        assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False)
        
        # Preparar contexto
        context = {
            'quadro': quadro,
            'assinaturas': assinaturas,
            'texto_intro': 'Texto de introdução do quadro de acesso.'
        }
        
        # Renderizar template
        template_path = 'militares/quadro_acesso_visualizar.html'
        resultado = render_to_string(template_path, context)
        
        # Verificar se o resultado contém "BM"
        if "BM" in resultado:
            print("  ✅ Template renderizado com 'BM' encontrado")
            
            # Encontrar a linha com a assinatura
            linhas = resultado.split('\n')
            for i, linha in enumerate(linhas):
                if "Documento assinado eletronicamente por" in linha and "BM" in linha:
                    print(f"    - Linha {i+1}: {linha.strip()}")
        else:
            print("  ❌ Template renderizado sem 'BM' encontrado")
            
    except Exception as e:
        print(f"  ❌ Erro ao testar template completo: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes de template...")
    
    # Testar template tag diretamente
    testar_template_diretamente()
    
    # Testar template completo
    testar_template_completo()
    
    print("\n✅ Testes concluídos!") 