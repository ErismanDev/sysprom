from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from .models import (
    Militar, FichaConceitoOficiais, FichaConceitoPracas, QuadroAcesso, ItemQuadroAcesso,
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio, PrevisaoVaga,
    ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, JustificativaEncerramento, AtaSessao, AssinaturaAta, ModeloAta, NotificacaoSessao, CargoComissao, UsuarioFuncao, CargoFuncao, PermissaoFuncao, PerfilAcesso,
    CalendarioPromocao, ItemCalendarioPromocao, AssinaturaCalendarioPromocao, AlmanaqueMilitar, AssinaturaAlmanaque
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
        'tempo_posto', 'cursos_especializacao', 'medalha_federal', 'elogio_individual',
        'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento',
        'data_registro'
    ]
    list_filter = [
        'militar__quadro', 'militar__posto_graduacao'
    ]
    search_fields = ['militar__nome_completo', 'militar__matricula']
    readonly_fields = ['pontuacao_total', 'data_registro']
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
                'tempo_posto', 'cursos_especializacao', 'cursos_csbm', 'cursos_cfsd', 'cursos_chc', 'cursos_chsgt',
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
    fields = ['pontuacao_total', 'tempo_posto', 'cursos_especializacao', 'cursos_csbm', 'medalha_federal', 'elogio_individual', 'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento']
    readonly_fields = ['pontuacao_total']

    def pontuacao_total(self, obj):
        return obj.calcular_pontos()
    pontuacao_total.short_description = 'Pontuação Total'


@admin.register(FichaConceitoPracas)
class FichaConceitoPracasAdmin(admin.ModelAdmin):
    list_display = [
        'militar', 'pontuacao_total',
        'tempo_posto', 'cursos_especializacao', 'medalha_federal', 'elogio_individual',
        'punicao_repreensao', 'punicao_detencao', 'punicao_prisao', 'falta_aproveitamento',
        'data_registro'
    ]
    list_filter = [
        'militar__quadro', 'militar__posto_graduacao'
    ]
    search_fields = ['militar__nome_completo', 'militar__matricula']
    readonly_fields = ['pontuacao_total', 'data_registro']
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
                'tempo_posto', 'cursos_especializacao', 'cursos_cfsd', 'cursos_chc', 'cursos_chsgt',
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
    search_fields = ['matricula', 'nome_completo', 'nome_guerra', 'cpf']
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
                'numeracao_antiguidade', 'matricula', 'nome_completo', 'nome_guerra', 'cpf', 'rg', 'orgao_expedidor',
                'data_nascimento', 'sexo'
            )
        }),
        ('Informações Militares', {
            'fields': (
                'quadro', 'posto_graduacao', 'data_ingresso', 'data_promocao_atual', 'situacao'
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
                situacao='AT',
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
                situacao='AT',
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
        'data_promocao', 'data_publicacao', 'numero_ato'
    ]
    list_filter = ['criterio', 'data_promocao', 'data_publicacao', 'militar__quadro']
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


@admin.register(UsuarioFuncao)
class UsuarioFuncaoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'cargo_funcao_nome',
        'tipo_funcao',
        'status',
        'data_inicio',
        'data_fim',
        'esta_ativo',
    ]
    list_filter = [
        'tipo_funcao',
        'status',
        'data_inicio',
        'data_fim',
        'cargo_funcao__nome',
    ]
    search_fields = [
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'cargo_funcao__nome',
        'descricao',
    ]
    readonly_fields = ['data_registro', 'data_atualizacao']
    date_hierarchy = 'data_inicio'
    autocomplete_fields = ['usuario', 'cargo_funcao']

    fieldsets = (
        ('Informações Gerais', {
            'fields': ('usuario', 'cargo_funcao', 'tipo_funcao', 'status', 'descricao')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Controle', {
            'fields': ('data_registro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

    def cargo_funcao_nome(self, obj):
        return obj.cargo_funcao.nome if obj.cargo_funcao else '-'
    cargo_funcao_nome.short_description = 'Cargo/Função'

    def esta_ativo(self, obj):
        return obj.status == 'ATIVO'
    esta_ativo.boolean = True
    esta_ativo.short_description = 'Ativo?'


@admin.register(CargoFuncao)
class CargoFuncaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'ativo', 'ordem', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem', 'nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    fieldsets = (
        ('Informações do Cargo/Função', {
            'fields': ('nome', 'descricao', 'ativo', 'ordem')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PermissaoFuncao)
class PermissaoFuncaoAdmin(admin.ModelAdmin):
    list_display = [
        'cargo_funcao',
        'modulo',
        'acesso',
        'ativo',
        'data_criacao',
    ]
    list_filter = [
        'cargo_funcao',
        'modulo',
        'acesso',
        'ativo',
        'data_criacao',
    ]
    search_fields = [
        'cargo_funcao__nome',
        'modulo',
        'acesso',
        'observacoes',
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['cargo_funcao__nome', 'modulo', 'acesso']
    
    fieldsets = (
        ('Informações da Permissão', {
            'fields': ('cargo_funcao', 'modulo', 'acesso', 'ativo')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'descricao',
        'ativo',
        'data_criacao',
        'total_permissoes',
    ]
    list_filter = [
        'ativo',
        'data_criacao',
    ]
    search_fields = [
        'nome',
        'descricao',
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    filter_horizontal = ['permissoes']
    
    fieldsets = (
        ('Informações do Perfil', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Permissões', {
            'fields': ('permissoes',),
            'description': 'Selecione as permissões que este perfil deve ter'
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def total_permissoes(self, obj):
        return obj.permissoes.count()
    total_permissoes.short_description = 'Total de Permissões'


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
        'almanaque', 'assinado_por', 'cargo_funcao', 'data_assinatura'
    ]
    list_filter = [
        'data_assinatura', 'almanaque__tipo'
    ]
    search_fields = [
        'assinado_por__username', 'assinado_por__first_name', 'assinado_por__last_name',
        'cargo_funcao', 'observacoes'
    ]
    readonly_fields = [
        'data_assinatura'
    ]
    date_hierarchy = 'data_assinatura'

    fieldsets = (
        ('Informações da Assinatura', {
            'fields': ('almanaque', 'assinado_por', 'cargo_funcao')
        }),
        ('Detalhes', {
            'fields': ('observacoes',)
        }),
        ('Controle', {
            'fields': ('data_assinatura',),
            'classes': ('collapse',)
        }),
    )



