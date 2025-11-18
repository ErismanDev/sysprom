from django.contrib import admin
from .models import (
    Medalha, ConcessaoMedalha, PropostaMedalha, AssinaturaConcessaoMedalha, AssinaturaPropostaMedalha,
    Qualificacao, FuncaoMilitar, Publicacao, Militar, FichaConceitoOficiais, FichaConceitoPracas, 
    QuadroAcesso, ItemQuadroAcesso, Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, 
    Intersticio, PrevisaoVaga, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, 
    DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, JustificativaEncerramento, AtaSessao, 
    AssinaturaAta, ModeloAta, NotificacaoSessao, MensagemInstantanea, Chat, MensagemChat, Chamada, CargoComissao, UsuarioFuncaoMilitar,
    CalendarioPromocao, ItemCalendarioPromocao, AssinaturaCalendarioPromocao, AlmanaqueMilitar, 
    AssinaturaAlmanaque, LogSistema,     PlanoFerias, Ferias, DocumentoFerias, PlanoLicencaEspecial, LicencaEspecial, Viatura, AbastecimentoViatura, ManutencaoViatura,
    TrocaOleoViatura, HistoricoAbastecimentoAssinado, AssinaturaHistoricoAbastecimento, Arma, ArmaParticular, MovimentacaoArma, ConfiguracaoArma, HistoricoAlteracaoArma, AssinaturaMovimentacaoArma, TransferenciaArma, CautelaArma,
    BemMovel, TombamentoBemMovel, HistoricoTombamento, ProdutoAlmoxarifado, EntradaAlmoxarifado, SaidaAlmoxarifado, HistoricoAlmoxarifado, ProcessoAdministrativo
)



from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone


@admin.register(Medalha)
class MedalhaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "tipo", "grau_tempo_servico", "ativo")
    list_filter = ("tipo", "grau_tempo_servico", "ativo")
    search_fields = ("codigo", "nome")
    ordering = ("nome",)


@admin.register(ConcessaoMedalha)
class ConcessaoMedalhaAdmin(admin.ModelAdmin):
    list_display = ("medalha", "beneficiario", "data_concessao", "portaria_numero")
    list_filter = ("medalha__tipo", "data_concessao")
    search_fields = ("medalha__nome", "militar__nome_completo", "nome_externo", "documento_externo", "portaria_numero")
    autocomplete_fields = ("medalha", "militar")

    def beneficiario(self, obj):
        if obj.militar:
            return f"{obj.militar.get_posto_graduacao_display()} {obj.militar.nome_completo}"
        return obj.nome_externo or "Externo"


@admin.register(AssinaturaConcessaoMedalha)
class AssinaturaConcessaoMedalhaAdmin(admin.ModelAdmin):
    list_display = ("concessao", "assinado_por", "tipo_assinatura", "data_assinatura", "funcao_assinatura")
    list_filter = ("tipo_assinatura", "data_assinatura")
    search_fields = ("concessao__medalha__nome", "assinado_por__username", "assinado_por__first_name", "assinado_por__last_name")
    readonly_fields = ("data_assinatura",)
    autocomplete_fields = ("concessao", "assinado_por")
    
    fieldsets = (
        ('Informações da Assinatura', {
            'fields': ('concessao', 'assinado_por', 'tipo_assinatura', 'funcao_assinatura')
        }),
        ('Detalhes', {
            'fields': ('observacoes', 'data_assinatura')
        }),
    )


