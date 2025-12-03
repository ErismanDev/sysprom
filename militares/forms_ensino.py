# -*- coding: utf-8 -*-
"""
Forms para o Módulo de Ensino Militar
Organizado na sequência: Curso → Turmas → Disciplinas → Instrutores → Monitores → Alunos → Aulas → Frequências → Notas
"""

from django import forms
from django.db.models import Q
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import (
    PessoaExterna, CursoEnsino, DisciplinaCurso, DisciplinaEnsino, EdicaoCurso, TurmaEnsino, 
    AlunoEnsino, InstrutorEnsino, MonitorEnsino, AulaEnsino, FrequenciaAula, 
    AproveitamentoDisciplina, AvaliacaoEnsino, NotaAvaliacao, CertificadoEnsino, 
    DocumentoAluno, OcorrenciaDisciplinar, EscalaInstrucao, MaterialEscolar, 
    CautelaMaterialEscolar, Militar, QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal,
    # Novos modelos ITE 01/2024
    PlanoGeralEnsino, ItemPlanoGeralEnsino, ProjetoPedagogico, PlanoCursoEstagio,
    PlanoDisciplina, PlanoPalestra, AtividadeTreinamentoCampo, AtividadeComplementarEnsino,
    TesteConhecimentosProfissionais, PlanoEstagioNivelamentoProfissional,
    RelatorioAnualDEIP, ProcessoSelecaoAlunos, InscricaoProcessoSelecao,
    RecursoProcessoSelecao, TrabalhoConclusaoCurso, PlanoSeguranca, ClassificacaoFinalCurso,
    PedidoRevisaoProva
)


# ============================================================================
# 1. CURSOS (Nível Principal)
# ============================================================================

