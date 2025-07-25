from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from .models import Militar, FichaConceitoOficiais, FichaConceitoPracas, Documento, ComissaoPromocao, MembroComissao, SessaoComissao, DeliberacaoComissao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao, QuadroAcesso, QuadroFixacaoVagas, UsuarioFuncao, CargoFuncao
from django_ckeditor_5.widgets import CKEditor5Widget
from dal_select2.widgets import ModelSelect2


class MilitarForm(forms.ModelForm):
    class Meta:
        model = Militar
        fields = [
            'numeracao_antiguidade', 'matricula', 'nome_completo', 'nome_guerra', 'cpf', 'rg', 'orgao_expedidor',
            'data_nascimento', 'sexo', 'quadro', 'posto_graduacao',
            'data_ingresso', 'data_promocao_atual', 'situacao', 'email', 'telefone',
            'celular', 'foto', 'observacoes',
            'curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_cho', 'nota_cho', 'curso_superior', 'pos_graduacao', 'curso_csbm', 'curso_adaptacao_oficial',
            'curso_cfsd', 'curso_formacao_pracas', 'curso_chc', 'nota_chc', 'curso_chsgt', 'nota_chsgt', 'curso_cas',
            'apto_inspecao_saude', 'data_inspecao_saude', 'data_validade_inspecao_saude',
        ]
        widgets = {
            'numeracao_antiguidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1, 2, 3...',
                'min': '1'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 123456'
            }),
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do militar'
            }),
            'nome_guerra': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de guerra'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control cpf-mask',
                'placeholder': '000.000.000-00'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do RG'
            }),
            'orgao_expedidor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: SSP-PI'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quadro': forms.Select(attrs={
                'class': 'form-select'
            }),
            'posto_graduacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_ingresso': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'data_promocao_atual': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'situacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '(00) 0000-0000'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '(00) 00000-0000'
            }),
            'data_inspecao_saude': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'data_validade_inspecao_saude': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'observacoes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Observações adicionais sobre o militar...'
            }),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'curso_formacao_oficial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_aperfeicoamento_oficial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_cho': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'nota_cho': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 8.5, 9.0, 10.0',
                'step': '0.01',
                'min': '0',
                'max': '10'
            }),
            'curso_superior': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'pos_graduacao': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_csbm': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_adaptacao_oficial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_cfsd': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_formacao_pracas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'curso_chc': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'nota_chc': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 8.5, 9.0, 10.0',
                'step': '0.01',
                'min': '0',
                'max': '10'
            }),
            'curso_chsgt': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'nota_chsgt': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 8.5, 9.0, 10.0',
                'step': '0.01',
                'min': '0',
                'max': '10'
            }),
            'curso_cas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'apto_inspecao_saude': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantir que os campos de data tenham o formato correto
        for field_name in ['data_nascimento', 'data_ingresso', 'data_promocao_atual', 
                          'data_inspecao_saude', 'data_validade_inspecao_saude']:
            if field_name in self.fields:
                field = self.fields[field_name]
                # Definir o formato de data para o widget
                field.widget.format = '%Y-%m-%d'

    def clean_data_promocao_atual(self):
        data_promocao = self.cleaned_data.get('data_promocao_atual')
        data_ingresso = self.cleaned_data.get('data_ingresso')
        
        if data_promocao and data_ingresso and data_promocao < data_ingresso:
            raise forms.ValidationError(
                "A data da promoção atual não pode ser anterior à data de ingresso."
            )
        
        return data_promocao

    def clean_data_validade_inspecao_saude(self):
        data_validade = self.cleaned_data.get('data_validade_inspecao_saude')
        data_inspecao = self.cleaned_data.get('data_inspecao_saude')
        
        if data_validade and data_inspecao and data_validade < data_inspecao:
            raise forms.ValidationError(
                "A data de validade da inspeção de saúde não pode ser anterior à data da inspeção."
            )
        
        return data_validade

    def clean(self):
        cleaned_data = super().clean()
        quadro = cleaned_data.get('quadro')
        posto_graduacao = cleaned_data.get('posto_graduacao')
        numeracao_antiguidade = cleaned_data.get('numeracao_antiguidade')
        
        # Se for NVRR (por quadro ou posto), remover numeração de antiguidade
        if quadro == 'NVRR' or posto_graduacao == 'NVRR':
            cleaned_data['numeracao_antiguidade'] = None
            # Limpar o campo para não mostrar erro de validação
            if 'numeracao_antiguidade' in self.errors:
                del self.errors['numeracao_antiguidade']
        
        return cleaned_data


