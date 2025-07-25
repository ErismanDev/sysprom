#!/usr/bin/env python
"""
Script para limpar cache e reiniciar o servidor
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.cache import cache
from django.template.loader import get_template
from django.template import Context

def limpar_cache():
    """Limpa o cache do Django"""
    
    print("🧹 Limpando cache do Django...")
    
    try:
        # Limpar cache
        cache.clear()
        print("  ✅ Cache limpo com sucesso!")
        
        # Limpar cache de templates
        from django.template.loader import get_template
        get_template.cache_clear()
        print("  ✅ Cache de templates limpo!")
        
    except Exception as e:
        print(f"  ❌ Erro ao limpar cache: {e}")

def testar_template_apos_limpeza():
    """Testa o template após limpeza do cache"""
    
    print("\n🧪 Testando template após limpeza...")
    
    try:
        from militares.models import Militar
        from militares.templatetags.militares_extras import nome_completo_militar
        
        # Buscar militar José ERISMAN
        militar = Militar.objects.get(nome_completo__icontains="ERISMAN")
        nome_formatado = nome_completo_militar(militar)
        
        print(f"  ✅ Nome formatado: {nome_formatado}")
        
        # Testar template simples
        template_text = """
        {% load militares_extras %}
        Nome: {{ militar|nome_completo_militar }}
        """
        
        from django.template import Template, Context
        template = Template(template_text)
        context = Context({'militar': militar})
        resultado = template.render(context)
        
        print(f"  ✅ Resultado do template: {resultado.strip()}")
        
    except Exception as e:
        print(f"  ❌ Erro ao testar template: {e}")

def verificar_arquivos_modificados():
    """Verifica se os arquivos foram modificados corretamente"""
    
    print("\n🔍 Verificando arquivos modificados...")
    
    arquivos_para_verificar = [
        "militares/templatetags/militares_extras.py",
        "militares/templates/militares/quadro_acesso_visualizar.html",
        "militares/templates/militares/quadro_acesso_detail.html",
        "militares/views.py"
    ]
    
    for arquivo in arquivos_para_verificar:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} - não encontrado")

if __name__ == "__main__":
    print("🚀 Iniciando limpeza de cache e reinicialização...")
    
    # Limpar cache
    limpar_cache()
    
    # Verificar arquivos
    verificar_arquivos_modificados()
    
    # Testar template após limpeza
    testar_template_apos_limpeza()
    
    print("\n✅ Processo concluído!")
    print("🔄 Reinicie o servidor Django para aplicar as mudanças:")
    print("   python manage.py runserver") 