class CursoEnsinoForm(forms.ModelForm):
    """Form para Curso de Ensino - Completo"""
    
    # Choices para escolaridade requerida
    ESCOLARIDADE_CHOICES = [
        ('', 'Selecione...'),
        ('FUNDAMENTAL_INCOMPLETO', 'Ensino Fundamental Incompleto'),
        ('FUNDAMENTAL_COMPLETO', 'Ensino Fundamental Completo'),
        ('MEDIO_INCOMPLETO', 'Ensino Médio Incompleto'),
        ('MEDIO_COMPLETO', 'Ensino Médio Completo'),
        ('SUPERIOR_INCOMPLETO', 'Ensino Superior Incompleto'),
        ('SUPERIOR_COMPLETO', 'Ensino Superior Completo'),
        ('POS_GRADUACAO', 'Pós-Graduação (Especialização)'),
        ('MESTRADO', 'Mestrado'),
        ('DOUTORADO', 'Doutorado'),
        ('TECNICO', 'Técnico'),
        ('TECNOLOGO', 'Tecnólogo'),
    ]
    
    escolaridade_requerida = forms.ChoiceField(
        choices=ESCOLARIDADE_CHOICES,
        required=False,
        label="Escolaridade Requerida",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CursoEnsino
        fields = '__all__'
        exclude = ['escolaridade_requerida']  # Excluir o campo do modelo para usar o customizado
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair instance antes de chamar super para poder usar depois
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        # Tornar campos opcionais se existirem
        if 'coordenador_militar' in self.fields:
            self.fields['coordenador_militar'].required = False
        if 'coordenador_externo' in self.fields:
            self.fields['coordenador_externo'].required = False
        if 'instrutores_curso' in self.fields:
            self.fields['instrutores_curso'].required = False
        if 'monitores_curso' in self.fields:
            self.fields['monitores_curso'].required = False
        # Tornar disciplinas não obrigatório, pois usamos interface customizada
        if 'disciplinas' in self.fields:
            self.fields['disciplinas'].required = False
        
        # Tornar código opcional se não estiver preenchido (pode ser gerado automaticamente)
        if 'codigo' in self.fields:
            self.fields['codigo'].required = False
            # Permitir valores vazios mesmo sendo unique
            self.fields['codigo'].widget.attrs.setdefault('placeholder', 'Ex: CBM-OP-2025 (opcional)')
        
        # Tornar campos com default não obrigatórios (mesmo que tenham default, podem não estar no template)
        campos_com_default = [
            'regime_matricula', 'status', 'percentual_frequencia_minima',
            'unidade_responsavel', 'numero_minimo_alunos', 'numero_maximo_alunos',
            'calendario_inicio', 'calendario_termino', 'media_minima_aprovacao',
            'media_minima_recuperacao'
        ]
        for campo in campos_com_default:
            if campo in self.fields:
                self.fields[campo].required = False
        
        # Tornar TODOS os campos não obrigatórios por padrão (já que o modelo permite blank=True, null=True)
        # Isso evita problemas com campos que não estão no template
        for field_name, field in self.fields.items():
            # Manter required=True apenas para campos que realmente precisam ser obrigatórios
            # Por enquanto, vamos tornar todos opcionais exceto se explicitamente marcado como required
            if field_name not in ['nome', 'codigo', 'finalidade', 'publico_alvo', 'carga_horaria']:
                field.required = False

        if self.instance and self.instance.pk:
            try:
                self.instance.refresh_from_db()
            except Exception:
                pass
            valor_existente = getattr(self.instance, 'escolaridade_requerida', None)
            if valor_existente:
                valores_choices = [choice[0] for choice in self.ESCOLARIDADE_CHOICES]
                if valor_existente in valores_choices:
                    self.initial['escolaridade_requerida'] = valor_existente
                else:
                    self.fields['escolaridade_requerida'].choices = [
                        ('', 'Selecione...'),
                        (valor_existente, f'{valor_existente} (valor atual)'),
                    ] + [choice for choice in self.ESCOLARIDADE_CHOICES if choice[0] != '']
                    self.initial['escolaridade_requerida'] = valor_existente
            elif not valor_existente:
                self.initial['escolaridade_requerida'] = ''

        for field_name, field in self.fields.items():
            if field_name not in ['observacoes', 'escolaridade_requerida']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.setdefault('class', 'form-select')
                elif isinstance(field.widget, forms.NumberInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.DateInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.EmailInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.URLInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault('class', 'form-check-input')
                elif isinstance(field.widget, forms.FileInput):
                    field.widget.attrs.setdefault('class', 'form-control')
    
    def clean_codigo(self):
        """Validar código único, mas permitir vazio"""
        codigo = self.cleaned_data.get('codigo')
        if not codigo:
            return codigo
        qs = CursoEnsino.objects.filter(codigo=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um curso com este código.')
        return codigo
    
    def clean_escolaridade_requerida(self):
        """Garantir que o valor seja salvo corretamente"""
        escolaridade = self.cleaned_data.get('escolaridade_requerida')
        # Se for uma das choices, retornar o valor
        # Se for um valor customizado (do banco antigo), manter como está
        return escolaridade if escolaridade else ''

    def save(self, commit=True):
        """Salvar o curso e mapear o campo escolaridade_requerida customizado"""
        curso = super().save(commit=False)
        
        # Mapear o campo customizado escolaridade_requerida para o campo do modelo
        if 'escolaridade_requerida' in self.cleaned_data:
            valor_escolaridade = self.cleaned_data['escolaridade_requerida']
            # Se o valor for vazio, salvar como None ou string vazia
            curso.escolaridade_requerida = valor_escolaridade if valor_escolaridade else None
        
        if commit:
            curso.save()
            # Salvar relacionamentos many-to-many se houver
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        
        return curso

class PedidoRevisaoProvaForm(forms.ModelForm):
    aceite_termos = forms.BooleanField(
        label="Li e concordo com as regras da revisão",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    def __init__(self, *args, **kwargs):
        self.nota_avaliacao = kwargs.pop('nota_avaliacao', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
        self.fields['fundamentacao'].widget.attrs.setdefault('placeholder', 'Descreva objetivamente os motivos do pedido')
        if 'itens_solicitados' in self.fields:
            self.fields['itens_solicitados'].widget.attrs.setdefault('placeholder', 'Informe os itens/questões específicos a serem revisados')

    class Meta:
        model = PedidoRevisaoProva
        fields = ['fundamentacao', 'itens_solicitados']
        widgets = {
            'fundamentacao': CKEditor5Widget(config_name='default'),
            'itens_solicitados': CKEditor5Widget(config_name='default'),
        }

    def clean(self):
        cleaned = super().clean()
        nota = self.nota_avaliacao or getattr(self.instance, 'nota_avaliacao', None)
        itens = cleaned.get('itens_solicitados')
        if not itens:
            raise forms.ValidationError('Informe os itens/questões específicos a serem revisados.')
        aceite = cleaned.get('aceite_termos')
        if not aceite:
            raise forms.ValidationError('Você deve concordar com as regras da revisão para enviar.')
        return cleaned

class DespachoInstrutorForm(forms.Form):
    despacho = forms.CharField(
        label="Despacho ao Instrutor",
        widget=CKEditor5Widget(config_name='default'),
        required=True
    )

class InstrutorParecerForm(forms.ModelForm):
    confirmar_limite_itens = forms.BooleanField(
        label="Confirmo que a revisão se limita aos itens solicitados",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = PedidoRevisaoProva
        fields = ['parecer_instrutor', 'parecer_instrutor_texto', 'nova_nota_instrutor']
        widgets = {
            'parecer_instrutor_texto': CKEditor5Widget(config_name='default'),
            'nova_nota_instrutor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
        }

    def clean(self):
        cleaned = super().clean()
        decisao = cleaned.get('parecer_instrutor')
        nova = cleaned.get('nova_nota_instrutor')
        nota_orig = None
        try:
            nota_orig = self.instance.nota_avaliacao.nota
        except Exception:
            pass
        if decisao == 'FAVORAVEL':
            if nova is None:
                raise forms.ValidationError('Informe a nova nota proposta pelo instrutor (não menor que a atual).')
            if nota_orig is not None and nova < nota_orig:
                raise forms.ValidationError('A nova nota do instrutor não pode ser menor que a nota atual.')
        else:
            if nova is not None:
                raise forms.ValidationError('Nova nota só deve ser informada quando o parecer for favorável.')
        if not cleaned.get('confirmar_limite_itens'):
            raise forms.ValidationError('É necessário confirmar que a revisão se limita aos itens solicitados.')
        return cleaned

class ComissaoParecerForm(forms.ModelForm):
    class Meta:
        model = PedidoRevisaoProva
        fields = ['parecer_final_texto', 'nova_nota_final']
        widgets = {
            'parecer_final_texto': CKEditor5Widget(config_name='default'),
            'nova_nota_final': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
        }

    def clean(self):
        cleaned = super().clean()
        nova = cleaned.get('nova_nota_final')
        nota_base = None
        try:
            base = [self.instance.nota_avaliacao.nota]
            if self.instance.nova_nota_instrutor is not None:
                base.append(self.instance.nova_nota_instrutor)
            nota_base = max([n for n in base if n is not None])
        except Exception:
            pass
        if nova is not None and nota_base is not None and nova < nota_base:
            raise forms.ValidationError('A nova nota final não pode ser menor que a nota atual/proposta.')
        return cleaned


# ============================================================================
# 2. EDIÇÕES DE CURSO (Para cursos permanentes)
# ============================================================================

class EdicaoCursoForm(forms.ModelForm):
    """Form para Edição de Curso"""
    
    class Meta:
        model = EdicaoCurso
        fields = [
            'curso', 'numero_edicao', 'nome', 'ano', 
            'data_inicio', 'data_fim', 'ativa', 'observacoes'
        ]
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'numero_edicao': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Listar TODOS os cursos cadastrados, ordenados por nome
        self.fields['curso'].queryset = CursoEnsino.objects.all().order_by('nome', 'codigo')
        if 'data_inicio' in self.fields:
            self.fields['data_inicio'].widget.format = '%Y-%m-%d'
        if 'data_fim' in self.fields:
            self.fields['data_fim'].widget.format = '%Y-%m-%d'


# ============================================================================
# 3. TURMAS (Dependem de Curso e podem ter Edição)
# ============================================================================

class TurmaEnsinoForm(forms.ModelForm):
    """Form para Turma de Ensino"""
    
    class Meta:
        model = TurmaEnsino
        fields = [
            'curso', 'edicao', 'identificacao', 'data_inicio', 'data_fim',
            'supervisor_curso', 'coordenador_curso',
            'instrutor_chefe_militar', 'instrutor_chefe_externo',
            'supervisor_turma', 'coordenador_turma',
            'monitores_militares', 'monitores_externos', 'disciplinas',
            'ativa', 'observacoes'
        ]
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'edicao': forms.Select(attrs={'class': 'form-select'}),
            'identificacao': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'supervisor_curso': forms.Select(attrs={'class': 'form-control militar-select2'}),
            'coordenador_curso': forms.Select(attrs={'class': 'form-control militar-select2'}),
            'instrutor_chefe_militar': forms.Select(attrs={'class': 'form-control militar-select2'}),
            'instrutor_chefe_externo': forms.Select(attrs={'class': 'form-select'}),
            'supervisor_turma': forms.Select(attrs={'class': 'form-control militar-select2'}),
            'coordenador_turma': forms.Select(attrs={'class': 'form-control militar-select2'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'monitores_militares': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'monitores_externos': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'disciplinas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar formato de data para input type="date" (YYYY-MM-DD)
        self.fields['data_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['data_fim'].input_formats = ['%Y-%m-%d']
        
        # Filtrar edições baseado no curso selecionado (se houver)
        # OBRIGATÓRIO: Todas as turmas devem estar dentro de uma edição
        if 'edicao' in self.fields:
            self.fields['edicao'].required = True  # TORNAR OBRIGATÓRIO
            
            # Se for edição de turma existente, carregar edições do curso da turma
            if self.instance and self.instance.pk and self.instance.curso:
                self.fields['edicao'].queryset = EdicaoCurso.objects.filter(
                    curso=self.instance.curso
                ).order_by('-ano', '-numero_edicao')
            # Se houver curso enviado via POST (self.data), carregar edições desse curso
            elif hasattr(self, 'data') and self.data.get('curso'):
                try:
                    curso_id = int(self.data.get('curso'))
                    self.fields['edicao'].queryset = EdicaoCurso.objects.filter(
                        curso_id=curso_id
                    ).order_by('-ano', '-numero_edicao')
                except (ValueError, TypeError):
                    self.fields['edicao'].queryset = EdicaoCurso.objects.none()
            # Se houver curso inicial no formulário, carregar edições desse curso
            elif 'curso' in self.initial and self.initial['curso']:
                try:
                    curso = CursoEnsino.objects.get(pk=self.initial['curso'])
                    self.fields['edicao'].queryset = EdicaoCurso.objects.filter(
                        curso=curso
                    ).order_by('-ano', '-numero_edicao')
                except CursoEnsino.DoesNotExist:
                    self.fields['edicao'].queryset = EdicaoCurso.objects.none()
            # Caso contrário, inicialmente vazio (será preenchido via JavaScript)
            else:
                self.fields['edicao'].queryset = EdicaoCurso.objects.none()
            
            self.fields['edicao'].widget.attrs.update({
                'data-url': '/militares/ensino/edicoes/por-curso/',  # URL será criada
                'required': 'required',  # Adicionar atributo HTML required
            })
        
        # Filtrar apenas militares ativos para todos os campos de militar
        from militares.models import Militar
        campos_militar = [
            'supervisor_curso', 'coordenador_curso',
            'instrutor_chefe_militar', 'supervisor_turma',
            'coordenador_turma'
        ]
        for campo in campos_militar:
            if campo in self.fields:
                self.fields[campo].queryset = Militar.objects.filter(
                    classificacao='ATIVO'
                ).order_by('posto_graduacao', 'nome_completo')
                self.fields[campo].required = False
        
        if 'monitores_militares' in self.fields:
            from militares.models import Militar
            self.fields['monitores_militares'].queryset = Militar.objects.filter(
                classificacao='ATIVO'
            ).order_by('posto_graduacao', 'nome_completo')
        
        # Garantir que as datas sejam formatadas corretamente para o input type="date"
        if self.instance and self.instance.pk:
            if self.instance.data_inicio:
                self.initial['data_inicio'] = self.instance.data_inicio.strftime('%Y-%m-%d')
            if self.instance.data_fim:
                self.initial['data_fim'] = self.instance.data_fim.strftime('%Y-%m-%d')


# ============================================================================
# 3. DISCIPLINAS (Relacionadas a Curso e Turma)
# ============================================================================

class DisciplinaEnsinoForm(forms.ModelForm):
    """Form para Disciplina de Ensino"""
    
    class Meta:
        model = DisciplinaEnsino
        exclude = ['arquivos_complementares', 'links_uteis']  # Excluir campos antigos, agora usamos modelos separados
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'carga_horaria': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequencia_minima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'media_minima_aprovacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'media_minima_recuperacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'conteudo_programatico': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar o campo código readonly e não obrigatório (será gerado automaticamente)
        if 'codigo' in self.fields:
            self.fields['codigo'].required = False
            self.fields['codigo'].widget.attrs['readonly'] = True
            self.fields['codigo'].widget.attrs['class'] = 'form-control bg-light'
            self.fields['codigo'].help_text = 'Código gerado automaticamente'
        
        # Adicionar classes Bootstrap aos campos que não têm widgets definidos
        for field_name, field in self.fields.items():
            if field_name not in ['observacoes', 'nome', 'codigo', 'carga_horaria', 'frequencia_minima', 'media_minima_aprovacao', 'conteudo_programatico']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.setdefault('class', 'form-select')
                elif isinstance(field.widget, forms.NumberInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault('class', 'form-check-input')
    
    def clean_codigo(self):
        """Permitir código vazio - será gerado automaticamente no save() do modelo"""
        codigo = self.cleaned_data.get('codigo')
        # Se o código estiver vazio ou None, permitir (será gerado no save)
        if not codigo or codigo.strip() == '':
            return None
        return codigo
    
    def clean(self):
        cleaned_data = super().clean()
        frequencia_minima = cleaned_data.get('frequencia_minima')
        media_minima_aprovacao = cleaned_data.get('media_minima_aprovacao')
        
        if frequencia_minima is None:
            cleaned_data['frequencia_minima'] = 75.0
        
        return cleaned_data


# ============================================================================
# 4. INSTRUTORES (Relacionados a Turma e Disciplina)
# ============================================================================

class InstrutorEnsinoForm(forms.ModelForm):
    """Form para Instrutor de Ensino - pode ser bombeiro, militar outra força ou civil"""
    
    class Meta:
        model = InstrutorEnsino
        fields = [
            # Tipo e identificação básica
            'tipo_instrutor', 'militar', 'foto', 'ativo',
            # Bombeiro - contatos e endereço específicos
            'email_bombeiro', 'telefone_bombeiro', 'endereco_bombeiro', 
            'cidade_bombeiro', 'uf_bombeiro', 'cep_bombeiro',
            # Militar de outra força
            'nome_outra_forca', 'posto_outra_forca', 'forca_armada', 'matricula_outra_forca',
            'cpf_outra_forca', 'email_outra_forca', 'telefone_outra_forca', 'instituicao_outra_forca',
            'endereco_outra_forca', 'cidade_outra_forca', 'uf_outra_forca', 'cep_outra_forca', 'foto_outra_forca',
            # Civil
            'nome_civil', 'cpf_civil', 'rg_civil', 'data_nascimento_civil', 'email_civil',
            'telefone_civil', 'endereco_civil', 'cidade_civil', 'uf_civil', 'cep_civil',
            'formacao_civil', 'instituicao_civil',
            # Campos comuns
            'habilitacoes', 'especialidades', 'experiencia_profissional', 'cursos_complementares', 'link_lattes', 'observacoes',
        ]
        widgets = {
            'tipo_instrutor': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'militar': forms.Select(attrs={'class': 'form-control select2-militar'}),
            'email_bombeiro': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_bombeiro': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_bombeiro': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_bombeiro': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_bombeiro': forms.Select(attrs={'class': 'form-control'}),
            'cep_bombeiro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'nome_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'posto_outra_forca': forms.Select(attrs={'class': 'form-control'}),
            'forca_armada': forms.Select(attrs={'class': 'form-control'}),
            'matricula_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_outra_forca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'email_outra_forca': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'instituicao_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_outra_forca': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_outra_forca': forms.Select(attrs={'class': 'form-control'}),
            'cep_outra_forca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'foto_outra_forca': forms.FileInput(attrs={'class': 'form-control'}),
            'nome_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_civil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'rg_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento_civil': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email_civil': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_civil': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_civil': forms.Select(attrs={'class': 'form-control'}),
            'cep_civil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'formacao_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'instituicao_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'habilitacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'especialidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experiencia_profissional': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cursos_complementares': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'link_lattes': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://lattes.cnpq.br/...'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas militares ativos para o campo militar
        if 'militar' in self.fields:
            from militares.models import Militar
            self.fields['militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
        
        # Tornar todos os campos opcionais
        for field_name, field in self.fields.items():
            field.required = False
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_instrutor = cleaned_data.get('tipo_instrutor')
        
        # Validação baseada no tipo
        if tipo_instrutor == 'BOMBEIRO':
            if not cleaned_data.get('militar'):
                raise forms.ValidationError({'militar': 'Selecione um militar bombeiro.'})
        elif tipo_instrutor == 'OUTRA_FORCA':
            if not cleaned_data.get('nome_outra_forca'):
                raise forms.ValidationError({'nome_outra_forca': 'Nome completo é obrigatório para militar de outra força.'})
        elif tipo_instrutor == 'CIVIL':
            if not cleaned_data.get('nome_civil'):
                raise forms.ValidationError({'nome_civil': 'Nome completo é obrigatório para instrutor civil.'})
        
        return cleaned_data


# ============================================================================
# 5. MONITORES (Relacionados a Turma)
# ============================================================================

class MonitorEnsinoForm(forms.ModelForm):
    """Form para Monitor de Ensino - pode ser bombeiro, militar outra força ou civil"""
    
    class Meta:
        model = MonitorEnsino
        fields = [
            # Tipo e identificação básica
            'tipo_monitor', 'militar', 'foto', 'ativo',
            # Bombeiro - contatos e endereço específicos
            'email_bombeiro', 'telefone_bombeiro', 'endereco_bombeiro', 
            'cidade_bombeiro', 'uf_bombeiro', 'cep_bombeiro',
            # Militar de outra força
            'nome_outra_forca', 'posto_outra_forca', 'forca_armada', 'matricula_outra_forca',
            'cpf_outra_forca', 'email_outra_forca', 'telefone_outra_forca', 'instituicao_outra_forca',
            'endereco_outra_forca', 'cidade_outra_forca', 'uf_outra_forca', 'cep_outra_forca', 'foto_outra_forca',
            # Civil
            'nome_civil', 'cpf_civil', 'rg_civil', 'data_nascimento_civil', 'email_civil',
            'telefone_civil', 'endereco_civil', 'cidade_civil', 'uf_civil', 'cep_civil',
            'formacao_civil', 'instituicao_civil',
            # Campos comuns
            'habilitacoes', 'especialidades', 'experiencia_profissional', 'cursos_complementares', 'observacoes',
        ]
        widgets = {
            'tipo_monitor': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'militar': forms.Select(attrs={'class': 'form-control select2-militar'}),
            'email_bombeiro': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_bombeiro': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_bombeiro': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_bombeiro': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_bombeiro': forms.Select(attrs={'class': 'form-control'}),
            'cep_bombeiro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'nome_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'posto_outra_forca': forms.Select(attrs={'class': 'form-control'}),
            'forca_armada': forms.Select(attrs={'class': 'form-control'}),
            'matricula_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_outra_forca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'email_outra_forca': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'instituicao_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_outra_forca': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_outra_forca': forms.Select(attrs={'class': 'form-control'}),
            'cep_outra_forca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'foto_outra_forca': forms.FileInput(attrs={'class': 'form-control'}),
            'nome_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_civil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'rg_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento_civil': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email_civil': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_civil': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_civil': forms.Select(attrs={'class': 'form-control'}),
            'cep_civil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'formacao_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'instituicao_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'habilitacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'especialidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experiencia_profissional': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cursos_complementares': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'link_lattes': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://lattes.cnpq.br/...'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas militares ativos para o campo militar
        if 'militar' in self.fields:
            from militares.models import Militar
            self.fields['militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
        
        # Tornar todos os campos opcionais
        for field_name, field in self.fields.items():
            field.required = False
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_monitor = cleaned_data.get('tipo_monitor')
        
        # Validação baseada no tipo
        if tipo_monitor == 'BOMBEIRO':
            if not cleaned_data.get('militar'):
                raise forms.ValidationError({'militar': 'Selecione um militar bombeiro.'})
        elif tipo_monitor == 'OUTRA_FORCA':
            if not cleaned_data.get('nome_outra_forca'):
                raise forms.ValidationError({'nome_outra_forca': 'Nome completo é obrigatório para militar de outra força.'})
        elif tipo_monitor == 'CIVIL':
            if not cleaned_data.get('nome_civil'):
                raise forms.ValidationError({'nome_civil': 'Nome completo é obrigatório para monitor civil.'})
        
        return cleaned_data


# ============================================================================
# 6. ALUNOS (Relacionados a Turma)
# ============================================================================

class AlunoEnsinoForm(forms.ModelForm):
    """Form para Aluno de Ensino - pode ser bombeiro, militar outra força ou civil"""
    
    class Meta:
        model = AlunoEnsino
        # Apenas os campos listados aparecerão no formulário
        # matricula e turma NÃO estão na lista, então não aparecerão
        fields = [
            # Tipo e identificação básica
            'tipo_aluno', 'militar', 'foto', 'situacao',
            # Militar de outra força
            'nome_outra_forca', 'posto_outra_forca', 'forca_armada', 'matricula_outra_forca',
            'cpf_outra_forca', 'rg_outra_forca', 'data_nascimento_outra_forca', 'email_outra_forca',
            'telefone_outra_forca', 'instituicao_outra_forca', 'endereco_outra_forca',
            'cidade_outra_forca', 'uf_outra_forca', 'cep_outra_forca',
            # Civil
            'nome_civil', 'cpf_civil', 'rg_civil', 'data_nascimento_civil', 'email_civil',
            'telefone_civil', 'endereco_civil', 'cidade_civil', 'uf_civil', 'cep_civil',
            'formacao_civil', 'instituicao_civil',
            # Campos comuns
            'observacoes'
        ]
        widgets = {
            'tipo_aluno': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'militar': forms.Select(attrs={'class': 'form-control select2-militar'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            # Militar de outra força
            'nome_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'posto_outra_forca': forms.Select(attrs={'class': 'form-control'}),
            'forca_armada': forms.Select(attrs={'class': 'form-control'}),
            'matricula_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_outra_forca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'rg_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento_outra_forca': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email_outra_forca': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'instituicao_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_outra_forca': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_outra_forca': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_outra_forca': forms.Select(attrs={'class': 'form-control'}),
            'cep_outra_forca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            # Civil
            'nome_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_civil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'rg_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento_civil': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email_civil': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco_civil': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cidade_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_civil': forms.Select(attrs={'class': 'form-control'}),
            'cep_civil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'formacao_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'instituicao_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'situacao': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas militares ativos para o campo militar
        if 'militar' in self.fields:
            from militares.models import Militar
            self.fields['militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
        
        # Tornar todos os campos opcionais inicialmente
        for field_name, field in self.fields.items():
            if field_name not in ['tipo_aluno', 'situacao']:
                field.required = False
        
        # Se já existe uma instância, definir o tipo baseado nos campos preenchidos
        if self.instance and self.instance.pk:
            if self.instance.tipo_aluno:
                self.fields['tipo_aluno'].initial = self.instance.tipo_aluno
            elif self.instance.militar:
                self.fields['tipo_aluno'].initial = 'BOMBEIRO'
            elif self.instance.pessoa_externa:
                self.fields['tipo_aluno'].initial = 'CIVIL'
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_aluno = cleaned_data.get('tipo_aluno')
        
        # Validação baseada no tipo
        if tipo_aluno == 'BOMBEIRO':
            if not cleaned_data.get('militar'):
                raise forms.ValidationError({'militar': 'Selecione um militar bombeiro.'})
            # Limpar campos de outras forças e civil
            cleaned_data['nome_outra_forca'] = None
            cleaned_data['nome_civil'] = None
            
            # Verificar se já existe aluno com este militar
            militar = cleaned_data.get('militar')
            if militar:
                alunos_existentes = AlunoEnsino.objects.filter(
                    tipo_aluno='BOMBEIRO',
                    militar=militar
                )
                # Se estiver editando, excluir o próprio registro
                if self.instance and self.instance.pk:
                    alunos_existentes = alunos_existentes.exclude(pk=self.instance.pk)
                
                if alunos_existentes.exists():
                    aluno_existente = alunos_existentes.first()
                    raise forms.ValidationError(
                        f'Já existe um cadastro para este militar: {aluno_existente.get_pessoa_nome()} '
                        f'(Matrícula: {aluno_existente.matricula or "N/A"}). '
                        f'Um aluno pode ter apenas um cadastro, mas pode estar matriculado em múltiplas turmas.'
                    )
                    
        elif tipo_aluno == 'OUTRA_FORCA':
            if not cleaned_data.get('nome_outra_forca'):
                raise forms.ValidationError({'nome_outra_forca': 'Nome completo é obrigatório para militar de outra força.'})
            if not cleaned_data.get('cpf_outra_forca'):
                raise forms.ValidationError({'cpf_outra_forca': 'CPF é obrigatório para militar de outra força.'})
            # Limpar campos de bombeiro e civil
            cleaned_data['militar'] = None
            cleaned_data['nome_civil'] = None
            
            # Verificar se já existe aluno com este CPF
            cpf_outra_forca = cleaned_data.get('cpf_outra_forca')
            if cpf_outra_forca:
                import re
                cpf_normalizado = re.sub(r'[^0-9]', '', str(cpf_outra_forca))
                alunos_existentes = AlunoEnsino.objects.filter(tipo_aluno='OUTRA_FORCA')
                # Se estiver editando, excluir o próprio registro
                if self.instance and self.instance.pk:
                    alunos_existentes = alunos_existentes.exclude(pk=self.instance.pk)
                
                for aluno in alunos_existentes:
                    if aluno.cpf_outra_forca:
                        cpf_existente = re.sub(r'[^0-9]', '', str(aluno.cpf_outra_forca))
                        if cpf_normalizado == cpf_existente:
                            raise forms.ValidationError(
                                f'Já existe um cadastro para este CPF: {aluno.get_pessoa_nome()} '
                                f'(Matrícula: {aluno.matricula or "N/A"}). '
                                f'Um aluno pode ter apenas um cadastro, mas pode estar matriculado em múltiplas turmas.'
                            )
                            
        elif tipo_aluno == 'CIVIL':
            if not cleaned_data.get('nome_civil'):
                raise forms.ValidationError({'nome_civil': 'Nome completo é obrigatório para aluno civil.'})
            if not cleaned_data.get('cpf_civil'):
                raise forms.ValidationError({'cpf_civil': 'CPF é obrigatório para aluno civil.'})
            # Limpar campos de bombeiro e outra força
            cleaned_data['militar'] = None
            cleaned_data['nome_outra_forca'] = None
            
            # Verificar se já existe aluno com este CPF
            cpf_civil = cleaned_data.get('cpf_civil')
            if cpf_civil:
                import re
                cpf_normalizado = re.sub(r'[^0-9]', '', str(cpf_civil))
                alunos_existentes = AlunoEnsino.objects.filter(tipo_aluno='CIVIL')
                # Se estiver editando, excluir o próprio registro
                if self.instance and self.instance.pk:
                    alunos_existentes = alunos_existentes.exclude(pk=self.instance.pk)
                
                for aluno in alunos_existentes:
                    if aluno.cpf_civil:
                        cpf_existente = re.sub(r'[^0-9]', '', str(aluno.cpf_civil))
                        if cpf_normalizado == cpf_existente:
                            raise forms.ValidationError(
                                f'Já existe um cadastro para este CPF: {aluno.get_pessoa_nome()} '
                                f'(Matrícula: {aluno.matricula or "N/A"}). '
                                f'Um aluno pode ter apenas um cadastro, mas pode estar matriculado em múltiplas turmas.'
                            )
        
        # Matrícula e turma são gerenciadas apenas quando o aluno é inserido em uma turma
        # Não devem ser editadas diretamente no formulário de aluno
        return cleaned_data


# ============================================================================
# 7. AULAS (Relacionadas a Turma e Disciplina)
# ============================================================================

class AulaEnsinoForm(forms.ModelForm):
    """Form para Aula de Ensino"""
    
    class Meta:
        model = AulaEnsino
        fields = '__all__'
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'disciplina': forms.Select(attrs={'class': 'form-select'}),
            'instrutor': forms.Select(attrs={'class': 'form-select'}),
            'data_aula': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'conteudo_ministrado': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar formato de data para input type="date"
        if 'data_aula' in self.fields:
            self.fields['data_aula'].widget.format = '%Y-%m-%d'
            # Se estiver editando e houver data, formatar corretamente
            if self.instance and self.instance.pk and self.instance.data_aula:
                try:
                    self.initial['data_aula'] = self.instance.data_aula.strftime('%Y-%m-%d')
                except:
                    pass
        
        # Configurar formato de hora para input type="time"
        if 'hora_inicio' in self.fields:
            self.fields['hora_inicio'].widget.format = '%H:%M'
            # Se estiver editando e houver hora, formatar corretamente
            if self.instance and self.instance.pk and self.instance.hora_inicio:
                try:
                    if hasattr(self.instance.hora_inicio, 'strftime'):
                        self.initial['hora_inicio'] = self.instance.hora_inicio.strftime('%H:%M')
                    else:
                        self.initial['hora_inicio'] = str(self.instance.hora_inicio)
                except:
                    pass
        
        if 'hora_fim' in self.fields:
            self.fields['hora_fim'].widget.format = '%H:%M'
            # Se estiver editando e houver hora, formatar corretamente
            if self.instance and self.instance.pk and self.instance.hora_fim:
                try:
                    if hasattr(self.instance.hora_fim, 'strftime'):
                        self.initial['hora_fim'] = self.instance.hora_fim.strftime('%H:%M')
                    else:
                        self.initial['hora_fim'] = str(self.instance.hora_fim)
                except:
                    pass
        
        # Filtrar turmas conforme vínculo do usuário
        try:
            if 'turma' in self.fields:
                from militares.models import TurmaEnsino, UsuarioMaster
                qs_turmas = TurmaEnsino.objects.filter(ativa=True).order_by('identificacao')
                if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                    master = False
                    try:
                        master = UsuarioMaster.objects.filter(username=user.username, ativo=True).exists()
                    except Exception:
                        master = False
                    if not (user.is_superuser or master):
                        militar = getattr(user, 'militar', None)
                        if militar:
                            from django.db.models import Q
                            qs_turmas = qs_turmas.filter(
                                Q(supervisor_curso_id=militar.id) |
                                Q(coordenador_curso_id=militar.id) |
                                Q(supervisor_turma_id=militar.id) |
                                Q(coordenador_turma_id=militar.id)
                            ).distinct()
                self.fields['turma'].queryset = qs_turmas
        except Exception:
            pass

        # Filtrar disciplinas conforme turma e vínculo do usuário
        try:
            turma_id = None
            if 'turma' in self.data and self.data.get('turma'):
                turma_id = self.data.get('turma')
            elif self.initial.get('turma'):
                turma_id = self.initial.get('turma')
            elif self.instance and getattr(self.instance, 'turma_id', None):
                turma_id = self.instance.turma_id
            if turma_id:
                from militares.models import TurmaEnsino, DisciplinaEnsino
                turma_ref = TurmaEnsino.objects.filter(pk=turma_id).first()
                qs = DisciplinaEnsino.objects.none()
                if turma_ref:
                    qs = turma_ref.disciplinas.all()
                    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                        militar = getattr(user, 'militar', None)
                        eh_coord_sup = False
                        if militar:
                            eh_coord_sup = (
                                getattr(turma_ref, 'supervisor_curso_id', None) == militar.id or
                                getattr(turma_ref, 'coordenador_curso_id', None) == militar.id or
                                getattr(turma_ref, 'supervisor_turma_id', None) == militar.id or
                                getattr(turma_ref, 'coordenador_turma_id', None) == militar.id
                            )
                        if not (user.is_superuser or eh_coord_sup):
                            from django.db.models import Q
                            instrutor_ext = None
                            try:
                                instrutor_ext = getattr(militar, 'instrutor_ensino', None)
                            except Exception:
                                instrutor_ext = None
                            qs = qs.filter(
                                Q(instrutor_responsavel_militar=militar) |
                                Q(monitores_militares=militar) |
                                Q(instrutor_responsavel_externo=instrutor_ext)
                            ).distinct()
                self.fields['disciplina'].queryset = qs
        except Exception:
            pass

        # Adicionar classes Bootstrap aos campos que não têm widgets definidos
        for field_name, field in self.fields.items():
            if field_name not in ['turma', 'disciplina', 'instrutor', 'data_aula', 'hora_inicio', 'hora_fim', 'conteudo_ministrado', 'observacoes']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.setdefault('class', 'form-select')
                elif isinstance(field.widget, forms.NumberInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault('class', 'form-check-input')
    
    def clean(self):
        cleaned_data = super().clean()
        turma = cleaned_data.get('turma')
        data_aula = cleaned_data.get('data_aula')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fim = cleaned_data.get('hora_fim')
        
        # Se todos os campos necessários estiverem presentes
        if turma and data_aula and hora_inicio and hora_fim:
            # Buscar todas as aulas da mesma turma na mesma data, ordenadas por horário de início
            aulas_existentes = AulaEnsino.objects.filter(
                turma=turma,
                data_aula=data_aula
            ).order_by('hora_inicio')
            
            # Se estiver editando, excluir a própria aula da verificação
            # IMPORTANTE: Sempre excluir a própria instância quando estiver editando
            aula_id_para_excluir = None
            if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
                aula_id_para_excluir = self.instance.pk
                aulas_existentes = aulas_existentes.exclude(pk=aula_id_para_excluir)
                # Debug: verificar se a exclusão funcionou
                print(f"Editando aula {aula_id_para_excluir}. Aulas restantes para validação: {aulas_existentes.count()}")
            
            # Verificar se há aulas existentes (excluindo a própria se estiver editando)
            if aulas_existentes.exists():
                # Verificar sobreposição de horários
                for aula_existente in aulas_existentes:
                    # Verificar se o horário de início da nova aula está dentro do horário de uma aula existente
                    if (hora_inicio >= aula_existente.hora_inicio and hora_inicio < aula_existente.hora_fim):
                        raise forms.ValidationError(
                            f'O horário de início ({hora_inicio.strftime("%H:%M")}) está sobreposto com uma aula existente '
                            f'({aula_existente.hora_inicio.strftime("%H:%M")} - {aula_existente.hora_fim.strftime("%H:%M")}). '
                            f'Disciplina: {aula_existente.disciplina.nome}. '
                            f'Por favor, escolha outro horário.'
                        )
                    
                    # Verificar se o horário de término da nova aula está dentro do horário de uma aula existente
                    if (hora_fim > aula_existente.hora_inicio and hora_fim <= aula_existente.hora_fim):
                        raise forms.ValidationError(
                            f'O horário de término ({hora_fim.strftime("%H:%M")}) está sobreposto com uma aula existente '
                            f'({aula_existente.hora_inicio.strftime("%H:%M")} - {aula_existente.hora_fim.strftime("%H:%M")}). '
                            f'Disciplina: {aula_existente.disciplina.nome}. '
                            f'Por favor, escolha outro horário.'
                        )
                    
                    # Verificar se a nova aula engloba completamente uma aula existente
                    if (hora_inicio <= aula_existente.hora_inicio and hora_fim >= aula_existente.hora_fim):
                        raise forms.ValidationError(
                            f'O horário da nova aula ({hora_inicio.strftime("%H:%M")} - {hora_fim.strftime("%H:%M")}) '
                            f'engloba completamente uma aula existente '
                            f'({aula_existente.hora_inicio.strftime("%H:%M")} - {aula_existente.hora_fim.strftime("%H:%M")}). '
                            f'Disciplina: {aula_existente.disciplina.nome}. '
                            f'Por favor, escolha outro horário.'
                        )
                
                # Validação de sequência: nova aula deve começar após o término da última aula do dia
                # IMPORTANTE: Esta validação só se aplica para NOVAS aulas, não para edições
                # Quando estamos editando, a própria aula já foi excluída de aulas_existentes
                # Então só aplicamos esta validação se NÃO estivermos editando
                if not (self.instance and self.instance.pk):
                    # Apenas para novas aulas: verificar sequência
                    ultima_aula = aulas_existentes.order_by('-hora_fim').first()
                    
                    # Verificar se o horário de início é antes do término da última aula
                    if ultima_aula and hora_inicio < ultima_aula.hora_fim:
                        raise forms.ValidationError(
                            f'O horário de início ({hora_inicio.strftime("%H:%M")}) deve ser após o término da última aula do dia '
                            f'({ultima_aula.hora_fim.strftime("%H:%M")}). '
                            f'Disciplina da última aula: {ultima_aula.disciplina.nome}. '
                            f'Por favor, escolha um horário após {ultima_aula.hora_fim.strftime("%H:%M")}.'
                        )
        
        return cleaned_data


# ============================================================================
# 8. FREQUÊNCIAS (Relacionadas a Aula e Aluno)
# ============================================================================

class FrequenciaAulaForm(forms.ModelForm):
    """Form para Frequência de Aula"""
    
    class Meta:
        model = FrequenciaAula
        fields = '__all__'
        widgets = {
            'aula': forms.Select(attrs={'class': 'form-select'}),
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justificativa': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Bootstrap aos campos que não têm widgets definidos
        for field_name, field in self.fields.items():
            if field_name not in ['aula', 'aluno', 'presente', 'justificativa', 'observacoes']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.setdefault('class', 'form-select')
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault('class', 'form-check-input')


# ============================================================================
# 9. AVALIAÇÕES (Relacionadas a Turma e Disciplina)
# ============================================================================

class AvaliacaoEnsinoForm(forms.ModelForm):
    """Form para Avaliação de Ensino"""
    
    POSICAO_AVALIACAO_CHOICES = [
        ('1', '1ª Avaliação'),
        ('2', '2ª Avaliação'),
        ('3', '3ª Avaliação'),
        ('4', '4ª Avaliação'),
        ('RECUPERACAO', 'Recuperação'),
    ]
    
    posicao_avaliacao = forms.ChoiceField(
        choices=POSICAO_AVALIACAO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Posição da Avaliação',
        help_text='Selecione a posição desta avaliação'
    )
    
    class Meta:
        model = AvaliacaoEnsino
        fields = '__all__'
        exclude = []  # Não excluir nada do modelo
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'disciplina': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_verificacao': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_avaliacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'nota_maxima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'criterios_aprovacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar posição da avaliação para edição
        if self.instance and self.instance.pk:
            # Se for recuperação, definir posição como RECUPERACAO
            if self.instance.tipo == 'RECUPERACAO':
                self.initial['posicao_avaliacao'] = 'RECUPERACAO'
            else:
                # Tentar determinar a posição baseado nas avaliações existentes
                if self.instance.turma and self.instance.disciplina:
                    from militares.models import AvaliacaoEnsino
                    avaliacoes_existentes = AvaliacaoEnsino.objects.filter(
                        turma=self.instance.turma,
                        disciplina=self.instance.disciplina
                    ).exclude(
                        tipo='RECUPERACAO'
                    ).exclude(
                        pk=self.instance.pk
                    ).order_by('data_avaliacao', 'id')
                    
                    posicao = avaliacoes_existentes.count() + 1
                    if posicao <= 4:
                        self.initial['posicao_avaliacao'] = str(posicao)
                    else:
                        self.initial['posicao_avaliacao'] = '1'  # Default
        
        # Configurar formato de data
        if 'data_avaliacao' in self.fields:
            self.fields['data_avaliacao'].widget.format = '%Y-%m-%d'
            if self.instance and self.instance.pk and self.instance.data_avaliacao:
                try:
                    self.initial['data_avaliacao'] = self.instance.data_avaliacao.strftime('%Y-%m-%d')
                except:
                    pass
        
        # Tornar campos de percentual opcionais (não são necessários para criar/editar avaliação)
        if 'percentual_questoes_faceis' in self.fields:
            self.fields['percentual_questoes_faceis'].required = False
        if 'percentual_questoes_medias' in self.fields:
            self.fields['percentual_questoes_medias'].required = False
        if 'percentual_questoes_dificeis' in self.fields:
            self.fields['percentual_questoes_dificeis'].required = False
        
        # Tornar campo nome opcional (será gerado automaticamente se não fornecido)
        if 'nome' in self.fields:
            self.fields['nome'].required = False
        
        # Filtrar disciplinas baseado na turma selecionada
        if 'turma' in self.fields and 'disciplina' in self.fields:
            # Verificar se há turma inicial (pode vir de initial ou instance)
            turma_initial = None
            if self.initial.get('turma'):
                try:
                    from militares.models import TurmaEnsino
                    turma_initial = TurmaEnsino.objects.get(pk=self.initial['turma'])
                except:
                    pass
            
            if self.instance and self.instance.pk and self.instance.turma:
                # Se estiver editando, filtrar disciplinas da turma
                turma = self.instance.turma
                # Buscar disciplinas diretamente relacionadas à turma
                disciplinas_turma = turma.disciplinas.all()
                # Também buscar disciplinas do curso da turma
                if turma.curso:
                    from militares.models import DisciplinaCurso
                    disciplinas_curso = DisciplinaCurso.objects.filter(
                        curso=turma.curso
                    ).select_related('disciplina')
                    disciplinas_ids = list(disciplinas_turma.values_list('pk', flat=True))
                    disciplinas_ids.extend([dc.disciplina.pk for dc in disciplinas_curso])
                    # Garantir que a disciplina atual esteja incluída
                    if self.instance.disciplina and self.instance.disciplina.pk not in disciplinas_ids:
                        disciplinas_ids.append(self.instance.disciplina.pk)
                    qs = DisciplinaEnsino.objects.filter(pk__in=disciplinas_ids).distinct()
                    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                        militar = getattr(user, 'militar', None)
                        eh_coord_sup = False
                        master = False
                        try:
                            from militares.models import UsuarioMaster
                            master = UsuarioMaster.objects.filter(username=user.username, ativo=True).exists()
                        except Exception:
                            master = False
                        if militar:
                            eh_coord_sup = (
                                getattr(turma, 'supervisor_curso_id', None) == militar.id or
                                getattr(turma, 'coordenador_curso_id', None) == militar.id or
                                getattr(turma, 'supervisor_turma_id', None) == militar.id or
                                getattr(turma, 'coordenador_turma_id', None) == militar.id
                            )
                        if not (user.is_superuser or master or eh_coord_sup):
                            from django.db.models import Q
                            instrutor_ext = None
                            try:
                                instrutor_ext = getattr(militar, 'instrutor_ensino', None)
                            except Exception:
                                instrutor_ext = None
                            qs = qs.filter(
                                Q(instrutor_responsavel_militar=militar) |
                                Q(monitores_militares=militar) |
                                Q(instrutor_responsavel_externo=instrutor_ext)
                            ).distinct()
                    self.fields['disciplina'].queryset = qs
                else:
                    # Garantir que a disciplina atual esteja incluída
                    disciplinas_ids = list(disciplinas_turma.values_list('pk', flat=True))
                    if self.instance.disciplina and self.instance.disciplina.pk not in disciplinas_ids:
                        disciplinas_ids.append(self.instance.disciplina.pk)
                    qs = DisciplinaEnsino.objects.filter(pk__in=disciplinas_ids).distinct()
                    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                        militar = getattr(user, 'militar', None)
                        eh_coord_sup = False
                        master = False
                        try:
                            from militares.models import UsuarioMaster
                            master = UsuarioMaster.objects.filter(username=user.username, ativo=True).exists()
                        except Exception:
                            master = False
                        if militar:
                            eh_coord_sup = (
                                getattr(turma, 'supervisor_curso_id', None) == militar.id or
                                getattr(turma, 'coordenador_curso_id', None) == militar.id or
                                getattr(turma, 'supervisor_turma_id', None) == militar.id or
                                getattr(turma, 'coordenador_turma_id', None) == militar.id
                            )
                        if not (user.is_superuser or master or eh_coord_sup):
                            from django.db.models import Q
                            instrutor_ext = None
                            try:
                                instrutor_ext = getattr(militar, 'instrutor_ensino', None)
                            except Exception:
                                instrutor_ext = None
                            qs = qs.filter(
                                Q(instrutor_responsavel_militar=militar) |
                                Q(monitores_militares=militar) |
                                Q(instrutor_responsavel_externo=instrutor_ext)
                            ).distinct()
                    self.fields['disciplina'].queryset = qs
            elif turma_initial:
                # Se houver turma inicial (pré-selecionada), carregar suas disciplinas
                disciplinas_turma = turma_initial.disciplinas.all()
                # Também buscar disciplinas do curso da turma
                if turma_initial.curso:
                    from militares.models import DisciplinaCurso
                    disciplinas_curso = DisciplinaCurso.objects.filter(
                        curso=turma_initial.curso
                    ).select_related('disciplina')
                    disciplinas_ids = list(disciplinas_turma.values_list('pk', flat=True))
                    disciplinas_ids.extend([dc.disciplina.pk for dc in disciplinas_curso])
                    qs = DisciplinaEnsino.objects.filter(pk__in=disciplinas_ids).distinct()
                    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                        militar = getattr(user, 'militar', None)
                        eh_coord_sup = False
                        master = False
                        try:
                            from militares.models import UsuarioMaster
                            master = UsuarioMaster.objects.filter(username=user.username, ativo=True).exists()
                        except Exception:
                            master = False
                        if militar:
                            eh_coord_sup = (
                                getattr(turma_initial, 'supervisor_curso_id', None) == militar.id or
                                getattr(turma_initial, 'coordenador_curso_id', None) == militar.id or
                                getattr(turma_initial, 'supervisor_turma_id', None) == militar.id or
                                getattr(turma_initial, 'coordenador_turma_id', None) == militar.id
                            )
                        if not (user.is_superuser or master or eh_coord_sup):
                            from django.db.models import Q
                            instrutor_ext = None
                            try:
                                instrutor_ext = getattr(militar, 'instrutor_ensino', None)
                            except Exception:
                                instrutor_ext = None
                            qs = qs.filter(
                                Q(instrutor_responsavel_militar=militar) |
                                Q(monitores_militares=militar) |
                                Q(instrutor_responsavel_externo=instrutor_ext)
                            ).distinct()
                    self.fields['disciplina'].queryset = qs
                else:
                    qs = disciplinas_turma
                    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                        militar = getattr(user, 'militar', None)
                        eh_coord_sup = False
                        master = False
                        try:
                            from militares.models import UsuarioMaster
                            master = UsuarioMaster.objects.filter(username=user.username, ativo=True).exists()
                        except Exception:
                            master = False
                        if militar:
                            eh_coord_sup = (
                                getattr(turma_initial, 'supervisor_curso_id', None) == militar.id or
                                getattr(turma_initial, 'coordenador_curso_id', None) == militar.id or
                                getattr(turma_initial, 'supervisor_turma_id', None) == militar.id or
                                getattr(turma_initial, 'coordenador_turma_id', None) == militar.id
                            )
                        if not (user.is_superuser or master or eh_coord_sup):
                            from django.db.models import Q
                            instrutor_ext = None
                            try:
                                instrutor_ext = getattr(militar, 'instrutor_ensino', None)
                            except Exception:
                                instrutor_ext = None
                            qs = qs.filter(
                                Q(instrutor_responsavel_militar=militar) |
                                Q(monitores_militares=militar) |
                                Q(instrutor_responsavel_externo=instrutor_ext)
                            ).distinct()
                    self.fields['disciplina'].queryset = qs
            else:
                # Se for criação sem turma pré-selecionada, começar sem disciplinas (será filtrado via JavaScript)
                self.fields['disciplina'].queryset = DisciplinaEnsino.objects.none()
        
        # Adicionar classes Bootstrap aos campos que não têm widgets definidos
        for field_name, field in self.fields.items():
            if field_name not in ['turma', 'disciplina', 'tipo', 'nome', 'data_avaliacao', 'peso', 'nota_maxima', 'descricao', 'criterios_aprovacao']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.setdefault('class', 'form-select')
                elif isinstance(field.widget, forms.NumberInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault('class', 'form-check-input')
    
    def clean(self):
        cleaned_data = super().clean()
        disciplina = cleaned_data.get('disciplina')
        turma = cleaned_data.get('turma')
        tipo = cleaned_data.get('tipo')
        posicao_avaliacao = cleaned_data.get('posicao_avaliacao')
        
        # IMPORTANTE: Não validar número de avaliações se for recuperação
        # A recuperação pode ser criada independentemente do número de avaliações regulares
        # Verificar tanto o campo 'tipo' quanto 'posicao_avaliacao' porque a conversão
        # de posicao_avaliacao para tipo só acontece depois da validação na view
        if tipo == 'RECUPERACAO' or posicao_avaliacao == 'RECUPERACAO':
            return cleaned_data
        
        # Validar número de avaliações apenas se disciplina e turma estiverem definidos
        # E apenas para avaliações regulares (não recuperação)
        if disciplina and turma and tipo != 'RECUPERACAO' and posicao_avaliacao != 'RECUPERACAO':
            # Contar avaliações existentes (exceto recuperação e a atual se estiver editando)
            from militares.models import AvaliacaoEnsino
            avaliacoes_existentes = AvaliacaoEnsino.objects.filter(
                disciplina=disciplina,
                turma=turma
            ).exclude(tipo='RECUPERACAO')  # Excluir recuperações da contagem
            
            # Se estiver editando, excluir a avaliação atual da contagem
            if self.instance and self.instance.pk:
                avaliacoes_existentes = avaliacoes_existentes.exclude(pk=self.instance.pk)
            
            numero_atual = avaliacoes_existentes.count()
            numero_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
            
            # Se já atingiu o número máximo de avaliações e está criando uma nova
            if not self.instance or not self.instance.pk:
                if numero_atual >= numero_obrigatorio:
                    # Mensagem detalhada conforme regra 15.6
                    if numero_obrigatorio == 1:
                        regra_texto = "até 20 horas aulas, 01 (uma) avaliação"
                    elif numero_obrigatorio == 2:
                        regra_texto = "acima de 20 e até 40 horas aulas, 02 (duas) avaliações"
                    elif numero_obrigatorio == 3:
                        regra_texto = "acima de 40 e até 60 horas aulas, 03 (três) avaliações"
                    else:
                        regra_texto = "acima de 60 horas aulas, 04 (quatro) avaliações"
                    
                    raise forms.ValidationError(
                        f"Conforme a regra 15.6, disciplinas com {regra_texto}. "
                        f"Esta disciplina possui {disciplina.carga_horaria} horas, "
                        f"portanto deve ter no máximo {numero_obrigatorio} avaliação(ões). "
                        f"Já existem {numero_atual} avaliação(ões) cadastrada(s) para esta disciplina nesta turma."
                    )
        
        return cleaned_data


# ============================================================================
# 10. NOTAS (Relacionadas a Avaliação e Aluno)
# ============================================================================

class NotaAvaliacaoForm(forms.ModelForm):
    """Form para Nota de Avaliação"""
    
    class Meta:
        model = NotaAvaliacao
        fields = '__all__'
        widgets = {
            'avaliacao': forms.Select(attrs={'class': 'form-select'}),
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'nota': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'data_lancamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Bootstrap aos campos que não têm widgets definidos
        for field_name, field in self.fields.items():
            if field_name not in ['avaliacao', 'aluno', 'nota', 'data_lancamento', 'observacoes']:
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.setdefault('class', 'form-select')
                elif isinstance(field.widget, forms.NumberInput):
                    field.widget.attrs.setdefault('class', 'form-control')
    
    def clean_nota(self):
        nota = self.cleaned_data.get('nota')
        if nota is not None:
            if nota < 0 or nota > 10:
                raise forms.ValidationError('A nota deve estar entre 0 e 10.')
        return nota


# ============================================================================
# FORMS AUXILIARES E COMPLEMENTARES
# ============================================================================

class PessoaExternaForm(forms.ModelForm):
    """Form para Pessoa Externa"""
    
    class Meta:
        model = PessoaExterna
        fields = [
            'nome_completo', 'cpf', 'rg', 'data_nascimento', 'email', 'telefone',
            'endereco', 'cidade', 'uf', 'cep', 'tipo_pessoa', 'instituicao_origem',
            'foto', 'observacoes', 'ativo'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select'}),
            'instituicao_origem': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cpf'].widget.attrs.update({'placeholder': 'Apenas números'})
        self.fields['cep'].widget.attrs.update({'placeholder': '00000-000'})


class AproveitamentoDisciplinaForm(forms.ModelForm):
    """Form para Aproveitamento de Disciplina"""
    
    class Meta:
        model = AproveitamentoDisciplina
        fields = '__all__'
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'disciplina': forms.Select(attrs={'class': 'form-select'}),
            'curso_origem': forms.TextInput(attrs={'class': 'form-control'}),
            'nota_aproveitamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_aproveitamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CertificadoEnsinoForm(forms.ModelForm):
    """Form para Certificado de Ensino"""
    
    class Meta:
        model = CertificadoEnsino
        fields = '__all__'
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'numero_certificado': forms.TextInput(attrs={'class': 'form-control'}),
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'carga_horaria_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class DocumentoAlunoForm(forms.ModelForm):
    """Form para Documento de Aluno"""
    
    class Meta:
        model = DocumentoAluno
        fields = '__all__'
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'orgao_emissor': forms.TextInput(attrs={'class': 'form-control'}),
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class OcorrenciaDisciplinarForm(forms.ModelForm):
    """Form para Ocorrência Disciplinar"""
    
    class Meta:
        model = OcorrenciaDisciplinar
        fields = '__all__'
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'tipo_ocorrencia': forms.Select(attrs={'class': 'form-select'}),
            'data_ocorrencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'penalidade': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class EscalaInstrucaoForm(forms.ModelForm):
    """Form para Escala de Instrução"""
    
    class Meta:
        model = EscalaInstrucao
        fields = '__all__'
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'disciplina': forms.Select(attrs={'class': 'form-select'}),
            'instrutor': forms.Select(attrs={'class': 'form-select'}),
            'data_aula': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class MaterialEscolarForm(forms.ModelForm):
    """Form para Material Escolar"""
    
    class Meta:
        model = MaterialEscolar
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'quantidade_disponivel': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CautelaMaterialEscolarForm(forms.ModelForm):
    """Form para Cautela de Material Escolar"""
    
    class Meta:
        model = CautelaMaterialEscolar
        fields = '__all__'
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'material': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_cautela': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_devolucao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'devolvido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ============================================================================
# QUADRO DE TRABALHO SEMANAL
# ============================================================================

class QuadroTrabalhoSemanalForm(forms.ModelForm):
    """Form para Quadro de Trabalho Semanal"""
    
    class Meta:
        model = QuadroTrabalhoSemanal
        fields = [
            'turma', 'numero_quadro', 'data_inicio_semana', 'data_fim_semana', 
            'local', 'observacoes'
        ]
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'numero_quadro': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_inicio_semana': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_semana': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Teresina/PI'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas turmas ativas
        if 'turma' in self.fields:
            from militares.models import TurmaEnsino, UsuarioMaster
            qs = TurmaEnsino.objects.filter(ativa=True).order_by('identificacao')
            try:
                if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
                    master = False
                    try:
                        master = UsuarioMaster.objects.filter(username=user.username, ativo=True).exists()
                    except Exception:
                        master = False
                    if not (user.is_superuser or master):
                        militar = getattr(user, 'militar', None)
                        if militar:
                            from django.db.models import Q
                            qs = qs.filter(
                                Q(supervisor_curso_id=militar.id) |
                                Q(coordenador_curso_id=militar.id) |
                                Q(supervisor_turma_id=militar.id) |
                                Q(coordenador_turma_id=militar.id)
                            ).distinct()
            except Exception:
                pass
            self.fields['turma'].queryset = qs
        
        # Configurar formato de data
        if 'data_inicio_semana' in self.fields:
            self.fields['data_inicio_semana'].widget.format = '%Y-%m-%d'
        if 'data_fim_semana' in self.fields:
            self.fields['data_fim_semana'].widget.format = '%Y-%m-%d'
        
        # Se não houver número do quadro, calcular o próximo
        if not self.instance.pk:
            turma_id = self.data.get('turma') if self.data else None
            if not turma_id and self.initial.get('turma'):
                turma_id = self.initial.get('turma')
            
            if turma_id:
                try:
                    ultimo_quadro = QuadroTrabalhoSemanal.objects.filter(turma_id=turma_id).order_by('-numero_quadro').first()
                    if ultimo_quadro:
                        self.fields['numero_quadro'].initial = ultimo_quadro.numero_quadro + 1
                    else:
                        self.fields['numero_quadro'].initial = 1
                except:
                    self.fields['numero_quadro'].initial = 1


class AulaQuadroTrabalhoSemanalForm(forms.ModelForm):
    """Form para Aula do Quadro de Trabalho Semanal"""
    
    class Meta:
        model = AulaQuadroTrabalhoSemanal
        fields = [
            'quadro', 'tipo_atividade', 'disciplina', 'instrutor_militar', 'instrutor_externo', 'dia_semana', 'data',
            'hora_inicio', 'hora_fim', 'horas_aula', 'carga_horaria_total',
            'descricao', 'observacoes', 'ordem'
        ]
        widgets = {
            'quadro': forms.HiddenInput(),
            'tipo_atividade': forms.Select(attrs={'class': 'form-select'}),
            'disciplina': forms.Select(attrs={'class': 'form-select'}),
            'instrutor_militar': forms.Select(attrs={'class': 'form-control militar-select2'}),
            'instrutor_externo': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'horas_aula': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Informe a quantidade de horas/aula'}),
            'carga_horaria_total': forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'placeholder': 'Calculado automaticamente'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Intervalo para Almoço, Horário Livre, Reunião'}),
            'observacoes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PROVA, À DISPOSIÇÃO DA DEIP'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        quadro = kwargs.pop('quadro', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if quadro:
            self.fields['quadro'].initial = quadro.pk
            # Filtrar disciplinas da turma do quadro
            if quadro and quadro.turma:
                self.fields['disciplina'].queryset = quadro.turma.disciplinas.all()
        elif self.instance and self.instance.pk and self.instance.quadro:
            self.fields['disciplina'].queryset = self.instance.quadro.turma.disciplinas.all()
        else:
            self.fields['disciplina'].queryset = DisciplinaEnsino.objects.none()

        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            try:
                militar = getattr(user, 'militar', None)
                turma_ref = None
                if quadro and getattr(quadro, 'turma', None):
                    turma_ref = quadro.turma
                elif self.instance and getattr(self.instance, 'quadro', None) and getattr(self.instance.quadro, 'turma', None):
                    turma_ref = self.instance.quadro.turma
                if militar and turma_ref:
                    eh_coord_sup = (
                        getattr(turma_ref, 'supervisor_curso_id', None) == militar.id or
                        getattr(turma_ref, 'coordenador_curso_id', None) == militar.id or
                        getattr(turma_ref, 'supervisor_turma_id', None) == militar.id or
                        getattr(turma_ref, 'coordenador_turma_id', None) == militar.id
                    )
                    if not (user.is_superuser or eh_coord_sup):
                        qs = self.fields['disciplina'].queryset
                        from django.db.models import Q
                        instrutor_ext = None
                        try:
                            instrutor_ext = getattr(militar, 'instrutor_ensino', None)
                        except Exception:
                            instrutor_ext = None
                        self.fields['disciplina'].queryset = qs.filter(
                            Q(instrutor_responsavel_militar=militar) |
                            Q(monitores_militares=militar) |
                            Q(instrutor_responsavel_externo=instrutor_ext)
                        ).distinct()
            except Exception:
                pass
        
        # Filtrar militares ativos para instrutor militar
        self.fields['instrutor_militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
        
        # Filtrar instrutores externos ativos
        from militares.models import InstrutorEnsino
        self.fields['instrutor_externo'].queryset = InstrutorEnsino.objects.filter(ativo=True).order_by('militar__posto_graduacao', 'militar__nome_completo', 'nome_civil', 'nome_outra_forca')
        
        # Tornar disciplina e instrutores opcionais (obrigatórios apenas para AULA)
        self.fields['disciplina'].required = False
        self.fields['instrutor_militar'].required = False
        self.fields['instrutor_externo'].required = False
        
        # Tornar descricao obrigatória para tipos que não são AULA
        self.fields['descricao'].required = False
        
        # Configurar formato de data
        if 'data' in self.fields:
            self.fields['data'].widget.format = '%Y-%m-%d'
        
        # Configurar formato de hora
        if 'hora_inicio' in self.fields:
            self.fields['hora_inicio'].widget.format = '%H:%M'
        if 'hora_fim' in self.fields:
            self.fields['hora_fim'].widget.format = '%H:%M'
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_atividade = cleaned_data.get('tipo_atividade', 'AULA')
        
        if tipo_atividade == 'AULA':
            # Para aula, disciplina é obrigatória
            if not cleaned_data.get('disciplina'):
                from django.core.exceptions import ValidationError
                raise ValidationError({'disciplina': 'Disciplina é obrigatória para tipo "Aula".'})
        else:
            # Para outros tipos, descricao é obrigatória
            if not cleaned_data.get('descricao'):
                from django.core.exceptions import ValidationError
                raise ValidationError({'descricao': 'Descrição é obrigatória para este tipo de atividade.'})
        
        return cleaned_data


# ============================================================================
# FORMULÁRIOS PARA MODELOS ITE 01/2024
# ============================================================================

class PlanoGeralEnsinoForm(forms.ModelForm):
    """Form para Plano Geral de Ensino"""
    
    class Meta:
        model = PlanoGeralEnsino
        fields = '__all__'
        widgets = {
            'data_elaboracao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_envio_homologacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_homologacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_publicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ItemPlanoGeralEnsinoForm(forms.ModelForm):
    """Form para Item do Plano Geral de Ensino"""
    
    class Meta:
        model = ItemPlanoGeralEnsino
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ProjetoPedagogicoForm(forms.ModelForm):
    """Form para Projeto Pedagógico"""
    
    class Meta:
        model = ProjetoPedagogico
        fields = '__all__'
        widgets = {
            'apresentacao': CKEditor5Widget(config_name='default'),
            'justificativa': CKEditor5Widget(config_name='default'),
            'objetivo_geral': CKEditor5Widget(config_name='default'),
            'objetivos_especificos': CKEditor5Widget(config_name='default'),
            'perfil_egresso_atitudes': CKEditor5Widget(config_name='default'),
            'perfil_egresso_habilidades': CKEditor5Widget(config_name='default'),
            'perfil_egresso_conhecimentos': CKEditor5Widget(config_name='default'),
            'area_atuacao': CKEditor5Widget(config_name='default'),
            'estrutura_gestao_curso': CKEditor5Widget(config_name='default'),
            'estrategias_pedagogicas': CKEditor5Widget(config_name='default'),
            'estrategias_administrativas': CKEditor5Widget(config_name='default'),
            'matriz_curricular_por_area_tematica': CKEditor5Widget(config_name='default'),
            'recursos_humanos': CKEditor5Widget(config_name='default'),
            'recursos_materiais': CKEditor5Widget(config_name='default'),
            'recursos_financeiros': CKEditor5Widget(config_name='default'),
            'estrutura_fisica': CKEditor5Widget(config_name='default'),
            'calendario_curso': CKEditor5Widget(config_name='default'),
            'criterios_avaliacao_curso': CKEditor5Widget(config_name='default'),
            'criterios_avaliacao_docente': CKEditor5Widget(config_name='default'),
            'criterios_avaliacao_discente': CKEditor5Widget(config_name='default'),
            'criterios_certificacao': CKEditor5Widget(config_name='default'),
            'prescricoes_diversas': CKEditor5Widget(config_name='default'),
            'referencias': CKEditor5Widget(config_name='default'),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'data_aprovacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class PlanoCursoEstagioForm(forms.ModelForm):
    """Form para Plano de Curso/Estágio"""
    
    class Meta:
        model = PlanoCursoEstagio
        fields = '__all__'
        widgets = {
            'data_inicio_desmobilizacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_desmobilizacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_inicio_recesso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_recesso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_aprovacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class PlanoDisciplinaForm(forms.ModelForm):
    """Form para Plano de Disciplina"""
    
    class Meta:
        model = PlanoDisciplina
        fields = '__all__'
        widgets = {
            'ementa_detalhada': CKEditor5Widget(config_name='default'),
            'conteudo_programatico_detalhado': CKEditor5Widget(config_name='default'),
            'objetivos_especificos': CKEditor5Widget(config_name='default'),
            'metodologia_ensino': CKEditor5Widget(config_name='default'),
            'recursos_didaticos': CKEditor5Widget(config_name='default'),
            'sistema_avaliacao': CKEditor5Widget(config_name='default'),
            'bibliografia_basica': CKEditor5Widget(config_name='default'),
            'bibliografia_complementar': CKEditor5Widget(config_name='default'),
            'cronograma_atividades': CKEditor5Widget(config_name='default'),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'data_aprovacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class PlanoPalestraForm(forms.ModelForm):
    """Form para Plano de Palestra"""
    
    class Meta:
        model = PlanoPalestra
        fields = '__all__'
        widgets = {
            'finalidade': CKEditor5Widget(config_name='default'),
            'referencias': CKEditor5Widget(config_name='default'),
            'objetivos': CKEditor5Widget(config_name='default'),
            'publico': CKEditor5Widget(config_name='default'),
            'formacao_palestrante': CKEditor5Widget(config_name='default'),
            'especializacoes_palestrante': CKEditor5Widget(config_name='default'),
            'recursos_necessarios': CKEditor5Widget(config_name='default'),
            'data_palestra': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class AtividadeTreinamentoCampoForm(forms.ModelForm):
    """Form para Atividade de Treinamento de Campo (ATC)"""
    
    class Meta:
        model = AtividadeTreinamentoCampo
        fields = '__all__'
        widgets = {
            'descricao': CKEditor5Widget(config_name='default'),
            'objetivos': CKEditor5Widget(config_name='default'),
            'criterios_avaliacao': CKEditor5Widget(config_name='default'),
            'data_realizacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class AtividadeComplementarEnsinoForm(forms.ModelForm):
    """Form para Atividade Complementar de Ensino (ACE)"""
    
    class Meta:
        model = AtividadeComplementarEnsino
        fields = '__all__'
        widgets = {
            'descricao': CKEditor5Widget(config_name='default'),
            'objetivos': CKEditor5Widget(config_name='default'),
            'data_realizacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class TesteConhecimentosProfissionaisForm(forms.ModelForm):
    """Form para Teste de Conhecimentos Profissionais (TCP)"""
    
    class Meta:
        model = TesteConhecimentosProfissionais
        fields = '__all__'
        widgets = {
            'descricao': CKEditor5Widget(config_name='default'),
            'objetivo': CKEditor5Widget(config_name='default'),
            'area_conhecimento': CKEditor5Widget(config_name='default'),
            'unidades_envolvidas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'data_convocacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_aplicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class PlanoEstagioNivelamentoProfissionalForm(forms.ModelForm):
    """Form para Plano de Estágio de Nivelamento Profissional"""
    
    class Meta:
        model = PlanoEstagioNivelamentoProfissional
        fields = '__all__'
        widgets = {
            'objetivo_geral': CKEditor5Widget(config_name='default'),
            'objetivos_especificos': CKEditor5Widget(config_name='default'),
            'conteudo_programatico': CKEditor5Widget(config_name='default'),
            'metodologia': CKEditor5Widget(config_name='default'),
            'sistema_avaliacao': CKEditor5Widget(config_name='default'),
            'publico_alvo': CKEditor5Widget(config_name='default'),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class RelatorioAnualDEIPForm(forms.ModelForm):
    """Form para Relatório Anual da DEIP"""
    
    class Meta:
        model = RelatorioAnualDEIP
        fields = '__all__'
        widgets = {
            'data_elaboracao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_finalizacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_publicacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'modalidades_cursos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'militares_coordenacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes_especificas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ProcessoSelecaoAlunosForm(forms.ModelForm):
    """Form para Processo de Seleção de Alunos"""
    
    class Meta:
        model = ProcessoSelecaoAlunos
        fields = '__all__'
        widgets = {
            'criterios_selecao': CKEditor5Widget(config_name='default'),
            'data_inicio_inscricoes': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_inscricoes': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_publicacao_edital': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_homologacao_diretor': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class InscricaoProcessoSelecaoForm(forms.ModelForm):
    """Form para Inscrição no Processo de Seleção"""
    
    class Meta:
        model = InscricaoProcessoSelecao
        fields = '__all__'
        widgets = {
            'data_desistencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motivo_desistencia': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class RecursoProcessoSelecaoForm(forms.ModelForm):
    """Form para Recurso no Processo de Seleção"""
    
    class Meta:
        model = RecursoProcessoSelecao
        fields = '__all__'
        widgets = {
            'fundamentacao': CKEditor5Widget(config_name='default'),
            'parecer': CKEditor5Widget(config_name='default'),
            'data_apresentacao': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'data_analise': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class TrabalhoConclusaoCursoForm(forms.ModelForm):
    """Form para Trabalho de Conclusão de Curso (TCC)"""
    
    class Meta:
        model = TrabalhoConclusaoCurso
        fields = '__all__'
        widgets = {
            'resumo': CKEditor5Widget(config_name='default'),
            'data_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_apresentacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class PlanoSegurancaForm(forms.ModelForm):
    """Form para Plano de Segurança"""
    
    class Meta:
        model = PlanoSeguranca
        fields = '__all__'
        widgets = {
            'riscos_identificados': CKEditor5Widget(config_name='default'),
            'medidas_seguranca': CKEditor5Widget(config_name='default'),
            'epis_necessarios': CKEditor5Widget(config_name='default'),
            'plano_emergencias': CKEditor5Widget(config_name='default'),
            'dispositivos_seguranca': CKEditor5Widget(config_name='default'),
            'observacoes_reconhecimento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'data_atividade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_briefing': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'data_aprovacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ClassificacaoFinalCursoForm(forms.ModelForm):
    """Form para Classificação Final do Curso"""
    
    class Meta:
        model = ClassificacaoFinalCurso
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
