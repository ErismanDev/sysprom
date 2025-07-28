#!/usr/bin/env python
"""
Script para forçar atualização do template e limpar cache
"""

import os
import sys
import django
import shutil

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.core.cache import cache

def forcar_atualizacao_template():
    """Força a atualização do template e limpa cache"""
    
    print("🔄 FORÇANDO ATUALIZAÇÃO DO TEMPLATE")
    print("=" * 60)
    
    # Limpar cache do Django
    print("🧹 Limpando cache do Django...")
    cache.clear()
    print("✅ Cache limpo!")
    
    # Limpar cache de templates
    print("🧹 Limpando cache de templates...")
    try:
        from django.template.loaders.app_directories import get_app_template_dirs
        template_dirs = get_app_template_dirs('templates')
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                print(f"📁 Template dir: {template_dir}")
    except Exception as e:
        print(f"⚠️ Erro ao listar template dirs: {e}")
    
    # Tentar recarregar o template
    print("🔄 Recarregando template...")
    try:
        template = get_template('militares/cargos/cargo_funcao_detail.html')
        print("✅ Template recarregado com sucesso!")
        
        # Verificar se o template tem os módulos novos
        template_content = template.template.source
        
        novos_modulos = [
            'ALMANAQUES', 'CALENDARIOS', 'NOTIFICACOES', 'MODELOS_ATA',
            'CARGOS_COMISSAO', 'QUADROS_FIXACAO', 'ASSINATURAS', 'ESTATISTICAS',
            'EXPORTACAO', 'IMPORTACAO', 'BACKUP', 'AUDITORIA', 'DASHBOARD',
            'BUSCA', 'AJAX', 'API', 'SESSAO', 'FUNCAO', 'PERFIL', 'SISTEMA'
        ]
        
        print("\n🔍 Verificando módulos no template:")
        for modulo in novos_modulos:
            if f"modulo == '{modulo}'" in template_content:
                print(f"   ✅ {modulo}: Encontrado no template")
            else:
                print(f"   ❌ {modulo}: NÃO encontrado no template")
        
        print(f"\n📄 Tamanho do template: {len(template_content)} caracteres")
        
    except TemplateDoesNotExist:
        print("❌ Template não encontrado!")
    except Exception as e:
        print(f"❌ Erro ao recarregar template: {e}")
    
    # Forçar reinicialização do Django
    print("\n🔄 Forçando reinicialização do Django...")
    try:
        from django.conf import settings
        from django.template.loaders.app_directories import Loader
        loader = Loader(settings.ENGINE)
        print("✅ Loader reinicializado!")
    except Exception as e:
        print(f"⚠️ Erro ao reinicializar loader: {e}")
    
    print("\n🎯 Agora teste acessando:")
    print("   http://127.0.0.1:8000/militares/cargos/1/")

if __name__ == "__main__":
    forcar_atualizacao_template() 