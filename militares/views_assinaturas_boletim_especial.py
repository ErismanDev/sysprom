#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views para assinaturas de boletim especial
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import Publicacao, AssinaturaNota, UsuarioFuncaoMilitar
from .permissoes import obter_funcao_atual


def atualizar_status_boletim_especial(boletim):
    """Atualiza o status do boletim especial baseado na hierarquia das assinaturas"""
    # Para boletins especiais, verificar tipos específicos de assinatura
    if boletim.tipo == 'BOLETIM_ESPECIAL':
        # Verificar se tem assinatura de Editor Geral (mais alta hierarquia)
        if boletim.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists():
            boletim.status = 'EDITADA'
        # Se não tem Editor Geral, verificar Editor Adjunto
        elif boletim.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists():
            boletim.status = 'EDITADA'
        # Se não tem Editor Adjunto, verificar Editor Chefe
        elif boletim.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists():
            boletim.status = 'EDITADA'
        # Se não tem nenhuma assinatura, manter como rascunho
        else:
            boletim.status = 'RASCUNHO'
    else:
        # Para outros tipos de publicação, usar lógica original
        # Verificar se tem assinatura de edição (status mais recente)
        if boletim.assinaturas.filter(tipo_assinatura='EDICAO').exists():
            boletim.status = 'EM_EDICAO'
        # Se não tem edição, verificar se tem aprovação
        elif boletim.assinaturas.filter(tipo_assinatura='APROVACAO').exists():
            boletim.status = 'APROVADA'
        # Se não tem aprovação, verificar se tem revisão
        elif boletim.assinaturas.filter(tipo_assinatura='REVISAO').exists():
            boletim.status = 'REVISADA'
        # Se não tem nenhuma assinatura, manter como rascunho
        else:
            boletim.status = 'RASCUNHO'
    boletim.save()


