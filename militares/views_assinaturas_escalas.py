#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views para assinaturas de escalas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from .models import EscalaServico, AssinaturaEscala, UsuarioFuncaoMilitar


def atualizar_status_escala(escala):
    """Atualiza o status da escala baseado na hierarquia das assinaturas"""
    # Verificar se tem assinatura de aprovação
    if escala.assinaturas.filter(tipo_assinatura='APROVACAO').exists():
        escala.status = 'aprovada'
    # Se não tem aprovação, verificar se tem revisão
    elif escala.assinaturas.filter(tipo_assinatura='REVISAO').exists():
        escala.status = 'em_revisao'
    # Se não tem nenhuma assinatura, manter como pendente
    else:
        escala.status = 'pendente'
    escala.save()


@login_required
def dados_assinatura_escala(request, pk):
    """Buscar dados da escala para assinatura via AJAX"""
    try:
        escala = get_object_or_404(EscalaServico, pk=pk)
        
        # Verificar permissões de assinatura
        tipo_assinatura = request.GET.get('tipo', 'APROVACAO')
        
        # Criar uma instância temporária para verificar permissões
        assinatura_temp = AssinaturaEscala(escala=escala)
        
        if tipo_assinatura == 'REVISAO':
            pode_assinar = assinatura_temp.pode_revisar(request.user)
        elif tipo_assinatura == 'APROVACAO':
            pode_assinar = assinatura_temp.pode_aprovar(request.user)
        else:
            pode_assinar = assinatura_temp.verificar_permissao_assinatura(request.user, tipo_assinatura)
        
        if not pode_assinar:
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para assinar esta escala com este tipo de assinatura.'
            })
        
        # Buscar funções do usuário
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True
        ).select_related('funcao_militar')
        
        funcoes_data = []
        for funcao in funcoes_usuario:
            funcoes_data.append({
                'id': funcao.id,
                'nome': str(funcao.funcao_militar),
                'publicacao': funcao.funcao_militar.publicacao
            })
        
        # Buscar assinaturas existentes ordenadas por data
        assinaturas = escala.assinaturas.all().order_by('data_assinatura')
        
        assinaturas_data = []
        for assinatura in assinaturas:
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
                'assinado_por': nome_completo,
                'data_assinatura': assinatura.data_assinatura.isoformat(),
                'funcao_assinatura': assinatura.funcao_assinatura,
                'observacoes': assinatura.observacoes
            })
        
        # Gerar códigos de verificação para o documento
        codigo_verificador = f"{escala.pk:08d}"
        codigo_crc = f"{hash(str(escala.pk)) % 0xFFFFFFF:07X}"
        
        return JsonResponse({
            'success': True,
            'escala': {
                'id': escala.pk,
                'data': escala.data.strftime('%d/%m/%Y'),
                'organizacao': escala.organizacao,
                'tipo_servico': escala.tipo_servico,
                'tipo_servico_display': escala.get_tipo_servico_display(),
                'status': escala.status,
                'status_display': escala.get_status_display(),
                'criado_por': escala.criado_por.get_full_name() if escala.criado_por else 'Sistema',
                'codigo_verificador': codigo_verificador,
                'codigo_crc': codigo_crc,
            },
            'assinaturas': assinaturas_data,
            'funcoes_usuario': funcoes_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def assinar_escala(request, pk):
    """Assinar escala"""
    try:
        escala = get_object_or_404(EscalaServico, pk=pk)
        
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'message': 'Método não permitido'
            })
        
        try:
            # Obter dados do formulário
            funcao_id = request.POST.get('funcao_id')
            tipo_assinatura = request.POST.get('tipo_assinatura', 'APROVACAO')
            observacoes = request.POST.get('observacoes', '')
            tipo_midia = request.POST.get('tipo_midia', 'ELETRONICA')
            
            # Verificar permissões de assinatura
            assinatura_temp = AssinaturaEscala(escala=escala)
            
            if tipo_assinatura == 'REVISAO':
                pode_assinar = assinatura_temp.pode_revisar(request.user)
            elif tipo_assinatura == 'APROVACAO':
                pode_assinar = assinatura_temp.pode_aprovar(request.user)
            else:
                pode_assinar = assinatura_temp.verificar_permissao_assinatura(request.user, tipo_assinatura)
            
            if not pode_assinar:
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para assinar esta escala com este tipo de assinatura.'
                })
            
            # Dados para assinatura eletrônica
            hash_documento = request.POST.get('hash_documento', '')
            timestamp = request.POST.get('timestamp', '')
            assinatura_digital = request.POST.get('assinatura_digital', '')
            certificado = request.POST.get('certificado', '')
            
            # Verificar se a função foi selecionada
            if not funcao_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Selecione uma função para assinar.'
                })
            
            try:
                funcao = UsuarioFuncaoMilitar.objects.get(
                    id=funcao_id,
                    usuario=request.user,
                    ativo=True
                )
                
                with transaction.atomic():
                    # Criar assinatura
                    assinatura_data = {
                        'escala': escala,
                        'assinado_por': request.user,
                        'funcao_assinatura': str(funcao.funcao_militar),
                        'tipo_assinatura': tipo_assinatura,
                        'observacoes': observacoes,
                        'tipo_midia': tipo_midia,
                    }
                    
                    # Adicionar dados específicos baseado no tipo de mídia
                    if tipo_midia == 'ELETRONICA':
                        if not all([hash_documento, timestamp, assinatura_digital]):
                            return JsonResponse({
                                'success': False,
                                'message': 'Dados de assinatura eletrônica incompletos.'
                            })
                        
                        assinatura_data.update({
                            'hash_documento': hash_documento,
                            'timestamp': timestamp,
                            'assinatura_digital': assinatura_digital,
                            'certificado': certificado or 'ASSINATURA_SIMPLES_SEI',
                            'ip_assinatura': request.META.get('REMOTE_ADDR', ''),
                            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        })
                    elif tipo_midia == 'FISICA':
                        # Para assinatura física, apenas salvar a imagem se fornecida
                        if 'assinatura_fisica' in request.FILES:
                            assinatura_data['assinatura_fisica'] = request.FILES['assinatura_fisica']
                    
                    # Criar a assinatura
                    assinatura = AssinaturaEscala.objects.create(**assinatura_data)
                    
                    # Atualizar status da escala
                    atualizar_status_escala(escala)
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Escala assinada como {assinatura.get_tipo_assinatura_display()} com sucesso!'
                    })
                    
            except UsuarioFuncaoMilitar.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Função selecionada não encontrada ou inativa.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao assinar escala: {str(e)}'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })
    
    # GET - mostrar formulário de assinatura
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        ativo=True
    ).select_related('funcao_militar')
    
    assinaturas = escala.assinaturas.all().order_by('data_assinatura')
    
    context = {
        'escala': escala,
        'funcoes_usuario': funcoes_usuario,
        'assinaturas': assinaturas,
    }
    
    return render(request, 'militares/assinaturas_escala.html', context)


@login_required
def verificar_assinaturas_escala(request, pk):
    """Verificar assinaturas de uma escala"""
    escala = get_object_or_404(EscalaServico, pk=pk)
    assinaturas = escala.assinaturas.all().order_by('data_assinatura')
    
    context = {
        'escala': escala,
        'assinaturas': assinaturas,
    }
    
    return render(request, 'militares/verificar_assinaturas_escala.html', context)
