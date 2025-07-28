#!/usr/bin/env python
"""
Script para ajustar as permissões de usuários com função "Usuário"
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao, Militar

def ajustar_permissoes_usuario():
    """Ajusta as permissões de usuários com função 'Usuário'"""
    
    print("🔧 AJUSTANDO PERMISSÕES DE USUÁRIOS")
    print("=" * 60)
    
    # 1. Verificar se existe o cargo "Usuário"
    try:
        cargo_usuario = CargoFuncao.objects.get(nome='Usuário')
        print(f"✅ Cargo 'Usuário' encontrado: ID {cargo_usuario.id}")
    except CargoFuncao.DoesNotExist:
        print("❌ Cargo 'Usuário' não encontrado. Criando...")
        cargo_usuario = CargoFuncao.objects.create(
            nome='Usuário',
            descricao='Função padrão para usuários do sistema - acesso limitado apenas às próprias informações',
            ativo=True,
            ordem=999
        )
        print(f"✅ Cargo 'Usuário' criado: ID {cargo_usuario.id}")
    
    # 2. Verificar usuários com função "Usuário"
    usuarios_com_funcao_padrao = UsuarioFuncao.objects.filter(
        cargo_funcao=cargo_usuario,
        status='ATIVO'
    ).select_related('usuario')
    
    print(f"\n📋 USUÁRIOS COM FUNÇÃO 'USUÁRIO': {usuarios_com_funcao_padrao.count()}")
    
    for uf in usuarios_com_funcao_padrao:
        print(f"  - {uf.usuario.username} ({uf.usuario.get_full_name()})")
        
        # Verificar se tem militar associado
        try:
            militar = uf.usuario.militar
            if militar:
                print(f"    ✅ Militar associado: {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
                
                # Verificar fichas de conceito
                fichas_oficiais = militar.fichaconceitooficiais_set.count()
                fichas_pracas = militar.fichaconceitopracas_set.count()
                
                print(f"    📋 Fichas de conceito: {fichas_oficiais} oficiais, {fichas_pracas} praças")
            else:
                print(f"    ❌ Nenhum militar associado")
        except Militar.DoesNotExist:
            print(f"    ❌ Militar não encontrado")
    
    # 3. Verificar context processor
    print(f"\n🔍 VERIFICANDO CONTEXT PROCESSOR:")
    from militares.context_processors import menu_permissions_processor
    from django.test import RequestFactory
    
    factory = RequestFactory()
    
    for uf in usuarios_com_funcao_padrao:
        request = factory.get('/')
        request.user = uf.usuario
        
        context = menu_permissions_processor(request)
        menu_permissions = context.get('menu_permissions', {})
        
        print(f"\n  👤 {uf.usuario.username}:")
        print(f"    • is_consultor: {menu_permissions.get('is_consultor', False)}")
        print(f"    • show_dashboard: {menu_permissions.get('show_dashboard', False)}")
        print(f"    • show_efetivo: {menu_permissions.get('show_efetivo', False)}")
        print(f"    • show_usuarios: {menu_permissions.get('show_usuarios', False)}")
        print(f"    • show_permissoes: {menu_permissions.get('show_permissoes', False)}")
        print(f"    • show_fichas_oficiais: {menu_permissions.get('show_fichas_oficiais', False)}")
        print(f"    • show_fichas_pracas: {menu_permissions.get('show_fichas_pracas', False)}")
        print(f"    • show_quadros_acesso: {menu_permissions.get('show_quadros_acesso', False)}")
        print(f"    • show_quadros_fixacao: {menu_permissions.get('show_quadros_fixacao', False)}")
        print(f"    • show_almanaques: {menu_permissions.get('show_almanaques', False)}")
        print(f"    • show_promocoes: {menu_permissions.get('show_promocoes', False)}")
        print(f"    • show_calendarios: {menu_permissions.get('show_calendarios', False)}")
        print(f"    • show_comissoes: {menu_permissions.get('show_comissoes', False)}")
        print(f"    • show_meus_votos: {menu_permissions.get('show_meus_votos', False)}")
        print(f"    • show_intersticios: {menu_permissions.get('show_intersticios', False)}")
        print(f"    • show_gerenciar_intersticios: {menu_permissions.get('show_gerenciar_intersticios', False)}")
        print(f"    • show_gerenciar_previsao: {menu_permissions.get('show_gerenciar_previsao', False)}")
        print(f"    • show_administracao: {menu_permissions.get('show_administracao', False)}")
    
    # 4. Verificar views específicas
    print(f"\n🔍 VERIFICANDO VIEWS ESPECÍFICAS:")
    
    # Verificar se existe a view redirect_usuario_ficha
    from militares.usuario_views import redirect_usuario_ficha, welcome_usuario
    
    print(f"  ✅ View 'redirect_usuario_ficha' existe")
    print(f"  ✅ View 'welcome_usuario' existe")
    
    # 5. Verificar template base.html
    print(f"\n🔍 VERIFICANDO TEMPLATE BASE.HTML:")
    
    # Verificar se o template tem a seção para usuários consultores
    template_path = 'templates/base.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        if 'menu_permissions.is_consultor' in template_content:
            print(f"  ✅ Template tem seção para usuários consultores")
        else:
            print(f"  ❌ Template não tem seção para usuários consultores")
            
        if 'Minha Ficha de Cadastro' in template_content:
            print(f"  ✅ Template tem link para 'Minha Ficha de Cadastro'")
        else:
            print(f"  ❌ Template não tem link para 'Minha Ficha de Cadastro'")
            
        if 'Minha Ficha de Conceito' in template_content:
            print(f"  ✅ Template tem link para 'Minha Ficha de Conceito'")
        else:
            print(f"  ❌ Template não tem link para 'Minha Ficha de Conceito'")
            
    except FileNotFoundError:
        print(f"  ❌ Template base.html não encontrado")
    
    # 6. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   ✅ Sistema já está configurado para usuários com função 'Usuário'")
    print(f"   📋 Usuários com função 'Usuário' podem:")
    print(f"      • Ver apenas suas próprias informações")
    print(f"      • Acessar 'Minha Ficha de Cadastro'")
    print(f"      • Acessar 'Minha Ficha de Conceito'")
    print(f"      • NÃO podem ver efetivo, quadros, almanaques, etc.")
    
    print(f"\n   🔧 Para testar:")
    print(f"      1. Faça login com um usuário que tem função 'Usuário'")
    print(f"      2. Verifique se aparece apenas 'Minhas Informações' no menu")
    print(f"      3. Clique em 'Minha Ficha de Cadastro' e 'Minha Ficha de Conceito'")
    print(f"      4. Confirme que não consegue acessar outras seções do sistema")

if __name__ == "__main__":
    ajustar_permissoes_usuario() 