@login_required
def dados_assinatura_boletim_especial(request, pk):
    """Buscar dados do boletim especial para assinatura via AJAX"""
    print(f"DEBUG: dados_assinatura_boletim_especial chamada - PK: {pk}, User: {request.user}")
    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_ESPECIAL')
        print(f"DEBUG: Boletim especial encontrado - ID: {boletim.pk}, Título: {boletim.titulo}")
        print(f"DEBUG: Conteúdo do boletim: {boletim.conteudo[:100] if boletim.conteudo else 'VAZIO'}...")
        print(f"DEBUG: Tópicos do boletim: {boletim.topicos}")
        
        # Obter funções ativas do usuário
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user
        ).select_related('funcao_militar')
        
        funcoes_data = []
        for ufm in funcoes_usuario:
            funcoes_data.append({
                'id': ufm.id,
                'nome': ufm.funcao_militar.nome,
                'ativo': ufm.ativo
            })
        
        # Obter assinaturas do boletim e ordenar por hierarquia militar
        assinaturas = boletim.assinaturas.all()
        
        # Ordenar assinaturas por hierarquia militar (de coronel a soldado)
        def obter_prioridade_hierarquica(assinatura):
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.posto_graduacao
                
                # Definir prioridades hierárquicas (menor número = maior hierarquia)
                prioridades = {
                    'CORONEL': 1,
                    'TENENTE_CORONEL': 2,
                    'MAJOR': 3,
                    'CAPITAO': 4,
                    'PRIMEIRO_TENENTE': 5,
                    'SEGUNDO_TENENTE': 6,
                    'ASPIRANTE_A_OFICIAL': 7,
                    'SUBTENENTE': 8,
                    'PRIMEIRO_SARGENTO': 9,
                    'SEGUNDO_SARGENTO': 10,
                    'TERCEIRO_SARGENTO': 11,
                    'CABO': 12,
                    'SOLDADO': 13,
                }
                return prioridades.get(posto, 99)  # Se não encontrar, colocar no final
            return 99  # Se não for militar, colocar no final
        
        assinaturas_ordenadas = sorted(assinaturas, key=obter_prioridade_hierarquica)
        
        assinaturas_data = []
        for assinatura in assinaturas_ordenadas:
            assinaturas_data.append({
                'id': assinatura.id,
                'assinado_por': assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username,
                'assinado_por_nome': assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username,
                'funcao_assinatura': assinatura.funcao_assinatura,
                'tipo_assinatura': assinatura.tipo_assinatura,
                'data_assinatura': assinatura.data_assinatura.isoformat(),
                'observacoes': assinatura.observacoes or '-',
                'tipo_midia': assinatura.tipo_midia,
            })
        
        print(f"DEBUG: Assinaturas encontradas: {len(assinaturas_data)}")
        for assinatura in assinaturas_data:
            print(f"  - {assinatura['assinado_por']} ({assinatura['tipo_assinatura']})")
        
        return JsonResponse({
            'success': True,
            'boletim': {
                'id': boletim.id,
                'titulo': boletim.titulo,
                'numero': boletim.numero,
                'conteudo': boletim.conteudo or '',
                'topicos': boletim.topicos or '',
                'status': boletim.status,
                'status_display': boletim.get_status_display(),
                'criado_por': boletim.criado_por.get_full_name() if boletim.criado_por else boletim.criado_por.username if boletim.criado_por else 'Sistema',
                'data_criacao': boletim.data_criacao.strftime('%d/%m/%Y %H:%M'),
            },
            'funcoes_usuario': funcoes_data,
            'assinaturas': assinaturas_data,
        })
        
    except Exception as e:
        print(f"DEBUG: Erro em dados_assinatura_boletim_especial: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def assinaturas_boletim_especial(request, pk):
    """Página de assinaturas do boletim especial"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_ESPECIAL')
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Buscar funções do usuário que podem assinar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        ativo=True
    ).select_related('funcao_militar')
    
    # Buscar assinaturas existentes
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    context = {
        'boletim': boletim,
        'funcao_atual': funcao_atual,
        'funcoes_usuario': funcoes_usuario,
        'assinaturas': assinaturas,
    }
    
    return render(request, 'militares/boletins_especiais/assinaturas_boletim_especial.html', context)


@login_required
def assinar_boletim_especial(request, pk):
    """Assinar boletim especial"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_ESPECIAL')
        
        # Obter dados do formulário (JSON ou POST)
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: Request body: {request.body}")
        
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            funcao_id = data.get('funcao_id')
            tipo_assinatura = data.get('tipo_assinatura')
            observacoes = data.get('observacoes', '').strip()
            tipo_midia = data.get('tipo_midia', 'ELETRONICA')
            print(f"DEBUG: JSON data - funcao_id: {funcao_id}, tipo_assinatura: {tipo_assinatura}")
        else:
            funcao_id = request.POST.get('funcao_id')
            tipo_assinatura = request.POST.get('tipo_assinatura')
            observacoes = request.POST.get('observacoes', '').strip()
            tipo_midia = request.POST.get('tipo_midia', 'ELETRONICA')
            print(f"DEBUG: POST data - funcao_id: {funcao_id}, tipo_assinatura: {tipo_assinatura}")
        
        if not funcao_id or not tipo_assinatura:
            return JsonResponse({'success': False, 'message': 'Dados obrigatórios não fornecidos'})
        
        # Verificar se a função pertence ao usuário
        try:
            funcao_usuario = UsuarioFuncaoMilitar.objects.get(
                id=funcao_id,
                usuario=request.user,
                ativo=True
            )
        except UsuarioFuncaoMilitar.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Função não encontrada ou inativa'})
        
        # Verificar se já existe assinatura desta função para este tipo
        assinatura_existente = boletim.assinaturas.filter(
            assinado_por=request.user,
            funcao_assinatura=funcao_usuario.funcao_militar.nome,
            tipo_assinatura=tipo_assinatura
        ).first()
        
        if assinatura_existente:
            return JsonResponse({'success': False, 'message': 'Você já assinou este boletim com esta função'})
        
        with transaction.atomic():
            # Criar assinatura
            assinatura = boletim.assinaturas.create(
                assinado_por=request.user,
                funcao_assinatura=funcao_usuario.funcao_militar.nome,
                tipo_assinatura=tipo_assinatura,
                observacoes=observacoes,
                tipo_midia=tipo_midia,
                data_assinatura=timezone.now()
            )
            
            # Atualizar status do boletim
            atualizar_status_boletim_especial(boletim)
            
            return JsonResponse({
                'success': True,
                'message': f'Boletim assinado com sucesso como {funcao_usuario.funcao_militar.nome}',
                'assinatura_id': assinatura.id
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao assinar boletim: {str(e)}'})


@login_required
def retirar_assinatura_boletim_especial(request, pk, assinatura_pk):
    """Retirar assinatura do boletim especial"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_ESPECIAL')
        assinatura = get_object_or_404(boletim.assinaturas, pk=assinatura_pk)
        
        # Verificar se o usuário pode retirar esta assinatura
        if assinatura.assinado_por != request.user and not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Você só pode retirar suas próprias assinaturas'})
        
        with transaction.atomic():
            # Remover assinatura
            assinatura.delete()
            
            # Atualizar status do boletim
            atualizar_status_boletim_especial(boletim)
            
            return JsonResponse({
                'success': True,
                'message': 'Assinatura retirada com sucesso'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao retirar assinatura: {str(e)}'})
