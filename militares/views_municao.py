"""
Views para o módulo de Controle de Munição
Gerencia entrada, saída, devolução e estoque de munição
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from .models import (
    Municao, EntradaMunicao, SaidaMunicao, DevolucaoMunicao,
    Orgao, GrandeComando, Unidade, SubUnidade, CautelaArma, CautelaArmaColetiva, CautelaMunicao
)
from .forms import (
    MunicaoForm, EntradaMunicaoForm, SaidaMunicaoForm, DevolucaoMunicaoForm
)


class MunicaoListView(LoginRequiredMixin, ListView):
    """Lista o estoque de munição"""
    model = Municao
    template_name = 'militares/municao_list.html'
    context_object_name = 'municoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Municao.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'criado_por'
        ).order_by('calibre', 'orgao', 'grande_comando', 'unidade', 'sub_unidade')
        
        # Filtros
        calibre = self.request.GET.get('calibre', '')
        if calibre:
            queryset = queryset.filter(calibre=calibre)
        
        orgao_id = self.request.GET.get('orgao', '')
        if orgao_id:
            queryset = queryset.filter(orgao_id=orgao_id)
        
        grande_comando_id = self.request.GET.get('grande_comando', '')
        if grande_comando_id:
            queryset = queryset.filter(grande_comando_id=grande_comando_id)
        
        unidade_id = self.request.GET.get('unidade', '')
        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)
        
        sub_unidade_id = self.request.GET.get('sub_unidade', '')
        if sub_unidade_id:
            queryset = queryset.filter(sub_unidade_id=sub_unidade_id)
        
        # Filtrar apenas com estoque positivo ou mostrar todos
        estoque_minimo = self.request.GET.get('estoque_minimo', '')
        if estoque_minimo:
            try:
                estoque_minimo = int(estoque_minimo)
                queryset = queryset.filter(quantidade_estoque__gte=estoque_minimo)
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calibres'] = Municao.CALIBRE_CHOICES
        context['orgaos'] = Orgao.objects.filter(ativo=True).order_by('nome')
        context['grandes_comandos'] = GrandeComando.objects.filter(ativo=True).order_by('nome')
        context['unidades'] = Unidade.objects.filter(ativo=True).order_by('nome')
        context['sub_unidades'] = SubUnidade.objects.filter(ativo=True).order_by('nome')
        
        # Estatísticas (usar queryset completo, não paginado)
        queryset_completo = Municao.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade'
        )
        
        # Aplicar mesmos filtros do queryset principal
        calibre = self.request.GET.get('calibre', '')
        if calibre:
            queryset_completo = queryset_completo.filter(calibre=calibre)
        
        orgao_id = self.request.GET.get('orgao', '')
        if orgao_id:
            queryset_completo = queryset_completo.filter(orgao_id=orgao_id)
        
        grande_comando_id = self.request.GET.get('grande_comando', '')
        if grande_comando_id:
            queryset_completo = queryset_completo.filter(grande_comando_id=grande_comando_id)
        
        unidade_id = self.request.GET.get('unidade', '')
        if unidade_id:
            queryset_completo = queryset_completo.filter(unidade_id=unidade_id)
        
        sub_unidade_id = self.request.GET.get('sub_unidade', '')
        if sub_unidade_id:
            queryset_completo = queryset_completo.filter(sub_unidade_id=sub_unidade_id)
        
        estoque_minimo = self.request.GET.get('estoque_minimo', '')
        if estoque_minimo:
            try:
                estoque_minimo = int(estoque_minimo)
                queryset_completo = queryset_completo.filter(quantidade_estoque__gte=estoque_minimo)
            except ValueError:
                pass
        
        context['total_municoes'] = queryset_completo.count()
        context['total_estoque'] = queryset_completo.aggregate(total=Sum('quantidade_estoque'))['total'] or 0
        context['municoes_com_estoque'] = queryset_completo.filter(quantidade_estoque__gt=0).count()
        context['municoes_sem_estoque'] = queryset_completo.filter(quantidade_estoque=0).count()
        
        return context


class MunicaoCreateView(LoginRequiredMixin, CreateView):
    """Cria novo registro de munição"""
    model = Municao
    form_class = MunicaoForm
    template_name = 'militares/municao_form.html'
    success_url = reverse_lazy('militares:municao_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Captura exceções e retorna JSON para requisições AJAX"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                import traceback
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao processar requisição: {str(e)}',
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.user.is_superuser else None
                }, status=500)
            raise
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        
        # Se for requisição AJAX, retornar JSON
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Munição {form.instance.get_calibre_display()} cadastrada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(self.request, f'Munição {form.instance.get_calibre_display()} cadastrada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                self.object = None
                form = self.get_form()
                context = self.get_context_data(form=form)
                from django.template.loader import render_to_string
                html = render_to_string('militares/municao_form_modal_content.html', context, request=request)
                return JsonResponse({'html': html})
            except Exception as e:
                import traceback
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao carregar formulário: {str(e)}',
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.user.is_superuser else None
                }, status=500)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Garantir que o request seja passado ao formulário
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class MunicaoDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma munição"""
    model = Municao
    template_name = 'militares/municao_detail.html'
    context_object_name = 'municao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        municao = self.object
        
        # Entradas recentes
        context['entradas'] = municao.entradas.select_related('responsavel').order_by('-data_entrada')[:10]
        
        # Saídas recentes
        context['saidas'] = municao.saidas.select_related(
            'responsavel', 'cautela_individual', 'cautela_coletiva'
        ).order_by('-data_saida')[:10]
        
        # Estatísticas
        total_entradas = municao.entradas.aggregate(total=Sum('quantidade'))['total'] or 0
        total_saidas = municao.saidas.aggregate(total=Sum('quantidade'))['total'] or 0
        total_devolvidas = municao.saidas.aggregate(total=Sum('quantidade_devolvida'))['total'] or 0
        
        context['total_entradas'] = total_entradas
        context['total_saidas'] = total_saidas
        context['total_devolvidas'] = total_devolvidas
        context['saldo'] = total_entradas - total_saidas + total_devolvidas
        
        return context


