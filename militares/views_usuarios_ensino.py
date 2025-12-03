# -*- coding: utf-8 -*-
"""
Views para Controle de Usuários do Módulo de Ensino
Gerenciamento de alunos, instrutores e monitores
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Case, When, Value, IntegerField
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from militares.models import AlunoEnsino, InstrutorEnsino, MonitorEnsino
from militares.views_ensino import pode_visualizar_ensino, pode_editar_ensino


@login_required
def usuarios_ensino_listar(request):
    """Lista todos os usuários do módulo de ensino (alunos, instrutores, monitores)"""
    if not pode_visualizar_ensino(request.user) and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para visualizar usuários do módulo de ensino.')
        return redirect('militares:home')
    
    # Parâmetros de filtro
    tipo_usuario = request.GET.get('tipo', '')
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    
    per_page = int(request.GET.get('per_page', '20') or 20)
    alunos = []
    instrutores = []
    monitores = []
    alunos_page = None
    instrutores_page = None
    monitores_page = None
    
    # Buscar alunos
    if not tipo_usuario or tipo_usuario == 'aluno':
        alunos_query = AlunoEnsino.objects.all()
        
        if query:
            alunos_query = alunos_query.filter(
                Q(matricula__icontains=query) |
                Q(militar__nome_completo__icontains=query) |
                Q(militar__cpf__icontains=query) |
                Q(nome_outra_forca__icontains=query) |
                Q(nome_civil__icontains=query) |
                Q(cpf_outra_forca__icontains=query) |
                Q(cpf_civil__icontains=query)
            )
        
        if status == 'ativo':
            alunos_query = alunos_query.filter(situacao='ATIVO')
        elif status == 'inativo':
            alunos_query = alunos_query.exclude(situacao='ATIVO')
        
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        alunos_query = alunos_query.select_related('militar', 'turma').annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'ordem_hierarquia',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'nome_outra_forca',
            'nome_civil',
            'matricula'
        )
        alunos_page = Paginator(alunos_query, per_page).get_page(request.GET.get('page_alunos') or request.GET.get('page') or 1)
        alunos = list(alunos_page.object_list)
    
    # Buscar instrutores
    if not tipo_usuario or tipo_usuario == 'instrutor':
        instrutores_query = InstrutorEnsino.objects.all()
        
        if query:
            instrutores_query = instrutores_query.filter(
                Q(militar__nome_completo__icontains=query) |
                Q(militar__cpf__icontains=query) |
                Q(nome_outra_forca__icontains=query) |
                Q(nome_civil__icontains=query) |
                Q(cpf_outra_forca__icontains=query) |
                Q(cpf_civil__icontains=query)
            )
        
        if status == 'ativo':
            instrutores_query = instrutores_query.filter(ativo=True)
        elif status == 'inativo':
            instrutores_query = instrutores_query.filter(ativo=False)
        
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        instrutores_query = instrutores_query.select_related('militar').annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'ordem_hierarquia',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'nome_outra_forca',
            'nome_civil'
        )
        instrutores_page = Paginator(instrutores_query, per_page).get_page(request.GET.get('page_instrutores') or request.GET.get('page') or 1)
        instrutores = list(instrutores_page.object_list)
    
    # Buscar monitores
    if not tipo_usuario or tipo_usuario == 'monitor':
        monitores_query = MonitorEnsino.objects.all()
        
        if query:
            monitores_query = monitores_query.filter(
                Q(militar__nome_completo__icontains=query) |
                Q(militar__cpf__icontains=query) |
                Q(nome_outra_forca__icontains=query) |
                Q(nome_civil__icontains=query) |
                Q(cpf_outra_forca__icontains=query) |
                Q(cpf_civil__icontains=query)
            )
        
        if status == 'ativo':
            monitores_query = monitores_query.filter(ativo=True)
        elif status == 'inativo':
            monitores_query = monitores_query.filter(ativo=False)
        
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        monitores_query = monitores_query.select_related('militar').annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'ordem_hierarquia',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'nome_outra_forca',
            'nome_civil'
        )
        monitores_page = Paginator(monitores_query, per_page).get_page(request.GET.get('page_monitores') or request.GET.get('page') or 1)
        monitores = list(monitores_page.object_list)
    
    # Estatísticas
    total_alunos = AlunoEnsino.objects.count()
    alunos_ativos = AlunoEnsino.objects.filter(situacao='ATIVO').count()
    total_instrutores = InstrutorEnsino.objects.count()
    instrutores_ativos = InstrutorEnsino.objects.filter(ativo=True).count()
    total_monitores = MonitorEnsino.objects.count()
    monitores_ativos = MonitorEnsino.objects.filter(ativo=True).count()
    
    context = {
        'alunos': alunos,
        'instrutores': instrutores,
        'monitores': monitores,
        'alunos_page': alunos_page,
        'instrutores_page': instrutores_page,
        'monitores_page': monitores_page,
        'alunos_start_index': (alunos_page.start_index() if alunos_page else 1),
        'alunos_end_index': (alunos_page.end_index() if alunos_page else len(alunos)),
        'instrutores_start_index': (instrutores_page.start_index() if instrutores_page else 1),
        'instrutores_end_index': (instrutores_page.end_index() if instrutores_page else len(instrutores)),
        'monitores_start_index': (monitores_page.start_index() if monitores_page else 1),
        'monitores_end_index': (monitores_page.end_index() if monitores_page else len(monitores)),
        'tipo_usuario': tipo_usuario,
        'query': query,
        'status': status,
        'per_page': per_page,
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'total_instrutores': total_instrutores,
        'instrutores_ativos': instrutores_ativos,
        'total_monitores': total_monitores,
        'monitores_ativos': monitores_ativos,
    }
    
    return render(request, 'militares/ensino/usuarios/listar.html', context)


@login_required
def usuario_ensino_definir_senha(request, tipo, pk):
    """Define ou altera a senha de um usuário do módulo de ensino"""
    if not pode_editar_ensino(request.user) and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar usuários do módulo de ensino.')
        return redirect('militares:ensino_usuarios_listar')
    
    if request.method == 'POST':
        senha = request.POST.get('senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()
        
        if not senha:
            messages.error(request, 'A senha é obrigatória.')
            return redirect('militares:ensino_usuario_definir_senha', tipo=tipo, pk=pk)
        
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('militares:ensino_usuario_definir_senha', tipo=tipo, pk=pk)
        
        if len(senha) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            return redirect('militares:ensino_usuario_definir_senha', tipo=tipo, pk=pk)
        
        # Buscar o usuário baseado no tipo
        if tipo == 'aluno':
            usuario = get_object_or_404(AlunoEnsino, pk=pk)
            nome = usuario.get_pessoa_nome()
        elif tipo == 'instrutor':
            usuario = get_object_or_404(InstrutorEnsino, pk=pk)
            nome = usuario.get_nome_completo()
        elif tipo == 'monitor':
            usuario = get_object_or_404(MonitorEnsino, pk=pk)
            nome = usuario.get_nome_completo()
        else:
            messages.error(request, 'Tipo de usuário inválido.')
            return redirect('militares:ensino_usuarios_listar')
        
        # Definir senha
        usuario.senha_hash = make_password(senha)
        usuario.save()
        
        messages.success(request, f'Senha definida com sucesso para {nome}!')
        return redirect('militares:ensino_usuarios_listar')
    
    # GET - mostrar formulário
    if tipo == 'aluno':
        usuario = get_object_or_404(AlunoEnsino, pk=pk)
        nome = usuario.get_pessoa_nome()
    elif tipo == 'instrutor':
        usuario = get_object_or_404(InstrutorEnsino, pk=pk)
        nome = usuario.get_nome_completo()
    elif tipo == 'monitor':
        usuario = get_object_or_404(MonitorEnsino, pk=pk)
        nome = usuario.get_nome_completo()
    else:
        messages.error(request, 'Tipo de usuário inválido.')
        return redirect('militares:ensino_usuarios_listar')
    
    context = {
        'usuario': usuario,
        'tipo': tipo,
        'nome': nome,
        'tem_senha': bool(usuario.senha_hash),
    }
    
    return render(request, 'militares/ensino/usuarios/definir_senha.html', context)


@login_required
def usuario_ensino_detalhes(request, tipo, pk):
    """Detalhes de um usuário do módulo de ensino"""
    if not pode_visualizar_ensino(request.user) and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para visualizar usuários do módulo de ensino.')
        return redirect('militares:home')
    
    if tipo == 'aluno':
        usuario = get_object_or_404(AlunoEnsino, pk=pk)
        nome = usuario.get_pessoa_nome()
        template = 'militares/ensino/alunos/detalhes.html'
    elif tipo == 'instrutor':
        usuario = get_object_or_404(InstrutorEnsino, pk=pk)
        nome = usuario.get_nome_completo()
        template = 'militares/ensino/instrutores/detalhes.html'
    elif tipo == 'monitor':
        usuario = get_object_or_404(MonitorEnsino, pk=pk)
        nome = usuario.get_nome_completo()
        template = 'militares/ensino/monitores/detalhes.html'
    else:
        messages.error(request, 'Tipo de usuário inválido.')
        return redirect('militares:ensino_usuarios_listar')
    
    context = {
        'usuario': usuario,
        'tipo': tipo,
        'nome': nome,
        'tem_senha': bool(usuario.senha_hash),
    }
    
    # Adicionar contexto específico baseado no tipo
    if tipo == 'aluno':
        context['aluno'] = usuario
    elif tipo == 'instrutor':
        context['instrutor'] = usuario
    elif tipo == 'monitor':
        context['monitor'] = usuario
    
    return render(request, template, context)