@admin.register(PropostaMedalha)
class PropostaMedalhaAdmin(admin.ModelAdmin):
    list_display = ("numero_proposta", "titulo", "status", "criado_por", "criado_em", "total_concessoes")
    list_filter = ("status", "criado_em")
    search_fields = ("numero_proposta", "titulo", "criado_por__username")
    readonly_fields = ("numero_proposta", "criado_em", "atualizado_em")
    filter_horizontal = ("concessoes",)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_proposta', 'titulo', 'descricao', 'status')
        }),
        ('Concessões', {
            'fields': ('concessoes',)
        }),
        ('Controle', {
            'fields': ('criado_por', 'criado_em', 'atualizado_em')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'aprovado_em', 'observacoes_aprovacao'),
            'classes': ('collapse',)
        }),
    )
    
    def total_concessoes(self, obj):
        return obj.get_total_concessoes()
    total_concessoes.short_description = "Total de Concessões"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se for uma nova proposta
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(AssinaturaPropostaMedalha)
class AssinaturaPropostaMedalhaAdmin(admin.ModelAdmin):
    list_display = ("proposta", "assinado_por", "tipo_assinatura", "data_assinatura", "funcao_assinatura")
    list_filter = ("tipo_assinatura", "data_assinatura")
    search_fields = ("proposta__numero_proposta", "proposta__titulo", "assinado_por__username", "assinado_por__first_name", "assinado_por__last_name")
    readonly_fields = ("data_assinatura",)
    autocomplete_fields = ("proposta", "assinado_por")
    
    fieldsets = (
        ('Informações da Assinatura', {
            'fields': ('proposta', 'assinado_por', 'tipo_assinatura', 'funcao_assinatura')
        }),
        ('Detalhes', {
            'fields': ('observacoes', 'data_assinatura')
        }),
    )


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['militar', 'tipo', 'titulo', 'status', 'data_upload', 'conferido_por']
    list_filter = ['tipo', 'status', 'data_upload']
    search_fields = ['militar__nome_completo', 'militar__matricula', 'titulo']
    readonly_fields = ['data_upload', 'filename']
    actions = ['aprovar_documentos', 'rejeitar_documentos', 'arquivar_documentos']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('militar', 'ficha_conceito', 'tipo', 'titulo')
        }),
        ('Arquivo', {
            'fields': ('arquivo', 'filename', 'data_upload')
        }),
        ('Conferência', {
            'fields': ('status', 'conferido_por', 'data_conferencia', 'observacoes')
        }),
    )
    
    def filename(self, obj):
        if obj.arquivo:
            return obj.filename()
        return "N/A"
    filename.short_description = "Nome do Arquivo"
    
    def aprovar_documentos(self, request, queryset):
        updated = queryset.update(
            status='APROVADO',
            conferido_por=request.user,
            data_conferencia=timezone.now()
        )
        self.message_user(request, f'{updated} documento(s) aprovado(s) com sucesso.')
    aprovar_documentos.short_description = "Aprovar documentos selecionados"
    
    def rejeitar_documentos(self, request, queryset):
        updated = queryset.update(
            status='REJEITADO',
            conferido_por=request.user,
            data_conferencia=timezone.now()
        )
        self.message_user(request, f'{updated} documento(s) rejeitado(s).')
    rejeitar_documentos.short_description = "Rejeitar documentos selecionados"
    
    def arquivar_documentos(self, request, queryset):
        updated = queryset.update(
            status='ARQUIVADO',
            conferido_por=request.user,
            data_conferencia=timezone.now()
        )
        self.message_user(request, f'{updated} documento(s) arquivado(s).')
    arquivar_documentos.short_description = "Arquivar documentos selecionados"
    
    def delete_model(self, request, obj):
        """Sobrescreve o método de exclusão para solicitar confirmação de senha"""
        if request.method == 'POST':
            password = request.POST.get('password')
            if not password:
                messages.error(request, 'Senha é obrigatória para excluir documentos.')
                return
            
            if not request.user.check_password(password):
                messages.error(request, 'Senha incorreta. Documento não foi excluído.')
                return
        
        super().delete_model(request, obj)
        messages.success(request, f'Documento "{obj.titulo}" excluído com sucesso.')
    
    def delete_queryset(self, request, queryset):
        """Sobrescreve o método de exclusão em lote para solicitar confirmação de senha"""
        if request.method == 'POST':
            password = request.POST.get('password')
            if not password:
                messages.error(request, 'Senha é obrigatória para excluir documentos.')
                return
            
            if not request.user.check_password(password):
                messages.error(request, 'Senha incorreta. Documentos não foram excluídos.')
                return
        
        count = queryset.count()
        super().delete_queryset(request, queryset)
        messages.success(request, f'{count} documento(s) excluído(s) com sucesso.')
    
    def get_urls(self):
        """Adiciona URLs personalizadas para confirmação de exclusão"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/delete/',
                self.admin_site.admin_view(self.delete_view_with_password),
                name='militares_documento_delete',
            ),
        ]
        return custom_urls + urls
    
    def delete_view_with_password(self, request, object_id, extra_context=None):
        """View personalizada para exclusão com confirmação de senha"""
        from django.contrib.admin.utils import unquote
        from django.shortcuts import get_object_or_404
        from django.template.response import TemplateResponse
        
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        
        if request.method == 'POST':
            password = request.POST.get('password')
            if not password:
                messages.error(request, 'Senha é obrigatória para excluir documentos.')
                context = {
                    **self.admin_site.each_context(request),
                    'title': 'Confirmar exclusão',
                    'object_name': self.model._meta.verbose_name,
                    'object': obj,
                    'opts': self.model._meta,
                    'app_label': self.model._meta.app_label,
                    'media': self.media,
                }
                return TemplateResponse(request, 'admin/militares/documento/delete_confirmation.html', context)
            
            if not request.user.check_password(password):
                messages.error(request, 'Senha incorreta. Documento não foi excluído.')
                context = {
                    **self.admin_site.each_context(request),
                    'title': 'Confirmar exclusão',
                    'object_name': self.model._meta.verbose_name,
                    'object': obj,
                    'opts': self.model._meta,
                    'app_label': self.model._meta.app_label,
                    'media': self.media,
                }
                return TemplateResponse(request, 'admin/militares/documento/delete_confirmation.html', context)
        
        return super().delete_view(request, object_id, extra_context)


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 1
    fields = ['tipo', 'titulo', 'arquivo', 'status', 'data_upload']
    readonly_fields = ['data_upload']


@admin.register(FichaConceitoOficiais)
class FichaConceitoOficiaisAdmin(admin.ModelAdmin):
    list_display = [
        'militar', 'pontuacao_total',
        'tempo_posto_extenso', 'cursos_especializacao', 'medalha_federal', 'elogio_individual',
        'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento',
        'data_registro'
    ]
    list_filter = [
        'militar__quadro', 'militar__posto_graduacao'
    ]
    search_fields = ['militar__nome_completo', 'militar__matricula']
    readonly_fields = ['pontuacao_total', 'data_registro', 'tempo_posto_extenso']
    fieldsets = (
        ('Identificação', {
            'fields': ('militar',)
        }),
        ('Informações Gerais', {
            'fields': (
                'categoria',
            )
        }),
        ('Pontos Positivos', {
            'fields': (
                ('tempo_posto_anos', 'tempo_posto_meses', 'tempo_posto_dias'),
                'tempo_posto_extenso',
                'cursos_especializacao', 'cursos_csbm', 'cursos_cfsd', 'cursos_chc', 'cursos_chsgt',
                'cursos_cas', 'cursos_cho', 'cursos_cfo', 'cursos_cao', 'cursos_instrutor_csbm',
                'cursos_civis_superior', 'cursos_civis_especializacao', 'cursos_civis_mestrado', 'cursos_civis_doutorado',
                'medalha_federal', 'medalha_estadual', 'medalha_cbmepi',
                'elogio_individual', 'elogio_coletivo',
            )
        }),
        ('Pontos Negativos', {
            'fields': (
                'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento',
            )
        }),
        ('Cálculo Final', {
            'fields': ('pontuacao_total', 'data_registro')
        }),
    )

    def pontuacao_total(self, obj):
        return obj.calcular_pontos()
    pontuacao_total.short_description = 'Pontuação Total'


class FichaConceitoOficiaisInline(admin.TabularInline):
    model = FichaConceitoOficiais
    extra = 0
    fields = ['pontuacao_total', 'tempo_posto_extenso', 'cursos_especializacao', 'cursos_csbm', 'medalha_federal', 'elogio_individual', 'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento']
    readonly_fields = ['pontuacao_total', 'tempo_posto_extenso']

    def pontuacao_total(self, obj):
        return obj.calcular_pontos()
    pontuacao_total.short_description = 'Pontuação Total'


@admin.register(FichaConceitoPracas)
class FichaConceitoPracasAdmin(admin.ModelAdmin):
    list_display = [
        'militar', 'pontuacao_total',
        'tempo_posto_extenso', 'cursos_especializacao', 'medalha_federal', 'elogio_individual',
        'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento',
        'data_registro'
    ]
    list_filter = [
        'militar__quadro', 'militar__posto_graduacao'
    ]
    search_fields = ['militar__nome_completo', 'militar__matricula']
    readonly_fields = ['pontuacao_total', 'data_registro', 'tempo_posto_extenso']
    fieldsets = (
        ('Identificação', {
            'fields': ('militar',)
        }),
        ('Informações Gerais', {
            'fields': (
                'observacoes',
            )
        }),
        ('Pontos Positivos', {
            'fields': (
                ('tempo_posto_anos', 'tempo_posto_meses', 'tempo_posto_dias'),
                'tempo_posto_extenso',
                'cursos_especializacao', 'cursos_cfsd', 'cursos_chc', 'cursos_chsgt',
                'cursos_cas', 'cursos_cho', 'cursos_civis_tecnico', 'cursos_civis_superior', 
                'cursos_civis_especializacao', 'cursos_civis_mestrado', 'cursos_civis_doutorado',
                'medalha_federal', 'medalha_estadual', 'medalha_cbmepi',
                'elogio_individual', 'elogio_coletivo',
            )
        }),
        ('Pontos Negativos', {
            'fields': (
                'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento',
            )
        }),
        ('Cálculo Final', {
            'fields': ('pontuacao_total', 'data_registro')
        }),
    )

    def pontuacao_total(self, obj):
        return obj.calcular_pontos()
    pontuacao_total.short_description = 'Pontuação Total'


class FichaConceitoPracasInline(admin.TabularInline):
    model = FichaConceitoPracas
    extra = 0
    fields = ['pontuacao_total', 'tempo_posto', 'cursos_especializacao', 'cursos_cfsd', 'medalha_federal', 'elogio_individual', 'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento']
    readonly_fields = ['pontuacao_total']

    def pontuacao_total(self, obj):
        return obj.calcular_pontos()
    pontuacao_total.short_description = 'Pontuação Total'


@admin.register(Militar)
class MilitarAdmin(admin.ModelAdmin):
    list_display = [
        'matricula', 'nome_completo', 'nome_guerra', 'posto_graduacao', 
        'quadro', 'numeracao_antiguidade', 'idade', 'tempo_servico', 'tempo_posto_atual', 'situacao'
    ]
    list_filter = [
        'quadro', 'posto_graduacao', 'situacao', 'sexo',
        'data_ingresso', 'data_promocao_atual'
    ]
    search_fields = ['matricula', 'nome_completo', 'nome_guerra', 'cpf', 'rgbm', 'titulo_eleitor']
    readonly_fields = [
        'idade', 'tempo_servico', 'tempo_posto_atual', 'apto_promocao_antiguidade',
        'get_pontuacao_ficha_conceito', 'data_cadastro', 'data_atualizacao'
    ]
    actions = ['gerar_ficha_conceito', 'verificar_requisitos_quadro', 'reordenar_antiguidade', 'reordenar_grupo_antiguidade']
    
    def save_model(self, request, obj, form, change):
        """Sobrescreve o método save para reordenar automaticamente após alteração da antiguidade"""
        # Se é uma alteração (não criação) e o campo numeracao_antiguidade foi alterado
        if change and 'numeracao_antiguidade' in form.changed_data:
            # Obter a numeração anterior
            obj_original = type(obj).objects.get(pk=obj.pk)
            numeracao_anterior = obj_original.numeracao_antiguidade

            # Salvar o objeto primeiro (com o novo número)
            super().save_model(request, obj, form, change)

            # Buscar o objeto atualizado do banco
            obj_atualizado = type(obj).objects.get(pk=obj.pk)

            # Chamar a reordenação automática
            obj_atualizado.reordenar_numeracoes_apos_alteracao(numeracao_anterior)

            # Mostrar mensagem de sucesso
            messages.success(request, f'Antiguidade alterada de {numeracao_anterior} para {obj.numeracao_antiguidade}. Reordenação automática realizada.')
        else:
            # Para criação ou outros campos, apenas salvar normalmente
            super().save_model(request, obj, form, change)
    
    def get_inlines(self, request, obj=None):
        """Retorna o inline correto baseado no tipo de militar"""
        if obj and obj.is_oficial():
            return [FichaConceitoOficiaisInline]
        else:
            return [FichaConceitoPracasInline]
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': (
                'numeracao_antiguidade', 'matricula', 'nome_completo', 'nome_guerra', 'cpf', 'rg', 'rgbm', 'orgao_expedidor',
                'data_nascimento', 'sexo', 'etnia', 'grupo_sanguineo', 'fator_rh'
            )
        }),
        ('Dados Familiares', {
            'fields': (
                'nome_pai', 'nome_mae', 'nacionalidade', 'naturalidade', 'uf_naturalidade'
            )
        }),
        ('Documentos', {
            'fields': (
                'titulo_eleitor', 'zona_eleitoral', 'secao_eleitoral', 'cnh_numero', 'cnh_categoria', 'cnh_validade'
            )
        }),
        ('Dados Bancários', {
            'fields': (
                'banco_codigo', 'banco_nome', 'agencia', 'conta', 'pis_pasep'
            )
        }),
        ('Dados Físicos', {
            'fields': (
                'altura', 'peso'
            )
        }),
        ('Fardamento', {
            'fields': (
                'combat_shirt', 'camisa', 'calca', 'comprimento_calca', 
                'gorro', 'coturno'
            )
        }),
        ('Informações Militares', {
            'fields': (
                'quadro', 'posto_graduacao', 'data_ingresso', 'data_promocao_atual', 'situacao', 'classificacao', 'comportamento'
            )
        }),
        ('Informações de Contato', {
            'fields': ('email', 'telefone', 'celular')
        }),
        ('Cursos e Formação', {
            'fields': (
                'curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_cho', 'nota_cho', 'curso_superior', 
                'pos_graduacao', 'curso_csbm', 'curso_adaptacao_oficial'
            ),
            'classes': ('collapse',)
        }),
        ('Cursos de Praças', {
            'fields': (
                'curso_cfsd', 'curso_formacao_pracas', 'curso_chc', 'curso_chsgt', 'nota_chsgt', 'curso_cas'
            ),
            'classes': ('collapse',)
        }),
        ('Inspeção de Saúde', {
            'fields': (
                'apto_inspecao_saude', 'data_inspecao_saude', 'data_validade_inspecao_saude'
            ),
            'classes': ('collapse',)
        }),
        ('Cálculos Automáticos', {
            'fields': (
                'idade', 'tempo_servico', 'tempo_posto_atual', 'apto_promocao_antiguidade',
                'get_pontuacao_ficha_conceito'
            ),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_cadastro', 'data_atualizacao', 'observacoes'),
            'classes': ('collapse',)
        }),
    )
    
    def idade(self, obj):
        return f"{obj.idade()} anos"
    idade.short_description = "Idade"
    
    def tempo_servico(self, obj):
        return f"{obj.tempo_servico()} anos"
    tempo_servico.short_description = "Tempo de Serviço"
    
    def tempo_posto_atual(self, obj):
        return f"{obj.tempo_posto_atual()} anos"
    tempo_posto_atual.short_description = "Tempo no Posto"
    
    def numeracao_antiguidade(self, obj):
        if obj.numeracao_antiguidade:
            return f"{obj.numeracao_antiguidade}º"
        return "—"
    numeracao_antiguidade.short_description = "Antiguidade"
    
    def apto_promocao_antiguidade(self, obj):
        if obj.apto_promocao_antiguidade():
            return "Sim"
        return "Não"
    apto_promocao_antiguidade.short_description = "Apto Promoção (Antiguidade)"
    
    def get_pontuacao_ficha_conceito(self, obj):
        return f"{obj.get_pontuacao_ficha_conceito()} pontos"
    get_pontuacao_ficha_conceito.short_description = "Pontuação Ficha de Conceito"
    
    class Media:
        js = ('js/militar_admin.js',)
    
    def gerar_ficha_conceito(self, request, queryset):
        for militar in queryset:
            if militar.is_oficial():
                # Gerar ficha de conceito para oficiais
                FichaConceitoOficiais.objects.get_or_create(
                    militar=militar,
                    defaults={
                        'tempo_posto': militar.tempo_posto_atual(),
                    }
                )
            else:
                # Gerar ficha de conceito para praças
                FichaConceitoPracas.objects.get_or_create(
                    militar=militar,
                    defaults={
                        'tempo_posto': militar.tempo_posto_atual(),
                    }
                )
        
        self.message_user(request, f'Fichas de conceito geradas para {queryset.count()} militar(es).')
    gerar_ficha_conceito.short_description = "Gerar fichas de conceito básicas"
    
    def verificar_requisitos_quadro(self, request, queryset):
        for militar in queryset:
            requisitos = militar.requisitos_ingresso_quadro()
            if requisitos:
                messages.info(request, f"{militar.nome_completo} - {requisitos['titulo']}")
                for req in requisitos['requisitos']:
                    messages.info(request, f"  • {req}")
        self.message_user(request, f'Verificação de requisitos concluída para {queryset.count()} militar(es).')
    verificar_requisitos_quadro.short_description = "Verificar requisitos de ingresso no quadro"
    
    def reordenar_antiguidade(self, request, queryset):
        """Reordena automaticamente a antiguidade dos militares selecionados"""
        total_reordenados = 0
        
        # Agrupar militares por posto e quadro para reordenar cada grupo separadamente
        grupos = {}
        for militar in queryset:
            chave = (militar.posto_graduacao, militar.quadro)
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(militar)
        
        # Reordenar cada grupo
        for (posto, quadro), militares_grupo in grupos.items():
            # Buscar todos os militares ativos deste posto/quadro
            todos_militares = Militar.objects.filter(
                classificacao='ATIVO',
                posto_graduacao=posto,
                quadro=quadro
            ).order_by('data_promocao_atual')
            
            # Reordenar sequencialmente
            for i, militar in enumerate(todos_militares, 1):
                if militar.numeracao_antiguidade != i:
                    militar.numeracao_antiguidade = i
                    militar.save(update_fields=['numeracao_antiguidade'])
                    total_reordenados += 1
        
        self.message_user(
            request, 
            f'Reordenação concluída! {total_reordenados} militares foram reordenados automaticamente.'
        )
    reordenar_antiguidade.short_description = "Reordenar antiguidade automaticamente"

    def reordenar_grupo_antiguidade(self, request, queryset):
        """Reordena a antiguidade de todos do mesmo posto/quadro dos militares selecionados"""
        grupos = set((m.posto_graduacao, m.quadro) for m in queryset)
        total = 0
        for posto, quadro in grupos:
            militares = Militar.objects.filter(
                classificacao='ATIVO',
                posto_graduacao=posto,
                quadro=quadro
            ).order_by('numeracao_antiguidade', 'pk')
            for i, militar in enumerate(militares, 1):
                if militar.numeracao_antiguidade != i:
                    militar.numeracao_antiguidade = i
                    militar.save(update_fields=['numeracao_antiguidade'])
                    total += 1
        self.message_user(request, f'Reordenação concluída! {total} militares foram reordenados.')
    reordenar_grupo_antiguidade.short_description = "Reordenar antiguidade deste grupo (posto/quadro)"

    actions = ['gerar_ficha_conceito', 'verificar_requisitos_quadro', 'reordenar_antiguidade', 'reordenar_grupo_antiguidade']


@admin.register(QuadroAcesso)
class QuadroAcessoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'data_promocao', 'status', 'ativo']
    list_filter = ['tipo', 'status', 'ativo', 'data_promocao']
    search_fields = ['tipo']
    actions = ['gerar_quadro_acesso']
    
    def gerar_quadro_acesso(self, request, queryset):
        for quadro in queryset:
            # Gerar o quadro completo automaticamente
            sucesso, mensagem = quadro.gerar_quadro_completo()
            if sucesso:
                self.message_user(request, f'Quadro de acesso gerado com sucesso: {mensagem}')
            else:
                self.message_user(request, f'Erro ao gerar quadro: {mensagem}')
        
        self.message_user(request, f'Processamento concluído para {queryset.count()} registro(s).')
    gerar_quadro_acesso.short_description = "Gerar quadro de acesso"


@admin.register(ItemQuadroAcesso)
class ItemQuadroAcessoAdmin(admin.ModelAdmin):
    list_display = ['quadro_acesso', 'militar', 'posicao', 'pontuacao', 'data_inclusao']
    list_filter = ['quadro_acesso__tipo', 'quadro_acesso__status']
    search_fields = ['militar__nome_completo', 'militar__matricula']
    ordering = ['quadro_acesso', 'posicao']


@admin.register(Promocao)
class PromocaoAdmin(admin.ModelAdmin):
    list_display = [
        'militar', 'posto_anterior', 'posto_novo', 'criterio', 
        'data_promocao', 'data_publicacao', 'numero_ato', 'is_historica'
    ]
    list_filter = ['criterio', 'data_promocao', 'data_publicacao', 'militar__quadro', 'is_historica']
    search_fields = ['militar__nome_completo', 'militar__matricula', 'numero_ato']
    readonly_fields = ['data_registro']


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = ['posto', 'quadro', 'efetivo_atual', 'efetivo_maximo', 'vagas_disponiveis', 'percentual_ocupacao']
    list_filter = ['posto', 'quadro']
    readonly_fields = ['vagas_disponiveis', 'percentual_ocupacao', 'data_atualizacao']
    
    def vagas_disponiveis(self, obj):
        return obj.vagas_disponiveis
    vagas_disponiveis.short_description = "Vagas Disponíveis"
    
    def percentual_ocupacao(self, obj):
        return f"{obj.percentual_ocupacao:.1f}%"
    percentual_ocupacao.short_description = "% Ocupação"


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'pontuacao', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']


@admin.register(MedalhaCondecoracao)
class MedalhaCondecoracaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'pontuacao', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']


@admin.register(PrevisaoVaga)
class PrevisaoVagaAdmin(admin.ModelAdmin):
    list_display = ['posto', 'quadro', 'efetivo_atual', 'efetivo_previsto', 'vagas_disponiveis', 'get_status_display', 'ativo']
    list_filter = ['quadro', 'posto', 'ativo']
    search_fields = ['posto', 'quadro']
    readonly_fields = ['vagas_disponiveis', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('posto', 'quadro', 'ativo')
        }),
        ('Efetivos', {
            'fields': ('efetivo_atual', 'efetivo_previsto', 'vagas_disponiveis')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Status'

# ============================================================================
# ADMIN DA COMISSÃO DE PROMOÇÃO DE OFICIAIS
# ============================================================================

@admin.register(ComissaoPromocao)
class ComissaoPromocaoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'nome', 'data_criacao', 'status', 'total_membros', 'data_registro']
    list_filter = ['tipo', 'status', 'data_criacao']
    search_fields = ['nome', 'observacoes']
    readonly_fields = ['data_registro', 'data_atualizacao']
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo', 'titulo', 'nome', 'data_criacao', 'data_termino', 'status')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_registro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MembroComissao)
class MembroComissaoAdmin(admin.ModelAdmin):
    list_display = ['militar', 'comissao', 'usuario', 'tipo', 'cargo', 'data_nomeacao', 'ativo']
    list_filter = ['tipo', 'cargo', 'ativo', 'data_nomeacao', 'comissao__tipo']
    search_fields = ['militar__nome_completo', 'militar__matricula', 'comissao__nome', 'usuario__username']
    readonly_fields = ['data_registro']
    date_hierarchy = 'data_nomeacao'
    
    fieldsets = (
        ('Informações do Membro', {
            'fields': ('comissao', 'militar', 'usuario', 'tipo', 'cargo')
        }),
        ('Período', {
            'fields': ('data_nomeacao', 'data_termino', 'ativo')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_registro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessaoComissao)
class SessaoComissaoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'comissao', 'tipo', 'data_sessao', 'status', 'total_presentes']
    list_filter = ['tipo', 'status', 'data_sessao', 'comissao']
    search_fields = ['comissao__nome', 'pauta', 'local']
    readonly_fields = ['data_registro']
    date_hierarchy = 'data_sessao'
    
    fieldsets = (
        ('Informações da Sessão', {
            'fields': ('comissao', 'numero', 'tipo', 'data_sessao')
        }),
        ('Horário e Local', {
            'fields': ('hora_inicio', 'hora_fim', 'local')
        }),
        ('Conteúdo', {
            'fields': ('pauta', 'status', 'observacoes')
        }),
        ('Controle', {
            'fields': ('data_registro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PresencaSessao)
class PresencaSessaoAdmin(admin.ModelAdmin):
    list_display = ['sessao', 'membro', 'presente', 'data_registro']
    list_filter = ['presente', 'sessao__comissao', 'sessao__data_sessao']
    search_fields = ['membro__militar__nome_completo', 'sessao__comissao__nome']
    readonly_fields = ['data_registro']
    
    fieldsets = (
        ('Informações da Presença', {
            'fields': ('sessao', 'membro', 'presente')
        }),
        ('Justificativa', {
            'fields': ('justificativa',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_registro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliberacaoComissao)
class DeliberacaoComissaoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'sessao', 'tipo', 'assunto', 'aprovada', 'total_votos']
    list_filter = ['tipo', 'sessao__comissao', 'sessao__data_sessao']
    search_fields = ['assunto', 'descricao', 'sessao__comissao__nome']
    readonly_fields = ['data_registro']
    
    fieldsets = (
        ('Informações da Deliberação', {
            'fields': ('sessao', 'numero', 'tipo', 'assunto')
        }),
        ('Conteúdo', {
            'fields': ('descricao', 'resultado')
        }),
        ('Votação', {
            'fields': ('votos_favor', 'votos_contra', 'votos_abstencao')
        }),
        ('Controle', {
            'fields': ('data_registro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentoSessao)
class DocumentoSessaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'sessao', 'tipo', 'upload_por', 'data_upload', 'deliberacao_gerada']
    list_filter = ['tipo', 'data_upload', 'sessao__comissao', 'sessao__status']
    search_fields = ['titulo', 'descricao', 'sessao__comissao__nome', 'upload_por__username']
    readonly_fields = ['data_upload', 'filename']
    date_hierarchy = 'data_upload'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('sessao', 'tipo', 'titulo', 'descricao')
        }),
        ('Arquivo', {
            'fields': ('arquivo', 'filename', 'data_upload')
        }),
        ('Upload', {
            'fields': ('upload_por',)
        }),
        ('Deliberação', {
            'fields': ('deliberacao_gerada',)
        }),
    )
    
    def filename(self, obj):
        if obj.arquivo:
            return obj.filename()
        return "N/A"
    filename.short_description = "Nome do Arquivo"
    
    def delete_model(self, request, obj):
        """Sobrescreve o método de exclusão para solicitar confirmação de senha"""
        if request.method == 'POST':
            password = request.POST.get('password')
            if not password:
                messages.error(request, 'Senha é obrigatória para excluir documentos.')
                return
            
            if not request.user.check_password(password):
                messages.error(request, 'Senha incorreta. Documento não foi excluído.')
                return
        
        super().delete_model(request, obj)
        messages.success(request, f'Documento "{obj.titulo}" excluído com sucesso.')
    
    def delete_queryset(self, request, queryset):
        """Sobrescreve o método de exclusão em lote para solicitar confirmação de senha"""
        if request.method == 'POST':
            password = request.POST.get('password')
            if not password:
                messages.error(request, 'Senha é obrigatória para excluir documentos.')
                return
            
            if not request.user.check_password(password):
                messages.error(request, 'Senha incorreta. Documentos não foram excluídos.')
                return
        
        count = queryset.count()
        super().delete_queryset(request, queryset)
        messages.success(request, f'{count} documento(s) excluído(s) com sucesso.')
    
    def get_urls(self):
        """Adiciona URLs personalizadas para confirmação de exclusão"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/delete/',
                self.admin_site.admin_view(self.delete_view_with_password),
                name='militares_documentosessao_delete',
            ),
        ]
        return custom_urls + urls
    
    def delete_view_with_password(self, request, object_id, extra_context=None):
        """View personalizada para exclusão com confirmação de senha"""
        from django.contrib.admin.utils import unquote
        from django.shortcuts import get_object_or_404
        from django.template.response import TemplateResponse
        
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        
        if request.method == 'POST':
            password = request.POST.get('password')
            if not password:
                messages.error(request, 'Senha é obrigatória para excluir documentos.')
                context = {
                    **self.admin_site.each_context(request),
                    'title': 'Confirmar exclusão',
                    'object_name': self.model._meta.verbose_name,
                    'object': obj,
                    'opts': self.model._meta,
                    'app_label': self.model._meta.app_label,
                    'media': self.media,
                }
                return TemplateResponse(request, 'admin/militares/documentosessao/delete_confirmation.html', context)
            
            if not request.user.check_password(password):
                messages.error(request, 'Senha incorreta. Documento não foi excluído.')
                context = {
                    **self.admin_site.each_context(request),
                    'title': 'Confirmar exclusão',
                    'object_name': self.model._meta.verbose_name,
                    'object': obj,
                    'opts': self.model._meta,
                    'app_label': self.model._meta.app_label,
                    'media': self.media,
                }
                return TemplateResponse(request, 'admin/militares/documentosessao/delete_confirmation.html', context)
        
        return super().delete_view(request, object_id, extra_context)


