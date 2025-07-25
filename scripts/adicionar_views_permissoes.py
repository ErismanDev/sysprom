import os

VIEWS_BLOCO = '''

@login_required
@permission_required('auth.change_group')
def gerenciar_permissoes_funcao(request, cargo_id):
    """Gerencia as permissões de uma função específica"""
    cargo = get_object_or_404(CargoFuncao, pk=cargo_id)
    
    if request.method == 'POST':
        permissoes_selecionadas = request.POST.getlist('permissoes')
        
        # Limpar permissões atuais da função
        PermissaoFuncao.objects.filter(cargo_funcao=cargo).delete()
        
        # Adicionar novas permissões
        for perm_id in permissoes_selecionadas:
            permissao = Permission.objects.get(id=perm_id)
            # Extrair módulo e acesso da permissão Django
            codename = permissao.codename
            if '_' in codename:
                modulo, acesso = codename.rsplit('_', 1)
                modulo = modulo.upper()
                acesso = acesso.upper()
            else:
                modulo = 'OUTROS'
                acesso = 'VISUALIZAR'
            
            PermissaoFuncao.objects.create(
                cargo_funcao=cargo,
                modulo=modulo,
                acesso=acesso
            )
        
        # Aplicar permissões aos usuários que possuem esta função
        aplicar_permissoes_funcao_a_usuarios(cargo)
        
        messages.success(request, f'Permissões da função "{cargo.nome}" atualizadas e aplicadas aos usuários com sucesso!')
        return redirect('militares:gerenciar_permissoes')
    
    # Buscar todas as permissões organizadas por app
    permissoes_por_app = {}
    for perm in Permission.objects.all().order_by('content_type__app_label', 'name'):
        app_label = perm.content_type.app_label
        if app_label not in permissoes_por_app:
            permissoes_por_app[app_label] = []
        permissoes_por_app[app_label].append(perm)
    
    # Buscar permissões atuais da função
    permissoes_atuais = set(
        (p.modulo, p.acesso)
        for p in PermissaoFuncao.objects.filter(cargo_funcao=cargo)
    )
    
    context = {
        'cargo': cargo,
        'permissoes_por_app': permissoes_por_app,
        'permissoes_atuais': list(permissoes_atuais)
    }
    
    return render(request, 'militares/permissoes/gerenciar_permissoes_funcao.html', context)

def aplicar_permissoes_funcao_a_usuarios(cargo_funcao):
    """Aplica as permissões de uma função a todos os usuários que possuem essa função"""
    # Buscar todos os usuários que possuem esta função
    usuarios_com_funcao = UsuarioFuncao.objects.filter(cargo_funcao=cargo_funcao)
    
    # Buscar todas as permissões desta função
    permissoes_funcao = PermissaoFuncao.objects.filter(cargo_funcao=cargo_funcao)
    
    for usuario_funcao in usuarios_com_funcao:
        usuario = usuario_funcao.usuario
        
        # Remover permissões antigas da função
        for permissao_funcao in permissoes_funcao:
            # Buscar permissão Django correspondente ao módulo e acesso
            try:
                permissao_django = Permission.objects.get(
                    content_type__app_label='militares',
                    codename=f"{permissao_funcao.modulo.lower()}_{permissao_funcao.acesso.lower()}"
                )
                usuario.user_permissions.remove(permissao_django)
            except Permission.DoesNotExist:
                # Se a permissão não existe, apenas continuar
                pass
        
        # Adicionar novas permissões
        for permissao_funcao in permissoes_funcao:
            # Buscar permissão Django correspondente ao módulo e acesso
            try:
                permissao_django = Permission.objects.get(
                    content_type__app_label='militares',
                    codename=f"{permissao_funcao.modulo.lower()}_{permissao_funcao.acesso.lower()}"
                )
                usuario.user_permissions.add(permissao_django)
            except Permission.DoesNotExist:
                # Se a permissão não existe, apenas continuar
                pass
'''

VIEWS_PATH = os.path.join('militares', 'views.py')

with open(VIEWS_PATH, 'r', encoding='utf-8') as f:
    conteudo = f.read()

if 'def gerenciar_permissoes_funcao' not in conteudo:
    with open(VIEWS_PATH, 'a', encoding='utf-8') as f:
        f.write(VIEWS_BLOCO)
    print('Views de gerenciamento de permissões adicionadas com sucesso!')
else:
    print('As views de gerenciamento de permissões já existem no arquivo.') 