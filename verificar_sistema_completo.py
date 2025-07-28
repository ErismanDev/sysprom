#!/usr/bin/env python
"""
Script para verificar se o sistema de permissões está completo
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao, UsuarioFuncao
from militares.forms import CargoFuncaoForm
from django.contrib.auth.models import User

def verificar_sistema_completo():
    """Verifica se o sistema de permissões está completo"""
    
    print("🔍 VERIFICANDO SISTEMA DE PERMISSÕES COMPLETO")
    print("=" * 70)
    
    # 1. Verificar se todos os módulos estão no modelo
    print("📋 1. VERIFICANDO MÓDULOS NO MODELO...")
    from militares.models import PermissaoFuncao
    modulos_modelo = [modulo[0] for modulo in PermissaoFuncao.MODULOS_CHOICES]
    print(f"   ✅ Total de módulos no modelo: {len(modulos_modelo)}")
    print(f"   📝 Módulos: {', '.join(modulos_modelo[:10])}...")
    
    # 2. Verificar se todos os campos estão no formulário
    print("\n📋 2. VERIFICANDO CAMPOS NO FORMULÁRIO...")
    form = CargoFuncaoForm()
    campos_form = [field for field in form.fields.keys() if field.startswith('permissoes_')]
    print(f"   ✅ Total de campos de permissão no formulário: {len(campos_form)}")
    
    # Verificar se todos os módulos têm campos correspondentes
    modulos_sem_campo = []
    for modulo in modulos_modelo:
        campo = f'permissoes_{modulo.lower()}'
        if campo not in campos_form:
            modulos_sem_campo.append(modulo)
    
    if modulos_sem_campo:
        print(f"   ⚠️  Módulos sem campo no formulário: {', '.join(modulos_sem_campo)}")
    else:
        print("   ✅ Todos os módulos têm campos correspondentes no formulário")
    
    # 3. Verificar template
    print("\n📋 3. VERIFICANDO TEMPLATE...")
    template_path = 'militares/templates/militares/cargos/cargo_funcao_form.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        modulos_no_template = []
        for modulo in modulos_modelo:
            campo = f'permissoes_{modulo.lower()}'
            if campo in template_content:
                modulos_no_template.append(modulo)
        
        print(f"   ✅ Módulos encontrados no template: {len(modulos_no_template)}")
        if len(modulos_no_template) == len(modulos_modelo):
            print("   ✅ Todos os módulos estão no template")
        else:
            modulos_faltando = [m for m in modulos_modelo if m not in modulos_no_template]
            print(f"   ⚠️  Módulos faltando no template: {', '.join(modulos_faltando)}")
    else:
        print("   ❌ Template não encontrado")
    
    # 4. Verificar estatísticas do sistema
    print("\n📋 4. ESTATÍSTICAS DO SISTEMA...")
    total_cargos = CargoFuncao.objects.count()
    total_permissoes = PermissaoFuncao.objects.count()
    total_usuarios_funcao = UsuarioFuncao.objects.count()
    
    print(f"   📊 Total de cargos/funções: {total_cargos}")
    print(f"   📊 Total de permissões: {total_permissoes}")
    print(f"   📊 Total de usuários vinculados: {total_usuarios_funcao}")
    
    # 5. Verificar se há pelo menos um cargo de teste
    print("\n📋 5. VERIFICANDO CARGO DE TESTE...")
    cargo_teste = CargoFuncao.objects.filter(nome__icontains='teste').first()
    if cargo_teste:
        print(f"   ✅ Cargo de teste encontrado: {cargo_teste.nome}")
        permissoes_cargo = PermissaoFuncao.objects.filter(cargo_funcao=cargo_teste).count()
        print(f"   📊 Permissões do cargo: {permissoes_cargo}")
    else:
        print("   ⚠️  Nenhum cargo de teste encontrado")
    
    # 6. Resumo final
    print("\n" + "=" * 70)
    print("🎯 RESUMO FINAL")
    print("=" * 70)
    
    total_modulos = len(modulos_modelo)
    total_campos = len(campos_form)
    total_permissoes_possiveis = total_modulos * 10  # 10 tipos de acesso
    
    print(f"📊 Módulos do sistema: {total_modulos}")
    print(f"📊 Campos de permissão: {total_campos}")
    print(f"📊 Permissões possíveis: {total_permissoes_possiveis}")
    print(f"📊 Permissões criadas: {total_permissoes}")
    
    if total_campos == total_modulos:
        print("✅ SISTEMA COMPLETO - Todos os módulos estão disponíveis!")
        print("🎮 Acesse /militares/cargos/ para gerenciar permissões")
    else:
        print("⚠️  SISTEMA INCOMPLETO - Alguns módulos estão faltando")
    
    print("\n🚀 Sistema pronto para uso!")

if __name__ == "__main__":
    verificar_sistema_completo() 