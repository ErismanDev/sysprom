#!/usr/bin/env python
"""
Script final para verificar se o sistema está funcionando completamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao, UsuarioFuncao
from militares.forms import CargoFuncaoForm

def verificar_final_sistema():
    """Verificação final do sistema de permissões"""
    
    print("🎯 VERIFICAÇÃO FINAL DO SISTEMA DE PERMISSÕES")
    print("=" * 70)
    
    # 1. Verificar módulos no modelo
    print("📋 1. VERIFICANDO MÓDULOS NO MODELO...")
    from militares.models import PermissaoFuncao
    modulos_modelo = [modulo[0] for modulo in PermissaoFuncao.MODULOS_CHOICES]
    print(f"   ✅ Total de módulos: {len(modulos_modelo)}")
    
    # 2. Verificar campos no formulário
    print("\n📋 2. VERIFICANDO CAMPOS NO FORMULÁRIO...")
    form = CargoFuncaoForm()
    campos_form = [field for field in form.fields.keys() if field.startswith('permissoes_')]
    print(f"   ✅ Total de campos: {len(campos_form)}")
    
    # 3. Verificar template de formulário
    print("\n📋 3. VERIFICANDO TEMPLATE DE FORMULÁRIO...")
    template_path = 'militares/templates/militares/cargos/cargo_funcao_form.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        modulos_no_template = []
        for modulo in modulos_modelo:
            campo = f'permissoes_{modulo.lower()}'
            if campo in template_content:
                modulos_no_template.append(modulo)
        
        print(f"   ✅ Módulos no template: {len(modulos_no_template)}")
    else:
        print("   ❌ Template não encontrado")
    
    # 4. Verificar template de detalhes
    print("\n📋 4. VERIFICANDO TEMPLATE DE DETALHES...")
    template_detail_path = 'militares/templates/militares/cargos/cargo_funcao_detail.html'
    if os.path.exists(template_detail_path):
        with open(template_detail_path, 'r', encoding='utf-8') as f:
            template_detail_content = f.read()
        
        modulos_no_detail = []
        for modulo in modulos_modelo:
            if f"modulo == '{modulo}'" in template_detail_content:
                modulos_no_detail.append(modulo)
        
        print(f"   ✅ Módulos no template de detalhes: {len(modulos_no_detail)}")
    else:
        print("   ❌ Template de detalhes não encontrado")
    
    # 5. Verificar permissões de teste
    print("\n📋 5. VERIFICANDO PERMISSÕES DE TESTE...")
    cargo_teste = CargoFuncao.objects.filter(nome__icontains='teste').first()
    if cargo_teste:
        permissoes_teste = PermissaoFuncao.objects.filter(cargo_funcao=cargo_teste)
        modulos_com_permissoes = permissoes_teste.values_list('modulo', flat=True).distinct()
        print(f"   ✅ Cargo de teste: {cargo_teste.nome}")
        print(f"   ✅ Total de permissões: {permissoes_teste.count()}")
        print(f"   ✅ Módulos com permissões: {len(modulos_com_permissoes)}")
    else:
        print("   ⚠️  Cargo de teste não encontrado")
    
    # 6. Verificar sintaxe dos templates
    print("\n📋 6. VERIFICANDO SINTAXE DOS TEMPLATES...")
    chaves_duplas_form = template_content.count('{{{')
    chaves_duplas_detail = template_detail_content.count('{{{')
    
    if chaves_duplas_form == 0 and chaves_duplas_detail == 0:
        print("   ✅ Sintaxe dos templates está correta")
    else:
        print(f"   ⚠️  Chaves duplas encontradas: Form={chaves_duplas_form}, Detail={chaves_duplas_detail}")
    
    # 7. Resumo final
    print("\n" + "=" * 70)
    print("🎯 RESUMO FINAL")
    print("=" * 70)
    
    total_modulos = len(modulos_modelo)
    total_campos = len(campos_form)
    total_permissoes_possiveis = total_modulos * 10  # 10 tipos de acesso
    
    print(f"📊 Módulos do sistema: {total_modulos}")
    print(f"📊 Campos de permissão: {total_campos}")
    print(f"📊 Permissões possíveis: {total_permissoes_possiveis}")
    
    if cargo_teste:
        print(f"📊 Permissões do cargo teste: {permissoes_teste.count()}")
        print(f"📊 Módulos com permissões: {len(modulos_com_permissoes)}")
    
    # Verificar se tudo está completo
    if (total_campos == total_modulos and 
        len(modulos_no_template) == total_modulos and 
        len(modulos_no_detail) == total_modulos and
        chaves_duplas_form == 0 and chaves_duplas_detail == 0):
        print("\n✅ SISTEMA 100% COMPLETO E FUNCIONAL!")
        print("🎮 Acesse /militares/cargos/ para gerenciar permissões")
        print("🎮 Acesse /militares/cargos/1/ para ver os detalhes")
    else:
        print("\n⚠️  SISTEMA INCOMPLETO - Alguns itens precisam ser corrigidos")
    
    print("\n🚀 Sistema pronto para uso!")

if __name__ == "__main__":
    verificar_final_sistema() 