class EntradaMunicaoCreateView(LoginRequiredMixin, CreateView):
    """Registra entrada de munição"""
    model = EntradaMunicao
    form_class = EntradaMunicaoForm
    template_name = 'militares/entrada_municao_form.html'
    success_url = reverse_lazy('militares:entrada_municao_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Captura exceções e retorna JSON para requisições AJAX"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                import traceback
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao processar requisição: {str(e)}',
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.user.is_superuser else None
                }, status=500)
            raise
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                self.object = None
                form = self.get_form()
                context = self.get_context_data(form=form)
                from django.template.loader import render_to_string
                html = render_to_string('militares/entrada_municao_form_modal_content.html', context, request=request)
                return JsonResponse({'html': html})
            except Exception as e:
                import traceback
                error_msg = str(e)
                error_trace = traceback.format_exc()
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao carregar formulário: {error_msg}',
                    'error': error_msg,
                    'traceback': error_trace if request.user.is_superuser else None
                }, status=500)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = super().form_valid(form)
            return JsonResponse({
                'success': True,
                'message': f'Entrada de {form.instance.quantidade} {form.instance.municao.get_calibre_display()} registrada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(
            self.request, 
            f'Entrada de {form.instance.quantidade} {form.instance.municao.get_calibre_display()} registrada com sucesso!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class EntradaMunicaoListView(LoginRequiredMixin, ListView):
    """Lista entradas de munição"""
    model = EntradaMunicao
    template_name = 'militares/entrada_municao_list.html'
    context_object_name = 'entradas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EntradaMunicao.objects.select_related(
            'municao', 'responsavel'
        ).order_by('-data_entrada')
        
        # Filtros
        municao_id = self.request.GET.get('municao', '')
        if municao_id:
            queryset = queryset.filter(municao_id=municao_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municoes'] = Municao.objects.all().order_by('calibre')
        return context


class SaidaMunicaoCreateView(LoginRequiredMixin, CreateView):
    """Registra saída de munição"""
    model = SaidaMunicao
    form_class = SaidaMunicaoForm
    template_name = 'militares/saida_municao_form.html'
    success_url = reverse_lazy('militares:saida_municao_list')
    
    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        messages.success(
            self.request, 
            f'Saída de {form.instance.quantidade} {form.instance.municao.get_calibre_display()} registrada com sucesso!'
        )
        return super().form_valid(form)


class SaidaMunicaoListView(LoginRequiredMixin, ListView):
    """Lista saídas de munição"""
    model = SaidaMunicao
    template_name = 'militares/saida_municao_list.html'
    context_object_name = 'saidas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SaidaMunicao.objects.select_related(
            'municao', 'responsavel', 'cautela_individual', 'cautela_coletiva'
        ).order_by('-data_saida')
        
        # Filtros
        municao_id = self.request.GET.get('municao', '')
        if municao_id:
            queryset = queryset.filter(municao_id=municao_id)
        
        tipo_saida = self.request.GET.get('tipo_saida', '')
        if tipo_saida:
            queryset = queryset.filter(tipo_saida=tipo_saida)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municoes'] = Municao.objects.all().order_by('calibre')
        return context


class DevolucaoMunicaoCreateView(LoginRequiredMixin, CreateView):
    """Registra devolução de munição"""
    model = DevolucaoMunicao
    form_class = DevolucaoMunicaoForm
    template_name = 'militares/devolucao_municao_form.html'
    success_url = reverse_lazy('militares:devolucao_municao_list')
    
    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        messages.success(
            self.request, 
            f'Devolução de {form.instance.quantidade_devolvida} {form.instance.saida.municao.get_calibre_display()} registrada com sucesso!'
        )
        return super().form_valid(form)


class DevolucaoMunicaoListView(LoginRequiredMixin, ListView):
    """Lista devoluções de munição"""
    model = DevolucaoMunicao
    template_name = 'militares/devolucao_municao_list.html'
    context_object_name = 'devolucoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = DevolucaoMunicao.objects.select_related(
            'saida', 'saida__municao', 'responsavel'
        ).order_by('-data_devolucao')
        
        # Filtros
        saida_id = self.request.GET.get('saida', '')
        if saida_id:
            queryset = queryset.filter(saida_id=saida_id)
        
        return queryset


