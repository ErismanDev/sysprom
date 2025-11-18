"""
Views para Requisições de Almoxarifado
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string

from .models import (
    RequisicaoAlmoxarifado,
    ProdutoAlmoxarifado,
    RequisicaoAlmoxarifadoProduto,
    HistoricoRequisicaoAlmoxarifado
)
from decimal import Decimal
from .forms import RequisicaoAlmoxarifadoForm
from .permissoes_sistema import tem_permissao
from .permissoes_militares import obter_sessao_ativa_usuario


class RequisicaoAlmoxarifadoListView(LoginRequiredMixin, ListView):
    model = RequisicaoAlmoxarifado
    template_name = 'militares/requisicao_almoxarifado_list.html'
    context_object_name = 'requisicoes'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
            messages.error(request, "Você não tem permissão para visualizar requisições.")
            return redirect('militares:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Começar com um queryset base
        queryset = RequisicaoAlmoxarifado.objects.filter(ativo=True)
        
        # Filtros
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')
        item_id = self.request.GET.get('item', '')
        tipo = self.request.GET.get('tipo', '')  # 'enviadas' ou 'recebidas'
        
        if search:
            queryset = queryset.filter(
                Q(produto__codigo__icontains=search) |
                Q(produto__descricao__icontains=search) |
                Q(produtos_requisicao__produto__codigo__icontains=search) |
                Q(produtos_requisicao__produto__descricao__icontains=search) |
                Q(observacoes__icontains=search)
            ).distinct()
        
        if status:
            queryset = queryset.filter(status=status)
        
        if item_id:
            queryset = queryset.filter(
                Q(produto_id=item_id) | Q(produtos_requisicao__produto_id=item_id)
            ).distinct()
        
        # Filtrar por requisições enviadas ou recebidas
        if tipo:
            funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
            if funcao_usuario and funcao_usuario.funcao_militar_usuario:
                funcao = funcao_usuario.funcao_militar_usuario
                
                if tipo == 'enviadas':
                    # Requisições criadas pela OM do usuário
                    queryset = queryset.filter(
                        Q(unidade_requisitante=funcao.unidade) |
                        Q(sub_unidade_requisitante=funcao.sub_unidade) |
                        Q(grande_comando_requisitante=funcao.grande_comando) |
                        Q(orgao_requisitante=funcao.orgao)
                    )
                elif tipo == 'recebidas':
                    # Requisições recebidas pela OM do usuário
                    queryset = queryset.filter(
                        Q(unidade_requisitada=funcao.unidade) |
                        Q(sub_unidade_requisitada=funcao.sub_unidade) |
                        Q(grande_comando_requisitada=funcao.grande_comando) |
                        Q(orgao_requisitada=funcao.orgao)
                    )
        
        # Obter IDs únicos primeiro para evitar duplicatas causadas por múltiplos filtros OR
        # Isso é necessário porque quando há múltiplos filtros Q() com OR, o distinct() pode não funcionar corretamente
        ids_unicos = list(queryset.values_list('id', flat=True).distinct())
        
        # Agora buscar os objetos completos com select_related usando os IDs únicos
        queryset = RequisicaoAlmoxarifado.objects.filter(
            id__in=ids_unicos
        ).select_related(
            'produto', 'criado_por', 'aprovado_por',
            'orgao_requisitante', 'grande_comando_requisitante', 'unidade_requisitante', 'sub_unidade_requisitante',
            'orgao_requisitada', 'grande_comando_requisitada', 'unidade_requisitada', 'sub_unidade_requisitada'
        ).prefetch_related(
            Prefetch(
                'produtos_requisicao',
                queryset=RequisicaoAlmoxarifadoProduto.objects.select_related('produto')
            )
        ).order_by('-data_requisicao', '-data_criacao')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['item_id'] = self.request.GET.get('item', '')
        context['tipo'] = self.request.GET.get('tipo', '')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_requisicoes'] = queryset.count()
        context['requisicoes_pendentes'] = queryset.filter(status='PENDENTE').count()
        context['requisicoes_aprovadas'] = queryset.filter(status='APROVADA').count()
        context['requisicoes_negadas'] = queryset.filter(status='NEGADA').count()
        context['requisicoes_atendidas'] = queryset.filter(status='ATENDIDA').count()
        
        # Itens para filtro
        context['itens'] = ProdutoAlmoxarifado.objects.filter(ativo=True).order_by('codigo')
        
        # Permissões
        context['pode_criar'] = tem_permissao(self.request.user, 'ALMOXARIFADO', 'CRIAR')
        context['pode_editar'] = tem_permissao(self.request.user, 'ALMOXARIFADO', 'EDITAR')
        context['pode_excluir'] = tem_permissao(self.request.user, 'ALMOXARIFADO', 'EXCLUIR')
        
        # Garantir que o queryset de requisicoes não tenha duplicatas ANTES de processar permissões
        # Converter para lista e remover duplicatas por ID
        if 'requisicoes' in context:
            requisicoes_unicas = []
            ids_vistos = set()
            for requisicao in context['requisicoes']:
                if requisicao.pk not in ids_vistos:
                    requisicoes_unicas.append(requisicao)
                    ids_vistos.add(requisicao.pk)
            context['requisicoes'] = requisicoes_unicas
        
        # Adicionar informações sobre quais requisições podem ser aprovadas/editadas/excluídas/confirmadas pelo usuário atual
        # Agora processar permissões apenas para requisições únicas
        requisicoes_com_permissao = {}
        requisicoes_pode_excluir = {}
        requisicoes_pode_editar = {}
        requisicoes_pode_confirmar = {}
        
        for requisicao in context['requisicoes']:
            pode_aprovar = requisicao.pode_aprovar(self.request.user)
            pode_excluir = requisicao.pode_excluir(self.request.user)
            pode_editar = requisicao.pode_editar(self.request.user)
            pode_confirmar = requisicao.pode_confirmar_recebimento(self.request.user)
            requisicoes_com_permissao[requisicao.pk] = pode_aprovar
            requisicoes_pode_excluir[requisicao.pk] = pode_excluir
            requisicoes_pode_editar[requisicao.pk] = pode_editar
            requisicoes_pode_confirmar[requisicao.pk] = pode_confirmar
        
        context['requisicoes_pode_aprovar'] = requisicoes_com_permissao
        context['requisicoes_pode_excluir'] = requisicoes_pode_excluir
        context['requisicoes_pode_editar'] = requisicoes_pode_editar
        context['requisicoes_pode_confirmar'] = requisicoes_pode_confirmar
        
        return context


@login_required
def requisicao_almoxarifado_create(request):
    """
    Cria uma nova requisição via modal.
    IMPORTANTE: Cria APENAS UMA requisição com TODOS os produtos.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'CRIAR'):
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
        messages.error(request, "Você não tem permissão para criar requisições.")
        return redirect('militares:requisicao_almoxarifado_list')

    if request.method == 'POST':
        from django.db import transaction
        from .models import RequisicaoAlmoxarifadoProduto, ProdutoAlmoxarifado
        import json
        import logging
        import traceback
        from django.utils import timezone
        from datetime import timedelta
        
        logger = logging.getLogger(__name__)
        
        try:
            # 1. Validar formulário
            try:
                form = RequisicaoAlmoxarifadoForm(request.POST, request=request)
            except Exception as e:
                logger.error(f'Erro ao criar formulário: {str(e)}\n{traceback.format_exc()}')
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao processar formulário: {str(e)}'
                    }, status=400)
                messages.error(request, f'Erro ao processar formulário: {str(e)}')
                return redirect('militares:requisicao_almoxarifado_list')
            
            if not form.is_valid():
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(e) for e in error_list]
                
                error_messages = []
                for field, field_errors in errors.items():
                    for error in field_errors:
                        error_messages.append(f'{field}: {error}')
                
                error_message = 'Erro de validação'
                if error_messages:
                    error_message += ': ' + '; '.join(error_messages[:3])
                
                logger.warning(f'Formulário inválido: {error_message}')
                logger.warning(f'Erros detalhados: {errors}')
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': error_message,
                        'errors': errors
                    }, status=400)
                messages.error(request, error_message)
                return redirect('militares:requisicao_almoxarifado_list')
            
            # 2. Validar que há itens_data
            itens_data = request.POST.get('itens_data')
            if not itens_data:
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'É necessário adicionar pelo menos um item à requisição.'
                    }, status=400)
                messages.error(request, 'É necessário adicionar pelo menos um item à requisição.')
                return redirect('militares:requisicao_almoxarifado_list')
            
            # 3. Parse dos itens
            try:
                itens_list = json.loads(itens_data)
            except json.JSONDecodeError as e:
                logger.error(f'Erro ao fazer parse de itens_data: {str(e)}')
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao processar dados dos itens: {str(e)}'
                    }, status=400)
                messages.error(request, f'Erro ao processar dados dos itens: {str(e)}')
                return redirect('militares:requisicao_almoxarifado_list')
            
            if not itens_list or not isinstance(itens_list, list) or len(itens_list) == 0:
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'É necessário adicionar pelo menos um item à requisição.'
                    }, status=400)
                messages.error(request, 'É necessário adicionar pelo menos um item à requisição.')
                return redirect('militares:requisicao_almoxarifado_list')
            
            # 4. Verificar duplicatas (proteção contra múltiplos envios)
            agora = timezone.now()
            cinco_segundos_atras = agora - timedelta(seconds=5)
            
            primeira_requisicao_recente = RequisicaoAlmoxarifado.objects.filter(
                criado_por=request.user,
                data_requisicao__gte=cinco_segundos_atras,
                status='PENDENTE',
                orgao_requisitante=form.cleaned_data.get('orgao_requisitante'),
                grande_comando_requisitante=form.cleaned_data.get('grande_comando_requisitante'),
                unidade_requisitante=form.cleaned_data.get('unidade_requisitante'),
                sub_unidade_requisitante=form.cleaned_data.get('sub_unidade_requisitante'),
                orgao_requisitada=form.cleaned_data.get('orgao_requisitada'),
                grande_comando_requisitada=form.cleaned_data.get('grande_comando_requisitada'),
                unidade_requisitada=form.cleaned_data.get('unidade_requisitada'),
                sub_unidade_requisitada=form.cleaned_data.get('sub_unidade_requisitada'),
            ).first()
            
            if primeira_requisicao_recente:
                # Verificar se os produtos são os mesmos
                produtos_recentes = sorted(list(primeira_requisicao_recente.produtos_requisicao.values_list('produto_id', 'quantidade')))
                produtos_novos = sorted([(int(item_data.get('item_id')), float(item_data.get('quantidade', 0))) for item_data in itens_list if item_data.get('item_id')])
                
                if produtos_recentes == produtos_novos:
                    logger.warning(f'Requisição duplicada detectada! Retornando requisição #{primeira_requisicao_recente.pk}')
                    if is_ajax:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Requisição criada com sucesso!',
                            'redirect': reverse('militares:requisicao_almoxarifado_list')
                        })
                    messages.success(request, 'Requisição criada com sucesso!')
                    return redirect('militares:requisicao_almoxarifado_list')
            
            # 5. CRIAR UMA ÚNICA REQUISIÇÃO COM TODOS OS PRODUTOS
            with transaction.atomic():
                logger.info(f'=== CRIANDO UMA ÚNICA REQUISIÇÃO COM {len(itens_list)} PRODUTOS ===')
                logger.info(f'Usuário: {request.user.username}')
                logger.info(f'Itens recebidos: {itens_list}')
                
                # Criar a requisição (UMA ÚNICA VEZ)
                requisicao = form.save(commit=False)
                requisicao.status = 'PENDENTE'
                requisicao.quantidade = None  # Não usar campo legado
                requisicao.produto = None  # Não usar campo legado
                requisicao.criado_por = request.user
                
                # Salvar a requisição (isso pode criar assinatura automaticamente)
                requisicao.save()
                logger.info(f'✓ Requisição #{requisicao.pk} criada')
                
                # Adicionar TODOS os produtos à MESMA requisição
                produtos_adicionados = []
                itens_validos = 0
                
                for item_data in itens_list:
                    item_id = item_data.get('item_id')
                    quantidade = item_data.get('quantidade', 0)
                    
                    if not item_id:
                        logger.warning(f'Item ignorado: sem item_id')
                        continue
                    
                    try:
                        quantidade = float(quantidade)
                    except (ValueError, TypeError):
                        logger.warning(f'Item ignorado: quantidade inválida ({quantidade})')
                        continue
                    
                    if quantidade <= 0:
                        logger.warning(f'Item ignorado: quantidade <= 0 ({quantidade})')
                        continue
                    
                    try:
                        produto = ProdutoAlmoxarifado.objects.get(pk=item_id, ativo=True)
                    except ProdutoAlmoxarifado.DoesNotExist:
                        logger.error(f'Produto com ID {item_id} não encontrado')
                        raise ValueError(f'Produto com ID {item_id} não encontrado.')
                    
                    # Criar RequisicaoAlmoxarifadoProduto (ligando produto à requisição)
                    RequisicaoAlmoxarifadoProduto.objects.create(
                        requisicao=requisicao,  # MESMA requisição para todos
                        produto=produto,
                        quantidade=quantidade
                    )
                    
                    produtos_adicionados.append(f'{produto.codigo} (qtd: {quantidade})')
                    itens_validos += 1
                    logger.info(f'✓ Produto {produto.codigo} (ID: {item_id}) adicionado à requisição #{requisicao.pk}')
                
                # Validar que pelo menos um produto foi adicionado
                if itens_validos == 0:
                    # Se não adicionou nenhum produto, excluir a requisição criada
                    requisicao.delete()
                    raise ValueError('Nenhum produto válido foi adicionado à requisição.')
                
                logger.info(f'=== REQUISIÇÃO #{requisicao.pk} FINALIZADA COM {itens_validos} PRODUTOS ===')
                logger.info(f'Produtos adicionados: {", ".join(produtos_adicionados)}')
                
                # Registrar histórico de criação (dentro da transação)
                try:
                    HistoricoRequisicaoAlmoxarifado.objects.create(
                        requisicao=requisicao,
                        tipo_acao='CRIACAO',
                        alterado_por=request.user,
                        observacoes=f'Requisição criada com {itens_validos} produto(s): {", ".join(produtos_adicionados)}'
                    )
                    logger.info(f'✓ Histórico de criação registrado para requisição #{requisicao.pk}')
                except Exception as e:
                    logger.error(f'Erro ao registrar histórico de criação: {str(e)}')
                    # Não re-raise para não interromper o fluxo
            
            # 6. Retornar sucesso
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': f'Requisição #{requisicao.pk} criada com sucesso com {itens_validos} produto(s)!',
                    'redirect': reverse('militares:requisicao_almoxarifado_list')
                })
            messages.success(request, f'Requisição #{requisicao.pk} criada com sucesso com {itens_validos} produto(s)!')
            return redirect('militares:requisicao_almoxarifado_list')
            
        except json.JSONDecodeError as e:
            logger.error(f'Erro JSON: {str(e)}')
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao processar dados dos itens: {str(e)}'
                }, status=400)
            messages.error(request, f'Erro ao processar dados dos itens: {str(e)}')
            return redirect('militares:requisicao_almoxarifado_list')
        except ProdutoAlmoxarifado.DoesNotExist as e:
            logger.error(f'Produto não encontrado: {str(e)}')
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Produto não encontrado: {str(e)}'
                }, status=400)
            messages.error(request, f'Produto não encontrado: {str(e)}')
            return redirect('militares:requisicao_almoxarifado_list')
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f'Erro ao criar requisição: {str(e)}\n{error_trace}')
            
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao criar requisição: {str(e)}',
                    'trace': error_trace if request.user.is_superuser else None
                }, status=500)
            messages.error(request, f'Erro ao criar requisição: {str(e)}')
            return redirect('militares:requisicao_almoxarifado_list')
    else:
        form = RequisicaoAlmoxarifadoForm(request=request)
    
    if is_ajax:
        html = render_to_string('militares/requisicao_almoxarifado_form_modal.html', {
            'form': form,
            'is_create': True
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/requisicao_almoxarifado_form.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def requisicao_almoxarifado_aprovar(request, pk):
    """Aprova uma requisição e cria a transferência"""
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EDITAR'):
        messages.error(request, "Você não tem permissão para aprovar requisições.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    # Recarregar a requisição do banco para garantir estado limpo
    try:
        # Recarregar a requisição do banco (fora de qualquer transação)
        requisicao = RequisicaoAlmoxarifado.objects.get(pk=pk, ativo=True)
    except RequisicaoAlmoxarifado.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Requisição não encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Erro ao carregar requisição {pk}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Erro ao carregar requisição: {str(e)}'}, status=500)
    
    if not requisicao.pode_aprovar(request.user):
        messages.error(request, "Você não tem permissão para aprovar esta requisição.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    if requisicao.status != 'PENDENTE':
        messages.error(request, f"Não é possível aprovar uma requisição com status '{requisicao.get_status_display()}'.")
        return JsonResponse({'status': 'error', 'message': 'Status inválido'}, status=400)
    
    try:
        observacoes = request.POST.get('observacoes', '').strip()
        
        logger.info(f'Iniciando aprovação da requisição {pk} pelo usuário {request.user.username}')
        logger.info(f'Observações: {observacoes}')
        
        # O método aprovar já tem sua própria transação atômica
        # Não criar transação aninhada aqui para evitar problemas
        requisicao.aprovar(request.user, criar_transferencia=True, observacoes=observacoes if observacoes else None)
        logger.info(f'Requisição {pk} aprovada com sucesso')
        
        messages.success(request, 'Requisição aprovada e transferência criada com sucesso!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Requisição aprovada e transferência criada com sucesso!',
                'redirect': reverse('militares:requisicao_almoxarifado_list')
            })
        return redirect('militares:requisicao_almoxarifado_list')
    except ValueError as e:
        # Erro de validação (status inválido, etc)
        logger.warning(f"Erro de validação ao aprovar requisição {pk}: {str(e)}")
        error_message = str(e)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('militares:requisicao_almoxarifado_list')
    except Exception as e:
        # Erro genérico (500)
        error_trace = traceback.format_exc()
        logger.error(f"Erro ao aprovar requisição {pk}: {str(e)}\n{error_trace}")
        
        # Verificar se é erro de transação
        error_str = str(e).lower()
        if 'transação atual foi interrompida' in str(e) or 'current transaction is aborted' in error_str:
            error_message = 'Erro ao processar aprovação. A transação foi interrompida. Por favor, tente novamente.'
        else:
            error_message = str(e)
            if request.user.is_superuser:
                error_message += f"\n\nDetalhes técnicos:\n{error_trace}"
        
        messages.error(request, f'Erro ao aprovar requisição: {error_message}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error', 
                'message': error_message,
                'trace': error_trace if request.user.is_superuser else None
            }, status=500)
        return redirect('militares:requisicao_almoxarifado_list')


@login_required
@require_http_methods(["POST"])
def requisicao_almoxarifado_negar(request, pk):
    """Nega uma requisição"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EDITAR'):
        messages.error(request, "Você não tem permissão para negar requisições.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    requisicao = get_object_or_404(RequisicaoAlmoxarifado, pk=pk, ativo=True)
    
    if not requisicao.pode_aprovar(request.user):
        messages.error(request, "Você não tem permissão para negar esta requisição.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    if requisicao.status != 'PENDENTE':
        messages.error(request, f"Não é possível negar uma requisição com status '{requisicao.get_status_display()}'.")
        return JsonResponse({'status': 'error', 'message': 'Status inválido'}, status=400)
    
    motivo = request.POST.get('motivo_negacao', '')
    if not motivo:
        return JsonResponse({'status': 'error', 'message': 'É necessário informar o motivo da negação.'}, status=400)
    
    try:
        observacoes = request.POST.get('observacoes', '').strip()
        requisicao.negar(request.user, motivo, observacoes_adicionais=observacoes if observacoes else None)
        
        messages.success(request, 'Requisição negada com sucesso!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Requisição negada com sucesso!',
                'redirect': reverse('militares:requisicao_almoxarifado_list')
            })
        return redirect('militares:requisicao_almoxarifado_list')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao negar requisição {pk}: {str(e)}")
        messages.error(request, f'Erro ao negar requisição: {str(e)}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def requisicao_almoxarifado_confirmar_recebimento(request, pk):
    """Confirma o recebimento de uma requisição pelo solicitante"""
    import logging
    import traceback
    from django.utils import timezone
    
    logger = logging.getLogger(__name__)
    
    try:
        requisicao = get_object_or_404(RequisicaoAlmoxarifado, pk=pk, ativo=True)
        
        # Verificar se o usuário pode confirmar o recebimento
        if not requisicao.pode_confirmar_recebimento(request.user):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Você não tem permissão para confirmar o recebimento desta requisição.'
                }, status=403)
            messages.error(request, 'Você não tem permissão para confirmar o recebimento desta requisição.')
            return redirect('militares:requisicao_almoxarifado_list')
        
        # Confirmar o recebimento
        requisicao.data_confirmacao_recebimento = timezone.now()
        requisicao.confirmado_por = request.user
        requisicao.save()
        
        logger.info(f'Requisição #{requisicao.pk} confirmada por {request.user.username}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Recebimento da requisição #{requisicao.pk} confirmado com sucesso!'
            })
        
        messages.success(request, f'Recebimento da requisição #{requisicao.pk} confirmado com sucesso!')
        return redirect('militares:requisicao_almoxarifado_list')
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f'Erro ao confirmar recebimento da requisição {pk}: {str(e)}\n{error_trace}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao confirmar recebimento: {str(e)}'
            }, status=500)
        
        messages.error(request, f'Erro ao confirmar recebimento: {str(e)}')
        return redirect('militares:requisicao_almoxarifado_list')


@login_required
def requisicao_almoxarifado_detail(request, pk):
    """Visualiza os detalhes de uma requisição"""
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
            messages.error(request, "Você não tem permissão para visualizar requisições.")
            return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
        
        # Fazer prefetch dos produtos relacionados
        from django.db.models import Prefetch
        requisicao = get_object_or_404(
            RequisicaoAlmoxarifado.objects.select_related(
                'produto', 'criado_por', 'aprovado_por',
                'orgao_requisitante', 'grande_comando_requisitante', 'unidade_requisitante', 'sub_unidade_requisitante',
                'orgao_requisitada', 'grande_comando_requisitada', 'unidade_requisitada', 'sub_unidade_requisitada'
            ).prefetch_related(
                Prefetch(
                    'produtos_requisicao',
                    queryset=RequisicaoAlmoxarifadoProduto.objects.select_related('produto')
                )
            ),
            pk=pk,
            ativo=True
        )
        
        # Verificar permissões específicas
        pode_aprovar = requisicao.pode_aprovar(request.user)
        pode_editar = requisicao.pode_editar(request.user)
        pode_excluir = requisicao.pode_excluir(request.user)
        
        # Buscar histórico da requisição
        historico = HistoricoRequisicaoAlmoxarifado.objects.filter(
            requisicao=requisicao
        ).select_related('alterado_por', 'produto').order_by('-data_alteracao')
        
        # Log para debug
        logger.info(f'Requisição {pk} - Total de registros de histórico: {historico.count()}')
        
        # Buscar assinaturas ordenadas: primeiro SOLICITANTE, depois APROVACAO/NEGACAO, depois por data
        from django.db.models import Case, When, IntegerField
        from .models import AssinaturaRequisicaoAlmoxarifado
        assinaturas = AssinaturaRequisicaoAlmoxarifado.objects.filter(
            requisicao=requisicao
        ).select_related('assinado_por', 'militar').annotate(
            ordem_tipo=Case(
                When(tipo_assinatura='SOLICITANTE', then=1),
                When(tipo_assinatura='APROVACAO', then=2),
                When(tipo_assinatura='NEGACAO', then=3),
                default=4,
                output_field=IntegerField()
            )
        ).order_by('ordem_tipo', 'data_assinatura')
        
        context = {
            'requisicao': requisicao,
            'assinaturas': assinaturas,
            'historico': historico,
            'pode_aprovar': pode_aprovar,
            'pode_editar': pode_editar,
            'pode_excluir': pode_excluir,
            'pode_confirmar': requisicao.pode_confirmar_recebimento(request.user),
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('militares/requisicao_almoxarifado_detail_modal.html', context, request=request)
            return JsonResponse({'status': 'success', 'html': html})
        
        return render(request, 'militares/requisicao_almoxarifado_detail.html', context)
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f'Erro ao visualizar detalhes da requisição {pk}: {str(e)}\n{error_trace}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao carregar detalhes: {str(e)}',
                'trace': error_trace if request.user.is_superuser else None
            }, status=500)
        
        messages.error(request, f'Erro ao carregar detalhes da requisição: {str(e)}')
        return redirect('militares:requisicao_almoxarifado_list')


@login_required
def requisicao_almoxarifado_update(request, pk):
    """Atualiza uma requisição via modal"""
    import logging
    logger = logging.getLogger(__name__)
    
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EDITAR'):
        messages.error(request, "Você não tem permissão para editar requisições.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    # Fazer prefetch dos itens relacionados - usar o mesmo padrão da view de detalhes
    from django.db.models import Prefetch
    requisicao = get_object_or_404(
        RequisicaoAlmoxarifado.objects.select_related(
            'produto', 'criado_por', 'aprovado_por',
            'orgao_requisitante', 'grande_comando_requisitante', 'unidade_requisitante', 'sub_unidade_requisitante',
            'orgao_requisitada', 'grande_comando_requisitada', 'unidade_requisitada', 'sub_unidade_requisitada'
        ).prefetch_related(
            Prefetch(
                'produtos_requisicao',
                queryset=RequisicaoAlmoxarifadoProduto.objects.select_related('produto')
            )
        ),
        pk=pk,
        ativo=True
    )
    
    # Verificar se o usuário pode editar
    if not requisicao.pode_editar(request.user):
        messages.error(request, "Você não tem permissão para editar esta requisição.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    # Verificar se pode editar (apenas pendentes)
    if requisicao.status != 'PENDENTE':
        messages.error(request, f"Não é possível editar uma requisição com status '{requisicao.get_status_display()}'.")
        return JsonResponse({'status': 'error', 'message': 'Status inválido'}, status=400)
    
    if request.method == 'POST':
        form = RequisicaoAlmoxarifadoForm(request.POST, instance=requisicao, request=request)
        if form.is_valid():
            from django.db import transaction
            
            # Verificar se o usuário pertence à OM requisitada (para validar estoque)
            from .permissoes_militares import obter_sessao_ativa_usuario
            sessao = obter_sessao_ativa_usuario(request.user)
            pertence_om_requisitada = False
            if sessao and sessao.funcao_militar_usuario:
                funcao = sessao.funcao_militar_usuario
                # Verificar se pertence à OM requisitada (mesma lógica do pode_editar)
                if requisicao.sub_unidade_requisitada:
                    pertence_om_requisitada = funcao.sub_unidade == requisicao.sub_unidade_requisitada
                elif requisicao.unidade_requisitada:
                    pertence_om_requisitada = (funcao.unidade == requisicao.unidade_requisitada or
                                              (funcao.sub_unidade and funcao.sub_unidade.unidade == requisicao.unidade_requisitada))
                elif requisicao.grande_comando_requisitada:
                    pertence_om_requisitada = (funcao.grande_comando == requisicao.grande_comando_requisitada or
                                              (funcao.unidade and funcao.unidade.grande_comando == requisicao.grande_comando_requisitada))
                elif requisicao.orgao_requisitada:
                    pertence_om_requisitada = (funcao.orgao == requisicao.orgao_requisitada or
                                              (funcao.grande_comando and funcao.grande_comando.orgao == requisicao.orgao_requisitada))
            
            with transaction.atomic():
                # Capturar estado anterior dos produtos para histórico
                produtos_anteriores = {}
                for produto_req in requisicao.produtos_requisicao.all():
                    produtos_anteriores[produto_req.produto_id] = {
                        'produto': produto_req.produto,
                        'quantidade': produto_req.quantidade
                    }
                
                requisicao = form.save(commit=False)
                # Garantir que quantidade e produto sejam None quando usando múltiplos itens
                requisicao.quantidade = None
                requisicao.produto = None  # Usar 'produto' em vez de 'item'
                requisicao.save()
                
                logger.info(f'Requisição {requisicao.pk} atualizada. Status: {requisicao.status}, OM Requisitada: {requisicao.orgao_requisitada or requisicao.grande_comando_requisitada or requisicao.unidade_requisitada or requisicao.sub_unidade_requisitada}')
                
                # Processar múltiplos itens
                itens_data = request.POST.get('itens_data')
                if itens_data:
                    import json
                    try:
                        itens_list = json.loads(itens_data)
                        
                        # Se a OM requisitada está editando, validar estoque antes de salvar
                        if pertence_om_requisitada:
                            for item_data in itens_list:
                                item_id = item_data.get('item_id')
                                quantidade_str = item_data.get('quantidade', 0)
                                
                                if not item_id:
                                    continue
                                
                                try:
                                    quantidade = Decimal(str(quantidade_str))
                                except (ValueError, TypeError):
                                    continue
                                
                                if quantidade <= 0:
                                    continue
                                
                                try:
                                    item = ProdutoAlmoxarifado.objects.get(pk=item_id, ativo=True)
                                except ProdutoAlmoxarifado.DoesNotExist:
                                    raise ValueError(f'Item com ID {item_id} não encontrado ou inativo.')
                                
                                # Calcular estoque disponível na OM requisitada
                                estoque_disponivel = item.get_estoque_por_om(
                                    orgao=requisicao.orgao_requisitada,
                                    grande_comando=requisicao.grande_comando_requisitada,
                                    unidade=requisicao.unidade_requisitada,
                                    sub_unidade=requisicao.sub_unidade_requisitada
                                )
                                
                                # Validar estoque
                                if estoque_disponivel < quantidade:
                                    raise ValueError(
                                        f'Estoque insuficiente para o item {item.get_codigo_limpo()} na OM requisitada. '
                                        f'Disponível: {estoque_disponivel}, Solicitado: {quantidade}. '
                                        f'Por favor, ajuste a quantidade para não exceder o estoque disponível.'
                                    )
                        
                        # Obter IDs dos itens que devem ser mantidos
                        itens_ids_manter = [item.get('id') for item in itens_list if item.get('id')]
                        
                        # Remover produtos que não estão mais na lista
                        RequisicaoAlmoxarifadoProduto.objects.filter(requisicao=requisicao).exclude(id__in=itens_ids_manter).delete()
                        
                        for item_data in itens_list:
                            item_requisicao_id = item_data.get('id')
                            item_id = item_data.get('item_id')
                            quantidade = item_data.get('quantidade', 0)
                            
                            if not item_id or quantidade <= 0:
                                continue
                            
                            try:
                                quantidade = Decimal(str(quantidade))
                            except (ValueError, TypeError):
                                continue
                            
                            try:
                                item = ProdutoAlmoxarifado.objects.get(pk=item_id)
                            except ProdutoAlmoxarifado.DoesNotExist:
                                raise ValueError(f'Item com ID {item_id} não encontrado.')
                            
                            # Em uma requisição, o item não pode ser None
                            if not item:
                                raise ValueError(f'Item com ID {item_id} é inválido. Não é possível processar requisição sem item válido.')
                            
                            # Atualizar ou criar produto da requisição
                            if item_requisicao_id:
                                try:
                                    produto_requisicao = RequisicaoAlmoxarifadoProduto.objects.get(
                                        id=item_requisicao_id,
                                        requisicao=requisicao
                                    )
                                    quantidade_anterior = produto_requisicao.quantidade
                                    produto_anterior = produto_requisicao.produto
                                    
                                    logger.info(f'Atualizando produto da requisição {requisicao.pk}: produto_id={item.id}, quantidade={quantidade}')
                                    produto_requisicao.produto = item
                                    produto_requisicao.quantidade = quantidade
                                    produto_requisicao.save()
                                    
                                    # Registrar histórico se houve alteração
                                    if produto_anterior != item or quantidade_anterior != quantidade:
                                        HistoricoRequisicaoAlmoxarifado.objects.create(
                                            requisicao=requisicao,
                                            tipo_acao='EDICAO',
                                            alterado_por=request.user,
                                            produto=item,
                                            quantidade_anterior=quantidade_anterior if produto_anterior == item else None,
                                            quantidade_nova=quantidade if produto_anterior == item else quantidade,
                                            campo_alterado='produto' if produto_anterior != item else 'quantidade',
                                            valor_anterior=f'{produto_anterior.codigo} - {quantidade_anterior}' if produto_anterior != item else str(quantidade_anterior),
                                            valor_novo=f'{item.codigo} - {quantidade}' if produto_anterior != item else str(quantidade),
                                            observacoes=f'Produto atualizado: {produto_anterior.codigo if produto_anterior != item else item.codigo}'
                                        )
                                except RequisicaoAlmoxarifadoProduto.DoesNotExist:
                                    logger.info(f'Criando novo produto da requisição {requisicao.pk}: produto_id={item.id}, quantidade={quantidade}')
                                    produto_requisicao = RequisicaoAlmoxarifadoProduto.objects.create(
                                        requisicao=requisicao,
                                        produto=item,
                                        quantidade=quantidade
                                    )
                                    
                                    # Registrar histórico de produto adicionado
                                    HistoricoRequisicaoAlmoxarifado.objects.create(
                                        requisicao=requisicao,
                                        tipo_acao='EDICAO',
                                        alterado_por=request.user,
                                        produto=item,
                                        quantidade_nova=quantidade,
                                        campo_alterado='produto_adicionado',
                                        valor_novo=f'{item.codigo} - {quantidade}',
                                        observacoes=f'Produto adicionado: {item.codigo}'
                                    )
                            else:
                                produto_requisicao, created = RequisicaoAlmoxarifadoProduto.objects.get_or_create(
                                    requisicao=requisicao,
                                    produto=item,
                                    defaults={'quantidade': quantidade}
                                )
                                if not created:
                                    quantidade_anterior = produto_requisicao.quantidade
                                    logger.info(f'Atualizando produto existente da requisição {requisicao.pk}: produto_id={item.id}, quantidade={quantidade}')
                                    produto_requisicao.quantidade = quantidade
                                    produto_requisicao.save()
                                    
                                    # Registrar histórico se quantidade mudou
                                    if quantidade_anterior != quantidade:
                                        HistoricoRequisicaoAlmoxarifado.objects.create(
                                            requisicao=requisicao,
                                            tipo_acao='EDICAO',
                                            alterado_por=request.user,
                                            produto=item,
                                            quantidade_anterior=quantidade_anterior,
                                            quantidade_nova=quantidade,
                                            campo_alterado='quantidade',
                                            valor_anterior=str(quantidade_anterior),
                                            valor_novo=str(quantidade),
                                            observacoes=f'Quantidade do produto {item.codigo} alterada'
                                        )
                                else:
                                    logger.info(f'Produto criado na requisição {requisicao.pk}: produto_id={item.id}, quantidade={quantidade}')
                                    
                                    # Registrar histórico de produto adicionado
                                    HistoricoRequisicaoAlmoxarifado.objects.create(
                                        requisicao=requisicao,
                                        tipo_acao='EDICAO',
                                        alterado_por=request.user,
                                        produto=item,
                                        quantidade_nova=quantidade,
                                        campo_alterado='produto_adicionado',
                                        valor_novo=f'{item.codigo} - {quantidade}',
                                        observacoes=f'Produto adicionado: {item.codigo}'
                                    )
                        
                        # Registrar histórico de produtos removidos
                        produtos_atuais_ids = {item.get('item_id') for item in itens_list if item.get('item_id')}
                        for produto_id, dados in produtos_anteriores.items():
                            if produto_id not in produtos_atuais_ids:
                                HistoricoRequisicaoAlmoxarifado.objects.create(
                                    requisicao=requisicao,
                                    tipo_acao='EDICAO',
                                    alterado_por=request.user,
                                    produto=dados['produto'],
                                    quantidade_anterior=dados['quantidade'],
                                    campo_alterado='produto_removido',
                                    valor_anterior=f'{dados["produto"].codigo} - {dados["quantidade"]}',
                                    observacoes=f'Produto removido: {dados["produto"].codigo}'
                                )
                    except (json.JSONDecodeError, ProdutoAlmoxarifado.DoesNotExist, ValueError) as e:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'status': 'error',
                                'message': f'Erro ao processar itens: {str(e)}'
                            }, status=400)
                        messages.error(request, f'Erro ao processar itens: {str(e)}')
                        return redirect('militares:requisicao_almoxarifado_list')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Requisição atualizada com sucesso!',
                    'redirect': reverse('militares:requisicao_almoxarifado_list')
                })
            messages.success(request, 'Requisição atualizada com sucesso!')
            return redirect('militares:requisicao_almoxarifado_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/requisicao_almoxarifado_form_modal.html', {
                    'form': form,
                    'requisicao': requisicao,
                    'is_create': False
                }, request=request)
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(e) for e in error_list]
                
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erro de validação',
                    'html': html,
                    'errors': errors,
                    'form_data': dict(form.data) if hasattr(form, 'data') else {}
                }, status=400)
    else:
        # Requisição GET - carregar formulário
        try:
            # Garantir que o prefetch seja aplicado novamente antes de renderizar - usar o mesmo padrão da view de detalhes
            requisicao = RequisicaoAlmoxarifado.objects.select_related(
                'produto', 'criado_por', 'aprovado_por',
                'orgao_requisitante', 'grande_comando_requisitante', 'unidade_requisitante', 'sub_unidade_requisitante',
                'orgao_requisitada', 'grande_comando_requisitada', 'unidade_requisitada', 'sub_unidade_requisitada'
            ).prefetch_related(
                Prefetch(
                    'produtos_requisicao',
                    queryset=RequisicaoAlmoxarifadoProduto.objects.select_related('produto')
                )
            ).get(pk=requisicao.pk)
            
            form = RequisicaoAlmoxarifadoForm(instance=requisicao, request=request)
            
            # Log dos dados da requisição antes de criar o formulário
            logger.info(f'Requisição {pk} - Dados da instância antes do formulário:')
            logger.info(f'  - OM Requisitante: orgao={requisicao.orgao_requisitante_id}, grande_comando={requisicao.grande_comando_requisitante_id}, unidade={requisicao.unidade_requisitante_id}, sub_unidade={requisicao.sub_unidade_requisitante_id}')
            logger.info(f'  - OM Requisitada: orgao={requisicao.orgao_requisitada_id}, grande_comando={requisicao.grande_comando_requisitada_id}, unidade={requisicao.unidade_requisitada_id}, sub_unidade={requisicao.sub_unidade_requisitada_id}')
            logger.info(f'  - Observações: {requisicao.observacoes}')
            
            # Log dos dados do formulário após criação
            logger.info(f'Requisição {pk} - Dados do formulário após criação:')
            logger.info(f'  - OM Requisitante (initial): orgao={form.initial.get("orgao_requisitante")}, grande_comando={form.initial.get("grande_comando_requisitante")}, unidade={form.initial.get("unidade_requisitante")}, sub_unidade={form.initial.get("sub_unidade_requisitante")}')
            logger.info(f'  - OM Requisitada (initial): orgao={form.initial.get("orgao_requisitada")}, grande_comando={form.initial.get("grande_comando_requisitada")}, unidade={form.initial.get("unidade_requisitada")}, sub_unidade={form.initial.get("sub_unidade_requisitada")}')
            
            # Se for requisição AJAX, renderizar e retornar imediatamente
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Forçar avaliação dos produtos antes de renderizar
                produtos_list = list(requisicao.produtos_requisicao.all())
                
                logger.info(f'Requisição {pk} - Total de produtos carregados: {len(produtos_list)}')
                for p in produtos_list:
                    logger.info(f'  - Produto ID: {p.produto.id}, Código: {p.produto.codigo}, Quantidade: {p.quantidade}')
                
                html = render_to_string('militares/requisicao_almoxarifado_form_modal.html', {
                    'form': form,
                    'requisicao': requisicao,
                    'is_create': False
                }, request=request)
                return JsonResponse({'status': 'success', 'html': html})
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f'Erro ao carregar requisição {pk} para edição: {str(e)}\n{error_trace}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                error_message = str(e)
                if request.user.is_superuser:
                    error_message += f"\n\nDetalhes técnicos:\n{error_trace}"
                
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao carregar requisição: {error_message}',
                    'trace': error_trace if request.user.is_superuser else None
                }, status=500)
            raise
    
    # Se chegou aqui, não é requisição AJAX ou não foi tratada acima
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Garantir prefetch antes de renderizar (caso não tenha sido feito acima)
            if not hasattr(requisicao, '_prefetched_objects_cache') or 'produtos_requisicao' not in requisicao._prefetched_objects_cache:
                requisicao = RequisicaoAlmoxarifado.objects.prefetch_related(
                    Prefetch('produtos_requisicao', queryset=RequisicaoAlmoxarifadoProduto.objects.select_related('produto'))
                ).get(pk=requisicao.pk)
            
            # Forçar avaliação dos produtos antes de renderizar
            produtos_list = list(requisicao.produtos_requisicao.all())
            
            # Log para debug
            logger.info(f'Requisição {pk} - Total de produtos carregados: {len(produtos_list)}')
            for p in produtos_list:
                logger.info(f'  - Produto ID: {p.produto.id}, Código: {p.produto.codigo}, Quantidade: {p.quantidade}')
            
            html = render_to_string('militares/requisicao_almoxarifado_form_modal.html', {
                'form': form,
                'requisicao': requisicao,
                'is_create': False
            }, request=request)
            return JsonResponse({'status': 'success', 'html': html})
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f'Erro ao renderizar formulário de edição da requisição {pk}: {str(e)}\n{error_trace}')
            
            error_message = str(e)
            if request.user.is_superuser:
                error_message += f"\n\nDetalhes técnicos:\n{error_trace}"
            
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao renderizar formulário de edição: {error_message}',
                'trace': error_trace if request.user.is_superuser else None
            }, status=500)
    
    return render(request, 'militares/requisicao_almoxarifado_form.html', {'form': form, 'requisicao': requisicao})


@login_required
@require_http_methods(["POST"])
def requisicao_almoxarifado_excluir(request, pk):
    """Exclui uma requisição (marca como inativa)"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EXCLUIR'):
        messages.error(request, "Você não tem permissão para excluir requisições.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    requisicao = get_object_or_404(RequisicaoAlmoxarifado, pk=pk, ativo=True)
    
    # Verificar se o usuário pode excluir (criador ou com permissão de excluir)
    if requisicao.criado_por != request.user and not tem_permissao(request.user, 'ALMOXARIFADO', 'EXCLUIR'):
        if not request.user.is_superuser:
            messages.error(request, "Você não tem permissão para excluir esta requisição.")
            return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    # Verificar se pode excluir usando o método do modelo
    if not requisicao.pode_excluir(request.user):
        messages.error(request, "Não é possível excluir esta requisição. Apenas requisições pendentes podem ser excluídas pelo criador.")
        return JsonResponse({'status': 'error', 'message': 'Não é possível excluir esta requisição'}, status=400)
    
    try:
        # Marcar como inativa ao invés de excluir fisicamente
        requisicao.ativo = False
        requisicao.save()
        messages.success(request, 'Requisição excluída com sucesso!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Requisição excluída com sucesso!',
                'redirect': reverse('militares:requisicao_almoxarifado_list')
            })
        return redirect('militares:requisicao_almoxarifado_list')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao excluir requisição {pk}: {str(e)}")
        messages.error(request, f'Erro ao excluir requisição: {str(e)}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

