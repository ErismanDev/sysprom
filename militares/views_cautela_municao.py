"""
Views para o módulo de Cautela de Munição
Gerencia o registro de cautelas (entregas temporárias) de munição
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from .models import (
    Municao, Militar, Orgao, GrandeComando, Unidade, SubUnidade, 
    CautelaMunicao, SaidaMunicao
)
from .forms import CautelaMunicaoForm, DevolucaoCautelaMunicaoForm


class CautelaMunicaoListView(LoginRequiredMixin, ListView):
    """Lista todas as cautelas de munição"""
    template_name = 'militares/cautela_municao_list.html'
    context_object_name = 'cautelas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CautelaMunicao.objects.select_related(
            'municao', 'militar', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'entregue_por', 'devolvido_por'
        ).order_by('-data_entrega')
        
        # Filtros
        status = self.request.GET.get('status', '')
        if status == 'ativa':
            queryset = queryset.filter(ativa=True)
        elif status == 'devolvida':
            queryset = queryset.filter(ativa=False)
        
        militar_id = self.request.GET.get('militar', '')
        if militar_id:
            queryset = queryset.filter(militar_id=militar_id)
        
        municao_id = self.request.GET.get('municao', '')
        if municao_id:
            queryset = queryset.filter(municao_id=municao_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municoes'] = Municao.objects.all().order_by('calibre')
        return context


class CautelaMunicaoCreateView(LoginRequiredMixin, CreateView):
    """Cria nova cautela de munição"""
    model = CautelaMunicao
    form_class = CautelaMunicaoForm
    template_name = 'militares/cautela_municao_form.html'
    success_url = reverse_lazy('militares:cautela_municao_list')
    
    def form_valid(self, form):
        municao = form.instance.municao
        militar = form.instance.militar
        quantidade = form.instance.quantidade
        
        # Preencher organização da munição automaticamente se não estiver preenchida
        if not form.instance.orgao and municao.orgao:
            form.instance.orgao = municao.orgao
            form.instance.grande_comando = municao.grande_comando
            form.instance.unidade = municao.unidade
            form.instance.sub_unidade = municao.sub_unidade
        
        # Garantir que a data de entrega seja a atual
        form.instance.data_entrega = timezone.now()
        form.instance.entregue_por = self.request.user
        form.instance.ativa = True
        
        with transaction.atomic():
            response = super().form_valid(form)
            cautela = form.instance
            
            # Criar saída de munição automaticamente
            try:
                SaidaMunicao.objects.create(
                    municao=municao,
                    quantidade=quantidade,
                    tipo_saida='CAUTELA_INDIVIDUAL',
                    cautela_municao=cautela,
                    data_saida=cautela.data_entrega,
                    responsavel=self.request.user,
                    observacoes=f"Saída automática para cautela de munição - {militar.nome_completo}"
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao criar saída de munição para cautela {cautela.pk}: {str(e)}')
                messages.warning(
                    self.request, 
                    f'Cautela criada com sucesso, mas houve erro ao registrar saída de munição: {str(e)}'
                )
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Cautela de {quantidade} {municao.get_calibre_display()} registrada com sucesso para {militar.nome_completo}!'
            })
        
        messages.success(
            self.request, 
            f'Cautela de {quantidade} {municao.get_calibre_display()} registrada com sucesso para {militar.nome_completo}!'
        )
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        return super().form_invalid(form)


class CautelaMunicaoDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma cautela de munição"""
    model = CautelaMunicao
    template_name = 'militares/cautela_municao_detail.html'
    context_object_name = 'cautela'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscar saída relacionada
        context['saida'] = SaidaMunicao.objects.filter(cautela_municao=self.object).first()
        return context


@login_required
@require_http_methods(["POST"])
def devolver_cautela_municao(request, pk):
    """Devolve uma cautela de munição"""
    cautela = get_object_or_404(CautelaMunicao, pk=pk)
    
    if not cautela.ativa:
        messages.error(request, 'Esta cautela já foi devolvida.')
        return redirect('militares:cautela_municao_detail', pk=cautela.pk)
    
    form = DevolucaoCautelaMunicaoForm(request.POST, cautela=cautela)
    
    if form.is_valid():
        quantidade_devolvida = form.cleaned_data['quantidade_devolvida']
        observacoes = form.cleaned_data.get('observacoes', '')
        
        with transaction.atomic():
            # Atualizar cautela
            cautela.quantidade_devolvida += quantidade_devolvida
            
            # Verificar se foi totalmente devolvida
            if cautela.quantidade_devolvida >= cautela.quantidade:
                cautela.ativa = False
                cautela.data_devolucao = timezone.now()
                cautela.devolvido_por = request.user
            
            if observacoes:
                if cautela.observacoes:
                    cautela.observacoes += f"\n\nDevolução: {observacoes}"
                else:
                    cautela.observacoes = f"Devolução: {observacoes}"
            
            cautela.save()
            
            # Atualizar estoque
            cautela.municao.quantidade_estoque += quantidade_devolvida
            cautela.municao.save()
            
            # Atualizar saída relacionada
            saida = SaidaMunicao.objects.filter(cautela_municao=cautela).first()
            if saida:
                saida.quantidade_devolvida += quantidade_devolvida
                if saida.quantidade_devolvida >= saida.quantidade:
                    saida.totalmente_devolvida = True
                saida.save()
        
        messages.success(
            request, 
            f'Devolução de {quantidade_devolvida} {cautela.municao.get_calibre_display()} registrada com sucesso!'
        )
        return redirect('militares:cautela_municao_detail', pk=cautela.pk)
    else:
        messages.error(request, 'Erro ao processar devolução. Verifique os dados.')
        return redirect('militares:cautela_municao_detail', pk=cautela.pk)


@login_required
@require_http_methods(["POST"])
def deletar_cautela_municao(request, pk):
    """Deleta uma cautela de munição"""
    cautela = get_object_or_404(CautelaMunicao, pk=pk)
    
    if cautela.ativa:
        messages.error(request, 'Não é possível deletar uma cautela ativa. Devolva primeiro.')
        return redirect('militares:cautela_municao_detail', pk=cautela.pk)
    
    with transaction.atomic():
        # Reverter estoque se necessário
        if cautela.quantidade_devolvida < cautela.quantidade:
            quantidade_nao_devolvida = cautela.quantidade - cautela.quantidade_devolvida
            cautela.municao.quantidade_estoque += quantidade_nao_devolvida
            cautela.municao.save()
        
        # Deletar saída relacionada se existir
        SaidaMunicao.objects.filter(cautela_municao=cautela).delete()
        
        cautela.delete()
    
    messages.success(request, 'Cautela de munição deletada com sucesso!')
    return redirect('militares:cautela_municao_list')

