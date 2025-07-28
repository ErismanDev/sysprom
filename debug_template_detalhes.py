#!/usr/bin/env python
"""
Script para debugar o template de detalhes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao
from django.template.loader import render_to_string
from django.test import RequestFactory

def debug_template_detalhes():
    """Debuga o template de detalhes"""
    
    print("🔍 DEBUGANDO TEMPLATE DE DETALHES")
    print("=" * 60)
    
    # Buscar o cargo de teste
    cargo = CargoFuncao.objects.filter(nome__icontains='teste').first()
    if not cargo:
        print("❌ Cargo de teste não encontrado")
        return
    
    print(f"✅ Cargo encontrado: {cargo.nome} (ID: {cargo.id})")
    
    # Buscar permissões do cargo
    permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo, ativo=True).order_by('modulo', 'acesso')
    
    # Agrupar permissões por módulo
    permissoes_por_modulo = {}
    for permissao in permissoes:
        if permissao.modulo not in permissoes_por_modulo:
            permissoes_por_modulo[permissao.modulo] = []
        permissoes_por_modulo[permissao.modulo].append(permissao)
    
    print(f"📊 Total de permissões: {permissoes.count()}")
    print(f"📊 Módulos com permissões: {len(permissoes_por_modulo)}")
    
    # Listar módulos com permissões
    print("\n📋 Módulos com permissões:")
    for modulo in sorted(permissoes_por_modulo.keys()):
        perms = permissoes_por_modulo[modulo]
        print(f"   - {modulo}: {len(perms)} permissões")
        for perm in perms:
            print(f"     * {perm.acesso}")
    
    # Verificar se há módulos novos
    novos_modulos = [
        'ALMANAQUES', 'CALENDARIOS', 'NOTIFICACOES', 'MODELOS_ATA',
        'CARGOS_COMISSAO', 'QUADROS_FIXACAO', 'ASSINATURAS', 'ESTATISTICAS',
        'EXPORTACAO', 'IMPORTACAO', 'BACKUP', 'AUDITORIA', 'DASHBOARD',
        'BUSCA', 'AJAX', 'API', 'SESSAO', 'FUNCAO', 'PERFIL', 'SISTEMA'
    ]
    
    print("\n🔍 Verificando módulos novos:")
    for modulo in novos_modulos:
        if modulo in permissoes_por_modulo:
            print(f"   ✅ {modulo}: {len(permissoes_por_modulo[modulo])} permissões")
        else:
            print(f"   ❌ {modulo}: Nenhuma permissão")
    
    # Tentar renderizar o template
    print("\n🎨 Testando renderização do template...")
    try:
        context = {
            'cargo': cargo,
            'permissoes_por_modulo': permissoes_por_modulo,
            'permissoes_count': permissoes.count(),
            'usuarios_count': 0,
            'title': f'Detalhes do Cargo/Função: {cargo.nome}',
        }
        
        # Renderizar o template
        html = render_to_string('militares/cargos/cargo_funcao_detail.html', context)
        
        # Verificar se os módulos novos estão no HTML renderizado
        print("\n🔍 Verificando HTML renderizado:")
        for modulo in novos_modulos:
            if f"modulo == '{modulo}'" in html:
                print(f"   ✅ {modulo}: Encontrado no HTML")
            else:
                print(f"   ❌ {modulo}: NÃO encontrado no HTML")
        
        print(f"\n📄 Tamanho do HTML renderizado: {len(html)} caracteres")
        
    except Exception as e:
        print(f"❌ Erro ao renderizar template: {e}")
    
    print("\n🎯 Para ver os detalhes, acesse:")
    print(f"   http://127.0.0.1:8000/militares/cargos/{cargo.id}/")

if __name__ == "__main__":
    debug_template_detalhes() 