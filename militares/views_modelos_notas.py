from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ModeloNota
from .forms import ModeloNotaForm


@login_required
def modelos_notas_list(request):
    """Listar modelos de notas"""
    modelos = ModeloNota.objects.filter(ativo=True).order_by('-padrao', 'nome')
    
    # Filtros
    busca = request.GET.get('busca')
    tipo_publicacao = request.GET.get('tipo_publicacao')
    
    if busca:
        modelos = modelos.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    if tipo_publicacao:
        modelos = modelos.filter(tipo_publicacao=tipo_publicacao)
    
    # Paginação
    paginator = Paginator(modelos, 12)
    page_number = request.GET.get('page')
    modelos_page = paginator.get_page(page_number)
    
    context = {
        'modelos': modelos_page,
        'tipos_publicacao': ModeloNota.TIPO_PUBLICACAO_CHOICES,
        'filtros': {
            'busca': busca,
            'tipo_publicacao': tipo_publicacao,
        }
    }
    
    return render(request, 'militares/modelos_notas_list.html', context)


@login_required
def modelo_nota_detail(request, pk):
    """Visualizar detalhes do modelo de nota"""
    modelo = get_object_or_404(ModeloNota, pk=pk, ativo=True)
    
    context = {
        'modelo': modelo,
    }
    
    return render(request, 'militares/modelo_nota_detail.html', context)


@login_required
def modelo_nota_create(request):
    """Criar novo modelo de nota"""
    if request.method == 'POST':
        form = ModeloNotaForm(request.POST)
        if form.is_valid():
            modelo = form.save(commit=False)
            modelo.criado_por = request.user
            modelo.save()
            messages.success(request, 'Modelo de nota criado com sucesso!')
            return redirect('militares:modelo_nota_detail', pk=modelo.pk)
    else:
        form = ModeloNotaForm()
    
    context = {
        'form': form,
        'title': 'Criar Modelo de Nota'
    }
    
    return render(request, 'militares/modelo_nota_form.html', context)


@login_required
def modelo_nota_edit(request, pk):
    """Editar modelo de nota"""
    modelo = get_object_or_404(ModeloNota, pk=pk, ativo=True)
    
    # Verificar permissão de edição
    if not (request.user.is_superuser or modelo.criado_por == request.user):
        messages.error(request, 'Você não tem permissão para editar este modelo.')
        return redirect('militares:modelos_notas_list')
    
    if request.method == 'POST':
        form = ModeloNotaForm(request.POST, instance=modelo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modelo de nota atualizado com sucesso!')
            return redirect('militares:modelo_nota_detail', pk=modelo.pk)
    else:
        form = ModeloNotaForm(instance=modelo)
    
    context = {
        'form': form,
        'modelo': modelo,
        'title': 'Editar Modelo de Nota'
    }
    
    return render(request, 'militares/modelo_nota_form.html', context)


@login_required
def modelo_nota_delete(request, pk):
    """Excluir modelo de nota"""
    modelo = get_object_or_404(ModeloNota, pk=pk, ativo=True)
    
    # Verificar permissão de exclusão
    if not (request.user.is_superuser or modelo.criado_por == request.user):
        messages.error(request, 'Você não tem permissão para excluir este modelo.')
        return redirect('militares:modelos_notas_list')
    
    if request.method == 'POST':
        modelo.ativo = False
        modelo.save()
        messages.success(request, 'Modelo de nota excluído com sucesso!')
        return redirect('militares:modelos_notas_list')
    
    context = {
        'modelo': modelo,
    }
    
    return render(request, 'militares/modelo_nota_confirm_delete.html', context)


@login_required
def ajax_modelos_notas(request):
    """Retorna lista de modelos de notas para AJAX"""
    try:
        modelos = ModeloNota.objects.filter(ativo=True).order_by('-padrao', 'nome')
        
        # Filtro por tipo de publicação se especificado
        tipo_publicacao = request.GET.get('tipo_publicacao')
        if tipo_publicacao and tipo_publicacao != 'GERAL':
            modelos = modelos.filter(tipo_publicacao=tipo_publicacao)
        
        # Filtro por busca se especificado
        busca = request.GET.get('busca')
        if busca:
            modelos = modelos.filter(
                Q(nome__icontains=busca) | 
                Q(descricao__icontains=busca)
            )
        
        modelos_data = []
        for modelo in modelos:
            modelos_data.append({
                'id': modelo.id,
                'nome': modelo.nome,
                'descricao': modelo.descricao or '',
                'tipo_publicacao': modelo.tipo_publicacao,
                'tipo_publicacao_display': modelo.get_tipo_publicacao_display(),
                'conteudo': modelo.conteudo,
                'padrao': modelo.padrao,
                'autor': modelo.get_autor_display(),
                'data_criacao': modelo.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'pode_editar': request.user.is_superuser or modelo.criado_por == request.user,
            })
        
        return JsonResponse({
            'success': True,
            'modelos': modelos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def ajax_modelo_nota_detail(request, pk):
    """Retorna detalhes de um modelo de nota específico para AJAX"""
    try:
        modelo = ModeloNota.objects.get(pk=pk, ativo=True)
        
        return JsonResponse({
            'success': True,
            'modelo': {
                'id': modelo.id,
                'nome': modelo.nome,
                'descricao': modelo.descricao or '',
                'tipo_publicacao': modelo.tipo_publicacao,
                'tipo_publicacao_display': modelo.get_tipo_publicacao_display(),
                'conteudo': modelo.conteudo,
                'padrao': modelo.padrao,
                'autor': modelo.get_autor_display(),
                'data_criacao': modelo.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'pode_editar': request.user.is_superuser or modelo.criado_por == request.user,
            }
        })
        
    except ModeloNota.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Modelo de nota não encontrado'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