class FichaConceitoOficiaisForm(forms.ModelForm):
    tempo_posto_calculado = forms.IntegerField(
        label="Tempo no Posto (calculado automaticamente)",
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',
            'style': 'background-color: #f8f9fa;'
        })
    )
    tempo_posto = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    class Meta:
        model = FichaConceitoOficiais
        exclude = ['militar', 'pontos']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Observações...'}),
        }
    
    def __init__(self, *args, **kwargs):
        militar = kwargs.pop('militar', None)
        super().__init__(*args, **kwargs)
        
        if militar:
            tempo_posto = militar.tempo_posto_atual()
            tempo_posto = int(tempo_posto)  # Garante inteiro
            self.fields['tempo_posto_calculado'].initial = tempo_posto
            self.fields['tempo_posto'].initial = tempo_posto
            self.initial['tempo_posto_calculado'] = tempo_posto
            self.initial['tempo_posto'] = tempo_posto
            if self.instance and hasattr(self.instance, 'tempo_posto'):
                self.instance.tempo_posto = tempo_posto

class FichaConceitoPracasForm(forms.ModelForm):
    tempo_posto_calculado = forms.IntegerField(
        label="Tempo no Posto (calculado automaticamente)",
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',
            'style': 'background-color: #f8f9fa;'
        })
    )
    tempo_posto = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    class Meta:
        model = FichaConceitoPracas
        exclude = ['militar', 'pontos']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Observações...'}),
        }
    
    def __init__(self, *args, **kwargs):
        militar = kwargs.pop('militar', None)
        super().__init__(*args, **kwargs)
        
        if militar:
            # Calcular e definir o tempo no posto
            tempo_posto = militar.tempo_posto_atual()
            self.fields['tempo_posto_calculado'].initial = tempo_posto
            self.fields['tempo_posto'].initial = tempo_posto


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['tipo', 'titulo', 'arquivo', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Diploma de Engenharia Civil', 'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            if arquivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 10MB.")
            
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            nome_arquivo = arquivo.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(
                    "Formato de arquivo não permitido. Use: PDF, JPG, PNG, DOC, DOCX"
                )
        
        return arquivo


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ConfirmarSenhaForm(forms.Form):
    senha = forms.CharField(
        label="Confirme sua senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha para confirmar'
        })
    ) 

# FORMULÁRIOS DA COMISSÃO DE PROMOÇÕES DE OFICIAIS

