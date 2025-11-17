from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .context_processors import menu_permissions_processor


@login_required
def configuracoes_cartucheira(request):
    """
    Página de configurações tipo cartucheira (grid de cards)
    """
    # Obter permissões do menu através do context processor
    menu_permissions_context = menu_permissions_processor(request)
    menu_permissions = menu_permissions_context.get('menu_permissions')
    
    # MenuPermissions tem método .get() que funciona como dicionário
    # Se não tiver menu_permissions, criar um vazio
    if not menu_permissions:
        from .context_processors import MenuPermissions
        menu_permissions = MenuPermissions({})
    
    # Lista de configurações disponíveis com suas permissões
    configuracoes = []
    
    # ===== PROMOÇÕES =====
    if menu_permissions.get('show_gerenciar_intersticios') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Gerenciar Interstícios',
            'descricao': 'Gerenciar interstícios do sistema',
            'icone': 'fa-hourglass-half',
            'url': 'militares:intersticio_manage',
            'cor': 'primary',
            'categoria': 'Promoções'
        })
    
    if menu_permissions.get('show_gerenciar_previsao') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Gerenciar Previsão de Vagas',
            'descricao': 'Gerenciar previsão de vagas',
            'icone': 'fa-calendar-alt',
            'url': 'militares:previsao_vaga_manage',
            'cor': 'primary',
            'categoria': 'Promoções'
        })
    
    # ===== ORGANIZACIONAL =====
    if menu_permissions.get('show_usuarios') or menu_permissions.get('show_administracao') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Órgãos',
            'descricao': 'Gerenciar órgãos do sistema',
            'icone': 'fa-building',
            'url': 'militares:orgao_list',
            'cor': 'success',
            'categoria': 'Organizacional'
        })
        configuracoes.append({
            'titulo': 'Organograma',
            'descricao': 'Visualizar organograma organizacional',
            'icone': 'fa-sitemap',
            'url': 'militares:organograma',
            'cor': 'success',
            'categoria': 'Organizacional'
        })
    
    if menu_permissions.get('show_grandes_comandos') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Grandes Comandos',
            'descricao': 'Gerenciar grandes comandos',
            'icone': 'fa-flag',
            'url': 'militares:grande_comando_list',
            'cor': 'success',
            'categoria': 'Organizacional'
        })
    
    if menu_permissions.get('show_unidades') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Unidades',
            'descricao': 'Gerenciar unidades',
            'icone': 'fa-building',
            'url': 'militares:unidade_list',
            'cor': 'success',
            'categoria': 'Organizacional'
        })
    
    if menu_permissions.get('show_sub_unidades') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Sub-Unidades',
            'descricao': 'Gerenciar sub-unidades',
            'icone': 'fa-sitemap',
            'url': 'militares:sub_unidade_list',
            'cor': 'success',
            'categoria': 'Organizacional'
        })
    
    # ===== USUÁRIOS E PERMISSÕES =====
    if menu_permissions.get('show_usuarios') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Gerenciar Usuários',
            'descricao': 'Gerenciar usuários do sistema',
            'icone': 'fa-users-cog',
            'url': 'militares:usuarios_custom_list',
            'cor': 'warning',
            'categoria': 'Usuários e Permissões'
        })
    
    if menu_permissions.get('show_permissoes') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Funções Militares',
            'descricao': 'Gerenciar funções e permissões',
            'icone': 'fa-user-tie',
            'url': 'militares:funcoes_militares_list',
            'cor': 'warning',
            'categoria': 'Usuários e Permissões'
        })
    
    # ===== SISTEMA =====
    if menu_permissions.get('show_logs') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Logs do Sistema',
            'descricao': 'Visualizar logs do sistema',
            'icone': 'fa-file-alt',
            'url': 'militares:logs_sistema_list',
            'cor': 'secondary',
            'categoria': 'Sistema'
        })
    
    if menu_permissions.get('show_administracao') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Administração',
            'descricao': 'Acessar painel administrativo',
            'icone': 'fa-cog',
            'url': 'admin:index',
            'cor': 'dark',
            'categoria': 'Sistema'
        })
    
    # ===== OPERAÇÕES =====
    if menu_permissions.get('show_administracao') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Configuração de Planejadas',
            'descricao': 'Configurar operações planejadas',
            'icone': 'fa-calendar-check',
            'url': 'militares:configuracao_planejadas_list',
            'cor': 'info',
            'categoria': 'Operações'
        })
    
    # ===== PUBLICACÕES =====
    if menu_permissions.get('show_titulos_publicacao') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Títulos de Publicações',
            'descricao': 'Gerenciar títulos de publicações',
            'icone': 'fa-file-alt',
            'url': 'militares:titulos_publicacao_list',
            'cor': 'info',
            'categoria': 'Publicações'
        })
    
    # ===== MATERIAL BÉLICO =====
    if menu_permissions.get('show_administracao') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Configurações de Armas',
            'descricao': 'Configurar armas do sistema',
            'icone': 'fa-gun',
            'url': 'militares:configuracao_arma_list',
            'cor': 'dark',
            'categoria': 'Material Bélico'
        })
    
    # ===== ALMOXARIFADO =====
    if menu_permissions.get('show_almoxarifado') or request.user.is_superuser:
        configuracoes.append({
            'titulo': 'Categorias',
            'descricao': 'Gerenciar categorias do almoxarifado',
            'icone': 'fa-tags',
            'url': 'militares:categoria_list',
            'cor': 'success',
            'categoria': 'Almoxarifado'
        })
        configuracoes.append({
            'titulo': 'Subcategorias',
            'descricao': 'Gerenciar subcategorias do almoxarifado',
            'icone': 'fa-tag',
            'url': 'militares:subcategoria_list',
            'cor': 'success',
            'categoria': 'Almoxarifado'
        })
    
    context = {
        'configuracoes': configuracoes,
        'menu_permissions': menu_permissions,
    }
    
    return render(request, 'militares/configuracoes_cartucheira.html', context)

