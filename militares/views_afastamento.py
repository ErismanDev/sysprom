from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from datetime import date, datetime
from django.utils import timezone
from django.template.loader import render_to_string

from .models import Afastamento, Militar, DocumentoAfastamento
from .forms import AfastamentoForm, DocumentoAfastamentoForm
from .permissoes_hierarquicas import obter_funcao_militar_ativa
from .filtros_hierarquicos import aplicar_filtro_hierarquico_afastamentos
from .permissoes_sistema import tem_permissao
from django.core.exceptions import PermissionDenied


class AfastamentoListView(LoginRequiredMixin, ListView):
    """Lista todos os afastamentos com filtros"""
    model = Afastamento
    template_name = 'militares/afastamento_list.html'
    context_object_name = 'afastamentos'
    paginate_by = 20
    
    def get_queryset(self):
        # Obter queryset base com otimizações para lotações
        queryset = Afastamento.objects.select_related(
            'militar', 'cadastrado_por'
        ).prefetch_related(
            'militar__lotacoes'
        ).order_by('-data_inicio', '-data_cadastro')
        
        # Aplicar filtro hierárquico baseado na função militar
        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
        queryset = aplicar_filtro_hierarquico_afastamentos(queryset, funcao_usuario, self.request.user)
        
        # Aplicar filtros
        militar_id = self.request.GET.get('militar')
        tipo_afastamento = self.request.GET.get('tipo_afastamento')
        status = self.request.GET.get('status')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        # Filtro por militar específico (por ID ou por busca de nome)
        militar_nome = self.request.GET.get('militar_nome')
        if militar_id:
            queryset = queryset.filter(militar_id=militar_id)
        elif militar_nome:
            # Buscar por nome, matrícula ou nome de guerra
            queryset = queryset.filter(
                Q(militar__nome_completo__icontains=militar_nome) |
                Q(militar__nome_guerra__icontains=militar_nome) |
                Q(militar__matricula__icontains=militar_nome)
            )
        
        if tipo_afastamento:
            queryset = queryset.filter(tipo_afastamento=tipo_afastamento)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if data_inicio:
            queryset = queryset.filter(data_inicio__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data_inicio__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Estatísticas gerais - aplicar filtro hierárquico também nas estatísticas
        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
        queryset_estatisticas = Afastamento.objects.all()
        queryset_estatisticas = aplicar_filtro_hierarquico_afastamentos(queryset_estatisticas, funcao_usuario, self.request.user)
        
        context['total_afastamentos'] = queryset_estatisticas.count()
        context['afastamentos_ativos'] = queryset_estatisticas.filter(status='ATIVO').count()
        context['afastamentos_encerrados'] = queryset_estatisticas.filter(status='ENCERRADO').count()
        context['afastamentos_cancelados'] = queryset_estatisticas.filter(status='CANCELADO').count()
        
        # Filtros aplicados
        context['filtro_militar'] = self.request.GET.get('militar', '')
        context['filtro_tipo'] = self.request.GET.get('tipo_afastamento', '')
        context['filtro_status'] = self.request.GET.get('status', '')
        context['filtro_data_inicio'] = self.request.GET.get('data_inicio', '')
        context['filtro_data_fim'] = self.request.GET.get('data_fim', '')
        
        # Adicionar todos os tipos de afastamento disponíveis (do modelo e da situação)
        context['afastamento_tipos'] = Afastamento.get_all_tipo_choices()
        
        return context


class AfastamentoCreateView(LoginRequiredMixin, CreateView):
    """Cria novo afastamento"""
    model = Afastamento
    form_class = AfastamentoForm
    template_name = 'militares/afastamento_form.html'
    success_url = reverse_lazy('militares:afastamento_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar permissão granular para criar afastamentos
        if not request.user.is_superuser:
            # Verificar diretamente no modelo PermissaoFuncao
            from .models import PermissaoFuncao
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            
            funcao_usuario = obter_funcao_militar_ativa(request.user)
            if not funcao_usuario or not funcao_usuario.ativo:
                messages.error(request, 'Você não tem uma função militar ativa.')
                return redirect('militares:afastamento_list')
            
            funcao_militar = funcao_usuario.funcao_militar
            if not funcao_militar or not funcao_militar.ativo:
                messages.error(request, 'Sua função militar não está ativa.')
                return redirect('militares:afastamento_list')
            
            # Verificar permissão AFASTAMENTOS_CRIAR
            tem_perm = PermissaoFuncao.objects.filter(
                funcao_militar=funcao_militar,
                modulo='AFASTAMENTOS',
                acesso='CRIAR',
                ativo=True
            ).exists()
            
            # Verificar também formato antigo AFASTAMENTOS_CRIAR
            if not tem_perm:
                tem_perm = PermissaoFuncao.objects.filter(
                    funcao_militar=funcao_militar,
                    modulo='AFASTAMENTOS_CRIAR',
                    ativo=True
                ).exists()
            
            if not tem_perm:
                messages.error(request, 'Você não tem permissão para criar afastamentos.')
                return redirect('militares:afastamento_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documento_form'] = DocumentoAfastamentoForm()
        return context
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário em modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            html = render_to_string('militares/afastamento_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        with transaction.atomic():
            # Definir quem cadastrou
            form.instance.cadastrado_por = self.request.user
            response = super().form_valid(form)
            
            # Processar upload de documento se houver arquivo
            # Verificar se há arquivo sendo enviado
            arquivo_enviado = self.request.FILES.get('arquivo')
            tipo_enviado = self.request.POST.get('tipo')
            titulo_enviado = self.request.POST.get('titulo')
            
            if arquivo_enviado or tipo_enviado or titulo_enviado:
                documento_form = DocumentoAfastamentoForm(self.request.POST, self.request.FILES)
                if documento_form.is_valid():
                    documento = documento_form.save(commit=False)
                    documento.afastamento = self.object
                    documento.upload_por = self.request.user
                    documento.save()
                    messages.success(self.request, 'Documento enviado com sucesso!')
                else:
                    # Se há dados mas o formulário não é válido, mostrar erros
                    error_msg = 'Afastamento criado, mas houve um problema ao processar o documento: '
                    if documento_form.errors:
                        error_msg += ', '.join([str(error) for errors in documento_form.errors.values() for error in errors])
                    else:
                        error_msg += 'Verifique se todos os campos obrigatórios (Tipo, Título e Arquivo) foram preenchidos.'
                    messages.warning(self.request, error_msg)
            
            # Se for requisição AJAX, retornar JSON
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Afastamento registrado com sucesso para {self.object.militar.nome_guerra}!'
                })
            
            messages.success(self.request, f'Afastamento registrado com sucesso para {self.object.militar.nome_guerra}!')
            return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            context = self.get_context_data(form=form)
            html = render_to_string('militares/afastamento_form_modal_content.html', context, request=self.request)
            return JsonResponse({
                'success': False,
                'html': html,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        return super().form_invalid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        initial['status'] = 'ATIVO'
        return initial


class AfastamentoDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de um afastamento"""
    model = Afastamento
    template_name = 'militares/afastamento_detail.html'
    context_object_name = 'afastamento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # O context processor global já injeta menu_permissions de forma consistente
        # Adicionar documentos do afastamento
        afastamento = self.get_object()
        context['documentos'] = DocumentoAfastamento.objects.filter(afastamento=afastamento).order_by('-data_upload')
        # Calcular dias
        context['dias_afastamento'] = afastamento.duracao_dias
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, afastamento.militar)
        
        return context
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário em modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string('militares/afastamento_detail_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class AfastamentoUpdateView(LoginRequiredMixin, UpdateView):
    """Atualiza afastamento e gerencia automaticamente a situação do militar"""
    """Edita um afastamento"""
    model = Afastamento
    form_class = AfastamentoForm
    template_name = 'militares/afastamento_form.html'
    success_url = reverse_lazy('militares:afastamento_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # O context processor global já injeta menu_permissions de forma consistente
        context['documento_form'] = DocumentoAfastamentoForm()
        # Adicionar documentos existentes do afastamento
        context['documentos'] = self.object.documentos.all().order_by('-data_upload')
        return context
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário em modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            form = self.get_form()
            context = self.get_context_data(form=form)
            html = render_to_string('militares/afastamento_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Processar upload de documento se houver arquivo (permitido na edição)
        # Verificar se há arquivo sendo enviado
        arquivo_enviado = self.request.FILES.get('arquivo')
        tipo_enviado = self.request.POST.get('tipo')
        titulo_enviado = self.request.POST.get('titulo')
        
        if arquivo_enviado or tipo_enviado or titulo_enviado:
            documento_form = DocumentoAfastamentoForm(self.request.POST, self.request.FILES)
            if documento_form.is_valid():
                documento = documento_form.save(commit=False)
                documento.afastamento = self.object
                documento.upload_por = self.request.user
                documento.save()
                messages.success(self.request, 'Documento enviado com sucesso!')
            else:
                # Se há dados mas o formulário não é válido, mostrar erros
                error_msg = 'Afastamento atualizado, mas houve um problema ao processar o documento: '
                if documento_form.errors:
                    error_msg += ', '.join([str(error) for errors in documento_form.errors.values() for error in errors])
                else:
                    error_msg += 'Verifique se todos os campos obrigatórios (Tipo, Título e Arquivo) foram preenchidos.'
                messages.warning(self.request, error_msg)
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Afastamento atualizado com sucesso para {self.object.militar.nome_guerra}!'
            })
        
        messages.success(self.request, f'Afastamento atualizado com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            context = self.get_context_data(form=form)
            html = render_to_string('militares/afastamento_form_modal_content.html', context, request=self.request)
            return JsonResponse({
                'success': False,
                'html': html,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        return super().form_invalid(form)


class AfastamentoDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui um afastamento - Apenas para superusuários"""
    model = Afastamento
    template_name = 'militares/afastamento_confirm_delete.html'
    success_url = reverse_lazy('militares:afastamento_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se é superusuário antes de permitir acesso"""
        if not request.user.is_superuser:
            messages.error(request, 'Apenas superusuários podem excluir afastamentos.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Apenas superusuários podem excluir afastamentos.'
                }, status=403)
            return redirect('militares:afastamento_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Retorna o modal se for requisição AJAX, senão retorna a página completa"""
        self.object = self.get_object()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            html = render_to_string('militares/afastamento_delete_modal.html', {
                'afastamento': self.object
            }, request=request)
            return JsonResponse({'html': html})
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def delete(self, request, *args, **kwargs):
        """Verificar novamente se é superusuário antes de excluir"""
        if not request.user.is_superuser:
            messages.error(request, 'Apenas superusuários podem excluir afastamentos.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Apenas superusuários podem excluir afastamentos.'
                }, status=403)
            return redirect('militares:afastamento_list')
        
        from django.db import transaction
        
        self.object = self.get_object()
        
        # Salvar referências antes de excluir
        militar = self.object.militar
        tipo_afastamento = self.object.tipo_afastamento
        situacao_anterior = self.object.situacao_anterior
        
        # Debug: verificar valores antes de excluir
        situacao_atual_antes = militar.situacao if militar else None
        
        # Salvar o PK do afastamento antes de excluir
        afastamento_pk = self.object.pk
        
        # Usar transação atômica para garantir que exclusão e atualização aconteçam juntas
        with transaction.atomic():
            # Excluir o afastamento
            messages.success(self.request, 'Afastamento excluído com sucesso!')
            response = super().delete(request, *args, **kwargs)
        
        # Após excluir (FORA da transação), verificar se o militar precisa voltar para a situação anterior
        if militar:
            # Recarregar o militar do banco para garantir que temos os dados atualizados
            # IMPORTANTE: Recarregar DEPOIS que o afastamento foi excluído
            militar = Militar.objects.get(pk=militar.pk)
            
            # Debug: imprimir valores
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'=== DEBUG EXCLUSÃO AFASTAMENTO ===')
            logger.info(f'Militar: {militar.nome_guerra} (PK: {militar.pk})')
            logger.info(f'Situação atual: {militar.situacao}')
            logger.info(f'Classificação: {militar.classificacao}')
            logger.info(f'Tipo afastamento excluído: {tipo_afastamento}')
            logger.info(f'Situação anterior salva: {situacao_anterior}')
            
            # Verificar se ainda há outros afastamentos válidos até a data atual
            # Um afastamento está válido se: data_inicio <= hoje E (data_fim_prevista >= hoje OU data_fim_real >= hoje OU não tem data_fim) E status != 'CANCELADO'
            from datetime import date
            hoje = date.today()
            
            afastamentos_validos = Afastamento.objects.filter(
                militar=militar
            ).exclude(status='CANCELADO').filter(
                data_inicio__lte=hoje
            ).filter(
                Q(data_fim_prevista__gte=hoje) | 
                Q(data_fim_real__gte=hoje) | 
                Q(data_fim_prevista__isnull=True, data_fim_real__isnull=True)
            ).exists()
            
            logger.info(f'Afastamentos válidos até hoje: {afastamentos_validos}')
            
            # Verificar também férias válidas até hoje
            from .models import Ferias, LicencaEspecial
            
            tem_ferias_valida = Ferias.objects.filter(
                militar=militar
            ).exclude(status='CANCELADA').filter(
                data_inicio__lte=hoje,
                data_fim__gte=hoje
            ).exists()
            
            # Verificar licenças especiais válidas até hoje
            tem_licenca_valida = LicencaEspecial.objects.filter(
                militar=militar
            ).exclude(status='CANCELADA').filter(
                data_inicio__lte=hoje
            ).filter(
                Q(data_fim__gte=hoje) | 
                Q(data_fim__isnull=True)
            ).exists()
            
            logger.info(f'Férias válidas até hoje: {tem_ferias_valida}')
            logger.info(f'Licenças válidas até hoje: {tem_licenca_valida}')
            logger.info(f'Condição para restaurar: {not afastamentos_validos and not tem_ferias_valida and not tem_licenca_valida and militar.classificacao == "ATIVO"}')
            
            # Verificar se a situação atual é um tipo de afastamento
            situacao_atual_eh_afastamento = militar.situacao and militar.situacao.startswith('AFASTAMENTO_')
            
            logger.info(f'Situação atual: {militar.situacao}')
            logger.info(f'Situação atual é afastamento: {situacao_atual_eh_afastamento}')
            logger.info(f'Afastamentos válidos: {afastamentos_validos}')
            logger.info(f'Férias válidas: {tem_ferias_valida}')
            logger.info(f'Licenças válidas: {tem_licenca_valida}')
            logger.info(f'Classificação: {militar.classificacao}')
            print(f'[DEBUG] Situação atual: {militar.situacao}')
            print(f'[DEBUG] Situação atual é afastamento: {situacao_atual_eh_afastamento}')
            print(f'[DEBUG] Afastamentos válidos: {afastamentos_validos}')
            print(f'[DEBUG] Férias válidas: {tem_ferias_valida}')
            print(f'[DEBUG] Licenças válidas: {tem_licenca_valida}')
            print(f'[DEBUG] Classificação: {militar.classificacao}')
            
            # Debug no navegador
            debug_msg = (
                f'DEBUG EXCLUSÃO:\n'
                f'Situação atual: {militar.situacao}\n'
                f'É afastamento: {situacao_atual_eh_afastamento}\n'
                f'Afastamentos válidos: {afastamentos_validos}\n'
                f'Férias válidas: {tem_ferias_valida}\n'
                f'Licenças válidas: {tem_licenca_valida}\n'
                f'Classificação: {militar.classificacao}'
            )
            messages.debug(request, debug_msg)
            
            # Se não há afastamentos válidos e a situação é um tipo de afastamento, restaurar para PRONTO
            # IMPORTANTE: Apenas para militares ATIVOS. Militares inativos não entram nesta regra
            if (militar.classificacao == 'ATIVO' and 
                situacao_atual_eh_afastamento and 
                not afastamentos_validos and 
                not tem_ferias_valida and 
                not tem_licenca_valida):
                # SEMPRE restaurar a situação para PRONTO quando não há outros afastamentos/férias/licenças válidas
                nova_situacao = 'PRONTO'
                
                logger.info(f'Restaurando situação para: {nova_situacao}')
                print(f'[DEBUG] Restaurando situação do militar {militar.nome_guerra} (PK: {militar.pk}) para: {nova_situacao}')
                print(f'[DEBUG] Situação atual antes: {militar.situacao}')
                
                # Debug no navegador
                messages.info(request, f'[DEBUG] Restaurando situação de {militar.situacao} para {nova_situacao}')
                
                # Usar update() diretamente no QuerySet para garantir que a mudança seja persistida
                # Isso evita qualquer interferência de signals ou métodos save() customizados
                from .models import Militar
                rows_updated = Militar.objects.filter(pk=militar.pk).update(situacao=nova_situacao)
                
                logger.info(f'Linhas atualizadas: {rows_updated}')
                print(f'[DEBUG] Linhas atualizadas: {rows_updated}')
                messages.info(request, f'[DEBUG] Linhas atualizadas no banco: {rows_updated}')
                
                # Recarregar do banco diretamente para garantir que foi salvo
                militar = Militar.objects.get(pk=militar.pk)
                
                logger.info(f'Situação após update: {militar.situacao}')
                print(f'[DEBUG] Situação após update: {militar.situacao}')
                messages.info(request, f'[DEBUG] Situação após update: {militar.situacao}')
                
                # Confirmar que foi salvo
                if militar.situacao == nova_situacao:
                    messages.success(request, f'Situação do militar restaurada para {militar.get_situacao_display()}.')
                    logger.info(f'SUCESSO: Situação restaurada para {militar.situacao}')
                    print(f'[DEBUG] SUCESSO: Situação restaurada para {militar.situacao}')
                else:
                    messages.error(request, f'Erro ao restaurar situação do militar. Situação atual: {militar.get_situacao_display()}.')
                    logger.warning(f'ERRO: Situação não foi restaurada. Esperado: {nova_situacao}, Atual: {militar.situacao}')
                    print(f'[DEBUG] ERRO: Situação não foi restaurada. Esperado: {nova_situacao}, Atual: {militar.situacao}')
                    messages.error(request, f'[DEBUG] ERRO: Esperado {nova_situacao}, Atual {militar.situacao}')
            else:
                logger.info(f'CONDIÇÃO NÃO SATISFEITA: Não restaurando situação')
                logger.info(f'  - afastamentos_validos: {afastamentos_validos}')
                logger.info(f'  - tem_ferias_valida: {tem_ferias_valida}')
                logger.info(f'  - tem_licenca_valida: {tem_licenca_valida}')
                logger.info(f'  - classificacao == ATIVO: {militar.classificacao == "ATIVO"}')
                print(f'[DEBUG] CONDIÇÃO NÃO SATISFEITA: Não restaurando situação')
                print(f'[DEBUG]   - afastamentos_validos: {afastamentos_validos}')
                print(f'[DEBUG]   - tem_ferias_valida: {tem_ferias_valida}')
                print(f'[DEBUG]   - tem_licenca_valida: {tem_licenca_valida}')
                print(f'[DEBUG]   - classificacao == ATIVO: {militar.classificacao == "ATIVO"}')
                
                # Debug no navegador
                debug_msg = (
                    f'[DEBUG] CONDIÇÃO NÃO SATISFEITA:\n'
                    f'Afastamentos válidos: {afastamentos_validos}\n'
                    f'Férias válidas: {tem_ferias_valida}\n'
                    f'Licenças válidas: {tem_licenca_valida}\n'
                    f'Classificação == ATIVO: {militar.classificacao == "ATIVO"}\n'
                    f'Situação é afastamento: {situacao_atual_eh_afastamento}'
                )
                messages.warning(request, debug_msg)
        
        # Se for requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Verificar se veio da ficha do militar (via referer ou parâmetro)
            redirect_url = str(self.success_url)  # Padrão: lista de afastamentos
            
            # Coletar mensagens de debug
            debug_messages = []
            for message in messages.get_messages(request):
                if '[DEBUG]' in str(message):
                    debug_messages.append(str(message))
            
            # Se temos o militar e a requisição veio da ficha do militar, redirecionar para lá
            if militar:
                referer = request.META.get('HTTP_REFERER', '')
                # Verificar se o referer contém a URL da ficha do militar
                from django.urls import reverse
                militar_detail_url = reverse('militares:militar_detail', args=[militar.pk])
                if militar_detail_url in referer or f'/militares/{militar.pk}/' in referer:
                    redirect_url = militar_detail_url
                # Também verificar se há parâmetro next na requisição
                elif 'next' in request.GET:
                    redirect_url = request.GET.get('next')
            
            # Recarregar militar para pegar situação atualizada
            situacao_atual = None
            if militar:
                try:
                    militar_atualizado = Militar.objects.get(pk=militar.pk)
                    situacao_atual = militar_atualizado.situacao
                except:
                    pass
            
            return JsonResponse({
                'success': True,
                'message': 'Afastamento excluído com sucesso!',
                'redirect_url': redirect_url,
                'debug_messages': debug_messages,
                'situacao_atual': situacao_atual
            })
        
        return response


@login_required
@require_http_methods(["POST"])
def documento_afastamento_upload(request, pk):
    """Upload de documento para afastamento"""
    try:
        afastamento = get_object_or_404(Afastamento, pk=pk)
        form = DocumentoAfastamentoForm(request.POST, request.FILES)
        
        if form.is_valid():
            documento = form.save(commit=False)
            documento.afastamento = afastamento
            documento.upload_por = request.user
            documento.save()
            messages.success(request, 'Documento enviado com sucesso!')
        else:
            messages.error(request, 'Erro ao enviar documento. Verifique os dados.')
            
    except Exception as e:
        messages.error(request, f'Erro ao processar documento: {str(e)}')
    
    return redirect('militares:afastamento_detail', pk=pk)


@login_required
@require_http_methods(["POST"])
def documento_afastamento_delete(request, documento_id):
    """Excluir documento de afastamento"""
    try:
        documento = get_object_or_404(DocumentoAfastamento, pk=documento_id)
        afastamento_pk = documento.afastamento.pk
        documento.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect('militares:afastamento_detail', pk=afastamento_pk)
    except Exception as e:
        messages.error(request, f'Erro ao excluir documento: {str(e)}')
        return redirect('militares:afastamento_list')


@login_required
def afastamento_certidao_pdf(request, militar_id):
    """Gera PDF com certidão de afastamentos de um militar"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    
    militar = get_object_or_404(Militar, pk=militar_id)
    
    # Obter filtros da URL
    tipo_afastamento_filtro = request.GET.get('tipo_afastamento', '').strip()
    data_inicio_filtro = request.GET.get('data_inicio', '').strip()
    data_fim_filtro = request.GET.get('data_fim', '').strip()
    
    # Busca afastamentos ordenados por data de início (apenas os não cancelados)
    afastamentos_list = Afastamento.objects.filter(militar=militar).exclude(status='CANCELADO')
    
    # Aplicar filtro por tipo de afastamento
    if tipo_afastamento_filtro:
        afastamentos_list = afastamentos_list.filter(tipo_afastamento=tipo_afastamento_filtro)
    
    # Aplicar filtro por período
    if data_inicio_filtro or data_fim_filtro:
        if data_inicio_filtro and data_fim_filtro:
            # Filtro por período: afastamentos que se sobrepõem ao período informado
            # Um afastamento se sobrepõe se:
            # - data_inicio do afastamento <= data_fim do filtro E
            # - (data_fim_real OU data_fim_prevista OU sem fim) >= data_inicio do filtro
            try:
                data_inicio = datetime.strptime(data_inicio_filtro, '%Y-%m-%d').date()
                data_fim = datetime.strptime(data_fim_filtro, '%Y-%m-%d').date()
                
                # Afastamentos que começam antes ou no último dia do período filtrado
                # E que terminam depois ou no primeiro dia do período filtrado (ou não têm fim)
                afastamentos_list = afastamentos_list.filter(
                    Q(data_inicio__lte=data_fim) & (
                        Q(data_fim_real__gte=data_inicio) |
                        Q(data_fim_prevista__gte=data_inicio) |
                        (Q(data_fim_real__isnull=True) & Q(data_fim_prevista__isnull=True))
                    )
                )
            except ValueError:
                pass  # Ignorar datas inválidas
        elif data_inicio_filtro:
            # Apenas data início: afastamentos que começam a partir desta data
            try:
                data_inicio = datetime.strptime(data_inicio_filtro, '%Y-%m-%d').date()
                afastamentos_list = afastamentos_list.filter(data_inicio__gte=data_inicio)
            except ValueError:
                pass  # Ignorar data inválida
        elif data_fim_filtro:
            # Apenas data fim: afastamentos que começam até esta data
            try:
                data_fim = datetime.strptime(data_fim_filtro, '%Y-%m-%d').date()
                afastamentos_list = afastamentos_list.filter(
                    Q(data_inicio__lte=data_fim) |
                    Q(data_fim_real__lte=data_fim) |
                    Q(data_fim_prevista__lte=data_fim)
                )
            except ValueError:
                pass  # Ignorar data inválida
    
    # Ordenar por data de início
    afastamentos_list = afastamentos_list.order_by('-data_inicio')
    
    if not afastamentos_list.exists():
        # Verificar se há filtros aplicados
        tem_filtros = tipo_afastamento_filtro or data_inicio_filtro or data_fim_filtro
        
        mensagem_erro = "Este militar não possui histórico de afastamentos para gerar certidão."
        if tem_filtros:
            mensagem_erro = "Não foram encontrados afastamentos que correspondam aos filtros selecionados."
            mensagem_ajuda = "Por favor, ajuste os filtros ou cadastre afastamentos para este militar."
        else:
            mensagem_ajuda = "Por favor, cadastre afastamentos para este militar antes de gerar a certidão."
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Afastamentos</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Afastamentos</h2>
                <p><strong>{mensagem_erro}</strong></p>
                <p>{mensagem_ajuda}</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=400, content_type='text/html')
    
    try:
        # Obter função para assinatura do parâmetro GET
        funcao_assinatura = request.GET.get('funcao', '')
        
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
        story.append(Paragraph("<u>CERTIDÃO DE AFASTAMENTOS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Texto de certificação com dados do militar (padrão das outras certidões)
        posto_display = militar.get_posto_graduacao_display()
        texto_certificacao = (
            f"Certifico para os devidos fins que conforme os registros funcionais desta instituição, "
            f"foi encontrado que o servidor <b>{posto_display} BM {militar.nome_completo}</b>, "
            f"CPF: <b>{militar.cpf or 'Não informado'}</b>, Matrícula: <b>{militar.matricula}</b>, "
            f"possui os seguintes afastamentos registrados no sistema conforme segue:"
        )
        story.append(Paragraph(texto_certificacao, ParagraphStyle('certificacao', parent=styles['Normal'], fontSize=11, alignment=4, spaceAfter=15)))
        story.append(Spacer(1, 10))
        
        # Estilo para células da tabela - leading menor para texto mais compacto (padrão das outras certidões)
        style_cell = ParagraphStyle('cell', parent=styles['Normal'], fontSize=7, alignment=1, leading=8.5, spaceBefore=0, spaceAfter=0)
        style_cell_header = ParagraphStyle('cell_header', parent=styles['Normal'], fontSize=7, alignment=1, fontName='Helvetica-Bold', leading=9, spaceBefore=0, spaceAfter=0)
        
        # Função auxiliar para quebrar texto longo
        def quebrar_texto(texto, max_chars=30):
            """Quebra texto longo em múltiplas linhas"""
            if not texto or texto == '-':
                return texto
            if len(str(texto)) <= max_chars:
                return str(texto)
            # Tentar quebrar em espaços
            palavras = str(texto).split()
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
        
        # Criar cabeçalho com Paragraphs
        cabecalho_curto = [
            Paragraph('Tipo de<br/>Afastamento', style_cell_header),
            Paragraph('Data<br/>Início', style_cell_header),
            Paragraph('Data<br/>Fim', style_cell_header),
            Paragraph('Duração', style_cell_header),
            Paragraph('Status', style_cell_header)
        ]
        afastamentos_data = [cabecalho_curto]
        
        # Adicionar dados usando Paragraphs para garantir que fique dentro das células
        for afastamento in afastamentos_list:
            # Usar data_fim_real se existir, senão data_fim_prevista, senão 'Em andamento'
            if afastamento.data_fim_real:
                data_fim_str = afastamento.data_fim_real.strftime('%d/%m/%Y')
            elif afastamento.data_fim_prevista:
                data_fim_str = afastamento.data_fim_prevista.strftime('%d/%m/%Y') + '<br/>(Prevista)'
            else:
                data_fim_str = 'Em andamento'
            
            duracao_str = f"{afastamento.duracao_dias} dia{'s' if afastamento.duracao_dias and afastamento.duracao_dias > 1 else ''}" if afastamento.duracao_dias else '-'
            status_display = afastamento.get_status_display()
            # Quebrar status se for muito longo
            status_display = quebrar_texto(status_display, 15)
            
            # Extrair apenas a parte após a barra se existir
            tipo_display = afastamento.get_tipo_afastamento_display()
            if '/' in tipo_display:
                tipo_display = tipo_display.split('/')[-1].strip()
            tipo_display = quebrar_texto(tipo_display, 25)
            
            afastamentos_data.append([
                Paragraph(tipo_display, style_cell),
                Paragraph(afastamento.data_inicio.strftime('%d/%m/%Y'), style_cell),
                Paragraph(data_fim_str, style_cell),
                Paragraph(duracao_str, style_cell),
                Paragraph(status_display, style_cell)
            ])
        
        # Criar tabela com larguras ajustadas (A4 width = 21cm, margens = 1.5cm cada = 3cm, largura útil = 18cm)
        # Distribuindo: 5.5 + 2.5 + 2.5 + 2.5 + 5.0 = 18cm
        afastamentos_table = Table(afastamentos_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 5.0*cm], repeatRows=1)
        afastamentos_table.setStyle(TableStyle([
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
        
        story.append(afastamentos_table)
        story.append(Spacer(1, 20))
        
        # Calcular total de dias de todos os afastamentos
        total_dias = 0
        for afastamento in afastamentos_list:
            if afastamento.duracao_dias:
                total_dias += afastamento.duracao_dias
        
        # Exibir total de dias
        if total_dias > 0:
            texto_total = f"<b>Total de dias de afastamentos: {total_dias} dia{'s' if total_dias > 1 else ''}</b>"
            story.append(Paragraph(texto_total, ParagraphStyle('total_dias', parent=styles['Normal'], fontSize=11, alignment=4, spaceAfter=20)))
            story.append(Spacer(1, 10))
        
        # Cidade e Data por extenso (centralizada) - padrão das outras certidões
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
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta) - padrão das outras certidões
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
        
        # Adicionar assinatura eletrônica com logo - padrão das outras certidões
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
        autenticador = gerar_autenticador_veracidade(militar, request, tipo_documento='certidao_afastamentos')
        
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
        
        # Retornar PDF para visualização no navegador
        filename = f'certidao_afastamentos_{militar.matricula}_{militar.nome_guerra.replace(" ", "_")}.pdf'
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar certidão de afastamentos para militar {militar.pk}: {str(e)}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Afastamentos</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Afastamentos</h2>
                <p><strong>Ocorreu um erro ao gerar a certidão.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')