class ComissaoPromocaoForm(forms.ModelForm):
    """Formulário para Comissão de Promoções (Oficiais e Praças)"""
    
    class Meta:
        model = ComissaoPromocao
        fields = ['tipo', 'nome', 'data_criacao', 'data_termino', 'status', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_criacao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'data_termino': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs.update({
            'onchange': 'preencherNomeComissao()'
        })
        self.fields['nome'].widget.attrs.update({
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        data_criacao = cleaned_data.get('data_criacao')
        data_termino = cleaned_data.get('data_termino')
        if data_termino and data_criacao and data_termino < data_criacao:
            raise forms.ValidationError('A data de término não pode ser anterior à data de criação.')
        return cleaned_data


class MembroComissaoForm(forms.ModelForm):
    """Formulário para Membro da Comissão"""
    
    # Campo para função do usuário (em vez de cargo da comissão)
    cargo = forms.ModelChoiceField(
        queryset=CargoFuncao.objects.filter(ativo=True).order_by('nome'),
        required=True,
        label='Função/Cargo do Usuário',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_cargo',
            'data-placeholder': 'Selecione o usuário primeiro...'
        }),
        help_text='Selecione a função do usuário do sistema'
    )
    
    class Meta:
        model = MembroComissao
        fields = ['militar', 'cargo', 'data_nomeacao', 'data_termino', 'ativo', 'observacoes']
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'Selecione o usuário do sistema...',
                'id': 'id_militar'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_nomeacao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'data_termino': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, comissao_tipo=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuários que têm militares vinculados e estão ativos
        usuarios_com_militares = User.objects.filter(
            militar__isnull=False,  # Apenas usuários com militar vinculado
            militar__situacao='AT',  # Apenas militares ativos
            is_active=True  # Apenas usuários ativos
        ).order_by('militar__nome_completo')
        
        # Filtrar baseado no tipo de comissão e funções específicas
        if comissao_tipo == 'CPO':
            # Para CPO: apenas usuários com funções CPO
            usuarios_com_militares = usuarios_com_militares.filter(
                militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS'],  # Apenas oficiais
                funcoes__cargo_funcao__nome__icontains='CPO',  # Com função CPO
                funcoes__status='ATIVO'  # Função ativa
            ).distinct()
            
        elif comissao_tipo == 'CPP':
            # Para CPP: apenas usuários com funções CPP
            usuarios_com_militares = usuarios_com_militares.filter(
                militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS'],  # Apenas oficiais
                funcoes__cargo_funcao__nome__icontains='CPP',  # Com função CPP
                funcoes__status='ATIVO'  # Função ativa
            ).distinct()
        
        # Criar choices para o campo militar baseado nos usuários
        choices = [('', 'Selecione o usuário...')]
        for user in usuarios_com_militares:
            militar = user.militar
            # Buscar a função específica do usuário
            funcao_cpo_cpp = user.funcoes.filter(
                status='ATIVO',
                cargo_funcao__nome__icontains=comissao_tipo if comissao_tipo else ''
            ).first()
            
            if funcao_cpo_cpp:
                display_text = f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula} ({funcao_cpo_cpp.cargo_funcao.nome})"
            else:
                display_text = f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}"
            
            choices.append((militar.id, display_text))
        
        self.fields['militar'].choices = choices
        self.fields['militar'].queryset = Militar.objects.filter(
            user__in=usuarios_com_militares
        ).order_by('nome_completo')
    
    def clean(self):
        cleaned_data = super().clean()
        data_nomeacao = cleaned_data.get('data_nomeacao')
        data_termino = cleaned_data.get('data_termino')
        
        if data_termino and data_nomeacao and data_termino < data_nomeacao:
            raise forms.ValidationError('A data de término não pode ser anterior à data de nomeação.')
        
        return cleaned_data


