#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views para assinaturas de notas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from .models import Publicacao, AssinaturaNota, UsuarioFuncaoMilitar
from .models import HistoricoDevolucaoNota


def atualizar_status_nota(nota):
    """Atualiza o status da nota baseado na hierarquia das assinaturas"""
    # Verificar se tem assinatura de edição (status mais recente)
    if nota.assinaturas.filter(tipo_assinatura='EDICAO').exists():
        nota.status = 'EM_EDICAO'
    # Se não tem edição, verificar se tem aprovação
    elif nota.assinaturas.filter(tipo_assinatura='APROVACAO').exists():
        nota.status = 'APROVADA'
    # Se não tem aprovação, verificar se tem revisão
    elif nota.assinaturas.filter(tipo_assinatura='REVISAO').exists():
        nota.status = 'REVISADA'
    # Se não tem nenhuma assinatura, manter como rascunho
    else:
        nota.status = 'RASCUNHO'
    nota.save()


@login_required
def dados_assinatura_nota(request, pk):
    """Buscar dados da nota para assinatura via AJAX"""
    try:
        nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
        print(f"DEBUG: Nota encontrada - ID: {nota.pk}, Título: {nota.titulo}")
        print(f"DEBUG: Conteúdo da nota: {nota.conteudo[:100] if nota.conteudo else 'VAZIO'}...")
        print(f"DEBUG: Tópicos da nota: {nota.topicos}")
        
        # Obter funções ativas do usuário
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user
        ).select_related('funcao_militar')
        
        funcoes_data = []
        for ufm in funcoes_usuario:
            funcoes_data.append({
                'nome': ufm.funcao_militar.nome,
                'ativo': ufm.ativo
            })
        
        # Obter assinaturas da nota e ordenar por hierarquia militar
        assinaturas = nota.assinaturas.all()
        
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
                'assinado_por': nome_completo,
                'data_assinatura': assinatura.data_assinatura.isoformat(),
                'funcao_assinatura': assinatura.funcao_assinatura,
                'observacoes': assinatura.observacoes
            })
        
        # Gerar códigos de verificação para o documento
        codigo_verificador = f"{nota.pk:08d}"
        codigo_crc = f"{hash(str(nota.pk)) % 0xFFFFFFF:07X}"
        
        return JsonResponse({
            'success': True,
            'nota': {
                'numero': nota.numero,
                'titulo': nota.titulo,
                'conteudo': nota.conteudo,
                'topicos': nota.topicos,
                'status': nota.status,
                'status_display': nota.get_status_display(),
                'criado_por': nota.criado_por.get_full_name(),
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
def assinar_nota_revisao(request, pk):
    """Assinar nota como revisor"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar permissão de revisão baseada na função militar (quem pode mais pode menos)
    from .permissoes_simples import obter_funcao_militar_ativa
    funcao_usuario = obter_funcao_militar_ativa(request.user)
    if not funcao_usuario or funcao_usuario.funcao_militar.publicacao in ['DIGITADOR', 'NENHUM']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sua função não tem permissão para revisar notas.'})
        messages.error(request, 'Sua função não tem permissão para revisar notas.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        
        # Verificar se já existe uma assinatura de revisão deste usuário
        assinatura_existente = AssinaturaNota.objects.filter(
            nota=nota,
            assinado_por=request.user,
            tipo_assinatura='REVISAO'
        ).first()
        
        if assinatura_existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você já assinou esta nota como Revisor.'})
            messages.error(request, 'Você já assinou esta nota como Revisor.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Validar função selecionada
        if not funcao_assinatura:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Por favor, selecione uma função para a assinatura.'})
            messages.error(request, 'Por favor, selecione uma função para a assinatura.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se o usuário tem a função selecionada ativa
        funcao_usuario_selecionada = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            funcao_militar__nome=funcao_assinatura,
            ativo=True
        ).first()
        
        if not funcao_usuario_selecionada:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você não tem permissão para usar a função selecionada.'})
            messages.error(request, 'Você não tem permissão para usar a função selecionada.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se a função tem permissão para revisar
        if funcao_usuario_selecionada.funcao_militar.publicacao in ['DIGITADOR', 'NENHUM']:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'A função selecionada não tem permissão para revisar notas.'})
            messages.error(request, 'A função selecionada não tem permissão para revisar notas.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Criar a assinatura
        assinatura = AssinaturaNota.objects.create(
            nota=nota,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura='REVISAO',
            funcao_assinatura=funcao_assinatura
        )
        
        # Atualizar status da nota baseado na hierarquia das assinaturas
        atualizar_status_nota(nota)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Nota assinada como Revisor com sucesso!'})
        
        messages.success(request, 'Nota assinada como Revisor com sucesso!')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    # Obter funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user
    ).select_related('funcao_militar')
    
    # Obter função atual do usuário
    funcao_atual = None
    funcao_ativa = funcoes_usuario.filter(ativo=True).first()
    if funcao_ativa:
        funcao_atual = funcao_ativa.funcao_militar.nome
    
    context = {
        'nota': nota,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
        'tipo_assinatura': 'REVISAO',
    }
    
    return render(request, 'militares/assinar_nota.html', context)


@login_required
def assinar_nota_aprovacao(request, pk):
    """Assinar nota como aprovador"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar permissão de aprovação baseada na função militar (quem pode mais pode menos)
    from .permissoes_simples import obter_funcao_militar_ativa
    funcao_usuario = obter_funcao_militar_ativa(request.user)
    if not funcao_usuario or funcao_usuario.funcao_militar.publicacao in ['REVISOR', 'DIGITADOR', 'NENHUM']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sua função não tem permissão para aprovar notas.'})
        messages.error(request, 'Sua função não tem permissão para aprovar notas.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        
        # Verificar se já existe uma assinatura de aprovação deste usuário
        assinatura_existente = AssinaturaNota.objects.filter(
            nota=nota,
            assinado_por=request.user,
            tipo_assinatura='APROVACAO'
        ).first()
        
        if assinatura_existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você já assinou esta nota como Aprovador.'})
            messages.error(request, 'Você já assinou esta nota como Aprovador.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Validar função selecionada
        if not funcao_assinatura:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Por favor, selecione uma função para a assinatura.'})
            messages.error(request, 'Por favor, selecione uma função para a assinatura.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se o usuário tem a função selecionada ativa
        funcao_usuario_selecionada = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            funcao_militar__nome=funcao_assinatura,
            ativo=True
        ).first()
        
        if not funcao_usuario_selecionada:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você não tem permissão para usar a função selecionada.'})
            messages.error(request, 'Você não tem permissão para usar a função selecionada.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se a função tem permissão para aprovar
        if funcao_usuario_selecionada.funcao_militar.publicacao in ['DIGITADOR', 'NENHUM']:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'A função selecionada não tem permissão para aprovar notas.'})
            messages.error(request, 'A função selecionada não tem permissão para aprovar notas.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Criar a assinatura
        assinatura = AssinaturaNota.objects.create(
            nota=nota,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura='APROVACAO',
            funcao_assinatura=funcao_assinatura
        )
        
        # Atualizar status da nota baseado na hierarquia das assinaturas
        atualizar_status_nota(nota)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Nota assinada como Aprovador com sucesso!'})
        
        messages.success(request, 'Nota assinada como Aprovador com sucesso!')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    # Obter funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user
    ).select_related('funcao_militar')
    
    # Obter função atual do usuário
    funcao_atual = None
    funcao_ativa = funcoes_usuario.filter(ativo=True).first()
    if funcao_ativa:
        funcao_atual = funcao_ativa.funcao_militar.nome
    
    context = {
        'nota': nota,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
        'tipo_assinatura': 'APROVACAO',
    }
    
    return render(request, 'militares/assinar_nota.html', context)


@login_required
def assinar_nota_edicao(request, pk):
    """Assinar nota como editor"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar permissão de edição baseada na função militar (quem pode mais pode menos)
    from .permissoes_simples import obter_funcao_militar_ativa
    funcao_usuario = obter_funcao_militar_ativa(request.user)
    if not funcao_usuario or funcao_usuario.funcao_militar.publicacao in ['APROVADOR', 'REVISOR', 'DIGITADOR', 'NENHUM']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sua função não tem permissão para editar notas.'})
        messages.error(request, 'Sua função não tem permissão para editar notas.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        
        # Verificar se já existe uma assinatura de edição deste usuário
        assinatura_existente = AssinaturaNota.objects.filter(
            nota=nota,
            assinado_por=request.user,
            tipo_assinatura='EDICAO'
        ).first()
        
        if assinatura_existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você já assinou esta nota como Editor.'})
            messages.error(request, 'Você já assinou esta nota como Editor.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Validar função selecionada
        if not funcao_assinatura:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Por favor, selecione uma função para a assinatura.'})
            messages.error(request, 'Por favor, selecione uma função para a assinatura.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se o usuário tem a função selecionada ativa
        funcao_usuario_selecionada = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            funcao_militar__nome=funcao_assinatura,
            ativo=True
        ).first()
        
        if not funcao_usuario_selecionada:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você não tem permissão para usar a função selecionada.'})
            messages.error(request, 'Você não tem permissão para usar a função selecionada.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se a função tem permissão para editar
        if funcao_usuario_selecionada.funcao_militar.publicacao not in ['EDITOR', 'EDITOR_ADJUNTO', 'EDITOR_GERAL']:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'A função selecionada não tem permissão para editar notas.'})
            messages.error(request, 'A função selecionada não tem permissão para editar notas.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        # Criar a assinatura
        assinatura = AssinaturaNota.objects.create(
            nota=nota,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura='EDICAO',
            funcao_assinatura=funcao_assinatura
        )
        
        # Atualizar status da nota baseado na hierarquia das assinaturas
        atualizar_status_nota(nota)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Nota assinada como Editor com sucesso!'})
        
        messages.success(request, 'Nota assinada como Editor com sucesso!')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    # Obter funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user
    ).select_related('funcao_militar')
    
    # Obter função atual do usuário
    funcao_atual = None
    funcao_ativa = funcoes_usuario.filter(ativo=True).first()
    if funcao_ativa:
        funcao_atual = funcao_ativa.funcao_militar.nome
    
    context = {
        'nota': nota,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
        'tipo_assinatura': 'EDICAO',
    }
    
    return render(request, 'militares/assinar_nota.html', context)


@login_required
def retirar_assinatura_nota(request, pk, assinatura_pk):
    """Retirar assinatura de uma nota"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    assinatura = get_object_or_404(AssinaturaNota, pk=assinatura_pk, nota=nota)
    
    # Verificar se o usuário pode retirar a assinatura (apenas o próprio assinante ou superusuário)
    if assinatura.assinado_por != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para retirar esta assinatura.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        tipo_assinatura = assinatura.tipo_assinatura
        assinatura.delete()
        
        # Atualizar status da nota baseado nas assinaturas restantes
        assinaturas_restantes = AssinaturaNota.objects.filter(nota=nota)
        
        if not assinaturas_restantes.exists():
            nota.status = 'RASCUNHO'
        elif assinaturas_restantes.filter(tipo_assinatura='APROVACAO').exists():
            nota.status = 'APROVADA'
        elif assinaturas_restantes.filter(tipo_assinatura='REVISAO').exists():
            nota.status = 'REVISADA'
        elif assinaturas_restantes.filter(tipo_assinatura='EDICAO').exists():
            nota.status = 'EM_EDICAO'
        
        nota.save()
        
        messages.success(request, f'Assinatura de {assinatura.get_tipo_assinatura_display()} retirada com sucesso!')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    context = {
        'nota': nota,
        'assinatura': assinatura,
    }
    
    return render(request, 'militares/retirar_assinatura_nota.html', context)


@login_required
def devolver_nota(request, pk):
    """Devolver nota removendo todas as assinaturas"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se a nota está em um boletim disponibilizado
    if nota.numero_boletim:
        from .models import Publicacao
        boletim = Publicacao.objects.filter(
            numero=nota.numero_boletim,
            tipo='BOLETIM_OSTENSIVO'
        ).first()
        
        if boletim and boletim.data_disponibilizacao:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.'
                }, status=403)
            messages.error(request, 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.')
            return redirect('militares:nota_detail', pk=nota.pk)
    
    # Verificar se o usuário tem permissão para devolver a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para devolver esta nota.'
            }, status=403)
        try:
            messages.error(request, 'Você não tem permissão para devolver esta nota.')
        except:
            pass  # Se o middleware de mensagens não estiver disponível
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_devolucao = request.POST.get('motivo_devolucao', '').strip()
        
        if not motivo_devolucao:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo da devolução é obrigatório.'
                })
            try:
                messages.error(request, 'Motivo da devolução é obrigatório.')
            except:
                pass  # Se o middleware de mensagens não estiver disponível
            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            with transaction.atomic():
                # Remover todas as assinaturas da nota
                assinaturas_removidas = AssinaturaNota.objects.filter(nota=nota).count()
                AssinaturaNota.objects.filter(nota=nota).delete()
                
                # Atualizar status da nota para RASCUNHO e remover do boletim
                nota.status = 'RASCUNHO'
                nota.numero_boletim = None  # Remover do boletim
                nota.editada_apos_devolucao = False  # Resetar flag de edição
                nota.save()
                
                # Salvar histórico da devolução
                HistoricoDevolucaoNota.objects.create(
                    nota=nota,
                    devolvido_por=request.user,
                    motivo_devolucao=motivo_devolucao,
                    assinaturas_removidas=assinaturas_removidas
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota devolvida com sucesso! {assinaturas_removidas} assinatura(s) removida(s).'
                })
            
            try:
                messages.success(request, f'Nota devolvida com sucesso! {assinaturas_removidas} assinatura(s) removida(s).')
            except:
                pass  # Se o middleware de mensagens não estiver disponível
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao devolver nota: {str(e)}'
                }, status=500)
            
            try:
                messages.error(request, f'Erro ao devolver nota: {str(e)}')
            except:
                pass  # Se o middleware de mensagens não estiver disponível
            return redirect('militares:nota_detail', pk=nota.pk)
    
    # Se não for POST, mostrar formulário
    context = {
        'nota': nota,
    }
    return render(request, 'militares/devolver_nota.html', context)


@login_required
def transferir_nota(request, pk):
    """Transferir nota de um boletim para outro"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se a nota está em um boletim disponibilizado
    if nota.numero_boletim:
        from .models import Publicacao
        boletim = Publicacao.objects.filter(
            numero=nota.numero_boletim,
            tipo='BOLETIM_OSTENSIVO'
        ).first()
        
        if boletim and boletim.data_disponibilizacao:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Esta nota não pode ser transferida pois o boletim já foi disponibilizado.'
                }, status=403)
            messages.error(request, 'Esta nota não pode ser transferida pois o boletim já foi disponibilizado.')
            return redirect('militares:nota_detail', pk=nota.pk)
    
    # Verificar se o usuário tem permissão para transferir a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para transferir esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para transferir esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        novo_boletim_id = request.POST.get('novo_boletim_id')
        motivo_transferencia = request.POST.get('motivo_transferencia', '').strip()
        
        if not novo_boletim_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Selecione um boletim de destino.'
                })
            messages.error(request, 'Selecione um boletim de destino.')
            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from datetime import date
            
            novo_boletim = Publicacao.objects.get(pk=novo_boletim_id, tipo='BOLETIM_OSTENSIVO')
            
            # VALIDAÇÃO CRÍTICA: Só permitir transferir para boletim do dia atual
            data_hoje = date.today()
            data_boletim_destino = novo_boletim.data_boletim if novo_boletim.data_boletim else novo_boletim.data_criacao.date()
            
            if data_boletim_destino != data_hoje:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Não é possível transferir notas para boletins de datas diferentes de hoje. Boletim de destino é de {data_boletim_destino.strftime("%d/%m/%Y")} e hoje é {data_hoje.strftime("%d/%m/%Y")}. As notas só podem ser transferidas para o boletim do dia atual.'
                    })
                try:
                    messages.error(request, f'Não é possível transferir notas para boletins de datas diferentes de hoje. Boletim de destino é de {data_boletim_destino.strftime("%d/%m/%Y")} e hoje é {data_hoje.strftime("%d/%m/%Y")}. As notas só podem ser transferidas para o boletim do dia atual.')
                except:
                    pass
                return redirect('militares:nota_detail', pk=nota.pk)
            
            with transaction.atomic():
                # Atualizar o número do boletim da nota
                nota.numero_boletim = novo_boletim.numero
                nota.save()
                
                # Registrar a transferência no histórico
                HistoricoDevolucaoNota.objects.create(
                    nota=nota,
                    devolvido_por=request.user,
                    motivo_devolucao=f'Transferida para boletim {novo_boletim.numero}. {motivo_transferencia}',
                    assinaturas_removidas=0
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota transferida com sucesso para o boletim {novo_boletim.numero}!'
                })
            
            messages.success(request, f'Nota transferida com sucesso para o boletim {novo_boletim.numero}!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Publicacao.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Boletim de destino não encontrado.'
                })
            messages.error(request, 'Boletim de destino não encontrado.')
            return redirect('militares:nota_detail', pk=nota.pk)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao transferir nota: {str(e)}'
                }, status=500)
    
    # Buscar boletins disponíveis para transferência
    boletins_disponiveis = Publicacao.objects.filter(
        tipo='BOLETIM_OSTENSIVO',
        status__in=['RASCUNHO', 'AGUARDANDO_APROVACAO']
    ).exclude(pk=nota.numero_boletim).order_by('-data_publicacao')
    
    context = {
        'nota': nota,
        'boletins_disponiveis': boletins_disponiveis,
    }
    
    return render(request, 'militares/transferir_nota.html', context)


