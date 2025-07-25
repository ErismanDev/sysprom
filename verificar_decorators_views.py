#!/usr/bin/env python
"""
Script para verificar se as views estão usando os decorators de permissão
"""

import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def verificar_decorators_views():
    """Verifica se as views estão usando os decorators corretos"""
    
    print("🔍 VERIFICANDO DECORATORS NAS VIEWS")
    print("=" * 60)
    
    # Ler o arquivo views.py
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar decorators específicos
        decorators = [
            '@requer_edicao_militares',
            '@requer_edicao_fichas_conceito',
            '@requer_gerenciamento_quadros_vagas',
            '@requer_gerenciamento_comissoes',
            '@requer_gerenciamento_usuarios',
            '@requer_assinatura_documentos',
            '@requer_funcao_especial',
            '@apenas_visualizacao_comissao',
            '@login_required',
            '@permission_required',
        ]
        
        print("📋 DECORATORS ENCONTRADOS:")
        for decorator in decorators:
            count = content.count(decorator)
            print(f"  {decorator}: {count} ocorrências")
        
        # Verificar views específicas que podem estar causando problemas
        views_problematicas = [
            'militar_create',
            'militar_update', 
            'militar_delete',
            'ficha_conceito_create',
            'ficha_conceito_update',
            'ficha_conceito_delete',
            'quadro_acesso_create',
            'quadro_acesso_update',
            'quadro_acesso_delete',
            'comissao_create',
            'comissao_update',
            'comissao_delete',
        ]
        
        print(f"\n📋 VIEWS PROBLEMÁTICAS:")
        for view in views_problematicas:
            if view in content:
                # Encontrar a linha da view
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if f'def {view}(' in line:
                        # Verificar decorators na linha anterior
                        decorators_encontrados = []
                        for j in range(max(0, i-5), i):
                            for decorator in decorators:
                                if decorator in lines[j]:
                                    decorators_encontrados.append(decorator)
                        
                        if decorators_encontrados:
                            print(f"  ✅ {view}: {', '.join(decorators_encontrados)}")
                        else:
                            print(f"  ❌ {view}: SEM decorator")
                        break
            else:
                print(f"  ⚠️ {view}: Não encontrada")
        
        # Verificar imports de decorators
        print(f"\n📋 IMPORTS DE DECORATORS:")
        imports_decorators = [
            'from militares.permissoes_simples import',
            'from militares.decorators import',
            'from militares.permissoes import',
        ]
        
        for import_line in imports_decorators:
            if import_line in content:
                print(f"  ✅ {import_line}")
            else:
                print(f"  ❌ {import_line}: Não encontrado")
        
    except FileNotFoundError:
        print("❌ Arquivo views.py não encontrado!")

def corrigir_decorators_views():
    """Corrige decorators nas views problemáticas"""
    
    print(f"\n🔧 CORRIGINDO DECORATORS NAS VIEWS")
    print("=" * 60)
    
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem o import correto
        if 'from militares.permissoes_simples import' not in content:
            # Adicionar import no início do arquivo
            import_line = 'from militares.permissoes_simples import (\n    requer_edicao_militares, requer_edicao_fichas_conceito,\n    requer_gerenciamento_quadros_vagas, requer_gerenciamento_comissoes,\n    requer_gerenciamento_usuarios, requer_assinatura_documentos,\n    requer_funcao_especial, apenas_visualizacao_comissao\n)\n\n'
            
            # Encontrar onde adicionar o import
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from django') or line.startswith('import django'):
                    lines.insert(i, import_line)
                    break
            
            content = '\n'.join(lines)
            print("✅ Import de decorators adicionado")
        
        # Views que precisam do decorator @requer_edicao_militares
        views_militares = [
            'militar_create',
            'militar_update',
            'militar_delete',
        ]
        
        # Views que precisam do decorator @requer_edicao_fichas_conceito
        views_fichas = [
            'ficha_conceito_create',
            'ficha_conceito_update',
            'ficha_conceito_delete',
        ]
        
        # Views que precisam do decorator @requer_gerenciamento_quadros_vagas
        views_quadros = [
            'quadro_acesso_create',
            'quadro_acesso_update',
            'quadro_acesso_delete',
        ]
        
        # Views que precisam do decorator @requer_gerenciamento_comissoes
        views_comissoes = [
            'comissao_create',
            'comissao_update',
            'comissao_delete',
        ]
        
        import re
        
        # Aplicar decorators para views de militares
        for view in views_militares:
            pattern = r'@login_required\s+def ' + view + r'\('
            if re.search(pattern, content) and f'@requer_edicao_militares' not in content:
                replacement = r'@login_required\n@requer_edicao_militares\ndef ' + view + r'('
                content = re.sub(pattern, replacement, content)
                print(f"   ✅ {view}: Decorator @requer_edicao_militares adicionado")
        
        # Aplicar decorators para views de fichas
        for view in views_fichas:
            pattern = r'@login_required\s+def ' + view + r'\('
            if re.search(pattern, content) and f'@requer_edicao_fichas_conceito' not in content:
                replacement = r'@login_required\n@requer_edicao_fichas_conceito\ndef ' + view + r'('
                content = re.sub(pattern, replacement, content)
                print(f"   ✅ {view}: Decorator @requer_edicao_fichas_conceito adicionado")
        
        # Aplicar decorators para views de quadros
        for view in views_quadros:
            pattern = r'@login_required\s+def ' + view + r'\('
            if re.search(pattern, content) and f'@requer_gerenciamento_quadros_vagas' not in content:
                replacement = r'@login_required\n@requer_gerenciamento_quadros_vagas\ndef ' + view + r'('
                content = re.sub(pattern, replacement, content)
                print(f"   ✅ {view}: Decorator @requer_gerenciamento_quadros_vagas adicionado")
        
        # Aplicar decorators para views de comissões
        for view in views_comissoes:
            pattern = r'@login_required\s+def ' + view + r'\('
            if re.search(pattern, content) and f'@requer_gerenciamento_comissoes' not in content:
                replacement = r'@login_required\n@requer_gerenciamento_comissoes\ndef ' + view + r'('
                content = re.sub(pattern, replacement, content)
                print(f"   ✅ {view}: Decorator @requer_gerenciamento_comissoes adicionado")
        
        # Salvar arquivo
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arquivo views.py atualizado!")
        
    except FileNotFoundError:
        print("❌ Arquivo views.py não encontrado!")

if __name__ == '__main__':
    print("Escolha uma opção:")
    print("1. Verificar decorators nas views")
    print("2. Corrigir decorators nas views")
    
    opcao = input("Opção (1-2): ").strip()
    
    if opcao == "1":
        verificar_decorators_views()
    elif opcao == "2":
        corrigir_decorators_views()
    else:
        print("❌ Opção inválida!") 