class SessaoComissaoForm(forms.ModelForm):
    """Formulário para Sessão da Comissão"""
    
    # Campos para documento da sessão
    documento_titulo = forms.CharField(
        max_length=200,
        required=False,
        label="Título do Documento",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Quadro de Acesso 2024 - Oficiais'
        })
    )
    
    documento_tipo = forms.ChoiceField(
        choices=[
            ('', 'Selecione o tipo...'),
            ('PAUTA', 'Pauta da Sessão'),
            ('ATA', 'Ata da Sessão'),
            ('MEMORANDO', 'Memorando'),
            ('OFICIO', 'Ofício'),
            ('REQUERIMENTO', 'Requerimento'),
            ('MANDADO_JUDICIAL', 'Mandado Judicial'),
            ('DESPACHO', 'Despacho'),
            ('PARECER', 'Parecer'),
            ('DECISAO', 'Decisão'),
            ('SENTENCA', 'Sentença'),
            ('NOTIFICACAO', 'Notificação'),
            ('INTIMACAO', 'Intimação'),
            ('CERTIDAO', 'Certidão'),
            ('PROCURACAO', 'Procuração'),
            ('CONTRATO', 'Contrato'),
            ('PORTARIA', 'Portaria'),
            ('DECRETO', 'Decreto'),
            ('RELATORIO', 'Relatório'),
            ('QUADRO_ACESSO', 'Quadro de Acesso'),
            ('FICHA_CONCEITO', 'Ficha de Conceito'),
            ('OUTROS', 'Outros'),
        ],
        required=False,
        label="Tipo do Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    documento_arquivo = forms.FileField(
        required=False,
        label="Arquivo do Documento",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Formatos aceitos: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX (máx. 10MB)"
    )
    
    documento_descricao = forms.CharField(
        required=False,
        label="Descrição do Documento",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descrição detalhada do documento...'
        })
    )
    
    class Meta:
        model = SessaoComissao
        fields = ['numero', 'tipo', 'data_sessao', 'hora_inicio', 'hora_fim', 'local', 'pauta', 'status', 'observacoes']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'data_sessao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'hora_inicio': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                },
                format='%H:%M'
            ),
            'hora_fim': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                },
                format='%H:%M'
            ),
            'pauta': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Digite observações importantes sobre a sessão...', 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fim = cleaned_data.get('hora_fim')
        
        # Validar horários apenas se ambos estiverem preenchidos
        if hora_fim and hora_inicio:
            if hora_fim <= hora_inicio:
                self.add_error('hora_fim', 'A hora de término deve ser posterior à hora de início.')
        
        # Validar documento se foi fornecido
        documento_titulo = cleaned_data.get('documento_titulo')
        documento_tipo = cleaned_data.get('documento_tipo')
        documento_arquivo = cleaned_data.get('documento_arquivo')
        
        # Se pelo menos um campo de documento foi preenchido, todos são obrigatórios
        if documento_titulo or documento_tipo or documento_arquivo:
            if not documento_titulo:
                self.add_error('documento_titulo', 'Título é obrigatório quando um documento é fornecido.')
            if not documento_tipo:
                self.add_error('documento_tipo', 'Tipo é obrigatório quando um documento é fornecido.')
            if not documento_arquivo:
                self.add_error('documento_arquivo', 'Arquivo é obrigatório quando um documento é fornecido.')
        
        return cleaned_data
    
    def clean_numero(self):
        """Validar número da sessão"""
        numero = self.cleaned_data.get('numero')
        comissao = self.cleaned_data.get('comissao')
        
        if numero and comissao:
            # Verificar se já existe uma sessão com este número na mesma comissão
            existing_sessao = SessaoComissao.objects.filter(
                comissao=comissao, 
                numero=numero
            )
            
            # Se estamos editando, excluir a sessão atual da verificação
            if self.instance.pk:
                existing_sessao = existing_sessao.exclude(pk=self.instance.pk)
            
            if existing_sessao.exists():
                raise forms.ValidationError('Já existe uma sessão com este número nesta comissão.')
        
        return numero
    
    def clean_data_sessao(self):
        """Validar data da sessão"""
        data_sessao = self.cleaned_data.get('data_sessao')
        
        if data_sessao:
            from datetime import date
            if data_sessao < date.today():
                raise forms.ValidationError('A data da sessão não pode ser anterior a hoje.')
        
        return data_sessao
    
    def clean_documento_arquivo(self):
        arquivo = self.cleaned_data.get('documento_arquivo')
        if arquivo:
            if arquivo.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("O arquivo deve ter no máximo 10MB.")
            
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx']
            nome_arquivo = arquivo.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(
                    "Formato de arquivo não permitido. Use: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX"
                )
        
        return arquivo


