import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Nova implementação da view usuario_create
nova_view = '''@login_required
@permission_required('auth.add_user')
def usuario_create(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            usuario.save()
            
            # Criar relação com função/cargo
            cargo_funcao = form.cleaned_data.get('cargo_funcao')
            if cargo_funcao:
                UsuarioFuncao.objects.create(
                    usuario=usuario, 
                    cargo_funcao=cargo_funcao, 
                    status='ATIVO'
                )
            
            # Associar militar se fornecido
            militar_id = form.cleaned_data.get('militar_id')
            if militar_id:
                try:
                    militar = Militar.objects.get(id=militar_id)
                    messages.success(request, f'Usuário "{usuario.username}" criado com sucesso e associado ao militar "{militar.nome_completo}"!')
                except Militar.DoesNotExist:
                    messages.warning(request, f'Usuário "{usuario.username}" criado com sucesso, mas militar não encontrado.')
            else:
                messages.success(request, f'Usuário "{usuario.username}" criado com sucesso!')
            
            return redirect('militares:usuarios_custom_list')
    else:
        form = UsuarioForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Usuário',
        'submit_text': 'Criar Usuário'
    }
    
    return render(request, 'militares/usuarios/form.html', context)'''

# Substituir a view antiga pela nova
import re
padrao = r'@login_required\s*\n@permission_required\(''auth\.add_user''\)\s*\ndef usuario_create\(request\):\s*"""[^"]*"""\s*if request\.method == ''POST'':\s*form = UsuarioForm\(request\.POST\)\s*if form\.is_valid\(\):\s*usuario = form\.save\(commit=False\)\s*password = form\.cleaned_data\.get\(''password''\)\s*if password:\s*usuario\.set_password\(password\)\s*usuario\.save\(\)\s*form\.save_m2m\(\)\s*# Salvar grupos\s*# Associar militar se fornecido\s*militar_id = form\.cleaned_data\.get\(''militar_id''\)\s*if militar_id:\s*try:\s*militar = Militar\.objects\.get\(id=militar_id\)\s*# Aqui você pode adicionar a lógica para associar o militar ao usuário\s*# Por exemplo, criar um perfil de militar ou adicionar um campo relacionado\s*messages\.success\(request, f''Usuário "''{usuario\.username}''" criado com sucesso e associado ao militar "''{militar\.nome_completo}''"!''\)\s*except Militar\.DoesNotExist:\s*messages\.warning\(request, f''Usuário "''{usuario\.username}''" criado com sucesso, mas militar não encontrado\.''\)\s*else:\s*messages\.success\(request, f''Usuário "''{usuario\.username}''" criado com sucesso!''\)\s*return redirect\(''militares:usuarios_custom_list''\)\s*else:\s*form = UsuarioForm\(\)\s*context = {\s*''form'': form,\s*''title'': ''Criar Novo Usuário'',\s*''submit_text'': ''Criar Usuário''\s*}\s*return render\(request, ''militares/usuarios/form\.html'', context\)'

conteudo_atualizado = re.sub(padrao, nova_view, conteudo, flags=re.DOTALL)

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(conteudo_atualizado)

print('View usuario_create atualizada para usar o formulário correto e criar relação UsuarioFuncao!') 