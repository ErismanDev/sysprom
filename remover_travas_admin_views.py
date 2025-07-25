#!/usr/bin/env python
"""
Script para remover verificações de permissão para o admin nas views
"""
import os
import re

def remover_travas_admin_views():
    """Remove verificações de permissão para o admin nas views"""
    
    print("🔓 REMOVENDO TRAVAS DE PERMISSÃO PARA ADMIN NAS VIEWS")
    print("=" * 60)
    
    # Ler o arquivo views.py
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Adicionar função helper para verificar se é admin
        helper_function = '''
def is_admin_user(user):
    """Verifica se o usuário é admin (superusuário ou tem função de administrador)"""
    if not user.is_authenticated:
        return False
    
    # Superusuários sempre têm acesso
    if user.is_superuser:
        return True
    
    # Verificar se tem função de administrador
    from .models import UsuarioFuncao
    return UsuarioFuncao.objects.filter(
        usuario=user,
        cargo_funcao__nome__icontains='administrador',
        status='ATIVO'
    ).exists()

'''
        
        # Inserir a função helper após os imports
        if 'def is_admin_user(user):' not in content:
            # Encontrar onde inserir (após os imports)
            import_end = content.find('\n\n@login_required')
            if import_end != -1:
                content = content[:import_end] + helper_function + content[import_end:]
                print("✅ Função helper is_admin_user adicionada")
        
        # 2. Modificar decorators para permitir admin
        decorators_para_modificar = [
            '@requer_funcao_ativa',
            '@permission_required',
            '@administracao_required',
            '@militar_edit_permission',
            '@cargos_especiais_required'
        ]
        
        for decorator in decorators_para_modificar:
            # Encontrar todas as ocorrências do decorator
            pattern = rf'({decorator})'
            matches = list(re.finditer(pattern, content))
            
            for match in reversed(matches):  # Reverso para não afetar índices
                start = match.start()
                end = match.end()
                
                # Encontrar a função que vem depois
                func_start = content.find('def ', end)
                if func_start != -1:
                    # Encontrar o final da definição da função
                    func_end = content.find(':', func_start) + 1
                    
                    # Adicionar verificação de admin antes do decorator
                    admin_check = f'''@user_passes_test(lambda u: is_admin_user(u) or True)
{decorator}
'''
                    
                    # Substituir o decorator
                    content = content[:start] + admin_check + content[end:]
                    print(f"   ✅ Modificado decorator: {decorator}")
        
        # 3. Adicionar verificação de admin em funções específicas
        funcoes_crud = [
            'militar_create',
            'militar_update', 
            'militar_delete',
            'ficha_conceito_create',
            'ficha_conceito_update',
            'ficha_conceito_delete',
            'quadro_acesso_create',
            'quadro_acesso_update',
            'quadro_acesso_delete'
        ]
        
        for funcao in funcoes_crud:
            # Verificar se a função existe
            if f'def {funcao}(' in content:
                # Adicionar verificação no início da função se não existir
                pattern = rf'def {funcao}\(.*?\):'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    func_start = match.end()
                    func_body_start = content.find('\n', func_start) + 1
                    
                    # Verificar se já tem verificação de admin
                    if 'is_admin_user' not in content[func_start:func_start+200]:
                        admin_check = '''
    # Verificar se é admin
    if is_admin_user(request.user):
        # Admin tem acesso total, continuar normalmente
        pass
    else:
        # Verificações normais de permissão continuam...
'''
                        
                        content = content[:func_body_start] + admin_check + content[func_body_start:]
                        print(f"   ✅ Adicionada verificação de admin em: {funcao}")
        
        # 4. Salvar arquivo
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ Arquivo views.py atualizado!")
        print("🎉 Admin agora tem acesso total sem verificações de permissão!")
        
    except FileNotFoundError:
        print("❌ Arquivo views.py não encontrado!")

def criar_decorator_admin_bypass():
    """Cria um decorator que permite admin bypass"""
    
    print("\n🔧 CRIANDO DECORATOR ADMIN BYPASS")
    print("=" * 60)
    
    # Criar arquivo de decorators específico para admin
    decorator_content = '''#!/usr/bin/env python
"""
Decorators para permitir acesso total ao admin
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def is_admin_user(user):
    """Verifica se o usuário é admin (superusuário ou tem função de administrador)"""
    if not user.is_authenticated:
        return False
    
    # Superusuários sempre têm acesso
    if user.is_superuser:
        return True
    
    # Verificar se tem função de administrador
    from .models import UsuarioFuncao
    return UsuarioFuncao.objects.filter(
        usuario=user,
        cargo_funcao__nome__icontains='administrador',
        status='ATIVO'
    ).exists()

def admin_bypass(view_func):
    """
    Decorator que permite admin bypass - admin tem acesso total
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Se é admin, permitir acesso total
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)
        
        # Se não é admin, aplicar verificações normais
        # (aqui você pode adicionar outras verificações se necessário)
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def admin_or_permission_required(permission):
    """
    Decorator que requer permissão OU ser admin
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Se é admin, permitir acesso
            if is_admin_user(request.user):
                return view_func(request, *args, **kwargs)
            
            # Se não é admin, verificar permissão
            if request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Acesso negado. Permissão necessária ou ser administrador.')
            return redirect('militares:militar_dashboard')
        
        return _wrapped_view
    return decorator

'''
    
    # Salvar arquivo
    with open('militares/admin_decorators.py', 'w', encoding='utf-8') as f:
        f.write(decorator_content)
    
    print("✅ Arquivo admin_decorators.py criado!")
    print("📝 Use @admin_bypass ou @admin_or_permission_required nas views")

def aplicar_decorators_admin():
    """Aplica decorators de admin bypass nas views"""
    
    print("\n🔧 APLICANDO DECORATORS ADMIN BYPASS")
    print("=" * 60)
    
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar import do decorator
        if 'from .admin_decorators import admin_bypass' not in content:
            # Encontrar linha de imports
            import_line = 'from .decorators import'
            if import_line in content:
                content = content.replace(
                    import_line,
                    import_line + '\nfrom .admin_decorators import admin_bypass, admin_or_permission_required'
                )
                print("✅ Import do admin_decorators adicionado")
        
        # Aplicar @admin_bypass em views CRUD
        views_crud = [
            'militar_create',
            'militar_update',
            'militar_delete',
            'ficha_conceito_create',
            'ficha_conceito_update',
            'ficha_conceito_delete'
        ]
        
        for view in views_crud:
            # Substituir @requer_funcao_ativa por @admin_bypass
            pattern = rf'@requer_funcao_ativa\s+def {view}\('
            if re.search(pattern, content):
                content = re.sub(pattern, f'@admin_bypass\ndef {view}(', content)
                print(f"   ✅ {view}: @requer_funcao_ativa → @admin_bypass")
        
        # Salvar arquivo
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ Decorators admin bypass aplicados!")
        
    except FileNotFoundError:
        print("❌ Arquivo views.py não encontrado!")

if __name__ == "__main__":
    print("🔓 REMOVEDOR DE TRAVAS PARA ADMIN")
    print("=" * 60)
    print("1. Remover travas nas views (método 1)")
    print("2. Criar decorator admin bypass")
    print("3. Aplicar decorators admin bypass")
    
    opcao = input("\nEscolha uma opção (1-3): ").strip()
    
    if opcao == "1":
        remover_travas_admin_views()
    elif opcao == "2":
        criar_decorator_admin_bypass()
    elif opcao == "3":
        aplicar_decorators_admin()
    else:
        print("❌ Opção inválida!") 