@login_required
def municao_estoque_ajax(request):
    """Retorna estoque de munição via AJAX"""
    calibre = request.GET.get('calibre')
    orgao_id = request.GET.get('orgao')
    grande_comando_id = request.GET.get('grande_comando')
    unidade_id = request.GET.get('unidade')
    sub_unidade_id = request.GET.get('sub_unidade')
    
    try:
        municao = Municao.objects.get(
            calibre=calibre,
            orgao_id=orgao_id if orgao_id else None,
            grande_comando_id=grande_comando_id if grande_comando_id else None,
            unidade_id=unidade_id if unidade_id else None,
            sub_unidade_id=sub_unidade_id if sub_unidade_id else None,
        )
        return JsonResponse({
            'success': True,
            'estoque': municao.quantidade_estoque,
            'id': municao.id
        })
    except Municao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'estoque': 0,
            'message': 'Munição não encontrada. Cadastre primeiro.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def municao_dados_ajax(request, pk):
    """Retorna dados da munição via AJAX"""
    try:
        municao = get_object_or_404(Municao, pk=pk)
        return JsonResponse({
            'success': True,
            'estoque': municao.quantidade_estoque,
            'organizacao': municao.get_organizacao(),
            'orgao_id': municao.orgao_id if municao.orgao else None,
            'grande_comando_id': municao.grande_comando_id if municao.grande_comando else None,
            'unidade_id': municao.unidade_id if municao.unidade else None,
            'sub_unidade_id': municao.sub_unidade_id if municao.sub_unidade else None,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

