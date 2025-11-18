"""
Views para o módulo de Controle de Combustível de Viaturas
Gerencia o registro e controle de abastecimentos
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django import forms

from .models import AbastecimentoViatura, Viatura, Militar, HistoricoAbastecimentoAssinado, AssinaturaHistoricoAbastecimento, ManutencaoViatura, TrocaOleoViatura, RodagemViatura
from .forms import AbastecimentoViaturaForm, ManutencaoViaturaForm, TrocaOleoViaturaForm


class AbastecimentoListView(LoginRequiredMixin, ListView):
    """Lista todos os abastecimentos"""
    model = AbastecimentoViatura
    template_name = 'militares/abastecimento_list.html'
    context_object_name = 'abastecimentos'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = AbastecimentoViatura.objects.select_related(
            'viatura', 'responsavel', 'criado_por'
        ).order_by('-data_abastecimento', '-km_abastecimento')
        
        # Filtros
        search = self.request.GET.get('search', '')
        viatura_id = self.request.GET.get('viatura', '')
        tipo_combustivel = self.request.GET.get('tipo_combustivel', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(viatura__placa__icontains=search) |
                Q(viatura__prefixo__icontains=search) |
                Q(posto_fornecedor__icontains=search) |
                Q(observacoes__icontains=search)
            )
        
        if viatura_id:
            queryset = queryset.filter(viatura_id=viatura_id)
        
        if tipo_combustivel:
            queryset = queryset.filter(tipo_combustivel=tipo_combustivel)
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                queryset = queryset.filter(data_abastecimento__gte=data_inicio_obj)
            except:
                pass
        
        if data_fim:
            try:
                from datetime import datetime
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                # Incluir o dia inteiro
                data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(data_abastecimento__lte=data_fim_obj)
            except:
                pass
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['viatura_id'] = self.request.GET.get('viatura', '')
        context['tipo_combustivel'] = self.request.GET.get('tipo_combustivel', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_abastecimentos'] = queryset.count()
        context['total_litros'] = queryset.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
        
        # Valores separados: combustível e aditivos
        context['total_valor_combustivel'] = queryset.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        context['total_valor_aditivo'] = queryset.aggregate(Sum('valor_total_aditivo'))['valor_total_aditivo__sum'] or 0
        context['total_valor_nota'] = queryset.aggregate(Sum('valor_total_nota'))['valor_total_nota__sum'] or 0
        
        # Mantido para compatibilidade (total geral)
        context['total_valor'] = context['total_valor_nota'] or context['total_valor_combustivel']
        context['media_valor_litro'] = queryset.aggregate(Avg('valor_litro'))['valor_litro__avg'] or 0
        
        
        # Lista de viaturas para filtro
        context['viaturas'] = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Lista de tipos de combustível
        context['tipos_combustivel'] = AbastecimentoViatura.TIPO_COMBUSTIVEL_CHOICES
        
        return context


class AbastecimentoCreateView(LoginRequiredMixin, CreateView):
    """Cria novo abastecimento"""
    model = AbastecimentoViatura
    form_class = AbastecimentoViaturaForm
    template_name = 'militares/abastecimento_form.html'
    success_url = reverse_lazy('militares:abastecimento_list')
    
    def get_initial(self):
        """Define valores iniciais"""
        initial = super().get_initial()
        viatura_id = self.request.GET.get('viatura', '')
        if viatura_id:
            try:
                viatura = Viatura.objects.get(pk=viatura_id, ativo=True)
                initial['viatura'] = viatura
                initial['km_abastecimento'] = viatura.km_atual
                initial['tipo_combustivel'] = viatura.combustivel if viatura.combustivel else 'DIESEL'
            except:
                pass
        
        # Definir responsável automaticamente como o militar logado
        try:
            if hasattr(self.request.user, 'militar'):
                initial['responsavel'] = self.request.user.militar
        except:
            pass
        
        return initial
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        # Se não houver responsável selecionado e o usuário estiver vinculado a um militar, usar o militar
        if not form.instance.responsavel:
            try:
                militar_usuario = form.instance.criado_por.militar if hasattr(form.instance.criado_por, 'militar') else None
                if militar_usuario:
                    form.instance.responsavel = militar_usuario
            except:
                pass
        
        messages.success(
            self.request, 
            f'Abastecimento registrado com sucesso! {form.instance.quantidade_litros}L de {form.instance.get_tipo_combustivel_display()} para {form.instance.viatura.placa}.'
        )
        return super().form_valid(form)


class AbastecimentoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um abastecimento"""
    model = AbastecimentoViatura
    template_name = 'militares/abastecimento_detail.html'
    context_object_name = 'abastecimento'


class AbastecimentoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita um abastecimento"""
    model = AbastecimentoViatura
    form_class = AbastecimentoViaturaForm
    template_name = 'militares/abastecimento_form.html'
    success_url = reverse_lazy('militares:abastecimento_list')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Abastecimento atualizado com sucesso!'
        )
        return super().form_valid(form)


class AbastecimentoDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """Exclui um abastecimento - Apenas para superusuários"""
    model = AbastecimentoViatura
    template_name = 'militares/abastecimento_confirm_delete.html'
    success_url = reverse_lazy('militares:abastecimento_list')
    
    def test_func(self):
        """Apenas superusuários podem excluir"""
        return self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem excluir abastecimentos.")
        abastecimento = self.get_object()
        placa = abastecimento.viatura.placa
        messages.success(request, f'Abastecimento da viatura {placa} excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def abastecimento_por_viatura(request, viatura_id):
    """Lista abastecimentos de uma viatura específica"""
    viatura = get_object_or_404(Viatura, pk=viatura_id)
    
    # Filtros de período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Ordenar do último (mais recente) para o primeiro (mais antigo)
    abastecimentos = AbastecimentoViatura.objects.filter(
        viatura=viatura
    ).select_related('responsavel', 'criado_por')
    
    # Aplicar filtros de data
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            abastecimentos = abastecimentos.filter(data_abastecimento__date__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            # Incluir o dia inteiro
            from datetime import time
            data_fim_completa = datetime.combine(data_fim_obj, time.max)
            abastecimentos = abastecimentos.filter(data_abastecimento__lte=data_fim_completa)
        except:
            pass
    
    abastecimentos = abastecimentos.order_by('-data_abastecimento', '-km_abastecimento')
    
    # Estatísticas
    total_litros = abastecimentos.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
    total_valor_combustivel = abastecimentos.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_valor_aditivo = abastecimentos.aggregate(Sum('valor_total_aditivo'))['valor_total_aditivo__sum'] or 0
    total_valor_nota = abastecimentos.aggregate(Sum('valor_total_nota'))['valor_total_nota__sum'] or 0
    total_valor = total_valor_nota or total_valor_combustivel
    media_valor_litro = abastecimentos.aggregate(Avg('valor_litro'))['valor_litro__avg'] or 0
    
    # Calcular consumo médio em KM por litro (se houver pelo menos 2 abastecimentos)
    consumo_medio_km_litro = None
    if abastecimentos.count() >= 2:
        # Ordenar por data para pegar o primeiro e último corretamente
        abastecimentos_ordenados = abastecimentos.order_by('data_abastecimento', 'km_abastecimento')
        primeiro = abastecimentos_ordenados.first()
        ultimo = abastecimentos_ordenados.last()
        
        if primeiro and ultimo and primeiro != ultimo:
            km_percorridos = ultimo.km_abastecimento - primeiro.km_abastecimento
            # Somar litros de todos exceto o último (o último ainda não foi consumido)
            litros_consumidos = sum(a.quantidade_litros for a in abastecimentos_ordenados.exclude(pk=ultimo.pk))
            
            if km_percorridos > 0 and litros_consumidos > 0:
                consumo_medio_km_litro = km_percorridos / litros_consumidos  # KM por litro
    
    paginator = Paginator(abastecimentos, 30)
    page = request.GET.get('page')
    abastecimentos_page = paginator.get_page(page)
    
    # Obter funções do usuário para assinatura
    from .models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        ativo=True
    ).select_related('funcao_militar')
    
    context = {
        'viatura': viatura,
        'abastecimentos': abastecimentos_page,
        'total_litros': total_litros,
        'total_valor_combustivel': total_valor_combustivel,
        'total_valor_aditivo': total_valor_aditivo,
        'total_valor_nota': total_valor_nota,
        'total_valor': total_valor,  # Mantido para compatibilidade
        'media_valor_litro': media_valor_litro,
        'consumo_medio_km_litro': consumo_medio_km_litro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'funcoes_usuario': funcoes_usuario,
    }
    
    return render(request, 'militares/abastecimento_por_viatura.html', context)


def abastecimento_qr(request, viatura_id=None):
    """
    Página pública acessível via QR Code ou código numérico para abastecimento móvel.
    Primeiro pede login, depois redireciona para formulário de abastecimento.
    Pode receber viatura_id diretamente na URL ou via código numérico no formulário.
    """
    # Se recebeu código numérico via POST (acesso manual)
    if request.method == 'POST' and 'codigo_viatura' in request.POST:
        codigo = request.POST.get('codigo_viatura', '').strip()
        try:
            viatura_id = int(codigo)
        except (ValueError, TypeError):
            messages.error(request, 'Código inválido. Por favor, verifique o código numérico.')
            return render(request, 'militares/abastecimento_qr_busca.html')
    
    # Validar viatura_id
    if not viatura_id:
        # Se não tem viatura_id e não é POST com código, mostrar página de busca
        if request.method != 'POST':
            return render(request, 'militares/abastecimento_qr_busca.html')
        else:
            messages.error(request, 'Código de viatura não fornecido.')
            return render(request, 'militares/abastecimento_qr_busca.html')
    
    # Verificar se a viatura existe
    try:
        viatura = Viatura.objects.get(pk=viatura_id, ativo=True)
    except Viatura.DoesNotExist:
        messages.error(request, 'Viatura não encontrada ou inativa.')
        return render(request, 'militares/abastecimento_qr_busca.html')
    
    # Redirecionar direto para o formulário mobile (que agora tem login integrado)
    return redirect('militares:frota_create_mobile', viatura_id=viatura_id)


def abastecimento_create_mobile(request, viatura_id):
    """
    Formulário mobile-friendly para abastecimento e manutenção pré-preenchido com a viatura.
    Permite login junto com o registro. Acessível via QR Code.
    """
    viatura = get_object_or_404(Viatura, pk=viatura_id, ativo=True)
    
    # Último abastecimento para sugerir KM
    ultimo_abastecimento = AbastecimentoViatura.objects.filter(
        viatura=viatura,
        ativo=True
    ).order_by('-data_abastecimento', '-km_abastecimento').first()
    
    # Última manutenção para sugerir KM
    ultima_manutencao = ManutencaoViatura.objects.filter(
        viatura=viatura,
        ativo=True
    ).order_by('-data_manutencao', '-km_manutencao').first()
    
    # Última troca de óleo para sugerir KM
    ultima_troca_oleo = TrocaOleoViatura.objects.filter(
        viatura=viatura,
        ativo=True
    ).order_by('-data_troca', '-km_troca').first()
    
    # Rodagem em andamento para esta viatura
    rodagem_em_andamento = RodagemViatura.objects.filter(
        viatura=viatura,
        status='EM_ANDAMENTO',
        ativo=True
    ).order_by('-data_saida', '-hora_saida').first()
    
    # Última rodagem finalizada para sugerir KM inicial
    ultima_rodagem_finalizada = RodagemViatura.objects.filter(
        viatura=viatura,
        status='FINALIZADA',
        ativo=True
    ).order_by('-data_retorno', '-hora_retorno', '-data_saida', '-hora_saida').first()
    
    # Se POST do formulário de rodagem (retorno)
    if request.method == 'POST' and request.POST.get('tipo_rodagem') == 'retorno':
        # Verificar se precisa fazer login primeiro
        if not request.user.is_authenticated:
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    request.session.save()
                else:
                    messages.error(request, 'Usuário ou senha incorretos.')
                    return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
            else:
                messages.error(request, 'É necessário fazer login para registrar o retorno.')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
        
        # Processar retorno
        if request.user.is_authenticated:
            rodagem_id = request.POST.get('rodagem_id')
            try:
                rodagem = RodagemViatura.objects.get(pk=rodagem_id, viatura=viatura, status='EM_ANDAMENTO', ativo=True)
                
                from datetime import datetime
                data_retorno = request.POST.get('data_retorno')
                hora_retorno = request.POST.get('hora_retorno')
                km_final = request.POST.get('km_final')
                
                if not data_retorno or not hora_retorno or not km_final:
                    messages.error(request, 'Todos os campos são obrigatórios!')
                    return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
                
                try:
                    km_final = int(km_final)
                    if km_final < rodagem.km_inicial:
                        messages.error(request, f'O KM final ({km_final}) não pode ser menor que o KM inicial ({rodagem.km_inicial})!')
                        return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
                except ValueError:
                    messages.error(request, 'KM final inválido!')
                    return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
                
                # Atualizar rodagem
                rodagem.data_retorno = datetime.strptime(data_retorno, '%Y-%m-%d').date()
                rodagem.hora_retorno = datetime.strptime(hora_retorno, '%H:%M').time()
                rodagem.km_final = km_final
                rodagem.status = 'FINALIZADA'
                rodagem.save()
                
                messages.success(request, f'Rodagem encerrada com sucesso! KM rodado: {rodagem.km_rodado} km')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
                
            except RodagemViatura.DoesNotExist:
                messages.error(request, 'Rodagem não encontrada ou já finalizada.')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
    
    # Se POST do formulário de rodagem (saída)
    elif request.method == 'POST' and request.POST.get('tipo_rodagem') == 'saida':
        # Verificar se precisa fazer login primeiro
        if not request.user.is_authenticated:
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    request.session.save()
                else:
                    messages.error(request, 'Usuário ou senha incorretos.')
                    return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
            else:
                messages.error(request, 'É necessário fazer login para registrar a saída.')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
        
        # Processar saída
        if request.user.is_authenticated:
            from datetime import datetime
            import pytz
            
            data_saida = request.POST.get('data_saida')
            hora_saida = request.POST.get('hora_saida')
            km_inicial = request.POST.get('km_inicial')
            objetivo = request.POST.get('objetivo')
            destino = request.POST.get('destino', '').strip()
            observacoes = request.POST.get('observacoes', '').strip()
            
            if not data_saida or not hora_saida or not km_inicial or not objetivo:
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos!')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
            
            try:
                km_inicial = int(km_inicial)
            except ValueError:
                messages.error(request, 'KM inicial inválido!')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
            
            # Obter militar do usuário
            responsavel_usuario = None
            try:
                if hasattr(request.user, 'militar'):
                    responsavel_usuario = request.user.militar
            except:
                pass
            
            if not responsavel_usuario:
                messages.error(request, 'Você não está vinculado a um militar. Entre em contato com o administrador.')
                return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
            
            # Criar rodagem
            rodagem = RodagemViatura.objects.create(
                viatura=viatura,
                data_saida=datetime.strptime(data_saida, '%Y-%m-%d').date(),
                hora_saida=datetime.strptime(hora_saida, '%H:%M').time(),
                km_inicial=km_inicial,
                objetivo=objetivo,
                destino=destino if destino else None,
                observacoes=observacoes if observacoes else None,
                condutor=responsavel_usuario,
                status='EM_ANDAMENTO',
                criado_por=request.user
            )
            
            messages.success(request, f'Saída registrada com sucesso! Rodagem iniciada para {viatura.placa}.')
            return redirect('militares:frota_create_mobile', viatura_id=viatura_id)
    
    # Se POST do formulário de abastecimento
    elif request.method == 'POST' and 'quantidade_litros' in request.POST:
        # Verificar se precisa fazer login primeiro
        if not request.user.is_authenticated:
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    # Garantir que a sessão seja salva antes de continuar
                    request.session.save()
                    # Continuar processamento após login
                else:
                    messages.error(request, 'Usuário ou senha incorretos. Por favor, verifique suas credenciais.')
                    # Recriar formulário para tentar novamente
                    responsavel_usuario = None
                    try:
                        if hasattr(request.user, 'militar'):
                            responsavel_usuario = request.user.militar
                    except:
                        pass
                    
                    initial = {
                        'viatura': viatura,
                        'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                        'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                    }
                    if responsavel_usuario:
                        initial['responsavel'] = responsavel_usuario
                    form = AbastecimentoViaturaForm(initial=initial)
                    if 'responsavel' in form.fields:
                        form.fields['responsavel'].widget = forms.HiddenInput()
                    
                    # Preparar formulário de manutenção também
                    initial_manutencao = {
                        'viatura': viatura,
                        'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                    }
                    if responsavel_usuario:
                        initial_manutencao['responsavel'] = responsavel_usuario
                    form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                    if 'responsavel' in form_manutencao.fields:
                        form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                    
                    # Preparar formulário de troca de óleo também
                    initial_troca_oleo = {
                        'viatura': viatura,
                        'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                    }
                    if responsavel_usuario:
                        initial_troca_oleo['responsavel'] = responsavel_usuario
                    form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                    if 'responsavel' in form_troca_oleo.fields:
                        form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                    
                    context = {
                        'form': form,
                        'form_manutencao': form_manutencao,
                        'form_troca_oleo': form_troca_oleo,
                        'viatura': viatura,
                        'ultimo_abastecimento': ultimo_abastecimento,
                        'ultima_manutencao': ultima_manutencao,
                        'ultima_troca_oleo': ultima_troca_oleo,
                        'rodagem_em_andamento': rodagem_em_andamento,
                        'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                        'responsavel_usuario': responsavel_usuario,
                        'show_login': True,  # Mostrar campos de login
                    }
                    return render(request, 'militares/abastecimento_form_mobile.html', context)
            else:
                messages.error(request, 'É necessário fazer login para registrar o abastecimento.')
                # Recriar formulário
                initial = {
                    'viatura': viatura,
                    'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                    'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                }
                form = AbastecimentoViaturaForm(initial=initial)
                if 'responsavel' in form.fields:
                    form.fields['responsavel'].widget = forms.HiddenInput()
                
                # Preparar formulário de manutenção também
                initial_manutencao = {
                    'viatura': viatura,
                    'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                }
                form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                if 'responsavel' in form_manutencao.fields:
                    form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                
                # Preparar formulário de troca de óleo também
                initial_troca_oleo = {
                    'viatura': viatura,
                    'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                }
                form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                if 'responsavel' in form_troca_oleo.fields:
                    form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                
                responsavel_usuario = None
                context = {
                    'form': form,
                    'form_manutencao': form_manutencao,
                    'form_troca_oleo': form_troca_oleo,
                    'viatura': viatura,
                    'ultimo_abastecimento': ultimo_abastecimento,
                    'ultima_manutencao': ultima_manutencao,
                    'ultima_troca_oleo': ultima_troca_oleo,
                    'rodagem_em_andamento': rodagem_em_andamento,
                    'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                    'responsavel_usuario': responsavel_usuario,
                    'show_login': True,
                }
                return render(request, 'militares/abastecimento_form_mobile.html', context)
        
        # Se chegou aqui, usuário está autenticado, processar formulário de abastecimento
        if request.user.is_authenticated:
            form = AbastecimentoViaturaForm(request.POST)
            if form.is_valid():
                abastecimento = form.save(commit=False)
                abastecimento.viatura = viatura
                abastecimento.criado_por = request.user
                
                # Obter militar do usuário para usar como responsável
                responsavel_usuario = None
                try:
                    if hasattr(request.user, 'militar'):
                        responsavel_usuario = request.user.militar
                except:
                    pass
                
                # Sempre usar o militar vinculado ao usuário logado como responsável (não pode ser alterado)
                if responsavel_usuario:
                    abastecimento.responsavel = responsavel_usuario
                    
                    abastecimento.save()
                    messages.success(
                        request, 
                        f'Abastecimento registrado com sucesso! {abastecimento.quantidade_litros}L de {abastecimento.get_tipo_combustivel_display()} para {viatura.placa}.'
                    )
                    return redirect('militares:abastecimento_qr_success', abastecimento_id=abastecimento.pk)
                else:
                    messages.error(request, 'Você não está vinculado a um militar. Entre em contato com o administrador.')
                    # Recriar form com valores iniciais
                    responsavel_usuario = None
                    try:
                        if hasattr(request.user, 'militar'):
                            responsavel_usuario = request.user.militar
                    except:
                        pass
                    
                    initial = {
                        'viatura': viatura,
                        'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                        'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                    }
                    if responsavel_usuario:
                        initial['responsavel'] = responsavel_usuario
                    form = AbastecimentoViaturaForm(initial=initial)
                    if 'responsavel' in form.fields:
                        form.fields['responsavel'].widget = forms.HiddenInput()
                    # Preparar formulário de manutenção também
                    initial_manutencao = {
                        'viatura': viatura,
                        'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                    }
                    if responsavel_usuario:
                        initial_manutencao['responsavel'] = responsavel_usuario
                    form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                    if 'responsavel' in form_manutencao.fields:
                        form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                    
                    # Preparar formulário de troca de óleo também
                    initial_troca_oleo = {
                        'viatura': viatura,
                        'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                    }
                    if responsavel_usuario:
                        initial_troca_oleo['responsavel'] = responsavel_usuario
                    form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                    if 'responsavel' in form_troca_oleo.fields:
                        form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                    
                    context = {
                        'form': form,
                        'form_manutencao': form_manutencao,
                        'form_troca_oleo': form_troca_oleo,
                        'viatura': viatura,
                        'ultimo_abastecimento': ultimo_abastecimento,
                        'ultima_manutencao': ultima_manutencao,
                        'ultima_troca_oleo': ultima_troca_oleo,
                        'rodagem_em_andamento': rodagem_em_andamento,
                        'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                        'responsavel_usuario': None,
                        'show_login': False,
                    }
                    return render(request, 'militares/abastecimento_form_mobile.html', context)
            else:
                # Form inválido, reexibir com erros
                if 'responsavel' in form.fields:
                    form.fields['responsavel'].widget = forms.HiddenInput()
                responsavel_usuario = None
                try:
                    if hasattr(request.user, 'militar'):
                        responsavel_usuario = request.user.militar
                except:
                    pass
                
                # Preparar formulário de manutenção também
                initial_manutencao = {
                    'viatura': viatura,
                    'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                }
                form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                if 'responsavel' in form_manutencao.fields:
                    form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                
                # Recriar form_troca_oleo
                initial_troca_oleo = {
                    'viatura': viatura,
                    'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                }
                form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                if 'responsavel' in form_troca_oleo.fields:
                    form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                
                context = {
                    'form': form,
                    'form_manutencao': form_manutencao,
                    'form_troca_oleo': form_troca_oleo,
                    'viatura': viatura,
                    'ultimo_abastecimento': ultimo_abastecimento,
                    'ultima_manutencao': ultima_manutencao,
                    'ultima_troca_oleo': ultima_troca_oleo,
                    'rodagem_em_andamento': rodagem_em_andamento,
                    'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                    'responsavel_usuario': responsavel_usuario,
                    'show_login': False,
                }
                return render(request, 'militares/abastecimento_form_mobile.html', context)
    
    # Se POST do formulário de manutenção
    elif request.method == 'POST' and 'tipo_manutencao' in request.POST:
        # Verificar se precisa fazer login primeiro
        if not request.user.is_authenticated:
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    request.session.save()
                else:
                    messages.error(request, 'Usuário ou senha incorretos. Por favor, verifique suas credenciais.')
                    # Recriar formulários
                    initial_abastecimento = {
                        'viatura': viatura,
                        'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                        'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                    }
                    initial_manutencao = {
                        'viatura': viatura,
                        'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                    }
                    form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                    form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                    if 'responsavel' in form_abastecimento.fields:
                        form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                    if 'responsavel' in form_manutencao.fields:
                        form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                    
                    responsavel_usuario = None
                    try:
                        if hasattr(request.user, 'militar'):
                            responsavel_usuario = request.user.militar
                    except:
                        pass
                    
                    context = {
                        'form': form_abastecimento,
                        'form_manutencao': form_manutencao,
                        'form_troca_oleo': form_troca_oleo,
                        'viatura': viatura,
                        'ultimo_abastecimento': ultimo_abastecimento,
                        'ultima_manutencao': ultima_manutencao,
                        'ultima_troca_oleo': ultima_troca_oleo,
                        'rodagem_em_andamento': rodagem_em_andamento,
                        'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                        'responsavel_usuario': responsavel_usuario,
                        'show_login': True,
                    }
                    return render(request, 'militares/abastecimento_form_mobile.html', context)
            else:
                messages.error(request, 'É necessário fazer login para registrar a manutenção.')
                # Recriar formulários
                initial_abastecimento = {
                    'viatura': viatura,
                    'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                    'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                }
                initial_manutencao = {
                    'viatura': viatura,
                    'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                }
                form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                initial_troca_oleo = {
                    'viatura': viatura,
                    'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                }
                form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                if 'responsavel' in form_abastecimento.fields:
                    form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                if 'responsavel' in form_manutencao.fields:
                    form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                if 'responsavel' in form_troca_oleo.fields:
                    form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                
                responsavel_usuario = None
                context = {
                    'form': form_abastecimento,
                    'form_manutencao': form_manutencao,
                    'form_troca_oleo': form_troca_oleo,
                    'viatura': viatura,
                    'ultimo_abastecimento': ultimo_abastecimento,
                    'ultima_manutencao': ultima_manutencao,
                    'ultima_troca_oleo': ultima_troca_oleo,
                    'rodagem_em_andamento': rodagem_em_andamento,
                    'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                    'responsavel_usuario': responsavel_usuario,
                    'show_login': True,
                }
                return render(request, 'militares/abastecimento_form_mobile.html', context)
        
        # Se chegou aqui, usuário está autenticado, processar formulário de manutenção
        if request.user.is_authenticated:
            form_manutencao = ManutencaoViaturaForm(request.POST)
            if form_manutencao.is_valid():
                manutencao = form_manutencao.save(commit=False)
                manutencao.viatura = viatura
                manutencao.criado_por = request.user
                
                # Obter militar do usuário para usar como responsável
                responsavel_usuario = None
                try:
                    if hasattr(request.user, 'militar'):
                        responsavel_usuario = request.user.militar
                except:
                    pass
                
                # Sempre usar o militar vinculado ao usuário logado como responsável
                if responsavel_usuario:
                    manutencao.responsavel = responsavel_usuario
                    
                    manutencao.save()
                    messages.success(
                        request, 
                        f'Manutenção registrada com sucesso! {manutencao.get_tipo_manutencao_display()} para {viatura.placa}.'
                    )
                    # Redirecionar de volta para o formulário com mensagem de sucesso (já foi exibida)
                    return redirect('militares:frota_create_mobile', viatura_id=viatura.pk)
                else:
                    messages.error(request, 'Você não está vinculado a um militar. Entre em contato com o administrador.')
                    # Recriar formulários
                    initial_abastecimento = {
                        'viatura': viatura,
                        'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                        'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                    }
                    initial_manutencao = {
                        'viatura': viatura,
                        'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                    }
                    form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                    form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                    if 'responsavel' in form_abastecimento.fields:
                        form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                    if 'responsavel' in form_manutencao.fields:
                        form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                    context = {
                        'form': form_abastecimento,
                        'form_manutencao': form_manutencao,
                        'form_troca_oleo': form_troca_oleo,
                        'viatura': viatura,
                        'ultimo_abastecimento': ultimo_abastecimento,
                        'ultima_manutencao': ultima_manutencao,
                        'ultima_troca_oleo': ultima_troca_oleo,
                        'rodagem_em_andamento': rodagem_em_andamento,
                        'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                        'responsavel_usuario': None,
                        'show_login': False,
                    }
                    return render(request, 'militares/abastecimento_form_mobile.html', context)
            else:
                # Form inválido, reexibir com erros
                if 'responsavel' in form_manutencao.fields:
                    form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                
                # Recriar form de abastecimento
                initial_abastecimento = {
                    'viatura': viatura,
                    'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                    'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                }
                form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                if 'responsavel' in form_abastecimento.fields:
                    form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                
                responsavel_usuario = None
                try:
                    if hasattr(request.user, 'militar'):
                        responsavel_usuario = request.user.militar
                except:
                    pass
                context = {
                    'form': form_abastecimento,
                    'form_manutencao': form_manutencao,
                    'viatura': viatura,
                    'ultimo_abastecimento': ultimo_abastecimento,
                    'ultima_manutencao': ultima_manutencao,
                    'responsavel_usuario': responsavel_usuario,
                    'show_login': False,
                }
                return render(request, 'militares/abastecimento_form_mobile.html', context)
    
    # Se POST do formulário de troca de óleo
    elif request.method == 'POST' and ('tipo_oleo' in request.POST or 'data_troca' in request.POST):
        # Verificar se precisa fazer login primeiro
        if not request.user.is_authenticated:
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    request.session.save()
                else:
                    messages.error(request, 'Usuário ou senha incorretos. Por favor, verifique suas credenciais.')
                    # Recriar formulários
                    initial_abastecimento = {
                        'viatura': viatura,
                        'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                        'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                    }
                    initial_manutencao = {
                        'viatura': viatura,
                        'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                    }
                    initial_troca_oleo = {
                        'viatura': viatura,
                        'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                    }
                    form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                    form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                    form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                    if 'responsavel' in form_abastecimento.fields:
                        form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                    if 'responsavel' in form_manutencao.fields:
                        form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                    if 'responsavel' in form_troca_oleo.fields:
                        form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                    
                    context = {
                        'form': form_abastecimento,
                        'form_manutencao': form_manutencao,
                        'form_troca_oleo': form_troca_oleo,
                        'viatura': viatura,
                        'ultimo_abastecimento': ultimo_abastecimento,
                        'ultima_manutencao': ultima_manutencao,
                        'ultima_troca_oleo': ultima_troca_oleo,
                        'rodagem_em_andamento': rodagem_em_andamento,
                        'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                        'responsavel_usuario': responsavel_usuario,
                        'show_login': True,
                    }
                    return render(request, 'militares/abastecimento_form_mobile.html', context)
        
        # Se chegou aqui, usuário está autenticado, processar formulário de troca de óleo
        if request.user.is_authenticated:
            form_troca_oleo = TrocaOleoViaturaForm(request.POST)
            if form_troca_oleo.is_valid():
                troca_oleo = form_troca_oleo.save(commit=False)
                troca_oleo.viatura = viatura
                troca_oleo.criado_por = request.user
                
                # Obter militar do usuário para usar como responsável
                responsavel_usuario = None
                try:
                    if hasattr(request.user, 'militar'):
                        responsavel_usuario = request.user.militar
                except:
                    pass
                
                # Sempre usar o militar vinculado ao usuário logado como responsável
                if responsavel_usuario:
                    troca_oleo.responsavel = responsavel_usuario
                    
                    troca_oleo.save()
                    messages.success(
                        request, 
                        f'Troca de óleo registrada com sucesso! {troca_oleo.quantidade_litros}L de {troca_oleo.get_tipo_oleo_display()} para {viatura.placa}.'
                    )
                    # Redirecionar de volta para o formulário com mensagem de sucesso
                    return redirect('militares:frota_create_mobile', viatura_id=viatura.pk)
                else:
                    messages.error(request, 'Você não está vinculado a um militar. Entre em contato com o administrador.')
                    # Recriar formulários
                    initial_abastecimento = {
                        'viatura': viatura,
                        'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                        'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                    }
                    initial_manutencao = {
                        'viatura': viatura,
                        'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                    }
                    initial_troca_oleo = {
                        'viatura': viatura,
                        'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
                    }
                    form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                    form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                    form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
                    if 'responsavel' in form_abastecimento.fields:
                        form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                    if 'responsavel' in form_manutencao.fields:
                        form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                    if 'responsavel' in form_troca_oleo.fields:
                        form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                    
                    context = {
                        'form': form_abastecimento,
                        'form_manutencao': form_manutencao,
                        'form_troca_oleo': form_troca_oleo,
                        'viatura': viatura,
                        'ultimo_abastecimento': ultimo_abastecimento,
                        'ultima_manutencao': ultima_manutencao,
                        'ultima_troca_oleo': ultima_troca_oleo,
                        'rodagem_em_andamento': rodagem_em_andamento,
                        'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                        'responsavel_usuario': None,
                        'show_login': False,
                    }
                    return render(request, 'militares/abastecimento_form_mobile.html', context)
            else:
                # Form inválido, reexibir com erros
                if 'responsavel' in form_troca_oleo.fields:
                    form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
                
                # Recriar outros formulários
                initial_abastecimento = {
                    'viatura': viatura,
                    'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
                    'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
                }
                initial_manutencao = {
                    'viatura': viatura,
                    'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
                }
                form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
                form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
                if 'responsavel' in form_abastecimento.fields:
                    form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
                if 'responsavel' in form_manutencao.fields:
                    form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
                
                responsavel_usuario = None
                try:
                    if hasattr(request.user, 'militar'):
                        responsavel_usuario = request.user.militar
                except:
                    pass
                
                context = {
                    'form': form_abastecimento,
                    'form_manutencao': form_manutencao,
                    'form_troca_oleo': form_troca_oleo,
                    'viatura': viatura,
                    'ultimo_abastecimento': ultimo_abastecimento,
                    'ultima_manutencao': ultima_manutencao,
                    'ultima_troca_oleo': ultima_troca_oleo,
                    'rodagem_em_andamento': rodagem_em_andamento,
                    'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
                    'responsavel_usuario': responsavel_usuario,
                    'show_login': False,
                }
                return render(request, 'militares/abastecimento_form_mobile.html', context)
    else:
        # GET request - Preencher formulários com valores iniciais
        initial_abastecimento = {
            'viatura': viatura,
            'km_abastecimento': ultimo_abastecimento.km_abastecimento if ultimo_abastecimento else viatura.km_atual,
            'tipo_combustivel': viatura.combustivel if viatura.combustivel else 'DIESEL',
        }
        
        initial_manutencao = {
            'viatura': viatura,
            'km_manutencao': ultima_manutencao.km_manutencao if ultima_manutencao else viatura.km_atual,
        }
        
        initial_troca_oleo = {
            'viatura': viatura,
            'km_troca': ultima_troca_oleo.km_troca if ultima_troca_oleo else viatura.km_atual,
        }
        
        # Definir responsável como o militar do usuário logado (obrigatório)
        responsavel_usuario = None
        try:
            if hasattr(request.user, 'militar'):
                responsavel_usuario = request.user.militar
                initial_abastecimento['responsavel'] = responsavel_usuario
                initial_manutencao['responsavel'] = responsavel_usuario
                initial_troca_oleo['responsavel'] = responsavel_usuario
        except Exception as e:
            pass
        
        form_abastecimento = AbastecimentoViaturaForm(initial=initial_abastecimento)
        form_manutencao = ManutencaoViaturaForm(initial=initial_manutencao)
        form_troca_oleo = TrocaOleoViaturaForm(initial=initial_troca_oleo)
        
        # Remover o campo responsavel dos formulários (será definido automaticamente)
        if 'responsavel' in form_abastecimento.fields:
            form_abastecimento.fields['responsavel'].widget = forms.HiddenInput()
        if 'responsavel' in form_manutencao.fields:
            form_manutencao.fields['responsavel'].widget = forms.HiddenInput()
        if 'responsavel' in form_troca_oleo.fields:
            form_troca_oleo.fields['responsavel'].widget = forms.HiddenInput()
        
        # Determinar se deve mostrar login
        mostrar_login = not request.user.is_authenticated
        
        context = {
            'form': form_abastecimento,
            'form_manutencao': form_manutencao,
            'form_troca_oleo': form_troca_oleo,
            'viatura': viatura,
            'ultimo_abastecimento': ultimo_abastecimento,
            'ultima_manutencao': ultima_manutencao,
            'ultima_troca_oleo': ultima_troca_oleo,
            'rodagem_em_andamento': rodagem_em_andamento,
            'ultima_rodagem_finalizada': ultima_rodagem_finalizada,
            'responsavel_usuario': responsavel_usuario,
            'show_login': mostrar_login,  # Mostrar login se não estiver autenticado
        }
        
        return render(request, 'militares/abastecimento_form_mobile.html', context)


def abastecimento_qr_success(request, abastecimento_id):
    """
    Página de sucesso após registro de abastecimento via QR Code.
    Acessível sem login obrigatório para permitir acesso após login mobile.
    """
    abastecimento = get_object_or_404(AbastecimentoViatura, pk=abastecimento_id)
    
    context = {
        'abastecimento': abastecimento,
    }
    
    return render(request, 'militares/abastecimento_qr_success.html', context)


def abastecimento_pdf(request, abastecimento_id):
    """
    Gera PDF do abastecimento de viatura no formato de cupom fiscal
    """
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    
    abastecimento = get_object_or_404(AbastecimentoViatura, pk=abastecimento_id)
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        # Tamanho de cupom fiscal (80mm de largura - papel térmico)
        # Altura será automática baseada no conteúdo
        from reportlab.lib.pagesizes import letter
        # 80mm = 3.15 polegadas (inches), altura padrão 11 polegadas
        cupom_width = 80 * 2.83465  # 80mm em pontos (1mm = 2.83465 pontos)
        cupom_height = 11 * 72  # 11 polegadas em pontos
        
        # Criar tamanho customizado para cupom fiscal
        cupom_size = (cupom_width, cupom_height)
        
        # Margens menores para formato cupom fiscal
        doc = SimpleDocTemplate(buffer, pagesize=cupom_size, rightMargin=0.5*cm, leftMargin=0.5*cm, topMargin=0.5*cm, bottomMargin=0.5*cm)
        story = []
        
        # Estilos para cupom fiscal (compacto, tamanho menor)
        styles = getSampleStyleSheet()
        style_header = ParagraphStyle('header', parent=styles['Normal'], alignment=1, fontSize=7, fontName='Helvetica-Bold', spaceAfter=1, leading=8)
        style_header_small = ParagraphStyle('header_small', parent=styles['Normal'], alignment=1, fontSize=6, fontName='Helvetica', spaceAfter=1, leading=7)
        style_title = ParagraphStyle('title', parent=styles['Normal'], alignment=1, fontSize=9, fontName='Helvetica-Bold', spaceAfter=5)
        style_line = ParagraphStyle('line', parent=styles['Normal'], fontSize=8, alignment=0, spaceAfter=3, leftIndent=0)
        style_line_value = ParagraphStyle('line_value', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=2, spaceAfter=3)
        style_total = ParagraphStyle('total', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=1, spaceAfter=5, textColor=colors.HexColor('#000000'))
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=7, alignment=0, spaceAfter=3)
        style_center_small = ParagraphStyle('center_small', parent=styles['Normal'], fontSize=7, alignment=1, spaceAfter=2)
        
        # Logo/Brasão (menor para cupom)
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        logo_img = None
        if os.path.exists(logo_path):
            logo_img = Image(logo_path, width=1.5*cm, height=1.5*cm)
        
        # Cabeçalho com logo ao lado - formato cupom fiscal
        largura_disponivel = cupom_width - (0.5*cm * 2)  # Largura do cupom menos margens
        largura_logo = 1.5*cm if logo_img else 0  # Logo menor para cupom
        largura_texto = largura_disponivel - largura_logo - 0.3*cm
        
        # Textos do cabeçalho (fonte menor para caber em uma linha)
        textos_cabecalho = [
            Paragraph("GOVERNO DO ESTADO DO PIAUÍ", style_header),
            Paragraph("CORPO DE BOMBEIROS MILITAR", style_header),
        ]
        
        # Adicionar OM da viatura (apenas a instância mais específica, sem hierarquia) em maiúsculo
        om_viatura = abastecimento.viatura.get_organizacao_instancia()
        if om_viatura and om_viatura != "Não definido":
            textos_cabecalho.append(Paragraph(om_viatura.upper(), style_header))
        
        # Obter endereço da OM (instância mais específica)
        endereco_om = None
        if abastecimento.viatura.sub_unidade and abastecimento.viatura.sub_unidade.endereco:
            endereco_om = abastecimento.viatura.sub_unidade.endereco
        elif abastecimento.viatura.unidade and abastecimento.viatura.unidade.endereco:
            endereco_om = abastecimento.viatura.unidade.endereco
        elif abastecimento.viatura.grande_comando and abastecimento.viatura.grande_comando.endereco:
            endereco_om = abastecimento.viatura.grande_comando.endereco
        elif abastecimento.viatura.orgao and abastecimento.viatura.orgao.endereco:
            endereco_om = abastecimento.viatura.orgao.endereco
        
        # Adicionar apenas o endereço (sem telefone e site fixos)
        if endereco_om:
            textos_cabecalho.append(Paragraph(endereco_om, style_header_small))
        
        # Logo centralizada acima do cabeçalho
        if logo_img:
            # Criar tabela para centralizar a logo
            logo_table = Table([[logo_img]], colWidths=[largura_disponivel])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(logo_table)
        
        # Adicionar textos do cabeçalho centralizados (já formatados com estilos menores)
        for texto in textos_cabecalho:
            story.append(texto)
        
        story.append(Spacer(1, 5))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Título
        story.append(Paragraph("COMPROVANTE DE ABASTECIMENTO", style_title))
        story.append(Spacer(1, 6))
        
        # Converter data/hora para timezone local (Brasil)
        import pytz
        from django.utils import timezone as django_timezone
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if django_timezone.is_aware(abastecimento.data_abastecimento):
            data_abastecimento_local = abastecimento.data_abastecimento.astimezone(brasilia_tz)
        else:
            data_abastecimento_local = brasilia_tz.localize(abastecimento.data_abastecimento)
        
        data_hora_formatada = data_abastecimento_local.strftime("%d/%m/%Y %H:%M")
        
        # Dados do abastecimento em formato cupom fiscal (linhas simples)
        largura_disponivel_cupom = cupom_width - (0.5*cm * 2)
        
        # Criar tabela com duas colunas: label e valor
        cupom_data = []
        
        # Linha: Viatura
        viatura_info = f"{abastecimento.viatura.placa}"
        if abastecimento.viatura.prefixo:
            viatura_info += f" - {abastecimento.viatura.prefixo}"
        cupom_data.append([
            Paragraph("<b>Viatura:</b>", style_line),
            Paragraph(viatura_info, style_line_value)
        ])
        
        # Linha: Data/Hora
        cupom_data.append([
            Paragraph("<b>Data/Hora:</b>", style_line),
            Paragraph(data_hora_formatada, style_line_value)
        ])
        
        # Linha: Tipo Combustível
        cupom_data.append([
            Paragraph("<b>Tipo Combustível:</b>", style_line),
            Paragraph(abastecimento.get_tipo_combustivel_display(), style_line_value)
        ])
        
        # Linha: Quantidade
        cupom_data.append([
            Paragraph("<b>Quantidade:</b>", style_line),
            Paragraph(f"{abastecimento.quantidade_litros:.2f} L", style_line_value)
        ])
        
        # Linha: Valor Unitário
        cupom_data.append([
            Paragraph("<b>Valor Unitário:</b>", style_line),
            Paragraph(f"R$ {abastecimento.valor_litro:.2f}", style_line_value)
        ])
        
        # Linha: KM
        cupom_data.append([
            Paragraph("<b>KM:</b>", style_line),
            Paragraph(f"{abastecimento.km_abastecimento} km", style_line_value)
        ])
        
        if abastecimento.posto_fornecedor:
            cupom_data.append([
                Paragraph("<b>Posto/Fornecedor:</b>", style_line),
                Paragraph(abastecimento.posto_fornecedor, style_line_value)
            ])
        
        # Criar tabela (ajustada para largura do cupom)
        largura_label = largura_disponivel_cupom * 0.5
        largura_valor = largura_disponivel_cupom * 0.5
        cupom_table = Table(cupom_data, colWidths=[largura_label, largura_valor])
        cupom_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(cupom_table)
        story.append(Spacer(1, 3))
        
        # Valor Total do Combustível
        style_combustivel_total = ParagraphStyle('combustivel_total', parent=styles['Normal'], alignment=2, fontSize=9, fontName='Helvetica-Bold', spaceAfter=5, textColor=colors.HexColor('#000000'))
        story.append(Paragraph(f"<b>Total Combustível: R$ {abastecimento.valor_total:.2f}</b>", style_combustivel_total))
        story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Seção de Aditivos (se houver)
        if abastecimento.com_aditivos and abastecimento.valor_total_aditivo:
            story.append(Spacer(1, 3))
            style_aditivo_title = ParagraphStyle('aditivo_title', parent=styles['Normal'], alignment=0, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3, textColor=colors.HexColor('#0066cc'))
            story.append(Paragraph("<b>ADITIVOS:</b>", style_aditivo_title))
            
            aditivo_data = []
            if abastecimento.tipo_aditivo:
                aditivo_data.append([
                    Paragraph("<b>Tipo:</b>", style_line),
                    Paragraph(abastecimento.tipo_aditivo, style_line_value)
                ])
            if abastecimento.quantidade_aditivo:
                aditivo_data.append([
                    Paragraph("<b>Quantidade:</b>", style_line),
                    Paragraph(f"{abastecimento.quantidade_aditivo:.2f}", style_line_value)
                ])
            if abastecimento.valor_unitario_aditivo:
                aditivo_data.append([
                    Paragraph("<b>Valor Unitário:</b>", style_line),
                    Paragraph(f"R$ {abastecimento.valor_unitario_aditivo:.2f}", style_line_value)
                ])
            if aditivo_data:
                aditivo_table = Table(aditivo_data, colWidths=[largura_label, largura_valor])
                aditivo_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(aditivo_table)
            
            # Valor total dos aditivos
            style_aditivo_total = ParagraphStyle('aditivo_total', parent=styles['Normal'], alignment=2, fontSize=8, fontName='Helvetica-Bold', spaceAfter=5, textColor=colors.HexColor('#0066cc'))
            story.append(Paragraph(f"<b>Total Aditivos: R$ {abastecimento.valor_total_aditivo:.2f}</b>", style_aditivo_total))
            story.append(Spacer(1, 3))
            story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Total destacado (valor total da nota se houver, senão valor do combustível)
        valor_total_final = abastecimento.valor_total_nota if abastecimento.valor_total_nota else abastecimento.valor_total
        story.append(Paragraph(f"<b>TOTAL DA NOTA: R$ {valor_total_final:.2f}</b>", style_total))
        
        # Responsável após o valor total em uma linha
        if abastecimento.responsavel:
            responsavel_texto = f"{abastecimento.responsavel.get_posto_graduacao_display()} {abastecimento.responsavel.nome_completo}"
            style_responsavel = ParagraphStyle('responsavel', parent=styles['Normal'], alignment=1, fontSize=8, fontName='Helvetica', spaceAfter=5, leading=9)
            story.append(Paragraph(responsavel_texto, style_responsavel))
        
        story.append(Spacer(1, 5))
        
        if abastecimento.observacoes:
            story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=3, spaceBefore=0, color=colors.grey))
            story.append(Paragraph("<b>Observações:</b>", style_line))
            story.append(Paragraph(abastecimento.observacoes, style_small))
            story.append(Spacer(1, 5))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=3, spaceBefore=0, color=colors.black))
        story.append(Spacer(1, 3))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        
        # Criar um objeto fake para o abastecimento (para o autenticador)
        class AbastecimentoFake:
            def __init__(self, abastecimento):
                self.id = f"abastecimento_{abastecimento.pk}"
                self.pk = abastecimento.pk
                self.tipo_documento = 'abastecimento'
        
        abastecimento_fake = AbastecimentoFake(abastecimento)
        autenticador = gerar_autenticador_veracidade(abastecimento_fake, request, tipo_documento='abastecimento')
        
        # Redimensionar QR code para cupom (menor)
        from reportlab.platypus import Image as RLImage
        import qrcode
        from io import BytesIO
        
        # Gerar QR code menor para cupom
        url_autenticacao_base = autenticador.get('url_autenticacao', autenticador.get('url', ''))
        
        qr_cupom = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,  # Menor para cupom
            border=2,
        )
        qr_cupom.add_data(url_autenticacao_base)
        qr_cupom.make(fit=True)
        
        qr_img_pil_cupom = qr_cupom.make_image(fill_color="black", back_color="white")
        qr_buffer_cupom = BytesIO()
        qr_img_pil_cupom.save(qr_buffer_cupom, format='PNG')
        qr_buffer_cupom.seek(0)
        qr_img_cupom = RLImage(qr_buffer_cupom, width=1.8*cm, height=1.8*cm)
        
        # Tabela do rodapé: QR + Texto de autenticação (compacto para cupom)
        largura_disponivel_qr = cupom_width - (0.5*cm * 2) - 0.04*cm
        largura_qr_cupom = 1.8*cm  # QR menor para cupom
        largura_texto_qr = largura_disponivel_qr - largura_qr_cupom - 0.2*cm
        
        rodape_data = [
            [qr_img_cupom, Paragraph(autenticador['texto_autenticacao'], style_center_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[largura_qr_cupom, largura_texto_qr])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="cupom_fiscal_abastecimento_{abastecimento.viatura.placa}_{abastecimento.pk}.pdf"'
        
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Abastecimento</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF do abastecimento.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <p><small>{str(e)}</small></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def historico_abastecimento_pdf(request, viatura_id):
    """
    Gera PDF do histórico de abastecimentos com assinatura eletrônica e autenticador de documentos
    """
    import os
    import hashlib
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    from datetime import datetime, time
    import pytz
    from django.db import transaction
    from django.utils import timezone
    
    try:
        viatura = get_object_or_404(Viatura, pk=viatura_id)
        
        # Obter parâmetros
        data_inicio_str = request.GET.get('data_inicio', '')
        data_fim_str = request.GET.get('data_fim', '')
        funcao_assinatura = request.GET.get('funcao_assinatura', '')
        
        if not data_inicio_str or not data_fim_str:
            messages.error(request, 'Período de datas não fornecido.')
            return redirect('militares:abastecimento_por_viatura', viatura_id=viatura_id)
        
        try:
            data_inicio_date = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim_date = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de data inválido.')
            return redirect('militares:abastecimento_por_viatura', viatura_id=viatura_id)
        
        # Filtrar abastecimentos pelo período - BUSCAR TODOS OS ABASTECIMENTOS
        # Usar filtros separados para garantir que todos os registros sejam incluídos
        # IMPORTANTE: Incluir TODOS os abastecimentos independente do status (ativo/inativo)
        
        # Primeiro obter todos os abastecimentos da viatura (ativos e inativos)
        abastecimentos_queryset = AbastecimentoViatura.objects.filter(
            viatura=viatura
        ).select_related('responsavel')
        
        # Filtrar por data início (inclui todos os registros a partir desta data)
        abastecimentos_queryset = abastecimentos_queryset.filter(
            data_abastecimento__date__gte=data_inicio_date
        )
        
        # Filtrar por data fim (inclui todos os registros até esta data)
        abastecimentos_queryset = abastecimentos_queryset.filter(
            data_abastecimento__date__lte=data_fim_date
        )
        
        # Ordenar por data e km
        abastecimentos_queryset = abastecimentos_queryset.order_by('data_abastecimento', 'km_abastecimento')
        
        # IMPORTANTE: Converter para lista ANTES de qualquer processamento
        # Usar list() para forçar avaliação completa do queryset no banco de dados
        # Garantir que estamos pegando TODOS os registros do queryset
        abastecimentos_lista = list(abastecimentos_queryset.all())
        
        if not abastecimentos_lista:
            # DEBUG: Verificar quantos abastecimentos existem (ativos e inativos)
            total_ativos = AbastecimentoViatura.objects.filter(
                viatura=viatura,
                ativo=True
            ).count()
            
            total_inativos = AbastecimentoViatura.objects.filter(
                viatura=viatura,
                ativo=False
            ).count()
            
            total_geral = AbastecimentoViatura.objects.filter(
                viatura=viatura
            ).count()
            
            # Verificar abastecimentos no período independente do status ativo
            abastecimentos_periodo_qualquer = AbastecimentoViatura.objects.filter(
                viatura=viatura,
                data_abastecimento__date__gte=data_inicio_date,
                data_abastecimento__date__lte=data_fim_date
            ).count()
            
            # Obter o primeiro e último abastecimento da viatura para referência
            primeiro_abastecimento = AbastecimentoViatura.objects.filter(
                viatura=viatura
            ).order_by('data_abastecimento').first()
            
            ultimo_abastecimento = AbastecimentoViatura.objects.filter(
                viatura=viatura
            ).order_by('-data_abastecimento').first()
            
            # Retornar página informativa em vez de redirecionar
            url_voltar = reverse('militares:abastecimento_por_viatura', args=[viatura_id])
            
            info_periodo = ""
            if primeiro_abastecimento and ultimo_abastecimento:
                info_periodo = f"""
                    <p><strong>Período dos abastecimentos existentes:</strong></p>
                    <ul>
                        <li>Primeiro abastecimento: {primeiro_abastecimento.data_abastecimento.strftime('%d/%m/%Y %H:%M')} ({'Ativo' if primeiro_abastecimento.ativo else 'Inativo'})</li>
                        <li>Último abastecimento: {ultimo_abastecimento.data_abastecimento.strftime('%d/%m/%Y %H:%M')} ({'Ativo' if ultimo_abastecimento.ativo else 'Inativo'})</li>
                    </ul>
                """
            
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nenhum Abastecimento Encontrado</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 50px; }}
                    .info-box {{ border: 2px solid #ffc107; border-radius: 5px; padding: 20px; 
                                max-width: 700px; margin: 0 auto; background-color: #fff3cd; }}
                    h2 {{ color: #856404; }}
                    p {{ color: #856404; }}
                    ul {{ color: #856404; }}
                    .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                           text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="info-box">
                    <h2>⚠️ Nenhum Abastecimento Encontrado</h2>
                    <p><strong>Período selecionado:</strong> {data_inicio_date.strftime('%d/%m/%Y')} a {data_fim_date.strftime('%d/%m/%Y')}</p>
                    <p><strong>Viatura:</strong> {viatura.placa}</p>
                    <hr>
                    <p><strong>Estatísticas da viatura:</strong></p>
                    <ul>
                        <li>Total de abastecimentos ativos: <strong>{total_ativos}</strong></li>
                        <li>Total de abastecimentos inativos: <strong>{total_inativos}</strong></li>
                        <li>Total geral de abastecimentos: <strong>{total_geral}</strong></li>
                        <li>Abastecimentos no período (qualquer status): <strong>{abastecimentos_periodo_qualquer}</strong></li>
                    </ul>
                    {info_periodo if primeiro_abastecimento else '<p><em>Nenhum abastecimento registrado para esta viatura.</em></p>'}
                    <div style="text-align: center;">
                        <a href="{url_voltar}" class="btn">Voltar para Abastecimentos</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_html, status=200, content_type='text/html')
        
        # Debug: verificar quantos registros foram encontrados
        # import logging
        # logger = logging.getLogger(__name__)
        # logger.info(f"Total de abastecimentos encontrados: {len(abastecimentos_lista)}")
        
        # Calcular estatísticas usando a lista completa
        quantidade_abastecimentos = len(abastecimentos_lista)
        total_litros = sum(float(a.quantidade_litros) for a in abastecimentos_lista)
        total_valor_combustivel = sum(float(a.valor_total) for a in abastecimentos_lista)
        total_valor_aditivo = sum(float(a.valor_total_aditivo or 0) for a in abastecimentos_lista)
        total_valor_nota = sum(float(a.valor_total_nota or a.valor_total) for a in abastecimentos_lista)
        total_valor = total_valor_nota or total_valor_combustivel
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos - seguindo padrão da certidão de férias
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional dinâmico com OM da viatura
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        ]
        
        # Adicionar OM da viatura (apenas a instância mais específica, sem hierarquia)
        om_viatura = viatura.get_organizacao_instancia()
        if om_viatura and om_viatura != "Não definido":
            cabecalho.append(om_viatura.upper())
        
        # Obter endereço da OM (instância mais específica)
        endereco_om = None
        if viatura.sub_unidade and viatura.sub_unidade.endereco:
            endereco_om = viatura.sub_unidade.endereco
        elif viatura.unidade and viatura.unidade.endereco:
            endereco_om = viatura.unidade.endereco
        elif viatura.grande_comando and viatura.grande_comando.endereco:
            endereco_om = viatura.grande_comando.endereco
        elif viatura.orgao and viatura.orgao.endereco:
            endereco_om = viatura.orgao.endereco
        
        # Adicionar endereço da OM se disponível
        if endereco_om:
            cabecalho.append(endereco_om)
        else:
            # Fallback para endereço padrão se não houver endereço na OM
            cabecalho.append("Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490")
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal sublinhado
        story.append(Paragraph("<u>HISTÓRICO DE ABASTECIMENTOS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Dados da viatura e período
        viatura_info = f"{viatura.placa}"
        if viatura.prefixo:
            viatura_info += f" - {viatura.prefixo}"
        if viatura.modelo:
            viatura_info += f" ({viatura.marca} {viatura.modelo})" if viatura.marca else f" ({viatura.modelo})"
        
        texto_dados = (
            f"<b>Viatura:</b> {viatura_info}<br/>"
            f"<b>Período:</b> {data_inicio_date.strftime('%d/%m/%Y')} a {data_fim_date.strftime('%d/%m/%Y')}"
        )
        story.append(Paragraph(texto_dados, style_normal))
        story.append(Spacer(1, 15))
        
        # Tabela de abastecimentos - padrão certidão de férias
        table_data = []
        
        # Cabeçalho com Paragraph (adicionar primeiro)
        table_data.append([
            Paragraph('Data/Hora', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Quantidade (L)', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Valor/Litro', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Valor Total', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('KM', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Tipo', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Responsável', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
        ])
        
        # Processar TODOS os abastecimentos da lista
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        # Verificar quantos abastecimentos foram encontrados
        total_encontrados = len(abastecimentos_lista)
        
        # Iterar sobre TODOS os abastecimentos e adicionar à tabela
        # IMPORTANTE: garantir que estamos processando TODOS
        for idx, abastecimento in enumerate(abastecimentos_lista):
            # Converter data/hora para timezone de Brasília
            if timezone.is_aware(abastecimento.data_abastecimento):
                data_abast_local = abastecimento.data_abastecimento.astimezone(brasilia_tz)
            else:
                data_abast_local = brasilia_tz.localize(abastecimento.data_abastecimento)
            
            data_hora = data_abast_local.strftime("%d/%m/%Y %H:%M")
            responsavel = f"{abastecimento.responsavel.get_posto_graduacao_display()} {abastecimento.responsavel.nome_completo}" if abastecimento.responsavel else "-"
            
            # Criar cada célula da linha como Paragraph separado
            # Garantir que cada linha seja uma nova lista (não reutilizar referências)
            linha_tabela = [
                Paragraph(str(data_hora), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(f"{abastecimento.quantidade_litros:.2f}"), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(f"R$ {abastecimento.valor_litro:.2f}"), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(f"R$ {abastecimento.valor_total:.2f}"), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(abastecimento.km_abastecimento), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(abastecimento.get_tipo_combustivel_display()), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(responsavel), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
            ]
            
            # Adicionar linha à tabela - IMPORTANTE: cada append adiciona uma nova linha
            table_data.append(linha_tabela)
        
        # Larguras das colunas (ajustadas para A4)
        col_widths = [3.2*cm, 2.2*cm, 2.2*cm, 2.5*cm, 1.8*cm, 2*cm, 3.1*cm]
        
        # Verificar se todas as linhas foram adicionadas (cabeçalho + dados)
        # Total esperado: 1 (cabeçalho) + total_encontrados (dados)
        total_linhas_esperadas = 1 + total_encontrados
        total_linhas_tabela = len(table_data)
        
        # Criar tabela - garantir que tem pelo menos cabeçalho
        abastecimentos_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        abastecimentos_table.setStyle(TableStyle([
            # Cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Linhas de dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(abastecimentos_table)
        story.append(Spacer(1, 20))
        
        # Estatísticas resumo
        texto_estatisticas = (
            f"<b>Total de Abastecimentos:</b> {quantidade_abastecimentos} | "
            f"<b>Total de Litros:</b> {total_litros:.2f} L<br/>"
            f"<b>Total Combustível:</b> R$ {total_valor_combustivel:.2f} | "
            f"<b>Total Aditivos:</b> R$ {total_valor_aditivo:.2f}<br/>"
            f"<b>Total Geral (Nota):</b> R$ {total_valor_nota:.2f}"
        )
        story.append(Paragraph(texto_estatisticas, ParagraphStyle('estatisticas', parent=styles['Normal'], fontSize=11, alignment=1, spaceAfter=20)))
        story.append(Spacer(1, 30))
        
        # Cidade e Data por extenso (centralizada) - padrão certidão de férias
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter cidade
            if militar_logado and militar_logado.cidade:
                cidade_doc = militar_logado.cidade
            else:
                cidade_doc = "Teresina"
            cidade_estado = f"{cidade_doc} - PI"
        except:
            cidade_estado = "Teresina - PI"
        
        # Data por extenso - usar timezone de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
        
        # Obter função do formulário ou função atual
        if not funcao_assinatura:
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_assinatura = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta) - padrão certidão
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 1*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_assinatura, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                story.append(Spacer(1, 1*cm))
                story.append(Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                story.append(Paragraph(funcao_assinatura, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo - padrão certidão
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                funcao_display = funcao_assinatura
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_assinatura
            
            # Data e hora da assinatura
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M')
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {funcao_display}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13*cm])
            assinatura_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
            ]))
            
            story.append(assinatura_table)
        except Exception as e:
            # Se houver erro na assinatura, continuar sem ela
            pass
        
        # Adicionar autenticador de documentos ANTES de construir o PDF
        # Espaçamento de 0,10cm entre assinatura e autenticador
        story.append(Spacer(1, 0.10*cm))
        
        # Criar um objeto fake para o histórico (será usado pelo autenticador)
        # O objeto será criado após o build do PDF, então usamos um ID temporário
        class HistoricoFake:
            def __init__(self, viatura_id, data_inicio_date, data_fim_date):
                # Criar um ID único baseado nos parâmetros
                data_inicio_str = data_inicio_date.strftime('%Y-%m-%d')
                data_fim_str = data_fim_date.strftime('%Y-%m-%d')
                self.id = f"historico_{viatura_id}_{data_inicio_str}_{data_fim_str}"
                # Gerar um PK numérico baseado no hash dos parâmetros
                hash_valor = abs(hash(f"{viatura_id}_{data_inicio_str}_{data_fim_str}"))
                self.pk = hash_valor % 100000000  # PK numérico de até 8 dígitos
                self.tipo_documento = 'historico_abastecimento'
        
        historico_fake = HistoricoFake(viatura_id, data_inicio_date, data_fim_date)
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(historico_fake, request, tipo_documento='historico_abastecimento')
        
        # Tabela do rodapé: QR Code + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        # Criar registro do histórico assinado
        brasilia_tz_final = pytz.timezone('America/Sao_Paulo')
        agora_final = timezone.now().astimezone(brasilia_tz_final) if timezone.is_aware(timezone.now()) else brasilia_tz_final.localize(timezone.now())
        timestamp_str = agora_final.strftime('%Y%m%d%H%M%S')
        data_inicio_str = data_inicio_date.strftime('%Y-%m-%d')
        data_fim_str = data_fim_date.strftime('%Y-%m-%d')
        hash_documento = hashlib.sha256(
            f"historico_{viatura_id}_{data_inicio_str}_{data_fim_str}_{timestamp_str}".encode('utf-8')
        ).hexdigest()
        
        with transaction.atomic():
            # Criar registro do histórico
            historico = HistoricoAbastecimentoAssinado.objects.create(
                viatura=viatura,
                data_inicio=data_inicio_date,
                data_fim=data_fim_date,
                total_litros=total_litros,
                total_valor=total_valor,
                quantidade_abastecimentos=quantidade_abastecimentos,
                gerado_por=request.user,
                hash_documento=hash_documento,
            )
            
            # Criar assinatura (verificar se já existe para evitar erro de unique_together)
            assinatura_digital = hashlib.sha256(
                f"{historico.pk}_{request.user.pk}_{funcao_assinatura}_{timestamp_str}".encode('utf-8')
            ).hexdigest()
            
            # Verificar se já existe assinatura para este histórico
            assinatura_existente = AssinaturaHistoricoAbastecimento.objects.filter(
                historico=historico,
                assinado_por=request.user,
                tipo_assinatura='APROVACAO'
            ).first()
            
            if not assinatura_existente:
                # Obter IP de forma segura
                ip_address = request.META.get('REMOTE_ADDR', '') or None
                user_agent_str = request.META.get('HTTP_USER_AGENT', '') or None
                
                AssinaturaHistoricoAbastecimento.objects.create(
                    historico=historico,
                    assinado_por=request.user,
                    tipo_assinatura='APROVACAO',
                    funcao_assinatura=funcao_assinatura,
                    tipo_midia='ELETRONICA',
                    hash_documento=hash_documento,
                    timestamp=timestamp_str,
                    assinatura_digital=assinatura_digital,
                    ip_assinatura=ip_address if ip_address else None,
                    user_agent=user_agent_str,
                )
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="historico_abastecimentos_{viatura.placa}_{data_inicio_date.strftime("%Y%m%d")}_a_{data_fim_date.strftime("%Y%m%d")}.pdf"'
        
        return response
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        # Log do erro completo para debug
        print(f"ERRO ao gerar PDF do histórico de abastecimentos: {str(e)}")
        print(f"Traceback completo:\n{error_traceback}")
        
        # Retornar página de erro em vez de redirecionar
        url_voltar = reverse('militares:abastecimento_por_viatura', args=[viatura_id])
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Histórico de Abastecimentos</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; text-align: left; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                pre {{ background-color: #fff; padding: 10px; border-radius: 3px; overflow-x: auto; font-size: 11px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                       text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .btn:hover {{ background-color: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF do Histórico de Abastecimentos</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF:</strong></p>
                <p><code>{str(e)}</code></p>
                <details>
                    <summary style="cursor: pointer; color: #721c24; margin-top: 10px;"><strong>Detalhes do Erro (clique para expandir)</strong></summary>
                    <pre>{error_traceback}</pre>
                </details>
                <div style="text-align: center;">
                    <a href="{url_voltar}" class="btn">Voltar para Abastecimentos</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')