class DeliberacaoComissaoForm(forms.ModelForm):
    """Formulário para Deliberação da Comissão"""
    
    class Meta:
        model = DeliberacaoComissao
        fields = ['numero', 'tipo', 'assunto', 'descricao', 'resultado']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'resultado': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'O resultado será preenchido após a votação ser concluída...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar o campo resultado opcional na criação
        if not self.instance.pk:  # Se é uma nova deliberação
            self.fields['resultado'].required = False
            self.fields['resultado'].widget.attrs['readonly'] = 'readonly'
            self.fields['resultado'].widget.attrs['style'] = 'background-color: #f8f9fa;'
            self.fields['resultado'].help_text = 'Este campo será habilitado após a votação ser concluída.'
        else:
            # Se é uma edição, verificar se a votação foi concluída
            if hasattr(self.instance, 'votos') and self.instance.votos.exists():
                total_presentes = self.instance.sessao.presencas.filter(presente=True).count()
                total_votos = self.instance.votos.count()
                if total_votos >= total_presentes:
                    # Votação concluída, permitir edição do resultado
                    self.fields['resultado'].required = True
                    self.fields['resultado'].widget.attrs.pop('readonly', None)
                    self.fields['resultado'].widget.attrs.pop('style', None)
                    self.fields['resultado'].help_text = 'Registre a decisão ou resultado da deliberação após a votação.'
                else:
                    # Votação ainda não concluída
                    self.fields['resultado'].required = False
                    self.fields['resultado'].widget.attrs['readonly'] = 'readonly'
                    self.fields['resultado'].widget.attrs['style'] = 'background-color: #f8f9fa;'
                    self.fields['resultado'].help_text = f'Votação em andamento: {total_votos}/{total_presentes} votos registrados.'
            else:
                # Nenhum voto registrado ainda
                self.fields['resultado'].required = False
                self.fields['resultado'].widget.attrs['readonly'] = 'readonly'
                self.fields['resultado'].widget.attrs['style'] = 'background-color: #f8f9fa;'
                self.fields['resultado'].help_text = 'Aguardando início da votação.'
    
    def clean_resultado(self):
        resultado = self.cleaned_data.get('resultado')
        # Se é uma nova deliberação, não permitir preenchimento do resultado
        if not self.instance.pk:
            if resultado:
                raise forms.ValidationError(
                    "O resultado da deliberação só pode ser preenchido após a votação ser concluída."
                )
            return ""
        # Removido: restrição de só permitir resultado após todos votarem
        return resultado


class DocumentoSessaoForm(forms.ModelForm):
    """Formulário para Documento da Sessão"""
    
    class Meta:
        model = DocumentoSessao
        fields = ['tipo', 'titulo', 'descricao', 'arquivo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Quadro de Acesso 2024'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição do documento...'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            if arquivo.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("O arquivo deve ter no máximo 10MB.")
            
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx']
            nome_arquivo = arquivo.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(
                    "Formato de arquivo não permitido. Use: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX"
                )
        
        return arquivo 

class AtaSessaoForm(forms.ModelForm):
    class Meta:
        model = AtaSessao
        fields = ['conteudo']
        widgets = {
            'conteudo': CKEditor5Widget(config_name='ata_config'),
        }


class ModeloAtaForm(forms.ModelForm):
    """Formulário para criação e edição de modelos de ata"""
    
    class Meta:
        model = ModeloAta
        fields = ['nome', 'descricao', 'tipo_comissao', 'tipo_sessao', 'conteudo', 'ativo', 'padrao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Modelo Padrão CPO Ordinária'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do modelo e quando usá-lo...'
            }),
            'tipo_comissao': forms.Select(attrs={'class': 'form-control'}),
            'tipo_sessao': forms.Select(attrs={'class': 'form-control'}),
            'conteudo': CKEditor5Widget(config_name='modelo_ata_config'),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'padrao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'conteudo': 'Use variáveis como {{sessao.numero}}, {{sessao.data_sessao}}, {{sessao.local}}, {{comissao.nome}}, etc.',
        } 

class CargoComissaoForm(forms.ModelForm):
    """Formulário para Cargo da Comissão"""
    
    class Meta:
        model = CargoComissao
        fields = ['nome', 'codigo', 'descricao', 'ativo', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        # Converter para maiúsculas e remover espaços
        codigo = codigo.upper().replace(' ', '_')
        return codigo


class QuadroAcessoForm(forms.ModelForm):
    """Formulário para Quadro de Acesso"""
    
    class Meta:
        model = QuadroAcesso
        fields = ['tipo', 'data_promocao', 'status', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'data_promocao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.HiddenInput(),  # Campo hidden com valor padrão
            'observacoes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Observações sobre o quadro de acesso...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir valor padrão para status
        if not self.instance.pk:  # Se é um novo registro
            self.fields['status'].initial = 'EM_ELABORACAO'


class QuadroFixacaoVagasForm(forms.ModelForm):
    """Formulário para Quadro de Fixação de Vagas"""
    
    class Meta:
        model = QuadroFixacaoVagas
        fields = ['titulo', 'tipo', 'data_promocao', 'status', 'observacoes']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Quadro de Fixação de Vagas 2024 - Oficiais'
            }),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'data_promocao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Observações sobre o quadro de fixação de vagas...'
            }),
        } 