@admin.register(VotoDeliberacao)
class VotoDeliberacaoAdmin(admin.ModelAdmin):
    list_display = ['deliberacao', 'membro', 'voto', 'data_registro']
    list_filter = ['voto', 'deliberacao__sessao__comissao', 'deliberacao__tipo']
    search_fields = ['membro__militar__nome_completo', 'deliberacao__assunto']
    readonly_fields = ['data_registro']
    
    fieldsets = (
        ('Informações do Voto', {
            'fields': ('deliberacao', 'membro', 'voto')
        }),
        ('Justificativa', {
            'fields': ('justificativa',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_registro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(JustificativaEncerramento)
class JustificativaEncerramentoAdmin(admin.ModelAdmin):
    list_display = ['sessao', 'membro', 'registrado_por', 'data_registro']
    list_filter = ['sessao__comissao', 'sessao__data_sessao', 'data_registro']
    search_fields = ['membro__militar__nome_completo', 'sessao__comissao__nome', 'justificativa']
    readonly_fields = ['data_registro']
    date_hierarchy = 'data_registro'
    
    fieldsets = (
        ('Informações da Justificativa', {
            'fields': ('sessao', 'membro', 'justificativa')
        }),
        ('Registro', {
            'fields': ('registrado_por', 'data_registro'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AtaSessao)
class AtaSessaoAdmin(admin.ModelAdmin):
    list_display = ['sessao', 'editado_por', 'data_edicao', 'versao', 'status']
    list_filter = ['sessao__comissao', 'data_edicao', 'status']
    search_fields = ['sessao__numero', 'editado_por__username']
    readonly_fields = ['data_edicao', 'versao']
    fieldsets = (
        ('Informações da Sessão', {
            'fields': ('sessao', 'editado_por')
        }),
        ('Conteúdo da Ata', {
            'fields': ('conteudo',),
            'classes': ('wide',)
        }),
        ('Status e Controle', {
            'fields': ('status', 'data_finalizacao'),
        }),
        ('Controle de Versão', {
            'fields': ('data_edicao', 'versao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AssinaturaAta)
class AssinaturaAtaAdmin(admin.ModelAdmin):
    list_display = ['ata', 'membro', 'assinado_por', 'data_assinatura', 'observacoes']
    list_filter = ['ata__sessao__comissao', 'data_assinatura']
    search_fields = ['ata__sessao__numero', 'membro__militar__nome_completo', 'assinado_por__username']
    readonly_fields = ['data_assinatura']
    fieldsets = (
        ('Informações da Assinatura', {
            'fields': ('ata', 'membro', 'assinado_por')
        }),
        ('Detalhes', {
            'fields': ('observacoes', 'data_assinatura')
        }),
    )


@admin.register(ModeloAta)
class ModeloAtaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_comissao', 'tipo_sessao', 'padrao', 'ativo', 'criado_por', 'data_criacao']
    list_filter = ['tipo_comissao', 'tipo_sessao', 'padrao', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao', 'criado_por__username']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    fieldsets = (
        ('Informações do Modelo', {
            'fields': ('nome', 'descricao', 'tipo_comissao', 'tipo_sessao')
        }),
        ('Conteúdo', {
            'fields': ('conteudo',),
            'classes': ('wide',)
        }),
        ('Configurações', {
            'fields': ('ativo', 'padrao')
        }),
        ('Controle', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é uma criação
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(CargoComissao)
class CargoComissaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ativo', 'ordem', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'codigo', 'descricao']
    ordering = ['ordem', 'nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'descricao')
        }),
        ('Configurações', {
            'fields': ('ativo', 'ordem')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificacaoSessao)
class NotificacaoSessaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'titulo', 'prioridade', 'lida', 'data_criacao']
    list_filter = ['tipo', 'prioridade', 'lida', 'data_criacao', 'comissao']
    search_fields = ['usuario__username', 'titulo', 'mensagem']
    readonly_fields = ['data_criacao', 'data_leitura']
    date_hierarchy = 'data_criacao'
    actions = ['marcar_como_lidas', 'limpar_notificacoes_antigas']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'tipo', 'titulo', 'mensagem', 'prioridade')
        }),
        ('Status', {
            'fields': ('lida', 'data_criacao', 'data_leitura')
        }),
        ('Referências', {
            'fields': ('sessao', 'deliberacao', 'comissao'),
            'classes': ('collapse',)
        }),
    )
    
    def marcar_como_lidas(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(lida=False).count()
        queryset.filter(lida=False).update(lida=True, data_leitura=timezone.now())
        self.message_user(request, f'{count} notificação(ões) marcada(s) como lida(s).')
    marcar_como_lidas.short_description = "Marcar como lidas"
    
    def limpar_notificacoes_antigas(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        data_limite = timezone.now() - timedelta(days=30)
        count = queryset.filter(data_criacao__lt=data_limite, lida=True).count()
        queryset.filter(data_criacao__lt=data_limite, lida=True).delete()
        self.message_user(request, f'{count} notificação(ões) antiga(s) removida(s).')
    limpar_notificacoes_antigas.short_description = "Limpar notificações antigas"


@admin.register(MensagemInstantanea)
class MensagemInstantaneaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'remetente', 'tipo', 'prioridade', 'ativa', 'lida', 'data_criacao']
    list_filter = ['tipo', 'prioridade', 'lida', 'ativa', 'data_criacao']
    search_fields = ['titulo', 'mensagem', 'remetente__username', 'destinatario__username']
    readonly_fields = ['data_criacao', 'data_leitura']
    date_hierarchy = 'data_criacao'
    actions = ['marcar_como_lidas', 'desativar_mensagens', 'ativar_mensagens']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('remetente', 'tipo', 'titulo', 'mensagem', 'prioridade')
        }),
        ('Destinatários', {
            'fields': ('destinatario', 'destinatarios_ids'),
            'description': 'Para mensagens específicas, selecione um destinatário. Para grupos, use o campo destinatarios_ids.'
        }),
        ('Status e Validade', {
            'fields': ('ativa', 'lida', 'data_criacao', 'data_leitura', 'expira_em')
        }),
    )
    
    def marcar_como_lidas(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(lida=False).count()
        queryset.filter(lida=False).update(lida=True, data_leitura=timezone.now())
        self.message_user(request, f'{count} mensagem(ns) marcada(s) como lida(s).')
    marcar_como_lidas.short_description = "Marcar como lidas"
    
    def desativar_mensagens(self, request, queryset):
        count = queryset.filter(ativa=True).count()
        queryset.filter(ativa=True).update(ativa=False)
        self.message_user(request, f'{count} mensagem(ns) desativada(s).')
    desativar_mensagens.short_description = "Desativar mensagens selecionadas"
    
    def ativar_mensagens(self, request, queryset):
        count = queryset.filter(ativa=False).count()
        queryset.filter(ativa=False).update(ativa=True)
        self.message_user(request, f'{count} mensagem(ns) ativada(s).')
    ativar_mensagens.short_description = "Ativar mensagens selecionadas"


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'participante1', 'participante2', 'ultima_atualizacao', 'ativo']
    list_filter = ['ativo', 'ultima_atualizacao']
    search_fields = ['participante1__username', 'participante2__username']
    readonly_fields = ['data_criacao', 'ultima_atualizacao']
    date_hierarchy = 'ultima_atualizacao'


@admin.register(Chamada)
class ChamadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'iniciador', 'tipo', 'status', 'data_inicio', 'data_fim', 'duracao_segundos')
    list_filter = ('tipo', 'status', 'data_inicio')
    search_fields = ('chat__id', 'iniciador__username', 'iniciador__first_name', 'iniciador__last_name')
    readonly_fields = ('data_inicio', 'data_fim', 'duracao_segundos')
    date_hierarchy = 'data_inicio'
    ordering = ('-data_inicio',)


@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'remetente', 'data_envio', 'lida']
    list_filter = ['lida', 'data_envio']
    search_fields = ['mensagem', 'remetente__username']
    readonly_fields = ['data_envio', 'data_leitura']
    date_hierarchy = 'data_envio'


@admin.register(UsuarioFuncaoMilitar)
class UsuarioFuncaoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'funcao_militar',
        'orgao',
        'unidade',
        'ativo',
        'data_criacao',
    ]
    list_filter = [
        'ativo',
        'data_criacao',
        'funcao_militar__nome',
        'orgao__nome',
    ]
    search_fields = [
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'funcao_militar__nome',
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_criacao'
    autocomplete_fields = ['usuario', 'funcao_militar']

    fieldsets = (
        ('Informações Gerais', {
            'fields': ('usuario', 'funcao_militar', 'ativo')
        }),
        ('Lotação', {
            'fields': ('orgao', 'grande_comando', 'unidade', 'sub_unidade')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )



@admin.register(FuncaoMilitar)
class FuncaoMilitarAdmin(admin.ModelAdmin):
    """Admin para Função Militar"""
    list_display = [
        'id', 'nome', 'acesso_sigilo_display', 'ordem', 'acesso_display', 
        'nivel', 'grupo_display', 'publicacao_display', 'ativo', 'data_criacao'
    ]
    list_filter = [
        'acesso_sigilo', 'acesso', 'nivel', 'grupo', 'publicacao', 'ativo', 'data_criacao'
    ]
    search_fields = ['nome', 'descricao']
    ordering = ['ordem', 'nome']
    list_editable = ['ordem', 'ativo']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ordem', 'ativo')
        }),
        ('Configurações de Acesso', {
            'fields': ('acesso_sigilo', 'acesso')
        }),
        ('Configurações de Hierarquia', {
            'fields': ('nivel', 'grupo', 'publicacao')
        }),
        ('Menus Principais', {
            'fields': (
                'menu_dashboard', 'menu_efetivo', 'menu_inativos', 
                'menu_usuarios', 'menu_permissoes'
            ),
            'classes': ('wide',)
        }),
        ('Seção de Promoções', {
            'fields': (
                'menu_fichas_oficiais', 'menu_fichas_pracas', 'menu_quadros_acesso', 
                'menu_quadros_fixacao', 'menu_almanaques', 'menu_promocoes', 
                'menu_calendarios', 'menu_comissoes', 'menu_meus_votos', 
                'menu_intersticios', 'menu_gerenciar_intersticios', 'menu_gerenciar_previsao'
            ),
            'classes': ('wide',)
        }),
        ('Administração', {
            'fields': (
                'menu_administracao', 'menu_logs', 'menu_medalhas', 'menu_lotacoes'
            ),
            'classes': ('wide',)
        }),
        ('Configurações Especiais', {
            'fields': ('menu_apenas_visualizacao',),
            'classes': ('wide',)
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def acesso_sigilo_display(self, obj):
        return obj.acesso_sigilo_display
    acesso_sigilo_display.short_description = 'Acesso/Sigilo'
    
    def acesso_display(self, obj):
        return obj.acesso_display
    acesso_display.short_description = 'Acesso'
    
    def grupo_display(self, obj):
        return obj.grupo_display
    grupo_display.short_description = 'Grupo'
    
    def publicacao_display(self, obj):
        return obj.publicacao_display
    publicacao_display.short_description = 'Publicação'




class ItemCalendarioPromocaoInline(admin.TabularInline):
    model = ItemCalendarioPromocao
    extra = 1
    fields = ['tipo_atividade', 'data_inicio', 'data_fim', 'ordem', 'observacoes']
    ordering = ['ordem']


@admin.register(CalendarioPromocao)
class CalendarioPromocaoAdmin(admin.ModelAdmin):
    list_display = ['periodo_completo', 'ativo', 'total_itens', 'data_criacao']
    list_filter = ['ano', 'semestre', 'ativo', 'data_criacao']
    search_fields = ['ano', 'observacoes']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_criacao'
    inlines = [ItemCalendarioPromocaoInline]
    actions = ['duplicar_calendario', 'ativar_calendario', 'desativar_calendario']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('ano', 'semestre', 'ativo')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def total_itens(self, obj):
        return obj.itens.count()
    total_itens.short_description = "Total de Itens"
    
    def duplicar_calendario(self, request, queryset):
        for calendario in queryset:
            # Criar novo calendário
            novo_calendario = CalendarioPromocao.objects.create(
                ano=calendario.ano,
                semestre=calendario.semestre,
                tipo=calendario.tipo,
                ativo=False,

                observacoes=f"Cópia do calendário {calendario.periodo_completo}"
            )
            
            # Copiar itens
            for item in calendario.itens.all():
                ItemCalendarioPromocao.objects.create(
                    calendario=novo_calendario,
                    tipo_atividade=item.tipo_atividade,
                    data_inicio=item.data_inicio,
                    data_fim=item.data_fim,
                    ordem=item.ordem,
                    observacoes=item.observacoes
                )
        
        self.message_user(request, f'{queryset.count()} calendário(s) duplicado(s) com sucesso.')
    duplicar_calendario.short_description = "Duplicar calendário selecionado"
    
    def ativar_calendario(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} calendário(s) ativado(s) com sucesso.')
    ativar_calendario.short_description = "Ativar calendário selecionado"
    
    def desativar_calendario(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} calendário(s) desativado(s) com sucesso.')
    desativar_calendario.short_description = "Desativar calendário selecionado"


@admin.register(ItemCalendarioPromocao)
class ItemCalendarioPromocaoAdmin(admin.ModelAdmin):
    list_display = [
        'calendario', 'tipo_atividade', 'periodo_formatado', 'status_atual', 'ordem'
    ]
    list_filter = [
        'calendario__ano', 'calendario__semestre', 'tipo_atividade', 'calendario__ativo'
    ]
    search_fields = [
        'calendario__ano', 'get_tipo_atividade_display', 'observacoes'
    ]
    readonly_fields = ['status_atual']
    ordering = ['calendario', 'ordem']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('calendario', 'tipo_atividade', 'ordem')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Status', {
            'fields': ('status_atual',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    def status_atual(self, obj):
        status_map = {
            'PENDENTE': 'Pendente',
            'EM_ANDAMENTO': 'Em Andamento',
            'CONCLUIDO': 'Concluído'
        }
        status = obj.status_atual
        return status_map.get(status, status)
    status_atual.short_description = "Status Atual"


@admin.register(AssinaturaCalendarioPromocao)
class AssinaturaCalendarioPromocaoAdmin(admin.ModelAdmin):
    list_display = [
        'calendario', 'tipo_assinatura', 'assinado_por', 'data_assinatura', 'codigo_verificacao'
    ]
    list_filter = [
        'tipo_assinatura', 'data_assinatura', 'calendario__tipo', 'calendario__status'
    ]
    search_fields = [
        'calendario__numero', 'assinado_por__username', 'assinado_por__first_name', 
        'assinado_por__last_name', 'codigo_verificacao'
    ]
    readonly_fields = ['data_assinatura', 'hash_assinatura', 'codigo_verificacao']
    date_hierarchy = 'data_assinatura'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('calendario', 'tipo_assinatura', 'assinado_por')
        }),
        ('Detalhes da Assinatura', {
            'fields': ('data_assinatura', 'hash_assinatura', 'codigo_verificacao')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )


@admin.register(AlmanaqueMilitar)
class AlmanaqueMilitarAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'data_geracao', 'total_geral', 'ativo'
    ]
    list_filter = [
        'tipo', 'data_geracao', 'ativo'
    ]
    search_fields = [
        'titulo', 'observacoes'
    ]
    readonly_fields = [
        'data_geracao', 'total_oficiais', 'total_pracas', 'total_geral'
    ]
    date_hierarchy = 'data_geracao'
    actions = ['reativar_almanaques', 'desativar_almanaques']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'tipo', 'ativo')
        }),
        ('Arquivo', {
            'fields': ('arquivo_pdf',)
        }),
        ('Estatísticas', {
            'fields': ('total_oficiais', 'total_pracas', 'total_geral'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_geracao',),
            'classes': ('collapse',)
        }),
    )

    def reativar_almanaques(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} almanaque(s) reativado(s) com sucesso.')
    reativar_almanaques.short_description = "Reativar almanaques selecionados"

    def desativar_almanaques(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} almanaque(s) desativado(s).')
    desativar_almanaques.short_description = "Desativar almanaques selecionados"


@admin.register(AssinaturaAlmanaque)
class AssinaturaAlmanaqueAdmin(admin.ModelAdmin):
    list_display = [
        'almanaque', 'assinado_por', 'funcao_militar', 'data_assinatura'
    ]
    list_filter = [
        'data_assinatura', 'almanaque__tipo'
    ]
    search_fields = [
        'assinado_por__username', 'assinado_por__first_name', 'assinado_por__last_name',
        'funcao_militar', 'observacoes'
    ]
    readonly_fields = [
        'data_assinatura'
    ]
    date_hierarchy = 'data_assinatura'

    fieldsets = (
        ('Informações da Assinatura', {
            'fields': ('almanaque', 'assinado_por', 'funcao_militar')
        }),
        ('Detalhes', {
            'fields': ('observacoes',)
        }),
        ('Controle', {
            'fields': ('data_assinatura',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LogSistema)
class LogSistemaAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'nivel', 'modulo', 'acao', 'usuario', 'descricao_resumida', 'ip_address'
    ]
    list_filter = [
        'nivel', 'modulo', 'acao', 'timestamp', 'processado', 'notificado'
    ]
    search_fields = [
        'descricao', 'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'modelo_afetado', 'objeto_str', 'ip_address'
    ]
    readonly_fields = [
        'timestamp', 'nivel', 'modulo', 'acao', 'usuario', 'descricao', 'detalhes',
        'modelo_afetado', 'objeto_id', 'objeto_str', 'ip_address', 'user_agent', 'url',
        'metodo_http', 'tempo_execucao', 'erro', 'traceback', 'processado', 'notificado'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    list_per_page = 50
    actions = ['marcar_como_processado', 'marcar_como_notificado', 'limpar_logs_antigos']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('timestamp', 'nivel', 'modulo', 'acao', 'usuario')
        }),
        ('Descrição', {
            'fields': ('descricao', 'detalhes')
        }),
        ('Objeto Afetado', {
            'fields': ('modelo_afetado', 'objeto_id', 'objeto_str'),
            'classes': ('collapse',)
        }),
        ('Informações da Requisição', {
            'fields': ('ip_address', 'user_agent', 'url', 'metodo_http'),
            'classes': ('collapse',)
        }),
        ('Performance e Erros', {
            'fields': ('tempo_execucao', 'erro', 'traceback'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('processado', 'notificado', 'observacoes')
        }),
    )
    
    def descricao_resumida(self, obj):
        return obj.get_descricao_resumida()
    descricao_resumida.short_description = "Descrição"
    
    def marcar_como_processado(self, request, queryset):
        count = queryset.count()
        queryset.update(processado=True)
        self.message_user(request, f'{count} log(s) marcado(s) como processado(s).')
    marcar_como_processado.short_description = "Marcar como processado"
    
    def marcar_como_notificado(self, request, queryset):
        count = queryset.count()
        queryset.update(notificado=True)
        self.message_user(request, f'{count} log(s) marcado(s) como notificado(s).')
    marcar_como_notificado.short_description = "Marcar como notificado"
    
    def limpar_logs_antigos(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        
        # Por padrão, remover logs com mais de 30 dias
        data_limite = timezone.now() - timedelta(days=30)
        logs_removidos = LogSistema.objects.filter(timestamp__lt=data_limite).count()
        LogSistema.objects.filter(timestamp__lt=data_limite).delete()
        
        self.message_user(request, f'{logs_removidos} log(s) antigo(s) removido(s).')
    limpar_logs_antigos.short_description = "Limpar logs antigos (30+ dias)"
    
    def has_add_permission(self, request):
        """Impede a criação manual de logs"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Permite apenas editar campos de controle para superusuários"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Permite exclusão apenas para superusuários"""
        return request.user.is_superuser
    
    class Media:
        css = {
            'all': ('admin/css/logs.css',)
        }


@admin.register(Qualificacao)
class QualificacaoAdmin(admin.ModelAdmin):
    list_display = ('militar', 'nome_curso', 'tipo', 'carga_horaria', 'instituicao', 'status_verificacao_display', 'data_conclusao')
    list_filter = ('tipo', 'status_verificacao', 'data_conclusao', 'data_cadastro')
    search_fields = ('militar__nome_completo', 'nome_curso', 'instituicao')
    autocomplete_fields = ('militar',)
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('militar', 'tipo', 'nome_curso', 'carga_horaria', 'instituicao')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_conclusao')
        }),
        ('Verificação', {
            'fields': ('status_verificacao', 'observacoes')
        }),
        ('Documento', {
            'fields': ('arquivo_certificado',)
        }),
        ('Metadados', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def status_verificacao_display(self, obj):
        return obj.status_verificacao_display
    status_verificacao_display.short_description = 'Status'


@admin.register(Publicacao)
class PublicacaoAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'titulo', 'tipo', 'status', 'data_criacao', 
        'data_publicacao', 'criado_por', 'ativo'
    ]
    list_filter = [
        'tipo', 'status', 'data_criacao', 'data_publicacao', 
        'origem_publicacao', 'tipo_publicacao', 'ativo'
    ]
    search_fields = [
        'numero', 'titulo', 'origem_publicacao', 'tipo_publicacao', 
        'topicos', 'criado_por__username', 'criado_por__first_name', 
        'criado_por__last_name'
    ]
    readonly_fields = [
        'data_criacao', 'numero', 'criado_por', 'data_atualizacao'
    ]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'titulo', 'tipo', 'status', 'ativo')
        }),
        ('Conteúdo', {
            'fields': ('origem_publicacao', 'tipo_publicacao', 'topicos', 'conteudo')
        }),
        ('Organograma', {
            'fields': ('orgao', 'grande_comando', 'unidade', 'sub_unidade'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_publicacao', 'data_boletim', 'data_disponibilizacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('criado_por', 'publicado_por', 'numero_boletim', 'editada_apos_devolucao'),
            'classes': ('collapse',)
        }),
        ('Militares Indexados', {
            'fields': ('militares_indexados',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Tornar campos readonly baseado no status e usuário"""
        readonly_fields = list(self.readonly_fields)
        
        # Se a publicação está publicada, tornar mais campos readonly
        if obj and obj.status == 'PUBLICADA':
            readonly_fields.extend([
                'titulo', 'origem_publicacao', 'tipo_publicacao', 'topicos', 
                'conteudo', 'tipo', 'status'
            ])
        
        return readonly_fields
    
    def has_change_permission(self, request, obj=None):
        """Controlar permissões de edição baseado no status"""
        if obj and obj.status == 'PUBLICADA':
            # Apenas superusuários podem editar publicações publicadas
            return request.user.is_superuser
        return super().has_change_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        """Personalizar salvamento"""
        if not change:  # Nova publicação
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(PlanoFerias)
class PlanoFeriasAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ano_referencia', 'ano_plano', 'status', 'total_ferias', 'data_criacao')
    list_filter = ('status', 'ano_referencia', 'ano_plano', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'ano_referencia', 'ano_plano')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    
    fieldsets = (
        ('Informações do Plano', {
            'fields': ('titulo', 'ano_referencia', 'ano_plano', 'descricao', 'status')
        }),
        ('Informações Adicionais', {
            'fields': ('documento_referencia', 'numero_documento')
        }),
        ('Controle', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    def total_ferias(self, obj):
        return obj.total_ferias
    total_ferias.short_description = "Total de Férias"


@admin.register(Ferias)
class FeriasAdmin(admin.ModelAdmin):
    list_display = ('militar', 'tipo', 'ano_referencia', 'data_inicio', 'data_fim', 'quantidade_dias', 'status')
    list_filter = ('tipo', 'status', 'ano_referencia', 'data_inicio')
    search_fields = ('militar__nome_completo', 'militar__nome_guerra', 'militar__matricula', 'ano_referencia')
    date_hierarchy = 'data_inicio'
    readonly_fields = ('data_cadastro', 'data_atualizacao', 'cadastrado_por')
    
    fieldsets = (
        ('Informações do Militar', {
            'fields': ('militar',)
        }),
        ('Dados das Férias', {
            'fields': ('tipo', 'ano_referencia', 'data_inicio', 'data_fim', 'quantidade_dias', 'status')
        }),
        ('Informações Adicionais', {
            'fields': ('observacoes', 'documento_referencia', 'numero_documento')
        }),
        ('Controle', {
            'fields': ('cadastrado_por', 'data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.cadastrado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(LicencaEspecial)
class LicencaEspecialAdmin(admin.ModelAdmin):
    list_display = ('militar', 'decenio', 'quantidade_meses', 'data_inicio', 'data_fim', 'status')
    list_filter = ('status', 'decenio', 'data_inicio')
    search_fields = ('militar__nome_completo', 'militar__nome_guerra', 'militar__matricula')
    date_hierarchy = 'data_inicio'
    readonly_fields = ('data_cadastro', 'data_atualizacao', 'cadastrado_por')
    
    fieldsets = (
        ('Informações do Militar', {
            'fields': ('plano', 'militar',)
        }),
        ('Dados da Licença Especial', {
            'fields': ('decenio', 'quantidade_meses', 'data_inicio', 'data_fim', 'status')
        }),
        ('Informações Adicionais', {
            'fields': ('observacoes', 'documento_referencia', 'numero_documento')
        }),
        ('Controle', {
            'fields': ('cadastrado_por', 'data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.cadastrado_por = request.user
        super().save_model(request, obj, form, change)


class PlanoLicencaEspecialAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ano_plano', 'status', 'total_licencas', 'data_criacao')
    list_filter = ('status', 'ano_plano', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'ano_plano')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    
    fieldsets = (
        ('Informações do Plano', {
            'fields': ('titulo', 'ano_plano', 'descricao', 'status')
        }),
        ('Informações Adicionais', {
            'fields': ('documento_referencia', 'numero_documento')
        }),
        ('Controle', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    def total_licencas(self, obj):
        return obj.total_licencas
    total_licencas.short_description = "Total de Licenças"


@admin.register(PlanoLicencaEspecial)
class PlanoLicencaEspecialAdminRegistered(PlanoLicencaEspecialAdmin):
    pass


@admin.register(DocumentoFerias)
class DocumentoFeriasAdmin(admin.ModelAdmin):
    list_display = ('ferias', 'tipo', 'titulo', 'upload_por', 'data_upload')
    list_filter = ('tipo', 'data_upload')
    search_fields = ('ferias__militar__nome_completo', 'titulo', 'descricao')
    readonly_fields = ('data_upload',)
    
    fieldsets = (
        ('Informações do Documento', {
            'fields': ('ferias', 'tipo', 'titulo', 'descricao')
        }),
        ('Arquivo', {
            'fields': ('arquivo',)
        }),
        ('Controle', {
            'fields': ('upload_por', 'data_upload'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Viatura)
class ViaturaAdmin(admin.ModelAdmin):
    list_display = ('prefixo', 'placa', 'tipo', 'marca', 'modelo', 'ano_fabricacao', 'status', 'ativo', 'get_organizacao_display')
    list_filter = ('tipo', 'status', 'combustivel', 'ativo', 'orgao', 'grande_comando', 'unidade', 'sub_unidade')
    search_fields = ('prefixo', 'placa', 'marca', 'modelo', 'chassi', 'renavam')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('prefixo', 'placa', 'tipo', 'marca', 'modelo', 'ano_fabricacao', 'ano_modelo')
        }),
        ('Documentação', {
            'fields': ('chassi', 'renavam', 'cor')
        }),
        ('Status e Uso', {
            'fields': ('status', 'km_atual', 'combustivel', 'capacidade_tanque')
        }),
        ('Organização', {
            'fields': ('orgao', 'grande_comando', 'unidade', 'sub_unidade')
        }),
        ('Aquisição', {
            'fields': ('data_aquisicao', 'valor_aquisicao', 'fornecedor'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Controle', {
            'fields': ('ativo', 'criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_organizacao_display(self, obj):
        return obj.get_organizacao_display()
    get_organizacao_display.short_description = 'Organização'


@admin.register(AbastecimentoViatura)
class AbastecimentoViaturaAdmin(admin.ModelAdmin):
    list_display = ('viatura', 'data_abastecimento', 'quantidade_litros', 'valor_litro', 'valor_total', 'km_abastecimento', 'tipo_combustivel', 'ativo')
    list_filter = ('tipo_combustivel', 'ativo', 'data_abastecimento', 'viatura')
    search_fields = ('viatura__placa', 'viatura__prefixo', 'posto_fornecedor', 'observacoes')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    date_hierarchy = 'data_abastecimento'
    
    fieldsets = (
        ('Informações do Abastecimento', {
            'fields': ('viatura', 'data_abastecimento', 'km_abastecimento', 'tipo_combustivel')
        }),
        ('Valores', {
            'fields': ('quantidade_litros', 'valor_litro', 'valor_total')
        }),
        ('Detalhes', {
            'fields': ('posto_fornecedor', 'responsavel', 'observacoes')
        }),
        ('Controle', {
            'fields': ('ativo', 'criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HistoricoAbastecimentoAssinado)
class HistoricoAbastecimentoAssinadoAdmin(admin.ModelAdmin):
    list_display = ('viatura', 'data_inicio', 'data_fim', 'total_valor', 'quantidade_abastecimentos', 'data_geracao', 'gerado_por')
    list_filter = ('data_geracao', 'viatura')
    search_fields = ('viatura__placa', 'viatura__prefixo')
    readonly_fields = ('data_geracao', 'gerado_por')
    date_hierarchy = 'data_geracao'


@admin.register(AssinaturaHistoricoAbastecimento)
class AssinaturaHistoricoAbastecimentoAdmin(admin.ModelAdmin):
    list_display = ('historico', 'assinado_por', 'tipo_assinatura', 'data_assinatura', 'funcao_assinatura')
    list_filter = ('tipo_assinatura', 'tipo_midia', 'data_assinatura')
    search_fields = ('historico__viatura__placa', 'assinado_por__username', 'assinado_por__first_name', 'assinado_por__last_name')
    readonly_fields = ('data_assinatura',)


@admin.register(ManutencaoViatura)
class ManutencaoViaturaAdmin(admin.ModelAdmin):
    list_display = ('viatura', 'data_manutencao', 'tipo_manutencao', 'valor_manutencao', 'km_manutencao', 'fornecedor_oficina', 'ativo')
    list_filter = ('tipo_manutencao', 'ativo', 'data_manutencao', 'viatura')
    search_fields = ('viatura__placa', 'viatura__prefixo', 'fornecedor_oficina', 'descricao_servico', 'pecas_trocadas', 'observacoes')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    date_hierarchy = 'data_manutencao'
    
    fieldsets = (
        ('Informações da Manutenção', {
            'fields': ('viatura', 'data_manutencao', 'tipo_manutencao', 'km_manutencao')
        }),
        ('Valores e Detalhes', {
            'fields': ('valor_manutencao', 'fornecedor_oficina', 'descricao_servico', 'pecas_trocadas', 'proximo_km_revisao')
        }),
        ('Outras Informações', {
            'fields': ('responsavel', 'observacoes')
        }),
        ('Controle', {
            'fields': ('ativo', 'criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TrocaOleoViatura)
class TrocaOleoViaturaAdmin(admin.ModelAdmin):
    list_display = ('viatura', 'data_troca', 'tipo_oleo', 'quantidade_litros', 'valor_total', 'km_troca', 'trocou_filtro_oleo', 'trocou_filtro_combustivel', 'trocou_filtro_ar', 'ativo')
    list_filter = ('tipo_oleo', 'trocou_filtro_oleo', 'trocou_filtro_combustivel', 'trocou_filtro_ar', 'ativo', 'data_troca', 'viatura')
    search_fields = ('viatura__placa', 'viatura__prefixo', 'fornecedor_oficina', 'observacoes', 'outras_pecas')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    date_hierarchy = 'data_troca'
    
    fieldsets = (
        ('Informações da Troca de Óleo', {
            'fields': ('viatura', 'data_troca', 'km_troca', 'tipo_oleo', 'nome_oleo')
        }),
        ('Quantidade e Valores', {
            'fields': ('quantidade_litros', 'valor_litro', 'valor_total')
        }),
        ('Filtros', {
            'fields': ('trocou_filtro_oleo', 'valor_filtro_oleo', 'trocou_filtro_combustivel', 'valor_filtro_combustivel', 'trocou_filtro_ar', 'valor_filtro_ar')
        }),
        ('Aditivo de Arrefecimento', {
            'fields': ('adicionou_aditivo_arrefecimento', 'quantidade_aditivo_arrefecimento', 'valor_aditivo_arrefecimento')
        }),
        ('Outras Peças', {
            'fields': ('outras_pecas', 'valor_outras_pecas')
        }),
        ('Outras Informações', {
            'fields': ('fornecedor_oficina', 'proximo_km_troca', 'responsavel', 'observacoes')
        }),
        ('Controle', {
            'fields': ('ativo', 'criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Arma)
class ArmaAdmin(admin.ModelAdmin):
    list_display = ('numero_serie', 'tipo', 'marca', 'modelo', 'calibre', 'situacao', 'militar_responsavel', 'get_organizacao_instancia', 'ativo')
    list_filter = ('tipo', 'calibre', 'situacao', 'ativo', 'orgao', 'grande_comando', 'unidade')
    search_fields = ('numero_serie', 'marca', 'modelo', 'numero_registro_policia', 'militar_responsavel__nome_completo', 'numero_inquerito_pm', 'numero_inquerito_pc', 'delegado_inquerito_pc')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    autocomplete_fields = ('militar_responsavel', 'encarregado_inquerito_pm')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(ArmaParticular)
class ArmaParticularAdmin(admin.ModelAdmin):
    list_display = ('militar', 'numero_serie', 'tipo', 'marca', 'modelo', 'calibre', 'status', 'autorizado_uso_servico', 'ativo')
    list_filter = ('tipo', 'calibre', 'status', 'autorizado_uso_servico', 'ativo')
    search_fields = ('numero_serie', 'marca', 'modelo', 'numero_registro_policia', 'militar__nome_completo', 'militar__matricula')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    autocomplete_fields = ('militar', 'autorizado_por')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(MovimentacaoArma)
class MovimentacaoArmaAdmin(admin.ModelAdmin):
    list_display = ('arma', 'tipo_movimentacao', 'data_movimentacao', 'militar_origem', 'militar_destino', 'responsavel_movimentacao')
    list_filter = ('tipo_movimentacao', 'data_movimentacao')
    search_fields = ('arma__numero_serie', 'militar_origem__nome_completo', 'militar_destino__nome_completo', 'observacoes')
    readonly_fields = ('data_criacao',)
    autocomplete_fields = ('arma', 'militar_origem', 'militar_destino', 'responsavel_movimentacao')


@admin.register(ConfiguracaoArma)
class ConfiguracaoArmaAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'tipo', 'get_tipo_acessorio_display', 'calibre', 'ativo', 'data_criacao')
    list_filter = ('tipo', 'tipo_acessorio', 'calibre', 'ativo')
    search_fields = ('marca', 'modelo')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    
    def get_tipo_acessorio_display(self, obj):
        if obj.tipo == 'ACESSORIO' and obj.tipo_acessorio:
            return obj.get_tipo_acessorio_display()
        return '-'
    get_tipo_acessorio_display.short_description = 'Tipo de Acessório'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(HistoricoAlteracaoArma)
class HistoricoAlteracaoArmaAdmin(admin.ModelAdmin):
    list_display = ('arma', 'campo_alterado', 'valor_anterior', 'valor_novo', 'alterado_por', 'data_alteracao')
    list_filter = ('data_alteracao', 'campo_alterado')
    search_fields = ('arma__numero_serie', 'campo_alterado', 'alterado_por__username', 'alterado_por__first_name', 'alterado_por__last_name')
    readonly_fields = ('arma', 'alterado_por', 'data_alteracao', 'campo_alterado', 'valor_anterior', 'valor_novo', 'observacao')
    date_hierarchy = 'data_alteracao'
    
    def has_add_permission(self, request):
        return False  # Histórico é criado automaticamente, não deve ser criado manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Histórico não deve ser editado
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Apenas superusuários podem deletar histórico


@admin.register(AssinaturaMovimentacaoArma)
class AssinaturaMovimentacaoArmaAdmin(admin.ModelAdmin):
    list_display = ('movimentacao', 'assinado_por', 'militar', 'tipo_assinatura', 'data_assinatura', 'funcao_assinatura')
    list_filter = ('tipo_assinatura', 'data_assinatura')
    search_fields = ('movimentacao__arma__numero_serie', 'assinado_por__username', 'militar__nome_completo', 'funcao_assinatura')
    readonly_fields = ('data_assinatura',)
    autocomplete_fields = ('movimentacao', 'assinado_por', 'militar')


@admin.register(TransferenciaArma)
class TransferenciaArmaAdmin(admin.ModelAdmin):
    list_display = ('arma', 'get_organizacao_origem', 'get_organizacao_destino', 'data_transferencia', 'transferido_por')
    list_filter = ('data_transferencia',)
    search_fields = ('arma__numero_serie', 'observacoes')
    readonly_fields = ('data_transferencia',)
    autocomplete_fields = ('arma', 'transferido_por')
    date_hierarchy = 'data_transferencia'
    
    def get_organizacao_origem(self, obj):
        return obj.get_organizacao_origem()
    get_organizacao_origem.short_description = 'Origem'
    
    def get_organizacao_destino(self, obj):
        return obj.get_organizacao_destino()
    get_organizacao_destino.short_description = 'Destino'


@admin.register(CautelaArma)
class CautelaArmaAdmin(admin.ModelAdmin):
    list_display = ('arma', 'militar', 'get_organizacao', 'data_entrega', 'data_devolucao', 'ativa', 'entregue_por')
    list_filter = ('ativa', 'data_entrega', 'data_devolucao')
    search_fields = ('arma__numero_serie', 'militar__nome_completo', 'observacoes')
    readonly_fields = ('data_entrega',)
    autocomplete_fields = ('arma', 'militar', 'entregue_por', 'devolvido_por')
    date_hierarchy = 'data_entrega'
    
    def get_organizacao(self, obj):
        return obj.get_organizacao()
    get_organizacao.short_description = 'Organização'


# ============================================================================
# ADMIN PARA TOMBAMENTO DE BENS MÓVEIS
# ============================================================================

@admin.register(BemMovel)
class BemMovelAdmin(admin.ModelAdmin):
    list_display = ('numero_tombamento', 'descricao', 'categoria', 'situacao', 'get_organizacao', 'responsavel_atual', 'ativo', 'data_criacao')
    list_filter = ('categoria', 'situacao', 'ativo', 'data_criacao')
    search_fields = ('numero_tombamento', 'descricao', 'marca', 'modelo', 'numero_serie', 'patrimonio')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ('responsavel_atual', 'criado_por')
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('numero_tombamento', 'descricao', 'categoria', 'marca', 'modelo', 'numero_serie', 'patrimonio')
        }),
        ('Localização', {
            'fields': ('orgao', 'grande_comando', 'unidade', 'sub_unidade', 'localizacao_detalhada')
        }),
        ('Informações de Aquisição', {
            'fields': ('data_aquisicao', 'valor_aquisicao', 'fornecedor', 'nota_fiscal')
        }),
        ('Controle', {
            'fields': ('situacao', 'responsavel_atual', 'observacoes', 'ativo')
        }),
        ('Sistema', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_organizacao(self, obj):
        return obj.get_organizacao()
    get_organizacao.short_description = 'Organização'


@admin.register(TombamentoBemMovel)
class TombamentoBemMovelAdmin(admin.ModelAdmin):
    list_display = ('bem_movel', 'tipo_tombamento', 'data_tombamento', 'get_origem', 'get_destino', 'ativo', 'criado_por')
    list_filter = ('tipo_tombamento', 'data_tombamento', 'ativo')
    search_fields = ('bem_movel__numero_tombamento', 'bem_movel__descricao', 'observacoes')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = (
        'bem_movel', 'responsavel_origem', 'responsavel_destino', 'criado_por'
    )
    date_hierarchy = 'data_tombamento'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('bem_movel', 'tipo_tombamento', 'data_tombamento')
        }),
        ('Origem', {
            'fields': ('orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem', 'responsavel_origem')
        }),
        ('Destino', {
            'fields': ('orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino', 'responsavel_destino')
        }),
        ('Informações Adicionais', {
            'fields': ('valor_atual', 'observacoes', 'ativo')
        }),
        ('Sistema', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_origem(self, obj):
        return obj.get_origem_formatada()
    get_origem.short_description = 'Origem'
    
    def get_destino(self, obj):
        return obj.get_destino_formatada()
    get_destino.short_description = 'Destino'


@admin.register(HistoricoTombamento)
class HistoricoTombamentoAdmin(admin.ModelAdmin):
    list_display = ('tombamento', 'campo_alterado', 'valor_anterior', 'valor_novo', 'data_alteracao', 'alterado_por')
    list_filter = ('campo_alterado', 'data_alteracao')
    search_fields = ('tombamento__bem_movel__numero_tombamento', 'campo_alterado', 'observacoes')
    readonly_fields = ('data_alteracao',)
    autocomplete_fields = ('tombamento', 'alterado_por')
    date_hierarchy = 'data_alteracao'


# ============================================================================
# ADMIN PARA ALMOXARIFADO
# ============================================================================

@admin.register(ProdutoAlmoxarifado)
class ProdutoAlmoxarifadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'categoria', 'quantidade_atual', 'get_status_estoque_display', 'valor_unitario', 'ativo', 'data_criacao')
    list_filter = ('categoria', 'unidade_medida', 'ativo', 'data_criacao')
    search_fields = ('codigo', 'descricao', 'marca', 'modelo')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ('criado_por',)
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'descricao', 'categoria', 'unidade_medida', 'marca', 'modelo')
        }),
        ('Estoque', {
            'fields': ('estoque_minimo', 'estoque_maximo', 'quantidade_atual', 'localizacao')
        }),
        ('Informações de Compra', {
            'fields': ('valor_unitario', 'fornecedor_principal')
        }),
        ('Controle', {
            'fields': ('observacoes', 'ativo')
        }),
        ('Sistema', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_estoque_display(self, obj):
        return obj.get_status_estoque_display()
    get_status_estoque_display.short_description = 'Status Estoque'


@admin.register(EntradaAlmoxarifado)
class EntradaAlmoxarifadoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo_entrada', 'data_entrada', 'quantidade', 'fornecedor', 'ativo', 'criado_por')
    list_filter = ('tipo_entrada', 'data_entrada', 'ativo')
    search_fields = ('produto__codigo', 'produto__descricao', 'fornecedor', 'nota_fiscal', 'observacoes')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ('produto', 'responsavel', 'criado_por')
    date_hierarchy = 'data_entrada'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('produto', 'tipo_entrada', 'data_entrada', 'quantidade')
        }),
        ('Origem', {
            'fields': ('fornecedor', 'nota_fiscal', 'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem', 'responsavel')
        }),
        ('Informações Adicionais', {
            'fields': ('observacoes', 'ativo')
        }),
        ('Sistema', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaidaAlmoxarifado)
class SaidaAlmoxarifadoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo_saida', 'data_saida', 'quantidade', 'requisitante', 'get_destino_formatada', 'ativo', 'criado_por')
    list_filter = ('tipo_saida', 'data_saida', 'ativo')
    search_fields = ('produto__codigo', 'produto__descricao', 'numero_requisicao', 'observacoes')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ('produto', 'requisitante', 'responsavel_entrega', 'criado_por')
    date_hierarchy = 'data_saida'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('produto', 'tipo_saida', 'data_saida', 'quantidade', 'numero_requisicao')
        }),
        ('Destino', {
            'fields': ('orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino', 'requisitante', 'responsavel_entrega')
        }),
        ('Informações Adicionais', {
            'fields': ('observacoes', 'ativo')
        }),
        ('Sistema', {
            'fields': ('criado_por', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_destino_formatada(self, obj):
        return obj.get_destino_formatada()
    get_destino_formatada.short_description = 'Destino'


@admin.register(HistoricoAlmoxarifado)
class HistoricoAlmoxarifadoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo_movimentacao', 'campo_alterado', 'quantidade_anterior', 'quantidade_nova', 'data_alteracao', 'alterado_por')
    list_filter = ('tipo_movimentacao', 'campo_alterado', 'data_alteracao')
    search_fields = ('produto__codigo', 'produto__descricao', 'tipo_movimentacao', 'campo_alterado', 'observacoes')
    readonly_fields = ('data_alteracao',)
    autocomplete_fields = ('produto', 'alterado_por')
    date_hierarchy = 'data_alteracao'


@admin.register(ProcessoAdministrativo)
class ProcessoAdministrativoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'assunto', 'tipo', 'status', 'prioridade', 'data_abertura', 'data_prazo', 'ativo', 'criado_por')
    list_filter = ('tipo', 'status', 'prioridade', 'ativo', 'data_abertura', 'data_criacao')
    search_fields = ('numero', 'assunto', 'descricao')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ('criado_por',)
    filter_horizontal = ('militares_envolvidos', 'militares_encarregados', 'escrivaos')
    date_hierarchy = 'data_abertura'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'tipo', 'assunto', 'descricao')
        }),
        ('Status e Prioridade', {
            'fields': ('status', 'prioridade', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_abertura', 'data_prazo', 'data_conclusao', 'data_arquivamento')
        }),
        ('Militares', {
            'fields': ('militares_envolvidos', 'militares_encarregados', 'escrivaos')
        }),
        ('Organograma', {
            'fields': ('orgao', 'grande_comando', 'unidade', 'sub_unidade'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('observacoes', 'criado_por', 'data_criacao', 'data_atualizacao')
        }),
    )

