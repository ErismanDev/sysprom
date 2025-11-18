#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views para assinaturas de boletim
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from .models import Publicacao, AssinaturaNota, UsuarioFuncaoMilitar
from .models import HistoricoDevolucaoNota


def atualizar_status_boletim(boletim):
    """Atualiza o status do boletim baseado na hierarquia das assinaturas"""
    # Para boletins ostensivos, verificar tipos específicos de assinatura
    if boletim.tipo == 'BOLETIM_OSTENSIVO':
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
def dados_assinatura_boletim(request, pk):
    """Buscar dados do boletim para assinatura via AJAX"""
    print(f"DEBUG: dados_assinatura_boletim chamada - PK: {pk}, User: {request.user}")
    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_OSTENSIVO')
        print(f"DEBUG: Boletim encontrado - ID: {boletim.pk}, Título: {boletim.titulo}")
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
        
        # Ordenar assinaturas por hierarquia
        assinaturas_ordenadas = sorted(assinaturas, key=obter_prioridade_hierarquica)
        
        assinaturas_data = []
        for assinatura in assinaturas_ordenadas:
            # Obter nome completo com posto se for militar
            nome_completo = assinatura.assinado_por.get_full_name()
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{militar.nome_completo} - {posto}"
            
            assinaturas_data.append({
                'tipo_assinatura': assinatura.tipo_assinatura,
                'tipo_assinatura_display': assinatura.get_tipo_assinatura_display(),
                'tipo_midia': assinatura.tipo_midia,
                'tipo_midia_display': assinatura.get_tipo_midia_display(),
                'assinado_por': nome_completo,
                'data_assinatura': assinatura.data_assinatura.isoformat() if assinatura.data_assinatura else None,
                'observacoes': assinatura.observacoes or '-',
                'funcao_assinatura': assinatura.funcao_assinatura or '-',
                'assinatura_fisica': assinatura.assinatura_fisica.url if assinatura.assinatura_fisica else None,
                'hash_documento': assinatura.hash_documento,
                'certificado': assinatura.certificado,
                'timestamp': assinatura.timestamp,
            })
        
        return JsonResponse({
            'success': True,
            'boletim': {
                'id': boletim.pk,
                'numero': boletim.numero or '-',
                'titulo': boletim.titulo or '-',
                'status': boletim.status,
                'status_display': boletim.get_status_display(),
                'criado_por': boletim.criado_por.get_full_name() if boletim.criado_por else '-',
                'conteudo': boletim.conteudo or '',
                'topicos': boletim.topicos or '',
            },
            'funcoes_usuario': funcoes_data,
            'assinaturas': assinaturas_data,
        })
        
    except Exception as e:
        print(f"DEBUG: Erro ao buscar dados do boletim: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def assinaturas_boletim(request, pk):
    """Visualizar assinaturas do boletim"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_OSTENSIVO')
    
    # Obter assinaturas existentes
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    # Obter funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user
    ).select_related('funcao_militar')
    
    funcoes_data = []
    for ufm in funcoes_usuario:
        funcoes_data.append({
            'id': ufm.id,
            'nome': ufm.funcao_militar.nome,
            'orgao': ufm.orgao.nome if ufm.orgao else None,
            'grande_comando': ufm.grande_comando.nome if ufm.grande_comando else None,
            'unidade': ufm.unidade.nome if ufm.unidade else None,
            'sub_unidade': ufm.sub_unidade.nome if ufm.sub_unidade else None,
        })
    
    # Preparar dados do boletim
    boletim_data = {
        'id': boletim.pk,
        'numero': boletim.numero,
        'titulo': boletim.titulo,
        'status': boletim.status,
        'status_display': boletim.get_status_display(),
        'criado_por': boletim.criado_por.get_full_name() if boletim.criado_por else 'N/A',
        'data_criacao': boletim.data_criacao.strftime('%d/%m/%Y %H:%M') if boletim.data_criacao else None,
    }
    
    # Preparar dados das assinaturas
    assinaturas_data = []
    for assinatura in assinaturas:
        assinaturas_data.append({
            'tipo_assinatura': assinatura.tipo_assinatura,
            'assinado_por': assinatura.assinado_por.get_full_name() if assinatura.assinado_por else 'N/A',
            'data_assinatura': assinatura.data_assinatura.isoformat() if assinatura.data_assinatura else None,
            'observacoes': assinatura.observacoes or '',
            'funcao_assinatura': assinatura.funcao_assinatura.nome if assinatura.funcao_assinatura else 'N/A',
        })
    
    return JsonResponse({
        'success': True,
        'boletim': boletim_data,
        'funcoes_usuario': funcoes_data,
        'assinaturas': assinaturas_data,
    })


@login_required
def assinar_boletim(request, pk):
    """Assinar boletim"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_OSTENSIVO')
    
    if request.method == 'POST':
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: Request body: {request.body}")
        
        # Verificar se é requisição JSON
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            funcao_id = data.get('funcao_id')
            tipo_assinatura = data.get('tipo_assinatura')
            observacoes = data.get('observacoes', '')
            tipo_midia = data.get('tipo_midia', 'FISICA')
            
            # Dados para assinatura eletrônica
            hash_documento = data.get('hash_documento')
            timestamp = data.get('timestamp')
            assinatura_digital = data.get('assinatura_digital')
            certificado = data.get('certificado')
            
            print(f"DEBUG: JSON data - funcao_id: {funcao_id}, tipo_assinatura: {tipo_assinatura}, tipo_midia: {tipo_midia}")
        else:
            funcao_id = request.POST.get('funcao_id')
            tipo_assinatura = request.POST.get('tipo_assinatura')
            observacoes = request.POST.get('observacoes', '')
            tipo_midia = request.POST.get('tipo_midia', 'FISICA')
            
            # Dados para assinatura física
            assinatura_fisica = request.FILES.get('assinatura_fisica')
            
            print(f"DEBUG: POST data - funcao_id: {funcao_id}, tipo_assinatura: {tipo_assinatura}, tipo_midia: {tipo_midia}")
        
        if not funcao_id or not tipo_assinatura or funcao_id == 'undefined':
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'Dados obrigatórios não fornecidos.'
                })
            messages.error(request, 'Dados obrigatórios não fornecidos.')
            return redirect('militares:assinaturas_boletim', pk=pk)
        
        # Converter funcao_id para inteiro
        try:
            funcao_id = int(funcao_id)
        except (ValueError, TypeError):
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'ID da função inválido.'
                })
            messages.error(request, 'ID da função inválido.')
            return redirect('militares:assinaturas_boletim', pk=pk)
        
        try:
            funcao = UsuarioFuncaoMilitar.objects.get(
                id=funcao_id,
                usuario=request.user,
                ativo=True
            )
            
            with transaction.atomic():
                # Criar assinatura
                assinatura_data = {
                    'nota': boletim,
                    'assinado_por': request.user,
                    'funcao_assinatura': funcao.funcao_militar,
                    'tipo_assinatura': tipo_assinatura,
                    'observacoes': observacoes,
                    'tipo_midia': tipo_midia,
                }
                
                # Adicionar dados específicos baseado no tipo de mídia
                if tipo_midia == 'ELETRONICA':
                    if not all([hash_documento, timestamp, assinatura_digital]):
                        if request.content_type == 'application/json':
                            return JsonResponse({
                                'success': False,
                                'message': 'Dados de assinatura eletrônica incompletos.'
                            })
                        messages.error(request, 'Dados de assinatura eletrônica incompletos.')
                        return redirect('militares:assinaturas_boletim', pk=pk)
                    
                    assinatura_data.update({
                        'hash_documento': hash_documento,
                        'timestamp': timestamp,
                        'assinatura_digital': assinatura_digital,
                        'certificado': certificado or 'ASSINATURA_SIMPLES_SEI',
                        'ip_assinatura': request.META.get('REMOTE_ADDR', ''),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    })
                elif tipo_midia == 'FISICA' and not request.content_type == 'application/json':
                    # Para assinatura física via POST (upload de imagem)
                    if assinatura_fisica:
                        assinatura_data['assinatura_fisica'] = assinatura_fisica
                
                assinatura = AssinaturaNota.objects.create(**assinatura_data)
                
                # Atualizar status do boletim
                atualizar_status_boletim(boletim)
                
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'Boletim assinado com sucesso como {tipo_assinatura.lower()}.'
                    })
                else:
                    messages.success(request, f'Boletim assinado com sucesso como {tipo_assinatura.lower()}.')
                    return redirect('militares:assinaturas_boletim', pk=pk)
                
        except UsuarioFuncaoMilitar.DoesNotExist:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'Função não encontrada ou não autorizada.'
                })
            messages.error(request, 'Função não encontrada ou não autorizada.')
            return redirect('militares:assinaturas_boletim', pk=pk)
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao assinar boletim: {str(e)}'
                })
            messages.error(request, f'Erro ao assinar boletim: {str(e)}')
            return redirect('militares:assinaturas_boletim', pk=pk)
    
    # Se não for POST, retornar erro
    if request.content_type == 'application/json':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido.'
        })
    messages.error(request, 'Método não permitido.')
    return redirect('militares:assinaturas_boletim', pk=pk)


@login_required
def retirar_assinatura_boletim(request, pk, assinatura_pk):
    """Retirar assinatura do boletim"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_OSTENSIVO')
    assinatura = get_object_or_404(AssinaturaNota, pk=assinatura_pk, nota=boletim)
    
    # Verificar se o usuário pode retirar a assinatura
    if assinatura.assinado_por != request.user:
        messages.error(request, 'Você só pode retirar suas próprias assinaturas.')
        return redirect('militares:assinaturas_boletim', pk=pk)
    
    try:
        with transaction.atomic():
            assinatura.delete()
            atualizar_status_boletim(boletim)
            messages.success(request, 'Assinatura retirada com sucesso.')
    except Exception as e:
        messages.error(request, f'Erro ao retirar assinatura: {str(e)}')
    
    return redirect('militares:assinaturas_boletim', pk=pk)