class EncerrarComissaoForm(forms.Form):
    """Formulário para encerrar comissão com data e opção de retornar"""
    data_encerramento = forms.DateField(
        label="Data de Encerramento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Data em que a comissão será encerrada"
    )
    observacoes = forms.CharField(
        label="Observações",
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        help_text="Observações sobre o encerramento da comissão"
    )
    retornar_comissao = forms.BooleanField(
        label="Retornar comissão à ativa",
        required=False,
        help_text="Marcar se deseja retornar a comissão ao status ativo"
    ) 

class UsuarioFuncaoForm(forms.ModelForm):
    """Formulário para Função do Usuário"""
    
    class Meta:
        model = UsuarioFuncao
        fields = ['cargo_funcao', 'tipo_funcao', 'descricao', 'status', 'data_inicio', 'data_fim', 'observacoes']
        widgets = {
            'cargo_funcao': forms.Select(attrs={'class': 'form-control'}),
            'tipo_funcao': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'data_fim': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas cargos/funções ativos
        self.fields['cargo_funcao'].queryset = CargoFuncao.objects.filter(ativo=True).order_by('nome') 

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Deixe em branco para manter a senha atual'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Confirmar Senha'
    )
    militar_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    cargo_funcao = forms.ModelChoiceField(
        queryset=CargoFuncao.objects.filter(ativo=True).order_by('nome'),
        required=True,
        label='Função/Cargo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'is_superuser', 'cargo_funcao'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '🔍 Digite o nome do militar para buscar e preencher automaticamente...',
                'autocomplete': 'off'
            }),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if not self.instance.pk:
            if not password:
                raise forms.ValidationError('Senha é obrigatória para novos usuários.')
            if not confirm_password:
                raise forms.ValidationError('Confirmação de senha é obrigatória para novos usuários.')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned_data 