@login_required
def editar_nota_modal(request, pk):
    """Editar nota via modal AJAX"""
    print(f"DEBUG: editar_nota_modal chamada - ID: {pk}, User: {request.user.username}, Method: {request.method}")
    print(f"DEBUG: Headers: {dict(request.headers)}")
    print(f"DEBUG: POST data: {dict(request.POST)}")
    
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    print(f"DEBUG: Nota encontrada - {nota.titulo}")
    
    # Verificar se o usuário tem permissão para editar a nota
    can_edit = nota.can_edit(request.user)
    print(f"DEBUG: Pode editar: {can_edit}")
    
    if not can_edit and not request.user.is_superuser:
        print(f"DEBUG: Usuário não tem permissão para editar")
        return JsonResponse({
            'success': False, 
            'error': 'Você não tem permissão para editar esta nota.'
        }, status=403)
    
    if request.method == 'POST':
        try:
            print(f"DEBUG: Editando nota ID {pk} - Usuário: {request.user.username}")
            print(f"DEBUG: Dados recebidos - Título: {request.POST.get('titulo')}")
            print(f"DEBUG: Dados recebidos - Origem: {request.POST.get('origem_publicacao')}")
            print(f"DEBUG: Dados recebidos - Tipo: {request.POST.get('tipo_publicacao')}")
            print(f"DEBUG: Dados recebidos - Tópicos: {request.POST.get('topicos')}")
            print(f"DEBUG: Dados recebidos - Conteúdo (primeiros 100 chars): {request.POST.get('conteudo', '')[:100]}...")
            
            # Atualizar campos da nota
            nota.titulo = request.POST.get('titulo', nota.titulo)
            nota.conteudo = request.POST.get('conteudo', nota.conteudo)
            nota.topicos = request.POST.get('topicos', nota.topicos)
            nota.origem_publicacao = request.POST.get('origem_publicacao', nota.origem_publicacao)
            nota.tipo_publicacao = request.POST.get('tipo_publicacao', nota.tipo_publicacao)
            
            print(f"DEBUG: Salvando nota atualizada - Título: {nota.titulo}")
            nota.save()
            print(f"DEBUG: Nota salva com sucesso!")
            
            # Atualizar conteúdo do boletim se a nota estiver publicada
            if nota.status == 'PUBLICADA' and nota.numero_boletim:
                print(f"DEBUG: Atualizando conteúdo do boletim {nota.numero_boletim}")
                from .models import Publicacao
                boletim = Publicacao.objects.filter(
                    tipo='BOLETIM_OSTENSIVO',
                    numero=nota.numero_boletim
                ).first()
                
                if boletim:
                    print(f"DEBUG: Boletim encontrado - {boletim.titulo}")
                    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
                    boletim.save(update_fields=['conteudo'])
                    print(f"DEBUG: Conteúdo do boletim atualizado com sucesso!")
                else:
                    print(f"DEBUG: Boletim {nota.numero_boletim} não encontrado")
            
            return JsonResponse({
                'success': True,
                'message': 'Nota editada com sucesso!'
            })
            
        except Exception as e:
            print(f"DEBUG: Erro ao editar nota: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Erro ao editar nota: {str(e)}'
            }, status=500)
    
    # Retornar dados da nota para o modal
    return JsonResponse({
        'success': True,
        'nota': {
            'id': nota.id,
            'titulo': nota.titulo,
            'conteudo': nota.conteudo,
            'topicos': nota.topicos,
            'origem_publicacao': nota.origem_publicacao,
            'tipo_publicacao': nota.tipo_publicacao,
            'numero': nota.numero,
        }
    })


