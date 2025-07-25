# Views para gerenciamento de usuários admin
# Adicionar ao final do arquivo militares/views.py

@admin_bypass
def criar_usuario_admin_web(request):
    """View para criar usuários admin via web"""
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validações
        if not username or not password:
            messages.error(request, 'Username e senha são obrigatórios!')
            return redirect('militares:criar_usuario_admin')
        
        if password != confirm_password:
            messages.error(request, 'Senhas não coincidem!')
            return redirect('militares:criar_usuario_admin')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Usuário "{username}" já existe!')
            return redirect('militares:criar_usuario_admin')
        
        try:
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            
            # Configurar permissões
            todas_permissoes = Permission.objects.all()
            user.user_permissions.set(todas_permissoes)
            
            # Adicionar a todos os grupos
            todos_grupos = Group.objects.all()
            for grupo in todos_grupos:
                user.groups.add(grupo)
            
            # Configurar função de administrador
            cargo_admin = CargoFuncao.objects.get_or_create(
                nome='Administrador',
                defaults={
                    'descricao': 'Administrador do sistema com acesso total',
                    'ativo': True
                }
            )[0]
            
            UsuarioFuncao.objects.get_or_create(
                usuario=user,
                cargo_funcao=cargo_admin,
                defaults={
                    'tipo_funcao': 'EFETIVA',
                    'status': 'ATIVO',
                    'data_inicio': '2024-01-01'
                }
            )
            
            messages.success(request, f'Usuário admin "{username}" criado com sucesso!')
            return redirect('militares:listar_usuarios_admin')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {e}')
            return redirect('militares:criar_usuario_admin')
    
    return render(request, 'militares/usuarios/criar_usuario_admin.html')

@admin_bypass
def listar_usuarios_admin_web(request):
    """View para listar usuários admin via web"""
    
    admins = User.objects.filter(is_superuser=True).order_by('username')
    
    # Buscar funções de cada admin
    for admin in admins:
        admin.funcao_ativa = UsuarioFuncao.objects.filter(
            usuario=admin,
            status='ATIVO'
        ).first()
    
    context = {
        'admins': admins,
    }
    
    return render(request, 'militares/usuarios/listar_usuarios_admin.html', context)

@admin_bypass
def remover_usuario_admin_web(request, user_id):
    """View para remover usuário admin via web"""
    
    try:
        user = User.objects.get(id=user_id)
        
        if not user.is_superuser:
            messages.error(request, f'Usuário "{user.username}" não é admin!')
            return redirect('militares:listar_usuarios_admin')
        
        if user.username == 'admin':
            messages.error(request, 'Não é possível remover o usuário admin principal!')
            return redirect('militares:listar_usuarios_admin')
        
        username = user.username
        user.delete()
        
        messages.success(request, f'Usuário admin "{username}" removido com sucesso!')
        
    except User.DoesNotExist:
        messages.error(request, 'Usuário não encontrado!')
    
    return redirect('militares:listar_usuarios_admin')

@admin_bypass
def gerenciar_usuarios_admin(request):
    """View principal para gerenciar usuários admin"""
    
    total_admins = User.objects.filter(is_superuser=True).count()
    admins_ativos = User.objects.filter(is_superuser=True, is_active=True).count()
    
    context = {
        'total_admins': total_admins,
        'admins_ativos': admins_ativos,
    }
    
    return render(request, 'militares/usuarios/gerenciar_usuarios_admin.html', context) 