class CargoFuncaoForm(forms.ModelForm):
    """Formulário para Cargo/Função com permissões"""
    
    # Campos de permissões por módulo
    MILITARES_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    FICHAS_CONCEITO_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('APROVAR', 'Aprovar'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    QUADROS_ACESSO_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    PROMOCOES_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('APROVAR', 'Aprovar'),
        ('HOMOLOGAR', 'Homologar'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    VAGAS_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    COMISSAO_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('ASSINAR', 'Assinar'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    DOCUMENTOS_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('GERAR_PDF', 'Gerar PDF'),
        ('IMPRIMIR', 'Imprimir'),
        ('ASSINAR', 'Assinar'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    USUARIOS_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    RELATORIOS_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('GERAR_PDF', 'Gerar PDF'),
        ('IMPRIMIR', 'Imprimir'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    CONFIGURACOES_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('EDITAR', 'Editar'),
        ('ADMINISTRAR', 'Administrar'),
    ]
    
    # Campos de permissões
    permissoes_militares = forms.MultipleChoiceField(
        choices=MILITARES_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Gestão de Militares'
    )
    
    permissoes_fichas_conceito = forms.MultipleChoiceField(
        choices=FICHAS_CONCEITO_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Fichas de Conceito'
    )
    
    permissoes_quadros_acesso = forms.MultipleChoiceField(
        choices=QUADROS_ACESSO_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Quadros de Acesso'
    )
    
    permissoes_promocoes = forms.MultipleChoiceField(
        choices=PROMOCOES_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Promoções'
    )
    
    permissoes_vagas = forms.MultipleChoiceField(
        choices=VAGAS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Gestão de Vagas'
    )
    
    permissoes_comissao = forms.MultipleChoiceField(
        choices=COMISSAO_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Comissão de Promoções'
    )
    
    permissoes_documentos = forms.MultipleChoiceField(
        choices=DOCUMENTOS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Documentos'
    )
    
    permissoes_usuarios = forms.MultipleChoiceField(
        choices=USUARIOS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Gestão de Usuários'
    )
    
    permissoes_relatorios = forms.MultipleChoiceField(
        choices=RELATORIOS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Relatórios'
    )
    
    permissoes_configuracoes = forms.MultipleChoiceField(
        choices=CONFIGURACOES_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Permissões - Configurações do Sistema'
    )
    
    class Meta:
        model = CargoFuncao
        fields = ['nome', 'descricao', 'ativo', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cargo/função'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição do cargo/função'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Bootstrap aos labels
        for field_name, field in self.fields.items():
            if field_name.startswith('permissoes_'):
                continue  # Pular campos de permissões
            field.label = field.label.title()
            if field_name == 'ativo':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Carregar permissões existentes se for edição
        if self.instance and self.instance.pk:
            self.carregar_permissoes_existentes()
    
    def carregar_permissoes_existentes(self):
        """Carrega as permissões existentes do cargo/função"""
        from .models import PermissaoFuncao
        
        permissoes = PermissaoFuncao.objects.filter(cargo_funcao=self.instance, ativo=True)
        
        # Mapear permissões por módulo
        permissoes_por_modulo = {}
        for permissao in permissoes:
            if permissao.modulo not in permissoes_por_modulo:
                permissoes_por_modulo[permissao.modulo] = []
            permissoes_por_modulo[permissao.modulo].append(permissao.acesso)
        
        # Definir valores iniciais para os campos de permissões
        mapeamento_campos = {
            'MILITARES': 'permissoes_militares',
            'FICHAS_CONCEITO': 'permissoes_fichas_conceito',
            'QUADROS_ACESSO': 'permissoes_quadros_acesso',
            'PROMOCOES': 'permissoes_promocoes',
            'VAGAS': 'permissoes_vagas',
            'COMISSAO': 'permissoes_comissao',
            'DOCUMENTOS': 'permissoes_documentos',
            'USUARIOS': 'permissoes_usuarios',
            'RELATORIOS': 'permissoes_relatorios',
            'CONFIGURACOES': 'permissoes_configuracoes',
        }
        
        for modulo, campo in mapeamento_campos.items():
            if modulo in permissoes_por_modulo:
                self.fields[campo].initial = permissoes_por_modulo[modulo]
    
    def save(self, commit=True):
        """Salva o cargo/função e suas permissões"""
        cargo = super().save(commit=False)
        
        if commit:
            cargo.save()
            self.salvar_permissoes(cargo)
        
        return cargo
    
    def salvar_permissoes(self, cargo):
        """Salva as permissões selecionadas para o cargo/função"""
        from .models import PermissaoFuncao
        
        # Mapeamento de campos para módulos
        mapeamento_campos = {
            'permissoes_militares': 'MILITARES',
            'permissoes_fichas_conceito': 'FICHAS_CONCEITO',
            'permissoes_quadros_acesso': 'QUADROS_ACESSO',
            'permissoes_promocoes': 'PROMOCOES',
            'permissoes_vagas': 'VAGAS',
            'permissoes_comissao': 'COMISSAO',
            'permissoes_documentos': 'DOCUMENTOS',
            'permissoes_usuarios': 'USUARIOS',
            'permissoes_relatorios': 'RELATORIOS',
            'permissoes_configuracoes': 'CONFIGURACOES',
        }
        
        # Limpar permissões existentes
        PermissaoFuncao.objects.filter(cargo_funcao=cargo).delete()
        
        # Criar novas permissões
        for campo, modulo in mapeamento_campos.items():
            acessos_selecionados = self.cleaned_data.get(campo, [])
            for acesso in acessos_selecionados:
                PermissaoFuncao.objects.create(
                    cargo_funcao=cargo,
                    modulo=modulo,
                    acesso=acesso,
                    ativo=True,
                    observacoes=f'Permissão definida no formulário de cargo/função'
                ) 