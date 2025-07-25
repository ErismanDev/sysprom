import os

VIEWS_BLOCO = '''\nfrom django.contrib.auth.models import Group, Permission\nfrom django.contrib.auth.decorators import login_required, permission_required\nfrom django.shortcuts import render, redirect, get_object_or_404\nfrom django.contrib import messages\n\n@login_required\n@permission_required('auth.view_group')\ndef grupo_list(request):\n    grupos = Group.objects.all().order_by('name')\n    return render(request, 'militares/permissoes/grupo_list.html', {'grupos': grupos})\n\n@login_required\n@permission_required('auth.add_group')\ndef grupo_create(request):\n    if request.method == 'POST':\n        nome = request.POST.get('name')\n        permissoes = request.POST.getlist('permissoes')\n        grupo = Group.objects.create(name=nome)\n        grupo.permissions.set(Permission.objects.filter(id__in=permissoes))\n        messages.success(request, 'Grupo criado com sucesso!')\n        return redirect('militares:grupo_list')\n    permissoes = Permission.objects.all().order_by('content_type__app_label', 'codename')\n    return render(request, 'militares/permissoes/grupo_form.html', {'permissoes': permissoes})\n\n@login_required\n@permission_required('auth.change_group')\ndef grupo_edit(request, grupo_id):\n    grupo = get_object_or_404(Group, pk=grupo_id)\n    if request.method == 'POST':\n        nome = request.POST.get('name')\n        permissoes = request.POST.getlist('permissoes')\n        grupo.name = nome\n        grupo.save()\n        grupo.permissions.set(Permission.objects.filter(id__in=permissoes))\n        messages.success(request, 'Grupo atualizado com sucesso!')\n        return redirect('militares:grupo_list')\n    permissoes = Permission.objects.all().order_by('content_type__app_label', 'codename')\n    grupo_permissoes = grupo.permissions.values_list('id', flat=True)\n    return render(request, 'militares/permissoes/grupo_form.html', {\n        'grupo': grupo,\n        'permissoes': permissoes,\n        'grupo_permissoes': grupo_permissoes\n    })\n\n@login_required\n@permission_required('auth.delete_group')\ndef grupo_delete(request, grupo_id):\n    grupo = get_object_or_404(Group, pk=grupo_id)\n    if request.method == 'POST':\n        grupo.delete()\n        messages.success(request, 'Grupo excluído com sucesso!')\n        return redirect('militares:grupo_list')\n    return render(request, 'militares/permissoes/grupo_confirm_delete.html', {'grupo': grupo})\n'''

VIEWS_PATH = os.path.join('militares', 'views.py')

with open(VIEWS_PATH, 'r', encoding='utf-8') as f:
    conteudo = f.read()

if 'def grupo_list' not in conteudo:
    with open(VIEWS_PATH, 'a', encoding='utf-8') as f:
        f.write(VIEWS_BLOCO)
    print('Views de grupos adicionadas com sucesso!')
else:
    print('As views de grupos já existem no arquivo.') 