from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import LicencaEspecial, Militar, PlanoLicencaEspecial
from .forms import LicencaEspecialForm, PlanoLicencaEspecialForm
from .permissoes_hierarquicas import obter_funcao_militar_ativa


class LicencaEspecialListView(LoginRequiredMixin, ListView):
    """Lista todas as licenças especiais"""
    
    model = LicencaEspecial
    template_name = 'militares/licenca_especial_list.html'
    context_object_name = 'licencas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = LicencaEspecial.objects.select_related('militar', 'cadastrado_por', 'plano')
        
        # Aplicar filtros
        filtro_nome = self.request.GET.get('filtro_nome', '').strip()
        filtro_cpf = self.request.GET.get('filtro_cpf', '').strip()
        status = self.request.GET.get('status')
        decenio = self.request.GET.get('decenio')
        
        if filtro_nome:
            queryset = queryset.filter(
                Q(militar__nome_completo__icontains=filtro_nome) |
                Q(militar__nome_guerra__icontains=filtro_nome)
            )
        
        if filtro_cpf:
            # Remove caracteres não numéricos do CPF para busca
            cpf_limpo = ''.join(filter(str.isdigit, filtro_cpf))
            if cpf_limpo:
                queryset = queryset.filter(militar__cpf__icontains=cpf_limpo)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if decenio:
            queryset = queryset.filter(decenio=decenio)
        
        # Ordenar por hierarquia militar
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        queryset = queryset.annotate(
            ordem_hierarquia=hierarquia_ordem
        ).select_related('militar')
        
        queryset = queryset.order_by(
            'ordem_hierarquia',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo'
        )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Estatísticas gerais
        context['total_licencas'] = LicencaEspecial.objects.count()
        context['total_planejadas'] = LicencaEspecial.objects.filter(status='PLANEJADA').count()
        context['total_gozando'] = LicencaEspecial.objects.filter(status='GOZANDO').count()
        context['total_gozadas'] = LicencaEspecial.objects.filter(status='GOZADA').count()
        context['total_canceladas'] = LicencaEspecial.objects.filter(status='CANCELADA').count()
        
        # Filtros aplicados
        context['filtro_nome'] = self.request.GET.get('filtro_nome', '').strip()
        context['filtro_cpf'] = self.request.GET.get('filtro_cpf', '').strip()
        context['filtro_status'] = self.request.GET.get('status', '')
        context['filtro_decenio'] = self.request.GET.get('decenio', '')
        
        return context


class LicencaEspecialCreateView(LoginRequiredMixin, CreateView):
    """Cria nova licença especial"""
    
    model = LicencaEspecial
    form_class = LicencaEspecialForm
    template_name = 'militares/licenca_especial_form.html'
    success_url = reverse_lazy('militares:licenca_especial_list')
    
    def get_initial(self):
        initial = super().get_initial()
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                initial['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        with transaction.atomic():
            form.instance.cadastrado_por = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, f'Licença especial registrada com sucesso para {self.object.militar.nome_guerra}!')
            return response


class LicencaEspecialDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de licença especial"""
    
    model = LicencaEspecial
    template_name = 'militares/licenca_especial_detail.html'
    context_object_name = 'licenca'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['duracao_dias'] = self.object.duracao_dias
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


class LicencaEspecialUpdateView(LoginRequiredMixin, UpdateView):
    """Edita licença especial"""
    
    model = LicencaEspecial
    form_class = LicencaEspecialForm
    template_name = 'militares/licenca_especial_form.html'
    success_url = reverse_lazy('militares:licenca_especial_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Licença especial atualizada com sucesso!')
        return response


class LicencaEspecialDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui licença especial"""
    
    model = LicencaEspecial
    template_name = 'militares/licenca_especial_confirm_delete.html'
    context_object_name = 'licenca'
    success_url = reverse_lazy('militares:licenca_especial_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        militar = self.object.militar
        
        # Excluir a licença
        messages.success(self.request, 'Licença especial excluída com sucesso!')
        response = super().delete(request, *args, **kwargs)
        
        # Após excluir, verificar se o militar precisa voltar para PRONTO
        if militar and militar.situacao == 'AFASTAMENTO_LICENCA_ESPECIAL':
            # Verificar se ainda há outras licenças ou férias ativas (GOZANDO) para este militar
            tem_licenca_ativa = LicencaEspecial.objects.filter(
                militar=militar,
                status='GOZANDO'
            ).exists()
            tem_ferias_ativa = militar.ferias.filter(status='GOZANDO').exists()
            
            # Se não há outras licenças ou férias ativas, voltar o militar para PRONTO
            if not tem_licenca_ativa and not tem_ferias_ativa:
                militar.situacao = 'PRONTO'
                militar.save(update_fields=['situacao'])
        
        return response


# ========== VIEWS PARA PLANOS DE LICENÇAS ESPECIAIS ==========

class PlanoLicencaEspecialListView(LoginRequiredMixin, ListView):
    """Lista todos os planos de licenças especiais"""
    
    model = PlanoLicencaEspecial
    template_name = 'militares/plano_licenca_especial_list.html'
    context_object_name = 'planos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PlanoLicencaEspecial.objects.select_related('criado_por').prefetch_related('licencas_especiais').order_by('-ano_plano', '-data_criacao')
        
        # Aplicar filtros
        ano_plano = self.request.GET.get('ano_plano')
        status = self.request.GET.get('status')
        
        if ano_plano:
            queryset = queryset.filter(ano_plano=ano_plano)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Estatísticas gerais
        context['total_planos'] = PlanoLicencaEspecial.objects.count()
        context['total_licencas'] = LicencaEspecial.objects.count()
        context['total_planejadas'] = LicencaEspecial.objects.filter(status='PLANEJADA').count()
        context['total_gozando'] = LicencaEspecial.objects.filter(status='GOZANDO').count()
        context['total_gozadas'] = LicencaEspecial.objects.filter(status='GOZADA').count()
        
        # Filtros aplicados
        context['filtro_ano_plano'] = self.request.GET.get('ano_plano', '')
        context['filtro_status'] = self.request.GET.get('status', '')
        
        # Obter OMs disponíveis para filtro do PDF
        from .forms import get_organizacoes_hierarquicas
        context['oms_disponiveis'] = get_organizacoes_hierarquicas()
        
        # Obter meses disponíveis das licenças especiais (para filtro do PDF)
        meses_disponiveis = []
        licencas_existentes = LicencaEspecial.objects.filter(
            status__in=['PLANEJADA', 'GOZANDO', 'GOZADA']
        ).values_list('data_inicio', flat=True).distinct()
        
        meses_portugues = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        meses_anos = set()
        for data in licencas_existentes:
            if data:
                meses_anos.add((data.month, data.year))
        
        meses_ordenados = sorted(meses_anos, key=lambda x: (x[1], x[0]), reverse=True)
        for mes_num, ano in meses_ordenados:
            meses_disponiveis.append({
                'valor': f"{ano}-{mes_num:02d}",
                'nome': f"{meses_portugues[mes_num]}/{ano}"
            })
        
        context['meses_disponiveis'] = meses_disponiveis
        
        # Adicionar informações de homologação para cada plano
        planos_com_homologacao = {}
        for plano in context['planos']:
            # Excluir licenças canceladas do cálculo
            todas_licencas = plano.licencas_especiais.exclude(status='CANCELADA')
            total_licencas = todas_licencas.count()
            licencas_homologadas = 0
            licencas_nao_homologadas_count = 0
            
            for licenca in todas_licencas:
                if licenca.observacoes and '✓ Homologado em' in licenca.observacoes:
                    licencas_homologadas += 1
                else:
                    licencas_nao_homologadas_count += 1
            
            planos_com_homologacao[plano.pk] = {
                'total_licencas': total_licencas,
                'licencas_homologadas': licencas_homologadas,
                'licencas_nao_homologadas': licencas_nao_homologadas_count,
                'todas_homologadas': licencas_nao_homologadas_count == 0 and total_licencas > 0
            }
        
        context['planos_homologacao'] = planos_com_homologacao
        
        return context


class PlanoLicencaEspecialCreateView(LoginRequiredMixin, CreateView):
    """Cria novo plano de licenças especiais"""
    model = PlanoLicencaEspecial
    form_class = PlanoLicencaEspecialForm
    template_name = 'militares/plano_licenca_especial_form.html'
    success_url = reverse_lazy('militares:plano_licenca_especial_list')
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, f'Plano de Licenças Especiais criado com sucesso!')
        return super().form_valid(form)


class PlanoLicencaEspecialDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de um plano de licenças especiais"""
    model = PlanoLicencaEspecial
    template_name = 'militares/plano_licenca_especial_detail.html'
    context_object_name = 'plano'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Obter filtros da URL
        filtro_nome = self.request.GET.get('filtro_nome', '').strip()
        filtro_cpf = self.request.GET.get('filtro_cpf', '').strip()
        filtro_status = self.request.GET.get('filtro_status', '').strip()
        filtro_decenio = self.request.GET.get('filtro_decenio', '').strip()
        
        # Construir filtros para licenças do plano
        licencas_queryset = self.object.licencas_especiais.select_related(
            'militar', 'cadastrado_por'
        )
        
        # Aplicar filtros
        if filtro_nome:
            licencas_queryset = licencas_queryset.filter(
                Q(militar__nome_completo__icontains=filtro_nome) |
                Q(militar__nome_guerra__icontains=filtro_nome)
            )
        
        if filtro_cpf:
            # Remove caracteres não numéricos do CPF para busca
            cpf_limpo = ''.join(filter(str.isdigit, filtro_cpf))
            if cpf_limpo:
                licencas_queryset = licencas_queryset.filter(militar__cpf__icontains=cpf_limpo)
        
        if filtro_status:
            licencas_queryset = licencas_queryset.filter(status=filtro_status)
        
        if filtro_decenio:
            licencas_queryset = licencas_queryset.filter(decenio=filtro_decenio)
        
        # Ordenar por hierarquia militar
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        licencas_queryset = licencas_queryset.annotate(
            ordem_hierarquia=hierarquia_ordem
        ).select_related('militar')
        
        licencas_queryset = licencas_queryset.order_by(
            'ordem_hierarquia',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo'
        )
        
        context['licencas'] = licencas_queryset
        context['filtro_nome'] = filtro_nome
        context['filtro_cpf'] = filtro_cpf
        context['filtro_status'] = filtro_status
        context['filtro_decenio'] = filtro_decenio
        
        return context


class PlanoLicencaEspecialUpdateView(LoginRequiredMixin, UpdateView):
    """Edita plano de licenças especiais"""
    model = PlanoLicencaEspecial
    form_class = PlanoLicencaEspecialForm
    template_name = 'militares/plano_licenca_especial_form.html'
    success_url = reverse_lazy('militares:plano_licenca_especial_list')
    
    def form_valid(self, form):
        # Registrar alterações antes de salvar
        plano_antigo = PlanoLicencaEspecial.objects.get(pk=self.object.pk)
        plano_novo = form.save(commit=False)
        self._registrar_alteracoes(plano_antigo, plano_novo)
        
        messages.success(self.request, f'Plano de Licenças Especiais atualizado com sucesso!')
        return super().form_valid(form)
    
    def _registrar_alteracoes(self, plano_antigo, plano_novo):
        """Registra as alterações realizadas no plano"""
        try:
            from .models import HistoricoAlteracaoPlanoLicencaEspecial
        except ImportError:
            # Modelo de histórico não existe, pular registro de alterações
            return
        
        # Lista de campos para monitorar alterações
        campos_monitorados = [
            'titulo', 'ano_plano', 'descricao', 'status',
            'documento_referencia', 'numero_documento'
        ]
        
        for campo in campos_monitorados:
            try:
                valor_antigo = getattr(plano_antigo, campo, None)
                valor_novo = getattr(plano_novo, campo, None)
            except:
                continue  # Campo não existe, pular
            
            # Formatar valores None, ForeignKeys, datas, etc
            def formatar_valor(valor):
                if valor is None:
                    return ''
                if hasattr(valor, 'strftime'):  # Datetime/Date
                    return valor.strftime('%d/%m/%Y %H:%M')
                if hasattr(valor, '__str__') and not isinstance(valor, (str, int, float, bool)):
                    return str(valor)
                return str(valor)
            
            valor_antigo_str = formatar_valor(valor_antigo)
            valor_novo_str = formatar_valor(valor_novo)
            
            # Se houve alteração, registrar
            if valor_antigo_str != valor_novo_str:
                try:
                    HistoricoAlteracaoPlanoLicencaEspecial.objects.create(
                        plano=plano_novo,
                        campo_alterado=campo.replace('_', ' ').title(),
                        valor_anterior=valor_antigo_str,
                        valor_novo=valor_novo_str,
                        alterado_por=self.request.user
                    )
                except Exception:
                    # Se houver erro ao criar o histórico, apenas continuar
                    # Não deve bloquear a edição do plano
                    pass


class PlanoLicencaEspecialDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui plano de licenças especiais"""
    model = PlanoLicencaEspecial
    template_name = 'militares/plano_licenca_especial_confirm_delete.html'
    context_object_name = 'plano'
    success_url = reverse_lazy('militares:plano_licenca_especial_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Plano de Licenças Especiais excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
@require_http_methods(["POST"])
def aprovar_plano_licenca_especial(request, pk):
    """Aprova um plano de licenças especiais com verificação de homologação"""
    try:
        plano = get_object_or_404(PlanoLicencaEspecial, pk=pk)
        
        # Verificar se já está aprovado
        if plano.status in ['APROVADO', 'PUBLICADO']:
            messages.warning(request, 'Este plano já está aprovado!')
            return redirect('militares:plano_licenca_especial_list')
        
        if plano.status == 'CANCELADO':
            messages.error(request, 'Plano cancelado não pode ser aprovado!')
            return redirect('militares:plano_licenca_especial_list')
        
        # Verificar se todas as licenças especiais do plano estão homologadas
        # Excluir licenças canceladas do cálculo
        todas_licencas = plano.licencas_especiais.exclude(status='CANCELADA')
        licencas_nao_homologadas = []
        
        for licenca in todas_licencas:
            # Verificar se tem marcação de homologação nas observações
            tem_homologacao = False
            if licenca.observacoes and '✓ Homologado em' in licenca.observacoes:
                tem_homologacao = True
            
            if not tem_homologacao:
                licencas_nao_homologadas.append(licenca)
        
        if licencas_nao_homologadas:
            total_nao_homologadas = len(licencas_nao_homologadas)
            total_licencas = todas_licencas.count()
            messages.error(
                request, 
                f'Não é possível aprovar o plano! {total_nao_homologadas} de {total_licencas} licenças especiais ainda não foram homologadas. '
                f'Por favor, homologue todas as licenças antes de aprovar o plano.'
            )
            return redirect('militares:plano_licenca_especial_detail', pk=pk)
        
        # Obter dados do formulário (opcional, para manter compatibilidade)
        documento_referencia = request.POST.get('documento_referencia', '').strip()
        numero_documento = request.POST.get('numero_documento', '').strip()
        
        # Aprovar o plano
        plano.status = 'APROVADO'
        plano.save()
        
        # Se houver dados de documento, pode salvar (opcional)
        if documento_referencia and numero_documento:
            # Aqui você pode adicionar campos ao modelo se necessário
            pass
        
        messages.success(request, f'Plano "{plano.titulo}" aprovado com sucesso!')
        return redirect('militares:plano_licenca_especial_list')
        
    except Exception as e:
        messages.error(request, f'Erro ao aprovar plano: {str(e)}')
        return redirect('militares:plano_licenca_especial_list')


@login_required
@require_http_methods(["POST"])
def licenca_especial_homologar(request, pk):
    """Homologa licença especial - apenas registra a homologação sem alterar o status"""
    try:
        licenca = get_object_or_404(LicencaEspecial, pk=pk)
        
        # Verificar se já foi homologada
        if licenca.observacoes and '✓ Homologado em' in licenca.observacoes:
            messages.warning(request, f'Esta licença especial já foi homologada!')
            if licenca.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        # Verificar se o plano está em RASCUNHO, APROVADO ou PUBLICADO
        if licenca.plano and licenca.plano.status in ['RASCUNHO', 'APROVADO', 'PUBLICADO']:
            from django.utils import timezone
            
            # Registrar homologação nas observações sem alterar o status
            data_homologacao = timezone.now().strftime('%d/%m/%Y %H:%M')
            homologador = request.user.get_full_name() or request.user.username
            
            if licenca.observacoes:
                licenca.observacoes = f"{licenca.observacoes}\n\n✓ Homologado em {data_homologacao} por {homologador}"
            else:
                licenca.observacoes = f"✓ Homologado em {data_homologacao} por {homologador}"
            
            # NÃO ALTERAR O STATUS - salvar APENAS as observações
            licenca.save(update_fields=['observacoes'])
            
            messages.success(request, f'Licença especial de {licenca.militar.nome_guerra} homologada com sucesso! Status atual: {licenca.get_status_display()}.')
        else:
            messages.error(request, 'Não é possível homologar licença especial deste plano no status atual!')
        
        # Redirecionar para o plano se houver
        if licenca.plano:
            return redirect('militares:plano_licenca_especial_detail', pk=licenca.plano.pk)
        return redirect('militares:licenca_especial_detail', pk=pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao homologar licença especial: {str(e)}')
        return redirect('militares:licenca_especial_list')


@login_required
@require_http_methods(["POST"])
def licenca_especial_desomologar(request, pk):
    """Desomologa licença especial removendo a marcação de homologação das observações"""
    try:
        licenca = get_object_or_404(LicencaEspecial, pk=pk)
        
        # Verificar se foi homologada
        if not licenca.observacoes or '✓ Homologado em' not in licenca.observacoes:
            messages.warning(request, f'Esta licença especial não foi homologada!')
            if licenca.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        # Verificar se o plano está em RASCUNHO, APROVADO ou PUBLICADO
        if licenca.plano and licenca.plano.status in ['RASCUNHO', 'APROVADO', 'PUBLICADO']:
            # Remover a marcação de homologação das observações
            linhas = licenca.observacoes.split('\n')
            linhas_filtradas = []
            dentro_homologacao = False
            
            for linha in linhas:
                if '✓ Homologado em' in linha:
                    dentro_homologacao = True
                    continue
                if dentro_homologacao and linha.strip() == '':
                    dentro_homologacao = False
                    continue
                if not dentro_homologacao:
                    linhas_filtradas.append(linha)
            
            # Remover linhas vazias no final
            while linhas_filtradas and linhas_filtradas[-1].strip() == '':
                linhas_filtradas.pop()
            
            licenca.observacoes = '\n'.join(linhas_filtradas)
            
            # Salvar APENAS as observações
            licenca.save(update_fields=['observacoes'])
            
            messages.success(request, f'Licença especial de {licenca.militar.nome_guerra} desomologada com sucesso!')
        else:
            messages.error(request, 'Não é possível desomologar licença especial deste plano no status atual!')
        
        # Redirecionar para o plano se houver
        if licenca.plano:
            return redirect('militares:plano_licenca_especial_detail', pk=licenca.plano.pk)
        return redirect('militares:licenca_especial_detail', pk=pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao desomologar licença especial: {str(e)}')
        if licenca.plano:
            return redirect('militares:plano_licenca_especial_detail', pk=licenca.plano.pk)
        return redirect('militares:licenca_especial_list')


@login_required
@require_http_methods(["POST"])
def licenca_especial_reprogramar(request, pk):
    """Reprograma licença especial: desativa a atual e cria uma nova"""
    try:
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        licenca_original = get_object_or_404(LicencaEspecial, pk=pk)
        
        # Verificar se o plano está aprovado - só permite reprogramar após aprovação (mas não bloqueia se não houver plano)
        if licenca_original.plano and licenca_original.plano.status not in ['APROVADO', 'PUBLICADO']:
            # Aviso, mas não bloqueia completamente
            messages.warning(request, 'A reprogramação é recomendada apenas após o plano estar aprovado, mas será permitida.')
        
        # Verificar se a licença está em status que permite reprogramação
        if licenca_original.status not in ['PLANEJADA', 'GOZANDO']:
            messages.error(request, f'A reprogramação só é permitida para licenças em status "Planejada" ou "Usufruindo"! Status atual: {licenca_original.get_status_display()}.')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        # Verificar se a licença já foi usufruída - não permitir reprogramar
        if licenca_original.status == 'GOZADA':
            messages.error(request, 'Não é possível reprogramar licença já usufruída!')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        # Também não permitir reprogramar licenças canceladas
        if licenca_original.status == 'CANCELADA':
            messages.error(request, f'Não é possível reprogramar licença com status: {licenca_original.get_status_display()}!')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        motivo_reprogramacao = request.POST.get('motivo_reprogramacao', '').strip()
        nova_data_inicio = request.POST.get('nova_data_inicio', '').strip()
        nova_quantidade_meses = request.POST.get('nova_quantidade_meses', '').strip()
        
        # Validar campos obrigatórios
        if not motivo_reprogramacao:
            messages.error(request, 'É obrigatório informar o motivo da reprogramação!')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        if not nova_data_inicio:
            messages.error(request, 'É obrigatório informar a nova data de início!')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        # Converter data de início
        try:
            data_inicio_obj = datetime.strptime(nova_data_inicio, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de data inválido!')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        # Se a licença está GOZANDO, calcular meses já gozados e reprogramar apenas o restante
        meses_ja_gozados = 0
        meses_restantes = 0
        if licenca_original.status == 'GOZANDO':
            from datetime import date
            hoje = date.today()
            
            # Obter data fim da licença em andamento informada pelo usuário
            data_fim_gozando_str = request.POST.get('data_fim_gozando', '').strip()
            if data_fim_gozando_str:
                try:
                    data_fim_gozando = datetime.strptime(data_fim_gozando_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Formato de data de término da licença em andamento inválido!')
                    if licenca_original.plano:
                        return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
                    return redirect('militares:licenca_especial_detail', pk=pk)
            else:
                # Se não informou, usar hoje como padrão
                data_fim_gozando = hoje
            
            # Calcular meses já gozados
            if licenca_original.data_inicio:
                quantidade_meses_original = licenca_original.quantidade_meses
                # Calcular diferença em meses
                meses_ja_gozados = (data_fim_gozando.year - licenca_original.data_inicio.year) * 12 + \
                                 (data_fim_gozando.month - licenca_original.data_inicio.month)
                if data_fim_gozando.day < licenca_original.data_inicio.day:
                    meses_ja_gozados -= 1
                meses_ja_gozados = max(0, min(meses_ja_gozados, quantidade_meses_original))
                meses_restantes = quantidade_meses_original - meses_ja_gozados
            else:
                messages.error(request, 'Licença em andamento sem data de início definida!')
                if licenca_original.plano:
                    return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
                return redirect('militares:licenca_especial_detail', pk=pk)
            
            # Se todos os meses já foram gozados, apenas marcar como GOZADA
            if meses_restantes <= 0:
                licenca_original.quantidade_meses = meses_ja_gozados
                licenca_original.data_fim = data_fim_gozando
                licenca_original.status = 'GOZADA'
                observacao_gozada = f"Licença concluída ao reprogramar. Período gozado: {licenca_original.data_inicio.strftime('%d/%m/%Y')} a {data_fim_gozando.strftime('%d/%m/%Y')} ({meses_ja_gozados} meses). Motivo da reprogramação: {motivo_reprogramacao}"
                if licenca_original.observacoes:
                    licenca_original.observacoes = f"{licenca_original.observacoes}\n\n{observacao_gozada}"
                else:
                    licenca_original.observacoes = observacao_gozada
                licenca_original.save()
                
                messages.success(request, f'Licença especial de {licenca_original.militar.nome_guerra} já estava concluída ({meses_ja_gozados} meses gozados). Status atualizado para GOZADA.')
                if licenca_original.plano:
                    return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
                return redirect('militares:licenca_especial_detail', pk=pk)
            
            # Ainda há meses restantes - reprogramar apenas os meses restantes
            quantidade_meses_nova = meses_restantes
            
            # Calcular data_fim automaticamente baseada na nova data_inicio e quantidade de meses restantes
            data_fim_ajustada = data_inicio_obj + relativedelta(months=quantidade_meses_nova, days=-1)
            
            # Ajustar licença original
            licenca_original.quantidade_meses = meses_ja_gozados
            licenca_original.data_fim = data_fim_gozando
            licenca_original.status = 'GOZADA'
            observacao_gozada = f"Parte da licença gozada. Período gozado: {licenca_original.data_inicio.strftime('%d/%m/%Y')} a {data_fim_gozando.strftime('%d/%m/%Y')} ({meses_ja_gozados} meses de {quantidade_meses_original} totais). {meses_restantes} meses restantes reprogramados. Motivo da reprogramação: {motivo_reprogramacao}"
            if licenca_original.observacoes:
                licenca_original.observacoes = f"{licenca_original.observacoes}\n\n{observacao_gozada}"
            else:
                licenca_original.observacoes = observacao_gozada
            licenca_original.save()
            
            # Criar nova licença apenas com os meses restantes
            observacoes_nova = f"Reprogramação da licença anterior (ID: {licenca_original.pk}). {meses_ja_gozados} meses já foram gozados, reprogramando {meses_restantes} meses restantes. Motivo: {motivo_reprogramacao}."
            
            nova_licenca = LicencaEspecial.objects.create(
                plano=licenca_original.plano,
                militar=licenca_original.militar,
                decenio=licenca_original.decenio,
                quantidade_meses=quantidade_meses_nova,
                data_inicio=data_inicio_obj,
                data_fim=data_fim_ajustada,
                status='PLANEJADA',
                observacoes=observacoes_nova,
                documento_referencia=licenca_original.documento_referencia,
                numero_documento=licenca_original.numero_documento,
                cadastrado_por=request.user
            )
            
            messages.success(request, f'Licença especial de {licenca_original.militar.nome_guerra} reprogramada com sucesso! {meses_ja_gozados} meses já gozados foram registrados, {meses_restantes} meses restantes foram reprogramados.')
            
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=nova_licenca.pk)
        
        # Se está PLANEJADA, usar o fluxo normal de reprogramação
        if not nova_quantidade_meses:
            messages.error(request, 'É obrigatório informar a nova quantidade de meses!')
            if licenca_original.plano:
                return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
            return redirect('militares:licenca_especial_detail', pk=pk)
        
        quantidade_meses_nova = int(nova_quantidade_meses)
        data_fim_ajustada = data_inicio_obj + relativedelta(months=quantidade_meses_nova, days=-1)
        
        # Marcar licença original como cancelada
        licenca_original.status = 'CANCELADA'
        observacao_cancelada = f"Licença cancelada ao reprogramar. Motivo: {motivo_reprogramacao}."
        if licenca_original.observacoes:
            licenca_original.observacoes = f"{licenca_original.observacoes}\n\n{observacao_cancelada}"
        else:
            licenca_original.observacoes = observacao_cancelada
        licenca_original.save()
        
        # Criar nova licença
        observacoes_nova = f"Reprogramação da licença anterior (ID: {licenca_original.pk}). Motivo: {motivo_reprogramacao}."
        
        nova_licenca = LicencaEspecial.objects.create(
            plano=licenca_original.plano,
            militar=licenca_original.militar,
            decenio=licenca_original.decenio,
            quantidade_meses=quantidade_meses_nova,
            data_inicio=data_inicio_obj,
            data_fim=data_fim_ajustada,
            status='PLANEJADA',
            observacoes=observacoes_nova,
            documento_referencia=licenca_original.documento_referencia,
            numero_documento=licenca_original.numero_documento,
            cadastrado_por=request.user
        )
        
        messages.success(request, f'Licença especial de {licenca_original.militar.nome_guerra} reprogramada com sucesso!')
        
        if licenca_original.plano:
            return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
        return redirect('militares:licenca_especial_detail', pk=nova_licenca.pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao reprogramar licença especial: {str(e)}')
        if licenca_original.plano:
            return redirect('militares:plano_licenca_especial_detail', pk=licenca_original.plano.pk)
        return redirect('militares:licenca_especial_list')


class LicencaEspecialCreateParaPlanoView(LoginRequiredMixin, CreateView):
    """Cria novas licenças especiais vinculadas a um plano específico"""
    model = LicencaEspecial
    form_class = LicencaEspecialForm
    template_name = 'militares/licenca_especial_form.html'
    
    def get_success_url(self):
        return reverse_lazy('militares:plano_licenca_especial_detail', kwargs={'pk': self.kwargs.get('plano_id')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plano_id = self.kwargs.get('plano_id')
        
        if plano_id:
            try:
                plano = PlanoLicencaEspecial.objects.get(pk=plano_id)
                context['plano'] = plano
            except PlanoLicencaEspecial.DoesNotExist:
                pass
        
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        plano_id = self.kwargs.get('plano_id')
        militar_id = self.request.GET.get('militar')
        
        if plano_id:
            try:
                plano = PlanoLicencaEspecial.objects.get(pk=plano_id)
                # Não definir plano no initial, será definido no form_valid
            except PlanoLicencaEspecial.DoesNotExist:
                pass
        
        if militar_id:
            try:
                initial['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        
        return initial
    
    def form_valid(self, form):
        plano_id = self.kwargs.get('plano_id')
        form.instance.plano_id = plano_id
        form.instance.cadastrado_por = self.request.user
        
        # Se o plano já tem documento de aprovação, replicar para a nova licença
        if plano_id:
            try:
                plano = PlanoLicencaEspecial.objects.get(pk=plano_id)
                if plano.documento_referencia and plano.numero_documento:
                    if not form.instance.documento_referencia:
                        form.instance.documento_referencia = plano.documento_referencia
                    if not form.instance.numero_documento:
                        form.instance.numero_documento = plano.numero_documento
            except PlanoLicencaEspecial.DoesNotExist:
                pass
        
        response = super().form_valid(form)
        messages.success(self.request, f'Licença especial registrada com sucesso para {self.object.militar.nome_guerra}!')
        return response


@login_required
def licenca_especial_certidao_pdf(request, militar_id):
    """Gera PDF com certidão de licenças especiais de um militar"""
    import os
    from io import BytesIO
    from datetime import date
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    
    militar = get_object_or_404(Militar, pk=militar_id)
    
    # Busca licenças especiais ordenadas por decênio e data de início (apenas as cadastradas)
    licencas_list = LicencaEspecial.objects.filter(militar=militar).exclude(status='CANCELADA').order_by('decenio', 'data_inicio')
    
    if not licencas_list.exists():
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Licenças Especiais</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error-box { border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }
                h2 { color: #721c24; }
                p { color: #721c24; }
                button { background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }
                button:hover { background-color: #c82333; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Licenças Especiais</h2>
                <p><strong>Este militar não possui histórico de licenças especiais para gerar certidão.</strong></p>
                <p>Por favor, cadastre licenças especiais para este militar antes de gerar a certidão.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=400, content_type='text/html')
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos
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
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE GESTÃO DE PESSOAS",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>CERTIDÃO DE LICENÇAS ESPECIAIS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Texto de certificação com dados do militar
        posto_display = militar.get_posto_graduacao_display()
        texto_certificacao = (
            f"Certifico para os devidos fins que conforme os registros funcionais desta instituição, "
            f"foi encontrado que o servidor <b>{posto_display} BM {militar.nome_completo}</b>, "
            f"CPF: <b>{militar.cpf or 'Não informado'}</b>, Matrícula: <b>{militar.matricula}</b>, "
            f"usufruiu licenças especiais decorrentes de decênios trabalhados conforme segue:"
        )
        story.append(Paragraph(texto_certificacao, ParagraphStyle('certificacao', parent=styles['Normal'], fontSize=11, alignment=4, spaceAfter=15)))
        story.append(Spacer(1, 10))
        
        # Tabela única com todas as licenças especiais cadastradas
        # Estilo para células da tabela - leading menor para texto mais compacto
        style_cell = ParagraphStyle('cell', parent=styles['Normal'], fontSize=7, alignment=1, leading=8.5, spaceBefore=0, spaceAfter=0)
        style_cell_header = ParagraphStyle('cell_header', parent=styles['Normal'], fontSize=7, alignment=1, fontName='Helvetica-Bold', leading=9, spaceBefore=0, spaceAfter=0)
        
        # Criar cabeçalho com Paragraphs para garantir quebra de linha
        cabecalho_curto = [
            Paragraph('Decênio', style_cell_header),
            Paragraph('Período<br/>Decênio', style_cell_header),
            Paragraph('Início', style_cell_header),
            Paragraph('Fim', style_cell_header),
            Paragraph('Duração', style_cell_header),
            Paragraph('Status', style_cell_header),
            Paragraph('Documento', style_cell_header)
        ]
        licencas_data = [cabecalho_curto]
        
        # Função auxiliar para quebrar texto longo
        def quebrar_texto(texto, max_chars=25):
            """Quebra texto longo em múltiplas linhas"""
            if not texto or texto == '-':
                return texto
            if len(texto) <= max_chars:
                return texto
            # Tentar quebrar em espaços
            palavras = texto.split()
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                if len(linha_atual + palavra) <= max_chars:
                    linha_atual += palavra + " "
                else:
                    if linha_atual:
                        linhas.append(linha_atual.strip())
                    linha_atual = palavra + " "
            if linha_atual:
                linhas.append(linha_atual.strip())
            return "<br/>".join(linhas)
        
        # Adicionar dados apenas das licenças cadastradas usando Paragraphs
        for licenca in licencas_list:
            documento = ''
            if licenca.documento_referencia and licenca.numero_documento:
                doc_ref = quebrar_texto(licenca.documento_referencia, 30)
                doc_num = quebrar_texto(licenca.numero_documento, 30)
                documento = f"{doc_ref}<br/>{doc_num}"
            elif licenca.documento_referencia:
                documento = quebrar_texto(licenca.documento_referencia, 30)
            elif licenca.numero_documento:
                documento = quebrar_texto(licenca.numero_documento, 30)
            else:
                documento = '-'
            
            periodo_decenio = licenca.periodo_decenio if licenca.periodo_decenio != "-" else '-'
            # Quebrar período do decênio se for muito longo
            periodo_decenio = quebrar_texto(periodo_decenio, 18)
            periodo_decenio = periodo_decenio.replace(' a ', '<br/>a ')
            
            # Quebrar status se for muito longo
            status_display = licenca.get_status_display()
            status_display = quebrar_texto(status_display, 15)
            
            licencas_data.append([
                Paragraph(f"{licenca.decenio}º", style_cell),
                Paragraph(periodo_decenio, style_cell),
                Paragraph(licenca.data_inicio.strftime("%d/%m/%Y"), style_cell),
                Paragraph(licenca.data_fim.strftime("%d/%m/%Y") if licenca.data_fim else '-', style_cell),
                Paragraph(f"{licenca.quantidade_meses} mês{'es' if licenca.quantidade_meses > 1 else ''}", style_cell),
                Paragraph(status_display, style_cell),
                Paragraph(documento, style_cell)
            ])
        
        # Criar tabela com larguras ajustadas
        # A4 width = 21cm, margens = 1.5cm cada = 3cm, largura útil = 18cm
        # Distribuindo: 1.5 + 3.5 + 2.2 + 2.2 + 1.8 + 2.0 + 4.8 = 18cm
        licencas_table = Table(licencas_data, colWidths=[1.5*cm, 3.5*cm, 2.2*cm, 2.2*cm, 1.8*cm, 2.0*cm, 4.8*cm], repeatRows=1)
        licencas_table.setStyle(TableStyle([
            # Cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Linhas de dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        story.append(licencas_table)
        story.append(Spacer(1, 20))
        
        # Texto final
        texto_final = "A presente certidão é emitida a pedido do(a) interessado(a), para fins de comprovação e demais usos legais que se fizerem necessários."
        story.append(Paragraph(texto_final, ParagraphStyle('texto_final', parent=styles['Normal'], fontSize=11, alignment=4, spaceAfter=20)))
        story.append(Spacer(1, 30))
        
        # Cidade e Data por extenso (centralizada)
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
        import pytz
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
        funcao_selecionada = request.GET.get('funcao', '')
        if not funcao_selecionada:
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta)
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 1*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                story.append(Spacer(1, 1*cm))
                story.append(Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Usar função selecionada do formulário
                funcao_display = funcao_selecionada
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_selecionada
            
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
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        # Usar o militar como objeto para gerar o autenticador
        autenticador = gerar_autenticador_veracidade(militar, request, tipo_documento='certidao_licenca_especial')
        
        # Tabela do rodapé: QR + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        buffer.seek(0)
        
        # Retornar PDF para visualização no navegador (sem download automático)
        filename = f'certidao_licenca_especial_{militar.matricula}_{militar.nome_guerra.replace(" ", "_")}.pdf'
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_details = str(e)
        # Log do erro completo para debug (remover traceback em produção se necessário)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar certidão de licenças especiais para militar {militar.pk}: {error_details}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Licenças Especiais</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                .error-detail {{ background-color: #fff; padding: 10px; border-radius: 3px; 
                               margin: 10px 0; font-size: 12px; text-align: left; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Licenças Especiais</h2>
                <p><strong>Ocorreu um erro ao gerar a certidão de licenças especiais.</strong></p>
                <div class="error-detail">
                    <strong>Detalhes do erro:</strong><br>
                    {error_details}
                </div>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def plano_licenca_especial_list_pdf(request):
    """Gera PDF listando licenças especiais agrupadas por mês e ordenadas por hierarquia"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse, FileResponse
    from datetime import datetime
    from django.db.models import Case, When, Value, IntegerField
    from collections import defaultdict
    import pytz
    
    try:
        # Obter parâmetros de filtro
        ano_plano = request.GET.get('ano_plano', '')
        plano_id = request.GET.get('plano_id', '')
        mes_filtro = request.GET.get('mes', '')
        om_filtro = request.GET.get('om', '')
        
        # Buscar licenças especiais
        licencas_queryset = LicencaEspecial.objects.select_related(
            'militar', 'plano'
        ).prefetch_related(
            'militar__lotacoes'
        ).filter(
            status__in=['PLANEJADA', 'GOZANDO', 'GOZADA']
        )
        
        # Aplicar filtros
        if plano_id:
            licencas_queryset = licencas_queryset.filter(plano_id=plano_id)
        elif ano_plano:
            licencas_queryset = licencas_queryset.filter(plano__ano_plano=ano_plano)
        
        # Filtro por mês
        if mes_filtro:
            try:
                ano_mes, mes_num = mes_filtro.split('-')
                ano_mes = int(ano_mes)
                mes_num = int(mes_num)
                from django.db.models import Q
                licencas_queryset = licencas_queryset.filter(
                    Q(data_inicio__year=ano_mes, data_inicio__month=mes_num) |
                    Q(data_fim__year=ano_mes, data_fim__month=mes_num)
                )
            except:
                pass
        
        # Filtro por OM - apenas a instância selecionada (sem ascendência e sem descendência)
        if om_filtro:
            from .models import Lotacao, Orgao, GrandeComando, Unidade, SubUnidade
            from django.db.models import Q
            
            # Identificar tipo de OM e ID - filtrar apenas pela instância exata
            militares_ids = []
            if om_filtro.startswith('orgao_'):
                om_id = int(om_filtro.replace('orgao_', ''))
                lotacoes = Lotacao.objects.filter(
                    orgao_id=om_id,
                    grande_comando__isnull=True,
                    unidade__isnull=True,
                    sub_unidade__isnull=True,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            elif om_filtro.startswith('gc_'):
                gc_id = int(om_filtro.replace('gc_', ''))
                lotacoes = Lotacao.objects.filter(
                    grande_comando_id=gc_id,
                    unidade__isnull=True,
                    sub_unidade__isnull=True,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            elif om_filtro.startswith('unidade_'):
                unidade_id = int(om_filtro.replace('unidade_', ''))
                lotacoes = Lotacao.objects.filter(
                    unidade_id=unidade_id,
                    sub_unidade__isnull=True,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            elif om_filtro.startswith('sub_'):
                sub_id = int(om_filtro.replace('sub_', ''))
                lotacoes = Lotacao.objects.filter(
                    sub_unidade_id=sub_id,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            
            if militares_ids:
                licencas_queryset = licencas_queryset.filter(militar_id__in=militares_ids)
        
        # Ordenar por hierarquia
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        licencas_lista = list(licencas_queryset.annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'data_inicio',
            'ordem_hierarquia',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade'
        ))
        
        if not licencas_lista:
            error_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nenhuma Licença Especial Encontrada</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .info-box { border: 2px solid #17a2b8; border-radius: 5px; padding: 20px; 
                               max-width: 600px; margin: 0 auto; background-color: #d1ecf1; }
                    h2 { color: #0c5460; }
                    p { color: #0c5460; }
                    .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                           text-decoration: none; border-radius: 5px; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="info-box">
                    <h2>ℹ️ Nenhuma Licença Especial Encontrada</h2>
                    <p>Não foram encontradas licenças especiais para os filtros selecionados.</p>
                    <a href="javascript:history.back()" class="btn">Voltar</a>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_html, content_type='text/html')
        
        # Obter nome do(s) plano(s) relacionado(s)
        planos_ids = set([licenca.plano_id for licenca in licencas_lista if licenca.plano_id])
        planos = PlanoLicencaEspecial.objects.filter(id__in=planos_ids)
        nome_planos = ", ".join([p.titulo for p in planos if p.titulo]) or "Plano de Licenças Especiais"
        
        # Obter ano do plano
        if planos.exists():
            primeiro_plano = planos.first()
            ano_gozo = primeiro_plano.ano_plano if primeiro_plano else None
        else:
            ano_gozo = ano_plano if ano_plano else None
        
        # Agrupar por mês
        licencas_por_mes = defaultdict(list)
        meses_portugues = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        for licenca in licencas_lista:
            mes_ano = licenca.data_inicio.strftime('%Y-%m')
            mes_numero = licenca.data_inicio.month
            mes_nome = meses_portugues.get(mes_numero, licenca.data_inicio.strftime('%B'))
            licencas_por_mes[mes_ano].append({
                'licenca': licenca,
                'mes_nome': mes_nome
            })
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                                rightMargin=1.5*cm, leftMargin=1.5*cm, 
                                topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        style_header = ParagraphStyle('header', parent=styles['Normal'], 
                                     fontSize=9, fontName='Helvetica-Bold', alignment=1)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE GESTÃO DE PESSOAS",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        titulo = "PLANO DE LICENÇAS ESPECIAIS"
        if ano_gozo:
            titulo += f" PARA GOZO EM {ano_gozo}"
        
        story.append(Paragraph(f"<u>{titulo}</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Processar cada mês
        meses_ordenados = sorted(licencas_por_mes.keys())
        
        for mes_ano in meses_ordenados:
            licencas_mes = licencas_por_mes[mes_ano]
            mes_nome = licencas_mes[0]['mes_nome']
            
            # Título do mês
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(f"{mes_nome.upper()}", style_subtitle))
            story.append(Spacer(1, 0.2*cm))
            
            # Cabeçalho da tabela
            table_data = [[
                Paragraph('Nº', style_header),
                Paragraph('Posto/Graduação', style_header),
                Paragraph('Nome', style_header),
                Paragraph('CPF', style_header),
                Paragraph('Lotação', style_header),
                Paragraph('Decênio', style_header),
                Paragraph('Período', style_header),
                Paragraph('Duração', style_header),
                Paragraph('Status', style_header),
            ]]
            
            # Adicionar licenças do mês
            for idx, item in enumerate(licencas_mes, 1):
                licenca = item['licenca']
                militar = licenca.militar
                
                # Obter lotação atual
                lotacao = militar.lotacao_atual()
                lotacao_nome = lotacao.instancia_om_nome if lotacao else "-"
                
                # Período
                periodo = f"{licenca.data_inicio.strftime('%d/%m/%Y')} a {licenca.data_fim.strftime('%d/%m/%Y') if licenca.data_fim else '-'}"
                
                # Duração
                duracao = f"{licenca.quantidade_meses} mês{'es' if licenca.quantidade_meses > 1 else ''}"
                
                # Status
                status_display = licenca.get_status_display()
                
                linha = [
                    Paragraph(str(idx), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(militar.get_posto_graduacao_display(), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(militar.nome_completo, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=0)),
                    Paragraph(militar.cpf[:11] if militar.cpf else "-", ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(lotacao_nome, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=0)),
                    Paragraph(f"{licenca.decenio}º", ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(periodo, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(duracao, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(status_display, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                ]
                table_data.append(linha)
            
            # Criar tabela (ajustado para landscape A4)
            largura_total = landscape(A4)[0] - 3*cm
            col_widths = [
                1*cm,    # Nº
                2.5*cm,  # Posto
                4*cm,    # Nome
                2.5*cm,  # CPF
                5*cm,    # Lotação
                1.5*cm,  # Decênio
                3.5*cm,  # Período
                1.5*cm,  # Duração
                2*cm,    # Status
            ]
            
            mes_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            mes_table.setStyle(TableStyle([
                # Cabeçalho
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
                ('TOPPADDING', (0, 0), (-1, 0), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                # Linhas de dados
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                # Bordas
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            story.append(mes_table)
            story.append(Spacer(1, 0.3*cm))
            
            # Total do mês
            total_mes = len(licencas_mes)
            story.append(Paragraph(f"<b>Total: {total_mes} licença{'s' if total_mes > 1 else ''} especial{'is' if total_mes > 1 else ''}</b>", 
                                   ParagraphStyle('total', parent=styles['Normal'], fontSize=9, alignment=2)))
            
            # Espaçamento após cada mês
            if mes_ano != meses_ordenados[-1]:
                story.append(Spacer(1, 0.5*cm))
        
        # Assinaturas e autenticador
        story.append(Spacer(1, 20))
        
        # Calcular largura total (mesma da tabela principal)
        largura_total_tabela = landscape(A4)[0] - 3*cm
        
        # Preparar dados
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
        
        # Obter função do formulário ou função atual
        funcao_assinatura = request.GET.get('funcao_assinatura', '')
        if not funcao_assinatura:
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_assinatura = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Preparar assinatura física
        if militar_logado:
            nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
        else:
            nome_usuario = request.user.get_full_name() or request.user.username
            nome_posto = nome_usuario
        
        # Preparar assinatura eletrônica
        try:
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
            
            # Logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path_assinatura = obter_caminho_assinatura_eletronica()
            logo_img = Image(logo_path_assinatura, width=3.0*cm, height=2.0*cm)
        except Exception as e:
            logo_img = None
            texto_assinatura = ""
        
        # Preparar autenticador
        class HistoricoFake:
            def __init__(self, ano_plano, plano_id):
                self.id = f"listagem_licencas_especiais_{ano_plano}_{plano_id}"
                hash_valor = abs(hash(f"{ano_plano}_{plano_id}"))
                self.pk = hash_valor % 100000000
                self.tipo_documento = 'listagem_licencas_especiais'
        
        historico_fake = HistoricoFake(ano_plano or 'todos', plano_id or 'todos')
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(historico_fake, request, tipo_documento='listagem_licencas_especiais')
        
        # Criar tabela única para todas as assinaturas e autenticador
        assinaturas_finais_data = []
        
        # Cidade e data
        assinaturas_finais_data.append([Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica'))])
        
        # Espaço
        assinaturas_finais_data.append([Spacer(1, 1*cm)])
        
        # Assinatura física
        assinaturas_finais_data.append([Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold'))])
        assinaturas_finais_data.append([Paragraph(funcao_assinatura, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica'))])
        assinaturas_finais_data.append([Spacer(1, 0.5*cm)])
        
        # Assinatura eletrônica (dentro de célula)
        if logo_img:
            assinatura_eletronica_interna = Table(
                [[logo_img, Paragraph(texto_assinatura, style_small)]],
                colWidths=[3*cm, largura_total_tabela - 3*cm]
            )
            assinatura_eletronica_interna.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            assinaturas_finais_data.append([assinatura_eletronica_interna])
        
        # Autenticador (dentro de célula)
        autenticador_interno = Table(
            [[autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]],
            colWidths=[3*cm, largura_total_tabela - 3*cm]
        )
        autenticador_interno.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        assinaturas_finais_data.append([autenticador_interno])
        
        # Tabela principal (uma coluna, mesma largura da tabela de dados)
        assinaturas_table_final = Table(assinaturas_finais_data, colWidths=[largura_total_tabela])
        assinaturas_table_final.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(assinaturas_table_final)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        
        # Nome do arquivo
        filename = "planos_licencas_especiais_listagem"
        if plano_id:
            filename += f"_plano_{plano_id}"
        elif ano_plano:
            filename += f"_ano_{ano_plano}"
        filename += ".pdf"
        
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_details = str(e)
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Plano de Licenças Especiais</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                .error-detail {{ background-color: #fff; padding: 10px; border-radius: 3px; 
                               margin: 10px 0; font-size: 12px; text-align: left; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF do plano de licenças especiais.</strong></p>
                <div class="error-detail">
                    <strong>Detalhes do erro:</strong><br>
                    {error_details}
                </div>
                <button onclick="javascript:history.back()">Voltar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')