def processar_formato_html(texto_html):
    """Processa formatação HTML para ReportLab mantendo formatação do CKEditor"""
    import re
    
    if not texto_html:
        return ""
    
    # Primeiro, limpar entidades HTML
    texto_html = texto_html.replace('&nbsp;', ' ')
    texto_html = texto_html.replace('&amp;', '&')
    texto_html = texto_html.replace('&lt;', '<')
    texto_html = texto_html.replace('&gt;', '>')
    texto_html = texto_html.replace('&quot;', '"')
    texto_html = texto_html.replace('&#39;', "'")
    
    # Converter parágrafos normais primeiro (sem alinhamento)
    texto_html = re.sub(r'<p(?!\s+[^>]*style="[^"]*text-align)[^>]*>(.*?)</p>', r'<para>\1</para>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<div(?!\s+[^>]*style="[^"]*text-align)[^>]*>(.*?)</div>', r'<para>\1</para>', texto_html, flags=re.DOTALL)
    
    # Agora converter os com alinhamento
    # Converter style="text-align: center" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</p>', r'<para align="center">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</div>', r'<para align="center">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    
    # Converter style="text-align: right" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</p>', r'<para align="right">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</div>', r'<para align="right">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    
    # Converter style="text-align: justify" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*justify[^"]*"[^>]*>(.*?)</p>', r'<para align="justify">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*justify[^"]*"[^>]*>(.*?)</div>', r'<para align="justify">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    
    # Converter tags de formatação para ReportLab
    # Negrito
    texto_html = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<b>(.*?)</b>', r'<b>\1</b>', texto_html, flags=re.DOTALL)
    
    # Itálico
    texto_html = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<i>(.*?)</i>', r'<i>\1</i>', texto_html, flags=re.DOTALL)
    
    # Sublinhado
    texto_html = re.sub(r'<u>(.*?)</u>', r'<u>\1</u>', texto_html, flags=re.DOTALL)
    
    # Títulos (h1, h2, h3, h4, h5, h6)
    texto_html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'<b><font size="16">\1</font></b><br/>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'<b><font size="14">\1</font></b><br/>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'<b><font size="13">\1</font></b><br/>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<h4[^>]*>(.*?)</h4>', r'<b><font size="12">\1</font></b><br/>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<h5[^>]*>(.*?)</h5>', r'<b><font size="11">\1</font></b><br/>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<h6[^>]*>(.*?)</h6>', r'<b><font size="10">\1</font></b><br/>', texto_html, flags=re.DOTALL)
    
    # Listas ordenadas e não ordenadas
    texto_html = re.sub(r'<ol[^>]*>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'</ol>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<ul[^>]*>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'</ul>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<li[^>]*>', '• ', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'</li>', '<br/>', texto_html, flags=re.DOTALL)
    
    # Converter parágrafos restantes que não foram convertidos
    texto_html = re.sub(r'<p[^>]*>(.*?)</p>', r'<para>\1</para>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<div[^>]*>(.*?)</div>', r'<para>\1</para>', texto_html, flags=re.DOTALL)
    
    # Quebras de linha
    texto_html = re.sub(r'<br\s*/?>', '<br/>', texto_html)
    
    # Links - manter apenas o texto
    texto_html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', texto_html, flags=re.DOTALL)
    
    # Código inline
    texto_html = re.sub(r'<code[^>]*>(.*?)</code>', r'<font name="Courier">\1</font>', texto_html, flags=re.DOTALL)
    
    # Pré-formatado
    texto_html = re.sub(r'<pre[^>]*>(.*?)</pre>', r'<font name="Courier">\1</font>', texto_html, flags=re.DOTALL)
    
    # Citações
    texto_html = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'<i>\1</i>', texto_html, flags=re.DOTALL)
    
    # Remover estilos inline (style="...")
    texto_html = re.sub(r'style="[^"]*"', '', texto_html)
    
    # Remover classes CSS
    texto_html = re.sub(r'class="[^"]*"', '', texto_html)
    
    # Remover outros atributos HTML
    texto_html = re.sub(r'\s+[a-zA-Z-]+="[^"]*"', '', texto_html)
    
    # Limpar tags vazias
    texto_html = re.sub(r'<[^>]*></[^>]*>', '', texto_html)
    
    # Remover apenas tags não suportadas pelo ReportLab, mantendo as de formatação
    # Manter tags de formatação do ReportLab: <b>, <i>, <u>, <br/>, <font>, <para>
    tags_para_manter = ['b', 'i', 'u', 'br', 'font', 'para']
    # Remover outras tags HTML
    texto_html = re.sub(r'<(?!/?(?:' + '|'.join(tags_para_manter) + r'))[^>]+>', '', texto_html)
    
    # Normalizar quebras de linha múltiplas
    texto_html = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', texto_html)
    
    # Limpar espaços em branco excessivos
    texto_html = re.sub(r'[ \t]+', ' ', texto_html)
    texto_html = re.sub(r'\n\s*\n', '\n\n', texto_html)
    
    return texto_html.strip()


def processar_formato_html_modal(texto_html):
    """Processa formatação HTML para ReportLab replicando exatamente o modal de visualização"""
    import re

    if not texto_html:
        return ""

    # Limpar entidades HTML
    texto_html = texto_html.replace('&nbsp;', ' ')
    texto_html = texto_html.replace('&amp;', '&')
    texto_html = texto_html.replace('&lt;', '<')
    texto_html = texto_html.replace('&gt;', '>')
    texto_html = texto_html.replace('&quot;', '"')
    texto_html = texto_html.replace('&#39;', "'")

    # Primeiro, converter todos os alinhamentos de texto para tags para
    # Converter style="text-align: center" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</p>', r'<para align="center">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</div>', r'<para align="center">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)

    # Converter style="text-align: right" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</p>', r'<para align="right">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</div>', r'<para align="right">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)

    # Converter style="text-align: justify" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*justify[^"]*"[^>]*>(.*?)</p>', r'<para align="justify">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*justify[^"]*"[^>]*>(.*?)</div>', r'<para align="justify">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)

    # Converter style="text-align: left" para tags de alinhamento
    texto_html = re.sub(r'<p[^>]*style="[^"]*text-align\s*:\s*left[^"]*"[^>]*>(.*?)</p>', r'<para align="left">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<div[^>]*style="[^"]*text-align\s*:\s*left[^"]*"[^>]*>(.*?)</div>', r'<para align="left">\1</para>', texto_html, flags=re.DOTALL | re.IGNORECASE)

    # Converter parágrafos normais (sem alinhamento) - apenas os que não foram convertidos acima
    texto_html = re.sub(r'<p(?!\s+[^>]*style="[^"]*text-align)[^>]*>(.*?)</p>', r'<para>\1</para>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<div(?!\s+[^>]*style="[^"]*text-align)[^>]*>(.*?)</div>', r'<para>\1</para>', texto_html, flags=re.DOTALL)

    # Converter tags de formatação para ReportLab
    # Negrito
    texto_html = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<b>(.*?)</b>', r'<b>\1</b>', texto_html, flags=re.DOTALL)

    # Itálico
    texto_html = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<i>(.*?)</i>', r'<i>\1</i>', texto_html, flags=re.DOTALL)

    # Sublinhado
    texto_html = re.sub(r'<u>(.*?)</u>', r'<u>\1</u>', texto_html, flags=re.DOTALL)

    # Títulos (h1, h2, h3, h4, h5, h6) - preservar alinhamento se houver
    texto_html = re.sub(r'<h1[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</h1>', r'<para align="center"><b><font size="16">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h1[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</h1>', r'<para align="right"><b><font size="16">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'<para><b><font size="16">\1</font></b></para>', texto_html, flags=re.DOTALL)
    
    texto_html = re.sub(r'<h2[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</h2>', r'<para align="center"><b><font size="14">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h2[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</h2>', r'<para align="right"><b><font size="14">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'<para><b><font size="14">\1</font></b></para>', texto_html, flags=re.DOTALL)
    
    texto_html = re.sub(r'<h3[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</h3>', r'<para align="center"><b><font size="13">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h3[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</h3>', r'<para align="right"><b><font size="13">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'<para><b><font size="13">\1</font></b></para>', texto_html, flags=re.DOTALL)
    
    texto_html = re.sub(r'<h4[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</h4>', r'<para align="center"><b><font size="12">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h4[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</h4>', r'<para align="right"><b><font size="12">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h4[^>]*>(.*?)</h4>', r'<para><b><font size="12">\1</font></b></para>', texto_html, flags=re.DOTALL)
    
    texto_html = re.sub(r'<h5[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</h5>', r'<para align="center"><b><font size="11">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h5[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</h5>', r'<para align="right"><b><font size="11">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h5[^>]*>(.*?)</h5>', r'<para><b><font size="11">\1</font></b></para>', texto_html, flags=re.DOTALL)
    
    texto_html = re.sub(r'<h6[^>]*style="[^"]*text-align\s*:\s*center[^"]*"[^>]*>(.*?)</h6>', r'<para align="center"><b><font size="10">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h6[^>]*style="[^"]*text-align\s*:\s*right[^"]*"[^>]*>(.*?)</h6>', r'<para align="right"><b><font size="10">\1</font></b></para>', texto_html, flags=re.DOTALL | re.IGNORECASE)
    texto_html = re.sub(r'<h6[^>]*>(.*?)</h6>', r'<para><b><font size="10">\1</font></b></para>', texto_html, flags=re.DOTALL)

    # Listas ordenadas e não ordenadas
    texto_html = re.sub(r'<ol[^>]*>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'</ol>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<ul[^>]*>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'</ul>', '', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'<li[^>]*>', '• ', texto_html, flags=re.DOTALL)
    texto_html = re.sub(r'</li>', '<br/>', texto_html, flags=re.DOTALL)

    # Quebras de linha
    texto_html = re.sub(r'<br\s*/?>', '<br/>', texto_html)

    # Links - manter apenas o texto
    texto_html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', texto_html, flags=re.DOTALL)

    # Código inline
    texto_html = re.sub(r'<code[^>]*>(.*?)</code>', r'<font name="Courier">\1</font>', texto_html, flags=re.DOTALL)

    # Pré-formatado
    texto_html = re.sub(r'<pre[^>]*>(.*?)</pre>', r'<font name="Courier">\1</font>', texto_html, flags=re.DOTALL)

    # Citações
    texto_html = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'<i>\1</i>', texto_html, flags=re.DOTALL)

    # Remover estilos inline (style="...") - mas preservar os que já foram convertidos
    texto_html = re.sub(r'style="[^"]*"', '', texto_html)

    # Remover classes CSS
    texto_html = re.sub(r'class="[^"]*"', '', texto_html)

    # Remover outros atributos HTML
    texto_html = re.sub(r'\s+[a-zA-Z-]+="[^"]*"', '', texto_html)

    # Limpar tags vazias
    texto_html = re.sub(r'<[^>]*></[^>]*>', '', texto_html)

    # Remover apenas tags não suportadas pelo ReportLab, mantendo as de formatação
    # Manter tags de formatação do ReportLab: <b>, <i>, <u>, <br/>, <font>, <para>
    tags_para_manter = ['b', 'i', 'u', 'br', 'font', 'para']
    # Remover outras tags HTML
    texto_html = re.sub(r'<(?!/?(?:' + '|'.join(tags_para_manter) + r'))[^>]+>', '', texto_html)

    # Normalizar quebras de linha múltiplas
    texto_html = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', texto_html)

    # Limpar espaços em branco excessivos
    texto_html = re.sub(r'[ \t]+', ' ', texto_html)
    texto_html = re.sub(r'\n\s*\n', '\n\n', texto_html)

    return texto_html.strip()

@login_required
def nota_gerar_pdf(request, pk):
    """Gera PDF da nota de serviço no modelo institucional"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from io import BytesIO
    import os
    import qrcode
    import locale
    from datetime import datetime

    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar formato padrão se não conseguir configurar

    try:
        nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        messages.error(request, f'Nota de serviço com ID {pk} não encontrada.')
        return redirect('militares:notas_list')

    buffer = BytesIO()
    
    # Obter assinaturas
    assinaturas = nota.assinaturas.all().order_by('-data_assinatura')
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=0.5*cm, bottomMargin=0.5*cm)
    styles = getSampleStyleSheet()

    # Estilos customizados seguindo ABNT - com espaçamento reduzido
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12, spaceAfter=3, spaceBefore=3)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, spaceAfter=3, spaceBefore=3)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=14, spaceAfter=6, spaceBefore=6, fontName='Helvetica-Bold')
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=12, spaceAfter=4, spaceBefore=4, fontName='Helvetica-Bold')
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=10, spaceAfter=2, spaceBefore=2)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=12, spaceAfter=3, spaceBefore=3, leading=12)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=11, spaceAfter=4, spaceBefore=4, leading=11)
    style_paragraph = ParagraphStyle('paragraph', parent=styles['Normal'], fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, alignment=4)

    story = []

    # Logo CBMEPI no topo
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2*cm, height=2*cm, hAlign='CENTER'))
        story.append(Spacer(1, 2))

    # Cabeçalho Oficial - replicando exatamente o modal
    story.append(Paragraph("ESTADO DO PIAUÍ", ParagraphStyle('estado', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("CORPO DE BOMBEIROS MILITAR DO PIAUÍ", ParagraphStyle('cbmepi', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
    
    # Processar hierarquia exatamente como no modal (usando organograma OU origem_publicacao)
    def expandir_siglas(texto):
        """Expandir siglas para nomes completos conforme organograma real"""
        siglas = {
            # Órgãos
            'CMDO GERAL': 'COMANDO GERAL',
            'COB': 'COMANDO OPERACIONAL DE BOMBEIROS',
            
            # Grandes Comandos
            'QCG': 'QUARTEL DO COMANDO GERAL',
            'CRBM-I': 'COMANDO REGIONAL DO MEIO-NORTE',
            'CRBM-II': 'COMANDO REGIONAL DO LITORAL',
            
            # Unidades
            'AJD GERAL': 'AJUDÂNCIA GERAL',
            'DGP': 'DIRETORIA DE GESTÃO DE PESSOAS',
            '1º GBM': '1º GRUPAMENTO DE BOMBEIROS MILITAR',
            '2º GBM': '2º GRUPAMENTO DE BOMBEIROS MILITAR',
            '3º GBM': '3º GRUPAMENTO DE BOMBEIROS MILITAR',
            
            # Siglas genéricas
            'GBM': 'GRUPAMENTO DE BOMBEIROS MILITAR',
            'SGBM': 'SUBGRUPAMENTO DE BOMBEIROS MILITAR',
            'GABCMDO': 'GABINETE DO COMANDO GERAL',
            'CBMEPI': 'CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ',
            'CBM': 'CORPO DE BOMBEIROS MILITAR'
        }
        
        texto_expandido = texto
        for sigla, nome_completo in siglas.items():
            import re
            regex = re.compile(r'\b' + re.escape(sigla) + r'\b', re.IGNORECASE)
            texto_expandido = regex.sub(nome_completo, texto_expandido)
        
        return texto_expandido
    
    def sao_equivalentes(str1, str2):
        """Verificar equivalências incluindo erros de digitação"""
        if not str1 or not str2:
            return False
        
        def normalizar(s):
            return s.lower().replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a').replace('ä', 'a') \
                          .replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e') \
                          .replace('í', 'i').replace('ì', 'i').replace('î', 'i').replace('ï', 'i') \
                          .replace('ó', 'o').replace('ò', 'o').replace('ô', 'o').replace('õ', 'o').replace('ö', 'o') \
                          .replace('ú', 'u').replace('ù', 'u').replace('û', 'u').replace('ü', 'u') \
                          .replace('ç', 'c').replace(' ', '').replace('-', '').replace('/', '')
        
        str1_norm = normalizar(str1)
        str2_norm = normalizar(str2)
        
        if str1_norm == str2_norm:
            return True
        
        equivalencias = [
            ['gabinetedocomandogeral', 'gabcmdo'],
            ['quarteldocomandogeral', 'qcg'],
            ['comandogeral', 'cmdogeral']
        ]
        
        for eq1, eq2 in equivalencias:
            if (eq1 in str1_norm and eq2 in str2_norm) or (eq2 in str1_norm and eq1 in str2_norm):
                return True
        
        return False
    
    # Usar origem da publicação expandida (igual à coluna Origem da listagem) - uma linha por parte
    print(f"DEBUG PDF: Usando origem_publicacao expandida")
    if nota.origem_publicacao and nota.origem_publicacao != '-':
        print(f"DEBUG PDF: Origem original: {nota.origem_publicacao}")
        
        # Dividir por ' - ' para processar cada parte
        partes = nota.origem_publicacao.split(' - ')
        print(f"DEBUG PDF: Partes da origem: {partes}")
        
        # Lista para controlar duplicações
        partes_adicionadas = []
        
        for parte in partes:
            parte = parte.strip()
            print(f"DEBUG PDF: Processando parte: '{parte}'")
            
            # Ignorar partes que contenham "do" ou "da" (versões por extenso como "1º Subgrupamento do 3º Grupamento")
            if ' do ' in parte.lower() or ' da ' in parte.lower():
                print(f"DEBUG PDF: Parte contém 'do'/'da' (versão por extenso) - ignorando: '{parte}'")
                continue
            
            # Se contém "/", processar separadamente
            if '/' in parte:
                print(f"DEBUG PDF: Parte contém '/' - processando barra")
                partes_barra = parte.split('/')
                if len(partes_barra) >= 2:
                    # Expandir unidade (parte após a barra)
                    unidade_texto = partes_barra[1].strip()
                    unidade_nome = expandir_siglas(unidade_texto)
                    print(f"DEBUG PDF: Unidade expandida: '{unidade_nome}'")
                    
                    # Expandir subunidade (parte antes da barra)
                    subunidade_texto = partes_barra[0].strip()
                    subunidade_nome = expandir_siglas(subunidade_texto)
                    print(f"DEBUG PDF: Subunidade expandida: '{subunidade_nome}'")
                    
                    # Verificar se a unidade já foi adicionada anteriormente
                    unidade_ja_existe = False
                    for parte_existente in partes_adicionadas:
                        if unidade_nome in parte_existente or parte_existente in unidade_nome:
                            unidade_ja_existe = True
                            print(f"DEBUG PDF: Unidade já existe: '{unidade_nome}' - não adicionando")
                            break
                    
                    # Adicionar unidade apenas se não existir
                    if not unidade_ja_existe:
                        story.append(Paragraph(unidade_nome, ParagraphStyle('origem', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
                        partes_adicionadas.append(unidade_nome)
                        print(f"DEBUG PDF: Adicionando unidade: {unidade_nome}")
                    
                    # Adicionar subunidade
                    story.append(Paragraph(subunidade_nome, ParagraphStyle('origem', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
                    partes_adicionadas.append(subunidade_nome)
                    print(f"DEBUG PDF: Adicionando subunidade: {subunidade_nome}")
                else:
                    # Se só tem uma parte após a barra, expandir ela
                    nome_completo = expandir_siglas(partes_barra[0].strip())
                    story.append(Paragraph(nome_completo, ParagraphStyle('origem', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
                    partes_adicionadas.append(nome_completo)
                    print(f"DEBUG PDF: Adicionando parte única: {nome_completo}")
            else:
                # Processar normalmente
                nome_completo = expandir_siglas(parte)
                story.append(Paragraph(nome_completo, ParagraphStyle('origem', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
                partes_adicionadas.append(nome_completo)
                print(f"DEBUG PDF: Adicionando parte normal: {nome_completo}")
        
        print(f"DEBUG PDF: Todas as partes da origem foram adicionadas ao PDF")
    else:
        # Cabeçalho padrão se não houver origem
        story.append(Paragraph("QUARTEL DO COMANDO GERAL", ParagraphStyle('origem', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
        story.append(Paragraph("AJUDÂNCIA GERAL", ParagraphStyle('origem', parent=styles['Normal'], alignment=1, fontSize=10, fontName='Helvetica-Bold', spaceAfter=1, spaceBefore=1)))
        print(f"DEBUG PDF: Cabeçalho padrão adicionado ao PDF")
    
    # Linha separadora - reduzindo espaçamento para caber em uma página
    story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=colors.black))
    story.append(Spacer(1, 8))  # Reduzido de 20pt para 8pt
    
    # Número da Nota - replicando exatamente o modal
    story.append(Paragraph(f"NOTA N° {nota.numero}", ParagraphStyle('numero', parent=styles['Normal'], alignment=1, fontSize=12, fontName='Helvetica-Bold', spaceAfter=3, spaceBefore=0)))
    
    # Título da Nota - reduzindo espaçamento para caber em uma página
    story.append(Paragraph(nota.titulo.upper(), ParagraphStyle('titulo', parent=styles['Normal'], alignment=1, fontSize=12, fontName='Helvetica-Bold', spaceAfter=12, spaceBefore=0)))  # Reduzido de 24pt para 12pt

    # Conteúdo da nota (replicando exatamente o modal de visualização)
    if nota.conteudo:
        import re
        
        # Usar o HTML original como no modal, sem processamento
        conteudo_html = nota.conteudo
        
        if not conteudo_html:
            conteudo_html = "Conteúdo não disponível."
        
        # Processar HTML para ReportLab mantendo formatação original do CKEditor
        conteudo_processado = processar_formato_html_modal(conteudo_html)
        
        # Dividir o conteúdo em parágrafos individuais para preservar alinhamento
        paragrafos = conteudo_processado.split('</para>')
        
        for paragrafo in paragrafos:
            if paragrafo.strip():
                # Adicionar tag de fechamento se foi removida pelo split
                if not paragrafo.strip().endswith('>'):
                    paragrafo = paragrafo.strip() + '</para>'
                
                # Determinar alinhamento baseado na tag para
                if 'align="center"' in paragrafo:
                    alignment = 1  # CENTER
                elif 'align="right"' in paragrafo:
                    alignment = 2  # RIGHT
                elif 'align="justify"' in paragrafo:
                    alignment = 4  # JUSTIFY
                else:
                    alignment = 0  # LEFT
                
                # Remover tags para para processamento
                paragrafo_limpo = re.sub(r'<para[^>]*>', '', paragrafo)
                paragrafo_limpo = re.sub(r'</para>', '', paragrafo_limpo)
                
                if paragrafo_limpo.strip():
                    story.append(Paragraph(paragrafo_limpo, ParagraphStyle('conteudo_nota', parent=styles['Normal'], fontSize=12, spaceAfter=6, spaceBefore=0, leading=14, alignment=alignment, leftIndent=0, rightIndent=0, fontName='Times-Roman')))

    # Cidade e Data por extenso (centralizada)
    story.append(Spacer(1, 20))
    
    # Função para converter data para extenso
    def data_por_extenso(data):
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        return f"{data.day} de {meses[data.month]} de {data.year}"
    
    # Data atual para o documento
    from django.utils import timezone
    data_atual = timezone.now().date()
    data_extenso = f"Teresina, {data_por_extenso(data_atual)}"
    
    # Adicionar cidade e data centralizada
    story.append(Paragraph(data_extenso, ParagraphStyle('DataExtenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Times-Roman', spaceAfter=12)))
    
    # Adicionar espaço reduzido abaixo da data para assinatura física
    story.append(Spacer(1, 0.5*cm))  # 0.5cm de espaço

    # Adicionar assinaturas ordenadas por hierarquia militar
    print(f"DEBUG: Total de assinaturas encontradas: {len(assinaturas) if assinaturas else 0}")
    if assinaturas:
        print(f"DEBUG: Processando {len(assinaturas)} assinaturas para PDF")
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
        
        # Adicionar até 3 assinaturas físicas em ordem hierárquica
        print(f"DEBUG: Adicionando {min(3, len(assinaturas_ordenadas))} assinaturas físicas")
        for i, assinatura in enumerate(assinaturas_ordenadas[:3]):  # Máximo 3 assinaturas
            print(f"DEBUG: Processando assinatura física {i+1}: {assinatura.assinado_por.get_full_name() if hasattr(assinatura.assinado_por, 'get_full_name') else 'N/A'}")
            # Nome e posto
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{militar.nome_completo} - {posto}"
            else:
                nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            
            # Função
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            # Adicionar assinatura física - seguindo o molde dos quadros de acesso
            print(f"DEBUG: Adicionando assinatura física: {nome_completo} - {funcao}")
            
            # Tipo de assinatura
            tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
            
            # Exibir no formato físico: Nome - Posto BM (negrito), Função (normal), Tipo (negrito menor)
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>{nome_completo}</b>", ParagraphStyle('Assinante', parent=styles['Normal'], alignment=1, fontSize=11, spaceAfter=4, fontName='Times-Roman')))
            story.append(Paragraph(f"{funcao}", ParagraphStyle('Funcao', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=4, fontName='Times-Roman')))
            story.append(Paragraph(f"<b>{tipo}</b>", ParagraphStyle('TipoAssinatura', parent=styles['Normal'], alignment=1, fontSize=9, spaceAfter=8, fontName='Times-Roman')))
        
        # Adicionar TODAS as assinaturas como eletrônicas (incluindo as primeiras 3 se houver mais de 3)
        if len(assinaturas_ordenadas) > 0:
            story.append(Spacer(1, 1*cm))  # Espaço antes das assinaturas eletrônicas
            
            for assinatura in assinaturas_ordenadas:  # TODAS as assinaturas
                # Nome e posto - seguir o mesmo padrão dos outros PDFs
                if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                    militar = assinatura.assinado_por.militar
                    posto = militar.get_posto_graduacao_display()
                    # Adicionar BM após o posto se não já estiver presente
                    if "BM" not in posto:
                        posto = f"{posto} BM"
                    nome_completo = f"{militar.nome_completo} - {posto}"
                else:
                    nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                
                # Função
                funcao = assinatura.funcao_assinatura or "Função não registrada"
                
                # Formatar data e hora
                data_formatada = assinatura.data_assinatura.strftime('%d/%m/%Y')
                hora_formatada = assinatura.data_assinatura.strftime('%H:%M')
                
                # Texto da assinatura
                texto_assinatura = f"Documento assinado eletronicamente por {nome_completo} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025."
                
                # Adicionar logo da assinatura eletrônica
                from .utils import obter_caminho_assinatura_eletronica
                logo_assinatura_path = obter_caminho_assinatura_eletronica()
                
                # Tabela das assinaturas: Logo + Texto de assinatura
                assinatura_data = [
                    [Image(logo_assinatura_path, width=1.8*cm, height=1.2*cm), Paragraph(texto_assinatura, ParagraphStyle('assinatura_texto', parent=styles['Normal'], fontSize=9, spaceAfter=1, spaceBefore=1, leading=8, alignment=4))]
                ]
                
                assinatura_table = Table(assinatura_data, colWidths=[2.5*cm, 13.5*cm])
                assinatura_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 1),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(assinatura_table)
                # Espaçamento mínimo entre assinaturas eletrônicas
                story.append(Spacer(1, 0.2*cm))  # Espaçamento bem curto
    else:
        # Quando não há assinaturas eletrônicas, adicionar espaço para assinatura física
        print("DEBUG: Nenhuma assinatura eletrônica encontrada - adicionando espaço para assinatura física")
        story.append(Spacer(1, 2*cm))  # Espaço para assinatura física manual
        
        # Adicionar linha para assinatura física
        story.append(Paragraph("_" * 50, ParagraphStyle('linha_assinatura', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=0.5*cm, fontName='Times-Roman')))
        story.append(Paragraph("Assinatura Física", ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=1*cm, fontName='Times-Roman')))
        
        # Sem espaçamento entre assinaturas e autenticador

    # Adicionar identificador de veracidade do documento
    from .utils import adicionar_autenticador_pdf
    adicionar_autenticador_pdf(story, nota, request, tipo_documento='nota')

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="nota_{nota.numero}.pdf"'
    return response


@login_required
def dados_devolucao_nota(request, pk):
    """Buscar dados da devolução de uma nota via AJAX"""
    print(f"DEBUG: dados_devolucao_nota chamada - ID: {pk}, User: {request.user.username}")
    
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    print(f"DEBUG: Nota encontrada - {nota.titulo}")
    
    # Verificar se o usuário pode visualizar a nota
    can_view = True
    if nota.status != 'PUBLICADA':
        if not nota.can_edit(request.user) and not request.user.is_superuser:
            can_view = False
    
    print(f"DEBUG: Pode visualizar: {can_view}")
    
    if not can_view:
        return JsonResponse({
            'success': False,
            'error': 'Você não tem permissão para visualizar esta nota'
        }, status=403)
    
    try:
        # Buscar a devolução mais recente
        devolucao = HistoricoDevolucaoNota.objects.filter(nota=nota).first()
        print(f"DEBUG: Devolução encontrada: {devolucao}")
        
        if not devolucao:
            print("DEBUG: Nenhuma devolução encontrada")
            return JsonResponse({
                'success': False,
                'error': 'Nenhuma devolução encontrada para esta nota'
            })
        
        print(f"DEBUG: Motivo da devolução: {devolucao.motivo_devolucao}")
        
        return JsonResponse({
            'success': True,
            'devolucao': {
                'motivo': devolucao.motivo_devolucao,
                'devolvido_por': devolucao.devolvido_por.get_full_name(),
                'data_devolucao': devolucao.data_devolucao.strftime('%d/%m/%Y às %H:%M'),
                'assinaturas_removidas': devolucao.assinaturas_removidas
            }
        })
        
    except Exception as e:
        print(f"DEBUG: Erro ao buscar devolução: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao buscar dados da devolução: {str(e)}'
        }, status=500)
